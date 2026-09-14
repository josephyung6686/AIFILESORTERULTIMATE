"""`00` amendment 7(c): the gate and the situation site ask EVERY file, so each
one's purse is the roster and never the observe sites' 200-call ceiling.

Measured 12 Sep 2026 on the owner's 371 files: with the 200 ceiling the gate
refused the last 106 askable files before any call, in every run, and the four
health forms the amendment exists to catch sat among them.
"""
from __future__ import annotations

from decimal import Decimal

import pytest

import cli
from llm_harness.budgets import ScanBudget, allowed_calls


def _fact(files: int) -> ScanBudget:
    return ScanBudget(
        scan_id="scan-1", corpus_file_count=files,
        max_calls_per_1000_files=cli.OBSERVE_CALLS_PER_1000_FILES,
        max_estimated_cost=cli.OBSERVE_CALLS_PER_SCAN_CEILING,
        min_calls_per_scan=cli.OBSERVE_MIN_CALLS_PER_SCAN)


def test_the_gates_ceiling_is_the_roster_and_one_call_per_file_fits_under_it():
    budget = cli.gate_scan_budget(_fact(371), corpus_file_count=371)
    assert budget.max_estimated_cost == Decimal(371)
    assert allowed_calls(budget) == 371
    assert budget.max_estimated_cost > cli.OBSERVE_CALLS_PER_SCAN_CEILING


def test_site_gs_ceiling_is_the_roster_twice_because_it_asks_twice():
    """`00` amendment 1 of 14 Sep: site G asks which KIND a file is and then,
    where the kind carries several situations and nothing has told them apart,
    which SITUATION -- so the number of questions it asks about a roster is two
    per file and its purse is sized by that.

    The rate and the ceiling move together, because a ceiling below what the rate
    allows un-asks the roster's tail exactly as the 200-call ceiling did in the
    measurement this file's docstring records. Measured one stage down: left at
    one per file, the six-file corpus of `tests/integration/test_each_file_is_
    filed_under_its_own_situation.py` lost the third research file's kind row.

    SABOTAGE: drop the doubling in `situation_scan_budget` and that corpus's last
    file is never asked what it is, which reads on the screen as a model that
    declined.
    """
    budget = cli.situation_scan_budget(_fact(371), corpus_file_count=371)
    assert budget.max_estimated_cost == Decimal(742)
    assert allowed_calls(budget) == 742
    assert budget.max_estimated_cost > cli.OBSERVE_CALLS_PER_SCAN_CEILING


@pytest.mark.parametrize("ledger", [cli.gate_scan_budget, cli.situation_scan_budget])
def test_an_empty_roster_keeps_the_floor(ledger):
    budget = ledger(_fact(0), corpus_file_count=0)
    assert budget.max_estimated_cost == Decimal(cli.OBSERVE_MIN_CALLS_PER_SCAN)


def test_site_as_purse_is_the_roster_too_and_keeps_the_floor_on_a_small_folder():
    """13 Sep 2026: the fact pass asks every gate-cleared file once, and its
    200-call ceiling deferred the last 35 of the owner's 371 files before any
    call. The roster is the ceiling; 200 stays as the floor for a small folder."""
    assert cli.fact_scan_budget("scan", corpus_file_count=371).max_estimated_cost == Decimal(371)
    assert cli.fact_scan_budget("scan", corpus_file_count=12).max_estimated_cost == Decimal(200)
