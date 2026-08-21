# R1a — spine roster

Date: 2026-08-21
Status: **R1a deliverable.** The schema list + template roster the R1b swarm is stamped onto,
plus the canonical field catalogue schemas reference.
Files: [`roster.json`](roster.json) · [`canonical_fields.json`](canonical_fields.json)
Contract chain (on conflict, in this order): `00` → [`prompts/ALIGNMENT.md`](../prompts/ALIGNMENT.md)
→ [`CONNECTION.md`](CONNECTION.md) (+ [`CONNECTION-EXAMPLES.md`](CONNECTION-EXAMPLES.md) fixtures)
→ the R1a dispatch prompt.
Decisions carried as recorded, not re-opened: D1 (narrowed — no career/identity/medical/legal
field rows), D2, D4, D6 (ratified — snake_case; the academic key is `subject`), PR-1…PR-8.

---

## 1. Counts — schemas few, templates honest

| Kind | Count | Launch split | Provenance split |
|---|---|---|---|
| `schema` | **10** | 6 `full` · 4 `safety` | 10 `design` |
| `template` | **73** | 11 `full` · 12 `safety` · 50 `placeholder` | 13 `design` · 41 `inference` · 19 `proposal` |

Templates per schema: academic 11 · finance 18 · photos 9 · research 9 · career 6 ·
code 5 · college_applications 5 · legal 4 · identity 3 · medical 3.

The ten schemas are exactly `00`'s named set and nothing else: the six launch domains
(academic, college_applications, research, career, photos, code) plus the four safety domains
(finance, identity, medical, legal). Career, identity, medical and legal are **field-less
placeholder rows** (D1 narrowed / PR-6); finance carries its four `00` fields and
`is_safety_domain: true` (PR-2). No eleventh schema was minted.

**Why 73 templates and not 200–300.** `00` sizes the eventual library at "roughly 200–300
domain-specific templates". This roster **stops under, deliberately**: a template must point at
exactly one existing schema and differ from that schema's default in detection signals,
recommended dimensions, or privacy rules (the CONNECTION.md §2 node test). With ten schemas —
four of them field-less — 73 is where honest rows run out. The gap to 200–300 is not padding
debt; it is **schema-shaped**: the professional and creative worlds the overnight 574 sketched
(~370 of its rows) have no schema to point at, and minting those schemas is exactly what `00`
forbids doing prematurely ("without prematurely hand-authoring hundreds of specialized
schemas") and what PR-6 closes for now. Expanding the roster toward `00`'s target is therefore a
Joseph decision about schemas (see NEEDS-JOSEPH), not an authoring quota. Per PR-3, the number
reported toward the 500+ request is the **connected catalogue** — 83 roster rows + 37 canonical
fields + 9 residual homes + the folder depth inside templates — never a manufactured row count.

## 2. Canonical fields — 37 keys, all from the named seed

`canonical_fields.json` holds **37 keys** and needed nothing beyond the seed CONNECTION.md §6
names: the six `00` universal fields, P6's recorded `download_session`, the six `00` domain
field sentences (with `subject` as the stored academic key per D6, and `project` /
`artifact_type` shared between research and code — the `shares_field` derivation, never
authored), and §3.8's role fields (`authored_by`, `target_school`, `our_firm`, `client`).
Every roster template's future `dimension_order` resolves against these keys; zero new keys
were required, which is the point — the 574's 2,295 private spellings collapse into this table.

- All keys snake_case; no spaced+snake pair. Spaced spellings appear only in `aliases`, which
  exist precisely so they never become keys.
- `role_split_with` is reciprocal on all three pairs (`school ↔ target_university`,
  `authored_by ↔ target_school`, `our_firm ↔ client`) — gate-verified.
- `destination_eligible` is per field; authorship/creator-identity fields (`authored_by`,
  `our_firm`, `instructor`) are `false` by `00`'s own rule. `people` and
  `programming_language` are seeded `false` conservatively — widening is Joseph's call (NJ-R1a-4).
- Every `00_cite` was grep-verified verbatim against `00` **before** the file was written.
- No JSON value anywhere in either file is a number; every threshold stays an injected slot.

## 3. Sources (named — not NAICS, not a quota)

1. **`00` itself**: the §3.11 field sentences, the §3.15 launch/safety/placeholder split, the
   §5.4 template table, §5.6's purpose-defined packet (a `full` template row: `00`'s own second
   branch pattern), §5.7's situation list (academic programs, university applications,
   recruiting, client engagements, research workflows, financial records, travel, legal,
   creative, software, personal administration, photos), and §7.3's nine residual names used in
   `must_consider_residuals`.
