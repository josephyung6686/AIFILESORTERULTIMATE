#!/usr/bin/env python3
"""Re-run typing + inferred connector on an existing plan database.

Use after a scan that already extracted evidence. Does not move files.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="project_context_graph")
    parser.add_argument("--database", type=Path, required=True)
    args = parser.parse_args(argv)
    import sqlite3
    from items.project import project_after_recognition
    from items.profile_items import mint_declared_items
    from items.schema import create_items_schema

    conn = sqlite3.connect(str(args.database))
    conn.row_factory = sqlite3.Row
    create_items_schema(conn)
    minted = mint_declared_items(conn)
    result = project_after_recognition(conn)
    conn.commit()
    print(f"minted\t{minted}")
    print(f"typed\t{result['typed']}")
    print(f"inferred\t{result['inferred']}")
    rows = conn.execute(
        "SELECT typing_state, COUNT(*) AS n FROM items "
        "WHERE item_type = 'file' GROUP BY typing_state ORDER BY n DESC"
    ).fetchall()
    print("## typing_state")
    for row in rows:
        print(f"{row['n']}\t{row['typing_state']}")
    rows = conn.execute(
        "SELECT type_schema, COUNT(*) AS n FROM items "
        "WHERE item_type = 'file' AND typing_state = 'typed' "
        "GROUP BY type_schema ORDER BY n DESC"
    ).fetchall()
    print("## typed schemas")
    for row in rows:
        print(f"{row['n']}\t{row['type_schema']}")
    print("Nothing was moved.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
