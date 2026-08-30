"""An `observation_key` resolved to something a person can read -- or a named failure.

M14 and §8.7: a negative example recorded today must still resolve after an
extractor upgrade, which is why the durable handle is the KEY and never the id.
This module never reaches for an observation by id; B13's guard and this task's
own twin assert it by parsing the package rather than by convention.

**An unresolvable citation is rendered, not dropped.** Done-means 3's second
clause is the whole reason this module returns a record for every key instead of
a shorter list. Silently omitting a broken citation turns an explanation with
three citations into an explanation with two, with nothing to say a third existed
-- and §6.4's rule that an explanation "must not claim evidence the file does not
carry" is only checkable by a reader if the missing evidence is visible AS
missing.

There is no scoring here, no ranking, and no choice about WHICH observation to
show when a key resolves to several. The key is content-addressed over
`(content_hash, extractor_name, locator, raw_value)`, so several rows under one
key are the same observation re-recorded; the first is taken and the count is
reported in the explanation rather than adjudicated.
"""
from __future__ import annotations

import sqlite3
from collections.abc import Sequence
from dataclasses import dataclass

from evidence_shape.store import observations_by_key

from placement.records import MatchingFact

RESOLVED: str = "resolved"
UNRESOLVABLE: str = "unresolvable"
CITATION_STATES: tuple[str, ...] = (RESOLVED, UNRESOLVABLE)


@dataclass(frozen=True)
class ResolvedCitation:
    """One citation, resolved or not. Both states carry an explanation."""

    observation_key: str
    state: str
    excerpt: str | None
    context_before: str | None
    context_after: str | None
    context_truncated: bool
    extractor_name: str | None
    reliability: str | None
    explanation: str


def resolve_citation(conn: sqlite3.Connection,
                     observation_key: str) -> ResolvedCitation:
    """Resolve one key. A miss is a record, never an omission and never a raise."""
    rows = observations_by_key(conn, observation_key)
    if not rows:
        return ResolvedCitation(
            observation_key=observation_key, state=UNRESOLVABLE, excerpt=None,
            context_before=None, context_after=None, context_truncated=False,
            extractor_name=None, reliability=None,
            explanation=(
                f"the citation {observation_key!r} does not resolve to a stored "
                "observation in this database. The decision that cites it was "
                "recorded when it did; an extractor upgrade or a re-scan can "
                "break a key. It is shown here rather than omitted, so an "
                "explanation cannot quietly lose a citation it claimed"))
    observation = rows[0]
    note = ""
    if len(rows) > 1:
        note = (f" This key resolves to {len(rows)} recorded observations; the "
                "first is shown and none is preferred over another.")
    return ResolvedCitation(
        observation_key=observation_key, state=RESOLVED,
        excerpt=observation.normalized_value or observation.raw_value,
        context_before=observation.context_before,
        context_after=observation.context_after,
        context_truncated=bool(observation.context_truncated),
        extractor_name=observation.extractor_name,
        reliability=observation.reliability,
        explanation=(f"resolved through {observation.extractor_name} "
                     f"{observation.extractor_version}." + note))


def resolve_matching_facts(conn: sqlite3.Connection,
                           facts: Sequence[MatchingFact],
                           ) -> tuple[tuple[MatchingFact, ResolvedCitation], ...]:
    """One pair per fact, in the decision's own order. Nothing is filtered out."""
    return tuple((fact, resolve_citation(conn, fact.evidence_ref))
                 for fact in facts)
