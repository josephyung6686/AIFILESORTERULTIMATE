"""P8 Task 11 — no-bypass and dependency-boundary guards.

AST and import introspection, never comment-sensitive substring scans. A docstring
that *explains* why transport is the only egress must not satisfy or break a guard.
"""
from __future__ import annotations

import ast
import inspect
import pathlib
from typing import get_type_hints

from llm_harness.harness import run_call
from llm_harness.transport import ModelClient, issue
from privacy.binding import consume_release
from privacy.release import Released


HARNESS_ROOT = pathlib.Path(__file__).resolve().parents[2] / "src" / "llm_harness"

SDK_ROOTS = frozenset({
    "openai", "anthropic", "litellm", "groq", "together", "vertexai",
    "google.generativeai", "google.genai", "boto3", "botocore",
    "cohere", "mistralai", "huggingface_hub", "transformers",
    "requests", "httpx", "aiohttp", "httpcore",
})

#: Planning trees, prompt corpora, deferred catalogues, and P5 reader adapters.
FORBIDDEN_ROOTS = frozenset({
    "planning", "prompts", "readers", "pdfminer", "Quartz", "Vision",
})

#: Evidence-store readers and unbuilt neighbour producers. Transport may import
#: none of these. P6 (`facts`) is allowed only on the Site-A seam, not on egress.
TRANSPORT_FORBIDDEN = frozenset({
    "facts", "grouping", "tree_design", "placement", "templates", "residual",
    "eval_harness", "orchestrator", "production", "evidence_shape.store",
    "extractors",
})

NEIGHBOUR_PRODUCERS = frozenset({
    "grouping", "tree_design", "placement", "templates", "residual",
})


def modules() -> list[pathlib.Path]:
    return sorted(
        path for path in HARNESS_ROOT.glob("*.py")
        if path.name != "__pycache__"
    )


def _docstrings(tree: ast.AST) -> set[int]:
    found = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef,
                             ast.AsyncFunctionDef)):
            body = getattr(node, "body", None)
            if (body and isinstance(body[0], ast.Expr)
                    and isinstance(body[0].value, ast.Constant)
                    and isinstance(body[0].value.value, str)):
                found.add(id(body[0].value))
    return found


def imports_of(path: pathlib.Path) -> set[str]:
    tree = ast.parse(path.read_text(), filename=str(path))
    found: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            found.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            found.add(module)
            found.update(f"{module}.{alias.name}" for alias in node.names)
    return found


def _is_invoke_call(node: ast.AST) -> bool:
    if not isinstance(node, ast.Call):
        return False
    func = node.func
    if isinstance(func, ast.Attribute) and func.attr == "invoke":
        return True
    if isinstance(func, ast.Call):
        inner = func.func
        if (isinstance(inner, ast.Name) and inner.id == "getattr"
                and len(func.args) >= 2
                and isinstance(func.args[1], ast.Constant)
                and func.args[1].value == "invoke"):
            return True
    return False


def invoke_sites(path: pathlib.Path) -> list[tuple[str, str | None]]:
    """Every `.invoke` call, with the enclosing function from a visitor stack.

    Line-range enclosing is wrong for nested functions; the stack is the
    function that actually contains the Call.
    """
    tree = ast.parse(path.read_text(), filename=str(path))
    found: list[tuple[str, str | None]] = []

    class Visitor(ast.NodeVisitor):
        def __init__(self) -> None:
            self.stack: list[str] = []

        def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
            self.stack.append(node.name)
            self.generic_visit(node)
            self.stack.pop()

        visit_AsyncFunctionDef = visit_FunctionDef

        def visit_Call(self, node: ast.Call) -> None:
            if _is_invoke_call(node):
                found.append((path.name, self.stack[-1] if self.stack else None))
            self.generic_visit(node)

        def visit_Assign(self, node: ast.Assign) -> None:
            if isinstance(node.value, ast.Attribute) and node.value.attr == "invoke":
                found.append((path.name, self.stack[-1] if self.stack else "aliased"))
            self.generic_visit(node)

        def visit_Lambda(self, node: ast.Lambda) -> None:
            for child in ast.walk(node):
                if _is_invoke_call(child) or (
                    isinstance(child, ast.Attribute) and child.attr == "invoke"
                ):
                    found.append((path.name, "lambda"))
            self.generic_visit(node)

    Visitor().visit(tree)
    return found


def function_def(path: pathlib.Path, name: str) -> ast.FunctionDef:
    tree = ast.parse(path.read_text(), filename=str(path))
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return node
    raise AssertionError(f"{path.name} defines no {name!r}")


def calls_named(fn: ast.FunctionDef, name: str) -> list[ast.Call]:
    found: list[ast.Call] = []
    for node in ast.walk(fn):
        if isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Name) and func.id == name:
                found.append(node)
            elif isinstance(func, ast.Attribute) and func.attr == name:
                found.append(node)
    return found


def code_strings(path: pathlib.Path) -> set[str]:
    tree = ast.parse(path.read_text(), filename=str(path))
    skip = _docstrings(tree)
    return {
        node.value for node in ast.walk(tree)
        if isinstance(node, ast.Constant) and id(node) not in skip
        and isinstance(node.value, str)
    }


