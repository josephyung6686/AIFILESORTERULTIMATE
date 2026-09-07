# tests/integration/test_cli_spreadsheet_ceiling_is_wired.py
"""The cell ceiling is not just declared -- it reaches the reader that reads sheets.

`84` §5 names this project's dominant defect: a part is complete, well-tested, and
connected to nothing. A ceiling is exactly the shape that fails that way, and
`test_cli_pdf_ceiling_is_wired.py` was written for the same reason about the same
kind of number. `assert SPREADSHEET_CELL_CEILING == n` passes just as happily when
nothing on the reading path has ever heard of it.

WHY THIS CEILING EXISTS AT ALL. §2.9 asks a spreadsheet for *"visible cell values"*
and names no limit, so the reader stored every non-empty cell of every sheet -- and
each one becomes a `text_units` row AND an `evidence` row. Measured on the owner's
199-file corpus, 2026-09-04: 13,994 of 23,983 text units, 58% of everything the
product had read, were spreadsheet cells carrying 3.5% of its characters. A data
export of a million cells is a third of a gigabyte of database for one file, and
every document the person actually wrote queues behind it.

So this file asserts the WIRING, by walking `cli.py`'s syntax tree. It deliberately
does not assert the ceiling's VALUE: that number is tuned against measurements and
will move, and a test that pinned it would have to be edited every time it was tuned,
which is a test that reports on itself.
"""
from __future__ import annotations

import ast
from pathlib import Path

CLI = Path(__file__).resolve().parents[2] / "src" / "cli.py"


def _macos_readers_call() -> ast.Call:
    """The one `macos_readers(...)` call in the composition root."""
    tree = ast.parse(CLI.read_text(encoding="utf-8"))
    calls = [node for node in ast.walk(tree)
             if isinstance(node, ast.Call)
             and isinstance(node.func, ast.Name)
             and node.func.id == "macos_readers"]
    assert len(calls) == 1, (
        f"expected exactly one macos_readers(...) call in cli.py, found {len(calls)}. "
        "If the composition moved, this test has to follow it rather than be deleted.")
    return calls[0]


def _ceiling_keyword() -> ast.keyword:
    for keyword in _macos_readers_call().keywords:
        if keyword.arg == "spreadsheet_cell_ceiling":
            return keyword
    raise AssertionError(
        "cli.py hands macos_readers no spreadsheet_cell_ceiling=, so the long-tail "
        "reader is built without one. Every cell of every sheet is stored again, and "
        "one export outweighs a person's whole corpus.")


def test_the_composition_root_supplies_the_cell_ceiling():
    """The whole point: the number reaches `stdlib_long_tail_reader(max_cells=...)`,
    which is where a cell is either stored or counted and dropped."""
    _ceiling_keyword()


def test_the_ceiling_passed_is_the_declared_constant_and_not_a_loose_number():
    """A literal here would be a second ceiling nobody knows to tune.

    `cli.py` is the only file that picks a number, and it picks each one ONCE. A
    `spreadsheet_cell_ceiling=10000` written inline would leave the constant sitting
    above it as a decoy: the documented rationale on one number and the behaviour on
    another. This is the rule `test_cli_pdf_ceiling_is_wired.py` states for pages.
    """
    passed = _ceiling_keyword().value
    assert isinstance(passed, ast.Name), (
        "spreadsheet_cell_ceiling= must be the name SPREADSHEET_CELL_CEILING, not a "
        "literal, so the rationale written above the constant governs the behaviour "
        "below it.")
    assert passed.id == "SPREADSHEET_CELL_CEILING"


def test_the_ceiling_is_a_positive_cell_count():
    """Not a check on the tuned value -- any positive integer passes. It rules out
    the two numbers that would turn the ceiling into something else: 0 admits no cell
    of any spreadsheet while still recording `capped`, and a negative is not a count.
    """
    import cli

    assert isinstance(cli.SPREADSHEET_CELL_CEILING, int)
    assert cli.SPREADSHEET_CELL_CEILING > 0


def test_the_reader_refuses_to_be_built_without_one():
    """"Absent means refuse, never guess." The guard belongs at the reader too, so a
    future composition root that forgets gets an error rather than a silent default.
    """
    import pytest

    from readers.long_tail_stdlib import stdlib_long_tail_reader

    with pytest.raises(TypeError):
        stdlib_long_tail_reader()


def test_the_deployment_bundle_refuses_to_be_built_without_one():
    """`macos_readers` cannot pick this number either -- it is a policy, and
    `readers/` is not where policy lives. It has to be handed one."""
    import pytest

    from readers.deployment import macos_readers

    with pytest.raises(TypeError):
        # Every OTHER required ceiling is supplied, so the refusal is about
        # this one. Omitting them all would let a later required argument
        # keep this test green while the cell ceiling grew a default.
        macos_readers(find_structured_strings=lambda text: (),
                      ocr_page_ceiling=1, ocr_seconds_per_file=1)
