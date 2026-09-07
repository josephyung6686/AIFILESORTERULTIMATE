"""The backlog from `planning/103-FABLE-5.1-DIAGNOSIS.md`, as strict xfails.

Every test here fails today for the reason its marker states, and each was watched
failing on 2026-09-05 before it was committed to prose. `strict=True` means the
suite goes RED the day one of them starts passing, which is the signal to remove
its marker and close the finding in `103`. That is `84` §2's convention: the
xfail message is the backlog, not a summary of it.

Every test drives `cli.main` over a synthetic corpus in `tmp_path` and reads the
plan database back. No model is configured (`conftest` sets
`GRAPH_AGENT_NO_DOTENV=1`) and nothing here can reach the network.
"""
from __future__ import annotations

import io
import re
import sqlite3
from pathlib import Path

import pytest

import cli

SITUATION = "academic.coursework"
LABEL = "Coursework"


def _corpus(root: Path) -> Path:
    corpus = root / "holder" / "corpus"
    corpus.mkdir(parents=True)
    (corpus / "PHYS 1401 syllabus.txt").write_text(
        "PHYS 1401 Syllabus\n\nSpring 2026. Instructor: Dr. Lee. Credits: 3.\n")
    (corpus / "Lecture 08.txt").write_text(
        "Lecture 08 - Rotational Dynamics\nPHYS 1401\nTorque and angular momentum.\n")
    (corpus / "HW 3.txt").write_text(
        "Homework 3\n\nProblem 1. A ball is thrown upward...\n")
    (corpus / "Columbia Essay.txt").write_text(
        "Dear Admissions Committee at Columbia University,\nMy essay follows.\n")
    return corpus


def _run(corpus: Path, database: Path, *extra: str) -> tuple[int, str]:
    out = io.StringIO()
    code = cli.main([str(corpus), "--situation", SITUATION, "--label", LABEL,
                     "--user", "t", "--database", str(database), *extra], out=out)
    return code, out.getvalue()


def _plan_version(report: str) -> str:
    match = re.search(r"Plan version: (\S+)", report)
    assert match, report
    return match.group(1)


def _query(database: Path, sql: str, *params):
    conn = sqlite3.connect(f"file:{database}?mode=ro", uri=True)
    try:
        return conn.execute(sql, params).fetchall()
    finally:
        conn.close()


# --- 103 §18 C15: a file edited between runs leaves a ghost version ---------------

def test_a_file_edited_between_runs_can_still_be_rejected_by_its_name(tmp_path):
    """103 C15, closed: `apply_rejections` matches only versions the corpus has.

    Before the filter this refused with "names 2 files" and printed the identical
    path twice as the way to say which one was meant -- a disambiguation nobody
    could type (`84` §6).
    """
    corpus = _corpus(tmp_path)
    database = tmp_path / "holder" / "plan.sqlite"
    _run(corpus, database)
    with (corpus / "Lecture 08.txt").open("a") as handle:
        handle.write("edited after the first run\n")
    _run(corpus, database)
    code, report = _run(corpus, database, "--reject", "Lecture 08.txt:work_type=lecture")
    assert "names 2 files" not in report
    assert code == 0


def test_a_superseded_file_version_gets_no_move_plan(tmp_path):
    """103 C15, closed: the ghost is never placed, so it is never frozen.

    The old version reached `place_group` through a `memberships` row an earlier
    run wrote, not through the roster -- measured as five placement decisions for
    four files. `accepted_group_as_of` now drops a member the corpus no longer
    has, and `freeze` never sees a decision to write a plan for.
    """
    corpus = _corpus(tmp_path)
    database = tmp_path / "holder" / "plan.sqlite"
    _run(corpus, database)
    with (corpus / "Lecture 08.txt").open("a") as handle:
        handle.write("edited after the first run\n")
    _run(corpus, database, "--freeze")
    ghosts = _query(
        database,
        "SELECT COUNT(*) FROM move_plans mp JOIN files f ON f.file_id = mp.file_id "
        "WHERE f.scan_state = 'superseded_content'")
    assert ghosts[0][0] == 0


# --- 103 §18 C16: --send-set writes no review action --------------------------------

@pytest.mark.xfail(
    strict=True,
    reason="103 C16: `review_gestures` (added in 4fc44a6) has no caller, so a "
           "`--send-set` that writes a `residual_set_decisions` row writes no "
           "`review_actions` row. The audit trail of the gesture is empty.")
def test_a_residual_send_is_recorded_as_a_review_action(tmp_path):
    corpus = _corpus(tmp_path)
    scans = corpus / "scans"
    scans.mkdir()
    (scans / "IMG_0001.bin").write_bytes(bytes(range(256)) * 8)
    database = tmp_path / "holder" / "plan.sqlite"
    _run(corpus, database)
    _run(corpus, database, "--residual", "Review Later",
         "--send-set", "Not yet placed=Review Later")
    decisions = _query(database, "SELECT COUNT(*) FROM residual_set_decisions")[0][0]
    if decisions == 0:
        pytest.skip("the send was refused before recording a decision; "
                    "this corpus did not exercise the seam")
    actions = _query(database, "SELECT COUNT(*) FROM review_actions")[0][0]
    assert actions >= 1


