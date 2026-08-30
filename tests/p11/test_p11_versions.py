"""§8.8 -- a new plan version marks work for review and reclassifies nothing.

Every v2 fixture is minted P10's way (`p10_fixtures.next_version`): a NEW
`node_id` per version, lineage in `origin_node_id`. That is not decoration. Under
P10's minting **no `node_id` survives a draft**, so a re-projection that matched
on `node_id` would find no successor for ANY node and would send every decision
back to review after a pure rename -- the outcome §8.8 forbids by name.
"""
from __future__ import annotations

from dataclasses import replace

import pytest

from placement import vocabulary as v
from placement.index import build_destination_index, legal_node_ids
from placement.learning import Suppression
from placement.records import Destination, Subject
from placement.store import record_decision
from placement.versions import (
    VersionDiff, learned_preferences_still_applicable, reproject,
)
from p11.conftest import FIXED_CLOCK
from p11.p10_fixtures import FROZEN_TREE, next_version
from p11.test_p11_records import _decision


def _placed(**overrides):
    """A decision naming a node the frozen tree actually has.

    `_decision`'s default destination is `n1`, which is in no tree. A decision
    about a node the from-version index never contained proves nothing about
    lineage: it is marked for review because its node was never there, which is a
    different sentence from the one this task implements.
    """
    values = dict(destination=Destination(node_id="n-course",
                                          node_role=v.ORDINARY))
    values.update(overrides)
    return _decision(**values)


def _v2(**kwargs):
    return next_version(plan_version_id="plan-2", suffix="@2", **kwargs)


def _renamed(node):
    if node.origin_node_id != "n-course":
        return node
    return replace(node, display_label="PHYS 1401 — Mechanics")


def _indexed(conn, tree):
    build_destination_index(conn, tree, component_version="P11-test",
                            observed_at=FIXED_CLOCK)


def _record(conn, decision):
    record_decision(conn, decision, component_version="P11-test",
                    observed_at=FIXED_CLOCK)


# --- removal ----------------------------------------------------------------------

def test_a_removed_node_marks_its_decisions_for_renewed_review(p11_conn):
    _indexed(p11_conn, FROZEN_TREE)
    _record(p11_conn, _placed(decision_id="d1"))
    _indexed(p11_conn, _v2(drop=("n-course",)))
    diff = reproject(p11_conn, from_plan_version="plan-1",
                     to_plan_version="plan-2")
    assert diff.requiring_renewed_review == ("d1",)
    assert diff.removed_node_ids == ("n-course",)
    assert diff.carried_unchanged == ()


def test_a_removed_node_is_never_matched_onto_a_similar_survivor(p11_conn):
    # The failure this exists to prevent: `n-course-alt` still exists and looks
    # like a plausible home. §8.8 forbids remapping, so nothing is written that
    # names it -- and the assertions below are only meaningful because the
    # survivor is genuinely there to be matched onto.
    _indexed(p11_conn, FROZEN_TREE)
    _record(p11_conn, _placed(decision_id="d1"))
    v2 = _v2(drop=("n-course",))
    _indexed(p11_conn, v2)
    assert "n-course-alt@2" in legal_node_ids(p11_conn, plan_version="plan-2")
    reproject(p11_conn, from_plan_version="plan-1", to_plan_version="plan-2")
    rows = p11_conn.execute(
        "SELECT record_id, plan_version, node_id FROM placement_decisions"
    ).fetchall()
    assert [(r["record_id"], r["plan_version"], r["node_id"]) for r in rows] == [
        ("d1", "plan-1", "n-course")]


def test_a_new_version_moves_nothing_already_placed(p11_conn):
    # §8.8: "A new plan should never silently reclassify or move old files."
    _indexed(p11_conn, FROZEN_TREE)
    _record(p11_conn, _placed(decision_id="d1"))
    _indexed(p11_conn, _v2(drop=("n-course",)))
    reproject(p11_conn, from_plan_version="plan-1", to_plan_version="plan-2")
    original = p11_conn.execute(
        "SELECT outcome, node_id, superseded_by FROM placement_decisions "
        "WHERE record_id = 'd1'").fetchone()
    assert original["outcome"] == v.PLACE
    assert original["node_id"] == "n-course"
    assert original["superseded_by"] is None


