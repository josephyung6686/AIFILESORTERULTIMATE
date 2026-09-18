# tests/p6/test_p6_no_situation_arm_withholds_group_levels.py
"""`00` amendment 15 of 17 Sep: the no-situation arm stops asking group-level
questions.

**THE WITHDRAWAL, AND THE DOOR IT LEFT OPEN.** `00`:11.2 step 2 withdrew the
per-file `school` question: `school` is a GROUP-level field -- it is settled from
the anchor of a group, not from one file -- and asking one file for it invites a
guess from a filename. The per-situation arm honours that: `open_question`
narrows to the situation's own `folder_levels`, and `anchor_only_levels` restores
a group-level field only where the file's settled `work_type` makes it an anchor.

The no-situation arm did not. When site G named no situation, `folder_levels` is
`None` and the whole pending allowlist was asked flat, with nothing stripped --
so the withdrawn question was asked anyway, guarded by one sentence of prose in
rule 12 of the fact template.

**IT WAS NOT THEORETICAL.** `104` §18.100, measured on the owner's corpus:
`target_school` is bound as a folder level in **0 of 208 situations**, so no
per-situation door can ask for it -- and **7 files carry it**. They can only have
come through this arm.

The owner ruled on it: *"Close it -- respect the withdrawal."*

WHY A PARAMETER AND NOT A LOOKUP HERE. `open_question` is a pure function; every
library question it needs is resolved by its caller and handed in, which is how
`folder_levels` already arrives. Reaching into the catalogue from inside it would
give this one function a second way to learn the same thing, and the two would
drift. The caller knows the active schemas; it passes what they withhold.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from llm_harness.records import FolderLevel  # noqa: E402
from model_facts import open_question  # noqa: E402


def test_the_no_situation_arm_does_not_offer_a_group_level_field():
    """The amendment, at its smallest.

    SABOTAGE: drop the strip from the `folder_levels is None` arm. `school` is
    offered again to every academic-active file whose situation is open, which is
    the question `00`:11.2 step 2 withdrew, and the only thing left guarding it is
    prompt prose -- which is what failed.
    """
    vocabulary, levels = open_question(
        pending=("subject", "school", "work_type"),
        folder_levels=None,
        group_level=("school",))

    assert "school" not in vocabulary, (
        "the withdrawn per-file school question is being asked through the "
        "no-situation arm, which is `104` §18.100's measured finding")
    assert set(vocabulary) == {"subject", "work_type"}
    assert levels == ()


def test_the_other_fields_still_reach_the_no_situation_question():
    """Stripping one field must not empty the question.

    The arm exists because a file whose schema is known and whose situation is
    open used to be asked NOTHING and came out with an empty facts column. Closing
    the group-level door must not reopen that.

    SABOTAGE: return `()` from the arm instead of the narrowed tuple. Red here.
    """
    vocabulary, _levels = open_question(
        pending=("subject", "work_type", "artifact_type"),
        folder_levels=None,
        group_level=("school",))

    assert set(vocabulary) == {"subject", "work_type", "artifact_type"}


def test_a_settled_group_level_field_is_withheld_too():
    """`settled` is concatenated into the question, so it is a second door in.

    SABOTAGE: strip only `pending`. A `school` the rules had already written would
    be re-opened to the model per file, which is the same withdrawn question
    wearing the re-ask clothes `104` §18.2 gap 1 put on for the RIGHT fields.
    """
    vocabulary, _levels = open_question(
        pending=("subject",),
        folder_levels=None,
        settled=("school",),
        group_level=("school",))

    assert "school" not in vocabulary
    assert set(vocabulary) == {"subject"}


def test_the_per_situation_arm_is_untouched_by_this():
    """The narrowing that already worked keeps working, and is not narrowed twice.

    A situation's own `folder_levels` is the authority in that arm -- if a
    situation binds a group-level field as one of ITS levels, that is the library
    saying this situation builds that level, and `anchor_only_levels` is the seam
    that decides whether this FILE may answer it. This function must not
    second-guess that.

    SABOTAGE: apply the strip in both arms. Red here, and the product stops being
    able to build a school level at all.
    """
    levels = (FolderLevel(field="school", label="My school",
                          requirement="required"),
              FolderLevel(field="subject", label="Course",
                          requirement="required"))

    vocabulary, shown = open_question(
        pending=("school", "subject"),
        folder_levels=levels,
        group_level=("school",))

    assert "school" in vocabulary, (
        "the per-situation arm narrows by the situation's own levels and this "
        "amendment is about the arm that has none")
    assert shown == levels


def test_withholding_nothing_is_the_default_and_changes_no_caller():
    """Every existing call passes no `group_level` and must behave as before.

    SABOTAGE: make the parameter required. Every caller in the product and the
    suite breaks at once, which is a signature change wearing a ruling's clothes.
    """
    vocabulary, _levels = open_question(
        pending=("subject", "school"),
        folder_levels=None)

    assert set(vocabulary) == {"subject", "school"}


def test_the_library_names_the_fields_the_no_situation_arm_withholds():
    """`00` amendment 15's other half: WHICH fields, asked of the library.

    The per-situation arm asks `group_level_fields_for(catalogue, situation)`,
    which needs a situation. This arm has none by definition, so the honest answer
    is the UNION: a field some situation fills from its group is not a field to ask
    one file for when nobody knows which situation the file is in.

    Conservative on purpose. Withholding a field that some OTHER situation treats
    as per-file costs one unasked question; asking a group-level field costs a
    `school` guessed off a filename, which `104` R-95 measured as 38 facts on 52
    files, "every one a `school`, most of them filenames".

    SABOTAGE: hand back every field, or an empty set. The first re-opens the
    withdrawn question; the second silently stops asking anything group-level in
    the per-situation arm's sibling, which is a fact nobody writes.
    """
    from production import (
        group_level_fields_for_schema, load_shipped_catalogue,
        read_packaged_library_file,
    )

    catalogue = load_shipped_catalogue(read_packaged_library_file)
    fields = group_level_fields_for_schema(catalogue, "academic")

    assert isinstance(fields, frozenset)
    assert fields, (
        "`academic` is the one schema `GROUP_LEVEL_ROLES` binds a group-level "
        "role for -- `holder_institution` -- so an empty answer means the roles "
        "were not resolved through `role_bindings` at all")
    assert "subject" not in fields, (
        "`subject` is the file's own level in every situation that carries it; "
        "withholding it would empty the question this arm exists to ask")


def test_a_schema_that_declares_no_group_level_role_withholds_nothing():
    """THE SCOPE IS THE SCHEMA'S, NOT THE LIBRARY'S (18 Sep 2026).

    Until today this was a union over every role in `GROUP_LEVEL_ROLES` matched
    across every applicability row in the library. `holder_institution` is bound
    to `lab` on research rows and to `school` on academic ones, and only
    `academic` declares it group-level -- so the union withheld `lab` from every
    research file to prevent a harm (`104` R-95's `school` guessed off a filename)
    that only exists under `academic`.

    `tests/integration/test_a_silent_file_is_asked_and_filed_under_one_situation`
    caught it: a silent file must be offered EVERY field its voted schema
    declares, and `lab` is one of `research`'s. With `subject` reaching 35 of 371
    files (`104` §18.108), a question withheld for nothing is a fact not written.

    SABOTAGE: drop the `GROUP_LEVEL_ROLES.get(schema)` gate and take the union
    again. Red here, and every research file goes back to being unable to say
    which lab it belongs to.
    """
    from production import (
        group_level_fields_for_schema, load_shipped_catalogue,
        read_packaged_library_file,
    )

    catalogue = load_shipped_catalogue(read_packaged_library_file)

    assert group_level_fields_for_schema(catalogue, "research") == frozenset(), (
        "`research` declares no group-level role, so the no-situation arm has "
        "nothing to withhold from it")
    assert "lab" not in group_level_fields_for_schema(catalogue, "research")
    # And the strip that the ruling's own evidence is about still happens.
    assert "school" in group_level_fields_for_schema(catalogue, "academic")
