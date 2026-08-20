#!/usr/bin/env python3
"""Render every catalogue's markdown from its JSON.

The JSON is the source of truth. The markdown is generated. Nobody hand-edits a
table: run `python3 render.py` after changing a JSON file and commit both.

`python3 render.py --check` re-renders in memory and exits non-zero if any
committed markdown differs from what the JSON produces — the no-drift guard.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent

#: Every column an entry may carry, in table order. An entry is not required to
#: carry all of them (a pattern list has `pattern` where a string list has
#: `match`); a column with no value in any entry of an array is dropped.
COLUMNS: tuple[tuple[str, str], ...] = (
    ("id", "id"),
    ("match", "match"),
    ("pattern", "pattern"),
    ("match_kind", "match_kind"),
    ("case_sensitive", "case sensitive"),
    ("role", "role"),
    ("status", "status"),
    ("aspect_ratio", "aspect ratio"),
    ("orientation", "orientation"),
    ("rationale", "rationale"),
    ("design_cite", "design cite"),
    ("false_positive_risk", "FP risk"),
    ("example_true", "example true"),
    ("example_false", "example false (must NOT match)"),
    ("source", "source"),
)

#: Keys whose value is an array of entries and therefore renders as a table.
#: Any other array key renders as a bullet list.
ENTRY_ARRAY_ORDER: tuple[str, ...] = (
    "entries",
    "p3_exclusion_roots",
    "p5_evidence_markers",
    "refused",
    "uncertain",
)

ARRAY_HEADINGS: dict[str, str] = {
    "entries": "Entries",
    "p3_exclusion_roots": "`p3_exclusion_roots` — P3 skips descendants of a directory holding one of these",
    "p5_evidence_markers": "`p5_evidence_markers` — P5 evidence that a file looks like part of a project",
    "refused": "Refused — deliberately NOT matched",
    "uncertain": "Uncertain — needs Joseph",
}


def cell(value: object) -> str:
    if value is None:
        return "—"
    if isinstance(value, bool):
        return "yes" if value else "no"
    if isinstance(value, list):
        return "<br>".join(cell(v) for v in value)
    text = str(value)
    # Markdown table cells: escape the delimiter and flatten newlines.
    return text.replace("|", "\\|").replace("\n", " ")


def code_cell(value: object) -> str:
    if value is None:
        return "—"
    return f"`{cell(value)}`"


def render_table(rows: list[dict]) -> list[str]:
    used = [(key, head) for key, head in COLUMNS
            if any(key in row for row in rows)]
    out = ["| " + " | ".join(head for _, head in used) + " |",
           "|" + "|".join("---" for _ in used) + "|"]
    literal = {"id", "match", "pattern", "example_true", "example_false"}
    for row in rows:
        cells = [code_cell(row.get(key)) if key in literal else cell(row.get(key))
                 for key, _ in used]
        out.append("| " + " | ".join(cells) + " |")
    return out


def render(doc: dict) -> str:
    out: list[str] = [f"# {doc['title']}", ""]

    front = (("list_id", "list_id"), ("version", "version"),
             ("authored", "authored"), ("owner", "owner"),
             ("consumer", "consumer"), ("match_field", "match_field"),
             ("normalization_for_matching", "normalization for matching"),
             ("boundary_rule", "boundary rule"))
    for key, label in front:
        if key in doc:
            out.append(f"- **{label}**: {doc[key]}")
    out.append("")

    if doc.get("design_cites"):
        out += ["## Design basis", ""]
        out += [f"- {line}" for line in doc["design_cites"]]
        out.append("")

    if doc.get("rules"):
        out += ["## Rules this list obeys", ""]
        out += [f"{i}. {line}" for i, line in enumerate(doc["rules"], 1)]
        out.append("")

    if doc.get("injection"):
        out += ["## Injection", "", doc["injection"], ""]

    if doc.get("coverage_note"):
        out += ["## Coverage note", "", doc["coverage_note"], ""]

    for key in ENTRY_ARRAY_ORDER:
        rows = doc.get(key)
        if rows is None:
            continue
        out += [f"## {ARRAY_HEADINGS[key]}", ""]
        if not rows:
            out += ["_None._", ""]
            continue
        out += [f"{len(rows)} entries.", ""]
        out += render_table(rows)
        out.append("")

    if doc.get("sources"):
        out += ["## Sources", ""]
        for src in doc["sources"]:
            note = f" — {src['note']}" if src.get("note") else ""
            out.append(f"- [{src['title']}]({src['url']}) — retrieved "
                       f"{src['retrieved']}{note}")
        out.append("")

    out += ["---", "",
            "_Generated from the JSON beside this file by `render.py`. "
            "Do not hand-edit: edit the JSON and re-run._", ""]
    return "\n".join(out)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    drift = []
    for path in sorted(HERE.glob("[0-9][0-9]-*.json")):
        doc = json.loads(path.read_text(encoding="utf-8"))
        text = render(doc)
        target = path.with_suffix(".md")
        if args.check:
            current = target.read_text(encoding="utf-8") if target.exists() else ""
            if current != text:
                drift.append(target.name)
        else:
            target.write_text(text, encoding="utf-8")
            counts = ", ".join(
                f"{k}={len(doc[k])}" for k in ENTRY_ARRAY_ORDER if k in doc)
            print(f"{target.name}: {counts}")

    if args.check:
        if drift:
            print("DRIFT: " + ", ".join(drift), file=sys.stderr)
            return 1
        print("no drift")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
