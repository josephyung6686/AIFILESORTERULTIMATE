# tools/gate_lives.py -- `106` §D, the "fewer than sixteen" gate. Prints
# numbers, names no file. Read-only. Run from the repository root with
# `GRAPH_AGENT_NO_DOTENV=1 python3 tools/gate_lives.py <run.sqlite>` AFTER the
# sort run has finished.
#
# **THE GATE REPORTS AND ASSERTS TWO NUMBERS, NOT ONE.** The first draft counted
# lives only, and on the owner's corpus it passed with ONE life while 218 of 257
# files reached none -- a failure wearing a pass, exactly the narrow-versus-
# broken case the gate exists to tell apart. So beside "how many lives" it now
# reports "how many files reached one", and a run where a file with a situation
# fact reached no life has failed however few lives it emitted.
#
# A file's life is resolved the way `branch_situation.partition_by_branch`
# resolves it: the situation fact's row (`life_of`) where the fact is a
# situation, else the KIND's own word (`life_of_kind`) where the fact holds the
# kind -- which on the owner's corpus is most of them (`104` §18.108).
from __future__ import annotations

import sqlite3
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from facts.domains import SCHEMA_IDS  # noqa: E402
from facts.llm_seam import SITUATION_FIELD  # noqa: E402
from facts.supersede import preferred_fact  # noqa: E402
from production import (  # noqa: E402
    life_of, life_of_kind, load_shipped_catalogue, read_packaged_library_file,
    shipped_situations,
)


def life_of_value(catalogue, value: str) -> str | None:
    """The life a `situation` fact's value reaches: the situation's row, else
    the kind's word. `None` for a value the library places nowhere."""
    if value in SCHEMA_IDS:
        return life_of_kind(catalogue, value)
    if value in {row.name for row in shipped_situations(catalogue)}:
        return life_of(catalogue, value)
    return None


def measure(conn: sqlite3.Connection, catalogue) -> dict:
    value_of = {r["value_id"]: r["canonical_value"] for r in conn.execute(
        'select value_id, canonical_value from "values" where field_key = ?',
        (SITUATION_FIELD,))}
    roster = [r["file_id"] for r in conn.execute("select file_id from files")]
    lives_in_facts: Counter = Counter()
    unmapped: Counter = Counter()
    no_fact = 0
    for file_id in roster:
        fact = preferred_fact(conn, file_id=file_id, field_key=SITUATION_FIELD)
        if fact is None:
            no_fact += 1
            continue
        value = value_of.get(fact["value_id"], "")
        life = life_of_value(catalogue, value)
        if life is None:
            unmapped[value] += 1
        else:
            lives_in_facts[life] += 1
    plan = conn.execute(
        "select plan_version_id from frozen_trees order by created_at desc limit 1"
    ).fetchone()
    roots = [] if plan is None else [r["display_label"] for r in conn.execute(
        "select display_label from tree_nodes where plan_version_id = ? and "
        "parent_node_id is null and node_type = 'proposed' order by ordinal",
        (plan[0],))]
    shipped_lives = ({row.life for row in catalogue.applicabilities.values()
                      if row.life} | set(catalogue.schema_lives.values()))
    decided = 0 if plan is None else conn.execute(
        "select count(distinct subject_ref) from placement_decisions "
        "where plan_version = ? and superseded_by is null", (plan[0],)).fetchone()[0]
    return {"files": len(roster), "with_fact": len(roster) - no_fact,
            "reached": sum(lives_in_facts.values()), "unmapped": unmapped,
            "lives": lives_in_facts, "roots": roots,
            "life_roots": [r for r in roots if r in shipped_lives],
            "shipped_lives": shipped_lives, "decided": decided}


def failures_of(m: dict) -> list[str]:
    """THE GATE, falsifiable in both directions AND on both numbers.

    `m` is `measure`'s dict. Pure, so `tests/tools/test_gate_lives.py` can pin
    the verdict on hand-built numbers -- the first draft's "fewer than sixteen"
    had no pin and passed the owner's corpus with one life and 218 files in
    none (`00` amendment 18).
    """
    failures = []
    if not 0 < len(m["life_roots"]) < 16:
        failures.append("no life root, or the sixteen-folder skeleton")
    if not set(m["life_roots"]) <= set(m["lives"]):
        failures.append("a root no file's situation supports (an empty Vehicles/)")
    if m["reached"] != m["with_fact"]:
        failures.append(f"{m['with_fact'] - m['reached']} of {m['with_fact']} files "
                        "with a situation fact reached NO life -- however few lives "
                        "were emitted, this run has failed")
    if m["decided"] != m["files"]:
        failures.append("a file with no placement decision at all")
    return failures


def main(db: str) -> int:
    conn = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    catalogue = load_shipped_catalogue(read_packaged_library_file)
    m = measure(conn, catalogue)
    print(f"files {m['files']}  with a situation fact {m['with_fact']}  "
          f"reached a life {m['reached']}  reached none {sum(m['unmapped'].values())}")
    print(f"lives the facts name: {len(m['lives'])} of {len(m['shipped_lives'])} "
          "shipped -> " + ", ".join(f"{life} {n}" for life, n in m["lives"].most_common()))
    if m["unmapped"]:
        print("values that reached no life: " + ", ".join(
            f"{value or '<empty>'} {n}" for value, n in m["unmapped"].most_common()))
    print(f"proposed roots: {len(m['roots'])}; of them lives: {len(m['life_roots'])} "
          f"-> {m['life_roots']}")
    print(f"files with a current placement decision: {m['decided']} of {m['files']}")
    failures = failures_of(m)
    for failure in failures:
        print("GATE FAILED:", failure)
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
