#!/usr/bin/env python3
"""Catalogue 10 — gazetteer checks.

Every invariant PROCEDURE.md marks [mechanical], made executable:

  1. every `quote` anywhere in the four JSONs exists verbatim in its named source file;
  2. word-boundary is real: MIT never matches inside "submit"/"SUBMIT", UNC never inside
     "uncertainty", German lowercase "mit" never matches the case-sensitive alias;
  3. 00's worked strings round-trip: Columbia -> Columbia University, U Chicago / UChicago ->
     University of Chicago, BUSIB 4300 / PHYS1401 match their format families;
  4. HW 3, AY 2024-25, FY2025, v2024, 90210, 2026, Spring 2026 — and the all-caps
     season/month forms FALL 2025, MAY 2024, WS 2024 — match NO course format;
  5. example_true matches its own row; example_false matches no row in its file;
  6. alias collisions across entity files require a recorded homonym; `ambiguous` aliases
     name one;
  7. no int or float anywhere in the JSONs (thresholds are named null slots);
  8. closed vocabularies (provenance, source_kind, status, entity_type, matching);
  9. a CJK alias fixture passes the row schema (representability; the matcher slot stays open);
 10. every backs_fields key resolves in planning/domains/canonical_fields.json (R1a's table).

Run:  python3 check.py     (exit non-zero on any failure)
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PLANNING = HERE.parents[1]

SOURCES = {
    "00": PLANNING / "00-database-agent-product-design.md",
    "P6-SPEC": PLANNING / "parts" / "P6-facts-facets" / "SPEC.md",
    "CONNECTION": PLANNING / "domains" / "CONNECTION.md",
}

CANONICAL_FIELDS = PLANNING / "domains" / "canonical_fields.json"

FILES = [
    "01-schools.json",
    "02-orgs-roles.json",
    "03-research-venues.json",
    "04-course-code-formats.json",
]

ENTITY_FILES = FILES[:3]
FORMAT_FILE = FILES[3]

PROVENANCE = {"design", "inference", "proposal"}
SOURCE_KIND = {"design_example", "official_list", "wikidata", "user_approved", "proposal"}
ROW_STATUS = {"seed"}
FILE_STATUS = {"seed", "schema_only"}
ENTITY_TYPES = {
    "university", "secondary_school", "firm", "financial_institution", "lab", "venue",
}

failures: list[str] = []


def fail(msg: str) -> None:
    failures.append(msg)


# ---------------------------------------------------------------- reference matcher

WORD = "A-Za-z0-9_"


def find_alias(alias: str, text: str, case_sensitive: bool) -> bool:
    """Word-boundary phrase match. The boundary is: the character before the first and after
    the last matched character (if any) is not in [A-Za-z0-9_]. Latin-script semantics —
    the cjk_matcher slot is deliberately NOT implemented here (PROCEDURE.md condition 9)."""
    pattern = rf"(?<![{WORD}]){re.escape(alias)}(?![{WORD}])"
    flags = 0 if case_sensitive else re.IGNORECASE
    return re.search(pattern, text, flags) is not None


def find_format(pattern: str, text: str, excluded_prefixes: list[str], apply_exclusions: bool) -> list[str]:
    """Word-boundary format match, then the term_collision_guard: a hit whose letter block is
    an excluded prefix and whose digit block is year-shaped is NOT a course-code hit."""
    rx = re.compile(rf"(?<![{WORD}])(?:{pattern})(?![{WORD}])")
    hits = []
    for m in rx.finditer(text):
        s = m.group(0)
        if apply_exclusions:
            parts = re.match(r"^([A-Z]+) ?([0-9]+)", s)
            if parts and parts.group(1) in excluded_prefixes and re.fullmatch(r"(19|20)[0-9]{2}", parts.group(2)):
                continue
        hits.append(s)
    return hits


# ---------------------------------------------------------------- load

data: dict[str, dict] = {}
for name in FILES:
    path = HERE / name
    try:
        data[name] = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001 - report and stop; nothing else can run
        print(f"FATAL {name}: {exc}")
        sys.exit(1)

sources_text = {}
for key, path in SOURCES.items():
    if path.exists():
        sources_text[key] = path.read_text(encoding="utf-8")
    else:
        fail(f"source file missing for quote verification: {key} -> {path}")


# ---------------------------------------------------------------- 1. verbatim quotes

def walk_quotes(node, where: str):
    if isinstance(node, dict):
        if "quote" in node:
            src = node.get("source")
            if src not in sources_text:
                fail(f"{where}: quote with unknown/missing source {src!r}")
            elif node["quote"] not in sources_text[src]:
                fail(f"{where}: quote NOT verbatim in {src}: {node['quote'][:80]!r}")
        for k, v in node.items():
            walk_quotes(v, f"{where}.{k}")
    elif isinstance(node, list):
        for i, v in enumerate(node):
            walk_quotes(v, f"{where}[{i}]")


for name, doc in data.items():
    walk_quotes(doc, name)


# ---------------------------------------------------------------- 7. no numbers anywhere

def walk_numbers(node, where: str):
    if isinstance(node, bool):
        return
    if isinstance(node, (int, float)):
        fail(f"{where}: numeric JSON value {node!r} — thresholds are injected, never written")
    elif isinstance(node, dict):
        for k, v in node.items():
            walk_numbers(v, f"{where}.{k}")
    elif isinstance(node, list):
        for i, v in enumerate(node):
            walk_numbers(v, f"{where}[{i}]")


for name, doc in data.items():
    walk_numbers(doc, name)


# ---------------------------------------------------------------- backs_fields resolve in R1a's table

# CONNECTION.md section 6: fields resolve to ONE canonical list. R1a's table has landed;
# every key a gazetteer claims to back must exist there (spelling included — snake_case, D6).
if CANONICAL_FIELDS.exists():
    canonical_keys = {f["key"] for f in json.loads(CANONICAL_FIELDS.read_text(encoding="utf-8"))["fields"]}
    for name, doc in data.items():
        for key in doc.get("backs_fields", []):
            if key not in canonical_keys:
                fail(f"{name}: backs_fields key {key!r} does not resolve in canonical_fields.json")
else:
    fail(f"canonical_fields.json missing at {CANONICAL_FIELDS} — backs_fields cannot be verified")


# ---------------------------------------------------------------- 8. closed vocabularies

for name, doc in data.items():
    if doc.get("owner") != "P6 (injected) — never P5":
        fail(f"{name}: owner must be exactly 'P6 (injected) — never P5'")
    if doc.get("status") not in FILE_STATUS:
        fail(f"{name}: file status {doc.get('status')!r} not in {sorted(FILE_STATUS)}")
    if doc.get("match_rule", {}).get("matching") != "word_boundary":
        fail(f"{name}: match_rule.matching must be 'word_boundary' — it is the consumer invariant")
    if not doc.get("universe"):
        fail(f"{name}: universe missing or empty (PROCEDURE.md condition 1)")
    slots = doc.get("injected_slots", {})
    for slot in ("min_score", "min_margin", "positional_weight_by_zone"):
        if slot not in slots:
            fail(f"{name}: injected slot {slot} missing")
        elif slots[slot] is not None:
            fail(f"{name}: injected slot {slot} must be null (injected, never authored)")
    for row in doc.get("entries", []):
        rid = row.get("id", "<no id>")
        if row.get("provenance") not in PROVENANCE:
            fail(f"{name}:{rid}: provenance {row.get('provenance')!r} not in {sorted(PROVENANCE)}")
        if row.get("source_kind") not in SOURCE_KIND:
            fail(f"{name}:{rid}: source_kind {row.get('source_kind')!r} not in {sorted(SOURCE_KIND)}")
        if row.get("status") not in ROW_STATUS:
            fail(f"{name}:{rid}: row status {row.get('status')!r} not in {sorted(ROW_STATUS)}")
        if row.get("provenance") == "design" and not row.get("design_cite"):
            fail(f"{name}:{rid}: provenance 'design' requires a design_cite with a verbatim quote")

for name in ENTITY_FILES:
    for row in data[name].get("entries", []):
        rid = row.get("id", "<no id>")
        if row.get("entity_type") not in ENTITY_TYPES:
            fail(f"{name}:{rid}: entity_type {row.get('entity_type')!r} not in the closed set")
        if not row.get("aliases"):
            fail(f"{name}:{rid}: no aliases — the canonical itself must appear as an alias row")
        for a in row.get("aliases", []):
            if "alias" not in a or "case_sensitive" not in a or "script" not in a:
                fail(f"{name}:{rid}: alias row missing alias/case_sensitive/script: {a!r}")
            if a.get("ambiguous") and not a.get("homonym"):
                fail(f"{name}:{rid}: alias {a.get('alias')!r} marked ambiguous without a homonym id")


# ---------------------------------------------------------------- helper: resolve over entity files

def resolve(text: str) -> set[str]:
    """All canonicals whose aliases hit `text` at a word boundary, across entity files."""
    out = set()
    for name in ENTITY_FILES:
        for row in data[name].get("entries", []):
            for a in row.get("aliases", []):
                if find_alias(a["alias"], text, a["case_sensitive"]):
                    out.add(row["canonical"])
    return out


# ---------------------------------------------------------------- 2. word-boundary adversarial (live rows)

for text in ("please submit the form", "PLEASE SUBMIT THE FORM", "Submit"):
    if "Massachusetts Institute of Technology" in resolve(text):
        fail(f"word-boundary: MIT matched inside {text!r} — the §3.7 failure this file exists to prevent")
for text in ("uncertainty principle", "UNCERTAINTY"):
    if "University of North Carolina" in resolve(text):
        fail(f"word-boundary: UNC matched inside {text!r}")
if "Massachusetts Institute of Technology" in resolve("Komm mit uns"):
    fail("case rule: lowercase German 'mit' matched the case-sensitive MIT alias")
if "Massachusetts Institute of Technology" not in resolve("MIT OpenCourseWare"):
    fail("word-boundary: 'MIT OpenCourseWare' should hit sch-mit (bounded, uppercase)")
# The honest limit, asserted so the homonym record stays true rather than decorative:
if "Massachusetts Institute of Technology" not in resolve("MIT License"):
    fail("hom-mit is stale: 'MIT License' no longer produces the wrong-entity hit it documents")
if "Columbia University" not in resolve("British Columbia"):
    fail("hom-columbia is stale: 'British Columbia' no longer produces the wrong-entity hit it documents")


# ---------------------------------------------------------------- 3. 00's worked strings round-trip

def expect_resolve(text: str, canonical: str):
    got = resolve(text)
    if canonical not in got:
        fail(f"round-trip: {text!r} did not resolve to {canonical!r} (got {sorted(got)})")


expect_resolve("Columbia", "Columbia University")
expect_resolve("Columbia Essay.docx", "Columbia University")
expect_resolve("U Chicago", "University of Chicago")
expect_resolve("UChicago", "University of Chicago")
expect_resolve("University of Chicago", "University of Chicago")
expect_resolve("Wash U.docx", "Washington University in St. Louis")
expect_resolve("EY Internship Application", "EY")

fmt = data[FORMAT_FILE]
guard = fmt.get("term_collision_guard", {})
excluded = guard.get("excluded_prefixes", [])


def format_hits(text: str) -> list[str]:
    out = []
    for row in fmt.get("entries", []):
        hits = find_format(row["pattern"], text, excluded, row.get("excluded_prefixes_apply", False))
        if hits:
            out.append(row["id"])
    return out


if "ccf-dept-space-number" not in format_hits("BUSIB 4300"):
    fail("round-trip: 'BUSIB 4300' did not match ccf-dept-space-number")
if "ccf-dept-number-nospace" not in format_hits("PHYS1401"):
    fail("round-trip: 'PHYS1401' did not match ccf-dept-number-nospace")
if "ccf-dept-space-number" not in format_hits("Syllabus BUSIB 4300 Spring 2026.pdf"):
    fail("round-trip: the design's syllabus filename did not yield a format hit")


# ---------------------------------------------------------------- 4. course-format negatives

for bad in ("HW 3", "AY 2024-25", "AY 2024", "FY2025", "v2024", "90210", "2026", "Spring 2026",
            "FALL 2025", "SPRING 2026", "MAY 2024", "SEPT 2024", "AUG 2019", "WS 2024", "MARCH 2025"):
    hits = format_hits(bad)
    if hits:
        fail(f"course-format negative: {bad!r} matched {hits} — must match no family")


# ---------------------------------------------------------------- 5. example_true / example_false

for name in ENTITY_FILES:
    doc = data[name]
    for row in doc.get("entries", []):
        rid = row["id"]
        ok = any(
            find_alias(a["alias"], row["example_true"], a["case_sensitive"])
            for a in row["aliases"]
        )
        if not ok:
            fail(f"{name}:{rid}: example_true {row['example_true']!r} does not match its own row")
        # example_false must match NO row in the same file
        for other in doc.get("entries", []):
            for a in other["aliases"]:
                if find_alias(a["alias"], row["example_false"], a["case_sensitive"]):
                    fail(
                        f"{name}:{rid}: example_false {row['example_false']!r} matches "
                        f"{other['id']} alias {a['alias']!r}"
                    )
    for ref in doc.get("refused", []):
        if "example_false" in ref:
            for other in doc.get("entries", []):
                for a in other["aliases"]:
                    if find_alias(a["alias"], ref["example_false"], a["case_sensitive"]):
                        fail(
                            f"{name}:{ref['id']}: refused example {ref['example_false']!r} "
                            f"matches {other['id']} alias {a['alias']!r}"
                        )

for row in fmt.get("entries", []):
    rid = row["id"]
    if not find_format(row["pattern"], row["example_true"], excluded, row.get("excluded_prefixes_apply", False)):
        fail(f"{FORMAT_FILE}:{rid}: example_true {row['example_true']!r} does not match its own pattern")
    if format_hits(row["example_false"]):
        fail(f"{FORMAT_FILE}:{rid}: example_false {row['example_false']!r} matches a family")
for ref in fmt.get("refused", []):
    if "example_false" in ref and format_hits(ref["example_false"]):
        fail(f"{FORMAT_FILE}:{ref['id']}: refused example {ref['example_false']!r} matches a family")


# ---------------------------------------------------------------- 6. alias collision registry

alias_map: dict[str, set[str]] = {}
alias_meta: dict[str, list[tuple[str, str, dict]]] = {}
for name in ENTITY_FILES:
    for row in data[name].get("entries", []):
        for a in row["aliases"]:
            key = a["alias"] if a["case_sensitive"] else a["alias"].casefold()
            alias_map.setdefault(key, set()).add(row["canonical"])
            alias_meta.setdefault(key, []).append((name, row["id"], a))

homonym_aliases = set()
for name in ENTITY_FILES:
    for h in data[name].get("homonyms", []):
        homonym_aliases.add(h["alias"].casefold())

for key, canonicals in alias_map.items():
    if len(canonicals) > 1 and key not in homonym_aliases:
        fail(f"alias collision without a homonym record: {key!r} -> {sorted(canonicals)}")
for name in ENTITY_FILES:
    declared = {h["id"] for h in data[name].get("homonyms", [])}
    for row in data[name].get("entries", []):
        for a in row["aliases"]:
            if a.get("ambiguous") and a.get("homonym") not in declared:
                fail(f"{name}:{row['id']}: alias {a['alias']!r} names homonym {a.get('homonym')!r} "
                     f"which is not declared in this file")


# ---------------------------------------------------------------- 9. CJK representability fixture

cjk_fixture = {
    "alias": "清华大学",
    "case_sensitive": False,
    "script": "Han",
}
if not (isinstance(cjk_fixture["alias"], str) and cjk_fixture["script"] == "Han"):
    fail("CJK fixture: schema cannot represent a Han-script alias")
# The matcher half stays open by design: Latin word boundaries around a Han run in Latin text
# do work mechanically, but boundaries INSIDE undelimited CJK prose do not exist — which is
# exactly why cjk_matcher is a named, unfilled slot rather than this function.
if not find_alias(cjk_fixture["alias"], "清华大学 admission letter", cjk_fixture["case_sensitive"]):
    fail("CJK fixture: a delimited Han alias should still match in mixed text")


# ---------------------------------------------------------------- report

if failures:
    print(f"FAIL — {len(failures)} problem(s)")
    for f in failures:
        print("  -", f)
    sys.exit(1)

counts = {name: len(doc.get("entries", [])) for name, doc in data.items()}
print("OK —",
      ", ".join(f"{name}: {n} entries" for name, n in counts.items()))
print("word-boundary, round-trips, negatives, collisions, quotes, no-numbers: all hold")
