# tests/integration/test_adversarial_seams.py
"""Defects found by attacking the composed product from angles its own suites do not.

Every part here has a green suite of its own. What these tests hold is the seam
between two of them, where each side is right about its own half and the pair is
wrong -- which is this codebase's dominant defect class (`84` §5.5).

Each was found by RUNNING `cli.main` over an ordinary corpus, not by reading.
"""
from __future__ import annotations

import io
import re
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

import cli  # noqa: E402


#: An internal node id as `tree_design` mints them: `node_36a7a69e_1`. A person
#: cannot act on one and cannot tell two apart. `version_1ac928fd_2` is NOT this --
#: the plan version is printed on purpose, and the line that prints it says so.
_INTERNAL_NODE_ID = re.compile(r"\bnode_[0-9a-f]{6,}_\d+\b")

#: A Python `repr` that has reached a screen. `Kind(field=...)`, which is what a
#: dataclass renders as when something formats it as though it were a sentence.
_DATACLASS_REPR = re.compile(r"\b[A-Za-z_]\w*\((?:\w+=|'|\")")


def _three_courses(tmp_path: Path) -> Path:
    """A student with three courses. There is no smaller ordinary corpus than this,
    and the shape it produces -- one child per course, each holding one file -- is
    what fires §5.9's `tiny-folder-distribution` warning on the FIRST run."""
    corpus = tmp_path / "corpus"
    corpus.mkdir()
    for course in ("PHYS 1401", "CHEM 1301", "MATH 2413"):
        (corpus / f"{course} syllabus.txt").write_text(
            f"{course} Syllabus\n\nSpring 2026.\n")
    return corpus


def _run(tmp_path: Path, corpus: Path, **overrides) -> str:
    argv = [str(corpus), "--situation", "academic.coursework",
            "--label", "Coursework", "--user", "jy",
            "--database", str(tmp_path / "plan.sqlite")]
    for flag, value in overrides.items():
        argv += [f"--{flag.replace('_', '-')}", value]
    out = io.StringIO()
    cli.main(argv, out=out)
    return out.getvalue()


@pytest.mark.xfail(strict=True, reason=(
    "§5.9's warnings reach the person as a Python repr with three internal node "
    "ids in it, on the `--answer` line the screen tells them to type. The fix is "
    "one line in `src/cli.py`, which belongs to the lead: at `_nesting_choices`, "
    "P10's `Warning_` records must be rendered to their own `reason` before they "
    "are put in a field declared `tuple[str, ...]`. Sent as a patch. Strict, so "
    "the suite turns red the day it lands and this marker is removed."))
def test_the_screen_never_prints_a_python_repr_or_an_internal_node_id(tmp_path):
    """§5.9's warnings reach the person as `Warning_(kind=..., node_id=...)`.

    `questions.triggers.NestingChoice.warnings` is declared `tuple[str, ...]` and
    `_nesting_label` renders each one with `f"warning: {warning}"`. P10's
    `candidates.VerticalOption.warnings` is `tuple[Warning_, ...]` -- a frozen
    dataclass. The composition root passes one straight into the other, so what a
    person reads on the line they are told to TYPE is:

        --answer 'branch:Coursework=school>term>subject>work_type'   ...
        -- warning: Warning_(kind='tiny-folder-distribution',
        node_id='node_36a7a69e_1', reason="3 of this level's children hold 1
        file(s) or fewer", evidence=('node_36a7a69e_2', ...))

    Both sides pass their own tests: P10 builds a correct `Warning_`, P15 renders a
    correct string. Neither is wrong and the pair is, which is why nothing caught it.

    The sentence the person needed was already in the record -- `reason` is written
    for them. What surrounds it is three internal ids they cannot act on, wrapped
    around the one clause they can, on a line whose whole job is to be copied.

    Both patterns are checked, not just the literal `Warning_`: a `repr` on a screen
    and an internal id on a screen are the same defect, and a guard that named only
    today's class would stop catching tomorrow's.
    """
    printed = _run(tmp_path, _three_courses(tmp_path))

    # It fired at all -- otherwise this test passes by measuring nothing, which is
    # the trap `84` §5.3 names. The warning text is the person's, so its own words
    # must be here even after the record around them is rendered properly.
    assert "of this level's children hold" in printed, printed

    reprs = _DATACLASS_REPR.findall(printed)
    assert not reprs, f"a Python repr reached the screen: {sorted(set(reprs))}"

    ids = _INTERNAL_NODE_ID.findall(printed)
    assert not ids, f"internal node ids reached the screen: {sorted(set(ids))[:5]}"


