# Template reuse inventory — what the landed domain rows actually justify

Date: 2026-08-27
Status: **authoring research.** Not a publication. Writes nothing into `planning/domains/`, creates no
`planning/templates/`, `tools/`, or `src/` artefact, opens none of G-DOMAINS / G-P10 / G-SELECTION.
Governing contract: [`domains/TEMPLATE-BUILDING-HANDOFF.md`](domains/TEMPLATE-BUILDING-HANDOFF.md) steps 1–3.
Consumer: Task 2 of [`docs/superpowers/plans/2026-08-26-composable-template-library.md`](../docs/superpowers/plans/2026-08-26-composable-template-library.md).
Authority: `planning/00-database-agent-product-design.md` ("00") wins on conflict; `01-product-design-structured.md` is its section-numbered restatement.

**Evidence snapshot frozen 2026-08-27T04:44:12Z** (`planning/domains/nodes/` is being written live by
another session; every count below is as of that instant and the frozen copy is what this document was
computed from). Every quoted row value was read out of its `.json` by `python3`/`jq`; nothing here is
quoted from memory.

---

## Executive summary

1. The evidence justifies **3 shared template fragments**, not more. Everything else that looked shared
   is either a schema default template wearing a fragment's clothes, or a wrongly-merged role.
2. It justifies **24 template definitions at launch**, bound by **54 applicability rows** — because only
   54 of 253 kept template rows can legally express a folder dimension today.
3. **Clearest one-definition-serves-many:** `def.subject-work-record` — the `subject_anchor → artifact_kind`
   recipe — binds to **14 rows across 3 schemas** (`academic` 7, `research` 6, `code` 1), e.g.
   `academic.coursework` (`school > term > subject > work_type`), `research.thesis-dissertation`
   (`project > artifact_type > stage`), `code.notebooks-experiments` (`project > artifact_type`).
   Three different fact schemas, one organization recipe, three separate one-schema bindings.
4. **199 of 253 kept template rows carry `dimension_order: []`** — 16 of 23 schemas declare zero fields
   (D1 / `_CONTRACT` rule 10), so their recipes exist only as prose. They cannot be bound yet.
5. The handoff's candidate **`project → stage → artifact kind` is realized by ZERO landed rows.** Where
   both appear, `artifact_kind` precedes `lifecycle_stage` (2/2 rows). 00's own §5.4 Research order is
   contradicted by every row that binds to it — each arguing the departure from 00's other rules.
6. The handoff's candidate **`counterpart → cycle → document kind` is realized by 1 row**
   (`applications.undergraduate-packet`). Its `counterpart` also merges two roles 00 forbids merging.
7. The handoff's candidate **`event → capture time` is realized by 1 row** (`photos.family-archive`),
   which argues the order as an *exception*. The dominant landed shape is its reverse, and every
   attestation is on one schema.
