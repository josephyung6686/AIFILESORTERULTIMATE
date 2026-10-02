#!/usr/bin/env python3
"""Embedding bake-off protocol skeleton (deep-dives §2 / T-P1-01).

Does not download models. Validates golden-set shape and computes paired
bootstrap CI helper so CI can fail noisy 20-query decisions.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from items.bakeoff import paired_bootstrap_ci, validate_golden  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--golden", type=Path, required=True)
    p.add_argument("--demo-deltas", action="store_true")
    args = p.parse_args(argv)
    stats = validate_golden(args.golden)
    print(json.dumps(stats, indent=2))
    if args.demo_deltas:
        # Toy: show CI API
        mean, lo, hi = paired_bootstrap_ci([0.1] * 50 + [-0.02] * 10)
        print(json.dumps({"mean": mean, "lo": lo, "hi": hi}))
        if lo <= 0:
            print("CI lower bound ≤ 0 — do not declare bake-off winner")
            return 2
    if not stats["ok_for_decision"]:
        print(
            "Golden set too small for bake-off decision "
            "(need ≥100 ZH or ≥100 total). Protocol OK; decision blocked."
        )
        return 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
