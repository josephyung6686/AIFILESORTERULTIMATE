# tests/tools/test_groundtruth_file_ceiling.py
"""`104` R-175 part b: one stuck file does not hold a 199-file scoreboard run.

**What happened.** r19 ran from 05:12 to 14:03 on 10 Sep 2026 and then stopped
producing dossiers. At 14:29 the worker tree sat at 0% CPU holding an ESTABLISHED
connection to the local model server, which was itself at 0.4%. The lead killed it
at 14:35 (`104` §18.22). Nine hours of measurement over 199 files ended because one
file would not finish, and nothing in the harness noticed -- there was no number
anywhere saying how long a file is allowed to take.

**The two halves, and why the ceiling is still worth having after part (a).** Part
(a) put one deadline over the whole local call, so no CALL can outlive
`cli.LOCAL_MODEL_TIMEOUT_SECONDS` whatever the server does. That bounds the socket.
It does not bound the day a deadline turns out to miss a phase -- which is R-175
itself, discovered by a run hanging rather than by a test -- and it does not bound
work outside a call. The ceiling is the backstop, and this file holds it: a file
past its share is skipped, RECORDED, and the run goes on to the next one.

**The ceiling is derived, never typed.** `tools.groundtruth._one_run.
file_ceiling_seconds` multiplies the deployment's local patience by the local call
sites one file can be asked at in a pass, both read off `cli`. The first test below
is the pin on that: a minute count typed into this package would be a third opinion
about how slow this machine is, sitting beside two that already exist.
"""
from __future__ import annotations

import io
import sqlite3
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))
# The stub ollama and the six-file corpus are `tests/integration`'s and are
# imported rather than copied: two stubs speaking one protocol is two places for
# the protocol to drift, which is the argument `test_site_g_end_to_end` already
# makes for importing the same one.
sys.path.insert(0, str(ROOT / "tests" / "integration"))

import cli  # noqa: E402
from database_agent.db import create_schema  # noqa: E402
from llm_harness.schema import create_llm_schema  # noqa: E402
from llm_harness.authorship import CALL_REFUSED  # noqa: E402
from llm_harness.vocabulary import (  # noqa: E402
    A_FACT, G_SITUATION_SENSITIVITY, pre_call_address,
)
from model_facts import FileTookTooLong, PerFileCeiling  # noqa: E402
from readers.model_ollama import (  # noqa: E402
    BASE_URL_NAME as LOCAL_BASE_URL_NAME, MODEL_NAME as LOCAL_MODEL_NAME,
)
from test_local_model_fact_pass import (  # noqa: E402
    MODEL_ID, StubOllama, _corpus, dossier_in,
)
from tools.groundtruth._one_run import file_ceiling_seconds  # noqa: E402

CEILING = 30.0
NOW = "2026-09-10T14:35:00+00:00"


class _Hand:
    """A clock the test winds, so a ceiling can be exceeded without waiting."""

    def __init__(self) -> None:
        self.at = 0.0

    def __call__(self) -> float:
        return self.at


@pytest.fixture
def conn():
    made = sqlite3.connect(":memory:")
    made.row_factory = sqlite3.Row
    create_schema(made)
    create_llm_schema(made)
    try:
        yield made
    finally:
        made.close()


def _refusals(conn) -> list[sqlite3.Row]:
    return conn.execute(
        "SELECT * FROM events WHERE event_type = ? ORDER BY rowid",
        (CALL_REFUSED,)).fetchall()


# --- the number ------------------------------------------------------------------


def test_the_ceiling_is_the_local_patience_times_the_calls_one_file_can_make():
    """The arithmetic, and both of its terms read off the code that makes the calls.

    SABOTAGE: type a number into `file_ceiling_seconds` -- ten minutes, an hour,
    anything -- and this goes red. So does raising `LOCAL_MODEL_TIMEOUT_SECONDS`
    without the ceiling following it, which is the drift a literal would hide.
    """
    assert file_ceiling_seconds(cli) == (
        cli.LOCAL_MODEL_TIMEOUT_SECONDS * len(cli.PER_FILE_LOCAL_CALL_SITES))
    # The multiplier is the SITES and not a count somebody kept in step by hand.
    assert cli.PER_FILE_LOCAL_CALL_SITES == (G_SITUATION_SENSITIVITY, A_FACT), (
        "the per-file local call sites are site G's loop in `ask_the_situation` and "
        "site A's stage in `model_facts.fact_call_stage`; a site added to one of "
        "them and not to this tuple is a file allowed to take longer than the "
        "ceiling says it may")
    # It is the LOCAL patience: the cloud number is smaller, and a ceiling built
    # from it would cut off local files that were answering.
    assert cli.LOCAL_MODEL_TIMEOUT_SECONDS > cli.MODEL_CALL_TIMEOUT_SECONDS