def test_the_invoke_and_import_helpers_fail_on_planted_violations(tmp_path):
    """Negative control: a walker that returned nothing would make every guard green."""
    planted = tmp_path / "planted_bypass.py"
    planted.write_text(
        "import openai\n"
        "from readers.pdf_pdfminer import parse\n"
        "from facts.llm_seam import FactRequest\n"
        "def run_call(model_client):\n"
        "    return model_client.invoke(b'x')\n"
        "def issue(released, model_client):\n"
        "    fn = model_client.invoke\n"
        "    return fn(b'y')\n",
        encoding="utf-8",
    )
    sites = invoke_sites(planted)
    assert ("planted_bypass.py", "run_call") in sites
    assert ("planted_bypass.py", "issue") in sites  # aliased invoke
    imported = imports_of(planted)
    assert "openai" in imported
    assert "readers.pdf_pdfminer" in imported
    assert "facts.llm_seam" in imported
    strings = code_strings(planted)
    assert "import openai" not in strings  # the statement is not a string literal


def test_run_call_accepts_model_client_but_does_not_invoke_it():
    hints = get_type_hints(run_call)
    assert hints["model_client"] is ModelClient
    parameters = inspect.signature(run_call).parameters
    assert parameters["model_client"].default is inspect.Parameter.empty
    assert parameters["model_client"].kind is inspect.Parameter.KEYWORD_ONLY

    harness = HARNESS_ROOT / "harness.py"
    assert invoke_sites(harness) == []
    issue_calls = calls_named(function_def(harness, "_issue_and_validate"), "issue")
    assert issue_calls, "run_call must forward the client to issue"
    forwarded = False
    for call in issue_calls:
        for keyword in call.keywords:
            if keyword.arg == "model_client":
                assert isinstance(keyword.value, ast.Name)
                assert keyword.value.id == "model_client"
                forwarded = True
    assert forwarded, "issue must be called with the same model_client object"


def test_only_transport_issue_invokes_the_model_client():
    sites: list[tuple[str, str | None]] = []
    for path in modules():
        sites.extend(invoke_sites(path))
    assert sites == [("transport.py", "issue")], sites


def test_transport_issue_requires_live_released_and_calls_consume_release():
    hints = get_type_hints(issue)
    assert hints["released"] is Released
    parameters = inspect.signature(issue).parameters
    assert parameters["released"].default is inspect.Parameter.empty
    assert "Denied" not in str(hints["released"])
    assert "NeedsConsent" not in str(hints["released"])

    fn = function_def(HARNESS_ROOT / "transport.py", "issue")
    consume_calls = calls_named(fn, "consume_release")
    assert consume_calls, "issue must spend the live P7 release before egress"
    invoke_in_issue = [
        node for node in ast.walk(fn) if _is_invoke_call(node)
    ]
    assert invoke_in_issue, "issue is the invoke site"
    consume_line = consume_calls[0].lineno
    invoke_line = invoke_in_issue[0].lineno
    assert consume_line < invoke_line, (
        "consume_release must precede model_client.invoke so a call is not "
        "constructible without spending the live Released"
    )
    assert consume_release is not None
    imported = imports_of(HARNESS_ROOT / "transport.py")
    assert "privacy.release" in imported
    assert "Released" in imported or "privacy.release.Released" in imported
    assert "privacy.binding" in imported
    assert "consume_release" in imported or "privacy.binding.consume_release" in imported


def test_outbound_transport_imports_neither_evidence_readers_nor_later_parts():
    imported = imports_of(HARNESS_ROOT / "transport.py")
    for forbidden in TRANSPORT_FORBIDDEN:
        assert forbidden not in imported, forbidden
        assert not any(
            name == forbidden or name.startswith(forbidden + ".")
            for name in imported
        ), (forbidden, imported)
    assert "privacy.binding" in imported
    assert "llm_harness.store" in imported


def test_no_p8_module_imports_planning_prompts_catalogues_sdks_or_readers():
    violations: list[tuple[str, str]] = []
    path_literals: list[tuple[str, str]] = []
    for path in modules():
        imported = imports_of(path)
        for name in imported:
            root = name.split(".", 1)[0]
            if root in SDK_ROOTS or name in SDK_ROOTS:
                violations.append((path.name, name))
            if root in FORBIDDEN_ROOTS or name in FORBIDDEN_ROOTS:
                violations.append((path.name, name))
            if root in NEIGHBOUR_PRODUCERS:
                violations.append((path.name, name))
        for literal in code_strings(path):
            collapsed = literal.replace("\\", "/")
            for token in (
                "planning/domains", "deferred-catalogues", "planning/prompts",
            ):
                if token in collapsed:
                    path_literals.append((path.name, literal[:80]))
    assert violations == [], violations
    assert path_literals == [], path_literals


def test_p8_public_surface_still_exports_no_transport_or_client():
    import llm_harness
    assert "ModelClient" not in llm_harness.__all__
    assert "issue" not in llm_harness.__all__
    assert llm_harness.run_call is run_call
    assert llm_harness.__all__ == [
        "run_call",
        "Dossier",
        "P8Verdict",
        "Refusal",
        "ValidationUnavailable",
        "NeedsConsent",
    ]
