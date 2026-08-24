# src/facts/budgets.py
"""§8.6 — the three ceilings P6 holds, and the one thing a ceiling may not change.

§00, verbatim: "If the budget is exhausted, the product should retain extracted
evidence, mark the deferred stage, and leave the file or group in review rather than
guessing. Cost exhaustion must never turn into lower-quality automatic
classification."

Every one of P6's three ceilings is a `model.*` ceiling. That is not a coincidence to
note in passing — it is what makes the sentence above mechanical here. By the time
any ceiling is consulted, `direct` and `rule` have already run, so the only route a
ceiling can close is the LLM route and there is no cheaper producer to fall back to.
Degradation in P6 is subtraction, never substitution.

P1 holds the ceiling VALUES and enforces none of them, so exhaustion arrives as an
injected predicate — P3's precedent, widened from `Callable[[], bool]` to
`Callable[[str], bool]` because §8.6's reporting requirement is per ceiling. No
number is defined in this module.
"""
from __future__ import annotations

import sqlite3
from typing import TYPE_CHECKING, Callable, Iterable

from database_agent.budget import CEILING_KEYS, get_ceiling

from facts.unresolved import (
    BUDGET_DEFERRED, DIRECT_ROUTE, LLM_ROUTE, RULE_ROUTE, unresolved_for_file,
)

if TYPE_CHECKING:  # `resolver` imports this module; the annotation must not.
    from facts.resolver import ResolveResult

#: §8.6's three model ceilings, spelled with P1's keys. P1 publishes sixteen; the
#: other thirteen belong to P4, P5, P9, P10, P11 and P13.
P6_CEILING_KEYS: tuple[str, str, str] = (
    "model.max_llm_calls_per_thousand_files",
    "model.max_cost_per_scan",
    "model.max_dossier_tokens_per_call",
)

#: §8.6: "Direct facts and high-precision rules run first because they are cheap and
#: reliable ... LLM calls are reserved for bounded ambiguities". P6's three producers
#: in that order. These are PRODUCER names, and they are Task 5's published constants
#: rather than three fresh literals (preamble §3.1) — so an abstention row and this
#: order cannot drift apart. `rule` is the producer; `validated` is the reliability
#: state it writes.
DEGRADATION_ORDER: tuple[str, str, str] = (DIRECT_ROUTE, RULE_ROUTE, LLM_ROUTE)

#: The only producer a ceiling can close, held as data so the resolver's gate is
#: readable from this module rather than from an `if` buried in a loop.
CEILING_GATED_STAGES: frozenset[str] = frozenset({LLM_ROUTE})


class UnknownCeiling(Exception):
    """A ceiling key outside P6's three was attributed a deferral."""


def ceiling_values(conn: sqlite3.Connection) -> dict[str, int | None]:
    """P6's three ceilings as P1 currently holds them.

    Returned for reporting and for a caller assembling its own predicate. P6 does
    not compare against these numbers: comparing would put the enforcement here,
    and P1's own docstring is explicit that reading a ceiling is not enforcing it.
    """
    return {key: get_ceiling(conn, key) for key in P6_CEILING_KEYS}


def exhausted_ceilings(*, budget_exhausted: Callable[[str], bool]) -> tuple[str, ...]:
    """Which of P6's three the caller reports exhausted, asked in published order.

    All of them are asked, not just the first: §8.6 requires P6 to report how much
    work it deferred against EACH ceiling, and a short-circuit would attribute a
    simultaneous exhaustion to whichever key happened to sort first.
    """
    return tuple(key for key in P6_CEILING_KEYS if budget_exhausted(key))


def deferred_counts(conn: sqlite3.Connection, *,
                    results: Iterable["ResolveResult"]) -> dict[str, int]:
    """How many fact-resolution requests were deferred against each ceiling.

    Scan-scoped, and cross-checked against the records: the count for a result is
    the number of `budget_deferred` rows that result actually wrote, so the report
    cannot drift from the table. A result exhausted against two ceilings counts
    against both — §8.6 asks what each ceiling cost, not which one to blame.

    There is no per-ceiling column on `unresolved` and P6 owns exactly four tables,
    so the DURABLE per-ceiling record is Task 21's `stage_output.payload`, which
    carries `deferred_against` verbatim and which P2 stores and never parses.
    """
    counts: dict[str, int] = {key: 0 for key in P6_CEILING_KEYS}
    for result in results:
        if not result.deferred_against:
            continue
        rows = unresolved_for_file(conn, result.file_id, result.content_hash,
                                   reason=BUDGET_DEFERRED)
        for key in result.deferred_against:
            if key not in P6_CEILING_KEYS:
                raise UnknownCeiling(
                    f"{key!r} is not one of P6's three model ceilings "
                    f"{P6_CEILING_KEYS}; P1 publishes it, another part holds it"
                )
            counts[key] += len(rows)
    return counts


# Asserted at import so a P1 rename is a startup failure rather than a silent
# miscount: P6 names three of P1's sixteen keys and owns none of them.
assert set(P6_CEILING_KEYS) <= set(CEILING_KEYS)
