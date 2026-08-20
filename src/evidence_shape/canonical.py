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
    """One form per value: key-ordered, unpadded, UTF-8, never ASCII-escaped."""
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _length_prefixed(part: str) -> bytes:
    encoded = part.encode("utf-8")
    return str(len(encoded)).encode("ascii") + b":" + encoded


def sha256_of(*parts: str) -> str:
    """An injective digest over an ordered tuple of strings, algorithm-prefixed."""
    digest = hashlib.sha256(b"".join(_length_prefixed(part) for part in parts))
    return "sha256:" + digest.hexdigest()
