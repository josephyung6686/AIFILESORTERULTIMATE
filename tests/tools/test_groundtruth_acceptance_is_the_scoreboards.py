# tests/tools/test_groundtruth_acceptance_is_the_scoreboards.py
"""`104` SF-3: a scoreboard run accepts its own groups, and the scorecard says so.

Since SF-3 a group is a draft until somebody decides it, and a run that decides
nothing places nothing. A scoreboard has nobody at the screen. So it must either
make the gesture itself or measure a product that files no file, and the first is
the honest one -- but only if the record says who made it.

The labels are what makes it defensible: `tools/groundtruth/labels.py` reads a
file the owner wrote by hand saying where each file belongs, so what the harness
supplies is the ACT and not the opinion. The act still has to be attributable,
and `DECIDED_BY` has no word for a measuring harness. That gap is the strict xfail
at the bottom, and until it closes the scorecard's own header carries the sentence
instead.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from grouping.vocabulary import DECIDED_BY, RULES, USER, VALIDATOR  # noqa: E402
from tools.groundtruth import _one_run  # noqa: E402
from tools.groundtruth.report import ACCEPTANCE_NOTE, measured_under  # noqa: E402


def test_the_harness_makes_the_gesture_through_the_flag_a_person_types(
        monkeypatch, tmp_path):
    """The acceptance is an ARGUMENT of the run, not a back door into its database.

    `_one_run` builds one argv and hands it to `cli.main`; that is the whole of the
    harness's authority over a run, and the accept has to be inside it or it is not
    the gesture a person makes. Asserted on the argv rather than on the flag's
    effect, because the effect is `cli`'s to test and this file's question is
    whether the harness asked for it out loud.
    """
    seen: dict[str, object] = {}

    class _Fake:
        LOCAL_MODEL_TIMEOUT_SECONDS = 1.0
        PER_FILE_LOCAL_CALL_SITES = ("a", "b")

        @staticmethod
        def main(argv, out=None, file_ceiling_seconds=None):
            seen["argv"] = list(argv)
            return 0

    monkeypatch.setitem(sys.modules, "cli", _Fake)
    report = tmp_path / "report.txt"
    _one_run.main([str(tmp_path), "academic.coursework", "Coursework",
                   str(tmp_path / "db.sqlite"), str(report)])

    assert "--accept-groups" in seen["argv"]
    # And the harness's own name is on the run, which is the one place the record
    # today can say the acting party was not a person.
    from tools.groundtruth.reuse import SCOREBOARD_USER
    assert SCOREBOARD_USER in seen["argv"]


def test_the_scorecard_says_the_scoreboard_accepted_and_not_a_person():
    """One line in the header, printed whether or not anything else was recorded.

    Beside the semantic setting and the prompt rows, for the same reason both of
    those are there: a number nobody can say what was true when it was measured is
    a number nobody can compare. An absent line here would leave a reader assuming
    the groups these placements rest on had been reviewed.
    """
    printed = measured_under(None)

    assert list(ACCEPTANCE_NOTE) == printed[-len(ACCEPTANCE_NOTE):]
    header = " ".join(printed)
    assert "accepted by the scoreboard" in header
    assert "not by a person" in header
    # The gap is named on the scorecard too, not only in the source: a reader of
    # the row sees `decided_by=user` and must be able to find out why.
    assert "--accept-groups" in header
    assert f"decided_by={USER}" in header


def test_decided_by_has_a_word_for_the_scoreboard():
    """THE OWED VOCABULARY MEMBER. Strict xfail: it fails the day it is ratified.

    `DECIDED_BY` is a closed set of three, and a scoreboard is none of them.
    `rules` is the engine deciding for the person, which is exactly what SF-3
    removed; `validator` is P8's judgement over a model claim and no model is
    involved; `user` is what the row says today and it is the false one -- no
    person reviewed these groups, and a replay, an audit log and P13 all read that
    column back.

    A member of a closed vocabulary is the owner's to ratify (`81` §14.1: "they are
    not minted by whoever notices the gap"), so this test names the gap rather than
    filling it. WHAT IS BEING ASKED FOR: one member of
    `grouping.vocabulary.DECIDED_BY` meaning "a measuring harness acted here, under
    labels a person wrote, and no person reviewed this group". The spelling is the
    owner's.

    Until then `report.ACCEPTANCE_NOTE` carries the sentence on every scorecard and
    the event's `user_id` is `groundtruth`, which is the only part of the record
    that is true about who acted.
    """
    assert set(DECIDED_BY) != {USER, RULES, VALIDATOR}


test_decided_by_has_a_word_for_the_scoreboard = pytest.mark.xfail(
    strict=True,
    reason="`104` SF-3: DECIDED_BY has three members and none of them is a "
           "measuring harness, so the scoreboard's acceptance is recorded as "
           "`user`. A member is the owner's to ratify; the scorecard says so in "
           "the meantime.",
)(test_decided_by_has_a_word_for_the_scoreboard)
