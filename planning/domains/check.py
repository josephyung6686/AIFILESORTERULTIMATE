#!/usr/bin/env python3
"""Gate every domain catalogue against `_CONTRACT.md`.

Fifteen authors and one shape. A catalogue that drifts is fifteen vocabularies for one
concept, which is this project's most expensive recurring defect -- so the check is a
script, not a reviewer's attention.
"""
import json
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).parent
DESIGN = (HERE.parent / "00-database-agent-product-design.md").read_text()

REQUIRED = ("id", "name", "supercategory", "one_line", "provenance", "schema",
            "recognition", "work_types", "grouping_reasons", "template",
            "collides_with", "sensitivity")
PROVENANCE = {"design", "inference", "proposal"}
#: §3.13's six. An extractor may write only the first two (P4 D11).
RELIABILITY = {"direct", "possible", "validated", "llm_supported", "user_confirmed",
               "rejected"}
SENSITIVITY = {"none", "potentially_sensitive"}
RECOGNITION_KEYS = {"deterministic", "needs_llm", "never_alone"}
#: A catalogue holds no numbers: every threshold in this product is injected.
NUMBER = re.compile(r"(?<![\w.])\d+(?:\.\d+)?(?![\w.])")
NUMBER_OK = re.compile(r"§|section |P\d\b|D\d\b|OQ\d|\bM\d\b|20\d\d|B\d\b|C\d\b|G\d\b")


#: A citation quotes the design. JSON's own delimiters are not quotation marks, so
#: only CURLY quotes and backticked spans inside a string value count. The first
#: version of this check scanned the raw file for `"..."` and matched every JSON
#: string in the catalogue: 1,870 false positives, zero findings. Scanning text for a
#: token has now produced a false result nine times in this project.
INNER_QUOTE = re.compile(r'“([^”]{25,})”|\'\'([^\']{25,})\'\'')


def cited_quotes(entry):
    """Every design quotation an entry actually makes."""
    out = []
    def walk(value, key=None):
        if isinstance(value, str):
            if key in ("design_cite", "why", "rationale", "signal"):
                for a, b in INNER_QUOTE.findall(value):
                    out.append(a or b)
        elif isinstance(value, dict):
            for k, v in value.items():
                walk(v, k)
        elif isinstance(value, list):
            for v in value:
                walk(v, key)
    walk(entry)
    return out


def held_numbers(value, path=()):
    """Numeric JSON values, excluding the few structural ones a catalogue may carry."""
    ALLOWED_KEYS = {"signal_tier"}
    found = []
    if isinstance(value, bool):
        return found
    if isinstance(value, (int, float)):
        if not (path and path[-1] in ALLOWED_KEYS):
            found.append(value)
    elif isinstance(value, dict):
        for k, v in value.items():
            found.extend(held_numbers(v, path + (k,)))
    elif isinstance(value, list):
        for v in value:
            found.extend(held_numbers(v, path))
    return found


def check_file(path):
    problems = []
    try:
        doc = json.loads(path.read_text())
    except Exception as exc:
        return [f"{path.name}: does not parse — {exc}"]
    entries = doc.get("entries")
    if not isinstance(entries, list) or not entries:
        return [f"{path.name}: no `entries` list"]

    seen = set()
    for i, e in enumerate(entries):
        tag = f"{path.name}[{i}] {e.get('id', '?')}"
        for field in REQUIRED:
            if field not in e:
                problems.append(f"{tag}: missing `{field}`")
        if e.get("id") in seen:
            problems.append(f"{tag}: duplicate id")
        seen.add(e.get("id"))
        if e.get("provenance") not in PROVENANCE:
            problems.append(f"{tag}: provenance {e.get('provenance')!r} not in {PROVENANCE}")
        if e.get("sensitivity") not in SENSITIVITY:
            problems.append(f"{tag}: sensitivity {e.get('sensitivity')!r} not in {SENSITIVITY}")
        # A `design` claim must carry a citation, and it must be real.
        if e.get("provenance") == "design" and not e.get("design_cite"):
            problems.append(f"{tag}: provenance=design with no design_cite")
        for field in e.get("schema") or []:
            ceiling = field.get("reliability_ceiling")
            if ceiling is not None and ceiling not in RELIABILITY:
                problems.append(f"{tag}: reliability_ceiling {ceiling!r} not one of §3.13's six")
        rec = e.get("recognition") or {}
        if set(rec) - RECOGNITION_KEYS:
            problems.append(f"{tag}: recognition has unknown keys {set(rec) - RECOGNITION_KEYS}")
        tmpl = e.get("template") or {}
        if "dimension_order" not in tmpl:
            problems.append(f"{tag}: template has no dimension_order")
        if not isinstance(tmpl.get("time_first"), bool):
            problems.append(f"{tag}: template.time_first is not a bool")
        # No held THRESHOLDS. A number written as a JSON number is a value the
        # catalogue holds; a number inside a string is an EXAMPLE, and examples are
        # required -- `BUSIB 4300` is §3.2's own. The first version of this check
        # scanned serialized text and flagged every course code, invoice number and
        # arXiv id in two catalogues: 1,926 false positives and not one real finding.
        for bad in held_numbers(e):
            problems.append(f"{tag}: holds the number {bad} as a value — every "
                            "threshold in this product is injected")
    # Every design quotation must actually appear in the design. A previous review in
    # this project invented three of four clauses inside quote marks.
    flat = " ".join(DESIGN.split())
    for entry in entries:
        for quote in cited_quotes(entry):
            needle = " ".join(quote.split())[:60]
            if needle and needle not in flat:
                problems.append(
                    f"{path.name} {entry.get('id')}: quotation not in the design — "
                    f"{needle!r}")
    return problems


def main():
    files = sorted(p for p in HERE.glob("*.json"))
    if not files:
        print("no catalogue files yet")
        return 0
    total = fails = 0
    for path in files:
        problems = check_file(path)
        entries = 0
        try:
            entries = len(json.loads(path.read_text()).get("entries", []))
        except Exception:
            pass
        total += entries
        mark = "OK " if not problems else "FAIL"
        print(f"{mark} {path.name:34} {entries:4} entries  {len(problems)} problems")
        for p in problems[:6]:
            print(f"       - {p}")
        if len(problems) > 6:
            print(f"       … and {len(problems) - 6} more")
        fails += len(problems)
    print(f"\n{len(files)} files, {total} entries, {fails} problems")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
