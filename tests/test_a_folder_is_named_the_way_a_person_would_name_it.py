# tests/test_a_folder_is_named_the_way_a_person_would_name_it.py
"""The owner, 18 Sep 2026: *"you need to make the phrasing and the names and
folder and stuff all human readable and not machine readable."*

**WHAT THEY ARE LOOKING AT.** The tree the product built over their 371 files has
seven top-level folders and five of them are `nonprofit`, `photos`, `research`,
`career`, `finance` -- lowercase internal identifiers, written onto a real disk as
real folder names. `partition_by_branch` builds a branch with `label=schema_id`
(`branch_situation.py:464`) and the label becomes the folder.

**THE NAMES ALREADY EXIST AND ARE SIMPLY NOT USED.** Every schema in the
recognition rules carries an authored `name` -- `academic` is `'Academic'`,
`nonprofit` is `'Nonprofit, civic and member organisations'` -- and `cli.py:18267`
already hands those names to site G so the MODEL reads a sentence rather than an
id. The person got the id and the model got the sentence. This inverts that.

**THE PARENTHETICAL IS A GLOSS AND IS NOT PART OF A NAME.** Several authored names
carry one: *"Business operations (the organisation's own running record)"*. It is
there to tell one schema from another on a MENU, and a folder called that is worse
than the id it replaces. The head of the name is the name.

**THIS IS NOT PHASE 3.** Phase 3 replaces the KIND with a LIFE as the partition
key -- `research` becomes Education. This changes nothing about which branch a
file lands in; it changes only what that branch is CALLED. The two compose: a life
is named by the owner's own word, and until Phase 3 lands a kind should at least
be spelled the way the library spells it.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from branch_situation import (  # noqa: E402
    folder_name_for_schema, partition_by_branch,
)

#: The authored names, verbatim from the shipped recognition rules, so the test
#: is about the product's own vocabulary and not about strings invented here.
AUTHORED = {
    "academic": "Academic",
    "research": "Research",
    "nonprofit": "Nonprofit, civic and member organisations",
    "business_operations":
        "Business operations (the organisation's own running record)",
    "creative": "Creative and media practice (the making record of a work)",
}


def test_a_branch_is_called_what_the_library_calls_it():
    """SABOTAGE: return the id. The owner's disk goes back to `nonprofit`."""
    assert folder_name_for_schema(AUTHORED["research"], "research") == "Research"
    assert folder_name_for_schema(AUTHORED["nonprofit"], "nonprofit") == (
        "Nonprofit, civic and member organisations")


def test_the_gloss_in_brackets_is_not_part_of_the_folders_name():
    """A menu line is not a folder name.

    SABOTAGE: use the whole authored string. The person gets a folder called
    `Business operations (the organisation's own running record)`, which is worse
    than `business_operations` -- it is long, it is a sentence, and it reads like
    documentation rather than a place to put things.
    """
    assert folder_name_for_schema(
        AUTHORED["business_operations"], "business_operations") == (
        "Business operations")
    assert folder_name_for_schema(AUTHORED["creative"], "creative") == (
        "Creative and media practice")


def test_a_schema_with_no_authored_name_keeps_its_id_rather_than_vanishing():
    """`104` §17.2 one more time: a gap in the vocabulary must never become a
    folder that has no name at all.

    SABOTAGE: return the authored value unguarded. A schema the rules carry no
    name for produces `None` or `''` as a folder name, and an unnamed folder is a
    crash at best and a file lost at worst.
    """
    for missing in (None, "", "   "):
        assert folder_name_for_schema(missing, "some_schema") == "some_schema"


def test_a_name_that_is_only_a_gloss_keeps_its_id():
    """Degenerate, and it must not produce an empty folder name.

    SABOTAGE: split on the bracket and return the head without checking it. A name
    authored as `"(see the other one)"` yields `''`.
    """
    assert folder_name_for_schema("(see the other one)", "odd") == "odd"