# --- the lineage half: a rename and a move are not removals -------------------------

def test_a_renamed_node_carries_the_decision_on_its_lineage_not_its_id(p11_conn):
    # The load-bearing test of this task. P10 mints a NEW node_id in plan-2, so
    # `n-course` does not exist there and an id match would find nothing. §8.8
    # forbids that outcome by name: a rename is not a removal and must not send
    # twenty-three files back to review. `origin_node_id` is what survives.
    _indexed(p11_conn, FROZEN_TREE)
    _record(p11_conn, _placed(decision_id="d1"))
    v2 = _v2(edit=_renamed)
    _indexed(p11_conn, v2)
    assert {node.node_id for node in v2.nodes}.isdisjoint(
        {node.node_id for node in FROZEN_TREE.nodes})   # nothing survives by id
    diff = reproject(p11_conn, from_plan_version="plan-1",
                     to_plan_version="plan-2")
    assert diff.requiring_renewed_review == ()
    assert diff.carried_unchanged == ("d1",)
    assert diff.removed_node_ids == ()


def test_a_moved_node_carries_the_decision_too(p11_conn):
    # A relocation also mints a new id, and the decision still carries. What
    # changes is the path P12 composes from the new parent chain, which is P12's
    # to compose and not a remap.
    _indexed(p11_conn, FROZEN_TREE)
    _record(p11_conn, _placed(decision_id="d1"))

    def moved(node):
        node = _renamed(node)
        return (replace(node, parent_node_id=None)
                if node.origin_node_id == "n-course" else node)

    v2 = _v2(edit=moved)
    _indexed(p11_conn, v2)
    assert next(n for n in v2.nodes
                if n.origin_node_id == "n-course").parent_node_id is None
    diff = reproject(p11_conn, from_plan_version="plan-1",
                     to_plan_version="plan-2")
    assert diff.carried_unchanged == ("d1",)


def test_every_decision_would_need_review_if_identity_came_from_node_id(p11_conn):
    # The negative twin that makes the two tests above discriminating. If lineage
    # were read from `node_id`, `carried_unchanged` above would be empty and
    # `requiring_renewed_review` would hold every decision -- so this pins the
    # world that makes that mistake possible: plan-2 shares NO id with plan-1,
    # and every plan-1 origin is still present.
    _indexed(p11_conn, FROZEN_TREE)
    _indexed(p11_conn, _v2(edit=_renamed))
    v1 = legal_node_ids(p11_conn, plan_version="plan-1")
    v2 = legal_node_ids(p11_conn, plan_version="plan-2")
    assert v1.isdisjoint(v2)
    assert len(v1) == len(v2)


# --- what the diff does not touch ----------------------------------------------------

def test_an_abstention_needs_no_renewed_review_when_a_node_disappears(p11_conn):
    # It named no node, so no node's removal invalidates it.
    _indexed(p11_conn, FROZEN_TREE)
    _record(p11_conn, _decision(decision_id="d1", outcome=v.ABSTAIN,
                                destination=None,
                                abstention_reason=v.NO_SUPPORTED_DESTINATION))
    _indexed(p11_conn, _v2(drop=("n-course",)))
    diff = reproject(p11_conn, from_plan_version="plan-1",
                     to_plan_version="plan-2")
    assert diff.requiring_renewed_review == ()
    assert diff.carried_unchanged == ()


def test_a_node_that_is_present_but_never_legal_is_neither_carried_nor_removed(
        p11_conn):
    # The standing ruling, at the version boundary: a node the user left alone is
    # IN the frozen tree and OUT of `legal_destination_ids`. Present and legal to
    # SEE is not the same as legal to PLACE INTO, and re-projection preserves both
    # halves -- `n-ignored` survives into plan-2 and is reported as neither
    # carried nor removed, because nothing was ever placed into it to carry and
    # nothing was taken away.
    _indexed(p11_conn, FROZEN_TREE)
    _record(p11_conn, _placed(decision_id="d1"))
    v2 = _v2(edit=_renamed)
    _indexed(p11_conn, v2)
    assert "n-ignored" in {node.origin_node_id for node in v2.nodes}
    assert "n-ignored@2" not in legal_node_ids(p11_conn, plan_version="plan-2")
    diff = reproject(p11_conn, from_plan_version="plan-1",
                     to_plan_version="plan-2")
    assert "n-ignored" not in diff.removed_node_ids
    assert "n-ignored@2" not in diff.removed_node_ids


