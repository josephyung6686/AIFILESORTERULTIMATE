"""`104` §18.110: a protected record is shown to no model, ever, and is filed by
the person one at a time -- and until this the product offered no way to do it.

The owner's ruling of 13 Sep (`00` amendment 2): `--file-held FILE_ID` is "keep
it here, FILE IT BY HAND". The first half existed. The second did not: once the
person kept a file, it dropped out of the closing question and no screen ever
asked what the file IS, so it had no situation, reached no branch, and the gate's
own first remedy -- `decide_locally` -- named a gesture nobody could type.

This is the person's path, in four runs, on a deployment with a cloud key and no
local model (the owner's deployment of 14 Sep):

1. the run that holds the file on the rules' word and asks keep-or-release;
2. `--file-held`: the file is kept, and the run now asks WHAT IT IS, with the
   gesture printed per file behind `--show-protected` (`planning/93`);
3. `--situation-of FILE=SITUATION`: the person's word is written
   `user_confirmed`, the branch the run partitions sees it, and the block stops
   asking;
4. a plain run: still so, with nothing retyped.

And at every step NOTHING ABOUT THE HELD FILE CROSSES THE MACHINE'S EDGE: the
stub records every subject offered to the cloud at every site, and the held
file's handle is never among them. A situation of another kind than the run's
own is chosen on purpose: the person's word outranks the branch's answer, and a
fall-through to the run's `--situation` would print the same screen for the
wrong reason.
"""
from __future__ import annotations

import io
import sqlite3
import sys
from pathlib import Path

import pytest

import cli
from facts.llm_seam import SITUATION_FIELD
from facts.states import USER_CONFIRMED
from facts.supersede import preferred_fact
from llm_harness.wire_handles import wire_handle

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE.parent / "p7"))
from test_p7_file_released import FREE_NAME, HELD_NAME, LABEL, SITUATION, _corpus  # noqa: E402
from test_a_fact_call_cache import (  # noqa: E402
    BASE_URL_NAME, CREDENTIAL_NAME, ENV, LOCAL_BASE_URL_NAME, LOCAL_MODEL_NAME,
    MODEL_NAME_OF_TIER, socket,  # noqa: F401  (the fixture, re-exported)
)

#: A situation of ANOTHER kind than the run's `academic.coursework`.
THEIR_WORD = "career.employment-records"


@pytest.fixture(autouse=True)
def _cloud_key_and_no_local_model(monkeypatch, tmp_path):
    for name in (CREDENTIAL_NAME, BASE_URL_NAME, *MODEL_NAME_OF_TIER.values(),
                 LOCAL_MODEL_NAME, LOCAL_BASE_URL_NAME):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setattr(cli, "ENV_FILE", tmp_path / "absent.env")
    for name, value in ENV.items():
        monkeypatch.setenv(name, value)


def _file_id(database, filename: str) -> str:
    conn = sqlite3.connect(f"file:{database}?mode=ro", uri=True)
    try:
        (row,) = conn.execute("SELECT file_id FROM files WHERE filename = ?",
                              (filename,)).fetchall()
        return row[0]
    finally:
        conn.close()


