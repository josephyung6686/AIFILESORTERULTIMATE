# src/tree_design/config.py
"""P10's limits, read from P1 or injected by the caller. No number lives here.

§8.6's configurable list contains one ceiling that is P10's outright — "Maximum
folder proposals and maximum depth" — and P1 publishes it as ONE key,
`tree.max_folder_proposals_and_depth`. §8.6 describes two numbers; P1 stores one.
P10 reads what P1 publishes and uses the single value for both the proposal
ceiling and the depth ceiling. Splitting it is a change to `database_agent.budget`
and to §8.6, not a P10 default, and this comment is where a reader finds that out.

The §5.9 thresholds have no ceiling key at all, so they are mandatory injected
arguments. Same rule, different mechanism: absent means refuse, never guess.
"""
from __future__ import annotations

import sqlite3
from collections.abc import Callable
from dataclasses import dataclass

from database_agent.budget import get_ceiling


class ConfigurationRequired(RuntimeError):
    """A limit P10 needs is absent or non-positive. Never a default."""


#: The two live P1 ceiling keys P10 reads. `CEILING_KEYS` in
#: `database_agent.budget` is the authority for the spellings.
CEILINGS: dict[str, str] = {
    "max_folder_proposals_and_depth": "tree.max_folder_proposals_and_depth",
    "max_dossier_tokens": "model.max_dossier_tokens_per_call",
}


@dataclass(frozen=True)
class TreeLimits:
    max_folder_proposals_and_depth: int
    max_dossier_tokens: int
    excessive_depth_warning: int
    tiny_folder_max_files: int
    tiny_folder_count_warning: int
    #: Returns True, False, or None for "no authored test decides this yet".
    #: None must never round to False: a flattening recommendation the product
    #: cannot justify is worse than none.
    materially_improves_retrieval: Callable[[object], bool | None]


def _positive(value: object, *, source: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
        raise ConfigurationRequired(
            f"{source} is {value!r}; P10 needs a positive limit and ships no "
            "fallback. §5.7 and §5.9 deliberately state no number, so a default "
            "here would be P10 authoring the design."
        )
    return value


def tree_limits(
    conn: sqlite3.Connection,
    *,
    excessive_depth_warning: int,
    tiny_folder_max_files: int,
    tiny_folder_count_warning: int,
    materially_improves_retrieval: Callable[[object], bool | None],
) -> TreeLimits:
    """P10's limits for this database. Every one is read or injected."""
    read = {
        name: _positive(get_ceiling(conn, key), source=key)
        for name, key in CEILINGS.items()
    }
    if not callable(materially_improves_retrieval):
        raise ConfigurationRequired(
            "materially_improves_retrieval is the §5.9 test for whether a "
            "dimension earns its level. The design states none, so the caller "
            "supplies one; a built-in test would be an invented threshold."
        )
    return TreeLimits(
        **read,
        excessive_depth_warning=_positive(
            excessive_depth_warning, source="excessive_depth_warning"),
        tiny_folder_max_files=_positive(
            tiny_folder_max_files, source="tiny_folder_max_files"),
        tiny_folder_count_warning=_positive(
            tiny_folder_count_warning, source="tiny_folder_count_warning"),
        materially_improves_retrieval=materially_improves_retrieval,
    )
