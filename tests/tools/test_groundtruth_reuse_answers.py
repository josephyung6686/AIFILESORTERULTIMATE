"""`104` R-123: what `--reuse-answers-from` copies, and everything it refuses.

The scoreboard deletes each situation's database at the top of its own run, and
`run.py` says why: answers, plan versions and consent are remembered between runs
against one database, so sharing one would let the first situation's decisions
reach the second. R-123 is the bill for that: R-109's reuse reads the product's own
database, so under the scoreboard it never fires, and the 7 Sep local rerun re-asked
all 172 A_fact dossiers although no file, prompt or model had changed.

This module measures the copier and the refusals. It runs no model and configures
none; the two tests that need a model to prove anything live in
`tests/integration/test_the_scoreboard_reuses_a_prior_runs_answers.py`, which is
also where the measurement that R-123 is NOT yet closed lives.
"""
from __future__ import annotations

# `tools/` is a sibling of `src/`, and `pyproject.toml` puts only `src` on the
# path. Done here rather than in a `conftest.py`, for the reason
# `test_groundtruth_end_to_end.py` gives at length: with no `__init__.py` in the
# tests tree every conftest is imported under the bare name `conftest`, and a
# conftest in this directory takes that name away from `tests/p5/conftest.py`.
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import json
import sqlite3
import subprocess

import pytest

from tools.groundtruth.reuse import (
    ReuseRefused, Seeded, prior_database, refuse_unless_seedable, seed, spend,
)
from tools.groundtruth.run import run_situations

CORPUS = Path(__file__).resolve().parent / "fixture_corpus"
ROOT = Path(__file__).resolve().parents[2]
SITUATION = "academic.coursework"

LABELS = {"files": [
    {"path": "Coursework/PHYS 1403 homework 2.txt", "group": "fixture",
     "situation": SITUATION, "destination": ["PHYS1403", "homework"],
     "expected_fields": {"subject": "PHYS1403"}},
]}

#: Tables the fresh database exists to keep out. One sentinel row goes into each of
#: the prior's, and every test that seeds asserts none of them arrived: a copier
#: that reached one of these would carry the previous situation's decisions into a
#: run whose whole purpose is not to have them.
KEPT_OUT = ("placement_decisions", "structural_answers", "cloud_consent",
            "plan_versions", "llm_call_reuse")

MARKER = "sentinel-from-the-prior-run"


def _bootstrapped(path: Path):
    """A database with every table a real run's database has."""
    sys.path.insert(0, str(ROOT / "src"))
    import cli
    from database_agent.db import open_database

    conn = open_database(path)
    cli._bootstrap(conn)
    return conn


#: The columns these tables CHECK, and a value each will accept. Everything else is
#: filled with the marker, so a copier that reached any of these tables is caught by
#: its own text rather than by a column this test happened to think of.
CONSTRAINED = {
    ("structural_answers", "state"): "confirmed",
    ("structural_answers", "answer_type"): "choice",
    ("structural_answers", "inferred"): 1,
    ("plan_versions", "state"): "draft",
    ("plan_versions", "cross_folder_moves"): 0,
}


def _stuff(conn, table: str) -> None:
    """One row in `table`, every column filled, marked so it can be recognised."""
    columns = list(conn.execute(f"PRAGMA table_info({table})"))
    names = [row["name"] for row in columns]
    values = []
    for row in columns:
        if (table, row["name"]) in CONSTRAINED:
            values.append(CONSTRAINED[(table, row["name"])])
        elif row["type"].upper().startswith("INT"):
            values.append(1)
        else:
            values.append(f"{MARKER}:{row['name']}")
    conn.execute(f"INSERT INTO {table} ({', '.join(names)}) "
                 f"VALUES ({', '.join('?' * len(names))})", values)


def _identity(conn, *, identity: str, dossier: str, subject: str) -> None:
    conn.execute(
        "INSERT INTO llm_call_identity (identity_id, dossier_id, call_site, "
        "subject_ref, dimensions, observed_at) VALUES (?, ?, 'A_fact', ?, ?, 'T')",
        (identity, dossier, subject, json.dumps({"subject_ref": subject})))


