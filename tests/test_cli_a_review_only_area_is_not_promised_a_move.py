# tests/test_cli_a_review_only_area_is_not_promised_a_move.py
"""`106` Phase 1.3: the screen stops promising a filing the apply step refuses.

**THE CONTRADICTION.** `PLACEMENT_WORDS[REVIEW_REQUIRED]` reads *"Ready for you
to approve, then file into {where}"*. A send into a residual area whose treatment
is `reviewed` records `REVIEW_REQUIRED` and a destination disposition that does
NOT move files (`placement/privacy.py:336`), and `mutation/plan.py:189` refuses
that write at apply. **Most shipped residual areas take this path**, so the
screen routinely promises a filing that cannot happen, and the person approves it
expecting a move.

**THE PRECEDENT THIS COPIES.** `104` R-92 already adjusts a heading conditionally
when a promise cannot be kept: *"'Once you say what these are' is a promise, and
it is kept only where the screen carries a gesture that reaches these files."*
Same shape, same reason, one more input -- the destination's own disposition,
which `placement.privacy.moves_files` already answers.

**BOTH DIRECTIONS ARE ASSERTED** or the fix becomes a heading that under-promises
everywhere, which is the mirror of the defect and just as dishonest.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import cli  # noqa: E402
from placement import vocabulary as pv  # noqa: E402


def test_a_review_required_placement_that_moves_says_it_will_file():
    """Unchanged where the promise is keepable.

    SABOTAGE: drop the disposition test and always use the cautious words. Every
    ordinary placement stops saying it will be filed, and the screen understates
    what approving actually does.
    """
    words = cli.placement_words(pv.REVIEW_REQUIRED, disposition="physical-destination")

    assert "file into" in words


def test_a_review_required_placement_that_does_not_move_does_not_say_it_will_file():
    """The defect, stated as an assertion.

    SABOTAGE: return `PLACEMENT_WORDS[policy]` regardless. Red here, and the
    screen goes back to telling a person that approving will file files that
    `mutation/plan.py` will then refuse to move.
    """
    words = cli.placement_words(pv.REVIEW_REQUIRED, disposition="review-only")

    assert "file into" not in words
    assert "{where}" in words, "the destination is still named -- `00`'s rule"

    # `leave-in-place` is the other disposition that does not move, and must
    # read the same: the person is approving a decision, not a movement.
    assert cli.placement_words(
        pv.REVIEW_REQUIRED, disposition="leave-in-place") == words


def test_an_unknown_disposition_keeps_the_ordinary_words():
    """A disposition this build does not recognise must not silently change what
    the screen promises.

    `104` §17.2's rule one more time: a gap in the vocabulary must never become a
    file that vanished, and it must not become a quietly different sentence
    either. `moves_files` RAISES on a value outside its closed set, so this is
    read defensively and falls back to the words that were always printed.

    SABOTAGE: let the raise escape. One unfamiliar disposition takes down the
    whole report.
    """
    words = cli.placement_words(pv.REVIEW_REQUIRED, disposition="not-a-real-word")

    assert words == cli.PLACEMENT_WORDS[pv.REVIEW_REQUIRED]


def test_no_disposition_recorded_keeps_the_ordinary_words():
    """A run written before dispositions existed reports as it always did."""
    words = cli.placement_words(pv.REVIEW_REQUIRED, disposition=None)

    assert words == cli.PLACEMENT_WORDS[pv.REVIEW_REQUIRED]


def test_the_other_policies_are_untouched():
    """Only the promise that was false is changed.

    SABOTAGE: apply the disposition test to every policy. `AUTO_ELIGIBLE` would
    stop saying it is ready to file, and `BLOCKED_PENDING_USER` would lose the
    sentence R-92 wrote for it.
    """
    for policy in (pv.AUTO_ELIGIBLE, pv.BLOCKED_PENDING_USER):
        assert cli.placement_words(policy, disposition="review-only") == (
            cli.PLACEMENT_WORDS[policy])


def test_an_unknown_policy_falls_back_rather_than_raising():
    """The call site's own rule, kept: "an unknown policy falls back to the
    outcome's word rather than to silence".

    SABOTAGE: subscript `PLACEMENT_WORDS[policy]` here. One run carrying a policy
    this build does not know takes down the whole report, and `104` §17.2's rule
    that a gap in the vocabulary never becomes a file that vanished is broken by
    the very function written to keep a screen honest.
    """
    assert cli.placement_words("a-policy-from-a-later-build",
                               disposition="review-only") is None
