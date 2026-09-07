# tests/p10/test_p10_group_levels_are_read_once_per_group.py
"""A group-level value was recomputed for every member of the group.

`104` §11.2 step 2 puts the course's school and term on the GROUP: the syllabus
anchor states them and the sparse members are carried, so `materialise_branch`
asks `group_value_for_member` for each member of a group-level dimension. The
answer is the group's and does not vary between its members -- and
`group_level_value` recomputed it from scratch each time, walking every direct
anchor and asking P6 for that anchor's settled value one at a time. A group of M
members with A anchors therefore cost M x A slot reads at one dimension, and both
grow with the corpus.

Measured, P8--P11 over a 1,000-file synthetic corpus under cProfile (`104`
R-110), after R-72's and R-79's fixes: 1,000 asks made 1,003,000
`preferred_value_for` calls and cost 47.9 of 77.8 profiled seconds. At 5,000
files it is essentially the whole of the 2,365.6 s the same span took -- the run
that took 804 s before the group-level dimension existed at all.

The answer each member needs is a property of the GROUP, so it is computed once
per group out of one corpus read per field (`facts.read_surface.preferred_in_field`,
the read `104` R-79 published) and every member reads it off that.
`tree_design.upstream.group_level_reader` is where that happens and
`tree_design.pipeline._option_bindings` binds it.

**What must not change is every answer.** The rule is untouched -- direct anchors
and nobody else, disagreement is `None`, the strongest agreeing reliability wins
-- and `test_p10_materialise.py` is what holds each of those against the levels
they produce. This file asserts the growth rate, because a fix that only made
each read faster would leave the shape intact and still pass any wall-clock test
on a small corpus; and it pins the reader's answer to the per-anchor reading it
was built out of, so the two cannot drift.
"""
from __future__ import annotations

import pytest

from database_agent.db import create_schema
from evidence_shape.schema import create_evidence_schema
from facts.fields import create_fields
from facts.states import strength

from grouping.vocabulary import CONTEXT_SUPPORTED, DIRECT_ANCHOR
from tree_design.upstream import (
    AcceptedGroup, GroupMember, group_level_reader, group_level_value,
    group_level_values, preferred_value_for,
)

from p9.test_p9_retrieval import _fact, _file, _hash

#: Two group sizes, three times apart. A reader that asks per member does nine
#: times the work between them; one that asks per group does the same work twice.
SMALL, LARGE = 20, 60

#: The bar on the ratio. Generous on purpose: the per-call constant is not
#: identical at the two sizes. Measured on this corpus, before the fix and after:
#: 4,000 statements at twenty members and 36,000 at sixty, a ratio of 9.0 -- the
#: square exactly; then 4 and 4, a ratio of 1.0.
FLAT_ENOUGH = 2.0

#: The group's level, and a second field so "once per field" has something to
#: count. Every anchor agrees about the school, which is what makes the group
#: have a value at all.
SCHOOL, SUBJECT = "school", "subject"


@pytest.fixture()
def corpus(conn):
    create_schema(conn)
    create_evidence_schema(conn)
    create_fields(conn)
    return conn


def _member(conn, tmp_path, name: str, *, basis: str) -> GroupMember:
    file_id = _file(conn, tmp_path, name)
    return GroupMember(file_id=file_id, content_hash=_hash(conn, file_id),
                       basis=basis)


def _group(members, *, group_id: str = "g_course") -> AcceptedGroup:
    return AcceptedGroup(group_id=group_id, label="BUSIB 4300", domain="academic",
                         members=tuple(members), anchor_facts=(),
                         excluded_members=())


def _one_course(conn, tmp_path, members: int) -> AcceptedGroup:
    """One course group whose every member is a direct anchor stating the school.

    Every member an anchor is the shape the measurement found: at a thousand files
    the group's anchors and its members were the same thousand-odd files, so the
    per-member ask walked the whole group every time. A group with two anchors and
    a thousand carried members has the same defect and a smaller constant.
    """
    made = []
    for index in range(members):
        member = _member(conn, tmp_path, f"{index:03d}-notes.pdf",
                         basis=DIRECT_ANCHOR)
        _fact(conn, member.file_id, field_key=SCHOOL, value="Columbia",
              run_id=f"run-school-{index}")
        _fact(conn, member.file_id, field_key=SUBJECT, value="BUSIB4300",
              run_id=f"run-subject-{index}")
        made.append(member)
    return _group(made)


