# tests/integration/test_a_packet_question_costs_no_standing_answer.py
"""`00` amendment 32, over a real database that has accepted packets in it.

Amendment 32 asks the situation once per ACCEPTED GROUP instead of once per file,
and a per-group key is a NEW key. Amendment 28 already recorded what that costs if
it is got wrong, in the strongest words in the document: *"A reader that looks only
for the new key silently loses every answer they have already given -- and no test
would catch it, because the fixtures write both halves."*

**WHAT THIS FILE PINS, AND WHAT IT HONESTLY DOES NOT.**

It pins two things and each is a test below:

1. **THE PREMISE OF THE WHOLE AMENDMENT.** P9 accepts groups inside
   `run_production_p8_p11`, which is below the whole of `downstream` -- so a run
   can only ever see the packets an EARLIER run accepted. That is only true
   because `PLAN_VERSION` is a constant of this command, and if it ever stops
   being one the per-packet question becomes dead code on every run, silently.
   So the packet map's own expression -- the enumeration and the per-file read the
   run uses, verbatim -- is run against the database a real run produced.
2. **THE THREE THINGS THE CHANGE MUST NOT COST**, end to end: a standing answer
   under the OLD key still settles its branch, the unanswered branch's question is
   still printed at a key the person can type, and the coverage arithmetic still
   closes over every file.

**IT DOES NOT PIN THE FALLBACK READ, AND SAYING SO IS THE POINT.** Sabotaging
`the_situation_chosen_for` to read the packet key alone leaves every test in this
file GREEN -- measured, not assumed. The reader amendment 32 changes is reached
only for a file something NAMED A KIND for, which offline is nobody: site G does
not run under `offline` and this corpus never reaches it. The fallback is pinned
where it can bite, in
`tests/p6/test_p6_the_situation_question_is_asked_once_per_accepted_group.py`,
whose three tests DO go red under that sabotage. A SABOTAGE line that does not
sabotage is worse than none, so this file claims only what it can show.

**GREEN BEFORE THE CHANGE AND AFTER IT, ON PURPOSE.** These are the things the
change must not cost, and a preservation test that went red first would be testing
the change rather than the preservation.

The corpus and the two-step are `test_an_unsettled_default_still_builds_the_rest`'s,
deliberately: it is the fixture that already holds a settled branch beside an
unsettled default, which is exactly the pair this has to keep true of each other.
"""
from __future__ import annotations

import io
import sqlite3
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import cli  # noqa: E402
from grouping.store import current_group  # noqa: E402
from grouping.vocabulary import ACCEPTED  # noqa: E402
from test_an_unsettled_default_still_builds_the_rest import (  # noqa: E402
    ANSWER_CAREER, TWO_LIVES,
)


def _corpus(root: Path) -> Path:
    corpus = root / "holder" / "corpus"
    corpus.mkdir(parents=True)
    for name, body in TWO_LIVES.items():
        (corpus / name).write_text(body)
    return corpus


def _run(corpus: Path, database: Path, *extra: str) -> tuple[int, str]:
    out = io.StringIO()
    code = cli.main([str(corpus), "--user", "t", "--database", str(database),
                     *extra], out=out)
    return code, out.getvalue()


