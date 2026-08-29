#!/usr/bin/env python3
"""Mechanical half of the 2026-08-26 edge repair. Deterministic renames only.

WHAT THIS FIXES (no judgement required — the argument text already exists, only the key is wrong):
  * `why`       -> `signal`     on collides_with entries   (_CONTRACT.md's shape is
                                 {"domain", "signal", "design_cite"})
  * `domain_id` -> `domain`     on collides_with / also_holds_with entries
  * `id`/`target` -> `domain`   same reason

WHAT THIS DELIBERATELY DOES NOT FIX (judgement — R1c, `planning/prompts/01c-merge-and-gate.md`):
  * one-way collides_with / also_holds_with — deciding whether B should name A back, or whether
    the edge is legitimately one-way with a `one_way_reason`, is a design call per pair.
  * also_holds_with on a template — must be LIFTED to the schema pair or CONVERTED to
    collides_with, depending on what the row meant. Guessing would destroy the distinction
    CONNECTION §5 exists to protect.
  * cross-kind collides_with — same: lift to the schema pair or push down to the template pair.
  * genuine overlaps (creative film-production/shoot-day-media/post-production;
    finance.household-property vs construction_property) — these need a boundary argued, not a key.

SAFETY
  * Refuses to run while any node file has been modified in the last 120s (an agent may still be
    writing it). Override with --force only when every dispatch has returned.
  * --dry-run (default) prints the diff summary and writes nothing.
  * --apply rewrites files in place, preserving key order and 2-space indent.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import time
from collections import OrderedDict, defaultdict

HERE = pathlib.Path(__file__).resolve().parent
NODES = HERE / "nodes"
EDGES = ("collides_with", "also_holds_with")
TARGET_ALIASES = ("domain_id", "id", "target")
SIGNAL_ALIASES = ("why", "discriminator")


def repair_entry(e: dict) -> tuple[dict, list[str]]:
    """Return (possibly rewritten entry, list of changes). Key order is preserved."""
    changes = []
    out = OrderedDict()
    for k, v in e.items():
        if k in TARGET_ALIASES and "domain" not in e:
            out["domain"] = v
            changes.append(f"{k}->domain")
        elif k in SIGNAL_ALIASES and "signal" not in e:
            out["signal"] = v
            changes.append(f"{k}->signal")
        else:
            out[k] = v
    return out, changes


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="write changes (default is dry-run)")
    ap.add_argument("--force", action="store_true", help="run even if files were touched recently")
    args = ap.parse_args()

    now = time.time()
    fresh = [p.name for p in NODES.glob("*.json") if now - p.stat().st_mtime < 120]
    if fresh and not args.force:
        print(f"REFUSING: {len(fresh)} node file(s) modified in the last 120s — agents may still be "
              f"writing (e.g. {fresh[:3]}). Re-run when every dispatch has returned, or --force.")
        return 2

    per_file = defaultdict(list)
    for p in sorted(NODES.glob("*.json")):
        try:
            d = json.loads(p.read_text(), object_pairs_hook=OrderedDict)
        except Exception as exc:
            print(f"  SKIP unparseable {p.name}: {exc}")
            continue
        touched = False
        for edge in EDGES:
            entries = d.get(edge)
            if not isinstance(entries, list):
                continue
            new_entries = []
            for e in entries:
                if isinstance(e, dict):
                    fixed, changes = repair_entry(e)
                    if changes:
                        per_file[p.name].extend(changes)
                        touched = True
                    new_entries.append(fixed)
                else:
                    new_entries.append(e)
            d[edge] = new_entries
        if touched and args.apply:
            p.write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n")

    total = sum(len(v) for v in per_file.values())
    kinds = defaultdict(int)
    for v in per_file.values():
        for c in v:
            kinds[c] += 1
    print(f"{'APPLIED' if args.apply else 'DRY RUN'}: {total} key repairs across {len(per_file)} files")
    for k, n in sorted(kinds.items(), key=lambda kv: -kv[1]):
        print(f"  {k}: {n}")
    if not args.apply and total:
        print("\nRe-run with --apply once every dispatch has returned, then:")
        print("  python3 planning/domains/check_edges.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