def _their_situation(database, file_id: str):
    conn = sqlite3.connect(f"file:{database}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    try:
        row = preferred_fact(conn, file_id=file_id, field_key=SITUATION_FIELD)
        if row is None:
            return None
        value = conn.execute(
            'SELECT canonical_value FROM "values" WHERE value_id = ?',
            (row["value_id"],)).fetchone()[0]
        return row["reliability_state"], value
    finally:
        conn.close()


@pytest.fixture()
def the_runs(tmp_path, socket, monkeypatch):
    """`cli.main` over the two-file corpus, with the `situations` mailbox each run
    filled -- the dict `main` hands `run`, read back through a spy on `cli.run`,
    because it is the one place the run writes what branch every file is under
    and the CLI prints no per-file line a test could read it off."""
    corpus = _corpus(tmp_path)
    database = tmp_path / "plan.sqlite"
    mailboxes: list[dict[str, str]] = []
    real_run = cli.run

    def spy(conn, directory, **kw):
        mailboxes.append(kw["situations"])
        return real_run(conn, directory, **kw)

    monkeypatch.setattr(cli, "run", spy)

    def once(*extra: str) -> str:
        out = io.StringIO()
        code = cli.main([str(corpus), "--situation", SITUATION, "--label", LABEL,
                         "--user", "t", "--database", str(database),
                         "--enable-cloud", *extra], out=out)
        assert code == 0, out.getvalue()
        return out.getvalue()

    return {"once": once, "database": database, "mailboxes": mailboxes,
            "socket": socket}


def test_a_kept_file_is_asked_what_it_is_and_the_persons_word_reaches_its_branch(
        the_runs):
    once, database = the_runs["once"], the_runs["database"]
    mailboxes, socket = the_runs["mailboxes"], the_runs["socket"]

    # 1. Held on the rules' word; the closing question is keep-or-release and
    #    NOT yet "what is it": a file nobody has answered for is asked one
    #    question at a time, and the second follows the first.
    said = once()
    held = _file_id(database, HELD_NAME)
    free = _file_id(database, FREE_NAME)
    assert "--release FILE_ID" in " ".join(said.split()), said
    assert "--situation-of" not in said, said
    # A held file nobody has filed falls through to the run's own situation
    # (`_the_situation_this_file_is_under`'s last arm): the run's word, not
    # the person's. Read off the run's own mailbox rather than assumed.
    assert mailboxes[-1].get(held) == SITUATION, mailboxes[-1]
    assert mailboxes[-1][free] == SITUATION

    # 2. Kept. Now the run asks what the file IS -- the count and the gesture on
    #    the plain screen, the name behind `--show-protected` (`planning/93`).
    said = once("--file-held", held)
    flat = " ".join(said.split())
    assert "--release FILE_ID" not in flat, "kept, so no longer keep-or-release"
    assert "yours to file" in flat and "--situation-of" in flat, said
    assert HELD_NAME not in said, "a protected name is never on the plain screen"
    assert "--show-protected" in said
    said = once("--show-protected")
    assert f"--situation-of '{HELD_NAME}=" in said, said
    assert mailboxes[-1].get(held) == SITUATION, "kept, and not yet named"

    # 3. The person's word: written as theirs, read by the branch, no longer asked.
    said = once("--situation-of", f"{HELD_NAME}={THEIR_WORD}")
    assert _their_situation(database, held) == (USER_CONFIRMED, THEIR_WORD)
    assert mailboxes[-1][held] == THEIR_WORD, (
        "the fact was written and the branch never saw it -- the SABOTAGE the "
        "plan warns of")
    assert mailboxes[-1][free] == SITUATION, "the other file is untouched"
    assert "--situation-of" not in said, "answered, so not asked again"
    assert "yours to file" not in said

    # 4. A plain run keeps it, with nothing retyped.
    once()
    assert mailboxes[-1][held] == THEIR_WORD
    assert _their_situation(database, held) == (USER_CONFIRMED, THEIR_WORD)

    # AND NOTHING ABOUT THE HELD FILE EVER LEFT THIS MACHINE. Every subject the
    # stub was offered, at every site, over all five runs.
    handle = wire_handle(held, key=cli.wire_handle_key_for(database))
    assert handle not in socket.subjects(), "the held file reached the wire"
    assert wire_handle(free, key=cli.wire_handle_key_for(database)) in socket.subjects(), (
        "the control: the cleared file was asked, so the stub is recording")


def test_a_word_about_no_file_or_no_situation_is_refused_by_name(the_runs):
    once = the_runs["once"]
    once()
    corpus_args = []
    for bad, expected in (
            (f"nope.txt={THEIR_WORD}", "is not a file in this plan"),
            (f"{FREE_NAME}=not.a.situation", "names no situation"),
            (f"{FREE_NAME}", "is not a situation")):
        out = io.StringIO()
        code = cli.main([str(the_runs["database"].parent / "corpus"),
                         "--situation", SITUATION, "--label", LABEL,
                         "--user", "t", "--database", str(the_runs["database"]),
                         "--enable-cloud", "--situation-of", bad, *corpus_args],
                        out=out)
        assert code != 0, (bad, out.getvalue())
        assert expected in out.getvalue(), (bad, out.getvalue())
