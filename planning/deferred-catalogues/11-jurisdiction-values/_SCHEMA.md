# Catalogue 11 — row and pack shape

Every JSON file in this directory conforms to this. `check.py` enforces the mechanical parts;
the prose parts are review contract.

Authored 2026-08-22 by R5. Nothing here is committed by the authoring agent — Joseph reviews and
commits.

Governing decision: **D4, ratified 2026-08-21** (`DECISION-BRIEF.md` RATIFIED table, applied at
`planning/domains/_CONTRACT.md` rule 9): "`jurisdiction` is a **value, never a field name and
never a destination dimension**. One jurisdiction's gazetteers in v1, injected." The ratification
fixes the *shape*; **which** jurisdiction is not named in it and remains open (see `RESEARCH.md`
NEEDS-JOSEPH). This schema is written so a pack can be authored the day Joseph answers, and so
nothing in this directory can express the forbidden things in the meantime.

---

## The objects

A **pack** is one jurisdiction's value lists, loaded per deployment. A deployment loads **one**
pack (D4: one jurisdiction in v1); a pack is a directory holding one `_pack.json` manifest plus
value files named by canonical `field_key`. Packs are **data the caller loads and injects** —
the same injection discipline as `../10-gazetteers` (P6-side) and `../08-sensitivity-detector`
(P7-side): never module-level constants, never P5's, required argument with no default.

A pack's rows have **two consumers**, and the row shape serves both:

- **P6 fact resolution** (value rows): jurisdiction-dependent members of a canonical field's
  value space — `W-2` as a value of `record_type`. A hit is a ranked candidate entering §3.7's
  ranking; never a fact by itself; constitutionally never-alone for schema activation
  (CONNECTION.md section 4, step 2).
- **P7's injected detector set** (gate projections): catalogue 08 declares four injected slots it
  names R5's — `tax_form_identifier_gazetteer`, `national_id_label_gazetteer`,
  `account_locator_patterns`, `legal_caption_gazetteer` (`../08-sensitivity-detector/
  01-detector-rules.json`, `injected_slots`). The loader **projects** slot content from pack rows
  (`gate_slots` below); this directory never holds a detector rule, a threshold, or a regex a
  detector fires on — catalogue 08 holds the types and conditions, this catalogue holds one
  jurisdiction's names.

## File-level keys (every value file)

| key | meaning |
|---|---|
| `list_id` | stable identifier for the file |
| `title` | human title |
| `pack` | the pack directory this file belongs to; must match its `_pack.json` `pack_id` |
| `version`, `authored` | strings; **no numeric JSON values exist anywhere in this directory** (rule N below) |
| `field_key` | the one canonical field whose values this file holds; the filename is `<field_key>.json` |
| `field_key_status` | `resolves` — the key exists in `planning/domains/canonical_fields.json` (checked mechanically) — or `field_pending_R1` (below) |
| `pending_reason` | required iff `field_key_status: field_pending_R1`: which deferral holds the field back and who authors it (in practice: D1's narrowed deferral — career/identity/medical/legal write no field rows until Joseph authors them) |
| `owner` | `P6 (injected) — never P5` for the fact path; gate projections are consumed by P7's injected detector set (catalogue 08's discipline) |
| `consumer` | prose: how the injected lookup is called, per `README.md` |
| `status` | `seed \| schema_only \| shape_example` — every file in this draft is incomplete and says so |
| `match_rule` | `matching: "word_boundary"` (mandatory), the case rule, the CJK slot (same convention as `../10-gazetteers/_SCHEMA.md` — representable per-alias `script`, matcher slot open) |
| `injected_slots` | named thresholds with **null** values (`min_score`, `min_margin`, `positional_weight_by_zone`); numbers are P6's deferred rows, injected, never written here |
| `entries`, `refused`, `uncertain` | as in catalogues 08–10: `refused` carries the analysis for things deliberately not listed; `uncertain` is recall-safe and every item is mirrored in `RESEARCH.md` NEEDS-JOSEPH |

### `field_pending_R1`, precisely

