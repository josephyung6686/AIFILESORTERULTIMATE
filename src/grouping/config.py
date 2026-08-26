# src/grouping/config.py
"""P9's ceilings, read from P1. No numeric fallback lives here.

Every structural limit P9 obeys is one of P1's published ceiling keys. P9 adds no
fifth key and no default: a fallback number would be P9 authoring a policy that
belongs to configuration, and the failure mode it hides is the worst kind —
running with a limit nobody chose and no error to say so.

The three open-question values (`generic_hub_frequency`,
`minimum_independent_anchors`, `max_excerpt_characters`) have no ceiling key yet
and are mandatory injected arguments. They are the same rule with a different
mechanism: absent means refuse, not guess. How short a "short excerpt" is decides
how much of a file reaches a model, so it is a policy and not a constant.
"""
from __future__ import annotations

import sqlite3
from dataclasses import dataclass

from database_agent.budget import get_ceiling


class ConfigurationRequired(RuntimeError):
    """A limit P9 needs is absent or non-positive. Never a default."""


#: The four live P1 ceiling keys P9 reads, mapped to the limits they set.
#: `CEILING_KEYS` in `database_agent.budget` is the authority for the spellings.
CEILINGS: dict[str, str] = {
    "max_retrieved_neighbors": "grouping.max_retrieved_neighbors",
    "max_graph_nodes": "grouping.max_local_graph_neighborhood",
    "max_candidate_members": "grouping.max_candidate_cluster_size",
    "max_dossier_tokens": "model.max_dossier_tokens_per_call",
}


@dataclass(frozen=True)
class GroupingLimits:
    max_retrieved_neighbors: int
    max_graph_nodes: int
    max_candidate_members: int
    max_dossier_tokens: int
    generic_hub_frequency: int
    minimum_independent_anchors: int
    max_excerpt_characters: int


def _positive(value: object, *, source: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
        raise ConfigurationRequired(
            f"{source} is {value!r}; P9 needs a positive limit and ships no "
            "fallback. A default here would run the corpus under a bound nobody "
            "chose, with nothing to say so."
        )
    return value


def grouping_limits(
    conn: sqlite3.Connection,
    *,
    generic_hub_frequency: int,
    minimum_independent_anchors: int,
    max_excerpt_characters: int,
) -> GroupingLimits:
    """P9's limits for this database. Every one is read or injected; none defaults."""
    read = {
        name: _positive(get_ceiling(conn, key), source=key)
        for name, key in CEILINGS.items()
    }
    return GroupingLimits(
        **read,
        generic_hub_frequency=_positive(
            generic_hub_frequency, source="generic_hub_frequency",
        ),
        minimum_independent_anchors=_positive(
            minimum_independent_anchors, source="minimum_independent_anchors",
        ),
        max_excerpt_characters=_positive(
            max_excerpt_characters, source="max_excerpt_characters",
        ),
    )
