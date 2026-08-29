#!/usr/bin/env python3
"""Catalogue 11 — jurisdiction-value checks.

Every invariant _SCHEMA.md marks mechanical, made executable:

  1.  the field/value split is mechanical: no field_key in this directory (or in
      planning/domains/canonical_fields.json) is `jurisdiction`, ends `_jurisdiction`,
      or starts `jurisdiction_`; no JSON here contains a `dimension_order` key at all —
      so P10 cannot discover a jurisdiction dimension from these files;
  2.  every value row points at a field_key that resolves in canonical_fields.json,
      or its file is marked `field_pending_R1` with a named `pending_reason`;
  3.  gate_label rows carry `field_key: null` plus `why_no_field_key`, and non-empty
      `gate_slots`;
  4.  `safety_relevant` is a bool on every row; when true, `detector_hook` resolves to an
      entry id in ../08-sensitivity-detector/01-detector-rules.json; no value row carries
      a `pattern` key (this catalogue writes no regex);
  5.  every `gate_slots` member is a slot catalogue 08 declares with an R5 owner;
  6.  every `quote` under any *cite key exists verbatim (whitespace-normalized) in its
      named source file — fabricated quotations are a test failure here;
  7.  no int or float anywhere in the JSONs (booleans excepted; thresholds are named
      null slots) — _CONTRACT.md rule 3 made mechanical;
  8.  closed vocabularies (provenance, source_kind, row_kind, statuses, field_key_status);
  9.  example_true matches its own row and example_false matches no row in its file,
      under the reference word-boundary matcher; adversarial fixtures: `W-2` matches
      nowhere in "SW-2000"/"W-2000", `P60` nowhere in "P600"/"UP60", lowercase "w-2"
      never matches the case-sensitive alias;
 10.  pack manifests: statuses legal; a deployable pack is single-jurisdiction and every
      row carries its tag; `00-example` stays `shape_example`; **no pack may claim `v1`
      until Joseph's "which jurisdiction" answer is recorded** (this check fails on any
      `v1` — flipping it is part of PACKS.md's ratification protocol, edited together);
      `unsupported_region_copy` present in every manifest, non-empty, provenance proposal;
 11.  00's Michaelmas pattern is not deleted: "Michaelmas Term 2024" is verbatim in 00,
      R6's term-pattern file still carries a Michaelmas entry, and any row here that
      mentions Michaelmas must be provenance `design` (none does today — the token is
      R6's, and this catalogue must never respell that ownership).

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
    "01": PLANNING / "01-product-design-structured.md",
    "CONNECTION": PLANNING / "domains" / "CONNECTION.md",
    "_CONTRACT": PLANNING / "domains" / "_CONTRACT.md",
    "DECISION-BRIEF": PLANNING / "overnight" / "council" / "DECISION-BRIEF.md",
    "seat-design-reading": PLANNING / "overnight" / "council" / "seat-design-reading.md",
    "seat-what-goes-wrong": PLANNING / "overnight" / "council" / "seat-what-goes-wrong.md",
    "P7-SPEC": PLANNING / "parts" / "P7-privacy-consent-gate" / "SPEC.md",
}

CANONICAL_FIELDS = PLANNING / "domains" / "canonical_fields.json"
R2_RULES = HERE.parent / "08-sensitivity-detector" / "01-detector-rules.json"
R6_TERMS = HERE.parent / "12-academic-capture-patterns" / "03-academic-term-patterns.json"

PROVENANCE = {"design", "inference", "proposal"}
SOURCE_KIND = {"design_example", "overnight_prose", "official_list", "user_approved", "proposal"}
ROW_KIND = {"value", "gate_label"}
ROW_STATUS = {"seed"}
FILE_STATUS = {"seed", "schema_only", "shape_example"}
PACK_STATUS = {"shape_example", "candidate", "v1"}
FIELD_KEY_STATUS = {"resolves", "field_pending_R1"}
JURISDICTION_TAG = re.compile(r"^[a-z][a-z0-9-]*$")

failures: list[str] = []


def fail(msg: str) -> None:
    failures.append(msg)


# ---------------------------------------------------------------- reference matcher

WORD = "A-Za-z0-9_"


def find_alias(alias: str, text: str, case_sensitive: bool) -> bool:
    """Word-boundary phrase match, same semantics as ../10-gazetteers/check.py: the
    character before the first and after the last matched character (if any) is not in
    [A-Za-z0-9_]. Hyphens inside an alias (W-2) are part of the phrase, not boundaries."""
    pattern = rf"(?<![{WORD}]){re.escape(alias)}(?![{WORD}])"
    flags = 0 if case_sensitive else re.IGNORECASE
    return re.search(pattern, text, flags) is not None


def row_matches(row: dict, text: str) -> bool:
    surfaces = [(row.get("label", ""), True)]
    # label matching uses the strictest casing among its aliases if the label itself is
    # also listed as an alias; otherwise case-sensitive by default for safety.
    for a in row.get("aliases", []):
        surfaces.append((a.get("alias", ""), bool(a.get("case_sensitive", False))))
        if a.get("alias") == row.get("label"):
            surfaces[0] = (row.get("label", ""), bool(a.get("case_sensitive", False)))
    return any(find_alias(s, text, cs) for s, cs in surfaces if s)


# ---------------------------------------------------------------- helpers

def norm_ws(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()


def walk_no_numbers(obj, path: str, fname: str) -> None:
    if isinstance(obj, bool):
        return
    if isinstance(obj, (int, float)):
        fail(f"{fname}: numeric JSON value at {path} — rule N forbids int/float anywhere")
    elif isinstance(obj, dict):
        for k, v in obj.items():
            walk_no_numbers(v, f"{path}.{k}", fname)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            walk_no_numbers(v, f"{path}[{i}]", fname)


def walk_collect(obj, key: str, path: str = "$"):
    """Yield (path, value) for every occurrence of dict key `key`."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k == key:
                yield (f"{path}.{k}", v)
            yield from walk_collect(v, key, f"{path}.{k}")
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from walk_collect(v, key, f"{path}[{i}]")


