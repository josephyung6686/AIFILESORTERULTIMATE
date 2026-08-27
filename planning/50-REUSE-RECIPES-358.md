# The reuse recipes, recomputed on the complete 358-row corpus

Date: 2026-08-27 · **Every count below was recomputed from `planning/domains/nodes/` at
2026-08-27T14:42:17Z.** Nothing is inherited from [`37-TEMPLATE-REUSE-INVENTORY.md`](37-TEMPLATE-REUSE-INVENTORY.md),
[`41-TEMPLATE-DECISION-BRIEF.md`](41-TEMPLATE-DECISION-BRIEF.md), [`42-REUSE-FULL-CORPUS-CHECK.md`](42-REUSE-FULL-CORPUS-CHECK.md)
or [`43-ROLE-VOCABULARY-AND-RECUT.md`](43-ROLE-VOCABULARY-AND-RECUT.md); where this pass disagrees with them, §9 says so.
`00-database-agent-product-design.md` wins on conflict.

**Status: PROPOSAL.** Nothing here is adopted. No `src/` file, no `planning/domains/*.json`, and no template
record was written or edited by this pass.

**Scope note.** All 237 field-less rows were read in full (362,996 bytes of `template.why`) and assigned a role
sequence by this pass. Every template row in the corpus is accounted for — none was sampled, skipped or
inferred from a sibling.

---

## 0. The answer, before the evidence

| | |
|---|---|
| **Recipes visible at 358 rows** | **16 role pairs clear a 4-domain bar with zero or negligible reversal**, and **23 full role SEQUENCES recur across two or more schemas.** The brief's three are all inside that set; so is doc 42's fourth. |
| **Do the earlier recipes survive?** | **All four survive and all four grew.** Not one dissolves. The "cut Recipe 2" advice stays wrong. **Two pairs doc 43 recorded as single-domain failures now pass**, and **three it held at exactly 3 domains now reach 4.** |
| **Definitions needed for 291 rows** | **133** at exact role sets, **79** if a definition may carry one optional role, **66** at two. The launch six need **28 / 14 / 11** on the same three rules. Not 24. |
| **Does 00's 200–300 hold?** | **Yes — for the situation catalogue, which is 291 non-refused rows.** It is **too high for `TemplateDefinition` records**, which the evidence puts at 66–133. The two numbers are different records and 00's sentence describes the first. |
| **`def.subject-work-record` = 14 rows / 3 schemas?** | **CORRECT, verified row by row.** academic 7, research 6, code 1. At full corpus the same recipe reaches **73 rows across 16 schemas with zero reversals anywhere** — the single most stable ordering fact in the corpus. |
| **The launch set** | **54 bindable rows, 3 cross-schema recipes, 28 definitions.** The other 13 recipes below are **entirely unbindable today** — 0 field rows between them. |
| **The one number that matters most** | `matter_anchor > artifact_kind` is now **55 rows across 12 schemas, zero reversals, and zero field rows.** It is the largest reuse fact in the product and it cannot produce a single folder at launch. |

**The single sentence.** The many-to-many is real and it is bigger than the catalogue has ever shown: **32 of
79 definitions serve two or more schemas and between them carry 212 of 276 rows** — but **23 of those 32 have
no bound row at all**, so what ships in wave 1 is 28 definitions serving 54 applicability rows, only 2 of
which cross a schema boundary, on 3 cross-schema recipes.

---

## 1. The corpus, re-derived

```
planning/domains/nodes/*.json                                 358 files
  ├─ schema rows                                               23
  └─ template rows                                            335
       ├─ refused (refuse_node: true)                          44   excluded
       └─ KEPT                                                291   the reuse population
            ├─ BINDABLE  (template.dimension_order non-empty)  54   6 schemas
            └─ GATED     (dimension_order == [])              237  17 schemas
```

Schemas declaring live `fields`: **6** — academic 5, code 4, college_applications 5, finance 4, photos 6,
research 6 = **30 live fields**.

> **The corpus moved while this pass ran.** At 2026-08-27T~13:00Z `finance` declared 5 live fields including
> `account_holder`; by 14:42Z that field had moved to `proposed_fields`, leaving 4. The live-field total is
> therefore **30, not 31**. Nothing else moved: 358/335/23/44/291/54/237 were identical at both reads, and
> `account_holder` was never a dimension token, so no count in this document is affected. Flagged because it
> proves the corpus is still being written and any number here has a timestamp attached to it.

**The binding contract holds without exception.** Across the 54 bindable rows there are **22 distinct
dimension tokens and 123 token uses**, and the number naming a field the row's own schema does not declare is
**0**. Every gated row's `dimension_order` is `[]` because its schema declares no fields — that is
`_CONTRACT` rule 8 meeting rule 10, not missing research.

### 1.1 Per-schema census

| Schema | live fields | kept rows | bindable | gated | refused | rows carrying a usable sequence |
|---|---:|---:|---:|---:|---:|---:|
| academic | 5 | 11 | **11** | 0 | 0 | 11 |
| business_operations | 0 | 22 | 0 | 22 | 2 | 22 |
| career | 0 | 6 | 0 | 6 | 0 | 6 |
| clinical_practice | 0 | 6 | 0 | 6 | 4 | 6 |
| code | 4 | 3 | **3** | 0 | 2 | 3 |
| college_applications | 5 | 5 | **5** | 0 | 0 | 5 |
| construction_property | 0 | 22 | 0 | 22 | 5 | 22 |
| creative | 0 | 32 | 0 | 32 | 9 | 26 |
| engineering | 0 | 19 | 0 | 19 | 5 | 19 |
| finance | 4 | 18 | **18** | 0 | 0 | 18 |
| government | 0 | 29 | 0 | 29 | 2 | 29 |
| hr | 0 | 11 | 0 | 11 | 0 | 11 |
| identity | 0 | 3 | 0 | 3 | 0 | **0** |
| law_practice | 0 | 28 | 0 | 28 | 8 | 27 |
| legal | 0 | 4 | 0 | 4 | 0 | **2** |
| logistics | 0 | 7 | 0 | 7 | 0 | 7 |
| manufacturing | 0 | 19 | 0 | 19 | 0 | 19 |
| medical | 0 | 3 | 0 | 3 | 0 | **0** |
| nonprofit | 0 | 4 | 0 | 4 | 6 | 4 |
| photos | 6 | 9 | **9** | 0 | 0 | 9 |
| research | 6 | 8 | **8** | 0 | 1 | 8 |
| resource_operations | 0 | 8 | 0 | 8 | 0 | 8 |
| retail_hospitality | 0 | 14 | 0 | 14 | 0 | 14 |
| **TOTAL** | **30** | **291** | **54** | **237** | **44** | **276** |

`54 = 11+3+5+18+9+8` exactly, and every bindable row sits on a field-bearing schema.

### 1.2 How the 237 gated rows were read, and what it is worth

The 54 bindable rows normalize **mechanically** from `dimension_order` through the field→role map in §1.3.
The 237 gated rows were **read in full by this pass** and each assigned one role sequence and a grade:

| Grade | Meaning | Rows |
|---|---|---:|
| **H** | the row states an ordered recommendation in its own words | **200** |
| **M** | hedged, conditional, split into two corpora, or written as a disjunction | **22** |
| **NONE** | the row positively recommends *no depth at all* — a finding, not a failed read | **8** |
| **UNK** | no order recoverable from the prose | **7** |

**276 of 291 kept rows (95%) carry a usable sequence**, across **21 of 23 schemas**.

The **8 NONE rows** are the whole of `identity` (`core-documents`, `credentials-passwords`, `immigration-visa`),
the whole of `medical` (`dependant-child-health`, `personal-health-records`, `wearable-health-exports`), and
`legal.estate-planning` and `legal.personal-legal-matters`. They refuse depth and say why:

> `identity.credentials-passwords`: *"A path such as Provider/Username/Recovery Codes would disclose both
> service usage and account-recovery capability even while file contents remain encrypted."*

The **7 UNK rows** are 6 `creative` rows (`3d-asset`, `brand-identity`, `music-session`, `print-production`,
`shoot-day-media`, `stock-asset-library`) plus **`law_practice.investigation`**, which names its two natural
axes only to ban both and never states a substitute.

**Two conventions, stated so they can be disagreed with.** (1) An optional level counts as present — the
recipe question is relative order, not depth. (2) A disjunctive level takes the first-named alternative,
unless both alternatives map to the same role. §10 lists the assignments most likely to be wrong.

**Prose evidence is weaker than field evidence on three counts and every table below splits them:** it is
conditional (most rows say "subject to R1c"), it is unbound (no prose level has been proved fillable), and it
passed through one reader. **Where a conclusion rests on prose alone this document says so in bold.**

### 1.3 The field→role map (mechanical, 22 tokens, 0 unmapped)

`work_type`·`artifact_type`·`record_type`·`application_document_type` → `artifact_kind` ·
`project`·`subject` → `subject_anchor` · `institution` → `issuing_org` · `school`·`lab` → `holder_institution` ·
`term`·`application_cycle` → `cycle_period` · `capture_year` → `capture_time` · `event` → `occasion_anchor` ·
`account_type` → `account_kind` · `target_university`·`venue` → `addressed_org` · `stage` → `lifecycle_stage` ·
`media_type` → `capture_kind` · `tax_year` → `scope_period` · `purpose` → `purpose_anchor` ·
`repository` → `repository_instance` · `location` → `place`.

