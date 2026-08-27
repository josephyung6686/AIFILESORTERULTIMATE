# The corrected role vocabulary, and the recipe set re-cut on it

Date: 2026-08-27 · **Counts computed at 2026-08-27T12:24:57Z** against `planning/domains/nodes/`
(being written live by another session; the corpus was identical at the start and end of this pass).
Builds on [`37-TEMPLATE-REUSE-INVENTORY.md`](37-TEMPLATE-REUSE-INVENTORY.md),
[`41-TEMPLATE-DECISION-BRIEF.md`](41-TEMPLATE-DECISION-BRIEF.md) and
[`42-REUSE-FULL-CORPUS-CHECK.md`](42-REUSE-FULL-CORPUS-CHECK.md). Revises none of them.
`00-database-agent-product-design.md` wins on conflict.

**Every number below was recomputed from scratch, not inherited from 42.** The 54 field-derived rows
normalize mechanically; the 216 prose rows were re-read in full (330,349 bytes of `template.why`) and
re-assigned a role sequence by this pass. §8 reports where my independent read disagrees with 42's. It
agrees within about 5% on every headline, which is the strongest thing that can be said for either.

---

## 0. The answer, before the evidence

| | |
|---|---|
| **Final role count** | **24 adopted** = 15 kept + 9 added. **Zero retired.** Three further roles are *named and not adopted* (single-domain). |
| **The four near-dead roles** | **All four kept**, each for a specific reason (§2.3). `purpose_anchor` is **promoted** — it now clears the 2-domain bar and answers brief **O7** with *no, purpose is not applications-only*. |
| **Recipes safe to freeze now** | **11 pairs at ≥4 domains**, of which 4 have zero counter-examples anywhere in 256 rows and 2 are field-backed (§4.2). |
| **Recipes to hold** | **6 more clear the 2-domain bar at exactly 3 domains** — real, but one schema decision away from collapsing (§4.3). |
| **Contested — do not freeze** | **2.** `artifact_kind ↔ scope_period` (32 vs 13, a role doing two jobs) and `lifecycle_stage > artifact_kind` (20 prose rows for, 2 *bound* rows against). |
| **The four org roles** | **All four survive as genuinely distinct.** The merge is now refuted **twice over** — by the split-collapse table (§5.1) and, new in this pass, by 00's own no-self-repeat rule firing in 2 named rows (§5.2). |
| **What changes for the launch six** | **Nothing at the binding level. Zero of the 54 bound rows uses any new role** (§6). Two *rejections* change their reason, one default's *status* changes from general to research-local. The shipped orders are unchanged. |

**The single sentence.** The vocabulary was the binding constraint and it is now fixed: 24 roles, none
retired, and on that vocabulary the recipe set is **11 freezable pairs, not 3** — but every one of the 8
new roles is **prose-only**, so the recipe set that can actually *bind* at launch is still exactly the
brief's three. Fixing the vocabulary changes wave 2, not wave 1.

---

## 1. Method and evidence weighting

### 1.1 The corpus, at write time

```
complete rows (.json AND .research.md present):       333
kept template rows (kind==template, refuse_node falsy): 270  across 23 schemas
  ├─ FIELD-DERIVED: declares template.dimension_order   54  (6 schemas)
  └─ PROSE-DERIVED: dimension_order == []              216  (17 schemas)
rows carrying a usable role sequence                   256  (95%)
  ├─ from fields, mechanically                          54
  └─ from prose, by this pass's reading                 202
excluded: 8 rows that positively refuse depth + 6 with no recoverable order
```

Unchanged from 42's snapshot. No row landed or moved while this analysis ran.

### 1.2 The field half is mechanical; the prose half is a reading

The 54 bound rows normalize through the published field→role map (37 §2.1). All 22 distinct dimension
tokens map to exactly one role; unmapped tokens: **0**.

The 216 prose rows were read in full. Each was assigned one role sequence and a grade:

| Grade | Meaning | Rows |
|---|---|---:|
| **H** | the row states an ordered recommendation in its own words | **157** |
| **M** | hedged, conditional, split into two corpora, or written as a disjunction | **45** |
| **NONE** | the row positively recommends no depth at all | 8 |
| **UNK** | no order recoverable | 6 |

Two conventions, stated so they can be disagreed with:

1. **Optional levels count as present.** A row that says *"the ASSOCIATION only where the corpus genuinely
   spans more than one"* contributes that level to its sequence. The recipe question is relative order,
   not depth — 00 and the handoff both say templates carry *"recommended order, not mandatory depth."*
2. **Disjunctive levels take the first-named alternative**, unless both alternatives map to the same role.
   `career.recruiting`'s *"role or recruiting cycle"* is therefore counted as a subject, not a cycle. §9
   lists the three rows where the other reading would move a count.

The 8 NONE rows are the whole of `identity` (3) and `medical` (3) plus `legal.estate-planning` and
`legal.personal-legal-matters`. The 6 UNK rows are all `creative`. Identical to 42's finding, reached
independently.

### 1.3 Field evidence is never silently outvoted by prose

**Every table in this document reports field rows and prose rows in separate columns, and every
conclusion says which carried it.** Prose evidence is weaker on three counts, all live:

- it is **conditional** (most rows say "subject to R1c" or "if fields ever land");
- it is **unbound** — no prose level has been proved fillable, because no field exists to fill it;
- it is **normalized by a human reader**, not by a machine.

Where a conclusion rests on prose alone this document says so **in bold**.

---

## 2. The corrected role vocabulary

### 2.1 The 15 kept roles, at full corpus

Counts are rows / domains over the 256 rows carrying a sequence. `[F]` = the field-derived subset.