def jurisdictionish_key(k: str) -> bool:
    return k == "jurisdiction" or k.endswith("_jurisdiction") or k.startswith("jurisdiction_")


# ---------------------------------------------------------------- load fixed inputs

source_texts: dict[str, str] = {}
for name, p in SOURCES.items():
    if not p.exists():
        fail(f"source file missing: {name} -> {p}")
    else:
        source_texts[name] = norm_ws(p.read_text(encoding="utf-8"))

try:
    canonical = json.loads(CANONICAL_FIELDS.read_text(encoding="utf-8"))
    canonical_keys = {f["key"] for f in canonical["fields"]}
except Exception as e:  # noqa: BLE001
    fail(f"cannot load canonical_fields.json: {e}")
    canonical_keys = set()

for k in canonical_keys:
    if jurisdictionish_key(k):
        fail(f"canonical_fields.json carries a jurisdiction field key: {k} — D4 forbids it")

try:
    r2 = json.loads(R2_RULES.read_text(encoding="utf-8"))
    r2_ids = {e["id"] for e in r2["entries"]}
    r2_r5_slots = {
        s["slot"] for s in r2.get("injected_slots", [])
        if isinstance(s, dict) and "R5" in str(s.get("owner", ""))
    }
except Exception as e:  # noqa: BLE001
    fail(f"cannot load catalogue 08 rules: {e}")
    r2_ids, r2_r5_slots = set(), set()

if r2_r5_slots and r2_r5_slots != {
    "tax_form_identifier_gazetteer", "national_id_label_gazetteer",
    "account_locator_patterns", "legal_caption_gazetteer",
}:
    fail(f"catalogue 08's R5-owned slot set changed: {sorted(r2_r5_slots)} — update _SCHEMA.md and this check together")

# Michaelmas guards (invariant 11)
if "Michaelmas Term 2024" not in source_texts.get("00", ""):
    fail("00 no longer contains 'Michaelmas Term 2024' — the design's required pattern must survive any pack choice")