A value file may exist for a field the canonical list does not yet hold **only** when the field
is one D1's narrowed deferral reserves for Joseph (identity, medical, legal, career — PR-6:
placeholder schemas carry `schema: []`). Such a file marks `field_key_status: field_pending_R1`,
names the deferral in `pending_reason`, and its rows **cannot land in P6's `values` table until
the field exists**. Its gate projections (`gate_slots`) are live regardless — protection does not
wait on a fact field, because the gate consumer is catalogue 08's detector set, not the fact
layer. This is the mechanical form of "safety does not depend on the pack" (`README.md`).

`field_pending_R1` is **not** a licence to invent fields. It never creates a canonical row; the
gate (`planning/domains/check.py`) still rejects an unresolvable field key in any schema; and a
pending file whose field Joseph declines to author simply never gains a fact-side consumer.

## Value row keys (`row_kind: "value"`)

```json
{
  "value_id": "rt-us-w2",
  "row_kind": "value",
  "field_key": "record_type",
  "label": "W-2",
  "aliases": [
    {"alias": "W-2", "case_sensitive": true, "script": "Latin"},
    {"alias": "Wage and Tax Statement", "case_sensitive": false, "script": "Latin"}
  ],
  "jurisdiction": "us",
  "provenance": "design | inference | proposal",
  "source_kind": "design_example | overnight_prose | official_list | user_approved | proposal",
  "source_cite": {"source": "…", "quote": "…verbatim span…"},
  "safety_relevant": true,
  "detector_hook": "det-tax-form-completed",
  "gate_slots": ["tax_form_identifier_gazetteer"],
  "example_true": "a string this row must match (word-boundary)",
  "example_false": "a string that must match no row in this file",
  "status": "seed",
  "notes": "free prose"
}
```

Rules:

- **`field_key` must equal the file's `field_key`** and resolve per the file's
  `field_key_status`. One file, one field. `check.py` asserts both.
