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
import re
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
    AUTO_ELIGIBLE, BLOCKED_PENDING_USER, DECIDED_BY_MODEL, DECIDED_BY_RULE,
    DECIDED_BY_USER, DECIDERS, HELD_POLICIES, REVIEW_REQUIRED,
    observe_run,
)
from tools.groundtruth.report import (
    DECIDER_NOT_RECORDED, FREE_TO_MOVE, HELD_FOR_THE_PERSON,
    POLICY_NOT_RECORDED, bucket_deciders, decided_by_counts, held_counts,
    model_share_note, outcome_counts, per_file_table, row_104, row_128,
    scorecard, sorting_lines,
)
from tools.groundtruth.score import (
    APPROPRIATE_ABSTENTION,
    CORRECT_PLACEMENT,
    INCORRECT_PLACEMENT,
    INVALID_OUTPUT,
    NOT_PLACED,
    NO_DECISION,
    NO_OUTCOME,
    PLACED_EXACT,
    PLACED_FLAT,
    PLACED_PARENT,
    PLACED_WRONG,
    UNNECESSARY_ABSTENTION,
    BREACH_FILED,
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
              review_policy: str | None, decided_by: str | None = None) -> None:
    """One `placement_decisions` row, with P11's policy in BOTH places it writes it.

    The column and the payload, because `store._payload` is `asdict(decision)` and
    the harness reads the payload: writing only the column would let this test pass
    against a scorer that reads nothing.

    `review_policy=None` writes NEITHER, which is the shape of a row from a build
    before the field existed -- the case `NO_POLICY` is here to cover.

    `decided_by` (`104` R-165) goes in the PAYLOAD ONLY, because that is the
    record's one home for it: P11 adds no column, `store._from_row` rebuilds from
    `payload` alone, and a column here would be a shape the product never writes.
    Left out when None, so `NO_POLICY` doubles as the row from a build before this
    field existed -- the case the report's `not recorded` remainder is printed for.
    """
    payload = {"ask": None}
    if review_policy is not None:
        payload["review_policy"] = review_policy
    if decided_by is not None:
        payload["decided_by"] = decided_by
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
    #
    # `104` R-165's three deciders are spread across the same rows, one apiece, so
    # every count below has a denominator bigger than one and a decider that is not
    # the majority. The two axes are deliberately CROSSED -- the held one is the
    # model's, the free one is a rule's -- because a fixture where the same rows
    # carried both facts would pass a scorer that read either field for the other.
    _decision(conn, "f1", outcome="place", node_id="n-1403-hw",
              review_policy=BLOCKED_PENDING_USER, decided_by=DECIDED_BY_MODEL)
    _decision(conn, "f2", outcome="place", node_id="n-1403-hw",
              review_policy=AUTO_ELIGIBLE, decided_by=DECIDED_BY_RULE)
    # Held, and on another course entirely. A hold is not an excuse.
    _decision(conn, "f3", outcome="place", node_id="n-1401-exam",
              review_policy=REVIEW_REQUIRED, decided_by=DECIDED_BY_USER)
    # P11 computes a policy for an ABSTENTION too, and almost always
    # `review_required` -- nothing was proposed, so nothing is being held. It names
    # no decider either: nothing was placed for anybody to have chosen.
    _decision(conn, "f4", outcome="abstain", node_id=None,
              review_policy=REVIEW_REQUIRED)
    # f5 gets no row at all.
    # Neither field, which is one row from a build that had neither -- and the
    # `not recorded` remainder R-165's line prints rather than folding away.
    _decision(conn, "f6", outcome="place", node_id="n-1403-hw", review_policy=None)
    _decision(conn, "f7", outcome="place", node_id="n-1403-hw",
              review_policy=BLOCKED_PENDING_USER, decided_by=DECIDED_BY_MODEL)

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
    assert width == 18
    assert {len(row.split("\t")) for row in rows} == {width}


# --- `104` R-165: who decided, beside what the model path cost --------------

