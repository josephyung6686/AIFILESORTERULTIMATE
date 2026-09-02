# tests/p15/test_p15_effects_composition.py
"""§17 asked of the COMMAND: does correcting an answer show a person anything?

    When a user edits or re-runs a structural answer, the product creates a draft
    plan version. It shows a meaningful diff. (`66` §17:576-582)

`tests/p15/test_p15_plan_effects.py` proves `questions.effects` thoroughly against
answers it writes itself. `src/cli.py` imports the module not at all.

So today `--answer` supersedes a row, the run comes out different, and nothing
anywhere says what the correction did. `effects.py` opens with that sentence about
itself, and `61` A.5 states the stake: "An answer that quietly rewrote a tree the
user could not trace is the defect this whole design exists to avoid."

**Only two of the module's three entry points are held here, and the split is the
finding.** `changed_answer` and `diff_for_answer_change` need nothing but P15's
own rows: the diff answers three of §17's six questions and NAMES the other three
with the reason each has no producer, which is the "nothing is silently omitted"
posture rather than a short list. `draft_for_answer_change` needs P10's
`open_draft`, and `85` §4.2 has already ruled why that cannot be called yet --
`_open_first_draft` opens an EMPTY draft, so a diff of first against last reports
every node as added. The draft half stays correctly dormant; the diff half is a
promise with no caller, and this file is about the diff half only.

Measured 2026-09-02 with PATCH C applied to a copy of `cli.py`. Answering a branch
question, then answering it differently, prints:

    What changing branch:Coursework does to this plan:
      Templates affected: keep-as-it-is, school>term>subject>work_type
      Coursework may need looking at again.
      Not worked out here, and why:
        placement_proposals: P11 owns placement. ...
        protected_area_change: Nothing records a protected AREA yet. ...
        filing_policy_paused: No filing policy has a producer. ...

The wiring is `src/cli.py`'s and is held for its owner as PATCH C.
"""
from __future__ import annotations

import io
import sys
from pathlib import Path

import pytest

from database_agent.db import open_database
from questions.effects import NOT_COMPUTED_BECAUSE, changed_answer
from questions.store import open_questions

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

import cli  # noqa: E402

CORPUS: dict[str, str] = {
    "PHYS 1401 syllabus.txt": "PHYS 1401 Syllabus\n\nSpring 2026. Instructor.\n",
}


def _corpus(tmp_path: Path) -> tuple[Path, Path]:
    corpus = tmp_path / "corpus"
    corpus.mkdir(parents=True, exist_ok=True)
    for name, text in CORPUS.items():
        (corpus / name).write_text(text, encoding="utf-8")
    return corpus, tmp_path / "plan.sqlite"


def _run(corpus: Path, database: Path, *extra: str) -> tuple[int, str]:
    out = io.StringIO()
    code = cli.main(
        [str(corpus), "--situation", "academic.coursework", "--label", "Coursework",
         "--user", "jy", "--database", str(database), *extra], out=out)
    return code, out.getvalue()


def _corrected(tmp_path: Path) -> tuple[Path, Path, str, str, list[str]]:
    """A run, an answer, and then a DIFFERENT answer to the same question.

    §17's trigger is "edits or re-runs", and `changed_answer` returns `None` for a
    first answer on purpose -- so a test that answered once would be measuring the
    case the module deliberately says nothing about.
    """
    corpus, database = _corpus(tmp_path)
    _run(corpus, database)
    question = open_questions(open_database(database))[0]
    options = [option.option_id for option in question.options]
    assert len(options) >= 2, "this question offers no correction to make"
    _run(corpus, database, "--answer", f"{question.question_id}={options[0]}")
    return corpus, database, question.question_id, question.scope, options


def test_correcting_an_answer_says_what_the_correction_did(tmp_path: Path):
    """§17:577's diff, on the invocation that makes the change.

    On this invocation and not the next one, for the reason `apply_answers`
    already gives about itself: a person who has just corrected something should
    not have to run the command again to find out what they corrected.
    """
    corpus, database, question_id, scope, options = _corrected(tmp_path)
    code, printed = _run(corpus, database,
                         "--answer", f"{question_id}={options[1]}")
    assert code == 0
    assert options[0] in printed and options[1] in printed, (
        "neither the shape being left nor the one being taken is named")


test_correcting_an_answer_says_what_the_correction_did = pytest.mark.xfail(
    strict=True,
    reason="measured 2026-09-02: `src/cli.py` imports `questions.effects` not at "
           "all, so `--answer` supersedes a row and the run simply comes out "
           "different. XPASSes -- and fails the suite, forcing this marker off -- "
           "with PATCH C in the reachability agent's CLI-PATCH.txt.",
)(test_correcting_an_answer_says_what_the_correction_did)


def test_the_three_questions_p15_cannot_answer_are_named_and_not_dropped(
        tmp_path: Path):
    """The half that makes the diff honest rather than merely present.

    §17 asks six questions and P15 can produce three. A diff that printed the
    three it has would read as a complete account of the consequences, and a
    person would act on it. `PlanEffectDiff` carries the other three as an
    explicit `None` with a reason each, and `is_empty`'s own docstring refuses to
    be read as "the answer had no effect" for exactly this reason -- so the
    reasons have to reach the screen too.
    """
    corpus, database, question_id, scope, options = _corrected(tmp_path)
    _, printed = _run(corpus, database, "--answer", f"{question_id}={options[1]}")
    for name in NOT_COMPUTED_BECAUSE:
        assert name in printed, (
            f"§17's {name!r} is neither computed nor named, so the diff reads as "
            f"a complete list of what the correction did")


test_the_three_questions_p15_cannot_answer_are_named_and_not_dropped = (
    pytest.mark.xfail(
        strict=True,
        reason="no diff is printed at all, so nothing names them. XPASSes with "
               "PATCH C.",
    )(test_the_three_questions_p15_cannot_answer_are_named_and_not_dropped))


def test_this_file_is_really_correcting_an_answer_and_the_diff_really_sees_it(
        tmp_path: Path):
    """The falsifying twin, against the two ways this stops measuring.

    §17 governs edits, and `changed_answer` returns `None` for a first answer --
    so a `_corrected` that quietly stopped supersedeing would leave both xfails
    true of a diff that correctly had nothing to say. And a `diff_for_answer_change`
    that had stopped seeing a template change would make them report a gap that
    was not the gap.

    Anchored to the correction and the reader, never to the screen, so it holds
    whether or not PATCH C has landed.
    """
    from questions.effects import diff_for_answer_change

    corpus, database, question_id, scope, options = _corrected(tmp_path)
    _run(corpus, database, "--answer", f"{question_id}={options[1]}")

    conn = open_database(database)
    change = changed_answer(conn, question_id=question_id, scope=scope)
    assert change is not None, (
        "the second `--answer` did not supersede the first, so §17's trigger "
        "never fired and both xfails are about a diff with nothing in it")
    assert change.before is not None and change.after is not None
    diff = diff_for_answer_change(change)
    assert not diff.is_empty, (
        "the reader sees no change between two different options, so the xfails "
        "would be measuring the differ rather than the wiring")
    assert diff.not_computed == tuple(NOT_COMPUTED_BECAUSE), (
        "the three §17 questions P15 cannot answer are no longer carried, so the "
        "second xfail would be asserting on names nothing produces")
