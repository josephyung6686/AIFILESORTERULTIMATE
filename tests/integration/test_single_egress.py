# tests/integration/test_single_egress.py
"""P8's Done-means 1, asked of the WHOLE tree instead of one module that volunteered.

> Exactly one function in the codebase constructs a model request, and its only
> parameter type is P7's `Released`. A call without a release is not constructible.
> Verified by inspection plus a test that the un-released path does not type-check /
> does not exist.  (quoted at `src/privacy/transport_guard.py`)

Two instruments already exist for that sentence and NEITHER of them is about the
codebase. `privacy.transport_guard.assert_single_egress` is an existence proof over
ONE module namespace, and it says so. `tests/p7/test_p7_skeleton_step.py` finds the
modules it should be pointed at by scanning `src/` for `IS_MODEL_TRANSPORT = True` --
which finds the modules that DECLARE THEMSELVES. Put together they prove that the
module which admits to being a transport is a good one.

**A guard that only catches the honest is not a guard.** Nothing here scanned for the
other shape: a module that imports no transport, annotates no `ModelClient`, declares
no flag, and calls `client.invoke(...)` on something it was handed. That is not a
hypothetical -- it is the shape the role matcher's missing narrowing step would have
had (`80` §6 leaves "which local model, and how it is obtained" open, and the obvious
answer is a helper in `src/questions/` that turns an injected client into a
`Proposer`). It was declined on the reasoning below, and this file is what makes the
next author's version of that decision unnecessary.

Four rules, each one a way the door opens, each proven in both directions.

**A. Exactly one module declares the flag.** "Exactly one" was never asserted; the
flag scan asserts only that the real transport is AMONG the declarers. Two transports
both passing `assert_single_egress` individually is two doors, both locked, both
doors.

**B. `.invoke(...)` is called only where the flag is declared.** The duck-typed
egress. No import to notice, no annotation to read, no flag to grep.

**C. A network reaches `src/` only through a provider module.** `readers/model_*.py`
is where a socket legitimately lives, and each of those modules keeps its network to
one function so a test can replace it. Everywhere else in `src/`, a network import is
a part that has grown its own way out.

**D. `src/questions/` does not even NAME a client.** Stricter than the rest of the
tree on purpose, because a self-description is a `user_edits` item under `80` §2 and
the amendment in §8.1 scopes its suspension to that one item: "this suspension
reaches nothing but the self-description". A package holding the one thing P7 may not
release should not hold the thing that would release it.

**AST and never text**, for the reason `transport_guard` gives for the same choice:
`proposal.py` says "invoke" and "llm_harness" in its own prose, `transport_guard.py`
says `IS_MODEL_TRANSPORT` in a comment and a docstring, and six modules say
"requests" and "sockets" in sentences about consent requests and symlinks. A
substring scan reports all of them and none of them is a finding.

**Stated limit**, because a guard whose reach is unstated will be trusted past it.
Rule C is a named list. An SDK nobody has used yet reaches the network and is not on
it, and adding a provider means adding its module to `NETWORK_MODULES` -- which is
the same shape of obligation `LOCALITIES` and `ALWAYS_LOCAL` already carry. Rule B is
what covers the gap in the meantime: whatever the network is reached through, the
bytes still have to be handed to something, and B is about the handing.
"""
from __future__ import annotations

import ast
import pathlib

import pytest

SRC = pathlib.Path(__file__).resolve().parents[2] / "src"
FIXTURES = pathlib.Path(__file__).resolve().parent / "egress_fixtures"

#: The one module P8's Done-means 1 is about, by path relative to `src/`.
THE_TRANSPORT: str = "llm_harness/transport.py"

#: Where a socket may live. `83` puts the provider clients in `src/readers/`, and
#: each one keeps its network to a single function "so a test can replace it"
#: (`model_deepseek._send`). A prefix rather than a list of file names, so a
#: provider added tomorrow is covered without this constant being edited.
PROVIDER_PREFIX: str = "readers/model_"

#: The flag `tests/p7/test_p7_skeleton_step.py` scans for, spelled once.
TRANSPORT_FLAG: str = "IS_MODEL_TRANSPORT"

#: The attribute a `ModelClient` is called through. `llm_harness.transport.ModelClient`
#: is `(model_target, invoke)`, and `invoke` is the half that moves bytes.
EGRESS_CALL: str = "invoke"