def test_the_decider_is_read_off_every_decision_the_run_wrote(built):
    """§13.5 rules that every placement goes through the model, and until this
    field existed the run could not say whether one had: a rule that fired first
    and skipped the model was indistinguishable from a model verdict."""
    files = built["run"].files
    assert files[HELD_EXACT].decided_by == DECIDED_BY_MODEL
    assert files[FREE_EXACT].decided_by == DECIDED_BY_RULE
    assert files[HELD_WRONG].decided_by == DECIDED_BY_USER
    # Nothing was placed, so nobody chose a folder. A decider here would be an
    # actor credited with a decision that never happened.
    assert files[ABSTAINED].decided_by is None
    # A row from a build that had no such field, and a file with no row at all.
    assert files[NO_POLICY].decided_by is None
    assert files[SILENT].decided_by is None


def test_the_placements_are_counted_by_who_decided_them(built):
    counted = decided_by_counts([built["run"]])
    assert counted[DECIDED_BY_MODEL] == 2          # f1 on the leaf, f7 protected
    assert counted[DECIDED_BY_RULE] == 1           # f2
    assert counted[DECIDED_BY_USER] == 1           # f3
    # Printed as a remainder rather than folded into one of the three, so the
    # arithmetic comes to the number of placements the run made.
    assert counted[DECIDER_NOT_RECORDED] == 1      # f6
    placements = sum(1 for o in built["run"].files.values()
                     if o.outcome == "place")
    assert sum(counted.values()) == placements == 5


def test_the_hold_and_the_decider_are_counted_on_different_denominators(built):
    """Not a discrepancy, and a reader adding one line against the other has to
    be able to tell why. The hold is counted against what the BLOCKS scored, so
    the protected file is left out of it; the decider is counted against what the
    RUN recorded, because the model's share is a fact about the run and not about
    which files happened to be labelled."""
    held = held_counts([built["run"]], built["labels"])
    deciders = decided_by_counts([built["run"]])
    assert sum(held.values()) == 4
    assert sum(deciders.values()) == 5
    assert built["labels"][PROTECTED].protected is True


def test_the_model_block_says_how_many_placements_each_actor_made(built):
    card = scorecard([built["run"]], [], built["labels"], [], [],
                     corpus_files=len(IDS), seconds=1.0)
    assert "placed by=model 2 / rule 1 / user 1, not recorded 1" in card


def test_the_line_is_printed_by_a_run_that_reached_no_model_at_all(built):
    """`model 0 / rule N` is the measurement on a deterministic-only run, which
    §6.6 makes a legal one -- so the line is not folded into the counts above it
    that collapse to "no model tables in these databases"."""
    run = dataclasses.replace(built["run"], files={
        path: dataclasses.replace(
            observation,
            decided_by=DECIDED_BY_RULE if observation.decided_by else None)
        for path, observation in built["run"].files.items()})
    card = scorecard([run], [], built["labels"], [], [],
                     corpus_files=len(IDS), seconds=1.0)
    # All three words every time, zeros included. A line that fell silent about
    # the actors it had nothing to report would leave a reader unable to tell
    # "no model decided anything" from "this build does not count that".
    assert "placed by=model 0 / rule 4 / user 0, not recorded 1" in card


def test_the_table_says_who_chose_the_folder_in_the_row(built):
    table = per_file_table([built["run"]], built["labels"])
    header, *rows = table.splitlines()
    columns = header.split("\t")
    by_path = {row.split("\t")[0]: row.split("\t") for row in rows}
    decider = columns.index("decided_by")
    # Directly after the policy, which is the promise the writer's docstring makes.
    assert columns[decider - 1] == "review_policy"

    assert by_path[HELD_EXACT][decider] == DECIDED_BY_MODEL
    assert by_path[FREE_EXACT][decider] == DECIDED_BY_RULE
    assert by_path[HELD_WRONG][decider] == DECIDED_BY_USER
    # Nothing was proposed for these three, so the cell is empty rather than
    # naming an actor for a folder nobody offered.
    assert by_path[ABSTAINED][decider] == ""
    assert by_path[SILENT][decider] == ""
    assert by_path[NO_POLICY][decider] == ""


