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

**Recaptured on 11 Sep 2026 for `104` §18.42 items 1, 4 and 5, and the diff was
read before it was taken.** The design's horizontal pass now has a screen: the
top-level branch cards print above the tree, every node says which of `00`:102's
five kinds it is, and §5.11's health view prints under the tree. The screen is
151 lines before and 168 after, and the growth is in exactly three places -- the
ten-line card block, the six-line health block, and `   [proposed]` appended to
each of the five tree lines. Nothing else on the screen moved.

**ALL FOURTEEN CAPTURED TABLES ARE IDENTICAL ROW FOR ROW**, `tree_nodes`,
`placement_decisions` and `placement_group_plans` among them, and that is the
fact worth recording: R-92's wait fires where a branch's own facts support more
than one shape or where the branch is a folder the person already made, and this
corpus is neither -- one composition plus `opt_no_split`, and a scan root that
`adopted_folders` has always refused to adopt. So the run this fixture captures
proceeds exactly as it did and places exactly what it placed; what changed is
that the person can now see the areas it was built from.

The card block names the scan root (`corpus`) as one of the person's own
folders, because `horizontal_candidates` offers every existing folder and
`cli.adopted_folders` is what excludes the root from being adopted as a branch.
The two filters disagree about the root by design and the card is true about it
-- it is their folder and it holds six files -- but it is an area nothing can
turn into a branch. Left as the chain computes it; whether the canvas should
show the folder it was pointed at is the owner's.
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

**Recaptured on 13 Sep 2026 for the identifier extractor, and the diff was read
before it was taken.** The `identifiers.*` readers arrived with the 12 Sep merges
and this corpus holds the one file they have anything to say about: the passport
scan carries a passport number and a date of birth, so `evidence` gains exactly
two rows -- `identifiers.passport_number` and `identifiers.date_of_birth`, both
`extractor_version` 0.1.0, both on `Passport scan.txt` -- and the passport's
`text.structured` row in `extraction_runs` reads `observation_count` 7 for 5.

**The second change is the first one counted, and that is the whole diff.** THE
SCREEN IS IDENTICAL, line for line, and TWELVE OF THE FOURTEEN CAPTURED TABLES
are identical row for row -- `file_facts`, `unresolved`, `tree_nodes`,
`placement_decisions`, `placement_group_plans`, `groups`, `memberships` and the
rest. So the readings reach the evidence table and stop there: nothing this
corpus settles, groups, places or prints moved because of them. That the passport
gains two readings and no placement is the measurement -- this run configures no
model of any kind, so what holds that file is the rules' own detector, and
readings of a held file are readings a person is shown rather than ones a folder
is built from.

**Recaptured on 13 Sep 2026 for `104` §18.60's row rule (`e131b1f2`, `0da7084e`),
and the diff was read before it was taken.** "A spreadsheet's unit is a row" does
not touch this corpus -- it holds no spreadsheet -- but `structured_text.py` is
the reader for every `.txt` file here too, and `104` R-164's rule bumps a reader's
VERSION with any change to what it emits, whatever kind of file triggered the
change. Read after masking `extractor_version` and the `cache_key`s (and the
`record_id`/`unresolved_id`/`fact_id` strings built from them) that move only
because that number is inside them: every row in `evidence`, `extraction_runs`,
`file_facts` and `unresolved` is otherwise byte-identical -- same locators, same
`normalized_value`, same `raw_value`, same `reason`, same `field_key`. Nothing
this corpus reads, resolves, groups or places moved; the version travelled and
nothing else did.

The corpus is `test_local_model_fact_pass._corpus`'s six files: a syllabus, a
lecture, a homework, a problem set, an application essay and a passport scan. The
anchors the work-type rule finds on it are all academic's, so it is one branch.