2. **CONNECTION.md / CONNECTION-EXAMPLES.md**: the eight fixtures are all expressible on this
   roster (coursework + teaching as two templates on one academic schema; research ∥
   college_applications co-activation; field-less safety identity falling to Protected Records;
   `.ics` as a `SOURCE_TYPE` not a domain; PR-8's three insurance templates on finance).
3. **The 574 harvest — ids and collisions only** (per the dispatch prompt): triaged below.
   No field spellings were copied.
4. **`SOURCE_TYPES` bottom-up**: all fourteen P5 families carry at least one `file_kind_owner`
   row — filesystem/code_structured → `code.software-project`; text_document/calendar/
   presentation → `academic.coursework` (the `.ics` fixture); spreadsheet →
   `research.dataset-analysis`, `finance.small-business-bookkeeping`; image →
   `photos.camera-events` (HEIC explicit); ocr → `photos.screenshot-captures`,
   `photos.scanned-documents`; email → `career.recruiting`, `finance.receipts-expenses`;
   contacts → `identity.core-documents` (privacy-protected, never a folder proposal);
   audio_video → `photos.home-video`; design_creative → `career.portfolio-work-samples`;
   archive → `applications.purpose-packet` (`00`'s submission.zip), `code.software-project`,
   `photos.social-media-export`; opaque_binary → `identity.credentials-passwords`.
5. **The 25-domains-verification gap list**: every named miss was resolved — kept as a template
   (crypto, HOA, cap tables, drone, PKM vaults, messenger exports, password managers,
   homeschool, MOOCs, IEP, social takeouts), covered by a residual (concert tickets, recipes,
   scrapbook), or refused with the reason recorded (§5 below: Time Machine, 3D print,
   SolidWorks/BIM, religion, divorce-as-such).

## 4. The 574 triaged — kept as templates vs dropped

Rough arithmetic over the 574 legacy ids: **~160 fold into the 73 template rows** (many-to-one
— e.g. four `res.manuscript-*`/review/preprint rows → `research.manuscript-publication`; a
dozen `career.*` employment rows → `career.employment-records`; `tax.filing` +
`tax.supporting-documents` → `finance.tax-filings`), **~40 drop as values** (work types,
document types, or formats masquerading as schemas), and **~370 are refused** professional
worlds with no schema to point at (recorded in §5, one carried as a placeholder row).

Representative mappings (kept → new id):

| Legacy (574) | Roster row |
|---|---|
| `acad.course-enrollment` / `acad.course-instruction` | `academic.coursework` / `academic.teaching` (PR-7: one schema) |
| `acad.college-application`, `acad.grad-school-application`, `acad.k12-school-admission` | `applications.undergraduate-packet`, `applications.graduate-professional`, `applications.k12-admission` |
| `res.manuscript-preparation` + `-submission` + `peer-review-*` + `preprint` + `published-article` | `research.manuscript-publication` |
| `res.lab-notebook`, `protocol-sop`, `instrument-output`, `sample-specimen` | `research.lab-notebook-protocols` |
| `career.job-search-campaign`, `job-application`, `interview-cycle`, `offer-and-negotiation` | `career.recruiting` |
| `career.consulting-engagement`, `client-proposal`, `freelance-contract-work` | `career.consulting-client-engagement` |
| `pers.photo-event`, `pers.screenshot`, `pers.scanned-document` | `photos.camera-events`, `photos.screenshot-captures`, `photos.scanned-documents` |
| `pers.travel-record` / `pers.travel-photos` | `travel.bookings-confirmations` (finance) / `travel.trip-photos` (photos) |
| `fin.insurance` + `pers.insurance` + `med.health-plan-coverage` + `med.insurance-claim-eob` | the three PR-8 insurance templates on finance |
| `corp.shareholder-captable`, `fundraising-investor` | `finance.cap-table-equity` |
| `npo.residents-association` | `finance.hoa-residents-association` |
| `pers.identity-document` / `admin.immigration` + `law.immigration-casework` | `identity.core-documents` / `identity.immigration-visa` |
| `med.*` patient-side (~12 rows) | `medical.personal-health-records`, `medical.dependant-child-health`, `medical.wearable-health-exports` |
| `legal.wills-trusts-estates`, `power-of-attorney`, `med.advance-directive`, `pers.estate` | `legal.estate-planning` |
| `law.*` (43 rows) | `legal.practice-matter-file` — one placeholder row for the whole practice world |
| `soft.source-project` (+ IaC, CI, containers, APIs …) | `code.software-project` |
| `soft.notebook-analysis`, `ml-experiment`, `dataset-artifact`, `model-artifact` | `code.notebooks-experiments` |

Dropped as **values, not nodes** (the fake-schema class): `career.resume`,
`career.cover-letter`, `career.academic-cv` (document types / version families);
`acad.recommendation-letter` received-side (an `application_document_type` value — the
recommender's own situation survives as `academic.recommendation-letters-written`);
`res.figure-and-source`, `res.poster` (artifact_type values); every `calendar.*` and `comms.*`
row (slice 14's format-as-schema bug — those are `SOURCE_TYPES` and extractors, now covered by
`file_kind_owner` assignments); most `soft.*` document kinds (ADRs, release notes, runbooks —
artifact_type values or repository content).

## 5. Coverage holes refused, and why

1. **Creative projects** — `00` §5.7 names them, and this roster cannot express them: no
   creative schema exists, PR-6 fixes the placeholder set at four, and the node test forbids an
   empty industry label. Only the portfolio face survives
   (`career.portfolio-work-samples`, which also owns `design_creative` files). ~46 legacy rows
   refused. **The largest hole — NJ-R1a-1.**
2. **Engineering/manufacturing (45), business ops/HR (45), government/civic (43), trades/
   property/logistics (56), clinician-side healthcare (~15), law-practice detail (42)** — the
   overnight pass's professional worlds. Refused rather than re-attached to ill-fitting
   schemas; one placeholder row (`legal.practice-matter-file`) marks the pattern. NJ-R1a-5.
3. **Travel as a schema** — refused per the dispatch rule (it needs no field `00` does not
   already have). Landed as two templates + the Receipts and Confirmations fallthrough;
   the real tension (no schema can express *trip → record type*) is NJ-R1a-2.
4. **Email / calendar / contacts as domains** — extractors and `SOURCE_TYPES`, never schemas
   (the `.ics` fixture). Covered via `file_kind_owner` instead.
5. **Time Machine / backups** — a P3 exclusion-policy concern (do not scan, do not propose),
   not an organizational situation. Recorded here so the gap list's mention is answered.
6. **Pets/veterinary, religion/faith life, hobbies & collections, genealogy documents,
   journals, gaming, 3D-print/maker files** — no honest schema; their isolated files are what
   the residual library exists for (Independent Records, Reference Clips, One-Off Images).
   Adding rows would have been the recorded failure mode.

## 6. Verification (both proofs run after the files landed)

- `python3 planning/domains/dispatch/make_prompt.py --all --out-dir …/r1b-prompts` →
  **wrote 83 prompts**, one per roster row, zero failures. Spot-checked stamps are correct.
- `python3 planning/domains/check.py` → the 14 legacy files report **exactly 566 in-file
  problems, 0 cross-file** — byte-identical to the pre-R1a baseline (the audited debt of the
  574; superseded, not repaired). `canonical_fields.json` parses, adds **zero** findings, and
  its `role_split_with` reciprocity passes. One new structural finding exists:
  `roster.json: no entries list` — `check.py`'s glob predates the roster and excludes only
  `_*` and `canonical_fields.json`; the roster is an assignment file, not a catalogue slice,
  and the dispatch-prompt shape (`nodes`, not `entries`) is deliberate. The one-line glob
  exclusion belongs to `check.py`'s owner (R1c/orchestrator); R1a's allowed paths do not
  include the gate.

## 7. NEEDS-JOSEPH

Open questions only — none closed here, none of CONNECTION.md's NJ-1…NJ-5 re-opened or
extended; PR-1…PR-8 are built on as recorded.

- **NJ-R1a-1 · Creative projects need a schema decision.** `00` §5.7 puts creative projects in
  the template library; no schema can host them and PR-6 closes the placeholder set at four.
  Options: (a) a fifth field-less placeholder schema for creative work, (b) a real small schema
  (candidate fields are mostly existing keys: `project`, `stage`, `artifact_type`, `client`),
  (c) wait for the §5.7 custom-template path. Until answered, ~46 legacy creative rows stay
  refused.
- **NJ-R1a-2 · Does travel deserve a small schema?** Neither photos nor finance can express
  *trip → record type* for bookings and itineraries. v1 ships `travel.trip-photos` (photos) +
  `travel.bookings-confirmations` (finance) + Receipts and Confirmations fallthrough. A travel
  schema would need no new canonical fields (`event`, `location`, `record_type`,
  `capture_year` exist) — the question is whether the *set* deserves a schema row.
- **NJ-R1a-3 · `target_school` vs `target_university`.** `00` spells the application-target
  concept both ways (§3.8 vs §3.11), and CONNECTION.md §6 seeds both as canonical keys — so
  both are emitted, with `target_school` referenced by **no** schema. Recommendation: fold
  `target_school` into `target_university` as an alias (one concept, one key — the D6
  discipline). Held open because CONNECTION.md names both in the seed.
- **NJ-R1a-4 · Two destination-eligibility calls seeded conservative.** `people` (photos) and
  `programming_language` (code) are seeded `destination_eligible: false` (privacy-loaded
  person-folders; preserved project structure). Real users do organize by person and by
  language; widening is a per-field canonical-list edit only Joseph should make.
- **NJ-R1a-5 · The professional worlds.** Engineering, ops/HR, government/civic,
  trades/property/logistics, clinician-side practice, law-practice detail — ~370 of the 574 —
  have no honest home under ten schemas. Which, if any, does v1 want as placeholder schemas
  (each would be a PR-6-style field-less row until demand justifies fields)?
- **NJ-R1a-6 · Scholarship sponsors strain `target_university`.**
  `applications.scholarship-fellowship` addresses packets to a sponsoring organization that is
  often not a university, yet the only target-side Applications key is `target_university`.
  Options: (a) sponsor names are simply values of `target_university` (one key, occasionally
  awkward), (b) rename the key to a broader target concept (a D6-style one-key decision), (c)
  a `role_split` sibling field. No new field was minted (the 574's failure mode); the row ships
  against the existing key until Joseph answers.
- **Carried, still open (not R1a's to answer):** NJ-1 (the counting rule for "500+" — this
  roster reports the connected-catalogue count per PR-3), NJ-2 (safety ordering — built to
  PR-2), NJ-3 (`purpose` scope — built to PR-1), NJ-4 (protected-record surfacing — PR-4),
  NJ-5 (does browse `parent_id` ship — PR-5; every roster `parent_id` is null, shelving left
  to R1c).
