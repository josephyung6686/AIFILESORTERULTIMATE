"""A fact the files named keeps the folder the person already made.

The document may spell that fact however it spells it. The folder they made
is the home. Files loose at the top of the scan are not a folder they made.
A kind of work is whichever closed vocabulary the catalogue calls a kind,
on any machine, and a name is any other field.
"""
from facts.states import PROPOSAL_ELIGIBLE_STATES, STRENGTH_ORDER
from tree_design.pipeline import (
    field_that_divides_a_folder, folder_a_course_already_sits_in,
    kinds_a_folder_already_separated, values_strong_enough_to_name_a_folder,
    values_that_divide_a_folder,
)


def test_every_file_of_a_course_in_one_nested_folder_names_that_folder():
    home = folder_a_course_already_sits_in(
        ("/disk/Desktop/Python 1006", "/disk/Desktop/Python 1006"),
        {"/disk/Desktop/Python 1006": "/disk/Desktop/Python 1006"})
    assert home == "/disk/Desktop/Python 1006"


def test_a_course_split_across_two_folders_is_not_either_of_them():
    assert folder_a_course_already_sits_in(
        ("/disk/Desktop/Python 1006", "/disk/Downloads"),
        {"/disk/Desktop/Python 1006": "/disk/Desktop/Python 1006",
         "/disk/Downloads": "/disk/Downloads"}) is None


def test_two_files_that_share_a_kind_of_work_separate_and_one_file_does_not():
    assert kinds_a_folder_already_separated(
        {"a": "lecture", "b": "lecture", "c": "exam"}) == ("lecture",)
    assert kinds_a_folder_already_separated({"a": "lecture"}) == ()


def test_a_dump_at_the_top_of_the_scan_is_not_a_course_folder():
    assert folder_a_course_already_sits_in(
        ("/disk/Downloads", "/disk/Downloads"),
        {"/disk/Desktop/Python 1006": "/disk/Desktop/Python 1006"}) is None


def test_a_value_every_file_in_the_folder_carries_does_not_become_a_folder():
    assert values_that_divide_a_folder(
        {"a": "lecture", "b": "lecture"}, files_in_folder=2) == ()


def test_a_value_two_files_share_that_leaves_another_file_out_does():
    assert values_that_divide_a_folder(
        {"a": "lecture", "b": "lecture", "c": "exam"}, files_in_folder=3) == (
            "lecture",)


def test_a_kind_of_work_divides_a_folder_ahead_of_a_name():
    assert field_that_divides_a_folder(
        {"name": {"a": "one-spelling", "b": "one-spelling", "c": "other"},
         "kind": {"a": "notes", "b": "notes"}},
        files_in_folder=3, kinds=("kind",)) == "kind"


def test_two_kinds_that_cover_the_same_files_are_not_a_guess():
    assert field_that_divides_a_folder(
        {"left": {"a": "one", "b": "one"},
         "right": {"a": "two", "b": "two"}},
        files_in_folder=3, kinds=("left", "right")) is None


def test_a_name_divides_a_folder_when_no_kind_of_work_does():
    assert field_that_divides_a_folder(
        {"name": {"a": "alpha", "b": "alpha"}},
        files_in_folder=3, kinds=()) == "name"


def test_a_name_already_absorbed_into_the_folder_is_not_split_back_out():
    assert field_that_divides_a_folder(
        {"name": {"a": "alpha", "b": "alpha"}},
        files_in_folder=3, kinds=(),
        absorbed=(("name", "alpha"),)) is None


def test_a_clue_too_weak_to_be_a_fact_does_not_name_a_folder():
    weak = STRENGTH_ORDER[0]
    kept = PROPOSAL_ELIGIBLE_STATES[0]
    assert values_strong_enough_to_name_a_folder({
        "a": {"canonical_value": "a title the model guessed",
              "reliability_state": weak},
        "b": {"canonical_value": "a title the model guessed",
              "reliability_state": weak},
        "c": {"canonical_value": "lecture", "reliability_state": kept},
        "d": {"canonical_value": "lecture", "reliability_state": kept},
    }) == {"c": "lecture", "d": "lecture"}


def test_a_kind_of_work_still_divides_when_a_parallel_folder_used_that_name():
    assert field_that_divides_a_folder(
        {"kind": {"a": "notes", "b": "notes"}},
        files_in_folder=3, kinds=("kind",),
        absorbed=(("kind", "notes"),)) == "kind"
