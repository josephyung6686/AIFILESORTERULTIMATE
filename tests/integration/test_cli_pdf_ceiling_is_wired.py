# tests/integration/test_cli_pdf_ceiling_is_wired.py
"""The page ceiling is not just declared -- it reaches the reader that reads PDFs.

`84` §5 names this project's dominant defect: a part is complete, well-tested, and
connected to nothing. `PDF_PAGE_CEILING` is exactly the shape that fails that way. It
is one integer in the composition root, and every test that could be written about it
by reading it back -- `assert PDF_PAGE_CEILING == 50` -- passes just as happily when
nothing on the reading path has ever heard of it. A 642-page datasheet would still
take 332 seconds and the suite would still be green.

So this file asserts the WIRING, by walking `cli.py`'s syntax tree for the call that
composes the readers. It deliberately does not assert the ceiling's VALUE: that number
is tuned against measurements and will move, and a test that pins it would have to be
edited every time it was tuned, which is a test that reports on itself.
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


def _read_pdf_argument(call: ast.Call) -> ast.Call:
    """The `read_pdf=` override handed to `macos_readers`."""
    for keyword in call.keywords:
        if keyword.arg == "read_pdf":
            assert isinstance(keyword.value, ast.Call), (
                "read_pdf= must be a reader BUILT here, so the ceiling can be given "
                "to it; a bare name is the un-ceilinged default reader.")
            return keyword.value
    raise AssertionError(
        "cli.py hands macos_readers no read_pdf= override, so the PDF reader is "
        "built with the module default -- max_pages=None, no ceiling, and the "
        "642-page datasheet is back.")


#: The readers this composition root is allowed to build for PDFs. A SET, because
#: the deployment's choice of library is a deployment fact and this guard is about
#: the CEILING rather than about the library -- but a closed set rather than "any
#: call", because the whole point below is that a BARE NAME here is the
#: un-ceilinged module default and the 642-page datasheet comes back.
#:
#: `pdfium_reader` joined `pdfminer_reader` on 2026-09-04, measured: 87.0 pages/s
#: against pdfminer's 5.7 on the owner's own PDFs, identical metadata and page
#: counts on 91 real files, and Apache-2.0 OR BSD-3-Clause where the other fast
#: option was AGPL. pdfminer.six STAYS in the tree and is still built here for the
#: Info dictionary, which pdfium cannot enumerate.
PDF_READERS: frozenset[str] = frozenset({"pdfminer_reader", "pdfium_reader"})


def test_the_composition_root_builds_the_pdf_reader_itself():
    """Not the default reader: one this file configures.

    The assertion is a SET rather than a single name, and the reason is worth
    stating because loosening a guard is usually the wrong move. What this test
    exists to catch is `read_pdf=some_name` -- a bare reference to the module
    default, which carries no page ceiling. Naming one library made it ALSO a
    guard on which library ships, which it was never written to be, and it went
    red the day a faster reader landed while the ceiling it actually guards was
    never in doubt. `test_the_pdf_reader_is_given_a_page_ceiling` below is the
    one that does the real work, and it is untouched.
    """
    built = _read_pdf_argument(_macos_readers_call())
    assert isinstance(built.func, ast.Name)
    assert built.func.id in PDF_READERS, (
        f"cli.py builds {built.func.id!r} for PDFs, which is not one of the "
        f"readers this deployment ships: {sorted(PDF_READERS)}")


def test_the_pdf_reader_is_given_a_page_ceiling():
    """The whole point. `max_pages` is what `extract_pages` receives as `maxpages`."""
    built = _read_pdf_argument(_macos_readers_call())
    assert "max_pages" in [k.arg for k in built.keywords], (
        "pdfminer_reader() is built without max_pages=, which is the module default "
        "of None -- read every page. The ceiling would be declared and unreachable.")


def test_the_ceiling_passed_is_the_declared_constant_and_not_a_loose_number():
    """A literal here would be a second ceiling nobody knows to tune.

    `cli.py` is the only file that picks a number, and it picks each one ONCE. A
    `max_pages=50` written inline would leave `PDF_PAGE_CEILING` sitting above it as
    a decoy: the documented rationale on one number and the behaviour on another.
    """
    built = _read_pdf_argument(_macos_readers_call())
    passed = next(k.value for k in built.keywords if k.arg == "max_pages")
    assert isinstance(passed, ast.Name), (
        "max_pages= must be the name PDF_PAGE_CEILING, not a literal, so the "
        "rationale written above the constant governs the behaviour below it.")
    assert passed.id == "PDF_PAGE_CEILING"


def test_the_ceiling_is_a_positive_page_count():
    """0 is pdfminer's spelling of "no limit" and would silently disable the ceiling.

    Not a check on the tuned value -- any positive integer passes. It rules out the
    one number that would turn the ceiling off while looking like it was set.
    """
    import cli

    assert isinstance(cli.PDF_PAGE_CEILING, int)
    assert cli.PDF_PAGE_CEILING > 0
