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

Five rules, each one a way the door opens, each proven in both directions.

**A. Exactly one module declares the flag.** "Exactly one" was never asserted; the
flag scan asserts only that the real transport is AMONG the declarers. Two transports
both passing `assert_single_egress` individually is two doors, both locked, both
doors.

**B. `.invoke` is REACHED FOR only where the flag is declared.** The duck-typed
egress. No import to notice, no annotation to read, no flag to grep. Reaching is the
line, not calling: `send = client.invoke` on one line and `send(b)` on the next is
the same door, and a rule that read only the call site was reading the half the
calling module names for itself. `getattr(client, "invoke")` builds no attribute node
at all, so the bare string counts as reaching too. `ModelClient(invoke=f)` is still
clean -- a keyword argument is neither, and that distinction is the rule's whole
subject: constructing the capability is composition, spending it is egress.

**C. A network reaches `src/` only through a provider module**, and **a provider
module is imported only by a provider module or the composition root.** The second
half is the one with no exotic syntax in it: `readers/model_*.py` is exempt from the
first half because a socket may legitimately live there, and until 2026-09-02 nothing
asked who may import one. `from readers.model_deepseek import deepseek_invoke` in a
part declares no flag, reaches for no `.invoke` and names no network module -- it is
CR-02's shape (bytes on the wire the gate never released) written in four lines.
Rule C also covers the import the source does not spell: `NETWORK_MODULES` is
compared against names read out of import syntax, so `__import__("openai")` reaches
the same SDK unread, and so does anything inside `eval`.

**E. `SelfDescription` is constructed in one place.** The owner's narrow release
path of 2026-09-02. Its type seals which kind may be released and which row it may
address; nothing in Python seals who may construct one, so this does. It is a CHECK
and not a type, and it is here rather than in `privacy/` because that is what was
available -- said plainly at the type in `items.py` too, because a seal whose
weakness is undocumented is trusted past it.

  **What rule E seals is MAKING, and not naming.** Constructing one through any
  spelling -- a bare name, an attribute, a name bound from either, the type named as
  a string to `getattr` -- is a finding. An annotation, an `isinstance`, a tuple
  membership is not, and deliberately: the gate has to be able to say which kind it
  materialises and `resolve.py` has to be able to type the row it looks up. A rule
  that flagged every mention would forbid wiring the very door it keeps narrow.

**D. `src/questions/` does not even NAME a client.** Stricter than the rest of the
tree on purpose, because a self-description is a `user_edits` item under `80` §2 and
the amendment in §8.1 scopes its suspension to that one item: "this suspension
reaches nothing but the self-description". A package holding the one thing P7 may not
release should not hold the thing that would release it.

**AST and never text**, for the reason `transport_guard` gives for the same choice:
`proposal.py` says "invoke" and "llm_harness" in its own prose, `transport_guard.py`
says `IS_MODEL_TRANSPORT` in a comment and a docstring, and six modules say
"requests" and "sockets" in sentences about consent requests and symlinks. A
substring scan reports all of them and none of them is a finding. Where a rule below
does read a string, it reads an `ast.Constant` that IS the whole word -- a docstring
mentioning "invoke" is one long constant and is not equal to it.

---

**STATED LIMIT -- what this scan cannot see.** Read this before trusting the file,
because `88` §4 rests its safety argument on it and a seal whose weakness is
undocumented gets trusted past it. Every finding below was written against a way out
somebody named. **This is an allowlist of NAMED EXITS, not a proof about behaviour.**

It does not see, and cannot be made to see without becoming a different instrument:

- `os.system`, `os.popen`, `os.execve`, `os.posix_spawn`. `subprocess` is bannable
  because it has no innocent reading in a part package; `os` is imported by half the
  tree for `os.path`, so the exit through `os` stays open. Rule C's `subprocess`
  member closes the common spelling and not the family.
- `ctypes` reaching libc's `socket()`, `pty`, `asyncio.open_connection`. `asyncio`
  has innocent readings; the others are simply not on the list.
- A module name or a whole program assembled at runtime and handed to `eval`,
  `exec`, or a C extension. Rule C flags the *call*, which is why the call is worth
  flagging -- but a scan that reads syntax cannot read a string it never sees.
- **Anything outside `src/**.py`.** Not `tests/`, not a script at the repo root, not
  `sitecustomize`, not a `.pth` file, not a compiled extension. `_modules()` says so.
- Any exit shape nobody has named yet, which is the whole of the class the four
  bypasses of 2026-09-02 came out of.

