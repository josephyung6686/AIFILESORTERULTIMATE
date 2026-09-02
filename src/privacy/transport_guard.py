"""Done-means 3's instrument: does a string-prompt entry point exist in this module?

§8.4 opens with a sequencing requirement -- "Privacy policy must be enforced before
content reaches any model or external connector" -- which is a PROPERTY of a transport
P7 does not own. P8's Done-means 1 states the method for checking it: "Exactly one
function in the codebase constructs a model request, and its only parameter type is
P7's `Released`. A call without a release is not constructible. Verified by inspection
plus a test that the un-released path does not type-check / does not exist."

This module is that inspection, mechanised. It is an EXISTENCE PROOF over a module
namespace, not a runtime check on a call: nothing here executes a transport, and a
transport that passes has been shown to have no place to put a string, not to have
declined to use one.

Three rules, each of which separates a guard from a decoration:

1. **Resolved annotations, never source text.** `inspect.signature(fn, eval_str=True)`.
   A text scan sees `Released` in a docstring and passes a transport that takes a
   string; `tests/p7/transport_fixtures.py` contains exactly that module.
2. **Containers and unions are walked.** `list[str]`, `Sequence[str]` and
   `Path | None` are how a transport that "takes no string" takes one.
3. **The content check follows the EGRESS SURFACE; only public functions are counted.**
   The surface is what a caller can hand content to on the way to a model: the entry
   point's parameters, the constructor of the class the entry point is a method of,
   and the constructors of any classes DEFINED HERE that appear in those parameters,
   transitively. Classes are walked because a client wrapper
   `Client.send(self, prompt: str)` is the likeliest real shape, and constructors
   because `Client.__init__(self, prompt: str)` is the same door one word away.

   **Amended once P8's transport existed.** This rule read "every function in the
   module is checked", and the module-wide `str` ban it implied is unsatisfiable by
   any transport that also satisfies §8.4's *other* requirement: "Every model call
   should be recorded in a consent-aware audit record ... which model received the
   data, and the prompt fingerprint." A model id and a prompt fingerprint are `str`,
   so §8.4 mandates in one sentence what the old wording forbade in the next. Worse,
   the old rule was satisfiable COSMETICALLY -- moving `ModelResponse` into
   `records.py` next door passes it without changing one byte of what reaches a
   model, and a privacy property a file-move satisfies is not a privacy property.
   `str` and `bytes` are therefore checked on the surface, where §8.4 scopes them
   ("its only CONTENT parameter is a `Released`"), and not in the module's interior.

   `CORPUS_ONLY_TYPES` keeps the module-wide ban for the three types that have no
   innocent reading: a `Path`, an `Observation` and a `TextUnit` exist only to carry
   the user's files and their extracted text, all of which §8.4 puts in the
   always-local set. A transport holding one, at any depth, is a finding.

This guard now runs over the real transport: `llm_harness.transport` sets
`IS_MODEL_TRANSPORT = True` and `tests/p7/test_p7_real_transport_egress.py` points
`assert_single_egress` at it. What P7 ships is a checker proven against four
conforming fixtures and seventeen non-conforming ones; what P8 supplies is the
module the property is actually about.

**Stated limit.** This is an existence proof over ONE module namespace. Classes the
transport imports -- P8's `CallPayload`, which carries the model-visible bytes -- are
not walked, exactly as an imported helper is not counted as a second entry point. So
NOTHING HERE SAYS ANYTHING ABOUT WHAT IS IN THOSE BYTES. This is a check on the SHAPE
of the door, and the door being the right shape does not make what goes through it
authorized.

**The sentence that used to stand here was false, and it is worth saying why.** It
read: "That a `CallPayload`'s bytes are the released dossier is proven at runtime by
`build_call_payload`, `CallPayload.__post_init__` and `issue`'s own
`_require_sources`." None of the three ever sees the `Released`.
`build_call_payload` takes bare values; `__post_init__` checks `model_visible_bytes
== assemble(prompt_definition, canonical_dossier_bytes)`; `_require_sources`
recomputes the fingerprint and reassembles the same two fields. All three are
self-consistency. A security review took that sentence at its word, went looking
anyway, and spent a real release on a payload carrying every `raw_value`, every path
and every content hash in the corpus (CR-02) -- and the sentence is why the hole
survived, because it told the previous reader not to look. A stated limit disposed of
by a false claim is worse than an unstated one.

WHAT ACTUALLY PROVES IT, since 2026-09-02, is P7's fourth binding term:
`llm_harness.released_content.released_content_digest` folds the payload's own bytes
and `privacy.binding.consume_release` compares them with the ledger row the gate
wrote, before the spend. That is a RUNTIME check on a call, not a static property of
a namespace, which is why it lives there and not here. Its own limits -- the
builder-authored strings it binds in shape and not in content -- are written at it.
"""
from __future__ import annotations

