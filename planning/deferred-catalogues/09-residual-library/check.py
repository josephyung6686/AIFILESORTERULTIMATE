#!/usr/bin/env python3
"""Gate for the residual template library (R3).

Asserts, mechanically, what the R3 dispatch's check clause names:

  1. exactly nine shipped template names, no extra, spelled 00's way;
  2. every one of the eight 00 slot keys present on every template
     (value, injected slot, or explicit empty-with-why);
  3. Protected Records carries the no-filename-no-content constraint,
     and its evidence patterns are deterministic-only;
  4. no fabricated 00 quotes: every curly-quoted span in every JSON here —
     and in README.md and RESEARCH.md, which reserve curly quotes for 00
     the same way — appears verbatim (whitespace-normalized) in
     planning/00-database-agent-product-design.md;
  5. expected_file_types is a subset of P5's closed SOURCE_TYPES union
     literal extension examples.

Plus the house rules this repo already enforces elsewhere:

  6. no numeric JSON values anywhere (every threshold is injected);
  7. provenance vocabulary is exactly design | inference | proposal;
  8. treatment vocabulary is exactly 00's three;
  9. every falls_through_to target is one of the nine names and no edge
     has a residual name as its source (terminal by construction);
 10. the review-set projection names all eight 00 review-set bullets;
 11. the user-defined shape defines exactly the eight slot keys and
     ships zero templates — 00's example names appear nowhere as a
     shipped template.

Run:  python3 planning/deferred-catalogues/09-residual-library/check.py
Exit non-zero on any problem.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_PLANNING = HERE.parent.parent
DESIGN = (REPO_PLANNING / "00-database-agent-product-design.md").read_text()
FLAT_DESIGN = " ".join(DESIGN.split())

# The nine, spelled 00's way. Order follows 00's own enumeration.
NINE = (
    "Temporary Screenshots",
    "One-Off Images",
    "Reference Clips",
    "Independent Records",
    "Receipts and Confirmations",
    "Reading Inbox",
    "Review Later",
    "Unsupported or Encrypted",
    "Protected Records",
)

# The eight 00 slot keys, verbatim order of 00's sentence.
EIGHT_SLOTS = (
    "display_name",
    "default_parent_location",
    "accepted_evidence_patterns",
    "expected_file_types",
    "sensitivity_restrictions",
    "optional_shallow_subfolders",
    "max_permitted_depth",
    "treatment",
)

# P5's closed fourteen (src/evidence_shape/vocabulary.py SOURCE_TYPES).
SOURCE_TYPES = (
    "filesystem", "text_document", "spreadsheet", "presentation", "image",
    "ocr", "email", "calendar", "contacts", "code_structured", "audio_video",
    "design_creative", "archive", "opaque_binary",
)

EXTENSION = re.compile(r"^\.[a-z0-9]+$")
PROVENANCE = ("design", "inference", "proposal")
TREATMENTS = ("reviewed", "retained", "merely kept searchable")

# 00's eight review-set example lines (§7.5), verbatim.
REVIEW_SETS = (
    "58 screenshots with no accepted project or event",
    "21 standalone PDFs and forms",
    "14 spreadsheets and presentations with unclear purpose",
    "17 receipts, tickets, and confirmations",
    "11 protected personal records",
    "9 encrypted, unreadable, or unsupported files",
    "16 files with multiple plausible destinations",
    "20 files with no extractable text, usable metadata, or graph relationship",
)

# 00's user-defined illustrations — shipped nowhere.
USER_DEFINED_ILLUSTRATIONS = (
    "Things to Read", "Ideas", "Shopping Research", "Memes", "Travel",
    "Receipts to Process", "Clips", "Stuff to Sort",
)

CURLY = re.compile(r"“([^”]+)”")

problems: list[str] = []


def walk_strings(value, path=""):
    if isinstance(value, str):
        yield path, value
    elif isinstance(value, dict):
        for k, v in value.items():
            yield from walk_strings(v, f"{path}.{k}")
    elif isinstance(value, list):
        for i, v in enumerate(value):
            yield from walk_strings(v, f"{path}[{i}]")


def walk_numbers(value, path=""):
    if isinstance(value, bool):
        return
    if isinstance(value, (int, float)):
        yield path, value
    elif isinstance(value, dict):
        for k, v in value.items():
            yield from walk_numbers(v, f"{path}.{k}")
    elif isinstance(value, list):
        for i, v in enumerate(value):
            yield from walk_numbers(v, f"{path}[{i}]")


def check_quotes(doc, name):
    """Every curly-quoted span must exist verbatim in 00 — the convention
    these files state: curly quotes are reserved for 00 quotations."""
    for path, s in walk_strings(doc):
        for span in CURLY.findall(s):
            needle = " ".join(span.split())
            if needle and needle not in FLAT_DESIGN:
                problems.append(
                    f"{name}{path}: quotation not in 00 — {needle[:80]!r}")


def check_no_numbers(doc, name):
    for path, n in walk_numbers(doc):
        problems.append(
            f"{name}{path}: holds the number {n} as a JSON value — every "
            "threshold in this product is injected")


def check_provenance(doc, name):
    for path, s in walk_strings(doc):
        if path.endswith(".provenance") and s not in PROVENANCE:
            problems.append(
                f"{name}{path}: provenance {s!r} not in {PROVENANCE}")


def load(fname):
    try:
        return json.loads((HERE / fname).read_text())
    except Exception as exc:  # noqa: BLE001 — a gate reports, it does not raise
        problems.append(f"{fname}: does not parse — {exc}")
        return None


# ---------------------------------------------------------------- 01
doc1 = load("01-nine-templates.json")
if doc1 is not None:
    check_quotes(doc1, "01-nine-templates.json ")
    check_no_numbers(doc1, "01-nine-templates.json ")
    check_provenance(doc1, "01-nine-templates.json ")

    templates = doc1.get("templates", [])
    names = [t.get("name") for t in templates]
    if names != list(NINE):
        problems.append(
            f"01: template names must be exactly the nine, 00's spelling and "
            f"order — got {names}")

    for t in templates:
        tag = f"01 {t.get('id', '?')}"
        slots = t.get("slots", {})
        missing = [k for k in EIGHT_SLOTS if k not in slots]
        if missing:
            problems.append(f"{tag}: missing slot keys {missing}")
        extra = [k for k in slots if k not in EIGHT_SLOTS]
        if extra:
            problems.append(f"{tag}: unknown slot keys {extra} — the eight "
                            "are 00's, closed")

        # display_name must equal the template name (fixed; user renames
        # happen on the node, not in this library).
        dn = slots.get("display_name", {}).get("value")
        if dn != t.get("name"):
            problems.append(f"{tag}: display_name {dn!r} != name")

        # expected_file_types ⊆ SOURCE_TYPES ∪ extensions.
        for ft in slots.get("expected_file_types", {}).get("value", []):
            if ft not in SOURCE_TYPES and not EXTENSION.match(ft):
                problems.append(
                    f"{tag}: expected_file_type {ft!r} is neither a P5 "
                    f"source_type nor an extension example")

        # max_permitted_depth is an injected slot, never a number.
        depth = slots.get("max_permitted_depth", {})
        if "injected_slot" not in depth:
            problems.append(f"{tag}: max_permitted_depth must name an "
                            "injected_slot")
        elif not str(depth["injected_slot"]).startswith("residual_max_depth."):
            problems.append(f"{tag}: injected slot "
                            f"{depth['injected_slot']!r} not in the "
                            "residual_max_depth namespace")

        # treatment ∈ 00's three.
        tr = slots.get("treatment", {}).get("value")
        if tr not in TREATMENTS:
            problems.append(f"{tag}: treatment {tr!r} not in {TREATMENTS}")

        # every evidence pattern names its pattern and signals.
        for i, p in enumerate(slots.get("accepted_evidence_patterns", {})
                              .get("value", [])):
            if not p.get("pattern") or not p.get("signals"):
                problems.append(f"{tag}: evidence pattern [{i}] lacks "
                                "pattern/signals")

        # empty-value slots must say why.
        subs = slots.get("optional_shallow_subfolders", {})
        if subs.get("value") == [] and not subs.get("why_empty"):
            problems.append(f"{tag}: empty subfolders without why_empty")

        # sensitivity_restrictions carries an explicit prompt_exposure.
        sens = slots.get("sensitivity_restrictions", {})
        if sens.get("prompt_exposure") not in ("governed_by_p7_gate",
                                               "forbidden_by_00_7_3"):
            problems.append(f"{tag}: sensitivity_restrictions must state "
                            "prompt_exposure")

    # Protected Records: the constraint, by construction.
    pr = next((t for t in templates if t.get("name") == "Protected Records"),
              None)
    if pr is None:
        problems.append("01: Protected Records missing")
    else:
        sens = pr["slots"]["sensitivity_restrictions"]
        if sens.get("prompt_exposure") != "forbidden_by_00_7_3":
            problems.append("01 protected_records: prompt_exposure must be "
                            "forbidden_by_00_7_3")
        constraint = sens.get("constraint", "")
        required = ("must not cause filenames or content to be exposed in "
                    "model prompts")
        if required not in " ".join(constraint.split()):
            problems.append("01 protected_records: sensitivity_restrictions "
                            "does not carry 00's no-filename-no-content "
                            "constraint verbatim")
        pats = pr["slots"]["accepted_evidence_patterns"]["value"]
        if not any(p.get("pattern") == "deterministic-only" for p in pats):
            problems.append("01 protected_records: needs the "
                            "deterministic-only pattern — membership may "
                            "never require a model prompt")
        if pr["slots"]["optional_shallow_subfolders"].get("value") != []:
            problems.append("01 protected_records: subfolders must be empty — "
                            "content-derived names republish sensitive facts "
                            "in paths")
        # forbidden_by_00_7_3 is Protected Records' alone.
        for t in templates:
            if t.get("name") != "Protected Records":
                if (t["slots"]["sensitivity_restrictions"]
                        .get("prompt_exposure") == "forbidden_by_00_7_3"):
                    problems.append(f"01 {t.get('id')}: forbidden_by_00_7_3 "
                                    "is Protected Records' constraint only")

    # Review-set projection: all eight 00 bullets, projectable.
    proj = doc1.get("review_set_projection", {}).get("sets", [])
    seen = [" ".join(CURLY.findall(s.get("review_set", ""))[0].split())
            if CURLY.findall(s.get("review_set", "")) else ""
            for s in proj]
    for bullet in REVIEW_SETS:
        if bullet not in seen:
            problems.append(f"01: review-set bullet not projected — "
                            f"{bullet!r}")
    if len(proj) != len(REVIEW_SETS):
        problems.append(f"01: expected the eight 00 review sets, got "
                        f"{len(proj)}")
    ids = {t.get("id") for t in templates}
    for s in proj:
        if not s.get("query"):
            problems.append(f"01: review set {s.get('review_set')!r} has no "
                            "query")
        for src in s.get("projects_from", []):
            if src not in ids:
                problems.append(f"01: review set projects from unknown "
                                f"template {src!r}")

# ---------------------------------------------------------------- 02
doc2 = load("02-user-defined-shape.json")
if doc2 is not None:
    check_quotes(doc2, "02-user-defined-shape.json ")
    check_no_numbers(doc2, "02-user-defined-shape.json ")
    check_provenance(doc2, "02-user-defined-shape.json ")

    shape_slots = doc2.get("shape", {}).get("slots", {})
    if sorted(shape_slots) != sorted(EIGHT_SLOTS):
        problems.append(
            f"02: shape must define exactly the eight slot keys — got "
            f"{sorted(shape_slots)}")
    if "templates" in doc2:
        problems.append("02: ships templates — the shape file is a form, "
                        "never a library")
    # 00's illustrations are never shipped, in either file.
    shipped_names = set()
    if doc1 is not None:
        shipped_names = {t.get("name") for t in doc1.get("templates", [])}
    for illustration in USER_DEFINED_ILLUSTRATIONS:
        if illustration in shipped_names:
            problems.append(f"user-defined illustration {illustration!r} "
                            "shipped as a template — 00 forbids it")

# ---------------------------------------------------------------- 03
doc3 = load("03-falls-through.json")
if doc3 is not None:
    check_quotes(doc3, "03-falls-through.json ")
    check_no_numbers(doc3, "03-falls-through.json ")
    check_provenance(doc3, "03-falls-through.json ")

    if not doc3.get("complement_rule", {}).get("statement"):
        problems.append("03: complement_rule.statement missing — the rule "
                        "must be written")

    for i, e in enumerate(doc3.get("edges", [])):
        tag = f"03 edges[{i}]"
        if e.get("to") not in NINE:
            problems.append(f"{tag}: falls_through_to target {e.get('to')!r} "
                            "is not one of the nine 00 names")
        if e.get("from") in NINE:
            problems.append(f"{tag}: residual name {e.get('from')!r} as a "
                            "source — residuals are terminal by construction")
        if e.get("from_kind") not in ("schema", "template"):
            problems.append(f"{tag}: from_kind must be schema|template")
        for key in ("from", "when", "does_not_fire_when"):
            if not e.get(key):
                problems.append(f"{tag}: missing {key}")

    for b in doc3.get("boundaries", []):
        if not b.get("rule"):
            problems.append(f"03 boundary {b.get('id')}: no rule text")
    known_boundaries = {b.get("id") for b in doc3.get("boundaries", [])}
    for w in doc3.get("worked_cases", []):
        if w.get("boundary") not in known_boundaries:
            problems.append(f"03 worked case {w.get('case')!r}: names "
                            f"unknown boundary {w.get('boundary')!r}")

# ------------------------------------------------------- README / RESEARCH
# Both reserve curly quotes for verbatim 00 quotations, like the JSONs.
# (The no-numbers rule does NOT extend to RESEARCH.md: the dispatch allows
# recommending injected-slot values there, marked proposal.)
for md_name in ("README.md", "RESEARCH.md"):
    md_path = HERE / md_name
    if not md_path.exists():
        problems.append(f"{md_name}: missing — the dispatch's output list "
                        "requires it")
        continue
    for span in CURLY.findall(md_path.read_text()):
        needle = " ".join(span.split())
        if needle and needle not in FLAT_DESIGN:
            problems.append(
                f"{md_name}: quotation not in 00 — {needle[:80]!r}")

# ---------------------------------------------------------------- verdict
if problems:
    print(f"{len(problems)} problem(s):")
    for p in problems:
        print(" -", p)
    sys.exit(1)

count = len(doc1.get("templates", [])) if doc1 else 0
edges = len(doc3.get("edges", [])) if doc3 else 0
print(f"OK: {count} templates (the nine), 8 slots each, {edges} "
      "falls_through_to edges, all quotes verbatim in 00, no numbers held.")