Rule B is the backstop, and it is a narrow one: whatever the network is reached
through, the bytes still have to be handed to something -- but B knows exactly one
attribute name. **This file raises the cost of a second door. It does not make one
impossible, and no reading of `88` §4 should say that it does.**
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

#: What the three shipped providers actually import, plus the raw HTTP libraries a
#: fourth would most likely reach for, plus the ways out that are not SDKs at all.
#: Every member is a way out of the process; none of them has an innocent reading
#: inside a part package.
#:
#: `subprocess` was missing until 2026-09-02 because this list was written as "what a
#: provider imports" -- a list about SDKs. Handing the bytes to `curl` is not a
#: future-SDK gap; it is the oldest way out of a process there is. `os` is NOT here
#: and cannot be: half the tree imports it for `os.path`, so `os.system` stays
#: outside this scan's reach and the stated limit above says so.
NETWORK_MODULES: frozenset[str] = frozenset({
    "anthropic", "openai", "ollama", "urllib", "urllib.request", "http",
    "http.client", "httpx", "requests", "socket", "aiohttp",
    "subprocess", "ssl", "ftplib", "smtplib", "telnetlib", "pycurl", "websockets",
})

#: Rule C's second half. A provider module is where a socket may live; these are the
#: only modules that may reach for one. `cli.py` is `84` §1's sole composition root --
#: it picks the provider -- and `readers/model_routing.py` assembles `83`'s three
#: tiers, which is why the prefix rather than a file name.
PROVIDER_IMPORT_PREFIX: str = "readers.model_"
COMPOSITION_ROOT: str = "cli.py"

#: Rule C's third half: a name the source does not spell. `_imported` reads import
#: syntax, so a module reached through any of these is compared against nothing.
#: `compile` is deliberately absent -- `re.compile` is an ordinary line, and a rule
#: that cried wolf on it would be turned off.
UNREADABLE_REACH: frozenset[str] = frozenset({"__import__", "eval", "exec"})
UNREADABLE_REACH_ATTRS: frozenset[str] = frozenset({"import_module"})

#: Rule E's type, and where the one construction of it may live. The owner opened a
#: narrow P7 release path on 2026-09-02 and `privacy.items.SelfDescription` is the
#: door; its type seals WHICH KIND and WHICH ROW, and no type can seal WHO
#: CONSTRUCTS one. This does.
#:
#: `src/privacy/items.py` defines it, and the composition root is where the person's
#: own gesture is turned into a request -- so those two, and nothing else. A third
#: module constructing one would be a second place a self-description enters the
#: release path, which is the shape `80` §8.1 forbids: "this suspension reaches
#: nothing but the self-description", and a suspension with two doors is two
#: suspensions.
SELF_DESCRIPTION_TYPE: str = "SelfDescription"
SELF_DESCRIPTION_HOMES: frozenset[str] = frozenset({"privacy/items.py", "cli.py"})

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

    `from a.b import c` contributes BOTH `a.b` and `a.b.c`, because `c` may be a
    module: `from readers import model_deepseek` and `import readers.model_deepseek`
    are the same import written twice, and rule C's second half is about the module
    reached, not the statement used to reach it.
    """
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            names.add(node.module)
            names.update(f"{node.module}.{alias.name}" for alias in node.names)
    return frozenset(names)


def _is_word(node: ast.AST, word: str) -> bool:
    """An `ast.Constant` that IS this word, which a docstring mentioning it is not.

    The one place this file reads a string, and it reads it as a whole value rather
    than as text: `transport_guard.py` writes `"invoke"` inside a sentence about not
    doing that, and the sentence is one long constant that equals nothing.
    """
    return (isinstance(node, ast.Constant) and isinstance(node.value, str)
            and node.value == word)


def _reaches_invoke(tree: ast.Module) -> bool:
    """Reaching FOR `.invoke`, which `ModelClient(invoke=f)` is not.

    `readers/model_routing.py` builds a `ModelClient(invoke=deepseek_invoke(...))`.
    That is a keyword argument naming a callable, not a reach for one, and the
    difference is the whole distinction this rule draws: constructing the capability
    is composition, spending it is egress.

    REACHING and not calling. The call site is the half a module names for itself:
    `send = client.invoke` then `send(b)` was not a finding until 2026-09-02, and it
    is the same door with one more line in front of it. So an attribute access
    anywhere counts -- and so does the bare word, because `getattr(c, "invoke")` and
    `methodcaller("invoke")` build no attribute node at all.
    """
    return any((isinstance(node, ast.Attribute) and node.attr == EGRESS_CALL)
               or _is_word(node, EGRESS_CALL)
               for node in ast.walk(tree))


def _constructs_self_description(tree: ast.Module) -> bool:
    """Rule E: MAKING one, through any spelling. Naming one is not a finding.

    Three spellings, two of which passed until 2026-09-02:

    * a call through the name or through an attribute -- `SelfDescription(...)` and
      `items.SelfDescription(...)` are one construction and two import lines;
    * a binding of either -- `Describe = SelfDescription` puts a second name on the
      type, and after the binding this scan knows only the first;
    * the word as a string, for `getattr(items, "SelfDescription")`.

    An annotation, an `isinstance`, a tuple membership: NOT findings. The gate must
    be able to say which kind it materialises and `resolve.py` must be able to type
    the row it looks up, and rule E is about who may make one.
    """
    def names_it(node: ast.AST) -> bool:
        return ((isinstance(node, ast.Name) and node.id == SELF_DESCRIPTION_TYPE)
                or (isinstance(node, ast.Attribute)
                    and node.attr == SELF_DESCRIPTION_TYPE))

    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and names_it(node.func):
            return True
        if isinstance(node, ast.Assign) and names_it(node.value):
            return True
        if isinstance(node, ast.AnnAssign) and node.value is not None \
                and names_it(node.value):
            return True
        if _is_word(node, SELF_DESCRIPTION_TYPE):
            return True
    return False


def _reaches_unread(tree: ast.Module) -> bool:
    """A module reached by a name `_imported` never sees. Rule C's third half."""
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if isinstance(func, ast.Name) and func.id in UNREADABLE_REACH:
            return True
        if isinstance(func, ast.Attribute) and func.attr in UNREADABLE_REACH_ATTRS:
            return True
    return False


