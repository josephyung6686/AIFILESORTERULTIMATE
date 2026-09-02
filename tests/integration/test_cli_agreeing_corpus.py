"""The easiest corpus there is, and the product asked for a model to file it.

The owner's question, in his words: *"why does every file need a model? I thought
we are only getting the dossier and stuff over and we have the OCR and their
stuff to parse information???"* He is right. Three files that name one course,
one term and one instructor produce two settled facts each -- `subject` direct,
`term` validated, straight out of `file_facts` -- and the run then reported that
deciding every one of them needed a model.

`76`/`72` state the position this file defends: *"The cheapest real saving is not
a smaller model, it is not making the call ... every fact settled locally is a
call not made."*

**Where the call came from.** §5.4 measures every level of a branch and builds a
folder only for the ones that DIVIDE -- `cli.py`'s own disclosure says so: "any
level your files did not actually divide ... is measured and not built". For this
corpus every level names one value, so nothing was built. What happened to the
measurement was nothing at all: `_top_level_node` records that a proposed
branch's "expectations are composed by `_project` from the branch's evidence",
`_project` composed them onto CHILDREN, and a branch with no child stated
nothing. A destination that states nothing cannot be reached by a fact. P11's
only candidate was the branch, matched on the accepted group alone at 2/7 = 0.29
against a 0.50 threshold, and §6.10 abstained -- through `needs_model_call`,
which is why the sentence named a model.

Answering the nesting question made it worse: `apply_review_action` refused the
whole run with *"accepting X produced no node"*, a message whose stated cause --
"none of the branch's files carry a settled value at any dimension" -- is the
opposite of what this corpus does.

`tree_design.materialise.branch_expectations` is the fix: a level that divides
nothing states its value ON THE BRANCH, which is the destination those files
actually have.
"""
from __future__ import annotations

import io
import json
import sqlite3
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

import cli  # noqa: E402

#: One course, one term, one instructor. Nothing here is ambiguous and nothing
#: here needs reading beyond what P4 already extracted.
AGREEING = {
    "PHYS 1401 syllabus.txt":
        "PHYS 1401 - Introduction to Mechanics\nFall 2024 Syllabus\n\n"
        "Instructor: Professor R. Villanueva\n"
        "Office hours: Wednesday 3:00-5:00 p.m.\nCredits: 3\n"
        "Lecture: Tuesday and Thursday 10:10-11:25 a.m.\n\n"
        "COURSE DESCRIPTION\n"
        "Kinematics, Newton's laws, work and energy, momentum, rotational "
        "motion.\n\nGRADING\n"
        "Problem sets 30%. Midterm 30%. Final examination 40%.\n"
        "Readings are assigned from the course textbook each week.\n",
    "PHYS 1401 lecture 08.txt":
        "PHYS 1401 - Lecture 08: Work and Energy\nFall 2024\n"
        "Professor R. Villanueva\n\n"
        "Lecture notes for the eighth meeting of the course.\n\n"
        "The work done by a constant force is the dot product of force and "
        "displacement.\n"
        "The work-energy theorem relates the net work to the change in kinetic "
        "energy.\n"
        "Worked examples are drawn from the assigned reading for this seminar.\n",
    "PHYS 1401 problem set 3.txt":
        "PHYS 1401 - Problem Set 3\nFall 2024\n"
        "Due: Thursday October 17, 2024 at the start of lecture\n"
        "Professor R. Villanueva\n\n"
        "1. A block of mass 2.0 kg slides down a frictionless incline of angle "
        "30 degrees.\n   Find the acceleration and the normal force.\n"
        "2. A 0.50 kg ball is thrown vertically upward at 12 m/s. How high does "
        "it rise?\n"
        "3. Derive the work-energy theorem for a constant force in one "
        "dimension.\n"
        "This assignment is graded coursework for the course.\n",
}

