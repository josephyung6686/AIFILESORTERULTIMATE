# tests/integration/test_r37_single_branch_is_byte_identical.py
"""`104` R-37 / R-100, ruling (4): with ONE branch, offline, nothing changes.

The per-branch situation answers the situation per top-level branch the run
proposes instead of once per folder. On a folder that is all one life -- every
kind-of-file anchor the library owns belongs to the situation the person typed --
the run proposes one branch, and the ruling pins that such a run is byte-identical
to the run before the change: the same screen and the same derived records.

**The fixture is captured on the base WITHOUT R-37's code**, by running this
module as a script (`python3 tests/integration/<this file> capture`) in a
checkout of that base -- first `ec6e46f`, and after the branch was rebased onto
the revert of its first merge, `ac712bb`, whose upstream merges had moved seven
lines of this screen. A fixture captured after the change would prove only that
the code agrees with itself; when the base moves, recapture it there, never here. Every minted id is replaced by what it names, exactly as
`test_two_runs_of_one_folder_agree` replaces them, so what is compared is what the
run concluded and not which uuid it drew.

**From `2c1eb87` on this is a drift pin, not a before/after proof.** R-37's
byte-identity on a single-branch corpus was proven against fixtures captured
WITHOUT its code at `ec6e46f`, `dcf5367`, `ac712bb` and `f0ff759`; R-135's gap 4
(`d5d0e18`) then renamed the minted line's extractor and kept derived readings
out of the rule pass, which changed this corpus's evidence table for a reason
that is not R-37's. R-37 is merged, so a checkout without it no longer exists
to capture from; the fixture is now captured at the merged head and pins the
single-branch screen and records against drift, to be recaptured deliberately
whenever a merge changes them on purpose.

**Recaptured on 10 Sep 2026 for `104` §18.2 gap 16, and the diff was read before
it was taken.** The gap adds `ConflictConsidered.found_on` -- which node a ruling
value was found on -- so every `conflicts_considered` entry in the stored payload
gains a key. Structurally the recapture differs from its predecessor in exactly
six places and every one of them is that key: the same placements, the same
suppressed node ids, the same counts, the same sentences. This corpus has no
chain conflict to find, because P10 gives each node its whole chain's expected
values, so every pair here reads `(node, that same node)` -- which is what a
conflict on a node's own value has always meant.

**Recaptured again on 10 Sep 2026 for `104` §18.2 gap 12, and the diff was read
before it was taken.** The gap declares the graph channel producible on a
retrieval whose candidate a typed edge supports, so a node reached by an accepted
group AND a typed edge scores 3 of 6 instead of 2 of 5. Structurally the
recapture differs from its predecessor in exactly two rows, the two
`privacy_blocked` abstentions: their `alternatives` support scores read 0.5 for
0.4 and `two_condition.meets_threshold` reads true for false; the outcome,
`privacy_blocked`, the placements, the counts and the sentences are unchanged.
That is `00`:109's arithmetic reaching the record and nothing else.

**Recaptured again on 10 Sep 2026 for `104` R-160's VERSION bump of the
structured-text extractor (0.3.0 -> 0.4.0, on R-164's rule, so cached notebooks
are re-read), and the diff was read before it was taken.** Twenty-one
`extractor_version` strings moved, and the eight `file_facts` and eight
`unresolved` rows whose `cache_key` is derived from that version moved with
them; sorted and compared with the version and the cache keys masked, every
table is identical to its predecessor. Nothing this corpus concludes changed.

**Recaptured on 11 Sep 2026 for `104` SF-3, and the diff was read before it was
taken.** SF-3 makes a group a DRAFT until a person's gesture or a ratified site B
decides it, so the run this fixture captures now types `--accept-groups`. That is
not a way around the change; it is the change. Without the flag the run designs no
tree and places no file -- correctly -- and the fixture would have captured four
lines of proposal screen and pinned nothing R-37 is about. The flag is the gesture
a person makes and the one the scoreboard makes (`tools/groundtruth/_one_run.py`),
so what is pinned here is the shape a decided run has.

Structurally the recapture differs from its predecessor in EXACTLY ONE FIELD OF ONE
ROW: `groups.proposed_basis` on the merged group gains its last clause, "so it is a
draft until somebody decides". The screen is 151 lines before and after with no
line changed; thirteen of the fourteen captured tables are identical row for row,
`placement_decisions` and `placement_group_plans` among them. **Nothing vanished
from this fixture, and that is the fact worth recording:** the acceptance is now
somebody's act rather than the run's assumption, and once it is made the plan is
the plan it always was. The rows that record WHO made it -- `group_acceptance`,
`review_actions`, `review_presentations` -- are not in this fixture's table set,
which is `test_two_runs_of_one_folder_agree`'s to widen and not this pin's;
`tests/integration/test_sf3_a_group_is_a_draft_until_decided.py` asserts them
directly.

**Recaptured on 11 Sep 2026 for `104` R-42, and the diff was read before it was
taken.** The residual screen gained §7.5's per-set card and §7.6's two other set
answers, so this screen gains SEVENTEEN LINES and loses none: under each of the
four review sets, two card lines -- examples by filename, file-type
distribution, age range, the OCR or text evidence, the sensitivity -- and, under
the three unprotected ones, a `--leave-set` and a `--review-set` line. The
protected set gets its card without the examples, which is the owner's
2026-09-02 ruling reaching the card.

**Every one of the fourteen captured tables is identical row for row**, which is
the fact worth recording: no placement row moved, no decision changed, nothing
vanished. The four items of R-42 that could have touched this run -- the
characteristic partition, the disposition read off a template's authored
treatment, the library actions, the user-defined areas -- all of them need a
`--residual` or a `--residual-library` this fixture's argv does not type, and a
PDF, a spreadsheet or a screenshot this corpus does not hold. Their absence from
this diff is the measurement, not an assumption.

The corpus is `test_local_model_fact_pass._corpus`'s six files: a syllabus, a
lecture, a homework, a problem set, an application essay and a passport scan. The
anchors the work-type rule finds on it are all academic's, so it is one branch.
"""
from __future__ import annotations