try:
    r6_text = R6_TERMS.read_text(encoding="utf-8")
    if "Michaelmas" not in r6_text:
        fail("R6's 03-academic-term-patterns.json no longer carries a Michaelmas entry")
except Exception as e:  # noqa: BLE001
    fail(f"cannot read R6 term patterns: {e}")

# ---------------------------------------------------------------- load this catalogue

pack_dirs = sorted(d for d in HERE.iterdir() if d.is_dir() and not d.name.startswith("__"))
if not pack_dirs:
    fail("no pack directories found — the 00-example shape seed must exist")

v1_count = 0

for pack_dir in pack_dirs:
    manifest_path = pack_dir / "_pack.json"
    if not manifest_path.exists():
        fail(f"{pack_dir.name}: missing _pack.json manifest")
        continue
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except Exception as e:  # noqa: BLE001
        fail(f"{manifest_path}: unparseable JSON: {e}")
        continue

    walk_no_numbers(manifest, "$", str(manifest_path))
    for path, _ in walk_collect(manifest, "dimension_order"):
        fail(f"{pack_dir.name}/_pack.json: contains a dimension_order key at {path} — inexpressible here by contract")

    if manifest.get("pack_id") != pack_dir.name:
        fail(f"{pack_dir.name}: pack_id {manifest.get('pack_id')!r} != directory name")
    status = manifest.get("status")
    if status not in PACK_STATUS:
        fail(f"{pack_dir.name}: pack status {status!r} not in {sorted(PACK_STATUS)}")
    if status == "v1":
        v1_count += 1
        fail(
            f"{pack_dir.name}: claims status v1, but 'which jurisdiction' is not ratified in "
            "this catalogue's recorded state. Flipping to v1 is PACKS.md's ratification "
            "protocol: record Joseph's answer there, then relax this assertion in the same "
            "edit."
        )
    jur = manifest.get("jurisdiction")
    if status == "shape_example":
        if jur is not None:
            fail(f"{pack_dir.name}: a shape_example pack must have jurisdiction null")
    else:
        if not (isinstance(jur, str) and JURISDICTION_TAG.match(jur)):
            fail(f"{pack_dir.name}: deployable pack needs a single lowercase jurisdiction tag, got {jur!r}")

    urc = manifest.get("unsupported_region_copy")
    if not isinstance(urc, dict) or not norm_ws(str(urc.get("text", ""))):
        fail(f"{pack_dir.name}: unsupported_region_copy missing or empty — every manifest carries the slot")
    elif urc.get("provenance") != "proposal":
        fail(f"{pack_dir.name}: unsupported_region_copy.provenance must stay 'proposal' until Joseph ratifies wording")

    listed = set(manifest.get("files", []))
    actual = {p.name for p in pack_dir.glob("*.json")} - {"_pack.json"}
    if listed != actual:
        fail(f"{pack_dir.name}: manifest files {sorted(listed)} != on-disk value files {sorted(actual)}")

    proj = manifest.get("gate_slot_projections")
    if not isinstance(proj, dict) or set(proj) != r2_r5_slots and r2_r5_slots:
        fail(f"{pack_dir.name}: gate_slot_projections must cover exactly catalogue 08's four R5 slots")

    # ---------------- value files
    for vf in sorted(pack_dir.glob("*.json")):
        if vf.name == "_pack.json":
            continue
        try:
            data = json.loads(vf.read_text(encoding="utf-8"))
        except Exception as e:  # noqa: BLE001
            fail(f"{vf}: unparseable JSON: {e}")
            continue

        walk_no_numbers(data, "$", str(vf))

        for path, _ in walk_collect(data, "dimension_order"):
            fail(f"{vf.name}: contains a dimension_order key at {path} — inexpressible here by contract")

        fkey = data.get("field_key")
        fstat = data.get("field_key_status")
        if fstat not in FIELD_KEY_STATUS:
            fail(f"{vf.name}: field_key_status {fstat!r} not in {sorted(FIELD_KEY_STATUS)}")
        if fkey is not None and jurisdictionish_key(str(fkey)):
            fail(f"{vf.name}: file field_key {fkey!r} is a jurisdiction field name — D4 forbids it")
        if vf.stem != str(fkey):
            fail(f"{vf.name}: filename must be <field_key>.json, field_key is {fkey!r}")
        if fstat == "resolves" and fkey not in canonical_keys:
            fail(f"{vf.name}: field_key {fkey!r} does not resolve in canonical_fields.json")
        if fstat == "field_pending_R1" and not norm_ws(str(data.get("pending_reason", ""))):
            fail(f"{vf.name}: field_pending_R1 requires a pending_reason naming the deferral")
        if data.get("status") not in FILE_STATUS:
            fail(f"{vf.name}: file status {data.get('status')!r} not in {sorted(FILE_STATUS)}")
        if (data.get("match_rule") or {}).get("matching") != "word_boundary":
            fail(f"{vf.name}: match_rule.matching must be 'word_boundary'")
        if data.get("pack") != pack_dir.name:
            fail(f"{vf.name}: pack {data.get('pack')!r} != directory {pack_dir.name}")

        rows = data.get("entries", [])
        seen_ids: set[str] = set()
        for row in rows:
            rid = row.get("value_id", "?")
            where = f"{vf.name}:{rid}"
            if rid in seen_ids:
                fail(f"{where}: duplicate value_id")
            seen_ids.add(rid)

            kind = row.get("row_kind")
            if kind not in ROW_KIND:
                fail(f"{where}: row_kind {kind!r} not in {sorted(ROW_KIND)}")
            if row.get("provenance") not in PROVENANCE:
                fail(f"{where}: provenance {row.get('provenance')!r} not in {sorted(PROVENANCE)}")
            if row.get("source_kind") not in SOURCE_KIND:
                fail(f"{where}: source_kind {row.get('source_kind')!r} not in {sorted(SOURCE_KIND)}")
            if row.get("status") not in ROW_STATUS:
                fail(f"{where}: row status {row.get('status')!r} not in {sorted(ROW_STATUS)}")
            if "pattern" in row:
                fail(f"{where}: rows must not carry a 'pattern' key — detectors and their regexes are catalogue 08's")

            rj = row.get("jurisdiction")
            if not (isinstance(rj, str) and JURISDICTION_TAG.match(rj)):
                fail(f"{where}: jurisdiction must be a lowercase tag, got {rj!r}")
            elif status not in ("shape_example",) and isinstance(jur, str) and rj != jur:
                fail(f"{where}: row jurisdiction {rj!r} != pack jurisdiction {jur!r} — one pack, one jurisdiction")

            sr = row.get("safety_relevant")
            if not isinstance(sr, bool):
                fail(f"{where}: safety_relevant must be a bool")
            hook = row.get("detector_hook")
            if sr is True:
                if not hook:
                    fail(f"{where}: safety_relevant true requires a detector_hook naming catalogue 08's rule")
            if hook is not None and hook not in r2_ids:
                fail(f"{where}: detector_hook {hook!r} not an entry id in catalogue 08's 01-detector-rules.json")

            slots = row.get("gate_slots")
            if not isinstance(slots, list):
                fail(f"{where}: gate_slots must be a list (may be empty on value rows)")
            else:
                for s in slots:
                    if r2_r5_slots and s not in r2_r5_slots:
                        fail(f"{where}: gate_slot {s!r} is not an R5-owned slot in catalogue 08")

            for a in row.get("aliases", []):
                if not (isinstance(a, dict) and isinstance(a.get("alias"), str)
                        and isinstance(a.get("case_sensitive"), bool) and isinstance(a.get("script"), str)):
                    fail(f"{where}: malformed alias {a!r}")

            if kind == "value":
                if row.get("field_key") != fkey:
                    fail(f"{where}: row field_key {row.get('field_key')!r} != file field_key {fkey!r}")
            elif kind == "gate_label":
                if row.get("field_key") is not None:
                    fail(f"{where}: gate_label rows carry field_key null by construction")
                if not norm_ws(str(row.get("why_no_field_key", ""))):
                    fail(f"{where}: gate_label rows must justify the null field_key")
                if not slots:
                    fail(f"{where}: gate_label rows need non-empty gate_slots — no gate consumer means dead data")

            if row.get("provenance") == "design" and not row.get("source_cite"):
                fail(f"{where}: provenance design requires a verbatim source_cite")

            # Michaelmas ownership guard (invariant 11)
            surfaces = [row.get("label", "")] + [a.get("alias", "") for a in row.get("aliases", [])]
            if any("Michaelmas" in s for s in surfaces) and row.get("provenance") != "design":
                fail(f"{where}: a Michaelmas row must be provenance design (00 section 3.10) — and the token is R6's to hold")

            et, ef = row.get("example_true"), row.get("example_false")
            if not isinstance(et, str) or not row_matches(row, et):
                fail(f"{where}: example_true does not match its own row under word-boundary rules")
            if not isinstance(ef, str):
                fail(f"{where}: example_false missing")

        for row in rows:
            ef = row.get("example_false")
            if isinstance(ef, str):
                for other in rows:
                    if row_matches(other, ef):
                        fail(f"{vf.name}:{row.get('value_id')}: example_false {ef!r} matches row {other.get('value_id')}")

        # quote authenticity for every *cite in the file
        for path, cite in list(walk_collect(data, "source_cite")) + list(walk_collect(data, "design_cite")):
            if cite is None:
                continue
            if not isinstance(cite, dict):
                fail(f"{vf.name}: cite at {path} must be an object or null")
                continue
            src, quote = cite.get("source"), cite.get("quote")
            if src not in source_texts:
                fail(f"{vf.name}: cite at {path} names unknown source {src!r}")
            elif not isinstance(quote, str) or norm_ws(quote) not in source_texts[src]:
                fail(f"{vf.name}: cite at {path}: quote not found verbatim in {src}: {str(quote)[:80]!r}")

