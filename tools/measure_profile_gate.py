#!/usr/bin/env python3
"""Count recognition outcomes with and without declared lives.

Usage:
  python3 tools/measure_profile_gate.py --database PATH \\
      --declared academic,career,college_applications,code

Prints schema Recognition counts and abstention reasons. Does not move files.
Does not invent a Downloads corpus: pass a database that already has evidence.
"""
from __future__ import annotations

import argparse
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="measure_profile_gate")
    parser.add_argument("--database", type=Path, required=True)
    parser.add_argument(
        "--declared",
        default="academic,career,college_applications,code",
        help="Comma-separated schema ids, or empty for no profile",
    )
    parser.add_argument("--limit", type=int, default=0,
                        help="Max files to score (0 = all with observations)")
    args = parser.parse_args(argv)

    from types import MappingProxyType

    import sqlite3
    from facts.domains import SCHEMA_IDS
    from recognition.detector import (
        Abstention, Detector, Handling, Recognition, SAFETY_DOMAIN_HANDLING,
    )
    from recognition.rules import load_rules

    conn = sqlite3.connect(str(args.database))
    conn.row_factory = sqlite3.Row
    declared_raw = args.declared.strip()
    lives = frozenset(
        part.strip() for part in declared_raw.split(",") if part.strip()
    ) if declared_raw else frozenset()

    ordinary = {
        sid: Handling(handling_class="personal_non_sensitive",
                      protected=False, basis="detector")
        for sid in SCHEMA_IDS
    }
    policy = MappingProxyType({**ordinary, **SAFETY_DOMAIN_HANDLING})
    manifest = ROOT / "src" / "recognition" / "library" / "recognition.json"
    rules = load_rules(manifest.read_text)
    detector = Detector(
        rules, handling_for=policy,
        now=lambda: "2026-10-02T00:00:00+00:00",
        declared_lives=(lambda: lives) if lives else None,
    )

    # Evidence rows live in P4's `evidence` table (not a table named observations).
    files = conn.execute(
        "SELECT DISTINCT e.file_id, e.content_hash FROM evidence e "
        "JOIN files f ON f.file_id = e.file_id "
        "WHERE e.superseded_by IS NULL "
        "AND f.scan_state NOT IN ('path_no_longer_exists') "
        "ORDER BY e.file_id"
    ).fetchall()
    if args.limit:
        files = files[: args.limit]
    if not files:
        print("No evidence rows. Scan a corpus into this database first.",
              file=sys.stderr)
        return 2

    recog = Counter()
    abstain = Counter()
    for row in files:
        outcome = detector.explain(conn, row["file_id"], row["content_hash"])
        if isinstance(outcome, Recognition):
            recog[outcome.schema_id] += 1
        elif isinstance(outcome, Abstention):
            abstain[outcome.reason] += 1
        else:
            abstain[type(outcome).__name__] += 1

    print(f"files_scored\t{len(files)}")
    print(f"declared_lives\t{','.join(sorted(lives)) or '(none)'}")
    print("## Recognition by schema")
    for schema, count in recog.most_common():
        print(f"{count}\t{schema}")
    print("## Abstentions by reason")
    for reason, count in abstain.most_common():
        print(f"{count}\t{reason}")
    print("Nothing was moved.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
