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

#: R0 (CONNECTION.md) — two roster kinds and a CLOSED edge vocabulary. The kind-scoped
#: checks below fire only on entries that carry `kind`, so the pre-R0 574 (which lack it
#: and are superseded by R1's roster, not migrated) gain no new findings from this delta.
KINDS = {"schema", "template"}
#: Known-bad spellings, each with a specific message: edges CONNECTION.md §5 rejects by
#: name (`related_to`, `broader`, `narrower`, `similar_to`), the split/dropped forms
#: (`parent_of`/`child_of`, `safety_for`), `role_split` (canonical field list only) and
#: `shares_field` (DERIVED from canonical field references, never authored). This list
#: fires on every entry, legacy included — but a blocklist cannot enforce "closed", so
#: on kind-bearing entries ALLOWED_ENTRY_KEYS below is the real fence.
FORBIDDEN_EDGE_KEYS = {"shares_field", "related_to", "parent_of", "child_of",
                       "safety_for", "broader", "narrower", "similar_to", "role_split"}
SCHEMA_ONLY_KEYS = {"also_holds_with", "file_kind_plausible", "is_safety_domain"}
TEMPLATE_ONLY_KEYS = {"uses_schema", "parent_id"}
#: The CLOSED set of legal entry keys on kind-bearing rows (CONNECTION.md §5,
#: _CONTRACT.md rule 14). "Closed" is enforced by construction: any key not in this set
#: is a finding, so a novel edge (`activates_with`, ...) cannot sail past a blocklist of
#: known-bad spellings. A new edge is a revision of CONNECTION.md, then of this set.
ALLOWED_ENTRY_KEYS = set(REQUIRED) | {
    "design_cite", "sensitivity_why", "open_question",   # the legacy contract's optionals
    "kind", "uses_schema", "parent_id", "also_holds_with",
    "file_kind_plausible", "falls_through_to", "is_safety_domain"}
#: §7.3's nine residual template names, 00's own spelling. Residuals are P10/P11's and
#: have no id in this namespace; `falls_through_to` names them as strings.
RESIDUAL_TEMPLATES = {
    "Temporary Screenshots", "One-Off Images", "Reference Clips", "Independent Records",
    "Receipts and Confirmations", "Reading Inbox", "Review Later",
    "Unsupported or Encrypted", "Protected Records"}
#: P5's closed fourteen, imported so this gate never re-spells them. On import failure
#: the membership check is skipped (never crashed) — the vocabulary stays single-homed.
try:
    sys.path.insert(0, str(HERE.parent.parent / "src"))
    from evidence_shape.vocabulary import SOURCE_TYPES
except Exception:
    SOURCE_TYPES = None
#: R1a's canonical field list (CONNECTION.md §6). Until it lands, the resolution checks
#: that need it are SKIPPED, not failed — R0 ships the contract before the list.
CANONICAL_FIELDS_PATH = HERE / "canonical_fields.json"


def edge_targets(value):
    """Ids named by a serialized edge list: bare strings or dicts keying the target."""
    out = []
    for item in value if isinstance(value, list) else [value]:
        if isinstance(item, str):
            out.append(item)
        elif isinstance(item, dict):
            for key in ("schema", "domain", "template", "id"):
                if isinstance(item.get(key), str):
                    out.append(item[key])
                    break
    return out


#: A citation quotes the design. JSON's own delimiters are not quotation marks, so
#: only CURLY quotes and backticked spans inside a string value count. The first
#: version of this check scanned the raw file for `"..."` and matched every JSON
#: string in the catalogue: 1,870 false positives, zero findings. Scanning text for a
#: token has now produced a false result nine times in this project.
INNER_QUOTE = re.compile(r'“([^”]{25,})”|\'\'([^\']{25,})\'\'')


