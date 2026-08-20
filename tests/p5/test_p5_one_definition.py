# tests/p5/test_p5_one_definition.py
"""One definition per rule, proved rather than asserted.

Every test here answers the same question about a different rule: is there exactly
ONE place that decides it? A second copy of a rule passes its own tests on the day it
is written and diverges silently afterwards, which is the defect this project has
paid for most often (`extractors/shape.py`'s module docstring).

Nothing below decides whether a rule is RIGHT -- the packages' own tests do that.
These decide only that the rule has one home.

**Never scan the source text for a token.** A name appears in comments and docstrings
too, and asserting "`canonical_json` appears nowhere in this module" against raw text
has produced five false passes in this repository. Every structural claim here parses
the module with `ast` and inspects real nodes.
"""
from __future__ import annotations

import ast
import pathlib

import pytest

from evidence_shape import observation as observation_module
from evidence_shape.canonical import canonical_json as p4_canonical_json
from evidence_shape.observation import (
    MalformedObservation, NON_EMPTY_FIELDS, check_non_empty,
)
from evidence_shape.runs import config_fingerprint

import extractors.shape as shape

from test_p5_shape import an_observation

SHAPE_SOURCE = pathlib.Path(shape.__file__)


def _tree() -> ast.Module:
    return ast.parse(SHAPE_SOURCE.read_text())


def _function_names(tree: ast.Module) -> set[str]:
    return {node.name for node in ast.walk(tree)
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))}


def _referenced_names(tree: ast.Module) -> set[str]:
    """Every real `Name` / `Attribute` root / import binding. Not comments, not text."""
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Name):
            names.add(node.id)
        elif isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name):
            names.add(node.value.id)
        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            for alias in node.names:
                names.add(alias.asname or alias.name.split(".")[0])
    return names


# --- `canonical_json`: one serialization -------------------------------------------

def test_p5_defines_no_second_canonical_json():
    """P5 held a byte-identical copy of P4's `canonical_json`.

    `fingerprint` delegates its DIGEST to P4's `sha256_of` -- because a second
    computation of that one value was found to reject every run record P5 emitted --
    but it still SERIALIZED with the local copy. One edit to P4's canonical form and
    the fingerprint diverges again, silently, with no test failing.

    A `FunctionDef` node, not the token: the name is in this module's imports and its
    docstrings, and a text scan cannot tell those from a definition.
    """
    assert "canonical_json" not in _function_names(_tree()), (
        "extractors.shape defines its own canonical_json; P4 owns the canonical form")


def test_shape_re_exports_p4s_canonical_json_under_that_exact_name():
    # `extractors/events.py` imports `canonical_json` from here, so the name stays
    # importable. Identity, not equality: a same-looking second function is the defect.
    assert shape.canonical_json is p4_canonical_json


def test_the_name_events_imports_still_resolves():
    from extractors.shape import canonical_json  # noqa: F401  -- events.py's import

    assert canonical_json is p4_canonical_json


def test_shape_references_no_hashing_module():
    """`import hashlib` was left behind by the fingerprint fix.

    P5 computes no digest of its own -- `fingerprint` delegates to P4's `sha256_of`,
    and the content hash is P1's and is never recomputed (O5). An import of a hashing
    module in this file is an invitation to write the second hash again.
    """
    assert "hashlib" not in _referenced_names(_tree())


# --- `config_fingerprint`: one digest ----------------------------------------------

def test_p5_fingerprint_equals_p4s_config_fingerprint():
    """The test that would have caught the original break.

    P5 hashed the canonical JSON with `hashlib.sha256`; P4's `sha256_of`
    length-prefixes the part first. The canonical bytes were identical, the digests
    never were, and `run_from_mapping` refused every run P5 emitted. The old test
    compared P5 against a re-derivation of P4's two steps, which is a third copy of
    the composition -- this one compares against the published function P4 validates
    with.

    Non-ASCII and nesting are in the config on purpose: `ensure_ascii` and key
    ordering are exactly the two places a second serialization drifts.
    """
    configs = (
        {},
        {"dpi": 200},
        {"languages": ["en", "zh-Hans"], "dpi": 200, "recognition": "accurate"},
        {"engine": "apple-vision", "hints": {"script": "提出書類", "emoji": "🧾"},
         "pages": [1, 2, 3], "threshold": 0.5, "strict": True, "fallback": None},
    )
    for config in configs:
        assert shape.fingerprint(config) == config_fingerprint(config), config