**RECAPTURED ON 19 Sep 2026, AND THE DIFF WAS READ BEFORE IT WAS TAKEN** -- which
is this file's own rule and `108` §4's: a recapture that is not diffed proves only
that the code equals itself. Three things moved and each is ratified:

  * `98 Review and Unsorted` / `Review Later` -- `106` Phase 7's RESIDUAL HOME,
    a root for files no branch of the plan can hold (`107`: "not a dumping
    ground");
  * the `problem set` and `syllabus` folders are gone and their values are carried
    on the terms that keep the files -- `00` AMENDMENT 26, the owner's floor: each
    of those terms holds exactly ONE file, and `107` asks that a single file rest
    at its parent rather than make a one-file leaf;
  * `artifact_kind` reads `work_type` again -- the option sentence names the FIELD
    and not the internal role key, which Phase 7 had changed.

**AND THE CAPTURE MUST BE TAKEN IN THE ENVIRONMENT THE TEST RUNS IN.** Running the
`capture` entry point from a shell reads the repository's `.env`, so it records the
cloud banner where a pytest run without a key records "No model was consulted" --
the same code writing two screens. Neutralise `cli.ENV_FILE` and the model
variables before capturing, or the fixture pins the developer's machine.

**Recaptured on 20 Sep 2026 for `98 Review and Unsorted`'s LINEAGE, and the diff
was read before it was taken.** `106` Phase 5.1 made `origin_node_id` a composed
key at every mint site; amendment 13's review root was added afterwards and kept
the fresh mint's own id, so it was the one node in the tree with no lineage
across versions and two identical runs reported it removed and added. It is a
parentless proposal and now takes `node_key.branch_key` like any other.

Structurally the recapture differs from its predecessor in EXACTLY ONE FIELD OF
ONE ROW: `placement_index_entries`, the review root's payload, whose
`origin_node_id` reads `branch:98 Review and Unsorted` for
`<node:proposed:None:98 Review and Unsorted>`. **The screen is identical line for
line and thirteen of the fourteen tables are identical row for row** --
`tree_nodes` among them, because the shared normaliser drops `origin_node_id` as
a MINTED column and only this payload blob carried the value as text. Nothing
this corpus concludes changed; no placement moved and no count did.

The fact worth recording is what the predecessor already showed: every other
node in it read a composed key -- `branch:Coursework/term=Fall2024`,
`residual:Review Later` -- and this root read a minted id. The fixture had been
printing the odd one out since Phase 5.1 and nothing was reading it.

**Recaptured on 20 Sep 2026 because `origin_node_id` is now COMPARED, and the
diff was read before it was taken.** The entry above ends "nothing was reading
it"; `test_two_runs_of_one_folder_agree` now does, and the shared normaliser it
owns no longer drops the column -- so every row of this fixture's `tree_nodes`
gains one key and the capture had to follow.

The recapture differs from its predecessor in EXACTLY ONE FIELD, `origin_node_id`,
added to all twelve `tree_nodes` rows and to no other table's. **The screen is
identical line for line and thirteen of the fourteen captured tables are identical
row for row**, and no `tree_nodes` row changed a value, was added or was removed.
Every origin it now prints is a composed key -- `branch:Coursework`,
`branch:Coursework/term=Fall2024`, `branch:98 Review and Unsorted`,
`residual:Review Later` -- which is the measurement that says no mint site in this
run is still keeping its own id.

Two things about the capture itself, because both cost time. It was taken through
this module's own `capture` entry point under `GRAPH_AGENT_NO_DOTENV=1` with
`GRAPH_AGENT_LOCAL_MODEL` and `OLLAMA_BASE_URL` unset, and the written fixture was
then compared BYTE FOR BYTE against the reading taken before it: two independent
runs of this corpus, identical. And a reading script that calls
`run_and_normalise` must be guarded by `if __name__ == "__main__"`, as this module
is -- `cli` reads its files in a spawned pool, an unguarded script has every
worker die re-importing it, and what comes back is a silently degraded extraction
(6 text units for 18, 24 evidence rows for 43) that reads like a real diff.
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
    # THE SCREEN PRINTS THE FILES' DATES ("Age range: ... to ..."), and a golden
    # captured on one day would differ on every other. The corpus is stamped with
    # the noon of the day the golden was captured (11 Sep 2026, local time), so a
    # byte-identical screen is byte-identical on any date. Measured: the pin failed
    # the first time the suite ran after midnight, on that one line.
    import os
    import time
    stamp = time.mktime((2026, 9, 11, 12, 0, 0, 0, 0, -1))
    for path in corpus.iterdir():
        os.utime(path, (stamp, stamp))
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
    # THE HOLDER DIRECTORY IS ON THE SCREEN TOO, and until 18 Sep it was not
    # normalised. `00`'s editable-structure block prints the path of
    # `proposed-structure.txt`, which lives beside the database and is neither the
    # corpus nor the database -- so a recapture baked one pytest tmp directory
    # into the fixture and the next run, under a different one, failed. Longest
    # paths first, and the RESOLVED spelling before the raw one: macOS puts a
    # temporary directory under `/var/folders`, a symlink to `/private/var/
    # folders`, and the run records whichever spelling it was handed -- the same
    # reason `say()` already does this for the table rows.
    text = printed
    for path, name in ((database, "<database>"), (corpus, "<corpus>"),
                       (database.parent, "<holder>")):
        for spelling in (path.resolve(), path):
            text = text.replace(str(spelling), name)
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
