"""The person can see what their own change did to the plan they froze.

`107` promises "every split can be changed before freeze". A control whose effect
nobody can see is not a control, and `110` §0.2 measured the gap: the diff exists
in four functions -- `tree_design.diff.diff_versions`,
`placement.versions.reproject`, `review_surface.versions_view.structural_diff_view`
and the `VersionDiff` between them -- and
`grep -rn "structural_diff_view(\\|reproject(" src` found no production caller.
The machinery was complete and reached nobody.

**The corpus here changes between the two runs, and that is the point.** Run one
freezes a plan with a folder per course. Run two is the same command over a folder
two of whose files are gone, so the plan the person froze names folders this
proposal does not build. That is the shape §8.8 is about -- "twenty-three files now
require renewed review because their previous destination no longer exists" -- and
it is reachable with no flag that does not yet exist.

**The arithmetic is the assertion, not the number.** `84` §1: material is marked
and counted and never silently omitted. A file whose folder went away and a file
whose folder stayed are two different facts and one total, and the total has to be
every file the frozen plan placed -- including the two that are no longer in the
folder at all. The test reads the run's OWN line and checks it against a count
taken from the database, so a screen that agreed with itself while dropping a file
still fails.
"""
from __future__ import annotations

import io
import re
import sqlite3
from pathlib import Path

import pytest

import cli

#: Two courses, two files each. Two so that a course folder is a folder that
#: separates something; two courses so that run two can lose one of them.
CORPUS = {
    "phys ps1.txt": "PHYS 1401 problem set 1\nMechanics homework, due "
                    "2024-02-10.\nStudent: jy\n",
    "phys ps2.txt": "PHYS 1401 problem set 2\nMechanics homework, due "
                    "2024-02-17.\nStudent: jy\n",
    "math ps1.txt": "MATH 2010 problem set 1\nLinear algebra homework, due "
                    "2024-02-11.\nStudent: jy\n",
    "math ps2.txt": "MATH 2010 problem set 2\nLinear algebra homework, due "
                    "2024-02-18.\nStudent: jy\n",
}

_ACCOUNTED = re.compile(
    r"^\s*Accounted for: (\d+) \+ (\d+) = (\d+)$", re.MULTILINE)
_PLACED = re.compile(r"^\s*Files the plan you froze had placed: (\d+)$",
                     re.MULTILINE)


def _run(corpus: Path, database: Path, *extra: str) -> str:
    out = io.StringIO()
    code = cli.main([str(corpus), "--situation", "academic.coursework",
                     "--label", "Uni", "--user", "jy",
                     "--database", str(database), "--accept-groups", *extra],
                    out=out)
    printed = out.getvalue()
    assert code == 0, printed
    return printed


def _two_runs(tmp_path: Path) -> tuple[str, Path]:
    """Freeze a plan, lose two of the files, and run the same command again."""
    corpus = tmp_path / "Uni"
    corpus.mkdir()
    for name, body in CORPUS.items():
        (corpus / name).write_text(body)
    database = tmp_path / "plan.sqlite"
    _run(corpus, database, "--freeze")
    (corpus / "math ps1.txt").unlink()
    (corpus / "math ps2.txt").unlink()
    return _run(corpus, database), database


def _block(text: str) -> str:
    """The diff block alone, so a containment test cannot pass on the report.

    Scoped for `test_cli_freeze_accounts_for_every_file`'s reason: the words this
    test looks for -- "review", a version id -- occur all over the report above,
    and an unscoped assertion would be green against a screen with no diff on it.
    """
    at = text.find("\nWhat changed since the plan you froze")
    assert at != -1, f"the run printed no comparison at all\n\n{text}"
    return text[at:]


