"""Scan-scoped call and estimated-cost reservations, plus the reduction ladder.

Ceilings are injected on `ScanBudget`. This module authors none. The ledger is
P8's own tables, created here, not by Task 3. Live `open_database` connections
use `isolation_level=None`, so every mutation issues its own `BEGIN` and
commits or rolls back. An already-open transaction is refused rather than
rewritten.
"""
from __future__ import annotations

import math
import sqlite3
import uuid
from collections.abc import Sequence
from dataclasses import dataclass
from decimal import Decimal

from llm_harness.records import GroundingReport, PreCallAbstention
from llm_harness.vocabulary import (
    BUDGET_EXHAUSTED,
    DEFERRED,
    PRESERVED_ANCHORS,
    REDUCTION_NONE,
    SPLIT,
    SUMMARIZED_FACTS,
)

MAX_CALLS_PER_1000_FILES: str = "model.max_calls_per_1000_files"
MAX_ESTIMATED_COST_PER_SCAN: str = "model.max_estimated_cost_per_scan"

_RESERVE_COUNTER_SQL = """
INSERT INTO llm_scan_budget (scan_id, calls_reserved, estimated_cost_reserved)
SELECT ?, 1, ?
WHERE 1 <= ? AND CAST(? AS NUMERIC) <= CAST(? AS NUMERIC)
ON CONFLICT(scan_id) DO UPDATE SET
    calls_reserved = llm_scan_budget.calls_reserved + 1,
    estimated_cost_reserved = CAST(llm_scan_budget.estimated_cost_reserved AS NUMERIC)
        + CAST(excluded.estimated_cost_reserved AS NUMERIC)
WHERE llm_scan_budget.calls_reserved + 1 <= ?
  AND CAST(llm_scan_budget.estimated_cost_reserved AS NUMERIC) + CAST(? AS NUMERIC)
      <= CAST(? AS NUMERIC)
RETURNING scan_id, calls_reserved, estimated_cost_reserved
"""

LLM_SCAN_BUDGET_DDL = """
CREATE TABLE IF NOT EXISTS llm_scan_budget (
    scan_id TEXT PRIMARY KEY,
    calls_reserved INTEGER NOT NULL,
    estimated_cost_reserved TEXT NOT NULL
);
"""

LLM_BUDGET_RESERVATION_DDL = """
CREATE TABLE IF NOT EXISTS llm_budget_reservation (
    reservation_id TEXT PRIMARY KEY,
    scan_id TEXT NOT NULL,
    estimated_cost TEXT NOT NULL,
    actual_cost TEXT,
    status TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS llm_budget_reservation_scan
    ON llm_budget_reservation (scan_id);
"""


class BudgetExhausted(Exception):
    """The scan's injected call or estimated-cost ceiling would be exceeded."""


class BudgetTransactionOpen(Exception):
    """Reservation helpers refuse to join an already-open transaction."""


def _require_finite_non_negative_decimal(value: object, *, name: str) -> Decimal:
    if not isinstance(value, Decimal):
        raise ValueError(f"{name} is an injected Decimal; there is no default")
    if not value.is_finite() or value < 0:
        raise ValueError(f"{name} must be a finite non-negative Decimal")
    return value


def _require_bool(value: object, *, name: str) -> bool:
    if value is not True and value is not False:
        raise ValueError(f"{name} must be a bool")
    return value


def _freeze_bool_sequence(value: object, *, name: str) -> tuple[bool, ...]:
    if isinstance(value, (str, bytes)) or not isinstance(value, Sequence):
        length = len(value) if isinstance(value, (str, bytes)) else 0
        raise ValueError(
            f"{name} is a sequence; a bare string would become {length} "
            "one-character references"
        )
    frozen = tuple(value)
    if not all(item is True or item is False for item in frozen):
        raise ValueError(f"{name} must be a sequence of bool")
    return frozen


@dataclass(frozen=True, slots=True)
class ScanBudget:
    scan_id: str
    corpus_file_count: int
    max_calls_per_1000_files: int
    max_estimated_cost: Decimal

    def __post_init__(self) -> None:
        if not self.scan_id:
            raise ValueError("scan_id is required")
        if self.corpus_file_count < 0:
            raise ValueError("corpus_file_count cannot be negative")
        if self.max_calls_per_1000_files < 0:
            raise ValueError(
                f"{MAX_CALLS_PER_1000_FILES} is injected; a negative ceiling is not an echo"
            )
        _require_finite_non_negative_decimal(
            self.max_estimated_cost, name=MAX_ESTIMATED_COST_PER_SCAN,
        )