def snake(key: str) -> str:
    """D6's spelling. Lowercase, word breaks folded to `_`.

    The same fold `extractors.ocr.extractor_name_for` applies to a provider name, and
    for the same reason: two spellings of one key are two join handles.
    """
    return re.sub(r"[ \-]+", "_", key.strip().lower())


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

        # D6, ratified 2026-08-21: one spelling for a stored field key.
        #
        # This catalogue shipped with 966 spaced keys and 959 snake_case ones side by
        # side -- 131 of them the SAME key spelled two ways, which is one concept in
        # two vocabularies, the most expensive defect on this project's own list. The
        # key is a stored join handle: it lands in a fact row, in §3.4's cache key and
        # in a template's branch order, so two spellings are two columns.
        declared = set()
        for field in e.get("schema") or []:
            key = field.get("field")
            if not isinstance(key, str) or key != snake(key):
                problems.append(f"{tag}: field key {key!r} is not snake_case (D6)")
            declared.add(key)

        # A template dimension MUST be a field the same domain's schema declares.
        #
        # A domain is a schema plus a template -- the allow-list §3.6 validates
        # against and the menu §5.3 draws branches from. A dimension naming a field
        # the schema does not legitimise opens a tree level no fact can ever fill:
        # §3.6's validator rejects the value, so the branch is empty by construction.
        # This check did not exist and 566 of 1,648 dimensions failed it on the day
        # it was added -- every one of them in a catalogue this same gate had just
        # called "0 problems". The gate only ever asked whether the template EXISTED.
        for dim in tmpl.get("dimension_order") or []:
            if not isinstance(dim, str) or dim != snake(dim):
                problems.append(f"{tag}: dimension {dim!r} is not snake_case (D6)")
            elif dim not in declared:
                problems.append(
                    f"{tag}: template branches on {dim!r}, which this domain's "
                    "schema does not declare — §3.6 would reject every value for it")
        # R0 (CONNECTION.md §5): closed edges, two kinds. Kind-scoped rules fire only on
        # entries that opted into the new shape by carrying `kind`.
        for bad_key in FORBIDDEN_EDGE_KEYS & set(e):
            problems.append(f"{tag}: `{bad_key}` is not in the closed edge vocabulary — "
                            "a new edge is a revision of CONNECTION.md, and "
                            "`shares_field` is derived, never authored")
        if "kind" in e:
            # Closed means closed: on rows that opted into the new shape, ANY key
            # outside ALLOWED_ENTRY_KEYS is a finding — enumerating known-bad spellings
            # would let every novel edge (`similar_to`, `activates_with`, ...) through.
            for bad_key in sorted(set(e) - ALLOWED_ENTRY_KEYS - FORBIDDEN_EDGE_KEYS):
                problems.append(f"{tag}: unrecognized key `{bad_key}` — the entry-key "
                                "vocabulary on kind-bearing rows is closed "
                                "(CONNECTION.md §5); a new edge or field is a revision "
                                "of CONNECTION.md, not an authoring choice")
            kind = e.get("kind")
            if kind not in KINDS:
                problems.append(f"{tag}: kind {kind!r} not in {KINDS}")
            if kind == "template":
                if not isinstance(e.get("uses_schema"), str) or not e.get("uses_schema"):
                    problems.append(f"{tag}: kind=template with no `uses_schema` — a "
                                    "template points at exactly one schema")
                for key in SCHEMA_ONLY_KEYS & set(e):
                    problems.append(f"{tag}: `{key}` is schema-only, not legal on a template")
            if kind == "schema":
                for key in TEMPLATE_ONLY_KEYS & set(e):
                    problems.append(f"{tag}: `{key}` is template-only, not legal on a schema")
                if "is_safety_domain" in e and not isinstance(e["is_safety_domain"], bool):
                    problems.append(f"{tag}: is_safety_domain must be a bool")
            for st in e.get("file_kind_plausible") or []:
                if not isinstance(st, str):
                    problems.append(f"{tag}: file_kind_plausible member {st!r} is not a string")
                elif st.startswith("."):
                    pass  # a literal extension
                elif SOURCE_TYPES is not None and st not in SOURCE_TYPES:
                    problems.append(f"{tag}: file_kind_plausible names {st!r}, which is "
                                    "neither an extension nor one of P5's SOURCE_TYPES")
            for target in e.get("falls_through_to") or []:
                name = target.get("residual_template") if isinstance(target, dict) else target
                if name not in RESIDUAL_TEMPLATES:
                    problems.append(f"{tag}: falls_through_to names {name!r}, which is not "
                                    "one of §7.3's nine residual templates")
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


