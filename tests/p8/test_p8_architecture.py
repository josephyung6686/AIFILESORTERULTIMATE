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
from privacy.release import Released


SRC_ROOT = pathlib.Path(__file__).resolve().parents[2] / "src"
HARNESS_ROOT = SRC_ROOT / "llm_harness"

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
    """P8 modules for P8-owned import and authorship guards."""
    return sorted(
        path for path in HARNESS_ROOT.rglob("*.py")
        if path.name != "__pycache__"
    )


def production_modules() -> list[pathlib.Path]:
    """Every production Python module for the product-wide egress invariant."""
    return sorted(SRC_ROOT.rglob("*.py"))


def source_label(path: pathlib.Path) -> str:
    try:
        return path.relative_to(SRC_ROOT).as_posix()
    except ValueError:
        return path.name


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


def _is_getattr_invoke(node: ast.AST) -> bool:
    """True for getattr(obj, "invoke") or builtins.getattr(obj, "invoke")."""
    if not isinstance(node, ast.Call):
        return False
    func = node.func
    is_getattr = (
        (isinstance(func, ast.Name) and func.id == "getattr")
        or (isinstance(func, ast.Attribute) and func.attr == "getattr")
    )
    if not is_getattr or len(node.args) < 2:
        return False
    key = node.args[1]
    return isinstance(key, ast.Constant) and key.value == "invoke"


def _is_invoke_binding(node: ast.AST) -> bool:
    if isinstance(node, ast.Attribute) and node.attr == "invoke":
        return True
    return _is_getattr_invoke(node)


def _is_invoke_call(node: ast.AST) -> bool:
    if not isinstance(node, ast.Call):
        return False
    func = node.func
    if isinstance(func, ast.Attribute) and func.attr == "invoke":
        return True
    if _is_getattr_invoke(func):
        return True
    return False


def _target_names(target: ast.AST) -> list[str]:
    if isinstance(target, ast.Name):
        return [target.id]
    if isinstance(target, (ast.Tuple, ast.List)):
        names: list[str] = []
        for elt in target.elts:
            names.extend(_target_names(elt))
        return names
    return []


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
            self.bound: list[set[str]] = [set()]

        def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
            self.stack.append(node.name)
            self.bound.append(set())
            self.generic_visit(node)
            self.bound.pop()
            self.stack.pop()

        visit_AsyncFunctionDef = visit_FunctionDef

        def _record_binding(self, value: ast.AST, names: list[str]) -> None:
            if not names or not _is_invoke_binding(value):
                return
            self.bound[-1].update(names)
            found.append((source_label(path), self.stack[-1] if self.stack else "aliased"))

        def visit_Call(self, node: ast.Call) -> None:
            if _is_invoke_call(node):
                found.append((source_label(path), self.stack[-1] if self.stack else None))
            elif isinstance(node.func, ast.Name) and node.func.id in self.bound[-1]:
                found.append((path.name, self.stack[-1] if self.stack else None))
            self.generic_visit(node)

        def visit_Assign(self, node: ast.Assign) -> None:
            names: list[str] = []
            for target in node.targets:
                names.extend(_target_names(target))
            self._record_binding(node.value, names)
            self.generic_visit(node)

        def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
            if node.value is not None and isinstance(node.target, ast.Name):
                self._record_binding(node.value, [node.target.id])
            self.generic_visit(node)

        def visit_NamedExpr(self, node: ast.NamedExpr) -> None:
            if isinstance(node.target, ast.Name):
                self._record_binding(node.value, [node.target.id])
            self.generic_visit(node)

        def visit_Lambda(self, node: ast.Lambda) -> None:
            for child in ast.walk(node):
                if _is_invoke_call(child) or _is_invoke_binding(child):
                    found.append((source_label(path), "lambda"))
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


_NESTED_SCOPES = (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)


def nodes_in_own_body(fn: ast.FunctionDef) -> list[ast.AST]:
    """AST nodes in fn.body, descending into With/Try/If, not nested defs."""
    found: list[ast.AST] = []

    class Own(ast.NodeVisitor):
        def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
            return

        visit_AsyncFunctionDef = visit_FunctionDef

        def visit_ClassDef(self, node: ast.ClassDef) -> None:
            return

        def generic_visit(self, node: ast.AST) -> None:
            found.append(node)
            super().generic_visit(node)

    for stmt in fn.body:
        if isinstance(stmt, _NESTED_SCOPES):
            continue
        Own().visit(stmt)
    return found