def _placed_by(database: Path, plan_version: str) -> int:
    conn = sqlite3.connect(f"file:{database}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    try:
        return conn.execute(
            "SELECT COUNT(*) FROM placement_decisions WHERE plan_version = ? "
            "AND outcome = 'place' AND superseded_by IS NULL",
            (plan_version,)).fetchone()[0]
    finally:
        conn.close()


def _frozen_version(database: Path) -> str:
    conn = sqlite3.connect(f"file:{database}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    try:
        from apply_run.freeze import frozen_plans
        versions = {plan.organization_plan_version
                    for plan in frozen_plans(conn)}
        assert len(versions) == 1, versions
        return versions.pop()
    finally:
        conn.close()


def test_a_run_after_a_freeze_shows_what_changed_since_the_freeze(tmp_path):
    """SABOTAGE: stop passing the view into `report` and this finds no block."""
    printed, _ = _two_runs(tmp_path)
    block = _block(printed)
    assert "Folders removed: 2" in block, block
    assert "MATH2010" in block, block
    assert "PHYS1401" in block, block


def test_the_screen_does_not_say_the_person_removed_those_folders(tmp_path):
    """`66` §4: two facts never share one message, and "Folders removed" is one.

    Nobody removed those two folders. The corpus lost two MATH files, so the MATH
    folder had nothing left to separate -- and PHYS then held every remaining
    file, so it separated nothing either. A person who reads a count of removals
    and did not remove anything goes looking for a change they did not make. The
    lists are the record exactly; the sentence this asserts is the fact the
    record does not carry.
    """
    flat = " ".join(_block(_two_runs(tmp_path)[0]).split())
    assert "for one of two reasons" in flat, flat
    assert "the files underneath it changed" in flat, flat


def test_the_comparison_names_both_versions_it_is_between(tmp_path):
    """`84` §6: a screen that says "what changed" without saying changed FROM
    WHAT is a sentence the person cannot check."""
    printed, database = _two_runs(tmp_path)
    block = _block(printed)
    frozen = _frozen_version(database)
    assert frozen in block, block
    proposal = re.search(r"^Plan version: (\S+)", printed, re.MULTILINE)
    assert proposal is not None, printed
    assert proposal.group(1) in block, block


def test_every_file_the_frozen_plan_placed_is_accounted_for(tmp_path):
    """`84` §1, read off the run's own arithmetic line.

    Two of these four files are not even in the folder any more. A screen that
    quietly counted only the files it can still see would be a true sentence
    about a smaller corpus, which is the omission `84` §1 forbids by name.
    """
    printed, database = _two_runs(tmp_path)
    block = _block(printed)
    sums = _ACCOUNTED.search(block)
    assert sums is not None, block
    carried, renewed, total = (int(group) for group in sums.groups())
    assert carried + renewed == total, block

    said = _PLACED.search(block)
    assert said is not None, block
    assert int(said.group(1)) == total, block
    assert total == _placed_by(database, _frozen_version(database)), (
        f"the screen accounts for {total} file(s); the plan the person froze "
        f"placed {_placed_by(database, _frozen_version(database))}\n\n{block}")
    # Not vacuous: a run where nothing was removed would satisfy the sum with
    # one number, and this corpus lost a whole course.
    assert renewed


def test_the_files_needing_review_again_are_explained_not_just_counted(tmp_path):
    """§8.8's own sentence, which `RenewedReviewStatement` already writes.

    Read off a whitespace-flattened copy, because the report wraps: the first
    draft of this looked for `not pre-accepted` in the raw text and failed
    against a screen that said it, with the line break between the two words.
    """
    block = _block(_two_runs(tmp_path)[0])
    flat = " ".join(block.split())
    assert "renewed review" in flat, block
    assert "not pre-accepted" in flat, block


def test_the_three_things_the_comparison_cannot_see_are_named(tmp_path):
    """`84` §6 and `110` §3.2: the three producer gaps NAMED, not omitted.

    `versions_view.GAP_NOTES` is written for a lead -- it cites `66` §17 three
    times -- and `104` R-M keeps a section number off the person's screen. So
    the screen says the same three things in its own words, and this asserts
    each of the three is there.
    """
    block = _block(_two_runs(tmp_path)[0])
    assert "turned on or off" in block, block
    assert "protected" in block, block
    assert "filing" in block, block


def test_a_first_proposal_is_compared_with_nothing(tmp_path):
    """`110` §3.2: nothing is diffed on a first proposal, which is
    `_print_answer_effects`' rule that a first answer is not a change."""
    corpus = tmp_path / "Uni"
    corpus.mkdir()
    for name, body in CORPUS.items():
        (corpus / name).write_text(body)
    printed = _run(corpus, tmp_path / "plan.sqlite")
    assert "What changed since the plan you froze" not in printed, printed


def test_the_comparison_says_it_cannot_tell_a_re_split_from_a_rebuild(tmp_path):
    """`110` §3.2's caveat, said on the screen instead of discovered later.

    A level's key is its parent's key plus `field=value`, so changing the order
    the folders split in re-keys every folder beneath the branch: `diff_versions`
    reports every level removed and every level added, and `DIFF_REORDERED` never
    fires. That is honest and unreadable. The cheap headline needs
    `chosen_order_id`, which is not written yet, so the screen says which of the
    two it cannot tell apart rather than guessing -- `66` §4, two facts never
    sharing one message.

    Asserted where it fires: a run that both added and removed folders. The two
    runs below differ by a residual area, which adds a folder, over a corpus that
    also lost a course, which removes two.
    """
    corpus = tmp_path / "Uni"
    corpus.mkdir()
    for name, body in CORPUS.items():
        (corpus / name).write_text(body)
    database = tmp_path / "plan.sqlite"
    _run(corpus, database, "--freeze")
    (corpus / "math ps1.txt").unlink()
    (corpus / "math ps2.txt").unlink()
    block = _block(_run(corpus, database, "--residual", "Review Later"))
    # The COUNTS rather than a number: enabling one residual area adds the area
    # and the folder that holds it, and how many folders a residual enablement
    # costs is that feature's business and not this test's. What this test is
    # about is that both lists are non-empty, which is the only condition the
    # caveat turns on.
    added = re.search(r"^\s*Folders added: (\d+)$", block, re.MULTILINE)
    removed = re.search(r"^\s*Folders removed: (\d+)$", block, re.MULTILINE)
    assert added is not None and int(added.group(1)) >= 1, block
    assert removed is not None and int(removed.group(1)) >= 1, block
    assert "Review Later" in block, block
    assert "cannot tell you why" in block, block


def _rerun_unchanged(tmp_path: Path, *extra: str) -> str:
    """Freeze, then run the same command over the same folder again."""
    corpus = tmp_path / "Uni"
    corpus.mkdir()
    for name, body in CORPUS.items():
        (corpus / name).write_text(body)
    database = tmp_path / "plan.sqlite"
    _run(corpus, database, "--freeze", *extra)
    return _block(_run(corpus, database, *extra))


def test_running_the_same_command_twice_reports_nothing_changed(tmp_path):
    """The commonest re-run there is, and the one a false diff is worst on.

    Somebody who freezes and runs again without changing anything has to read
    four zeroes. A comparison that invented a change here would send a person
    looking for something they did not do, and every count below is what a
    reader checks the rest of the screen against.
    """
    block = _rerun_unchanged(tmp_path)
    for heading in ("Folders added", "Folders removed", "Folders renamed",
                    "Folders moved under a different folder"):
        assert f"{heading}: 0" in block, block
    sums = _ACCOUNTED.search(block)
    assert sums is not None, block
    carried, renewed, total = (int(group) for group in sums.groups())
    assert (carried, renewed) == (total, 0), block
    assert total == len(CORPUS), block


@pytest.mark.xfail(strict=True, reason=(
    "NOT THIS SCREEN'S DEFECT, pinned where it shows. The review home a "
    "residual enablement mints -- `98 Review and Unsorted` -- carries its own "
    "per-version `node_id` as its `origin_node_id`, so it has no lineage to "
    "match across versions and two identical runs report it removed and added "
    "and the area beneath it moved. `node_key` gives every other node a key "
    "spelled from its claim; this one was missed. The comparison is reporting "
    "the record faithfully, which is why the fix belongs where the node is "
    "minted and not here. When it lands, this test passes and says so."))
def test_an_unchanged_run_with_a_residual_area_reports_nothing_changed(tmp_path):
    block = _rerun_unchanged(tmp_path, "--residual", "Review Later")
    for heading in ("Folders added", "Folders removed",
                    "Folders moved under a different folder"):
        assert f"{heading}: 0" in block, block
