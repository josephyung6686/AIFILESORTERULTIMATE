"""Done-means 22, by runtime introspection. Not by scanning text for tokens.

`74` §6 B13's named test is
`test_no_module_in_review_surface_imports_a_mutation_or_scoring_surface` and its
negative twin is `test_the_guard_rejects_a_sabotage_module_that_calls_os_rename`.

**Why introspection and not a text search.** The authoring brief: "a text search
matches comments and docstrings, and scanning text for a token has produced a
false result nine times on this project." So the guards below walk what each
module BINDS, not what its source spells -- and every one of them is written to
take a mapping of modules, so it can be pointed at a deliberately sabotaged module
that is not on disk. A guard proven only against a clean package is
indistinguishable from a guard that cannot find anything.
"""
from __future__ import annotations

import ast
import importlib
import inspect
import os
import os.path
import pathlib
import pkgutil
import shutil
import sys
import types

import pytest

import review_surface

MODULE_NAMES = tuple(
    sorted(info.name for info in pkgutil.iter_modules(review_surface.__path__)))


def _modules() -> dict[str, types.ModuleType]:
    return {name: importlib.import_module(f"review_surface.{name}")
            for name in MODULE_NAMES}


def _sabotage(source: str, name: str = "offender") -> dict[str, types.ModuleType]:
    """A real, importable module built from source and never written to disk.

    This is what makes each guard below a TWIN rather than a smoke test: the same
    function that reports nothing against the package must report something
    against this.
    """
    module = types.ModuleType(f"review_surface_sabotage_{name}")
    module.__file__ = f"<sabotage {name}>"
    module.__source__ = source
    exec(compile(source, module.__file__, "exec"), module.__dict__)
    return {name: module}


def _bindings(module: types.ModuleType) -> dict[str, object]:
    """Every name the module BINDS, with what it is. Not its source text."""
    return {name: value for name, value in vars(module).items()
            if not name.startswith("__")}


#: The callables that MUTATE a filesystem. Held as objects, so a module that
#: imported one under any alias is still caught and a module that merely writes
#: the word "rename" in prose is not.
FILESYSTEM_MUTATORS = frozenset({
    os.rename, os.replace, os.remove, os.unlink, os.rmdir, os.makedirs,
    os.mkdir, shutil.move, shutil.copy, shutil.copy2, shutil.rmtree,
})


def _is(value, forbidden) -> bool:
    """Membership that survives an unhashable binding.

    A module binds dicts and lists as well as functions, and `value in {...}`
    raises `TypeError` on those. A guard that crashed on the first dict would
    stop checking the rest of the module, which is a guard that passes by not
    finishing.
    """
    return any(value is one for one in forbidden)


def _mutation_bindings(modules) -> list[str]:
    """Every binding that is, or leads to, a filesystem mutation.

    `os` itself is bound as an offender because it is a route to every mutator
    in the set; a module that has no business renaming a file has no business
    holding the module that can.
    """
    offenders: list[str] = []
    for name, module in modules.items():
        for bound, value in _bindings(module).items():
            if _is(value, FILESYSTEM_MUTATORS) or value is os:
                offenders.append(f"{name}.{bound}")
    return offenders


def _path_bindings(modules) -> list[str]:
    """B3: P13 composes no path. Judged on bindings, not on the word "path"."""
    forbidden = (pathlib, pathlib.Path, pathlib.PurePath, os.path)
    return [f"{name}.{bound}" for name, module in modules.items()
            for bound, value in _bindings(module).items()
            if _is(value, forbidden)]


def _decision_bindings(modules) -> list[str]:
    """Callables owned by the parts that DO score, classify and validate.

    Held as live objects, so a rename in P6/P7/P8/P11 breaks this guard instead
    of silently defeating it.
    """
    from llm_harness.validation import validate_response
    from placement.scoring import assess, score_candidates
    from privacy.classification import resolve_class

    forbidden = (score_candidates, assess, resolve_class, validate_response)
    return [f"{name}.{bound}" for name, module in modules.items()
            for bound, value in _bindings(module).items()
            if _is(value, forbidden)]


