# tests/integration/test_site_g_records_a_file_with_no_route.py
"""`104` §18.33 gap 25: a file site G could route nowhere now has a row.

**The defect, in the trail surface's own words.** `review_surface/trail.py` shipped
with this paragraph: *"The fact pass counts a file with no route ... and prints the
count, but writes no per-file row for it -- so this module cannot say 'no site had
a model to ask' about a particular file without inventing it."* §18.33 states it as
the one thing gap 25 could not print: *"`no_route` is an in-memory count with no
row (a row nobody has authorised)"*.

**What the row is, and why it is this one.** Site A already records its own
no-route file per file -- `model_facts.NOT_ASKED_NO_ROUTE`, one `unresolved` row
per pending field under `privacy_withheld`. Site G asks about a file's SITUATION
and not about P6 fields, so it has no pending field to write such a row about; what
it has is a call whose request was never built, and P8 already has a record for
that: `store.record_unbuilt_call_abstention`, which `placement.pipeline._not_asked`
writes for exactly this event ("one file the model is not asked about, recorded and
handed back"). `NOT_ELIGIBLE_FOR_MODEL` is that writer's own word;
`PRE_CALL_REASON_CODES` is a closed set of three and minting a fourth is a P8
vocabulary widening and the owner's.

**And the count is taken off the rows.** `00`:259's rule is that a person can see
the difference between completed and deferred work; a counter kept beside a table
is two accounts of one fact, and the screen is the one a person believes. The pass
returns `len` of the rows it wrote.

**WHY THE PASS IS CALLED DIRECTLY HERE AND NOT THROUGH `cli.main`.** `ask_the_
situation` runs only where `site_has_a_destination` is true, and a deployment with
a local model routes every file at this site -- `model_route_permitted` refuses
LOCAL to none of them. So the state this file is about is reached with a routing
that has a cloud client and no local one, which is `site_destination`'s own
"correctly configured, and it simply does not run the observe sites" seen from
inside the loop: the pass is asked what it does with a file it cannot route, which
is a question about this branch and about nothing else. The routing is
`test_per_file_model_route`'s, imported rather than rebuilt.
"""
from __future__ import annotations

import io
import sqlite3
from pathlib import Path
from types import SimpleNamespace

import pytest

import cli
from database_agent.db import open_database
from database_agent.files_table import record_file
from llm_harness.vocabulary import G_SITUATION_SENSITIVITY, NOT_ELIGIBLE_FOR_MODEL
from p1_contract import p3_basic_record
from recognition.detector import Abstention
from review_surface.trail import file_trail
from test_per_file_model_route import _both, _cloud_only

WHEN = "2026-09-10T19:30:00Z"

#: Two candidates and a reason, which is what makes a file ASKABLE at all:
#: `SituationQuestion` refuses a shortlist of one and refuses one that cannot end
#: in `none_of_these`. A file that reaches the route is what this file is about, so
#: the outcome that gets it there is stated rather than left to a detector run.
AMBIGUOUS = Abstention(reason="ambiguous", schema_id="academic",
                       detail="two schemas matched and neither corroborated",
                       tied_schema_ids=("finance",))


def _explain(_conn, _file_id: str, _content_hash: str) -> Abstention:
    return AMBIGUOUS


def _never_held(*_args, **_kwargs):
    """The rules hold nothing in this corpus, and nothing may ask them to.

    These files carry no classification record at all, so `ask_the_situation`
    never reaches for a precaution -- and a callable that raises is how that is
    asserted rather than assumed: `104` §18 gap 24's hold is another part's
    decision and this file must not be measuring it.
    """
    raise AssertionError(
        "the precaution was read for a file with no live safety-domain row")


@pytest.fixture()
def corpus(tmp_path: Path):
    """Two files in one plan database, through P1's own writer.

    `cli._bootstrap` builds every schema the pass and the trail read, which is
    what `tests/test_cli_trail.py` does for the same reason: a hand-made table is
    a shape nothing in `src/` writes.
    """
    folder = tmp_path / "corpus"
    folder.mkdir()
    database = tmp_path / "plan.sqlite"
    conn = open_database(database)
    cli._bootstrap(conn)
    roster = []
    for name, body in (("HW 3.txt", b"Problem 1. A ball is thrown upward."),
                       ("Statement.txt", b"Account summary for the quarter.")):
        path = folder / name
        path.write_bytes(body)
        file_id = record_file(conn, path, parent_folder_context="corpus",
                              mime_type="text/plain", detected_format="txt",
                              scan_state="scanned", materialized=True,
                              **p3_basic_record(path))
        content_hash = conn.execute(
            "SELECT content_hash FROM files WHERE file_id = ?",
            (file_id,)).fetchone()[0]
        roster.append((file_id, content_hash))
    conn.commit()
    yield conn, tuple(roster)
    conn.close()


