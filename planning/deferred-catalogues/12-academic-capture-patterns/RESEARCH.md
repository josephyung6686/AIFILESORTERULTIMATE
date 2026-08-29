# RESEARCH — 12-academic-capture-patterns (R6)

Two runs produced this directory. An interrupted first run (2026-08-21) drafted 01–03 and was
killed before writing 04, 05, README, RESEARCH or check.py. The salvage run (2026-08-22) treated
those drafts as untrusted, verified every quotation mechanically against `00`, verified every
cross-reference against the live repo, ran the external verification the drafts had promised,
fixed what was wrong (§4 below), and completed the missing files. This file is the record.

---

## 1. Externally verified findings (web survey, 2026-08-22)

Each claim below is load-bearing in a catalogue entry and was verified against the listed sources.

**UK named terms** (12/03 `atp-uk-named-term`): Oxford runs Michaelmas / Hilary / Trinity;
Cambridge runs Michaelmas / Lent / Easter; Durham's winter term is Epiphany. Sources:
https://en.wikipedia.org/wiki/Hilary_term · https://en.wikipedia.org/wiki/Epiphany_term ·
https://www.oxfordhistory.org.uk/university/terms.html ·
https://acadcalendar.com/cambridge-term-dates/

**English legal year collision** (same row's must-not-conclude): the courts' sitting terms use the
same four names — Michaelmas, Hilary, Easter, Trinity — so "Michaelmas Term 2024" in a barrister's
listing is a legal term, not coursework. Sources:
https://www.judiciary.uk/about-the-judiciary/our-justice-system/legal-year/ ·
https://supremecourt.uk/term-sittings

**German semesters** (12/03 `atp-german-semester*`): the year divides into Wintersemester
(1 October – 31 March, written with a slash range) and Sommersemester (1 April – 30 September),
abbreviated WiSe and SoSe. Sources:
https://www.uni-assist.de/en/tools/glossary-of-terms/description/term/semester/ ·
https://www.tu-darmstadt.de/studieren/studieninteressierte/internationale_studieninteressierte/austauschprogramme_inbound/artikel_details_de_en_56840.en.jsp ·
https://www.academicjobs.com/higher-education-news/germany-universities-semester-dates-2026-or-academic-guide-18588
("The academic year in Germany is divided into winter semester (WiSe) and summer semester (SoSe)")

**Japanese 年度** (12/03 `atp-cjk-nendo`; 12/04 fiscal notes): nendo is the April-to-March year,
used identically for the fiscal year and the school year — which is why the string alone cannot
route between `term` and `tax_year` (NJ-R6-2). Sources:
https://www.japandict.com/%E5%B9%B4%E5%BA%A6 · https://mailmate.jp/blog/japan-fiscal-year ·
https://web-japan.org/kidsweb/explore/calendar/april/schoolyear.html

**Salesforce seasonal releases** (12/03 `atp-season-year` false friend): Salesforce ships three
releases a year named Spring / Summer / Winter plus a year, in both apostrophe form (Winter '25)
and full form ("Salesforce Spring 2026 Release" is the vendor's own page title) — so season+year is
genuinely software-release vocabulary, not only academic. Sources:
https://www.salesforce.com/products/innovation/spring-26-release/ ·
https://help.salesforce.com/s/articleView?id=release-notes.salesforce_release_notes.htm&language=en_US&release=252&type=5

**Notre Dame five-digit course numbers** (12/02 `unc-five-digit-numbers`): "Courses at Notre Dame
are identified with a subject code of up to four letters and a 5-digit course number" — the
witness that five-digit numbers exist, and the ZIP collision is why they stay uncertain. Source:
https://registrar.nd.edu/courses-classrooms/courses/course-numbering/

**Australian Semester 1/2** (12/03 `atp-semester-ordinal`): ANU and Australian universities
generally run two semesters named Semester 1 (February) and Semester 2 (July); transcripts reflect
grades by semester. Sources: https://www.anu.edu.au/directories/university-calendar?year=2026 ·
https://academiquirk.com/article/australia-academic-calendars-2026-preview/

## 2. General-knowledge anchors (not surveyed; recorded so nothing masquerades as verified)

- US Supreme Court opinions open with a headnote section titled **Syllabus** (12/01 ctx-syllabus
  false friend).
- **Daft Punk — Homework (1997)**; "do your homework" as business idiom (12/01 ctx-homework).
- **Canvas** (Instructure) and **Blackboard** (Anthology) as LMS names vs their ordinary senses
  (12/01).
- **US quarter system** (Stanford, UChicago, UW): season + Quarter naming (12/03
  `atp-quarter-year`).
- **MIT department.number** subject numbering (6.006, 18.06) — refused as a v1 family in both
  12/02 and 10/04 for the software-version collision.
- **UK/AU attached course codes** (UCL COMP0034, UNSW COMP1511) — format witnesses for
  `ccf-dept-attached-number`.
- **JEITA CP-3461 (DCF)** camera basenames — reused from catalogue 04's own sourcing, including
  its finding that the unrestricted DCF shape *is* the attached course-code shape.
- Layouts in 12/04: EXIF colon datetimes (`YYYY:MM:DD HH:MM:SS`), PDF `D:` date strings,
  ISO 8601, Android `IMG_YYYYMMDD_HHMMSS` / `Screenshot_YYYYMMDD-HHMMSS` naming.
- **Oxbridge term abbreviations** (MT/HT/TT), UNSW T1/T2/T3 trimesters, UK schools' six terms —
  uncertain rows only.

## 3. Seam analysis: 12/02 vs 10-gazetteers/04 (NJ-R6-1)

R4's `10-gazetteers/04-course-code-formats.json` and R6's `12/02` both author course-code format
families. R4's file already consumes 12/01 by reference (context terms) and defers term patterns
to 12/03 — those two seams are clean. The format-family overlap is not, and R4's file flags it:
its unc-r6-merge-owner row asks which of the two files is the one owner, and its
term_collision_guard note says the overlapping token lists "must be unified when the
course-code-format seam gets one owner". Differences, so the review can pick an owner:

| Axis | 10/04 (R4) | 12/02 (R6) |
|---|---|---|
| letter block | `[A-Z]{2,6}` | `[A-Z]{2,5}` (six letters admits AUGUST + year shapes) |
| digit guard | none beyond shape | `{3,4}` plus dept stoplist (months, seasons, standards, FORM/ROOM/SUITE/UNIT/APT, camera prefixes) |
| term collision | four excluded prefixes (AY/FY/CY/SY) with year-shaped digit rule | stoplist rows AY/FY/WS/FALL + the claiming order with 12/03 and 12/04 |
| `1234.DEPT` | unauthored (uncertain row) | authored as `proposal` with mandatory extension stoplist (dispatch names the shape; no registrar witness found) |
| camera filenames | not addressed | DSC/DSCF/DSCN/PICT/CIMG/IMGP stoplisted + filename-zone arbitration with catalogue 04 |
| MIT dotted numbers | refused (uncertain) | refused (uncertain) — independent agreement |

Both files agree on everything structural: format-not-course-list, context always required,
`HW 3` refused by name, values auto-create. The fork is width and guard style, and it needs one
owner (README NEEDS-JOSEPH NJ-R6-1). R6 did not edit 10/04 (outside allowed paths).

## 4. Salvage audit — what the second run changed in the drafts

Verified unchanged: every `00` quotation in 01/02/03 (mechanical containment check — all
authentic); the D6 statements (ratified key `subject`, `_CONTRACT.md` rule 8); the P6 SPEC
citations (N-6, Done-means 5/8/10, unresolved reasons, Task 10/12 names and file paths); the P4
zone names used; catalogue 04's DCF refusal and catalogue 06's `Q3 2024`/`05/11/2024` leak list;
A01–A03 contents.

Fixed:

1. **`atp-year-range-full` accepted `2024-2025-26`** (lookahead only refused a bare digit).
   Now `(?![-–]?\d)`, matching the standalone row's discipline.
2. **Both standalone range rows accepted letter-attached ranges** (`v2024-25`, `FY2024-25`) —
   lookbehind was `(?<![\d-])`. Now `(?<![\w-])`; the spaced `FY 2024-25` case is handled by the
   claiming order instead (band 2, `fam-fiscal-year`), and check.py exercises it.
3. **`consecutive_year_two_digit_when_range` was referenced by two German rows and defined
   nowhere.** Defined in `validation_rules`; the two-digit rule also now states its four-digit-tail
   behavior (`2024/2025`).
4. **German rows missed the full-year tail** (`Wintersemester 2024/2025` matched only as a
   rangeless single year, silently dropping the range). Tails widened to `(/(19|20)?\d{2})?`.
5. **Sourcing claims the first run could not back** (surveys attributed to DAAD/PONS/Universities
   Australia/UCCS/W&M/Rutgers, dated 2026-08-21) were re-verified where possible and reworded to
   the sources actually consulted (§1) or moved to the anchor list (§2); survey dates now read
   2026-08-22.
6. **12/02 had no acknowledgment of the 10/04 seam** — added `seam_with_10_04` (§3 above) and
   NJ-R6-1.
7. **12/02 wording** used "role-splitting" for positional weighting — renamed; `role_split` is
   CONNECTION.md's field-level edge and must not be overloaded.
8. **12/02 extension stoplist** widened (WEBP/HEIF/RAW-format/AV/office/config extensions) with an
   explicit extendability note.

## 5. Fixture inventory correction

The dispatch summarized A01–A03 as "MIT-in-submit, UNC-in-uncertainty, v2024". The fixtures on
disk are: A01 `MIT` in "submit", A02 `UNC` in "uncertainty", **A03 = ZIP code (`MA 02139`) and
device model (`XPS 13`)** — no A-fixture carries `v2024`. The `v2024` obligation is real but lives
in P6 SPEC Done-means 10 and `00` §3.10's confusable list; 12/04 lists it as a named refused
non-date and check.py asserts no family matches it. Catalogue files cite the fixtures as they
exist, not as the dispatch summarized them. (A03 also spells the field `course`; it predates D6's
ratification of `subject` and binds on the forbidden *values*.)

## 6. Decisions and their reasoning (the ones a reviewer will ask about)

- **Case rules differ per row on purpose.** Season words and month-day dates tolerate case (OCR
  and filenames lowercase freely; the frame is strong); designators (AY, FY, WiSe, WS) and month-
  only dates do not (lowercase forms are ordinary words; the frame is weak). Each row states its
  rule; none inherits silently.
- **The standalone year-range family exists at all** (despite being the riskiest row in 12/03)
  because `2024-25` folder and file names are how real academic corpora write the year — but it is
  `proposal`, evaluated last, 20xx-only, and identity-validated.
- **Calendar identities are not thresholds.** Consecutive-year and real-month/day checks are
  properties of the calendar (like catalogue 06's ISBN checksums), so they may live in data
  without violating the no-numbers rule. Everything tunable is a named null slot.
- **12/04 splits metadata slots from text regexes** because the design splits them: a labeled slot
  is a Direct source (§3.13); text dates take the §3.10 candidate path and are `validated` at
  best. The EXIF family is deliberately the *only* author of `capture_date`.
- **G7 stays nameless-valued.** The dispatch is explicit: name the slots, fill nothing. 12/05
  names three (`event_time_window`, `event_gps_radius`, `camera_identity_test`) and check.py
  asserts their definitions carry no digits.
