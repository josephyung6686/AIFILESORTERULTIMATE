#!/usr/bin/env python3
"""Checks for the 08-sensitivity-detector catalogue.

Asserts, mechanically:
  1. the three JSON files parse and carry no numeric value anywhere (bools allowed) —
     every count is a named injected slot, never a number;
  2. ids are unique across all three files (entries, refused, uncertain);
  3. every detector rule carries a non-empty never_alone;
  4. basis is closed (detector | safety_domain); basis=detector rules carry a kind from
     the closed kind vocabulary and a non-empty evidence_refs_shape; basis=safety_domain
     rules carry kind null, a safety_domain from 00's four, and protected true;
  5. every one of 00's five protected kinds has at least one rule;
  6. handling-class vocabulary is exactly P7's five tokens; near-miss respellings fail;
  7. every identifier class names a transform that exists; always_local classes use a
     dropping transform; every transform preserves the two context fields;
  8. provenance vocabulary is exactly design | inference | proposal;
  9. every injected-slot name referenced anywhere resolves to a declared slot;
 10. no fabricated quotes: every structured design_cite quote, and every long quoted
     span embedded in prose (in the JSONs and the companion .md files), exists verbatim
     (whitespace-normalized) in its source corpus.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]  # repo root: planning/deferred-catalogues/08-.../ -> repo

SOURCES = {
    "00": ROOT / "planning/00-database-agent-product-design.md",
    "01": ROOT / "planning/01-product-design-structured.md",
    "P7 SPEC": ROOT / "planning/parts/P7-privacy-consent-gate/SPEC.md",
    "P5 SPEC": ROOT / "planning/parts/P5-extractors/SPEC.md",
    "CONNECTION": ROOT / "planning/domains/CONNECTION.md",
    "22": ROOT / "planning/22-p1-p7-connection-contract.md",
    "long_tail": ROOT / "src/extractors/long_tail.py",
    "NEEDS-JOSEPH-overnight": ROOT / "planning/overnight/NEEDS-JOSEPH.md",
}

HANDLING_CLASSES = {
    "public_low",
    "personal_non_sensitive",
    "sensitive_personal",
    "highly_sensitive_credential_bearing",
    "unreadable_unclassified",
}
# Respellings that would be the two-vocabularies defect wearing a plausible name.
CLASS_NEAR_MISSES = [
    "public-low", "publiclow", "personal_nonsensitive", "non_sensitive_personal",
    "sensitive-personal", "highly_sensitive_credential", "credential_bearing_only",
    "highly_sensitive_or_credential_bearing", "unreadable-unclassified",
    "unclassified_unreadable",
]
DESIGN_KINDS = {"passport", "tax_statement", "medical_document",
                "authentication_key", "account_record"}
SAFETY_DOMAINS = {"finance", "identity", "medical", "legal"}
PROVENANCE = {"design", "inference", "proposal"}
BASES = {"detector", "safety_domain"}
DROPPING_TRANSFORMS = {"drop_span", "drop_gps"}
QUOTE_MIN_CHARS = 40  # a checker constant, not catalogue data

problems: list[str] = []


def norm(s: str) -> str:
    return re.sub(r"\s+", " ", s)


def load(name: str) -> dict:
    return json.loads((HERE / name).read_text(encoding="utf-8"))


def walk_strings(node, out: list[str]) -> None:
    if isinstance(node, str):
        out.append(node)
    elif isinstance(node, dict):
        for v in node.values():
            walk_strings(v, out)
    elif isinstance(node, list):
        for v in node:
            walk_strings(v, out)


def walk_numbers(node, path: str) -> None:
    if isinstance(node, bool):
        return
    if isinstance(node, (int, float)):
        problems.append(f"numeric value {node!r} at {path} — thresholds are injected slots, never numbers")
    elif isinstance(node, dict):
        for k, v in node.items():
            walk_numbers(v, f"{path}.{k}")
    elif isinstance(node, list):
        for i, v in enumerate(node):
            walk_numbers(v, f"{path}[{i}]")


def collect_cites(node, out: list[dict]) -> None:
    if isinstance(node, dict):
        if "quote" in node and "source" in node and isinstance(node.get("quote"), str):
            out.append(node)
        for v in node.values():
            collect_cites(v, out)
    elif isinstance(node, list):
        for v in node:
            collect_cites(v, out)


def main() -> int:
    rules = load("01-detector-rules.json")
    classes = load("02-identifier-classes.json")
    transforms = load("03-redaction-transforms.json")
    catalogues = {"01": rules, "02": classes, "03": transforms}

    corpora = {k: norm(p.read_text(encoding="utf-8")) for k, p in SOURCES.items()}

    # 1. no numbers anywhere
    for name, cat in catalogues.items():
        walk_numbers(cat, name)

    # 2. unique ids across all three files
    seen: dict[str, str] = {}
    def note_id(i: str, where: str) -> None:
        if i in seen:
            problems.append(f"duplicate id {i!r} in {where} (already in {seen[i]})")
        seen[i] = where
    for e in rules["entries"] + rules["refused"] + rules["uncertain"]:
        note_id(e["id"], "01")
    for e in classes["entries"]:
        note_id(e["class_id"], "02")
    for e in classes.get("refused", []) + classes.get("uncertain", []):
        note_id(e["id"], "02")
    for e in transforms["entries"]:
        note_id(e["transform_id"], "03")
    for e in transforms.get("refused", []) + transforms.get("uncertain", []):
        note_id(e["id"], "03")

    # kind vocabulary
    proposed_kinds = {k["kind"] for k in rules["kinds"]["proposed"]}
    design_kinds = {k["kind"] for k in rules["kinds"]["design"]}
    if design_kinds != DESIGN_KINDS:
        problems.append(f"design kinds are {sorted(design_kinds)}, expected 00's five {sorted(DESIGN_KINDS)}")
    all_kinds = design_kinds | proposed_kinds

    # 3-5. per-rule checks
    kinds_with_rules: set[str] = set()
    for e in rules["entries"]:
        rid = e["id"]
        if not e.get("never_alone"):
            problems.append(f"{rid}: never_alone missing or empty")
        basis = e.get("basis")
        if basis not in BASES:
            problems.append(f"{rid}: basis {basis!r} not in {sorted(BASES)}")
        if basis == "detector":
            if e.get("kind") not in all_kinds:
                problems.append(f"{rid}: detector rule kind {e.get('kind')!r} not in kind vocabulary")
            else:
                kinds_with_rules.add(e["kind"])
            if not e.get("evidence_refs_shape"):
                problems.append(f"{rid}: basis=detector requires non-empty evidence_refs_shape (P7 SPEC)")
        if basis == "safety_domain":
            if e.get("kind") is not None:
                problems.append(f"{rid}: basis=safety_domain rules carry kind null")
            if e.get("safety_domain") not in SAFETY_DOMAINS:
                problems.append(f"{rid}: safety_domain {e.get('safety_domain')!r} not one of 00's four")
            if e.get("protected") is not True:
                problems.append(f"{rid}: safety-domain activation protects; protected must be true")
        if not isinstance(e.get("protected"), bool):
            problems.append(f"{rid}: protected must be a boolean")
        for key in ("provenance", "ceiling_provenance"):
            if key in e and e[key] not in PROVENANCE:
                problems.append(f"{rid}: {key} {e[key]!r} not in {sorted(PROVENANCE)}")
        hc = e.get("handling_class_ceiling")
        if hc not in HANDLING_CLASSES:
            problems.append(f"{rid}: handling_class_ceiling {hc!r} not one of P7's five")
    for kind in DESIGN_KINDS - kinds_with_rules:
        problems.append(f"00 protected kind {kind!r} has no detector rule — done-when violated")

    # kinds.proposed provenance
    for k in rules["kinds"]["proposed"]:
        if k.get("provenance") != "proposal":
            problems.append(f"proposed kind {k['kind']}: provenance must be 'proposal'")

    # 6. handling-class vocabulary closure + near-miss respellings
    all_strings: list[str] = []
    for cat in catalogues.values():
        walk_strings(cat, all_strings)
    joined = "\n".join(all_strings)
    for miss in CLASS_NEAR_MISSES:
        # Token-boundary match: a near-miss inside a LONGER legitimate token is not a
        # respelling (highly_sensitive_credential_bearing must not trip its own prefix).
        if re.search(r"(?<![a-z_])" + re.escape(miss) + r"(?![a-z_])", joined):
            problems.append(f"near-miss handling-class respelling {miss!r} found — vocabulary is P7's five only")

    # 7. identifier classes and transforms
    transform_ids = {t["transform_id"] for t in transforms["entries"]}
    for c in classes["entries"]:
        cid = c["class_id"]
        if c.get("transform_id") not in transform_ids:
            problems.append(f"{cid}: transform_id {c.get('transform_id')!r} does not exist in 03")
        if not isinstance(c.get("always_local"), bool) or not isinstance(c.get("jurisdiction_dependent"), bool):
            problems.append(f"{cid}: always_local and jurisdiction_dependent must be booleans")
        if c.get("always_local") and c.get("transform_id") not in DROPPING_TRANSFORMS:
            problems.append(f"{cid}: always_local classes must use a dropping transform, got {c.get('transform_id')!r}")
        if c.get("provenance") not in PROVENANCE:
            problems.append(f"{cid}: provenance {c.get('provenance')!r} invalid")
        if not c.get("why_this_is_an_identifier_not_a_fact"):
            problems.append(f"{cid}: missing why_this_is_an_identifier_not_a_fact")
        if not c.get("examples"):
            problems.append(f"{cid}: examples required (fake, never real PII)")
    for t in transforms["entries"]:
        tid = t["transform_id"]
        preserves = t.get("preserves", [])
        joined_p = " ".join(preserves)
        if "context_before" not in joined_p or "context_after" not in joined_p:
            problems.append(f"{tid}: preserves must name context_before and context_after (M5)")
        if t.get("reversible_locally") is not True:
            problems.append(f"{tid}: reversible_locally must be true — the original stays in local SQLite")
        if not t.get("never_does"):
            problems.append(f"{tid}: never_does missing or empty")
        if t.get("provenance") not in PROVENANCE:
            problems.append(f"{tid}: provenance {t.get('provenance')!r} invalid")

    # 9. injected-slot references resolve
    declared = {s["slot"] for s in rules.get("injected_slots", [])} | \
               {s["slot"] for s in transforms.get("injected_slots", [])}
    referenced = set(re.findall(r"\b(?:min_[a-z_]+|redaction_keep_n|[a-z][a-z_]*_gazetteer|account_locator_patterns)\b",
                                joined))
    for slot in sorted(referenced - declared):
        problems.append(f"referenced injected slot {slot!r} is not declared in any injected_slots registry")

    # 10. quote verification — structured cites first
    cites: list[dict] = []
    for cat in catalogues.values():
        collect_cites(cat, cites)
    for c in cites:
        src, quote = c["source"], c["quote"]
        if src not in corpora:
            problems.append(f"cite names unknown source {src!r}")
        elif norm(quote) not in corpora[src]:
            problems.append(f"FABRICATED QUOTE (source {src}): {quote[:90]!r}")

    # 10b. long quoted spans embedded in prose, JSON and companion .md files.
    # Scanned PER LINE: a real quotation is opened and closed by its author on one
    # line of prose, while a cross-line "pair" is almost always a closing mark from
    # one short phrase aliased against the opening mark of the next.
    prose_texts = list(all_strings)
    for md in HERE.glob("*.md"):
        prose_texts.append(md.read_text(encoding="utf-8"))
    everything = " ".join(corpora.values())
    for text in prose_texts:
        for line in text.splitlines():
            for span in re.findall(r'"([^"]{%d,})"' % QUOTE_MIN_CHARS, line):
                if norm(span) not in everything:
                    problems.append(f"FABRICATED QUOTE (embedded): {span[:90]!r}")

    if problems:
        for p in problems:
            print(f"PROBLEM: {p}")
        print(f"\n{len(problems)} problem(s)")
        return 1
    n_rules = len(rules["entries"])
    n_classes = len(classes["entries"])
    n_transforms = len(transforms["entries"])
    print(f"OK: {n_rules} rules ({len(kinds_with_rules)} kinds with coverage), "
          f"{n_classes} identifier classes, {n_transforms} transforms, "
          f"{len(cites)} structured quotes verified, 0 problems")
    return 0


if __name__ == "__main__":
    sys.exit(main())
