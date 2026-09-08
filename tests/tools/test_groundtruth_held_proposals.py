"""`104` R-151: a held placement is a PROPOSAL, and the scorecard scores its folder.

R-121 lets a local model be asked about a file nothing has classified yet, while
the MOVE waits for the person -- so P11 writes `outcome = place` with
`review_policy = blocked_pending_user`, and what the person sees on screen is "we
suggest this folder; confirm". The folder in that sentence is an answer, right or
wrong, and the scorecard exists to say which. Scoring it as nothing would mean the
first right answers a model gives on a corpus of unclassified files never appear on
the row at all.

So the six buckets and `105` §14.7's five classes read the PROPOSED NODE and never
the policy -- R-128 is closed and its classes do not move -- and the hold is
counted beside them, on a line of its own, because "exact" and "exact, and waiting
for you" are two different facts about the same file.

Against a SYNTHETIC plan database built here, for the reason
`test_groundtruth_five_classes.py` gives: waiting for a corpus that happened to
produce a held placement on the label's folder, a free one, and a held one on the
wrong folder would be waiting for the model to be non-deterministic in a
particular way. Every table is created by the PRODUCT's own DDL, so a column that
moves breaks this test rather than silently changing what it measures.

Nothing here reads, lists or runs anything under `.groundtruth/`, and no model is
configured or invoked.
"""
from __future__ import annotations

# `tools/` is a sibling of `src/`, and `pyproject.toml` puts only `src` on the path.
# Done HERE rather than in a `conftest.py`, for the reason the sibling test modules
# spell out at length: with no `__init__.py` in the tests tree, a `conftest.py` in
# this directory would take the bare name `conftest` away from `tests/p5/conftest.py`,
# whose tests import from it by that name at call time.
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import dataclasses
import hashlib
import json
import sqlite3

import pytest

from database_agent.db import create_schema
from evidence_shape.schema import create_evidence_schema
from extractors.router import ROUTING_DDL
from facts.schema import create_facts_schema
from llm_harness.schema import create_llm_schema
from placement.schema import create_placement_schema
from privacy.schema import create_privacy_schema
from questions.schema import create_questions_schema
from scan_agent.exclusion import EXCLUSION_DDL
from tree_design.schema import create_tree_schema

from tools.groundtruth.labels import load_labels
from tools.groundtruth.measure import (
    AUTO_ELIGIBLE, BLOCKED_PENDING_USER, HELD_POLICIES, REVIEW_REQUIRED,
    observe_run,
)
from tools.groundtruth.report import (
    FREE_TO_MOVE, HELD_FOR_THE_PERSON, POLICY_NOT_RECORDED, held_counts,
    outcome_counts, per_file_table, sorting_lines,
)
from tools.groundtruth.score import (
    APPROPRIATE_ABSTENTION,
    CORRECT_PLACEMENT,
    INCORRECT_PLACEMENT,
    NOT_PLACED,
    NO_DECISION,
    NO_OUTCOME,
    PLACED_EXACT,
    PLACED_FLAT,
    PLACED_PARENT,
    PLACED_WRONG,
    protected_verdict,
    score_sorting,
)
from tools.groundtruth.shadow import ObservedVerdict, SUBSTITUTED, shadow_run

SITUATION = "academic.coursework"
CLOCK = "2026-09-07T00:00:00Z"
PLAN = "plan-1"

#: Seven labelled files. The first three are R-151's whole question: the same
#: folder, proposed three ways.
HELD_EXACT = "Coursework/PHYS 1403 homework 2.txt"   # place, held, labelled leaf
FREE_EXACT = "Coursework/PHYS 1403 homework 3.txt"   # place, free, labelled leaf
HELD_WRONG = "Coursework/PHYS 1403 syllabus.txt"     # place, held, another course
ABSTAINED = "Coursework/PHYS 1402 lab notes.txt"     # abstain, and a policy on it
SILENT = "Coursework/PHYS 1401 exam equations.txt"   # no decision row at all
NO_POLICY = "Coursework/PHYS 1403 homework 4.txt"    # placed by a run with no policy
PROTECTED = "Loose/vaccination record.txt"           # protected, and placed anyway