def test_the_scoreboard_run_sets_the_ceiling_and_a_persons_own_run_does_not():
    """Who gets a ceiling is a decision, and it is made in one place.

    `cli.main` defaults it to `None`: a person watching their own scan can stop it.
    `tools.groundtruth._one_run` passes it, because nobody is at the screen for nine
    hours.

    SABOTAGE: default `file_ceiling_seconds` to a number in `cli.main`, and a
    person's scan starts skipping their own files on a slow morning.
    """
    import inspect

    assert inspect.signature(
        cli.main).parameters["file_ceiling_seconds"].default is None
    assert inspect.signature(
        cli.run).parameters["file_ceiling_seconds"].default is None
    source = (ROOT / "tools" / "groundtruth" / "_one_run.py").read_text("utf-8")
    assert "file_ceiling_seconds=file_ceiling_seconds(cli)" in source


# --- the skip ---------------------------------------------------------------------


def test_the_ceiling_refuses_a_file_that_burned_its_budget_and_the_row_says_so(conn):
    """The mechanism and the recording path, either side of the wiring test below.

    A file has already burned more than the ceiling -- which is what site G's turn
    looks like after a call that would not end -- so `check` refuses it, and the
    refusal goes through `store.refusal_outcome`: the same path a `MalformedRequest`
    from the builder takes, addressed to the pre-call address, carrying the class
    name and no message. A file dropped in silence reads exactly like a file the
    model had nothing to say about, which is `104` R-04's own failure.

    SABOTAGE: make `check` compare against the ceiling with `>=` reversed, or record
    the skip with a bare `return`, and one of the two halves below goes red. What
    the SEAM does with this pair is the next test's business, not this one's.
    """
    hand = _Hand()
    ceiling = PerFileCeiling(seconds=CEILING, clock=hand)

    # Site G's turn with this file: one call that would not end.
    ceiling.open_turn("f-stuck")
    hand.at += CEILING * 2
    ceiling.close_turn()

    with pytest.raises(FileTookTooLong) as over:
        ceiling.check("f-stuck")
    assert f"{CEILING:.0f}" in str(over.value)

    # And the same check, made where site A's stage makes it, writes the row.
    from llm_harness.store import refusal_outcome

    refused = refusal_outcome(conn, call_site=A_FACT, subject_ref="f-stuck",
                              error=over.value, observed_at=NOW)
    assert refused.refusal_class == "FileTookTooLong"
    rows = _refusals(conn)
    assert len(rows) == 1
    assert pre_call_address(A_FACT, "f-stuck") in rows[0]["explanation"]
    assert "FileTookTooLong" in rows[0]["explanation"]


def test_only_the_file_that_ate_its_budget_is_refused_and_only_once(conn):
    """The other 198, at the level of the ceiling's own bookkeeping.

    Two passes over three files, which is the shape `_model_fact_pass` has: site G
    walks the roster and site A walks it again. Every file is asked the first time
    round because nothing has been charged yet; the second time round exactly the
    file whose turn ran long is refused, once, and its neighbours are asked.

    SABOTAGE: charge every file the ceiling's own `seconds` in `open_turn`, or let
    `close_turn` add a turn twice, and the innocent files are refused beside the
    stuck one. This is the ARITHMETIC; the wiring is the test below.
    """
    hand = _Hand()
    ceiling = PerFileCeiling(seconds=CEILING, clock=hand)
    walked, skipped = [], []
    for file_id, turn in (("f-1", 1.0), ("f-stuck", CEILING * 3), ("f-3", 1.0)):
        ceiling.open_turn(file_id)
        try:
            ceiling.check(file_id)
        except FileTookTooLong as over:
            refusal_outcome_row(conn, file_id, over)
            skipped.append(file_id)
            continue
        walked.append(file_id)
        hand.at += turn
    ceiling.close_turn()

    # First pass: nothing has been charged yet, so every file is asked.
    assert walked == ["f-1", "f-stuck", "f-3"] and skipped == []

    # Second pass over the same files, which is what site A is: only the file that
    # ate its budget is skipped, and it is skipped once and recorded once.
    walked, skipped = [], []
    for file_id in ("f-1", "f-stuck", "f-3"):
        ceiling.open_turn(file_id)
        try:
            ceiling.check(file_id)
        except FileTookTooLong as over:
            refusal_outcome_row(conn, file_id, over)
            skipped.append(file_id)
            continue
        walked.append(file_id)
    ceiling.close_turn()

    assert skipped == ["f-stuck"], (
        "exactly the file that would not finish, and not the ones beside it")
    assert walked == ["f-1", "f-3"], "the run went on"
    assert len(_refusals(conn)) == 1


def refusal_outcome_row(conn, file_id: str, over: FileTookTooLong) -> None:
    """What the loop does with the refusal, spelled once for the test above."""
    from llm_harness.store import refusal_outcome

    refusal_outcome(conn, call_site=A_FACT, subject_ref=file_id, error=over,
                    observed_at=NOW)