def _dossier(conn, dossier: str, subject: str) -> None:
    conn.execute(
        "INSERT INTO llm_dossier (dossier_id, call_site, subject_ref, "
        "eligibility_reason, plan_version, policy_version, reduction_rung, "
        "payload, observed_at) VALUES (?, 'A_fact', ?, 'r', NULL, 'p', 'full', "
        "'{}', 'T')", (dossier, subject))
    conn.execute(
        "INSERT INTO llm_response (response_id, dossier_id, response_bytes, "
        "model_id, prompt_fingerprint, release_audit_id, release_id, observed_at) "
        "VALUES (?, ?, ?, 'm', 'f', 1, 'rel', 'T')",
        (f"resp-{dossier}", dossier, b"{}"))


def _verdict(conn, dossier: str, field: str, *, superseded_by: str | None = None) -> str:
    verdict_id = f"{dossier}:{field}"
    conn.execute(
        "INSERT INTO llm_verdict (verdict_id, dossier_id, claim_ref, outcome, "
        "disposition, validator_version, policy_version, plan_version, payload, "
        "observed_at, supersedes, superseded_by, supersede_reason) "
        "VALUES (?, ?, ?, 'reject', 'd', 'v', 'p', NULL, '{}', 'T', NULL, ?, NULL)",
        (verdict_id, dossier, field, superseded_by))
    return verdict_id


@pytest.fixture()
def prior(tmp_path) -> Path:
    """A prior run's out directory: one database with answers and with sentinels.

    Two dossiers carry an identity and are the answers a reuse is decided from. A
    third carries none -- which is what a refusal, a call failure and a pre-call
    abstention leave behind -- and must not travel.
    """
    directory = tmp_path / "prior"
    directory.mkdir()
    conn = _bootstrapped(prior_database(directory, SITUATION))
    try:
        for number in (1, 2):
            _dossier(conn, f"dossier-{number}", f"file-{number}")
            _identity(conn, identity=f"identity-{number}",
                      dossier=f"dossier-{number}", subject=f"file-{number}")
            _verdict(conn, f"dossier-{number}", "term")
            _verdict(conn, f"dossier-{number}", "work_type")
        # No identity row: the file was refused at the door, or the call failed.
        _dossier(conn, "dossier-no-identity", "file-3")
        _verdict(conn, "dossier-no-identity", "term")
        # A re-judgement under a dossier that IS copied, and one that is not.
        old = _verdict(conn, "dossier-1", "superseded", superseded_by="dossier-1:term")
        conn.execute(
            "INSERT INTO llm_verdict_supersession (supersession_id, old_verdict_id, "
            "new_verdict_id, reason, observed_at) VALUES ('s-copied', ?, ?, 'r', 'T')",
            (old, "dossier-1:term"))
        conn.execute(
            "INSERT INTO llm_verdict_supersession (supersession_id, old_verdict_id, "
            "new_verdict_id, reason, observed_at) "
            "VALUES ('s-dangling', 'dossier-no-identity:term', 'dossier-1:term', "
            "'r', 'T')")
        # The sentinels are MARKERS and not valid records: several of these tables
        # reference rows a real run would have written first, and inventing that
        # whole graph would be inventing a run. What is under test is whether a row
        # in one of these tables can travel, and a row that travels is recognised
        # by its text whatever it references.
        conn.execute("PRAGMA foreign_keys = OFF")
        for table in KEPT_OUT:
            _stuff(conn, table)
        conn.execute("PRAGMA foreign_keys = ON")
    finally:
        conn.close()
    return directory


def _rows(database: Path, sql: str) -> list[dict]:
    conn = sqlite3.connect(database)
    conn.row_factory = sqlite3.Row
    try:
        return [dict(row) for row in conn.execute(sql)]
    finally:
        conn.close()


def _count(database: Path, table: str) -> int:
    return _rows(database, f"SELECT count(*) AS n FROM {table}")[0]["n"]


# --- what is copied ---------------------------------------------------------------


def test_the_four_tables_a_reuse_is_decided_from_are_copied(prior, tmp_path):
    fresh = tmp_path / "fresh.sqlite"

    given = seed(fresh, prior_database(prior, SITUATION))

    assert given == Seeded(
        answers=2,
        rows={"llm_call_identity": 2, "llm_dossier": 2, "llm_response": 2,
              "llm_verdict": 5, "llm_verdict_supersession": 1},
        responses=2)
    assert {row["identity_id"] for row in
            _rows(fresh, "SELECT identity_id FROM llm_call_identity")} == {
        "identity-1", "identity-2"}