def test_the_warning_is_still_shown_and_not_merely_silenced(tmp_path):
    """The twin, and the one that matters.

    Deleting the warnings from the line passes the test above and is strictly worse
    than the defect: `questions.triggers._nesting_label` says in as many words that a
    question offering the shapes WITHOUT the counts and warnings "would be strictly
    worse than the default it replaced, because it would move the decision to the
    person and keep the information here."

    So the fix is a rendering, never a removal, and this holds the line: the option
    the person is offered still tells them what is wrong with it.
    """
    printed = _run(tmp_path, _three_courses(tmp_path))

    offered = [line for line in printed.splitlines()
               if "--answer 'branch:Coursework=" in line]
    assert offered, printed
    assert any("warning" in line for line in offered), (
        "the shape with three one-file children is offered with nothing said "
        "against it: " + "\n".join(offered))


def test_p12_refuses_to_move_a_bundle_named_in_another_case(tmp_path):
    """The other half of the absolute rule, at the seam that enforces it.

    "Applications and system items are never read, never MOVED, and no gesture
    makes them movable." P12's `special.inspect_objects` enforces the second half
    with the same predicate P3 uses for the first, `is_protected_container` -- so
    for as long as that predicate compared the `.app` suffix exactly, a bundle
    reached by its other spelling was not merely readable but MOVABLE, and P12
    would have walked it, listed it and relocated it.

    macOS is case-insensitive by default, so `Numbers.APP` and `Numbers.app` name
    one directory. Both ends of the move are checked, so both are checked here:
    a protected source and a protected destination.

    The seam is the point. `tests/p3/` proves P3's predicate and `tests/p12/`
    proves P12 calls it; each passed while the pair let a protected bundle move,
    because every test on both sides spelled the suffix lower-case.
    """
    from mutation.special import inspect_objects
    from mutation import vocabulary as v

    bundle = tmp_path / "Numbers.app"
    (bundle / "Contents").mkdir(parents=True)
    (bundle / "Contents" / "sheet.numbers").write_text("never moved")
    ordinary = tmp_path / "Syllabus.pdf"
    ordinary.write_bytes(b"%PDF-1.4\n")
    destination = tmp_path / "Filed"
    destination.mkdir()

    def verdict(*, source, destination_directory):
        return inspect_objects(
            source=source, destination_directory=destination_directory,
            source_root=tmp_path, destination_root=tmp_path,
            extra_protected=None, conflict_copies=lambda path: (),
            dataless_of=lambda path: False)

    # The bundle as the SOURCE, named the other way.
    assert verdict(source=tmp_path / "Numbers.APP",
                   destination_directory=destination
                   ).refusal_class == v.PACKAGE_BUNDLE_UNAPPROVED
    # A file INSIDE it, named the other way.
    assert verdict(source=tmp_path / "Numbers.APP" / "Contents" / "sheet.numbers",
                   destination_directory=destination
                   ).refusal_class == v.PACKAGE_BUNDLE_UNAPPROVED
    # And as the DESTINATION: moving an ordinary file INTO the bundle.
    assert verdict(source=ordinary,
                   destination_directory=tmp_path / "Numbers.APP" / "Contents"
                   ).refusal_class == v.PACKAGE_BUNDLE_UNAPPROVED

    # Non-vacuous: an ordinary move past this check is not refused as a bundle,
    # so the three assertions above are about the spelling and not about
    # `inspect_objects` refusing everything it is handed.
    assert verdict(source=ordinary, destination_directory=destination
                   ).refusal_class != v.PACKAGE_BUNDLE_UNAPPROVED
