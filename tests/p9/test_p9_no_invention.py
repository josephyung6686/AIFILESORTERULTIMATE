# tests/p9/test_p9_no_invention.py
"""P9 authors no knowledge. This file is the check that says so, mechanically.

Every rule below has the same shape: a value P9 could plausibly hard-code, and a
statement of who actually owns it. A domain name, a document-compatibility table,
a gazetteer entry, an identifier-detection rule, a numeric threshold — each of
them is a policy tuned on somebody else's corpus, and a copy inside P9 is a policy
this user never chose with nothing to say so.

The other half is architectural: P9 must not grow a second validator, a second
model route, or a destination concept. `llm_harness.run_call` is the only
evaluation seam, `grouping/p8_seam.py` is the only module that may name P8's
request type, and no module may name a node, a path or a tree.
"""
from __future__ import annotations

import ast
import pathlib

import pytest

import grouping

ROOT = pathlib.Path(grouping.__file__).resolve().parent
MODULES = sorted(ROOT.glob("*.py"))


def _tree(path: pathlib.Path) -> ast.Module:
    return ast.parse(path.read_text())


def _docstring_ids(tree: ast.Module) -> set[int]:
    found: set[int] = set()
    for node in ast.walk(tree):
        body = getattr(node, "body", None)
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef,
                             ast.AsyncFunctionDef)) and body:
            first = body[0]
            if (isinstance(first, ast.Expr) and isinstance(first.value, ast.Constant)
                    and isinstance(first.value.value, str)):
                found.add(id(first.value))
    return found


def _code_strings(path: pathlib.Path):
    """Every string literal that is not a docstring, with its line."""
    tree = _tree(path)
    docstrings = _docstring_ids(tree)
    for node in ast.walk(tree):
        if (isinstance(node, ast.Constant) and isinstance(node.value, str)
                and id(node) not in docstrings):
            yield node.lineno, node.value


def _imports(path: pathlib.Path):
    for node in ast.walk(_tree(path)):
        if isinstance(node, ast.Import):
            for alias in node.names:
                yield node.lineno, alias.name, alias.asname
        elif isinstance(node, ast.ImportFrom) and node.module:
            for alias in node.names:
                yield node.lineno, node.module, alias.name


# --- no domain knowledge ---------------------------------------------------------


def test_no_module_names_a_domain(  ):
    """A domain is a user's, not a product's. §3.11's active schema arrives
    injected, and a domain name here would be P9 asserting one exists."""
    domains = {
        "academic", "legal", "medical", "financial", "insurance", "tax",
        "employment", "immigration", "real estate", "photography",
    }
    offenders = [
        f"{path.name}:{line}:{value!r}"
        for path in MODULES for line, value in _code_strings(path)
        if value.lower() in domains
    ]
    assert offenders == [], offenders


def test_no_module_carries_a_document_compatibility_table():
    """`document_compatible` is an injected predicate. A table here would decide
    that a screenshot goes with a receipt for every user who ever runs this."""
    offenders = []
    for path in MODULES:
        for node in ast.walk(_tree(path)):
            if not isinstance(node, ast.Dict):
                continue
            keys = [
                item.value for item in node.keys
                if isinstance(item, ast.Constant) and isinstance(item.value, str)
            ]
            if len(keys) >= 2 and any(
                    key in {"pdf", "png", "jpg", "docx", "csv", "eml"}
                    for key in keys):
                offenders.append(f"{path.name}:{node.lineno}")
    assert offenders == [], offenders


def test_no_module_carries_a_gazetteer_or_an_identifier_rule():
    """Which strings are institutions, and which look like credentials, is P7's
    and the user's. A list here is a list tuned on a corpus that is not theirs."""
    offenders = []
    for path in MODULES:
        if path.name == "fixtures.py":
            # The published examples name a course and a school on purpose; they
            # are the design's own worked cases, not a lookup table.
            continue
        for line, value in _code_strings(path):
            lowered = value.lower()
            if "@" in value:
                offenders.append(f"{path.name}:{line}:{value!r}")
            if any(word in lowered for word in
                   ("university", "college", "columbia", "harvard", "ssn",
                    "passport", "iban")):
                offenders.append(f"{path.name}:{line}:{value!r}")
    assert offenders == [], offenders


def test_no_module_carries_a_prompt():
    """P8 owns the prompt. A template string here would be a second one, and the
    fingerprint P8 binds its call to would not describe it.

    Length is not the test: a SQL INSERT and a refusal message are both long and
    both legitimate. What a prompt has is an addressee.
    """
    markers = (
        "you are", "your task", "respond with", "return json", "step by step",
        "do not include", "the following", "assistant",
    )
    offenders = [
        f"{path.name}:{line}:{marker}"
        for path in MODULES for line, value in _code_strings(path)
        for marker in markers if marker in value.lower()
    ]
    assert offenders == [], offenders


# --- no numeric policy -----------------------------------------------------------


def test_no_module_writes_a_threshold_or_a_ceiling():
    """Every structural limit is one of P1's ceilings or an injected argument.
    0 and 1 are the two numbers that are not policy: an empty count, and one of
    something. Anything else is a bound nobody chose, with nothing to say so."""
    offenders = []
    for path in MODULES:
        if path.name in {"fixtures.py", "records.py"}:
            # Fixtures are the published examples; their numbers ARE the example.
            # `records.py` numbers are ARITY -- "fewer than two competing values
            # is not a conflict" is what the word means, not a tunable bar.
            continue
        for node in ast.walk(_tree(path)):
            if (isinstance(node, ast.Constant)
                    and isinstance(node.value, (int, float))
                    and not isinstance(node.value, bool)
                    and node.value not in (0, 1)):
                offenders.append(f"{path.name}:{node.lineno}:{node.value}")
    assert offenders == [], offenders