import ast
import inspect
import typing
from collections.abc import Callable
from pathlib import Path
from types import FunctionType, ModuleType

from evidence_shape.observation import Observation
from evidence_shape.text_units import TextUnit

from privacy.release import Released

#: The types a transport may not take. Done-means 3: "No transport function accepts a
#: string, a file path, or an observation record." `bytes` and `TextUnit` are the same
#: refusal wearing different clothes -- P4's `TextUnit.text` is the complete extracted
#: text, which §8.4 puts in the always-local set.
CONTENT_PARAMETER_TYPES: frozenset[type] = frozenset(
    {str, bytes, Path, Observation, TextUnit})

#: The subset with no innocent reading anywhere in a transport, checked module-wide.
#: §8.4's always-local set names "Paths" and "complete extracted text" outright, and
#: neither a model id nor a prompt fingerprint nor an ISO timestamp is one of these --
#: so unlike `str` and `bytes`, banning them in the interior cannot collide with the
#: audit record §8.4 requires the transport to write.
CORPUS_ONLY_TYPES: frozenset[type] = frozenset({Path, Observation, TextUnit})

#: This module is the INSTRUMENT, not a transport. Task 22 greps `src/` for
#: `IS_MODEL_TRANSPORT is True`; `llm_harness/transport.py` is the one writer of
#: `True`, and the skeleton step now asserts that the scan finds exactly it -- the
#: scan returned `[]` for as long as no module set the flag, which made the loop
#: under it a check that could never fire. The flag is declared here because this
#: module names every forbidden content type by import and would otherwise be the
#: most transport-shaped file in `src/`.
IS_MODEL_TRANSPORT: bool = False

#: Skipped on a method: it is the instance, not a parameter the caller supplies.
_RECEIVER_NAMES: frozenset[str] = frozenset({"self", "cls"})


class EgressGuardFailure(AssertionError):
    """A module does not satisfy Done-means 3's static property.

    An `AssertionError` because this is an assertion helper: it is called from a test
    and its failure is a test failure, not an exception a running product handles.
    """


class MultipleEgressPoints(EgressGuardFailure):
    """More than one public entry point.

    "Exactly one function ... constructs a model request" -- two doors is two places
    to audit and one of them will be forgotten.
    """


class NoEgressPoint(EgressGuardFailure):
    """No public entry point at all.

    Zero violates "exactly one" as surely as two, and a module with no entry point is
    not the transport the caller thinks it is.
    """


class UnreleasedContentParameter(EgressGuardFailure):
    """A parameter that could carry content without a release.

    Raised for a forbidden type, for a container or union that has one inside it, for
    an unannotated parameter (which is not SHOWN to be a `Released`, and "shown to be"
    is the only standard an inspection can hold), for an annotation that cannot be
    resolved, and for an entry point that takes no `Released` at all.
    """


def _defined_here(obj: object, module: ModuleType) -> bool:
    return getattr(obj, "__module__", None) == module.__name__


def _functions(module: ModuleType, *,
               public_only: bool) -> list[tuple[str, FunctionType, bool]]:
    """Every function this module defines, as `(qualified_name, fn, has_receiver)`.

    Module-level functions and the methods of module-level classes. Imported members
    are excluded by `__module__`, so a transport that imports a helper is not accused
    of having two entry points.
    """
    found: list[tuple[str, FunctionType, bool]] = []
    for name, value in vars(module).items():
        if name.startswith("__"):
            continue
        if public_only and name.startswith("_"):
            continue
        if isinstance(value, FunctionType) and _defined_here(value, module):
            found.append((name, value, False))
        elif isinstance(value, type) and _defined_here(value, module):
            for attribute, member in vars(value).items():
                # `__init__` IS checked. Every other dunder is skipped: they are
                # value-semantics methods a dataclass generates (`__repr__` returns
                # `str` by definition, `__eq__` takes `object`) and counting them
                # would make every dataclass a finding. A CONSTRUCTOR is different --
                # it is the one dunder that ADMITS content, and skipping it let
                # `class Client: def __init__(self, prompt: str)` and
                # `@dataclass class PromptEnvelope: text: str` through the guard
                # entirely: constructible un-released string paths, neither counted
                # nor content-checked, in a module whose whole claim is that no such
                # path exists. Rule 3 says "every function in the module is checked;
                # only the public ones are counted", and `__init__` is a function in
                # the module.
                if attribute.startswith("__") and attribute != "__init__":
                    continue
                if public_only and attribute.startswith("_"):
                    continue
                if public_only and attribute == "__init__":
                    continue          # checked, never COUNTED as an egress point
                if isinstance(member, (staticmethod, classmethod)):
                    found.append((f"{name}.{attribute}", member.__func__,
                                  isinstance(member, classmethod)))
                elif isinstance(member, FunctionType):
                    found.append((f"{name}.{attribute}", member, True))
    found.sort(key=lambda entry: entry[0])
    return found


