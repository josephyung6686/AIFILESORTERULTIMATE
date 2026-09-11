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

def test_a_residual_send_is_recorded_as_a_review_action(tmp_path):
    """103 C16, closed by `104` R-26: `--send-set` now writes `review_actions`.

    `review_gestures.py` was added by `4fc44a6` to fix exactly this and had no
    caller, so `review_surface.collect` -- the one function in the product that
    turns a person's gesture into a stored `review_action` -- was reachable from
    nothing. Audited over the owner's own folder, `review_actions` had 0 rows
    while the report on the same screen offered `--send-set "SET=AREA"` and a
    person could type it. The gesture happened; the record of it did not.

    **The set is scraped off the report rather than named here.** The marked
    version of this test hardcoded "Not yet placed" and skipped itself when no
    decision row appeared, so a removed marker could have passed on a body that
    never ran. The report prints the `--send-set` line for every set it
    surfaces; typing back what the screen printed is both what a person does and
    the only way this test cannot silently stop exercising the seam.
    """
    corpus = _corpus_with_an_unreadable_folder(tmp_path)
    database = tmp_path / "holder" / "plan.sqlite"
    _, report = _run(corpus, database, "--residual", "Review Later")
    typed = re.findall(r"--send-set '([^']+)'", report)
    assert typed, report

    code, report = _run(corpus, database, "--residual", "Review Later",
                        "--send-set", typed[0])
    assert code == 0, report
    decisions = _query(database, "SELECT COUNT(*) FROM residual_set_decisions")[0][0]
    assert decisions >= 1, report
    actions = _query(
        database,
        "SELECT action, correction_scope FROM review_actions")
    assert actions, report
    # The gesture P13 already had a name for, at the scope the composition root
    # chose: one `--send-set` files a whole set into one area without a per-file
    # look, which is `accept_bulk`, and the area is a node of this plan version.
    assert ("accept_bulk", "node") in {tuple(row) for row in actions}, actions


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


# --- 103 C21 / `104` R-40: the home answer lifts the unclassified hold -------------


def _corpus_with_an_unreadable_folder(root: Path) -> Path:
    """The shape the `home:` question exists for, and it is the smallest one.

    `IMG_0001.txt` is empty, so every text-producing extractor opens it and
    recovers nothing and it reaches P11 as `unreadable_unclassified` with no
    evidence at all. `IMG_0002.txt` is its readable-by-a-newline twin, which the
    question is NOT asked about: it is what a file nobody has said anything about
    still has to look like after the hold is lifted for the one they did.
    """
    corpus = _corpus(root)
    scans = corpus / "scans"
    scans.mkdir()
    (scans / "IMG_0001.txt").write_text("")
    (scans / "IMG_0002.txt").write_text("\n")
    return corpus


def _policies(database: Path, plan_version: str) -> dict[str, str]:
    """Filename -> the review policy its live placement decision carries."""
    return {row[0]: row[1] for row in _query(
        database,
        "SELECT f.filename, p.review_policy FROM placement_decisions p "
        # `subject_ref` is the file VERSION -- P11 addresses a decision by
        # `(plan_version, subject_ref)` and a file id alone would name two rows
        # for a file edited between runs -- so the id is its leading segment.
        "JOIN files f ON p.subject_ref LIKE 'file:' || f.file_id || ':%' "
        "WHERE p.superseded_by IS NULL AND p.plan_version = ?", plan_version)}


def _frozen_names(database: Path) -> set[str]:
    return {row[0] for row in _query(
        database,
        "SELECT f.filename FROM move_plans m JOIN files f ON f.file_id = m.file_id "
        "WHERE m.superseded_by IS NULL")}


def test_answering_where_an_unreadable_file_goes_lets_it_freeze(tmp_path):
    """`104` R-40, end to end: the one question asked about an unreadable file.

    `review_policy_for` returned `blocked_pending_user` for an unclassified
    subject before every other test, so the answer wrote a `place` decision that
    `freeze._withheld` then held as `awaiting_classification`. The person
    answered and nothing filed -- measured on this corpus as no `move_plans` row
    for the answered file at all, while the two readable files were frozen beside
    it.

    The second assertion is what makes the first honest: the hold lifts for the
    file the person named and for no other, so the twin nobody answered about is
    still not frozen.
    """
    corpus = _corpus_with_an_unreadable_folder(tmp_path)
    database = tmp_path / "holder" / "plan.sqlite"
    code, report = _run(corpus, database)
    assert code == 0, report
    assert "--answer home:scans=" in report, report

    code, report = _run(corpus, database,
                        "--answer", "home:scans=Coursework", "--freeze")
    assert code == 0, report
    frozen = _frozen_names(database)
    assert "IMG_0001.txt" in frozen, report
    assert "IMG_0002.txt" not in frozen, report


def test_the_answered_file_is_review_required_and_its_twin_is_not(tmp_path):
    """The same fact one layer down, on the record rather than on the outcome.

    `review_required` and not `auto_eligible`: naming a home is not authorising a
    move, and §6.11 keeps those apart. `blocked_pending_user` for the file nobody
    answered about, because nothing has classified it and nobody has said where it
    goes either.
    """
    corpus = _corpus_with_an_unreadable_folder(tmp_path)
    database = tmp_path / "holder" / "plan.sqlite"
    _run(corpus, database)
    code, report = _run(corpus, database, "--answer", "home:scans=Coursework")
    assert code == 0, report
    policies = _policies(database, _plan_version(report))
    assert policies.get("IMG_0001.txt") == "review_required", policies
    assert policies.get("IMG_0002.txt") == "blocked_pending_user", policies


def test_nothing_freezes_from_that_folder_when_nobody_answers(tmp_path):
    """The negative twin of the first test, with the answer taken away.

    A change that lifted the hold for every unclassified file would pass the
    first test and fail this one, and it is the failure that matters: the freeze
    would be approving moves for files nothing has looked at.
    """
    corpus = _corpus_with_an_unreadable_folder(tmp_path)
    database = tmp_path / "holder" / "plan.sqlite"
    _run(corpus, database)
    code, report = _run(corpus, database, "--freeze")
    assert code == 0, report
    frozen = _frozen_names(database)
    assert "IMG_0001.txt" not in frozen, report
    assert "IMG_0002.txt" not in frozen, report