def _statements_for_every_member(conn, tmp_path, members: int) -> int:
    """Every statement one branch's group-level pass issues, over both dimensions.

    Counted rather than timed, for the reason the folder-expectations sibling
    gives: a stopwatch on a small corpus cannot tell a faster constant from a
    better shape. The reader is asked exactly as `materialise_branch` asks it --
    once per member per group-level dimension -- and what is counted is what the
    database was asked in the course of answering.
    """
    group = _one_course(conn, tmp_path, members)
    reader = group_level_reader(conn, groups=(group,))
    counted = 0

    def count(_statement: str) -> None:
        nonlocal counted
        counted += 1

    conn.set_trace_callback(count)
    try:
        for field_ref in (SCHOOL, SUBJECT):
            for member in group.members:
                reader(member, field_ref)
    finally:
        conn.set_trace_callback(None)
    return counted


def test_a_whole_level_costs_statements_that_do_not_count_the_members(corpus,
                                                                     tmp_path):
    """The item, as a growth rate rather than a stopwatch.

    Two databases, because the two groups have to be measured separately: sixty
    members in the database that already holds twenty would measure eighty
    against twenty and the ratio would mean nothing.
    """
    from database_agent.db import open_database

    small = _statements_for_every_member(corpus, tmp_path / "small", SMALL)
    other = open_database(tmp_path / "large.sqlite")
    try:
        create_schema(other)
        create_evidence_schema(other)
        create_fields(other)
        large = _statements_for_every_member(other, tmp_path / "large", LARGE)
    finally:
        other.close()

    growth = large / small
    assert growth < FLAT_ENOUGH, (
        f"a group of {SMALL} members cost {small} statements and a group of "
        f"{LARGE} cost {large}: {growth:.1f}x for 3x the group. The group-level "
        "value is being recomputed for each member, so five times the files is "
        "twenty-five times the work and a 5,000-file plan does not finish")
    assert large < LARGE, (
        f"{large} statements for {LARGE} members is at least one per member, and "
        "the answer is the GROUP's: it is computed once and read off, so a whole "
        "pass costs fewer statements than the group has members")


def test_the_field_is_read_once_however_many_members_ask(corpus, tmp_path):
    """The claim in its own terms, and the one a growth rate cannot make.

    Two group-level dimensions and twenty members: the corpus reading is fetched
    twice, not forty times, and not twice per member.
    """
    from facts import read_surface

    group = _one_course(corpus, tmp_path, SMALL)
    asked: list[str] = []
    original = read_surface.preferred_in_field

    def counting(conn, *, field_key):
        asked.append(field_key)
        return original(conn, field_key=field_key)

    import tree_design.upstream as upstream

    upstream.preferred_in_field = counting
    try:
        reader = group_level_reader(corpus, groups=(group,))
        for field_ref in (SCHOOL, SUBJECT):
            for member in group.members:
                reader(member, field_ref)
    finally:
        upstream.preferred_in_field = original

    assert sorted(asked) == sorted(set(asked)), (
        f"a field was read more than once: {asked}")
    assert set(asked) == {SCHOOL, SUBJECT}, asked


def _by_the_anchors_own_readings(conn, group: AcceptedGroup, field_ref: str):
    """The rule read one anchor at a time, which is the loop the fix replaced.

    Kept here rather than compared against `group_level_value` -- that now
    delegates to the bulk form, so comparing them would be comparing a function
    with itself. What can drift is P6's corpus-wide reading against P6's per-file
    one, and this is the per-file one.
    """
    found = []
    for member in group.members:
        if member.basis != DIRECT_ANCHOR:
            continue
        value = preferred_value_for(conn, file_id=member.file_id,
                                    field_ref=field_ref)
        if value is not None:
            found.append(value)
    if not found:
        return None
    if len({item.canonical_value for item in found}) != 1:
        return None
    return max(found, key=lambda item: strength(item.reliability))