def cross_file(files):
    """Checks no single file can make. Fifteen authors, one namespace."""
    problems = []
    owner, supers = {}, {}
    for path in files:
        try:
            doc = json.loads(path.read_text())
        except Exception:
            continue
        sup = doc.get("supercategory")
        for e in doc.get("entries", []):
            eid = e.get("id")
            if eid in owner:
                problems.append(f"id {eid!r} is claimed by {owner[eid]} and {path.name}")
            owner[eid] = path.name
            if e.get("supercategory") != sup:
                problems.append(f"{path.name} {eid}: entry supercategory "
                                f"{e.get('supercategory')!r} != file's {sup!r}")
            supers.setdefault(sup, 0)
            supers[sup] += 1
    # A collision that names a domain nobody authored is a dangling promise: §4.8's
    # "an application packet does not silently absorb a document with a conflicting
    # target institution" only works if both sides of the pair exist.
    for path in files:
        try:
            doc = json.loads(path.read_text())
        except Exception:
            continue
        for e in doc.get("entries", []):
            for c in e.get("collides_with") or []:
                # A collision may name a DOMAIN or a §7 residual template, and they
                # are different kinds of thing: a residual template is P10/P11's
                # (§7.2–7.4), not a fact schema, so it has no id in this namespace
                # and must not be checked against one. The contract originally had
                # only `domain`, so two authors put a template description there and
                # the gate read it as a broken id — my gap, not theirs.
                if isinstance(c, dict) and "residual_template" in c:
                    continue
                other = c.get("domain") if isinstance(c, dict) else c
                if isinstance(other, str) and other and other not in owner:
                    problems.append(f"{path.name} {e.get('id')}: collides_with names "
                                    f"{other!r}, which no catalogue defines")
    problems.extend(connection_checks(files, owner))
    return problems, owner, supers


