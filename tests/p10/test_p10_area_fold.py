# tests/p10/test_p10_area_fold.py
"""`00`:67 -- "aggregates ... into a small set of proposed major areas" -- had
no producer: one root card per accepted group. After amendment 12 a life that
spans two schemas is two drafts wearing one label, and this is the fold that
makes them one area with plural `accepted_group_ids`. No new node type; the
plural field `_design_one_branch` already reads.
"""
from __future__ import annotations

import pytest

from tree_design.candidates import horizontal_candidates, same_label_areas
from tree_design.schema import create_tree_schema
from tree_design.upstream import AcceptedGroup, GroupMember


def _group(group_id, label, domain, files):
    return AcceptedGroup(
        group_id=group_id, label=label, domain=domain,
        members=tuple(GroupMember(f, f"h_{f}", "direct-anchor") for f in files),
        anchor_facts=(f"fact_{group_id}",), excluded_members=())


NOTES = _group("v1:academic:Education:aaaa", "Education", "academic", ["n1", "n2"])
PACKET = _group("v1:college_applications:Education:bbbb", "Education",
                "college_applications", ["p1", "n2"])
CV = _group("v1:career:Career:cccc", "Career", "career", ["c1"])


def test_same_label_groups_fold_and_different_labels_do_not():
    areas = same_label_areas((NOTES, PACKET, CV))

    assert [[g.group_id for g in area] for area in areas] == [
        [NOTES.group_id, PACKET.group_id], [CV.group_id]]


STALE = _group("v1:academic:Education:0ld0", "Education", "academic", ["n1"])


def test_only_the_groups_the_decision_names_fold_into_an_area():
    """A draft accepted in an EARLIER run and superseded in content by this
    run's draft of the same label is still "accepted" at `PLAN_VERSION` (a
    constant), so `accepted_groups` keeps returning it. Before the fold its
    card was simply not chosen; folded into the area it rides in on the new
    draft's id and P11 refuses the whole branch at the tree's version
    (`GroupNotAcceptedInVersion`) -- measured on the silent-file pin's third
    run. So an area folds only the groups the decision names; every other
    group is its own card, unchosen, exactly as before."""
    areas = same_label_areas((NOTES, PACKET, STALE),
                             foldable=frozenset({NOTES.group_id, PACKET.group_id}))

    assert [[g.group_id for g in area] for area in areas] == [
        [NOTES.group_id, PACKET.group_id], [STALE.group_id]]


def test_a_group_the_decision_did_not_name_is_not_in_the_areas_card(conn):
    create_tree_schema(conn)
    cards = horizontal_candidates(
        conn, accepted=(NOTES, PACKET, STALE), existing_folders=(), user_labels=(),
        active_domains=("academic",), sensitive_group_ids=frozenset(),
        foldable=frozenset({NOTES.group_id, PACKET.group_id}))

    by_subject = {card.subject_id: card for card in cards}
    assert by_subject["area:Education"].accepted_group_ids == (
        NOTES.group_id, PACKET.group_id)
    assert by_subject[STALE.group_id].accepted_group_ids == (STALE.group_id,)


def test_a_folded_area_is_one_card_naming_every_group_and_counting_every_file_once(conn):
    """SABOTAGE: sum the two counts. `n2` is in both groups (`00`:63) and the
    card says 4 files over 3. SABOTAGE: fold the cards after they are built --
    the same double count, because a card carries no member ids. (`106`'s
    draft of this test asserted 4, which IS the double count; the members are
    `n1`, `n2`, `p1`.)"""
    create_tree_schema(conn)
    cards = horizontal_candidates(
        conn, accepted=(NOTES, PACKET, CV), existing_folders=(), user_labels=(),
        active_domains=("academic", "college_applications", "career"),
        sensitive_group_ids=frozenset())

    education = next(c for c in cards if c.display_label == "Education")
    assert education.subject_id == "area:Education"
    assert education.accepted_group_ids == (NOTES.group_id, PACKET.group_id)
    assert education.supporting_file_count == 3
    assert education.source == "accepted-group"
    career = next(c for c in cards if c.display_label == "Career")
    assert career.subject_id == CV.group_id
    assert career.accepted_group_ids == (CV.group_id,)