def test_the_decider_changes_no_number_in_the_six_buckets_or_the_five_classes(built):
    """The line is a count beside the classes and never a class, exactly as the
    hold is. Scoring the run with every decider stripped off must give bucket for
    bucket the same card."""
    run = built["run"]
    stripped = dataclasses.replace(run, files={
        path: dataclasses.replace(observation, decided_by=None)
        for path, observation in run.files.items()})
    assert (outcome_counts([run], built["labels"])
            == outcome_counts([stripped], built["labels"]))
    from tools.groundtruth.report import _split_buckets
    assert (_split_buckets([run], built["labels"])
            == _split_buckets([stripped], built["labels"]))


def test_the_three_decider_words_are_the_ones_the_product_writes():
    """The harness spells them rather than importing them -- it must read a run an
    older build wrote -- so something has to check the spellings still agree."""
    from placement import vocabulary as pv

    assert DECIDERS == pv.DECIDERS
    assert (DECIDED_BY_MODEL, DECIDED_BY_RULE, DECIDED_BY_USER) == (
        pv.DECIDED_BY_MODEL, pv.DECIDED_BY_RULE, pv.DECIDED_BY_USER)
    # Not a fourth decider, and it must never collide with one: it is the absence
    # of a value, and a scorer that read it as a word would count it as an actor.
    assert DECIDER_NOT_RECORDED not in pv.DECIDERS


# --- protected is the protected block's business, not this one --------------

def test_a_held_placement_on_a_protected_file_is_still_a_breach(built):
    """R-151 changes nothing here, and neither does `104` §18.7. A protected file
    the run proposed to move has failed the hard pass/fail, and "the person will
    confirm" is not a defence: the proposal is on screen either way.

    SABOTAGE: `if observation.outcome == "place" and not observation.held`. §18.7
    forbids filing protected material AUTOMATICALLY, and a reading that let a
    held proposal through would excuse exactly the case this fixture builds --
    the run named a folder for a vaccination record on its own.

    The kind is `filed` since §18.7 and was `placed` before it; the word moved
    with the ruling and the verdict did not.
    """
    breaches = protected_verdict(built["labels"], built["run"].files)
    assert [(b.path, b.kind) for b in breaches] == [(PROTECTED, BREACH_FILED)]
    # The detail is where the hold survives, so a reader sees the split the
    # verdict deliberately does not make.
    assert "held" in breaches[0].detail


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


def test_a_shadow_placement_names_no_decider_p11_never_recorded(built):
    """`104` R-165 travels with R-151, by the identical argument. The substituted
    row is a placement P11 never made, so keeping the applied decision's decider
    would credit `rule` or `user` with a node the rules and the person never
    chose, and the model's share would be counted off the wrong record."""
    run = built["run"]
    observed = {
        ABSTAINED: ObservedVerdict(
            path=ABSTAINED, outcome="accept_direct", reasons=(),
            destination=("Coursework", "PHYS1403", "homework"),
            source=SUBSTITUTED),
    }
    shadow, _sources = shadow_run(run, observed)
    assert shadow.files[ABSTAINED].outcome == "place"
    assert shadow.files[ABSTAINED].decided_by is None
    assert shadow.files[HELD_EXACT].decided_by == DECIDED_BY_MODEL


def test_the_two_policy_words_are_the_ones_the_product_writes():
    """The harness spells them rather than importing them -- it must read a run an
    older build wrote -- so something has to check the spellings still agree."""
    from placement import vocabulary as pv

    assert HELD_POLICIES == (pv.BLOCKED_PENDING_USER, pv.REVIEW_REQUIRED)
    assert AUTO_ELIGIBLE == pv.AUTO_ELIGIBLE
    assert set(HELD_POLICIES) | {AUTO_ELIGIBLE} == set(pv.REVIEW_POLICIES)


# ---------------------------------------------------------------------------
# `104` R-165 second half: the split is on the SORTING line, not only in a
# block of its own further down the card
# ---------------------------------------------------------------------------
# The chain-w1bl case is the whole reason these exist. That run scored 5 of 41
# `right parent, wrong leaf`; the next chain scored 0, and the 5 turned out
# never to have been real -- a term counter had matched `cells`, `source` and
# `kernelspec` as JSON dictionary KEYS in a raw notebook and "recognised" four
# files the model never saw. A rule artifact read as a win for weeks because the
# number and the actor who produced it were printed a screen apart. `00`:110
# sanctions a deterministic pre-filter for a unique direct match and nothing
# else; every other placement is the model's or it is a defect, so the scoreboard
# has to say which on the line the number is on.