### 1.4 Role census at 276 rows

| Role | rows | schemas | [F] rows | [F] schemas | | Role | rows | schemas | [F] rows | [F] schemas |
|---|---:|---:|---:|---:|---|---|---:|---:|---:|---:|
| `artifact_kind` | **228** | **20** | 40 | 5 | | `issuing_org` | 15 | 3 | 13 | 1 |
| `subject_anchor` | **89** | **16** | 17 | 3 | | `series_instalment` | 13 | 7 | 0 | 0 |
| `matter_anchor` | **82** | **13** | **0** | **0** | | `capture_time` | 10 | 3 | 8 | 1 |
| `site_anchor` | **52** | **10** | **0** | **0** | | `addressed_org` | 9 | 5 | 6 | 2 |
| `scope_period` | 45 | 11 | 2 | 1 | | `account_kind` | 5 | 1 | 5 | 1 |
| `lifecycle_stage` | 38 | 7 | 4 | 1 | | `standard_ref` | 3 | 2 | 0 | 0 |
| `component_anchor` | 35 | 9 | **0** | **0** | | `capture_kind` | 3 | 1 | 3 | 1 |
| `cycle_period` | 34 | 9 | 8 | 2 | | `purpose_anchor` | 2 | 2 | 1 | 1 |
| `occasion_anchor` | 25 | 11 | 6 | 1 | | `direction_role` | 2 | 2 | 0 | 0 |
| `holder_institution` | 24 | 7 | 8 | 2 | | `variant_axis` | 2 | 2 | 0 | 0 |
| `asset_instance` | 19 | 7 | **0** | **0** | | `channel_locus` | 2 | **1** | 0 | 0 |
| `counterparty_org` | 18 | 9 | **0** | **0** | | `repository_instance` | 1 | 1 | 1 | 1 |
| `org_unit` | 16 | 6 | **0** | **0** | | `provenance_role` | 1 | 1 | 0 | 0 |
| | | | | | | `place` | 1 | 1 | 1 | 1 |

**Six roles carrying 222 role-uses across 13, 10, 9, 9, 7 and 6 schemas have ZERO field rows**
(`matter_anchor`, `site_anchor`, `component_anchor`, `counterparty_org`, `asset_instance`, `org_unit`). That is
the whole reason the 54-row sample could not see most of what follows.

---

## 2. Every reuse recipe visible at 358 rows

A recipe is a dimension pattern recurring across rows from **different schemas**. Both readings are given,
because they answer different questions.

### 2.1 Recipes as adjacent role pairs — the full ranked table

`adj` = adjacent rows · `dom` = distinct schemas · `rel` = same order at any distance ·
`aREV`/`rREV` = rows placing the pair the other way, adjacently / at any distance ·
`F` = field-derived rows · `BIND` = rows bindable today.
Bar: 2+ schemas, and reverse under 25% of the pair's own count.

| # | Recipe (adjacent) | F | Fdom | P | Pdom | **TOT** | **DOM** | aREV | rREV | BIND | Bar |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | `matter_anchor > artifact_kind` | 0 | 0 | 55 | 12 | **55** | **12** | **0** | **0** | **0** | PASS |
| 2 | `subject_anchor > artifact_kind` | **14** | **3** | 18 | 8 | **32** | **11** | **0** | **0** | **14** | PASS |
| 3 | `artifact_kind > scope_period` | 0 | 0 | 29 | 7 | 29 | 7 | 14 | 15 | 0 | **CONTESTED** |
| 4 | `cycle_period > artifact_kind` | **4** | **2** | 22 | 5 | **26** | **7** | 1 | 1 | **4** | PASS |
| 5 | `lifecycle_stage > artifact_kind` | 0 | 0 | 20 | 3 | 20 | 3 | 2 | 2 | 0 | **CONTESTED** (§4.2) |
| 6 | `subject_anchor > lifecycle_stage` | 1 | 1 | 19 | 2 | 20 | 3 | 0 | 0 | 1 | PASS |
| 7 | `component_anchor > artifact_kind` | 0 | 0 | 18 | 7 | **18** | **7** | 1 | 1 | 0 | PASS |
| 8 | `site_anchor > matter_anchor` | 0 | 0 | 15 | 5 | **15** | **5** | **0** | **0** | 0 | PASS |
| 9 | `scope_period > artifact_kind` | 2 | 1 | 12 | 6 | 14 | 7 | 29 | 29 | 2 | **CONTESTED** |
| 10 | `subject_anchor > component_anchor` | 0 | 0 | 13 | 6 | **13** | **6** | 1 | 1 | 0 | PASS |
| 11 | `holder_institution > subject_anchor` | **4** | **2** | 7 | 3 | **11** | **5** | **0** | **0** | **4** | PASS |
| 12 | `occasion_anchor > artifact_kind` | 0 | 0 | 10 | 6 | **10** | **6** | **0** | **0** | 0 | PASS |
| 13 | `matter_anchor > lifecycle_stage` | 0 | 0 | 9 | 4 | **9** | **4** | **0** | **0** | 0 | PASS |
| 14 | `issuing_org > artifact_kind` | 8 | 1 | 0 | 0 | 8 | **1** | 1 | 1 | 8 | fail (1 schema) |
| 15 | `site_anchor > asset_instance` | 0 | 0 | 8 | 4 | **8** | **4** | **0** | **0** | 0 | PASS |
| 16 | `asset_instance > artifact_kind` | 0 | 0 | 6 | 4 | **6** | **4** | **0** | **0** | 0 | PASS |
| 17 | `series_instalment > artifact_kind` | 0 | 0 | 6 | 5 | **6** | **5** | **0** | **0** | 0 | PASS |
| 18 | `site_anchor > artifact_kind` | 0 | 0 | 6 | 4 | **6** | **4** | **0** | **0** | 0 | PASS (44/9 rel) |
| 19 | `site_anchor > component_anchor` | 0 | 0 | 6 | 4 | **6** | **4** | **0** | **0** | 0 | PASS |
| 20 | `counterparty_org > matter_anchor` | 0 | 0 | 5 | 4 | **5** | **4** | 0 | 1 | 0 | PASS |
| 21 | `counterparty_org > subject_anchor` | 0 | 0 | 5 | 2 | 5 | 2 | 0 | 0 | 0 | PASS |
| 22 | `org_unit > cycle_period` | 0 | 0 | 5 | 4 | 5 | 4 | 0 | 4 | 0 | CONTESTED (rel) |
| 23 | `subject_anchor > cycle_period` | 0 | 0 | 5 | 4 | 5 | 4 | 4 | 4 | 0 | CONTESTED |
| 24 | `subject_anchor > matter_anchor` | 0 | 0 | 5 | 3 | 5 | 3 | 0 | 0 | 0 | PASS |
| 25 | `account_kind > artifact_kind` | 4 | 1 | 0 | 0 | 4 | 1 | 1 | 1 | 4 | fail (1 schema) |
| 26 | `artifact_kind > org_unit` | 0 | 0 | 4 | 1 | 4 | 1 | 2 | 11 | 0 | fail (1 schema) |
| 27 | `capture_time > occasion_anchor` | 4 | 1 | 0 | 0 | 4 | 1 | 1 | 1 | 4 | fail (1 schema) |
| 28 | `cycle_period > subject_anchor` | 3 | 1 | 1 | 1 | 4 | 2 | 5 | 5 | 3 | CONTESTED |
| 29 | `holder_institution > cycle_period` | 3 | 1 | 1 | 1 | 4 | 2 | **0** | **0** | 3 | PASS |
| 30 | `matter_anchor > cycle_period` | 0 | 0 | 4 | 3 | 4 | 3 | 1 | 1 | 0 | CONTESTED |
| 31 | `matter_anchor > occasion_anchor` | 0 | 0 | 4 | 2 | 4 | 2 | 1 | 1 | 0 | CONTESTED |
| 32 | `subject_anchor > series_instalment` | 0 | 0 | 4 | 4 | **4** | **4** | **0** | **0** | 0 | PASS |
| 33 | `addressed_org > subject_anchor` | 1 | 1 | 2 | 2 | 3 | 3 | 1 | 1 | 1 | CONTESTED |
| 34 | `asset_instance > occasion_anchor` | 0 | 0 | 3 | 3 | 3 | 3 | 0 | 0 | 0 | PASS |
| 35 | `component_anchor > scope_period` | 0 | 0 | 3 | 2 | 3 | 2 | 0 | 0 | 0 | PASS |
| 36 | `counterparty_org > cycle_period` | 0 | 0 | 3 | 2 | 3 | 2 | 0 | 0 | 0 | PASS |
| 37 | `matter_anchor > component_anchor` | 0 | 0 | 3 | 2 | 3 | 2 | 0 | 0 | 0 | PASS |
| 38 | `asset_instance > matter_anchor` | 0 | 0 | 3 | 2 | 3 | 2 | 1 | 1 | 0 | CONTESTED |
| 39 | `component_anchor > series_instalment` | 0 | 0 | 3 | 2 | 3 | 2 | 1 | 1 | 0 | CONTESTED |
| 40 | `issuing_org > account_kind` | 3 | 1 | 0 | 0 | 3 | 1 | 0 | 0 | 3 | fail (1 schema) |
| 41 | `site_anchor > occasion_anchor` | 0 | 0 | 3 | 1 | 3 | 1 | 0 | 0 | 0 | fail (1 schema) |