LABELS = {"files": [
    {"path": HELD_EXACT, "group": "fixture", "situation": SITUATION,
     "destination": ["PHYS1403", "homework"]},
    {"path": FREE_EXACT, "group": "fixture", "situation": SITUATION,
     "destination": ["PHYS1403", "homework"]},
    {"path": HELD_WRONG, "group": "fixture", "situation": SITUATION,
     "destination": ["PHYS1403", "syllabus"]},
    # Its folder is deliberately NOT in NODES, so abstaining was the honest answer
    # and the class beneath the bucket is `appropriate abstention`.
    {"path": ABSTAINED, "group": "fixture", "situation": SITUATION,
     "destination": ["PHYS1402", "lab notes"]},
    {"path": SILENT, "group": "fixture", "situation": SITUATION,
     "destination": ["PHYS1401", "exam"]},
    {"path": NO_POLICY, "group": "fixture", "situation": SITUATION,
     "destination": ["PHYS1403", "homework"]},
    {"path": PROTECTED, "group": "fixture", "situation": SITUATION,
     "destination": None, "protected": True},
]}

NODES = {
    "n-root": ("Coursework", None),
    "n-1403": ("PHYS1403", "n-root"),
    "n-1403-hw": ("homework", "n-1403"),
    "n-1403-syl": ("syllabus", "n-1403"),
    "n-1401": ("PHYS1401", "n-root"),
    "n-1401-exam": ("exam", "n-1401"),
}

IDS = {HELD_EXACT: "f1", FREE_EXACT: "f2", HELD_WRONG: "f3", ABSTAINED: "f4",
       SILENT: "f5", NO_POLICY: "f6", PROTECTED: "f7"}


def _hash(file_id: str) -> str:
    return hashlib.sha256(file_id.encode()).hexdigest()


def _subject(file_id: str) -> str:
    return f"file:{file_id}:{_hash(file_id)}"


