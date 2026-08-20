# src/evidence_shape/canonical.py
"""Byte-identical serialization, and the digest every published key is built from.

Conformance rule 8 requires "byte-identical observation set" for the same content
hash, extractor version and config fingerprint; §3.4 keys a cache on it and §8.5
diffs on it. All three fail if two equal records can serialize two ways, so there is
exactly one canonical form and one place that produces it.

`sha256_of` length-prefixes each part before concatenating. The SPEC writes the key
as `sha256(a ‖ b ‖ c ‖ d)`, and plain concatenation is not injective -- ("ab", "c")
and ("a", "bc") produce the same bytes. §8.7 requires a negative example recorded
today to still resolve after an extractor upgrade, which a colliding handle cannot do.
"""
from __future__ import annotations

import hashlib
import json


def canonical_json(value) -> str:
    """One form per value: key-ordered, unpadded, UTF-8, never ASCII-escaped.

    `allow_nan=False` because `NaN`, `Infinity` and `-Infinity` are not JSON. Python's
    own `json.loads` reads the tokens back, so nothing inside this process notices;
    every other consumer of a stored form does, and §8.5's replay diff is a diff
    between stored forms. Worse, `NaN != NaN`: a value holding one can never equal
    itself.

    The refusal is HERE, and not at fingerprint time, because a non-finite float
    reaches the canonical form down three paths and only one of them passes through a
    fingerprint:

      1. `run.config` -> `runs.config_fingerprint`, which is in §3.4's cache key and
         in rule 8's four-field replay key. The cache would miss a configuration it
         had already run, forever.
      2. `observation.confidence` -> `determinism.observation_set_bytes`. §2.7 names
         no scale and §3.13 says confidence is not comparable across extractors, so
         P4 stores the extractor's own number and asserts no range -- NaN included.
         It then serializes to the token `NaN`, and two DIFFERENT readings come out
         byte-identical: rule 8 would report determinism that did not happen.
      3. `location.region` -> the `location` column (`store.record_observation`).
         §2.7's bounding box is four numbers and `Region` accepts any `int | float`.

    Paths 2 and 3 never touch a fingerprint. This function is the one door all three
    pass through, which makes it the only boundary that cannot be walked around.
    """
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False, allow_nan=False)


def _length_prefixed(part: str) -> bytes:
    encoded = part.encode("utf-8")
    return str(len(encoded)).encode("ascii") + b":" + encoded


def sha256_of(*parts: str) -> str:
    """An injective digest over an ordered tuple of strings, algorithm-prefixed."""
    digest = hashlib.sha256(b"".join(_length_prefixed(part) for part in parts))
    return "sha256:" + digest.hexdigest()
