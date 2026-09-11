# tests/test_cli_the_screen_has_an_order.py
"""`104` R-116 and R-117: two lists on the screen that came out in no order.

Both were measured by running the product over a folder rather than by reading
it, and both are about the same thing -- a person reading a list has to be able
to follow it, and "whatever order the ids came out of the engine in" is not one.

R-116. *"Where should the files in Downloads go?"* offered sixteen folders as
Coursework, Spring2026, CS3134, ECON2010/lecture, PHYS1401/lecture,
W3134/lecture, cover letter, ECON2010 -- nine lines under a picture of those same
folders drawn in the order they nest. The list IS the tree, so it is printed in
the tree's order.

R-117. The apply and undo listings came out differently run to run: the same ten
files, the same byte-identical outcome, two unrelated listing orders on two
builds over one corpus. A person comparing two runs, or reading the undo list
against the apply list, gets one order -- destination, then name.

These run the real command over a real folder, because both defects are about
what comes out of the composition root and neither is visible from a fixture that
hands `report` a tree it made up.
"""
from __future__ import annotations

import io
import re
import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import cli  # noqa: E402

#: `104` SF-3: a group is a DRAFT until a person decides it, and a run that
#: decides nothing prints the proposal only -- no tree, no reading question, no
#: freeze, no placement. Every screen this file reads is downstream of that
#: decision, so every run has to type the accept, exactly as
#: `tests/test_cli.py`'s `ACCEPTS_THE_PROPOSAL` does.
ACCEPTS_THE_PROPOSAL: tuple[str, ...] = ("--accept-groups",)

COURSES = ("CS3134", "ECON2010", "PHYS1401")
#: `104` §18.42 puts a node-type word on every tree line (`[proposed]`,
#: `[yours already]`, ...), same as `tests/integration/test_r37_per_branch_
#: situation.py`'s own `re.sub(r"\s+\[[^\]]+\]$", ...)` strips it -- generalised
#: here to REPEATED trailing marks, because a node can carry its type word AND
#: "[marked, not a destination]" on the same line. This parser only ever
#: exercised the two marks an EXISTING folder can carry: under SF-3 an
#: undecided run draws only the corpus's own folders (here, `scans`), and the
#: invented `Coursework` structure -- carrying `[proposed]` -- only reaches this
#: screen once `--accept-groups` is typed.
_TRAILING_MARKS = re.compile(r"(?:\s+\[[^\]]+\])+$")


def _corpus(root: Path, *, opaque: bool) -> Path:
    """Enough coursework to nest, and optionally a folder nothing can be read from."""
    root.mkdir(parents=True)
    for course in COURSES:
        (root / f"{course.lower()}-syllabus.txt").write_text(
            f"{course} Syllabus\nColumbia, Fall 2026.\nInstructor: Dr. Ramirez\n")
        (root / f"{course.lower()}-lecture-1.txt").write_text(
            f"{course} Lecture 1 notes. Columbia.\n")
        (root / f"{course.lower()}-lecture-2.txt").write_text(
            f"{course} Lecture 2 notes. Columbia.\n")
        (root / f"{course.lower()}-problem-set-1.txt").write_text(
            f"{course} Problem Set 1. Due Friday.\n")
    if opaque:
        # Byte ranges out of the C0 control block, for
        # `tests/test_cli_opaque_only_folder.py`'s reason: `readers.signatures`
        # reads a control character as proof this is not text, so nothing
        # downstream can decode these into words and the folder holding them is
        # one the product opened and read nothing from.
        scans = root / "scans"
        scans.mkdir()
        for number in range(1, 4):
            (scans / f"blob-{number:02d}.bin").write_bytes(
                bytes(range(1, 32)) * 64)
    return root


def _run(argv) -> str:
    out = io.StringIO()
    code = cli.main(argv, out=out)
    printed = out.getvalue()
    assert code == 0, printed
    return printed


def _plan_run(tmp_path: Path, *args, opaque: bool = False) -> str:
    corpus = _corpus(tmp_path / "corpus", opaque=opaque)
    return _run([str(corpus), "--situation", "academic.coursework",
                 "--label", "Coursework", "--user", "t",
                 "--database", str(tmp_path / "plan.sqlite"),
                 *ACCEPTS_THE_PROPOSAL, *args])


def _folders_in_this_plan(printed: str) -> list[str]:
    """The tree block, read back as full paths in the order it drew them.

    Two spaces per level, which is what `report`'s own `draw` indents by. Read
    from the screen rather than from the run, because the whole claim of R-116 is
    that these two parts of one screen agree, and re-deriving the order from the
    records would be asserting that the derivation agrees with itself.
    """
    lines = printed.splitlines()
    start = next(i for i, line in enumerate(lines)
                 if line.startswith("Folders in this plan:"))
    paths: list[str] = []
    chain: list[str] = []
    for line in lines[start + 1:]:
        if not line.strip():
            break
        label = _TRAILING_MARKS.sub("", line.rstrip())
        depth = (len(label) - len(label.lstrip())) // 2 - 1
        chain = chain[:depth] + [label.strip()]
        paths.append("/".join(chain))
    return paths


def _offered(printed: str, question: str) -> list[str]:
    """The destinations one question offers, in the order it printed them.

    The label after the command is the display path -- `_option_lines` prints
    them from the same object the answer is resolved through -- and the command
    itself never holds three spaces in a row, quoted or not, so the first run of
    three is where the command ends and the label begins.
    """
    offered: list[str] = []
    for line in printed.splitlines():
        if f"--answer {question}" not in line and f"--answer '{question}" not in line:
            continue
        offered.append(line.strip().split("   ", 1)[1].strip())
    return offered