#: What the three shipped providers actually import, plus the two raw HTTP libraries
#: a fourth would most likely reach for. Every member is a way out of the process;
#: none of them has an innocent reading inside a part package.
NETWORK_MODULES: frozenset[str] = frozenset({
    "anthropic", "openai", "ollama", "urllib", "urllib.request", "http",
    "http.client", "httpx", "requests", "socket", "aiohttp",
})

#: Rule D's package, and what it may not say. `ModelClient` by name, because an
#: annotation is how the helper `80` §6 leaves open would most naturally be written.
QUESTIONS_PACKAGE: str = "questions/"
CLIENT_TYPE: str = "ModelClient"


def _modules() -> tuple[tuple[str, pathlib.Path], ...]:
    """Every module in `src/`, as (path relative to src, path), sorted."""
    return tuple(sorted(
        (str(path.relative_to(SRC)), path)
        for path in SRC.rglob("*.py")
        if "__pycache__" not in path.parts and ".egg-info" not in str(path)))


def _declares_transport(tree: ast.Module) -> bool:
    """`IS_MODEL_TRANSPORT = True` at module level, read as syntax and not as text.

    The same reading `tests/p7/test_p7_skeleton_step.py` does, and for the reason it
    gives: the flag appears in a comment and in a docstring in
    `privacy/transport_guard.py`, and a text search finds both.
    """
    for node in tree.body:
        targets = (node.targets if isinstance(node, ast.Assign)
                   else [node.target] if isinstance(node, ast.AnnAssign) else [])
        for target in targets:
            if isinstance(target, ast.Name) and target.id == TRANSPORT_FLAG:
                value = node.value
                if isinstance(value, ast.Constant) and value.value is True:
                    return True
    return False


def _imported(tree: ast.Module) -> frozenset[str]:
    """Every module name this one imports, at any depth including inside a function.

    Inside a function too, deliberately: `model_deepseek._send` does `import openai`
    in its body, which is where a part hiding an egress would put it as well.
    """
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            names.add(node.module)
    return frozenset(names)


def _calls_invoke(tree: ast.Module) -> bool:
    """A CALL through an `.invoke` attribute, which `invoke=f(...)` is not.

    `readers/model_routing.py` builds a `ModelClient(invoke=deepseek_invoke(...))`.
    That is a keyword argument naming a callable, not a call through one, and the
    difference is the whole distinction this rule draws: constructing the capability
    is composition, spending it is egress.
    """
    return any(isinstance(node, ast.Call)
               and isinstance(node.func, ast.Attribute)
               and node.func.attr == EGRESS_CALL
               for node in ast.walk(tree))


def findings(relative: str, source: str) -> tuple[str, ...]:
    """Every way this one module could put content on a wire. The whole instrument."""
    tree = ast.parse(source, filename=relative)
    declares = _declares_transport(tree)
    imported = _imported(tree)
    found: list[str] = []
    if declares and relative != THE_TRANSPORT:
        found.append(f"declares {TRANSPORT_FLAG}")
    if _calls_invoke(tree) and not declares:
        found.append(f"calls .{EGRESS_CALL}() without declaring {TRANSPORT_FLAG}")
    if not relative.startswith(PROVIDER_PREFIX):
        for name in sorted(imported & NETWORK_MODULES):
            found.append(f"imports {name} outside a provider module")
    if relative.startswith(QUESTIONS_PACKAGE):
        if any(isinstance(node, ast.Name) and node.id == CLIENT_TYPE
               for node in ast.walk(tree)):
            found.append(f"names {CLIENT_TYPE} inside {QUESTIONS_PACKAGE}")
        if any(name.startswith("llm_harness.transport")
               or name.startswith("readers.model_") for name in imported):
            found.append(f"imports a transport inside {QUESTIONS_PACKAGE}")
    return tuple(found)


def _fixture(name: str, *, at: str | None = None) -> tuple[str, ...]:
    """One fixture, read as though it sat at `at` inside `src/`.

    Rules C and D are about WHERE a module is, so a fixture has to be presented
    somewhere: `egress_by_network.py` is only a finding outside a provider module,
    and rule D only reaches `src/questions/`.
    """
    path = FIXTURES / name
    return findings(at or path.name, path.read_text())


# --- the property, over the real tree ------------------------------------------------


