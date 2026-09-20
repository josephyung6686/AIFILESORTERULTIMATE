"""A person leaves one branch out, and no file of theirs leaves with it.

`110` §2.1's *Disable*, end to end. `107` promises that "every split can be
changed before freeze"; `110` measured the code and found the `IGNORE` writer
built (`tree_design/store.py`: the node becomes `ignored` and
`accepts_placement=False`) and reachable by no gesture. This is the gesture.

**The branch is named exactly as `--apply` names one** -- `apply_run.branches_named`,
the bare label when it is unique in the tree and the `/`-joined path always,
refusing an ambiguous word by naming the alternatives. One selector for "which
branch did you mean", not two.

**`84` §1 is the rule this gesture is most likely to break.** Material is marked
and counted and never silently omitted. An ignored branch's files do not vanish
with it: the run's own coverage arithmetic still closes, and the screen says
where they went. Both are read off the run's OWN lines rather than off a number
this test computes, because those lines are what the person is shown and are the
thing that has to be true.

**Three runs and not two**, for `test_cli_level_relabel`'s reason: run one is the
screen that has to print the branch, run two makes the gesture, run three proves
re-derivation did not take it back.
"""
from __future__ import annotations

import io
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

import cli  # noqa: E402

#: `test_cli_level_relabel`'s corpus, for its reason: two courses, so `subject`
#: divides and the branch this gesture disables is one the tree actually BUILT.
#: A corpus whose ignored branch had no folder and no file beneath it could not
#: tell a gesture that reached the plan from one that reached only the screen.
CORPUS = {
    "week 3 syllabus.pdf.txt":
        "PHYS 1401 Syllabus\n\nSpring 2026. Instructor: Dr. Ross.\n",
    "notes.txt":
        "PHYS 1401 lecture notes, week 3.\n",
    "COMS 4995 problem set 1.txt":
        "COMS 4995 Problem Set 1\n\nSpring 2026. Instructor: Dr. Okafor.\n",
}

#: The person's own word for the top folder, typed at `--label`. It is the ONE
#: name this file supplies: the branch the gesture names is read off the run's
#: own folder list, so nothing here is true of this corpus and no other.
LABEL = "Coursework"

#: The heading the folder list is printed under, and the one after it. The block
#: between them is what a person reads a branch name off, so it is what this test
#: reads one off too.
FOLDERS_HEADING = "Folders in this plan:"


def _corpus(tmp_path: Path) -> Path:
    """Under `holder/corpus`, for `test_cli_level_relabel`'s reason: pytest names
    `tmp_path` after the test function, and a directory name above the corpus
    root has changed classification before now."""
    corpus = tmp_path / "holder" / "corpus"
    corpus.mkdir(parents=True)
    for name, body in CORPUS.items():
        (corpus / name).write_text(body)
    return corpus


def _run(corpus: Path, *extra: str) -> str:
    out = io.StringIO()
    cli.main([str(corpus), "--situation", "academic.coursework",
              "--label", LABEL, "--user", "jy",
              "--database", str(corpus.parent / "plan.sqlite"),
              "--accept-groups", *extra], out=out)
    return out.getvalue()


def _conn(corpus: Path) -> sqlite3.Connection:
    return cli.open_database(corpus.parent / "plan.sqlite")


def _folder_lines(printed: str) -> list[tuple[int, str]]:
    """The folder list as `(depth, label)`, read off the screen.

    Off the SCREEN and not out of `tree_nodes`, because half of what this gesture
    has to get right is that the name the folder list prints is a name the flag
    takes (`84` §6). A test that took the label from the database could not tell
    those two apart.
    """
    lines: list[tuple[int, str]] = []
    inside = False
    for raw in printed.splitlines():
        if raw.startswith(FOLDERS_HEADING):
            inside = True
            continue
        if inside:
            if not raw.startswith("  "):
                break
            body = raw.split("   [")[0]
            depth = (len(body) - len(body.lstrip())) // 2
            lines.append((depth - 1, body.strip()))
    return lines


def _a_branch_with_children(printed: str) -> str:
    """One branch below the root that has folders under it, by its own name.

    Any such branch will do and the corpus decides which: what is being asked is
    that ignoring a branch takes its SUBTREE out of the destinations, and a leaf
    could not tell that from ignoring one node.
    """
    folders = _folder_lines(printed)
    for index, (depth, label) in enumerate(folders):
        if depth < 1:
            continue
        if index + 1 < len(folders) and folders[index + 1][0] > depth:
            return label
    raise AssertionError(f"no branch with children in:\n{printed}")


def _marks(printed: str, label: str) -> str:
    for raw in printed.splitlines():
        if raw.split("   [")[0].strip() == label and raw.startswith("  "):
            return raw
    return "ABSENT"


def _nodes(corpus: Path) -> list[sqlite3.Row]:
    """Every node of the newest plan version, as the database holds it."""
    conn = _conn(corpus)
    try:
        version = conn.execute(
            "SELECT plan_version_id FROM plan_versions "
            "ORDER BY created_at DESC, rowid DESC LIMIT 1").fetchone()[0]
        return list(conn.execute(
            "SELECT node_id, parent_node_id, display_label, origin_node_id, "
            "node_type, accepts_placement FROM tree_nodes "
            "WHERE plan_version_id = ?", (version,)).fetchall())
    finally:
        conn.close()


