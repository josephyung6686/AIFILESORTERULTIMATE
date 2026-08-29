# Full-corpus re-test of the template-reuse conclusion

Date: 2026-08-27 · Checks [`37-TEMPLATE-REUSE-INVENTORY.md`](37-TEMPLATE-REUSE-INVENTORY.md) and
[`41-TEMPLATE-DECISION-BRIEF.md`](41-TEMPLATE-DECISION-BRIEF.md). Revises neither.
`00-database-agent-product-design.md` wins on conflict.

**The objection being tested, in Joseph's words:** *"make sure you're not only looking at like 5 or 6
templates but like every template possible."* He was right to raise it. The brief's three recipes were
derived from **54 rows in 6 domains**. This document recomputes them against **all 270 kept template rows
in 23 domains** — including the 216 whose schemas declare zero fields and whose ordering therefore lives
only in prose.

---

## 0. The answer, before the evidence

| | Verdict |
|---|---|
| **Recipe 1 — subject then kind** | **HOLDS.** 14 rows / 3 domains → **31 rows / 9 domains**. Zero counter-examples in 270 rows. |
| **Recipe 2 — my institution first** | **HOLDS, and it was mis-flagged.** 4 rows / 2 domains → **11 rows / 5 domains**, zero counter-examples. It was the weakest of three in a 6-domain sample because five of the domains that use it were not in the sample. **Do not cut it.** |
| **Recipe 3 — term then kind** | **HOLDS, and it is now the second-strongest.** 4 rows / 2 domains → **24 rows / 7 domains**, 2 counter-examples. |
| **A 4th recipe** | **YES — and it is bigger than all three.** `matter_anchor > artifact_kind` ("**the case then the kind**"): **55 rows across 11 domains**, zero counter-examples. It is invisible to the 54-row sample because the role it needs **does not exist in the 15-role vocabulary**. |
| **A 5th** | **Two candidates, both contested.** `lifecycle_stage > artifact_kind` (22 rows / 4 domains) and `artifact_kind > scope_period` (31 rows / 8 domains, but 13 rows run the other way). Neither is safe to freeze today. |
| **The forbidden merge** | **Still forbidden — and now genuinely tempting.** Merging the org roles produces `ORG > subject_anchor` at **20 rows / 6 domains** and `ORG > artifact_kind` at **13 rows / 5 domains**, where the brief could only see 10 rows / 2 domains. Split correctly, both collapse. The bigger numbers make the refusal *more* important, not less. |

**Single clearest recommendation:** *do not ship a recipe set derived from the 6 field-declaring domains.*
The three survive, but they are the small half of the picture: the largest reusable ordering fact in the
corpus (`matter_anchor > artifact_kind`, 55 rows, 11 domains) cannot even be *stated* in today's role
vocabulary. **Fix the vocabulary first** (§5), then re-cut the recipes. Approving §3 of the brief today is
safe on its own terms; approving it as *complete* is not.

---

## 1. Method, and what each number is worth

### 1.1 The corpus, computed at write time

```
complete rows (both .json and .research.md present):  333
kept template rows (kind==template, refuse_node falsy): 270  across 23 schemas
  ├─ with a declared `template.dimension_order`:        54  (6 schemas)  <- FIELD-DERIVED
  └─ with `dimension_order == []`:                     216  (17 schemas) <- PROSE-DERIVED
```

The brief's count of 54 field-derived rows is still exactly right. The other number has moved: the brief
said "212 of 266"; it is now **216 of 270**. Four rows landed while this analysis ran
(`resource_operations.farm-records`, `.fisheries-catch`, `.forestry-records`, `.mining-operations`); all
four are included.

### 1.2 How order was extracted from the 216 prose rows

The 17 field-less schemas cannot bind a dimension, but almost every row **argues an order in
`template.why` anyway** — usually as a stated departure from its schema's own default paragraph, because
the node test requires each row to say how it differs. I read all 216 `why` blocks in full (326 KB) and
recorded one role sequence per row, with a confidence grade:

| Grade | Meaning | Rows |
|---|---|---:|
| **HIGH** | the row states an ordered recommendation in its own words (`"the recommendation is X, then Y, then Z"`) | 157 |
| **MED** | order inferable but the row hedges, splits its corpus in two, or writes a level as a disjunction | 41 |
| **LOW** | order is purely hypothetical (`"if fields ever land, X would precede Y"`) | 3 |
| **NONE** | the row positively recommends **no depth at all** — this is a finding, not a failed extraction | 8 |
| **UNK** | no order recoverable from the prose | 6 |

**202 of 216 prose rows yielded a usable order. Together with the 54 field rows, 256 of 270 rows (95%)
are in the counts below.**

The 8 NONE rows are the whole of `identity` (3) and `medical` (3) plus `legal.estate-planning` and
`legal.personal-legal-matters`. They are not undecided — they refuse depth outright, and say why:

> `identity.credentials-passwords`: *"A path such as Provider/Username/Recovery Codes would disclose both
> service usage and account-recovery capability even while file contents remain encrypted."*