**123 distinct adjacent pairs exist; 62 occur exactly once** (none cross-domain by construction). Pairs at
exactly 2 rows and 2 schemas, omitted above for length: `asset_instance > component_anchor` ·
`component_anchor > variant_axis` · `counterparty_org > artifact_kind` (**16 rows / 9 schemas at any
distance, 0 reversals** — adjacency badly under-reads this one) · `holder_institution > asset_instance` ·
`holder_institution > matter_anchor` · `holder_institution > org_unit` · `site_anchor > lifecycle_stage` ·
`site_anchor > org_unit` · `site_anchor > scope_period` · `occasion_anchor > component_anchor` (rev 1) ·
`org_unit > artifact_kind` (rev 4) · `subject_anchor > site_anchor` (rev 1).

### 2.2 THE SIXTEEN THAT CLEAR A 4-SCHEMA BAR

These clear 2+ schemas, ≥4 schemas, and reverse under 25%. **Ten have zero reversals anywhere in 276 rows.**

| Recipe | Plain English | Rows | Schemas | Rev | Bindable | Carried by |
|---|---|---:|---:|---:|---:|---|
| **1 · `matter_anchor > artifact_kind`** | the case, then the kind | **55** | **12** | **0** | **0** | **PROSE ONLY** |
| **2 · `subject_anchor > artifact_kind`** | the project-or-course, then the kind | **32** | **11** | **0** | **14** | **FIELD** + prose |
| **3 · `cycle_period > artifact_kind`** | the term-or-round, then the kind | **26** | **7** | 1 | **4** | **FIELD** + prose |
| **4 · `component_anchor > artifact_kind`** | the part-or-sheet, then the kind | **18** | **7** | 1 | 0 | **PROSE ONLY** |
| **5 · `site_anchor > matter_anchor`** | the place, then the case on it | **15** | **5** | **0** | 0 | **PROSE ONLY** |
| **6 · `subject_anchor > component_anchor`** | the design, then the part of it | **13** | **6** | 1 | 0 | **PROSE ONLY** |
| **7 · `holder_institution > subject_anchor`** | my institution, then my work | **11** | **5** | **0** | **4** | **FIELD** + prose |
| **8 · `occasion_anchor > artifact_kind`** | the meeting-or-event, then the kind | **10** | **6** | **0** | 0 | **PROSE ONLY** |
| **9 · `matter_anchor > lifecycle_stage`** | the case, then where it has got to | **9** | **4** | **0** | 0 | **PROSE ONLY** |
| **10 · `site_anchor > asset_instance`** | the facility, then the machine in it | **8** | **4** | **0** | 0 | **PROSE ONLY** |
| **11 · `asset_instance > artifact_kind`** | the machine-or-vehicle, then the kind | **6** | **4** | **0** | 0 | **PROSE ONLY** |
| **12 · `series_instalment > artifact_kind`** | the issue-or-baseline, then the kind | **6** | **5** | **0** | 0 | **PROSE ONLY** |
| **13 · `site_anchor > artifact_kind`** | the place, then the kind (44/9 at any distance) | **6** | **4** | **0** | 0 | **PROSE ONLY** |
| **14 · `site_anchor > component_anchor`** | the place, then the part of it | **6** | **4** | **0** | 0 | **PROSE ONLY** |
| **15 · `counterparty_org > matter_anchor`** | the client, then the engagement | **5** | **4** | 0 | 0 | **PROSE ONLY** |
| **16 · `subject_anchor > series_instalment`** | the work, then the instalment of it | **4** | **4** | **0** | 0 | **PROSE ONLY** |

**Thirteen of sixteen have zero field rows.** The launch six can bind three of them and nothing else.

#### Membership, by `domain_id`

**1 · `matter_anchor > artifact_kind` — 55 rows / 12 schemas / 68 rows-13 schemas at any distance / 0 reversals**
`business_operations` (3): `.compliance-audit` `.contract-administration` `.partnerships-bd` ·
`career` (1): `.employer-side-hiring` · `clinical_practice` (1): `.malpractice-incident` ·
`construction_property` (7): `.agency-listing` `.building-control` `.commercial-lease` `.construction-project`
`.tenancy-management` `.trade-job` `.variation-claim` · `engineering` (1): `.aerospace-airworthiness` ·
`government` (14): `.constituent-casework` `.diplomatic-consular` `.environmental-regulation`
`.grant-programme-administration` `.housing-authority` `.legislative-record` `.museum-collection`
`.permit-licensing` `.planning-application` `.professional-regulator` `.public-consultation`
`.public-health-administration` `.public-procurement` `.transport-authority` · `hr` (1): `.employee-relations` ·
`law_practice` (16): `.client-intake` `.conveyancing` `.court-filing-record` `.criminal-defence`
`.depositions-testimony` `.discovery` `.due-diligence` `.expert-materials` `.family-law` `.immigration-casework`
`.ip-prosecution` `.motions-and-briefs` `.opinions-advice` `.pro-bono` `.time-and-billing` `.transactional-deal` ·
`legal` (2): `.leases-agreements` `.practice-matter-file` · `logistics` (3): `.customs-export` `.last-mile-pod`
`.shipment` · `manufacturing` (3): `.hse-incident` `.nonconformance-capa` `.warranty-claim` ·
`retail_hospitality` (3): `.premises-licensing` `.returns-warranty` `.supplier-order`

**2 · `subject_anchor > artifact_kind` — 32 adjacent / 11 schemas; 73 rows / 16 schemas at any distance; 0 reversals anywhere**
`academic` (7): `.continuing-education` `.coursework` `.homeschool` `.online-course` `.standardized-testing`
`.study-abroad` `.teaching` · `business_operations` (5): `.market-research` `.policy-handbook`
`.project-delivery` `.retrospective-postmortem` `.support-operations` · `career` (5):
`.consulting-client-engagement` `.credentials-licenses` `.employment-records` `.portfolio-work-samples`
`.recruiting` · `code` (1): `.notebooks-experiments` · `creative` (2): `.printmaking-editions`
`.short-form-writing` · `government` (2): `.library-administration` `.policy-development` · `hr` (1):
`.dei-program` · `law_practice` (1): `.estates-administration` · `logistics` (1): `.route-dispatch` ·
`research` (6): `.conference-presentation` `.dataset-analysis` `.ethics-compliance` `.lab-notebook-protocols`
`.reading-library` `.thesis-dissertation` · `retail_hospitality` (1): `.menu-recipe-costing`

**3 · `cycle_period > artifact_kind` — 26 rows / 7 schemas / 1 reversal**
`academic` (2): `.k12-schooling` `.recommendation-letters-written` · `business_operations` (4):
`.budget-forecast` `.customer-account-management` `.product-roadmap` `.strategy-plan` ·
`college_applications` (2): `applications.scholarship-fellowship` `applications.undergraduate-packet` ·
`creative` (1): `.submission-query` · `government` (6): `.education-accreditation`
`.education-institution-governance` `.parks-public-lands` `.school-district-administration`
`.social-services-casework` `.statistical-programme` · `hr` (8): `.compensation-planning` `.engagement-survey`
`.onboarding-offboarding` `.org-design-headcount` `.payroll-benefits-administration` `.performance-cycle`
`.training-development` `.workforce-analytics` · `nonprofit` (3): `.fundraising-donor` `.member-association`
`.trade-union`
*Sole reversal:* `government.permit-licensing` (`matter > kind > cycle`).

**4 · `component_anchor > artifact_kind` — 18 rows / 7 schemas / 1 reversal**
`business_operations` (1): `.product-requirements` · `construction_property` (1): `.subcontract` ·
`engineering` (8): `.change-order` `.civil-structural` `.commissioning-handover` `.drawing-package`
`.process-plant-design` `.risk-analysis-fmea` `.simulation-analysis` `.verification-validation` ·
`government` (2): `.archives-recordkeeping` `.elections-administration` · `manufacturing` (4):
`.production-planning` `.spare-parts` `.supplier-qualification` `.tooling-fixture` · `resource_operations` (1):
`.forestry-records` · `retail_hospitality` (1): `.stocktake`
*Sole reversal:* `construction_property.site-health-safety`.

**5 · `site_anchor > matter_anchor` — 15 rows / 5 schemas / 0 reversals**
`construction_property` (7): `.agency-listing` `.building-control` `.commercial-lease` `.inventory-inspection`
`.materials-delivery` `.plant-hire` `.tenancy-management` · `government` (4): `.diplomatic-consular`
`.environmental-regulation` `.housing-authority` `.planning-application` · `law_practice` (1): `.conveyancing` ·
`manufacturing` (1): `.hse-incident` · `retail_hospitality` (2): `.premises-licensing` `.returns-warranty`

