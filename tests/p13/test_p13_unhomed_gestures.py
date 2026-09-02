"""§8.7's gestures, and whether P13 has a name for each of them.

`81` §14 ruled Q1' as reading (i): **the part that COLLECTS a gesture owns its
name.** `review_action` is P13's record, so P13 names the gestures and P9, P10 and
P11 carry those names verbatim (MINOR 6/7). The ruling's own consequence, in its
own words: *"P13's eighteen must grow to cover §8.7's six unhomed gestures and
§5's canvas ... Each addition is a closed-vocabulary member and needs the owner's
approval recorded at the member. They are not minted by whoever notices the gap."*

**All six are homed as of 2026-09-02, on the owner's approval of seven members
recorded at `ACTIONS` in `src/review_surface/vocabulary.py`.** This module was the
report while they were not: a strict xfail that stated the gap and would turn the
suite RED the day the members landed, so they could not land without someone
reading the reason and filling in the approval the ruling requires. It did exactly
that, twice -- a delegated approval was refused on it, and a relay that listed six
of the seven left it in place naming the missing one.

**The marker is gone now, removed by the commit that closed the gap**, which is
the interlock working rather than a formality: the tuple and the marker could not
move in separate commits in either direction. What remains is the live guard --
every §8.7 gesture still names an action P13 publishes, and a member retired or
respelled brings the report back.

The alternative shape -- declaring the `ACTION_*` constants early with an empty
approval line -- was rejected on `vocabulary.py`'s own evidence: a constant whose
string `review_surface.vocabulary.check` refuses is a second home for a name
nobody has approved, and *"a literal is a second home for a vocabulary and this
project's most expensive defect class"* (`src/review_surface/vocabulary.py:4-6`).
"""
from __future__ import annotations

from review_surface import vocabulary as v

#: **ALL SIX ARE HOMED as of 2026-09-02.** The owner approved seven members --
#: six gestures, seven members, because "merging or splitting groups" is one §8.7
#: phrase and two gestures -- recorded at `ACTIONS` in
#: `review_surface/vocabulary.py`. There is nothing left to propose here, so
#: every entry below points at a real `v.ACTION_*` constant and the strict-xfail
#: marker that reported the gap is gone, removed by the commit that closed it.
#: §8.7's own sentence, `planning/01-product-design-structured.md`:1842-1845, split
#: into the eleven gestures it names and mapped to the P13 action(s) that record
#: each. This is `81` §4.4's table, transcribed. The right-hand column is P13's,
#: not P9's or P10's: under the ruling those two carry P13's names, so "P10 has
#: `rename`" is not a home for "renaming a branch" -- it is the gesture P13 still
#: has to name, and `PROPOSED_RENAME` above is a placeholder for the name it will
#: have, not a member.
SECTION_8_7_GESTURES: dict[str, tuple[str, ...]] = {
    "accepting or rejecting a group": (v.ACTION_ACCEPT, v.ACTION_REJECT),
    "excluding one member from a packet": (v.ACTION_EXCLUDE_FROM_PACKET,),
    "renaming a branch": (v.ACTION_RENAME,),
    "merging or splitting groups": (v.ACTION_MERGE, v.ACTION_SPLIT),
    "changing template order": (v.ACTION_REORDER,),
    "creating a custom template": (v.ACTION_CREATE_CUSTOM_TEMPLATE,),
    "moving a residual file to a custom location": (
        v.ACTION_CHANGE_DESTINATION, v.ACTION_CREATE_CUSTOM_FOLDER),
    "choosing a shallow fallback": (v.ACTION_SET_REFINEMENT_DISPOSITION,),
    "keeping a file in place": (v.ACTION_LEAVE_UNTOUCHED,),
    "marking a file private": (v.ACTION_MARK_PRIVATE,),
    "disabling a type of suggestion": (v.ACTION_DISABLE_SUGGESTION_TYPE,),
}

#: Empty, and the whole point of this module is that it stays empty. It was six
#: until 2026-09-02. A gesture appearing here again means §8.7 grew or a member
#: was retired, and either way somebody made a gesture the product cannot record.
UNHOMED: tuple[str, ...] = ()


def unhomed_gestures(actions: tuple[str, ...]) -> tuple[str, ...]:
    """Every §8.7 gesture with no action in `actions` to be recorded as.

    Takes the vocabulary rather than reading `v.ACTIONS` directly, so the twin
    below can hand it a doctored one and watch the answer change.
    """
    return tuple(
        gesture for gesture, recorded_as in SECTION_8_7_GESTURES.items()
        if not all(name in actions for name in recorded_as)
    )


def test_every_gesture_in_the_table_names_an_action_p13_actually_publishes():
    """The live half. If a name in the table above is respelled or dropped from
    `ACTIONS`, this fails -- so the table cannot quietly go stale and make the
    report below look smaller than it is."""
    for gesture in SECTION_8_7_GESTURES:
        if gesture in UNHOMED:
            continue
        for name in SECTION_8_7_GESTURES[gesture]:
            assert name in v.ACTIONS, (
                f"{gesture!r} is recorded as {name!r}, which P13 no longer "
                "publishes")


def test_the_seven_the_owner_approved_are_all_published():
    """The live half of the 2026-09-02 approval. If any of the seven is respelled
    or dropped, this names it.

    Approved in TWO askings and the distinction cost a correction commit
    (`6ad5110`): the first six were shown as a tuple and approved together, and
    `create_custom_template` was put to him separately and approved by name after
    a relay dropped it. The block above `ACTIONS` in `review_surface/vocabulary.py`
    keeps that history.

    Spelled as literals rather than read off `v.ACTION_*`, deliberately: these are
    the strings he approved, and a test that compared the constants to themselves
    would pass through any rename.
    """
    for approved in ("exclude_from_packet", "rename", "merge", "split",
                     "reorder", "create_custom_template",
                     "set_refinement_disposition"):
        assert approved in v.ACTIONS, (
            f"{approved!r} was approved by the owner on 2026-09-02 and recorded "
            "at the member; it is no longer published")


def test_the_report_can_tell_a_homed_gesture_from_an_unhomed_one():
    """The negative twin of the checker, as a pair -- `74` §6 A1's shape.

    Handed P13's real eighteen it reports the six; handed an eighteen with
    `mark_private` removed it reports seven; handed a vocabulary that covers
    everything it reports none. A checker that answered "six" to all three would
    be measuring nothing.
    """
    assert unhomed_gestures(v.ACTIONS) == UNHOMED

    without_private = tuple(n for n in v.ACTIONS if n != v.ACTION_MARK_PRIVATE)
    assert unhomed_gestures(without_private) == UNHOMED + (
        "marking a file private",)

    everything = v.ACTIONS + tuple(
        name for names in SECTION_8_7_GESTURES.values() for name in names)
    assert unhomed_gestures(everything) == ()


def test_every_gesture_section_8_7_names_has_a_p13_action():
    """§8.7 says every one of these *"should become local learning records with
    scope"*. A gesture P13 cannot name is a gesture that becomes no record at
    all, so the person makes it and the product forgets."""
    assert unhomed_gestures(v.ACTIONS) == (), (
        "§8.7 names these and P13 has no action for them: "
        f"{list(unhomed_gestures(v.ACTIONS))}")
