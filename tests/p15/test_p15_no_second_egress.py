# tests/p15/test_p15_no_second_egress.py
"""`src/questions/` holds no model egress, and this is the instrument that says so.

`80` §1 rules that a model proposes the shortlist, and building that raised a
question the ruling leaves open by name -- `80` §6: *"Which local model, and how it
is obtained. Not addressed by the ruling."* The obvious answer, a helper in
`src/questions/` that turns an injected `ModelClient` into `proposal.Proposer`, is
one this project already forbids elsewhere:

> Exactly one function in the codebase constructs a model request, and its only
> parameter type is P7's `Released`. A call without a release is not constructible.
> (P8 Done-means 1, quoted at `src/privacy/transport_guard.py`)

`tests/p7/test_p7_real_transport_egress.py` asserts that function is
`llm_harness.transport.issue` and that it takes a `Released`. A self-description is
a `user_edits` item (`80` §2, recorded at `privacy.vocabulary.ALWAYS_LOCAL`), so no
`Released` can name one, and `80` §8.1 scopes the development suspension to that one
item -- loosening P7 to release it would reach the other eight always-local kinds,
which §8.1 forbids by name. So the narrowing step stays injected, and until the
owner rules on how a model is obtained, `propose=None` is `80` §1's Option 1: the
whole closed list, unnarrowed, which is a fallback rather than a failure.

**The gap this file closes.** P7's flag scan
(`tests/p7/test_p7_skeleton_step.py::_declares_transport`) finds modules that set
`IS_MODEL_TRANSPORT = True` -- modules that declare themselves. A module that calls
a client's `invoke` and declares nothing is found by no instrument in this repo.
That is the exact shape the missing piece would have had, so this asserts the
package has none: not by inspection at one moment, but by a scan that runs every
time and that is proven able to fail against three fixtures beside it.

**AST and never text**, for the reason `transport_guard` gives for the same choice:
`proposal.py` says "invoke" and "llm_harness" in its own prose, and a substring scan
flags the one module in the package whose entire point is that it holds no
transport.
"""
from __future__ import annotations

import ast
import pathlib

import pytest

QUESTIONS = pathlib.Path(__file__).resolve().parents[2] / "src" / "questions"
FIXTURES = pathlib.Path(__file__).resolve().parent / "egress_fixtures"

#: The one egress this product has, by module path. A `questions` module importing
#: from here would be reaching for the transport rather than being handed a
#: narrowing step, which is the distinction `proposal.Proposer` exists to keep.
TRANSPORT_MODULE: str = "llm_harness.transport"

#: The provider clients, which are the `invoke` half of a `ModelClient`. `83` puts
#: them in `src/readers/`; naming the prefix rather than the modules means a
#: provider added tomorrow is covered without this list being updated, which is the
#: failure mode a list of module names has.
PROVIDER_PREFIX: str = "readers.model_"

#: What a client is called, and what is done to one. Both are checked because either
#: alone is half a guard: an annotation without the call is a module that holds a
#: client it never uses, and a call without the annotation is the duck-typed shape
#: that arrives when nobody decided to add an egress at all.
CLIENT_TYPE: str = "ModelClient"
EGRESS_CALL: str = "invoke"


def _findings(path: pathlib.Path) -> tuple[str, ...]:
    """Every way this one module could put content on a wire, as syntax."""
    found: list[str] = []
    tree = ast.parse(path.read_text(), filename=str(path))
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            if (node.module == TRANSPORT_MODULE
                    or node.module.startswith(PROVIDER_PREFIX)):
                found.append(f"imports {node.module}")
        if isinstance(node, ast.Import):
            for alias in node.names:
                if (alias.name == TRANSPORT_MODULE
                        or alias.name.startswith(PROVIDER_PREFIX)):
                    found.append(f"imports {alias.name}")
        if isinstance(node, ast.Name) and node.id == CLIENT_TYPE:
            found.append(f"names {CLIENT_TYPE}")
        if isinstance(node, ast.Attribute) and node.attr == EGRESS_CALL:
            found.append(f"reaches .{EGRESS_CALL}")
    return tuple(found)


def _package_modules() -> tuple[pathlib.Path, ...]:
    return tuple(sorted(p for p in QUESTIONS.glob("*.py")))


def test_the_package_has_modules_to_scan():
    """`84` §5.3: a guard that has never failed is not a guard, and a guard over an
    empty list has never had the chance. The residual library shipped empty for
    exactly this reason."""
    assert len(_package_modules()) > 1


@pytest.mark.parametrize("path", _package_modules(), ids=lambda p: p.name)
def test_no_questions_module_can_put_a_sentence_on_a_wire(path):
    """The property, module by module, so a failure names the file that broke it."""
    assert _findings(path) == ()


def test_a_module_that_imports_the_transport_is_found():
    assert "imports llm_harness.transport" in _findings(
        FIXTURES / "egress_by_import.py")


def test_a_module_that_only_calls_invoke_is_found():
    """The likelier shape, and the one no other instrument in this repo catches:
    no import, no annotation, one duck-typed call."""
    assert _findings(FIXTURES / "egress_by_invoke.py") == ("reaches .invoke",)


def test_prose_about_a_transport_is_not_a_transport():
    """The other direction, so this is a distinction rather than a blanket ban.

    Without it the guard flags `proposal.py`, which says "invoke" and "llm_harness"
    in its own docstring and whose whole subject is that it holds neither."""
    assert _findings(FIXTURES / "clean.py") == ()


def test_the_proposal_step_still_takes_its_narrowing_injected():
    """What is here INSTEAD, so this file records a design and not just an absence.

    `80` §1's Option 2 is a model proposing and a person confirming. The proposing
    arrives as a callable the composition root supplies; `None` is Option 1, the
    fallback the ruling names for when no local model is present, and it is why the
    product works end to end with no model at all."""
    import inspect

    from questions.proposal import propose_roles

    parameters = inspect.signature(propose_roles).parameters
    assert parameters["propose"].default is inspect.Parameter.empty
    assert "client" not in parameters and "conn" not in parameters