**6 · `subject_anchor > component_anchor` — 13 rows / 6 schemas / 1 reversal**
`business_operations` (1): `.product-requirements` · `creative` (1): `.ad-campaign` · `engineering` (8):
`.cad-model` `.change-order` `.civil-structural` `.industrial-design` `.pcb-layout` `.process-plant-design`
`.risk-analysis-fmea` `.simulation-analysis` · `government` (1): `.archives-recordkeeping` · `law_practice` (1):
`.contract-negotiation` · `manufacturing` (1): `.production-planning`

**7 · `holder_institution > subject_anchor` — 11 rows / 5 schemas / 0 reversals**
`academic` (3): `.continuing-education` `.online-course` `.study-abroad` · `business_operations` (5):
`.market-research` `.meeting-record` `.policy-handbook` `.product-requirements` `.product-roadmap` ·
`career` (1): `.employment-records` · `nonprofit` (1): `.religious-institution` · `research` (1):
`.lab-notebook-protocols`

**8 · `occasion_anchor > artifact_kind` — 10 rows / 6 schemas / 0 reversals**
`business_operations` (3): `.board-governance` `.go-to-market` `.meeting-record` · `clinical_practice` (1):
`.case-conference` · `construction_property` (1): `.inventory-inspection` · `law_practice` (1):
`.hearing-transcripts` · `resource_operations` (1): `.fisheries-catch` · `retail_hospitality` (3):
`.bookings-reservations` `.pos-reporting` `.store-operations`

**9 · `matter_anchor > lifecycle_stage` — 9 rows / 4 schemas / 0 reversals**
`business_operations` (1): `.procurement-sourcing` · `construction_property` (3): `.final-account`
`.plant-hire` `.quote-estimate` · `government` (4): `.defence-veterans` `.international-development`
`.public-records-foi` `.regulatory-rulemaking` · `retail_hospitality` (1): `.catering-contract`

**10 · `site_anchor > asset_instance` — 8 rows / 4 schemas / 0 reversals**
`business_operations` (1): `.facilities-workplace` · `manufacturing` (2): `.asset-register` `.tooling-fixture` ·
`resource_operations` (4): `.fisheries-catch` `.mining-operations` `.oil-gas-operations`
`.renewable-generation` · `retail_hospitality` (1): `.pos-reporting`

**11 · `asset_instance > artifact_kind` — 6 rows / 4 schemas / 0 reversals**
`business_operations` (2): `.facilities-workplace` `.it-asset-inventory` · `logistics` (1): `.fleet-vehicle` ·
`manufacturing` (2): `.calibration-record` `.inspection-record` · `resource_operations` (1): `.grid-connection`

**12 · `series_instalment > artifact_kind` — 6 rows / 5 schemas / 0 reversals**
`creative` (1): `.podcast-episode` · `engineering` (2): `.embedded-firmware` `.material-specification` ·
`law_practice` (1): `.appeals` · `nonprofit` (1): `.religious-institution` · `retail_hospitality` (1):
`.product-catalogue`

**13 · `site_anchor > artifact_kind` — 6 adjacent / 4 schemas; 44 rows / 9 schemas at any distance; 0 reversals**
`construction_property` (3): `.block-management` `.site-health-safety` `.site-survey` · `hr` (1):
`.workplace-health-safety` · `logistics` (1): `.warehouse-ops` · `manufacturing` (1): `.work-instruction`

**14 · `site_anchor > component_anchor` — 6 rows / 4 schemas / 0 reversals**
`construction_property` (1): `.snagging-defects` · `manufacturing` (2): `.energy-audit` `.spare-parts` ·
`resource_operations` (2): `.farm-records` `.forestry-records` · `retail_hospitality` (1): `.food-safety`

**15 · `counterparty_org > matter_anchor` — 5 rows / 4 schemas / 0 adjacent reversals**
`business_operations` (2): `.contract-administration` `.partnerships-bd` · `construction_property` (1):
`.trade-job` · `logistics` (1): `.shipment` · `retail_hospitality` (1): `.supplier-order`

**16 · `subject_anchor > series_instalment` — 4 rows / 4 schemas / 0 reversals**
`creative` (1): `.periodical-issue` · `engineering` (1): `.material-specification` · `nonprofit` (1):
`.religious-institution` · `retail_hospitality` (1): `.product-catalogue`

### 2.3 Seven more clear the 2-schema bar at 2–3 schemas

Real, but one schema decision from collapsing.

| Recipe | Rows | Schemas | Rev | Schemas named |
|---|---:|---:|---:|---|
| `subject_anchor > lifecycle_stage` | 20 | 3 | 0 | creative (17), engineering (2), research (1 · **field**) |
| `counterparty_org > subject_anchor` | 5 | 2 | 0 | career (1), creative (4) |
| `subject_anchor > matter_anchor` | 5 | 3 | 0 | construction_property, law_practice, manufacturing (3) |
| `holder_institution > cycle_period` | 4 | 2 | 0 | academic (3 · **field**), nonprofit (1) |
| `asset_instance > occasion_anchor` | 3 | 3 | 0 | manufacturing, resource_operations, retail_hospitality |
| `counterparty_org > cycle_period` | 3 | 2 | 0 | business_operations, government (2) |
| `component_anchor > scope_period` | 3 | 2 | 0 | manufacturing, construction_property |

### 2.4 Recipes as FULL SEQUENCES — 23 recur across two or more schemas

The pair table is the strongest evidence, but the product ships whole recipes. Twenty-three *exact* role
sequences are used by rows from more than one schema; 127 sequences are confined to one schema and are
single-domain templates, not reuse.

| Rows | Schemas | F | Sequence | Schemas named |
|---:|---:|---:|---|---|
| **22** | **10** | 0 | `matter_anchor > artifact_kind` | career, clinical_practice, construction_property, engineering, government, hr, law_practice, legal, logistics, manufacturing |
| **13** | 2 | 0 | `subject_anchor > lifecycle_stage > artifact_kind` | creative, engineering |
| **11** | 4 | 0 | `site_anchor > matter_anchor > artifact_kind` | construction_property, government, manufacturing, retail_hospitality |
| **9** | **7** | 4 | `subject_anchor > artifact_kind` | academic, code, creative, government, hr, law_practice, research |
| **7** | 4 | 4 | `holder_institution > subject_anchor > artifact_kind` | academic, business_operations, career, research |
| 5 | 3 | 0 | `artifact_kind > scope_period` | clinical_practice, law_practice, logistics |
| 4 | 2 | 1 | `cycle_period > artifact_kind` | academic, hr |
| 4 | 3 | 0 | `site_anchor > artifact_kind > scope_period` | construction_property, hr, logistics |
| 3 | 2 | 0 | `org_unit > cycle_period > artifact_kind` | business_operations, hr |
| 3 | 3 | 0 | `counterparty_org > matter_anchor > artifact_kind` | business_operations, construction_property, logistics |
| 3 | 3 | 0 | `subject_anchor > matter_anchor > artifact_kind` | construction_property, law_practice, manufacturing |
| 3 | 2 | 2 | `artifact_kind` (single level) | finance, law_practice |
| 2 | 2 | 1 | `holder_institution > cycle_period > artifact_kind` | academic, nonprofit |
| 2 | 2 | 0 | `counterparty_org > cycle_period > artifact_kind` | business_operations, government |
| 2 | 2 | 0 | `counterparty_org > artifact_kind > scope_period` | business_operations, law_practice |
| 2 | 2 | 1 | `addressed_org > subject_anchor > artifact_kind` | career, research |
| 2 | 2 | 0 | `site_anchor > scope_period > artifact_kind` | construction_property, resource_operations |
| 2 | 2 | 1 | `subject_anchor > lifecycle_stage` | creative, research |
| 2 | 2 | 0 | `subject_anchor > series_instalment > artifact_kind` | engineering, retail_hospitality |
| 2 | 2 | 0 | `subject_anchor > component_anchor > series_instalment` | engineering, law_practice |
| 2 | 2 | 0 | `site_anchor > component_anchor > scope_period > artifact_kind` | manufacturing, retail_hospitality |
| 2 | 2 | 0 | `site_anchor > component_anchor > artifact_kind` | manufacturing, resource_operations |
| 2 | 2 | 0 | `site_anchor > asset_instance > occasion_anchor > artifact_kind` | resource_operations, retail_hospitality |

**`matter_anchor > artifact_kind` used verbatim, with no other level, by 22 rows in 10 schemas is the single
strongest reuse fact in the corpus.** Twenty-two situations in ten unrelated professions all reduce to "the
case, then the kind of document" — and not one of them can build a folder today.

---

## 3. What survives from the earlier passes, and what does not

**Nothing that was previously accepted dissolves at 358 rows.** Every claimed recipe grew or held.