| Role | One-sentence definition | Rows | Dom | [F] rows | [F] dom | Evidence, verbatim |
|---|---|---:|---:|---:|---:|---|
| **`artifact_kind`** | what kind of document or record this is — the function level | **214** | **20** | 40 | 5 | canonical `record_type`: *"what kind of financial record this is"*; `work_type`: *"what kind of coursework artifact this is"* |
| **`subject_anchor`** | the named ongoing work or study the material belongs to, which outlives any one proceeding | **78** | **13** | 17 | 3 | canonical `project`: *"the named project a file belongs to"*; `creative.short-form-writing`: *"The recommendation is therefore the piece, then artifact_type"* |
| **`scope_period`** | the period a record *covers* or is measured over | 46 | 12 | 2 | 1 | `finance.tax-filings`: *"the filing IS the year"* |
| **`lifecycle_stage`** | where in a workflow an artifact sits | 33 | 7 | 4 | 1 | `engineering.stage-gate-review`: *"lifecycle_stage rises to second position because the gate IS the organising fact here"* |
| **`cycle_period`** | a named recurring process instance — term, round, wave, run, season — that is not a date | 31 | 7 | 8 | 2 | `hr.engagement-survey`: *"a wave is a named process instance, not a date"* |
| **`holder_institution`** | the organisation the *holder* belongs to, attends or files as | 22 | 7 | 8 | 2 | canonical `school`: *"the institution the holder attends, attended, or teaches at - the person's own school, never the application target"* |
| **`occasion_anchor`** | a bounded occurrence: a meeting, sitting, event, build, delivery, count | 22 | 11 | 6 | 1 | `business_operations.board-governance` orders the constituted body, *"then the meeting occurrence or cycle, then the document function"* |
| **`issuing_org`** | the organisation a record was **issued by** | 15 | 3 | 13 | 1 | canonical `institution`: *"the financial or record-issuing institution a record belongs to"* |
| **`addressed_org`** | the organisation the holder's material is **addressed to** | 10 | 5 | 6 | 2 | canonical `target_university`: *"the institution an application is addressed TO - never the holder's own school"* |
| **`capture_time`** | the year a capture was taken, from capture metadata | 10 | 3 | 8 | 1 | canonical `capture_year`; `construction_property.progress-photos`: *"SITE or job first, then the capture date, and nothing below that"* |
| **`account_kind`** | the **kind** of account a record belongs to — a category, not an instance | 5 | 1 | 5 | 1 | canonical `account_type`: *"the kind of account a financial record belongs to"* |
| **`capture_kind`** | what kind of capture this is — photo, screenshot, scan, video | 3 | 1 | 3 | 1 | canonical `media_type`: *"what kind of capture this is"* |
| **`purpose_anchor`** | what the file was **for**, as opposed to what it is about | 2 | **2** | 1 | 1 | `construction_property.survey-valuation` cites 00 by name: *"Topic answers what a file is about, while purpose answers what the file was for."* |
| **`place`** | where a capture was taken, resolved from GPS or content | 1 | 1 | 1 | 1 | canonical `location`: *"where a capture was taken, resolved from GPS or content"* |
| **`repository_instance`** | the named source repository a code file belongs to | 1 | 1 | 1 | 1 | canonical `repository`: *"the source repository a code file belongs to, from repo markers"* |

**`artifact_kind` reaches 20 of 23 schemas** and 214 of 256 rows. It is the only role that is nearly
universal, and every recipe that ends in it is really the same sentence: the function level goes last.

### 2.2 The 9 roles added

All nine are **prose-only** — zero field rows, zero of the 6 launch schemas. That is the whole reason
the 54-row sample could not see them.

| New role | One-sentence definition | Rows | Dom | [F] | Evidence, verbatim |
|---|---|---:|---:|---:|---|
| **`matter_anchor`** | a bounded proceeding, case, claim, application, transaction, engagement, tenancy, requisition or job that opens, runs and closes, usually against its own reference | **77** | **11** | 0 | `government.constituent-casework`: *"the only defensible first level here is the CASE as a bounded, opaque reference"* |
| **`site_anchor`** | a fixed facility, parcel, premises, installation or dwelling that the record is *about* | **48** | **10** | 0 | `logistics.warehouse-ops`: *"the same code `A-12-03-B` exists in every facility an operator runs"* |
| **`component_anchor`** | a designed or physical part nested inside a subject or matter: item, sheet, plot, unit, structure, package | **30** | **8** | 0 | `engineering.civil-structural`: *"a member mark is unintelligible outside the structure that contains it"* |
| **`counterparty_org`** | the client, customer or supplier an engagement serves — the **fourth** org role | 18 | **9** | 0 | canonical `client`, already destination-eligible: *"the counterparty organization an engagement serves - the target side of the our_firm split"* |
| **`asset_instance`** | an operated physical thing with an identity: vehicle, machine, meter, well, installed unit | 16 | 6 | 0 | `manufacturing.maintenance-work-order`: *"A job number is unintelligible without its asset"* |
| **`org_unit`** | an internal unit, cost centre, department, service area or constituted body — below the institution | 14 | 4 | 0 | `hr.org-design-headcount`: *"an establishment artifact is ABOUT a unit"* |
| **`series_instalment`** | a serial position that is neither a period nor a stage: issue no., volume, edition, baseline, valuation no., tier | 11 | 7 | 0 | `creative.periodical-issue`: *"the issue designator maps to no candidate key"* |
| **`standard_ref`** | an external standard, scheme or framework the material answers to | 4 | 2 | 0 | `business_operations.compliance-audit`: *"an EXTERNAL referent the entity is measured against, and it outlives every occurrence beneath it"* |
| **`variant_axis`** | a concurrent variant of one design: colourway, market, placement | 2 | 2 | 0 | `engineering.industrial-design`: *"appearance corpora carry a labelled variant slot far more reliably than a lifecycle gate"* |

`variant_axis` is adopted **provisionally**: it clears the 2-domain bar (`creative.ad-campaign`,
`engineering.industrial-design`) on only 2 rows. It is named so the two rows do not each invent it; it
should not carry a recipe.

**`counterparty_org` is not an invention.** `client` is already a canonical, `destination_eligible: true`
key with an explicit `role_split_with: our_firm`. It is missing from the *live* vocabulary only because
none of the six field-declaring schemas declares it. `manufacturing.field-service-report` names the key
verbatim when it argues for the level.

### 2.3 The four near-dead roles — all four KEPT

The instruction was not to retire a role merely for being small. None of the four should be retired, and
three of them for reasons that have nothing to do with size.

| Role | Size | Verdict | Why |
|---|---|---|---|
| **`purpose_anchor`** | 2 rows / **2 domains** | **KEEP — and promote** | It gained a second domain and now clears the same bar every recipe must clear. `construction_property.survey-valuation` argues it against 00 by name and against topic specifically: *"the same property, the same surveyor and nearly the same report exist in three purposes with three different audiences."* **This answers brief O7: purpose is not applications-only.** Prose evidence only. |
| **`capture_kind`** | 3 rows / 1 domain | **KEEP** | It is **bound** (3 of the 54). 37's R9 rejection is unchanged: `capture_kind` **leads** in `photos.scanned-documents` and `photos.screenshot-captures`, which no `artifact_kind` field ever does. Nothing in the 216 prose rows touches it — the rejection is untested at scale, not re-tested. |
| **`place`** | 1 row / 1 domain | **KEEP — and do not let `site_anchor` absorb it** | It is **bound** (`travel.trip-photos`). The corpus argues the split explicitly: `creative.raw-photo-catalogue` writes *"a camera roll goes to many places once, a site walk goes to one place many times"* — one place recurring is what makes a site a durable subject, and that is not what a capture location is. Merging them would also let a photos binding resolve a construction site. |
| **`repository_instance`** | 1 row / 1 domain | **KEEP** | It is **bound** (`code.dotfiles-environment`, whose whole argument is *"project is deliberately absent"*). Retiring it leaves `code` with no non-project anchor and forces exactly the `container` merge 37's **R2** already refused on instance-vs-category grounds. `account_kind` remains 5 rows / 1 domain, so R2's other half is also unchanged. |

