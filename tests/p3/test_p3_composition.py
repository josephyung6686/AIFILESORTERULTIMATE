# tests/p3/test_p3_composition.py
"""§1.1's exclusions asked of the RUN: is what was set aside ever said out loud?

`tests/p3/test_p3_exclusion.py` proves the four rules thoroughly -- which paths
each one catches, that an excluded path yields no `files` row and no descendants,
and that the verdict is recorded with the rule that made it. It proves all of it
about `scan_agent.exclusion`, against verdicts the test itself writes.

`scan_agent.summary.set_aside_paths` is the reader that turns those verdicts into
something a person can be told, and it is reached by nothing a person runs.
`src/cli.py` prints `tree_design.upstream.protected_areas`, which filters to
`RULE_PROTECTED_CONTAINER` alone. §1.1's other three rules -- literal directory
name, category, software-project-root descendant -- reach no screen.

**Measured 2026-09-02 by running the real command**, on the corpus below. The
report printed "Protected containers: 0 marked, none opened" and nothing else,
while `set_aside_paths` on the database that same run produced returned four rows:

    'Library'      rule='literal directory name'           subject='Library'
    'node_modules' rule='literal directory name'           subject='node_modules'
    'index.js'     rule='software project root descendant' subject='package.json'
    'package.json' rule='software project root descendant' subject='package.json'

`84` §1's first standing rule is "marked and counted, NEVER SILENTLY OMITTED", and
it has no exception for the three rules that are not `protected container`.
`summary.py`'s own module docstring makes the same complaint about itself: the
counters "say HOW MANY paths a rule excluded; they cannot say WHICH, and a person
cannot ask for a folder back that they were never told was left behind. ... That
is `Library/` on a real person's machine, which is where their mail and their app
data live."

**Not cosmetic, and the corpus below shows why.** `myproject/` appears in the plan
as "[yours already]" -- a folder of the person's own that the product proposes to
keep -- while both of the files inside it were set aside and never read. A person
reading that report sees a folder in their plan with nothing in it and is given no
reason at all.

The fix is `_print_set_aside` in the composition root; the hunks are held for its
owner. This file drives `cli.main` rather than reaching into it, because the
exclusion verdicts are produced inside `cli.run`'s nested `downstream` closure.
"""
from __future__ import annotations

import io
import sys
from pathlib import Path

import pytest

from database_agent.db import open_database
from scan_agent.exclusion import RULE_PROTECTED_CONTAINER
from scan_agent.summary import scan_run_summary, set_aside_paths

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

import cli  # noqa: E402

#: One real file so the chain reaches a plan, and one instance of each of §1.1's
#: two rules that fire without a hand-authored category list. `Library/` is in
#: `EXCLUDED_DIRECTORY_NAMES` and is the case `summary.py` names by hand;
#: `package.json` is one of §1.1's four project-root markers, so its siblings are
#: descendants of a software project root.
CORPUS: dict[str, str] = {
    "PHYS 1401 syllabus.txt": "PHYS 1401 Syllabus\n\nSpring 2026. Instructor.\n",
    "node_modules/left-pad.js": "module.exports = 1\n",
    "Library/Mail.sqlite": "not really mail, but named like it\n",
    "myproject/package.json": '{"name": "x"}\n',
    "myproject/index.js": "console.log(1)\n",
}


def _real_run(tmp_path: Path) -> tuple[str, tuple, dict]:
    """Run the shipped command on a real folder; hand back what it PRINTED.

    The same invocation a person types, through `cli.main`'s own argument parser,
    so nothing here can be right about a call the product does not make. The
    report is captured rather than the database queried, because the whole
    question is whether a person is told.
    """
    corpus = tmp_path / "corpus"
    for name, text in CORPUS.items():
        path = corpus / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    database = tmp_path / "plan.sqlite"
    out = io.StringIO()
    exit_code = cli.main(
        [str(corpus), "--situation", "academic.coursework", "--label", "Coursework",
         "--user", "jy", "--database", str(database)], out=out)
    assert exit_code == 0, "the run must reach a plan before its report means anything"
    conn = open_database(database)
    scan_run_id = conn.execute(
        "SELECT scan_run_id FROM scan_runs ORDER BY rowid DESC LIMIT 1").fetchone()[0]
    aside = set_aside_paths(conn, scan_run_id=scan_run_id)
    summary = scan_run_summary(conn, scan_run_id)
    return out.getvalue(), aside, summary


