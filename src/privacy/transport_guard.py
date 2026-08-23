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
3. **Every function in the module is checked; only the public ones are counted.**
   "The un-released path does not exist" is a claim about the module, not its exports,
   so a private `_format(text: str)` fails it. Classes are walked too: a client
   wrapper `Client.send(self, prompt: str)` is the likeliest real shape.

Running this over the real transport is P8's obligation and cannot happen here --
there is no transport module in this repository. What P7 ships is a checker proven
against four conforming fixtures and seventeen non-conforming ones.
"""
from __future__ import annotations

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

#: This module is the INSTRUMENT, not a transport. Task 22 greps `src/` for
#: `IS_MODEL_TRANSPORT is True`; P8's transport module is the one writer of `True`,
#: and until P8 exists that scan is empty, which is the honest result. The flag is
#: declared here because this module names every forbidden content type by import and
#: would otherwise be the most transport-shaped file in `src/`.
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
                if attribute.startswith("__"):
                    continue
                if public_only and attribute.startswith("_"):
                    continue
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
    """
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


def egress_functions(module: ModuleType) -> list[Callable]:
    """The module's public entry points, sorted by name.

    Public module-level functions plus the public methods of public module-level
    classes. This is what Done-means 3 counts; the content check below looks wider.
    """
    return [function for _, function, _ in _functions(module, public_only=True)]


def assert_single_egress(module: ModuleType) -> None:
    """Assert Done-means 3's static property of `module`.

    Raises `NoEgressPoint` or `MultipleEgressPoints` when the module does not have
    exactly one public entry point, and `UnreleasedContentParameter` when any function
    it defines -- public or private, module-level or method -- has a parameter that
    could carry content, or when the entry point takes no `Released`.

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

    for qualified_name, function, has_receiver in _functions(module,
                                                            public_only=False):
        for parameter in _parameters(qualified_name, function, has_receiver):
            if parameter.annotation is inspect.Parameter.empty:
                raise UnreleasedContentParameter(
                    f"{qualified_name}({parameter.name}) is unannotated, so it cannot "
                    "be shown to be a Released")
            for leaf in _leaves(parameter.annotation):
                # Identity, not `leaf in CONTENT_PARAMETER_TYPES`: set membership
                # hashes the leaf, and `Annotated[int, {...}]` puts an unhashable
                # object in `get_args`. A `TypeError` out of the guard is the
                # ambiguous signal this module exists to avoid, and the two tests
                # agree on every leaf that is a type, which is every forbidden one.
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