def test_the_scan_has_a_tree_to_walk():
    """`84` §5.3: a guard that has never failed is not a guard, and a guard over an
    empty list has never had the chance. The residual library shipped empty for
    exactly this reason, and four tests here had quietly stopped being able to fail
    on the day this instrument was written."""
    modules = _modules()
    assert len(modules) > 100
    assert any(relative == THE_TRANSPORT for relative, _ in modules)


@pytest.mark.parametrize("relative,path", _modules(),
                         ids=[relative for relative, _ in _modules()])
def test_no_module_in_the_source_opens_a_second_door_to_a_model(relative, path):
    """Rules A-D, module by module, so a failure names the file that broke it."""
    assert findings(relative, path.read_text()) == ()


def test_the_one_transport_is_still_the_one_that_declares_itself():
    """The positive half of rule A. Without it, deleting the flag from
    `transport.py` would satisfy every assertion above -- and silently empty the
    P7 scan that finds the module `assert_single_egress` is pointed at."""
    source = (SRC / THE_TRANSPORT).read_text()
    assert _declares_transport(ast.parse(source))
    assert _calls_invoke(ast.parse(source)), (
        "the transport no longer calls its client, so rule B is exempting a module "
        "that does nothing and every real caller is somewhere else")


# --- and the four ways it must be able to fail ---------------------------------------


def test_a_second_module_declaring_itself_a_transport_is_found():
    """Rule A. Two doors, both locked, both doors: each would pass
    `assert_single_egress` on its own, which is what makes counting them a separate
    question from checking them."""
    assert _fixture("second_transport.py") == (
        f"declares {TRANSPORT_FLAG}",)


def test_a_module_that_only_calls_invoke_is_found():
    """Rule B, and the one no other instrument in this repo catches: no import, no
    annotation, no flag, one duck-typed call."""
    assert _fixture("egress_by_invoke.py") == (
        f"calls .{EGRESS_CALL}() without declaring {TRANSPORT_FLAG}",)


def test_a_part_that_grew_its_own_way_out_is_found():
    """Rule C. The failure that skips the `ModelClient` contract entirely, so rules
    A and B never see it."""
    assert _fixture("egress_by_network.py") == (
        "imports openai outside a provider module",)


def test_a_questions_module_that_names_a_client_is_found():
    """Rule D, which is about `src/questions/` and not about the tree."""
    assert _fixture("egress_by_import.py",
                    at=f"{QUESTIONS_PACKAGE}matching.py") == (
        f"names {CLIENT_TYPE} inside {QUESTIONS_PACKAGE}",
        f"imports a transport inside {QUESTIONS_PACKAGE}")


def test_the_same_module_anywhere_else_in_the_tree_is_not_a_rule_d_finding():
    """Rule D is a fence around one package, not a fourth repo-wide rule. `cli.py`
    imports the transport legitimately and must go on being able to."""
    assert _fixture("egress_by_import.py", at="llm_harness/somewhere.py") == ()


def test_prose_about_a_transport_is_not_a_transport():
    """The other direction, without which this is a blanket ban rather than a rule.

    Six modules in `src/` say "requests" or "sockets" in sentences about consent
    requests and symlinks; `transport_guard.py` says `IS_MODEL_TRANSPORT` in a
    comment and a docstring; `proposal.py` says "invoke" and "llm_harness" in the
    docstring of the one module whose subject is that it holds neither."""
    assert _fixture("clean.py") == ()


def test_building_a_client_is_not_spending_one():
    """`readers/model_routing.py` in miniature, and the distinction rule B draws.

    A composition root that assembles `ModelClient(invoke=...)` is doing its job;
    P7's own guard already ruled on this direction -- "a callable sink is not a
    content parameter", because the caller hands over no bytes at all."""
    assert _fixture("builds_a_client.py") == ()


def test_the_proposal_step_still_takes_its_narrowing_injected():
    """What is here INSTEAD, so this file records a design and not just an absence.

    `80` §1's Option 2 is a model proposing and a person confirming. The proposing
    arrives as a callable the composition root supplies; `None` is Option 1, the
    fallback the ruling names for when no local model is present, and it is why the
    product works end to end with no model at all. Rules B and D above are what stop
    that callable being built inside the package that consumes it.
    """
    import inspect

    from questions.proposal import propose_roles

    parameters = inspect.signature(propose_roles).parameters
    assert parameters["propose"].default is inspect.Parameter.empty
    assert "client" not in parameters and "conn" not in parameters