def findings(relative: str, source: str) -> tuple[str, ...]:
    """Every way this one module could put content on a wire. The whole instrument."""
    tree = ast.parse(source, filename=relative)
    declares = _declares_transport(tree)
    imported = _imported(tree)
    found: list[str] = []
    if declares and relative != THE_TRANSPORT:
        found.append(f"declares {TRANSPORT_FLAG}")
    if _reaches_invoke(tree) and not declares:
        found.append(f"reaches .{EGRESS_CALL} without declaring {TRANSPORT_FLAG}")
    if not relative.startswith(PROVIDER_PREFIX):
        for name in sorted(imported & NETWORK_MODULES):
            found.append(f"imports {name} outside a provider module")
        if relative != COMPOSITION_ROOT:
            # Named by the MODULE and not by what was taken out of it: `import
            # readers.model_deepseek` and `from readers.model_deepseek import
            # deepseek_invoke` are one import, and `_imported` deliberately reports
            # the second as two names so either statement is seen.
            for name in sorted({".".join(n.split(".")[:2]) for n in imported
                                if n.startswith(PROVIDER_IMPORT_PREFIX)}):
                found.append(f"imports the provider module {name} outside a "
                             f"provider module or the composition root")
        if _reaches_unread(tree):
            found.append("reaches a module by a name the scan cannot read")
    if (_constructs_self_description(tree)
            and relative not in SELF_DESCRIPTION_HOMES):
        found.append(f"constructs {SELF_DESCRIPTION_TYPE} outside "
                     f"{sorted(SELF_DESCRIPTION_HOMES)}")
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
    assert _reaches_invoke(ast.parse(source)), (
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
        f"reaches .{EGRESS_CALL} without declaring {TRANSPORT_FLAG}",)


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


# --- and the six ways it could NOT fail until 2026-09-02 ------------------------------
#
# A security review ran `findings()` itself over synthetic modules and returned `()`
# for four of these. They are here as fixtures rather than as a note because the
# standard this file set for itself is that every rule is proven in both directions,
# and a rule proven only against the spelling its author happened to write is a rule
# that measures spellings.


def test_an_attribute_qualified_construction_is_a_rule_e_finding():
    """Rule E read the call target as an `ast.Name`, so `items.SelfDescription(...)`
    passed. The construction is the same one; only the import line differs, and the
    import line is the half the calling module chooses."""
    assert _fixture("egress_by_qualified_construction.py") == (
        f"constructs {SELF_DESCRIPTION_TYPE} outside "
        f"{sorted(SELF_DESCRIPTION_HOMES)}",)