@dataclass(frozen=True, slots=True)
class BudgetReservation:
    reservation_id: str
    scan_id: str
    estimated_cost: Decimal
    actual_cost: Decimal | None


@dataclass(frozen=True, slots=True)
class ReductionDecision:
    rung: str
    fitting_shard_count: int
    attempted_transformations: tuple[str, ...]
    gate_releases: int
    reservations: int
    invocations: int
    abstention: PreCallAbstention | None


def create_budget_schema(conn: sqlite3.Connection) -> None:
    """Create Task 4's two tables. Idempotent. Call after `create_llm_schema`."""
    conn.executescript(LLM_SCAN_BUDGET_DDL)
    conn.executescript(LLM_BUDGET_RESERVATION_DDL)


def allowed_calls(budget: ScanBudget) -> int:
    return math.floor(
        budget.corpus_file_count * budget.max_calls_per_1000_files / 1000
    )


def _reject_open_transaction(conn: sqlite3.Connection) -> None:
    if conn.in_transaction:
        raise BudgetTransactionOpen(
            "budget reservation rejects an already-open transaction"
        )


def _as_decimal(value: object) -> Decimal:
    if isinstance(value, Decimal):
        return value
    return Decimal(str(value))


def reserve_call(
    conn: sqlite3.Connection,
    budget: ScanBudget, *,
    estimated_cost: Decimal,
) -> BudgetReservation:
    _require_finite_non_negative_decimal(estimated_cost, name="estimated_cost")
    _reject_open_transaction(conn)
    allowed = allowed_calls(budget)
    cost_text = format(estimated_cost, "f")
    ceiling_text = format(budget.max_estimated_cost, "f")
    begun = False
    try:
        conn.execute("BEGIN")
        begun = True
        row = conn.execute(
            _RESERVE_COUNTER_SQL,
            (
                budget.scan_id,
                cost_text,
                allowed,
                cost_text,
                ceiling_text,
                allowed,
                cost_text,
                ceiling_text,
            ),
        ).fetchone()
        if row is None:
            conn.execute("ROLLBACK")
            begun = False
            raise BudgetExhausted(
                f"scan {budget.scan_id!r} cannot reserve another call or cost"
            )
        reservation_id = str(uuid.uuid4())
        conn.execute(
            "INSERT INTO llm_budget_reservation ("
            "reservation_id, scan_id, estimated_cost, actual_cost, status"
            ") VALUES (?, ?, ?, NULL, 'reserved')",
            (reservation_id, budget.scan_id, cost_text),
        )
        conn.execute("COMMIT")
        begun = False
        return BudgetReservation(
            reservation_id=reservation_id,
            scan_id=budget.scan_id,
            estimated_cost=estimated_cost,
            actual_cost=None,
        )
    except BudgetExhausted:
        raise
    except Exception:
        if begun:
            conn.execute("ROLLBACK")
        raise


def settle_call(
    conn: sqlite3.Connection,
    reservation: BudgetReservation, *,
    actual_cost: Decimal,
) -> BudgetReservation:
    _require_finite_non_negative_decimal(actual_cost, name="actual_cost")
    _reject_open_transaction(conn)
    begun = False
    try:
        conn.execute("BEGIN")
        begun = True
        row = conn.execute(
            "UPDATE llm_budget_reservation "
            "SET actual_cost = ?, status = 'settled' "
            "WHERE reservation_id = ? AND status = 'reserved' "
            "RETURNING reservation_id, scan_id, estimated_cost, actual_cost",
            (format(actual_cost, "f"), reservation.reservation_id),
        ).fetchone()
        if row is None:
            conn.execute("ROLLBACK")
            begun = False
            raise ValueError(
                f"reservation {reservation.reservation_id!r} is not reserved"
            )
        conn.execute("COMMIT")
        begun = False
        return BudgetReservation(
            reservation_id=row["reservation_id"],
            scan_id=row["scan_id"],
            estimated_cost=_as_decimal(row["estimated_cost"]),
            actual_cost=_as_decimal(row["actual_cost"]),
        )
    except Exception:
        if begun:
            conn.execute("ROLLBACK")
        raise