def connection_checks(files, owner):
    """R0 (CONNECTION.md §5): joins, reciprocity, cycles — kind-bearing entries only.

    Scoped to entries carrying `kind` so the legacy 574 keep their exact pre-delta
    finding count until R1 replaces them. What WILL fail on migration is documented in
    CONNECTION.md's appendix; this gate is that documentation made executable.
    """
    problems = []
    entries = {}
    for path in files:
        try:
            doc = json.loads(path.read_text())
        except Exception:
            continue
        for e in doc.get("entries", []):
            if isinstance(e.get("id"), str):
                entries[e["id"]] = e
    kinds = {eid: e.get("kind") for eid, e in entries.items() if "kind" in e}

    def kinded(eid):
        return eid in kinds

    for eid, e in entries.items():
        if "kind" not in e:
            continue
        # `uses_schema` resolves, and to a schema.
        target = e.get("uses_schema")
        if isinstance(target, str) and target:
            if target not in entries:
                problems.append(f"{eid}: uses_schema names {target!r}, which no catalogue defines")
            elif kinds.get(target) != "schema":
                problems.append(f"{eid}: uses_schema names {target!r}, which is not kind=schema")
        # `parent_id` is browse-only among templates; naming a schema is the smuggled
        # schema-tree (CONNECTION.md §1).
        parent = e.get("parent_id")
        if isinstance(parent, str) and parent:
            if parent not in entries:
                problems.append(f"{eid}: parent_id names {parent!r}, which no catalogue defines")
            elif kinds.get(parent) != "template":
                problems.append(f"{eid}: parent_id names {parent!r}, which is not kind=template "
                                "— browse parents join templates only")
        # `also_holds_with`: schemas only, targets resolve, reciprocal.
        for other in edge_targets(e.get("also_holds_with") or []):
            if other not in entries:
                problems.append(f"{eid}: also_holds_with names {other!r}, "
                                "which no catalogue defines")
                continue
            if kinds.get(other) != "schema" or kinds.get(eid) != "schema":
                problems.append(f"{eid}: also_holds_with joins {other!r} — both ends must be "
                                "kind=schema (co-activation is a schema relation)")
            if kinded(other) and eid not in edge_targets(entries[other].get("also_holds_with") or []):
                problems.append(f"{eid}: also_holds_with names {other!r} with no reciprocal edge")
        # `collides_with` among kind-bearing entries: same kind, reciprocal.
        collisions = [c for c in e.get("collides_with") or []
                      if not (isinstance(c, dict) and "residual_template" in c)]
        for other in edge_targets(collisions):
            if other not in entries or not kinded(other):
                continue  # dangling ids are already reported by cross_file
            if kinds.get(other) != kinds.get(eid):
                problems.append(f"{eid}: collides_with {other!r} crosses kinds "
                                f"({kinds.get(eid)} vs {kinds.get(other)}) — a collision "
                                "joins two schemas or two templates, never one of each")
            if eid not in edge_targets([c for c in entries[other].get("collides_with") or []
                                        if not (isinstance(c, dict) and "residual_template" in c)]):
                problems.append(f"{eid}: collides_with names {other!r} with no reciprocal edge")
            # A pair may carry BOTH collides_with and also_holds_with — explicitly
            # allowed (CONNECTION.md §5 invariant 1) — but then the collision must name
            # its discriminating signal.
            if other in edge_targets(e.get("also_holds_with") or []):
                signals = [c.get("signal") for c in collisions
                           if isinstance(c, dict) and other in edge_targets([c])]
                if not any(isinstance(s, str) and s.strip() for s in signals):
                    problems.append(f"{eid}: pair with {other!r} carries collides_with AND "
                                    "also_holds_with, but the collision names no `signal` "
                                    "discriminating the shared evidence")

    # Cycles in the browse tree. Parents optional, roots many — but no cycle.
    parent_of = {eid: e["parent_id"] for eid, e in entries.items()
                 if isinstance(e.get("parent_id"), str) and e["parent_id"] in entries}
    for start in parent_of:
        seen, node = set(), start
        while node in parent_of:
            if node in seen:
                problems.append(f"{start}: parent_id chain contains a cycle through {node!r}")
                break
            seen.add(node)
            node = parent_of[node]

    # Canonical field resolution — SKIPPED until R1a lands the list (CONNECTION.md §6).
    if CANONICAL_FIELDS_PATH.exists():
        try:
            canonical = json.loads(CANONICAL_FIELDS_PATH.read_text())
            keys = {f.get("key") for f in canonical.get("fields", []) if isinstance(f, dict)}
        except Exception as exc:
            problems.append(f"canonical_fields.json does not parse — {exc}")
            keys = None
        if keys:
            for eid, e in entries.items():
                if "kind" not in e:
                    continue
                for field in e.get("schema") or []:
                    key = field.get("field") if isinstance(field, dict) else field
                    if isinstance(key, str) and key not in keys:
                        problems.append(f"{eid}: schema field {key!r} does not resolve to "
                                        "canonical_fields.json — no private field names")
            # role_split lives in the canonical list and is reciprocal there.
            by_key = {f.get("key"): f for f in canonical.get("fields", [])
                      if isinstance(f, dict)}
            for key, row in by_key.items():
                for other in row.get("role_split_with") or []:
                    if other not in by_key:
                        problems.append(f"canonical_fields.json {key}: role_split_with names "
                                        f"{other!r}, which the list does not define")
                    elif key not in (by_key[other].get("role_split_with") or []):
                        problems.append(f"canonical_fields.json {key}: role_split_with "
                                        f"{other!r} has no reciprocal entry")
    return problems


def main():
    #: `canonical_fields.json` is the one-table field list (CONNECTION.md §6), not a
    #: catalogue slice — it is read by connection_checks, never scanned as entries.
    files = sorted(p for p in HERE.glob("*.json")
                   if not p.name.startswith("_") and p.name != "canonical_fields.json")
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
    problems, owner, supers = cross_file(files)
    print(f"\n{len(files)} files, {total} entries, {fails} in-file problems")
    print(f"cross-file: {len(owner)} unique ids, {len(problems)} problems")
    for pr in problems[:12]:
        print(f"  - {pr}")
    if len(problems) > 12:
        print(f"  … and {len(problems) - 12} more")
    return 1 if (fails or problems) else 0


if __name__ == "__main__":
    sys.exit(main())
