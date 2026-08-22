# src/facts/cache.py
"""§3.4's cache key, and what invalidates a fact -- Done-means 15 and 16.

The design, in one sentence: "The cache key includes content hash, extractor version,
analysis tier, model identifier when relevant, and prompt fingerprint for model-derived
results. This prevents stale results from surviving a content rewrite, avoids
unnecessary work when a file is merely renamed, and makes model or prompt changes
auditable."

Three consequences, and every one of them is a test:

  - There is NO path input. Not ignored, not nullable -- absent. That absence IS
    "avoids unnecessary work when a file is merely renamed": a rename cannot reach the
    key because the key has nowhere to put a path.
  - `content_hash` is a part, so a content rewrite is a different slot and the old
    facts cannot be found in it. That is "prevents stale results from surviving a
    content rewrite".
  - `model_identifier` and `prompt_fingerprint` are parts, so a prompt change
    re-resolves and BOTH keys stay computable and readable. That is "makes model or
    prompt changes auditable" -- §8.2's supersede-never-overwrite, at the cache.

TWO CACHE KEYS EXIST, AND THIS IS NOT THE OTHER ONE. `extractors.runs.cache_key(*,
content_hash, extractor_name, extractor_version, analysis_tier, config_fingerprint)`
identifies an EXTRACTION RESULT -- which extractor at which configuration produced
these observations. This one identifies a FACT -- which evidence, under which model and
prompt, produced this conclusion. §3.4 predates §3.2's observation/fact split, so one
design sentence has two subjects and the built system has two functions. Neither list
of parts is a subset of the other, so neither can be expressed in terms of the other,
and this module imports nothing from `extractors`.

`None` VS `""`. `sha256_of` is length-prefixed and therefore injective over the tuple
of strings it is handed, but it takes strings and `None` is not one. Every part is
encoded through `canonical_json` first: `None` becomes `null` and `""` becomes `""`
(with the quotes) -- different strings, different lengths, different digests. An absent
model identifier and an empty one are not the same cache slot.

WHAT IS NOT DECIDED HERE. §3.4 says "model identifier when relevant" and "prompt
fingerprint for model-derived results" and states no dependency between them, so no
both-or-neither guard is imposed: P8 is the part that would know whether one is true and
P8 does not exist.

THE FIVE PARTS ARE THE CALLER'S. The tests pin `fact_cache_key` to exactly
`CACHE_KEY_PARTS` as keyword-only arguments with no defaults and no `conn` / `file_id`.
A defaulted part is a part that silently stops distinguishing cache slots. Deriving
`extractor_version` and `analysis_tier` from every observation of a file version is
the rule later producers must apply before they call this helper; the helper itself
hashes the five parts it is given, so a rename cannot reach the key and a caller
cannot add a sixth.
"""
from __future__ import annotations

import sqlite3

from evidence_shape.canonical import canonical_json, sha256_of
from evidence_shape.vocabulary import ANALYSIS_TIERS, check

__all__ = ["CACHE_KEY_PARTS", "fact_cache_key", "is_stale"]

#: §3.4's five parts, in §3.4's own order. The order is part of the key: the digest is
#: over an ordered tuple, so reordering this tuple would invalidate every stored key.
CACHE_KEY_PARTS: tuple[str, ...] = (
    "content_hash",
    "extractor_version",
    "analysis_tier",
    "model_identifier",
    "prompt_fingerprint",
)

#: The two tables whose rows record "work was done under this key". `unresolved` is
#: here because the SPEC gives its `cache_key` the "same composition as `file_facts`
#: (§3.4), so an abstention is invalidated by the same events that invalidate a fact".
#: A file whose deterministic pass produced only refusals HAS been resolved under that
#: key; a reader that saw only `file_facts` would call it stale forever.
#:
#: Addressed by SQL rather than by importing `facts.file_facts` and `facts.unresolved`,
#: because every Wave B producer imports both this module and those, and a module that
#: imports none of its siblings cannot be half of an import cycle.
_RECORD_TABLES: tuple[str, ...] = ("file_facts", "unresolved")


def _required(value: str, *, name: str) -> str:
    """`content_hash` and `extractor_version` identify the work. An empty one means
    "unknown", and two unknowns must not silently share a cache slot with each other
    or with a real value."""
    if not isinstance(value, str) or not value:
        raise ValueError(f"{name} is required and must be a non-empty string")
    return value


def fact_cache_key(*, content_hash: str, extractor_version: str,
                   analysis_tier: str, model_identifier: str | None,
                   prompt_fingerprint: str | None) -> str:
    """§3.4's key for one (file version, deterministic pass). A `sha256:` digest.

    THE ONE HELPER. Every producer imports this; no task writes its own copy of the
    five-part composition, and `facts.cache` is the module that owns it.

    All five parts are the caller's and carry no default. The two model parts are
    `None` on every deterministic fact P6 writes (§3.3), and Task 17's LLM-supported
    fact is the one place that is not true. A defaulted part is a part that silently
    stops distinguishing cache slots.

    `analysis_tier` is checked against P4's `ANALYSIS_TIERS` rather than hashed
    blindly: P6 never infers a tier, and a value P4 does not publish is a contract
    revision, not a row this module quietly accepts.
    """
    _required(content_hash, name="content_hash")
    _required(extractor_version, name="extractor_version")
    check(analysis_tier, ANALYSIS_TIERS, name="analysis_tier")
    parts = (content_hash, extractor_version, analysis_tier,
             model_identifier, prompt_fingerprint)
    assert len(parts) == len(CACHE_KEY_PARTS)
    return sha256_of(*(canonical_json(part) for part in parts))


def is_stale(conn: sqlite3.Connection, *, file_id: str, content_hash: str,
             cache_key: str) -> bool:
    """True unless some record for `(file_id, content_hash)` was written under exactly
    this key.

    Three cases, one rule:

      - a rename, content unchanged  -> facts under this same key   -> False
      - a content rewrite            -> new slot, nothing in it     -> True
      - a bumped version or prompt   -> facts under the OLD key     -> True

    "Nothing has been computed for this file version" and "the content was rewritten"
    are the same case, and both need computing, which is why one predicate serves all
    three. This function re-resolves nothing and writes nothing: §8.2's supersession is
    `facts/supersede.py`'s and the sequencing is `facts/resolver.py`'s.
    """
    _required(file_id, name="file_id")
    _required(content_hash, name="content_hash")
    _required(cache_key, name="cache_key")
    for table in _RECORD_TABLES:
        found = conn.execute(
            f"SELECT 1 FROM {table} "
            "WHERE file_id = ? AND content_hash = ? AND cache_key = ? LIMIT 1",
            (file_id, content_hash, cache_key),
        ).fetchone()
        if found is not None:
            return False
    return True
