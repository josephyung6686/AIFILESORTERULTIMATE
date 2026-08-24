# R1a — spine roster

Date: 2026-08-21
Status: **R1a deliverable, extended by the J-IND roster expansion (2026-08-22).** The schema list
+ template roster the R1b swarm is stamped onto, plus the canonical field catalogue schemas
reference. R1a's ten schemas and 73 templates are **unchanged and unrenumbered** — 83 landed node
files are keyed to them. J-IND adds thirteen placeholder schemas and 262 placeholder templates for
the professional worlds, and closes the 574's triage: **every one of the 574 legacy ids is now
accounted for in §4 and Appendix A** — as a row, as a documented fold into a row, or as a
documented value/format drop. Nothing is silently dropped.
Files: [`roster.json`](roster.json) · [`canonical_fields.json`](canonical_fields.json)
Contract chain (on conflict, in this order): `00` → [`prompts/ALIGNMENT.md`](../prompts/ALIGNMENT.md)
→ [`CONNECTION.md`](CONNECTION.md) (+ [`CONNECTION-EXAMPLES.md`](CONNECTION-EXAMPLES.md) fixtures)
→ the R1a dispatch prompt.
Decisions carried as recorded, not re-opened: D1 (narrowed — no career/identity/medical/legal
field rows), D2, D4, D6 (ratified — snake_case; the academic key is `subject`), PR-1…PR-8.

---

## 1. Counts — schemas few, templates honest

### 1a. R1a's roster (rows 1–83, frozen)

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
`is_safety_domain: true` (PR-2).