def release_reservation(
    conn: sqlite3.Connection,
    reservation: BudgetReservation,
) -> None:
    _reject_open_transaction(conn)
    begun = False
    try:
        conn.execute("BEGIN")
        begun = True
        row = conn.execute(
            "UPDATE llm_budget_reservation SET status = 'released' "
            "WHERE reservation_id = ? AND status = 'reserved' "
            "RETURNING scan_id, estimated_cost",
            (reservation.reservation_id,),
        ).fetchone()
        if row is None:
            conn.execute("ROLLBACK")
            begun = False
            raise ValueError(
                f"reservation {reservation.reservation_id!r} is not reserved"
            )
        conn.execute(
            "UPDATE llm_scan_budget SET "
            "calls_reserved = calls_reserved - 1, "
            "estimated_cost_reserved = CAST(estimated_cost_reserved AS NUMERIC) "
            "- CAST(? AS NUMERIC) "
            "WHERE scan_id = ?",
            (row["estimated_cost"], row["scan_id"]),
        )
        conn.execute("COMMIT")
        begun = False
    except Exception:
        if begun:
            conn.execute("ROLLBACK")
        raise


def plan_reduction(
    *,
    unreduced_fits: bool,
    summarized_fits: bool,
    anchors_fit: bool,
    split_shard_fits: tuple[bool, ...],
    call_site: str,
    subject_ref: str,
) -> ReductionDecision:
    """Pure size transitions. Fit flags are injected; this module does not measure."""
    unreduced_fits = _require_bool(unreduced_fits, name="unreduced_fits")
    summarized_fits = _require_bool(summarized_fits, name="summarized_fits")
    anchors_fit = _require_bool(anchors_fit, name="anchors_fit")
    split_shard_fits = _freeze_bool_sequence(
        split_shard_fits, name="split_shard_fits",
    )
    idle = dict(gate_releases=0, reservations=0, invocations=0)
    if unreduced_fits is True:
        return ReductionDecision(
            rung=REDUCTION_NONE,
            fitting_shard_count=1,
            attempted_transformations=(),
            abstention=None,
            **idle,
        )
    if summarized_fits is True:
        return ReductionDecision(
            rung=SUMMARIZED_FACTS,
            fitting_shard_count=1,
            attempted_transformations=(),
            abstention=None,
            **idle,
        )
    if anchors_fit is True:
        return ReductionDecision(
            rung=PRESERVED_ANCHORS,
            fitting_shard_count=1,
            attempted_transformations=(SUMMARIZED_FACTS,),
            abstention=None,
            **idle,
        )
    fitting = sum(1 for fits in split_shard_fits if fits is True)
    if fitting:
        return ReductionDecision(
            rung=SPLIT,
            fitting_shard_count=fitting,
            attempted_transformations=(SUMMARIZED_FACTS, PRESERVED_ANCHORS),
            abstention=None,
            **idle,
        )
    return ReductionDecision(
        rung=DEFERRED,
        fitting_shard_count=0,
        attempted_transformations=(SUMMARIZED_FACTS, PRESERVED_ANCHORS, SPLIT),
        abstention=PreCallAbstention(
            reason=BUDGET_EXHAUSTED,
            call_site=call_site,
            subject_ref=subject_ref,
        ),
        **idle,
    )


def report_for_budget_exhausted(
    *,
    dossier_id: str,
    call_site: str,
    model_id: str,
    prompt_fingerprint: str,
    validator_version: str,
    dossier_builder: str,
) -> GroundingReport:
    return GroundingReport(
        dossier_id=dossier_id,
        call_site=call_site,
        model_id=model_id,
        prompt_fingerprint=prompt_fingerprint,
        validator_version=validator_version,
        citations_total=0,
        citations_resolved=0,
        citations_span_matched=0,
        claims_total=0,
        claims_abstained=0,
        claims_accepted_direct=0,
        claims_accepted_context=0,
        claims_weak=0,
        claims_rejected=0,
        reasons_histogram={BUDGET_EXHAUSTED: 1},
        reduction_rung=DEFERRED,
        release_audit_id=None,
        dossier_builder=dossier_builder,
    )
