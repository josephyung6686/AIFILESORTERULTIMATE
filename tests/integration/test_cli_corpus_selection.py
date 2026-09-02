"""`00`:20-21 — step one, the first thing the design says the product does.

    *"The user first chooses which folders should be analyzed and which
    high-level locations may serve as roots for a future file tree… The user can
    also select whether files may move across high-level folders."*

    *"At this stage, roots are context for the proposal canvas, not permission to
    move files… to show where a proposed branch could eventually live."*

Three choices belong to the person. `src/cli.py` called `record_selection` with
three literals — one source, no roots, crossing off — so `selection_sources`,
`selection_candidate_roots` and `cross_folder_moves` were built, tested, and
handed an answer nobody was ever asked for. `scan_agent/scan.py` has read all
three from the R1 row since it was written: it walks every source, walks the
candidate roots under `APPLIES_TO_CANDIDATE_ROOT`, and drops root-side FILES so a
root is landscape and never corpus. Nothing below builds any of that. What was
missing was the person's answer reaching it.

**`src/cli.py` is the composition root and belongs to the lead**, so this file
names the gestures rather than editing them in.

**The hunks landed on 2026-09-02 and every test below now runs for real.** They
were written as strict xfails while `src/cli.py` belonged to the lead, on the
reasoning this repo already uses: a dozen sessions share this suite, so red tests
here would have been a dozen false alarms, and an XPASS the moment the hunks
landed was the signal to strip the markers. All seventeen went XPASS on the first
run after the patch and the markers came off with it, rather than in a later
tidying pass.

The three gestures proposed to the owner, whose names are the owner's under
`84` §1:

    --also-read PATH        a second, third, fourth folder to analyse
    --could-live-in PATH    a high-level location a branch could eventually live
                            in. Context, never permission.
    --may-cross-folders     files may move between high-level folders

`--could-live-in` over `--root` deliberately: §21 spends a paragraph insisting a
root is not permission, and a flag called `--root` invites the opposite reading
every time a person types it. The name has to carry the sentence.
"""
from __future__ import annotations

import io
import shlex
import sqlite3
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

import cli  # noqa: E402
from database_agent.cloud_consent import DISABLED  # noqa: E402
from scan_agent.selection import (  # noqa: E402
    selection_candidate_roots,
    selection_sources,
)

DOWNLOADS = {
    "BUSIB 4300 Syllabus.txt":
        "BUSIB 4300 Syllabus\n\nSpring 2026. Course outline and grading policy.\n"
        "Office hours Tuesdays. Readings are posted weekly.\n",
    "BUSIB 4300 Problem Set 1.txt":
        "BUSIB 4300 Problem Set 1\n\nSpring 2026. Due 4 February. "
        "Answer all four questions and show your working.\n",
}

DESKTOP = {
    "BUSIB 4300 Lecture Notes.txt":
        "BUSIB 4300 Lecture Notes -- Week 2\n\nSpring 2026. Cost structures "
        "and contribution margin.\n",
    "BUSIB 4300 Reading List.txt":
        "BUSIB 4300 Reading List\n\nSpring 2026. Required and recommended "
        "reading for the whole term.\n",
}


def _corpus(tmp_path: Path) -> tuple[Path, Path, Path]:
    """Two real sources and a candidate root outside both.

    Everything hangs off a fixed `holder`, never directly off the pytest-named
    `tmp_path`: `84` §4 records that a directory name ABOVE a corpus root once
    changed a classification, and the database has to sit beside the corpus
    rather than inside any folder being read.
    """
    holder = tmp_path / "holder"
    downloads = holder / "Downloads"
    desktop = holder / "Desktop"
    root = holder / "Academic"
    for folder, files in ((downloads, DOWNLOADS), (desktop, DESKTOP)):
        folder.mkdir(parents=True)
        for name, body in files.items():
            (folder / name).write_text(body)
    (root / "Semester One").mkdir(parents=True)
    (root / "Semester One" / "an earlier essay.txt").write_text(
        "An essay from last term.\n")
    return downloads, desktop, root


def _run(*argv: str, database: Path) -> str:
    out = io.StringIO()
    cli.main([*argv, "--situation", "academic.coursework",
              "--label", "Coursework", "--user", "jy",
              "--database", str(database)], out=out)
    return out.getvalue()