def _egress_bindings(modules) -> list[str]:
    roots = ("urllib", "http", "socket", "smtplib", "ftplib", "requests",
             "httpx", "subprocess")
    offenders: list[str] = []
    for name, module in modules.items():
        for bound, value in _bindings(module).items():
            origin = str(getattr(value, "__module__", "")
                         or getattr(value, "__name__", ""))
            if origin.split(".")[0] in roots:
                offenders.append(f"{name}.{bound} from {origin}")
    return offenders


def test_no_module_in_review_surface_imports_a_mutation_or_scoring_surface():
    """`74` §6 B13's named test, and Done-means 22.

    Four properties, one assertion each, all read off live bindings:
    no filesystem mutation, no path composition, no scoring/classification/
    validation callable, and no route off this machine.
    """
    modules = _modules()
    assert _mutation_bindings(modules) == []
    assert _path_bindings(modules) == []
    assert _decision_bindings(modules) == []
    assert _egress_bindings(modules) == []


def test_the_guard_rejects_a_sabotage_module_that_calls_os_rename():
    """`74` §6 B13's negative twin, and the point of the whole task.

    A guard whose only evidence is "it found nothing in the real package" is
    worth nothing. Each of the four guards above is driven against a module that
    genuinely does the forbidden thing -- imported, bound, executable -- and must
    report it. The `os.rename` case is asserted three ways, because the three
    import forms are three different bindings and a guard that caught only one
    would leave the other two open.
    """
    # 1. `from os import rename` -- the direct binding.
    assert _mutation_bindings(_sabotage(
        "from os import rename\n"
        "def move(a, b):\n"
        "    rename(a, b)\n"))
    # 2. `import os` then `os.rename(...)` -- the module is the route.
    assert _mutation_bindings(_sabotage(
        "import os\n"
        "def move(a, b):\n"
        "    os.rename(a, b)\n"))
    # 3. An alias, which no text search for "os.rename" would ever find.
    assert _mutation_bindings(_sabotage(
        "from os import rename as _mv\n"
        "def move(a, b):\n"
        "    _mv(a, b)\n"))
    assert _mutation_bindings(_sabotage("from shutil import move\n"))
    # And the other three guards fail against their own sabotage.
    assert _path_bindings(_sabotage("import pathlib\n"))
    assert _path_bindings(_sabotage("from pathlib import Path\n"))
    assert _decision_bindings(_sabotage(
        "from placement.scoring import score_candidates\n"))
    assert _decision_bindings(_sabotage(
        "from privacy.classification import resolve_class\n"))
    assert _egress_bindings(_sabotage("import urllib.request\n"))
    assert _egress_bindings(_sabotage("import subprocess\n"))
    # A module that does none of it is clean, so the guards are about the
    # forbidden thing rather than about having any imports at all.
    clean = _sabotage("import json\nimport sqlite3\n", name="clean")
    assert _mutation_bindings(clean) == []
    assert _path_bindings(clean) == []
    assert _decision_bindings(clean) == []
    assert _egress_bindings(clean) == []


def test_the_package_is_the_modules_this_wave_has_built():
    """A new module is a deliberate act, so it updates this list on the way in."""
    assert set(MODULE_NAMES) == {
        "bulk", "citations", "collect", "consent_surface", "evaluation",
        "items", "labels", "learning_view", "locations", "move_permission",
        "presentation", "progress", "records", "redaction_boundary",
        "rejections", "residual", "routing", "schema", "states", "store",
        "versions_view", "vocabulary",
    }


def _numeric_literals(trees) -> list[str]:
    """Every integer literal beyond 0 and 1 in a module body.

    The brief: no invented threshold, weight or catalogue as a module-level
    constant. A count is read or passed; a literal is how one gets CHOSEN by
    accident, and P13 has no number of its own to choose.
    """
    offenders: list[str] = []
    for name, tree in trees:
        for node in ast.walk(tree):
            if (isinstance(node, ast.Constant)
                    and isinstance(node.value, int)
                    and not isinstance(node.value, bool)
                    and node.value not in (0, 1)):
                offenders.append(f"{name}:{node.lineno} {node.value}")
    return offenders


