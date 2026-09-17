# tests/integration/test_site_g_counts_a_call_that_never_answered.py
"""`104` §18.96: a call that never came back is not a model declining to answer.

**The defect, measured on the owner's own run.** Run 21 walked 371 files and the
screen said 173 were given their own situation and the rest were "asked and left
alone: a model was asked and named no situation it could cite". Fifty-four of
those files had no such thing happen to them. The `llm_call_failure` rows for that
run name what did: fifty APIConnectionError, three body timeouts, one connect
timeout. The judge never saw those files. The screen said it had read them and had
nothing to say.

That is the failure mode the owner named in as many words -- a screen claiming
more than the run supports -- and it is worse than a wrong number, because the two
readings ask a person to do opposite things. A judge that read a file and could not
place it is a file that needs a person. A call that dropped on the network is a
file that needs the run again. One line told a person the first about fifty-four
files that were the second.

**Both stages, because the hole is in both.** The kind stage and the level stage
each end at `situation is None` and each counted every road to it as a decline.

NO NETWORK AND NO OLLAMA. The stub HTTP server of `test_local_model_fact_pass`
answers on loopback; here its site-G answer raises instead of replying, so the
connection closes with nothing on it and the client sees exactly what a dropped
call looks like from inside the product.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import cli  # noqa: E402
from test_site_g_end_to_end import _rows, _run, _decline  # noqa: E402


def _never_answers(_dossier: dict) -> str:
    """The stub drops the connection instead of replying.

    A `RuntimeError` out of the handler closes the socket with no response on it,
    which is what `readers.model_ollama` reports as a failed call and what the
    fifty APIConnectionError rows of run 21 were.
    """
    raise RuntimeError("the stub is standing in for a dropped connection")


def test_a_dropped_call_is_counted_apart_from_a_decline(tmp_path, monkeypatch):
    """`104` §18.96 stated as an assertion, at the kind stage.

    SABOTAGE: collapse the two arms of `if situation is None` in
    `ask_the_situation` back into one `declined += 1`. The first assertion goes
    red, and with it the only thing on the screen that tells a person whether to
    call the judge again or to answer for the file themselves.
    """
    _database, report, stub = _run(tmp_path, monkeypatch, _never_answers)

    said = " ".join(report.split())
    no_answer = cli.SITUATION_SENTENCE["no_answer_returned"]
    declined = cli.SITUATION_SENTENCE["declined"]

    assert f"0 {declined[:30]}" in said, (
        "a call that never came back was counted as a model declining to answer, "
        "which is `104` §18.96 back in the product")
    assert f"0 {no_answer[:30]}" not in said, (
        "no file was counted as a call that never answered, so either the stub "
        "answered after all or the counter is not wired")


def test_a_real_decline_is_still_a_decline(tmp_path, monkeypatch):
    """The other half of the split, or the fix would be a counter that eats both.

    SABOTAGE: count every `situation is None` as `no_answer_returned`. This goes
    red: a judge that read the menu and named none it could cite is the file a
    person has to answer for, and it must keep saying so.
    """
    _database, report, stub = _run(tmp_path, monkeypatch, _decline)

    said = " ".join(report.split())
    no_answer = cli.SITUATION_SENTENCE["no_answer_returned"]
    declined = cli.SITUATION_SENTENCE["declined"]

    assert f"0 {no_answer[:30]}" in said, (
        "a model that answered and declined was counted as a call that never "
        "came back")
    assert f"0 {declined[:30]}" not in said, (
        "no file was counted as declined, so the declining stub never reached "
        "the site")


def test_the_dropped_call_left_a_failure_row_the_screen_can_be_checked_against(
        tmp_path, monkeypatch):
    """The number on the screen has a table behind it.

    `104` §17.2 is what a number with no provenance costs. A person told "N calls
    never answered" can go and read why each one did not, and that is the whole
    difference between this line and the one it replaces.

    SABOTAGE: report the count without the call ever recording a failure, and this
    goes red -- the screen would again be the only witness to itself.
    """
    database, _report, _stub = _run(tmp_path, monkeypatch, _never_answers)

    rows = _rows(database,
                 "SELECT failure_class FROM llm_call_failure")
    assert rows, (
        "no failure row was written for a call that never came back, so the "
        "count on the screen cannot be checked against anything")
