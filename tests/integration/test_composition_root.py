"""The composition root's database is complete with respect to the source.

`src/cli.py` is the only place a person's run installs its schema, and it is the
one place no part's own test suite looks: every part builds its tables in its own
fixture, so a table that ships in `src/` and is created by nothing outside a test
is invisible to all 5,386 of them at once. This module is that blind spot's test.

It is the database-side twin of `tests/p11/test_p11_groups.py`'s
`_placement_sources_calling`, whose docstring already names the pattern -- "the
four concepts this codebase shipped fully-tested and connected to nothing all had
references" -- and of the strict xfail standing on it in
`tests/p11/test_p11_versions.py:311`, which counts the shape at seven. That
instrument is scoped to `src/placement/`; this one is scoped to the whole tree,
because every instance found since was somewhere else.

LIMITATION, stated rather than hidden: `_tables_declared_in_source` reads literal
DDL. A table whose name arrives through an f-string placeholder is not counted, so
this test can under-report and never over-report. A missing table it names is
always real.
"""
from __future__ import annotations

import ast
import re
import sys
from pathlib import Path

import pytest

from database_agent.db import open_database

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

import cli  # noqa: E402

_SRC = Path(__file__).resolve().parents[2] / "src"
_DECLARATION = re.compile(r'CREATE\s+TABLE\s+IF\s+NOT\s+EXISTS\s+"?([a-z_]+)"?')


def _tables_declared_in_source() -> set[str]:
    """Every table the shipped source declares, by reading its own DDL."""
    return {match.group(1)
            for path in sorted(_SRC.rglob("*.py"))
            for match in _DECLARATION.finditer(path.read_text(encoding="utf-8"))}


def _tables_present(conn) -> set[str]:
    return {row["name"] for row in conn.execute(
        "SELECT name FROM sqlite_master WHERE type = 'table'")}


#: Tables their owning writer creates on demand instead of at bootstrap, each with the
#: reason it may not join `_bootstrap`. A name earns a place here only by being PROVEN
#: created below -- an exemption nothing checks is how a census rots into a whitelist.
LAZY_TABLES: dict[str, str] = {
    "llm_cd_plan_identity":
        "created per C/D verdict write by `_ensure_identity_table` "
        "(`placement_validation.py:461`), which must run inside the caller's open "
        "transaction: `executescript` at bootstrap would commit the harness's "
        "transaction out from under it.",
}


def test_the_bootstrap_creates_every_table_the_source_declares(tmp_path: Path):
    """A part whose tables the run never creates fails at its first write.

    Not at import, not at start-up, and not in any test -- at the first write, in
    front of the person, after their disk has already been read.
    """
    conn = open_database(tmp_path / "agent.sqlite")
    cli._bootstrap(conn)
    missing = sorted(
        _tables_declared_in_source() - _tables_present(conn) - set(LAZY_TABLES))
    assert not missing, (
        "declared in src/ and created by nothing a person runs: " + ", ".join(missing))


def _sources_calling(function_name: str) -> set[str]:
    """Modules anywhere in `src/` that CALL `function_name`, by AST, not by grep.

    The whole-tree twin of `tests/p11/test_p11_groups.py`'s
    `_placement_sources_calling`, and deliberately the same method, including its
    rule: *a reference is not a call and an import is not a use*. Every mechanism
    found unreachable since that helper was written lives outside `src/placement/`,
    which is the only reason it was not caught by it.
    """
    callers = set()
    for path in sorted(_SRC.rglob("*.py")):
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            if not isinstance(node, ast.Call):
                continue
            func = node.func
            name = (func.attr if isinstance(func, ast.Attribute)
                    else func.id if isinstance(func, ast.Name) else None)
            if name == function_name:
                callers.add(str(path.relative_to(_SRC)))
    return callers


def test_the_reachability_instrument_can_tell_a_caller_from_a_reference():
    """The falsifying twin for `_sources_calling`, and it is not a formality.

    `create_llm_schema` gained its first production caller in this same change, so
    it proves the instrument SEES a real call. `record_user_level_edit` is named in
    its own module's `__all__` and called by nothing, so it proves the instrument is
    not merely matching the name -- which a grep would, and which is how this gap
    stayed invisible.
    """
    assert "cli.py" in _sources_calling("create_llm_schema")
    assert not _sources_calling("record_user_level_edit")


def test_the_renaming_overlay_has_a_writer_somewhere_in_the_product():
    """`64` §1's rename is readable, appliable, durable -- and unreachable.

    `apply_user_level_edits` is wired into routing (`routing.py:506`) and the
    overlay's own writer refuses an edit nothing can apply, on the grounds that
    "the user would see their edit accepted and never honoured". Nothing calls the
    writer, and `routing.py:303` defaults `user_edits` to `()`, so the person
    cannot rename a level at all: the edit is not honoured because it cannot be
    made. Its owed caller is P13's review surface, which is unbuilt.

    `xfail(strict=True)`: it reports the gap today and turns the suite RED the day
    a writer appears, which forces the marker off.
    """
    assert _sources_calling("record_user_level_edit")


test_the_renaming_overlay_has_a_writer_somewhere_in_the_product = pytest.mark.xfail(
    strict=True,
    reason="P13's review surface is unbuilt; nothing calls record_user_level_edit, "
           "so a person cannot rename a level. XPASSes and fails the suite the "
           "moment a writer appears.",
)(test_the_renaming_overlay_has_a_writer_somewhere_in_the_product)


def test_every_lazily_created_table_is_created_by_the_writer_that_claims_it(tmp_path):
    """The exemption above is proven, not asserted.

    A census with an unchecked exemption list is a census anyone can pass by adding
    a name to it. Each entry must really be created by the call its reason names.
    """
    from llm_harness.placement_validation import _ensure_identity_table

    conn = open_database(tmp_path / "lazy.sqlite")
    cli._bootstrap(conn)
    assert "llm_cd_plan_identity" not in _tables_present(conn)
    _ensure_identity_table(conn)
    assert "llm_cd_plan_identity" in _tables_present(conn)
    assert set(LAZY_TABLES) <= _tables_declared_in_source()


def test_the_census_can_fail(tmp_path: Path):
    """The falsifying twin: an empty database must NOT satisfy the census.

    Without this, a `_tables_declared_in_source` that silently returned nothing --
    a moved directory, a changed DDL spelling -- would make the test above pass by
    measuring nothing, which is the failure mode a census has.
    """
    conn = open_database(tmp_path / "empty.sqlite")
    assert _tables_declared_in_source() - _tables_present(conn)