def _selection(database: Path) -> tuple[sqlite3.Connection, str]:
    """The R1 row the run just wrote — the latest, by the time it was chosen."""
    conn = sqlite3.connect(database)
    conn.row_factory = sqlite3.Row
    row = conn.execute(
        "SELECT selection_id, cross_folder_moves FROM corpus_selections "
        "ORDER BY selected_at DESC, rowid DESC LIMIT 1").fetchone()
    assert row is not None, "the run recorded no corpus selection at all"
    return conn, row["selection_id"]


# --- the first choice: which folders should be analysed -----------------------

def test_a_person_can_name_more_than_one_folder_to_read(tmp_path):
    """`00`:20's own example is three at once, and one folder per run is not it.

    The design names "Downloads, Desktop, or the loose files at the top of
    Documents" in one breath. A person whose coursework is split across two
    folders — which is the ordinary case, not the exotic one — could not ask this
    product about it: they would get two plans over two databases, and neither
    would ever see that the syllabus and the lecture notes are the same course.
    """
    downloads, desktop, _ = _corpus(tmp_path)
    printed = _run(str(downloads), "--also-read", str(desktop),
                   database=tmp_path / "holder" / "plan.sqlite")

    # Both sources' files, by the name their owner calls them. The count is
    # asserted whole rather than as a prefix: `85` §13.8 — a containment check
    # passes on a sentence that happens to hold the substring.
    assert "Files: 4 decided" in printed, printed
    assert "BUSIB 4300 Syllabus.txt" in printed, printed
    assert "BUSIB 4300 Lecture Notes.txt" in printed, printed
    # And named the way the person names them, from BOTH folders. `file_names`
    # showed a file relative to the one folder it knew and fell back to the
    # absolute path for everything else -- so the second source's files would
    # arrive in the report as `/private/var/.../holder/Desktop/BUSIB 4300
    # Lecture Notes.txt` in a column of bare filenames.
    assert str(desktop) not in printed, printed


def test_every_folder_the_person_named_is_in_the_record_that_drives_the_scan(
        tmp_path):
    """R1 is what `scan.py` reads. If the answer is not in the row, it never ran.

    This is the seam the whole defect lived at: the scan has read
    `selection_sources` since it was written, and the composition root wrote a
    one-element list into it.
    """
    downloads, desktop, _ = _corpus(tmp_path)
    database = tmp_path / "holder" / "plan.sqlite"
    _run(str(downloads), "--also-read", str(desktop), database=database)

    conn, selection_id = _selection(database)
    assert selection_sources(conn, selection_id) == [downloads, desktop]


# --- the second choice: which locations may serve as roots --------------------

def test_a_candidate_root_is_recorded_as_context(tmp_path):
    downloads, _, root = _corpus(tmp_path)
    database = tmp_path / "holder" / "plan.sqlite"
    _run(str(downloads), "--could-live-in", str(root), database=database)

    conn, selection_id = _selection(database)
    assert selection_candidate_roots(conn, selection_id) == [root]
    # And it is not a source. Naming a place a branch could live is not asking
    # for it to be organised.
    assert selection_sources(conn, selection_id) == [downloads]


def test_a_file_inside_a_candidate_root_is_not_taken_into_the_corpus(tmp_path):
    """§21: roots are context for the canvas, not material to organise.

    `scan._record` already drops root-side files — `if item.applies_to !=
    APPLIES_TO_SCANNED_SOURCE: return`. This is the run that proves the drop is
    reached by a root a person actually named.
    """
    downloads, _, root = _corpus(tmp_path)
    printed = _run(str(downloads), "--could-live-in", str(root),
                   database=tmp_path / "holder" / "plan.sqlite")

    assert "Files: 2 decided" in printed, printed
    assert "an earlier essay.txt" not in printed, printed


