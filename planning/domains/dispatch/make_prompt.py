#!/usr/bin/env python3
"""Stamp the R1b per-domain prompt with one roster ASSIGNMENT.

    python3 planning/domains/dispatch/make_prompt.py acad.coursework.enrollment
    python3 planning/domains/dispatch/make_prompt.py --all --out-dir /tmp/r1b-prompts

Does not invent ids. Roster must already exist (R1a).
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]  # planning/
REPO = HERE.parents[2]
ROSTER = ROOT / "domains" / "roster.json"
TEMPLATE = ROOT / "prompts" / "01b-per-domain-research.md"
PLACEHOLDER_START = "Dispatcher replaces this object."


def load_roster() -> dict:
    if not ROSTER.exists():
        sys.exit(
            f"missing {ROSTER}\nRun R1a first (planning/prompts/01a-spine-roster.md)."
        )
    return json.loads(ROSTER.read_text())


def node_for(roster: dict, domain_id: str) -> dict:
    for row in roster.get("nodes", []):
        if row.get("domain_id") == domain_id or row.get("id") == domain_id:
            return row
    known = sorted(
        row.get("domain_id") or row.get("id") for row in roster.get("nodes", [])
    )
    sys.exit(f"id not on roster: {domain_id!r}\n{len(known)} ids, first: {known[:8]}")


def assignment_block(row: dict) -> str:
    domain_id = row.get("domain_id") or row["id"]
    payload = {
        "kind": row.get("kind") or "template",
        "domain_id": domain_id,
        "schema_id": row.get("schema_id") or domain_id,
        "parent_id": row.get("parent_id"),
        "name": row.get("name"),
        "one_line_hint": row.get("one_line_hint") or row.get("one_line"),
        "launch": row.get("launch"),
        "must_consider_neighbors": row.get("must_consider_neighbors") or [],
        "must_consider_residuals": row.get("must_consider_residuals") or [],
        "inherited_field_keys": row.get("inherited_field_keys") or [],
        "output_json": row.get("output_json")
        or f"planning/domains/nodes/{domain_id}.json",
        "output_research": row.get("output_research")
        or f"planning/domains/nodes/{domain_id}.research.md",
    }
    return json.dumps(payload, indent=2, ensure_ascii=False)


def stamp(template: str, row: dict) -> str:
    """Replace the ASSIGNMENT JSON fence. Fail if the template shape moved."""
    fence = "```json"
    start = template.find(fence)
    if start < 0 or PLACEHOLDER_START not in template[: start + 400]:
        sys.exit("01b template ASSIGNMENT block not found; update make_prompt.py")
    # first json fence after ASSIGNMENT heading
    assign_h = template.find("## ASSIGNMENT")
    start = template.find(fence, assign_h)
    end = template.find("```", start + len(fence))
    if start < 0 or end < 0:
        sys.exit("01b ASSIGNMENT json fence not found")
    inner_start = start + len(fence)
    return (
        template[:inner_start]
        + "\n"
        + assignment_block(row)
        + "\n"
        + template[end:]
    )


def header(row: dict) -> str:
    domain_id = row.get("domain_id") or row["id"]
    return (
        f"<!-- stamped R1b for {domain_id} — do not hand-edit the ASSIGNMENT -->\n\n"
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("domain_id", nargs="?")
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--out-dir", type=pathlib.Path)
    parser.add_argument("--list", action="store_true", help="print roster ids")
    args = parser.parse_args()
    roster = load_roster()
    nodes = roster.get("nodes") or []
    if args.list:
        for row in nodes:
            print(row.get("domain_id") or row.get("id"))
        return
    template = TEMPLATE.read_text()
    if args.all:
        out = args.out_dir or (ROOT / "domains" / "dispatch" / "prompts")
        out.mkdir(parents=True, exist_ok=True)
        for row in nodes:
            domain_id = row.get("domain_id") or row["id"]
            text = header(row) + stamp(template, row)
            (out / f"{domain_id}.md").write_text(text)
        print(f"wrote {len(nodes)} prompts under {out}", file=sys.stderr)
        return
    if not args.domain_id:
        parser.error("domain_id required unless --all or --list")
    row = node_for(roster, args.domain_id)
    sys.stdout.write(header(row) + stamp(template, row))


if __name__ == "__main__":
    main()