import importlib.util
import io
import json
import re
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

import cli  # noqa: E402

HERE = Path(__file__).resolve().parent
FIXTURE = HERE / "fixtures" / "r37_single_branch_offline.json"

SITUATION = "academic.coursework"
LABEL = "Coursework"

UUID = re.compile(
    r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}")
STAMP = re.compile(
    r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?([+-]\d{2}:\d{2}|Z)?")
PLAN_VERSION = re.compile(r"version_[0-9a-f]{6,}_(\d+)")
NODE_ID = re.compile(r"node_[0-9a-f]{6,}_(\d+)")


def _corpus(root: Path) -> Path:
    corpus = root / "holder" / "corpus"
    corpus.mkdir(parents=True)
    (corpus / "PHYS 1401 syllabus.txt").write_text(
        "PHYS 1401 Syllabus\n\nSpring 2026. Instructor: Dr. Lee. Credits: 3.\n")
    (corpus / "Lecture 08.txt").write_text(
        "Lecture 08 - Rotational Dynamics\nPHYS 1401\nTorque and angular momentum.\n")
    (corpus / "HW 3.txt").write_text(
        "Homework 3\n\nProblem 1. A ball is thrown upward...\n")
    (corpus / "BUSIB 4300 Problem Set 4.txt").write_text(
        "Problem Set 4\nFall 2024\n\nProblem 1. Compute the net present value.\n")
    (corpus / "Columbia Essay.txt").write_text(
        "Dear Admissions Committee at Columbia University,\nMy essay follows.\n")
    (corpus / "Passport scan.txt").write_text(
        "Passport\nHong Kong Special Administrative Region\n"
        "Passport No. K12345678\nDate of birth: 1 January 1990\n")
    return corpus


def _normaliser():
    """`test_two_runs_of_one_folder_agree._normalised`, imported by path so there
    is ONE definition of what "the same records" means."""
    spec = importlib.util.spec_from_file_location(
        "two_runs", HERE / "test_two_runs_of_one_folder_agree.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module._normalised


def _screen(printed: str, corpus: Path, database: Path) -> list[str]:
    text = printed.replace(str(corpus), "<corpus>").replace(
        str(database), "<database>")
    text = PLAN_VERSION.sub(lambda found: f"<plan:{found.group(1)}>", text)
    text = NODE_ID.sub(lambda found: f"<node:{found.group(1)}>", text)
    text = UUID.sub("<uuid>", text)
    text = STAMP.sub("<stamp>", text)
    return text.splitlines()


def run_and_normalise(root: Path) -> dict:
    corpus = _corpus(root)
    database = root / "holder" / "plan.sqlite"
    out = io.StringIO()
    code = cli.main([str(corpus), "--situation", SITUATION, "--label", LABEL,
                     "--user", "t", "--database", str(database),
                     # `104` SF-3, and the flag is what keeps this fixture a pin on
                     # the single-branch SCREEN rather than on the proposal screen.
                     # A group is a draft until somebody accepts it, and a run that
                     # accepts nothing designs no tree and places no file -- so
                     # without this the fixture would capture four lines of
                     # proposal and pin nothing R-37 is about. This is the shape the
                     # scoreboard captures for the same reason: the gesture is made
                     # explicitly, by the harness, through the flag a person types.
                     "--accept-groups"], out=out)
    assert code == 0, out.getvalue()
    return {"screen": _screen(out.getvalue(), corpus, database),
            "tables": _tables(database, root)}


def _tables(database: Path, root: Path) -> dict[str, list[str]]:
    """The shared normaliser, plus the two things that differ ONLY because the
    corpus sits under a different temporary directory each time: the directory
    itself, and the content-addressed key of a `path`-zone observation, which is
    a digest OF that directory. Each is replaced by what it names."""
    import sqlite3
    conn = sqlite3.connect(f"file:{database}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    try:
        keys = {row["observation_key"]: (
            f"<obs:path:{Path(row['current_path']).name}>")
            for row in conn.execute(
                "SELECT e.observation_key, f.current_path FROM evidence e "
                "JOIN files f ON f.file_id = e.file_id "
                "WHERE e.location LIKE '%\"zone\":\"path\"%'")}
    finally:
        conn.close()
    tables = _normaliser()(database)

    def say(row: str) -> str:
        for key, name in keys.items():
            row = row.replace(key, name)
        # The resolved path first: macOS puts a temporary directory under
        # `/var/folders`, which is a symlink to `/private/var/folders`, and the
        # scan records whichever spelling it was handed.
        return row.replace(str(root.resolve()), "<tmp>").replace(
            str(root), "<tmp>")

    return {table: sorted(say(row) for row in rows)
            for table, rows in tables.items()}


def test_a_single_branch_offline_run_is_byte_identical_to_before_r37(tmp_path):
    expected = json.loads(FIXTURE.read_text())
    actual = run_and_normalise(tmp_path)

    assert actual["screen"] == expected["screen"], "\n".join(
        line for line in _diff(expected["screen"], actual["screen"]))
    for table, rows in expected["tables"].items():
        assert actual["tables"].get(table) == rows, (
            table + "\n" + "\n".join(_diff(rows, actual["tables"].get(table, []))))


def _diff(before: list[str], after: list[str]) -> list[str]:
    import difflib
    return list(difflib.unified_diff(before, after, "captured", "now", lineterm=""))


if __name__ == "__main__":
    if sys.argv[1:] != ["capture"]:
        sys.exit("usage: capture")
    import tempfile
    with tempfile.TemporaryDirectory() as scratch:
        FIXTURE.parent.mkdir(exist_ok=True)
        FIXTURE.write_text(json.dumps(run_and_normalise(Path(scratch)),
                                      indent=1, sort_keys=True) + "\n")
    print(f"captured {FIXTURE}")
