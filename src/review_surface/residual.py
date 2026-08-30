"""§7.5's residual surfacing screen, and §7.6's ordering.

    "The residual process should begin with a visible residual surfacing screen,
    not an automatic cleanup operation."
    "The system should divide these files into understandable review sets using
    reliable characteristics, rather than presenting a single intimidating pile."

The seven attributes are a CONTRACT and not a nice-to-have: §7.5 says each set
"should display representative examples, file-type distribution, age range,
available OCR or text evidence, sensitivity status, any weak graph neighbors, and
the reason the system could not safely place the files through the normal
pipeline." A card missing one is a rendering failure, so `residual_card` raises
rather than emitting a shorter card. That is the difference between a screen that
helps and a screen that admits it does not know while looking complete.

`member_file_ids` is deliberately NOT projected onto the card. A card that carried
the member list would let a protected set be expanded into a filename list by
anything holding the card, and Done-means 15 forbids exactly that while the policy
redacts names. The list stays on P11's record.

THE SET COUNT AND THE SET NAMES ARE NOT THIS MODULE'S BUSINESS. §7.5's eight lines
are prefaced "It may show", P11 defers the partition, and SPEC Open question 2 is
open. This renders whatever partition P11 publishes, including none.

**§7.6's gate is the constructor.** The set decision comes before the LLM analyzes
individual files, and a set the user leaves in place must cost zero model calls. A
caller-side `if` is a rule one caller can forget; a constructor that cannot produce
the object is a rule nobody can forget. `recommendations_for` is invoked at most
once and never before the decision is in hand, so "zero model calls" is observable
with a counting double rather than assumed from a comment.

`SetDecisionRequired` is IMPORTED from P11 and re-exported, not minted again. P11's
`require_set_decision` already raises it and means the same fact; a second class of
the same name in a second module is a second home, and a caller catching one while
the other was raised would see the gate as a crash.
"""
from __future__ import annotations

import sqlite3
from collections.abc import Callable, Sequence
from dataclasses import dataclass

from placement.residual import (
    ResidualSet,
    ResidualSetDecision,
    SET_CHOICES,
    SetDecisionRequired,
    model_calls_permitted,
    require_set_decision,
)

__all__ = [
    "SEVEN_ATTRIBUTES", "IncompleteResidualCard", "ResidualFileView",
    "ResidualScreen", "ResidualSetCard", "SetDecisionRequired",
    "residual_card", "residual_file_view", "residual_screen",
]

#: §7.5's seven, by the `ResidualSet` field that carries each. Named here once so
#: the completeness check and the card cannot drift apart.
SEVEN_ATTRIBUTES: tuple[str, ...] = (
    "representative_examples", "file_type_distribution", "age_range",
    "evidence_availability", "sensitivity_status", "weak_graph_neighbours",
    "reason_not_placed",
)


class IncompleteResidualCard(RuntimeError):
    """A set missing one of §7.5's seven. A failure, not a shorter card."""


@dataclass(frozen=True)
class ResidualSetCard:
    """One set, with all seven attributes and P7's protected flag beside them.

    `protected` is carried because `67` §1 requires protected material to be
    marked and counted rather than silently omitted. It is NOT one of the seven:
    Done-means 5 says seven, and counting it would make the completeness check
    disagree with the sentence it enforces.
    """

    set_id: str
    plan_version: str
    label: str
    file_count: int
    representative_examples: tuple[str, ...]
    file_type_distribution: tuple[tuple[str, int], ...]
    age_range: tuple[str, ...]
    evidence_availability: str
    sensitivity_status: str
    weak_graph_neighbours: tuple[str, ...]
    reason_not_placed: str
    protected: bool
    choices: tuple[str, ...]

    def attribute(self, name: str) -> object:
        if name not in SEVEN_ATTRIBUTES:
            raise KeyError(
                f"{name!r} is not one of §7.5's seven display attributes")
        return getattr(self, name)


@dataclass(frozen=True)
class ResidualScreen:
    plan_version: str
    summary_line: str
    total_unplaced: int
    cards: tuple[ResidualSetCard, ...]


def residual_card(residual_set: ResidualSet) -> ResidualSetCard:
    """One card. Raises if any of §7.5's seven attributes is absent or empty."""
    missing = [name for name in SEVEN_ATTRIBUTES
               if not getattr(residual_set, name)]
    if missing:
        raise IncompleteResidualCard(
            f"residual set {residual_set.set_id!r} has no value for {missing}. "
            "§7.5 requires all seven attributes on every set, and a card that "
            "silently drops one looks complete while hiding the thing the user "
            "needs in order to decide")
    return ResidualSetCard(
        set_id=residual_set.set_id,
        plan_version=residual_set.plan_version,
        label=residual_set.label,
        file_count=residual_set.file_count,
        representative_examples=tuple(residual_set.representative_examples),
        file_type_distribution=tuple(residual_set.file_type_distribution),
        age_range=tuple(residual_set.age_range),
        evidence_availability=residual_set.evidence_availability,
        sensitivity_status=residual_set.sensitivity_status,
        weak_graph_neighbours=tuple(residual_set.weak_graph_neighbours),
        reason_not_placed=residual_set.reason_not_placed,
        protected=bool(residual_set.protected),
        # §7.6's four, imported from P11. A fifth invented here would be a set
        # decision P11 has no branch for.
        choices=SET_CHOICES)


def residual_screen(sets: Sequence[ResidualSet], *,
                    plan_version: str) -> ResidualScreen:
    """§7.5's summary sentence, then a card per set P11 published.

    The count is summed from the cards rather than passed in, so the sentence and
    the cards cannot disagree -- a summary saying 146 above cards totalling 131
    is the two-denominator shape D11 was ruled on. Every WORD of the sentence is
    deferred by the SPEC's Deferred table; the design's own wording stands in
    until a renderer with copy replaces it.
    """
    cards = tuple(residual_card(one) for one in sets)
    total = sum(card.file_count for card in cards)
    return ResidualScreen(
        plan_version=plan_version,
        summary_line=(
            f"Your main structure is ready. We found {total} files that do not "
            "fit a confirmed group or approved destination."),
        total_unplaced=total,
        cards=cards)


@dataclass(frozen=True)
class ResidualFileView:
    """The per-file residual surface. It cannot exist before the set decision."""

    set_id: str
    plan_version: str
    set_decision: ResidualSetDecision
    recommendations: tuple[object, ...]
    model_calls_permitted: bool


def residual_file_view(conn: sqlite3.Connection, *, plan_version: str,
                       set_id: str,
                       recommendations_for: Callable[[str], Sequence[object]],
                       ) -> ResidualFileView:
    """Fetch the decision FIRST. Ask for recommendations only if it permits them.

    `require_set_decision` raises `SetDecisionRequired` and that exception is let
    through unchanged: it already names the set, the plan version and the reason,
    and re-raising it under a P13 wrapper would put a second sentence on one
    fact. What P13 adds is the ORDER -- the call happens before
    `recommendations_for` is ever reached, which is why an undecided set produces
    no request rather than a discarded result.
    """
    decision = require_set_decision(conn, plan_version=plan_version,
                                    set_id=set_id)
    permitted = model_calls_permitted(decision)
    recommendations = tuple(recommendations_for(set_id)) if permitted else ()
    return ResidualFileView(
        set_id=set_id, plan_version=plan_version, set_decision=decision,
        recommendations=recommendations, model_calls_permitted=permitted)