8. **Top rejections:** `issuing_org`≡`addressed_org` (00: *"The system must separate roles that happen to
   contain the same entity type."*); `repository`≡`account_type` (instance vs kind); promoting the
   photos and finance schema defaults to fragments (zero reuse gained).
9. **Hardest blocker:** 3 of 4 §3.15 safety schemas (`finance`, `identity`, `medical`) do not carry
   `is_safety_domain` in their landed JSON; only `legal` does. No privacy floor can be computed until fixed.
10. **Library scale:** 00's 200–300 is right for the *catalogue* (~293 rows projected) and wrong for
    *launch*, which the evidence puts at 54 activatable bindings.

---

## 1. What actually landed

Frozen snapshot, 2026-08-27T04:44:12Z, computed against `planning/domains/roster.json` (358 rows, 23 schemas).

| Bucket | Count | Rule applied |
|---|---:|---|
| Roster rows | 358 | `roster.json` `nodes[]` |
| **Complete** (`.json` **and** `.research.md` present) | **312** | included |
| — schema rows | 23 | included as context, never as applicability sources |
| — template rows | 289 | |
| — — **kept** (`refuse_node: false`) | **253** | **the reuse population** |
| — — refused (`refuse_node: true`) | 36 | excluded, §1.2 |
| JSON-only partials | 3 | **excluded**, §1.1 |
| Not started | 43 | **excluded**, §1.1 |

Within the 253 kept template rows:

| | Count | |
|---|---:|---|
| **Live** — non-empty `template.dimension_order` | **54** | can be bound to a definition today |
| **Prose-only** — `dimension_order: []` | **199** | recipe held as prose; unbindable |

### 1.1 Excluded: rows that did not land (46)

Both buckets are excluded because they carry no argued research memo, per the task's rule and
`26-research-dispatch-state.md` §0's memo clause (*"a row can have JSON and no memo … they would be
skipped forever, carrying unverified, unargued JSON into R1c"*).

**JSON-only partials (3):** `law_practice.estates-administration`, `manufacturing.asset-register`,
`nonprofit.advocacy-campaign`.

**Not started (43):** `creative.commissioned-shoot`; `law_practice.` ×12 (contract-negotiation,
criminal-defence, due-diligence, expert-materials, investigation, legal-research, motions-and-briefs,
orders-and-judgments, regulatory-submission, settlement, trial-preparation); `logistics.` ×4;
`manufacturing.` ×9; `nonprofit.` ×6; `resource_operations.` ×4; `retail_hospitality.` ×9.

> **EVIDENCE — this exclusion cannot change any conclusion in §§2–5.** All 46 owed rows sit on schemas
> that declare zero fields (`law_practice` 12, `manufacturing` 9, `retail_hospitality` 9, `nonprofit` 7,
> `logistics` 4, `resource_operations` 4, `creative` 1). Verified: the set of owed rows whose
> `schema_id` is in {academic, college_applications, research, photos, code, finance} is **empty**.
> The 54-row live evidence base is therefore **closed**: no owed row can ever add a live dimension to it.

### 1.2 Excluded: refused rows (36)

`refuse_node: true` rows are refusals of the node test (CONNECTION.md §2), not templates. By schema:
`creative` 9, `engineering` 5, `construction_property` 5, `law_practice` 5, `clinical_practice` 4,
`business_operations` 2, `code` 2, `government` 2, `research` 1, `nonprofit` 1.

They are excluded from reuse but are **positive evidence for §4's threshold**: a row was refused
precisely when it would only have repeated its schema's own recipe. `code.software-project`'s
`refuse_reason` reads: *"Fails the template half of the node test on all three limbs — detection
signals, recommended dimensions, and privacy rules are the Code schema's own, not a seco…"*. A fragment
extracted from such a row would be a duplicate of a schema default, which is exactly what §4 rejects.

### 1.3 The structural fact that governs everything below

| Schema | declares fields | kept rows | live rows |
|---|---:|---:|---:|
| `finance` | 5 | 18 | **18** |
| `academic` | 5 | 11 | **11** |
| `photos` | 6 | 9 | **9** |
| `research` | 6 | 8 | **8** |
| `college_applications` | 5 | 5 | **5** |
| `code` | 4 | 3 | **3** |
| `career`, `identity`, `medical`, `legal`, `creative`, `engineering`, `manufacturing`, `business_operations`, `hr`, `government`, `nonprofit`, `construction_property`, `retail_hospitality`, `logistics`, `resource_operations`, `clinical_practice`, `law_practice` (17) | **0** | 199 | **0** |

> **EVIDENCE.** 54 = 18+11+9+8+5+3 exactly. Every row with a live dimension is on a field-bearing
> schema; every row on a fieldless schema has `dimension_order: []`. This is `_CONTRACT` rule 8's second
> half enforced (*"a template may only branch on a field the same entry's schema declares"*) meeting
> rule 10 (*"No career, identity, medical or legal field rows … This catalogue is a placeholder that
> writes no field rows"*), extended to the J-IND schemas by PR-6.

`creative.3d-asset`'s `template.why` states it plainly: *"The creative schema declares no field rows, so
no folder dimensions are legal at launch."*

**JUDGMENT.** This is not a gap in the research — it is the research doing its job. But it means the
reuse inventory has two tiers of evidence, and they must never be mixed: **ratified dimensions (54 rows)**
and **prose recommendations (199 rows)**. §§2–5 build only on the first. §6 records what the second would
change.

---

## 2. Normalized semantic roles (handoff step 1)

Roles are organization-layer names. **They are not P6 facts** and never become facts (P10 gate C2:
*"Every resolved dimension maps to a P6 field; template roles never become facts."*). Every role below
was derived by reading the `role` string on the field's own row in
`planning/domains/canonical_fields.json` (37 canonical fields) and grouping fields whose stated role is
the same organizational function. Every role maps back to a field the binding row's **one** `uses_schema`
declares.

### 2.1 Candidate role vocabulary

| Role | Live P6 fields it maps to | Rows | Schemas spanned | Canonical `role` evidence |
|---|---|---:|---|---|
| `artifact_kind` | `work_type`, `artifact_type`, `record_type`, `application_document_type` | **40** | academic, code, college_applications, finance, research | *"what kind of coursework artifact this is"* / *"what kind of artifact this is"* / *"what kind of financial record this is"* / *"what role a document plays inside an application"* |
| `subject_anchor` | `project`, `subject` | **17** | academic, code, research | *"the named project a file belongs to"* / *"the course or study subject the material belongs to"* |
| `issuing_org` | `institution` | 11 | finance | *"the financial or record-issuing institution a record belongs to"* |
| `addressed_org` | `target_university`, `venue` | 8 | college_applications, research | *"the institution an application is addressed TO — never the holder's own"* / *"the journal, conference, or publication venue an artifact targets"* |
| `cycle_period` | `term`, `application_cycle` | 8 | academic, college_applications | *"academic term or cycle the material belongs to"* / *"the admissions cycle an application belongs to"* |
| `holder_institution` | `school`, `lab` | 8 | academic, research | *"the institution the holder attends, attended, or teaches at"* / *"the lab or research group the work belongs to"* |
| `capture_time` | `capture_year` | 8 | photos | *"the year a photo or capture was taken, from capture metadata"* |
| `occasion_anchor` | `event` | 6 | photos | *"the named occasion, trip, or gathering a capture or record belongs to"* |
| `container` | `account_type`, `repository` | 6 | code, finance | see §3.4 — **this role is REJECTED as a merge** |
| `lifecycle_stage` | `stage` | 4 | research | *"where in its workflow a research artifact sits"* |
| `capture_kind` | `media_type` | 3 | photos | *"what kind of capture this is (photo, screenshot, scan, video)"* |
| `scope_period` | `tax_year` | 2 | finance | *"the tax year a financial record belongs to"* |
| `purpose_anchor` | `purpose` | 1 | college_applications | *"what the file was FOR, as opposed to what it is about"* |
| `place` | `location` | 1 | photos | *"where a capture was taken, resolved from GPS or content"* |

All 22 distinct dimension tokens across the 54 live rows map to exactly one role. No token is unmapped.

### 2.2 Three role distinctions that must not be collapsed

**(a) `holder_institution` ≠ `addressed_org` ≠ `issuing_org`.** 00: *"The system must separate roles that
happen to contain the same entity type."* This is not theoretical here — it is the most-authored
`role_split` in the corpus. Across the 54 live rows: `target_university ↔ school` appears 11 times,
`institution ↔ school` twice, `institution ↔ client` twice, `venue ↔ school` once, `lab ↔ institution`
once, `institution ↔ our_firm` once.

`finance.insurance-corporate` states the consequence in both directions:

> *"a certificate of insurance carries three organization roles on one page and the canonical list has
> keys for only two of them: the carrier is the finance issuer (institution) and the certificate holder
> is the engagement's counterparty (client) … the consequence here is strict in both directions — a
> certificate holder must never fill institution, and a carrier must never fill client."*

`research.grants-funding`: *"Same entity type, different role: the organization that PERFORMS the funded
work versus the organization that FUNDS it."*

**(b) `subject_anchor` ≠ `occasion_anchor`.** A project or course is an ongoing named work; an event is a
bounded occurrence. They order differently against time — see §3.3.

**(c) Three privacy classes, not one.** `sensitivity` alone is nearly constant (250 of 253 kept rows are
`potentially_sensitive`), so it is useless as a discriminator. The **`sensitivity_why` direction of
exposure** is not:

| Privacy class | Evidence | Rows |
|---|---|---|
| holder's own record | `academic.coursework`: *"this situation holds the holder's own record and should not accumulate other people's"* | most |
| third-party subject | `academic.recommendation-letters-written`: *"Every substantive file here is about someone who is not the holder, and most are evaluative and often confidential"*; `academic.teaching`: *"This situation routinely holds other people's data"*; `photos.family-archive`: *"People are the subject matter of this situation rather than an incidental field"* | ≥4 live |
| not holder-personal | `research.reading-library` (`sensitivity: "none"`): *"the one part of the Research domain whose material carries no holder-personal content"* | 1 live (3 kept) |

**JUDGMENT.** Direction-of-exposure is the privacy discriminator a fragment must carry, not the
`sensitivity` enum. Two rows can share a role sequence and still need separate definitions because one
holds the holder's record and the other holds third parties'.

---

## 3. Reuse candidates (handoff step 2)

Method: normalize each live row's `dimension_order` to a role sequence, then compare **relative order,
adjacency, optionality, and privacy class** — never labels. 54 rows collapse to **31 distinct role
sequences**.

### 3.0 Relative-order stability across all 54 rows

| Role pair | Direction | n | Schemas | Verdict |
|---|---|---:|---|---|
| `subject_anchor` → `artifact_kind` | one direction only | **14** | academic, code, research | **STABLE** |
| `cycle_period` → `artifact_kind` | one direction only | 7 | academic, college_applications | **STABLE** |
| `holder_institution` → `artifact_kind` | one direction only | 7 | academic, research | **STABLE** |
| `holder_institution` → `subject_anchor` | one direction only | 5 | academic, research | **STABLE** |
| `subject_anchor` → `lifecycle_stage` | one direction only | 4 | research | STABLE (1 schema) |
| `holder_institution` → `cycle_period` | one direction only | 3 | academic | STABLE (1 schema) |
| `artifact_kind` → `lifecycle_stage` | one direction only | 2 | research | STABLE (1 schema) |
| `issuing_org` → `artifact_kind` | 11 for / 1 against | 12 | finance | contested |
| `container` → `artifact_kind` | 5 for / 1 against | 6 | code, finance | contested |
| `capture_time` → `occasion_anchor` | 4 for / 1 against | 5 | photos | contested |
| `capture_kind` → `capture_time` | 2 for / 1 against | 3 | photos | contested |
| `addressed_org` ↔ `cycle_period` | 1 / 1 | 2 | college_applications | **UNRESOLVED** |
| `subject_anchor` ↔ `addressed_org` | 1 / 1 | 2 | research | **UNRESOLVED** |

### 3.1 Candidate A — `project → stage → artifact kind`

Handoff proposal: *"project → stage → artifact kind across research, software, client, and creative work."*
00 §5.4: *"a Research template may define project → stage → artifact type."*

> **EVIDENCE: not one landed row realizes it.** Rows whose `dimension_order` begins
> `["project","stage","artifact_type"]`: **[] (empty).** Rows whose role sequence begins
> `subject_anchor > lifecycle_stage > artifact_kind`: **[] (empty).**

Every row that binds to the `research` schema departs from that schema's own recorded default
(`research.json` `template.dimension_order` = `["project","stage","artifact_type"]`):

| Row | Live order | Departure, in the row's own words |
|---|---|---|
| `research.dataset-analysis` | `project > artifact_type > stage` | *"artifact_type rises above stage. Data work's primary axis is lineage — raw, cleaned, codebook, analysis, results — and one dataset keeps all of those forms while its stage moves"* |
| `research.thesis-dissertation` | `project > artifact_type > stage` | *"THE CHANGE THIS ROW MAKES to the schema default (project → stage → artifact_type) is to lift artifact_type above stage"* |
| `research.reading-library` | `project > artifact_type` | *"STAGE IS STRUCK from the schema default … a published paper by somebody else occupies none of it"* |
| `research.lab-notebook-protocols` | `lab > project > artifact_type` | *"stage DROPPED from the order. A standing procedure has no workflow position"* |
| `research.ethics-compliance` | `project > artifact_type` | *"stage is a legal fact and is del[iberately not a level]"* |
| `research.conference-presentation` | `venue > project > artifact_type` | *"stage is deliberately NOT a dimension here: inside an accepted meeting bundle it carries one value for nearly every member"* |
| `research.grants-funding` | `project > stage` | *"artifact_type is deliberately NOT a folder level in this recommendation — it is metadata-only"* |
| `research.manuscript-publication` | `project > venue > stage` | *"venue is the level this template adds and the schema's default order deliberately leaves out"* |
| `code.notebooks-experiments` | `project > artifact_type` | *"the level the default leans on is absent BY DEFINITION of this situation"* |
| `code.pkm-vault` | `project` | *"One dimension, deliberately"* |
| `code.dotfiles-environment` | `repository > artifact_type` | *"project is deliberately absent, and its absence is the whole difference from the Code schema's default order"* |

**VERDICT: the candidate is REFUTED as stated, and a narrower shape is SUPPORTED.**

- What survives: `subject_anchor → artifact_kind`, **14 rows, 3 schemas**, order stable 14/14 with zero
  counter-attestations, and adjacent in all 14.
- What does not: `lifecycle_stage` appears in only **4 rows, all on `research`**, and when it co-occurs
  with `artifact_kind` it is **below** it (2/2), never above. `lifecycle_stage` therefore fails the
  cross-context test and must be a **definition-local optional role**, not part of a shared fragment.
- Where it breaks by design: `code.dotfiles-environment` has no `subject_anchor` at all;
  `research.grants-funding` has no `artifact_kind`.

**Software and creative work — the parts of the candidate that cannot be tested.** `code` contributes one
supporting row. `creative` contributes **none**: all 31 kept `creative` rows are prose-only.
`creative.client-engagement`'s prose is the closest thing to a fourth context and it is *stronger* than
the landed evidence, naming *"client corpus, then project, then stage, then artifact_type"*.
`creative.film-production`: *"If creative fields are ratified later, the natural recommendation would be
project → stage → artifact_type."*

> **JUDGMENT.** The creative prose supports the handoff's original shape — stage above artifact — and the
> landed evidence contradicts it. That is an unresolved disagreement, not a tie to be split. The fragment
> must ship without `lifecycle_stage`, and the question reopens when the creative schema lands (§6).

### 3.2 Candidate B — `counterpart → cycle → document kind`

Handoff proposal: *"counterpart → cycle → document kind across applications, recruiting, procurement, and claims."*
00 §5.4 names two instances: *"an Applications template may define target institution → application
cycle → document type"* and *"a Career template may define company → role or recruiting cycle → document type."*

> **EVIDENCE: realized by exactly ONE landed row.** `applications.undergraduate-packet`,
> `target_university > application_cycle > application_document_type`, whose `why` cites 00 verbatim for it.

Everything else on the candidate diverges:

| Row | Live order | Why it diverges |
|---|---|---|
| `applications.graduate-professional` | `target_university > application_document_type` | cycle dropped |
| `applications.k12-admission` | `target_university > application_document_type` | *"A K-12 admission season is normally ONE entry year across SEVERAL schools, so a cycle level beneath each school produces exactly one child"* |
| `applications.scholarship-fellowship` | `application_cycle > application_document_type > target_university` | **counterpart moved to the leaf**: *"one applicant addresses many sponsors in one season, most of them receiving one essay and one form"* |
| `applications.purpose-packet` | `purpose` | no counterpart at all: *"this packet frequently has no single addressee"* |
| `finance.payroll-received` | `institution > tax_year > record_type` | matches the *shape* with different fields |
| 10 × `finance.*` | `institution > record_type` | no cycle level |
| `finance.tax-filings` | `tax_year > record_type` | period first, counterpart absent |
| `finance.small-business-bookkeeping` | `record_type > account_type` | **inverted**: *"FUNCTION FIRST … a general ledger, invoice register, expense report or receivables report refers to many banks and counterparties"* |
| `travel.bookings-confirmations` | `record_type > institution` | **inverted** |

**VERDICT: REFUTED twice over.**

**(i) The cycle level is not stable.** `cycle_period` co-occurs with an org role in 2 rows and they
disagree: `applications.undergraduate-packet` puts counterpart first, `applications.scholarship-fellowship`
puts cycle first. One-for-one is not evidence of an order; it is evidence there isn't one.

**(ii) `counterpart` is a wrongly-merged role.** Treating `institution`, `target_university` and `venue`
as one role produces an attractive statistic — `counterparty > artifact_kind`, 10 rows, 2 schemas — that
dissolves the moment 00's role-separation rule is applied. Split correctly:

| Split role | Sequence | Rows | Schemas |
|---|---|---:|---|
| `issuing_org` (record comes **from** it) | `issuing_org > artifact_kind` | 8 | **finance only** |
| `addressed_org` (holder's material goes **to** it) | `addressed_org > artifact_kind` | 2 | **college_applications only** |

Both halves become single-schema. **The cross-domain claim was entirely an artefact of the merge.**

**Recruiting, procurement, claims — untestable.** `career` has 6 kept rows, all prose-only, because
`career` declares zero fields. `career.json`'s own `template.why`:

> *"EMPTY BY CONTRACT, not by refusal. 00 records the recommendation verbatim — 'a Career template may
> define company → role or recruiting cycle → document type' — but a dimension may only branch on a field
> the schema declares, and this placeholder declares none."*

So **the design's own named instance of this candidate is unbuildable at launch.** Procurement
(`business_operations.vendor-management`, `retail_hospitality.supplier-order`) and claims
(`finance.insurance-*` aside) are prose-only or owed.

### 3.3 Candidate C — `event → capture time`

Handoff proposal: *"event → capture time across photos, media production, travel, and field work."*
00 §5.4: *"a Photos template may define year → event"* — i.e. 00 states the **reverse**.

> **EVIDENCE: realized by ONE landed row, which argues it as an exception.**

| Row | Live order | `time_first` |
|---|---|---|
| `photos.camera-events` | `capture_year > event` | true |
| `photos.home-video` | `capture_year > event` | true |
| `photos.drone-captures` | `capture_year > event` | true |
| `photos.social-media-export` | `capture_year > event > media_type` | true |
| **`photos.family-archive`** | **`event > capture_year`** | **false** |
| `photos.messenger-export` | `capture_year` | true |
| `photos.scanned-documents` | `media_type > capture_year` | false |
| `photos.screenshot-captures` | `media_type > capture_year` | false |
| `travel.trip-photos` | `event > location` | false |

`photos.family-archive` states why it is the exception:

> *"In this situation the capture date is precisely the thing that is not recoverable — the only
> machine-readable timestamp belongs to the scanner or the phone that re-photographed the print, so a
> capture_year level at the top would collect prints under the year somebody digitized them."*

**VERDICT: REFUTED as a cross-domain fragment; the reverse is supported as a within-family recipe.**

- Direction: 4 rows for `capture_time → occasion_anchor`, 1 against. The proposed direction is the
  minority reading and its single instance is explicitly evidence-forced.
- **Scope: every one of the 9 rows is on `schema_id: "photos"`, including `travel.trip-photos`.** There is
  no second schema. Media production (`creative.shoot-day-media`), travel and field work
  (`manufacturing.field-service-report`, `resource_operations.*`) are prose-only or owed.
- `travel.trip-photos` — the closest thing to a second domain — has no capture-time level at all
  (`event > location`), and explains why: *"a trip value in this product's own vocabulary carries its own
  year ('Japan Trip 2025'), so a year level above it is the case 00 tells the canvas to warn about."*

### 3.4 Two further merges tested and rejected

**`container` = `repository` + `account_type` — REJECTED.** The statistic looks good
(`container > artifact_kind`, 5 rows, 2 schemas: `code.dotfiles-environment`, `finance.personal-records`,
`finance.investment-brokerage`, `finance.loans-mortgage`, `finance.insurance-corporate`). But the roles
are different in kind: `repository` is *"the source repository a code file belongs to"* — a named
instance; `account_type` is *"the **kind** of account a financial record belongs to"* — a category. A
categorical level and an instance level have different one-child hazards and different value
vocabularies. Merging them would let a compiler bind a code binding's instance role to a finance
binding's category field. **Two honest duplicates.**

**`artifact_kind` across five fields — ACCEPTED, and it is the one merge that survives scrutiny.**
`work_type`, `artifact_type`, `record_type` and `application_document_type` all answer *"what kind of
document is this"* on their canonical rows, all are `destination_eligible: true`, all sit at or near the
leaf, and no row orders any of them above a `subject_anchor`, `holder_institution` or `cycle_period`
(7/7, 7/7 and 14/14 stable). `media_type` is held **separate** as `capture_kind` because its canonical
role is *"what kind of **capture** this is"* and it behaves differently — it *leads* in 2 rows
(`photos.scanned-documents`, `photos.screenshot-captures`), which no `artifact_kind` field ever does.

---

## 4. Proposed fragment set (handoff step 3)

Threshold applied verbatim: *"Create a fragment only when at least two reviewed contexts share stable
semantics and compatible constraints."*

**Additional threshold applied, and stated so it can be overruled:** a candidate is *not* a fragment when
its only contexts are rows of one schema whose sequence already equals that schema's own recorded default
template. Such a "fragment" buys an indirection and zero reuse — and §1.2's 36 refusals refused exactly
that reasoning at the row level. **JUDGMENT, not evidence.** It is what cuts the count from 5 to 3.

### 4.1 Accepted — 3 fragments, ranked by evidence strength

#### `frag.subject-then-artifact@1.0.0` — RANK 1

| | |
|---|---|
| Roles | `subject_anchor` (required) → `artifact_kind` (required), adjacent |
| Order constraint | `subject_anchor` strictly precedes `artifact_kind`. **14/14, zero counter-attestations.** |
| Contexts | **3 schemas, 14 rows** — `academic` 7, `research` 6, `code` 1 |
| Privacy floor | none above baseline; direction-of-exposure set per binding (§4.3) |
| Shared rationale | every context argues from the same 00 sentence: *"a parent dimension should provide the context required to understand the child"* |

Binding rows: `academic.coursework`, `academic.continuing-education`, `academic.online-course`,
`academic.study-abroad`, `academic.standardized-testing`, `academic.teaching`, `academic.homeschool`,
`research.ethics-compliance`, `research.reading-library`, `research.dataset-analysis`,
`research.thesis-dissertation`, `research.lab-notebook-protocols`, `research.conference-presentation`,
`code.notebooks-experiments`.

Role→field per schema (each binding names one schema; no field crosses):
`academic` → `subject`,`work_type` · `research` → `project`,`artifact_type` · `code` → `project`,`artifact_type`.

#### `frag.holder-affiliation-prefix@1.0.0` — RANK 2

| | |
|---|---|
| Roles | `holder_institution` (optional) preceding `subject_anchor` |
| Order constraint | `holder_institution` precedes `subject_anchor` **5/5**; precedes `artifact_kind` **7/7** |
| Contexts | **2 schemas, 4 adjacent rows** — `academic.continuing-education`, `academic.online-course`, `academic.study-abroad`, `research.lab-notebook-protocols` |
| Why optional | `academic.continuing-education`: *"school comes first because the provider is what makes a prose course title intelligible and disambiguable"*; `research.lab-notebook-protocols`: *"lab BEFORE project, because bench material's stable owner is the lab and its project association is often absent or plural"* |
| Hard constraint it must carry | `holder_institution` may **never** bind to `target_university`, `venue` or `institution`. 11 `target_university ↔ school` role_splits enforce it. |

Role→field: `academic` → `school` · `research` → `lab`.

#### `frag.cycle-then-artifact@1.0.0` — RANK 3

| | |
|---|---|
| Roles | `cycle_period` (optional) → `artifact_kind` |
| Order constraint | `cycle_period` precedes `artifact_kind` **7/7** |
| Contexts | **2 schemas, 4 adjacent rows** — `academic.k12-schooling`, `academic.recommendation-letters-written`, `applications.undergraduate-packet`, `applications.scholarship-fellowship` |
| Known instability it must NOT assert | position relative to an org role is **unresolved** (1 v 1, §3.0). The fragment fixes `cycle_period < artifact_kind` and asserts nothing else. |
| Drop rationale to carry | `applications.k12-admission`: *"a cycle level beneath each school produces exactly one child, which is what 00 tells the canvas to warn about"* |

Role→field: `academic` → `term` · `college_applications` → `application_cycle`.

### 4.2 Rejected near-misses — the list that matters more than the accepted one

| # | Near-miss | Statistic that tempted | Why REJECTED |
|---|---|---|---|
| **R1** | `counterparty → artifact_kind` merging issuer and addressee | 10 rows, 2 schemas | 00: *"The system must separate roles that happen to contain the same entity type."* Split correctly it is 8 finance + 2 applications rows — **both single-schema**. `finance.insurance-corporate`: *"a certificate holder must never fill institution, and a carrier must never fill client."* |
| **R2** | `container → artifact_kind` merging `repository` and `account_type` | 5 rows, 2 schemas | Instance vs category. `repository` = *"the source repository a code file belongs to"*; `account_type` = *"the **kind** of account"*. Different one-child hazards, different value vocabularies. §3.4. |
| **R3** | `frag.capture-time-then-occasion` | 4 rows, one direction dominant | **All 9 contexts are one schema (`photos`)** and the sequence is verbatim `photos.json`'s own default (`["capture_year","event"]`, `time_first: true`). Zero reuse gained; it is the schema default and should stay a definition. |
| **R4** | `frag.issuer-then-record` | 11 rows — the largest single cluster | Same defect as R3: `finance` only, and `institution > (account_type) > record_type` is verbatim `finance.json`'s default. It is the finance schema's template, not a shared fragment. |
| **R5** | `project → stage → artifact kind` (handoff's own candidate) | 00 §5.4 states it | **Zero landed rows realize it.** Where both appear, `artifact_kind` precedes `lifecycle_stage` 2/2. §3.1. |
| **R6** | `counterpart → cycle → document kind` (handoff's own candidate) | 00 §5.4 states it twice | One landed row. Its counterpart role is R1's bad merge; its cycle position is contested 1-for-1. §3.2. |
| **R7** | `event → capture time` (handoff's own candidate) | — | One landed row, which argues it as an exception; 00 states the reverse; single schema. §3.3. |
| **R8** | Folding `academic.teaching` into `frag.subject-then-artifact`'s definition | identical role sequence to `academic.homeschool` | **Privacy**, not shape. `academic.teaching`: *"This situation routinely holds other people's data."* `academic.coursework`: *"this situation holds the holder's own record and should not accumulate other people's — a roster column or a scores table is … a routing signal away from this template."* Same recipe, opposite exposure direction. Two definitions, one fragment. |
| **R9** | Folding `media_type` into `artifact_kind` | both are "what kind of thing" | `media_type` **leads** in 2 rows; no `artifact_kind` field ever leads a sequence containing a subject/institution/cycle role. §3.4. |
| **R10** | A fragment for `lifecycle_stage` | 00 names it in the Research template | `research` only, 4 rows, and its position is unstable (leaf in 4/4 but with two different predecessors). Definition-local optional role. |

> **R8 is the template for how this inventory reads the handoff's warning.** *"Different meanings, privacy
> rules, or ordering requirements keep the definitions separate."* R8 keeps the **definitions** separate
> while still sharing the **fragment** — which is the entire reason the four-record decomposition exists.

### 4.3 Where the privacy floor belongs — a decision this inventory cannot make alone

C7 requires *"The combined sensitivity policy is no weaker than any included fragment or P7 restriction."*
`frag.subject-then-artifact` spans `research.reading-library` (`sensitivity: "none"`) and
`academic.teaching` (third-party data). If the fragment carries the strictest floor, the reading-library
binding is over-restricted; if the weakest, the teaching binding is under-restricted.

**JUDGMENT (needs ratification, §6):** fragments carry **no** privacy floor above baseline. Safety status
is a **schema** property (`is_safety_domain`, `_CONTRACT` rule 15) enforced by P6/P7 before P10 sees the
branch, and PR-2 already says no deep template unlocks from safety activation. Direction-of-exposure lives
on the **applicability row**, which is per-schema and per-context. This keeps C7 satisfiable without a
fragment ever weakening a safety domain. It is a contract decision for plan Task 1/Task 3, not mine.

---

## 5. The many-to-many matrix

### 5.1 One definition → several domains

**Proposed launch definition set: 24 definitions over the 54 live rows** (one per role-sequence family
that survives §2.2(c)'s privacy split; sub-sequences that drop a level *and preserve relative order* are
depth variants of one definition, per handoff step 4: *"Definitions carry recommended order, not
mandatory depth"*).

| Definition | Composed from | Schemas bound | Applicability rows |
|---|---|---|---:|
| **`def.subject-work-record`** | `frag.holder-affiliation-prefix?` + `frag.cycle-then-artifact?` + **`frag.subject-then-artifact`** | **`academic`, `research`, `code`** | **10** |
| `def.teaching-delivery` | `frag.cycle-then-artifact?` + `frag.subject-then-artifact` | `academic` | 1 |
| `def.evaluative-third-party-letters` | `frag.cycle-then-artifact` | `academic` | 1 |
| `def.institution-record-by-period` | `frag.holder-affiliation-prefix` + `frag.cycle-then-artifact?` | `academic` | 3 |
| `def.research-lineage` | `frag.subject-then-artifact` + local `lifecycle_stage` | `research` | 2 |
| `def.research-workflow-split` | local `subject_anchor` + `lifecycle_stage` | `research` | 1 |
| `def.submission-to-venue` | local `subject_anchor`, `addressed_org`, `lifecycle_stage` | `research` | 1 |
| `def.venue-bundle` | local `addressed_org` + `frag.subject-then-artifact` | `research` | 1 |
| `def.preserved-root` | local `subject_anchor` | `code` | 1 |
| `def.container-artifact` | local `container` + `artifact_kind` | `code` | 1 |
| `def.addressee-packet` | local `addressed_org` + `frag.cycle-then-artifact?` | `college_applications` | 3 |
| `def.cycle-led-many-sponsors` | `frag.cycle-then-artifact` + trailing local `addressed_org` | `college_applications` | 1 |
| `def.purpose-packet` | local `purpose_anchor` | `college_applications` | 1 |
| `def.issuer-record` | local `issuing_org` + `container?` + `artifact_kind` | `finance` | 11 |
| `def.issuer-period-record` | local `issuing_org`, `scope_period`, `artifact_kind` | `finance` | 1 |
| `def.period-scoped-filing` | local `scope_period` + `artifact_kind` | `finance` | 1 |
| `def.loan-kind-record` | local `container` + `artifact_kind` | `finance` | 1 |
| `def.function-first-book` | local `artifact_kind` + `container?` | `finance` | 1 |
| `def.group-scoped-record` | local `artifact_kind` | `finance` | 2 |
| `def.function-then-issuer` | local `artifact_kind` + `issuing_org?` | `finance` | 1 |
| `def.capture-time-events` | local `capture_time` + `occasion_anchor?` + `capture_kind?` | `photos` | 5 |
| `def.occasion-led-archive` | local `occasion_anchor` + `capture_time` | `photos` | 1 |
| `def.capture-kind-led` | local `capture_kind` + `capture_time` | `photos` | 2 |
| `def.occasion-place` | local `occasion_anchor` + `place` | `photos` | 1 |
| | | | **54** |

**The headline, concretely.** `def.subject-work-record` is one versioned definition. It reaches three fact
schemas through **ten separate one-schema applicability rows**:

```
                          def.subject-work-record@1.0.0
                                     |
                  +------------------+------------------+
                  |                  |                  |
     TemplateApplicability  TemplateApplicability  TemplateApplicability
       uses_schema:academic   uses_schema:research   uses_schema:code
       subject_anchor→subject subject_anchor→project subject_anchor→project
       artifact_kind→work_type artifact_kind→artifact_type artifact_kind→artifact_type
       holder_institution→school holder_institution→lab   (prefix omitted)
       cycle_period→term        (cycle omitted)
       rows (6):                rows (3):                rows (1):
         coursework                 ethics-compliance        notebooks-experiments
         continuing-education       reading-library
         online-course              lab-notebook-protocols
         study-abroad
         standardized-testing
         homeschool
```
Four further rows import the **same fragment version** through *other* definitions:
`academic.teaching` (`def.teaching-delivery`), `research.dataset-analysis` and
`research.thesis-dissertation` (`def.research-lineage`), `research.conference-presentation`
(`def.venue-bundle`) — which is why the fragment has 14 binding rows (§4.1) while this definition
has 10 applicability rows.

**The fact-authority boundary is never crossed.** `academic`'s binding may only resolve
`subject`/`work_type`/`school`/`term`; `research`'s may only resolve `project`/`artifact_type`/`lab`. The
fragment carries roles and order — no field names, no values. Compare `academic.coursework`'s live order
`school > term > subject > work_type` with `research.lab-notebook-protocols`' `lab > project >
artifact_type`: same role sequence, disjoint field sets, two schemas, zero union.

### 5.2 One domain → several definitions

| Schema | Definitions it needs | Why more than one |
|---|---:|---|
| `finance` | **7** | `finance.small-business-bookkeeping` inverts to `record_type > account_type` (*"FUNCTION FIRST … a general ledger … refers to many banks and counterparties"*); `finance.tax-filings` is time-first (`time_first: true`, *"the filing IS the year"*); `finance.household-property`/`vehicle-records` are single-level inside an accepted group. One schema, four incompatible order constraints. |
| `photos` | **4** | `capture_time`-led (4 rows) vs `occasion_anchor`-led (`family-archive`) vs `capture_kind`-led (2 rows) vs `occasion→place` (`trip-photos`). All on `schema_id: photos`. |
| `academic` | **4** | Shape would allow 2; **privacy forces 4** (R8): holder's own record, teaching (third-party), evaluative letters (third-party), institution-issued records. |
| `research` | **5** | `lifecycle_stage` present / absent / leaf-only, plus a venue-led bundle (`conference-presentation`) and a venue-in-the-middle submission chain (`manuscript-publication`) whose order conflicts (B7). |
| `college_applications` | **3** | addressee-led, cycle-led, purpose-led — 00 itself: *"the product should not assume that all applications are best organized in the same way."* |
| `code` | **3** | `project` + `artifact_kind`; `project` alone (`pkm-vault`: *"One dimension, deliberately"*); `repository`-anchored (`dotfiles-environment`: *"project is deliberately absent"*). |

### 5.3 A mixed-domain purpose packet, from the design's own example

00: *"An academic abstract submitted as part of a university application can retain project = PVA/RDP and
document type = abstract while also carrying purpose = university application and target university =
UChicago."* The `research` schema row records the reciprocal edge as `also_holds_with:
college_applications`, provenance `design`, with fixture `Abstract_PVA-RDP_UChicago.pdf`.

Composed as this inventory proposes:

- `def.subject-work-record` via the **research** binding → `project`, `artifact_type`
- `def.purpose-packet` via the **college_applications** binding → `purpose`

Two definitions, two one-schema bindings, one branch. The `research` binding may not resolve `purpose` or
`target_university`; the `college_applications` binding may not resolve `project`. **The packet composes
the bindings; it does not union the schemas.** `applications.purpose-packet` states the member-loss rule
the composition must respect: *"A transcript may be part of several application packets"* and *"If no
shared branch exists, the system should not arbitrarily choose one university. It should abstain or ask
the user to choose a primary home."*

Landed `also_holds_with` edges available as further mixed-domain seams: `academic ↔ {college_applications,
research, photos, career}`, `research ↔ {college_applications, academic, code, medical}`,
`code ↔ {research, career, identity}`, `finance ↔ {medical, academic, legal, identity, photos}`,
`photos ↔ {research}`, `college_applications ↔ {research, academic, identity}`.

---

## 6. Blockers — what this inventory cannot decide

### B1. 199 of 253 kept rows have no live field to bind (BLOCKING, R1c)

16 of 23 schemas declare `fields: []`. Their recipes exist only as `template.why` prose. **This is not a
configuration gap to be patched by inventing fields** — `_CONTRACT` rule 8: *"Do not invent fields to make
the gate green"*; rule 10 places the career/identity/medical/legal deferral with S3 and D1.
**Decider: R1c / Joseph.** Until then these rows produce no applicability rows.

### B2. R1c open field proposals (BLOCKING for named families)

Aggregated from `proposed_fields` across all 312 landed rows — 74 distinct proposed keys. The ones the
task names, with their real counts and reach:

| Proposed key | Proposals | Schemas proposing it | Would unblock |
|---|---:|---|---|
| `organization` | **14** | business_operations, construction_property, nonprofit | the largest single unblock; would give ~53 prose rows an org-anchor role |
| `fiscal_period` | **12** | business_operations, law_practice, nonprofit | would create a second `cycle_period`/`scope_period` context outside academic/finance |
| `subject_of_record` | 4 | clinical_practice, law_practice, nonprofit | the *third-party subject* privacy class as a **field**; would let §2.2(c) be checked mechanically |
| `property` | 5 | construction_property, finance | `finance.household-property`: *"The intended useful order, if R1c accepts the proposed key, is property then record_type"* |
| `instruction` | 3 | construction_property | `construction_property.construction-project`'s prose spine |
| `revision` | **0 as a proposed field** | — | **CORRECTION to the brief:** `revision` is not in any row's `proposed_fields`. It appears as prose (`construction_property.drawings-revisions`, 29 mentions) and is **explicitly refused as a level** by `engineering.drawing-package`: *"The revision designator is REFUSED as a level outright."* |

Also material and not on the brief's list: `asset` (6, four schemas), `site` (6, four schemas),
`record_type` proposed *again* by four J-IND schemas that cannot reference finance's copy, `project` (4,
three schemas), `client` (2), `people_cycle` (4, hr).

**Decider: R1c merge gate (not started per `26-research-dispatch-state.md` §0a).**

### B3. Career is the design's own instance of Candidate B and is empty (BLOCKING for §3.2)

`_CONTRACT` rule 10: *"**Career is owed before P10**, where a destination dimension first needs one.
Adding one earlier is reversing S3 and must say so explicitly rather than arriving as a plan edit."*
Until career lands, `counterpart → cycle → document kind` has one landed attestation and cannot be
promoted. **Decider: Joseph, explicitly, per rule 10.**

### B4. Three of four safety schemas do not carry `is_safety_domain` (BLOCKING for §4.3)

> **EVIDENCE.** `planning/domains/nodes/finance.json` → key **ABSENT**; `identity.json` → **ABSENT**;
> `medical.json` → **ABSENT**; `legal.json` → `true`. Only `legal.json` and 25 non-safety rows carry the key.

00 §3.15: *"Finance, identity, medical, and legal material should be implemented first as safety domains."*
`finance.json`'s `sensitivity_why` asserts the status in prose — *"Consequences carried by the safety flag,
not invented here"* — but the flag it names is not set. A compiler computing a privacy floor from landed
JSON would read finance as an ordinary domain. **Decider: R1c / the domain gate. Not fixable from here —
`planning/domains/` is another session's write territory.**

### B5. The 46 owed rows (NON-BLOCKING for §§2–5, blocking for scale)

They cannot change any conclusion in §§2–5 (§1.1's proof). They change §7's arithmetic and they are the
only remaining source of evidence for three of the handoff's four untested contexts:
`manufacturing.field-service-report` and `resource_operations.*` (field work, Candidate C),
`retail_hospitality.supplier-order` (procurement, Candidate B), `law_practice.*` ×12 (claims/matters).
**Decider: the active research swarm.** Redispatch state and per-family owed counts are in
`planning/26-research-dispatch-state.md` (note: its header figure of "147 of 358 landed" is stale —
312 are complete as of this snapshot).

### B6. Roles with no live P6 field — configuration gaps, never inventions

Every role in §2.1 maps to at least one live field, so **there are no orphan roles in the accepted
fragment set**. Three roles are one-field, one-schema and would become gaps the moment a second context
appears: `purpose_anchor` (`purpose` only, and `applications.purpose-packet`'s own `open_question` asks
*"whether purpose stays Applications-scoped (NJ-3 / PR-1) … a purpose-coherent packet outside admissions
would have no row to land on"*), `place` (`location`, photos only), `scope_period` (`tax_year`, finance
only). Prose roles with **no** live field anywhere — client/counterparty for creative and law_practice,
site, asset, fiscal period, matter — are B2's list and must stay configuration gaps. Handoff step 5:
*"The compiler must not invent a field or copy a field from another schema."*

### B7. Two unresolved ordering questions inside one schema

`addressed_org` vs `cycle_period` (`applications.undergraduate-packet` vs `applications.scholarship-fellowship`)
and `subject_anchor` vs `addressed_org` (`research.manuscript-publication` vs `research.conference-presentation`)
are each attested 1-for-1 in opposite directions. Both rows argue their order from evidence, so this is
not an error to correct — it is two situations with genuinely different shapes. **No fragment may fix
either pair's order.** Handled by keeping them in separate definitions (§5.1). Recorded here so a later
pass does not "resolve" it by picking one.

### B8. Also observed, outside this inventory's scope

`academic.coursework`'s `open_question`: *"The Academic schema row already carries an inline template block
with this same dimension_order, so two rows now state one recommendation … R1c or Joseph decides which row
owns it."* This matters to §4's threshold: if the schema row's block *is* the default definition, then R3
and R4 are decided by contract rather than by my judgment.

---

## 7. Design fidelity

### 7.1 Against §5.4 — templates as controlled schemas

00 §5.4: a template *"defines the dimensions that are meaningful for one type of material, their
recommended order, which dimensions are optional, which ones are metadata only, and what safety or
usability constraints apply."*

| §5.4 requirement | Where it lives in this proposal | Conformant? |
|---|---|---|
| meaningful dimensions | fragment roles + definition-local roles | yes — every role maps to a `destination_eligible: true` canonical field |
| **recommended** order | fragment relative-order constraints, all evidence-graded in §3.0 | yes — and §3.0 marks four pairs contested and two unresolved rather than asserting an order |
| which are optional | `frag.holder-affiliation-prefix` and `frag.cycle-then-artifact` are optional prefixes; depth variants live in the definition | yes |
| which are metadata only | `research.grants-funding`: *"artifact_type is deliberately NOT a folder level … it is metadata-only"*; `research.lab-notebook-protocols`: *"stage remains a legal fact on this schema and is metadata-only for this situation"* | yes — carried per definition, not per fragment |
| safety constraints | **§4.3, unratified; B4 unresolved** | **NO** |

The §5.7 validator checks are respected by construction: no fragment repeats a role (each role appears
once per sequence); no fragment forces depth (handoff step 4: *"recommended order, not mandatory depth"*);
no fragment uses an org merely as a collector — `frag.holder-affiliation-prefix` is the one that could,
and `finance.small-business-bookkeeping` records the guard: *"using the holder's own operation as the
leading institution would turn authorship-side identity into the collector 00 forbids."*

Three fragments over 22 dimension tokens and 37 canonical fields is well inside "controlled". The risk
§5.4 guards against is a template that becomes an open-ended vocabulary; a 13-role vocabulary of which 3
compose into fragments is not that.

### 7.2 Against §5.7 — the 200–300 library

00: *"The product should eventually maintain a library of roughly 200–300 domain-specific templates …
The product does not need to fully implement every template at launch."*

| Measure | Count | |
|---|---:|---|
| Kept template rows, landed | 253 | |
| Owed rows | 46 | |
| Expected refusals among owed | ~6 | at the observed 36/289 ≈ 12.5% refusal rate |
| **Projected final catalogue** | **~293** | 253 + 46 − 6 |
| **Activatable at launch (live dimensions)** | **54** | §1.3 — closed, cannot grow (§1.1) |
| Proposed definitions for those 54 | 24 | §5.1 |
| Proposed shared fragments | 3 | §4.1 |

**VERDICT: the evidence supports 200–300 as the eventual catalogue size and refutes it as a launch
number.** The projected ~293 lands inside 00's band almost exactly — which is a real corroboration of the
roster's arithmetic, not a coincidence, since `roster.json`'s own `_comment` says the count *"deliberately
stops UNDER 00's roughly-200-300 target"* before the J-IND expansion restored it.

**What that implies, in three parts.**

1. **The gap between 293 and 54 is not implementation effort — it is B1.** 239 of the 293 are blocked on a
   schema decision (R1c / D1 / Joseph), not on a compiler. No amount of P10 work moves that number.
   00 anticipated the shape of this (*"Other domains remain placeholders until user demand and corpus
   evidence justify detailed templates"*), and the catalogue has honoured it literally.
2. **Fragment count does not scale with library size, and the evidence says so.** 54 rows over 6 schemas
   yield 3 fragments. If the ratio held, 293 rows would yield ~16 — but it will not hold, because the
   fragments found are the *general* ones (subject→artifact, affiliation prefix, cycle→artifact) and the
   long tail is domain-specific. **JUDGMENT: expect roughly 5–10 fragments at full catalogue, not 50.**
   A library that grows fragments proportionally to rows has stopped extracting reuse and started
   copying — plan §"copying the same fragment into several domain packages until the copies drift".
3. **G-SELECTION is the right gate and 54 is the right first wave.** The plan already says
   *"The design's eventual 200–300 library is not a licence to publish every research row automatically."*
   The 54 live rows are the only rows that can pass G-FIELDS today, so the release manifest writes itself:
   **54 applicability rows, 24 definitions, 3 fragments** — and everything else waits on B1–B4.

---

## Appendix — reproduction

```bash
cd "/Users/jy/GRAPH AGENT"
# inventory (§1)
python3 -c "
import json,os
r=json.load(open('planning/domains/roster.json')); N='planning/domains/nodes/'
f=set(os.listdir(N))
comp=[n for n in r['nodes'] if n['domain_id']+'.json' in f and n['domain_id']+'.research.md' in f]
rows=[json.load(open(N+n['domain_id']+'.json')) for n in comp]
t=[d for d in rows if d['kind']=='template']; kept=[d for d in t if not d['refuse_node']]
live=[d for d in kept if d['template']['dimension_order']]
print(len(comp),'complete /',len(t),'template /',len(kept),'kept /',len(live),'live')"
# role sequences (§3.0, §5.1) — role map is in section 2.1
```

Frozen evidence copy used for every count above:
`/private/tmp/claude-501/-Users-jy-GRAPH-AGENT/2f52e9a2-f991-458d-9ce2-7eeedfbf9349/scratchpad/snapshot.json`
(312 complete rows, 2026-08-27T04:44:12Z).
