"""Context-graph package must never import the sorter move stack.

Architecture map §6 kill rule 1: ``src/items/`` must not import ``mutation``
or ``apply_run``. ``cli`` may compose both; items must not.
"""
from __future__ import annotations

import ast
import importlib
from pathlib import Path

import pytest

ITEMS_ROOT = Path(__file__).resolve().parents[2] / "src" / "items"
FORBIDDEN_ROOTS = ("mutation", "apply_run")


def _py_files():
    return sorted(p for p in ITEMS_ROOT.rglob("*.py") if p.is_file())


def _forbidden_import(module: str | None) -> str | None:
    if not module:
        return None
    top = module.split(".", 1)[0]
    if top in FORBIDDEN_ROOTS:
        return module
    return None


def _scan_source(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    tree = ast.parse(text, filename=str(path))
    hits: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                bad = _forbidden_import(alias.name)
                if bad:
                    hits.append(f"import {bad}")
        elif isinstance(node, ast.ImportFrom):
            bad = _forbidden_import(node.module)
            if bad:
                hits.append(f"from {bad} import …")
        elif isinstance(node, ast.Call):
            # importlib.import_module("mutation…") / __import__("apply_run…")
            func = node.func
            name = None
            if isinstance(func, ast.Name):
                name = func.id
            elif isinstance(func, ast.Attribute):
                name = func.attr
            if name in {"import_module", "__import__"} and node.args:
                arg0 = node.args[0]
                if isinstance(arg0, ast.Constant) and isinstance(arg0.value, str):
                    bad = _forbidden_import(arg0.value)
                    if bad:
                        hits.append(f"{name}({bad!r})")
    return hits


@pytest.mark.parametrize("path", _py_files(), ids=lambda p: str(p.relative_to(ITEMS_ROOT)))
def test_items_source_never_imports_mutation_or_apply_run(path: Path):
    hits = _scan_source(path)
    assert hits == [], f"{path.relative_to(ITEMS_ROOT)}: {hits}"


def test_loaded_items_modules_have_no_forbidden_deps():
    """Import every items submodule and check sys.modules edges stay clean."""
    import sys

    before = set(sys.modules)
    package = importlib.import_module("items")
    root = Path(package.__file__).resolve().parent
    for path in sorted(root.rglob("*.py")):
        if path.name == "__init__.py" and path.parent == root:
            mod_name = "items"
        else:
            rel = path.relative_to(root).with_suffix("")
            mod_name = "items." + ".".join(rel.parts)
        importlib.import_module(mod_name)
    added = set(sys.modules) - before
    leaked = sorted(
        name for name in added
        if name == "mutation"
        or name.startswith("mutation.")
        or name == "apply_run"
        or name.startswith("apply_run.")
    )
    assert leaked == [], f"importing items pulled in {leaked}"
