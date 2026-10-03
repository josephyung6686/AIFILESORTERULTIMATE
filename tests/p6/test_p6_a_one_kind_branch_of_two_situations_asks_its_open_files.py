# tests/p6/test_p6_a_one_kind_branch_of_two_situations_asks_its_open_files.py
"""A one-kind life branch whose files carry two situations still asks its kind's
question of the files nothing has answered.

Measured on a 33-file Desktop: Photos and Media held 17 `photos` files, six named
`photos.screenshot-captures`, one `photos.scanned-documents`, ten named nothing
(text-less captures are settled by kind and not asked, `00` 13 Sep item 5).
`_asked_of_a_life` offers no branch question when the files carry two
situations -- true of the BRANCH -- and `_each_kinds_question_under` asked each
kind's question only on a branch of two kinds. So the ten files had no
situation, no question and no way out, while the screen said "the question for
its branch is printed below". `00` amendment 1 of 14 Sep: the person is asked
only where the judge cannot -- and IS asked there.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from branch_situation import Branch  # noqa: E402
from cli import kinds_asked_one_by_one  # noqa: E402


def _branch(schemas, *, candidates=(), default=False):
    return Branch(label="Photos and Media", life="Photos and Media",
                  schemas=tuple(schemas), situations=(), situation=None,
                  is_default=default, anchor_file_ids=(), file_ids=("a", "b"),
                  candidate_situations=tuple(candidates))


def test_one_kind_carrying_two_situations_is_asked_its_kinds_question():
    assert kinds_asked_one_by_one(_branch(("photos",))) == ("photos",)


def test_two_kinds_are_asked_one_by_one_as_before():
    assert kinds_asked_one_by_one(_branch(("academic", "research"))) == (
        "academic", "research")


def test_a_branch_with_its_own_question_is_not_asked_per_kind():
    assert kinds_asked_one_by_one(_branch(
        ("photos",), candidates=("photos.a", "photos.b"))) == ()


def test_the_default_branch_is_not_asked_here():
    assert kinds_asked_one_by_one(_branch(("photos",), default=True)) == ()
