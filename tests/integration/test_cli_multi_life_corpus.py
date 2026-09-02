"""`74` §6 G4 -- `68`'s four corpora, run again, and the one that stopped working.

G4 is the wave's re-run rather than a build: the full suite, the same suite in a
random order, and `68-PERSONA-RERUN.md`'s four corpora through the shipped
command. Three of the four still produce a report. **The fourth -- `68`'s
"one person, three lives", the union of the other three -- ends in a traceback**,
and this is the reproduction.

`grouping.pipeline` halts a group when a stop rule fires, and it deliberately does
not record it: *"Before the dossier and before the call: a group that cannot form
should not cost either one."* The halted `Group` is still returned on the
`GroupingResult`, because the caller has to be able to say WHY nothing formed.
`cli.review_and_accept` then merges every result whose `group is not None`, and
makes the first of them the record its merged group `supersedes` -- so when the
first one is a group that never formed, `grouping.store` refuses the supersession
and the whole run dies with `RecordAbsent`.

**Why it bites the multi-life person and nobody else.** The rule that fires is
SR3, *"one high-frequency entity acts as the only bridge"* -- a hub was suppressed
and nothing else holds the graph together. That is the shape of a disk with
several unrelated lives on it. The more genuinely multi-role the person, the more
likely they are to get a traceback instead of a plan, which is the north star
exactly inverted.

**`src/cli.py` is the composition root and belongs to the lead**, so this test
names the defect rather than fixing it. The hunk is written out in
`scratchpad/waveG/CLI-PATCH.txt`. When it lands, this xfail turns into a failure
and should be unmarked, not deleted -- the run below is worth keeping either way.
"""
from __future__ import annotations

import io
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

import cli  # noqa: E402
from grouping.store import RecordAbsent  # noqa: E402

#: `68` §0's table, reduced to the smallest set that still reproduces. Ten files
#: from three of `68`'s four corpora: it is not a contrived corpus, it is the
#: multi-life one with the three files delta-debugging could remove.
MULTI_LIFE = {
    "E-Filing Receipt.txt":
        "ELECTRONIC FILING RECEIPT\n\nDocument accepted 12 March 2026. "
        "Confirmation 8841-2026. Superior Court e-filing system.\n",
    "Client Passport.txt":
        "PASSPORT\n\nSurname: ALVAREZ\nGiven names: ROSA MARIA\n"
        "Passport No: X12345678\nNationality: SPAIN\nDate of birth: 4 June 1984\n",
    "PHYS1401 Problem Set 4.txt":
        "PHYS 1401 Problem Set 4\n\nSpring 2026. Due 18 March. Show all work.\n"
        "1. A block slides down an incline...\n",
    "PHYS1401 Lecture Notes.txt":
        "PHYS 1401 Lecture Notes -- Week 7\n\nSpring 2026. Rotational dynamics.\n",
    "PHYS2801 Solution Set 2.txt":
        "PHYS 2801 Solution Set 2\n\nSpring 2026. For teaching assistants only. "
        "Prepared by the TA. Do not distribute to students before 20 March.\n",
    "PHYS2801 Grading Rubric.txt":
        "PHYS 2801 Grading Rubric -- Problem Set 2\n\nSpring 2026. Full credit "
        "for a correct free-body diagram. Partial credit as below.\n",
    "Ada Report Card.txt":
        "REPORT CARD -- Spring Term 2026\n\nStudent: Ada Whitfield\nGrade 4\n"
        "Reading: exceeds expectations. Mathematics: meets expectations.\n",
    "Sam Report Card.txt":
        "REPORT CARD -- Spring Term 2026\n\nStudent: Sam Whitfield\nGrade 2\n"
        "Reading: meets expectations. Mathematics: exceeds expectations.\n",
    "Lease Agreement.txt":
        "RESIDENTIAL LEASE AGREEMENT\n\nLandlord and Tenant agree as follows. "
        "Term: 1 June 2026 to 31 May 2027. Monthly rent payable in advance.\n",
    "Insurance Claim.txt":
        "HOMEOWNERS INSURANCE CLAIM\n\nClaim number 2026-33917. Date of loss: "
        "2 February 2026. Water damage to the kitchen ceiling.\n",
}


def _multi_life_corpus(tmp_path: Path) -> Path:
    """`68`'s multi-life corpus, under a holder the run's database can sit beside.

    Two levels below `tmp_path` on purpose. `84` §4's warning is that a directory
    name ABOVE the corpus root once changed classification and that pytest names
    `tmp_path` after the test function -- so the corpus is put under a fixed
    `holder/corpus` and never directly under the pytest-named directory, and the
    database goes in `holder/` rather than inside the corpus being scanned.
    """
    corpus = tmp_path / "holder" / "corpus"
    corpus.mkdir(parents=True)
    for name, body in MULTI_LIFE.items():
        (corpus / name).write_text(body)
    return corpus


def _run(corpus: Path) -> str:
    out = io.StringIO()
    cli.main([str(corpus), "--situation", "academic.coursework",
              "--label", "Coursework", "--user", "jy",
              "--database", str(corpus.parent / "plan.sqlite")], out=out)
    return out.getvalue()


@pytest.mark.xfail(strict=True, raises=RecordAbsent, reason=(
    "`src/cli.py:895` -- `review_and_accept` merges every result whose `group` "
    "is not None, including one a stop rule halted, and `supersedes` the first "
    "of them. `grouping.pipeline:539` deliberately does not record a halted "
    "group, so the supersession names a row that is not in `groups` and the run "
    "dies with `RecordAbsent`. Fires on `68`'s multi-life corpus via SR3, and on "
    "no smaller corpus. The fix is one predicate in `src/cli.py`, which is the "
    "lead's file; the hunk is in `scratchpad/waveG/CLI-PATCH.txt`."))
def test_a_person_with_three_lives_gets_a_plan_and_not_a_traceback(tmp_path):
    """Found by running the product, which is the only way it could have been.

    Every unit test of `review_and_accept` hands it groups that formed, and every
    unit test of the pipeline checks that a halted group is not recorded. Both
    are right. The defect is the join, and it needed ten files on a real disk.
    """
    printed = _run(_multi_life_corpus(tmp_path))

    # What the run says once it survives, measured under the patch rather than
    # guessed: `68` §2 recorded 1 folder and 0 ready to file for this person.
    assert "Files: 13 decided" not in printed          # ten files, not thirteen
    assert "Files: 10 decided" in printed, printed
    assert "PHYS1401" in printed and "PHYS2801" in printed, printed
    # The passport is `68` F4's file. It is named and counted, never opened.
    assert "Client Passport.txt" in printed, printed
    assert "Nothing was moved." in printed, printed


def test_the_same_corpus_one_file_smaller_still_produces_a_report(tmp_path):
    """The control, and the reason the xfail above is about a join and not a corpus.

    Drop one file and SR3 does not fire, nothing is halted, every merged group is
    a recorded one, and the command prints a report. So the ten files are not
    malformed input and the product is not refusing them: it is the halted group
    reaching a caller that assumes every group it holds was written down.
    """
    corpus = _multi_life_corpus(tmp_path)
    (corpus / "Insurance Claim.txt").unlink()

    printed = _run(corpus)

    assert "Files: 9 decided" in printed, printed
    assert "Nothing was moved." in printed, printed
