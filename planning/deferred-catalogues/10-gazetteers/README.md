# Catalogue 10 — validated gazetteers (P6 only; never P5)

The deferred row this fills — P6 SPEC, *Deferred — manual design required*:
"Gazetteer contents and the validation procedure that makes them \"validated\"" (§3.7 —
universities, course-code formats, institutions, companies, labs, venues; manual).

`00` §3.7: "The system should use rules, metadata, validated gazetteers, and document structure
before invoking heavyweight models." Catalogues 01–07 help P5 **observe**; nothing in them can
name a school. These four files are the naming half, and `PROCEDURE.md` is the definition of
"validated" that makes the adjective testable.

Authored 2026-08-21 by R4. Nothing is committed by the authoring agent — Joseph reviews and
commits.

---

## The four files

| file | backs (canonical field keys) | status | seed size |
|---|---|---|---|
| `01-schools.json` | `school`, `target_university`, `target_school` | seed | 8 entries, all from `00`'s own examples |
| `02-orgs-roles.json` | `our_firm`, `client`, `institution` | seed | 1 entry (`EY`, the design's one named firm) |
| `03-research-venues.json` | `lab`, `venue` | schema_only | 0 entries — `00` names no venue or lab values, and padding is the failure mode |
| `04-course-code-formats.json` | `subject` | seed | 2 format families (`DEPT NNNN`, `DEPTNNNN`) from `BUSIB 4300` / `PHYS1401` |

`planning/domains/canonical_fields.json` has **landed** (R1a ran concurrently with the first
draft; verified at re-verification 2026-08-22): every `backs_fields` key above resolves in R1a's
table, and `check.py` now asserts that mechanically. R1a's per-field `gazetteer` tags confirm the
wiring for schools (`school`/`target_university`/`target_school` → `"schools"`) and orgs
(`our_firm`/`client`/`institution` → `"orgs"`) — with two recorded seams: R1a tags `lab`/`venue`
as `"orgs"` rather than a research tag (03's `unc-r1a-gazetteer-tag`), and `target_school` is held
unreferenced pending Joseph's fold-or-keep decision (ROSTER.md). See `RESEARCH.md`.

**Shared entity, split role — explicit.** One entity list backs several role-split fields. The
schools list backs `school` (Academic) *and* `target_university` (College applications) — §3.8's
role split, the only licensed near-duplicate. The orgs list backs `our_firm` *and* `client`
*and* Finance's `institution`. A row never records a role; the field's context rule decides which
field a hit may fill. Do **not** merge the fields because the gazetteer is shared, and do not
duplicate the gazetteer because the fields are split.

## How P6 consumes these — never as module-level constants

Same rule as catalogues 01–07 (see `../README.md`): these files are **data the caller loads and
injects**. Catalogue 01's injection row is the precedent this one copies — *"fact-resolver
construction, or the P1-namespaced configuration object (G4)"*, consumed by P6 only, never P5.

- **Injection point:** P6 fact-resolver construction, as a caller-supplied lookup (sketch:
  `gazetteer_candidates(text) -> candidates`, built from these JSONs by the caller). Required
  argument, no default — a default is where an invented list would hide.
- **Never P5.** P5 emits observations (what the text says, where); it does not name schools.
  Nothing under `src/extractors/` may import these files, and P5's Task-20-style namespace
  introspection convention applies to whatever module hosts the P6 resolver.
- **Never a substring matcher.** Word-boundary is a consumer invariant carried by every file's
  `match_rule` and asserted by `check.py` against live rows (`MIT` finds nothing in "submit").
  An injected matcher that substring-matches fails P6's §8.5 suite by design.
- **A hit is a candidate, not a fact.** It enters §3.7's ranking (positional weighting; injected
  `min_score` / `min_margin` slots) and is constitutionally never-alone for schema activation
  (CONNECTION.md section 4, step 2). Match **plus** the field's context rule, or it is `possible`
  at most. A university name alone must not create a group.
- **Misses block nothing stronger.** User entries are `user_confirmed`; labeled form fields are
  `direct`; new values auto-create (§3.12). The gazetteer feeds only the `validated` path.

## Boundaries with the neighbouring catalogues

- **01–07:** untouched. Tool strings, resolutions, ratios, camera patterns, repo markers,
  identifier patterns, archive markers are P5-side observation vocabulary. `BUSIB 4300` still
  matches nothing there.
- **R5 (`11-jurisdiction-values/`):** owns jurisdiction-varying **form types, court names,
  statute labels, permit names** — values for Finance/legal/government record fields. It does not
  duplicate institution lists (its brief says so verbatim: "do not duplicate institution lists");
  institution *names* live here. R5 had not landed at re-verification (2026-08-22); the boundary
  is from its dispatch brief.
- **R6 (`12-academic-capture-patterns/`):** owns context terms, term patterns, narrow dates.
  File 04 consumes R6's context-term catalogue **by reference** and quotes only the design's five
  literals. R6 has **landed**, including its own `02-course-code-formats.json` — a real overlap
  with file 04 here; one owner must win at merge (recommendation: R6's, which is the stronger
  file). The seam and the concrete deltas are in file 04's `unc-r6-merge-owner` and
  `RESEARCH.md` NEEDS-JOSEPH.
- **Jurisdiction (D4, ratified):** a value, never a field, never a destination dimension. v1
  ships one jurisdiction's gazetteers, injected per deployment; *which* jurisdiction is the open
  half, recorded in `RESEARCH.md`.

## Working on these files

```bash
cd "planning/deferred-catalogues/10-gazetteers"
python3 check.py          # every invariant below; non-zero on any failure
```

What `check.py` asserts (see `PROCEDURE.md` for the definition each test serves):

- every `quote` anywhere in the four JSONs exists **verbatim** in its named source file
  (`00`, `P6-SPEC`, `CONNECTION`) — fabricated quotations are a test failure here;
- the reference word-boundary matcher finds `MIT` nowhere in "please submit" / "SUBMIT", `UNC`
  nowhere in "uncertainty", and lowercase German "mit" never matches the case-sensitive alias;
- `00`'s worked strings round-trip: `Columbia` → Columbia University, `U Chicago` and `UChicago`
  → University of Chicago, `BUSIB 4300` and `PHYS1401` match their format families;
- `HW 3`, `AY 2024-25`, `FY2025`, `v2024`, `90210`, `2026`, `Spring 2026` match **no** course
  format;
- every `example_true` matches its own row; every `example_false` matches no row in its file;
- alias collisions across all entity files require a recorded homonym; `ambiguous` aliases name
  one;
- no `int` or `float` exists anywhere in the JSONs (thresholds are named null slots);
- vocabulary closure: `provenance`, `source_kind`, `status`, `entity_type`, `match_rule.matching`
  all draw from the closed sets in `_SCHEMA.md`;
- a CJK alias fixture passes the schema (representability today; the `cjk_matcher` slot stays
  open and flagged).