def test_a_files_turns_are_summed_and_not_measured_from_when_it_was_first_seen():
    """The defect a first version of this had, pinned so it cannot come back.

    The passes are sequential over the whole roster: site G asks about all 199 files
    and only then does site A walk them again. A ceiling measured from "when this
    file was first seen" therefore reads, at site A, the length of the ENTIRE first
    pass -- hours -- and every file is over it. What is charged to a file is the time
    the run spends WITH it.

    SABOTAGE: charge the file the wall-clock since its first turn began, and the
    innocent file below is skipped along with the stuck one.
    """
    hand = _Hand()
    ceiling = PerFileCeiling(seconds=CEILING, clock=hand)

    ceiling.open_turn("f-quick")
    hand.at += 1.0
    # 198 other files take the rest of the pass.
    ceiling.open_turn("f-others")
    hand.at += CEILING * 100
    ceiling.close_turn()

    assert ceiling.spent["f-quick"] == pytest.approx(1.0)
    ceiling.check("f-quick")  # does not raise: it has had one second of the run


def test_a_ceiling_of_zero_is_refused_where_it_is_built():
    """Zero is not a ceiling; it is a run that skips every file while reporting
    that it asked. Refused at construction, which is before a folder is read.

    SABOTAGE: drop `__post_init__`'s guard and a mis-derived zero -- an empty
    `PER_FILE_LOCAL_CALL_SITES`, say -- silently measures nothing.
    """
    for bad in (0, -1.0, True, "30"):
        with pytest.raises(ValueError):
            PerFileCeiling(seconds=bad)


# --- the wiring, through `cli.main` the way `_one_run` calls it -------------------


#: `PerFileCeiling` accepts any positive number, and this one is smaller than a scan
#: can possibly spend on a file. So site G, which sees each file first and has
#: nothing charged to it yet, asks every file -- and site A, which walks the same
#: roster afterwards, finds every one of them over budget. That is a whole run's
#: worth of the skip in one six-file corpus.
IMPOSSIBLE_CEILING = 1e-9

SITUATION = "academic.coursework"
LABEL = "Coursework"


def _main_over(corpus, database, stub, monkeypatch, **injected) -> tuple[int, str]:
    monkeypatch.setenv(LOCAL_MODEL_NAME, MODEL_ID)
    monkeypatch.setenv(LOCAL_BASE_URL_NAME, stub.base_url)
    out = io.StringIO()
    code = cli.main([str(corpus), "--situation", SITUATION, "--label", LABEL,
                     "--user", "t", "--database", str(database)],
                    out=out, **injected)
    return code, out.getvalue()


def _sites_asked(stub) -> set:
    return {dossier_in(prompt).get("call_site") for prompt in stub.prompts()}


def test_the_scoreboard_skips_a_file_past_its_ceiling_and_records_it(
        tmp_path, monkeypatch):
    """SABOTAGE: THE MANDATED ONE, through `cli.main` and the real local transport.

    The run is composed exactly as `tools.groundtruth._one_run` composes it -- the
    same keyword -- carrying a ceiling no file can stay under. Site G asks about
    every file, because it sees each one first and nothing has been charged to it
    yet. Site A then walks the same roster, finds every file already over its
    budget, builds no dossier and asks nothing; what it does instead is RECORD, and
    the run finishes and reports.

    Three assertions, each a different half of R-175 part b: the run ENDS (a ceiling
    that killed the run would be the hang with a better error message), no `A_fact`
    call was made about a file that had already had its share, and the skip is on
    the screen under its own class name.

    SABOTAGE: delete the `per_file_ceiling` check from `model_facts.fact_call_stage`
    and site A's dossiers reappear and the refused line vanishes. Drop
    `per_file_ceiling=` from the `fact_call_authorities` call in `_model_fact_pass`
    and the same two go red -- the ceiling would be built and never consulted.
    """
    corpus = _corpus(tmp_path / "corpus")
    with StubOllama() as stub:
        code, said = _main_over(corpus, tmp_path / "plan.sqlite", stub, monkeypatch,
                                file_ceiling_seconds=IMPOSSIBLE_CEILING)

    assert code == 0, said
    sites = _sites_asked(stub)
    assert G_SITUATION_SENSITIVITY in sites, (
        "site G sees each file first, so nothing is charged to it yet and every "
        "file is still asked. A ceiling that skipped this too would be measuring "
        "nothing at all")
    assert A_FACT not in sites, (
        "every file had already spent more than its share at site G, so site A "
        "must build no dossier and make no call about any of them")
    assert "FileTookTooLong" in said, (
        "a skipped file is RECORDED. `104` R-04: a site that asked nothing looks "
        "exactly like a site nobody wired, and this line is the difference")


def test_the_same_corpus_with_no_ceiling_asks_site_a_about_its_files(
        tmp_path, monkeypatch):
    """The control, and without it the test above proves only that site A is quiet.

    The same corpus and the same stub, composed the way a person's own scan is --
    `file_ceiling_seconds` absent. Site A asks, and nothing is refused for time. So
    the difference between the two runs is the ceiling and not the corpus.

    SABOTAGE: give `cli.main`'s `file_ceiling_seconds` a default number. This goes
    red, which is exactly the person-facing regression it would be.
    """
    corpus = _corpus(tmp_path / "corpus")
    with StubOllama() as stub:
        code, said = _main_over(corpus, tmp_path / "plan.sqlite", stub, monkeypatch)

    assert code == 0, said
    assert A_FACT in _sites_asked(stub), said
    assert "FileTookTooLong" not in said