def _connect(path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    for create in (create_schema, create_evidence_schema, create_facts_schema,
                   create_privacy_schema, create_placement_schema,
                   create_tree_schema, create_questions_schema, create_llm_schema):
        create(conn)
    conn.executescript(EXCLUSION_DDL)
    conn.executescript(ROUTING_DDL)
    return conn


def _file_row(conn, file_id: str, corpus: Path, relative: str, *,
              protected: int = 0) -> None:
    conn.execute(
        "INSERT INTO files (file_id, current_path, filename, normalized_filename, "
        "extension, directory_position, volume_id, content_hash, hash_algorithm, "
        "observed_size, observed_timestamps, mime_type, detected_format, scan_state, "
        "extraction_status_by_tier, sensitivity_state) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'sha256', 0, '{}', 'text/plain', 'text', "
        "'included', '{}', 'unknown')",
        (file_id, str(corpus / relative), Path(relative).name,
         Path(relative).name.casefold(), Path(relative).suffix, "0",
         "vol-1", _hash(file_id)))
    conn.execute(
        "INSERT INTO classifications (fact_id, file_id, content_hash, handling_class, "
        "protected, basis, evidence_refs, reliability_state, observed_at) "
        "VALUES (?, ?, ?, 'personal_non_sensitive', ?, 'rule', '[]', 'corroborated', ?)",
        (f"c-{file_id}", file_id, _hash(file_id), protected, CLOCK))


def _decision(conn, file_id: str, *, outcome: str, node_id: str | None,
              review_policy: str | None) -> None:
    """One `placement_decisions` row, with P11's policy in BOTH places it writes it.

    The column and the payload, because `store._payload` is `asdict(decision)` and
    the harness reads the payload: writing only the column would let this test pass
    against a scorer that reads nothing.

    `review_policy=None` writes NEITHER, which is the shape of a row from a build
    before the field existed -- the case `NO_POLICY` is here to cover.
    """
    payload = {"ask": None}
    if review_policy is not None:
        payload["review_policy"] = review_policy
    conn.execute(
        "INSERT INTO placement_decisions (record_id, subject_ref, plan_version, "
        "origin_stage, outcome, node_id, review_policy, created_at, payload) "
        "VALUES (?, ?, ?, 'placement', ?, ?, ?, ?, ?)",
        (f"d-{file_id}", _subject(file_id), PLAN, outcome, node_id, review_policy,
         CLOCK, json.dumps(payload)))


@pytest.fixture(scope="module")
def built(tmp_path_factory):
    """One corpus, one database, and the same folder proposed three ways."""
    # `.resolve()` because `observe_run` resolves the corpus root before comparing
    # it with `files.current_path`, and on this platform the temporary directory is
    # reached through a symlink. Unresolved, every file falls out of the `files`
    # table's half of the read and is re-found on disk with no decision at all --
    # which looks exactly like the defect this module is about and is not it.
    base = tmp_path_factory.mktemp("held_proposals").resolve()
    corpus = base / "corpus"
    for relative in IDS:
        (corpus / relative).parent.mkdir(parents=True, exist_ok=True)
        (corpus / relative).write_text("", encoding="utf-8")
    out = base / "out"
    out.mkdir()
    database = out / f"{SITUATION.replace('.', '_')}.sqlite"
    conn = _connect(database)

    for node_id, (label, parent) in NODES.items():
        conn.execute(
            "INSERT INTO tree_nodes (node_id, plan_version_id, origin_node_id, "
            "node_type, display_label, parent_node_id, root_anchor, ordinal, "
            "associated_group_ids, explanation, node_role, accepts_placement, "
            "handling_class) "
            "VALUES (?, ?, ?, 'folder', ?, ?, 'anchor', 0, '[]', '', 'ordinary', 1, "
            "'personal_non_sensitive')",
            (node_id, PLAN, node_id, label, parent))

    for relative, file_id in IDS.items():
        _file_row(conn, file_id, corpus, relative,
                  protected=1 if relative == PROTECTED else 0)

    # The label's own leaf, proposed twice: once the person has to confirm, once
    # the product would carry it out. The only difference is the policy.
    _decision(conn, "f1", outcome="place", node_id="n-1403-hw",
              review_policy=BLOCKED_PENDING_USER)
    _decision(conn, "f2", outcome="place", node_id="n-1403-hw",
              review_policy=AUTO_ELIGIBLE)
    # Held, and on another course entirely. A hold is not an excuse.
    _decision(conn, "f3", outcome="place", node_id="n-1401-exam",
              review_policy=REVIEW_REQUIRED)
    # P11 computes a policy for an ABSTENTION too, and almost always
    # `review_required` -- nothing was proposed, so nothing is being held.
    _decision(conn, "f4", outcome="abstain", node_id=None,
              review_policy=REVIEW_REQUIRED)
    # f5 gets no row at all.
    _decision(conn, "f6", outcome="place", node_id="n-1403-hw", review_policy=None)
    _decision(conn, "f7", outcome="place", node_id="n-1403-hw",
              review_policy=BLOCKED_PENDING_USER)

    conn.commit()
    conn.close()

    labels_path = base / "labels.json"
    labels_path.write_text(json.dumps(LABELS), encoding="utf-8")
    labels = load_labels(labels_path, known_situations=frozenset({SITUATION}))
    run = observe_run(database, corpus, situation=SITUATION, label="Coursework",
                      promised_levels=("Course", "Kind of work"))
    return {"corpus": corpus, "out": out, "database": database, "labels": labels,
            "run": run}


# --- what the run recorded --------------------------------------------------

def test_the_policy_is_read_off_every_decision_the_run_wrote(built):
    files = built["run"].files
    assert files[HELD_EXACT].review_policy == BLOCKED_PENDING_USER
    assert files[FREE_EXACT].review_policy == AUTO_ELIGIBLE
    assert files[HELD_WRONG].review_policy == REVIEW_REQUIRED
    assert files[ABSTAINED].review_policy == REVIEW_REQUIRED
    # A row from a build that had no such field, and a file with no row at all.
    # Both read None, which is the truth: this run recorded no policy for them.
    assert files[NO_POLICY].review_policy is None
    assert files[SILENT].review_policy is None


def test_only_a_placement_can_be_held(built):
    files = built["run"].files
    assert files[HELD_EXACT].held is True
    assert files[HELD_WRONG].held is True
    assert files[FREE_EXACT].held is False
    # The abstention carries `review_required` and is NOT held: nothing was
    # proposed for this file, so there is nothing for the person to confirm.
    assert files[ABSTAINED].held is False
    assert files[NO_POLICY].held is False
    assert files[SILENT].held is False


# --- the five classes, unchanged by the hold --------------------------------

def test_a_held_placement_on_the_labels_folder_is_exact(built):
    """R-151's whole point. Two of the eight site C accepted on r13 were the
    label's own folder, and the row said nothing about them."""
    labels, files = built["labels"], built["run"].files
    assert score_sorting(labels[HELD_EXACT], files[HELD_EXACT]) == PLACED_EXACT


def test_the_same_placement_free_scores_exactly_the_same(built):
    """The policy has no bearing on whether the folder is the right one, so the
    two files score the same bucket and differ only in the count beside it."""
    labels, files = built["labels"], built["run"].files
    assert (score_sorting(labels[HELD_EXACT], files[HELD_EXACT])
            == score_sorting(labels[FREE_EXACT], files[FREE_EXACT])
            == PLACED_EXACT)
    assert files[HELD_EXACT].held is not files[FREE_EXACT].held


def test_a_held_placement_on_the_wrong_folder_is_still_wrong(built):
    """A hold is not an excuse. R-128's classes are closed and this is one of
    them: the file was proposed into another course, and that is `wrong`."""
    labels, files = built["labels"], built["run"].files
    assert score_sorting(labels[HELD_WRONG], files[HELD_WRONG]) == PLACED_WRONG


def test_an_abstention_stays_not_placed_and_a_missing_decision_stays_no_decision(built):
    labels, files = built["labels"], built["run"].files
    assert score_sorting(labels[ABSTAINED], files[ABSTAINED]) == NOT_PLACED
    assert score_sorting(labels[SILENT], files[SILENT]) == NO_DECISION


def test_the_five_classes_come_to_the_same_numbers_they_would_without_a_policy(built):
    counted = outcome_counts([built["run"]], built["labels"])
    # Three placements on the labelled leaf -- held, free, and no policy at all.
    assert counted[CORRECT_PLACEMENT] == 3
    assert counted[INCORRECT_PLACEMENT] == 1        # held, another course
    assert counted[APPROPRIATE_ABSTENTION] == 1     # nowhere legal was built
    assert counted[NO_OUTCOME] == 1                 # nobody decided anything
    # The protected file is left out of the five, exactly as `_split_buckets`
    # leaves it out of the blocks above them.
    assert sum(counted.values()) == len(LABELS["files"]) - 1


# --- the count beside them --------------------------------------------------

def test_the_placements_are_counted_held_against_free(built):
    counted = held_counts([built["run"]], built["labels"])
    assert counted[HELD_FOR_THE_PERSON] == 2        # f1 on the leaf, f3 elsewhere
    assert counted[FREE_TO_MOVE] == 1               # f2
    assert counted[POLICY_NOT_RECORDED] == 1        # f6
    # Every placement the blocks scored, and nothing else: the abstention and the
    # file with no decision are not placements, and the protected file is not
    # scored in these blocks at all.
    assert sum(counted.values()) == 4


def test_the_count_adds_up_against_the_buckets_printed_above_it(built):
    """The promise the line makes to a reader: these are the SAME placements."""
    from tools.groundtruth.report import _split_buckets

    confident, uncertain = _split_buckets([built["run"]], built["labels"])
    placed = sum(
        confident.get(bucket, 0) + uncertain.get(bucket, 0)
        for bucket in (PLACED_EXACT, PLACED_PARENT, PLACED_FLAT, PLACED_WRONG))
    assert sum(held_counts([built["run"]], built["labels"]).values()) == placed


def test_the_block_says_how_many_are_held_and_how_many_are_free(built):
    lines = sorting_lines([built["run"]], built["labels"], heading="SORTING",
                          confident_on_uncertain=0)
    block = "\n".join(lines)
    assert "4 of the files above were placed: 2 held for the person, 1 free to move" \
        in block
    # The two policy words, so a reader knows what "held" was read off, and the
    # sentence that says what a hold means to the person reading the row.
    assert f"a hold ({BLOCKED_PENDING_USER}, {REVIEW_REQUIRED}) is a PROPOSAL" in block
    assert "the folder above is scored either way, the MOVE waits for the person" \
        in block
    # The remainder, printed because it happened. Held plus free plus this is the
    # number of placements, or the line is flattering somebody.
    assert f"1 {POLICY_NOT_RECORDED}" in block


def test_the_hold_changes_no_number_in_the_six_buckets_or_the_five_classes(built):
    """The line is a count beside the classes and never a class. Scoring the run
    with every policy stripped off must give bucket for bucket the same card."""
    run = built["run"]
    stripped = dataclasses.replace(run, files={
        path: dataclasses.replace(observation, review_policy=None)
        for path, observation in run.files.items()})
    assert (outcome_counts([run], built["labels"])
            == outcome_counts([stripped], built["labels"]))
    from tools.groundtruth.report import _split_buckets
    assert (_split_buckets([run], built["labels"])
            == _split_buckets([stripped], built["labels"]))


# --- the per-file table -----------------------------------------------------

def test_the_table_tells_placed_exact_held_from_placed_exact_free(built):
    table = per_file_table([built["run"]], built["labels"])
    header, *rows = table.splitlines()
    columns = header.split("\t")
    by_path = {row.split("\t")[0]: row.split("\t") for row in rows}
    sorting, policy = columns.index("sorting"), columns.index("review_policy")

    held, free = by_path[HELD_EXACT], by_path[FREE_EXACT]
    assert held[sorting] == free[sorting] == PLACED_EXACT
    assert held[policy] == BLOCKED_PENDING_USER
    assert free[policy] == AUTO_ELIGIBLE
    # Which hold it is, and not merely that there is one: "nothing has classified
    # this file yet" and "somebody should look at this" are different obligations.
    assert by_path[HELD_WRONG][policy] == REVIEW_REQUIRED
    # Nothing was proposed for these three, so the cell is empty rather than
    # reporting a hold on a file nobody offered a folder for.
    assert by_path[ABSTAINED][policy] == ""
    assert by_path[SILENT][policy] == ""
    assert by_path[NO_POLICY][policy] == ""


def test_every_row_has_a_cell_for_the_column(built):
    """A ragged table is a table something parses wrong, and the file with no
    decision at all takes the shorter branch through the writer."""
    header, *rows = per_file_table([built["run"]], built["labels"]).splitlines()
    width = len(header.split("\t"))
    assert width == 17
    assert {len(row.split("\t")) for row in rows} == {width}


# --- protected is the protected block's business, not this one --------------

def test_a_held_placement_on_a_protected_file_is_still_a_breach(built):
    """R-151 changes nothing here. A protected file the run proposed to move has
    failed the hard pass/fail, and "the person will confirm" is not a defence:
    the proposal is on screen either way."""
    breaches = protected_verdict(built["labels"], built["run"].files)
    assert [(b.path, b.kind) for b in breaches] == [(PROTECTED, "placed")]


# --- the shadow row ---------------------------------------------------------

def test_a_shadow_placement_carries_no_policy_p11_never_wrote(built):
    """`--shadow` asks what site C's answer would have done. That placement is one
    P11 never made, so no policy was decided for it -- and inheriting the applied
    decision's would report a hold nobody chose, since P11 writes a policy on
    abstentions too."""
    run = built["run"]
    observed = {
        # The abstention, re-read as the placement site C would have made.
        ABSTAINED: ObservedVerdict(
            path=ABSTAINED, outcome="accept_direct", reasons=(),
            destination=("Coursework", "PHYS1403", "homework"),
            source=SUBSTITUTED),
    }
    shadow, sources = shadow_run(run, observed)
    substituted = shadow.files[ABSTAINED]
    assert substituted.outcome == "place"
    assert substituted.review_policy is None
    assert substituted.held is False
    # A file site C was never asked about keeps the decision P11 really wrote.
    assert shadow.files[HELD_EXACT].review_policy == BLOCKED_PENDING_USER
    assert sources[ABSTAINED] == SUBSTITUTED


def test_the_two_policy_words_are_the_ones_the_product_writes():
    """The harness spells them rather than importing them -- it must read a run an
    older build wrote -- so something has to check the spellings still agree."""
    from placement import vocabulary as pv

    assert HELD_POLICIES == (pv.BLOCKED_PENDING_USER, pv.REVIEW_REQUIRED)
    assert AUTO_ELIGIBLE == pv.AUTO_ELIGIBLE
    assert set(HELD_POLICIES) | {AUTO_ELIGIBLE} == set(pv.REVIEW_POLICIES)