def test_a_dossier_no_identity_answered_for_is_not_copied(prior, tmp_path):
    """A refusal, a call failure and a pre-call abstention record no identity.

    R-109 promises those are asked again, because each is a transient state -- a
    denied release, an exhausted budget, a provider that hung up -- and carrying one
    forward would turn it into a permanent silence about the file. The dossier
    filter is what keeps that promise here, rather than a second rule about it.
    """
    fresh = tmp_path / "fresh.sqlite"

    seed(fresh, prior_database(prior, SITUATION))

    assert {row["dossier_id"] for row in
            _rows(fresh, "SELECT dossier_id FROM llm_dossier")} == {
        "dossier-1", "dossier-2"}
    assert not _rows(fresh, "SELECT 1 FROM llm_verdict "
                            "WHERE dossier_id = 'dossier-no-identity'")


def test_a_supersession_is_copied_only_when_both_its_verdicts_are(prior, tmp_path):
    """So the copy can never hold a reference to a row that is not in it."""
    fresh = tmp_path / "fresh.sqlite"

    seed(fresh, prior_database(prior, SITUATION))

    assert [row["supersession_id"] for row in
            _rows(fresh, "SELECT supersession_id FROM llm_verdict_supersession")] == [
        "s-copied"]


def test_nothing_about_placement_answers_consent_or_plan_versions_is_copied(
        prior, tmp_path):
    """The list this asserts against is the reason the database is fresh at all."""
    fresh = tmp_path / "fresh.sqlite"

    seed(fresh, prior_database(prior, SITUATION))

    # `llm_call_reuse` is the one of the five the fresh database already has, and
    # the one most easily copied by accident: it sits beside the four that ARE
    # copied. A reuse row carried forward would report a saving this run did not
    # make. The other four tables the run has not even created yet.
    assert _count(fresh, "llm_call_reuse") == 0
    # And the general form, because a list of five is a list somebody has to keep
    # up to date: no row anywhere in the fresh database carries the marker.
    for row in _rows(fresh, "SELECT name FROM sqlite_master WHERE type = 'table'"):
        found = _rows(fresh, f'SELECT * FROM "{row["name"]}"')
        assert not any(MARKER in str(value)
                       for cell in found for value in cell.values()), (
            f"a sentinel row from the prior run reached {row['name']}")


def test_the_run_is_told_what_it_reused_and_what_it_paid_for_anyway(prior, tmp_path):
    """`spend` subtracts what was HANDED to the run from what the run sent."""
    fresh = tmp_path / "fresh.sqlite"
    given = seed(fresh, prior_database(prior, SITUATION))
    conn = sqlite3.connect(fresh)
    # One call this run made, and one question it did not ask.
    conn.execute("INSERT INTO llm_response (response_id, dossier_id, "
                 "response_bytes, model_id, prompt_fingerprint, release_audit_id, "
                 "release_id, observed_at) VALUES ('new', 'dossier-9', ?, 'm', 'f', "
                 "2, 'rel', 'T')", (b"{}",))
    conn.execute("INSERT INTO llm_call_reuse (reuse_id, identity_id, "
                 "prior_dossier_id, call_site, subject_ref, reused_fields, "
                 "observed_at) VALUES ('r', 'identity-1', 'dossier-1', 'A_fact', "
                 "'file-1', '[]', 'T')")
    conn.commit()
    conn.close()

    assert spend(fresh, given) == (1, 1)


# --- what is refused, and it is refused before anything runs ----------------------


def test_a_missing_directory_is_refused(tmp_path):
    with pytest.raises(ReuseRefused) as refused:
        refuse_unless_seedable(tmp_path / "nowhere", [SITUATION],
                               out_dir=tmp_path / "out", score_only=False)
    assert "no such directory" in str(refused.value)
    assert "Nothing has been run" in str(refused.value)


def test_a_situation_with_no_database_there_is_refused(prior, tmp_path):
    with pytest.raises(ReuseRefused) as refused:
        refuse_unless_seedable(prior, [SITUATION, "code.notebooks-experiments"],
                               out_dir=tmp_path / "out", score_only=False)
    assert "no database for code.notebooks-experiments" in str(refused.value)


def test_a_prior_whose_llm_schema_is_not_this_ones_is_refused(prior, tmp_path):
    """Half-seeding a changed schema would put rows under columns that moved."""
    conn = sqlite3.connect(prior_database(prior, SITUATION))
    conn.execute("DROP TABLE llm_verdict_supersession")
    conn.commit()
    conn.close()

    with pytest.raises(ReuseRefused) as refused:
        refuse_unless_seedable(prior, [SITUATION], out_dir=tmp_path / "out",
                               score_only=False)
    assert "llm_* schema is not this checkout's" in str(refused.value)
    assert "llm_verdict_supersession" in str(refused.value)
    assert "Nothing has been run" in str(refused.value)