#: The control. TWO folders whose own contents both settle `subject = PHYS1401`,
#: and a third holding a different course so that the value divides the corpus
#: and both folders may claim it (`upstream._divides_the_corpus`). A file then
#: has two destinations its evidence supports equally, which is a bounded
#: ambiguity and exactly what §6.6 keeps a model for. `87` §2.4 measured this
#: shape on a real corpus: `Work/Hendricks matter` and `Downloads` both claimed
#: `CV20264417` and four good files stopped.
TWO_HOMES = {
    "Uni/PHYS 1401 syllabus.txt":
        "PHYS 1401 - Introduction to Mechanics\nFall 2024 Syllabus\n"
        "Instructor: Professor R. Villanueva\n"
        "Kinematics, Newton's laws, work and energy.\n"
        "Readings are assigned from the course textbook each week.\n",
    "Uni/PHYS 1401 problem set 3.txt":
        "PHYS 1401 - Problem Set 3\nFall 2024\nProfessor R. Villanueva\n"
        "This assignment is graded coursework for the course.\n",
    "Saved/PHYS 1401 syllabus (1).txt":
        "PHYS 1401 - Introduction to Mechanics\nFall 2024 Syllabus\n"
        "Instructor: Professor R. Villanueva\n"
        "Saved copy. Kinematics, Newton's laws, work and energy.\n"
        "Readings are assigned from the course textbook.\n",
    "Saved/PHYS 1401 lecture 08.txt":
        "PHYS 1401 - Lecture 08: Work and Energy\nFall 2024\n"
        "Professor R. Villanueva\n"
        "Lecture notes for the eighth meeting of this seminar.\n",
    "Other/ECON 2105 syllabus.txt":
        "ECON 2105 - Principles of Macroeconomics\nFall 2024 Syllabus\n"
        "Instructor: Professor L. Whitfield\n"
        "Readings are assigned from the course textbook for this seminar.\n",
    "Other/ECON 2105 notes.txt":
        "ECON 2105 - Lecture notes\nFall 2024\nProfessor L. Whitfield\n"
        "Notes for the course, covering aggregate demand.\n",
}


def _corpus(tmp_path: Path, files: dict[str, str]) -> Path:
    """Under `holder/corpus`, never directly under the pytest-named directory.

    `84` §4's warning: a directory name ABOVE the corpus root once changed
    classification, and `tmp_path` is named after the test function.
    """
    corpus = tmp_path / "holder" / "corpus"
    corpus.mkdir(parents=True)
    for name, body in files.items():
        path = corpus / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(body)
    return corpus


def _run(corpus: Path, label: str, *extra: str) -> str:
    out = io.StringIO()
    cli.main([str(corpus), "--situation", "academic.coursework",
              "--label", label, "--user", "jy",
              "--database", str(corpus.parent / "plan.sqlite"), *extra], out=out)
    return out.getvalue()


def _headline(printed: str) -> str:
    for line in printed.splitlines():
        if line.strip().startswith("Files:"):
            return line.strip()
    return "ABSENT"


def _nesting_answer(printed: str) -> str:
    """The `--answer` line the run itself printed, read rather than guessed.

    The key is `cli._nesting_key`'s, derived from the option's own level chain,
    and hard-coding it here would pin a template's shape in a test about
    placement.
    """
    for line in printed.splitlines():
        text = line.strip()
        if text.startswith("--answer 'branch:") and "keep-as-it-is" not in text:
            return text.split("'")[1]
    raise AssertionError(f"no branch nesting answer was offered:\n{printed}")