def _partition(*, name_of_schema, default_label="Typed", default_schema="academic"):
    """`partition_by_branch` over two files of two kinds, with every other input
    held at its most boring: the naming is the only thing under test."""
    return partition_by_branch(
        roster=(("f1", "h1"), ("f2", "h2")),
        default_label=default_label,
        default_situation=None,
        default_schema=default_schema,
        anchor_facts_of=lambda _f, _h: (),
        owner_of_term={},
        fields_of_schema=lambda _s: (),
        verdict_of=lambda _f, _h: None,
        # A NAMED SCHEMA THE LIBRARY CARRIES NO SITUATION FOR OPENS NOTHING --
        # `partition_by_branch`'s own rule, and returning `()` here made the first
        # cut of this test assert against an empty list. Two situations, so the
        # branch opens and is UNSETTLED, which is the ordinary case.
        situations_of=lambda _s: ("kind.one", "kind.two"),
        chosen_situation=lambda _scope: None,
        named_by_the_model={"f1": "academic", "f2": "research"},
        name_of_schema=name_of_schema,
    )


def test_the_partition_gives_an_opened_branch_a_human_folder_name():
    """The end of the wire: the branch site G opened is CALLED something a person
    would write, on the FOLDER.

    SABOTAGE: drop `display_name` from the `Branch(` in the non-default arm.
    Green above, red here, and the fix never reaches the disk.
    """
    partition = _partition(name_of_schema=AUTHORED.get)

    opened = [b for b in partition.branches if not b.is_default]
    assert opened, "site G named a second kind, so a branch was opened for it"
    for branch in opened:
        assert branch.folder_name == folder_name_for_schema(
            AUTHORED.get(branch.schema), branch.schema)
        assert branch.folder_name != branch.schema, (
            f"the folder for {branch.schema!r} is still its id")


def test_the_scope_key_is_untouched_and_that_is_the_whole_point():
    """**THE REGRESSION THIS FILE EXISTS TO PREVENT, and the lead caused it.**

    The first cut of this change put the authored name in `Branch.label`. But
    `Branch.scope` is `f"{SCOPE_BRANCH}:{self.label}"` -- the label is the key a
    branch's QUESTION is recorded at, the key `--answer situation:academic=...`
    matches on, and the key every answer already stored in a person's database is
    filed under. Renaming it broke the question-and-answer round trip across
    sixteen integration tests, and on a real database it would have silently
    orphaned every answer the person had ever given.

    A display string and a primary key are not the same thing even when they
    start out spelled the same.

    SABOTAGE: set `label=folder_name_for_schema(...)` again. Every other test in
    this file still passes and the product stops being able to hear the person.
    """
    partition = _partition(name_of_schema=AUTHORED.get)

    for branch in partition.branches:
        assert branch.scope.endswith(f":{branch.label}"), (
            "the scope is built from the label, so the label is a key")
        if branch.is_default:
            # The DEFAULT branch's key has always been the person's own typed
            # `--label`, or the schema id when they typed none. Untouched.
            continue
        assert branch.label == branch.schema, (
            f"the branch for {branch.schema!r} is keyed by something other than "
            "its id, and every answer already recorded against it is orphaned")


def test_the_persons_own_label_outranks_the_librarys_name():
    """A typed `--label` is the person's word, and §3.13's ordering is not
    negotiable about whose word wins.

    SABOTAGE: always use the library's name for the default branch. A person who
    typed `--label Coursework` gets a folder called `Academic`, which is the
    product overruling them about the name of their own folder.
    """
    partition = _partition(name_of_schema=AUTHORED.get,
                           default_label="Coursework")

    (default,) = [b for b in partition.branches if b.is_default]
    assert default.folder_name == "Coursework"


def test_the_schema_is_untouched_so_every_other_reader_still_works():
    """The LABEL is what a person reads; the SCHEMA is what the code joins on.

    SABOTAGE: rename `Branch.schema` too. Every applicability lookup, every
    `DOMAIN_FIELDS` join and P11's guards are keyed on the schema id, and a human
    name would match none of them -- the tree would be beautifully named and
    completely empty.
    """
    partition = _partition(name_of_schema=AUTHORED.get)

    assert {b.schema for b in partition.branches} <= {"academic", "research"}
    for branch in partition.branches:
        assert branch.schema.islower(), "the id stays the id"


def test_without_a_name_table_nothing_changes():
    """A caller that passes no names gets exactly today's behaviour.

    SABOTAGE: default `name_of_schema` to something that invents a name. Every
    caller that has not been taught about names -- tests, tools, an older
    composition root -- silently starts renaming the person's folders.
    """
    partition = _partition(name_of_schema=lambda _s: None)

    for branch in partition.branches:
        if not branch.is_default:
            assert branch.label == branch.schema