# --- no second validator, no second model route ----------------------------------


def test_run_call_is_the_only_evaluation_seam():
    banned = {
        "llm_harness.transport", "llm_harness.harness", "llm_harness.sites",
        "llm_harness.validation", "llm_harness.group_validation",
        "llm_harness.dossier", "llm_harness.fact_validation",
        "llm_harness.placement_validation", "llm_harness.template_validation",
        "privacy.gate", "privacy.binding", "privacy.resolve",
    }
    offenders = [
        f"{path.name}:{line}:{module}"
        for path in MODULES for line, module, _name in _imports(path)
        if module in banned
    ]
    assert offenders == [], offenders


def test_only_the_p8_seam_names_p8s_request_type():
    """The conversion from P9's dossier to P8's reference-only request happens in
    one module. A second one would be a second answer to what P8 is owed."""
    offenders = [
        f"{path.name}:{line}"
        for path in MODULES for line, module, name in _imports(path)
        if name in {"DossierRequest", "EvidenceItem"} and path.name != "p8_seam.py"
    ]
    assert offenders == [], offenders


def test_no_module_imports_p8s_materialised_dossier():
    """P8 materialises released evidence and constructs `Dossier`. A P9 import of
    it is P9 holding released content."""
    offenders = [
        f"{path.name}:{line}"
        for path in MODULES for line, _module, name in _imports(path)
        if name == "Dossier"
    ]
    assert offenders == [], offenders


def test_p9_defines_none_of_the_names_the_repair_plan_forbids():
    """`P8GroupResult`, `BuildModelCallRequest` and `EvaluateGroup` are the three
    shapes a second validator arrives wearing."""
    banned = {"P8GroupResult", "BuildModelCallRequest", "EvaluateGroup"}
    offenders = []
    for path in MODULES:
        for node in ast.walk(_tree(path)):
            name = getattr(node, "name", None)
            if name in banned:
                offenders.append(f"{path.name}:{node.lineno}:{name}")
    assert offenders == [], offenders


def test_no_module_imports_a_test_fixture():
    """P13 is specification only, and P10/P11 consume P9's fixtures rather than
    the reverse. A `tests.` import in `src/` inverts every one of those."""
    offenders = [
        f"{path.name}:{line}:{module}"
        for path in MODULES for line, module, _name in _imports(path)
        if module.startswith("tests") or "p13" in module.lower()
    ]
    assert offenders == [], offenders


def test_no_module_uses_the_legacy_overwrite_vector_store():
    """P1's versioned store keeps a vector per file VERSION. `put_embedding`
    overwrites, and a similarity against overwritten text is a similarity to a
    document that no longer exists."""
    offenders = []
    for path in MODULES:
        for node in ast.walk(_tree(path)):
            if isinstance(node, ast.Name) and node.id in {
                    "put_embedding", "get_embedding"}:
                offenders.append(f"{path.name}:{node.lineno}:{node.id}")
    assert offenders == [], offenders


# --- no destination concept ------------------------------------------------------


def test_no_module_names_a_destination_node_path_or_tree():
    """P9 says which files belong together. Where they go is P10's and P11's, and
    the graph calls its own vertices `file_ids` for exactly this reason."""
    # `prompt_template_id` is P8's prompt identity and is not a P10 template, so
    # the banned word is the P10 concept rather than the substring.
    banned = ("destination", "folder_path", "node_id", "parent_node",
              "tree_", "_tree", "placement", "branch_template", "node_type")
    offenders = []
    for path in MODULES:
        tree = _tree(path)
        docstrings = _docstring_ids(tree)
        for node in ast.walk(tree):
            if isinstance(node, ast.Name):
                for word in banned:
                    if word in node.id.lower():
                        offenders.append(f"{path.name}:{node.lineno}:{node.id}")
            if (isinstance(node, ast.Constant) and isinstance(node.value, str)
                    and id(node) not in docstrings):
                for word in banned:
                    if word in node.value.lower():
                        offenders.append(f"{path.name}:{node.lineno}:{word}")
    assert offenders == [], offenders


def test_no_p9_table_has_a_destination_column():
    from grouping.schema import GROUPING_DDL

    for word in ("destination", "node_id", "folder", "path", "tree"):
        assert word not in GROUPING_DDL.lower(), word


# --- the vocabulary lives in one place -------------------------------------------


def test_only_the_vocabulary_module_spells_a_closed_p9_value():
    """Already enforced by `test_p9_vocabulary.py`; asserted here too because the
    two guards fail for different reasons and a reader of either should see it."""
    from grouping import vocabulary

    closed = {
        value for name, value in vars(vocabulary).items()
        if name.isupper() and isinstance(value, str)
    }
    offenders = []
    for path in MODULES:
        if path.name in {"vocabulary.py", "fixtures.py"}:
            continue
        for line, value in _code_strings(path):
            if value in closed:
                offenders.append(f"{path.name}:{line}:{value!r}")
    assert offenders == [], offenders
