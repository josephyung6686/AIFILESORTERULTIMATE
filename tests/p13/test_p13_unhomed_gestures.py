"""§8.7's gestures, and whether P13 has a name for each of them.

`81` §14 ruled Q1' as reading (i): **the part that COLLECTS a gesture owns its
name.** `review_action` is P13's record, so P13 names the gestures and P9, P10 and
P11 carry those names verbatim (MINOR 6/7). The ruling's own consequence, in its
own words: *"P13's eighteen must grow to cover §8.7's six unhomed gestures and
§5's canvas ... Each addition is a closed-vocabulary member and needs the owner's
approval recorded at the member. They are not minted by whoever notices the gap."*

**That approval has not been given, so nothing is minted here.** This module is
the report, in the shape `84` §2 describes: a strict xfail that states the gap
today and turns the suite RED the day the six are added, so the addition cannot
land without someone reading the reason and filling in the approval the ruling
requires. The same pattern is at `tests/integration/test_composition_root.py:143`,
`tests/p13/test_p13_fixture_compatibility.py:72` and `tests/p6/test_p6_llm_seam.py:517`.

The alternative shape -- declaring six `ACTION_*` constants in
`src/review_surface/vocabulary.py` with an empty approval line -- was rejected on
that file's own evidence: a constant whose string `review_surface.vocabulary.check`
refuses is a second home for a name nobody has approved, and *"a literal is a
second home for a vocabulary and this project's most expensive defect class"*
(`src/review_surface/vocabulary.py:4-6`). The record of what is owed is instead a
comment AT the `ACTIONS` member, which is where `src/privacy/vocabulary.py:143-168`
records the one ruling this project has already taken on a closed vocabulary.
"""
from __future__ import annotations

import pytest

from review_surface import vocabulary as v

#: **PROPOSED SPELLINGS, NOT APPROVED, AND NOT PUBLISHED ANYWHERE IN `src/`.**
#:
#: The six §8.7 gestures P13 cannot name (`81` §4.4's table). A checker needs
#: something to look for, so each carries the name this file would expect P13 to
#: publish; `review_surface.vocabulary.check` refuses every one of them today and
#: no module under `src/` spells any of them. **The spelling is the owner's to
#: rule** -- when he does, replace these with what he ruled, add the members with
#: his approval recorded at them, and delete the marker below.
PROPOSED_EXCLUDE_FROM_PACKET: str = "exclude_from_packet"
PROPOSED_RENAME: str = "rename"
PROPOSED_MERGE: str = "merge"
PROPOSED_SPLIT: str = "split"
PROPOSED_REORDER: str = "reorder"
PROPOSED_CREATE_CUSTOM_TEMPLATE: str = "create_custom_template"
PROPOSED_SET_REFINEMENT_DISPOSITION: str = "set_refinement_disposition"

#: §8.7's own sentence, `planning/01-product-design-structured.md`:1842-1845, split
#: into the eleven gestures it names and mapped to the P13 action(s) that record
#: each. This is `81` §4.4's table, transcribed. The right-hand column is P13's,
#: not P9's or P10's: under the ruling those two carry P13's names, so "P10 has
#: `rename`" is not a home for "renaming a branch" -- it is the gesture P13 still
#: has to name, and `PROPOSED_RENAME` above is a placeholder for the name it will
#: have, not a member.
SECTION_8_7_GESTURES: dict[str, tuple[str, ...]] = {
    "accepting or rejecting a group": (v.ACTION_ACCEPT, v.ACTION_REJECT),
    "excluding one member from a packet": (PROPOSED_EXCLUDE_FROM_PACKET,),
    "renaming a branch": (PROPOSED_RENAME,),
    "merging or splitting groups": (PROPOSED_MERGE, PROPOSED_SPLIT),
    "changing template order": (PROPOSED_REORDER,),
    "creating a custom template": (PROPOSED_CREATE_CUSTOM_TEMPLATE,),
    "moving a residual file to a custom location": (
        v.ACTION_CHANGE_DESTINATION, v.ACTION_CREATE_CUSTOM_FOLDER),
    "choosing a shallow fallback": (PROPOSED_SET_REFINEMENT_DISPOSITION,),
    "keeping a file in place": (v.ACTION_LEAVE_UNTOUCHED,),
    "marking a file private": (v.ACTION_MARK_PRIVATE,),
    "disabling a type of suggestion": (v.ACTION_DISABLE_SUGGESTION_TYPE,),
}

#: The six with no member of `ACTIONS` behind them today. Named rather than
#: re-derived at the call site so the xfail's reason and the guard cannot disagree.
UNHOMED: tuple[str, ...] = (
    "excluding one member from a packet",
    "renaming a branch",
    "merging or splitting groups",
    "changing template order",
    "creating a custom template",
    "choosing a shallow fallback",
)


def unhomed_gestures(actions: tuple[str, ...]) -> tuple[str, ...]:
    """Every §8.7 gesture with no action in `actions` to be recorded as.

    Takes the vocabulary rather than reading `v.ACTIONS` directly, so the twin
    below can hand it a doctored one and watch the answer change.
    """
    return tuple(
        gesture for gesture, recorded_as in SECTION_8_7_GESTURES.items()
        if not all(name in actions for name in recorded_as)
    )


def test_the_five_homed_gestures_name_actions_p13_actually_publishes():
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


def test_no_proposed_name_is_in_p13s_closed_vocabulary_yet():
    """The proposals above are proposals. `check` refuses every one, which is what
    "not minted" means concretely -- an action carrying one of these names cannot
    be collected today."""
    for proposed in (PROPOSED_EXCLUDE_FROM_PACKET, PROPOSED_RENAME,
                     PROPOSED_MERGE, PROPOSED_SPLIT, PROPOSED_REORDER,
                     PROPOSED_CREATE_CUSTOM_TEMPLATE,
                     PROPOSED_SET_REFINEMENT_DISPOSITION):
        assert proposed not in v.ACTIONS
        with pytest.raises(v.OutOfVocabulary):
            v.check(proposed, v.ACTIONS, name="action")


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


@pytest.mark.xfail(strict=True, reason=(
    "`81` §14's ruling: P13 owns the name of a gesture, so P13's eighteen must "
    "grow to cover the six §8.7 gestures with no home -- excluding one member "
    "from a packet, renaming a branch, merging or splitting groups, changing "
    "template order, creating a custom template, choosing a shallow fallback. "
    "OWNER APPROVAL IS OWED AND HAS NOT BEEN GIVEN: adding a member to a closed "
    "vocabulary requires the owner's approval recorded AT THE MEMBER "
    "(`src/review_surface/move_permission.py:33-34`), and the ruling says in its "
    "own words that these 'are not minted by whoever notices the gap'. What is "
    "owed is recorded at the member, in the block above `ACTIONS` in "
    "`src/review_surface/vocabulary.py`. The spellings this file proposes are "
    "placeholders and the owner's ruling replaces them. When the six are approved "
    "and added this test XPASSES and the suite goes RED -- delete the marker "
    "then, and not before."))
def test_every_gesture_section_8_7_names_has_a_p13_action():
    """§8.7 says every one of these *"should become local learning records with
    scope"*. A gesture P13 cannot name is a gesture that becomes no record at
    all, so the person makes it and the product forgets."""
    assert unhomed_gestures(v.ACTIONS) == (), (
        "§8.7 names these and P13 has no action for them: "
        f"{list(unhomed_gestures(v.ACTIONS))}")