# ======================================================================================
# `104` R-116
# ======================================================================================

def test_the_folders_a_question_offers_are_in_the_order_the_tree_drew_them(
        tmp_path):
    """The list IS the tree, so it is printed in the tree's order.

    Not sorted as strings, which is a different order and a wrong one:
    `Coursework/W3134` sorts above `Coursework/W3134/exam` by accident, and the
    whole thing falls apart the first time somebody's folder starts with a digit.
    The assertion is against the picture printed nine lines above the question on
    the same screen, which is the thing a person is actually comparing it to.
    """
    printed = _plan_run(tmp_path, opaque=True)
    tree = _folders_in_this_plan(printed)
    offered = _offered(printed, "home:scans=")

    assert len(offered) > 4, (
        f"the question offered {len(offered)} folders; there is no order to "
        f"test:\n{printed}")
    assert offered[-1] == "Skip for now", (
        f"'skip' is not last in the list: {offered[-3:]}")
    destinations = offered[:-1]
    assert destinations == [path for path in tree if path in set(destinations)], (
        "the folders are offered in an order the picture above them does not "
        f"have.\n  offered: {destinations}\n  the tree: {tree}")


def test_ordering_the_offer_did_not_shorten_it(tmp_path):
    """The negative twin. A list can be put in order by dropping most of it.

    Every folder in this plan that a file can go in is still offered: the walk
    orders the destinations and removes none, and a destination missing from the
    question is one an answer can never name.
    """
    printed = _plan_run(tmp_path, opaque=True)
    tree = _folders_in_this_plan(printed)
    destinations = set(_offered(printed, "home:scans=")[:-1])

    missing = [path for path in tree if path not in destinations]
    assert not missing, (
        f"{len(missing)} folder(s) in the plan are offered by no answer line, "
        f"so nothing a person can type reaches them: {missing}")


# ======================================================================================
# `104` R-117
# ======================================================================================

def _moved(printed: str) -> list[str]:
    """The destination path of every file the apply or undo listing named."""
    return [line.split("-> ", 1)[1].strip()
            for line in printed.splitlines() if line.strip().startswith("-> ")]


def test_two_applies_of_one_plan_list_the_same_files_in_the_same_order(tmp_path):
    """Apply, take it back, apply again: one order, and it is a readable one.

    The order used to come out of `frozen_plans`, which follows `record_id`,
    which follows the order P11 handed its decisions to the freeze -- a group
    pass whose membership order nothing pins. Two runs over one corpus listed the
    same twenty-four files two ways.

    Asserted as SORTED and not merely as EQUAL, because equal is what a run
    compared with itself gets for free: `plans_under` orders the plans by the
    path P12 resolved for each one, so the listing reads destination by
    destination and, inside a destination, by name.
    """
    corpus = _corpus(tmp_path / "corpus", opaque=False)
    database = str(tmp_path / "plan.sqlite")
    common = [str(corpus), "--user", "t", "--database", database]
    _run([*common, "--situation", "academic.coursework",
          "--label", "Coursework", "--freeze", *ACCEPTS_THE_PROPOSAL])

    first = _moved(_run([*common, "--apply-everything"]))
    undone = _moved(_run([*common, "--undo-everything"]))
    second = _moved(_run([*common, "--apply-everything"]))

    assert len(first) > 4, f"only {len(first)} file(s) moved; nothing to order"
    assert first == second, (
        "two applies of one plan listed the same files in two orders")
    assert first == sorted(first), (
        "the apply listing is stable but in no order a person can follow:\n  "
        + "\n  ".join(first))
    # And the undo list can be read against the apply list, which is what it is
    # for. Its own paths are the ones the files came BACK to, so the comparison
    # is on the count and the order of the destinations it took them from.
    assert len(undone) == len(first)


def test_the_undo_listing_is_read_in_the_same_order_as_the_apply_listing(
        tmp_path):
    """The two lists side by side, which is how a person checks an undo.

    `undo_order` still puts the files back newest first -- a folder made for a
    later move can sit inside one made for an earlier one, and only the inner one
    may be removed first -- so this is about the LISTING and not about the order
    the work was done in. That the folders did come back out is asserted too, so
    a change that flattened the execution order to match the listing would be
    caught here rather than by an empty directory somebody finds later.
    """
    corpus = _corpus(tmp_path / "corpus", opaque=False)
    database = str(tmp_path / "plan.sqlite")
    common = [str(corpus), "--user", "t", "--database", database]
    _run([*common, "--situation", "academic.coursework",
          "--label", "Coursework", "--freeze", *ACCEPTS_THE_PROPOSAL])
    applied = _run([*common, "--apply-everything"])
    undone = _run([*common, "--undo-everything"])

    filed = [line.strip() for line in applied.splitlines()
             if line.startswith("    ") and not line.strip().startswith("->")
             and line.strip().endswith(".txt")]
    put_back = [line.strip() for line in undone.splitlines()
                if line.startswith("    ") and not line.strip().startswith("->")
                and line.strip().endswith(".txt")]

    assert filed and put_back, applied + undone
    assert [Path(name).name for name in put_back] == filed, (
        "the undo list does not read against the apply list:\n"
        f"  filed:    {filed}\n  put back: {put_back}")
    assert "folder(s) this product had made are gone again" in undone, (
        "the folders the product made were not removed; the execution order "
        "that removes an inner folder first has been changed")
    assert not (corpus / "Coursework").exists(), undone