# --- 103 §18 C7: the dossier token cap is asserted, never measured ------------------
#
# CLOSED 2026-09-07 (`104` §7 Phase 1 step 1, SF-5). Both markers removed in the
# commit that fixed them. `cli._bootstrap` now seeds
# `model.max_dossier_tokens_per_call` at `GROUPING_LIMITS.max_dossier_tokens`, and
# `cli.fact_call_authorities` supplies `measure_tokens`, so `over_dossier_ceiling`
# can fire and `model_facts._call_dependencies` measures `unreduced_fits` instead
# of asserting it. `tests/integration/test_cli_dossier_ceiling_is_measured.py`
# carries the rest of the property, including the deferral rung.


def test_the_stored_dossier_ceiling_matches_the_one_requests_carry(conn):
    from database_agent.budget import get_ceiling

    cli._bootstrap(conn)
    stored = get_ceiling(conn, "model.max_dossier_tokens_per_call")
    assert stored == cli.GROUPING_LIMITS.max_dossier_tokens


def test_the_a_fact_gate_measures_dossier_tokens(conn):
    from production import (
        folder_levels_for, load_shipped_catalogue, read_packaged_library_file,
    )
    from readers.model_routing import FAST, LOGIC, REASONING, deepseek_routing

    catalogue = load_shipped_catalogue(read_packaged_library_file)
    levels = folder_levels_for(catalogue, SITUATION)
    routing = deepseek_routing(
        api_key="not-a-key", base_url="https://example.invalid",
        model_id_of_tier={REASONING: "r", LOGIC: "l", FAST: "f"},
        tier_of_call_site=cli.TIER_OF_CALL_SITE,
        max_response_tokens=cli.MAX_RESPONSE_TOKENS, timeout_seconds=1.0)
    cli._bootstrap(conn)
    authorities = cli.fact_call_authorities(
        conn, routing=routing, scan_run_id="scan", corpus_file_count=1,
        policy_version="policy", wire_handle_key=bytes(32), schema="academic",
        folder_levels=levels, user_id="t",
        now=lambda: "2026-09-05T00:00:00+00:00")
    assert authorities.gate._measure_tokens is not None


# --- 103 §9 D1: the gate denies every ordinary file a cloud call -------------------

# CLOSED 2026-09-07 (`104` §13.2). The owner ruled D1 = BOTH, and ruled again on
# 2026-09-05 evening that the cloud half "is lifted the moment SF-1 (R-07,
# whole-document release) is closed" and does not wait for the bakeoff. SF-1 closed
# first, in this same branch, and the instrument measured what it was protecting: 20
# of the owner's Word documents would have released their entire text before it, 0
# after. The marker comes off here; the meaning lives in
# `tests/p7/test_p7_no_safety_evidence.py`, rewritten around both halves.


def test_an_ordinary_file_with_no_safety_vocabulary_may_reach_a_cloud_model():
    """An ordinary file with a releasable reading of its own words may be sent.

    The predicate's signature gained the condition the ruling names, so this passes
    it: `releasable_evidence=True` is what `Gate.release` computes for a file the
    request carries a text-bearing item for, which on the production path is every
    file `fact_call_stage` builds a call about -- it returns `()` rather than build
    one otherwise.
    """
    from privacy.denial import no_safety_evidence_denies

    assert not no_safety_evidence_denies(
        locality="cloud", releasable_evidence=True)


def test_a_file_with_nothing_releasable_still_cannot_reach_a_cloud_model():
    """The negative twin the ruling asked for, beside its positive.

    `96` §19's finding is what this keeps: a file whose entire contribution is that
    it acquired a class is a silence, and a cloud call on one turns that silence
    into a confident negative.
    """
    from privacy.denial import no_safety_evidence_denies

    assert no_safety_evidence_denies(
        locality="cloud", releasable_evidence=False)


# --- 103 §18 C17: keep-as-it-is silently un-files the branch -----------------------

@pytest.mark.xfail(
    strict=True,
    reason="103 C17: answering `branch:Coursework=keep-as-it-is` leaves the branch "
           "stating no values, so P11's direct-fact channel reaches nothing and "
           "three files that were ready to file become 'waiting for you'. The option "
           "text says only 'Nothing moves and nothing is created'. `00`:111 places at "
           "the accepted parent when the deeper level is unavailable.")
def test_keeping_a_branch_as_it_is_does_not_unfile_its_members(tmp_path):
    corpus = _corpus(tmp_path)
    database = tmp_path / "holder" / "plan.sqlite"
    _, before = _run(corpus, database)
    placed_before = _query(
        database, "SELECT COUNT(*) FROM placement_decisions WHERE outcome = 'place' "
                  "AND plan_version = ?", _plan_version(before))[0][0]
    assert placed_before >= 3, before
    _, after = _run(corpus, database, "--answer", "branch:Coursework=keep-as-it-is")
    placed_after = _query(
        database, "SELECT COUNT(*) FROM placement_decisions WHERE outcome = 'place' "
                  "AND plan_version = ?", _plan_version(after))[0][0]
    assert placed_after >= placed_before