def test_a_candidate_root_is_not_a_place_this_plan_may_file_anything_into(
        tmp_path):
    """The §21 trap, and the one thing in this build that could do real harm.

    `adopted_folders()` offers every directory in P3's inventory to the design as
    a branch, and P3's inventory holds the directories under a candidate root
    too — it records them for exactly the landscape §21 asks for. Adopted, they
    become `existing` nodes, and an `existing` ancestor short-circuits
    `resolve_destination` to its own path. So a root, named as context, would
    have become a legal destination: `Semester One` would appear as a branch and
    a Downloads file could be planned into it with crossing switched off,
    because `resolve_destination` compares the SOURCE's high-level folder to the
    anchor and never looks at where the destination lands.

    Naming a place a branch could eventually live must not be permission to put
    anything there today.
    """
    downloads, _, root = _corpus(tmp_path)
    database = tmp_path / "holder" / "plan.sqlite"
    printed = _run(str(downloads), "--could-live-in", str(root),
                   database=database)

    # The tree itself, not the screen. `Semester One` IS on the screen, under
    # "Could eventually live in" -- that is §21's landscape and it is the point.
    # What must not exist is a NODE over it: a node is a place a file can be put.
    conn, _ = _selection(database)
    nodes = conn.execute(
        "SELECT display_label, existing_path FROM tree_nodes").fetchall()
    assert nodes, "the run built no tree at all, so this proves nothing"
    assert not [row for row in nodes if row["display_label"] == "Semester One"], (
        [tuple(row) for row in nodes])
    assert not [row for row in nodes if row["existing_path"]
                and str(root) in row["existing_path"]], (
        [tuple(row) for row in nodes])
    # And the person is told the count, which is how they would notice: the
    # root's folder is not one of the folders this plan adopted.
    assert "0 yours already" in printed, printed


def test_the_report_says_the_roots_are_context_and_that_nothing_moved_there(
        tmp_path):
    """§21's other half: the engine uses roots "to show where a proposed branch
    could eventually live". A root that changes nothing a person can see is a
    flag that records an answer into a database and reports nothing back."""
    downloads, _, root = _corpus(tmp_path)
    printed = _run(str(downloads), "--could-live-in", str(root),
                   database=tmp_path / "holder" / "plan.sqlite")

    assert "Could eventually live in:" in printed, printed
    assert str(root) in printed, printed
    assert "Nothing is filed there by this plan" in printed, printed


def test_the_exclusion_rules_reach_a_candidate_root_too(tmp_path):
    """§22 says so in one sentence: "The exclusion must apply both to scanned
    sources and to candidate roots." A `node_modules` under a root is set aside
    by the same rule, named on screen, and never walked into."""
    downloads, _, root = _corpus(tmp_path)
    (root / "node_modules" / "left-pad").mkdir(parents=True)
    (root / "node_modules" / "left-pad" / "index.js").write_text("module.exports\n")
    printed = _run(str(downloads), "--could-live-in", str(root),
                   database=tmp_path / "holder" / "plan.sqlite")

    assert "node_modules" in printed, printed
    assert "literal directory name" in printed, printed
    # Never walked into: the rule excludes the directory and its descendants.
    assert "left-pad" not in printed, printed


# --- the third choice: whether files may cross high-level folders -------------

def test_crossing_high_level_folders_is_off_until_the_person_says_otherwise(
        tmp_path):
    """The design's own example, in its own words: a Downloads file "can go to a
    Personal Projects folder on Desktop, or it can remain within Downloads as a
    separately organized file". Absent is not a guess here — it is the absence of
    a permission, which `review_surface/move_permission.py` already treats as no
    permission rather than as an unanswered question."""
    downloads, desktop, _ = _corpus(tmp_path)
    database = tmp_path / "holder" / "plan.sqlite"
    _run(str(downloads), "--also-read", str(desktop), database=database)

    conn, selection_id = _selection(database)
    assert conn.execute(
        "SELECT cross_folder_moves FROM corpus_selections WHERE selection_id = ?",
        (selection_id,)).fetchone()["cross_folder_moves"] == 0


def test_the_person_can_say_that_files_may_cross_high_level_folders(tmp_path):
    downloads, desktop, _ = _corpus(tmp_path)
    database = tmp_path / "holder" / "plan.sqlite"
    _run(str(downloads), "--also-read", str(desktop), "--may-cross-folders",
         database=database)

    conn, selection_id = _selection(database)
    assert conn.execute(
        "SELECT cross_folder_moves FROM corpus_selections WHERE selection_id = ?",
        (selection_id,)).fetchone()["cross_folder_moves"] == 1


