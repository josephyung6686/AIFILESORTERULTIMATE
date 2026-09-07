"""`104` R-128 / `105` §14.7: five outcome classes, and fresh told from reused.

The six sorting buckets answer "where did the file go". The owner's five classes
answer "was that the right thing to do", and the buckets cannot: `not placed` is
the pass for a file whose right answer is a question and the miss for a file whose
folder the run built and then did not use, and neither bucket knows which case it
is looking at. This module builds a run in which every one of the five happens at
least once, and asserts them in BOTH blocks -- the applied one and the shadow one
-- because a class that is counted differently in the two would make the pair
unreadable, which is the one thing the shadow row is for.

Against a SYNTHETIC plan database built here, for the reason
`test_groundtruth_shadow.py` gives at length: waiting for a corpus that happened to
produce a rejected verdict, an abstention with nowhere legal to go, and an
abstention with somewhere legal to go would be waiting for the model to be
non-deterministic in a particular way. Every table is created by the PRODUCT's own
DDL, so a column that moves breaks this test rather than silently changing what it
measures.

Nothing here reads, lists or runs anything under `.groundtruth/`, and no model is
configured or invoked: the verdicts are written by hand, which is what makes the
five classes reachable at all.
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
from tools.groundtruth.measure import observe_run
from tools.groundtruth.report import (
    _split_buckets, outcome_counts, row_128, scorecard, sorting_lines,
)
from tools.groundtruth.score import (
    APPROPRIATE_ABSTENTION,
    CORRECT_PLACEMENT,
    INCORRECT_PLACEMENT,
    INVALID_OUTPUT,
    NO_OUTCOME,
    UNNECESSARY_ABSTENTION,
    has_legal_candidate,
    protected_verdict,
    score_situation,
)
from tools.groundtruth.shadow import shadow_block

SITUATION = "academic.coursework"
CLOCK = "2026-09-07T00:00:00Z"
PLAN = "plan-1"

#: The six labelled files, and the class each one is here to reach.
CORRECT = "Coursework/PHYS 1403 homework 2.txt"          # placed on the labelled leaf
MISPLACED = "Coursework/PHYS 1403 syllabus.txt"          # placed, wrong folder
ASK = "Loose/logo.svg"                                   # 'ask the person', abstained
NOWHERE = "Coursework/PHYS 1402 lab notes.txt"           # abstained, no folder built
COULD_HAVE = "Coursework/PHYS 1401 exam equations.txt"   # abstained, folder built
BROKEN = "Coursework/PHYS 1403 homework 3.txt"           # the verdict rejected it

#: A protected file, to prove the five classes are counted over the same files the
#: two sorting blocks are: `_split_buckets` leaves protected out, and a five-class
#: table that counted it would not add up against the blocks above it.
PROTECTED = "Loose/vaccination record.txt"

LABELS = {"files": [
    {"path": CORRECT, "group": "fixture", "situation": SITUATION,
     "destination": ["PHYS1403", "homework"]},
    {"path": MISPLACED, "group": "fixture", "situation": SITUATION,
     "destination": ["PHYS1403", "syllabus"]},
    {"path": ASK, "group": "fixture", "situation": SITUATION,
     "destination": None, "uncertain": "a logo with no course anywhere near it"},
    # The folder this one wants is deliberately NOT in NODES: the run never built
    # anywhere legal to put it, so abstaining was the only honest answer.
    {"path": NOWHERE, "group": "fixture", "situation": SITUATION,
     "destination": ["PHYS1402", "lab notes"]},
    {"path": COULD_HAVE, "group": "fixture", "situation": SITUATION,
     "destination": ["PHYS1401", "exam"]},
    {"path": BROKEN, "group": "fixture", "situation": SITUATION,
     "destination": ["PHYS1403", "homework"]},
    {"path": PROTECTED, "group": "fixture", "situation": SITUATION,
     "destination": None, "protected": True},
]}

#: The folders the run froze. `Coursework` is the top level the run supplies; the
#: labels name what is below it. `PHYS1402/lab notes` is absent on purpose, and
#: `PHYS1401/exam` is present and REFUSES placement -- the two halves of "the run
#: had no legal candidate", which is not the same question as "a folder with that
#: name exists".
NODES = {
    "n-root": ("Coursework", None, 1),
    "n-1403": ("PHYS1403", "n-root", 1),
    "n-1403-hw": ("homework", "n-1403", 1),
    "n-1403-syl": ("syllabus", "n-1403", 1),
    "n-1401": ("PHYS1401", "n-root", 1),
    "n-1401-exam": ("exam", "n-1401", 1),
}

IDS = {CORRECT: "f1", MISPLACED: "f2", ASK: "f3", NOWHERE: "f4",
       COULD_HAVE: "f5", BROKEN: "f6", PROTECTED: "f7"}


def _corpus(root: Path) -> Path:
    for relative in IDS:
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("", encoding="utf-8")
    return root


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


def _hash(file_id: str) -> str:
    return hashlib.sha256(file_id.encode()).hexdigest()


def _subject(file_id: str) -> str:
    return f"file:{file_id}:{_hash(file_id)}"


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


def _decision(conn, file_id: str, *, outcome: str, node_id: str | None) -> None:
    conn.execute(
        "INSERT INTO placement_decisions (record_id, subject_ref, plan_version, "
        "origin_stage, outcome, node_id, created_at, payload) "
        "VALUES (?, ?, ?, 'placement', ?, ?, ?, ?)",
        (f"d-{file_id}", _subject(file_id), PLAN, outcome, node_id, CLOCK,
         json.dumps({"ask": None})))


def _dossier(conn, dossier_id: str, file_id: str) -> None:
    conn.execute(
        "INSERT INTO llm_dossier (dossier_id, call_site, subject_ref, "
        "eligibility_reason, plan_version, policy_version, reduction_rung, payload, "
        "observed_at) VALUES (?, 'C_placement', ?, 'bounded_ambiguity', ?, 'pol-1', "
        "'unreduced', '{}', ?)",
        (dossier_id, _subject(file_id), PLAN, CLOCK))


def _response(conn, dossier_id: str, destination: str) -> None:
    body = {"claims": [{
        "claim_ref": "claim-1",
        "payload": {"destination": destination, "per_dimension_support": [],
                    "alternatives": [], "conflicts_considered": [],
                    "support": 2, "next_support": 0,
                    "refinement": "not_applicable"},
        "citations": [],
    }]}
    conn.execute(
        "INSERT INTO llm_response (response_id, dossier_id, response_bytes, model_id, "
        "prompt_fingerprint, release_audit_id, release_id, observed_at) "
        "VALUES (?, ?, ?, 'fixture-model', 'fp-1', 1, ?, ?)",
        (f"r-{dossier_id}", dossier_id, json.dumps(body).encode("utf-8"),
         f"rel-{dossier_id}", CLOCK))


def _verdict(conn, dossier_id: str, *, outcome: str, reasons=()) -> None:
    payload = json.dumps({
        "verdict_id": f"v-{dossier_id}", "dossier_id": dossier_id,
        "claim_ref": "claim-1", "outcome": outcome, "disposition": "unresolved",
        "reasons": list(reasons), "may_propose": False, "requires_review": False,
        "citations_checked": [], "scope": "single_claim", "validator_version": "v-1",
        "policy_version": "pol-1", "plan_version": PLAN}, sort_keys=True)
    conn.execute(
        "INSERT INTO llm_verdict (verdict_id, dossier_id, claim_ref, outcome, "
        "disposition, validator_version, policy_version, plan_version, payload, "
        "observed_at) VALUES (?, ?, 'claim-1', ?, 'unresolved', 'v-1', 'pol-1', ?, "
        "?, ?)",
        (f"v-{dossier_id}", dossier_id, outcome, PLAN, payload, CLOCK))


#: What this run was HANDED rather than bought, as `reuse.write_seeded` records it.
#: Two tables with rows and six without, so the assertion covers both halves of
#: R-128's first sentence: a count that was seeded, and a count that was not.
SEEDED = {"llm_dossier": 2, "llm_verdict": 3}


@pytest.fixture(scope="module")
def built(tmp_path_factory):
    """One corpus, one database, and every one of the five classes reached once."""
    base = tmp_path_factory.mktemp("five_classes")
    corpus = _corpus(base / "corpus")
    out = base / "out"
    out.mkdir()
    database = out / f"{SITUATION.replace('.', '_')}.sqlite"
    conn = _connect(database)

    for node_id, (label, parent, accepts) in NODES.items():
        conn.execute(
            "INSERT INTO tree_nodes (node_id, plan_version_id, origin_node_id, "
            "node_type, display_label, parent_node_id, root_anchor, ordinal, "
            "associated_group_ids, explanation, node_role, accepts_placement, "
            "handling_class) "
            "VALUES (?, ?, ?, 'folder', ?, ?, 'anchor', 0, '[]', '', 'ordinary', ?, "
            "'personal_non_sensitive')",
            (node_id, PLAN, node_id, label, parent, accepts))

    for relative, file_id in IDS.items():
        _file_row(conn, file_id, corpus, relative,
                  protected=1 if relative == PROTECTED else 0)

    # WHAT THE RUN APPLIED. One exact, one in the wrong course, four abstentions.
    _decision(conn, "f1", outcome="place", node_id="n-1403-hw")   # correct
    _decision(conn, "f2", outcome="place", node_id="n-1401-exam")  # incorrect
    for file_id in ("f3", "f4", "f5", "f6"):
        _decision(conn, file_id, outcome="abstain", node_id=None)
    _decision(conn, "f7", outcome="abstain", node_id=None)         # protected

    # WHAT SITE C ANSWERED. `f6`'s answer was REJECTED by the validator, which is
    # how a response that did not decode or did not fit the shape is recorded --
    # `SCHEMA_INVALID` is a `reject` verdict, so the fifth class is reachable from
    # `llm_verdict.outcome` alone and the response bytes are never read.
    _dossier(conn, "dos-1", "f1")
    _response(conn, "dos-1", "n-1403-hw")
    _verdict(conn, "dos-1", outcome="accept_direct")

    _dossier(conn, "dos-2", "f2")
    _response(conn, "dos-2", "n-1403-syl")          # the labelled leaf: exact
    _verdict(conn, "dos-2", outcome="accept_direct")

    _dossier(conn, "dos-3", "f3")                   # the 'ask the person' file
    _verdict(conn, "dos-3", outcome="abstain")

    _dossier(conn, "dos-5", "f5")                   # a folder exists; it declined
    _verdict(conn, "dos-5", outcome="abstain")

    _dossier(conn, "dos-6", "f6")
    _response(conn, "dos-6", "n-1403-hw")
    _verdict(conn, "dos-6", outcome="reject", reasons=("SCHEMA_INVALID",))

    # f4 was never asked: no dossier at all.

    conn.commit()
    conn.close()

    labels_path = base / "labels.json"
    labels_path.write_text(json.dumps(LABELS), encoding="utf-8")
    labels = load_labels(labels_path, known_situations=frozenset({SITUATION}))
    run = observe_run(database, corpus, situation=SITUATION, label="Coursework",
                      promised_levels=("Course", "Kind of work"), seeded=SEEDED,
                      seeded_from="a prior run at abcdef123456")
    scores = [score_situation(run, labels)]
    return {"corpus": corpus, "out": out, "database": database, "labels": labels,
            "run": run, "scores": scores}


# --- what the run recorded, before anything is scored -----------------------

def test_the_tree_offers_only_the_folders_it_accepts_placements_into(built):
    """`node_paths` is what "no legal candidate" is decided against, so it has to
    be the placeable folders and not merely the named ones."""
    chains = built["run"].node_paths
    assert ("Coursework", "PHYS1403", "homework") in chains
    assert ("Coursework", "PHYS1401", "exam") in chains
    # PHYS1402 was never built at all, which is why abstaining on its file is the
    # honest answer rather than a miss.
    assert not any("PHYS1402" in chain for chain in chains)


def test_a_rejected_verdict_marks_that_file_and_only_that_file(built):
    """Read from the verdict, never from the response bytes: `measure.py` promises
    it counts and does not read, and `response_bytes` carries `cited_span`."""
    files = built["run"].files
    assert files[BROKEN].invalid_model_output is True
    assert files[CORRECT].invalid_model_output is False
    # An abstention is the model declining, not an answer that failed. Counting it
    # as invalid would report the caution the harness asks for as a defect.
    assert files[ASK].invalid_model_output is False
    assert files[COULD_HAVE].invalid_model_output is False
    # Never asked at all: no answer, so no failed answer.
    assert files[NOWHERE].invalid_model_output is False


def test_a_legal_candidate_is_a_folder_the_run_actually_built(built):
    labels, run = built["labels"], built["run"]
    assert has_legal_candidate(labels[COULD_HAVE], run.node_paths) is True
    assert has_legal_candidate(labels[NOWHERE], run.node_paths) is False
    # A label with no destination has no candidate by definition, which is why
    # `score_outcome` decides `is_uncertain` first and never lets this answer it.
    assert has_legal_candidate(labels[ASK], run.node_paths) is False


# --- the five classes, in the applied block ---------------------------------

def test_every_one_of_the_five_classes_is_reached_at_least_once(built):
    """The whole point of the fixture. Five classes, five files, one each."""
    counted = outcome_counts([built["run"]], built["labels"])
    assert counted[CORRECT_PLACEMENT] == 1          # f1, on the labelled leaf
    assert counted[INCORRECT_PLACEMENT] == 1        # f2, filed in another course
    assert counted[APPROPRIATE_ABSTENTION] == 2     # f3 ask-the-person, f4 nowhere
    assert counted[UNNECESSARY_ABSTENTION] == 1     # f5, the folder was there
    assert counted[INVALID_OUTPUT] == 1             # f6, the verdict rejected it
    assert counted[NO_OUTCOME] == 0


def test_the_five_classes_count_the_same_files_the_sorting_blocks_do(built):
    """So a reader may add the five and check the total against the blocks above.

    Protected is left out of both, by the same rule: a protected file is a hard
    pass/fail with named files and has no placement outcome to classify.
    """
    run, labels = built["run"], built["labels"]
    counted = outcome_counts([run], labels)
    labelled = len(LABELS["files"]) - 1              # every label but the protected
    assert sum(counted.values()) == labelled
    # THE INVARIANT `outcome_lines` STANDS ON. It prints the three placed-elsewhere
    # sub-counts from `_split_buckets` beside the class counts from
    # `outcome_counts`, so if those two ever counted different files the roll-up
    # would stop adding up to the rows printed under it and nobody would be told.
    confident, uncertain = _split_buckets([run], labels)
    assert sum(counted.values()) == sum(confident.values()) + sum(uncertain.values())


def test_correct_and_incorrect_agree_with_the_buckets_printed_above_them(built):
    """The reason placement is decided BEFORE an invalid answer is looked at.

    `f6`'s model answer failed and `f6` was not placed, so it is `invalid output`.
    Had it been placed, it would have been scored on where it landed -- otherwise
    this table's `correct placement` would disagree with the `exact` line directly
    above it and neither number could be checked against the other.
    """
    score = built["scores"][0]
    counted = outcome_counts([built["run"]], built["labels"])
    assert counted[CORRECT_PLACEMENT] == score.sorting["exact"]
    assert counted[INCORRECT_PLACEMENT] == (
        score.sorting["right parent, wrong leaf"]
        + score.sorting["top folder only"] + score.sorting["wrong"])


def test_the_applied_block_prints_the_five_beneath_the_two_it_already_had(built):
    """Every existing line survives; the table is added under them."""
    lines = sorting_lines([built["run"]], built["labels"], heading="SORTING",
                          confident_on_uncertain=0)
    text = "\n".join(lines)
    assert "files whose right folder is known" in text
    assert "files whose right answer is 'ask the person'" in text
    assert "in the owner's five outcome classes (`105` §14.7)" in text
    for name in (CORRECT_PLACEMENT, INCORRECT_PLACEMENT, APPROPRIATE_ABSTENTION,
                 UNNECESSARY_ABSTENTION, INVALID_OUTPUT):
        assert f"  {name}" in text, name
    # The roll-up, taken apart: the owner asked for the two older buckets to keep
    # being counted separately as well as rolled up.
    assert "of which right parent, wrong leaf" in text
    assert "of which top folder only" in text


def test_the_row_names_the_five_counts_on_one_line(built):
    row = row_128([built["run"]], built["labels"])
    assert row == ("correct placement 1 / incorrect placement 1 / "
                   "appropriate abstention 2 / unnecessary abstention 1 / "
                   "invalid output 1")


# --- the same five, in the shadow block -------------------------------------

@pytest.fixture(scope="module")
def shadowed(built):
    block, shadow_runs, _sources = shadow_block(
        [built["run"]], built["scores"], built["labels"], built["out"],
        built["corpus"])
    return {"block": block, "runs": shadow_runs}


def test_the_shadow_block_prints_the_same_five_classes(shadowed):
    block = shadowed["block"]
    assert "SHADOW SORT" in block
    assert "in the owner's five outcome classes (`105` §14.7)" in block
    for name in (CORRECT_PLACEMENT, INCORRECT_PLACEMENT, APPROPRIATE_ABSTENTION,
                 UNNECESSARY_ABSTENTION, INVALID_OUTPUT):
        assert f"  {name}" in block, name


def test_the_shadow_five_move_with_the_verdicts_and_the_applied_five_do_not(
        built, shadowed):
    """What the block is FOR. The applied row cannot move while the prompt is
    unratified, so the pair is the only way to see what ratifying would buy."""
    counted = outcome_counts(shadowed["runs"], built["labels"])
    # `f2`'s verdict named the labelled leaf, so what the run filed in the wrong
    # course the model would have filed correctly: correct rises, incorrect falls.
    assert counted[CORRECT_PLACEMENT] == 2
    assert counted[INCORRECT_PLACEMENT] == 0
    # `f5`'s verdict is an abstention on a file whose folder the run built, which
    # is still the unnecessary one -- the model declined a home that existed.
    assert counted[UNNECESSARY_ABSTENTION] == 1
    assert counted[INVALID_OUTPUT] == 1
    # And the applied five are unmoved. The shadow must never write back.
    assert outcome_counts([built["run"]], built["labels"])[CORRECT_PLACEMENT] == 1


def test_the_shadow_block_prints_the_row_for_both_and_they_differ(built, shadowed):
    block = shadowed["block"]
    applied = row_128([built["run"]], built["labels"])
    shadow = row_128(shadowed["runs"], built["labels"])
    assert f"applied:  {applied}" in block
    assert f"shadow:   {shadow}" in block
    assert applied != shadow


# --- fresh told from reused -------------------------------------------------

def test_every_model_count_on_the_card_says_fresh_and_reused(built):
    """`105` §14.7's first sentence. A single total would report a rerun that
    spent nothing as one that spent everything again."""
    card = scorecard([built["run"]], built["scores"], built["labels"],
                     protected_verdict(built["labels"], built["run"].files), [],
                     corpus_files=len(IDS), seconds=1.0)
    lines = card.splitlines()
    start = next(i for i, line in enumerate(lines) if line.startswith("MODEL"))
    block = " ".join(line.strip() for line in lines[start:start + 6]
                     if line.startswith("MODEL") or "=fresh " in line)
    # Five dossiers were written and two of them were handed to this run, so the
    # fresh half is three. The same arithmetic on the verdicts: five, three seeded.
    assert "dossier=fresh 3 / reused 2" in block, block
    assert "verdict=fresh 2 / reused 3" in block, block
    # A table nobody seeded still says so, rather than falling silent: `reused 0`
    # is what tells a reader the count was checked and not merely unmentioned.
    assert "response=fresh 3 / reused 0" in block, block
    assert "refusal=fresh 0 / reused 0" in block, block
    # And the line naming where they came from survives underneath.
    assert "seeded from a prior run, not bought here: " in card
    assert "from a prior run at abcdef123456" in card


def test_the_card_carries_the_row_for_the_five_classes(built):
    card = scorecard([built["run"]], built["scores"], built["labels"],
                     protected_verdict(built["labels"], built["run"].files), [],
                     corpus_files=len(IDS), seconds=1.0)
    row = next(line for line in card.splitlines() if line.startswith("ROW (128)"))
    assert row_128([built["run"]], built["labels"]) in row
    # `104` §14.5's row is untouched beside it.
    assert any(line.startswith("ROW (104)") for line in card.splitlines())