**Zero roles retired.** Two of the four are one-row roles that are nevertheless *bound*, and retiring a
bound role would break a launch binding to tidy a table.

### 2.4 Three roles named and NOT adopted

Each is real in its own row and none reaches a second domain. Named so that a later pass does not
re-discover them, and so no recipe is cut along them.

| Candidate | Rows | Dom | The row that needs it |
|---|---:|---:|---|
| `channel_locus` — the platform or sales channel an utterance or order lives on | 2 | **1** | `retail_hospitality.guest-feedback`: *"a single-site hotel has one trading unit and five review channels"* — the row insists `site` cannot absorb it, and it is right, but both users are `retail_hospitality`. |
| `direction_role` — sent versus received | 1 | 1 | `clinical_practice.referral-correspondence`: *"direction is the property this situation is actually organized by and it discloses nothing about any patient"* |
| `provenance_role` — obtained versus authored versus published | 1 | 1 | `creative.journalism-reporting`: *"an interview recording and a draft are not two stages of one thing; one is input and one is output"* |

---

## 3. The full ranked adjacency table, re-cut

Bar, unchanged from the brief and 42: **a pair must appear in 2+ distinct domains.** "adjREV" counts rows
that place the same two roles the other way *adjacently*; "relREV" counts them at any distance. Field and
prose rows are split in every column. All 57 pairs occurring exactly once are omitted (none is
cross-domain by construction).

| # | Pair (adjacent) | F rows | F dom | P rows | P dom | **Total** | **Dom** | adjREV | relREV | Bar |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | `matter_anchor` > `artifact_kind` | 0 | 0 | 51 | 10 | **51** | **10** | **0** | **0** | PASS |
| 2 | `artifact_kind` > `scope_period` | 0 | 0 | 32 | 8 | 32 | 8 | 13 | 13 | **CONTESTED** |
| 3 | `subject_anchor` > `artifact_kind` | **14** | **3** | 16 | 6 | **30** | **9** | **0** | **0** | PASS |
| 4 | `cycle_period` > `artifact_kind` | **4** | **2** | 18 | 5 | **22** | **7** | 2 | 3 | PASS |
| 5 | `lifecycle_stage` > `artifact_kind` | 0 | 0 | 20 | 3 | 20 | 3 | 2 | 2 | **CONTESTED** |
| 6 | `subject_anchor` > `lifecycle_stage` | 1 | 1 | 17 | 2 | 18 | 3 | 0 | 0 | PASS |
| 7 | `site_anchor` > `matter_anchor` | 0 | 0 | 16 | 5 | **16** | **5** | **0** | **0** | PASS |
| 8 | `component_anchor` > `artifact_kind` | 0 | 0 | 14 | 6 | **14** | **6** | 2 | 2 | PASS |
| 9 | `scope_period` > `artifact_kind` | 2 | 1 | 11 | 6 | 13 | 7 | 32 | 32 | **CONTESTED** |
| 10 | `holder_institution` > `subject_anchor` | **4** | **2** | 7 | 3 | **11** | **5** | **0** | **0** | PASS |
| 11 | `subject_anchor` > `component_anchor` | 0 | 0 | 10 | 3 | 10 | 3 | 0 | 0 | PASS |
| 12 | `site_anchor` > `asset_instance` | 0 | 0 | 8 | 3 | 8 | 3 | 0 | 0 | PASS |
| 13 | `matter_anchor` > `lifecycle_stage` | 0 | 0 | 8 | 3 | 8 | 3 | 0 | 0 | PASS |
| 14 | `issuing_org` > `artifact_kind` | 8 | 1 | 0 | 0 | 8 | **1** | 1 | 1 | fail (1 dom) |
| 15 | `series_instalment` > `artifact_kind` | 0 | 0 | 7 | 5 | 7 | **5** | 0 | 0 | PASS |
| 16 | `site_anchor` > `artifact_kind` | 0 | 0 | 7 | 4 | 7 | 4 | 0 | 0 | PASS (38/9 rel) |
| 17 | `asset_instance` > `artifact_kind` | 0 | 0 | 6 | 5 | 6 | **5** | 0 | 0 | PASS |
| 18 | `occasion_anchor` > `artifact_kind` | 0 | 0 | 6 | 5 | 6 | **5** | 0 | 0 | PASS |
| 19 | `counterparty_org` > `matter_anchor` | 0 | 0 | 5 | 4 | 5 | 4 | 0 | 1 | PASS |
| 20 | `subject_anchor` > `cycle_period` | 0 | 0 | 5 | 4 | 5 | 4 | 3 | 3 | CONTESTED |
| 21 | `site_anchor` > `component_anchor` | 0 | 0 | 5 | 4 | 5 | 4 | 1 | 1 | PASS |
| 22 | `subject_anchor` > `matter_anchor` | 0 | 0 | 5 | 3 | 5 | 3 | 0 | 0 | PASS |
| 23 | `capture_time` > `occasion_anchor` | 4 | 1 | 1 | 1 | 5 | **2** | 1 | 1 | PASS |
| 24 | `artifact_kind` > `org_unit` | 0 | 0 | 5 | 2 | 5 | 2 | 2 | 8 | CONTESTED |
| 25 | `counterparty_org` > `subject_anchor` | 0 | 0 | 5 | 1 | 5 | 1 | 0 | 0 | fail (1 dom) |
| 26 | `subject_anchor` > `series_instalment` | 0 | 0 | 4 | 4 | 4 | 4 | 0 | 0 | PASS |
| 27 | `addressed_org` > `subject_anchor` | 1 | 1 | 3 | 2 | 4 | 3 | 1 | 1 | CONTESTED |
| 28 | `org_unit` > `cycle_period` | 0 | 0 | 4 | 3 | 4 | 3 | 1 | 5 | CONTESTED |
| 29 | `holder_institution` > `cycle_period` | 3 | 1 | 1 | 1 | 4 | 2 | 0 | 0 | PASS |
| 30 | `matter_anchor` > `occasion_anchor` | 0 | 0 | 4 | 2 | 4 | 2 | 1 | 1 | CONTESTED |
| 31 | `account_kind` > `artifact_kind` | 4 | 1 | 0 | 0 | 4 | 1 | 1 | 1 | fail (1 dom) |
| 32 | `asset_instance` > `scope_period` | 0 | 0 | 4 | 1 | 4 | 1 | 0 | 0 | fail (1 dom) |
| 33 | `counterparty_org` > `cycle_period` | 0 | 0 | 3 | 3 | 3 | 3 | 0 | 0 | PASS |
| 34 | `matter_anchor` > `cycle_period` | 0 | 0 | 3 | 2 | 3 | 2 | 1 | 1 | CONTESTED |
| 35 | `cycle_period` > `subject_anchor` | 3 | 1 | 0 | 0 | 3 | 1 | 5 | 5 | fail (1 dom) |
| 36 | `issuing_org` > `account_kind` | 3 | 1 | 0 | 0 | 3 | 1 | 0 | 0 | fail (1 dom) |
| — | 21 further pairs at exactly 2 rows | | | | | 2 | ≤2 | | | see §3.1 |

