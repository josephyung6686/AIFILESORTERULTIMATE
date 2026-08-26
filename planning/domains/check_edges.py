#!/usr/bin/env python3
"""Edge-invariant gate for planning/domains/nodes/ — the checks CONNECTION.md §5 states
and check.py does not yet enforce (check.py does not scan nodes/ at all; that is R1c's).

Found by the 2026-08-26 audit, which returned FAIL on both auditors:
  1. collides_with entries with a null/empty `signal` — §5 makes the signal mandatory
     ("Must carry `signal`: the discriminating evidence"). P6 activation step 3 and P8's
     validator read it to decide which side an evidence item counts toward; null is
     uninterpretable.
  2. collides_with joining mismatched kinds — §5: "schema <-> schema, or template <-> template
     (same kind only)". A schema-level mutex and a template-level mutex mean different things.
  3. also_holds_with on a template — §5 restricts it to "schema <-> schema only".
  4. one-way collides_with / also_holds_with without a recorded one_way_reason — §5 marks both
     reciprocal-required.

Run:  python3 planning/domains/check_edges.py [--json]
Exit: 0 clean, 1 findings.
"""
from __future__ import annotations

import json
import pathlib
import sys
from collections import defaultdict

HERE = pathlib.Path(__file__).resolve().parent
NODES = HERE / "nodes"
ROSTER = HERE / "roster.json"


# The corpus spells these three ways (2026-08-26 audit): target as `domain` | `domain_id` | `id`
# | `target`, discriminator as `signal` | `why`. Normalising the read here is not blessing the
# drift — KEY_DRIFT below reports it, and R1c should pick one spelling for the whole forest.
TARGET_KEYS = ("domain", "domain_id", "id", "target")
SIGNAL_KEYS = ("signal", "why", "discriminator")


def _edge_ids(entry, key):
    """Yield (id, signal, one_way_reason, target_key, signal_key)."""
    for e in entry.get(key) or []:
        if isinstance(e, dict):
            tk = next((k for k in TARGET_KEYS if e.get(k)), None)
            sk = next((k for k in SIGNAL_KEYS if (e.get(k) or "").strip()), None)
            yield (e.get(tk) if tk else None, e.get(sk) if sk else None,
                   e.get("one_way_reason"), tk, sk)
        else:
            yield (e, None, None, "bare-string", None)


def main() -> int:
    roster = json.loads(ROSTER.read_text())
    rows = roster["nodes"] if isinstance(roster, dict) else roster
    kind_of = {r["domain_id"]: r.get("kind") for r in rows}

    nodes = {}
    for p in sorted(NODES.glob("*.json")):
        try:
            nodes[p.stem] = json.loads(p.read_text())
        except Exception as exc:  # a malformed row is check.py's finding, not ours
            print(f"  UNPARSEABLE {p.name}: {exc}")

    findings = defaultdict(list)
    declared = {"collides_with": defaultdict(set), "also_holds_with": defaultdict(set)}

    for nid, d in nodes.items():
        my_kind = d.get("kind") or kind_of.get(nid)
        for edge in ("collides_with", "also_holds_with"):
            for tid, signal, one_way, tkey, skey in _edge_ids(d, edge):
                if tkey and tkey != "domain":
                    findings["KEY_DRIFT_target"].append(f"{nid}.{edge}: uses {tkey!r} not 'domain' (_CONTRACT.md shape)")
                if skey and skey != "signal":
                    findings["KEY_DRIFT_signal"].append(f"{nid}.{edge}: uses {skey!r} not 'signal'")
                if not isinstance(tid, str):
                    continue
                declared[edge][nid].add(tid)
                their_kind = kind_of.get(tid)
                if edge == "collides_with":
                    if not (signal or "").strip():
                        findings["collides_signal_missing"].append(f"{nid} -> {tid}")
                    if their_kind and my_kind and their_kind != my_kind:
                        findings["collides_kind_mismatch"].append(
                            f"{nid}({my_kind}) -> {tid}({their_kind})")
                else:
                    if my_kind == "template":
                        findings["also_holds_on_template"].append(f"{nid}(template) -> {tid}")
                    elif their_kind == "template":
                        findings["also_holds_target_template"].append(f"{nid} -> {tid}(template)")

    # reciprocity: only judged where BOTH rows are on disk (a row not yet written is owed, not one-way)
    for edge in ("collides_with", "also_holds_with"):
        for nid, targets in declared[edge].items():
            for tid in targets:
                if tid not in nodes:
                    continue
                if nid not in declared[edge].get(tid, set()):
                    reason = next((e[2] for e in _edge_ids(nodes[nid], edge)
                                   if e[0] == tid and e[2]), None)
                    if not reason:
                        findings[f"{edge}_one_way"].append(f"{nid} -> {tid} (no reciprocal, no one_way_reason)")

    total = sum(len(v) for v in findings.values())
    if "--json" in sys.argv:
        print(json.dumps({k: sorted(v) for k, v in findings.items()}, indent=2))
    else:
        print(f"edge gate: {len(nodes)} node files")
        for k, v in sorted(findings.items()):
            by_row = defaultdict(int)
            for item in v:
                by_row[item.split(" ")[0]] += 1
            worst = sorted(by_row.items(), key=lambda kv: -kv[1])[:6]
            print(f"  {k}: {len(v)} across {len(by_row)} rows — worst: {worst}")
        print(f"  TOTAL: {total}")
    return 1 if total else 0


if __name__ == "__main__":
    raise SystemExit(main())
