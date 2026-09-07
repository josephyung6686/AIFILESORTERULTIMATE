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
import pathlib
import sqlite3
import subprocess

import pytest

from tools.groundtruth import reuse as reuse_module
from tools.groundtruth.reuse import (
    ReuseRefused, prior_database, refuse_unless_seedable, seed, spend,
    wire_handle_key_file,
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


def _scanned(path: Path):
    """A database holding the corpus as a run would have recorded it.

    Scanned rather than invented, because the whole of R-123's remaining work is
    the translation from one database's `file_id` to another's, and a fixture that
    made those ids up would test the copier while pretending to test the
    translation.
    """
    sys.path.insert(0, str(ROOT / "src"))
    from database_agent.db import open_database

    conn = open_database(path)
    reuse_module._scan_the_corpus(conn, CORPUS)
    from llm_harness.schema import create_llm_schema
    create_llm_schema(conn)
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


def _dimensions(subject: str) -> dict:
    """All nine terms `store.CALL_IDENTITY_DIMENSIONS` names, none extra.

    Spelled in full rather than stubbed, because `call_identity` refuses a mapping
    over a different set of terms and the seeder recomputes the digest through it:
    a fixture with a short mapping would be testing a path the product forbids.
    """
    return {"call_site": "A_fact", "content_hash": "a-hash",
            "extractor_versions": [["text.structured", "1"]],
            "model_id": "a-model", "plan_version": None, "policy": "{}",
            "prompt_fingerprint": "a-fingerprint", "schema_id": ["academic"],
            "subject_ref": subject}


def _identity(conn, *, identity: str, dossier: str, subject: str) -> None:
    conn.execute(
        "INSERT INTO llm_call_identity (identity_id, dossier_id, call_site, "
        "subject_ref, dimensions, observed_at) VALUES (?, ?, 'A_fact', ?, ?, 'T')",
        (identity, dossier, subject, json.dumps(_dimensions(subject))))


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


#: Two files of the fixture corpus the prior run is pretended to have answered
#: about, and one path that is not in it at all.
ANSWERED = ("Coursework/PHYS 1403 homework 2.txt", "Coursework/PHYS 1403 syllabus.txt")
GONE = "Coursework/a file this corpus does not have.txt"


@pytest.fixture()
def prior(tmp_path) -> Path:
    """A prior run's out directory: one database with answers and with sentinels.

    Two dossiers carry an identity and are the answers a reuse is decided from. A
    third carries none -- which is what a refusal, a call failure and a pre-call
    abstention leave behind -- and must not travel. A fourth is about a file this
    corpus does not have, and must not travel either.
    """
    directory = tmp_path / "prior"
    directory.mkdir()
    # Every real out directory has one: `cli.wire_handle_key_for` mints it the
    # first time anything opens a database beside it, and `104` R-127 makes the
    # seeder carry it forward, because the answers here name their evidence
    # through handles keyed by it. These fixtures build their databases by hand
    # and so would leave the directory in a state no run can produce.
    wire_handle_key_file(directory).write_bytes(bytes(range(32)))
    conn = _scanned(prior_database(directory, SITUATION))
    try:
        ids = {pathlib.Path(row["current_path"]).relative_to(CORPUS).as_posix():
               row["file_id"]
               for row in conn.execute("SELECT current_path, file_id FROM files")}
        for number, relative in enumerate(ANSWERED, start=1):
            subject = ids[relative]
            _dossier(conn, f"dossier-{number}", subject)
            _identity(conn, identity=f"identity-{number}",
                      dossier=f"dossier-{number}", subject=subject)
            _verdict(conn, f"dossier-{number}", "term")
            _verdict(conn, f"dossier-{number}", "work_type")
        # An answer about a file this corpus does not have. Its identity cannot be
        # translated, so neither it nor anything under it may travel.
        _dossier(conn, "dossier-gone", "a-file-id-from-another-corpus")
        _identity(conn, identity="identity-gone", dossier="dossier-gone",
                  subject="a-file-id-from-another-corpus")
        _verdict(conn, "dossier-gone", "term")
        # No identity row: the file was refused at the door, or the call failed.
        _dossier(conn, "dossier-no-identity", ids[ANSWERED[0]])
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

    given = seed(fresh, prior_database(prior, SITUATION), corpus=CORPUS)

    assert given.answers == 2
    assert given.rows == {"llm_call_identity": 2, "llm_dossier": 2,
                          "llm_response": 2, "llm_verdict": 5,
                          "llm_verdict_supersession": 1}
    assert given.responses == 2
    # The answer about a file this corpus does not have.
    assert given.skipped == 1


def test_the_identity_is_recomputed_for_the_file_id_this_database_will_use(
        prior, tmp_path):
    """The whole of what R-123 needed beyond the copy.

    `subject_ref` is the per-database `file_id`, so a copied identity is under a
    digest this run will never compute. The seeder scans first, learns what this
    database calls each file, rewrites the term and asks the PRODUCT's own
    `call_identity` for the digest -- never editing the stored one, because the
    mapping is stored beside the digest exactly so the two can be checked against
    each other.
    """
    sys.path.insert(0, str(ROOT / "src"))
    from llm_harness.store import call_identity

    fresh = tmp_path / "fresh.sqlite"
    seed(fresh, prior_database(prior, SITUATION), corpus=CORPUS)

    mine = {pathlib.Path(row["current_path"]).relative_to(CORPUS).as_posix():
            row["file_id"]
            for row in _rows(fresh, "SELECT current_path, file_id FROM files")}
    seeded = _rows(fresh, "SELECT identity_id, subject_ref, dimensions "
                          "FROM llm_call_identity")
    assert {row["subject_ref"] for row in seeded} == {
        mine[relative] for relative in ANSWERED}
    for row in seeded:
        dimensions = json.loads(row["dimensions"])
        assert dimensions["subject_ref"] == row["subject_ref"]
        assert call_identity(dimensions) == row["identity_id"], (
            "the stored digest must be the one the product computes from the "
            "stored mapping, or nothing can ever check it")
    # And the prior's own ids are gone: a digest under them is one nothing will
    # ever look up, which is the defect this closes.
    assert {"identity-1", "identity-2"}.isdisjoint(
        {row["identity_id"] for row in seeded})


def test_an_answer_about_a_file_this_corpus_does_not_have_is_left_behind(
        prior, tmp_path):
    """With everything under it, so no seeded row can name a file that is absent."""
    fresh = tmp_path / "fresh.sqlite"

    given = seed(fresh, prior_database(prior, SITUATION), corpus=CORPUS)

    assert given.skipped == 1
    assert not _rows(fresh, "SELECT 1 FROM llm_dossier "
                            "WHERE dossier_id = 'dossier-gone'")
    assert not _rows(fresh, "SELECT 1 FROM llm_verdict "
                            "WHERE dossier_id = 'dossier-gone'")
    here = {row["file_id"] for row in _rows(fresh, "SELECT file_id FROM files")}
    for table in ("llm_call_identity", "llm_dossier"):
        for row in _rows(fresh, f"SELECT subject_ref FROM {table}"):
            assert row["subject_ref"] in here, (
                f"{table} names a file this database does not have")


def test_a_dossier_no_identity_answered_for_is_not_copied(prior, tmp_path):
    """A refusal, a call failure and a pre-call abstention record no identity.

    R-109 promises those are asked again, because each is a transient state -- a
    denied release, an exhausted budget, a provider that hung up -- and carrying one
    forward would turn it into a permanent silence about the file. The dossier
    filter is what keeps that promise here, rather than a second rule about it.
    """
    fresh = tmp_path / "fresh.sqlite"

    seed(fresh, prior_database(prior, SITUATION), corpus=CORPUS)

    assert {row["dossier_id"] for row in
            _rows(fresh, "SELECT dossier_id FROM llm_dossier")} == {
        "dossier-1", "dossier-2"}
    assert not _rows(fresh, "SELECT 1 FROM llm_verdict "
                            "WHERE dossier_id = 'dossier-no-identity'")


def test_a_supersession_is_copied_only_when_both_its_verdicts_are(prior, tmp_path):
    """So the copy can never hold a reference to a row that is not in it."""
    fresh = tmp_path / "fresh.sqlite"

    seed(fresh, prior_database(prior, SITUATION), corpus=CORPUS)

    assert [row["supersession_id"] for row in
            _rows(fresh, "SELECT supersession_id FROM llm_verdict_supersession")] == [
        "s-copied"]


def test_nothing_about_placement_answers_consent_or_plan_versions_is_copied(
        prior, tmp_path):
    """The list this asserts against is the reason the database is fresh at all."""
    fresh = tmp_path / "fresh.sqlite"

    seed(fresh, prior_database(prior, SITUATION), corpus=CORPUS)

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
    given = seed(fresh, prior_database(prior, SITUATION), corpus=CORPUS)
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
    # The whole sentence, not its opening. It has three times said something the
    # code then stopped doing -- once promising a saving the key could not deliver,
    # once saying the MODEL line counted seeded rows after it had been changed not
    # to, and once saying it counted only what the run bought after R-128 made it
    # print both halves.
    assert ("scorecard's MODEL line splits every count into fresh and reused, and "
            "names the seeded rows beneath it") in completed.stdout
    # Seeded is what it was handed, reused is what it therefore did not ask, and
    # called is what it paid for anyway. Three numbers rather than one, because
    # "reused 2" alone cannot be told from a run that dropped every file. The
    # fourth appears only when there is one: the prior holds an answer about a
    # file this corpus does not have, and a person deciding whether to trust a
    # cheap rerun needs to know the corpus moved on.
    assert "seeded 2, 1 not in this corpus, reused 0, called 0" in completed.stdout
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


def _model_block(card: str) -> str:
    """The whole MODEL block on one string, continuation lines included.

    R-128 puts `fresh N / reused M` on every one of the eight tables, which no
    longer fits a single 78-column line, so `report._packed` carries the rest onto
    indented continuations. A test that read only the line beginning `MODEL` would
    silently stop asserting anything about the tables that moved onto line two --
    which on this card are `response` and `verdict`, the two the money is in.
    """
    lines = card.splitlines()
    start = next(i for i, line in enumerate(lines) if line.startswith("MODEL"))
    block = [lines[start]]
    for line in lines[start + 1:]:
        if "=fresh " not in line:
            break
        block.append(line)
    return " ".join(part.strip() for part in block)


def _score(out: Path, labels: Path, *extra: str):
    return subprocess.run(
        [sys.executable, "-m", "tools.groundtruth", "--corpus", str(CORPUS),
         "--labels", str(labels), "--out", str(out), "--workers", "1", "--force",
         *extra],
        cwd=ROOT, capture_output=True, text=True)


def test_the_scorecard_never_counts_a_seeded_row_as_a_call_somebody_paid_for(
        prior, tmp_path):
    """`104` R-123: two lines, never one total, and the difference is money.

    The seeded rows are in the same tables the run writes, so a single MODEL total
    would report a rerun that spent nothing as one that spent everything again --
    exactly the number a person reads to decide whether the rerun was worth it.
    And `report.py` reads an empty `llm_dossier` as "no model was configured": a
    seeded dossier is a record of a call an EARLIER run made, so counting it there
    would put three blocked-file numbers under a heading that exists to say none
    of them is a fact about the files.

    This run is offline -- no model is configured for it -- so everything under
    MODEL is seeded and nothing is its own, which is the sharpest form of the test.
    """
    labels = tmp_path / "labels.json"
    labels.write_text(json.dumps(LABELS), encoding="utf-8")
    out = tmp_path / "out"

    completed = _score(out, labels, "--reuse-answers-from", str(prior))

    assert completed.returncode in (0, 1), completed.stderr
    card = (out / "scorecard.txt").read_text(encoding="utf-8")
    assert "seeded from a prior run, not bought here: " in card
    assert "dossier=2" in card and "verdict=5" in card and "response=2" in card
    # R-128: the same two numbers, now on the MODEL line itself. `fresh 0` is this
    # offline run's own spend and `reused` is what it was handed, and the assertion
    # is on BOTH halves of one part: a line that said `fresh 0` while dropping the
    # reused count would pass a test written on the fresh half alone, and that is
    # the reading -- "nothing happened here" -- R-123 exists to make impossible.
    assert "dossier=fresh 0 / reused 2" in _model_block(card)
    assert "verdict=fresh 0 / reused 5" in _model_block(card)
    assert "no model was configured for these runs" in card


def test_score_only_still_knows_which_rows_were_seeded(prior, tmp_path):
    """Which is the whole reason the count is written beside the database.

    `--score-only` re-reads databases a previous run left in `--out`, and it is
    what a person uses while changing the scoring rules. Without the note it would
    read every seeded row as a call this project paid for, months after the run
    that was handed them.
    """
    labels = tmp_path / "labels.json"
    labels.write_text(json.dumps(LABELS), encoding="utf-8")
    out = tmp_path / "out"
    seeded_first = _score(out, labels, "--reuse-answers-from", str(prior))
    assert seeded_first.returncode in (0, 1), seeded_first.stderr

    again = _score(out, labels, "--score-only")

    assert again.returncode in (0, 1), again.stderr
    card = (out / "scorecard.txt").read_text(encoding="utf-8")
    assert "seeded from a prior run, not bought here: " in card
    assert "no model was configured for these runs" in card


def test_one_dossier_asked_of_two_models_is_two_answers_and_not_one(prior, tmp_path):
    """`model_id` is a dimension of the identity and is not in the dossier's bytes.

    So the same file asked of two models is one dossier and TWO identities -- and
    that is the rerun this flag exists for, which makes it the worst case to
    under-report. Counting dossiers as answers would say "seeded 1" for two
    answers, and a person comparing it with the reuse count would find the
    scoreboard short by one and have no way to tell which.
    """
    conn = sqlite3.connect(prior_database(prior, SITUATION))
    dimensions = _dimensions(_rows(
        prior_database(prior, SITUATION),
        "SELECT subject_ref FROM llm_call_identity WHERE identity_id = 'identity-1'"
    )[0]["subject_ref"])
    dimensions["model_id"] = "a-second-model"
    conn.execute(
        "INSERT INTO llm_call_identity (identity_id, dossier_id, call_site, "
        "subject_ref, dimensions, observed_at) "
        "VALUES ('identity-1b', 'dossier-1', 'A_fact', ?, ?, 'T')",
        (dimensions["subject_ref"], json.dumps(dimensions)))
    conn.commit()
    conn.close()
    fresh = tmp_path / "fresh.sqlite"

    given = seed(fresh, prior_database(prior, SITUATION), corpus=CORPUS)

    assert given.answers == 3
    assert given.rows["llm_call_identity"] == 3
    assert _count(fresh, "llm_dossier") == 2, "still two dossiers, not three"


def test_a_prior_whose_files_table_cannot_be_matched_against_is_refused(
        prior, tmp_path):
    """The `llm_*` comparison says nothing about `files`, and translation needs it.

    Checked with the other refusals rather than found in a worker thread: by then
    the situation's database has been deleted and the refusal arrives after the
    thing it was protecting.
    """
    conn = sqlite3.connect(prior_database(prior, SITUATION))
    conn.execute("ALTER TABLE files RENAME COLUMN content_hash TO was_content_hash")
    conn.commit()
    conn.close()

    with pytest.raises(ReuseRefused) as refused:
        refuse_unless_seedable(prior, [SITUATION], out_dir=tmp_path / "out",
                               score_only=False)
    assert "`files` table has no content_hash" in str(refused.value)
    assert "Nothing has been run" in str(refused.value)


def test_a_situation_whose_seeding_fails_does_not_take_the_others_down(
        prior, tmp_path, monkeypatch):
    """One situation, not the scoreboard.

    Before R-123 nothing in `one()` could raise -- `subprocess.run` captures
    whatever the run does. Seeding is real work in the pool's own thread, so an
    exception would come out of `future.result()` and lose every other situation's
    result, after their databases had already been deleted.
    """
    import tools.groundtruth.run as run_module

    def explode(*_args, **_kwargs):
        raise OSError("the disk went away mid-scan")

    monkeypatch.setattr(run_module, "seed", explode)

    results = run_situations(CORPUS, [SITUATION], tmp_path / "out", workers=1,
                             load_ceiling=0.0, force=True,
                             reuse_answers_from=prior)

    assert results[0].exit_code == 1
    assert "seeding failed, and the run was not started" in results[0].stderr
    assert "the disk went away mid-scan" in results[0].stderr


def test_a_seeded_row_can_be_traced_to_the_run_and_the_commit_it_came_from(
        prior, tmp_path):
    """A count nobody can trace is a number a reader has to take on trust.

    This one is about money somebody either did or did not spend, so the sidecar
    and the scorecard both name the prior directory and the commit that produced
    it. The commit has to come from the scoreboard, because the product's own
    database records none: `cli.COMPONENT_VERSION` is a hand-written string and
    `run_manifest` belongs to P2's eval harness.
    """
    import subprocess as sp

    from tools.groundtruth.reuse import provenance_note, write_provenance

    labels = tmp_path / "labels.json"
    labels.write_text(json.dumps(LABELS), encoding="utf-8")
    # The prior directory was written by a scoreboard run, so it carries the note.
    write_provenance(prior)
    head = sp.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"],
                  capture_output=True, text=True).stdout.strip()
    out = tmp_path / "out"

    completed = _score(out, labels, "--reuse-answers-from", str(prior))

    assert completed.returncode in (0, 1), completed.stderr
    # The run this one produced says what wrote it, for whoever seeds from IT.
    assert json.loads(provenance_note(out).read_text(
        encoding="utf-8"))["commit"] == head
    note = json.loads(
        (out / f"{SITUATION.replace('.', '_')}.seeded.json").read_text(
            encoding="utf-8"))
    assert note["from"] == str(prior)
    assert note["prior_checkout"]["commit"] == head
    assert head[:12] in note["source"] and str(prior) in note["source"]
    card = (out / "scorecard.txt").read_text(encoding="utf-8")
    assert f"from {prior} at {head[:12]}" in card


def test_a_prior_that_never_said_what_produced_it_is_labelled_as_such(
        prior, tmp_path):
    """"Commit not recorded" and silence are different facts and must look it.

    A directory written before this note existed, or outside a checkout, cannot
    say what code produced its answers. Saying so is the honest form; going quiet
    would let a reader assume the answers came from the checkout in front of them.
    """
    from tools.groundtruth.reuse import describe_source, provenance_note

    assert not provenance_note(prior).exists()
    assert describe_source(prior) == f"{prior} (commit not recorded)"

    labels = tmp_path / "labels.json"
    labels.write_text(json.dumps(LABELS), encoding="utf-8")
    out = tmp_path / "out"

    completed = _score(out, labels, "--reuse-answers-from", str(prior))

    assert completed.returncode in (0, 1), completed.stderr
    card = (out / "scorecard.txt").read_text(encoding="utf-8")
    assert f"from {prior} (commit not recorded)" in card