def _line_for(lines, bucket):
    """The one SORTING line whose bucket is `bucket`, exactly.

    Matched on the bucket ENDING the line or running straight into the aside,
    rather than on `in`. Two of these names are prefixes of something else on
    the same card -- `wrong` of `right parent, wrong leaf`, and `no decision` of
    the five classes' `no decision at all (outside the five)` -- so a looser
    match reads a line from the wrong block.
    """
    found = [line for line in lines
             if re.match(rf"^\s+\d+\s+[\d.]+%\s+{re.escape(bucket)}(\s+--\s|$)",
                         line)]
    assert len(found) == 1, f"{bucket}: {found}"
    return found[0]


def test_each_placed_sorting_bucket_says_who_decided_the_placements_in_it(built):
    """The fixture crosses the two axes on purpose: three files land in `exact`
    by three different routes and the fourth placement is a user's in `wrong`.
    A renderer that read one decider for the whole block, or the block's most
    common one, passes neither line."""
    lines = sorting_lines([built["run"]], built["labels"],
                          heading="SORTING", confident_on_uncertain=0)
    # f1 model, f2 rule, f6 nobody -- all three in the same bucket.
    assert "-- decided by model 1 / rule 1 / user 0, not recorded 1" in _line_for(
        lines, PLACED_EXACT)
    # f3, and `model 0` is the point: the count is a person's, not the product's.
    assert "-- decided by model 0 / rule 0 / user 1" in _line_for(lines, PLACED_WRONG)


def test_a_bucket_holding_no_placement_names_no_decider(built):
    """`not placed` and `no decision` are not placements and an empty bucket
    holds none, so there is nobody to name. Printing three zeros beside them
    would put an actor's name on a line about a decision that never happened --
    the same error `NO_OUTCOME` is kept out of the five classes to avoid."""
    lines = sorting_lines([built["run"]], built["labels"],
                          heading="SORTING", confident_on_uncertain=0)
    for bucket in (PLACED_PARENT, PLACED_FLAT, NOT_PLACED, NO_DECISION):
        assert "decided by" not in _line_for(lines, bucket)


def test_the_bucket_splits_come_to_what_the_blocks_scored(built):
    """Addable, and against the blocks rather than against the MODEL line. The
    two denominators differ by the protected file -- `decided_by_counts` counts
    every placement the RUN made and this counts the ones the BLOCKS scored --
    so a reader who adds the lines has to land on the block's number or one of
    the two is lying."""
    confident, uncertain = bucket_deciders([built["run"]], built["labels"])
    total = sum(sum(c.values()) for c in confident.values())
    total += sum(sum(c.values()) for c in uncertain.values())
    assert total == sum(held_counts([built["run"]], built["labels"]).values()) == 4
    # And it is NOT the MODEL line's five: the protected file was placed too.
    assert sum(decided_by_counts([built["run"]]).values()) == 5


def test_the_w1bl_shape_cannot_present_a_bucket_as_a_win(built):
    """The regression, reproduced in the small: every placement a rule's, and
    one of them in `right parent, wrong leaf`. The number is unchanged -- this
    row does not re-score anything -- and it can no longer be read alone."""
    run = dataclasses.replace(built["run"], files={
        path: dataclasses.replace(observation, decided_by=DECIDED_BY_RULE)
        for path, observation in built["run"].files.items()
        if observation.outcome == "place"
    } | {
        path: observation for path, observation in built["run"].files.items()
        if observation.outcome != "place"
    })
    lines = sorting_lines([run], built["labels"],
                          heading="SORTING", confident_on_uncertain=0)
    exact = _line_for(lines, PLACED_EXACT)
    assert "3" in exact and "-- decided by model 0 / rule 3 / user 0" in exact


