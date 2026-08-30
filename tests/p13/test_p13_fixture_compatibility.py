"""Three parts guessed at P13's record before P13 published one. Report the gap.

`74` §6 A4's negative twin, and `74` §8 Q2. `tests/p9/p13_fixtures.py`,
`tests/p10/p13_fixtures.py` and `tests/p11/p13_fixtures.py` each publish a
`ReviewActionFixture` with a different field list and a different action
vocabulary, each correct in the vocabulary of the part that expects to RECEIVE
the action. Only P11's matches the SPEC.

This is the same shape as the `scan_state` defect `69` §2 records -- two parts,
two spellings of one thing, each correct in its own vocabulary, both green -- and
it will bite the same way when P13's record reaches a receiver.

**The test's NAME states the finding; its BODY asserts the state that would close
it.** So it fails, is marked `xfail(strict=True)`, and the suite stays green while
the failure stays visible with its lists printed. It is a real negative twin in
both directions:

* Widening `review_surface.vocabulary.ACTIONS` to absorb P9's or P10's names, or
  narrowing theirs, would make it XPASS -- and a strict xfail that passes FAILS
  the suite, so the sabotage cannot land quietly.
* Deleting the fixtures would make it ERROR rather than xfail, which also fails.

DO NOT "fix" it. Reconciling four vocabularies is the owner's decision (`74` §8
Q2): widening P13's set, narrowing P9's and P10's, and writing a translation
table are three different products.
"""
from __future__ import annotations

import ast
import dataclasses
import pathlib
import sys

import pytest

from review_surface.records import ReviewAction
from review_surface.vocabulary import ACTIONS

TESTS = pathlib.Path(__file__).resolve().parent.parent
if str(TESTS) not in sys.path:  # pragma: no cover - import-path plumbing
    sys.path.insert(0, str(TESTS))


def _actions_in(module) -> tuple[str, ...]:
    """The action vocabulary a fixture module publishes, or the one it uses.

    P10 publishes no tuple at all -- its action names live only as keyword
    literals inside its factory functions -- and that absence is itself part of
    the report, so it is read out of the source rather than papered over with a
    hand-copied list that would rot.
    """
    for name in ("REVIEW_ACTIONS", "ACTIONS"):
        published = getattr(module, name, None)
        if published is not None:
            return tuple(published)
    tree = ast.parse(pathlib.Path(module.__file__).read_text())
    used = {keyword.value.value
            for node in ast.walk(tree) if isinstance(node, ast.Call)
            for keyword in node.keywords
            if keyword.arg == "action" and isinstance(keyword.value, ast.Constant)}
    return tuple(sorted(used))


def _gap(module) -> tuple[list[str], list[str]]:
    """(fields P13 cannot supply, actions P13 does not publish)."""
    ours = {field.name for field in dataclasses.fields(ReviewAction)}
    theirs = {field.name
              for field in dataclasses.fields(module.ReviewActionFixture)}
    return sorted(theirs - ours), sorted(set(_actions_in(module)) - set(ACTIONS))


@pytest.mark.xfail(strict=True, reason=(
    "P9, P10 and P11 each built a P13 review_action fixture before P13 "
    "published one. Four vocabularies disagree and the reconciliation is the "
    "owner's, not a plan author's -- see 74 §8 Q2. The failure message prints "
    "the exact fields and actions each fixture asks for and P13 does not supply."))
def test_the_three_shipped_fixtures_cannot_supply_p13s_record():
    from p9 import p13_fixtures as p9
    from p10 import p13_fixtures as p10
    from p11 import p13_fixtures as p11

    report = {"P9": _gap(p9), "P10": _gap(p10), "P11": _gap(p11)}
    assert report == {"P9": ([], []), "P10": ([], []), "P11": ([], [])}, report


def test_the_report_is_over_the_three_fixtures_that_actually_ship():
    """The xfail above would also 'pass' by importing nothing. Pin the inputs
    separately, outside the xfail, so an ImportError cannot masquerade as the
    known disagreement."""
    from p9 import p13_fixtures as p9
    from p10 import p13_fixtures as p10
    from p11 import p13_fixtures as p11

    for module in (p9, p10, p11):
        assert dataclasses.is_dataclass(module.ReviewActionFixture)
        assert _actions_in(module), f"{module.__name__} names no action at all"


def test_p11s_fixture_is_the_one_that_matches_and_the_other_two_do_not():
    """Which of the three agrees with the SPEC is the whole shape of the
    decision, so it is asserted rather than left in a comment."""
    from p9 import p13_fixtures as p9
    from p10 import p13_fixtures as p10
    from p11 import p13_fixtures as p11

    assert _gap(p11) == ([], [])
    assert _gap(p9) != ([], [])
    assert _gap(p10) != ([], [])
