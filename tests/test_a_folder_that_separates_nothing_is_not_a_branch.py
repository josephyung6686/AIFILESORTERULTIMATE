# tests/test_a_wrapper_folder_is_not_a_top_level_folder.py
"""The owner, 18 Sep 2026: *"make sure no single file root and stuff happens."*

**WHAT THEY SAW.** Seven top-level folders over 371 files, and one of them was a
single file's own name -- a document at the top of the tree wearing a folder's
clothes, beside `research` and `career`.

**WHERE IT COMES FROM, and it is not the tree designer.** `adopted_folders` offers
every row of the directory inventory that has a parent, is not sealed, and is not
a candidate root, with no test of what the directory CONTAINS.

**THE FIRST RULE THE LEAD WROTE WAS WORSE THAN THE DEFECT.** It was "a directory
is a branch only if it holds two or more files or a subdirectory", and
`tests/test_cli.py`'s everyday corpus is `Screenshots/` with one file, `Memes/`
with one file, and a loose note. It deleted both of the person's own folders from
their own proposal and the report lost its folder section. `00`:98 is explicit
that "a two-file packet may remain a single folder", and one file is that same
argument one step further down. **A one-file folder is not the problem.**

**THE WRAPPER IS.** A directory holding exactly one file, no subdirectory, and
carrying THAT FILE'S OWN NAME -- `foo/foo.pdf` -- says nothing the file does not
already say. Promoting it tells the person the product found a category when it
found a filename.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from cli import folders_that_separate_nothing  # noqa: E402
from tree_design.upstream import ExistingFolder  # noqa: E402


def _folder(path, *, files, parent="/corpus"):
    return ExistingFolder(directory_path=path, parent_directory=parent,
                          file_count=files, curation_signal="undetermined")


def _holding(**by_path):
    """`only_file_in`, from a plain map of directory basename -> filename."""
    return lambda path: by_path.get(path)


def test_a_folder_named_after_the_one_file_inside_it_is_a_wrapper():
    """The defect, stated as an assertion.

    SABOTAGE: return an empty set. The owner's tree goes back to having a single
    document as a top-level folder.
    """
    got = folders_that_separate_nothing(
        (_folder("/corpus/report", files=1),),
        only_file_in=_holding(**{"/corpus/report": "report.pdf"}))

    assert got == frozenset({"/corpus/report"})


def test_a_folder_holding_one_file_of_a_different_name_is_kept():
    """**THE REGRESSION THE FIRST RULE CAUSED, pinned so it cannot come back.**

    `Screenshots/` holding one screenshot is a folder the person made, named, and
    expects to see. It is not a wrapper -- the folder says something the file does
    not.

    SABOTAGE: drop the name comparison and test only `file_count == 1`. Red here,
    and the product deletes the person's own folders from their own proposal --
    which is what the lead shipped for ten minutes on 18 Sep.
    """
    got = folders_that_separate_nothing(
        (_folder("/corpus/Screenshots", files=1),
         _folder("/corpus/Memes", files=1)),
        only_file_in=_holding(**{
            "/corpus/Screenshots": "Screenshot 2026-08-14 at 11.03.47.png",
            "/corpus/Memes": "drake-format.jpg"}))

    assert got == frozenset()


def test_the_match_ignores_case_and_the_extension():
    """`Foo/foo.PDF` is the same accident as `foo/foo.pdf`.

    SABOTAGE: compare the raw strings. An unzip that title-cased the directory
    walks straight through.
    """
    got = folders_that_separate_nothing(
        (_folder("/corpus/Foo", files=1),),
        only_file_in=_holding(**{"/corpus/Foo": "foo.PDF"}))

    assert got == frozenset({"/corpus/Foo"})


def test_a_wrapper_that_also_holds_a_subfolder_is_kept():
    """Depth is structure even when breadth is not.

    SABOTAGE: test only the name. A hand-built hierarchy whose top level happens
    to hold one like-named file loses its top.
    """
    got = folders_that_separate_nothing(
        (_folder("/corpus/thesis", files=1),
         _folder("/corpus/thesis/chapters", files=8, parent="/corpus/thesis")),
        only_file_in=_holding(**{"/corpus/thesis": "thesis.pdf"}))

    assert got == frozenset()


def test_a_folder_of_several_files_is_never_a_wrapper():
    """SABOTAGE: drop the `file_count != 1` guard. A real folder that happens to
    contain a like-named file -- `Invoices/invoices.csv` beside nine others --
    disappears."""
    got = folders_that_separate_nothing(
        (_folder("/corpus/invoices", files=10),),
        only_file_in=_holding(**{"/corpus/invoices": "invoices.csv"}))

    assert got == frozenset()


def test_an_unreadable_directory_is_kept_rather_than_dropped():
    """A directory whose contents this run cannot name is NOT a wrapper.

    `104` §17.2: a gap in what the run knows must never become something the
    person loses. The safe direction here is to keep the folder.

    SABOTAGE: treat `None` as a match. Any directory the file rows do not cover --
    a partial scan, a rename mid-run -- is silently removed from the proposal.
    """
    got = folders_that_separate_nothing(
        (_folder("/corpus/mystery", files=1),),
        only_file_in=lambda _path: None)

    assert got == frozenset()


def test_it_answers_about_folders_only_and_never_about_files():
    """The contract that keeps `104` §17.2 true.

    SABOTAGE: have it return file ids. A wrapper stops being a branch AND its file
    stops being placed, which is the one outcome worse than the defect.
    """
    folders = (_folder("/corpus/report", files=1),
               _folder("/corpus/real", files=5))

    got = folders_that_separate_nothing(
        folders, only_file_in=_holding(**{"/corpus/report": "report.pdf"}))

    assert got <= {f.directory_path for f in folders}
    assert all(isinstance(path, str) for path in got)


# --- the PASS-THROUGH, which is the shape actually on the owner's disk ---------


def test_a_pass_through_folder_is_KEPT_and_here_is_why():
    """**THE CORRECTION, and the measurement that forced it.**

    The owner's one `existing` root holds `file_count=0, subdirectory_count=1`.
    That looked like the obvious third shape -- a pass-through adds a level and
    divides nothing -- and the lead refused it.

    `Uni/` holding `PHYS1401` is the same shape. It is a person's own category
    with one course in it so far, and
    `test_an_adopted_folder_enters_as_the_persons_folder_not_as_a_proposal` exists
    to stop precisely that nesting being flattened. Nothing in the structure tells
    a download's leftovers from a category with one thing in it -- only the person
    can. So the product keeps both, and folding a chain that divides nothing is
    `106` Phase 7's depth rule, beneath a built node where a folded value still
    has a chain to reach it (`104` Q-H), not here.

    SABOTAGE: refuse `here <= 1`. `Uni/` disappears and the person's own two-level
    filing is flattened into one.
    """
    got = folders_that_separate_nothing(
        (_folder("/corpus/Uni", files=0),
         _folder("/corpus/Uni/PHYS1401", files=6, parent="/corpus/Uni")),
        only_file_in=lambda _p: None)

    assert got == frozenset(), "a person's own nesting is theirs to keep"


def test_a_folder_with_no_files_but_several_subfolders_is_a_branch():
    """`Photos/` holding `2019/`, `2020/`, `2021/` divides, so it stays.

    SABOTAGE: refuse every directory with no files of its own. Every intermediate
    level of a hand-built hierarchy vanishes and the tree flattens to its leaves.
    """
    got = folders_that_separate_nothing((
        _folder("/corpus/Photos", files=0),
        _folder("/corpus/Photos/2019", files=4, parent="/corpus/Photos"),
        _folder("/corpus/Photos/2020", files=7, parent="/corpus/Photos"),
    ), only_file_in=lambda _p: None)

    assert "/corpus/Photos" not in got


def test_an_empty_folder_with_no_children_is_not_a_branch():
    """Nothing in it and nothing under it.

    SABOTAGE: keep it. Every empty directory on the disk becomes a proposed root.
    """
    got = folders_that_separate_nothing(
        (_folder("/corpus/empty", files=0),), only_file_in=lambda _p: None)

    assert got == frozenset({"/corpus/empty"})
