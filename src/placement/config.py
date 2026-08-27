"""P11's ceilings, read from P1, and the two-condition policy, injected.

No numeric fallback lives here. §8.6 names seven ceilings that are P11's and P1
already publishes a key for every one, so a default here would be P11 authoring a
policy that belongs to configuration -- and the failure it hides is the worst
kind: running a corpus under a limit nobody chose, with nothing to say so.

The support threshold and the margin threshold are SPEC Open question 1 and stay
open. They arrive as a `SupportPolicy` with an id, because SPEC:802-804 requires
both to be recorded on every decision so that a changed threshold is auditable and
replayable rather than invisible.
"""
from __future__ import annotations

import sqlite3
from dataclasses import dataclass

from database_agent.budget import get_ceiling


class ConfigurationRequired(RuntimeError):
    """A limit or threshold P11 needs is absent, non-positive, or out of range."""


#: The seven §8.6 ceilings that are P11's (SPEC:714-717), mapped to live P1 keys.
CEILINGS: dict[str, str] = {
    "max_retrieved_neighbors": "placement.max_retrieved_neighbors",
    "max_local_graph_neighborhood": "placement.max_local_graph_neighborhood",
    "max_candidate_cluster_size": "placement.max_candidate_cluster_size",
    "max_residual_files_per_batch": "residual.max_files_per_review_batch",
    "max_dossier_tokens": "model.max_dossier_tokens_per_call",
    "max_llm_calls_per_thousand_files": "model.max_llm_calls_per_thousand_files",
    "max_cost_per_scan": "model.max_cost_per_scan",
}


@dataclass(frozen=True)
class PlacementLimits:
    max_retrieved_neighbors: int
    max_local_graph_neighborhood: int
    max_candidate_cluster_size: int
    max_residual_files_per_batch: int
    max_dossier_tokens: int
    max_llm_calls_per_thousand_files: int
    max_cost_per_scan: int


@dataclass(frozen=True)
class SupportPolicy:
    """§6.10's two conditions, as configuration rather than as constants.

    `support_scale_max` exists because SPEC Open question 2 says the design names
    "deterministic scores" and a "minimum support threshold" with no scale, and a
    P2 replay assertion cannot compare scores across versions without one. It is
    declared, not chosen.
    """

    policy_id: str
    support_scale_max: float
    minimum_support_threshold: float
    margin_threshold: float

    def __post_init__(self) -> None:
        if not isinstance(self.policy_id, str) or not self.policy_id:
            raise ConfigurationRequired(
                "a support policy carries an id, because §6.10's thresholds are "
                "recorded on every decision and a changed threshold must be "
                "identifiable in a replay"
            )
        for name in ("support_scale_max", "minimum_support_threshold",
                     "margin_threshold"):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise ConfigurationRequired(f"{name} must be a real number")
            object.__setattr__(self, name, float(value))
        if self.support_scale_max <= 0:
            raise ConfigurationRequired("support_scale_max must be positive")
        for name in ("minimum_support_threshold", "margin_threshold"):
            value = getattr(self, name)
            if not 0 <= value <= self.support_scale_max:
                raise ConfigurationRequired(
                    f"{name}={value} lies outside the declared support scale "
                    f"0..{self.support_scale_max}; a threshold no score can reach "
                    "abstains on everything and a threshold every score clears "
                    "gates nothing"
                )

    def margin_predicate(self, best: object, next_best: object) -> bool:
        """P8's Site C authority. The comparison is the policy's, not P8's."""
        return float(best) - float(next_best) >= self.margin_threshold


def _positive(value: object, *, source: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
        raise ConfigurationRequired(
            f"{source} is {value!r}; P11 needs a positive limit and ships no "
            "fallback. A default here would run the corpus under a bound nobody "
            "chose, with nothing to say so."
        )
    return value


def placement_limits(conn: sqlite3.Connection) -> PlacementLimits:
    """P11's seven ceilings for this database. Every one read; none defaulted."""
    return PlacementLimits(**{
        name: _positive(get_ceiling(conn, key), source=key)
        for name, key in CEILINGS.items()
    })


def require_policy(policy: SupportPolicy | None) -> SupportPolicy:
    if not isinstance(policy, SupportPolicy):
        raise ConfigurationRequired(
            "§6.10's minimum support threshold and meaningful margin are "
            "unsettled by the design (SPEC Open question 1) and are injected. "
            "Absent means refuse, not guess."
        )
    return policy