def test_a_corpus_that_agrees_on_everything_is_filed_from_its_own_facts(tmp_path):
    """The whole point, through the shipped command and no model.

    Two runs because the first is what raises the question and the second is what
    answers it. Before this fix the second run did not file these files -- it
    ended `ReviewActionRefused`, with no plan at all.
    """
    corpus = _corpus(tmp_path, AGREEING)

    first = _run(corpus, "PHYS 1401")
    answer = _nesting_answer(first)

    second = _run(corpus, "PHYS 1401", "--answer", answer)

    assert _headline(second) == "Files: 3 decided, 3 ready to file", second
    assert "Ready to file into PHYS 1401 -- 3 files" in second, second
    # And no file was sent anywhere, asked for, or held for a model.
    assert "needed a model" not in second, second

    # ON DIRECT FACTS, which is the half the headline cannot show. `accept_direct`
    # is §6.6's own case -- validated facts uniquely matching one path -- and it
    # is the verdict `needs_model_call` refuses to call a model for. A run that
    # filed these on group similarity would print the same headline and would not
    # be the fix.
    conn = sqlite3.connect(corpus.parent / "plan.sqlite")
    conn.row_factory = sqlite3.Row
    verdicts = [json.loads(row["payload"])["two_condition"]["verdict"]
                for row in conn.execute(
                    "SELECT payload FROM placement_decisions "
                    "WHERE superseded_by IS NULL ORDER BY rowid")]
    conn.close()
    # The last three, because the first run's decisions are still here and are
    # not superseded: two runs against one database is two assessments per file.
    # Only the last three are asserted, and deliberately: what the FIRST run's
    # three say depends on `cli.choose_option`, which the xfail below is about,
    # so pinning them here would make this test fail on the hunk landing rather
    # than on anything being wrong.
    assert verdicts[-3:] == ["accept_direct"] * 3, verdicts
    # Nothing was even prepared for a model: no dossier, no pre-call abstention.
    assert "Nothing about it left this device" not in second, second


def test_the_option_that_files_them_does_not_promise_folders_it_will_not_build(
        tmp_path):
    """The sentence beside the answer, which was a promise of two folders.

    `resulting_child_counts` counts a level's distinct VALUES without asking
    whether the level divides, so the option that builds nothing summarised
    itself as "This option would create 1 term, and 1 subject". A person choosing
    on that sentence is choosing on a claim the run will not keep.
    """
    corpus = _corpus(tmp_path, AGREEING)
    printed = _run(corpus, "PHYS 1401")
    offered = [line.strip() for line in printed.splitlines()
               if line.strip().startswith("--answer 'branch:")
               and "keep-as-it-is" not in line]
    assert offered, printed
    assert "would create no folders" in offered[0], offered
    assert "PHYS1401" in offered[0] and "Fall2024" in offered[0], offered


def test_two_folders_that_both_claim_the_value_still_have_to_ask(tmp_path):
    """The control, and it matters more than the two above.

    A fix that files everything is as wrong as one that files nothing: "absent
    means refuse, never guess" is the standing rule, and §6.6 keeps the model for
    "a bounded ambiguity" -- which this is and the corpus above is not. Two
    folders the person already made both hold `PHYS1401` files, so both settle
    `subject = PHYS1401`; a third course makes that value divide the corpus, so
    both may claim it. Each candidate scores 0.71, the margin between them is
    zero, and §6.10 must abstain.

    Measured identical before and after the branch fix, which is the point: the
    fix reaches a branch that states NOTHING, and says nothing about a file with
    two destinations that state the same thing.
    """
    corpus = _corpus(tmp_path, TWO_HOMES)

    printed = _run(corpus, "Coursework")

    assert _headline(printed) == "Files: 6 decided, 0 ready to file", printed
    assert "needed a model" in printed, printed


@pytest.mark.xfail(strict=True, reason=(
    "`cli.choose_option` takes the first option that passes its checks AND has "
    "CHILDREN, so the option that populates the branch itself -- no children, "
    "one rewritten node -- is skipped and `keep-as-it-is` is taken instead. "
    "`src/cli.py` is the composition root and belongs to the lead; the hunk is "
    "written out in scratchpad/q1/CLI-PATCH.txt. Measured under it: this XPASSes "
    "and EIGHT other tests turn red, seven of them because their corpora were "
    "built to leave a file unplaced and it no longer is -- the fixtures need "
    "re-cutting, not the hunk reverting. The eighth is a message: a protected "
    "file contradicted off the branch's new expectation is told "
    "`conflicting_facts` where it used to be told `protected material`, which is "
    "`66` §4's collapse and is the lead's to rule on. UNMARK when it lands, do "
    "not delete."))
def test_the_first_run_files_them_without_being_answered(tmp_path):
    """`80` R2: the friction budget is spent once. A person whose files agree on
    everything should not have to answer a question to be told what the product
    already measured -- the first run is the one they judge it by."""
    corpus = _corpus(tmp_path, AGREEING)

    printed = _run(corpus, "PHYS 1401")

    assert _headline(printed) == "Files: 3 decided, 3 ready to file", printed