def _open(database: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(f"file:{database}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    return conn


def _counts(database: Path) -> dict[str, int]:
    conn = _open(database)
    try:
        return {table: conn.execute(f"SELECT count(*) FROM {table}").fetchone()[0]
                for table in ("tree_nodes", "group_acceptance",
                              "placement_decisions")}
    finally:
        conn.close()


@pytest.fixture
def answered_then_run_again_over_accepted_packets(tmp_path):
    """Three runs: ask, answer and accept, then run again over the acceptances.

    The THIRD run is the one this file is about: it is the first run in which any
    file of this corpus has a packet at all while its situation is being read.
    """
    corpus = _corpus(tmp_path)
    database = tmp_path / "holder" / "plan.sqlite"
    _run(corpus, database)
    _run(corpus, database, *ANSWER_CAREER, "--accept-groups")
    code, report = _run(corpus, database, "--accept-groups")
    return code, report, database


def test_a_packet_an_earlier_run_accepted_is_a_packet_this_run_can_ask_about(
        answered_then_run_again_over_accepted_packets):
    """THE PREMISE, and the one architectural fact amendment 32 rests on.

    P9 accepts below the whole of `downstream`, so the questions are minted before
    any group of THIS run exists. The per-packet question is therefore asked about
    packets an EARLIER run accepted -- which works only because `PLAN_VERSION` is a
    constant of this command, so an acceptance recorded last run is accepted as of
    this one.

    Asserted through the run's own expression, verbatim: the composition root's
    enumeration, filtered to group-level rows that are accepted, then
    `accepted_memberships_of` per file and the same display name the closing
    screen uses. A file of this corpus is in a named packet, so the loops have
    something to ask about.

    SABOTAGE: mint `PLAN_VERSION` per run, or filter the enumeration by
    `membership_id IS NOT NULL`. The map comes back empty, every question reverts
    to the per-kind one, and amendment 32 is built and dead -- which is exactly the
    failure no other test in this repository would notice.
    """
    _code, _report, database = answered_then_run_again_over_accepted_packets
    conn = _open(database)
    try:
        accepted = tuple(dict.fromkeys(
            row.group_id
            for row in cli.AcceptedGroupEnumeration(conn).accepted(
                cli.PLAN_VERSION)
            if row.membership_id is None and row.acceptance == ACCEPTED))
        assert accepted, (
            "an earlier run accepted groups and this run can see none of them, "
            "so no question can ever be asked once per accepted group")
        held = {
            file_id: cli.accepted_memberships_of(conn, file_id,
                                                 accepted=accepted)
            for file_id, _hash in conn.execute(
                "SELECT file_id, content_hash FROM files")}
        in_a_packet = {file_id: groups
                       for file_id, groups in held.items() if groups}
        assert in_a_packet, (
            f"{len(accepted)} packets were accepted and no file is in one: "
            "the map amendment 32 asks through would be empty on every run")
        named = {(current_group(conn, groups[0]).display_label or groups[0])
                 for groups in in_a_packet.values()}
    finally:
        conn.close()

    assert all(name and isinstance(name, str) for name in named), named


def test_the_standing_answer_under_the_old_key_still_settles_its_branch(
        answered_then_run_again_over_accepted_packets):
    """AMENDMENT 28'S RULING, over a database that now has packets in it.

    `situation:career=career.recruiting` was recorded on the second run under the
    BARE KIND, which is where every answer in the owner's live database is filed.
    The third run reads it while packets exist, and the settled branch still gets
    its folders and its placements.

    SABOTAGE: change the signature of `_the_situation_the_person_chose` without
    keeping its kind-scoped read, or let the packet map raise on a database with
    acceptances in it. The career branch goes unsettled and both counts fall to
    zero.
    """
    code, report, database = answered_then_run_again_over_accepted_packets
    counts = _counts(database)

    assert code == 0, report
    assert counts["tree_nodes"] > 0, (
        f"a branch the person answered for has folders, and this run built "
        f"none: {counts}")
    assert counts["placement_decisions"] > 0, (
        f"a branch the person answered for reaches destinations: {counts}")


def test_the_unanswered_branchs_question_is_still_printed_at_its_own_key(
        answered_then_run_again_over_accepted_packets):
    """THE QUESTION IS STILL PRINTED, and at a key the person can type.

    `academic` is the default and nobody has answered for it. Amendment 32 must
    not pay for its saving by asking one question fewer, and the line the screen
    tells them to type is the line the reader reads.

    SABOTAGE: give the branch question a packet key. The printed line names
    something no `--answer` of theirs will match, which is the failure amendment
    28 was ruled against, one layer up.
    """
    _code, report, _database = answered_then_run_again_over_accepted_packets
    flat = " ".join(report.split())

    assert "Which of these is academic?" in flat, report
    assert "--answer situation:academic=" in flat, report


def test_no_file_is_dropped_once_the_packets_exist(
        answered_then_run_again_over_accepted_packets):
    """COVERAGE IS SACRED, read off the run's own arithmetic.

    Ten files went in and the coverage block accounts for ten. A file whose packet
    nobody asked about, or whose packet swallowed it out of the kind's question,
    shows up here as a file the sum cannot place.

    SABOTAGE: drop the `None` residue from `groups_of_files_still_open`. Every
    ungrouped file stops being asked anything and the arithmetic stops closing.
    """
    _code, report, _database = answered_then_run_again_over_accepted_packets

    assert "Coverage: 10 files indexed." in report, report
    assert "= 10, and every file is on exactly one line above." in report, report