def test_a_freeze_reads_the_persons_answer_and_not_a_literal(tmp_path):
    """The second half of the third choice, and the half that decides a move.

    `freeze(cross_folder_moves=False)` was a literal beside a comment saying it
    was "the one nothing here can ask them about yet". Now it can be asked.

    The seam is asserted, not the screen. Whether anything is READY to freeze
    depends on whether a model was reachable on the day the suite ran, and a
    twin that goes quiet when `DEEPSEEK_API_KEY` is absent is a twin that
    reports green for the wrong reason. What must hold either way is that the
    permission P12 is handed is the one the person typed, and that it is the
    same one R1 recorded -- two places that each decide whether a file may cross
    a high-level folder is one place too many.
    """
    downloads, desktop, _ = _corpus(tmp_path)
    database = tmp_path / "holder" / "plan.sqlite"
    seen: list[object] = []
    original = cli.freeze

    def watching(*args, **kwargs):
        seen.append(kwargs["cross_folder_moves"])
        return original(*args, **kwargs)

    cli.freeze = watching
    try:
        _run(str(downloads), "--also-read", str(desktop), "--may-cross-folders",
             "--freeze", database=database)
    finally:
        cli.freeze = original

    assert seen == [True], seen
    conn, selection_id = _selection(database)
    assert conn.execute(
        "SELECT cross_folder_moves FROM corpus_selections WHERE selection_id = ?",
        (selection_id,)).fetchone()["cross_folder_moves"] == 1


def test_the_landscape_p12_is_given_holds_every_folder_the_person_named(
        tmp_path):
    """`high_level_folders` IS §1.1's folder landscape, and it held one entry.

    A file from a second source was therefore under NO high-level folder:
    `_source_folder` returns `None`, the crossing verdict is decided against
    nothing, and P12's refusal `detail` names a `source_high_level_folder` of
    `None` -- a refusal a person cannot act on because it does not say what was
    crossed. The candidate roots belong in it for the same reason and cannot
    become destinations by being there: a destination needs a node whose
    `root_anchor` names it, and no node is built over a root.
    """
    downloads, desktop, root = _corpus(tmp_path)
    seen: list[dict] = []
    original = cli.freeze

    def watching(*args, **kwargs):
        seen.append(kwargs["high_level_folders"])
        return original(*args, **kwargs)

    cli.freeze = watching
    try:
        _run(str(downloads), "--also-read", str(desktop),
             "--could-live-in", str(root), "--freeze",
             database=tmp_path / "holder" / "plan.sqlite")
    finally:
        cli.freeze = original

    assert seen, "the run never reached the freeze"
    assert set(seen[0].values()) == {downloads, desktop, root}, seen[0]


# --- refusals: a named folder that cannot mean what it says -------------------

def test_a_second_source_that_is_not_a_folder_is_refused_in_a_sentence(tmp_path):
    """The same sentence the positional argument already gets. A traceback here
    would be the product answering a typo with a stack."""
    downloads, _, _ = _corpus(tmp_path)
    missing = tmp_path / "holder" / "Documnets"
    out = io.StringIO()
    code = cli.main([str(downloads), "--also-read", str(missing),
                     "--situation", "academic.coursework", "--label", "C",
                     "--user", "jy",
                     "--database", str(tmp_path / "holder" / "plan.sqlite")],
                    out=out)

    assert code != 0
    assert f"{missing} is not a folder" in out.getvalue(), out.getvalue()


def test_a_root_inside_a_folder_being_read_is_refused_rather_than_guessed(
        tmp_path):
    """One path cannot be both the material and the landscape it might move
    into. Which role wins would be a guess, and §21's whole point is that the two
    are not the same kind of answer."""
    downloads, _, _ = _corpus(tmp_path)
    inside = downloads / "Academic"
    inside.mkdir()
    out = io.StringIO()
    code = cli.main([str(downloads), "--could-live-in", str(inside),
                     "--situation", "academic.coursework", "--label", "C",
                     "--user", "jy",
                     "--database", str(tmp_path / "holder" / "plan.sqlite")],
                    out=out)

    assert code != 0
    printed = out.getvalue()
    assert str(inside) in printed, printed
    assert "is inside" in printed, printed


# --- what a second source does to a permission keyed by folder ---------------