| Claim | Where from | At 291 kept rows | Verdict |
|---|---|---|---|
| Recipe 1 · `subject_anchor > artifact_kind` | 37/41 (14 rows / 3 schemas) | **32 adjacent / 11 schemas; 73 / 16 at any distance; 0 reversals in 276 rows** | **HOLDS, strongest in corpus** |
| Recipe 2 · `holder_institution > subject_anchor` | 41 (4 rows / 2 schemas, "if you want one cut, cut Recipe 2") | **11 rows / 5 schemas / 0 reversals** | **HOLDS. Do not cut it.** The cut advice remains an artifact of a 6-schema sample. |
| Recipe 3 · `cycle_period > artifact_kind` | 41 (4 rows / 2 schemas) | **26 rows / 7 schemas / 1 reversal** | **HOLDS, grew 6×** |
| Recipe 4 · `matter_anchor > artifact_kind` | 42 §4.1 (55 rows / 11 domains) | **55 rows / 12 schemas / 0 reversals** | **HOLDS. Row count identical, one more schema.** |
| Doc 43's 11-recipe freeze set | 43 §4.2 | **all 11 still clear their bar** | **HOLDS in full** |
| `artifact_kind ↔ scope_period` | 42 F2 / 43 §4.4A, "not a recipe" | **29 vs 14** (was 32 vs 13) — ratio softened from 2.5:1 to 2.1:1, both field rows still on the minority side | **STILL NOT A RECIPE** |
| `lifecycle_stage > artifact_kind` | 42 F3 / 43 §4.4B, OPEN | **20 rows / 3 schemas for; 2 rows / 1 schema against, and the 2 against are the only BOUND rows** | **STILL OPEN — see §4.2** |
| `def.subject-work-record` = 14 rows / 3 schemas | 37 §Executive-3 | **VERIFIED EXACTLY**: academic 7, research 6, code 1 | **CORRECT** |
| 24 definitions / 54 bindings at launch | 37 §Executive-2 | **28 definitions / 54 applicability rows** at exact role sets | **CORRECTED upward** |
| "recipes should reach ~5–10 at full size" | 41 §7.8 | **16 clear a 4-schema bar; 23 clear 2 schemas** | **TOO LOW** |

### 3.1 Three things that CHANGED direction since doc 43's 270-row snapshot

1. **`counterparty_org > subject_anchor` was recorded as a single-schema failure (5 rows / 1 domain). It now
   passes at 5 rows / 2 schemas** — `career.consulting-client-engagement` joins the four `creative` rows
   (`.client-engagement` `.commissioned-shoot` `.content-marketing` `.motion-graphics`). *This rests on reading
   career's "client first, then the engagement" as counterparty-then-subject; §10.1.*
2. **Three pairs held at exactly 3 schemas now reach 4 or more and move into the freeze set:**
   `subject_anchor > component_anchor` (10/3 → 13/6), `matter_anchor > lifecycle_stage` (8/3 → 9/4),
   `site_anchor > asset_instance` (8/3 → 8/4). A fourth, `subject_anchor > series_instalment`, reaches 4/4.
3. **`direction_role` — named and NOT adopted in doc 43 at 1 row / 1 domain — now reaches 2 rows / 2 schemas**
   (`clinical_practice.referral-correspondence`, `law_practice.regulatory-submission`). It clears the same
   2-domain bar every adopted role clears. *It clears it on my reading of law_practice's "shallow
   outbound/inbound split"; §10.2. It is 2 rows and should not carry a recipe, but it should stop being
   described as single-domain.*

### 3.2 One thing that got WEAKER

`asset_instance > artifact_kind` was 6 rows / 5 domains in doc 43 and is **6 rows / 4 schemas** here. It still
clears the bar. The difference is one row's assignment, not new evidence.

### 3.3 The forbidden org merge — refused again, and now refuted a third way

Four org roles remain distinct: `holder_institution` (24 rows / 7 schemas), `counterparty_org` (18 / 9),
`issuing_org` (15 / 3), `addressed_org` (9 / 5). Merging them into one `ORG` would produce an attractive
`ORG > artifact_kind` and `ORG > subject_anchor`, and both are illusions:

- `holder_institution > subject_anchor` **already clears the bar unaided at 11 rows / 5 schemas.** The merge
  buys nothing it does not already have.
- `counterparty_org > subject_anchor` (5/2) and `addressed_org > subject_anchor` (3/3) point in the same
  direction but at **different objects**, and the corpus says so in its own words:
  > `creative.submission-query`: *"its organizing anchor is an ADDRESSEE IN A SUBMITTED-TO ROLE and `client`
  > is a COMMISSIONING role. A literary agent, a magazine editor, a juror and a festival programmer have
  > commissioned nothing; recording them as `client` would assert a relationship that does not exist and
  > would fuse a rejection with a paid job."*
- **New this pass:** the merge produces an illegal self-repeat in `business_operations.partnerships-bd`, whose
  own sequence is `holder_institution > counterparty_org > matter_anchor > artifact_kind` — two different org
  roles in one path. 00 forbids a template that would *"repeat a parent dimension."* The corpus refuses the
  merge structurally, not just semantically. `business_operations.corporate-regulatory-filings`
  (`holder_institution > addressed_org > …`) does the same.

**Refuse the merge.** 00: *"The system must separate roles that happen to contain the same entity type."*

---

## 4. The two that are still not recipes

### 4.1 `artifact_kind ↔ scope_period` — one role doing two jobs

| Direction | Rows | Schemas | Field rows |
|---|---:|---:|---:|
| `artifact_kind > scope_period` — period is a trailing discriminator | **29** | 7 | 0 |
| `scope_period > artifact_kind` — period IS the record's identity | 14 | 7 | **2** |

Both bound rows sit on the minority side and both argue it: `finance.tax-filings` — *"it cannot scatter a
filing, because the filing IS the year"*; `finance.payroll-received`. Against them, all twelve
`law_practice` rows in the majority column put the period last under function, and five of the six
`resource_operations` rows put a reporting period above record type.

Majority (29): `business_operations` `.project-delivery` `.retrospective-postmortem` `.risk-register`
`.support-operations` `.vendor-management` · `clinical_practice` `.patient-chart` `.pharmacy-operations`
`.practice-administration` · `construction_property` `.block-management` `.site-survey` `.subcontract` ·
`government` `.archives-recordkeeping` `.transport-authority` · `hr` `.workplace-health-safety` ·
`law_practice` `.appeals` `.client-intake` `.conflicts-check` `.conveyancing` `.corporate-secretarial`
`.depositions-testimony` `.discovery` `.family-law` `.immigration-casework` `.motions-and-briefs` `.pro-bono`
`.time-and-billing` · `logistics` `.driver-compliance` `.fleet-vehicle` `.warehouse-ops`.
Minority (14): `business_operations.corporate-regulatory-filings` · `construction_property.site-diary` ·
`finance.payroll-received` `finance.tax-filings` · `government.emergency-management` ·
`manufacturing.energy-audit` `.environmental-compliance` · `resource_operations.farm-records`
`.mining-operations` `.oil-gas-operations` `.renewable-generation` `.utility-metering-billing` ·
`retail_hospitality.ecommerce-ops` `.food-safety`.

**`scope_period` is doing two jobs and until they separate this is not a recipe.** The split is legible:
*a period a record is measured over* versus *a period under which a function repeats*.

### 4.2 `lifecycle_stage > artifact_kind` — the count says yes, the bound rows say no

| Direction | Rows | Schemas | Field rows | Consecutive `subject > stage > kind` |
|---|---:|---:|---:|---:|
| `lifecycle_stage > artifact_kind` — 00 §5.4's original order | **20** | 3 (creative 14, government 4, engineering 2) | **0** | **16 rows / 2 schemas** |
| `artifact_kind > lifecycle_stage` — the brief's §4-B flip | 2 | 1 (research) | **2** | 2 rows / 1 schema |

00 §5.4's chain `project → stage → artifact type` — which doc 37 recorded as realized by *"not one landed
row"* — is realized as a **consecutive three-level chain by 16 rows across `creative` (14) and `engineering`
(2)**, and 13 of those use it as their *entire* sequence
(`creative.architectural-visualisation` `.book-manuscript` `.client-engagement` `.content-marketing`
`.deliverable-handoff` `.exhibition` `.fashion-collection` `.film-production` `.game-art-asset`
`.motion-graphics` `.publishing-title` `.sound-design` `.translation-project` `.uiux-product-design`;
`engineering.invention-disclosure` `.stage-gate-review`). By the brief's own 2-schema bar **00's original
order clears it and the flip does not** — but the only *bound* rows on the pair are `research`'s two and they
go the other way.

**Recommendation: scope the §4-B flip to `research` and do not generalize it.** Ship
`subject_anchor > lifecycle_stage > artifact_kind` as a definition with **both orders as candidates** — which
is exactly what `DimensionOrder` is for, and which makes this a settled UX question instead of an open
design one. See §5.1.

---

## 5. The definition count

### 5.1 The code decides the shape of the question

`src/tree_design/templates.py:333-368` enforces two rules that change how definitions must be counted:

* **All candidate orders of one definition must cover the same role set** — *"an order that drops or adds a
  role is a different RECIPE"* (`templates.py:353-360`).
* **A definition with more than one dimension must offer at least two candidate orders** — one candidate is
  *"a single `dimensions` tuple wearing a new field name"* (`templates.py:361-368`).

**A `TemplateDefinition` is therefore a role SET plus two or more orderings of it, not a sequence.** Rows that
share a role set but disagree on order share **one** definition and contribute a candidate order each. This
resolves several things doc 37 recorded as contested:

