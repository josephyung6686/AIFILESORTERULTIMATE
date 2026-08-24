"""Conforming and non-conforming transports, for proving the guard in both directions.

Each factory builds a real `ModuleType` populated with real function objects, rather
than a source string: the guard resolves annotations through `fn.__globals__`, which
is this module's namespace, so `Released`, `Path`, `Observation` and `TextUnit` all
resolve exactly as they would in a real transport module. Nothing here is executed by
the guard; only its signature is read.

`_module` sets `__module__` on each member it is given, because the guard filters on
`__module__` to distinguish a function a module DEFINES from one it merely imported.
Members passed as keywords are left alone, which is how the imported-helper fixture is
built.

Four conforming factories and seventeen non-conforming ones. A checker only proven on
the passing case is an assertion that has never been tested.
"""
from __future__ import annotations

import json
from collections.abc import Sequence
from pathlib import Path
from types import ModuleType

from evidence_shape.observation import Observation
from evidence_shape.text_units import TextUnit

from privacy.release import Released


def _module(name: str, *defined, **imported) -> ModuleType:
    module = ModuleType(name)
    for member in defined:
        member.__module__ = name
        setattr(module, member.__name__, member)
    for attribute, value in imported.items():
        setattr(module, attribute, value)
    return module


# --- conforming ---------------------------------------------------------------

def conforming_transport() -> ModuleType:
    """The shape P8's Done-means 1 requires: one public function, one parameter,
    annotated `Released`."""

    def send(released: Released) -> str:
        return released.release_id

    return _module("conforming_transport", send)


def conforming_transport_with_a_timeout() -> ModuleType:
    """A non-content parameter beside the release. Done-means 3 constrains the
    CONTENT parameter -- "No transport function accepts a string, a file path, or an
    observation record" -- and says nothing about a timeout."""

    def send(released: Released, timeout: int = 30) -> str:
        return released.release_id

    return _module("conforming_transport_with_a_timeout", send)


def conforming_transport_as_a_class() -> ModuleType:
    """The likeliest real shape: a client wrapper. The receiver is skipped; the
    parameter is not."""

    class Client:
        def send(self, released: Released) -> str:
            return released.release_id

    return _module("conforming_transport_as_a_class", Client)


def conforming_transport_with_an_imported_helper() -> ModuleType:
    """`json.dumps` in the namespace is not an entry point this module defines."""

    def send(released: Released) -> str:
        return released.release_id

    return _module("conforming_transport_with_an_imported_helper", send,
                   dumps=json.dumps)


# --- non-conforming: the count --------------------------------------------------

def transport_with_two_entry_points() -> ModuleType:
    def send(released: Released) -> str:
        return released.release_id

    def send_batch(released: Released) -> str:
        return released.release_id

    return _module("transport_with_two_entry_points", send, send_batch)


def transport_with_no_entry_point() -> ModuleType:
    return _module("transport_with_no_entry_point")


# --- non-conforming: the content types -----------------------------------------

def transport_taking_a_string() -> ModuleType:
    def send(prompt: str) -> str:
        return prompt

    return _module("transport_taking_a_string", send)


def transport_taking_a_path() -> ModuleType:
    def send(document: Path) -> str:
        return str(document)

    return _module("transport_taking_a_path", send)


def transport_taking_an_observation() -> ModuleType:
    def send(observation: Observation) -> str:
        return observation.raw_value

    return _module("transport_taking_an_observation", send)


def transport_taking_a_text_unit() -> ModuleType:
    def send(unit: TextUnit) -> str:
        return unit.text

    return _module("transport_taking_a_text_unit", send)


def transport_taking_bytes() -> ModuleType:
    def send(payload: bytes) -> str:
        return payload.decode()

    return _module("transport_taking_bytes", send)


def transport_taking_a_list_of_strings() -> ModuleType:
    """The hole a naive checker leaves: no parameter is annotated `str`, and every
    element of one of them is."""

    def send(released: Released, extra: list[str]) -> str:
        return released.release_id

    return _module("transport_taking_a_list_of_strings", send)


def transport_taking_a_sequence_of_strings() -> ModuleType:
    def send(released: Released, extra: Sequence[str]) -> str:
        return released.release_id

    return _module("transport_taking_a_sequence_of_strings", send)


def transport_taking_an_optional_path() -> ModuleType:
    def send(released: Released, attachment: Path | None = None) -> str:
        return released.release_id

    return _module("transport_taking_an_optional_path", send)


# --- non-conforming: the ways a parameter avoids being annotated ----------------

def transport_with_an_unannotated_parameter() -> ModuleType:
    def send(released):
        return released

    return _module("transport_with_an_unannotated_parameter", send)


def transport_taking_var_keyword() -> ModuleType:
    """`**payload` accepts a prompt under any name at all."""

    def send(released: Released, **payload) -> str:
        return released.release_id

    return _module("transport_taking_var_keyword", send)


def transport_taking_var_positional() -> ModuleType:
    def send(released: Released, *parts) -> str:
        return released.release_id

    return _module("transport_taking_var_positional", send)


def transport_with_no_released_parameter() -> ModuleType:
    """One entry point, nothing forbidden, and no release either -- so nothing binds
    the call to a policy version, a model target or an audit record."""

    def send(timeout: int = 30) -> str:
        return "sent"

    return _module("transport_with_no_released_parameter", send)


# --- non-conforming: the ones a source scan would pass --------------------------

def transport_with_a_private_string_helper() -> ModuleType:
    """The un-released path, unexported. It is still a path."""

    def send(released: Released) -> str:
        return _format(released.release_id)

    def _format(text: str) -> str:
        return text

    return _module("transport_with_a_private_string_helper", send, _format)


def transport_as_a_class_taking_a_string() -> ModuleType:
    class Client:
        def send(self, prompt: str) -> str:
            return prompt

    return _module("transport_as_a_class_taking_a_string", Client)


def transport_whose_docstring_mentions_released() -> ModuleType:
    """The fixture that decides the technique.

    A source-text scan for `Released` passes this module. Its entry point takes a
    string.
    """

    def send(prompt: str) -> str:
        """Send a Released to the model. Accepts only a Released. Released, Released."""
        return prompt

    return _module("transport_whose_docstring_mentions_released", send)


# --- the constructor gap: neither counted nor content-checked -----------------

def transport_with_a_content_taking_constructor() -> ModuleType:
    """A hand-written `__init__` that admits a prompt string.

    The eighteenth non-conforming shape, and it used to PASS. `_functions` skipped
    every `__`-prefixed attribute, so a constructor was neither counted as an egress
    point nor content-checked — a constructible un-released string path inside a
    module whose entire claim is that no such path exists.
    """

    class Client:
        def __init__(self, prompt: str) -> None:
            self.prompt = prompt

        def send(self, released: Released) -> str:
            return released.release_id

    return _module("transport_with_a_content_taking_constructor", Client)


def transport_with_a_dataclass_envelope() -> ModuleType:
    """The same hole reached through a GENERATED `__init__`.

    `@dataclass class PromptEnvelope: text: str` writes the constructor for you, so
    nothing in the source looks like a dunder at all.
    """
    import dataclasses

    @dataclasses.dataclass
    class PromptEnvelope:
        text: str

    def send(released: Released) -> str:
        return released.release_id

    return _module("transport_with_a_dataclass_envelope", PromptEnvelope, send)