# at most zero v1 packs until the protocol runs (the per-pack failure above already fired)
if v1_count == 0:
    packs_md = HERE / "PACKS.md"
    if packs_md.exists() and "awaiting Joseph" not in packs_md.read_text(encoding="utf-8"):
        fail("PACKS.md must say the v1 pack is awaiting Joseph while no pack is ratified")
    if not packs_md.exists():
        fail("PACKS.md missing")

# ---------------------------------------------------------------- adversarial fixtures

_w2 = {"label": "W-2", "aliases": [{"alias": "W-2", "case_sensitive": True, "script": "Latin"}]}
_p60 = {"label": "P60", "aliases": [{"alias": "P60", "case_sensitive": True, "script": "Latin"}]}
for text in ("SW-2000 spec sheet", "W-2000 turbine", "lowercase w-2 in prose"):
    if row_matches(_w2, text):
        fail(f"adversarial: W-2 must not match in {text!r}")
if not row_matches(_w2, "attached W-2 for 2025"):
    fail("adversarial: W-2 must match in 'attached W-2 for 2025'")
for text in ("P600 printer manual", "UP60 valve", "p60x fixture"):
    if row_matches(_p60, text):
        fail(f"adversarial: P60 must not match in {text!r}")
if not row_matches(_p60, "your P60 is enclosed"):
    fail("adversarial: P60 must match in 'your P60 is enclosed'")

# ---------------------------------------------------------------- report

if failures:
    print(f"FAIL — {len(failures)} problem(s):")
    for f in failures:
        print(f"  - {f}")
    sys.exit(1)

n_packs = len(pack_dirs)
print(f"OK — {n_packs} pack dir(s) checked; field/value split mechanical; no jurisdiction "
      "field key or dimension expressible; quotes verbatim; catalogue-08 hooks and slots "
      "resolve; Michaelmas guarded; no v1 pack (awaiting Joseph).")