| Rows disagreeing on order | Doc 37's reading | Under the built model |
|---|---|---|
| `photos.camera-events` (`capture_year > event`) vs `photos.family-archive` (`event > capture_year`) | "contested, 4 for / 1 against" | **one definition**, role set `{capture_time, occasion_anchor}`, two candidate orders |
| `finance.loans-mortgage` (`account_type > record_type`) vs `finance.small-business-bookkeeping` (`record_type > account_type`) | "contested" | **one definition**, `{account_kind, artifact_kind}`, two orders |
| `finance.receipts-expenses` (`institution > record_type`) vs `travel.bookings-confirmations` (`record_type > institution`) | "contested, 11 for / 1 against" | **one definition**, `{issuing_org, artifact_kind}`, two orders |
| `applications.undergraduate-packet` vs `applications.scholarship-fellowship` | "UNRESOLVED" | **one definition**, `{addressed_org, cycle_period, artifact_kind}`, two orders |

**This is the design working.** Ordering is a runtime choice; a disagreement about order between two rows is
not a conflict to adjudicate, it is the second candidate order.

### 5.2 The count, under three explicit rules

`TemplateApplicability` does **not** require every definition role to be bound (`templates.py:397-452` checks
only that bound fields sit inside `allowed_fields`), so a definition may carry an optional role a given
schema cannot fill. How many optional roles a definition may carry is a policy choice, so all three are given.

| Rule | Definitions for 276 rows | Cross-schema | Rows they serve | Single-schema |
|---|---:|---:|---:|---:|
| **cap 0** — a definition carries exactly the roles its rows use | **133** | 30 | 142 | 103 |
| **cap 1** — one optional role permitted | **79** | **32** | **212** | 47 |
| **cap 2** — two optional roles permitted | **66** | 28 | 224 | 38 |

For reference, counted as rigid sequences rather than role sets: 150 / 94 / 83 under the same three caps.

**Recommendation: cap 1.** It is where reuse peaks (32 cross-schema definitions covering 212 of 276 rows) and
it keeps a definition honest — one optional level is a level the *other* bound rows demonstrably use, whereas
cap 2 starts absorbing 1-role rows into 3-role definitions whose extra levels no bound row can fill, which is
00's *"produce empty branches when tested against the accepted group"* failure waiting to happen.

**Add 15 for the rows carrying no sequence.** The 8 NONE rows and 7 UNK rows still need applicability rows —
the NONE rows need a *shallow protected packet* definition with no dimensions, which the record model cannot
express today (`DimensionOrder` requires at least one dimension, `templates.py:272-275`). **That is a gap: 8
rows across 3 schemas positively recommend zero depth and there is no record shape for them.**

### 5.3 Does 00's 200–300 hold?

00: *"The product should eventually maintain a library of roughly **200–300 domain-specific templates**,
covering common organizational situations… Each template should define the domain's allowed fact fields,
detection signals, recommended folder dimensions, preferred dimension order, optional branch patterns,
privacy rules, and validation constraints."*

The properties 00 lists split across the four records: *allowed fact fields* and *detection signals* are
`TemplateApplicability`; *recommended folder dimensions*, *preferred order*, *optional branch patterns* and
*validation constraints* are `TemplateDefinition`; *privacy rules* are the fragment's `privacy_floor`. **00's
"template" is the situation-shaped record — the applicability row — not the definition.**

| What is counted | Evidence at 358 rows | 00's 200–300 |
|---|---:|---|
| Organizational situations / `TemplateApplicability` rows | **291** (+23 schema anchors = 314) | **CONFIRMED — dead centre of the range** |
| `TemplateDefinition` records | **66–133** (79 recommended) | **Too high by roughly 2–4×** |
| `TemplateFragment` records | ≈ 16–23 (the freeze set) | far too high |

**The evidence supports 200–300, but for the wrong record.** Say "291 situations, 79 definitions, ~16
fragments" and the number stops being ambiguous.

---

## 6. Reuse ratio per definition — which definitions earn their keep

At cap 1, **32 definitions serve two or more schemas and carry 212 of 276 rows (77%)**; 47 definitions serve
one schema and carry 64 rows. **Twenty-three of the 32 have no bound row at all**; only 9 have a field-derived
half, and they are the ones with a non-zero `F` column below. Ranked by schema reach:

| Rows | Schemas | F | Role set | Schemas served |
|---:|---:|---:|---|---|
| **35** | **14** | 4 | `{subject_anchor, matter_anchor, artifact_kind}` | academic, career, clinical_practice, code, construction_property, creative, engineering, government, hr, law_practice, legal, logistics, manufacturing, research |
| **14** | **6** | **8** | `{holder_institution, subject_anchor, cycle_period, artifact_kind}` | academic, business_operations, career, government, nonprofit, research |
| **16** | 5 | 0 | `{site_anchor, matter_anchor, occasion_anchor, artifact_kind}` | construction_property, government, law_practice, manufacturing, retail_hospitality |
| 7 | 5 | 0 | `{site_anchor, matter_anchor, scope_period, artifact_kind}` | construction_property, hr, law_practice, logistics, resource_operations |
| 6 | 5 | 0 | `{site_anchor, asset_instance, component_anchor, artifact_kind}` | business_operations, construction_property, engineering, manufacturing, resource_operations |
| **20** | 4 | 2 | `{counterparty_org, subject_anchor, lifecycle_stage, artifact_kind}` | career, creative, engineering, research |
| **16** | 4 | **11** | `{issuing_org, scope_period, artifact_kind}` | clinical_practice, finance, law_practice, logistics |
| 10 | 4 | 0 | `{subject_anchor, component_anchor, scope_period, artifact_kind}` | business_operations, engineering, government, logistics |
| 5 | 4 | 3 | `{addressed_org, subject_anchor, cycle_period, artifact_kind}` | career, college_applications, creative, research |
| 4 | 4 | 0 | `{site_anchor, counterparty_org, matter_anchor, artifact_kind}` | business_operations, construction_property, logistics, retail_hospitality |
| 12 | 3 | 0 | `{asset_instance, matter_anchor, scope_period, artifact_kind}` | government, law_practice, logistics |
| 8 | 3 | 0 | `{org_unit, cycle_period, subject_anchor, artifact_kind}` | business_operations, government, hr |
| 5 | 3 | 0 | `{component_anchor, occasion_anchor, artifact_kind}` | clinical_practice, engineering, government |
| 4 | 3 | 0 | `{matter_anchor, lifecycle_stage, series_instalment}` | construction_property, law_practice, retail_hospitality |
| 3 | 3 | 2 | `{capture_time, subject_anchor}` | code, creative, photos |
| 3 | 3 | 0 | `{subject_anchor, series_instalment, artifact_kind}` | creative, engineering, retail_hospitality |
| 6 | 2 | 3 | `{holder_institution, cycle_period, artifact_kind}` | academic, hr |
| 4 | 2 | 2 | `{matter_anchor, artifact_kind}` | finance, law_practice |
| 3 | 2 | 0 | `{org_unit, counterparty_org, cycle_period, artifact_kind}` | business_operations, government |
| 3 | 2 | 0 | `{holder_institution, subject_anchor, occasion_anchor, artifact_kind}` | business_operations, career |
| 3 | 2 | 0 | `{holder_institution, asset_instance, artifact_kind}` | business_operations, manufacturing |
| 3 | 2 | 1 | `{subject_anchor, lifecycle_stage, provenance_role}` | creative, research |
| 3 | 2 | 0 | `{subject_anchor, component_anchor, series_instalment}` | engineering, law_practice |
| 3 | 2 | 0 | `{subject_anchor, matter_anchor, cycle_period, artifact_kind}` | government, nonprofit |
| 2 | 2 | 0 | `{counterparty_org, scope_period, artifact_kind}` | business_operations, law_practice |
| 2 | 2 | 0 | `{site_anchor, subject_anchor, lifecycle_stage, component_anchor}` | construction_property, creative |
| 2 | 2 | 0 | `{matter_anchor, component_anchor, scope_period, artifact_kind}` | construction_property, manufacturing |
| 2 | 2 | 0 | `{subject_anchor, component_anchor, variant_axis, artifact_kind}` | creative, engineering |
| 2 | 2 | 0 | `{site_anchor, org_unit, cycle_period, artifact_kind}` | government, manufacturing |
| 2 | 2 | 0 | `{site_anchor, component_anchor, scope_period, artifact_kind}` | manufacturing, retail_hospitality |
| 2 | 2 | 0 | `{site_anchor, subject_anchor, artifact_kind}` | manufacturing, retail_hospitality |
| 2 | 2 | 0 | `{site_anchor, asset_instance, occasion_anchor, artifact_kind}` | resource_operations, retail_hospitality |

**The winner is not `def.subject-work-record`.** It is the role set that fuses the subject and the matter
anchors under one function level — **35 rows across 14 of 23 schemas** — and it is the clearest possible
statement of the many-to-many. Second is the academic/research spine at 14 rows / 6 schemas, which is the
only high-reach definition with a substantial bound half (8 field rows).

### 6.1 Verifying `def.subject-work-record`

**The claim of 14 rows across 3 schemas is CORRECT.** Bindable rows placing `subject_anchor` above
`artifact_kind` at any distance: **14**, in `academic` (7), `research` (6), `code` (1) —
`academic.continuing-education` `.coursework` `.homeschool` `.online-course` `.standardized-testing`
`.study-abroad` `.teaching`; `research.conference-presentation` `.dataset-analysis` `.ethics-compliance`
`.lab-notebook-protocols` `.reading-library` `.thesis-dissertation`; `code.notebooks-experiments`.

