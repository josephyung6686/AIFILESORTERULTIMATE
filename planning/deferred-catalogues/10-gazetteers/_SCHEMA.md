# Catalogue 10 — row shape

Every gazetteer file in this directory conforms to this shape. `check.py` enforces the mechanical
parts; the prose parts are review contract.

Authored 2026-08-21 by R4. Nothing here is committed by the authoring agent — Joseph reviews and
commits.

---

## Two row kinds

Files 01–03 hold **entity rows** (a canonical value plus its aliases). File 04 holds **format
rows** (a pattern family that recognizes the *shape* of a value, never a list of the values
themselves). Both kinds share the file-level keys; they differ in the row keys.

## File-level keys (all files)

| key | meaning |
|---|---|
| `list_id` | stable identifier for the file |
| `title` | human title |
| `version`, `authored` | strings; no numeric JSON values exist anywhere in these files (see rule N below) |
| `owner` | always **P6 (injected) — never P5**. P5 observes text; naming a school is a fact-layer job |
| `consumer` | the injected call P6's fact resolver receives; see `README.md` |
| `status` | `seed \| schema_only` — every file in v1 is **incomplete** and says so |
| `backs_fields` | the canonical field keys this gazetteer backs. `planning/domains/canonical_fields.json` (R1a's table) has landed and every key resolves in it — `check.py` asserts this mechanically. If R1a's table later respells a key, `backs_fields` follows the table, not this file |
| `universe` | the stated universe of the file — what a complete version of this list would contain, named precisely. v1 seeds use `design_examples` (only values the design itself names or implies) |
| `match_rule` | the consumer invariant block: `matching: "word_boundary"` (mandatory, every file), the case rule, and the CJK slot (below) |
| `injected_slots` | named thresholds with **null** values: `min_score`, `min_margin`, `positional_weight_by_zone`. §3.7 requires them; the numbers are P6's deferred rows and are injected, never written here |
| `entries`, `refused`, `uncertain` | as in catalogues 01–07: `refused` carries the false-positive analysis for things deliberately not matched; `uncertain` is recall-safe — when in doubt a row goes there, and every item is mirrored in `RESEARCH.md` NEEDS-JOSEPH |
| `homonyms` | the collision registry (below) |

## Entity row keys (files 01–03)

```json
{
  "id": "sch-uchicago",
  "canonical": "University of Chicago",
  "entity_type": "university | secondary_school | firm | financial_institution | lab | venue",
  "aliases": [
    {"alias": "University of Chicago", "case_sensitive": false, "script": "Latin"},
    {"alias": "U Chicago",             "case_sensitive": false, "script": "Latin"},
    {"alias": "UChicago",              "case_sensitive": false, "script": "Latin"}
  ],
  "scripts": ["Latin"],
  "provenance": "design | inference | proposal",
  "source_kind": "design_example | official_list | wikidata | user_approved | proposal",
  "design_cite": {"source": "00", "section": "§2.8", "quote": "…verbatim span…"},
  "false_positive_risk": "low | medium | high",
  "example_true": "a string this row must match (word-boundary)",
  "example_false": "a string that must match no row in this file",
  "status": "seed",
  "notes": "free prose"
}
```

Rules:

- **`canonical` is the stored normalized value** (§2.8: raw observation preserved verbatim; a
  resolver normalizes; the user re-displays). Aliases are **value-level only** — CONNECTION.md
  section 6: there are no field aliases, and nothing in this catalogue names a field twice.
- **`provenance` is the repo vocabulary and nothing else**: `design` only when the design names
  the exact string; `inference` when the row expands something the design names (`Duke` →
  `Duke University`); `proposal` when the design does not name it at all. The *sourcing* question
  the validation procedure asks (official list? Wikidata? user-approved?) is a **separate key**,
  `source_kind`, so the two vocabularies never blur.
- **`design_cite.quote` is verbatim or absent.** `check.py` loads the named source file
  (`00` → `planning/00-database-agent-product-design.md`, `P6-SPEC`, `CONNECTION`) and asserts the
  span exists. A row with nothing quotable carries `"design_cite": null` and cannot claim
  `provenance: design`.
- **An alias marked `"ambiguous": true` must name a `homonym` id**, and every alias that resolves
  to more than one canonical (across all three entity files, case-folded per its case rule) must be
  covered by a homonym row. `check.py` builds the map and fails on an unrecorded collision.
- **`case_sensitive: true` is for acronym aliases** (`MIT`, `UNC`, `EY`, `WUSTL`) — lowercase
  `mit` is the German preposition, not a school. Name aliases are case-insensitive.
- **`script` is per alias; `scripts` is the row's union.** v1 rows are Latin-script. The key
  exists so a CJK alias (for example a Chinese university name) is representable **without a
  schema change** — see the CJK slot below.

## Format row keys (file 04)

```json
{
  "id": "ccf-dept-space-number",
  "pattern": "[A-Z]{2,6} [0-9]{3,4}[A-Z]{0,2}",
  "pattern_label": "DEPT NNNN",
  "case_sensitive": true,
  "scripts": ["Latin"],
  "provenance": "design | inference | proposal",
  "design_cite": {"source": "00", "section": "§3.5", "quote": "…"},
  "false_positive_risk": "low | medium | high",
  "example_true": "BUSIB 4300",
  "example_false": "HW 3",
  "excluded_prefixes_apply": true,
  "status": "seed",
  "notes": "…"
}
```

- Patterns are applied **at word boundaries** like every alias: the reference matcher wraps them in
  non-word-character lookarounds. A format hit recognizes a course-code-*shaped* string; it is
  **never a fact by itself** (the §3.5 context requirement, restated in `PROCEDURE.md`).
- The digit counts inside a pattern are part of the format's definition (as catalogue 06's ISBN
  digit counts are), not thresholds. Scores, margins and weights are injected slots and appear
  nowhere in this directory as numbers.
- `excluded_prefixes` is file-level data in 04: letter blocks that, followed by a year-shaped digit
  block, belong to R6's academic-term patterns (`AY 2024-25`, `FY2025`), not to a course format.

## Homonym row keys

```json
{
  "id": "hom-columbia",
  "alias": "Columbia",
  "readings": ["Columbia University", "British Columbia", "District of Columbia",
               "Columbia, SC", "Columbia Sportswear", "Columbia Pictures"],
  "resolution": "never alone; role context plus §3.7 ranking, or the match stays possible",
  "notes": "…"
}
```

A homonym row records that an alias is a **word-boundary hit that can still be the wrong entity**
(`British Columbia` contains a clean word-boundary `Columbia`). The matcher cannot fix this and
must not try; the containment is the §3.7 ranking discipline plus the never-alone rule. Recording
the collision is what makes the gazetteer honest rather than silently wrong.

## Rule N — no numeric JSON values

No integer or float appears anywhere in these four JSON files. Versions and dates are strings;
thresholds are named null slots; pattern quantifiers live inside pattern strings. `check.py` walks
every JSON tree and fails on any `int` or `float`. This is _CONTRACT.md rule 3 made mechanical.
