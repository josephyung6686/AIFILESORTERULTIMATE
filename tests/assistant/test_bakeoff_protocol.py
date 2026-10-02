"""Bake-off protocol: CI helper rejects noisy small-N decisions."""
from __future__ import annotations

from pathlib import Path

from items.bakeoff import paired_bootstrap_ci, validate_golden


def test_bootstrap_ci_and_stub_golden():
    mean, lo, hi = paired_bootstrap_ci([0.2] * 80 + [0.0] * 20, seed=1)
    assert hi >= mean >= lo
    # Clear positive lift → lo > 0
    mean2, lo2, hi2 = paired_bootstrap_ci([0.15] * 100, seed=2)
    assert lo2 > 0
    stub = Path("tests/fixtures/bakeoff_golden_stub.json")
    stats = validate_golden(stub)
    assert stats["n_zh"] >= 2
    assert stats["ok_for_decision"] is False  # stub too small — correct


def test_100zh_size_fixture_passes_sample_gate():
    path = Path("tests/fixtures/bakeoff_golden_100zh.json")
    stats = validate_golden(path)
    assert stats["n_zh"] >= 100
    assert stats["ok_for_decision"] is True
    # Still synthetic — winner requires labeled relevant_item_ids (manual)