def consume_release_in_own_body(fn: ast.FunctionDef) -> ast.Call | None:
    """First consume_release Call that is a statement in fn's own body."""
    for node in nodes_in_own_body(fn):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if isinstance(func, ast.Name) and func.id == "consume_release":
            return node
        if isinstance(func, ast.Attribute) and func.attr == "consume_release":
            return node
    return None


def invokes_in_own_body(fn: ast.FunctionDef) -> list[ast.Call]:
    """Invoke Calls in fn's own body, including later calls of a bound invoke."""
    bound: set[str] = set()
    found: list[ast.Call] = []
    for node in nodes_in_own_body(fn):
        if isinstance(node, ast.Assign) and _is_invoke_binding(node.value):
            for target in node.targets:
                bound.update(_target_names(target))
        elif isinstance(node, ast.AnnAssign) and node.value is not None:
            if _is_invoke_binding(node.value) and isinstance(node.target, ast.Name):
                bound.add(node.target.id)
        elif isinstance(node, ast.NamedExpr):
            if _is_invoke_binding(node.value) and isinstance(node.target, ast.Name):
                bound.add(node.target.id)
        elif isinstance(node, ast.Call):
            if _is_invoke_call(node):
                found.append(node)
            elif isinstance(node.func, ast.Name) and node.func.id in bound:
                found.append(node)
    return found


def consume_precedes_every_invoke(fn: ast.FunctionDef) -> bool:
    consume = consume_release_in_own_body(fn)
    invokes = invokes_in_own_body(fn)
    if consume is None or not invokes:
        return False
    return all(node.lineno > consume.lineno for node in invokes)


#: `104` §18.15: THE NAME OF THE THING THAT CAN REACH THE SOCKET. The round trip
#: moved off the calling thread so the cloud lane could hold several at once, and
#: what crosses that boundary is a carrier holding the finished bytes and the
#: client. It is the transport's own private class, and the property Done-means 3
#: is about now reads: nothing can be sent that was not carried, and nothing is
#: carried until the release has been spent.
CARRIER = "_PendingSend"


def carrier_builds(path: pathlib.Path) -> list[tuple[str, str | None]]:
    """Every construction of the carrier, with the function that built it."""
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
            if isinstance(node.func, ast.Name) and node.func.id == CARRIER:
                found.append((source_label(path), self.stack[-1] if self.stack
                              else None))
            self.generic_visit(node)

    Visitor().visit(tree)
    return found


def carriers_in_own_body(fn: ast.FunctionDef) -> list[ast.Call]:
    """Carrier constructions that are statements in `fn`'s own body."""
    return [node for node in nodes_in_own_body(fn)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
            and node.func.id == CARRIER]


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
        "    return fn(b'y')\n"
        "def getattr_bind(model_client):\n"
        "    fn = getattr(model_client, 'invoke')\n"
        "    return fn(b'x')\n"
        "def annotated_bind(model_client):\n"
        "    fn: object = model_client.invoke\n"
        "    return fn(b'x')\n"
        "def walrus_bind(model_client):\n"
        "    return (fn := model_client.invoke)(b'x')\n"
        "def invoke_then_consume(released, model_client):\n"
        "    model_client.invoke(b'x')\n"
        "    consume_release(released)\n"
        "def nested_spend_then_invoke(released, model_client):\n"
        "    def unused():\n"
        "        consume_release(released)\n"
        "    model_client.invoke(b'x')\n"
        "def consume_then_invoke(released, model_client):\n"
        "    consume_release(released)\n"
        "    model_client.invoke(b'x')\n",
        encoding="utf-8",
    )
    sites = invoke_sites(planted)
    assert ("planted_bypass.py", "run_call") in sites
    assert ("planted_bypass.py", "issue") in sites  # aliased invoke
    assert ("planted_bypass.py", "getattr_bind") in sites  # getattr bind-then-call
    assert ("planted_bypass.py", "annotated_bind") in sites  # AnnAssign alias
    assert ("planted_bypass.py", "walrus_bind") in sites  # NamedExpr alias
    assert consume_precedes_every_invoke(
        function_def(planted, "invoke_then_consume")
    ) is False
    assert consume_precedes_every_invoke(
        function_def(planted, "nested_spend_then_invoke")
    ) is False
    assert consume_precedes_every_invoke(
        function_def(planted, "consume_then_invoke")
    ) is True
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
    # `104` §18.15: the forwarding statement is in `_issue_and_validate_steps`,
    # which is `_issue_and_validate` with the round trip left for the caller to
    # run. What is asserted is unchanged and is the whole point of the assertion:
    # the harness hands the transport the SAME client object it was given and
    # never touches it itself.
    issue_calls = calls_named(
        function_def(harness, "_issue_and_validate_steps"), "_issue_steps")
    assert issue_calls, "run_call must forward the client to the transport"
    forwarded = False
    for call in issue_calls:
        for keyword in call.keywords:
            if keyword.arg == "model_client":
                assert isinstance(keyword.value, ast.Name)
                assert keyword.value.id == "model_client"
                forwarded = True
    assert forwarded, "the transport must be called with the same model_client"