def test_a_second_source_does_not_send_under_the_first_ones_consent(tmp_path):
    """A hole this feature would otherwise have opened, not one it found.

    `--enable-cloud` promises in its own help text that a decision is "Recorded
    against THIS FOLDER … another folder is another decision". Consent is keyed
    by folder and the run read one key. The moment a run reads two folders, the
    second folder's files would have left this device under a permission that
    never named it -- and the person would have been told sending was on, which
    is true, and not told which folder they had cleared, which is the part that
    mattered.

    The weakest answer across the sources governs. Absent is refusal.
    """
    downloads, desktop, _ = _corpus(tmp_path)
    database = tmp_path / "holder" / "plan.sqlite"
    # Cleared for Downloads alone, in an earlier run, exactly as a person would.
    _run(str(downloads), "--enable-cloud", database=database)
    printed = _run(str(downloads), "--also-read", str(desktop), database=database)

    # The posture line, measured rather than guessed: an enabled run prints
    # "Cloud sending is ON for this folder". `85` §13.8 -- assert the sentence
    # the product actually says, not one that reads plausibly and can never fire.
    assert "Cloud sending is ON" not in printed, printed


def test_enabling_the_cloud_for_a_multi_source_run_names_every_folder(tmp_path):
    """The other half: having cleared them together, the run may send."""
    downloads, desktop, _ = _corpus(tmp_path)
    database = tmp_path / "holder" / "plan.sqlite"
    _run(str(downloads), "--also-read", str(desktop), "--enable-cloud",
         database=database)

    conn = sqlite3.connect(database)
    conn.row_factory = sqlite3.Row
    cleared = {row["corpus_root"] for row in conn.execute(
        "SELECT corpus_root FROM cloud_consent")}
    assert cleared == {str(downloads), str(desktop)}, cleared


def test_turning_the_cloud_off_reaches_every_folder_it_was_turned_on_for(
        tmp_path):
    """`--disable-cloud` printing "off" while one of two folders was still
    sending is the worst sentence this product could print."""
    downloads, desktop, _ = _corpus(tmp_path)
    database = tmp_path / "holder" / "plan.sqlite"
    _run(str(downloads), "--also-read", str(desktop), "--enable-cloud",
         database=database)
    out = io.StringIO()
    cli.main([str(downloads), "--also-read", str(desktop), "--disable-cloud",
              "--user", "jy", "--database", str(database)], out=out)

    conn = sqlite3.connect(database)
    conn.row_factory = sqlite3.Row
    for folder in (downloads, desktop):
        row = conn.execute(
            "SELECT decision FROM cloud_consent WHERE corpus_root = ? "
            "ORDER BY decision_id DESC LIMIT 1", (str(folder),)).fetchone()
        # `== DISABLED`, not `!= ENABLED`: a malformed write satisfies the
        # negative and this has to be the withdrawal, not merely not-a-grant.
        assert row is not None and row["decision"] == DISABLED, (folder, row)


def test_the_turn_off_line_the_screen_prints_turns_every_source_off(tmp_path):
    """`84` §6: what the screen tells a person to type has to be true.

    A run cleared for two folders printed `database-agent A --disable-cloud`.
    Pasted, it turns off A, prints "Cloud sending is off for A", and leaves B
    cleared -- so the next run over B sends. That is the footgun `--disable-cloud`
    was widened to close, handed back to the person by the line the product tells
    them to type. The line must name every folder this run reads, and the
    posture block must name them too: a person told that sending is on for one
    folder, while two are about to leave their device, has been told the scope
    of the permission is smaller than it is.
    """
    downloads, desktop, _ = _corpus(tmp_path)
    database = tmp_path / "holder" / "plan.sqlite"
    printed = _run(str(downloads), "--also-read", str(desktop), "--enable-cloud",
                   database=database)

    assert "Cloud sending is ON" in printed, printed
    # Both folders named in the posture block...
    assert f"    {downloads}\n" in printed, printed
    assert f"    {desktop}\n" in printed, printed
    # ...and both in the command it tells them to paste, on one line.
    off = [line for line in printed.splitlines() if "--disable-cloud" in line]
    assert len(off) == 1, printed
    assert str(downloads) in off[0] and str(desktop) in off[0], off[0]

    # And it is true: pasting it leaves neither folder cleared.
    out = io.StringIO()
    cli.main(shlex.split(off[0].strip())[1:] + ["--database", str(database)],
             out=out)
    conn = sqlite3.connect(database)
    conn.row_factory = sqlite3.Row
    for folder in (downloads, desktop):
        row = conn.execute(
            "SELECT decision FROM cloud_consent WHERE corpus_root = ? "
            "ORDER BY decision_id DESC LIMIT 1", (str(folder),)).fetchone()
        assert row is not None and row["decision"] == DISABLED, (folder, row)
