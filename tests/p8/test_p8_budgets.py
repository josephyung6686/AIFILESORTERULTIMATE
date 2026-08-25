"""Scan-scoped call/cost reservations and the fixed reduction ladder."""
from __future__ import annotations

import ast
import inspect
import math
import threading
from decimal import Decimal
from pathlib import Path

import pytest

import llm_harness
from database_agent.db import open_database
from llm_harness.budgets import (
    MAX_CALLS_PER_1000_FILES,
    MAX_ESTIMATED_COST_PER_SCAN,
    BudgetExhausted,
    BudgetReservation,
    BudgetTransactionOpen,
    ScanBudget,
    allowed_calls,
    create_budget_schema,
    plan_reduction,
    release_reservation,
    report_for_budget_exhausted,
    reserve_call,
    settle_call,
)
from llm_harness.records import GroundingReport, PreCallAbstention
from llm_harness.schema import create_llm_schema
from llm_harness.vocabulary import (
    A_FACT,
    BUDGET_EXHAUSTED,
    DEFERRED,
    PRESERVED_ANCHORS,
    REDUCTION_NONE,
    REDUCTION_RUNGS,
    SPLIT,
    SUMMARIZED_FACTS,
)
from p8.conftest import BUDGET_TABLES, TASK3_TABLES

SRC_BUDGETS = Path(__file__).resolve().parents[2] / "src" / "llm_harness" / "budgets.py"


@pytest.fixture()
def budget_conn(p8_conn):
    create_budget_schema(p8_conn)
    return p8_conn


def _budget(*, scan_id: str = "scan-1", files: int = 1000,
            rate: int = 1, cost: str = "10") -> ScanBudget:
    return ScanBudget(
        scan_id=scan_id,
        corpus_file_count=files,
        max_calls_per_1000_files=rate,
        max_estimated_cost=Decimal(cost),
    )


def _tables(conn) -> set[str]:
    return {
        row["name"]
        for row in conn.execute("SELECT name FROM sqlite_master WHERE type = 'table'")
    }


def test_budget_helpers_are_not_on_the_task_1_public_surface():
    assert llm_harness.__all__ == [
        "Dossier",
        "P8Verdict",
        "Refusal",
        "ValidationUnavailable",
        "NeedsConsent",
    ]
    assert "reserve_call" not in llm_harness.__all__
    assert not hasattr(llm_harness, "reserve_call")
    assert not hasattr(llm_harness, "ScanBudget")


def test_metric_names_are_the_design_spellings_and_carry_no_default_values():
    assert MAX_CALLS_PER_1000_FILES == "model.max_calls_per_1000_files"
    assert MAX_ESTIMATED_COST_PER_SCAN == "model.max_estimated_cost_per_scan"
    parameters = inspect.signature(ScanBudget.__init__).parameters
    for name in (
        "scan_id", "corpus_file_count", "max_calls_per_1000_files", "max_estimated_cost",
    ):
        assert parameters[name].default is inspect.Parameter.empty, name


def test_create_budget_schema_is_called_after_create_llm_schema(p8_conn):
    names = _tables(p8_conn)
    assert set(TASK3_TABLES) <= names
    assert not set(BUDGET_TABLES) & names
    create_budget_schema(p8_conn)
    create_budget_schema(p8_conn)
    names = _tables(p8_conn)
    assert set(BUDGET_TABLES) <= names


def test_budget_schema_lives_in_budgets_not_schema():
    from llm_harness import schema as schema_mod
    assert not hasattr(schema_mod, "create_budget_schema")
    source = Path(schema_mod.__file__).read_text()
    assert "llm_scan_budget" not in source or "belong wholly to Task 4" in source
    assert "CREATE TABLE IF NOT EXISTS llm_scan_budget" not in source


@pytest.mark.parametrize("files,rate,expected", (
    (0, 1, 0),
    (1, 1, 0),
    (999, 1, 0),
    (1000, 1, 1),
    (1001, 1, 1),
))
def test_allowed_calls_are_floor_of_files_times_rate_over_1000(files, rate, expected):
    budget = _budget(files=files, rate=rate)
    assert allowed_calls(budget) == expected
    assert allowed_calls(budget) == math.floor(files * rate / 1000)