def _ask(conn, roster, routing) -> cli.SituationPass:
    """The pass itself, on the one authority the no-route path reads.

    `per_file_ceiling` is `None` -- `104` R-175's ceiling is not what this file
    measures and a run that sets none is every run a person is watching -- and
    nothing else on the bundle is reached, because a file with no route is turned
    away before the gate, the budget or the transport is asked anything. A stand-in
    that carried more would be describing authorities this branch never uses.
    """
    return cli.ask_the_situation(
        conn, roster=roster, explain=_explain, precaution_of=_never_held,
        fact_authorities=SimpleNamespace(per_file_ceiling=None),
        routing=routing, prompt=cli.prompt_for(G_SITUATION_SENSITIVITY),
        now=lambda: WHEN, user_id="t")


def _rows(conn) -> list[sqlite3.Row]:
    return list(conn.execute(
        "SELECT * FROM llm_pre_call_abstention WHERE call_site = ? "
        "ORDER BY rowid", (G_SITUATION_SENSITIVITY,)))


def test_a_file_with_no_route_leaves_a_row_that_names_the_site(corpus):
    """`104` §18.33 gap 25, stated as an assertion: one file, one row.

    SABOTAGE: put `no_route += 1` back in place of the writer. Every assertion
    here goes red, and so does the trail's below.
    """
    conn, roster = corpus

    situation = _ask(conn, roster, _cloud_only())

    rows = _rows(conn)
    assert situation.no_route == len(roster), (
        "the pass could route none of these files and did not say so")
    assert [row["subject_ref"] for row in rows] == [
        file_id for file_id, _hash in roster], (
        "a file the run could not ask about is missing from the one table that "
        "records a call that did not happen")
    assert {row["reason"] for row in rows} == {NOT_ELIGIBLE_FOR_MODEL}


def test_the_printed_count_is_the_rows_and_not_a_tally_beside_them(corpus):
    """The number on the screen and the number in the table are one number.

    `104` §17.2 is what a number with no provenance costs. A counter incremented
    in the loop and a table written in the same loop are two accounts that agree
    until the day somebody adds a `continue` between them, and the screen is the
    account a person believes.

    SABOTAGE: return a separate tally from the pass. This stays green until the
    two disagree, which is the day it is worth failing.
    """
    conn, roster = corpus

    situation = _ask(conn, roster, _cloud_only())

    out = io.StringIO()
    cli._print_situation_pass(situation, files=len(roster),
                              model_id="qwen3:8b", out=out)
    said = " ".join(out.getvalue().split())
    counted = conn.execute(
        "SELECT count(*) FROM llm_pre_call_abstention WHERE call_site = ? "
        "AND reason = ?",
        (G_SITUATION_SENSITIVITY, NOT_ELIGIBLE_FOR_MODEL)).fetchone()[0]
    assert counted == len(roster)
    assert f"{counted} no target" in said, said


def test_the_trail_prints_why_the_file_was_never_asked(corpus):
    """The surface gap 25 built, reading the row gap 25 could not write.

    The sentence is `trail._asked`'s own for every pre-call abstention -- "was not
    asked at all, because ...  Nothing was assembled and nothing was sent" -- so
    site G's no-route file reads beside site A's and site C's rather than in a
    shape of its own.
    """
    conn, roster = corpus
    _ask(conn, roster, _cloud_only())

    trail = file_trail(conn, roster[0][0])

    printed = " ".join("\n".join(trail.lines).split())
    assert trail.found
    assert (f"{G_SITUATION_SENSITIVITY} was not asked at all, because "
            f"{NOT_ELIGIBLE_FOR_MODEL}") in printed, printed
    assert "Nothing was assembled and nothing was sent." in printed


def test_a_file_that_has_a_route_leaves_no_such_row(corpus):
    """The row says "no target", so a file that HAD one must not carry it.

    The same two files under a routing with a local model: this deployment can ask
    about them, so whatever else becomes of them at this site, none of them is a
    file no model could take. Without this the branch could be moved a line up and
    every file in every run would be recorded as unaskable.
    """
    conn, roster = corpus

    situation = _ask(conn, roster, _both())

    assert situation.no_route == 0
    assert _rows(conn) == []
