# 12 — Academic and capture pattern catalogues (R6)

Authored 2026-08-21/22 (an interrupted first run wrote 01–03; this salvage run verified them
against the sources, fixed what was wrong, and completed 04, 05, RESEARCH.md and check.py — the
audit trail is in RESEARCH.md). Nothing is committed by the authoring agent — Joseph reviews and
commits.

These files fill four rows of P6's *Deferred — manual design required* table:

| P6 SPEC deferred row | Filled by |
|---|---|
| Rule context-term lists beyond the five literal academic terms (§3.5) | `01-academic-context-terms.json` |
| Gazetteer "course-code formats" half (§3.7) — the format families, never a course list | `02-course-code-formats.json` (seam with 10/04 — see NEEDS-JOSEPH) |
| Date and academic-term regex catalogue beyond the three named patterns (§3.10) | `03-academic-term-patterns.json` + `04-narrow-date-families.json` |
| Photo-event clustering parameters (§2.6, §4.2 — G7) | `05-capture-composition.md` — **named slots only, no values** |

Patterns are **data**. Nothing here may be imported by `src/` at module level; the P5/P6 plans
forbid module-level pattern constants, and every consumer below takes these files as injected
arguments.

---

## Who injects what

**P6 is the consumer of everything in this directory. P5 already has its own catalogues (top-level
02–04: screen resolutions, sensor ratios, camera filename patterns) and takes nothing from here.**

| File | Injected into | As |
|---|---|---|
| `01-academic-context-terms.json` | P6 Task 10 (`src/facts/rules.py`) | the `required_context_terms` of injected `Rule` instances; consumed by `context_check(before, after, terms)` |
| `02-course-code-formats.json` | P6 Task 10 | the `pattern` half of the same `Rule` instances (field key `subject`, D6 as ratified) |
| `03-academic-term-patterns.json` | P6 Task 12 (`src/facts/dates.py`) | required members of the injected `DatePatterns` (the three `00` literals are asserted by pattern identity) |
| `04-narrow-date-families.json` | P6 Task 12 (regex families); P6 Task 8 (`src/facts/direct.py` — the metadata-slot families) | the non-term half of `DatePatterns`; the labeled-slot list for direct date facts |
| `05-capture-composition.md` | P6's media/photo fact resolution (Tasks per SPEC M2/G7) | composition rules + the G7 named slots (`event_time_window`, `event_gps_radius`, `camera_identity_test`) |

**CONNECTION.md section 4 step 1** is the same consumer seen from activation: deterministic
activation evaluates pattern-plus-context rules — a course-code pattern (02) together with academic
context (01, the `00` five-term floor) is the worked Academic activation signal, and a term-pattern
hit (03) is a never-alone supporting signal. These catalogues are exactly what plugs into that
step; the floor is `design`, every extension is `proposal` with `never_alone: true`.

## The claiming order (canonical statement, referenced by 03 and 04)

Text families across 12/03 and 12/04 evaluate in bands; a span claimed by an earlier band is not
offered to a later one:

1. **Metadata-slot families** (12/04) — read labeled slots, compete with no text pattern.
2. **Designator-prefixed families** — 12/03: AY, AY-full, WS, WiSe/SoSe,
   Wintersemester/Sommersemester, 年度; 12/04: FY. So `AY 2024-25` is one AY term candidate and
   `FY 2024-25` is one fiscal (tax-year) candidate — neither ever reaches band 4.
3. **Worded families** — 12/03: named UK terms, quarters, Semester N, season+year; 12/04: written
   month-day-year, day-month-year, month-year.
4. **Bare numeric shapes** — 12/04: iso-ymd, compact-ymd; then 12/03's standalone year ranges
   **last of all**.

Within a band the families are disjoint by construction; check.py exercises the cross-band cases
(`AY 2024-25`, `FY 2024-25`, `2024-05-11`).

## Standing rules (all files)

- **Word-boundary, never substring** — the discipline that keeps `MIT` out of "submit" and `UNC`
  out of "uncertainty" (A01/A02 are standing acceptance fixtures).
- **Context required for course codes, no exception** — a match with no context term yields
  `unresolved(context_check_failed)`, never a fact. `HW 3` is a work-type clue, never a course.
- **No numeric thresholds anywhere.** Injected slots are named and hold null; regex quantifiers and
  calendar identities (consecutive years, real month/day) are shapes, not tunables.
- **Provenance vocabulary:** `design` | `inference` | `proposal`, exactly.
- **No fuzzy date parsing.** `v2024`, builds, ZIPs, ISO numbers and software versions are named
  non-dates (12/04 refused rows; P6 Done-means 10).
- **No EXIF ⇒ nothing.** Absence of EXIF is never evidence; OCR density is never a screenshot
  detector (12/05 Rules 1.2, 2.2; fixture A07).

## Verification

```
python3 planning/deferred-catalogues/12-academic-capture-patterns/check.py
```

Exit 0 = every assertion holds: the three `00` term literals match their dedicated patterns;
course-code entries all require context and none matches `HW 3`; `v2024` is a listed non-date and
matches no family; every stated example behaves as stated (including validation failures and
cross-band claiming); no numeric value sits in an injected slot; the G7 slot definitions carry no
digits; and every span quoted from `00`/`01` or a SPEC exists verbatim in its source.

## NEEDS-JOSEPH (open forks — recorded, never closed here)

- **NJ-R6-1 · Course-code formats have two authors.** `10-gazetteers/04-course-code-formats.json`
  (R4) and `12/02` both author the DEPT-space/attached families; R4's file flagged the seam itself.
  Differences: letter block `{2,6}` (10/04) vs `{2,5}` (12/02); guard style (four-prefix
  term-collision guard vs full dept stoplist + camera-prefix arbitration); `1234.DEPT` (unauthored
  there, `proposal` here — the dispatch names the shape, research found no registrar witness).
  Exactly one file must be the injected source; until picked, injecting both is forbidden.
- **NJ-R6-2 · 年度 field routing.** A Japanese `2024年度` string is the school year and the fiscal
  year in one spelling (verified — RESEARCH.md). Does the candidate route to `term`, to Finance's
  `tax_year`, or split on surrounding evidence? (12/03 `atp-cjk-nendo` carries the row as
  `proposal`.)
- **NJ-R6-3 · `extension_context_policy`.** May any combination of `never_alone` extension terms
  satisfy the §3.5 context check with no floor term present? Slot named in 12/01; the safe reading
  until answered is no.
- **NJ-R6-4 · Per-zone case policy.** Lowercase course codes in filenames (`phys1401_hw3.pdf`) are
  missed by the case-sensitive entries; a filename-zone-only case-insensitive policy would recover
  them at a measured false-positive cost (12/02 `unc-lowercase-filename-codes`).
- **NJ-R6-5 · `locale_numeric_date_policy`.** Ambiguous numeric orders (`05/11/2024`, `17.05.2026`)
  are refused in v1; a locale-injected family is the named slot if Joseph wants recovery.
- **NJ-R6-6 · G7 slot values.** `event_time_window`, `event_gps_radius`, `camera_identity_test` are
  named and empty by design; their values are a product decision measured against real corpora.
- **NJ-R6-7 · `media_type` enum.** Deferred in the P6 SPEC; 12/05 composes evidence for the two
  `00`-named hypotheses only.
- **Proposal rows awaiting review** (not forks, just unratified authorship): 12/01 extension terms;
  12/02 `ccf-number-dot-dept`; 12/03 `atp-cjk-nendo`, standalone year ranges; 12/04
  `fam-month-year`. Each is marked `provenance: proposal` in place.