The 6 UNK rows are all `creative` (`3d-asset`, `brand-identity`, `music-session`, `print-production`,
`shoot-day-media`, `stock-asset-library`) — short rows that name a lifecycle without ordering folders.

### 1.3 Evidence weighting — stated up front so prose cannot outvote fields silently

**Every table below reports field rows and prose rows in separate columns.** Prose evidence is weaker for
three specific reasons, all of which matter:

1. It is **conditional** — most rows say "subject to R1c" or "if fields are ever ratified". A schema
   decision could invalidate it.
2. It is **unbound** — no row proves its levels can be filled, because no field exists to fill them.
   A field-derived row has already passed that check (the brief verified: *"folder levels with no real
   field behind them: 0"*).
3. It is **normalized by me**, not by a machine. The 54 field rows normalize mechanically from
   `dimension_order` through the inventory's published field→role map; the 216 prose rows passed through
   my reading. §5.3 lists the four judgement calls that would most change the numbers.

**Where a conclusion rests on prose alone, this document says so in bold.**

---

## 2. The full ranked adjacency table

Same bar the brief used: **a recipe must appear in 2+ different domains**. "Reverse" counts rows anywhere
in the corpus that order the same two roles the *other* way — the brief's own contradiction test.
"CONTESTED" marks a pair whose reverse direction reaches 25% of its own count.

| # | Pair (adjacent) | Field rows | Field dom. | Prose rows | Prose dom. | **Total** | **Domains** | **Reverse** | Bar |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | `matter_anchor` > `artifact_kind` | 0 | 0 | 55 | 11 | **55** | **11** | 0 | PASS |
| 2 | `subject_anchor` > `artifact_kind` | 14 | 3 | 17 | 6 | **31** | **9** | 0 | PASS |
| 3 | `artifact_kind` > `scope_period` | 0 | 0 | 31 | 8 | 31 | 8 | 13 | CONTESTED |
| 4 | `cycle_period` > `artifact_kind` | 4 | 2 | 20 | 5 | **24** | **7** | 2 | PASS |
| 5 | `lifecycle_stage` > `artifact_kind` | 0 | 0 | 22 | 4 | 22 | 4 | 2 | PASS |
| 6 | `subject_anchor` > `lifecycle_stage` | 1 | 1 | 18 | 2 | 19 | 3 | 0 | PASS |
| 7 | `site_anchor` > `matter_anchor` | 0 | 0 | 15 | 5 | 15 | 5 | 0 | PASS |
| 8 | `component_anchor` > `artifact_kind` | 0 | 0 | 14 | 7 | 14 | 7 | 2 | PASS |
| 9 | `scope_period` > `artifact_kind` | 2 | 1 | 11 | 6 | 13 | 7 | 31 | CONTESTED |
| 10 | `holder_institution` > `subject_anchor` | 4 | 2 | 7 | 3 | **11** | **5** | 0 | PASS |
| 11 | `subject_anchor` > `component_anchor` | 0 | 0 | 10 | 3 | 10 | 3 | 0 | PASS |
| 12 | `issuing_org` > `artifact_kind` | 8 | 1 | 0 | 0 | 8 | 1 | 1 | fail (1 domain) |
| 13 | `matter_anchor` > `lifecycle_stage` | 0 | 0 | 8 | 3 | 8 | 3 | 0 | PASS |
| 14 | `site_anchor` > `asset_instance` | 0 | 0 | 7 | 4 | 7 | 4 | 0 | PASS |
| 15 | `account_kind` > `artifact_kind` | 4 | 1 | 2 | 2 | 6 | 3 | 1 | PASS |
| 16 | `occasion_anchor` > `artifact_kind` | 0 | 0 | 6 | 5 | 6 | 5 | 0 | PASS |
| 17 | `capture_time` > `occasion_anchor` | 4 | 1 | 1 | 1 | 5 | 2 | 1 | PASS |
| 18 | `subject_anchor` > `cycle_period` | 0 | 0 | 5 | 4 | 5 | 4 | 3 | CONTESTED |
| 19 | `series_instalment` > `artifact_kind` | 0 | 0 | 5 | 5 | 5 | 5 | 0 | PASS |
| 20 | `asset_instance` > `artifact_kind` | 0 | 0 | 5 | 4 | 5 | 4 | 0 | PASS |
| 21 | `counterparty_org` > `matter_anchor` | 0 | 0 | 5 | 4 | 5 | 4 | 1 | PASS |
| 22 | `site_anchor` > `artifact_kind` | 0 | 0 | 5 | 3 | 5 | 3 | 0 | PASS |
| 23 | `holder_institution` > `cycle_period` | 3 | 1 | 1 | 1 | 4 | 2 | 0 | PASS |
| 24 | `addressed_org` > `subject_anchor` | 1 | 1 | 3 | 2 | 4 | 3 | 1 | CONTESTED |
| 25 | `counterparty_org` > `subject_anchor` | 0 | 0 | 4 | 2 | 4 | 2 | 0 | PASS |
| 26 | `subject_anchor` > `series_instalment` | 0 | 0 | 4 | 4 | 4 | 4 | 0 | PASS |
| 27 | `subject_anchor` > `matter_anchor` | 0 | 0 | 4 | 3 | 4 | 3 | 0 | PASS |
| 28 | `asset_instance` > `matter_anchor` | 0 | 0 | 4 | 2 | 4 | 2 | 0 | PASS |
| 29 | `site_anchor` > `component_anchor` | 0 | 0 | 4 | 3 | 4 | 3 | 0 | PASS |
| 30 | `matter_anchor` > `occasion_anchor` | 0 | 0 | 4 | 2 | 4 | 2 | 0 | PASS |
| 31 | `cycle_period` > `subject_anchor` | 3 | 1 | 0 | 0 | 3 | 1 | 5 | CONTESTED |
| 32 | `issuing_org` > `account_kind` | 3 | 1 | 0 | 0 | 3 | 1 | 0 | fail (1 domain) |
| 33 | `matter_anchor` > `component_anchor` | 0 | 0 | 3 | 2 | 3 | 2 | 0 | PASS |
| 34 | `org_unit` > `cycle_period` | 0 | 0 | 3 | 2 | 3 | 2 | 0 | PASS |
| 35 | `counterparty_org` > `cycle_period` | 0 | 0 | 3 | 2 | 3 | 2 | 0 | PASS |
| 36 | `artifact_kind` > `org_unit` | 0 | 0 | 3 | 1 | 3 | 1 | 1 | CONTESTED |
| 37 | `matter_anchor` > `cycle_period` | 0 | 0 | 3 | 2 | 3 | 2 | 2 | CONTESTED |
| 38 | `asset_instance` > `scope_period` | 0 | 0 | 3 | 1 | 3 | 1 | 0 | fail (1 domain) |
| 39 | `addressed_org` > `artifact_kind` | 2 | 1 | 0 | 0 | 2 | 1 | 1 | CONTESTED |
| 40 | `artifact_kind` > `lifecycle_stage` | 2 | 1 | 0 | 0 | 2 | 1 | 22 | CONTESTED |
| 41 | `capture_kind` > `capture_time` | 2 | 1 | 0 | 0 | 2 | 1 | 0 | fail (1 domain) |
| 42 | `component_anchor` > `lifecycle_stage` | 0 | 0 | 2 | 2 | 2 | 2 | 1 | CONTESTED |
| 43 | `component_anchor` > `series_instalment` | 0 | 0 | 2 | 1 | 2 | 1 | 0 | fail (1 domain) |
| 44 | `component_anchor` > `account_kind` | 0 | 0 | 2 | 2 | 2 | 2 | 0 | PASS |
| 45 | `asset_instance` > `occasion_anchor` | 0 | 0 | 2 | 2 | 2 | 2 | 0 | PASS |
| 46 | `cycle_period` > `matter_anchor` | 0 | 0 | 2 | 2 | 2 | 2 | 3 | CONTESTED |
| 47 | `holder_institution` > `matter_anchor` | 0 | 0 | 2 | 2 | 2 | 2 | 0 | PASS |
| 48 | `counterparty_org` > `artifact_kind` | 0 | 0 | 2 | 2 | 2 | 2 | 0 | PASS |
| 49 | `artifact_kind` > `cycle_period` | 0 | 0 | 2 | 2 | 2 | 2 | 24 | CONTESTED |
| 50 | `occasion_anchor` > `component_anchor` | 0 | 0 | 2 | 2 | 2 | 2 | 1 | CONTESTED |
| 51 | `matter_anchor` > `scope_period` | 0 | 0 | 2 | 2 | 2 | 2 | 0 | PASS |
| 52 | `account_kind` > `matter_anchor` | 0 | 0 | 2 | 1 | 2 | 1 | 0 | fail (1 domain) |
| 53 | `lifecycle_stage` > `series_instalment` | 0 | 0 | 2 | 1 | 2 | 1 | 0 | fail (1 domain) |
| 54 | `artifact_kind` > `component_anchor` | 0 | 0 | 2 | 1 | 2 | 1 | 14 | CONTESTED |
| 55 | `site_anchor` > `scope_period` | 0 | 0 | 2 | 2 | 2 | 2 | 0 | PASS |
| 56 | `account_kind` > `scope_period` | 0 | 0 | 2 | 1 | 2 | 1 | 0 | fail (1 domain) |

59 further pairs occur exactly once and are omitted; none is cross-domain by construction.

---

## 3. The three claimed recipes, re-tested

### 3.1 Recipe 1 — "subject then kind" — **HOLDS, and doubles**

| | Rows | Domains |
|---|---:|---|
| Brief (54-row sample) | 14 | academic, code, research |
| **Full corpus** | **31** | **+ business_operations, career, creative, government, hr, retail_hospitality = 9** |
| Counter-examples (`artifact_kind` above `subject_anchor`, adjacent **or** at any distance) | **0** | — |

Relative-order check (not just adjacency): **68 rows across 13 domains** place a `subject_anchor` above an
`artifact_kind` somewhere in their sequence. **Zero rows anywhere in 270 place them the other way.**

The 17 new prose rows: `business_operations.market-research` · `.policy-handbook` · `.project-delivery` ·
`.support-operations` · `career.consulting-client-engagement` · `.credentials-licenses` ·
`.employment-records` · `.portfolio-work-samples` · `.recruiting` · `creative.podcast-episode` ·
`.printmaking-editions` · `.short-form-writing` · `government.archives-recordkeeping` ·
`.library-administration` · `.policy-development` · `hr.dei-program` ·
`retail_hospitality.menu-recipe-costing`.

The brief's own honest caveat — that research and code use the same two underlying fields, so Recipe 1
might really span two domains not three — **is dissolved.** It now spans nine, six of which share no field
with any other.

### 3.2 Recipe 2 — "my institution first" — **HOLDS. The "cut it" flag was an artifact of the sample.**

| | Rows | Domains |
|---|---:|---|
| Brief | 4 (3 of them academic) | academic, research |
| **Full corpus** | **11** | **+ business_operations (5), career (1), nonprofit (1) = 5** |
| Counter-examples | **0** | — |

The brief wrote: *"Recipe 2 is the weakest: only 4 rows, 3 of them academic. If you want one cut, cut
Recipe 2."* That reads differently now. The rows that use it most are `business_operations`, which had no
vote:

> `business_operations.policy-handbook`: *"the natural anchor is the organisation whose rules these are,
> then the policy AREA or function … the document is meaningless without the organisation, since the same
> policy title exists at every employer a person has ever had."*

> `business_operations.product-requirements`: *"the natural anchor is the organisation, then the PRODUCT,
> then the feature or initiative being specified."*

**And the optionality the brief asserted is confirmed, not assumed.** Every prose row that uses this
recipe independently marks the top level conditional, in near-identical language — the level exists only
where the corpus spans more than one organisation:

> `nonprofit.member-association`: *"the ASSOCIATION only where the corpus genuinely spans more than one and
> never in a single-association corpus, where it is 'use an author or organization merely as a collector'
> and would 'create meaningless one-child levels'."*

**Recommendation: keep Recipe 2.** Cutting it was cheap when it covered 4 rows in 2 domains. At 11 rows in
5 domains, writing the same optional-institution logic five times is exactly the duplication the recipe
mechanism exists to prevent.

**One warning attached to it — §4.3.** Three *different* org roles now sit in the same top-of-tree slot,
and they must not be merged into Recipe 2.

### 3.3 Recipe 3 — "term then kind" — **HOLDS, and grows sixfold**

| | Rows | Domains |
|---|---:|---|
| Brief | 4 | academic, college_applications |
| **Full corpus** | **24** | **+ business_operations, creative, government, hr, nonprofit = 7** |
| Counter-examples (`artifact_kind` above `cycle_period`) | **2** | `government.permit-licensing`, `construction_property.block-management` |

`hr` alone contributes 8 of the 20 new rows, and every one of them argues the same thing the brief's
academic rows argue — that the cycle is what makes the artefact intelligible:

> `hr.performance-cycle`: *"a self-assessment or a calibration extract is unintelligible without the round
> it belongs to, in the same way a homework item is unintelligible without its course."*

> `hr.payroll-benefits-administration`: *"the run is what makes a register, a bank file, a filing receipt
> and a reconciliation intelligible together, exactly as a course makes Homework 3 intelligible."*

The brief's worry — *"Recipe 3 merges an academic term with an admissions season, which are not quite the
same kind of time"* — is now a seven-way version of the same worry: an academic term, an admissions
season, a pay run, a survey wave, a review round, a giving year, a design round, a census point. What they
share is that **none of them is a capture date**; every one of the 24 rows sets `time_first: false` and
several say so explicitly:

> `hr.engagement-survey`: *"a wave is a named process instance, not a date; two waves can close in the same
> quarter and a report can be written a quarter after fielding."*

That is a real shared property and it is the one the recipe encodes. The 2 counter-examples are both rows
where the period is a **recurring compliance year sitting under a function** rather than a cycle above it;
they are the seam with §4.2, not a refutation.

---

## 4. The fourth recipe — and why the 54-row sample could not see it

### 4.1 `matter_anchor > artifact_kind` — "the case then the kind"

> **55 rows · 11 domains · zero counter-examples · zero field rows.**

This is the largest single ordering fact in the corpus — nearly double Recipe 1 — and it appears in
**eleven** domains: `business_operations`, `career`, `clinical_practice`, `construction_property`,
`engineering`, `government`, `hr`, `law_practice`, `legal`, `manufacturing`, `retail_hospitality`.
Relative-order check: **67 rows / 12 domains** put the matter above the kind at any distance; **0** put it
below.

A `matter_anchor` is **a bounded proceeding, case, engagement, transaction, competition, claim, permission
or job** — something with a start, an end and its own reference. It is not a `subject_anchor` (an ongoing
named work) and the corpus insists on the difference by using **both in one path**:

```
construction_property.tenancy-management   property -> TENANCY -> function
government.planning-application            SITE     -> determination proceeding -> document function
law_practice.ip-prosecution                the RIGHT -> the MATTER -> function
business_operations.partnerships-bd        organisation -> counterparty -> PURSUIT -> function
```

`law_practice.corporate-secretarial` argues the distinction explicitly, and its argument is the reason the
two roles cannot be one:

> *"corporate secretarial work is a PERPETUAL RETAINER, not a matter with a start and an end, and a matter
> level under it would hold one child forever."*

**Why the brief could not see it.** `matter_anchor` is not one of the 15 roles, and no field in the six
live domains maps to it. The recipe is therefore not merely under-counted in the 54-row sample — it is
**unstateable** in it.

**The strongest argument against merging it.** The 55 rows agree on the *order* but disagree sharply on
whether the level may be **named at all**. In `construction_property` a job reference is an ordinary
folder name; in `law_practice` and `clinical_practice` the identical structural level is a disclosure:

> `law_practice.family-law`: *"it discloses that a named person is being divorced, is seeking protection
> from someone, or has a child in proceedings."*

> `law_practice.immigration-casework`: *"a branch called asylum, removal defence, trafficking … states
> that the human being underneath it is a claimed refugee … and it survives redaction of the name."*

This is the inventory's own §2.2(c) test — *"Direction-of-exposure is the privacy discriminator a fragment
must carry"* — arriving at industrial scale. **One recipe cannot carry both exposure classes.** If
`matter_anchor > artifact_kind` is written once, it must be written with the label-eligibility of the
level left to the binding, or it must be split in two by exposure class. That is a real design decision,
not a formality, and it is the reason to define this recipe deliberately rather than let 55 rows each
invent it.

### 4.2 Fifth candidate A — `artifact_kind > scope_period` — **CONTESTED, do not freeze**

31 rows / 8 domains put a covering period **below** the function level; 13 rows / 7 domains (including the
only 2 field rows on this pair) put it **above**. Ratio 31:13 — well past the brief's own bar for calling
a recipe contradicted.

The split is not noise; it tracks a distinction the vocabulary does not make:

| Period is a **trailing discriminator** (31 rows) | Period **is the record's identity** (13 rows) |
|---|---|
| `business_operations.vendor-management` — a review period under a scorecard | `finance.tax-filings` (field) — *"it cannot scatter a filing, because the filing IS the year"* |
| `law_practice.motions-and-briefs` — period last under function | `resource_operations.utility-metering-billing` — `service point → reporting_period → record_type` |
| `logistics.fleet-vehicle` — *"Time survives as a leaf … the date is the only thing distinguishing two otherwise identical sheets"* | `government.emergency-management` — *"`ICS-209 … OP 6` … unintelligible outside the period they report on"* |
| `clinical_practice.pharmacy-operations` — function then period | `retail_hospitality.ecommerce-ops` — the export window is *"a date RANGE chosen by whoever pulled the report"* |

**`scope_period` is doing two jobs.** Until they are separated this is not a recipe. It is, however, the
clearest single piece of evidence that the role vocabulary is under-specified.

### 4.3 Fifth candidate B — `lifecycle_stage > artifact_kind` — **and it contradicts the brief's §4-B default**

> 22 rows / 4 domains (`creative`, `engineering`, `government`, `retail_hospitality`) — all prose.
> Against: **2 rows, both `research`, both field-derived.**

The brief's §4 Decision B flipped 00's own Research order on the strength of those 2 rows, and flagged the
risk itself: *"the creative domain's prose backs 00's original order, but creative has zero fields and
cannot vote yet — so this may reopen in wave 2."*

**It reopens now, and by more than creative.** 00 §5.4's full chain — `project → stage → artifact type` —
which the inventory recorded as realized by *"not one landed row … [] (empty)"*, is realized as a
**consecutive three-level chain by 17 rows across 2 domains**: 15 `creative` rows plus
`engineering.invention-disclosure` and `engineering.stage-gate-review`. By the brief's own 2-domain bar,
**00's original order now clears it and the flip does not.**

Two things keep this from settling the question:
- The 2 rows against are **field-derived and bound**; the 17 for are prose and conditional. §1.3 applies.
- `engineering` is the loudest voice *against* a standing stage level — 9 of its 19 rows drop
  `lifecycle_stage` from their schema's own default, each for a different reason
  (`engineering.drawing-package`: *"a document state that would build a Superseded folder competing with
  the version family for the same bytes"*). Engineering supports stage-above-kind **where a stage level
  exists at all**, which is not often.

**OPEN.** The honest reading is that the brief's §4-B default is defensible for research and indefensible
as a general rule, which is precisely what shipping 2–3 candidate orders per template (the brief's §4.1
amendment) is for. Recorded so it is not discovered after `research`'s flip has been generalized.

### 4.4 Everything else clearing the 2-domain bar that the sample could not see

All prose-only; all involve at least one role outside the 15. Listed because a "recipes should reach
~5–10 at full size" estimate (brief §7.8) is now visibly low:

| Pair | Rows | Domains | Reverse |
|---|---:|---:|---:|
| `site_anchor` > `matter_anchor` | 15 | 5 | 0 |
| `component_anchor` > `artifact_kind` | 14 | 7 | 2 |
| `subject_anchor` > `component_anchor` | 10 | 3 | 0 |
| `matter_anchor` > `lifecycle_stage` | 8 | 3 | 0 |
| `site_anchor` > `asset_instance` | 7 | 4 | 0 |
| `occasion_anchor` > `artifact_kind` | 6 | 5 | 0 |
| `series_instalment` > `artifact_kind` | 5 | 5 | 0 |
| `asset_instance` > `artifact_kind` | 5 | 4 | 0 |
| `counterparty_org` > `matter_anchor` | 5 | 4 | 1 |
| `site_anchor` > `artifact_kind` | 5 | 3 | 0 |

---

## 5. The role vocabulary is the real finding

### 5.1 Nine roles the corpus needs and the 15-role list does not have

| New role | What it is | Rows | Domains | A row that states the need |
|---|---|---:|---:|---|
| **`matter_anchor`** | a bounded proceeding / case / engagement / transaction / job, with its own reference | **80** | **12** | `government.constituent-casework`: *"the only defensible first level here is the CASE as a bounded, opaque reference"* |
| **`site_anchor`** | a fixed facility, parcel, premises, installation or dwelling as the organizing anchor | **43** | **10** | `logistics.warehouse-ops`: *"a bin code is only meaningful relative to a building, the same code `A-12-03-B` exists in every facility"* |
| **`component_anchor`** | a designed item / part / sheet / plot / structure **nested inside** a subject or matter | **29** | **9** | `engineering.civil-structural`: *"a member mark is unintelligible outside the structure that contains it"* |
| **`counterparty_org`** | the client / customer / supplier an engagement serves — **a fourth org role** | **17** | **8** | `manufacturing.field-service-report` names the canonical key: *"the canonical `client` key (role: 'the counterparty organization an engagement serves')"* |
| **`asset_instance`** | an operated physical thing with an identity: vehicle, machine, meter, well, installed unit | **17** | **7** | `manufacturing.maintenance-work-order`: *"A job number is unintelligible without its asset"* |
| **`series_instalment`** | a serial position that is neither a period nor a stage: issue no., volume, edition, baseline | **9** | **6** | `creative.periodical-issue`: *"the issue designator maps to no candidate key … It is not `project` … not `stage` … not `artifact_type`"* |
| **`org_unit`** | an internal unit, cost centre, department or constituted body — below the institution | **9** | **3** | `hr.org-design-headcount`: *"an establishment artifact is ABOUT a unit"* |
| **`standard_ref`** | an external standard / scheme / framework the material answers to | 3 | 2 | `business_operations.compliance-audit`: *"an EXTERNAL referent the entity is measured against, and it outlives every occurrence beneath it"* |
| `provenance_role`, `variant_axis`, `direction_role` | obtained-vs-authored; colourway; sent-vs-received | 1 each | 1 each | `creative.journalism-reporting` (`proposed_fields.material_role`), `engineering.industrial-design`, `clinical_practice.referral-correspondence` |

For contrast, four of the existing 15 are near-dead at full corpus scale: `place` (1 row),
`repository_instance` (1), `purpose_anchor` (2), `capture_kind` (3).

**`purpose_anchor` gains a second domain** — `construction_property.survey-valuation` uses it and cites
00 by name: *"the same property, the same surveyor and nearly the same report exist in three purposes with
three different audiences — 00's own distinction applies exactly: 'Topic answers what a file is about,
while purpose answers what the file was for.'"* That answers brief **O7** ("Does `purpose` stay
applications-only?") with **no** — on prose evidence.

### 5.2 `place` cannot absorb `site_anchor`

`place` is defined in the inventory as *"where a capture was taken, resolved from GPS or content"* and maps
to one field (`location`, photos) in one row. A regulated installation, a let premises or a warehouse is
not that — it is a durable subject that the record is *about*. Two rows argue the difference against each
other and both are right:

> `creative.raw-photo-catalogue` vs `construction_property.progress-photos`: *"a camera roll goes to many
> places once, a site walk goes to one place many times"* — *"one place recurring is what makes PLACE the
> stable parent there."*

### 5.3 Four judgement calls that would move the numbers — stated so they can be disagreed with

1. **`matter_anchor` vs `subject_anchor`.** If merged, Recipe 1 becomes **86 rows / 15 domains** — but
   **5 rows collapse to `subject_anchor > subject_anchor`**, an illegal self-repeat under 00's *"does not
   repeat a parent dimension"*: `business_operations.go-to-market`, `construction_property.variation-claim`,
   `law_practice.ip-prosecution`, `manufacturing.production-record`, `manufacturing.warranty-claim`. The
   corpus itself refuses the merge.
2. **`component_anchor` vs `subject_anchor`.** Same structure, same refusal — engineering's
   `project → design_item` would become `subject_anchor > subject_anchor` in 10 rows.
3. **`operating_authority` → `holder_institution`** in the four `resource_operations` rows. If the operator
   is a third party these are `counterparty_org` instead. Affects 1 pair count; flagged, not resolved.
4. **`career.recruiting`'s "company" → `addressed_org`.** A prospective employer is applied *to*, exactly
   as a target university is. If instead it is `holder_institution`, `addressed_org > subject_anchor` drops
   from 4 rows / 3 domains to 3 / 2 and Recipe 2 gains a row.

---

## 6. Re-testing the rejections at full scale

### 6.1 R1 — merging `issuing_org` with `addressed_org` — **STILL FORBIDDEN, and now far more tempting**

00: *"The system must separate roles that happen to contain the same entity type."*

The brief refused a merge worth **10 rows / 2 domains**. At full scale there are **four** org roles, and
merging them all produces this:

| Merge | Merged appearance | What it really is when split correctly |
|---|---|---|
| all 4 org roles → one `ORG` > `artifact_kind` | **13 rows / 5 domains** (academic, business_operations, college_applications, construction_property, finance) | `issuing_org` 8/**1** · `addressed_org` 2/**1** · `counterparty_org` 2/2 · `holder_institution` 1/**1** |
| all 4 org roles → one `ORG` > `subject_anchor` | **20 rows / 6 domains** | `holder_institution` 11/5 · `counterparty_org` 4/2 · `addressed_org` 4/3 · `issuing_org` 1/1 |

**The numbers would absolutely have tempted someone.** A 5-domain and a 6-domain "organization then kind /
then subject" recipe are the two most attractive statistics in this entire document, and both are
illusions of exactly the kind the brief caught at smaller scale. The corpus's own defence is unusually
loud at full size:

> `career.consulting-client-engagement`: *"`our_firm` must NOT be a level, ever, even though it is the
> single most reliably extractable organization on these files."*

> `creative.submission-query`: *"its organizing anchor is an ADDRESSEE IN A SUBMITTED-TO ROLE and `client`
> is a COMMISSIONING role. A literary agent, a magazine editor, a juror and a festival programmer have
> commissioned nothing; recording them as `client` would assert a relationship that does not exist and
> would fuse a rejection with a paid job."*

> `manufacturing.field-service-report`: *"the schema's `site` is expressly the facility that PERFORMS
> production, which the holder does not have in these files — the only site present belongs to a third
> party."*

**Note the second row of that table carefully.** `holder_institution > subject_anchor` **already clears the
bar on its own at 5 domains**. The merge buys nothing it does not already have and costs the distinction
00 forbids losing. That is the cleanest possible refutation.

### 6.2 R2 — `container` merging `repository` and `account_type` — **rejection holds; the merge is now also pointless**

The brief refused this at 5 rows / 2 domains on instance-vs-category grounds. At full scale:
`account_kind > artifact_kind` reaches **6 rows / 3 domains** unaided (finance + `business_operations`
+ `government`), while `repository_instance` is still **1 row**. The category role clears the bar by
itself; merging an instance into it would add one row and one domain and destroy the distinction. **Refuse,
and note it no longer costs anything.**

### 6.3 R5 — 00 §5.4's `project → stage → artifact kind` — **the refutation does not survive**

The inventory recorded: *"EVIDENCE: not one landed row realizes it … [] (empty)."* True of the 54, and now
false of the 270: **17 rows across 2 domains realize the consecutive chain** (15 creative, 2 engineering),
which clears the brief's own bar. See §4.3. The brief's §4-B recommendation should be treated as a
**research-local default**, not a general finding.

### 6.4 R9 — folding `media_type` into `artifact_kind` — **rejection holds, unchanged**

`capture_kind` is still 3 rows in `photos` only. Nothing in the 17 prose domains touches it. No change.

### 6.5 The privacy-class split (inventory §2.2(c)) — **massively reinforced**

The inventory found ≥4 live rows needing a third-party-exposure class. At full corpus the third-party
class is the dominant privacy fact in six domains — `law_practice` (23 rows), `clinical_practice` (6),
`government` (29), `hr` (11), `nonprofit` (3), `medical`/`identity`/`legal` (10). It is the reason 8 rows
refuse depth entirely. **Any recipe crossing these domains must carry the exposure class or must not
cross them.** This bears directly on brief **O4** (do recipes carry a privacy floor): the corpus says a
recipe alone cannot, because `construction_property.trade-job` and `law_practice.family-law` share the
`matter_anchor > artifact_kind` shape and could not be more different in what the folder name may say.

---

## 7. Contradiction audit — every claimed recipe, every counter-example

| Recipe | Rows for | Rows against (adjacent) | Rows against (any distance) | Verdict |
|---|---:|---:|---:|---|
| 1 · `subject_anchor` > `artifact_kind` | 31 | **0** | **0 of 270** | clean |
| 2 · `holder_institution` > `subject_anchor` | 11 | **0** | **0 of 270** | clean |
| 3 · `cycle_period` > `artifact_kind` | 24 | 2 | 2 of 270 | clean enough — both counter-rows are §4.2's other period sense |
| 4 · `matter_anchor` > `artifact_kind` | 55 | **0** | **0 of 270** | clean |
| A · `artifact_kind` > `scope_period` | 31 | 13 | 13 | **not a recipe** |
| B · `lifecycle_stage` > `artifact_kind` | 22 | 2 | 2 | clean by count, but the 2 against are the only *bound* rows — **OPEN** |

The two counter-examples to Recipe 3, in their own words:

> `government.permit-licensing`: *"Function (application / decision / register / enforcement) would come
> second and the cycle or year third."*

> `construction_property.block-management`: *"a SERVICE-CHARGE YEAR level under the service-charge branch
> only, because that branch genuinely cycles annually and nothing else here does."*

Neither disputes that a cycle above a kind is right where the cycle *bounds* the work; both are cases where
the year is a recurring compliance leaf under a function. This is the §4.2 seam, not a contradiction of
Recipe 3.

---

## 8. What this changes, and what it does not

**Does not change:**
- The three recipes are all real. None dissolves. Nothing in §3 of the brief needs revising.
- The forbidden merge stays forbidden (§6.1), and is now better evidenced than before.
- Decisions 1, 2, 4, 5 of the brief (folder names, branch words, bindings, refuse-vs-warn) are untouched by
  anything here — they concern the 54 bound rows only.

**Does change:**
1. **Recipe 2 must not be cut.** The "cut one" advice was correct arithmetic on a 6-domain sample and is
   wrong at 23. (§3.2)
2. **Decision 2 of the brief ("there is no fourth") is false at full corpus.** There is a fourth and it is
   the biggest one. (§4.1)
3. **The 15-role vocabulary is the binding constraint, not the recipe count.** Nine roles are missing and
   three of them (`matter_anchor`, `site_anchor`, `component_anchor`) carry 152 role-uses across 12, 10 and
   9 domains. A recipe set cut before the vocabulary is fixed will be cut along the wrong seams. (§5)
4. **Brief §4-B (research: kind above stage) should be scoped to research, not generalized.** (§4.3)
5. **Brief O7 answered:** `purpose_anchor` is not applications-only. (§5.1)
6. **Brief §7.8's estimate is low.** "Recipes should reach ~5–10 at full size" — at full corpus, 10 pairs
   beyond the three already clear the 2-domain bar (§4.4), before the vocabulary is even repaired.

**OPEN — the corpus does not decide these:**

| | Question | What would settle it |
|---|---|---|
| **F1** | Is `matter_anchor` one recipe or two, split by whether the level may be *named*? | A privacy-class decision, not more rows. §4.1, §6.5. |
| **F2** | Does `scope_period` split into "period the record covers" and "period under which a function repeats"? | A vocabulary decision. Until then §4.2 is not a recipe. |
| **F3** | Does the §4-B flip generalize beyond research? | 17 prose rows say no; 2 bound rows say yes for research. Needs the creative/engineering schemas to land fields. |
| **F4** | Do prose-derived orders bind at all, or must every recipe be re-derived once fields land? | R1c. Every conclusion in §3–§4 that rests on prose alone is conditional on this. |

---

## Appendix — reproduction

The field-derived half is fully mechanical:

```bash
cd "/Users/jy/GRAPH AGENT"

# corpus census (the counts in §1.1)
python3 -c "
import json,os
r=json.load(open('planning/domains/roster.json')); N='planning/domains/nodes/'; f=set(os.listdir(N))
rows=[json.load(open(N+n['domain_id']+'.json')) for n in r['nodes']
      if n['domain_id']+'.json' in f and n['domain_id']+'.research.md' in f]
kept=[d for d in rows if d['kind']=='template' and not d.get('refuse_node')]
bound=[d for d in kept if d['template'].get('dimension_order')]
print('complete', len(rows), '| kept template', len(kept), 'across', len({d['schema_id'] for d in kept}),
      'schemas | bound', len(bound), '| prose-only', len(kept)-len(bound))"

# the two field rows that contradict 'artifact_kind > scope_period' (§4.2)
python3 -c "
import json
for i in ['finance.tax-filings','finance.payroll-received']:
    d=json.load(open('planning/domains/nodes/%s.json'%i))
    print(i, ' > '.join(d['template']['dimension_order']))"

# the two field rows behind brief §4-B (research: kind above stage)
python3 -c "
import json
for i in ['research.dataset-analysis','research.thesis-dissertation']:
    d=json.load(open('planning/domains/nodes/%s.json'%i))
    print(i, ' > '.join(d['template']['dimension_order']))"

# the creative/engineering rows arguing 00's original stage-above-kind order (§4.3).
# NOTE: a lexical probe only - the phrasings vary, so this under-counts the 17 and the
# list must be read, not trusted. It is here to locate the rows, not to produce the number.
grep -il 'stage.*artifact_type\|stage, then artifact_type\|lifecycle stage, then asset type' \
  planning/domains/nodes/creative.*.json planning/domains/nodes/engineering.*.json
```

The prose half is a manual read of `template.why` on all 216 field-less rows. To regenerate the corpus that
was read:

```bash
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

The role sequence assigned to each of those 216 rows, with its confidence grade, is the one judgement layer
in this document. §5.3 names the four calls most likely to be wrong.
