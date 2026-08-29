"""Where this package may and may not reach.

`src/facts/fields.py` states the rule and `src/tree_design/catalogue.py` enforces the
same shape for the template library: *"`planning/domains/` is a research and
authorship surface, not a runtime import target. A later deterministic compiler
consumes ratified records and emits a versioned manifest."*

This file is what makes that checkable by import inspection rather than by hope.
"""
from __future__ import annotations

import ast
import importlib
import json
from pathlib import Path

import pytest

from recognition.compile import compile_rules

PACKAGE = Path(__file__).resolve().parents[2] / "src" / "recognition"
NODES = Path(__file__).resolve().parents[2] / "planning" / "domains" / "nodes"
MANIFEST = PACKAGE / "library" / "recognition.json"

#: `compile.py` is the build step and is the one module allowed near a node row.
#: Everything else in the package is on a runtime path.
RUNTIME_MODULES = ("__init__", "vocabulary", "rules", "detector")

#: `tests/p7/test_p7_no_invention.py` guards these repo-wide: exactly three modules
#: may bind a P4 text materialiser. A detector that pulled whole text units to match
#: against would quietly become a fourth.
MATERIALISERS = frozenset({"raw_value_at", "text_units_for_run", "text_unit_at",
                           "unit_for_observation"})


def module_source(name: str) -> ast.Module:
    return ast.parse((PACKAGE / f"{name}.py").read_text(encoding="utf-8"))


def imported_names(tree: ast.Module) -> set[str]:
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                names.add(node.module)
            names.update(alias.name for alias in node.names)
    return names


@pytest.mark.parametrize("name", RUNTIME_MODULES)
def test_no_runtime_module_imports_the_compiler(name):
    assert "recognition.compile" not in imported_names(module_source(name)), name


@pytest.mark.parametrize("name", RUNTIME_MODULES)
def test_no_runtime_module_can_reach_the_filesystem(name):
    # `PurePath` is allowed and `Path` is not: `PurePath` is string algebra over a
    # path and cannot stat, open or list anything, which is exactly what
    # `scan_agent.exclusion.is_protected_container` needs and all it needs.
    names = imported_names(module_source(name))
    for forbidden in ("os", "io", "pathlib.Path", "Path", "glob", "shutil",
                      "importlib.resources"):
        assert forbidden not in names, (name, forbidden)
    source = (PACKAGE / f"{name}.py").read_text(encoding="utf-8")
    for node in ast.walk(module_source(name)):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            assert node.func.id != "open", name
    assert "read_text" not in source, name


def test_no_module_in_the_package_imports_planning_code():
    for path in sorted(PACKAGE.glob("*.py")):
        names = imported_names(ast.parse(path.read_text(encoding="utf-8")))
        assert not [name for name in names if name.startswith("planning")], path.name


def test_no_module_in_the_package_binds_a_P4_text_materialiser():
    for path in sorted(PACKAGE.glob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        assert not (imported_names(tree) & MATERIALISERS), path.name
        module = importlib.import_module(f"recognition.{path.stem}"
                                         if path.stem != "__init__"
                                         else "recognition")
        assert not (set(vars(module)) & MATERIALISERS), path.name


def test_the_compiler_is_the_only_module_that_names_a_node_row_directory():
    # The build step reads `planning/domains/nodes` and it does so under a
    # `__main__` guard, so importing it reads nothing.
    named = [path.name for path in sorted(PACKAGE.glob("*.py"))
             if "planning" in path.read_text(encoding="utf-8").lower()
             and path.name != "compile.py"]
    # Prose citations of the rule are expected; a module that BUILDS the path is
    # not. Checked as syntax rather than as text.
    for name in named:
        tree = ast.parse((PACKAGE / name).read_text(encoding="utf-8"))
        literals = [node.value for node in ast.walk(tree)
                    if isinstance(node, ast.Constant) and isinstance(node.value, str)
                    and node.value.startswith("planning/")]
        assert not literals, (name, literals)


def test_importing_the_runtime_modules_reads_no_file():
    # A module that loaded a default manifest at import would make `load_rules`'s
    # injected reader decorative.
    for name in RUNTIME_MODULES:
        module = importlib.import_module(
            "recognition" if name == "__init__" else f"recognition.{name}")
        assert not [value for value in vars(module).values()
                    if isinstance(value, Path)], name


def test_the_packaged_manifest_is_exactly_what_the_live_node_rows_compile_to():
    """The artifact is derived, not authored.

    If this fails after someone edits `planning/domains/nodes/`, the manifest is
    stale and the remedy is to re-run the compiler::

        PYTHONPATH=src python3 -m recognition.compile planning/domains/nodes \\
            > src/recognition/library/recognition.json

    It is asserted rather than trusted because a hand-edited manifest is a rule set
    with no research behind it, which is worse than no rule set at all.
    """
    recompiled = compile_rules(
        json.loads(path.read_text(encoding="utf-8"))
        for path in sorted(NODES.glob("*.json")))
    packaged = json.loads(MANIFEST.read_text(encoding="utf-8"))
    assert json.dumps(recompiled, sort_keys=True) == json.dumps(
        packaged, sort_keys=True), (
        "src/recognition/library/recognition.json is stale; re-run "
        "`python3 -m recognition.compile planning/domains/nodes`")