Two things to add to the claim:
1. **At full corpus it is 73 rows across 16 schemas with zero reversals anywhere in 276 rows.** No other
   ordering fact in this product is that stable.
2. **The bound 14 span only two underlying field pairs** — `subject`/`work_type` (academic) and
   `project`/`artifact_type` (research, code). The brief's own caveat that it "might really span two domains
   not three" is correct *for the bound half*, and is dissolved by the prose half, which adds 13 further
   schemas sharing no field with any of them.

---

## 7. The launch set — what actually ships

**54 bindable rows in 6 schemas.** This is a **closed** evidence base: every schema that declares fields is
already fully landed (11+3+5+18+9+8 = 54, gated = 0 for all six), so no future row can add a bound dimension.

### 7.1 Every ordering fact the launch set can express

| Rows | Schemas | Recipe | Reuse? |
|---:|---:|---|---|
| **14** | **3** | `subject_anchor > artifact_kind` | **CROSS-SCHEMA** — academic, code, research |
| 8 | 1 | `issuing_org > artifact_kind` | finance only |
| **4** | **2** | `holder_institution > subject_anchor` | **CROSS-SCHEMA** — academic, research |
| **4** | **2** | `cycle_period > artifact_kind` | **CROSS-SCHEMA** — academic, college_applications |
| 4 | 1 | `capture_time > occasion_anchor` | photos only |
| 4 | 1 | `account_kind > artifact_kind` | finance only |
| 3 | 1 | `holder_institution > cycle_period` | academic only |
| 3 | 1 | `issuing_org > account_kind` | finance only |
| 3 | 1 | `cycle_period > subject_anchor` | academic only |
| 2 | 1 | `capture_kind > capture_time` | photos only |
| 2 | 1 | `addressed_org > artifact_kind` | college_applications only |
| 2 | 1 | `artifact_kind > lifecycle_stage` | research only |
| 2 | 1 | `scope_period > artifact_kind` | finance only |
| 1 each | 1 | `artifact_kind > account_kind` · `artifact_kind > issuing_org` · `artifact_kind > addressed_org` · `occasion_anchor > capture_time` · `occasion_anchor > capture_kind` · `addressed_org > subject_anchor` · `issuing_org > scope_period` · `holder_institution > artifact_kind` · `subject_anchor > addressed_org` · `addressed_org > lifecycle_stage` · `addressed_org > cycle_period` · `occasion_anchor > place` · `subject_anchor > lifecycle_stage` · `repository_instance > artifact_kind` | one schema each |

**Three of the sixteen full-corpus recipes are bindable. Thirteen are not — they have zero field rows between
them.** Everything `matter_anchor`, `site_anchor`, `component_anchor`, `asset_instance`, `counterparty_org`,
`org_unit` and `series_instalment` touches is wave 2 or later.

### 7.2 The 28 launch definitions (exact role sets, cap 0)

| Rows | Sch | Role set | Candidate orders present in the corpus | Rows |
|---:|---:|---|---|---|
| 9 | 1 | `{issuing_org, artifact_kind}` | `issuing_org > artifact_kind` · `artifact_kind > issuing_org` | finance `.cap-table-equity` `.crypto-assets` `.hoa-residents-association` `.insurance-healthcare` `.insurance-personal` `.receipts-expenses` `.student-financial-aid` `.subscriptions-utilities`, `travel.bookings-confirmations` |
| **4** | **2** | `{holder_institution, subject_anchor, artifact_kind}` | `holder_institution > subject_anchor > artifact_kind` | academic `.continuing-education` `.online-course` `.study-abroad`; `research.lab-notebook-protocols` |
| **4** | **3** | `{subject_anchor, artifact_kind}` | `subject_anchor > artifact_kind` | `academic.standardized-testing`; `code.notebooks-experiments`; research `.ethics-compliance` `.reading-library` |
| 4 | 1 | `{capture_time, occasion_anchor}` | `capture_time > occasion_anchor` · `occasion_anchor > capture_time` | photos `.camera-events` `.drone-captures` `.family-archive` `.home-video` |
| 3 | 1 | `{issuing_org, account_kind, artifact_kind}` | `issuing_org > account_kind > artifact_kind` | finance `.insurance-corporate` `.investment-brokerage` `.personal-records` |
| 2 | 1 | `{account_kind, artifact_kind}` | `account_kind > artifact_kind` · `artifact_kind > account_kind` | finance `.loans-mortgage` `.small-business-bookkeeping` |
| 2 | 1 | `{addressed_org, artifact_kind}` | `addressed_org > artifact_kind` | `applications.graduate-professional` `.k12-admission` |
| 2 | 1 | `{addressed_org, cycle_period, artifact_kind}` | `addressed_org > cycle_period > artifact_kind` · `cycle_period > artifact_kind > addressed_org` | `applications.scholarship-fellowship` `.undergraduate-packet` |
| 2 | 1 | `{artifact_kind}` | `artifact_kind` | finance `.household-property` `.vehicle-records` |
| 2 | 1 | `{cycle_period, subject_anchor, artifact_kind}` | `cycle_period > subject_anchor > artifact_kind` | academic `.homeschool` `.teaching` |
| 2 | 1 | `{subject_anchor, lifecycle_stage, artifact_kind}` | `subject_anchor > artifact_kind > lifecycle_stage` | research `.dataset-analysis` `.thesis-dissertation` |
| 2 | 1 | `{capture_kind, capture_time}` | `capture_kind > capture_time` | photos `.scanned-documents` `.screenshot-captures` |
| 1 each (17 more) | 1 | `{addressed_org, subject_anchor, artifact_kind}` `research.conference-presentation` · `{addressed_org, lifecycle_stage, subject_anchor}` `research.manuscript-publication` · `{cycle_period, artifact_kind}` `academic.recommendation-letters-written` · `{holder_institution, cycle_period, artifact_kind}` `academic.k12-schooling` · `{holder_institution, cycle_period, subject_anchor, artifact_kind}` `academic.coursework` · `{holder_institution, artifact_kind}` `academic.transcripts-credentials` · `{issuing_org, scope_period, artifact_kind}` `finance.payroll-received` · `{repository_instance, artifact_kind}` `code.dotfiles-environment` · `{scope_period, artifact_kind}` `finance.tax-filings` · `{capture_kind, capture_time, occasion_anchor}` `photos.social-media-export` · `{capture_time}` `photos.messenger-export` · `{cycle_period, holder_institution}` `academic.iep-accommodation-plans` · `{lifecycle_stage, subject_anchor}` `research.grants-funding` · `{occasion_anchor, place}` `travel.trip-photos` · `{purpose_anchor}` `applications.purpose-packet` · `{subject_anchor}` `code.pkm-vault` | | |

**28 definitions, 54 applicability rows, and exactly 2 definitions that cross a schema boundary** (serving 8
rows). Allowing one optional role collapses this to **14 definitions**, with 2 cross-schema definitions then
serving 15 rows — the academic/research spine absorbing `academic.coursework` and `academic.k12-schooling`,
and `{subject_anchor, artifact_kind}` picking up `code.pkm-vault`, `finance.household-property` and
`finance.vehicle-records` (the last two by leaving `subject_anchor` unbound, which `TemplateApplicability`
permits and finance's field list requires).

**The honest launch headline: 54 bindings, 14–28 definitions, 3 cross-schema recipes.** The composable
library's payoff is real and almost all of it is in wave 2.

---

## 8. What a recipe cannot carry across, even where the shape matches

Two rows can share a role sequence exactly and still need separate definitions, because
`TemplateFragment.privacy_floor` and `TemplateDefinition.sensitivity_policy_ref` are per-record.

`construction_property.trade-job` and `law_practice.family-law` both realize
`matter_anchor > artifact_kind`. In the first, a job reference is an ordinary folder name. In the second:

> *"it discloses that a named person is being divorced, is seeking protection from someone, or has a child in
> proceedings."*

> `law_practice.immigration-casework`: *"a branch called asylum, removal defence, trafficking … states that
> the human being underneath it is a claimed refugee … and it survives redaction of the name."*

Within recipe 1's 55 rows the third-party-exposure class dominates six schemas — `law_practice` (16 of its 27
rows), `government` (14 of 29), `clinical_practice`, `legal`, `hr`, and parts of `manufacturing`. **Either
`matter_anchor > artifact_kind` is written once with label-eligibility left entirely to the binding, or it is
split in two by exposure class.** That is a decision for the product owner, not a count this document can
produce. The same question applies to `site_anchor > matter_anchor` (`government.housing-authority`'s dwelling
anchor *"must therefore be displayed as a redacted or aliased label rather than a street address"*).

**And a gap worth naming:** the 8 NONE rows recommend a shallow protected packet with **no dimensions at
all**, and `DimensionOrder.__post_init__` rejects an order with zero dimensions (`templates.py:272-275`).
There is currently no record shape for "this situation is organized by refusing to organize it."

---

## 9. Where this pass disagrees with docs 42 and 43

