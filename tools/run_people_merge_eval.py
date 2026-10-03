#!/usr/bin/env python3
"""CI: labeled people merge precision eval."""
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
        default=ROOT / "tests/fixtures/people_merge_eval.json")
    p.add_argument(
        "--out", type=Path,
        default=ROOT / "docs/superpowers/measurements/"
        "2026-10-02-people-merge-eval.json")
    args = p.parse_args(argv)

    from database_agent.db import open_database
    from items.people import merge_candidates, merge_precision, mint_person
    from items.schema import create_items_schema

    data = json.loads(args.golden.read_text(encoding="utf-8"))
    with tempfile.TemporaryDirectory() as td:
        conn = open_database(Path(td) / "t.sqlite", scan_roots=[])
        create_items_schema(conn)
        key_to_id = {}
        for person in data["people"]:
            pitem = mint_person(
                conn,
                display_label=person["label"],
                email=person.get("email"),
            )
            key_to_id[person["key"]] = pitem.item_id
        gold = {
            tuple(sorted((key_to_id[a], key_to_id[b])))
            for a, b in data["gold_merges"]
        }
        cands = merge_candidates(conn)
        if data.get("score_blocking") == "label":
            cands = [c for c in cands if c.blocking_key.startswith("label:")]
        metrics = merge_precision(cands, gold)
        conn.close()

    bar = float(data.get("precision_bar") or 0.95)
    out = {
        "golden": str(args.golden),
        "precision": metrics["precision"],
        "n_pred": metrics["n_pred"],
        "n_tp": metrics["n_tp"],
        "n_gold": len(gold),
        "precision_bar": bar,
        "passed": metrics["precision"] >= bar and metrics["n_tp"] >= len(gold),
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(out, indent=2))
    if not out["passed"]:
        print("FAIL: people merge precision below bar", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