def test_no_group_is_lost_in_the_fold(conn):
    """Every accepted group is named by exactly one card."""
    create_tree_schema(conn)
    cards = horizontal_candidates(
        conn, accepted=(NOTES, PACKET, CV), existing_folders=(), user_labels=(),
        active_domains=("academic",), sensitive_group_ids=frozenset())

    named = [g for c in cards for g in c.accepted_group_ids]
    assert sorted(named) == sorted([NOTES.group_id, PACKET.group_id, CV.group_id])
    assert len(named) == len(set(named))


def test_a_sensitive_group_makes_the_whole_area_sensitive(conn):
    """Marked and counted: one protected draft under a life marks the area,
    never the reverse. SABOTAGE: `all(...)` instead of `any(...)`."""
    create_tree_schema(conn)
    cards = horizontal_candidates(
        conn, accepted=(NOTES, PACKET), existing_folders=(), user_labels=(),
        active_domains=("academic",), sensitive_group_ids=frozenset({PACKET.group_id}))

    assert next(c for c in cards if c.display_label == "Education").sensitive_content_present


def test_an_inactive_schema_inside_a_folded_area_is_named_and_the_area_still_shown(conn):
    """The standing rule at the area grain: a schema that did not activate is
    said on the card, and nothing is left out. SABOTAGE: read `inactive` off
    the first group only. The packet's schema is inactive here and the card
    would not say so."""
    create_tree_schema(conn)
    cards = horizontal_candidates(
        conn, accepted=(NOTES, PACKET), existing_folders=(), user_labels=(),
        active_domains=("academic",), sensitive_group_ids=frozenset())

    (education,) = cards
    assert "college_applications" in education.why_suggested
    assert "did not activate" in education.why_suggested


# --- Task 4.2: a folded area is chosen when any of its drafts was ----------------

from p10.test_p10_multi_life import corpus  # noqa: E402,F401


def test_a_folded_area_is_designed_once_and_every_file_of_both_lives_is_under_it(corpus):
    """THE GATE: no file loses a home in the fold. Through `design_tree` on the
    three-life corpus with the practice and the degree relabelled to one word by
    the person, exactly as 12a(ii) lets them.

    SABOTAGE: leave the chosen filter on `subject_id` alone. `area:Work` is in
    no `branch_group_ids`, `NothingToDesign` is raised, and two accepted lives
    have no node at all -- the silent omission the standing rule forbids.
    """
    import dataclasses

    from p10.multi_life_corpus import ACADEMIC_GROUP, LAW_GROUP, MEDICAL_GROUP
    from p10.test_p10_multi_life import authorities, design

    class _Relabelled:
        """The person renamed two drafts to one word; the store is untouched."""
        def __init__(self, inner):
            self._inner = inner

        def __getattr__(self, name):
            return getattr(self._inner, name)

        def group(self, group_id):
            group = self._inner.group(group_id)
            if group_id in (ACADEMIC_GROUP, LAW_GROUP):
                return dataclasses.replace(group, display_label="Work")
            return group

    result = design(corpus, auth=authorities(
        corpus, group_reader=_Relabelled(corpus.reader())))

    work = next(b for b in result.branches if b.candidate.display_label == "Work")
    assert set(work.candidate.accepted_group_ids) == {ACADEMIC_GROUP, LAW_GROUP}
    every_file = corpus.group_file_ids(ACADEMIC_GROUP) | corpus.group_file_ids(LAW_GROUP)
    assert work.options[0].member_count == len(every_file)
    covered = frozenset().union(*(frozenset(c.covered_file_ids)
                                  for c in work.routing.candidates))
    assert covered == every_file
    roots = [n for n in result.tree.nodes if n.parent_node_id is None
             and n.node_type == "proposed"]
    assert [n.display_label for n in roots].count("Work") == 1
    associated = {g for n in result.tree.nodes for g in n.associated_group_ids}
    assert {ACADEMIC_GROUP, LAW_GROUP, MEDICAL_GROUP} <= associated