def test_the_prior_directory_may_not_be_the_out_directory(prior):
    """Each run deletes its own database first, so this would destroy the prior."""
    with pytest.raises(ReuseRefused) as refused:
        refuse_unless_seedable(prior, [SITUATION], out_dir=prior, score_only=False)
    assert "is also --out" in str(refused.value)


def test_score_only_is_refused(prior, tmp_path):
    with pytest.raises(ReuseRefused) as refused:
        refuse_unless_seedable(prior, [SITUATION], out_dir=tmp_path / "out",
                               score_only=True)
    assert "--score-only" in str(refused.value)


def test_the_command_refuses_before_it_deletes_the_database_it_would_replace(tmp_path):
    """The whole reason every check is at the composition root.

    `run.py` unlinks each situation's database at the top of its own run. A
    refusal discovered inside a run would arrive after the thing it was protecting
    had already been deleted, so the out directory here has to come back untouched.
    """
    labels = tmp_path / "labels.json"
    labels.write_text(json.dumps(LABELS), encoding="utf-8")
    out = tmp_path / "out"
    out.mkdir()
    standing = out / f"{SITUATION.replace('.', '_')}.sqlite"
    standing.write_bytes(b"a database an earlier run left here")

    completed = subprocess.run(
        [sys.executable, "-m", "tools.groundtruth", "--corpus", str(CORPUS),
         "--labels", str(labels), "--out", str(out), "--workers", "1", "--force",
         "--reuse-answers-from", str(tmp_path / "nowhere")],
        cwd=ROOT, capture_output=True, text=True)

    assert completed.returncode == 2, completed.stdout
    assert "no such directory" in completed.stderr
    assert standing.read_bytes() == b"a database an earlier run left here"


# --- the flag off, and the flag on, through the command a person types ------------


def test_without_the_flag_a_fresh_database_holds_no_answer_at_all(prior, tmp_path):
    """Today's behaviour, unchanged, measured beside a prior that is full of them."""
    out = tmp_path / "out"

    results = run_situations(CORPUS, [SITUATION], out, workers=1,
                             load_ceiling=0.0, force=True)

    assert results[0].exit_code == 0, results[0].stderr
    assert (results[0].seeded, results[0].reused, results[0].calls) == (0, 0, 0)
    sys.path.insert(0, str(ROOT / "src"))
    from llm_harness.schema import TASK3_TABLES
    assert {table: _count(results[0].database, table) for table in TASK3_TABLES} == {
        table: 0 for table in TASK3_TABLES}


def test_the_flag_seeds_the_run_and_the_scoreboard_says_how_many(prior, tmp_path):
    """The command a person types, end to end, with a prior directory beside it."""
    labels = tmp_path / "labels.json"
    labels.write_text(json.dumps(LABELS), encoding="utf-8")
    out = tmp_path / "out"

    completed = subprocess.run(
        [sys.executable, "-m", "tools.groundtruth", "--corpus", str(CORPUS),
         "--labels", str(labels), "--out", str(out), "--workers", "1", "--force",
         "--reuse-answers-from", str(prior)],
        cwd=ROOT, capture_output=True, text=True)

    assert completed.returncode in (0, 1), completed.stderr
    assert f"seeding each run's answers from {prior}" in completed.stdout
    # Seeded is what it was handed, reused is what it therefore did not ask, and
    # called is what it paid for anyway. Three numbers rather than one, because
    # "reused 2" alone cannot be told from a run that dropped every file.
    assert "seeded 2, reused 0, called 0" in completed.stdout
    database = out / f"{SITUATION.replace('.', '_')}.sqlite"
    assert _count(database, "llm_call_identity") == 2
    assert _count(database, "llm_verdict") == 5
    assert _count(database, "llm_call_reuse") == 0
    # The run writes its own plan versions and its own placement decisions, so the
    # question is never "are these tables empty" -- it is whether any row in them
    # came from the prior run, and a marked row is how that is told apart.
    for row in _rows(database, "SELECT name FROM sqlite_master WHERE type = 'table'"):
        found = _rows(database, f'SELECT * FROM "{row["name"]}"')
        assert not any(MARKER in str(value)
                       for cell in found for value in cell.values()), (
            f"a sentinel row from the prior run reached {row['name']}")
