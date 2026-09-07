# tests/test_packaging_declares_what_the_readers_import.py
"""R-34 -- the install that produces a working product, and the one that does not.

`pyproject.toml` declared four of the twelve third-party names `src/readers/`
actually imports. A person who ran `pip install .[readers]` got pdfium, pdfminer
and Apple's Vision and Quartz, and did NOT get `python-docx`, `onnxruntime`,
`tokenizers`, `numpy`, Cocoa, `anthropic` or `openai` -- so every `.docx` in their
corpus, the whole semantic recogniser and both model transports were missing from a
deployment that believed it was complete.

**The rule this must not break, and how it is kept.** P5's SPEC says the engine
"adds no third-party runtime dependency": every format reader is a caller-supplied
callable, so the libraries belong to a deployment that chose them and never to the
part consuming their output. `[project] dependencies` therefore stays EMPTY and a
test below holds it empty. Everything measured here is declared in an optional
group, which is what `[project.optional-dependencies]` is for.

**The declaration is derived, not transcribed.** This file re-runs the measurement
rather than comparing against a list somebody typed: it parses every module under
`src/readers/`, keeps the top-level import names that are neither standard library
nor this repo's own, and resolves each to its distribution through
`importlib.metadata.packages_distributions()`. That mapping is the installed
environment's own answer -- `docx` to `python-docx`, `AppKit` to
`pyobjc-framework-Cocoa` -- so no alias table is authored here and a new reader
with a new library fails this test on the day it lands rather than on the day
somebody installs it.

**A missing library must arrive by name.** The failure this guards is not a
crash, it is a quiet one: a reader that caught `ImportError` and returned a no-op
would make an uninstalled library indistinguishable from §2.4's `unsupported`, and
the run would report "no extractor exists for this format in this deployment"
about a format this deployment reads perfectly once the wheel is there. The last
test holds every `except ImportError` in the readers layer to raising.
"""
from __future__ import annotations

import ast
import pathlib
import sys
import tomllib
from importlib.metadata import packages_distributions

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
READERS = ROOT / "src" / "readers"
PYPROJECT = ROOT / "pyproject.toml"


def _manifest() -> dict:
    return tomllib.loads(PYPROJECT.read_text(encoding="utf-8"))


def _own_modules() -> set[str]:
    """Everything importable from `src/`, which is this repo and not a dependency."""
    source = ROOT / "src"
    return ({path.stem for path in source.glob("*.py")}
            | {path.name for path in source.iterdir() if path.is_dir()})


def _third_party_imports() -> dict[str, set[str]]:
    """Top-level import name -> the reader modules that import it."""
    stdlib = set(sys.stdlib_module_names)
    own = _own_modules()
    found: dict[str, set[str]] = {}
    for path in sorted(READERS.rglob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                names = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
                names = [node.module]
            else:
                continue
            for name in names:
                top = name.split(".")[0]
                if top in stdlib or top in own or top == "__future__":
                    continue
                found.setdefault(top, set()).add(path.name)
    return found


def _declared_distributions() -> set[str]:
    """Every distribution named in any optional group, normalised.

    Read off the whole table rather than one group by name: which group a library
    belongs in is a packaging judgement that may change, and a test that pinned the
    group would fail for a rearrangement that broke nothing.
    """
    groups = _manifest()["project"].get("optional-dependencies", {})
    declared = set()
    for requirements in groups.values():
        for requirement in requirements:
            # "pyobjc-framework-Vision>=10.0; sys_platform == 'darwin'" -> the name
            head = requirement.split(";")[0]
            for separator in (">=", "==", "<=", "~=", "!=", ">", "<", "["):
                head = head.split(separator)[0]
            declared.add(head.strip().lower().replace("_", "-"))
    return declared


def test_every_library_the_readers_import_is_declared():
    """The measurement, re-run. This is the whole of R-34's first half."""
    declared = _declared_distributions()
    imports = _third_party_imports()
    resolver = packages_distributions()

    undeclared = {}
    for name, modules in sorted(imports.items()):
        providers = resolver.get(name)
        assert providers, (
            f"{name!r} is imported by {sorted(modules)} and no installed "
            "distribution provides it, so this test cannot say what to declare. "
            "Install it, or remove the import.")
        if not any(p.lower().replace("_", "-") in declared for p in providers):
            undeclared[name] = providers

    assert not undeclared, (
        "these libraries are imported by `src/readers/` and declared by no "
        f"optional group in pyproject.toml: {undeclared}. An install that "
        "believed it was complete would be missing them.")


def test_the_engine_still_declares_no_runtime_dependency():
    """P5's SPEC: it "adds no third-party runtime dependency". Every library above
    belongs to a deployment that chose it, so `dependencies` is empty and the
    engine can be installed and read without one of them present."""
    assert _manifest()["project"]["dependencies"] == []


def test_there_is_a_console_script_and_it_points_at_the_cli():
    """A product a person installs is a product a person can then run. The name is
    the one `cli.py` already gives its own parser, so `--help` names the command
    that produced it rather than a second spelling nobody chose."""
    scripts = _manifest()["project"].get("scripts", {})
    assert scripts, "an installed product with no command is a library"
    assert scripts.get("database-agent") == "cli:main", scripts


def test_no_reader_turns_a_missing_library_into_an_unsupported_format():
    """Every `except ImportError` in the readers layer must raise.

    The quiet failure: a handler that returned `None` or a no-op reader would make
    an uninstalled wheel indistinguishable from §2.4's `unsupported`, and the run
    would tell a person "no extractor exists for this format in this deployment"
    about a format it reads perfectly once the library is installed. A raise
    carries the library's name to whoever can act on it.
    """
    masked = []
    for path in sorted(READERS.rglob("*.py")):
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            if not isinstance(node, ast.ExceptHandler):
                continue
            caught = ast.dump(node.type) if node.type else ""
            if "ImportError" not in caught and "ModuleNotFoundError" not in caught:
                continue
            if not any(isinstance(inner, ast.Raise)
                       for inner in ast.walk(ast.Module(body=node.body,
                                                        type_ignores=[]))):
                masked.append(f"{path.name}:{node.lineno}")

    assert not masked, (
        "these handlers swallow a missing library instead of naming it: "
        f"{masked}")


@pytest.mark.parametrize("module", sorted(
    path.stem for path in READERS.glob("*.py") if path.stem != "__init__"))
def test_every_reader_module_imports(module):
    """The blunt one, and it is the test the item asked for: in THIS environment,
    with the declared libraries installed, every reader module imports. A missing
    declaration shows up here as an ImportError naming the module that needs it.
    """
    __import__(f"readers.{module}")
