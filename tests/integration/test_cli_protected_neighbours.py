"""`94` F1 — one protected file in a folder made every file in it unmovable.

The audit's own reproduction, run as a test. A student's folder holds a syllabus,
a lecture, a reading list, a homework sheet and one passport scan. They do the
sanctioned thing -- enable a residual area, file the review set, freeze -- and got:

    Nothing was frozen: no placement in this run is ready to move.

    Not frozen, and still exactly where they are -- 4 file(s):
        PHYS 1401 syllabus.txt
        Uni/PHYS 1401 lecture 08.txt
        reading list.txt
          Each of these is no plan could be made for it.
          protected_without_policy

Delete the passport and re-run the identical command and three files froze. That
is the causality, both directions, on one corpus -- and it is why this file runs
the corpus twice rather than asserting the fixed direction alone: an assertion
that only the passport corpus freezes would pass just as well if the run had
stopped freezing everything, and one that only the clean corpus freezes tests
nothing about the defect at all.

**The mechanism.** `src/cli.py`'s `collapse_handling_classes` gives a branch the
STRONGEST handling class among its members, so one passport gave the whole
`Coursework` branch `sensitive_personal` -- correctly: that class is the FLOOR
that stops the passport landing somewhere weaker. `mutation.resolution` then read
the same field as *this label was composed from protected material* and refused
to compose a path through the branch, which is every destination in the tree.
Two parts, one field, two meanings, and the person's coursework named on the
screen as the protected thing.

**What must not change, and is asserted here too.** The passport is still not
filed, still counted, still never opened, and its name is still not on the screen
(`93`'s ruling). What changed is that its neighbours stopped being punished for
sharing a folder with it.

The command is `cli.main`, not a seam. The audit found this by running the
product and no unit test could have: the tree, the classification, the collapse
and the composition each behaved exactly as their own tests say they should.
"""
from __future__ import annotations

import io
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

import cli  # noqa: E402

#: Four ordinary coursework files. Every one of them is the person's own work and
#: none of them is protected material by any rule this build has.
COURSEWORK = {
    "PHYS 1401 syllabus.txt":
        "PHYS 1401 syllabus. Columbia University, Spring 2026 term.\n"
        "Course syllabus for PHYS 1401. Weekly readings and problem sets.\n",
    "Uni/PHYS 1401 lecture 08.txt":
        "PHYS 1401 lecture 08 notes. Columbia University, Spring 2026 term.\n"
        "Lecture notes for the eighth week of PHYS 1401.\n",
    "reading list.txt":
        "PHYS 1401 reading list. Columbia University, Spring 2026 term.\n"
        "Required reading for the course PHYS 1401.\n",
    "homework 3.txt":
        "PHYS 1401 homework 3. Columbia University, Spring 2026 term.\n"
        "Problem set three for PHYS 1401.\n",
}

#: The fifth file, and the north star's own person: a real disk has one of these.
#: `recognition.detector` names `identity` from its own words and
#: `SAFETY_DOMAIN_HANDLING` gives it `sensitive_personal` with `protected=True`.
PASSPORT_NAME = "passport scan.txt"
PASSPORT_BODY = ("Passport number X12345678. Client identity document.\n"
                 "Passport scan, identity document, date of birth "
                 "and nationality.\n")

#: The refusal class the person was shown under their own coursework. It is the
#: right class for a name composed from protected material and the wrong one for
#: "a folder above this one has a strong floor", so its absence is asserted by
#: name rather than by counting what froze.
REFUSAL_CLASS = "protected_without_policy"


def _corpus(tmp_path: Path, *, with_passport: bool) -> Path:
    """The corpus under a fixed holder, with the database beside it, never in it.

    `84` §4: a directory name ABOVE the corpus root once changed classification,
    and pytest names `tmp_path` after the test function -- so the corpus is
    always `holder/corpus` and never the pytest-named directory itself.
    """
    corpus = tmp_path / "holder" / "corpus"
    (corpus / "Uni").mkdir(parents=True)
    for name, body in COURSEWORK.items():
        (corpus / name).write_text(body)
    if with_passport:
        (corpus / PASSPORT_NAME).write_text(PASSPORT_BODY)
    return corpus


def _run(corpus: Path) -> str:
    """The sanctioned gesture, verbatim: a residual area, a review set, a freeze."""
    out = io.StringIO()
    cli.main([str(corpus), "--situation", "academic.coursework",
              "--label", "Coursework", "--user", "jy",
              "--residual", "Review Later",
              "--send-set", "Not yet placed=Review Later",
              "--freeze",
              "--database", str(corpus.parent / "plan.sqlite")], out=out)
    return out.getvalue()


def test_the_ordinary_files_beside_a_passport_scan_still_freeze(tmp_path):
    """The defect, gone, on the corpus that produced it.

    The whole freeze line is asserted rather than "more than zero froze": a run
    that froze one file and called it a plan would satisfy the weaker claim, and
    the person's complaint was about a count. The three names are asserted too,
    because "3 file(s)" over the wrong three is the same screen.
    """
    printed = _run(_corpus(tmp_path, with_passport=True))

    assert "Frozen: 3 file(s) are ready to move, in 1 branch(es)." in printed, \
        printed
    for name in ("homework 3.txt", "reading list.txt",
                 "Uni/PHYS 1401 lecture 08.txt"):
        assert name in printed, (name, printed)
    # The gesture that moves them is offered. `94` F1's screen offered none.
    assert "--apply Coursework/PHYS1401" in printed, printed

    # And the sentence the person was owed and did not get: nothing in this run
    # tells them their coursework is protected.
    assert REFUSAL_CLASS not in printed, printed
    assert "no plan could be made for it" not in printed, printed


def test_the_passport_is_still_held_counted_and_never_named(tmp_path):
    """`84` §1's standing rule, on the same run. The fix may not buy anything here.

    Marked, counted, not filed, not opened, and -- under `93`'s ruling -- not
    named, with the command that would name it on the screen beside the count.
    A fix that freed the neighbours by reclassifying the passport would pass the
    test above and fail this one.
    """
    printed = _run(_corpus(tmp_path, with_passport=True))
    collapsed = " ".join(printed.split())

    assert "1 protected file, marked and counted, and none of them opened" \
        in collapsed, printed
    assert "--show-protected" in printed, printed
    # Neither the file nor anything it says reaches the screen.
    assert PASSPORT_NAME not in printed, printed
    assert "X12345678" not in printed, printed
    # And it is not in the frozen set: nothing offers to move it.
    assert "Frozen: 3 file(s)" in printed, printed


def test_the_same_corpus_without_the_passport_freezes_the_same_three(tmp_path):
    """The control, and the half that made `94` F1 a causal claim.

    Same command, same four coursework files, one file deleted. Before the fix
    this run froze three and the run above froze none, which is what proved the
    passport was the cause rather than the coursework. After it, both freeze
    three -- and the destination differs (`Review Later` here, `PHYS1401` above)
    only because the fifth file changes what the `subject` level divides, which
    is P10 doing its job and not this guard doing anything.
    """
    printed = _run(_corpus(tmp_path, with_passport=False))

    assert "Frozen: 3 file(s) are ready to move, in 1 branch(es)." in printed, \
        printed
    assert REFUSAL_CLASS not in printed, printed