def test_every_path_a_rule_set_aside_is_named_on_the_screen(tmp_path: Path):
    """The standing rule, applied to the report the product actually printed.

    By PATH and not by count. A count is `paths_excluded_by_rule`, which the
    report does not print either, and which would not let a person ask for a
    folder back in any case: `summary.py` draws exactly that line between how many
    and which, and this is the "which" half.
    """
    printed, aside, _ = _real_run(tmp_path)
    unmentioned = [entry.path for entry in aside if entry.path not in printed]
    assert not unmentioned, (
        f"{len(unmentioned)} of {len(aside)} paths §1.1 set aside are in no line "
        f"of the report: {unmentioned}. `84` §1: marked and counted, never "
        f"silently omitted.")


test_every_path_a_rule_set_aside_is_named_on_the_screen = pytest.mark.xfail(
    strict=True,
    reason="measured 2026-09-02 against a real run: `src/cli.py` prints "
           "`protected_areas`, which filters to RULE_PROTECTED_CONTAINER, and "
           "calls `scan_agent.summary.set_aside_paths` nowhere -- so §1.1's other "
           "three rules reach no screen. XPASSes -- and fails the suite, forcing "
           "this marker off -- the day the composition root prints them. The "
           "hunks are in the reachability agent's CLI-PATCH.txt as PATCH A.",
)(test_every_path_a_rule_set_aside_is_named_on_the_screen)


def test_the_rule_that_set_each_path_aside_is_named_beside_it(tmp_path: Path):
    """Naming the folder is half of it; a person also has to know WHY.

    Separate from the assertion above because it is a separate failure: a report
    that listed four paths under one heading would still leave a person unable to
    tell a folder skipped because of its NAME -- which they could rename -- from
    one skipped because it sits under a `package.json`, which they cannot.
    """
    printed, aside, _ = _real_run(tmp_path)
    for rule in sorted({entry.rule for entry in aside}):
        assert rule in printed, (
            f"no line of the report says {rule!r}, so a person cannot tell why "
            f"these paths were left out or whether it is something they can change")


test_the_rule_that_set_each_path_aside_is_named_beside_it = pytest.mark.xfail(
    strict=True,
    reason="the same gap seen from the other side: no set-aside block exists at "
           "all, so no rule is named. XPASSes with PATCH A.",
)(test_the_rule_that_set_each_path_aside_is_named_beside_it)


def test_this_file_is_really_reading_the_run_and_the_corpus_really_excludes(
        tmp_path: Path):
    """The falsifying twin, and it has to catch both ways this file stops measuring.

    A `_real_run` that captured nothing, or a corpus that stopped tripping §1.1,
    would make the two xfails above report the composition root while measuring an
    empty list -- `not unmentioned` is vacuously true of no paths, which is the
    exact shape of the four guards `84` §5.3 records as having quietly stopped
    being able to fail.

    So this pins three things: the report really was captured and is the report
    (it carries the block `cli.py` DOES print), the corpus really produced
    verdicts under more than one rule, and none of them is a protected container
    -- because `set_aside_paths` excluding those is the reason it is a second
    reader rather than a wider one.

    Anchored to the corpus and the capture, never to the gap. A twin anchored to
    the gap would break the day the gap closes, which would make this file punish
    its own finding being fixed.
    """
    printed, aside, summary = _real_run(tmp_path)
    assert "Protected containers:" in printed, (
        "this is not the run's report -- the block `cli.py` does print is absent, "
        "so a passing assertion above would be about a string nobody printed")
    assert len(aside) >= 4, (
        f"the corpus stopped tripping §1.1: {len(aside)} paths set aside. The two "
        f"xfails would then be true of nothing")
    assert len({entry.rule for entry in aside}) >= 2, (
        "one rule only -- the second xfail would pass on a report that named it "
        "by accident")
    assert all(entry.rule != RULE_PROTECTED_CONTAINER for entry in aside), (
        "`set_aside_paths` returned a protected container, which is the one thing "
        "it promises to leave to the block that already has its own wording")
    assert summary["files_indexed"] == 1, (
        "one file survived §1.1 in this corpus; a different count means the "
        "exclusions stopped applying and the measurement above is about a corpus "
        "this file no longer describes")