def test_p5_fingerprint_inherits_p4s_refusal_of_a_non_finite_config():
    # Not a second check in P5: `fingerprint` serializes with P4's canonical form, so
    # P4's refusal arrives through it. If P5 kept its own serialization this would
    # produce `{"threshold":NaN}` and a digest of a config that is not JSON.
    with pytest.raises(ValueError):
        shape.fingerprint({"threshold": float("nan")})


# --- non-empty fields: one rule, two callers ----------------------------------------

def test_the_builder_refuses_an_empty_raw_value_with_p4s_own_exception():
    """A span of empty text died at the store, not at the extractor.

    `Observation.__post_init__` has always refused an empty `raw_value`; P5's builder
    accepted one, so the refusal arrived at write time, deep in a scan, on a file the
    extractor had already finished with -- and §2.4 forbids conflating "unsupported
    format" with "empty document", which is exactly the distinction a crash at the
    sink destroys.

    The exception TYPE is the evidence. P5 raises `MalformedObservation`, which is
    P4's, because the decision is P4's. A P5-local `ValueError` here would mean a
    second rule that happens to agree with P4's today.
    """
    with pytest.raises(MalformedObservation):
        an_observation(raw_value="")


def test_p4s_record_still_refuses_the_same_value():
    # The other caller. Both sides of the rule, in one test file, so neither can be
    # relaxed without the pair visibly disagreeing.
    with pytest.raises(MalformedObservation):
        check_non_empty("", name="raw_value")
    assert check_non_empty("BUSIB 4300", name="raw_value") == "BUSIB 4300"


def test_p5_restates_none_of_p4s_rule():
    """Neutralise the checker P5 calls and P5 accepts the empty string.

    This is the "removing P4's check makes the P5 test fail too" proof. If P5 also
    held its own `if not raw_value`, this would still raise and there would be two
    definitions to keep in step -- which is how one concept ends up with two answers
    (`extractors/shape.py`'s module docstring).
    """
    patch = pytest.MonkeyPatch()
    try:
        patch.setattr(shape, "check_non_empty", lambda value, *, name: value)
        assert an_observation(raw_value="")["raw_value"] == ""
    finally:
        patch.undo()
    # Restored: one switch, one rule, in both directions.
    with pytest.raises(MalformedObservation):
        an_observation(raw_value="")


def test_the_checker_p5_calls_is_the_one_p4s_record_enforces():
    # Identity first -- one function object, reached from both sides, so a
    # same-looking second implementation fails here. Then the AST: P4's own record
    # must enforce the rule THROUGH the function it publishes, or publishing it just
    # adds a third place the rule lives.
    assert shape.check_non_empty is check_non_empty
    called = {node.func.id for node in ast.walk(
        ast.parse(pathlib.Path(observation_module.__file__).read_text()))
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)}
    assert "check_non_empty" in called


def test_p5_gates_the_fields_it_owns_and_derives_that_list_from_p4():
    """P5 does not carry its own list of which fields may not be empty.

    P4 publishes `NON_EMPTY_FIELDS`; the only member P5 cannot check is `run_id`,
    which P4 assigns and P5's builder never receives. Deriving the set by subtraction
    -- rather than typing six names into P5 -- is what keeps a seventh field added to
    P4 from silently going ungated in P5.
    """
    assert shape.BUILDER_NON_EMPTY_FIELDS == tuple(
        name for name in NON_EMPTY_FIELDS if name != "run_id")
    assert "run_id" in NON_EMPTY_FIELDS and "raw_value" in NON_EMPTY_FIELDS

    for name in shape.BUILDER_NON_EMPTY_FIELDS:
        with pytest.raises(MalformedObservation):
            an_observation(**{name: ""})