def test_binding_the_type_to_another_name_is_a_rule_e_finding():
    """`Describe = SelfDescription` then `Describe(...)`: no call through the sealed
    name anywhere in the file. Binding it is what this catches, because after the
    binding the type has a second name and the scan knows only the first."""
    assert findings("grouping/somewhere.py",
                    "from privacy.items import SelfDescription\n"
                    "Describe = SelfDescription\n"
                    "x = Describe('role:me')\n") == (
        f"constructs {SELF_DESCRIPTION_TYPE} outside "
        f"{sorted(SELF_DESCRIPTION_HOMES)}",)


def test_the_type_named_as_a_string_is_a_rule_e_finding():
    """`getattr(items, "SelfDescription")` spells the sealed name as data. There is
    no `ast.Name` and no `ast.Attribute` to find; the word is still in the file."""
    assert findings("grouping/somewhere.py",
                    "from privacy import items\n"
                    "x = getattr(items, 'SelfDescription')('role:me')\n") == (
        f"constructs {SELF_DESCRIPTION_TYPE} outside "
        f"{sorted(SELF_DESCRIPTION_HOMES)}",)


def test_naming_the_type_in_an_annotation_is_not_a_rule_e_finding():
    """The other direction, and the reason rule E is about MAKING and not naming.

    The gate has to be able to say which kind it materialises, and `resolve.py` has
    to be able to type the row it looks up. A rule that flagged every mention would
    forbid wiring the door the rule exists to keep narrow -- so an annotation, an
    `isinstance`, and a tuple membership all stay legal, and the docstring says so.
    """
    assert findings("privacy/gate.py",
                    "from privacy.items import SelfDescription\n"
                    "TEXT_BEARING = (SelfDescription,)\n"
                    "def f(x: SelfDescription) -> bool:\n"
                    "    return isinstance(x, SelfDescription)\n") == ()


def test_an_aliased_invoke_is_a_rule_b_finding():
    """Rule B matched a call whose func was an `ast.Attribute`. One extra line moves
    the attribute off the call site, and the call becomes an ordinary name."""
    assert _fixture("egress_by_alias.py") == (
        f"reaches .{EGRESS_CALL} without declaring {TRANSPORT_FLAG}",)


def test_invoke_named_as_a_string_is_a_rule_b_finding():
    """`getattr(c, "invoke")(b)` and `methodcaller("invoke")` build no attribute node
    at all. Same door, same word, moved from syntax into data."""
    assert _fixture("egress_by_getattr.py") == (
        f"reaches .{EGRESS_CALL} without declaring {TRANSPORT_FLAG}",)


def test_a_module_that_shells_out_is_a_rule_c_finding():
    """`subprocess` was not on `NETWORK_MODULES` because the list was written as the
    SDKs a provider imports. Handing the bytes to `curl` is not a future-SDK gap."""
    assert _fixture("egress_by_subprocess.py") == (
        "imports subprocess outside a provider module",)


def test_importing_a_provider_from_a_part_is_a_finding():
    """The fifth, found after the reviewer's four, and the one with no exotic syntax.

    Rule C exempts `readers/model_*` because that is where a socket may live.
    Nothing asked who may IMPORT one, so a part calling `deepseek_invoke` directly
    matched no rule at all: no flag, no `.invoke`, no network module name.
    """
    assert _fixture("egress_by_provider_import.py", at="grouping/somewhere.py") == (
        "imports the provider module readers.model_deepseek outside a provider "
        "module or the composition root",)


def test_the_provider_named_as_a_member_is_the_same_import():
    """`from readers import model_deepseek` reaches exactly the module
    `import readers.model_deepseek` reaches, and `ast.ImportFrom.module` is
    `readers` for one of them. Both spellings, or the rule reads statements."""
    assert findings("grouping/somewhere.py",
                    "from readers import model_deepseek\n"
                    "x = model_deepseek.deepseek_invoke\n") == (
        "imports the provider module readers.model_deepseek outside a provider "
        "module or the composition root",)


def test_the_composition_root_may_import_a_provider():
    """The other direction, and the whole point of a composition root: `cli.py` picks
    the provider, and `readers/model_routing.py` assembles the three tiers. A rule
    that could not tell those from a part reaching past the gate would forbid
    wiring the product to a model at all."""
    assert _fixture("egress_by_provider_import.py", at="cli.py") == ()
    assert _fixture("egress_by_provider_import.py",
                    at="readers/model_routing.py") == ()


def test_an_import_the_source_does_not_spell_is_a_finding():
    """Rule C compares `NETWORK_MODULES` against names read out of import syntax, so
    a module name that arrives as a string reaches the same SDK unread."""
    assert _fixture("egress_by_dynamic_import.py") == (
        "reaches a module by a name the scan cannot read",)
