# src/tree_design/config.py
"""P10's limits, read from P1 or injected by the caller. No number lives here.

§8.6's configurable list contains one line that is P10's outright -- "Maximum
folder proposals and maximum depth" (`00`:256) -- and it names TWO numbers where
every other line in that list names one. P1 published ONE key for both,
`tree.max_folder_proposals_and_depth`, and this module used the single value for
four different questions: how many OPTIONS the picker offers
(`routing.route_branch`), how DEEP a candidate may go (`validation._v3`), how
WIDE a date level may be before it is coarsened to the granularity `00`:88's
Photos template names (`materialise.narrow_wide_date_levels`), and the sample
size of the lists §5.9 and §5.5 print (`health.sample_size`).

The first two want opposite values and no P10 change could reconcile them:
`00`:78's own recommended tree is five levels deep, so the depth job wants at
least five, and a picker offering five options per branch is not a picker.
`test_one_ceiling_can_serve_both_the_picker_and_the_depth_limit` failed for as
long as the key was one, and this docstring recorded the complaint.

Since 2026-08-29 P1 publishes the two numbers §8.6 already names --
`tree.max_folder_proposals` and `tree.max_depth`. `_v3` reads the depth one; the
picker, the date-level width and the sample size read the breadth one. That is
still three questions on one number, and it is the reading §8.6's words plainly
carry: all three are "how many things does the interface put in front of the user
at once". Depth was never that question, which is why it is the one that left.

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
    "max_folder_proposals": "tree.max_folder_proposals",
    "max_depth": "tree.max_depth",
    "max_dossier_tokens": "model.max_dossier_tokens_per_call",
}


@dataclass(frozen=True)
class TreeLimits:
    max_folder_proposals: int
    #: The other half of `00`:256's line. Read by `validation._v3` and by nothing
    #: else: depth is not "how many things are in front of the user at once".
    max_depth: int
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
