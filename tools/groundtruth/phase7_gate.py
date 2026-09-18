"""`106` Phase 7's gate over one run database. Aggregates only.

Usage: python3 tools/groundtruth/phase7_gate.py ~/.graph-agent/lead/corpus2-gate1/runNN.sqlite

Read-only. Prints counts and never a path, a filename, a folder name or a label
from the corpus. Four numbers, `106` Phase 7 §F:

1. the depth histogram `{depth: folders}` of the latest frozen tree, and the
   count of single-child runs that never divide (Task 7.3 folds these; must be 0);
2. single-file roots (must be 0) -- an `existing` root whose directory holds one
   file and no subdirectory in the latest scan;
3. ordinary review sets whose offered home is not a residual node of the tree
   (must be 0); protected sets are counted and offered nothing;
4. nothing moved -- not measurable here; `tests/integration`'s `_on_disk`
   comparison is the check, and this script does not touch the corpus.

THE DEPTH HALF IS OBSERVABLE ONLY AFTER PHASE 6'S GATE IS MET (`106` Phase 7 §G):
before the fact producers fill more levels the histogram is nearly flat and the
single-run count is trivially 0. The screen says so.

Which version is "the" tree is passed in by nobody, so it is the LATEST FROZEN
one; the tie among versions written in one second is broken by row order and
never by the id, whose suffix is a counter and not a number to sort on (`104`
§18.111; `tree_design.store.latest_plan_version` breaks the same tie the same way).
"""
from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

LATEST_FROZEN = (
    "SELECT plan_version_id FROM plan_versions WHERE state = 'frozen' "
    "ORDER BY created_at DESC, rowid DESC LIMIT 1")

DEPTH = """
WITH RECURSIVE walk(node_id, depth) AS (
    SELECT node_id, 0 FROM tree_nodes WHERE plan_version_id = :v AND parent_node_id IS NULL
    UNION ALL
    SELECT n.node_id, w.depth + 1 FROM tree_nodes n JOIN walk w ON n.parent_node_id = w.node_id
    WHERE n.plan_version_id = :v)
SELECT depth, COUNT(*) FROM walk GROUP BY depth ORDER BY depth
"""

#: A node with exactly one child whose child has no children -- the shape Task
#: 7.3 folds. Beneath the root only: the branch root is where the rule stops.
SINGLE_RUNS = """
WITH kids AS (SELECT parent_node_id AS p, COUNT(*) AS n FROM tree_nodes
              WHERE plan_version_id = :v AND parent_node_id IS NOT NULL
              GROUP BY parent_node_id)
SELECT COUNT(*) FROM tree_nodes n
JOIN kids ON kids.p = n.node_id AND kids.n = 1
JOIN tree_nodes c ON c.parent_node_id = n.node_id AND c.plan_version_id = :v
LEFT JOIN kids gk ON gk.p = c.node_id
WHERE n.plan_version_id = :v AND n.parent_node_id IS NOT NULL AND gk.n IS NULL
"""

SINGLE_FILE_ROOTS = """
SELECT COUNT(*) FROM tree_nodes n
JOIN directory_inventory d
  ON d.directory_path = n.existing_path
 -- the LATEST scan only: a database rescanned holds one inventory row per scan
 -- per directory, and joining them all would count each root once per scan
 AND d.scan_run_id = (SELECT scan_run_id FROM scan_runs ORDER BY rowid DESC LIMIT 1)
WHERE n.plan_version_id = :v AND n.parent_node_id IS NULL AND n.node_type = 'existing'
  AND d.file_count = 1 AND d.subdirectory_count = 0
"""

UNHOMED = """
SELECT COUNT(*) FROM residual_sets s
WHERE s.plan_version = :v
  AND json_extract(s.payload, '$.protected') = 0
  AND json_extract(s.payload, '$.set_key') = :key
  AND NOT EXISTS (SELECT 1 FROM tree_nodes n
                  WHERE n.plan_version_id = :v AND n.node_role = 'residual'
                    AND n.display_label = :home)
"""


def measure(conn: sqlite3.Connection) -> dict:
    """The four numbers, as data, so a test can read them without the screen."""
    from cli import REVIEW_HOME_FOR_SET  # the one table, not a copy of it

    row = conn.execute(LATEST_FROZEN).fetchone()
    if row is None:
        return {"frozen_version": None}
    version = row[0]
    # The sets a run surfaces name the version they were surfaced AGAINST, which
    # is the one the homes were then minted onto; a later re-freeze carries the
    # decisions but the set rows keep their version. Read them off every version
    # in this tree's chain rather than the latest alone.
    chain: list[str] = []
    current = version
    while current is not None:
        chain.append(current)
        parent = conn.execute(
            "SELECT predecessor_id FROM plan_versions WHERE plan_version_id = ?",
            (current,)).fetchone()
        current = None if parent is None else parent[0]
    unhomed = 0
    for key, home in REVIEW_HOME_FOR_SET.items():
        for surfaced_against in chain:
            unhomed += conn.execute(
                UNHOMED.replace("s.plan_version = :v", "s.plan_version = :against"),
                {"v": version, "against": surfaced_against, "key": key, "home": home},
            ).fetchone()[0]
    return {
        "frozen_version": version,
        "depth_histogram": dict(conn.execute(DEPTH, {"v": version}).fetchall()),
        "single_child_runs": conn.execute(SINGLE_RUNS, {"v": version}).fetchone()[0],
        "single_file_roots": conn.execute(SINGLE_FILE_ROOTS, {"v": version}).fetchone()[0],
        "unhomed_ordinary_sets": unhomed,
    }


def main(path: str) -> int:
    conn = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    try:
        found = measure(conn)
    finally:
        conn.close()
    if found["frozen_version"] is None:
        print("no frozen plan version in this database; nothing to gate")
        return 1
    print("depth distribution (depth: folders):", found["depth_histogram"])
    print("single-child runs that never divide (must be 0):", found["single_child_runs"])
    print("  the shape half of this gate is observable only after Phase 6's gate is "
          "met: before the fact producers fill more levels the histogram is nearly "
          "flat and this count is trivially 0")
    print("single-file roots (must be 0):", found["single_file_roots"])
    print("ordinary review sets with no offered home in the tree (must be 0):",
          found["unhomed_ordinary_sets"])
    print("nothing moved: not measured here -- `tests/integration`'s `_on_disk` "
          "comparison is that check")
    passed = (found["single_child_runs"] == 0 and found["single_file_roots"] == 0
              and found["unhomed_ordinary_sets"] == 0)
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