- **`label` is the stored normalized value**; `aliases` are value-level only (§3.12 /
  CONNECTION.md section 6: value aliases are P6's values table; there are no field aliases).
  `case_sensitive: true` is for short form codes (`W-2`, `P60`) whose lowercase forms collide
  with ordinary text.
- **`jurisdiction` is a lowercase tag** (`us`, `uk`, …) — a **value on the row**, never a field
  key, never a folder dimension. In a deployable pack every row's tag equals the pack's
  (`check.py`); the `00-example` pack mixes tags on purpose and is not deployable.
- **`provenance` is the repo vocabulary and nothing else**: `design` only when `00` names the
  exact string (for this catalogue that is nearly never — `00` names no jurisdiction and no
  form; `Michaelmas Term 2024` is the one design-named jurisdiction-flavoured token, and it is
  **R6's**, not this catalogue's); `inference` when expanding something the design names;
  `proposal` otherwise. `source_kind` answers the separate sourcing question; `overnight_prose`
  marks a string taken from the council/seat record rather than from any design file.
- **`source_cite.quote` is verbatim or the key is null.** `check.py` loads the named source and
  asserts the span (whitespace-normalized, so wrapped markdown lines still verify). A row with
  nothing quotable carries `"source_cite": null` and cannot claim `provenance: design`.
- **`safety_relevant` is a mandatory bool.** `true` means this value names material the four
  safety domains protect (tax forms, identity documents, court records, medical records —
  §3.15's list). When `true`, `detector_hook` **must** name an entry id in
  `../08-sensitivity-detector/01-detector-rules.json` — the detector that should fire on
  documents of this kind. **This catalogue never writes the detector's regex, signals, or
  thresholds; the hook is a pointer, and catalogue 08 owns everything behind it.** `check.py`
  resolves every hook mechanically and rejects any `pattern` key on a value row.
- **`gate_slots`** lists which of catalogue 08's four R5 slots this row's `label` + `aliases`
  project into (empty list when none). Members must be slot names catalogue 08 declares.
- `example_true` / `example_false` feed the reference word-boundary matcher in `check.py`
  (same semantics as `../10-gazetteers`: `W-2` matches nowhere in `SW-2000`).

## Gate-label row keys (`row_kind: "gate_label"`)

For jurisdiction-owned wordings that are **not values of any fact field and never will be** —
national-identifier labels and their per-label value shapes, court-caption wordings, account
locator shapes. The corresponding *identifier values* are redaction input, never facts
(catalogue 08's `02-identifier-classes.json`: `jurisdiction_dependent: true` classes name R5 as
the owner of label wordings and value shapes).

```json
{
  "value_id": "nid-us-ssn-label",
  "row_kind": "gate_label",
  "field_key": null,
  "why_no_field_key": "an identifier label serves detection and redaction; the identifier value is never extracted as a fact (catalogue 08, 02-identifier-classes: government_id_number is redacted, not extracted)",
  "label": "Social Security number",
  "aliases": [],
  "value_shape": null,
  "jurisdiction": "us",
  "provenance": "proposal",
  "source_kind": "proposal",
  "source_cite": null,
  "safety_relevant": true,
  "detector_hook": "det-id-national-id-labeled",
  "gate_slots": ["national_id_label_gazetteer"],
  "status": "seed",
  "notes": "…"
}
```

- `field_key` is **null by construction** and `why_no_field_key` is mandatory — this is the one
  row kind exempt from field resolution, and the exemption must justify itself.
- `value_shape` holds the label's adjacent value shape **when a pack is authored** (catalogue
  08's `det-id-national-id-labeled` consumes "shape supplied per-label by the same R5
  gazetteer"). It is a format definition like catalogue 10's course-code patterns — its internal
  digit counts are part of the format, not thresholds — and it stays `null` until the pack is
  chosen. No seed row carries one.
- `gate_slots` is mandatory and non-empty: a gate-label row with no gate consumer is dead data.

## Pack manifest (`_pack.json`)

| key | meaning |
|---|---|
| `pack_id` | equals the directory name |
| `status` | `shape_example \| candidate \| v1` — `v1` requires Joseph's "which jurisdiction" answer recorded in `PACKS.md`; `check.py` fails any `v1` until that protocol runs |
| `jurisdiction` | the pack's single tag; `null` only under `status: shape_example` |
| `deployability` | prose; `shape_example` packs state that no loader may accept them |
| `unsupported_region_copy` | the one factual string residual/UI may show for a domain the loaded pack does not model — see `unsupported-region.md`. Present in **every** manifest, `provenance: proposal` until Joseph ratifies wording |
| `match_rule`, `injected_slots` | as at file level |
| `files` | the value files the pack ships |
| `gate_slot_projections` | for each of catalogue 08's four R5 slots: which rows project into it, or an explicit empty-with-why |

## Rule N — no numeric JSON values

No integer or float appears anywhere in this directory's JSON. Versions and dates are strings;
thresholds are named null slots; any format quantifier lives inside a pattern string. `check.py`
walks every JSON tree and fails on any `int` or `float`. (`_CONTRACT.md` rule 3 made mechanical
— same as catalogues 08–10.)

## What this schema makes inexpressible

- **A jurisdiction field.** No row key is `jurisdiction`-as-field: the token appears only as a
  row *value tag*. `check.py` fails any `field_key` equal to `jurisdiction`, ending
  `_jurisdiction`, or starting `jurisdiction_` — in this directory **and** in
  `planning/domains/canonical_fields.json` (so P10 cannot discover one through the canonical
  table either).
- **A jurisdiction dimension.** No file here may contain a `dimension_order` key at all. Packs
  hold values; templates are P10's; a tree that branches on country is P10's one-way door and
  this directory refuses to hand it the key.
- **Multiple live jurisdictions.** One `v1` pack maximum; a deployable pack is single-tag
  throughout; D4 option 2 ("multiple at launch") was refused and stays refused here.
- **A second detector vocabulary.** No `pattern` on value rows, no thresholds anywhere, no
  handling classes on any row (those are P7's, per `_CONTRACT.md` rule 5).