**Why R1a stopped at 73 templates.** `00` sizes the eventual library at "roughly 200–300
domain-specific templates". R1a stopped under, deliberately: a template must point at exactly one
existing schema and differ from that schema's default in detection signals, recommended
dimensions, or privacy rules (the CONNECTION.md §2 node test). With ten schemas — four of them
field-less — 73 is where honest rows ran out. The gap was **schema-shaped**: the professional and
creative worlds the overnight 574 sketched had no schema to point at, and minting those schemas
was exactly what `00` forbids doing prematurely ("without prematurely hand-authoring hundreds of
specialized schemas"). R1a recorded that as NJ-R1a-1 and NJ-R1a-5 rather than padding.

### 1b. The J-IND expansion (rows 84–358)

J-IND (ratified 2026-08-22, `overnight/council/DECISION-BRIEF.md`) answers NJ-R1a-1 and
NJ-R1a-5: the professional worlds get **placeholder coverage now plus gist-level per-industry
research**, and none of the 574's coverage is dropped silently. This pass adds:

| Kind | Added | Launch | Provenance |
|---|---|---|---|
| `schema` | **13** | 13 `placeholder` | 13 `proposal` |
| `template` | **262** | 262 `placeholder` | 262 `proposal` |

**Roster totals: 23 schemas · 335 templates · 358 rows.**

Every added row follows the **PR-6 placeholder shape**: `inherited_field_keys: []`, and the row
writes **no field rows**. D1's career/identity/medical/legal deferral stands and is extended to
all thirteen new schemas; **no canonical field key was minted** by this pass (proposed fields
belong to the R1c backlog, `26-research-dispatch-state.md` §4).

The thirteen new schemas, and the one line that licenses each:

| Schema | New templates | Why it is its own schema, not a fold |
|---|---|---|
| `creative` | 41 | `00` §5.7 names creative projects; the whole creative-media-design world (design, film, photo commissions, audio, writing, publishing, marketing, art, performance) has no other home. **Answers NJ-R1a-1.** |
| `engineering` | 24 | Design of physical product, plant and infrastructure. Its situations key on a **revision-controlled design artifact**, which neither `code` (repository structure) nor `research` (project → stage) expresses. |
| `manufacturing` | 19 | Making, inspecting and maintaining. Keys on a **batch, an asset or a nonconformance**, not on a design revision — a different situation from `engineering`, so a separate schema rather than a forced merge. |
| `business_operations` | 24 | How an organisation runs itself: strategy, governance, budgets, projects, policies, procurement, commercial and product management, and the IT function. `career` is the individual's side and cannot host the organisation's. |
| `hr` | 11 | The employer's people record. Split from `business_operations` because the material is employee-identifying and must be protected before any cloud step — a **privacy rule difference**, the node test's third licence. |
| `government` | 31 | The public authority's side: policy, legislation, rulemaking, consultation, public procurement, permits, casework, statistics, elections, and the state's education, cultural and archival bodies. |
| `nonprofit` | 10 | Charities, campaigns, unions, faith institutions, standards bodies, member associations. Split from `government` because the owner is a **private association, not a public authority** — different privacy posture and different record set. |
| `construction_property` | 27 | The job and the building: quotes, site surveys, drawings under revision, subcontracts, site diaries, statutory certificates, valuations, letting and block management. |
| `retail_hospitality` | 14 | Trading premises and guest-facing operations: catalogues, stock, till and e-commerce reporting, menus and food safety, licensing, bookings, events. |
| `logistics` | 7 | Moving and storing goods: consignments, customs, fleet and driver compliance, dispatch, warehousing, proof of delivery. |
| `resource_operations` | 8 | Metered, extracted and grown output: utility metering, generation and grid connection, oil and gas, mining, farming, fisheries, forestry. **The coarsest of the thirteen, and recorded as such** — see NJ-J-IND-2. |
| `clinical_practice` | 10 | The clinician's side of healthcare — charts *authored about* patients, referrals sent, credentialing, practice administration. The `medical` safety domain is the **patient's own** record; the role reverses and the privacy owner changes. |
| `law_practice` | 36 | A practitioner's matter work. R1a marked this world with one placeholder row (`legal.practice-matter-file`); that row **stays exactly as it is**, and `law_practice` now carries the detail. Client-confidential and privileged by default. |

Per PR-3, the number reported toward the 500+ request is still the **connected catalogue** — now
358 roster rows + 37 canonical fields + 9 residual homes + the folder depth inside templates —
never a manufactured row count. NJ-1 narrows accordingly (DECISION-BRIEF J-IND).

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

## 4. The 574 triaged — complete, and reconciled to the last id

**This is the J-IND obligation: every one of the 574 legacy ids ends as a row or as a written
reason. The per-id table is Appendix A.** The arithmetic:

| Outcome | Count | What it means |
|---|---|---|
| Became a roster row (1:1) | **270** | the id is now a `launch: placeholder` template row on one of the thirteen new schemas |
| Folded into an R1a row | **229** | the situation already exists among rows 1–83; the legacy id was a narrower spelling of it |
| Folded into a new J-IND row | **34** | two or more legacy ids describe one situation; the sibling is named in the surviving row's `one_line_hint` |
| Dropped — a **value**, not a node | **15** | a document type, work type, artifact type or version family masquerading as a schema |
| Dropped — a **format / SOURCE_TYPE** | **18** | calendar, mail, chat, call, contact and log material: P5 `SOURCE_TYPES` and extractors, never domains (CONNECTION.md's `.ics` fixture) |
| Dropped — **no honest schema**, residual library | **8** | genealogy, pets, recipes, hobbies, journals, gift occasions, personal faith life: ROSTER §5.6's refusal, unchanged by J-IND |
| **Total** | **574** | ✓ |

**262 new rows carry those 270 1:1 ids plus the 34 folded into them** — the surplus is deliberate
consolidation, and every absorbed id is named in the absorbing row's hint so the gist-swarm agent
sees what it owns.

R1a's prose estimate ("~160 fold / ~40 values / ~370 refused") was rounded and is superseded by
these exact counts. Its "~370 refused" was never counted precisely; what that bucket actually
contained is now split between the 270 ids that became rows, the 34 that fold into those new rows,
and the 8 that stay honestly refused to the residual library.

### Representative mappings (kept → roster row)

| Legacy (574) | Roster row |
|---|---|
| `acad.course-enrollment` / `acad.course-instruction` | `academic.coursework` / `academic.teaching` (PR-7: one schema) |
| `res.manuscript-preparation` + `-submission` + `peer-review-*` + `preprint` + `published-article` | `research.manuscript-publication` |
| `career.job-search-campaign`, `job-application`, `interview-cycle`, `offer-and-negotiation` | `career.recruiting` |
| `fin.insurance` + `pers.insurance` + `med.health-plan-coverage` + `med.insurance-claim-eob` | the three PR-8 insurance templates on finance |
| `law.*` (43 rows) | `legal.practice-matter-file` (unchanged marker) + **36 `law_practice.*` rows** |
| `med.clinician-*` (~10 rows) | **10 `clinical_practice.*` rows** |
| slice 10's 46 creative rows | **41 `creative.*` rows** + `career.portfolio-work-samples` |
| slice 09's 45 rows | **24 `engineering.*` + 19 `manufacturing.*`** |
| slice 11's 45 rows | **20 `business_operations.*` + 10 `hr.*`**, the employer-side hiring four folding into `career.employer-side-hiring` |
| slice 12's 44 rows | **31 `government.*` + 9 `nonprofit.*`** |
| slice 13's 56 rows | **27 `construction_property.*` + 14 `retail_hospitality.*` + 7 `logistics.*` + 8 `resource_operations.*`** |
| slice 14's 14 rows | **none** — format-as-schema, dropped with reason |

### Dropped as values, not nodes (the fake-schema class)

`career.resume`, `career.cover-letter`, `career.academic-cv` (document types / version families);
`acad.recommendation-letter` received-side (an `application_document_type` value — the
recommender's own situation survives as `academic.recommendation-letters-written`);
`res.figure-and-source`, `res.poster`, `design.presentation-deck` (artifact_type values); the
eight `soft.*` document kinds (design docs, ADRs, specs, release notes, runbooks, user docs, code
review artifacts, issue exports — artifact_type values or repository content). Every one is
listed with its reason in Appendix A.

### Dropped as formats

Every `calendar.*` and `comms.*` row (slice 14's format-as-schema bug), `soft.monitoring-log-export`,
`ops.internal-comms`, `pers.correspondence`, `career.networking-and-referrals`. These are
`SOURCE_TYPES` and extractors, now covered by `file_kind_owner` assignments on the roster; the
*export* case survives as `photos.messenger-export` and `photos.social-media-export`.

## 5. Coverage holes — what J-IND closed, and what stays refused

**Closed by J-IND (2026-08-22):**

1. ~~**Creative projects**~~ — **closed.** `creative` is now a placeholder schema with 41
   templates. `career.portfolio-work-samples` keeps the portfolio face and still owns
   `design_creative` files. NJ-R1a-1 is answered.
2. ~~**Engineering, business ops/HR, government/civic, trades/property/logistics, clinician-side
   healthcare, law-practice detail**~~ — **closed.** Twelve further placeholder schemas
   (`engineering`, `manufacturing`, `business_operations`, `hr`, `government`, `nonprofit`,
   `construction_property`, `retail_hospitality`, `logistics`, `resource_operations`,
   `clinical_practice`, `law_practice`) carry 221 templates between them. NJ-R1a-5 is answered.
   `legal.practice-matter-file` stays exactly as R1a wrote it — the marker row that named the
   pattern — and `law_practice` carries the detail beside it.

**Still refused, unchanged:**

3. **Travel as a schema** — still refused per the R1a dispatch rule (it needs no field `00` does
   not already have). Two templates + the Receipts and Confirmations fallthrough; NJ-R1a-2 stands.
4. **Email / calendar / contacts as domains** — extractors and `SOURCE_TYPES`, never schemas (the
   `.ics` fixture). All 14 of slice 14 dropped on this ground.
5. **Time Machine / backups** — a P3 exclusion-policy concern (do not scan, do not propose), not
   an organizational situation.
6. **Pets/veterinary as an owner's record, religion/faith life as personal practice, hobbies and
   collections, genealogy documents, journals, recipes, gift occasions** — still no honest schema;
   their isolated files are what the residual library exists for (Independent Records, Reference
   Clips, One-Off Images). Eight legacy ids stay here, each named in Appendix A. Note the two that
   changed *side*, not status: `npo.religious-institution` became `nonprofit.religious-institution`
   (an institution's administration is a real record set) and `med.veterinary-practice` became
   `clinical_practice.veterinary-practice` (a practice), while the **personal** faith and pet rows
   stay refused. That is a role split, not a reversal.
7. **3D-print / maker files** — R1a refused these; J-IND does not reopen them. `eng.prototype-build`
   → `engineering.prototype-build` covers additive manufacturing *as a professional build record*,
   which is a different owner from a hobbyist's print files.

## 6. Verification

### R1a (run after R1a's files landed)

- `python3 planning/domains/dispatch/make_prompt.py --all --out-dir …/r1b-prompts` →
  **wrote 83 prompts**, one per roster row, zero failures.
- `python3 planning/domains/check.py` → the 14 legacy files report **exactly 566 in-file
  problems, 0 cross-file** — byte-identical to the pre-R1a baseline (the audited debt of the
  574; superseded, not repaired). `canonical_fields.json` parses, adds **zero** findings, and
  its `role_split_with` reciprocity passes. `check.py`'s glob predates the roster and does not
  scan it or `nodes/`; extending it there is R1c's job.

### J-IND expansion (run after this pass's edits, 2026-08-23)

- `python3 -c "import json;json.load(open('planning/domains/roster.json'))"` → **parses.**
- `python3 planning/domains/dispatch/make_prompt.py --all --out-dir …` → **wrote 358 prompts**,
  one per roster row including all 275 new ones, zero failures.
- **The first 83 nodes are byte-identical to the pre-expansion file**, in the same order, with
  the same ids — proved by an element-wise comparison against a copy taken before the edit. No
  duplicate `domain_id` anywhere in the 358.
- `python3 planning/domains/check.py` → **14 files, 574 entries, 566 in-file problems;
  cross-file: 574 unique ids, 0 problems.** The legacy baseline is unchanged, as required.
- **Zero numeric values** anywhere in `roster.json` (rule 3 — every threshold stays an injected
  slot). All 574 legacy ids appear exactly once in the triage map, with no id triaged twice and
  no id left untriaged; the four outcome buckets sum to 574 (§4).

## 7. NEEDS-JOSEPH

Open questions only — none closed here, none of CONNECTION.md's NJ-1…NJ-5 re-opened or
extended; PR-1…PR-8 are built on as recorded.

- **NJ-R1a-1 · ~~Creative projects need a schema decision.~~ ANSWERED by J-IND** (2026-08-22):
  option (a) — a field-less placeholder schema. `creative` ships with 41 placeholder templates and
  no field rows. If a later pass wants option (b), the candidate fields are still the existing keys
  `project`, `stage`, `artifact_type`, `client`; nothing here forecloses it.
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
- **NJ-R1a-5 · ~~The professional worlds.~~ ANSWERED by J-IND** (2026-08-22): all of them, as
  PR-6-style field-less placeholder rows, plus gist-level per-industry research. Twelve schemas
  beyond `creative`; see §1b. Depth is a much later pass.
- **NJ-R1a-6 · Scholarship sponsors strain `target_university`.**
  `applications.scholarship-fellowship` addresses packets to a sponsoring organization that is
  often not a university, yet the only target-side Applications key is `target_university`.
  Options: (a) sponsor names are simply values of `target_university` (one key, occasionally
  awkward), (b) rename the key to a broader target concept (a D6-style one-key decision), (c)
  a `role_split` sibling field. No new field was minted (the 574's failure mode); the row ships
  against the existing key until Joseph answers.
### New, opened by the J-IND expansion

- **NJ-J-IND-1 · Thirteen new schemas, or fewer?** J-IND said "roughly 20" and this pass landed
  **23**. The count was driven by the 574, not by the target: `manufacturing` was split from
  `engineering` (batch/asset vs design revision), `hr` from `business_operations` (a privacy-rule
  difference, not a topic one), `nonprofit` from `government` (private association vs public
  authority), and `retail_hospitality` / `logistics` / `resource_operations` were kept apart
  because a freight consignment, a menu costing and a farm yield record share no situation. Each
  split is defensible on the CONNECTION.md §2 node test; **none is load-bearing.** If v1 wants the
  count nearer 20, merging `manufacturing` into `engineering` and `logistics` into
  `retail_hospitality` is the cheapest honest trim — say so and it is a rename pass, not a rewrite.
- **NJ-J-IND-2 · `resource_operations` is the coarsest schema on the roster.** Utility metering,
  renewable generation, grid connection, oil and gas, mining, farming, fisheries and forestry are
  one row family only because they all key on a site, an asset and a periodic regulated return.
  That is thinner than the licence the other twelve have. Split it, keep it, or let the gist swarm
  report back before deciding.
- **NJ-J-IND-3 · Where does an *organisation's* finance live?** `business_operations` hosts budgets
  and procurement, but the corporate accounting rows (`biz.*`, `corp.*`) were folded onto the
  **`finance` safety schema** (`finance.small-business-bookkeeping`, `finance.cap-table-equity`) as
  R1a placed them, while `corp.regulatory-filings` and `corp.compliance-audit` went to
  `business_operations`. That boundary is defensible but was drawn by this pass, not by `00`. A
  one-sentence ruling would settle it before the gist swarm writes 262 node files against it.
- **NJ-J-IND-4 · Do the new schemas need `is_safety_domain`?** `clinical_practice` (patient-
  identifying), `hr` (employee-identifying) and `law_practice` (privileged) all carry material as
  sensitive as the four §3.15 safety domains, and their rows say so in prose. But
  `is_safety_domain: true` marks **§3.15's four**, and inventing a fifth, sixth and seventh is not
  this pass's call (rule 15 / PR-2). None of the thirteen carries the flag. If they should, that is
  a decision, and it changes ordering (NJ-2).

- **Carried, still open (not R1a's to answer):** NJ-1 (the counting rule for "500+" — this
  roster reports the connected-catalogue count per PR-3), NJ-2 (safety ordering — built to
  PR-2), NJ-3 (`purpose` scope — built to PR-1), NJ-4 (protected-record surfacing — PR-4),
  NJ-5 (does browse `parent_id` ship — PR-5; every roster `parent_id` is null, shelving left
  to R1c).

---

## Appendix A — all 574 legacy ids, one line each

Generated from the triage map used to write `roster.json`; **every id in the fourteen legacy
catalogue files appears here exactly once.** Outcome codes:

- **ROW** — became a `launch: placeholder` template row on a new schema (the named row is new).
- **FOLD** — the situation is an existing roster row; the reason says why the two are one.
- **DROP·value** / **DROP·format** / **DROP·residual** — not a node; the reason says which class.

### 01-education-academia.json (40)

| Legacy id | Outcome | Roster row / reason |
|---|---|---|
| `acad.course-enrollment` | FOLD | → `academic.coursework` (existing row) — the same situation under its roster name |
| `acad.course-instruction` | FOLD | → `academic.teaching` (existing row) — the instructor side of one course; TA, tutoring and curriculum work differ in employment status, not in detection signals or dimensions |
| `acad.k12-schooling` | FOLD | → `academic.k12-schooling` (existing row) — the same situation under its roster name |
| `acad.undergraduate-program` | FOLD | → `academic.coursework` (existing row) — programme-level, lab, clinical, jury, advising, conduct and eligibility paperwork all key on school + term + subject; they add no dimension the coursework row does not already recommend |
| `acad.graduate-program` | FOLD | → `academic.coursework` (existing row) — programme-level, lab, clinical, jury, advising, conduct and eligibility paperwork all key on school + term + subject; they add no dimension the coursework row does not already recommend |
| `acad.professional-school` | FOLD | → `academic.coursework` (existing row) — programme-level, lab, clinical, jury, advising, conduct and eligibility paperwork all key on school + term + subject; they add no dimension the coursework row does not already recommend |
| `acad.continuing-education` | FOLD | → `academic.continuing-education` (existing row) — non-degree cohort and CPD study; one situation |
| `acad.bootcamp-cohort` | FOLD | → `academic.continuing-education` (existing row) — non-degree cohort and CPD study; one situation |
| `acad.self-study` | FOLD | → `academic.online-course` (existing row) — self-organised and language study are the MOOC row's own case |
| `acad.lab-course` | FOLD | → `academic.coursework` (existing row) — programme-level, lab, clinical, jury, advising, conduct and eligibility paperwork all key on school + term + subject; they add no dimension the coursework row does not already recommend |
| `acad.teaching-assistantship` | FOLD | → `academic.teaching` (existing row) — the instructor side of one course; TA, tutoring and curriculum work differ in employment status, not in detection signals or dimensions |
| `acad.tutoring` | FOLD | → `academic.teaching` (existing row) — the instructor side of one course; TA, tutoring and curriculum work differ in employment status, not in detection signals or dimensions |
| `acad.curriculum-development` | FOLD | → `academic.teaching` (existing row) — the instructor side of one course; TA, tutoring and curriculum work differ in employment status, not in detection signals or dimensions |
| `acad.college-application` | FOLD | → `applications.undergraduate-packet` (existing row) — the same situation under its roster name |
| `acad.k12-school-admission` | FOLD | → `applications.k12-admission` (existing row) — the same situation under its roster name |
| `acad.grad-school-application` | FOLD | → `applications.graduate-professional` (existing row) — the same situation under its roster name |
| `acad.standardized-testing` | FOLD | → `academic.standardized-testing` (existing row) — the same situation under its roster name |
| `acad.recommendation-letter` | DROP·value | received-side letters are an application_document_type VALUE; the writer's own situation survives as academic.recommendation-letters-written |
| `acad.transcript-record` | FOLD | → `academic.transcripts-credentials` (existing row) — official record of study held by the graduate |
| `acad.transfer-credit` | FOLD | → `academic.transcripts-credentials` (existing row) — official record of study held by the graduate |
| `acad.financial-aid` | FOLD | → `finance.student-financial-aid` (existing row) — aid and the student account are one finance situation |
| `acad.scholarship-fellowship` | FOLD | → `applications.scholarship-fellowship` (existing row) — the same situation under its roster name |
| `acad.tuition-billing` | FOLD | → `finance.student-financial-aid` (existing row) — aid and the student account are one finance situation |
| `acad.campus-employment` | FOLD | → `career.employment-records` (existing row) — a job held while studying is still one employer's employment record |
| `acad.thesis-dissertation` | FOLD | → `research.thesis-dissertation` (existing row) — the same situation under its roster name |
| `acad.undergrad-research` | FOLD | → `research.project-workspace` (existing row) — an undergraduate placement is a research project workspace |
| `acad.conference-travel-student` | FOLD | → `research.conference-presentation` (existing row) — student conference travel is the presentation row plus travel bookings |
| `acad.study-abroad` | FOLD | → `academic.study-abroad` (existing row) — the same situation under its roster name |
| `acad.clinical-rotation` | FOLD | → `academic.coursework` (existing row) — programme-level, lab, clinical, jury, advising, conduct and eligibility paperwork all key on school + term + subject; they add no dimension the coursework row does not already recommend |
| `acad.internship-for-credit` | FOLD | → `career.employment-records` (existing row) — a job held while studying is still one employer's employment record |
| `acad.language-study` | FOLD | → `academic.online-course` (existing row) — self-organised and language study are the MOOC row's own case |
| `acad.arts-jury-portfolio` | FOLD | → `academic.coursework` (existing row) — programme-level, lab, clinical, jury, advising, conduct and eligibility paperwork all key on school + term + subject; they add no dimension the coursework row does not already recommend |
| `acad.athletics-eligibility` | FOLD | → `academic.coursework` (existing row) — programme-level, lab, clinical, jury, advising, conduct and eligibility paperwork all key on school + term + subject; they add no dimension the coursework row does not already recommend |
| `acad.advising` | FOLD | → `academic.coursework` (existing row) — programme-level, lab, clinical, jury, advising, conduct and eligibility paperwork all key on school + term + subject; they add no dimension the coursework row does not already recommend |
| `acad.accommodations` | FOLD | → `academic.iep-accommodation-plans` (existing row) — the same situation under its roster name |
| `acad.integrity-case` | FOLD | → `academic.coursework` (existing row) — programme-level, lab, clinical, jury, advising, conduct and eligibility paperwork all key on school + term + subject; they add no dimension the coursework row does not already recommend |
| `acad.student-organization` | ROW | `nonprofit.member-association` |
| `acad.accreditation-institutional` | ROW | `government.education-accreditation` |
| `acad.alumni-record` | FOLD | → `academic.transcripts-credentials` (existing row) — official record of study held by the graduate |
| `acad.credential-certificate` | FOLD | → `academic.transcripts-credentials` (existing row) — official record of study held by the graduate |

### 02-career-recruiting.json (43)

| Legacy id | Outcome | Roster row / reason |
|---|---|---|
| `career.job-search-campaign` | FOLD | → `career.recruiting` (existing row) — one job search; stage is a value of the campaign, not a separate domain |
| `career.job-posting-collected` | FOLD | → `career.recruiting` (existing row) — one job search; stage is a value of the campaign, not a separate domain |
| `career.job-application` | FOLD | → `career.recruiting` (existing row) — one job search; stage is a value of the campaign, not a separate domain |
| `career.internship-application` | FOLD | → `career.recruiting` (existing row) — one job search; stage is a value of the campaign, not a separate domain |
| `career.academic-job-application` | FOLD | → `career.recruiting` (existing row) — one job search; stage is a value of the campaign, not a separate domain |
| `career.resume` | DROP·value | document types and version families, not organizational situations (the fake-schema class) |
| `career.academic-cv` | DROP·value | document types and version families, not organizational situations (the fake-schema class) |
| `career.cover-letter` | DROP·value | document types and version families, not organizational situations (the fake-schema class) |
| `career.portfolio` | FOLD | → `career.portfolio-work-samples` (existing row) — work samples and talks a person shows for career purposes |
| `career.interview-cycle` | FOLD | → `career.recruiting` (existing row) — one job search; stage is a value of the campaign, not a separate domain |
| `career.take-home-assessment` | FOLD | → `career.recruiting` (existing row) — one job search; stage is a value of the campaign, not a separate domain |
| `career.offer-and-negotiation` | FOLD | → `career.recruiting` (existing row) — one job search; stage is a value of the campaign, not a separate domain |
| `career.reference-and-recommendation` | FOLD | → `career.recruiting` (existing row) — one job search; stage is a value of the campaign, not a separate domain |
| `career.onboarding-paperwork` | FOLD | → `career.employment-records` (existing row) — the lifecycle of one employment relationship; each is a record_type inside it |
| `career.employment-contract` | FOLD | → `career.employment-records` (existing row) — the lifecycle of one employment relationship; each is a record_type inside it |
| `career.restrictive-covenant` | FOLD | → `career.employment-records` (existing row) — the lifecycle of one employment relationship; each is a record_type inside it |
| `career.work-authorization` | FOLD | → `identity.immigration-visa` (existing row) — sponsorship and work authorisation are immigration paperwork |
| `career.payroll` | FOLD | → `finance.payroll-received` (existing row) — payslips received are a finance record |
| `career.benefits-enrollment` | FOLD | → `career.employment-records` (existing row) — the lifecycle of one employment relationship; each is a record_type inside it |
| `career.equity-compensation` | FOLD | → `finance.cap-table-equity` (existing row) — grant and vesting paperwork sits with the equity row |
| `career.compensation-record` | FOLD | → `career.employment-records` (existing row) — the lifecycle of one employment relationship; each is a record_type inside it |
| `career.performance-review` | FOLD | → `career.employment-records` (existing row) — the lifecycle of one employment relationship; each is a record_type inside it |
| `career.promotion-packet` | FOLD | → `career.employment-records` (existing row) — the lifecycle of one employment relationship; each is a record_type inside it |
| `career.employment-verification` | FOLD | → `career.employment-records` (existing row) — the lifecycle of one employment relationship; each is a record_type inside it |
| `career.sabbatical-and-leave` | FOLD | → `career.employment-records` (existing row) — the lifecycle of one employment relationship; each is a record_type inside it |
| `career.layoff-and-severance` | FOLD | → `career.employment-records` (existing row) — the lifecycle of one employment relationship; each is a record_type inside it |
| `career.exit-and-offboarding` | FOLD | → `career.employment-records` (existing row) — the lifecycle of one employment relationship; each is a record_type inside it |
| `career.retirement-records` | FOLD | → `finance.investment-brokerage` (existing row) — pension and retirement accounts are investment accounts |
| `career.professional-license` | FOLD | → `career.credentials-licenses` (existing row) — licences, certifications, memberships and their CPD evidence are one credential file |
| `career.certification` | FOLD | → `career.credentials-licenses` (existing row) — licences, certifications, memberships and their CPD evidence are one credential file |
| `career.continuing-education` | FOLD | → `career.credentials-licenses` (existing row) — licences, certifications, memberships and their CPD evidence are one credential file |
| `career.professional-membership` | FOLD | → `career.credentials-licenses` (existing row) — licences, certifications, memberships and their CPD evidence are one credential file |
| `career.conference-attendance` | FOLD | → `career.credentials-licenses` (existing row) — licences, certifications, memberships and their CPD evidence are one credential file |
| `career.speaking-engagement` | FOLD | → `career.portfolio-work-samples` (existing row) — work samples and talks a person shows for career purposes |
| `career.networking-and-referrals` | DROP·format | contact and correspondence material; a contacts/email SOURCE_TYPE, not a domain |
| `career.consulting-engagement` | FOLD | → `career.consulting-client-engagement` (existing row) — one client engagement from proposal to invoice |
| `career.client-proposal` | FOLD | → `career.consulting-client-engagement` (existing row) — one client engagement from proposal to invoice |
| `career.freelance-contract-work` | FOLD | → `career.consulting-client-engagement` (existing row) — one client engagement from proposal to invoice |
| `career.service-invoicing` | FOLD | → `career.consulting-client-engagement` (existing row) — one client engagement from proposal to invoice |
| `career.employer-job-requisition` | FOLD | → `career.employer-side-hiring` (existing row) — the employer's side of one hire |
| `career.employer-candidate-packet` | FOLD | → `career.employer-side-hiring` (existing row) — the employer's side of one hire |
| `career.employer-interview-scorecard` | FOLD | → `career.employer-side-hiring` (existing row) — the employer's side of one hire |
| `career.employer-offer-approval` | FOLD | → `career.employer-side-hiring` (existing row) — the employer's side of one hire |

### 03-research-science.json (40)

| Legacy id | Outcome | Roster row / reason |
|---|---|---|
| `res.research-project` | FOLD | → `research.project-workspace` (existing row) — the same situation under its roster name |
| `res.manuscript-preparation` | FOLD | → `research.manuscript-publication` (existing row) — one manuscript from draft to published record; stage is a value |
| `res.manuscript-submission` | FOLD | → `research.manuscript-publication` (existing row) — one manuscript from draft to published record; stage is a value |
| `res.peer-review-author` | FOLD | → `research.manuscript-publication` (existing row) — one manuscript from draft to published record; stage is a value |
| `res.peer-review-referee` | FOLD | → `research.manuscript-publication` (existing row) — refereeing for others is the same schema with a role difference, not a new domain |
| `res.preprint` | FOLD | → `research.manuscript-publication` (existing row) — one manuscript from draft to published record; stage is a value |
| `res.published-article` | FOLD | → `research.manuscript-publication` (existing row) — one manuscript from draft to published record; stage is a value |
| `res.figure-and-source` | DROP·value | artifact_type values of the research schema |
| `res.dataset` | FOLD | → `research.dataset-analysis` (existing row) — data, its documentation, its outputs and its deposit are one analysis situation |
| `res.data-dictionary` | FOLD | → `research.dataset-analysis` (existing row) — data, its documentation, its outputs and its deposit are one analysis situation |
| `res.analysis-code` | FOLD | → `code.notebooks-experiments` (existing row) — analysis code and notebooks are the code schema's notebook row |
| `res.computational-notebook` | FOLD | → `code.notebooks-experiments` (existing row) — analysis code and notebooks are the code schema's notebook row |
| `res.statistical-output` | FOLD | → `research.dataset-analysis` (existing row) — data, its documentation, its outputs and its deposit are one analysis situation |
| `res.lab-notebook` | FOLD | → `research.lab-notebook-protocols` (existing row) — bench and field records of one project |
| `res.protocol-sop` | FOLD | → `research.lab-notebook-protocols` (existing row) — bench and field records of one project |
| `res.instrument-output` | FOLD | → `research.lab-notebook-protocols` (existing row) — bench and field records of one project |
| `res.sample-specimen` | FOLD | → `research.lab-notebook-protocols` (existing row) — bench and field records of one project |
| `res.grant-proposal` | FOLD | → `research.grants-funding` (existing row) — pre-award, post-award and the agreements that carry them |
| `res.grant-reporting` | FOLD | → `research.grants-funding` (existing row) — pre-award, post-award and the agreements that carry them |
| `res.irb-ethics` | FOLD | → `research.ethics-compliance` (existing row) — approvals, consent and trial documentation on the researcher side |
| `res.human-subjects-consent` | FOLD | → `research.ethics-compliance` (existing row) — approvals, consent and trial documentation on the researcher side |
| `res.clinical-trial` | FOLD | → `research.ethics-compliance` (existing row) — approvals, consent and trial documentation on the researcher side |
| `res.research-agreement` | FOLD | → `research.grants-funding` (existing row) — pre-award, post-award and the agreements that carry them |
| `res.conference-abstract` | FOLD | → `research.conference-presentation` (existing row) — the same situation under its roster name |
| `res.poster` | DROP·value | artifact_type values of the research schema |
| `res.talk` | FOLD | → `research.conference-presentation` (existing row) — the same situation under its roster name |
| `res.reading-library` | FOLD | → `research.reading-library` (existing row) — literature held for a project, however it is managed |
| `res.reference-library` | FOLD | → `research.reading-library` (existing row) — literature held for a project, however it is managed |
| `res.systematic-review` | FOLD | → `research.reading-library` (existing row) — literature held for a project, however it is managed |
| `res.thesis-supervision` | FOLD | → `research.thesis-dissertation` (existing row) — the supervisor's side of the same thesis |
| `res.patent-disclosure` | ROW | `engineering.invention-disclosure` |
| `res.software-release` | FOLD | → `code.software-project` (existing row) — a released research package is a software project |
| `res.reproducibility-package` | FOLD | → `research.dataset-analysis` (existing row) — data, its documentation, its outputs and its deposit are one analysis situation |
| `res.data-management-plan` | FOLD | → `research.grants-funding` (existing row) — pre-award, post-award and the agreements that carry them |
| `res.repository-deposit` | FOLD | → `research.dataset-analysis` (existing row) — data, its documentation, its outputs and its deposit are one analysis situation |
| `res.facility-booking` | FOLD | → `research.lab-notebook-protocols` (existing row) — bench and field records of one project |
| `res.field-work` | FOLD | → `research.lab-notebook-protocols` (existing row) — bench and field records of one project |
| `res.survey-instrument` | FOLD | → `research.dataset-analysis` (existing row) — data, its documentation, its outputs and its deposit are one analysis situation |
| `res.qualitative-coding` | FOLD | → `research.dataset-analysis` (existing row) — data, its documentation, its outputs and its deposit are one analysis situation |
| `res.correction-retraction` | FOLD | → `research.manuscript-publication` (existing row) — one manuscript from draft to published record; stage is a value |

### 04-personal-household.json (37)

| Legacy id | Outcome | Roster row / reason |
|---|---|---|
| `pers.photo-event` | FOLD | → `photos.camera-events` (existing row) — the same situation under its roster name |
| `pers.photo-occasion` | FOLD | → `photos.camera-events` (existing row) — the same situation under its roster name |
| `pers.family-photo-archive` | FOLD | → `photos.family-archive` (existing row) — the same situation under its roster name |
| `pers.screenshot` | FOLD | → `photos.screenshot-captures` (existing row) — the same situation under its roster name |
| `pers.scanned-document` | FOLD | → `photos.scanned-documents` (existing row) — the same situation under its roster name |
| `pers.home-video` | FOLD | → `photos.home-video` (existing row) — the same situation under its roster name |
| `pers.genealogy` | DROP·residual | no honest schema (ROSTER.md section 5.6, unchanged by J-IND): isolated personal files whose home is the residual library - Independent Records, Reference Clips, One-Off Images |
| `pers.travel-record` | FOLD | → `travel.bookings-confirmations` (existing row) — the same situation under its roster name |
| `pers.travel-visa-entry` | FOLD | → `identity.immigration-visa` (existing row) — visas and entry documents are identity paperwork |
| `pers.travel-photos` | FOLD | → `travel.trip-photos` (existing row) — the same situation under its roster name |
| `pers.household-admin` | FOLD | → `finance.household-property` (existing row) — the home as one record set: tenure, move, inventory and warranties |
| `pers.utilities` | FOLD | → `finance.subscriptions-utilities` (existing row) — recurring supply and membership billing |
| `pers.insurance` | FOLD | → `finance.insurance-personal` (existing row) — the same situation under its roster name |
| `pers.vehicle` | FOLD | → `finance.vehicle-records` (existing row) — the same situation under its roster name |
| `pers.home-tenure` | FOLD | → `finance.household-property` (existing row) — the home as one record set: tenure, move, inventory and warranties |
| `pers.moving` | FOLD | → `finance.household-property` (existing row) — the home as one record set: tenure, move, inventory and warranties |
| `pers.household-inventory` | FOLD | → `finance.household-property` (existing row) — the home as one record set: tenure, move, inventory and warranties |
| `pers.pet` | DROP·residual | no honest schema (ROSTER.md section 5.6, unchanged by J-IND): isolated personal files whose home is the residual library - Independent Records, Reference Clips, One-Off Images |
| `pers.medical-record` | FOLD | → `medical.personal-health-records` (existing row) — the same situation under its roster name |
| `pers.dependant-care` | FOLD | → `medical.dependant-child-health` (existing row) — health records held for another person, child or adult |
| `pers.eldercare` | FOLD | → `medical.dependant-child-health` (existing row) — health records held for another person, child or adult |
| `pers.fitness-activity` | FOLD | → `medical.wearable-health-exports` (existing row) — the same situation under its roster name |
| `pers.recipe-meal` | DROP·residual | no honest schema (ROSTER.md section 5.6, unchanged by J-IND): isolated personal files whose home is the residual library - Independent Records, Reference Clips, One-Off Images |
| `pers.hobby-collection` | DROP·residual | no honest schema (ROSTER.md section 5.6, unchanged by J-IND): isolated personal files whose home is the residual library - Independent Records, Reference Clips, One-Off Images |
| `pers.music-practice` | ROW | `creative.performing-practice` |
| `pers.creative-project` | ROW | `creative.self-initiated-work` |
| `pers.journal` | DROP·residual | no honest schema (ROSTER.md section 5.6, unchanged by J-IND): isolated personal files whose home is the residual library - Independent Records, Reference Clips, One-Off Images |
| `pers.correspondence` | DROP·format | personal correspondence is an email SOURCE_TYPE, never a domain (the .ics fixture rule) |
| `pers.gift-occasion` | DROP·residual | no honest schema (ROSTER.md section 5.6, unchanged by J-IND): isolated personal files whose home is the residual library - Independent Records, Reference Clips, One-Off Images |
| `pers.estate` | FOLD | → `legal.estate-planning` (existing row) — the same situation under its roster name |
| `pers.identity-document` | FOLD | → `identity.core-documents` (existing row) — the same situation under its roster name |
| `pers.membership` | FOLD | → `finance.subscriptions-utilities` (existing row) — recurring supply and membership billing |
| `pers.everyday-finance` | FOLD | → `finance.personal-records` (existing row) — the same situation under its roster name |
| `pers.child-school-record` | FOLD | → `academic.k12-schooling` (existing row) — the same situation under its roster name |
| `pers.volunteering` | ROW | `nonprofit.volunteer-management` |
| `pers.faith-community` | DROP·residual | personal faith life has no honest schema (ROSTER.md section 5.6); the institution-side situation survives as nonprofit.religious-institution |
| `pers.personal-legal` | FOLD | → `legal.personal-legal-matters` (existing row) — the same situation under its roster name |

### 05-finance-legal-admin.json (38)

| Legacy id | Outcome | Roster row / reason |
|---|---|---|
| `fin.financial-records` | FOLD | → `finance.personal-records` (existing row) — personal accounts and statements |
| `fin.bank-account` | FOLD | → `finance.personal-records` (existing row) — personal accounts and statements |
| `fin.investment-brokerage` | FOLD | → `finance.investment-brokerage` (existing row) — brokerage and retirement accounts are one account family |
| `fin.retirement-account` | FOLD | → `finance.investment-brokerage` (existing row) — brokerage and retirement accounts are one account family |
| `tax.filing` | FOLD | → `finance.tax-filings` (existing row) — a filing and the documents that support it are one tax_year record |
| `tax.supporting-documents` | FOLD | → `finance.tax-filings` (existing row) — a filing and the documents that support it are one tax_year record |
| `fin.receipts-expenses` | FOLD | → `finance.receipts-expenses` (existing row) — receipts, including donation receipts |
| `biz.expense-report` | FOLD | → `finance.small-business-bookkeeping` (existing row) — the books of one small business |
| `biz.invoice-issued` | FOLD | → `finance.small-business-bookkeeping` (existing row) — the books of one small business |
| `biz.invoice-received` | FOLD | → `finance.small-business-bookkeeping` (existing row) — the books of one small business |
| `biz.bookkeeping` | FOLD | → `finance.small-business-bookkeeping` (existing row) — the books of one small business |
| `biz.payroll-employer` | ROW | `hr.payroll-benefits-administration` |
| `corp.business-formation` | FOLD | → `finance.cap-table-equity` (existing row) — formation, ownership and fundraising are one corporate ownership record |
| `corp.shareholder-captable` | FOLD | → `finance.cap-table-equity` (existing row) — formation, ownership and fundraising are one corporate ownership record |
| `corp.fundraising-investor` | FOLD | → `finance.cap-table-equity` (existing row) — formation, ownership and fundraising are one corporate ownership record |
| `fin.loan-mortgage` | FOLD | → `finance.loans-mortgage` (existing row) — the same situation under its roster name |
| `fin.credit` | FOLD | → `finance.personal-records` (existing row) — personal accounts and statements |
| `fin.insurance` | FOLD | → `finance.insurance-personal` (existing row) — the same situation under its roster name |
| `legal.contracts` | FOLD | → `legal.leases-agreements` (existing row) — signed agreements of any kind |
| `legal.lease` | FOLD | → `legal.leases-agreements` (existing row) — signed agreements of any kind |
| `legal.litigation-dispute` | FOLD | → `legal.personal-legal-matters` (existing row) — a dispute a person is party to, at any stage |
| `legal.wills-trusts-estates` | FOLD | → `legal.estate-planning` (existing row) — the same situation under its roster name |
| `legal.power-of-attorney` | FOLD | → `legal.estate-planning` (existing row) — the same situation under its roster name |
| `corp.regulatory-filings` | ROW | `business_operations.corporate-regulatory-filings` |
| `corp.compliance-audit` | ROW | `business_operations.compliance-audit` |
| `admin.licences-permits` | FOLD | → `career.credentials-licenses` (existing row) — licences and registrations held by their holder |
| `legal.ip-registration` | ROW | `engineering.invention-disclosure` |
| `admin.immigration` | FOLD | → `identity.immigration-visa` (existing row) — the same situation under its roster name |
| `legal.court-records` | FOLD | → `legal.personal-legal-matters` (existing row) — a dispute a person is party to, at any stage |
| `legal.notarised-documents` | FOLD | → `legal.leases-agreements` (existing row) — signed agreements of any kind |
| `legal.debt-collection` | FOLD | → `legal.personal-legal-matters` (existing row) — a dispute a person is party to, at any stage |
| `legal.bankruptcy-insolvency` | FOLD | → `legal.personal-legal-matters` (existing row) — a dispute a person is party to, at any stage |
| `fin.charitable-giving` | FOLD | → `finance.receipts-expenses` (existing row) — receipts, including donation receipts |
| `fin.grants-received` | FOLD | → `research.grants-funding` (existing row) — awards received sit with the grant row |
| `admin.subscriptions-recurring` | FOLD | → `finance.subscriptions-utilities` (existing row) — the same situation under its roster name |
| `admin.warranties` | FOLD | → `finance.household-property` (existing row) — warranties and product registrations belong to the household inventory |
| `biz.procurement-po` | ROW | `business_operations.procurement-sourcing` |
| `biz.vendor-management` | ROW | `business_operations.vendor-management` |

### 06-healthcare-medicine.json (43)

| Legacy id | Outcome | Roster row / reason |
|---|---|---|
| `med.personal-health-record` | FOLD | → `medical.personal-health-records` (existing row) — the patient's own record; specialty and document kind are record_type values inside a field-less safety domain (D1/PR-6), never separate rows |
| `med.lab-result` | FOLD | → `medical.personal-health-records` (existing row) — the patient's own record; specialty and document kind are record_type values inside a field-less safety domain (D1/PR-6), never separate rows |
| `med.imaging-radiology` | FOLD | → `medical.personal-health-records` (existing row) — the patient's own record; specialty and document kind are record_type values inside a field-less safety domain (D1/PR-6), never separate rows |
| `med.prescription-medication` | FOLD | → `medical.personal-health-records` (existing row) — the patient's own record; specialty and document kind are record_type values inside a field-less safety domain (D1/PR-6), never separate rows |
| `med.immunisation-record` | FOLD | → `medical.personal-health-records` (existing row) — the patient's own record; specialty and document kind are record_type values inside a field-less safety domain (D1/PR-6), never separate rows |
| `med.referral-received` | FOLD | → `medical.personal-health-records` (existing row) — the patient's own record; specialty and document kind are record_type values inside a field-less safety domain (D1/PR-6), never separate rows |
| `med.hospital-admission-discharge` | FOLD | → `medical.personal-health-records` (existing row) — the patient's own record; specialty and document kind are record_type values inside a field-less safety domain (D1/PR-6), never separate rows |
| `med.surgical-procedure-record` | FOLD | → `medical.personal-health-records` (existing row) — the patient's own record; specialty and document kind are record_type values inside a field-less safety domain (D1/PR-6), never separate rows |
| `med.physical-therapy-rehab` | FOLD | → `medical.personal-health-records` (existing row) — the patient's own record; specialty and document kind are record_type values inside a field-less safety domain (D1/PR-6), never separate rows |
| `med.mental-health-record` | FOLD | → `medical.personal-health-records` (existing row) — the patient's own record; specialty and document kind are record_type values inside a field-less safety domain (D1/PR-6), never separate rows |
| `med.dental-record` | FOLD | → `medical.personal-health-records` (existing row) — the patient's own record; specialty and document kind are record_type values inside a field-less safety domain (D1/PR-6), never separate rows |
| `med.vision-eyecare-record` | FOLD | → `medical.personal-health-records` (existing row) — the patient's own record; specialty and document kind are record_type values inside a field-less safety domain (D1/PR-6), never separate rows |
| `med.allergy-intolerance-record` | FOLD | → `medical.personal-health-records` (existing row) — the patient's own record; specialty and document kind are record_type values inside a field-less safety domain (D1/PR-6), never separate rows |
| `med.chronic-condition-management` | FOLD | → `medical.personal-health-records` (existing row) — the patient's own record; specialty and document kind are record_type values inside a field-less safety domain (D1/PR-6), never separate rows |
| `med.pregnancy-maternity-record` | FOLD | → `medical.personal-health-records` (existing row) — the patient's own record; specialty and document kind are record_type values inside a field-less safety domain (D1/PR-6), never separate rows |
| `med.paediatric-child-health` | FOLD | → `medical.dependant-child-health` (existing row) — health records held for another person |
| `med.caregiving-dependant` | FOLD | → `medical.dependant-child-health` (existing row) — health records held for another person |
| `med.advance-directive` | FOLD | → `legal.estate-planning` (existing row) — advance directives are end-of-life legal instruments |
| `med.genetic-testing-report` | FOLD | → `medical.personal-health-records` (existing row) — the patient's own record; specialty and document kind are record_type values inside a field-less safety domain (D1/PR-6), never separate rows |
| `med.clinical-trial-participation` | FOLD | → `medical.personal-health-records` (existing row) — the patient's own record; specialty and document kind are record_type values inside a field-less safety domain (D1/PR-6), never separate rows |
| `med.medical-travel` | FOLD | → `medical.personal-health-records` (existing row) — the patient's own record; specialty and document kind are record_type values inside a field-less safety domain (D1/PR-6), never separate rows |
| `med.wearable-health-export` | FOLD | → `medical.wearable-health-exports` (existing row) — the same situation under its roster name |
| `med.medical-certification-letter` | FOLD | → `medical.personal-health-records` (existing row) — the patient's own record; specialty and document kind are record_type values inside a field-less safety domain (D1/PR-6), never separate rows |
| `med.occupational-health-screening` | FOLD | → `hr.workplace-health-safety` (new row) — employer-side screening is workplace health and safety administration |
| `med.health-plan-coverage` | FOLD | → `finance.insurance-healthcare` (existing row) — coverage, claims and their disputes are the PR-8 healthcare-insurance row |
| `med.insurance-claim-eob` | FOLD | → `finance.insurance-healthcare` (existing row) — coverage, claims and their disputes are the PR-8 healthcare-insurance row |
| `med.provider-billing-dispute` | FOLD | → `finance.insurance-healthcare` (existing row) — coverage, claims and their disputes are the PR-8 healthcare-insurance row |
| `med.clinician-patient-chart` | ROW | `clinical_practice.patient-chart` |
| `med.clinician-clinical-note` | FOLD | → `clinical_practice.patient-chart` (new row) — notes and plans are the chart's own contents |
| `med.clinician-treatment-plan` | FOLD | → `clinical_practice.patient-chart` (new row) — notes and plans are the chart's own contents |
| `med.clinician-case-conference` | ROW | `clinical_practice.case-conference` |
| `med.clinician-licensure-credentialing` | ROW | `clinical_practice.licensure-credentialing` |
| `med.clinician-cme` | FOLD | → `clinical_practice.licensure-credentialing` (new row) — CME is the evidence a registration requires |
| `med.clinician-malpractice-incident` | ROW | `clinical_practice.malpractice-incident` |
| `med.clinician-referral-sent` | ROW | `clinical_practice.referral-correspondence` |
| `med.clinical-protocol-guideline` | ROW | `clinical_practice.protocol-guideline` |
| `med.medical-teaching-material` | ROW | `clinical_practice.teaching-material` |
| `med.practice-administration` | ROW | `clinical_practice.practice-administration` |
| `med.device-and-implant-record` | FOLD | → `medical.personal-health-records` (existing row) — the patient's own record; specialty and document kind are record_type values inside a field-less safety domain (D1/PR-6), never separate rows |
| `med.pharmacy-operations` | ROW | `clinical_practice.pharmacy-operations` |
| `med.public-health-reporting` | FOLD | → `government.public-health-administration` (new row) — notifiable-disease and registry reporting is public health administration |
| `med.veterinary-practice` | ROW | `clinical_practice.veterinary-practice` |
| `med.veterinary-pet-owner` | DROP·residual | an owner's pet records have no honest schema (ROSTER.md section 5.6); the practice-side situation survives as clinical_practice.veterinary-practice |

### 07-law-legal-practice.json (43)

| Legacy id | Outcome | Roster row / reason |
|---|---|---|
| `law.matter-file` | FOLD | → `legal.practice-matter-file` (existing row) — the existing placeholder row that marked this whole world; it stays, and law_practice now carries the detail |
| `law.client-intake` | ROW | `law_practice.client-intake` |
| `law.conflicts-check` | ROW | `law_practice.conflicts-check` |
| `law.engagement-terms` | ROW | `law_practice.engagement-terms` |
| `law.time-and-billing` | ROW | `law_practice.time-and-billing` |
| `law.matter-correspondence` | ROW | `law_practice.matter-correspondence` |
| `law.limitation-and-diary` | ROW | `law_practice.deadlines-diary` |
| `law.pleadings` | ROW | `law_practice.pleadings` |
| `law.court-filing-record` | ROW | `law_practice.court-filing-record` |
| `law.motions-and-briefs` | ROW | `law_practice.motions-and-briefs` |
| `law.orders-and-judgments` | ROW | `law_practice.orders-and-judgments` |
| `law.appeals` | ROW | `law_practice.appeals` |
| `law.discovery-requests` | ROW | `law_practice.discovery` |
| `law.document-review` | FOLD | → `law_practice.discovery` (new row) — review work product and productions are stages of one disclosure exercise |
| `law.ediscovery-production` | FOLD | → `law_practice.discovery` (new row) — review work product and productions are stages of one disclosure exercise |
| `law.evidence-exhibits` | ROW | `law_practice.evidence-exhibits` |
| `law.depositions` | ROW | `law_practice.depositions-testimony` |
| `law.witness-statements` | FOLD | → `law_practice.depositions-testimony` (new row) — sworn witness evidence, written or oral |
| `law.expert-materials` | ROW | `law_practice.expert-materials` |
| `law.trial-preparation` | ROW | `law_practice.trial-preparation` |
| `law.jury-materials` | FOLD | → `law_practice.trial-preparation` (new row) — jury-facing material is prepared for one hearing |
| `law.hearing-transcripts` | ROW | `law_practice.hearing-transcripts` |
| `law.settlement` | ROW | `law_practice.settlement` |
| `law.adr` | FOLD | → `law_practice.settlement` (new row) — mediation and arbitration are how a settlement is reached |
| `law.legal-research` | ROW | `law_practice.legal-research` |
| `law.opinions` | ROW | `law_practice.opinions-advice` |
| `law.knowhow-precedents` | ROW | `law_practice.precedent-bank` |
| `law.transactional-deal` | ROW | `law_practice.transactional-deal` |
| `law.due-diligence` | ROW | `law_practice.due-diligence` |
| `law.closing-binder` | ROW | `law_practice.closing-binder` |
| `law.contract-negotiation` | ROW | `law_practice.contract-negotiation` |
| `law.corporate-secretarial` | ROW | `law_practice.corporate-secretarial` |
| `law.regulatory-submission` | ROW | `law_practice.regulatory-submission` |
| `law.compliance-programme` | FOLD | → `law_practice.regulatory-submission` (new row) — programme material and submissions are one regulatory file |
| `law.investigation` | ROW | `law_practice.investigation` |
| `law.ip-prosecution` | ROW | `law_practice.ip-prosecution` |
| `law.immigration-casework` | ROW | `law_practice.immigration-casework` |
| `law.family-law` | ROW | `law_practice.family-law` |
| `law.criminal-defence` | ROW | `law_practice.criminal-defence` |
| `law.estates-administration` | ROW | `law_practice.estates-administration` |
| `law.conveyancing` | ROW | `law_practice.conveyancing` |
| `law.bar-admission-cle` | ROW | `law_practice.admission-cle` |
| `law.pro-bono` | ROW | `law_practice.pro-bono` |

### 08-software-technology.json (40)

| Legacy id | Outcome | Roster row / reason |
|---|---|---|
| `soft.source-project` | FOLD | → `code.software-project` (existing row) — one repository; infrastructure, CI, schemas, specs and their security and licence findings live inside the project structure the code schema preserves |
| `soft.library-package` | FOLD | → `code.software-project` (existing row) — one repository; infrastructure, CI, schemas, specs and their security and licence findings live inside the project structure the code schema preserves |
| `soft.infrastructure-as-code` | FOLD | → `code.software-project` (existing row) — one repository; infrastructure, CI, schemas, specs and their security and licence findings live inside the project structure the code schema preserves |
| `soft.configuration-and-secrets` | FOLD | → `code.software-project` (existing row) — one repository; infrastructure, CI, schemas, specs and their security and licence findings live inside the project structure the code schema preserves |
| `soft.ci-cd-definition` | FOLD | → `code.software-project` (existing row) — one repository; infrastructure, CI, schemas, specs and their security and licence findings live inside the project structure the code schema preserves |
| `soft.container-deployment` | FOLD | → `code.software-project` (existing row) — one repository; infrastructure, CI, schemas, specs and their security and licence findings live inside the project structure the code schema preserves |
| `soft.database-schema-migration` | FOLD | → `code.software-project` (existing row) — one repository; infrastructure, CI, schemas, specs and their security and licence findings live inside the project structure the code schema preserves |
| `soft.api-specification` | FOLD | → `code.software-project` (existing row) — one repository; infrastructure, CI, schemas, specs and their security and licence findings live inside the project structure the code schema preserves |
| `soft.sdk-integration` | FOLD | → `code.software-project` (existing row) — one repository; infrastructure, CI, schemas, specs and their security and licence findings live inside the project structure the code schema preserves |
| `soft.data-pipeline` | FOLD | → `code.software-project` (existing row) — one repository; infrastructure, CI, schemas, specs and their security and licence findings live inside the project structure the code schema preserves |
| `soft.notebook-analysis` | FOLD | → `code.notebooks-experiments` (existing row) — one experiment and the data, models and prompts it consumes |
| `soft.ml-experiment` | FOLD | → `code.notebooks-experiments` (existing row) — one experiment and the data, models and prompts it consumes |
| `soft.dataset-artifact` | FOLD | → `code.notebooks-experiments` (existing row) — one experiment and the data, models and prompts it consumes |
| `soft.model-artifact` | FOLD | → `code.notebooks-experiments` (existing row) — one experiment and the data, models and prompts it consumes |
| `soft.prompt-eval-asset` | FOLD | → `code.notebooks-experiments` (existing row) — one experiment and the data, models and prompts it consumes |
| `soft.design-doc-rfc` | DROP·value | artifact_type values or repository content, not situations (ROSTER.md section 4's soft.* document-kind drop) |
| `soft.architecture-decision-record` | DROP·value | artifact_type values or repository content, not situations (ROSTER.md section 4's soft.* document-kind drop) |
| `soft.technical-specification` | DROP·value | artifact_type values or repository content, not situations (ROSTER.md section 4's soft.* document-kind drop) |
| `soft.issue-ticket-export` | DROP·value | artifact_type values or repository content, not situations (ROSTER.md section 4's soft.* document-kind drop) |
| `soft.code-review-artifact` | DROP·value | artifact_type values or repository content, not situations (ROSTER.md section 4's soft.* document-kind drop) |
| `soft.release-notes-changelog` | DROP·value | artifact_type values or repository content, not situations (ROSTER.md section 4's soft.* document-kind drop) |
| `soft.incident-postmortem` | FOLD | → `business_operations.retrospective-postmortem` (new row) — incident reviews and retrospectives are one situation |
| `soft.runbook-operational-doc` | DROP·value | artifact_type values or repository content, not situations (ROSTER.md section 4's soft.* document-kind drop) |
| `soft.monitoring-log-export` | DROP·format | generated machine output; a SOURCE_TYPE, never a domain |
| `soft.performance-load-test` | FOLD | → `code.software-project` (existing row) — one repository; infrastructure, CI, schemas, specs and their security and licence findings live inside the project structure the code schema preserves |
| `soft.security-finding-report` | FOLD | → `code.software-project` (existing row) — one repository; infrastructure, CI, schemas, specs and their security and licence findings live inside the project structure the code schema preserves |
| `soft.vulnerability-disclosure` | FOLD | → `code.software-project` (existing row) — one repository; infrastructure, CI, schemas, specs and their security and licence findings live inside the project structure the code schema preserves |
| `soft.tech-compliance-evidence` | FOLD | → `business_operations.compliance-audit` (new row) — control evidence is gathered for an audit |
| `soft.licence-oss-compliance` | FOLD | → `code.software-project` (existing row) — one repository; infrastructure, CI, schemas, specs and their security and licence findings live inside the project structure the code schema preserves |
| `soft.dev-environment-setup` | FOLD | → `code.dotfiles-environment` (existing row) — the same situation under its roster name |
| `soft.personal-dotfiles` | FOLD | → `code.dotfiles-environment` (existing row) — the same situation under its roster name |
| `soft.scratch-prototype` | FOLD | → `code.scratch-prototypes` (existing row) — the same situation under its roster name |
| `soft.game-development-asset` | FOLD | → `creative.game-art-asset` (new row) — game assets are a creative production |
| `soft.embedded-firmware` | ROW | `engineering.embedded-firmware` |
| `soft.hardware-design-file` | FOLD | → `engineering.pcb-layout` (new row) — board and hardware design files are engineering fabrication packages |
| `soft.network-diagram` | FOLD | → `business_operations.it-asset-inventory` (new row) — diagrams describe the estate the inventory records |
| `soft.it-asset-inventory` | ROW | `business_operations.it-asset-inventory` |
| `soft.helpdesk-ticket` | ROW | `business_operations.support-operations` |
| `soft.user-documentation` | DROP·value | artifact_type values or repository content, not situations (ROSTER.md section 4's soft.* document-kind drop) |
| `soft.training-material` | FOLD | → `hr.training-development` (new row) — technical training material is learning-and-development content |

### 09-engineering-manufacturing.json (45)

| Legacy id | Outcome | Roster row / reason |
|---|---|---|
| `eng.engineering-project` | ROW | `engineering.project` |
| `eng.requirements-specification` | ROW | `engineering.requirements-specification` |
| `eng.stage-gate-review` | ROW | `engineering.stage-gate-review` |
| `eng.industrial-design` | ROW | `engineering.industrial-design` |
| `eng.cad-model` | ROW | `engineering.cad-model` |
| `eng.drawing-package` | ROW | `engineering.drawing-package` |
| `eng.gdt-tolerance` | FOLD | → `engineering.drawing-package` (new row) — tolerancing is stated on the drawing it belongs to |
| `eng.bill-of-materials` | ROW | `engineering.bill-of-materials` |
| `eng.change-order` | ROW | `engineering.change-order` |
| `eng.simulation-fea` | ROW | `engineering.simulation-analysis` |
| `eng.electrical-schematic` | ROW | `engineering.electrical-schematic` |
| `eng.pcb-layout` | ROW | `engineering.pcb-layout` |
| `eng.civil-structural` | ROW | `engineering.civil-structural` |
| `eng.process-flow-pid` | ROW | `engineering.process-plant-design` |
| `eng.aerospace-airworthiness` | ROW | `engineering.aerospace-airworthiness` |
| `eng.automotive-program` | ROW | `engineering.automotive-program` |
| `eng.material-specification` | ROW | `engineering.material-specification` |
| `eng.component-datasheet` | FOLD | → `engineering.material-specification` (new row) — vendor datasheets are the specification's reference material |
| `eng.risk-analysis-fmea` | ROW | `engineering.risk-analysis-fmea` |
| `eng.prototype-build` | ROW | `engineering.prototype-build` |
| `eng.verification-validation` | ROW | `engineering.verification-validation` |
| `eng.commissioning-handover` | ROW | `engineering.commissioning-handover` |
| `eng.as-built-record` | FOLD | → `engineering.commissioning-handover` (new row) — as-built documentation is what handover delivers |
| `eng.invention-disclosure` | ROW | `engineering.invention-disclosure` |
| `cert.certification-file` | ROW | `engineering.product-certification` |
| `cert.standards-library` | ROW | `engineering.standards-library` |
| `mfg.production-planning` | ROW | `manufacturing.production-planning` |
| `mfg.work-instruction` | ROW | `manufacturing.work-instruction` |
| `mfg.production-record` | ROW | `manufacturing.production-record` |
| `mfg.tooling-fixture` | ROW | `manufacturing.tooling-fixture` |
| `qual.management-system` | ROW | `manufacturing.quality-management-system` |
| `qual.inspection-record` | ROW | `manufacturing.inspection-record` |
| `qual.calibration-record` | ROW | `manufacturing.calibration-record` |
| `qual.nonconformance-capa` | ROW | `manufacturing.nonconformance-capa` |
| `qual.failure-analysis-rca` | ROW | `manufacturing.failure-analysis` |
| `qual.supplier-qualification` | ROW | `manufacturing.supplier-qualification` |
| `qual.warranty-claim` | ROW | `manufacturing.warranty-claim` |
| `mro.asset-record` | ROW | `manufacturing.asset-register` |
| `mro.maintenance-work-order` | ROW | `manufacturing.maintenance-work-order` |
| `mro.spare-parts` | ROW | `manufacturing.spare-parts` |
| `mro.field-service-report` | ROW | `manufacturing.field-service-report` |
| `hse.safety-case` | ROW | `manufacturing.safety-case` |
| `hse.incident-record` | ROW | `manufacturing.hse-incident` |
| `hse.environmental-compliance` | ROW | `manufacturing.environmental-compliance` |
| `hse.energy-audit` | ROW | `manufacturing.energy-audit` |

### 10-creative-media-design.json (46)

| Legacy id | Outcome | Roster row / reason |
|---|---|---|
| `studio.client-engagement` | ROW | `creative.client-engagement` |
| `studio.creative-brief` | ROW | `creative.creative-brief` |
| `studio.revision-round` | ROW | `creative.revision-round` |
| `studio.deliverable-handoff` | ROW | `creative.deliverable-handoff` |
| `studio.licensing-rights` | ROW | `creative.licensing-rights` |
| `studio.stock-asset-library` | ROW | `creative.stock-asset-library` |
| `studio.portfolio-showreel` | FOLD | → `career.portfolio-work-samples` (existing row) — the existing row that already owns design_creative work samples |
| `studio.self-initiated-work` | ROW | `creative.self-initiated-work` |
| `design.graphic-project` | ROW | `creative.graphic-design-project` |
| `design.brand-identity` | ROW | `creative.brand-identity` |
| `design.uiux-product` | ROW | `creative.uiux-product-design` |
| `design.design-system-library` | FOLD | → `creative.uiux-product-design` (new row) — a design system is the product design work's own component library |
| `design.illustration` | ROW | `creative.illustration` |
| `design.typeface-and-font` | ROW | `creative.typeface-font` |
| `design.print-production` | ROW | `creative.print-production` |
| `design.presentation-deck` | DROP·value | a deck is an artifact_type value; the situation that produces it is the engagement or the pitch it belongs to |
| `design.interior` | ROW | `creative.interior-design` |
| `design.architecture-visual` | ROW | `creative.architectural-visualisation` |
| `design.fashion` | ROW | `creative.fashion-collection` |
| `photo.commissioned-shoot` | ROW | `creative.commissioned-shoot` |
| `photo.raw-catalogue` | ROW | `creative.raw-photo-catalogue` |
| `film.production` | ROW | `creative.film-production` |
| `film.shoot-day-media` | ROW | `creative.shoot-day-media` |
| `film.post-production` | ROW | `creative.post-production` |
| `film.motion-graphics` | ROW | `creative.motion-graphics` |
| `cg.3d-asset` | ROW | `creative.3d-asset` |
| `game.art-asset` | ROW | `creative.game-art-asset` |
| `audio.music-session` | ROW | `creative.music-session` |
| `audio.podcast-episode` | ROW | `creative.podcast-episode` |
| `audio.sound-design` | ROW | `creative.sound-design` |
| `write.manuscript` | ROW | `creative.book-manuscript` |
| `write.short-form` | ROW | `creative.short-form-writing` |
| `write.screenplay` | ROW | `creative.screenplay` |
| `write.editing-pass` | FOLD | → `creative.book-manuscript` (new row) — an editing pass is a stage of the manuscript's version family |
| `write.translation` | ROW | `creative.translation-project` |
| `news.reporting` | ROW | `creative.journalism-reporting` |
| `pub.title-production` | ROW | `creative.publishing-title` |
| `pub.submission-query` | ROW | `creative.submission-query` |
| `pub.periodical-issue` | ROW | `creative.periodical-issue` |
| `media.content-marketing` | ROW | `creative.content-marketing` |
| `media.social-assets` | FOLD | → `creative.content-marketing` (new row) — social assets are content-marketing deliverables |
| `media.ad-campaign` | ROW | `creative.ad-campaign` |
| `art.exhibition` | ROW | `creative.exhibition` |
| `art.printmaking` | ROW | `creative.printmaking-editions` |
| `perf.theatre-production` | ROW | `creative.theatre-production` |
| `perf.performing-artist` | ROW | `creative.performing-practice` |

### 11-business-operations.json (45)

| Legacy id | Outcome | Roster row / reason |
|---|---|---|
| `ops.business-records` | ROW | `business_operations.organisational-records` |
| `ops.strategy-plan` | ROW | `business_operations.strategy-plan` |
| `ops.board-governance` | ROW | `business_operations.board-governance` |
| `ops.okr-goals` | FOLD | → `business_operations.strategy-plan` (new row) — goals and investment cases are how a strategy is stated and funded |
| `ops.operating-plan-budget` | ROW | `business_operations.budget-forecast` |
| `ops.business-case` | FOLD | → `business_operations.strategy-plan` (new row) — goals and investment cases are how a strategy is stated and funded |
| `ops.meeting-record` | ROW | `business_operations.meeting-record` |
| `ops.status-report` | FOLD | → `business_operations.project-delivery` (new row) — portfolio roll-up and status reporting are views of the same delivery record |
| `ops.internal-comms` | DROP·format | internal communications are an email or chat SOURCE_TYPE, never a domain (the .ics fixture rule) |
| `ops.project` | ROW | `business_operations.project-delivery` |
| `ops.programme-portfolio` | FOLD | → `business_operations.project-delivery` (new row) — portfolio roll-up and status reporting are views of the same delivery record |
| `ops.retrospective-postmortem` | ROW | `business_operations.retrospective-postmortem` |
| `ops.risk-register` | ROW | `business_operations.risk-register` |
| `ops.business-continuity` | FOLD | → `business_operations.risk-register` (new row) — continuity planning is the register's treatment side |
| `ops.policy-handbook` | ROW | `business_operations.policy-handbook` |
| `ops.process-documentation` | FOLD | → `business_operations.policy-handbook` (new row) — policies and procedures are one governing-document set |
| `ops.facilities-workplace` | ROW | `business_operations.facilities-workplace` |
| `ops.business-travel` | FOLD | → `travel.bookings-confirmations` (existing row) — the existing travel row covers bookings whoever pays |
| `ops.sourcing-rfp` | ROW | `business_operations.procurement-sourcing` |
| `ops.contract-administration` | ROW | `business_operations.contract-administration` |
| `ops.client-engagement` | FOLD | → `career.consulting-client-engagement` (existing row) — the existing engagement row already covers professional-services delivery |
| `ops.customer-success` | ROW | `business_operations.customer-account-management` |
| `ops.support-operations` | ROW | `business_operations.support-operations` |
| `ops.partnerships-bd` | ROW | `business_operations.partnerships-bd` |
| `ops.market-competitive-research` | ROW | `business_operations.market-research` |
| `ops.pricing` | FOLD | → `business_operations.market-research` (new row) — pricing work is built on the same commercial analysis |
| `ops.product-roadmap` | ROW | `business_operations.product-roadmap` |
| `ops.product-requirements` | ROW | `business_operations.product-requirements` |
| `ops.user-research` | ROW | `business_operations.user-research` |
| `ops.go-to-market` | ROW | `business_operations.go-to-market` |
| `hr.org-design-headcount` | ROW | `hr.org-design-headcount` |
| `hr.job-requisition` | FOLD | → `career.employer-side-hiring` (existing row) — the existing employer-side hiring row covers one hire end to end |
| `hr.recruiting-pipeline` | FOLD | → `career.employer-side-hiring` (existing row) — the existing employer-side hiring row covers one hire end to end |
| `hr.interview-panel` | FOLD | → `career.employer-side-hiring` (existing row) — the existing employer-side hiring row covers one hire end to end |
| `hr.offer-package` | FOLD | → `career.employer-side-hiring` (existing row) — the existing employer-side hiring row covers one hire end to end |
| `hr.onboarding` | ROW | `hr.onboarding-offboarding` |
| `hr.offboarding` | FOLD | → `hr.onboarding-offboarding` (new row) — joining and leaving are one lifecycle record |
| `hr.training-lnd` | ROW | `hr.training-development` |
| `hr.performance-cycle` | ROW | `hr.performance-cycle` |
| `hr.engagement-survey` | ROW | `hr.engagement-survey` |
| `hr.compensation-planning` | ROW | `hr.compensation-planning` |
| `hr.workforce-analytics` | ROW | `hr.workforce-analytics` |
| `hr.dei-program` | ROW | `hr.dei-program` |
| `hr.employee-relations` | ROW | `hr.employee-relations` |
| `hr.health-safety` | ROW | `hr.workplace-health-safety` |

### 12-government-civic.json (44)

| Legacy id | Outcome | Roster row / reason |
|---|---|---|
| `gov.public-authority-record` | ROW | `government.public-authority-record` |
| `gov.policy-development` | ROW | `government.policy-development` |
| `gov.legislative-record` | ROW | `government.legislative-record` |
| `gov.regulatory-rulemaking` | ROW | `government.regulatory-rulemaking` |
| `gov.public-consultation` | ROW | `government.public-consultation` |
| `gov.intergovernmental-agreement` | FOLD | → `government.policy-development` (new row) — an agreement is an instrument of the policy it implements |
| `gov.municipal-administration` | ROW | `government.municipal-administration` |
| `gov.grant-programme-administration` | ROW | `government.grant-programme-administration` |
| `gov.procurement-tender` | ROW | `government.public-procurement` |
| `gov.contract-award-record` | FOLD | → `government.public-procurement` (new row) — award and contract management close the tender that opened them |
| `gov.planning-application` | ROW | `government.planning-application` |
| `gov.permit-licensing-authority` | ROW | `government.permit-licensing` |
| `gov.public-records-foi` | ROW | `government.public-records-foi` |
| `gov.census-statistical-programme` | ROW | `government.statistical-programme` |
| `gov.elections-administration` | ROW | `government.elections-administration` |
| `civic.political-campaign` | ROW | `nonprofit.political-campaign` |
| `gov.constituent-casework` | ROW | `government.constituent-casework` |
| `gov.international-development-programme` | ROW | `government.international-development` |
| `gov.diplomatic-consular-record` | ROW | `government.diplomatic-consular` |
| `gov.defence-veterans-administration` | ROW | `government.defence-veterans` |
| `gov.emergency-management` | ROW | `government.emergency-management` |
| `gov.public-health-administration` | ROW | `government.public-health-administration` |
| `gov.social-services-casework` | ROW | `government.social-services-casework` |
| `gov.housing-authority` | ROW | `government.housing-authority` |
| `gov.transport-authority` | ROW | `government.transport-authority` |
| `gov.environmental-regulation` | ROW | `government.environmental-regulation` |
| `gov.parks-public-lands` | ROW | `government.parks-public-lands` |
| `gov.professional-regulator` | ROW | `government.professional-regulator` |
| `gov.library-administration` | ROW | `government.library-administration` |
| `gov.archives-recordkeeping` | ROW | `government.archives-recordkeeping` |
| `gov.museum-collection` | ROW | `government.museum-collection` |
| `edadmin.school-district` | ROW | `government.school-district-administration` |
| `edadmin.institution-governance` | ROW | `government.education-institution-governance` |
| `edadmin.accreditation-body` | ROW | `government.education-accreditation` |
| `civic.standards-body` | ROW | `nonprofit.standards-body` |
| `npo.governance` | ROW | `nonprofit.governance` |
| `npo.fundraising-donor` | ROW | `nonprofit.fundraising-donor` |
| `npo.volunteer-management` | ROW | `nonprofit.volunteer-management` |
| `npo.grant-reporting-recipient` | ROW | `nonprofit.grant-reporting` |
| `civic.advocacy-campaign` | ROW | `nonprofit.advocacy-campaign` |
| `civic.community-organising` | FOLD | → `nonprofit.advocacy-campaign` (new row) — organising and campaigning are one situation at different scales |
| `npo.religious-institution` | ROW | `nonprofit.religious-institution` |
| `npo.residents-association` | FOLD | → `finance.hoa-residents-association` (existing row) — the existing HOA row already covers it |
| `civic.trade-union` | ROW | `nonprofit.trade-union` |

### 13-trades-property-logistics.json (56)

| Legacy id | Outcome | Roster row / reason |
|---|---|---|
| `trade.job` | ROW | `construction_property.trade-job` |
| `trade.quote-estimate` | ROW | `construction_property.quote-estimate` |
| `cons.site-survey` | ROW | `construction_property.site-survey` |
| `cons.project` | ROW | `construction_property.construction-project` |
| `cons.drawings-revisions` | ROW | `construction_property.drawings-revisions` |
| `cons.subcontract` | ROW | `construction_property.subcontract` |
| `cons.site-diary` | ROW | `construction_property.site-diary` |
| `cons.progress-photos` | ROW | `construction_property.progress-photos` |
| `cons.snagging` | ROW | `construction_property.snagging-defects` |
| `cons.building-control` | ROW | `construction_property.building-control` |
| `trade.compliance-certificate` | ROW | `construction_property.compliance-certificate` |
| `cons.method-statement-ra` | ROW | `construction_property.site-health-safety` |
| `cons.plant-hire` | ROW | `construction_property.plant-hire` |
| `cons.materials-delivery` | ROW | `construction_property.materials-delivery` |
| `trade.timesheet` | ROW | `construction_property.timesheet` |
| `cons.variation-claim` | ROW | `construction_property.variation-claim` |
| `cons.final-account` | ROW | `construction_property.final-account` |
| `prop.sale-purchase` | ROW | `construction_property.sale-purchase` |
| `prop.tenancy` | ROW | `construction_property.tenancy-management` |
| `prop.inventory-inspection` | ROW | `construction_property.inventory-inspection` |
| `prop.service-charge` | ROW | `construction_property.service-charge` |
| `prop.block-management` | ROW | `construction_property.block-management` |
| `prop.commercial-lease` | ROW | `construction_property.commercial-lease` |
| `prop.development-appraisal` | ROW | `construction_property.development-appraisal` |
| `prop.survey-valuation` | ROW | `construction_property.survey-valuation` |
| `prop.listing` | ROW | `construction_property.agency-listing` |
| `prop.mortgage-brokering` | ROW | `construction_property.mortgage-brokering` |
| `retail.product-catalogue` | ROW | `retail_hospitality.product-catalogue` |
| `retail.stocktake` | ROW | `retail_hospitality.stocktake` |
| `retail.supplier-order` | ROW | `retail_hospitality.supplier-order` |
| `retail.pos-reporting` | ROW | `retail_hospitality.pos-reporting` |
| `retail.ecommerce-ops` | ROW | `retail_hospitality.ecommerce-ops` |
| `retail.returns-warranty` | ROW | `retail_hospitality.returns-warranty` |
| `retail.store-ops` | ROW | `retail_hospitality.store-operations` |
| `hosp.menu-recipe-costing` | ROW | `retail_hospitality.menu-recipe-costing` |
| `hosp.food-safety` | ROW | `retail_hospitality.food-safety` |
| `hosp.premises-licensing` | ROW | `retail_hospitality.premises-licensing` |
| `event.production` | ROW | `retail_hospitality.event-production` |
| `hosp.bookings` | ROW | `retail_hospitality.bookings-reservations` |
| `hosp.catering-contract` | ROW | `retail_hospitality.catering-contract` |
| `hosp.guest-feedback` | ROW | `retail_hospitality.guest-feedback` |
| `log.shipment` | ROW | `logistics.shipment` |
| `log.customs-export` | ROW | `logistics.customs-export` |
| `fleet.vehicle` | ROW | `logistics.fleet-vehicle` |
| `fleet.driver-compliance` | ROW | `logistics.driver-compliance` |
| `log.route-dispatch` | ROW | `logistics.route-dispatch` |
| `log.warehouse-ops` | ROW | `logistics.warehouse-ops` |
| `log.last-mile-pod` | ROW | `logistics.last-mile-pod` |
| `util.metering-billing` | ROW | `resource_operations.utility-metering-billing` |
| `energy.renewable-generation` | ROW | `resource_operations.renewable-generation` |
| `energy.grid-connection` | ROW | `resource_operations.grid-connection` |
| `energy.oil-gas-ops` | ROW | `resource_operations.oil-gas-operations` |
| `mining.ops` | ROW | `resource_operations.mining-operations` |
| `agri.farm-records` | ROW | `resource_operations.farm-records` |
| `fish.catch-records` | ROW | `resource_operations.fisheries-catch` |
| `forest.records` | ROW | `resource_operations.forestry-records` |

### 14-time-scheduling-communications.json (14)

| Legacy id | Outcome | Roster row / reason |
|---|---|---|
| `calendar.events` | DROP·format | slice 14's format-as-schema bug: calendar, mail, chat, call and contact material are P5 SOURCE_TYPES and extractors, never domains (CONNECTION.md's .ics fixture). Covered by file_kind_owner assignments and, for exports, photos.messenger-export / photos.social-media-export |
| `calendar.appointment` | DROP·format | slice 14's format-as-schema bug: calendar, mail, chat, call and contact material are P5 SOURCE_TYPES and extractors, never domains (CONNECTION.md's .ics fixture). Covered by file_kind_owner assignments and, for exports, photos.messenger-export / photos.social-media-export |
| `calendar.recurring-commitment` | DROP·format | slice 14's format-as-schema bug: calendar, mail, chat, call and contact material are P5 SOURCE_TYPES and extractors, never domains (CONNECTION.md's .ics fixture). Covered by file_kind_owner assignments and, for exports, photos.messenger-export / photos.social-media-export |
| `calendar.invitation-rsvp` | DROP·format | slice 14's format-as-schema bug: calendar, mail, chat, call and contact material are P5 SOURCE_TYPES and extractors, never domains (CONNECTION.md's .ics fixture). Covered by file_kind_owner assignments and, for exports, photos.messenger-export / photos.social-media-export |
| `calendar.availability` | DROP·format | slice 14's format-as-schema bug: calendar, mail, chat, call and contact material are P5 SOURCE_TYPES and extractors, never domains (CONNECTION.md's .ics fixture). Covered by file_kind_owner assignments and, for exports, photos.messenger-export / photos.social-media-export |
| `calendar.deadline-reminder` | DROP·format | slice 14's format-as-schema bug: calendar, mail, chat, call and contact material are P5 SOURCE_TYPES and extractors, never domains (CONNECTION.md's .ics fixture). Covered by file_kind_owner assignments and, for exports, photos.messenger-export / photos.social-media-export |
| `calendar.schedule-change` | DROP·format | slice 14's format-as-schema bug: calendar, mail, chat, call and contact material are P5 SOURCE_TYPES and extractors, never domains (CONNECTION.md's .ics fixture). Covered by file_kind_owner assignments and, for exports, photos.messenger-export / photos.social-media-export |
| `comms.email-thread` | DROP·format | slice 14's format-as-schema bug: calendar, mail, chat, call and contact material are P5 SOURCE_TYPES and extractors, never domains (CONNECTION.md's .ics fixture). Covered by file_kind_owner assignments and, for exports, photos.messenger-export / photos.social-media-export |
| `comms.chat-export` | DROP·format | slice 14's format-as-schema bug: calendar, mail, chat, call and contact material are P5 SOURCE_TYPES and extractors, never domains (CONNECTION.md's .ics fixture). Covered by file_kind_owner assignments and, for exports, photos.messenger-export / photos.social-media-export |
| `comms.call-and-voicemail` | DROP·format | slice 14's format-as-schema bug: calendar, mail, chat, call and contact material are P5 SOURCE_TYPES and extractors, never domains (CONNECTION.md's .ics fixture). Covered by file_kind_owner assignments and, for exports, photos.messenger-export / photos.social-media-export |
| `comms.notification-alert` | DROP·format | slice 14's format-as-schema bug: calendar, mail, chat, call and contact material are P5 SOURCE_TYPES and extractors, never domains (CONNECTION.md's .ics fixture). Covered by file_kind_owner assignments and, for exports, photos.messenger-export / photos.social-media-export |
| `comms.mailing-list-newsletter` | DROP·format | slice 14's format-as-schema bug: calendar, mail, chat, call and contact material are P5 SOURCE_TYPES and extractors, never domains (CONNECTION.md's .ics fixture). Covered by file_kind_owner assignments and, for exports, photos.messenger-export / photos.social-media-export |
| `comms.contact-record` | DROP·format | slice 14's format-as-schema bug: calendar, mail, chat, call and contact material are P5 SOURCE_TYPES and extractors, never domains (CONNECTION.md's .ics fixture). Covered by file_kind_owner assignments and, for exports, photos.messenger-export / photos.social-media-export |
| `comms.mailbox-archive` | DROP·format | slice 14's format-as-schema bug: calendar, mail, chat, call and contact material are P5 SOURCE_TYPES and extractors, never domains (CONNECTION.md's .ics fixture). Covered by file_kind_owner assignments and, for exports, photos.messenger-export / photos.social-media-export |