def test_exact_boundary_accepts_the_last_allowed_call(budget_conn):
    budget = _budget(files=1000, rate=1, cost="10")
    first = reserve_call(budget_conn, budget, estimated_cost=Decimal("1"))
    assert isinstance(first, BudgetReservation)
    assert first.scan_id == "scan-1"
    row = budget_conn.execute(
        "SELECT calls_reserved FROM llm_scan_budget WHERE scan_id = ?",
        ("scan-1",),
    ).fetchone()
    assert row["calls_reserved"] == 1


def test_one_over_the_call_ceiling_is_refused(budget_conn):
    budget = _budget(files=1000, rate=1, cost="10")
    reserve_call(budget_conn, budget, estimated_cost=Decimal("1"))
    with pytest.raises(BudgetExhausted):
        reserve_call(budget_conn, budget, estimated_cost=Decimal("1"))
    count = budget_conn.execute(
        "SELECT count(*) AS c FROM llm_budget_reservation",
    ).fetchone()["c"]
    assert count == 1


def test_zero_files_refuse_the_first_call(budget_conn):
    budget = _budget(files=0, rate=1, cost="10")
    with pytest.raises(BudgetExhausted):
        reserve_call(budget_conn, budget, estimated_cost=Decimal("1"))


@pytest.mark.parametrize("files", (1, 999))
def test_sub_thousand_corpora_at_rate_one_have_no_calls(budget_conn, files):
    budget = _budget(files=files, rate=1, cost="10")
    with pytest.raises(BudgetExhausted):
        reserve_call(budget_conn, budget, estimated_cost=Decimal("1"))


def test_one_thousand_one_files_at_rate_one_allows_exactly_one_call(budget_conn):
    budget = _budget(files=1001, rate=1, cost="10")
    reserve_call(budget_conn, budget, estimated_cost=Decimal("1"))
    with pytest.raises(BudgetExhausted):
        reserve_call(budget_conn, budget, estimated_cost=Decimal("1"))


def test_estimated_cost_equality_is_accepted_and_overflow_is_refused(budget_conn):
    budget = _budget(files=10000, rate=1, cost="5")
    reserve_call(budget_conn, budget, estimated_cost=Decimal("5"))
    with pytest.raises(BudgetExhausted):
        reserve_call(budget_conn, budget, estimated_cost=Decimal("0.01"))


def test_cost_overflow_on_the_first_call_is_refused(budget_conn):
    budget = _budget(files=1000, rate=1, cost="5")
    with pytest.raises(BudgetExhausted):
        reserve_call(budget_conn, budget, estimated_cost=Decimal("5.01"))


def test_release_rolls_back_a_reservation_after_a_pre_transport_failure(budget_conn):
    budget = _budget(files=1000, rate=1, cost="10")
    reservation = reserve_call(budget_conn, budget, estimated_cost=Decimal("3"))
    release_reservation(budget_conn, reservation)
    row = budget_conn.execute(
        "SELECT calls_reserved, estimated_cost_reserved FROM llm_scan_budget "
        "WHERE scan_id = ?",
        ("scan-1",),
    ).fetchone()
    assert row["calls_reserved"] == 0
    assert Decimal(str(row["estimated_cost_reserved"])) == Decimal("0")
    status = budget_conn.execute(
        "SELECT status FROM llm_budget_reservation WHERE reservation_id = ?",
        (reservation.reservation_id,),
    ).fetchone()["status"]
    assert status == "released"
    again = reserve_call(budget_conn, budget, estimated_cost=Decimal("3"))
    assert again.reservation_id != reservation.reservation_id


def test_settle_call_records_actual_cost_and_keeps_the_slot(budget_conn):
    budget = _budget(files=1000, rate=1, cost="10")
    reservation = reserve_call(budget_conn, budget, estimated_cost=Decimal("3"))
    settled = settle_call(budget_conn, reservation, actual_cost=Decimal("2.50"))
    assert settled.actual_cost == Decimal("2.50")
    row = budget_conn.execute(
        "SELECT actual_cost, status FROM llm_budget_reservation "
        "WHERE reservation_id = ?",
        (reservation.reservation_id,),
    ).fetchone()
    assert Decimal(row["actual_cost"]) == Decimal("2.50")
    assert row["status"] == "settled"
    counters = budget_conn.execute(
        "SELECT calls_reserved FROM llm_scan_budget WHERE scan_id = ?",
        ("scan-1",),
    ).fetchone()
    assert counters["calls_reserved"] == 1
    with pytest.raises(BudgetExhausted):
        reserve_call(budget_conn, budget, estimated_cost=Decimal("1"))