def test_the_diff_counts_what_88s_example_counts(p11_conn):
    # §8.8's own sentence is a COUNT of files, so the diff must be able to give
    # one without the caller re-deriving it.
    # Three distinct subjects: the store's one-current-row index is keyed on
    # (plan_version, subject_ref), so three decisions about one file would be
    # three attempts at the same live row rather than three files.
    _indexed(p11_conn, FROZEN_TREE)
    for index in range(1, 4):
        _record(p11_conn, _placed(
            decision_id=f"d{index}",
            subject=Subject(kind=v.FILE, file_id=f"f{index}",
                            content_hash=f"h{index}", group_id=None,
                            member_file_ids=())))
    _indexed(p11_conn, _v2(drop=("n-course",)))
    diff = reproject(p11_conn, from_plan_version="plan-1",
                     to_plan_version="plan-2")
    assert len(diff.requiring_renewed_review) == 3
    assert diff.renewed_review_count == 3


def test_a_decision_naming_a_node_the_from_version_never_had_asks_again(p11_conn):
    # `_decision`'s own default names `n1`, which is in no tree. There is no
    # lineage to follow, so there is no basis for carrying it -- and the safe
    # answer is the user, not a plausible successor.
    _indexed(p11_conn, FROZEN_TREE)
    _record(p11_conn, _decision(decision_id="d1"))
    _indexed(p11_conn, _v2())
    diff = reproject(p11_conn, from_plan_version="plan-1",
                     to_plan_version="plan-2")
    assert diff.requiring_renewed_review == ("d1",)
    assert diff.removed_node_ids == ("n1",)


# --- learned preferences ---------------------------------------------------------------

def _suppression(node_id):
    return Suppression(node_id=node_id, scope="node", subject_id=node_id,
                       basis_key=f"{node_id}->{node_id}", event_id=1)


def test_a_preference_about_a_surviving_node_still_applies_after_a_rename(p11_conn):
    # §8.8: "Learned preferences carry across versions." A suppression recorded
    # against plan-1 names a plan-1 `node_id`, which P10's per-version minting
    # guarantees is absent from plan-2. Filtered on `node_id` alone, EVERY
    # learned preference would silently stop applying at the first tree edit --
    # the exact opposite of the sentence.
    _indexed(p11_conn, _v2(edit=_renamed))
    kept = learned_preferences_still_applicable(
        p11_conn, plan_version="plan-2",
        suppressions=(_suppression("n-course"),))
    assert [item.node_id for item in kept] == ["n-course"]


def test_a_preference_named_in_the_new_versions_own_ids_also_applies(p11_conn):
    # The other identity: a preference recorded AGAINST plan-2 names plan-2's own
    # ids. Matching only on origin would drop it, which is the same failure from
    # the other side.
    _indexed(p11_conn, _v2(edit=_renamed))
    kept = learned_preferences_still_applicable(
        p11_conn, plan_version="plan-2",
        suppressions=(_suppression("n-course@2"),))
    assert [item.node_id for item in kept] == ["n-course@2"]


def test_a_preference_recorded_against_a_minted_id_carries_to_the_next_version(
        p11_conn):
    """The general case the docstring already claimed and the code did not do.

    The two tests above both pass by coincidence: `n-course` is plan-1's id AND
    its own origin, so `item.node_id in surviving_origins` happens to match. From
    plan-2 onward that stops being true — every id is minted and no id equals its
    origin — so a preference recorded against plan-2 and filtered against plan-3
    was matched against neither identity and was silently dropped.

    §8.8's sentence is "preferences carry across versions", and a filter that
    works only for the FIRST version is one that fails on every real tree, since
    a user reaches plan-2 the moment they rename a folder. Found by driving
    P10's own chain, which mints exactly this way.
    """
    v2 = _v2()
    _indexed(p11_conn, v2)
    _indexed(p11_conn, next_version(v2, plan_version_id="plan-3", suffix="@3"))
    kept = learned_preferences_still_applicable(
        p11_conn, plan_version="plan-3",
        suppressions=(_suppression("n-course@2"),))
    assert [item.node_id for item in kept] == ["n-course@2"]