def _leaves(annotation: object) -> list[object]:
    """Every leaf of a possibly-parameterised annotation.

    `list[str]` -> `[str]`; `Path | None` -> `[Path, NoneType]`;
    `dict[str, Released]` -> `[str, Released]`. This is rule 2, and without it a
    transport declares `extra: list[str]` and passes.

    A `Callable[...]` is a LEAF and is not descended into. Rule 2 is about the values
    a caller can put INSIDE a parameter: `list[str]` is a way of handing over a
    string. `Callable[[bytes], bytes]` is a way of handing over a FUNCTION -- the
    caller supplies no bytes at all, and the bytes that later cross it are the ones
    the transport computed for itself downstream of `Gate.release`. §8.4 orders
    privacy "before content reaches any model"; the sink is where released content is
    SUPPOSED to arrive, so reading its argument type as an inbound parameter inverts
    the direction the whole rule is about. `ModelClient.invoke` is that parameter.
    """
    if typing.get_origin(annotation) is Callable:
        return [annotation]
    arguments = typing.get_args(annotation)
    if not arguments:
        return [annotation]
    leaves: list[object] = []
    for argument in arguments:
        leaves.extend(_leaves(argument))
    return leaves


def _parameters(qualified_name: str, function: FunctionType,
                has_receiver: bool) -> list[inspect.Parameter]:
    try:
        signature = inspect.signature(function, eval_str=True)
    except (NameError, TypeError) as error:
        raise UnreleasedContentParameter(
            f"{qualified_name}: an annotation could not be resolved ({error}), so no "
            "parameter can be shown to be a Released"
        ) from error
    parameters = list(signature.parameters.values())
    if has_receiver and parameters and parameters[0].name in _RECEIVER_NAMES:
        parameters = parameters[1:]
    return parameters


def _constructor(cls: type) -> FunctionType | None:
    """A class's OWN `__init__`, generated or hand-written; `object`'s is not one."""
    init = vars(cls).get("__init__")
    return init if isinstance(init, FunctionType) else None


def _egress_surface(module: ModuleType,
                    entry: tuple[str, FunctionType, bool],
                    ) -> list[tuple[str, FunctionType, bool]]:
    """Everything a caller can put content into on the way to a model.

    The entry point; the constructor of the class it is a method of, because a caller
    must build that object to call it; and the constructors of classes DEFINED HERE
    that appear in a checked signature, transitively, because handing one over is
    handing over whatever it was built from. Nothing else in the module is reachable
    from outside with a caller's value in it.
    """
    surface = [entry]
    pending: list[type] = []
    if "." in entry[0]:
        owner = getattr(module, entry[0].split(".", 1)[0], None)
        if isinstance(owner, type) and _defined_here(owner, module):
            pending.append(owner)
    seen: set[type] = set()
    index = 0
    while index < len(surface) or pending:
        while pending:
            cls = pending.pop()
            if cls in seen:
                continue
            seen.add(cls)
            init = _constructor(cls)
            if init is not None:
                surface.append((f"{cls.__name__}.__init__", init, True))
        if index >= len(surface):
            break
        qualified_name, function, has_receiver = surface[index]
        index += 1
        for parameter in _parameters(qualified_name, function, has_receiver):
            if parameter.annotation is inspect.Parameter.empty:
                continue                      # the unannotated check reports it
            for leaf in _leaves(parameter.annotation):
                if isinstance(leaf, type) and _defined_here(leaf, module):
                    pending.append(leaf)
    return surface


def egress_functions(module: ModuleType) -> list[Callable]:
    """The module's public entry points, sorted by name.

    Public module-level functions plus the public methods of public module-level
    classes. This is what Done-means 3 counts; the content check below looks wider.
    """
    return [function for _, function, _ in _functions(module, public_only=True)]


def sink_names(module: ModuleType) -> set[str]:
    """The names on the egress surface that are annotated as a `Callable`.

    Found by ANNOTATION, never by spelling: `ModelClient.invoke` is a sink because its
    type is `Callable[[bytes], bytes]`, and renaming it to `dispatch` changes nothing.
    A hardcoded `"invoke"` would be the source-text technique rule 1 exists to reject.
    """
    public = _functions(module, public_only=True)
    if len(public) != 1:
        return set()
    names: set[str] = set()
    for qualified_name, function, has_receiver in _egress_surface(module, public[0]):
        for parameter in _parameters(qualified_name, function, has_receiver):
            if typing.get_origin(parameter.annotation) is Callable:
                names.add(parameter.name)
    return names