def _package_trees():
    root = pathlib.Path(review_surface.__file__).resolve().parent
    return [(path.name, ast.parse(path.read_text()))
            for path in sorted(root.glob("*.py"))]


def test_no_numeric_literal_beyond_zero_and_one_lives_in_the_package():
    """Every number is injected, and absent means refuse.

    Asserted in both directions: nothing in the package, and a module that picks
    a threshold out of the air is caught.
    """
    assert _numeric_literals(_package_trees()) == []
    assert _numeric_literals([("offender.py", ast.parse("LIMIT = 90\n"))])
    assert _numeric_literals([("offender.py", ast.parse("x = items[:10]\n"))])
    assert _numeric_literals(
        [("offender.py", ast.parse("flag = 0\nother = 1\n"))]) == []


def test_no_module_binds_a_test_fixture_module():
    """`src/review_surface/` never imports a tests-only stand-in."""
    for name, tree in _package_trees():
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module:
                assert "fixtures" not in node.module, (
                    f"{name} imports {node.module}")
            if isinstance(node, ast.Import):
                for alias in node.names:
                    assert "fixtures" not in alias.name, (
                        f"{name} imports {alias.name}")


def test_p13_writes_only_its_own_three_tables(p13_conn):
    """Done-means 22's writing clause, over every table in the live database."""
    from review_surface.schema import REVIEW_TABLES

    all_tables = {row["name"] for row in p13_conn.execute(
        "SELECT name FROM sqlite_master WHERE type = 'table'")}
    other = all_tables - set(REVIEW_TABLES) - {"events"}
    assert other, "the fixture database must hold other parts' tables"
    for name, module in _modules().items():
        source = inspect.getsource(module)
        for table in sorted(other):
            for statement in (f"INSERT INTO {table}", f"UPDATE {table}",
                              f"DELETE FROM {table}"):
                assert statement not in source, (
                    f"review_surface.{name} writes {table}, which P13 does not "
                    "own")


def test_every_module_is_stdlib_plus_this_project_only():
    """The brief: stdlib only. No third-party import anywhere in the package."""
    project_roots = {
        "database_agent", "eval_harness", "evidence_shape", "extractors",
        "facts", "grouping", "llm_harness", "placement", "privacy",
        "questions", "readers", "recognition", "review_surface", "scan_agent",
        "tree_design",
    }
    for name, module in _modules().items():
        for bound, value in _bindings(module).items():
            origin = str(getattr(value, "__module__", "")
                         or getattr(value, "__name__", ""))
            root = origin.split(".")[0]
            if not root or root in project_roots:
                continue
            assert root in sys.stdlib_module_names, (
                f"review_surface.{name} binds {bound} from third-party "
                f"package {root!r}")


def test_the_untouched_protected_refusal_is_reachable_from_every_collector():
    """`67` §1, restated as a structural property of the package.

    Every function that produces a `ReviewAction` must go through `collect`,
    which is where the protected-container refusal lives. A second collection
    path would be a second place that refusal has to be remembered.
    """
    from review_surface import collect as collect_module

    writers = []
    for name, tree in _package_trees():
        if name in ("collect.py", "records.py", "store.py"):
            continue
        for node in ast.walk(tree):
            if (isinstance(node, ast.FunctionDef)
                    and isinstance(node.returns, ast.Name)
                    and node.returns.id == "ReviewAction"):
                writers.append((name, node))
    assert writers, "no action-producing function found; the guard checks nothing"
    for name, node in writers:
        calls = {sub.func.id for sub in ast.walk(node)
                 if isinstance(sub, ast.Call) and isinstance(sub.func, ast.Name)}
        assert "collect" in calls, (
            f"{name}.{node.name} returns a ReviewAction without going through "
            "collect, so the untouched-protected refusal is not in its path")
    assert collect_module.ProtectedContainerHasNoAction is not None