Both were computed on 270 kept rows against a 216-row prose read; this pass is 291 kept rows against a 237-row
prose read, re-done from scratch. Agreement is close, which is the strongest thing that can be said for either.

| Fact | Doc 42 (270 rows) | Doc 43 (270 rows) | **This pass (291 rows)** |
|---|---|---|---|
| `matter_anchor > artifact_kind` | 55 / 11 | 51 / 10 | **55 / 12** |
| `subject_anchor > artifact_kind` | 31 / 9 | 30 / 9 | **32 / 11** |
| `cycle_period > artifact_kind` | 24 / 7 | 22 / 7 | **26 / 7** |
| `holder_institution > subject_anchor` | 11 / 5 | 11 / 5 | **11 / 5** (identical) |
| `component_anchor > artifact_kind` | 14 / 7 | 14 / 6 | **18 / 7** |
| `subject_anchor > component_anchor` | 10 / 3 | 10 / 3 | **13 / 6** |
| `occasion_anchor > artifact_kind` | 6 / 5 | 6 / 5 | **10 / 6** |
| `artifact_kind > scope_period` vs reverse | 31 : 13 | 32 : 13 | **29 : 14** |
| `lifecycle_stage > artifact_kind` | 22 / 4 | 20 / 3 | **20 / 3** |
| NONE rows | 8 (same 8) | 8 (same 8) | **8 (same 8)** |
| UNK rows | 6 (creative) | 6 (creative) | **7** — same 6 creative + `law_practice.investigation` |
| `counterparty_org > subject_anchor` | 4 / 2 | 5 / **1** (failed) | **5 / 2 (passes)** |
| `direction_role` | 1 / 1 | 1 / 1, not adopted | **2 / 2** |
| Definitions | — | not computed | **133 / 79 / 66** by cap |
| Launch definitions | — | — | **28 / 14 / 11** by cap (doc 37 said 24) |

**Three headline disagreements, all mine to defend:** `counterparty_org > subject_anchor` passing,
`direction_role` reaching two schemas, and `law_practice.investigation` being UNK rather than carrying its
schema's default. All three are reading calls on prose, and §10 states them.

---

## 10. The judgement calls most likely to be wrong

Every one of these is a prose reading. They are stated so the product owner can disagree with a specific
sentence rather than with a table.

1. **`career.consulting-client-engagement` — "client first, then the engagement, then document type."** Read as
   `counterparty_org > subject_anchor > artifact_kind`. If the client is instead `holder_institution`,
   `counterparty_org > subject_anchor` drops to 4 rows / 1 schema and **fails the bar**, and recipe 2 gains a
   row. This single row is the whole of §3.1's first finding.
2. **`law_practice.regulatory-submission` — "matter → submission reference → then a shallow outbound/inbound
   split."** Read the third level as `direction_role`. If it is `artifact_kind` instead, `direction_role`
   returns to 1 row / 1 schema and doc 43's non-adoption stands.
3. **`career.recruiting` — "company → role or recruiting cycle → document type."** Read `company` as
   `addressed_org` (a prospective employer is applied *to*, exactly as a target university is) and the
   disjunction as its first alternative, `subject_anchor`. If `company` is `holder_institution`,
   `addressed_org > subject_anchor` drops to 2 rows / 2 schemas and recipe 7 gains one.
4. **`construction_property.variation-claim` — "the project or contract first, then the change or claim."**
   Read as `subject_anchor > matter_anchor`, which is what keeps `subject_anchor` and `matter_anchor` from
   collapsing. If both are `matter_anchor` the row is an illegal self-repeat under 00's *"does not repeat a
   parent dimension"* — which is itself the argument that the two roles are distinct. The same test fires on
   `law_practice.ip-prosecution`, `manufacturing.production-record`, `manufacturing.warranty-claim` and
   `manufacturing.failure-analysis`. **The corpus refuses the matter/subject merge five times over.**
5. **"authority-side function" in `government`** (`library-administration`, `parks-public-lands`,
   `school-district-administration`, `social-services-casework`) read as `org_unit` rather than
   `artifact_kind`. Reading it the other way would put `artifact_kind` above `artifact_kind` in each — again
   a self-repeat — but it does move `org_unit` from 16 rows / 6 schemas to 12 / 4.
6. **`resource_operations`'s `operating_authority`** read as `holder_institution` in `grid-connection`. If the
   operator is a third party it is `counterparty_org` instead. Affects one pair count.
7. **`construction_property.drawings-revisions` ("job → discipline/package → sheet") and
   `government.elections-administration` ("poll → contest → station")** each want **two nested
   `component_anchor` levels**, which `DimensionOrder` forbids (*"names one role twice; a role is one
   level"*, `templates.py:275-278`). Both were collapsed to one `component_anchor`. **These two rows are
   evidence that `component_anchor` may need to split into a container level and an item level.**
8. **`logistics.last-mile-pod` — "consignment/parcel → delivery event or record_type."** Read the disjunction
   as `artifact_kind` against the first-named convention, because the row's subject is proof-of-delivery
   documents. Reading it as `occasion_anchor` moves one row.

---

## 11. What this proposes

1. **Freeze the sixteen recipes in §2.2** as `TemplateFragment` candidates, with §8's exposure-class question
   answered first for recipe 1 and recipe 5.
2. **Do not cut Recipe 2.** It is 11 rows across 5 schemas with zero reversals and it is one of only three
   recipes with a bound half.
3. **Count definitions as role sets, not sequences** — the built code already requires it — and adopt **cap 1**:
   **79 definitions for the full catalogue, 14 for launch.**
4. **Say "291 situations, 79 definitions, ~16 fragments"** rather than "200–300 templates." 00's range is
   right about the first number and roughly 2–4× too high for the second.
5. **Scope the research stage-flip to research** and ship `{subject_anchor, lifecycle_stage, artifact_kind}`
   with both orders as candidates. §4.2 stops being an open design question the moment the definition offers
   both.
6. **Do not merge the four org roles**, and record `business_operations.partnerships-bd` and
   `.corporate-regulatory-filings` as the structural proof (§3.3).
7. **Open a record-shape question for the 8 NONE rows** (§8): a situation whose recommendation is zero depth
   has no representable definition today.
8. **Treat the 13 unbindable recipes as the wave-2 backlog**, and note that they are unbindable because six
   roles carrying 222 role-uses across up to 13 schemas have no field anywhere in the product.

---

## Appendix — reproduction

The field half is fully mechanical:

```bash
cd "/Users/jy/GRAPH AGENT"

# §1 census
python3 -c "
import json,glob
from collections import Counter
rows=[json.load(open(p)) for p in sorted(glob.glob('planning/domains/nodes/*.json'))]
print('files',len(rows),Counter(r['kind'] for r in rows))
print('refused',sum(1 for r in rows if r.get('refuse_node')))
t=[r for r in rows if r['kind']=='template' and not r.get('refuse_node')]
b=[r for r in t if r['template'].get('dimension_order')]
print('kept',len(t),'bindable',len(b),'gated',len(t)-len(b))
s=[r for r in rows if r['kind']=='schema' and r['fields']]
print('live-field schemas',len(s),'fields',sum(len(x['fields']) for x in s))"

# §1 binding contract: every bound token names a field its own schema declares
python3 -c "
import json,glob
rows=[json.load(open(p)) for p in sorted(glob.glob('planning/domains/nodes/*.json'))]
sch={r['id']:{f['field'] for f in r['fields']} for r in rows if r['kind']=='schema'}
bad=[(r['id'],t) for r in rows if r['kind']=='template' and not r.get('refuse_node')
     for t in r['template'].get('dimension_order',[]) if t not in sch[r['schema_id']]]
print('unmapped tokens:',len(bad),bad)"

# §6.1 def.subject-work-record, verified against the bound rows only
python3 -c "
import json,glob
M={'work_type':'K','artifact_type':'K','record_type':'K','application_document_type':'K',
   'project':'S','subject':'S'}
rows=[json.load(open(p)) for p in sorted(glob.glob('planning/domains/nodes/*.json'))]
n=[]
for r in rows:
    d=r['template'].get('dimension_order') if r['kind']=='template' else None
    if not d or r.get('refuse_node'): continue
    m=[M.get(t) for t in d]
    if 'S' in m and 'K' in m and m.index('S')<m.index('K'): n.append((r['schema_id'],r['id']))
print(len(n),'rows,',len({s for s,_ in n}),'schemas'); [print(' ',s,i) for s,i in sorted(n)]"
```

**The prose half is a manual read of `template.why` on all 237 field-less rows.** To regenerate the exact
corpus this pass read:

```bash
python3 -c "
import json,glob,collections
by=collections.defaultdict(list)
for p in sorted(glob.glob('planning/domains/nodes/*.json')):
    d=json.load(open(p))
    if d['kind']=='template' and not d.get('refuse_node') and not d['template'].get('dimension_order'):
        by[d['schema_id']].append((d['id'],d['template']['why']))
for s in sorted(by):
    print('#'*8,s,len(by[s]))
    for i,w in sorted(by[s]): print('###',i); print(w); print()"
```

The role sequence assigned to each of those 237 rows is the one judgement layer in this document. §10 names
the eight calls most likely to be wrong; §1.2 states the two conventions that produced them.