def test_reserve_call_rejects_an_already_open_transaction(budget_conn):
    budget_conn.execute("BEGIN")
    try:
        with pytest.raises(BudgetTransactionOpen):
            reserve_call(budget_conn, _budget(), estimated_cost=Decimal("1"))
    finally:
        budget_conn.execute("ROLLBACK")


def test_two_connections_race_the_final_slot_and_exactly_one_succeeds(tmp_path):
    path = tmp_path / "race.sqlite"
    setup = open_database(path)
    create_llm_schema(setup)
    create_budget_schema(setup)
    setup.close()
    budget = _budget(files=1000, rate=1, cost="10")
    barrier = threading.Barrier(2)
    outcomes: list[object] = []
    lock = threading.Lock()

    def worker():
        # Live open_database connections are thread-affine; each racer opens its own.
        connection = open_database(path)
        connection.execute("PRAGMA busy_timeout = 5000")
        try:
            barrier.wait()
            try:
                result: object = reserve_call(
                    connection, budget, estimated_cost=Decimal("1"),
                )
            except BudgetExhausted as exc:
                result = exc
            with lock:
                outcomes.append(result)
        finally:
            connection.close()

    threads = [threading.Thread(target=worker), threading.Thread(target=worker)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    won = [item for item in outcomes if isinstance(item, BudgetReservation)]
    lost = [item for item in outcomes if isinstance(item, BudgetExhausted)]
    assert len(won) == 1
    assert len(lost) == 1
    inspect = open_database(path)
    try:
        counters = inspect.execute(
            "SELECT calls_reserved FROM llm_scan_budget WHERE scan_id = ?",
            ("scan-1",),
        ).fetchone()
        assert counters["calls_reserved"] == 1
        details = inspect.execute(
            "SELECT count(*) AS c FROM llm_budget_reservation WHERE status = 'reserved'",
        ).fetchone()["c"]
        assert details == 1
        assert inspect.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
    finally:
        inspect.close()


def test_reduction_rungs_are_none_then_summarized_then_anchors_then_split_then_deferred():
    assert REDUCTION_RUNGS == (
        REDUCTION_NONE, SUMMARIZED_FACTS, PRESERVED_ANCHORS, SPLIT, DEFERRED,
    )


def test_none_records_an_unreduced_fitting_request_and_is_not_a_transformation():
    decision = plan_reduction(
        unreduced_fits=True,
        summarized_fits=False,
        anchors_fit=False,
        split_shard_fits=(),
        call_site=A_FACT,
        subject_ref="file-1",
    )
    assert decision.rung == REDUCTION_NONE
    assert decision.fitting_shard_count == 1
    assert decision.attempted_transformations == ()
    assert decision.gate_releases == 0
    assert decision.reservations == 0
    assert decision.invocations == 0
    assert decision.abstention is None


def test_oversized_summarization_and_anchors_spend_nothing():
    decision = plan_reduction(
        unreduced_fits=False,
        summarized_fits=False,
        anchors_fit=False,
        split_shard_fits=(True, True),
        call_site=A_FACT,
        subject_ref="file-1",
    )
    assert decision.rung == SPLIT
    assert decision.fitting_shard_count == 2
    assert decision.attempted_transformations == (
        SUMMARIZED_FACTS, PRESERVED_ANCHORS,
    )
    assert decision.gate_releases == 0
    assert decision.reservations == 0
    assert decision.invocations == 0
    assert decision.abstention is None


def test_each_fitting_split_shard_may_take_its_own_reservation(budget_conn):
    decision = plan_reduction(
        unreduced_fits=False,
        summarized_fits=False,
        anchors_fit=False,
        split_shard_fits=(True, False, True),
        call_site=A_FACT,
        subject_ref="file-1",
    )
    assert decision.rung == SPLIT
    assert decision.fitting_shard_count == 2
    budget = _budget(files=3000, rate=1, cost="10")
    first = reserve_call(budget_conn, budget, estimated_cost=Decimal("1"))
    second = reserve_call(budget_conn, budget, estimated_cost=Decimal("1"))
    assert first.reservation_id != second.reservation_id
    assert budget_conn.execute(
        "SELECT calls_reserved FROM llm_scan_budget WHERE scan_id = ?",
        ("scan-1",),
    ).fetchone()["calls_reserved"] == 2


def test_deferred_yields_budget_exhausted_a_zero_count_report_and_no_call():
    decision = plan_reduction(
        unreduced_fits=False,
        summarized_fits=False,
        anchors_fit=False,
        split_shard_fits=(False, False),
        call_site=A_FACT,
        subject_ref="file-1",
    )
    assert decision.rung == DEFERRED
    assert decision.fitting_shard_count == 0
    assert decision.gate_releases == 0
    assert decision.reservations == 0
    assert decision.invocations == 0
    assert isinstance(decision.abstention, PreCallAbstention)
    assert decision.abstention.reason == BUDGET_EXHAUSTED
    report = report_for_budget_exhausted(
        dossier_id="dossier-1",
        call_site=A_FACT,
        model_id="fixture-model",
        prompt_fingerprint="fp-canonical",
        validator_version="P8/0.1.0",
        dossier_builder="fixture",
    )
    assert isinstance(report, GroundingReport)
    assert report.release_audit_id is None
    assert report.reduction_rung == DEFERRED
    assert report.citations_total == 0
    assert report.citations_resolved == 0
    assert report.citations_span_matched == 0
    assert report.claims_total == 0
    assert report.claims_abstained == 0
    assert report.claims_accepted_direct == 0
    assert report.claims_accepted_context == 0
    assert report.claims_weak == 0
    assert report.claims_rejected == 0
    assert dict(report.reasons_histogram) == {BUDGET_EXHAUSTED: 1}


def test_summarized_facts_that_fit_are_still_pre_egress_until_the_caller_reserves():
    decision = plan_reduction(
        unreduced_fits=False,
        summarized_fits=True,
        anchors_fit=True,
        split_shard_fits=(True,),
        call_site=A_FACT,
        subject_ref="file-1",
    )
    assert decision.rung == SUMMARIZED_FACTS
    assert decision.fitting_shard_count == 1
    assert decision.gate_releases == 0
    assert decision.reservations == 0
    assert decision.invocations == 0


def test_preserved_anchors_that_fit_skip_split():
    decision = plan_reduction(
        unreduced_fits=False,
        summarized_fits=False,
        anchors_fit=True,
        split_shard_fits=(True, True),
        call_site=A_FACT,
        subject_ref="file-1",
    )
    assert decision.rung == PRESERVED_ANCHORS
    assert decision.fitting_shard_count == 1
    assert decision.attempted_transformations == (SUMMARIZED_FACTS,)


@pytest.mark.parametrize("cost", (
    Decimal("Infinity"),
    Decimal("-Infinity"),
    Decimal("NaN"),
))
def test_reserve_call_rejects_non_finite_estimated_cost(budget_conn, cost):
    budget = _budget(files=1000, rate=1, cost="10")
    with pytest.raises(ValueError):
        reserve_call(budget_conn, budget, estimated_cost=cost)
    row = budget_conn.execute(
        "SELECT count(*) AS c FROM llm_scan_budget",
    ).fetchone()
    assert row["c"] == 0
    details = budget_conn.execute(
        "SELECT count(*) AS c FROM llm_budget_reservation",
    ).fetchone()
    assert details["c"] == 0


def test_plan_reduction_rejects_a_bare_string_as_split_shard_fits():
    with pytest.raises(ValueError):
        plan_reduction(
            unreduced_fits=False,
            summarized_fits=False,
            anchors_fit=False,
            split_shard_fits="yes",
            call_site=A_FACT,
            subject_ref="file-1",
        )


def test_plan_reduction_rejects_a_truthy_string_as_unreduced_fits():
    with pytest.raises(ValueError):
        plan_reduction(
            unreduced_fits="no",
            summarized_fits=False,
            anchors_fit=False,
            split_shard_fits=(),
            call_site=A_FACT,
            subject_ref="file-1",
        )


def test_budgets_contain_no_client_prompt_or_default_ceiling():
    tree = ast.parse(SRC_BUDGETS.read_text())
    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(alias.name.split(".", 1)[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module.split(".", 1)[0])
    assert "privacy" not in imported
    source = SRC_BUDGETS.read_text()
    assert "ModelClient" not in source
    assert "def normalize(" not in source
    assert "def contradicts(" not in source
    assert "4000" not in source