def test_a_preference_about_a_node_no_version_ever_held_is_not_applied(p11_conn):
    """The negative twin. Resolving through the index must not become a way for
    an unknown id to pass: a suppression naming a node no plan version contains
    has nothing to suppress and is filtered out, not carried."""
    v2 = _v2()
    _indexed(p11_conn, v2)
    _indexed(p11_conn, next_version(v2, plan_version_id="plan-3", suffix="@3"))
    assert learned_preferences_still_applicable(
        p11_conn, plan_version="plan-3",
        suppressions=(_suppression("n-invented"),)) == ()


def test_a_preference_about_a_removed_node_is_kept_but_not_applied(p11_conn):
    # It is still a true fact about what the user decided, so it is preserved --
    # it is simply not applied, because there is nothing left for it to suppress.
    # Deleting it instead would lose the reason if the node ever came back.
    _indexed(p11_conn, _v2(drop=("n-course",)))
    suppressions = (_suppression("n-course"), _suppression("n-general"))
    kept = learned_preferences_still_applicable(
        p11_conn, plan_version="plan-2", suppressions=suppressions)
    assert [item.node_id for item in kept] == ["n-general"]
    assert len(suppressions) == 2       # nothing was deleted


# --- the gap this task leaves open, tracked rather than described -----------------------

def test_the_version_diff_is_reachable_from_somewhere_in_placement():
    """`reproject` and `learned_preferences_still_applicable` have no caller.

    Their owed consumer is the pipeline's adopt-a-new-version path and P13's
    version-diff surface. Until one lands, §8.8's re-projection is a fully-tested
    component connected to nothing -- the shape this codebase shipped seven times.

    **Corrected 2026-08-31: P13's surface IS built, and the gap is still open.**
    This docstring used to say "neither of which is built", and half of that is
    now false: `review_surface/versions_view.py:115`'s `structural_diff_view`
    exists and takes a `VersionDiff`. It does not call `reproject` -- deliberately,
    per its own docstring at `versions_view.py:120-124`, because "`reproject` is a
    P11 call with its own revalidation inputs and P13 must not choose them" -- and
    `structural_diff_view` is itself unreachable from `cli.main`, which imports
    only `review_surface.schema` and `review_surface.vocabulary`.

    So the caller is still owed, and the reason has moved: it is no longer "the
    consumer is unbuilt" but "the consumer is built, unreached, and correct not to
    call this itself". The remaining blocker is upstream of all three names --
    `cli.py:1211` mints a fresh `uuid4` run token per run and
    `tree_design/pipeline.py:789` writes each run's root version with
    `predecessor_id=None`, so two runs share no `origin_node_id` and a `reproject`
    across them would report every file as needing renewed review. Wiring a call
    before that lineage exists would return confident nonsense, not a missing
    answer.

    `xfail(strict=True)`: it reports the gap today and turns the suite RED the
    day a caller appears, which forces the marker off.
    """
    from p11.test_p11_groups import _placement_sources_calling

    for entry_point in ("reproject", "learned_preferences_still_applicable"):
        assert _placement_sources_calling(entry_point) - {"versions.py"}, entry_point


test_the_version_diff_is_reachable_from_somewhere_in_placement = pytest.mark.xfail(
    strict=True,
    reason="the adopt-a-version path is unbuilt; nothing calls reproject or "
           "learned_preferences_still_applicable. XPASSes and fails the suite "
           "the moment a caller appears.",
)(test_the_version_diff_is_reachable_from_somewhere_in_placement)


def test_the_diff_is_a_record_and_not_a_rewrite():
    # §8.8's mark is COMPUTED, not stamped onto the decision row. `store.py` is
    # append-only by doctrine -- "Nothing here rewrites a decision" -- so a
    # re-projection that set `review_policy` on an existing row would be the one
    # mutation the store exists to forbid, and the diff would stop being
    # re-derivable from the two versions.
    assert VersionDiff.__dataclass_fields__.keys() == {
        "from_plan_version", "to_plan_version", "requiring_renewed_review",
        "carried_unchanged", "removed_node_ids"}