def assert_single_call_site(module: ModuleType) -> None:
    """Assert that the module CALLS its sink exactly once.

    `assert_single_egress` reads signatures and never a function body, so a second
    `model_client.invoke(...)` inside the one entry point -- handing over the
    unreleased `canonical_dossier_bytes` a line before the released
    `model_visible_bytes` -- changes no signature and is invisible to it. That is a
    real §8.4 leak and a real door, and P8's Done-means 1 is about the call, not only
    the door: "Exactly one function in the codebase constructs a model request."

    This is the second instrument, over the module's SOURCE. It is deliberately not
    folded into `assert_single_egress`, whose whole contract is that it imports
    nothing, executes nothing and reads no text.
    """
    names = sink_names(module)
    if not names:
        return
    source = Path(inspect.getfile(module)).read_text()
    calls = [
        node for node in ast.walk(ast.parse(source, filename=module.__name__))
        if isinstance(node, ast.Call)
        and ((isinstance(node.func, ast.Attribute) and node.func.attr in names)
             or (isinstance(node.func, ast.Name) and node.func.id in names))
    ]
    if len(calls) != 1:
        raise MultipleEgressPoints(
            f"{module.__name__} calls its sink {sorted(names)} {len(calls)} times "
            f"at lines {[node.lineno for node in calls]}; Done-means 1 requires "
            "exactly one call that constructs a model request, and a second call is "
            "a second thing that reaches the model with no second release spent")


def assert_single_egress(module: ModuleType) -> None:
    """Assert Done-means 3's static property of `module`.

    Raises `NoEgressPoint` or `MultipleEgressPoints` when the module does not have
    exactly one public entry point; `UnreleasedContentParameter` when any function it
    defines -- public or private, module-level or method -- has an unannotated
    parameter or one carrying a `CORPUS_ONLY_TYPES` leaf, when anything on the egress
    surface carries a `CONTENT_PARAMETER_TYPES` leaf, or when the entry point takes
    no `Released`.

    Returns `None` on success. Nothing is executed, nothing is written, and the module
    under inspection is not imported by this function: the caller imports it and hands
    it over, which is what keeps the guard usable from a test in another package.
    """
    public = _functions(module, public_only=True)
    if not public:
        raise NoEgressPoint(
            f"{module.__name__} defines no public entry point; Done-means 3 requires "
            "exactly one, and zero violates it as surely as two")
    if len(public) > 1:
        raise MultipleEgressPoints(
            f"{module.__name__} defines {len(public)} public entry points "
            f"{[name for name, _, _ in public]}; Done-means 3 requires exactly one, "
            "because two doors is two places to audit")

    # Module-wide, still: an unannotated parameter anywhere, and the three types that
    # exist only to carry the user's files. Identity, not `leaf in SET`: set
    # membership hashes the leaf, and `Annotated[int, {...}]` puts an unhashable
    # object in `get_args`. A `TypeError` out of the guard is the ambiguous signal
    # this module exists to avoid, and the tests agree on every leaf that is a type.
    for qualified_name, function, has_receiver in _functions(module,
                                                            public_only=False):
        for parameter in _parameters(qualified_name, function, has_receiver):
            if parameter.annotation is inspect.Parameter.empty:
                raise UnreleasedContentParameter(
                    f"{qualified_name}({parameter.name}) is unannotated, so it cannot "
                    "be shown to be a Released")
            for leaf in _leaves(parameter.annotation):
                if any(leaf is forbidden for forbidden in CORPUS_ONLY_TYPES):
                    raise UnreleasedContentParameter(
                        f"{qualified_name}({parameter.name}) accepts {leaf!r}, which "
                        "is content the gate never minted a release for")

    # On the egress surface, every content type. Rule 3: this is where §8.4 scopes
    # the ban -- "its only CONTENT parameter is a Released" -- and where a caller
    # actually has a value to put.
    for qualified_name, function, has_receiver in _egress_surface(module, public[0]):
        for parameter in _parameters(qualified_name, function, has_receiver):
            if parameter.annotation is inspect.Parameter.empty:
                continue                    # already raised by the loop above
            for leaf in _leaves(parameter.annotation):
                if any(leaf is forbidden for forbidden in CONTENT_PARAMETER_TYPES):
                    raise UnreleasedContentParameter(
                        f"{qualified_name}({parameter.name}) accepts {leaf!r}, which "
                        "is content the gate never minted a release for")

    name, entry_point, has_receiver = public[0]
    if not any(parameter.annotation is Released
               for parameter in _parameters(name, entry_point, has_receiver)):
        raise UnreleasedContentParameter(
            f"{name} takes no Released; SPEC §6 binds a release to one model target "
            "and one prompt fingerprint, and a call carrying none is bound to nothing")