### 3.1 The 2-row tail, for completeness

`component_anchor > variant_axis` (2/2) · `component_anchor > occasion_anchor` (2/2, rev 2) ·
`site_anchor > subject_anchor` (2/2, rev 1) · `asset_instance > matter_anchor` (2/2, rev 1) ·
`matter_anchor > component_anchor` (2/2) · `component_anchor > scope_period` (2/2) ·
`holder_institution > matter_anchor` (2/2) · `holder_institution > artifact_kind` (2/2, **20/7 rel**) ·
`counterparty_org > artifact_kind` (2/2, **16/9 rel**) · `org_unit > artifact_kind` (2/2, rev 5) ·
`artifact_kind` > `cycle_period` (2/2, rev 22) · `occasion_anchor > component_anchor` (2/2, rev 2) ·
`matter_anchor > scope_period` (2/2, **16/6 rel**) · `site_anchor > scope_period` (2/2, **15/7 rel**) ·
`standard_ref > artifact_kind` (2/1) · plus 6 single-domain pairs.

**Note the four with large relative-order counts.** `counterparty_org > artifact_kind` is adjacent in only
2 rows but holds at a distance in **16 rows across 9 domains with zero reversals** — the counterparty is
almost always separated from the function by a matter or an asset. Adjacency under-reads it; §4 uses
relative order where the difference is material.

---

## 4. The recommended recipe set

### 4.1 The rule I applied

A recipe is frozen when it clears **all four**: (a) 2+ distinct domains; (b) reverse count under 25% of
its own count; (c) the two roles are distinct after §5's merge tests; (d) the direction is argued, not
merely observed, in at least one row. I then split the survivors by domain reach, because a 10-domain
pair and a 3-domain pair are not the same kind of fact.

### 4.2 FREEZE NOW — 11 pairs at 4 or more domains

| Recipe | Plain English | F rows/dom | P rows/dom | Total | Dom | Rev | Carried by |
|---|---|---|---|---:|---:|---:|---|
| **1 · `matter_anchor > artifact_kind`** | the case, then the kind | 0 / 0 | 51 / 10 | **51** | **10** | **0** | **PROSE ONLY** |
| **2 · `subject_anchor > artifact_kind`** | the project-or-course, then the kind | **14 / 3** | 16 / 6 | **30** | **9** | **0** | **FIELD**, corroborated by prose |
| **3 · `cycle_period > artifact_kind`** | the term-or-round, then the kind | **4 / 2** | 18 / 5 | **22** | **7** | 2 | **FIELD**, corroborated by prose |
| **4 · `site_anchor > matter_anchor`** | the place, then the case on it | 0 / 0 | 16 / 5 | **16** | **5** | **0** | **PROSE ONLY** |
| **5 · `component_anchor > artifact_kind`** | the part-or-sheet, then the kind | 0 / 0 | 14 / 6 | **14** | 6 | 2 | **PROSE ONLY** |
| **6 · `holder_institution > subject_anchor`** | my institution, then my work | **4 / 2** | 7 / 3 | **11** | **5** | **0** | **FIELD**, corroborated by prose |
| **7 · `series_instalment > artifact_kind`** | the issue-or-baseline, then the kind | 0 / 0 | 7 / 5 | 7 | **5** | **0** | **PROSE ONLY** |
| **8 · `site_anchor > artifact_kind`** | the place, then the kind (38 rows / 9 dom at any distance) | 0 / 0 | 7 / 4 | 7 | 4 | **0** | **PROSE ONLY** |
| **9 · `asset_instance > artifact_kind`** | the machine-or-vehicle, then the kind | 0 / 0 | 6 / 5 | 6 | **5** | **0** | **PROSE ONLY** |
| **10 · `occasion_anchor > artifact_kind`** | the meeting-or-event, then the kind | 0 / 0 | 6 / 5 | 6 | **5** | **0** | **PROSE ONLY** |
| **11 · `counterparty_org > matter_anchor`** | the client, then the engagement | 0 / 0 | 5 / 4 | 5 | 4 | 0 | **PROSE ONLY** |

**Four of the eleven have zero counter-examples anywhere in 256 rows, in either direction, adjacent or at
distance: 1, 2, 4, 6.** Those four are as clean as this corpus can make anything.

**The three original recipes all survive, and their identities are unchanged.** Recipe 1 of the brief is
#2 here; Recipe 2 is #6; Recipe 3 is #3. Recipe 2 — the one the brief offered to cut — is still 11 rows
in 5 domains with zero counter-examples, and it is one of only three recipes with a field-derived half.
**Do not cut it.**

**The one that dominates the corpus is #1, and it is entirely unbound.** 51 adjacent rows across 10
domains, 64 rows across 11 at any distance, zero reversals — and not one of them can produce a folder
today. Eight of its ten domains are `law_practice`, `government`, `construction_property`,
`business_operations`, `hr`, `manufacturing`, `retail_hospitality`, `career`.

### 4.3 HOLD — 6 more clear the bar at exactly 3 domains

Real, but three domains is one schema decision from two, and none has a field row except #6's single one.