def _subtree(rows: list[sqlite3.Row], label: str) -> list[sqlite3.Row]:
    by_parent: dict[str | None, list[sqlite3.Row]] = {}
    for row in rows:
        by_parent.setdefault(row["parent_node_id"], []).append(row)
    root = next(row for row in rows if row["display_label"] == label)
    found, pending = [], [root]
    while pending:
        node = pending.pop()
        found.append(node)
        pending.extend(by_parent.get(node["node_id"], ()))
    return found


def test_an_ignored_branch_stays_in_the_plan_and_stops_being_a_destination(
        tmp_path):
    """The whole gesture in one test, because its halves are worth nothing apart.

    Run one prints the folder list and the line that says what to type. Run two
    types it: the branch and everything under it are `ignored` and accept no
    placement, and the two records land -- P13's `review_action`, which is the
    audit trail `81` §13.1 requires every canvas edit to travel in, and the node
    rows P10's `IGNORE` writer edits. Run three re-derives the whole tree from
    the catalogue and comes back with the branch still out, which is what makes
    this a preference and not a one-run flag.
    """
    corpus = _corpus(tmp_path)

    first = _run(corpus)
    left_out = _a_branch_with_children(first)
    # `84` §6: what the screen tells a person to type has to be true, so the
    # screen has to tell them. `--rename-level` earns its line one block down for
    # the same reason.
    assert "--ignore-branch" in first, first

    second = _run(corpus, "--ignore-branch", left_out)
    assert "[ignored]" in _marks(second, left_out), second
    assert "marked, not a destination" in _marks(second, left_out), second

    rows = _nodes(corpus)
    under = _subtree(rows, left_out)
    assert len(under) > 1, [dict(row) for row in under]
    assert all(row["node_type"] == "ignored" for row in under), (
        "a branch is named WITH everything under it, and a child that still "
        f"accepts files is a folder the person left out: {[dict(r) for r in under]}")
    assert not any(row["accepts_placement"] for row in under), (
        [dict(row) for row in under])
    # Everything else keeps its own answer: a gesture about one branch that
    # quieted the rest would be the product taking a decision nobody made.
    others = [row for row in rows
              if row["node_id"] not in {node["node_id"] for node in under}]
    assert any(row["accepts_placement"] for row in others), (
        [dict(row) for row in others])

    conn = _conn(corpus)
    try:
        actions = conn.execute(
            "SELECT surface, action, subject_ref, correction_scope, routed_to "
            "FROM review_actions WHERE correction_scope = 'branch' "
            "AND action = 'reject'").fetchall()
        assert len(actions) == 1, [tuple(row) for row in actions]
        assert actions[0]["surface"] == "canvas"
        # THE ORIGIN KEY and not a node id: §8.8 mints a new node id per plan
        # version, so a row filed under one would stop applying at the first
        # edit. `node_key` spells the origin from the node's own claim, which is
        # what makes the next run able to find the same branch.
        assert actions[0]["subject_ref"].startswith("branch:"), \
            dict(actions[0])
    finally:
        conn.close()

    third = _run(corpus)
    assert "[ignored]" in _marks(third, left_out), third


def test_the_files_of_an_ignored_branch_are_still_counted_and_still_named(
        tmp_path):
    """`84` §1, which is the rule this gesture is most likely to break.

    The arithmetic is read off the run's own coverage block rather than computed
    here: that block is what the person checks, and a test that added the numbers
    up itself would pass over a screen that does not.

    SABOTAGE: drop the ignored branch's files from the roster instead of leaving
    them unplaced. The coverage sum still prints and no longer closes.
    """
    corpus = _corpus(tmp_path)
    first = _run(corpus)
    left_out = _a_branch_with_children(first)
    # The names the first run was ready to file INTO the branch about to be left
    # out -- the files that have to turn up somewhere else on the second run.
    total = len(CORPUS)

    second = _run(corpus, "--ignore-branch", left_out)

    assert f"Coverage: {total} files indexed." in second, second
    assert f"= {total}, and every file is on exactly one line above." in second, \
        second
    # Named, not merely counted. Every file of the corpus is still on this
    # screen; the ones that were going into the branch are on it under the block
    # that says what happens to a file no folder can hold.
    for name in CORPUS:
        assert name in second, (name, second)
    assert "Held for review" in second, second
    # And the branch is not a place anything was filed into any more.
    assert f"Ready to file into {left_out}" not in second, second


def test_a_word_that_names_no_branch_is_refused_by_naming_the_ones_there_are(
        tmp_path):
    """The negative twin, and it guards the refusal rather than the happy path.

    A silently dropped gesture is the worst of both -- no effect, and no way to
    tell -- which is `--reject`'s own rule one flag over. `branches_named`
    already refuses by listing every branch by a path that can be typed, and this
    asserts the person meets that sentence rather than a traceback.
    """
    corpus = _corpus(tmp_path)
    _run(corpus)
    refused = _run(corpus, "--ignore-branch", "no such folder of mine")
    assert "names no branch in this plan" in refused, refused

    conn = _conn(corpus)
    try:
        assert conn.execute(
            "SELECT count(*) AS n FROM review_actions "
            "WHERE correction_scope = 'branch' AND action = 'reject'"
        ).fetchone()["n"] == 0
    finally:
        conn.close()
