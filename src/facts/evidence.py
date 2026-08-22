# src/facts/evidence.py
"""The read over P4, and the one place P6 turns an observation into a citation.

Four properties live here because each of them must exist exactly once:

* **The citation is `observation_key`** (M14). It hashes `content_hash · extractor_name
  · locator · raw_value` and excludes `extractor_version` by construction, so a
  reference stored today resolves after an extractor upgrade -- which is what §8.7's
  requirement that rejected proposals "must be stored with the evidence that produced
  them" needs in order to still mean something in six months. `observation_id` is
  P4's per-row identity and is never cited.

* **The read is per file version.** §3.4's cache key and §8.2's abstention row are both
  per content hash, and P4 publishes only `observations_for_file`, which spans every
  hash the file has ever had. The filter is here and nowhere else (finding F12).

* **The context is a pair with its flag** (M5, §8.6). `context_before` and
  `context_after` are never concatenated, and `context_truncated` is returned beside
  them so a caller cannot read one without the other. §8.6: a prompt over budget
  "should not truncate silently in a way that removes the decisive evidence."

* **Nothing here branches on a format.** §2.8 exists so downstream logic does not, and
  Done-means 6 asserts P6 resolves a source type it has never seen. There is no
  mapping keyed by `source_type` and no string naming one anywhere in `facts`;
  `tests/p6/test_p6_evidence.py` asserts that by runtime introspection of every
  module in the package, not by reading the source text.

P4's reads are `ORDER BY rowid`, which is insertion order -- a property of the
database, not of the corpus. Every read published here imposes a total order of P6's
own before returning, so the same corpus extracted in a different order produces the
same facts (§8.5 replay).

`unit_for_observation` is part of P4's read surface and is deliberately not called
here: the text unit is the span substrate §3.6's quote check needs, and that check is
the P8 seam's. Re-deriving context P4 already split is what M5 forbids.
"""
from __future__ import annotations

import sqlite3
from typing import Iterable

from evidence_shape.observation import Observation
from evidence_shape.store import (
    observations_by_key, observations_for_file, runs_for_content,
)


class UnknownRun(Exception):
    """An observation whose `run_id` has no `extraction_runs` row.

    P6 never re-derives what P4 assigns, so there is no fallback: an inferred
    `analysis_tier` would land in §3.4's cache key, and a wrong cache key is a fact
    that never invalidates.
    """


def cite(observation: Observation) -> str:
    """M14: the citation handle P6 stores. Content-addressed, version-independent."""
    return observation.observation_key


def observations_for_version(conn: sqlite3.Connection, file_id: str,
                             content_hash: str) -> tuple[Observation, ...]:
    """Every observation P4 holds for one *version* of one file, in P6's own order.

    P4's `observations_for_file` spans content hashes and returns insertion order.
    Both are corrected here: the filter is §3.4's per-version scope, and the sort is
    the total order every downstream ranking starts from.
    """
    return _ordered(one for one in observations_for_file(conn, file_id)
                    if one.content_hash == content_hash)


def resolve_citation(conn: sqlite3.Connection,
                     observation_key: str) -> tuple[Observation, ...]:
    """Every observation carrying this key -- one per extractor version that saw it.

    Returns an empty tuple when nothing carries the key: §3.6 check 2 asks whether a
    cited quote is present in the evidence, and "no" is an answer, not a crash.
    """
    return _ordered(observations_by_key(conn, observation_key))


def context_pair(observation: Observation) -> tuple[str, str, bool]:
    """§2.8's surrounding context, as M5 split it: `(before, after, truncated)`.

    Never a concatenation, and never the pair without the flag. `None` renders as the
    empty string so a word-boundary check over an absent context finds nothing rather
    than raising.
    """
    return (observation.context_before or "",
            observation.context_after or "",
            bool(observation.context_truncated))


def analysis_tier_for_observation(conn: sqlite3.Connection,
                                  observation: Observation) -> str:
    """I4's tier, read from P4's run. Never inferred from the extractor or the zone."""
    for run in runs_for_content(conn, observation.content_hash):
        if run.run_id == observation.run_id:
            return run.analysis_tier
    raise UnknownRun(
        f"observation {observation.observation_key} names run "
        f"{observation.run_id!r}, which has no extraction_runs row; P6 reads "
        f"analysis_tier from P4 and derives it from nothing"
    )


def _ordered(observations: Iterable[Observation]) -> tuple[Observation, ...]:
    """Score-free total order: `observation_key` ascending, then extractor version.

    The key is content-addressed, so this order is a property of the corpus. P4's
    `rowid` order is a property of the database and reverses when the same three runs
    are written in the opposite sequence (verified by execution, 2026-08-21).
    """
    return tuple(sorted(observations,
                        key=lambda one: (one.observation_key,
                                         one.extractor_version, one.run_id)))