def test_a_run_the_model_decided_nothing_in_says_so_where_the_numbers_are(built):
    """`00`:110 again. A run whose every placement came from a rule can still
    print a good-looking table, and the two one-line rows are what get pasted
    into a diagnosis -- so the fact travels with them and not only with the
    block it was measured in."""
    run = dataclasses.replace(built["run"], files={
        path: dataclasses.replace(
            observation,
            decided_by=DECIDED_BY_RULE if observation.decided_by else None)
        for path, observation in built["run"].files.items()})
    note = model_share_note([run])
    assert note == "the model decided none of this run's 5 placements"
    lines = sorting_lines([run], built["labels"],
                          heading="SORTING", confident_on_uncertain=0)
    # The heading of each block, where the block's denominator is.
    carrying = [line for line in lines if note in line]
    assert len(carrying) == 2, carrying
    assert carrying[0].startswith("SORTING")
    assert "ask the person" in carrying[1]
    # And both grep rows.
    assert note in row_104([run], built["labels"], [])
    assert note in row_128([run], built["labels"])
    assert note in scorecard([run], [], built["labels"], [], [],
                             corpus_files=len(IDS), seconds=1.0)


def test_a_run_that_placed_nothing_says_that_beside_its_abstention_rate(built):
    """The w1bn shape: 100% not placed and 98.6% appropriate abstention, both
    excellent-looking, and no model was ever asked. `0 of 0` is not English, so
    this case gets its own sentence rather than a number that reads as a rate."""
    run = dataclasses.replace(built["run"], files={
        path: dataclasses.replace(observation, outcome="abstain", decided_by=None)
        for path, observation in built["run"].files.items()})
    assert model_share_note([run]) == (
        "this run placed nothing, so the model decided nothing")


def test_the_note_is_absent_when_the_model_decided_any_placement(built):
    """Exactly zero and not a threshold. A share the reader should worry about
    is a judgement, and R-165's row is an instrument -- the per-bucket splits
    above print the ratio on every line and let the reader make it."""
    assert model_share_note([built["run"]]) == ""
    lines = sorting_lines([built["run"]], built["labels"],
                          heading="SORTING", confident_on_uncertain=0)
    assert not [line for line in lines if "the model decided none" in line]
    assert "the model decided none" not in row_104([built["run"]], built["labels"], [])



def test_the_owners_five_classes_carry_the_split_the_buckets_do(built):
    """`correct placement` is the headline number on the whole card, and until
    now it was the one line in the SORTING block that could be read without
    knowing who produced it. `score_outcome` builds it from `PLACED_EXACT`
    alone, so it carries that bucket's split unchanged -- a mapping, not a
    second scoring."""
    lines = sorting_lines([built["run"]], built["labels"],
                          heading="SORTING", confident_on_uncertain=0)
    correct = _line_for(lines, CORRECT_PLACEMENT)
    assert "-- decided by model 1 / rule 1 / user 0, not recorded 1" in correct
    # The same words the `exact` bucket above it printed, because they are the
    # same four placements counted twice under two questions.
    assert correct.split("-- decided by")[1] == (
        _line_for(lines, PLACED_EXACT).split("-- decided by")[1])
    assert "-- decided by model 0 / rule 0 / user 1" in _line_for(
        lines, INCORRECT_PLACEMENT)


def test_the_three_classes_that_chose_no_folder_name_nobody(built):
    """An abstention and an invalid answer placed nothing. Naming an actor
    beside them would credit a decision that was never made -- `not placed`'s
    rule, applied to the five classes."""
    lines = sorting_lines([built["run"]], built["labels"],
                          heading="SORTING", confident_on_uncertain=0)
    for name in (APPROPRIATE_ABSTENTION, UNNECESSARY_ABSTENTION, INVALID_OUTPUT):
        assert "decided by" not in _line_for(lines, name)


def test_the_class_split_is_added_over_both_kinds_of_label(built):
    """`outcome_counts` counts confident and uncertain labels together while the
    two blocks above keep them apart, so the split beside a class has to be the
    sum of both or it sits beside a number it was not measured on."""
    confident, uncertain = bucket_deciders([built["run"]], built["labels"])
    from_classes = sum(sum(c.values()) for c in confident.values())
    from_classes += sum(sum(c.values()) for c in uncertain.values())
    counted = outcome_counts([built["run"]], built["labels"])
    assert from_classes == (counted[CORRECT_PLACEMENT]
                            + counted[INCORRECT_PLACEMENT]) == 4