def test_only_transport_issue_invokes_the_model_client_product_wide():
    """One invoke in the whole product, and it is in `llm_harness/transport.py`.

    `104` §18.15 moved the round trip off the calling thread so the cloud lane
    could hold several at once, and moved the LINE from `issue`'s own body into
    the private carrier's `perform` -- the same module, the same one call. The
    module is what Done-means 3 is about ("`transport.issue` is the sole egress"),
    and the count is what this guard is about, so this is the same assertion with
    the function's new name in it.
    """
    sites: list[tuple[str, str | None]] = []
    for path in production_modules():
        sites.extend(invoke_sites(path))
    assert sites == [("llm_harness/transport.py", "perform")], sites


def test_transport_issue_requires_live_released_and_calls_consume_release():
    """A call is not constructible without spending the live `Released`.

    **`104` §18.15 CHANGED THE PROOF AND NOT THE PROPERTY.** Before the cloud lane
    the socket was a statement in `issue`'s own body, so "consume_release comes
    first" was a question about two lines of one function. The round trip now runs
    on whichever thread the driver chooses, and what crosses that boundary is a
    carrier holding the finished bytes and the client. So the property is stated
    over the carrier instead: nothing can reach the socket that was not carried;
    the carrier is built in exactly one place in the product; and in that place
    `consume_release` is a statement of the same body, above it.

    That is stronger in one respect and equal in the rest: a second construction of
    the carrier anywhere in `src/` now fails this test, where a second module-level
    helper calling `invoke` was already caught by the count above.
    """
    hints = get_type_hints(issue)
    assert hints["released"] is Released
    parameters = inspect.signature(issue).parameters
    assert parameters["released"].default is inspect.Parameter.empty
    assert "Denied" not in str(hints["released"])
    assert "NeedsConsent" not in str(hints["released"])

    transport = HARNESS_ROOT / "transport.py"
    # ONE PLACE IN THE PRODUCT BUILDS THE THING THAT CAN SEND.
    built: list[tuple[str, str | None]] = []
    for path in production_modules():
        built.extend(carrier_builds(path))
    assert built == [("llm_harness/transport.py", "_issue_steps")], built

    fn = function_def(transport, "_issue_steps")
    consume = consume_release_in_own_body(fn)
    assert consume is not None, (
        "the release must be spent in the same body that builds the carrier")
    carriers = carriers_in_own_body(fn)
    assert carriers, "the carrier is built in this body and nowhere else"
    assert all(node.lineno > consume.lineno for node in carriers), (
        "consume_release must be a statement above every carrier, so bytes cannot "
        "leave the device without the live Released having been spent first")
    # AND `issue` IS STILL THE MODULE'S ONE PUBLIC DOOR, which is P7's own guard
    # (`privacy.transport_guard.assert_single_egress`, run by tests/p7) and is what
    # keeps the carrier and its `perform` unreachable from outside this package.
    assert consume_release_in_own_body(function_def(transport, "issue")) is None
    imported = imports_of(transport)
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
        "DossierRequest",
        "Dossier",
        "P8Verdict",
        "Refusal",
        "CallFailed",
        "ValidationUnavailable",
        "NeedsConsent",
    ]