def _mixed_corpus(conn, tmp_path):
    """Four groups that answer differently, and one file in none of them.

    * `agree` -- two anchors saying Columbia at two different strengths, a third
      anchor silent about the school, and a context-supported member that names a
      school of its own. The answer is Columbia at the stronger state, and the
      carried member's own reading is not the group's (`104` §11.1).
    * `disagree` -- two anchors naming two schools. The answer is `None`.
    * `silent` -- an anchor with no school fact at all. The answer is `None`.
    * `shared` -- claims the same file as `agree` does, second in branch order,
      so the reader's first-group-wins rule has something to decide.
    """
    def anchor(name, *, school=None, state="validated", basis=DIRECT_ANCHOR):
        member = _member(conn, tmp_path, name, basis=basis)
        if school is not None:
            _fact(conn, member.file_id, field_key=SCHOOL, value=school,
                  reliability_state=state, run_id=f"run-{name}")
        return member

    weak = anchor("syllabus.pdf", school="Columbia", state="validated")
    strong = anchor("registration.pdf", school="Columbia", state="direct")
    mute = anchor("problem-set.pdf")
    carried = anchor("essay.pdf", school="Georgetown Prep",
                     basis=CONTEXT_SUPPORTED)
    agree = _group([weak, strong, mute, carried], group_id="g_agree")

    disagree = _group([anchor("transfer-a.pdf", school="Columbia"),
                       anchor("transfer-b.pdf", school="NYU")],
                      group_id="g_disagree")
    silent = _group([anchor("scan.pdf")], group_id="g_silent")
    shared = _group([weak, anchor("reading-list.pdf", school="NYU")],
                    group_id="g_shared")
    loose = anchor("stray.pdf", school="Georgetown Prep")
    return (agree, disagree, silent, shared), loose


def test_the_reader_answers_what_the_anchors_own_readings_answer(corpus,
                                                                tmp_path):
    """The fork, pinned, over groups that agree, disagree, and say nothing."""
    groups, loose = _mixed_corpus(corpus, tmp_path)

    together = group_level_values(corpus, groups=groups, field_ref=SCHOOL)
    reader = group_level_reader(corpus, groups=groups)
    for group in groups:
        expected = _by_the_anchors_own_readings(corpus, group, SCHOOL)
        assert together[group.group_id] == expected, group.group_id
        assert group_level_value(
            corpus, group=group, field_ref=SCHOOL) == expected, group.group_id
        for member in group.members:
            if member.file_id in {other.file_id for first in groups
                                  for other in first.members
                                  if first is not group}:
                continue
            assert reader(member, SCHOOL) == expected, (group.group_id,
                                                        member.file_id)

    assert reader(loose, SCHOOL) is None, (
        "a file in no group of this branch has no group-level value, which is "
        "`00`:57's essay outside any group")
    assert group_level_values(corpus, groups=(), field_ref=SCHOOL) == {}


def test_a_file_two_groups_claim_is_answered_by_the_first_of_them(corpus,
                                                                 tmp_path):
    """`_members`' own rule for a shared file, kept where the value is read.

    `g_agree` and `g_shared` both hold the syllabus and they answer differently.
    The reader is built over the branch's groups in order, so the syllabus takes
    the first group's answer and is counted once -- not twice, and not the
    second group's.
    """
    (agree, disagree, silent, shared), _ = _mixed_corpus(corpus, tmp_path)
    syllabus = agree.members[0]
    assert syllabus.file_id in {member.file_id for member in shared.members}

    first = group_level_reader(corpus, groups=(agree, shared))
    second = group_level_reader(corpus, groups=(shared, agree))
    assert first(syllabus, SCHOOL) == group_level_value(
        corpus, group=agree, field_ref=SCHOOL)
    assert second(syllabus, SCHOOL) == group_level_value(
        corpus, group=shared, field_ref=SCHOOL)
    assert first(syllabus, SCHOOL) != second(syllabus, SCHOOL)


def test_the_comparison_above_rests_on_groups_that_answer_differently(corpus,
                                                                     tmp_path):
    """The teeth. If every group answered `None`, or all answered the same, the
    comparison would pass for the wrong reason."""
    groups, loose = _mixed_corpus(corpus, tmp_path)
    answers = group_level_values(corpus, groups=groups, field_ref=SCHOOL)

    assert answers["g_agree"] is not None
    assert answers["g_agree"].canonical_value == "Columbia"
    assert answers["g_agree"].reliability == "direct", (
        "two anchors agree at two strengths and the STRONGER is the group's, so "
        "`max` over the agreeing anchors is doing work here")
    assert answers["g_disagree"] is None, (
        "two anchors naming two schools is a real state and P10 does not pick "
        "between them")
    assert answers["g_silent"] is None
    assert answers["g_shared"] is None

    carried = next(member for member in groups[0].members
                   if member.basis == CONTEXT_SUPPORTED)
    own = preferred_value_for(corpus, file_id=carried.file_id, field_ref=SCHOOL)
    assert own is not None and own.canonical_value == "Georgetown Prep", (
        "the carried member does state a school of its own; the point is that "
        "the group's answer is not it")
    assert preferred_value_for(
        corpus, file_id=loose.file_id, field_ref=SCHOOL) is not None
