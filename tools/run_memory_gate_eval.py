#!/usr/bin/env python3
"""CI: frozen precision eval for memory atoms gate."""
from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument(
        "--golden", type=Path,
        default=ROOT / "tests/fixtures/memory_gate_golden.json")
    p.add_argument(
        "--out", type=Path,
        default=ROOT / "docs/superpowers/measurements/"
        "2026-10-02-memory-gate-eval.json")
    args = p.parse_args(argv)

    from database_agent.db import open_database
    from assistant.memory_v2 import (
        COVERAGE_FLOOR, PRECISION_BAR, evaluate_gate, record_gate,
        atoms_steering_allowed,
    )

    data = json.loads(args.golden.read_text(encoding="utf-8"))
    proposals = [
        {"proposal_id": x["proposal_id"], "willing": x["willing"]}
        for x in data["proposals"]
    ]
    gold = {x["proposal_id"] for x in data["proposals"] if x.get("gold")}
    rules = set(data.get("rules_only_accepted") or [])
    result = evaluate_gate(
        proposals=proposals, gold_accepted=gold, rules_only_accepted=rules)

    with tempfile.TemporaryDirectory() as td:
        conn = open_database(Path(td) / "t.sqlite", scan_roots=[])
        record_gate(conn, result)
        # Without ASSISTANT_ATOMS_STEER=0, passing gate opens steering
        open_steer = atoms_steering_allowed(conn)
        conn.close()

    coverage = 1.0 - result.abstention
    out = {
        "golden": str(args.golden),
        "passed": result.passed,
        "precision": result.precision,
        "abstention": result.abstention,
        "coverage": coverage,
        "rules_only_precision": result.rules_only_precision,
        "n_proposals": result.n_proposals,
        "precision_bar": PRECISION_BAR,
        "coverage_floor": COVERAGE_FLOOR,
        "steering_would_open": open_steer,
        "notes": result.notes,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(out, indent=2))
    if not result.passed:
        print("FAIL: memory gate did not pass on frozen golden", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