| Recipe | Total | Dom | Rev | Note |
|---|---:|---:|---:|---|
| `subject_anchor > lifecycle_stage` | 18 | 3 | 0 | 17 prose (`creative`, `engineering`) + 1 field (`research.grants-funding`). Entangled with the contested pair below. |
| `subject_anchor > component_anchor` | 10 | 3 | 0 | `business_operations`, `creative`, `engineering`. The engineering spine. |
| `site_anchor > asset_instance` | 8 | 3 | 0 | `business_operations`, `manufacturing`, `resource_operations`. |
| `matter_anchor > lifecycle_stage` | 8 | 3 | 0 | `business_operations`, `construction_property`, `government`. |
| `subject_anchor > matter_anchor` | 5 | 3 | 0 | The nesting that proves matter ≠ subject. See §5.2. |
| `counterparty_org > cycle_period` | 3 | 3 | 0 | `business_operations`, `government`, `hr`. Thin on rows, wide on domains. |

### 4.4 CONTESTED — do not freeze

**A · `artifact_kind ↔ scope_period` — a role doing two jobs.**

| Direction | Rows | Dom | Field |
|---|---:|---:|---:|
| `artifact_kind > scope_period` (period is a trailing discriminator) | **32** | 8 | 0 |
| `scope_period > artifact_kind` (period is the record's identity) | 13 | 7 | **2** |

The split is not noise; it tracks a distinction the vocabulary does not make. Both of the *bound* rows are
on the minority side, and both argue it: `finance.tax-filings` — *"the filing IS the year"*;
`government.emergency-management` — the operational period's reports are *"unintelligible outside the
period they report on"*. Against them, `law_practice.motions-and-briefs` puts period last under function,
and all six `resource_operations` rows put a reporting period above record type. **Until `scope_period`
splits, this is not a recipe.** (42's F2, confirmed at 32:13.)

**B · `lifecycle_stage > artifact_kind` — the count says yes, the bound rows say no.**

| Direction | Rows | Dom | Field | Consecutive `subject > stage > kind` |
|---|---:|---:|---:|---:|
| `lifecycle_stage > artifact_kind` — 00's original order | **20** | 3 (`creative`, `engineering`, `government`) | **0** | **16 rows / 2 domains** |
| `artifact_kind > lifecycle_stage` — the brief's §4-B flip | 2 | 1 (`research`) | **2** | 2 rows / 1 domain |

00 §5.4's full chain `project → stage → artifact type` — which 37 recorded as realized by *"not one landed
row"* — is realized as a consecutive three-level chain by **16 rows across `creative` (14) and
`engineering` (2)**. By the brief's own 2-domain bar, **00's original order clears it and the flip does
not.** But the 2 rows against are the only **bound** rows on the pair, and they are `research`'s own.
**The honest reading: the brief's §4-B default is right for research and cannot be generalized.** §6
states the consequence. (42's F3, reached independently; my count is 16/2, 42's was 17/2.)

### 4.5 What this does to brief §7.8

The brief estimated *"recipes should reach ~5–10 at full size."* At the corrected vocabulary,
**11 pairs clear a 4-domain bar and 17 clear the 2-domain bar** before any of the contested pairs is
resolved. The estimate is low, and it was low because the vocabulary was short, not because the corpus
is noisy.

---

## 5. Re-testing the rejections at the corrected vocabulary

### 5.1 The org merge — STILL FORBIDDEN, and now refuted twice

00: *"The system must separate roles that happen to contain the same entity type."* With
`counterparty_org` added there are four org roles. Merging all four into one `ORG`:

| Merged appearance | What it really is when split correctly |
|---|---|
| `ORG > subject_anchor` — **21 rows / 6 domains** | `holder_institution` 11 / **5** · `counterparty_org` 5 / **1** · `addressed_org` 4 / 3 · `issuing_org` 1 / **1** |
| `ORG > artifact_kind` — **14 rows / 5 domains** | `issuing_org` 8 / **1** · `holder_institution` 2 / 2 · `addressed_org` 2 / **1** · `counterparty_org` 2 / 2 |
| `ORG > matter_anchor` — 7 rows / 5 domains | `counterparty_org` 5 / 4 · `holder_institution` 2 / 2 |
| `ORG > cycle_period` — 8 rows / 6 domains | `holder_institution` 4 / 2 · `counterparty_org` 3 / 3 · `addressed_org` 1 / **1** |

**The cleanest refutation is arithmetic.** `holder_institution > subject_anchor` **already reaches 5
domains on its own** (§4.2 #6). The merge adds one domain and destroys the distinction 00 forbids losing.
It buys nothing.

**Are all four genuinely distinct? Yes — and each has row evidence.**

| Role | The row that refuses to be any of the other three |
|---|---|
| `holder_institution` | `career.consulting-client-engagement`: *"`our_firm` must NOT be a level, ever, even though it is the single most reliably extractable organization on these files."* The holder's own org is bound to `our_firm`, whose canonical row is `destination_eligible: false`. |
| `counterparty_org` | `creative.submission-query`: *"its organizing anchor is an ADDRESSEE IN A SUBMITTED-TO ROLE and `client` is a COMMISSIONING role."* The row refuses `client` for itself and takes `addressed_org` instead — a distinction it could not draw if the two were one role. |
| `addressed_org` | canonical `target_university`, which carries `role_split_with: school` explicitly: *"the institution an application is addressed TO - never the holder's own school."* |
| `issuing_org` | `manufacturing.field-service-report`: *"the schema's `site` is expressly the facility that PERFORMS production, which the holder does not have in these files - the only site present belongs to a third party."* The row reaches for `client`, not for the issuer, and says why. |

`business_operations.corporate-regulatory-filings` settles it in one sequence:
`holder_institution > addressed_org > scope_period > artifact_kind` — *"the entity whose obligation it
is"* on top and the authority it files **to** beneath. Two org roles, one path, opposite directions.

### 5.2 A second, independent refutation the corpus supplies on its own

00 forbids a template that would *"repeat a parent dimension."* Running every proposed merge against that
rule, over all 256 sequences:

| Proposed merge | Rows that become an illegal self-repeat |
|---|---:|
| `component_anchor` → `subject_anchor` | **10** |
| `matter_anchor` → `subject_anchor` | **5** |
| **4 org roles → one `ORG`** | **2** |
| `asset_instance` → `component_anchor` | 1 |
| `site_anchor` → `place` | 0 |
| `scope_period` → `cycle_period` | 0 |

The org merge breaks `business_operations.corporate-regulatory-filings` and
`business_operations.partnerships-bd` — the latter reading *organisation → counterparty → pursuit →
function*. **The corpus refuses the merge structurally, not just statistically.** This is new: 42
established the arithmetic refutation; the self-repeat refutation is this pass's.

The matter/subject merge fails in 5 named rows: `business_operations.go-to-market` (*"the offering, then
the launch or release, then the function or document type"*), `law_practice.ip-prosecution`,
`manufacturing.failure-analysis`, `manufacturing.production-record` (*"product, then executed order or
batch"*), `manufacturing.warranty-claim`. The component/subject merge fails in 10, all `engineering` and
`business_operations`. **Neither tempting merge is available.**

### 5.3 The other four rejections

| # | Rejection | Status at the corrected vocabulary |
|---|---|---|
| **R2** | `container` merging `repository` and `account_type` | **HOLDS, and now costs nothing.** `account_kind` is still 5 rows / **1 domain** (finance) and `repository_instance` still 1 row / 1 domain (code). Neither gained a domain from the 216 prose rows. The merge would add one row and one domain and destroy an instance-vs-category distinction. |
| **R4** | `frag.issuer-then-record` — finance's own default wearing a fragment's clothes | **HOLDS on the pair, with a correction to its reason.** `issuing_org` is **no longer a single-domain role** — it reaches 15 rows / 3 domains (`finance`, `career.credentials-licenses`, `engineering.standards-library`). But the *pair* `issuing_org > artifact_kind` is still **8 rows / 1 domain**. The other two rows order it differently (`issuing_org > subject_anchor`, `issuing_org > standard_ref`). The rejection stands; the reason narrows from "single-domain role" to "single-domain pair". |
| **R3** | `frag.capture-time-then-occasion` — rejected because *"all 9 contexts are one schema"* | **The stated reason no longer holds; the rejection does.** `capture_time > occasion_anchor` now reaches **2 domains** — 4 photos field rows plus `creative.raw-photo-catalogue`, which recommends *"CAPTURE DATE FIRST, then at most one slug level, and then nothing."* It clears the 2-domain bar. It still cannot ship: `creative` declares zero fields. **Re-reject on bindability, not on domain count** — and note that `construction_property.progress-photos` names the discriminator from the other side (*"SITE or job first, then the capture date"*). |
| **R9** | folding `media_type` into `artifact_kind` | **HOLDS, untouched.** `capture_kind` is 3 rows in `photos` only; nothing in the 17 prose domains touches it. |

---

## 6. What changes for the launch six

**Short version: nothing you ship changes. Two rejections change their stated reason and one default
changes its scope. The 54 bindings are untouched.**

### 6.1 Does any launch binding now use a new role? **No — zero.**

> **Verified mechanically.** Bound rows whose role sequence contains any of the 12 new roles: **0 of 54**.
> All 22 dimension tokens across the 54 bound rows map to the original 15 roles, and all 12 new roles are
> used **only** by prose rows: `matter_anchor`, `site_anchor`, `component_anchor`, `counterparty_org`,
> `asset_instance`, `series_instalment`, `org_unit`, `standard_ref`, `variant_axis`, `channel_locus`,
> `direction_role`, `provenance_role`.

The 15-role list published in brief §2.3 **is exactly the launch vocabulary**, and it remains correct as
a launch document. The 9 added roles are a wave-2 vocabulary. Brief §5's 54 bindings and §7's ownership
list need no edit.

### 6.2 Does the default order change for any of the 7 families? **One family changes status, none changes order.**

| Family | Brief's default | Corpus at the corrected vocabulary | Change |
|---|---|---|---|
| **A · Academics** | `school > term > subject > work_type` | Every pair in it is a §4.2 freeze-now recipe (#6, #3, #2), all with zero counter-examples. | **None. Reinforced.** |
| **B · Research work** | the flip: `project > artifact_type > stage` | `lifecycle_stage > artifact_kind` is 20 rows / 3 domains against 2 rows / 1 domain; the consecutive `subject > stage > kind` chain is 16 rows / 2 domains against 2 / 1. **Both bound rows are on the brief's side and both are research's own.** | **Keep the default; change its status.** It is a **research-local** default, not a general finding. The brief already ships 00's order as Option B, so nothing shipped moves — but §4-B must not be generalized to `creative` or `engineering` in wave 2. |
| **C · Research manuscripts** | flat | Nothing in the 216 prose rows touches `subject_anchor ↔ addressed_org`. Still 1-for-1 (brief **O2**). | **None.** |
| **D · Applications** | `target_university > cycle > document` | `addressed_org > subject_anchor` reaches 4 rows / 3 domains (`career`, `creative`, `research`) but `addressed_org > cycle_period` is still 1-for-1. Brief **O1** unchanged. | **None.** |
| **E · Photos** | `capture_year > event` | The pair now reaches **2 domains** (§5.3 R3) — but the second is `creative`, which has no fields. `place` keeps its distinctness (§2.3). | **None shipped.** R3's reason changes from "one schema" to "one *bindable* schema". |
| **F · Finance** | `institution > account_type > record_type` | `issuing_org` widens to 3 domains as a **role** but the pair stays finance-only; `account_kind` stays finance-only. | **None.** R2 and R4 both hold. |
| **G · Code** | `project > artifact_type` | `repository_instance` kept (§2.3); `subject_anchor > artifact_kind` is now a 9-domain recipe. | **None. Reinforced.** |

### 6.3 One binding-level consequence worth recording

`purpose_anchor` is no longer applications-only (brief **O7** answered: *no*). But
`construction_property` declares zero fields, so `def.purpose-packet` stays a one-schema definition at
launch and generalizes in wave 2. **This changes the answer to O7 without changing the launch manifest.**

---

## 7. Where the design and the evidence disagree

Recorded plainly, not resolved. These are the owner's, not mine.

1. **00 §5.4's Research order versus the two bound research rows.** §4.4 B. 00 says
   `project → stage → artifact type`; the only two rows that can bind it invert it and argue the
   inversion. The corpus at large (16 rows / 2 domains) is on 00's side; the bound evidence (2 rows /
   1 domain) is on the brief's. Shipping 2–3 candidate orders per template — the brief's own §4.1
   amendment — is exactly what this situation is for, and it is why that amendment matters more now than
   when it was written.
2. **`matter_anchor` nests inside itself in one row.** `construction_property.variation-claim` recommends
   *"the project or contract first, then the change or claim itself as its own container"* — two bounded
   engagements, one inside the other. Under any consistent reading of the role that is
   `matter_anchor > matter_anchor`, which 00's *"does not repeat a parent dimension"* forbids at the role
   level. It is legal at the **field** level (two different fields would fill the two slots), which is
   how the runtime actually validates. **This is the one place my vocabulary produces an illegal
   sequence, and I am flagging it rather than reading the row differently to make the table clean.**
   It is also why the merge tests in §5.2 all report a baseline of 1.
3. **Three rows carry a "service function" or "business area" level that no role fits.**
   `government.library-administration` (stock / membership / programming / performance),
   `government.parks-public-lands` (estate function), `government.school-district-administration`
   (authority-side function). These sit *above* a subject and *above* the document-function level, so
   they are neither `artifact_kind` nor `org_unit`, and I mapped them to `org_unit` as the least-wrong
   option. A `function_area` role may be owed. All three are `government`; it does not clear the bar.

---

## 8. Where this pass disagrees with 42, and by how much

42's prose reading and mine were made independently from the same 216 `template.why` blocks. Publishing
the deltas is the only way to say how much either is worth.

| Quantity | 42 | This pass | Delta |
|---|---:|---:|---:|
| Grade distribution (HIGH / hedged / NONE / UNK) | 157 / 44 / 8 / 6 | 157 / 45 / 8 / 6 | ~0 |
| `matter_anchor` role uses | 80 rows / 12 dom | 77 / 11 | −3 / −1 |
| `site_anchor` | 43 / 10 | 48 / 10 | +5 / 0 |
| `component_anchor` | 29 / 9 | 30 / 8 | +1 / −1 |
| `counterparty_org` | 17 / 8 | 18 / 9 | +1 / +1 |
| `asset_instance` | 17 / 7 | 16 / 6 | −1 / −1 |
| `series_instalment` | 9 / 6 | 11 / 7 | +2 / +1 |
| `org_unit` | 9 / 3 | 14 / 4 | +5 / +1 |
| `standard_ref` | 3 / 2 | 4 / 2 | +1 / 0 |
| Recipe `matter_anchor > artifact_kind` | 55 / 11 | 51 / 10 | −4 / −1 |
| Recipe `subject_anchor > artifact_kind` | 31 / 9 | 30 / 9 | −1 / 0 |
| Recipe `holder_institution > subject_anchor` | 11 / 5 | **11 / 5** | **exact** |
| Recipe `cycle_period > artifact_kind` | 24 / 7 | 22 / 7 | −2 / 0 |
| `artifact_kind > scope_period` vs reverse | 31 : 13 | 32 : 13 | +1 : 0 |
| `lifecycle_stage > artifact_kind` | 22 / 4 | 20 / 3 | −2 / −1 |
| 00's `subject > stage > kind` chain | 17 / 2 | 16 / 2 | −1 / 0 |

**Every headline survives at both readings, and no verdict flips.** The largest single divergence is
`org_unit` (+5 rows), because I read `government`'s "service area" and "authority-side function" levels
as units where 42 did not; and `lifecycle_stage > artifact_kind` loses `retail_hospitality` because I read
`retail_hospitality.event-production` as `occasion_anchor > lifecycle_stage` with no function level below.
**Two independent readings agreeing within ~5% on a 216-row manual pass is the useful result here** — it
means the prose layer is reproducible enough to cut recipes on, which was not previously known.

---

## 9. OPEN — what the corpus does not settle

| | Question | What would settle it |
|---|---|---|
| **O1** | **Does `scope_period` split into "the period a record covers" and "the period under which a function repeats"?** 32 rows put the period below the function, 13 above, and both bound rows are in the minority. | A vocabulary decision. Until then §4.4 A is not a recipe. (= 42's F2.) |
| **O2** | **Does the brief's §4-B flip generalize beyond research?** 16 prose rows in 2 domains say no; 2 bound rows say yes for research. | `creative` or `engineering` landing fields. (= 42's F3.) |
| **O3** | **Do prose-derived orders bind at all, or must every recipe be re-derived once fields land?** 8 of the 11 freeze-now recipes are prose-only, including the largest. | R1c. Every conclusion in §4 that rests on prose alone is conditional on this. (= 42's F4.) |
| **O4** | **Is `matter_anchor > artifact_kind` one recipe or two, split by whether the level may be *named*?** `construction_property.trade-job` and `law_practice.family-law` share the shape exactly; one names a job number, the other *"discloses that a named person is being divorced."* | A privacy-class decision, not more rows. (= 42's F1, and brief **O4**.) |
| **O5** | **May `matter_anchor` nest inside itself?** §7.2. One row needs it; 00's no-repeat rule appears to forbid it at role level and permit it at field level. | A P10 contract decision about whether the no-repeat check runs on roles or on fields. |
| **O6** | **Is `channel_locus` a role?** 2 rows, 1 domain. `retail_hospitality.guest-feedback` proves `site_anchor` cannot absorb it; nothing proves it generalizes. | A second domain, or a decision that channel is an `addressed_org`. |
| **O7** | **`operating_authority` in the four `resource_operations` rows — `holder_institution` or `counterparty_org`?** I read it as the holder; if the operator is a third party it is a counterparty. | R1c. Affects one pair count. (= 42's judgement call 3, still unresolved.) |
| **O8** | **Is there a `function_area` role?** §7.3 — three `government` rows carry a business-area level above both subject and function. All three are one domain. | A second domain. |
| **O9** | **Three rows where my first-named-alternative rule changes a count.** `creative.podcast-episode` (*"episode identifier or project facet"* — I took `series_instalment`; the other reading adds a row to Recipe 2 of §4.2), `career.recruiting` (*"role or recruiting cycle"* — I took `subject_anchor`), `business_operations.retrospective-postmortem` (*"the effort or the incident"* — I took `matter_anchor`). | Nothing; they are genuinely ambiguous rows. Recorded so the numbers can be audited. |
| **O10** | **`variant_axis` at 2 rows / 2 domains** — adopted provisionally. Two rows is a thin basis for a role. | A third row, or a decision to fold it into a per-definition local role. |

---

## Appendix — reproduction

The field half is fully mechanical. The prose half is a reading; the assignment table it produced lives in
this session's scratchpad at `prose_seqs.py` and is reproduced in full by re-reading the corpus dumped by
the last command below.

```bash
cd "/Users/jy/GRAPH AGENT"

# §1.1 corpus census
python3 -c "
import json,os
r=json.load(open('planning/domains/roster.json')); N='planning/domains/nodes/'; f=set(os.listdir(N))
rows=[json.load(open(N+n['domain_id']+'.json')) for n in r['nodes']
      if n['domain_id']+'.json' in f and n['domain_id']+'.research.md' in f]
kept=[d for d in rows if d['kind']=='template' and not d.get('refuse_node')]
bound=[d for d in kept if d['template'].get('dimension_order')]
print('complete',len(rows),'| kept',len(kept),'across',len({d['schema_id'] for d in kept}),
      'schemas | bound',len(bound),'| prose',len(kept)-len(bound))"

# §2.1 the 22 tokens across the 54 bound rows, and the role each maps to
python3 -c "
import json,os,collections
r=json.load(open('planning/domains/roster.json')); N='planning/domains/nodes/'; f=set(os.listdir(N))
rows=[json.load(open(N+n['domain_id']+'.json')) for n in r['nodes']
      if n['domain_id']+'.json' in f and n['domain_id']+'.research.md' in f]
t=collections.Counter(x for d in rows if d['kind']=='template' and not d.get('refuse_node')
                        for x in (d['template'].get('dimension_order') or []))
print(len(t),'distinct tokens'); [print(' ',k,v) for k,v in t.most_common()]"

# §2.2 counterparty_org is already canonical and already destination-eligible
python3 -c "
import json
for f in json.load(open('planning/domains/canonical_fields.json'))['fields']:
    if f['key'] in ('client','our_firm','school','target_university'):
        print(f['key'], '| split_with', f.get('role_split_with'), '| dest', f['destination_eligible'])
        print('   ', f['role'])"

# §6.1 no bound row uses a new role - the launch vocabulary is exactly the original 15
python3 -c "
import json,os,collections
M={'work_type':'artifact_kind','artifact_type':'artifact_kind','record_type':'artifact_kind',
'application_document_type':'artifact_kind','project':'subject_anchor','subject':'subject_anchor',
'institution':'issuing_org','target_university':'addressed_org','venue':'addressed_org',
'term':'cycle_period','application_cycle':'cycle_period','school':'holder_institution',
'lab':'holder_institution','capture_year':'capture_time','event':'occasion_anchor',
'account_type':'account_kind','repository':'repository_instance','stage':'lifecycle_stage',
'media_type':'capture_kind','tax_year':'scope_period','purpose':'purpose_anchor','location':'place'}
r=json.load(open('planning/domains/roster.json')); N='planning/domains/nodes/'; f=set(os.listdir(N))
rows=[json.load(open(N+n['domain_id']+'.json')) for n in r['nodes']
      if n['domain_id']+'.json' in f and n['domain_id']+'.research.md' in f]
u=collections.Counter()
for d in rows:
    if d['kind']=='template' and not d.get('refuse_node'):
        for x in (d['template'].get('dimension_order') or []): u[M[x]]+=1
print(len(u),'roles used by bound rows:'); [print(' ',k,v) for k,v in u.most_common()]"

# §4.4 B - the two bound rows that contradict 00's Research order
python3 -c "
import json
for i in ['research.dataset-analysis','research.thesis-dissertation','research.grants-funding']:
    print(i, ' > '.join(json.load(open('planning/domains/nodes/%s.json'%i))['template']['dimension_order']))"

# the 216 prose corpus this pass read in full (330,349 bytes)
python3 -c "
import json,os,collections
r=json.load(open('planning/domains/roster.json')); N='planning/domains/nodes/'; f=set(os.listdir(N))
rows=[json.load(open(N+n['domain_id']+'.json')) for n in r['nodes']
      if n['domain_id']+'.json' in f and n['domain_id']+'.research.md' in f]
by=collections.defaultdict(list)
for d in rows:
    if d['kind']=='template' and not d.get('refuse_node') and not d['template'].get('dimension_order'):
        by[d['schema_id']].append((d['id'], d['template']['why']))
for s in sorted(by):
    print('#'*8, s, len(by[s]))
    for i,w in sorted(by[s]): print('###', i); print(w); print()"
```

Every quotation in this document was checked against its row's `template.why` by exact substring match
before publication; misses: **0** of 48.

---

## 9. Requirement for P10 Task 8 — the vocabulary must not be a ceiling

Added 2026-08-27 after the owner asked: *"we cannot be limited to the ones in my computer."*
He is right, and the design agrees — but one unbuilt piece decides whether it is true in practice.

**What the design promises.** §5.7: *"When an accepted organizational group does not fit any existing
template, the LLM may generate a **candidate custom template**"*, which *"cannot invent unsupported
facts, silently create new high-level domains, or become active merely because it is syntactically
valid."* §3.15: other domains *"remain placeholders until user demand and corpus evidence justify
detailed templates"* — hand-authoring hundreds of schemas was explicitly never the plan.

**What live code does today.** `src/llm_harness/template_validation.py:102-103` rejects any proposed
dimension whose name is outside the allowed set:

```python
vocab = set(dossier.allowed_vocabulary)
dimensions = _dimensions(payload)
if any(item.get("name") not in vocab for item in dimensions):
```

`vocab` is read from the **dossier**, per call — correctly. P8 imposes no global ceiling.

**The requirement.** P10 Task 8 builds the Site-E dossier. Whatever it puts in `allowed_vocabulary`
becomes the real limit on what the product can organize.

1. `allowed_vocabulary` MUST NOT be the 24 canonical roles alone. A group from an unresearched
   domain would then have every proposed dimension rejected, and §5.7's custom-template path would be
   dead on arrival — the product would be limited to the domains in this repository's research.
2. It MUST carry the canonical roles **plus template-local dimension names justified by that group's
   own evidence**. `TEMPLATE-BUILDING-HANDOFF.md` already draws this line: a Site E prompt *"may
   include template-local semantic dimensions, but it cannot publish or propose a new canonical
   fragment. Repeated local dimensions become fragment candidates only in the later human-reviewed
   synthesis pass."*
3. A template-local dimension MUST still satisfy every other Site-E check — schema validity, an
   `evidence_ref` per dimension (`:112-113`), and the §5.7 engine checks (no repeated parent
   dimension, no one-child level, depth limits, no organization-as-collector, no protected exposure,
   no empty branch).
4. Promotion of a recurring local dimension into the canonical vocabulary is a **human-reviewed
   pass**, never automatic and never a model's decision.

**The asymmetry to preserve:** the product adapts to a new domain *immediately*, at template-local
scope; the shared vocabulary grows *deliberately*, after a human sees the pattern recur. A test should
assert both halves — that an evidence-backed novel dimension is accepted, and that nothing promotes it
to canonical without review.

**Status:** OPEN. P10 Task 8 is unbuilt. This section is the requirement it must meet.
