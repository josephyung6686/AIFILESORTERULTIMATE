# The launch set — a draft of the template records that can ship today

Date: 2026-08-27 · Status: **PROPOSAL. Nothing here is adopted.**
For: Joseph · Governed by [`00-database-agent-product-design.md`](00-database-agent-product-design.md), which wins on every conflict.

This document writes **no** template into `src/`, edits **no** `planning/domains/**.json`, and opens no
gate. It is the thing the owner said had to exist before anything ships: *"I need to manually approve
the template and stuff and its actual mechanisms."*

Built against the record shapes in [`src/tree_design/templates.py`](../src/tree_design/templates.py),
which are built and green. Continues
[`37-TEMPLATE-REUSE-INVENTORY.md`](37-TEMPLATE-REUSE-INVENTORY.md),
[`41-TEMPLATE-DECISION-BRIEF.md`](41-TEMPLATE-DECISION-BRIEF.md) and
[`43-ROLE-VOCABULARY-AND-RECUT.md`](43-ROLE-VOCABULARY-AND-RECUT.md). Every count below was
re-derived from `planning/domains/nodes/*.json` at the commit named in the appendix; nothing is
carried over on trust.

> ### ⚠️ Two numbers in the brief that commissioned this draft are now stale
>
> **1. The live-field count is 30, not 31.** Commit `b2dbb08` ("fix account_holder"), which landed
> *during* this pass, moved `account_holder` out of `finance.json`'s `fields` and into its
> `proposed_fields`. Finance now declares **four** live fields — `institution`, `account_type`,
> `tax_year`, `record_type` — and `account_holder` is a proposal, not a field. Nothing in this draft
> ever wanted it as a level (00 forbids it), so **no template changes**; but any document still
> saying "31 live fields" or "finance: 5" is describing a corpus that no longer exists.
>
> **2. The serialized key is `schema_id`, not `uses_schema`.** In the catalogue JSON the join key is
> spelled `schema_id` on all 358 node files; `_CONTRACT.md`'s own correction of 2026-08-27 says so
> and says not to rename the files. In the built Python record the attribute *is*
> `TemplateApplicability.uses_schema`. Both spellings are correct in their own layer. This draft
> writes `uses_schema` when it means the record field and `schema_id` when it means the catalogue row.
>
> **The 54 did not move.** Re-derived after both changes: still exactly 54.

---

## 0. The answer, before the evidence

| | |
|---|---:|
| Bindable template rows (§1) | **54** |
| Field-declaring schemas | **6** |
| Live fields across them | **30** |
| Of those, fields that may never be a folder level | **6** |
| Distinct destination-eligible keys, all of them used | **22** |
| Distinct role sequences the 54 rows produce | **32** |
| **`TemplateDefinition` records proposed** | **29** (21 if you decline Judgment Call 1) |
| **`TemplateApplicability` records proposed** | **54** — one per row, always |
| **Shared `TemplateFragment` records** (reuse, 2+ schemas) | **3** |
| Order-carrier fragments the built composition path forces (Judgment Call 2) | **19** |
| Definitions serving more than one schema | **2** (one serves three) |
| Candidate orders I had to author because the corpus attests only one | **10** |

**Six things need the owner and cannot be settled here** — §8. Everything else in this document is
mechanical once those six are answered.

**Three findings came out of running the built code rather than reading it** (§3.4, verified in the
appendix): a definition that references no fragment *raises* at composition time; a
definition-local dimension carries no ordering constraint and sorts last; and the three shared
fragments, merged, derive 00's own Academic order `school → term → course → work type` with no
further input. The first two are why §3 has two tiers of fragment. The third is the strongest
evidence in this document that the role vocabulary is right.

---

## 1. The 54 bindable rows, re-derived

### 1.1 How 54 falls out

Not a hand-count. Three filters, in order, over all 358 node files:

```
358 node files
  ├─  23 kind:schema
  └─ 335 kind:template
       ├─ 278 whose schema_id names a schema with NO live fields  → GATED, wave 2
       └─  57 whose schema_id names one of the six field-declaring schemas
            ├─   3 carrying refuse_node: true                     → produce no node at all
            └─  54 BINDABLE                                       ← this document
```

The three refusals are `code.scratch-prototypes`, `code.software-project` and
`research.project-workspace`. All three carry an **empty** `dimension_order`: they exist to record
that the situation must *not* open a folder level (a preserved project root is structure 00 says to
leave alone), not to organize anything. They are correctly excluded, and excluding them is not a
loss — it is the catalogue working.

Verified mechanically over the 54: **dimension tokens that are not a live, destination-eligible
field of the row's own schema: 0. Bindable rows with an empty order: 0.** Nothing needs a field
invented, and nothing is unmapped.

### 1.2 The six schemas and their fields

| Schema | Live fields | Destination-eligible (may be a folder level) | Declared but **never** a level, by design |
|---|---:|---|---|
| `academic` | 5 | `school` · `term` · `subject` · `work_type` | `instructor` |
| `code` | 4 | `project` · `repository` · `artifact_type` | `programming_language` |
| `college_applications` | 5 | `target_university` · `application_cycle` · `application_document_type` · `purpose` | `school` |
| `finance` | 4 | `institution` · `account_type` · `tax_year` · `record_type` | — |
| `photos` | 6 | `capture_year` · `event` · `location` · `media_type` | `people` · `camera_information` |
| `research` | 6 | `project` · `stage` · `artifact_type` · `lab` · `venue` | `authored_by` |
| | **30** | 24 slots = **22 distinct keys** (`project` and `artifact_type` each serve two schemas) | **6** |

The six exclusions are not omissions. Five of them are 00's own rule — *"It should avoid using
authorship or creator identity as a destination dimension. A folder should not become a collection
point for everything produced by the same person or organization"* — applied to `instructor`,
`authored_by`, `people`, `camera_information` and `programming_language`. The sixth is a role
separation: `college_applications` declares `school` (the applicant's own school, which appears on
a transcript inside the packet) and forbids it as a level, because the addressee is
`target_university` and merging the two is the one merge 00 names outright.

**Every one of the 22 destination-eligible keys is used by at least one of the 54 rows. None is
unused, and no row uses anything else.**

### 1.3 The 54 rows

Ordered by schema, then by id. "Order" is the row's own `template.dimension_order` — the
recommendation it landed, not a path.

**`academic` — 11 rows**

| # | Row | Order |
|---:|---|---|
| 1 | `academic.continuing-education` | school › subject › work_type |
| 2 | `academic.coursework` | school › term › subject › work_type |
| 3 | `academic.homeschool` | term › subject › work_type |
| 4 | `academic.iep-accommodation-plans` | school › term |
| 5 | `academic.k12-schooling` | school › term › work_type |
| 6 | `academic.online-course` | school › subject › work_type |
| 7 | `academic.recommendation-letters-written` | term › work_type |
| 8 | `academic.standardized-testing` | subject › work_type |
| 9 | `academic.study-abroad` | school › subject › work_type |
| 10 | `academic.teaching` | term › subject › work_type |
| 11 | `academic.transcripts-credentials` | school › work_type |

**`code` — 3 rows**

| # | Row | Order |
|---:|---|---|
| 12 | `code.dotfiles-environment` | repository › artifact_type |
| 13 | `code.notebooks-experiments` | project › artifact_type |
| 14 | `code.pkm-vault` | project |

**`college_applications` — 5 rows**

| # | Row | Order |
|---:|---|---|
| 15 | `applications.graduate-professional` | target_university › application_document_type |
| 16 | `applications.k12-admission` | target_university › application_document_type |
| 17 | `applications.purpose-packet` | purpose |
| 18 | `applications.scholarship-fellowship` | application_cycle › application_document_type › target_university |
| 19 | `applications.undergraduate-packet` | target_university › application_cycle › application_document_type |

**`finance` — 18 rows**

| # | Row | Order |
|---:|---|---|
| 20 | `finance.cap-table-equity` | institution › record_type |
| 21 | `finance.crypto-assets` | institution › record_type |
| 22 | `finance.hoa-residents-association` | institution › record_type |
| 23 | `finance.household-property` | record_type |
| 24 | `finance.insurance-corporate` | institution › account_type › record_type |
| 25 | `finance.insurance-healthcare` | institution › record_type |
| 26 | `finance.insurance-personal` | institution › record_type |
| 27 | `finance.investment-brokerage` | institution › account_type › record_type |
| 28 | `finance.loans-mortgage` | account_type › record_type |
| 29 | `finance.payroll-received` | institution › tax_year › record_type |
| 30 | `finance.personal-records` | institution › account_type › record_type |
| 31 | `finance.receipts-expenses` | institution › record_type |
| 32 | `finance.small-business-bookkeeping` | record_type › account_type |
| 33 | `finance.student-financial-aid` | institution › record_type |
| 34 | `finance.subscriptions-utilities` | institution › record_type |
| 35 | `finance.tax-filings` | tax_year › record_type |
| 36 | `finance.vehicle-records` | record_type |
| 37 | `travel.bookings-confirmations` | record_type › institution |

**`photos` — 9 rows**

| # | Row | Order |
|---:|---|---|
| 38 | `photos.camera-events` | capture_year › event |
| 39 | `photos.drone-captures` | capture_year › event |
| 40 | `photos.family-archive` | event › capture_year |
| 41 | `photos.home-video` | capture_year › event |
| 42 | `photos.messenger-export` | capture_year |
| 43 | `photos.scanned-documents` | media_type › capture_year |
| 44 | `photos.screenshot-captures` | media_type › capture_year |
| 45 | `photos.social-media-export` | capture_year › event › media_type |
| 46 | `travel.trip-photos` | event › location |

**`research` — 8 rows**

| # | Row | Order |
|---:|---|---|
| 47 | `research.conference-presentation` | venue › project › artifact_type |
| 48 | `research.dataset-analysis` | project › artifact_type › stage |
| 49 | `research.ethics-compliance` | project › artifact_type |
| 50 | `research.grants-funding` | project › stage |
| 51 | `research.lab-notebook-protocols` | lab › project › artifact_type |
| 52 | `research.manuscript-publication` | project › venue › stage |
| 53 | `research.reading-library` | project › artifact_type |
| 54 | `research.thesis-dissertation` | project › artifact_type › stage |

> **Two rows are named for a domain they do not bind.** `travel.bookings-confirmations` binds
> `finance`; `travel.trip-photos` binds `photos`. Under the six approved top-level names they surface
> under **Finance** and **Photos**, and a user who thinks of them as travel will not find them there.
> That is Judgment Call **6**.

---

## 2. The role vocabulary this draft uses

Roles are organization-layer names. They are **not** facts and never become facts — P10 gate C2:
*"Every resolved dimension maps to a P6 field; template roles never become facts."* Each role below
maps back, through an applicability row, to a field that row's **one** schema declares.

The vocabulary is the 15 published in `41` §2.3, unchanged.
[`43-ROLE-VOCABULARY-AND-RECUT.md`](43-ROLE-VOCABULARY-AND-RECUT.md) §6.1 verified mechanically that
**zero of the 54 bound rows uses any of the 12 roles added at full corpus** — the 15 are exactly the
launch vocabulary, and the additions are a wave-2 concern. I re-derived it and reach the same place:
all 22 dimension tokens across the 54 rows map to one of the 15, and none is unmapped.

| Role | Fields it binds, per schema |
|---|---|
| `artifact_kind` | academic `work_type` · code/research `artifact_type` · finance `record_type` · applications `application_document_type` |
| `subject_anchor` | academic `subject` · code/research `project` |
| `holder_institution` | academic `school` · research `lab` |
| `cycle_period` | academic `term` · applications `application_cycle` |
| `addressed_org` | applications `target_university` · research `venue` |
| `issuing_org` | finance `institution` |
| `account_kind` | finance `account_type` |
| `scope_period` | finance `tax_year` |
| `capture_time` | photos `capture_year` |
| `occasion_anchor` | photos `event` |
| `capture_kind` | photos `media_type` |
| `place` | photos `location` |
| `lifecycle_stage` | research `stage` |
| `repository_instance` | code `repository` |
| `purpose_anchor` | applications `purpose` |

**The three role names that must never collapse into one "organization" role** — 00: *"The system
must separate roles that happen to contain the same entity type."* `holder_institution` is the school
you attend or the lab you work in; `addressed_org` is the university you apply to or the journal you
submit to; `issuing_org` is the bank that issued the statement. Merging any pair produces a bigger
apparent recipe and a wrong tree. `finance.insurance-corporate` states the consequence in both
directions: *"a certificate holder must never fill institution, and a carrier must never fill client."*

### 2.1 The 32 role sequences the 54 rows actually produce

Re-derived. `37` reported 31; my count is **32**, and I report mine rather than adopt theirs. The
distribution is the important part:

| Sequence | Rows | Schemas |
|---|---:|---|
| `issuing_org › artifact_kind` | 8 | finance |
| `holder_institution › subject_anchor › artifact_kind` | 4 | academic, research |
| `subject_anchor › artifact_kind` | 4 | academic, code, research |
| `capture_time › occasion_anchor` | 3 | photos |
| `issuing_org › account_kind › artifact_kind` | 3 | finance |
| `addressed_org › artifact_kind` | 2 | applications |
| `artifact_kind` | 2 | finance |
| `capture_kind › capture_time` | 2 | photos |
| `cycle_period › subject_anchor › artifact_kind` | 2 | academic |
| `subject_anchor › artifact_kind › lifecycle_stage` | 2 | research |
| *(22 further sequences, one row each)* | 22 | — |

---

## 3. The fragments

A `TemplateFragment` is reusable organization logic: roles, a partial order between them,
optionality, metadata-only roles, a privacy floor, and provenance. **It holds no user value and no
field mapping, and it creates no node.**

### 3.1 Tier 1 — the three shared fragments

These are the reuse claim. Each clears the handoff's bar — *"at least two reviewed contexts share
stable semantics and compatible constraints"* — at **two or more schemas**, with the direction
argued in the rows' own words rather than merely observed.

#### `frag.subject-then-artifact@1` — RANK 1

```
roles                (subject_anchor, artifact_kind)
relative_order       subject_anchor → artifact_kind
optional_roles       ()                       both required where the fragment is included
metadata_only_roles  ()
privacy_floor        baseline                 see Judgment Call 3
provenance           ("academic", "research", "code")
```

**Reach: 3 schemas, 14 of the 54 rows, zero counter-attestations.** Every context argues from the
same 00 sentence: *"a parent dimension should provide the context required to understand the
child"*, and its worked instance, *"A work type such as Homework 3 is meaningful only after the
course is known."*

Rows: `academic.coursework`, `academic.continuing-education`, `academic.online-course`,
`academic.study-abroad`, `academic.standardized-testing`, `academic.homeschool`, `academic.teaching`,
`research.ethics-compliance`, `research.reading-library`, `research.lab-notebook-protocols`,
`research.dataset-analysis`, `research.thesis-dissertation`, `research.conference-presentation`,
`code.notebooks-experiments`.

`43` §4.2 re-ran this at full corpus and it grows rather than shrinks: **30 rows across 9 domains,
zero reversals.** It is one of only four pairs in the entire 256-row corpus with no counter-example
anywhere, in either direction, adjacent or at distance.

#### `frag.holder-affiliation-prefix@1` — RANK 2

```
roles                (holder_institution, subject_anchor)
relative_order       holder_institution → subject_anchor
optional_roles       (holder_institution,)    the prefix is offered, never imposed
privacy_floor        baseline
provenance           ("academic", "research")
```

**Reach: 2 schemas, 5 rows where both roles bind** (4 of them adjacent). `holder_institution`
precedes `subject_anchor` 5/5 and precedes `artifact_kind` 7/7, with zero reversals.

`academic.continuing-education`: *"school comes first because the provider is what makes a prose
course title intelligible and disambiguable."* `research.lab-notebook-protocols`: *"lab BEFORE
project, because bench material's stable owner is the lab and its project association is often
absent or plural."*

**The hard constraint this fragment must carry:** `holder_institution` may **never** bind to
`target_university`, `venue` or `institution`. Eleven authored `target_university ↔ school`
role-splits across the corpus enforce it.

> `41` §3 offered to cut this fragment as the weakest of the three. **Do not.** That offer was made
> on a 6-domain sample; at full corpus it is 11 rows across 5 domains with zero counter-examples
> (`43` §4.2 #6, `42` §0). `41` carries the correction inline.

#### `frag.cycle-then-artifact@1` — RANK 3

```
roles                (cycle_period, artifact_kind)
relative_order       cycle_period → artifact_kind
optional_roles       (cycle_period,)
privacy_floor        baseline
provenance           ("academic", "college_applications")
```

**Reach: 2 schemas, 7 rows where both roles bind.** `cycle_period` precedes `artifact_kind` 7/7.

**What it must NOT assert:** the position of `cycle_period` relative to an *organization* role is
unresolved at 1-for-1 (`applications.undergraduate-packet` puts the addressee above the cycle;
`applications.scholarship-fellowship` puts it below both). The fragment fixes
`cycle_period < artifact_kind` and asserts nothing else. That is why both readings can ship as
**candidate orders of one definition** rather than as two definitions — §4, `def.addressee-packet`.

The drop rationale it carries: `applications.k12-admission` — *"a cycle level beneath each school
produces exactly one child, which is what 00 tells the canvas to warn about."*

### 3.2 What was tested as a fourth shared fragment and refused

| Near-miss | The statistic that tempted | Why refused |
|---|---|---|
| `counterparty → artifact_kind`, merging issuer with addressee | 10 rows, 2 schemas | 00's forbidden merge. Split correctly: 8 finance rows + 2 applications rows — **both single-schema.** The cross-schema claim was an artefact of the merge. |
| `container → artifact_kind`, merging `repository` with `account_type` | 5 rows, 2 schemas | A named instance versus a category. `repository` = *"the source repository a code file belongs to"*; `account_type` = *"the **kind** of account"*. Different one-child hazards, different value vocabularies. |
| `capture_time → occasion_anchor` | 4 rows, one direction dominant | All contexts are `photos`, and the sequence is verbatim `photos.json`'s own default. Zero reuse gained. It is the photos schema's template — see Tier 2. |
| `issuer → record` | 11 rows — the biggest single cluster in the launch set | `finance` only, and verbatim `finance.json`'s default. It is the finance schema's template — see Tier 2. |
| `project → stage → artifact kind` (00 §5.4's own Research order) | 00 states it | **Zero of the 54 rows realize it.** Both research rows that carry all three levels invert the last two and argue the inversion. It ships as a candidate *order*, not as a fragment — §4, `def.research-lineage`. |

**`matter_anchor › artifact_kind`** — 51 rows across 10 domains, zero reversals, the largest recipe
in the whole corpus (`43` §4.2 #1) — **cannot bind at launch**: it needs a role no live field
carries. It is wave 2, and it is the reason `41`'s *"there is no fourth"* must not be read as settled.

### 3.3 Tier 2 — the 19 order-carrier fragments, and why they exist

**They are not a reuse claim.** They exist because of §3.4's two findings. Nineteen definitions
either have no Tier-1 coverage at all, or need one ordering edge Tier 1 does not supply.

| Carrier fragment | Roles and edges | Definitions it serves | Rows |
|---|---|---|---:|
| `frag.affiliation-prefix-to-cycle@1` | holder_institution → cycle_period | D01 D02 D03 D05 D06 D07 D08 | 14 |
| `frag.issuer-then-record@1` | issuing_org → account_kind → artifact_kind | D14 | 11 |
| `frag.issuer-then-period-then-record@1` | issuing_org → scope_period → artifact_kind | D15 | 1 |
| `frag.period-then-record@1` | scope_period → artifact_kind → issuing_org | D16 | 1 |
| `frag.loan-kind-then-record@1` | account_kind → issuing_org → artifact_kind | D17 | 1 |
| `frag.function-then-container@1` | artifact_kind → account_kind | D18 | 1 |
| `frag.function-then-issuer@1` | artifact_kind → issuing_org | D19 | 1 |
| `frag.record-kind-only@1` | artifact_kind (no edge) | D20 | 2 |
| `frag.capture-time-then-occasion@1` | capture_time → occasion_anchor → capture_kind | D21 D22 | 6 |
| `frag.capture-kind-then-time@1` | capture_kind → capture_time | D23 D24 | 2 |
| `frag.occasion-then-place@1` | occasion_anchor → place → capture_time | D25 | 1 |
| `frag.addressee-prefix@1` | addressed_org → cycle_period | D11 D12 | 4 |
| `frag.purpose-only@1` | purpose_anchor (no edge) | D13 | 1 |
| `frag.preserved-root@1` | subject_anchor (no edge) | D09 | 1 |
| `frag.container-then-artifact@1` | repository_instance → artifact_kind | D10 | 1 |
| `frag.subject-then-stage@1` | subject_anchor → lifecycle_stage | D27 | 1 |
| `frag.artifact-then-stage@1` | artifact_kind → lifecycle_stage | D26 | 2 |
| `frag.venue-in-submission-chain@1` | subject_anchor → addressed_org → lifecycle_stage | D28 | 1 |
| `frag.venue-prefix@1` | addressed_org → subject_anchor | D29 | 1 |

Each carrier's `provenance` names the one context that produced it, honestly — a carrier claiming
two contexts it does not have would be exactly the padding the 36 refused rows refused.

### 3.4 Why Tier 2 exists — three facts about the built code, verified by running it

I ran these rather than read them. Reproduction is in the appendix.

**(a) A definition that references no fragment raises at composition time.**
`merge_fragment_constraints([])` reaches `max([])` on the privacy-floor list and raises
`ConfigurationRequired: "no ordering is available for the privacy floors []"`. So
`fragment_refs` is effectively mandatory even though `TemplateDefinition.__post_init__` does not say
so. Eleven of the 54 rows sit on one finance definition that would have had no fragment at all.

**(b) A definition-local dimension carries no ordering constraint and sorts last.** The merge derives
`ordered_roles` from fragment `relative_order` only, and `routing.py:272` positions any role the
merge did not see with `position.get(role, len(position))` — the end, with ties. Demonstrated:

```
definition default:  addressed_org > subject_anchor > artifact_kind
fragments supply:    subject_anchor → artifact_kind
router nests:        subject_anchor > artifact_kind > addressed_org     ← the venue moves to the leaf
```

That is `research.conference-presentation`'s recipe inverted by the composer. The fix inside the
current records is `frag.venue-prefix@1`; the fix outside them is Judgment Call **2**.

**(c) The three shared fragments, merged, derive 00's Academic order with no further input.**

```
merge(frag.subject-then-artifact, frag.holder-affiliation-prefix, frag.cycle-then-artifact)
  → holder_institution > cycle_period > subject_anchor > artifact_kind
  → school            > term          > course         > work type
  → optional roles: cycle_period, holder_institution
```

00: *"An Academic template may define school → term → course → work type."* Nobody wrote that order
into a fragment; three independently-argued pairwise constraints produce it. That is the single
best piece of evidence in this document that the role cut is right.

**A rule I applied because of (b):** for every definition, **the default candidate order equals the
order the fragments derive.** A user who takes the default needs no override; a user who takes an
alternative supplies it as a `role_order` at bind time and the binding records which through
`chosen_order_id`. Where I could not satisfy this rule, I say so.

---

## 4. The 29 template definitions

### 4.0 The two rules that produced this cut

**Rule A — depth is not identity.** A row that drops a level while preserving the relative order of
the levels it keeps is the **same recipe at a shallower depth**, not a different one. It becomes one
applicability row against a definition where that role is `optional`, and the omission is a runtime
`omitted` action. This is the handoff's own step 4: *"Definitions carry recommended order, not
mandatory depth."* It is what keeps 54 rows at 29 definitions instead of 32.

**Rule B — a different data subject is a different definition.** Where a row's own
`sensitivity_why` says the substantive material is about someone who is **not** the holder, it does
not share a definition with a row that holds the holder's own record — even when the shape is
identical. `academic.coursework`: *"this situation holds the holder's own record and should not
accumulate other people's."* `academic.teaching`: *"This situation routinely holds other people's
data."* Same recipe, opposite exposure.

Rule B is **Judgment Call 1** and it is the only thing standing between 29 definitions and 21.
It is forced by the record shape: `TemplateApplicability` — the per-schema, per-context row — carries
**no privacy field at all**. The only homes for privacy in the built records are
`TemplateFragment.privacy_floor` and `TemplateDefinition.sensitivity_policy_ref`. A floor on a shared
fragment over-restricts every context it reaches (it would put `research.reading-library`, whose
`sensitivity` is literally `none`, under a floor written for a file of other people's grades). So the
exposure difference has nowhere to live except the definition.

**The four policy refs this draft uses.** These are *references to authored policy records*, not P7
handling classes — `_CONTRACT.md` rule 5 reserves that vocabulary, and this draft does not touch it.
Each is named for the distinction a row itself drew.

| Ref | What it means | Rows |
|---|---|---:|
| `sp.holder-own-record@1` | the holder is the subject | 22 |
| `sp.safety-domain-protected@1` | the schema is a safety domain; protection precedes any placement path | 18 (all finance) |
| `sp.third-party-confidential@1` | the substantive material is about, or written by, people outside the household | 7 |
| `sp.household-member-record@1` | the subject is a household member, usually a minor | 4 |
| `sp.not-holder-personal@1` | published third-party work; no personal content | 1 |
| `sp.credential-bearing@1` | the ordinary member of the set *is* the credential | 1 |
| `sp.document-reproduced-whole@1` | the capture carries the whole document's content | 1 |

### 4.1 Family A — subject then kind (academic + research + code)

Roles: `holder_institution`(opt) · `cycle_period`(opt) · `subject_anchor`(req) · `artifact_kind`(req)
Fragments: `frag.holder-affiliation-prefix@1` + `frag.cycle-then-artifact@1` +
`frag.subject-then-artifact@1` + `frag.affiliation-prefix-to-cycle@1`
Derived order = `holder_institution › cycle_period › subject_anchor › artifact_kind` (§3.4c)

---

#### **D01 · `def.subject-work-record@1`** — `scope_kind: cross-domain` · `sp.holder-own-record@1`

**The headline. One definition, three schemas, seven rows, zero shared data.**

| Candidate order | Nesting | Attested by |
|---|---|---|
| **`ord.affiliation-period-subject-kind`** ★ DEFAULT | holder_institution › cycle_period › subject_anchor › artifact_kind | 00 verbatim: *"An Academic template may define school → term → course → work type"*; `academic.coursework` |
| `ord.affiliation-subject-period-kind` | holder_institution › subject_anchor › cycle_period › artifact_kind | 00 §5.5's own Option B path, `Academics/BUSIB 4300/Spring 2026/Syllabus`, with the school retained rather than dropped |
| `ord.subject-affiliation-period-kind` | subject_anchor › holder_institution › cycle_period › artifact_kind | `academic.continuing-education` verbatim: *"one who browses by topic will reverse to subject → school"* |

**Why the default is the first.** A course code recurs every term and the term is what keeps two
enrolments apart — `academic.coursework`: *"a course code recurs every term and the term is what
keeps two enrolments apart."* Putting the subject above the school is what 00 names the risk of:
*"Option B would merge material across schools when course codes collide."* And the pair the second
and third orders break — `holder_institution › subject_anchor` — is attested 5/5 with zero
reversals in the launch set and 11/11 at full corpus.

Note that 00's Option B *also drops the school*. A candidate order may not drop a role (the record
refuses it: *"An order that drops or adds a role is a different RECIPE"*), so the dropping half is a
runtime `omitted` action and the reordering half is the candidate order. Both together reproduce 00's
path exactly.

**Rows served (7):**

| Row | Schema | Roles it binds | Levels it omits, and why in its own words |
|---|---|---|---|
| `academic.coursework` | academic | all four | — (the full recipe) |
| `academic.continuing-education` | academic | hi, sa, ak | `term` — *"the academic-term rule family cannot fire on material that has no semester"* |
| `academic.online-course` | academic | hi, sa, ak | `term` — *"self-paced platform study routinely produces no term evidence at all"* |
| `academic.study-abroad` | academic | hi, sa, ak | `term` — *"one host institution and usually one term, so a term level under it produces a single child"* |
| `academic.standardized-testing` | academic | sa, ak | `school` (*"no institution in these files occupies the school role"*), `term` (*"a test date is not a term"*) |
| `research.lab-notebook-protocols` | research | hi, sa, ak | `stage` is not a role here; research has no time field to fill `cycle_period` |
| `code.notebooks-experiments` | code | sa, ak | `repository` is *"absent BY DEFINITION of this situation"*; code has no `holder_institution` or time field |

`example_label_chains`: `("Columbia", "2026-Spring", "PHYS1401", "Homework")` ·
`("Chen Lab", "PVA-RDP", "protocol")` · `("graphify", "notebook")`

`optional_branch_patterns`: *"insert `cycle_period` where a provider runs dated cohorts"* ·
*"flatten to `holder_institution › artifact_kind` for a professional with few certificates per
provider"* · *"a scoped `General` under the deepest resolved parent rather than a global Unsorted"*

`validation_constraints`: `holder_institution` may never bind `target_university`, `venue` or
`institution` · `instructor`, `authored_by` and `programming_language` may never become a level ·
where `subject_anchor` resolves to one value the level is flagged by V2 and flattened on the canvas,
not removed from the recipe.

---

#### **D02 · `def.subject-work-record.third-party@1`** — `cross-domain` · `sp.third-party-confidential@1`

**The second cross-schema definition: same fragments, opposite exposure.**

| Candidate order | Nesting | Attested by |
|---|---|---|
| **`ord.affiliation-period-subject-kind`** ★ | holder_institution › cycle_period › subject_anchor › artifact_kind | `academic.teaching`: *"Term stays ahead of subject because a teaching load is re-planned each term"* |
| `ord.affiliation-subject-period-kind` | holder_institution › subject_anchor › cycle_period › artifact_kind | `academic.teaching` verbatim: *"The reverse order (subject before term) is a legitimate user choice"* |

**Rows (2):** `academic.teaching` (binds cp, sa, ak — drops `school` because *"an instructor's
teaching corpus usually names one employing institution"*) · `research.ethics-compliance` (binds sa,
ak — drops `stage` because *"the ethics file for one study is small, most of its documents sit at
approved for years"*).

`validation_constraints`: no level may be a participant, a signature set, or any participant-derived
value · a roster, gradebook or consent-signature leaf is a *folder name* and a folder name is visible
where the file's contents are not.

---

#### **D03 · `def.subject-work-record.household@1`** — `domain-focused` · `sp.household-member-record@1`

| Candidate order | Nesting | Attested by |
|---|---|---|
| **`ord.affiliation-period-subject-kind`** ★ | holder_institution › cycle_period › subject_anchor › artifact_kind | `academic.homeschool`: *"Term leads because a homeschool year is the unit the household plans, logs and reports in"*; the prefix is its own optional pattern, *"`school` first for a household enrolled under an umbrella or cover school"* |
| `ord.affiliation-subject-period-kind` | holder_institution › subject_anchor › cycle_period › artifact_kind | **AUTHORED** — no row attests a reversal here; it is D01's second order carried across |

**Row (1):** `academic.homeschool`. The applicability row's expected shape **omits**
`holder_institution` by default: *"in a household-run situation there is usually no institution to
fill it"*, and *"a self-named home school on a parent-issued transcript (Torres Family Academy) is a
label the household invented, which no schools gazetteer will ever confirm."*

> This is the thinnest of the four Family-A splits — one row. If you decline Judgment Call 1, it
> merges into D01. If you accept Judgment Call 1 but read a homeschooling parent's own children as
> not "third parties", it merges into D02. Both are defensible; the row itself calls the underlying
> question *"Joseph's call, not this node's."*

---

#### **D04 · `def.reading-shelf@1`** — `domain-focused` · `sp.not-holder-personal@1`

| Candidate order | Nesting | Attested by |
|---|---|---|
| **`ord.project-then-kind`** ★ | subject_anchor › artifact_kind | `research.reading-library`: *"project leads because it is the only association that makes somebody else's paper filable inside the holder's tree at all"* |
| `ord.kind-then-project` | artifact_kind › subject_anchor | the row's own optional pattern (b): *"artifact_type-first, for a reader who separates books from papers before anything else"* |

**Row (1):** `research.reading-library` — the only one of the 54 whose `sensitivity` is `none`.

`validation_constraints`, from the row verbatim: *"When no project association is evidenced on the
file, the branch has no first level and the honest destination is the Reading Inbox residual, not a
deeper path invented to fill the shape."* · `venue` is legal here and is **never** a level — *"branching
on it produces one folder per journal over a long tail of single papers"* · `lab` is worse — *"for a
paper by others, the affiliation describes its authors, and an author-or-affiliation level is the
collector 00 forbids outright."*

### 4.2 Family B — an institution-issued record with no subject (academic)

Roles: `holder_institution` · `cycle_period` · `artifact_kind`
Fragments: `frag.affiliation-prefix-to-cycle@1` + `frag.cycle-then-artifact@1`
Derived order = `holder_institution › cycle_period › artifact_kind`

The subject is absent **by construction**, not by shortage: an official record enumerates many
courses across many terms inside one file, so choosing one as its folder level would be inventing a
value the document does not assert.

#### **D05 · `def.institution-issued-record@1`** — `sp.holder-own-record@1`

| Candidate order | Nesting | Attested by |
|---|---|---|
| **`ord.issuer-period-kind`** ★ | holder_institution › cycle_period › artifact_kind | `academic.transcripts-credentials`: *"a folder named Transcript means nothing until the institution that issued it is known, while Columbia/Transcript is complete"*; the row's own optional pattern restores `term` *"where a record does cover exactly one term"* |
| `ord.kind-issuer-period` | artifact_kind › holder_institution › cycle_period | **AUTHORED** — for a holder who looks for "my diplomas" before "my Columbia things" |

**Row (1):** `academic.transcripts-credentials` (binds hi, ak).

#### **D06 · `def.household-school-record@1`** — `sp.household-member-record@1`

| Candidate order | Nesting | Attested by |
|---|---|---|
| **`ord.school-year-kind`** ★ | holder_institution › cycle_period › artifact_kind | `academic.k12-schooling`: *"school stays first because the school is what makes a marking period intelligible"* |
| `ord.year-school-kind` | cycle_period › holder_institution › artifact_kind | **AUTHORED** — for a household whose child changed schools inside one school year |

**Row (1):** `academic.k12-schooling`. The row states plainly that *"The order this situation actually
wants is child → school year → work type, and no declared field names the child"* — that is
**Judgment Call 5**.

#### **D07 · `def.evaluative-letters@1`** — `sp.third-party-confidential@1`

Roles: `cycle_period`(req) · `artifact_kind`(req). Fragment: `frag.cycle-then-artifact@1`.

| Candidate order | Nesting | Attested by |
|---|---|---|
| **`ord.cycle-then-kind`** ★ | cycle_period › artifact_kind | `academic.recommendation-letters-written`: *"term leads because the writing cycle is the batch a recommender actually re-finds"* |
| `ord.kind-then-cycle` | artifact_kind › cycle_period | the row verbatim: *"The reverse order (work_type before term) is a legitimate user choice and is recorded in this node's research notes"* |

**Row (1):** `academic.recommendation-letters-written`. `school` is dropped — *"a recommender writes
from one employing institution"* — and `subject` is dropped because *"the course in which the writer
taught one applicant is sparse in these files and, where present, yields a folder holding a single
letter."* No dimension names the person a letter is about, and none may.

#### **D08 · `def.protected-plan-record@1`** — `sp.household-member-record@1`

Roles: `holder_institution`(req) · `cycle_period`(req). Fragment: `frag.affiliation-prefix-to-cycle@1`.

| Candidate order | Nesting | Attested by |
|---|---|---|
| **`ord.school-then-year`** ★ | holder_institution › cycle_period | `academic.iep-accommodation-plans`: *"a plan is issued and administered by one school and a change of school is the real break in this material"* |
| `ord.year-then-school` | cycle_period › holder_institution | **AUTHORED** |

**Row (1):** `academic.iep-accommodation-plans`. **`artifact_kind` is not a role of this definition
and is recorded as an `exclusion` on the applicability row.** The row's reason, verbatim: its values
*"(iep, 504 plan, eligibility determination, evaluation report) would publish a named child's
disability determination as a visible folder label, in a namespace Finder, Spotlight, backup tools
and sync clients all read."* The `work_type` fact still extracts and still drives search; it is
simply never a level. This is the one place in the launch set where a privacy rule removes a
dimension rather than restricting a file, and it is why D08 cannot merge into D06.

### 4.3 Family C — code

#### **D09 · `def.preserved-root@1`** — `domain-focused` · `sp.holder-own-record@1`
Role: `subject_anchor`(req) only. Fragment: `frag.preserved-root@1`. **One** candidate order, which
the record permits for a single-role recipe.

`ord.project-only` ★ — `subject_anchor`. **Row (1):** `code.pkm-vault`, whose own words are *"One
dimension, deliberately"*, because 00 says *"Existing folders must not be automatically flattened,
renamed, or reorganized simply because a template would produce a different structure."*

#### **D10 · `def.container-artifact@1`** — `domain-focused` · `sp.credential-bearing@1`
Roles: `repository_instance`(req) · `artifact_kind`(req). Fragment: `frag.container-then-artifact@1`.

| Candidate order | Nesting | Attested by |
|---|---|---|
| **`ord.collection-then-kind`** ★ | repository_instance › artifact_kind | `code.dotfiles-environment`: *"A branch whose label is the bare value environment file is unreadable on its own; under the collection that holds it, it is a machine's environment"* |
| `ord.kind-then-collection` | artifact_kind › repository_instance | **AUTHORED** |

**Row (1):** `code.dotfiles-environment`. Its own honest default is shallower than either order —
*"for the very common case of a handful of loose dotfiles with no collection above them, the honest
recommendation is to flatten to nothing and leave them where they are"*, because *"A dotfile that the
machine reads from a fixed location… moving it breaks the tool that reads it."* That is
**Judgment Call 4**.

### 4.4 Family D — college applications

#### **D11 · `def.addressee-packet@1`** — `domain-focused` · `sp.holder-own-record@1`

Roles: `addressed_org`(req) · `cycle_period`(opt) · `artifact_kind`(req).
Fragments: `frag.addressee-prefix@1` + `frag.cycle-then-artifact@1`.

**This is the definition that proves candidate orders earn their place.** Two rows landed with
opposite orders over the *same three roles*, both argued, and 00 refuses to choose between them:
*"the product should not assume that all applications are best organized in the same way."* Under a
single frozen ordering one of them would have to be wrong. Under `candidate_orders` they are one
recipe with two shipped options.

| Candidate order | Nesting | Attested by |
|---|---|---|
| **`ord.addressee-cycle-kind`** ★ | addressed_org › cycle_period › artifact_kind | 00 verbatim: *"an Applications template may define target institution → application cycle → document type"*, producing *"Applications/UChicago/2026/Supplemental Essays"*; `applications.undergraduate-packet` |
| `ord.cycle-kind-addressee` | cycle_period › artifact_kind › addressed_org | `applications.scholarship-fellowship`: *"one applicant addresses many sponsors in one season, most of them receiving one essay and one form"* — institution-first there gives a shelf of one-file folders |

**Why the default is the first.** 00 states it; and the row that reverses it flags its own reversal
rather than asserting it: *"this order should be treated as a recommendation to test, not a
finding."*

**Rows served (3):** `applications.undergraduate-packet` (all three) ·
`applications.graduate-professional` (ao, ak — drops the cycle: *"a CV, a writing sample, a
transcript and a score report carry no cycle, and a graduate applicant usually has one"*) ·
`applications.scholarship-fellowship` (all three, taking the second order).

`example_label_chains`: `("UChicago", "2026", "Supplemental Essays")` ·
`("2026", "Personal Statement", "Coca-Cola Scholars")`

`validation_constraints`: `school` is declared by this schema and may **never** be a level ·
a shared supporting document attached to several packets never inherits an addressee — 00: *"If no
shared branch exists, the system should not arbitrarily choose one university. It should abstain or
ask the user to choose a primary home."*

#### **D12 · `def.addressee-packet.household@1`** — `sp.household-member-record@1`

| Candidate order | Nesting | Attested by |
|---|---|---|
| **`ord.addressee-cycle-kind`** ★ | addressed_org › cycle_period › artifact_kind | `applications.k12-admission`, which omits the cycle by default and says where to reinsert it: *"beneath target_university"* |
| `ord.cycle-addressee-kind` | cycle_period › addressed_org › artifact_kind | **AUTHORED** |

**Row (1):** `applications.k12-admission`.

#### **D13 · `def.purpose-packet@1`** — `scope_kind: purpose-focused` · `sp.holder-own-record@1`

Role: `purpose_anchor`(req) only. Fragment: `frag.purpose-only@1`. One candidate order.
**`purpose_profile_ref: pp.application-submission@1`** — the only row in the launch set that carries
one, and the one place 00 supplies the profile itself: *"an ID, transcript, resume, personal
statement, award certificate, and portal screenshot may be content-incoherent but purpose-coherent as
an application submission."*

`ord.purpose-only` ★ — `purpose_anchor`. 00: *"The user may keep it as one flat purpose folder."*

**Row (1):** `applications.purpose-packet`. Its own reasoning for why nothing else may lead:
`target_university` cannot, because *"this packet frequently has no single addressee"*;
`application_document_type` cannot, because *"a folder of loose Certificates is exactly the
fragmentation the flat packet exists to prevent."*

### 4.5 Family E — finance (18 rows, all `sp.safety-domain-protected@1`)

#### **D14 · `def.issuer-record@1`** — `domain-focused`

Roles: `issuing_org`(req) · `account_kind`(opt) · `artifact_kind`(req).
Fragment: `frag.issuer-then-record@1`. **The largest definition in the launch set: 11 rows.**

| Candidate order | Nesting | Attested by |
|---|---|---|
| **`ord.issuer-account-kind`** ★ | issuing_org › account_kind › artifact_kind | 11/11 rows put the issuer above the record kind; `finance.personal-records`: *"one institution commonly runs several accounts for the same person and a single statements folder would mix a checking account with a credit card"* |
| `ord.account-issuer-kind` | account_kind › issuing_org › artifact_kind | `finance.investment-brokerage` optional pattern (b): *"`account_type` ABOVE `institution` where a household holds one continuing retirement account across successive custodians, because a transfer changes the institution value while the account continues"*; `finance.insurance-personal` records the same shape for coverage lines — *"Auto/2026-Carrier/ retrieves better than Carrier/Auto/ for someone who has switched insurers twice"* |

**Rows (11):** with the middle level — `finance.personal-records`, `finance.insurance-corporate`,
`finance.investment-brokerage`. Without it (8) — `finance.cap-table-equity`,
`finance.crypto-assets`, `finance.hoa-residents-association`, `finance.insurance-healthcare`,
`finance.insurance-personal`, `finance.receipts-expenses`, `finance.student-financial-aid`,
`finance.subscriptions-utilities`.

Each of the eight argues the same drop: *"most households hold one line per carrier, so a
coverage-line level under each carrier would usually open a branch with a single child."*

`validation_constraints`: `tax_year` is destination-eligible and is **not** a standing level here —
*"most account records carry no labelled tax-year slot"* — but may be an **optional leaf under**
`artifact_kind`, never above `issuing_org`, and never filled from a statement period ·
`account_holder` is not a live field and would never be a level if it became one.

#### **D15 · `def.issuer-period-record@1`**
Roles: `issuing_org`(req) · `scope_period`(req) · `artifact_kind`(req). Fragment: `frag.issuer-then-period-then-record@1`.

| Candidate order | Nesting | Attested by |
|---|---|---|
| **`ord.issuer-year-kind`** ★ | issuing_org › scope_period › artifact_kind | `finance.payroll-received`: *"institution leads because Pay Statement, Correction or Annual Summary is not intelligible until the paying employer is known, and one person may have several employers in one year"* |
| `ord.year-issuer-kind` | scope_period › issuing_org › artifact_kind | **AUTHORED** — D16's shape applied here; the row does say `tax_year` *"keeps a long employer history navigable"* |

**Row (1):** `finance.payroll-received`. This is deliberately **not** a depth variant of D14: D14's
rows put `tax_year` *under* the record kind as an optional leaf; this row puts it *above*. Different
position is a different recipe.

#### **D16 · `def.period-scoped-filing@1`** — the one finance definition that is time-first
Roles: `scope_period`(req) · `artifact_kind`(req) · `issuing_org`(opt). Fragment: `frag.period-then-record@1`.

| Candidate order | Nesting | Attested by |
|---|---|---|
| **`ord.year-kind-issuer`** ★ | scope_period › artifact_kind › issuing_org | `finance.tax-filings`, which argues the exception rather than assuming it: *"Year-first scatters related work when the year is incidental to the document; it cannot scatter a filing, because the filing IS the year"* |
| `ord.kind-year-issuer` | artifact_kind › scope_period › issuing_org | attested **outside** the launch set: `artifact_kind › scope_period` is 32 rows across 8 domains in the unbound corpus (`43` §4.4 A) |

**Row (1):** `finance.tax-filings`. The row marks its own argument `inference`: *"That reasoning is
mine, not 00's."* 00 licenses exactly one exception to subject-before-time by name, and it is
capture media, not this. Shipping 00's direction as the second order is what keeps the departure
honest.

`validation_constraints`, from the row's open question: under a year-first order **a supporting
document with no year fact of its own has no legal branch** — a donation receipt, a childcare
invoice — because *"The graph does not automatically copy those missing facts onto sparse files."*
Those members land in a scoped `General` under the year, or in review. That consequence is real and
is **Judgment Call 5(b)**.

#### **D17 · `def.loan-kind-record@1`**
Roles: `account_kind`(req) · `issuing_org`(opt) · `artifact_kind`(req). Fragment: `frag.loan-kind-then-record@1`.

| Candidate order | Nesting | Attested by |
|---|---|---|
| **`ord.loan-kind-issuer-record`** ★ | account_kind › issuing_org › artifact_kind | `finance.loans-mortgage`: *"institution is offered as a level BETWEEN account_type and record_type, never above account_type"* |
| `ord.loan-kind-record-issuer` | account_kind › artifact_kind › issuing_org | **AUTHORED** |

**Row (1):** `finance.loans-mortgage`. `validation_constraints` carries the row's prohibition as a
constraint rather than a preference: **no candidate order may put `issuing_org` above
`account_kind`**, because *"One loan is commonly originated by one company, sold to a second, and
serviced by a third; institution-first scatters a single loan across sibling folders whose members
belong together."*

#### **D18 · `def.function-first-book@1`**
Roles: `artifact_kind`(req) · `account_kind`(opt). Fragment: `frag.function-then-container@1`.

| Candidate order | Nesting | Attested by |
|---|---|---|
| **`ord.function-then-account`** ★ | artifact_kind › account_kind | `finance.small-business-bookkeeping`: *"a general ledger, invoice register, expense report or receivables report refers to many banks and counterparties, while record_type states the function that makes the material intelligible"* |
| `ord.account-then-function` | account_kind › artifact_kind | **AUTHORED** |

**Row (1):** `finance.small-business-bookkeeping`. `issuing_org` is omitted for a reason that is 00's
own rule, not a preference: *"using the holder's own operation as the leading institution would turn
authorship-side identity into the collector 00 forbids."*

#### **D19 · `def.function-then-issuer@1`**
Roles: `artifact_kind`(req) · `issuing_org`(opt). Fragment: `frag.function-then-issuer@1`.

| Candidate order | Nesting | Attested by |
|---|---|---|
| **`ord.function-then-issuer`** ★ | artifact_kind › issuing_org | `travel.bookings-confirmations`: *"inside an accepted trip branch, boarding passes, lodging reservations, rail tickets and rental confirmations are intelligible functional children"* |
| `ord.issuer-then-function` | issuing_org › artifact_kind | the finance default, attested by 11 sibling rows; the row itself says these *"ordinarily use the Finance schema's issuing institution and record_type"* |

**Row (1):** `travel.bookings-confirmations`. Its desired parent — the trip — **cannot be
expressed**: *"the Finance schema cannot express it: the trip remains a P9 group or user-created
branch and is never smuggled into dimension_order."*

#### **D20 · `def.group-scoped-record@1`**
Role: `artifact_kind`(req) only. Fragment: `frag.record-kind-only@1`. One candidate order,
`ord.kind-only` ★.

**Rows (2):** `finance.household-property`, `finance.vehicle-records`. Both are **deliberately
scoped inside an accepted single-asset group** and both say the same thing: the useful order needs a
field that does not exist (`property`, `vehicle`), and *"this row does not smuggle an unratified
field into dimension_order."* `finance.vehicle-records`: *"institution-first scatters one vehicle
across issuers and record_type-first at the corpus root merges several vehicles."*

### 4.6 Family F — photos

#### **D21 · `def.capture-time-events@1`** — `sp.holder-own-record@1`
Roles: `capture_time`(req) · `occasion_anchor`(opt). Fragment: `frag.capture-time-then-occasion@1`.

| Candidate order | Nesting | Attested by |
|---|---|---|
| **`ord.year-then-event`** ★ | capture_time › occasion_anchor | 00 verbatim: *"a Photos template may define year → event"*, and its stated reason — *"Photos and capture-based media are the major exception: time often belongs first because capture date is a defining aspect of the material"* |
| `ord.event-then-year` | occasion_anchor › capture_time | 00's own menu: *"whether photographs should branch by year, event, location, or remain mostly flat"* |

**Rows (2):** `photos.camera-events`, `photos.drone-captures`.

`validation_constraints`: `people` and `camera_information` are not destination-eligible and never
become levels — *"It should avoid using authorship or creator identity as a destination dimension"*.

#### **D22 · `def.capture-time-events.third-party@1`** — `sp.third-party-confidential@1`
Roles: `capture_time`(req) · `occasion_anchor`(opt) · `capture_kind`(opt). Same fragment.

| Candidate order | Nesting | Attested by |
|---|---|---|
| **`ord.year-event-kind`** ★ | capture_time › occasion_anchor › capture_kind | `photos.home-video`, `photos.social-media-export` — the latter earns the third level: *"an account export returns stills, clips, uploaded screenshots and profile images in one bundle, so the leaf is genuinely multi-valued"* |
| `ord.event-year-kind` | occasion_anchor › capture_time › capture_kind | `photos.family-archive` verbatim: *"a capture_year level at the top would collect prints under the year somebody digitized them"* |

**Rows (4):** `photos.home-video` (ct, oa) · `photos.messenger-export` (ct only — *"a conversation
archive is not [an occasion] — it has a span, not an occasion"*) · `photos.social-media-export` (all
three) · `photos.family-archive` (oa, ct — takes the second order).

**`photos.family-archive` is the one photos row that reverses 00's own time-first exception, and it
reverses it on evidence rather than taste:** in this situation *"the capture date is precisely the
thing that is not recoverable — the only machine-readable timestamp belongs to the scanner."*

#### **D23 · `def.capture-kind-led@1`** — `sp.holder-own-record@1`
Roles: `capture_kind`(req) · `capture_time`(opt). Fragment: `frag.capture-kind-then-time@1`.

| Candidate order | Nesting | Attested by |
|---|---|---|
| **`ord.kind-then-year`** ★ | capture_kind › capture_time | `photos.screenshot-captures`: *"media_type leads because it is the only fact this material reliably has and the only one that separates it from photos.camera-events under a shared Photos parent"*; 00 writes them as separate things — *"Photos supported by image events and screenshot groups"* |
| `ord.year-then-kind` | capture_time › capture_kind | the row itself: *"Where the user has already made screenshots their own root, the media_type level has one child and should be flattened away, leaving capture_year leading"* |

**Row (1):** `photos.screenshot-captures`.

#### **D24 · `def.capture-kind-led.document@1`** — `sp.document-reproduced-whole@1`
Same roles, same fragment, same two candidate orders. **Row (1):** `photos.scanned-documents`.

Split from D23 because the row's privacy rule is categorically different and 00 names this material
first: *"A scanned passport, tax statement, medical document, authentication key, or account record
should enter a protected state immediately."* The row also carries the launch set's most important
**deferral** pattern, which belongs in `optional_branch_patterns` rather than in an order: *"when the
recovered OCR activates another schema, that schema's template governs the placement and this
template contributes `media_type` as a search fact only, so the scanned tax statement lands in the
finance branch and the photographed homework page lands under the course, not under Scans."*

#### **D25 · `def.occasion-place@1`** — `sp.holder-own-record@1`
Roles: `occasion_anchor`(req) · `place`(opt) · `capture_time`(opt). Fragment: `frag.occasion-then-place@1`.

| Candidate order | Nesting | Attested by |
|---|---|---|
| **`ord.trip-place-year`** ★ | occasion_anchor › place › capture_time | `travel.trip-photos`: *"a place under a trip reads (Kyoto inside a Japan trip) where a trip under a place does not"* |
| `ord.year-trip-place` | capture_time › occasion_anchor › place | the row itself: *"Reinstating capture_year at the top returns this branch to the schema's default order, which is exactly the reversal 00 licenses"* |

**Row (1):** `travel.trip-photos`. The default omits `capture_time` because *"a trip value in this
product's own vocabulary carries its own year ('Japan Trip 2025'), so a year level above it… 'repeats
a concept already expressed in the parent'."* `place` is offered *"only where the trip actually
visited more than one resolved place."*

### 4.7 Family G — research beyond Family A

#### **D26 · `def.research-lineage@1`** — `sp.holder-own-record@1`
Roles: `subject_anchor`(req) · `artifact_kind`(req) · `lifecycle_stage`(opt).
Fragments: `frag.subject-then-artifact@1` + `frag.artifact-then-stage@1`.

**This is the one place where the launch set contradicts 00, and it ships 00's order as an option
rather than deleting it.**

| Candidate order | Nesting | Attested by |
|---|---|---|
| **`ord.project-kind-stage`** ★ | subject_anchor › artifact_kind › lifecycle_stage | both bound rows, 2/2. `research.dataset-analysis`: *"Putting stage above artifact_type… splits one dataset's raw table from the cleaned table derived from it."* `research.thesis-dissertation`: *"putting stage on top interleaves a chapter draft with a defense deck under one Revision folder"* |
| `ord.project-stage-kind` | subject_anchor › lifecycle_stage › artifact_kind | **00 §5.4 verbatim**: *"a Research template may define project → stage → artifact type"*, plus 16 unbound rows across `creative` and `engineering` (`43` §4.4 B) |

**Why the default is the flip.** Zero of the 54 rows realize 00's chain; the only two rows that can
bind all three levels invert it and argue the inversion in their own words. But the *wider* corpus
is on 00's side — 20 rows / 3 domains against 2 rows / 1 domain. `43` §6.2's ruling, which I adopt:
**keep the flip as the default and change its status — it is a research-local default, not a general
finding, and it must not be generalized to `creative` or `engineering` in wave 2.** Nothing is lost
either way, because both orders ship.

**Rows (2):** `research.dataset-analysis`, `research.thesis-dissertation`.

#### **D27 · `def.research-workflow-split@1`**
Roles: `subject_anchor`(req) · `lifecycle_stage`(req). Fragment: `frag.subject-then-stage@1`.

| Candidate order | Nesting | Attested by |
|---|---|---|
| **`ord.project-then-stage`** ★ | subject_anchor › lifecycle_stage | `research.grants-funding`: *"this situation's whole shape is a before-and-after, pre-award drafting versus post-award reporting"* |
| `ord.stage-then-project` | lifecycle_stage › subject_anchor | **AUTHORED** |

**Row (1):** `research.grants-funding`. `artifact_kind` is deliberately **metadata-only** here —
*"a submitted proposal is a purpose-coherent packet and branching it by artifact type scatters the
narrative, budget, justification, biosketches and letters that were submitted as one thing."* The
level this row actually wants first is the **sponsor**, and no organization key on the research
schema carries the funding role. That is a gate, not an ordering question — **Judgment Call 5(c)**.

#### **D28 · `def.submission-to-venue@1`**
Roles: `subject_anchor`(req) · `addressed_org`(opt) · `lifecycle_stage`(req).
Fragment: `frag.venue-in-submission-chain@1`.

| Candidate order | Nesting | Attested by |
|---|---|---|
| **`ord.project-venue-stage`** ★ | subject_anchor › addressed_org › lifecycle_stage | `research.manuscript-publication`: *"a manuscript that goes to one journal, is rejected, and goes to another produces two complete submission families whose stage values repeat, so putting stage above venue interleaves two submissions under one Revision folder"* |
| `ord.venue-project-stage` | addressed_org › subject_anchor › lifecycle_stage | the venue-first reading `research.conference-presentation` argues for the neighbouring situation; `41` O2 records project-first vs venue-first as attested 1-for-1 |

**Row (1):** `research.manuscript-publication`.

> **How this reconciles `41` §4-C.** The brief recommends defaulting this branch **flat**
> (`project › stage`), overriding the landed row, because *"a researcher whose manuscripts each go to
> one journal gets a one-child level, which is precisely what 00 asks the canvas to warn about."*
> Under the built record "flat" is **not an order** — a candidate order may not drop a role. So the
> brief's recommendation lands as: `addressed_org` is **optional**, and the applicability row's
> expected shape **omits it** until a second venue appears for the same version family. The default
> order still names it, the default *branch* does not open it. Both documents get what they asked
> for.

#### **D29 · `def.venue-bundle@1`**
Roles: `addressed_org`(req) · `subject_anchor`(opt) · `artifact_kind`(req).
Fragments: `frag.venue-prefix@1` + `frag.subject-then-artifact@1`.

| Candidate order | Nesting | Attested by |
|---|---|---|
| **`ord.venue-project-kind`** ★ | addressed_org › subject_anchor › artifact_kind | `research.conference-presentation`: *"A branch named Poster is meaningless on its own — a lab may present the same project as a poster at one meeting and a talk at the next"* |
| `ord.project-venue-kind` | subject_anchor › addressed_org › artifact_kind | the row's own recorded counter-case: *"For a holder with one project shown at five meetings, project-first keeps the work together and venue-first scatters it"* |

**Row (1):** `research.conference-presentation`. `stage` is not a role — *"inside an accepted meeting
bundle it carries one value for nearly every member"*. `lab` is not a role — *"a PI-named lab folder
is one step from the authorship collector 00 forbids."*

### 4.8 The ten authored alternatives

The record requires a recipe with two or more dimensions to offer **two or more** candidate orders:
*"one candidate is a single `dimensions` tuple wearing a new field name."* For **ten** definitions the
corpus attests exactly one order, so I authored the second. Every one is flagged **AUTHORED** in §4
above: D03, D05, D06, D08, D10, D12, D15, D17, D18, D27.

**This is a real cost and it should be seen before it is accepted.** An authored alternative is a
choice the interface will offer a user with a rationale nobody argued from a real corpus. Three ways
to spend it, and the choice is the owner's (**Judgment Call 3**): ship them as drafted; mark them
`publication_state: draft` while the attested order is `published`; or relax the two-order rule for
recipes with a single attested order and let the user reorder freely instead.

---

## 5. The 54 applicability records

`TemplateApplicability` is the join row. **Exactly one `uses_schema` each**, always — that is what
keeps reuse from turning a per-schema fact allow-list into a cross-domain union. The record enforces
it structurally: `role_bindings` may only target fields in the row's own `allowed_fields`, and *"A
row that binds outside its own allow-list is how reuse turns a per-schema fact allow-list into a
cross-domain union."*

`provenance` is mandatory on every row: the `domain_id` of the catalogue row and its research memo.
`detection_signal_refs` point at the node's own `recognition` block — R2 owns the actual patterns and
this draft writes none.

### 5.1 `uses_schema: academic` — 11 rows

| Applicability id | Definition | Role → field | Rows / provenance |
|---|---|---|---|
| `ap.academic.coursework@1` | D01 | holder_institution→`school` · cycle_period→`term` · subject_anchor→`subject` · artifact_kind→`work_type` | `academic.coursework` |
| `ap.academic.continuing-education@1` | D01 | holder_institution→`school` · subject_anchor→`subject` · artifact_kind→`work_type` | `academic.continuing-education` |
| `ap.academic.online-course@1` | D01 | holder_institution→`school` · subject_anchor→`subject` · artifact_kind→`work_type` | `academic.online-course` |
| `ap.academic.study-abroad@1` | D01 | holder_institution→`school` · subject_anchor→`subject` · artifact_kind→`work_type` | `academic.study-abroad` |
| `ap.academic.standardized-testing@1` | D01 | subject_anchor→`subject` · artifact_kind→`work_type` | `academic.standardized-testing` |
| `ap.academic.teaching@1` | D02 | cycle_period→`term` · subject_anchor→`subject` · artifact_kind→`work_type` | `academic.teaching` |
| `ap.academic.homeschool@1` | D03 | cycle_period→`term` · subject_anchor→`subject` · artifact_kind→`work_type` | `academic.homeschool` |
| `ap.academic.transcripts-credentials@1` | D05 | holder_institution→`school` · artifact_kind→`work_type` | `academic.transcripts-credentials` |
| `ap.academic.k12-schooling@1` | D06 | holder_institution→`school` · cycle_period→`term` · artifact_kind→`work_type` | `academic.k12-schooling` |
| `ap.academic.recommendation-letters@1` | D07 | cycle_period→`term` · artifact_kind→`work_type` | `academic.recommendation-letters-written` |
| `ap.academic.iep-plans@1` | D08 | holder_institution→`school` · cycle_period→`term` — **`exclusions: ("work_type as a folder level",)`** | `academic.iep-accommodation-plans` |

`allowed_fields` for every row above is a subset of `{school, term, subject, work_type}`. **`instructor`
appears in no `allowed_fields` and in no binding.**

### 5.2 `uses_schema: code` — 3 rows

| Applicability id | Definition | Role → field | Rows |
|---|---|---|---|
| `ap.code.notebooks-experiments@1` | D01 | subject_anchor→`project` · artifact_kind→`artifact_type` | `code.notebooks-experiments` |
| `ap.code.pkm-vault@1` | D09 | subject_anchor→`project` | `code.pkm-vault` |
| `ap.code.dotfiles-environment@1` | D10 | repository_instance→`repository` · artifact_kind→`artifact_type` | `code.dotfiles-environment` |

**`programming_language` appears in no `allowed_fields`.**

### 5.3 `uses_schema: college_applications` — 5 rows

| Applicability id | Definition | Role → field | Rows |
|---|---|---|---|
| `ap.applications.undergraduate-packet@1` | D11 | addressed_org→`target_university` · cycle_period→`application_cycle` · artifact_kind→`application_document_type` | `applications.undergraduate-packet` |
| `ap.applications.graduate-professional@1` | D11 | addressed_org→`target_university` · artifact_kind→`application_document_type` | `applications.graduate-professional` |
| `ap.applications.scholarship-fellowship@1` | D11 | addressed_org→`target_university` · cycle_period→`application_cycle` · artifact_kind→`application_document_type` | `applications.scholarship-fellowship` |
| `ap.applications.k12-admission@1` | D12 | addressed_org→`target_university` · artifact_kind→`application_document_type` | `applications.k12-admission` |
| `ap.applications.purpose-packet@1` | D13 | purpose_anchor→`purpose` · **`purpose_profile_ref: pp.application-submission@1`** | `applications.purpose-packet` |

**`school` is declared by this schema and appears in no `allowed_fields`** — it is the applicant's own
school and the schema forbids it as a level.

### 5.4 `uses_schema: finance` — 18 rows

| Applicability id | Definition | Role → field | Rows |
|---|---|---|---|
| `ap.finance.personal-records@1` | D14 | issuing_org→`institution` · account_kind→`account_type` · artifact_kind→`record_type` | `finance.personal-records` |
| `ap.finance.investment-brokerage@1` | D14 | same three | `finance.investment-brokerage` |
| `ap.finance.insurance-corporate@1` | D14 | same three | `finance.insurance-corporate` |
| `ap.finance.insurance-personal@1` | D14 | issuing_org→`institution` · artifact_kind→`record_type` | `finance.insurance-personal` |
| `ap.finance.insurance-healthcare@1` | D14 | issuing_org · artifact_kind | `finance.insurance-healthcare` |
| `ap.finance.crypto-assets@1` | D14 | issuing_org · artifact_kind | `finance.crypto-assets` |
| `ap.finance.cap-table-equity@1` | D14 | issuing_org · artifact_kind | `finance.cap-table-equity` |
| `ap.finance.hoa-residents-association@1` | D14 | issuing_org · artifact_kind | `finance.hoa-residents-association` |
| `ap.finance.receipts-expenses@1` | D14 | issuing_org · artifact_kind | `finance.receipts-expenses` |
| `ap.finance.student-financial-aid@1` | D14 | issuing_org · artifact_kind | `finance.student-financial-aid` |
| `ap.finance.subscriptions-utilities@1` | D14 | issuing_org · artifact_kind | `finance.subscriptions-utilities` |
| `ap.finance.payroll-received@1` | D15 | issuing_org→`institution` · scope_period→`tax_year` · artifact_kind→`record_type` | `finance.payroll-received` |
| `ap.finance.tax-filings@1` | D16 | scope_period→`tax_year` · artifact_kind→`record_type` | `finance.tax-filings` |
| `ap.finance.loans-mortgage@1` | D17 | account_kind→`account_type` · artifact_kind→`record_type` | `finance.loans-mortgage` |
| `ap.finance.small-business-bookkeeping@1` | D18 | artifact_kind→`record_type` · account_kind→`account_type` | `finance.small-business-bookkeeping` |
| `ap.travel.bookings-confirmations@1` | D19 | artifact_kind→`record_type` · issuing_org→`institution` | `travel.bookings-confirmations` |
| `ap.finance.household-property@1` | D20 | artifact_kind→`record_type` | `finance.household-property` |
| `ap.finance.vehicle-records@1` | D20 | artifact_kind→`record_type` | `finance.vehicle-records` |

### 5.5 `uses_schema: photos` — 9 rows

| Applicability id | Definition | Role → field | Rows |
|---|---|---|---|
| `ap.photos.camera-events@1` | D21 | capture_time→`capture_year` · occasion_anchor→`event` | `photos.camera-events` |
| `ap.photos.drone-captures@1` | D21 | capture_time · occasion_anchor | `photos.drone-captures` |
| `ap.photos.home-video@1` | D22 | capture_time · occasion_anchor | `photos.home-video` |
| `ap.photos.messenger-export@1` | D22 | capture_time→`capture_year` | `photos.messenger-export` |
| `ap.photos.social-media-export@1` | D22 | capture_time · occasion_anchor · capture_kind→`media_type` | `photos.social-media-export` |
| `ap.photos.family-archive@1` | D22 | occasion_anchor · capture_time | `photos.family-archive` |
| `ap.photos.screenshot-captures@1` | D23 | capture_kind→`media_type` · capture_time→`capture_year` | `photos.screenshot-captures` |
| `ap.photos.scanned-documents@1` | D24 | capture_kind · capture_time | `photos.scanned-documents` |
| `ap.travel.trip-photos@1` | D25 | occasion_anchor→`event` · place→`location` | `travel.trip-photos` |

**`people` and `camera_information` appear in no `allowed_fields` and in no binding.**

### 5.6 `uses_schema: research` — 9 rows

| Applicability id | Definition | Role → field | Rows |
|---|---|---|---|
| `ap.research.lab-notebook-protocols@1` | D01 | holder_institution→`lab` · subject_anchor→`project` · artifact_kind→`artifact_type` | `research.lab-notebook-protocols` |
| `ap.research.ethics-compliance@1` | D02 | subject_anchor→`project` · artifact_kind→`artifact_type` | `research.ethics-compliance` |
| `ap.research.reading-library@1` | D04 | subject_anchor · artifact_kind | `research.reading-library` |
| `ap.research.dataset-analysis@1` | D26 | subject_anchor · artifact_kind · lifecycle_stage→`stage` | `research.dataset-analysis` |
| `ap.research.thesis-dissertation@1` | D26 | subject_anchor · artifact_kind · lifecycle_stage | `research.thesis-dissertation` |
| `ap.research.grants-funding@1` | D27 | subject_anchor→`project` · lifecycle_stage→`stage` | `research.grants-funding` |
| `ap.research.manuscript-publication@1` | D28 | subject_anchor · addressed_org→`venue` · lifecycle_stage | `research.manuscript-publication` |
| `ap.research.conference-presentation@1` | D29 | addressed_org→`venue` · subject_anchor · artifact_kind | `research.conference-presentation` |

`research` carries **9** template rows, of which one — `research.project-workspace` — is
`refuse_node: true` and excluded at §1.1. **8 bindable rows, 8 applicability records.**

**`authored_by` appears in no `allowed_fields`.**

---

## 6. Where two rows want the same definition — the reuse map

This is what the owner asked to see.

### 6.1 One definition reaching three schemas

```
                       def.subject-work-record@1
                    (3 shared fragments, 4 roles, 3 candidate orders)
                                     │
        ┌────────────────────────────┼────────────────────────────┐
        │                            │                            │
 TemplateApplicability        TemplateApplicability        TemplateApplicability
 uses_schema: academic        uses_schema: research        uses_schema: code
 ─────────────────────        ─────────────────────        ─────────────────────
 holder_institution→school    holder_institution→lab       (prefix unbound)
 cycle_period      →term      (no time field on research)  (no time field on code)
 subject_anchor    →subject   subject_anchor    →project   subject_anchor→project
 artifact_kind     →work_type artifact_kind →artifact_type artifact_kind →artifact_type
        │                            │                            │
  5 rows                       1 row                        1 row
  coursework                   lab-notebook-protocols       notebooks-experiments
  continuing-education
  online-course
  study-abroad
  standardized-testing

  Academics/Columbia/2026-Spring/PHYS1401/Homework
  Research/Chen Lab/PVA-RDP/protocol
  Code/graphify/notebook
```

**Zero shared data.** The academic binding physically cannot resolve a research field: it would have
to bind outside its own `allowed_fields`, and the record refuses that at construction. The fragment
carries roles and an order — **no field names, no values**.

### 6.2 Every reuse point in the launch set

| Reuse point | Definition or fragment | Reaches |
|---|---|---|
| **3 schemas, 1 definition** | `def.subject-work-record@1` | academic (5 rows) · research (1) · code (1) |
| **2 schemas, 1 definition** | `def.subject-work-record.third-party@1` | academic (`teaching`) · research (`ethics-compliance`) |
| **3 schemas, 1 fragment, 6 definitions** | `frag.subject-then-artifact@1` | D01 D02 D03 D04 D26 D29 — **14 rows** |
| **2 schemas, 1 fragment** | `frag.holder-affiliation-prefix@1` | academic `school` · research `lab` — 5 rows |
| **2 schemas, 1 fragment** | `frag.cycle-then-artifact@1` | academic `term` · applications `application_cycle` — 7 rows |
| **3 rows, 1 definition, opposite orders** | `def.addressee-packet@1` | `undergraduate-packet` and `scholarship-fellowship` land on the **same** definition through **different candidate orders** — the clearest demonstration that ordering is runtime |
| **11 rows, 1 definition** | `def.issuer-record@1` | the finance spine; 8 rows omit the middle level, 3 keep it |
| **4 rows, 1 definition** | `def.capture-time-events.third-party@1` | `home-video`, `messenger-export`, `social-media-export`, `family-archive` — the last taking the reversed order |
| **2 rows, 1 definition** | `def.research-lineage@1` | `dataset-analysis`, `thesis-dissertation` — both inverting 00, both arguing it |
| **2 rows, 1 definition** | `def.group-scoped-record@1` | `household-property`, `vehicle-records` — both shallow-by-necessity |
| **2 rows, 1 definition** | `def.capture-kind-led@1` / `.document@1` | same shape, split only by privacy (Judgment Call 1) |

### 6.3 A mixed-domain purpose packet, composed

00's own case: *"An academic abstract submitted as part of a university application can retain
project = PVA/RDP and document type = abstract while also carrying purpose = university application
and target university = UChicago."*

```
  def.subject-work-record@1  ──▶ ap.research.*        ──▶ project, artifact_type
  def.purpose-packet@1       ──▶ ap.applications.*    ──▶ purpose  (+ pp.application-submission@1)
```

Two definitions, two one-schema bindings, one branch. **The packet composes the bindings; it does
not union the schemas.** The research binding may not resolve `purpose` or `target_university`; the
applications binding may not resolve `project`. C6 then checks that no member was silently dropped.

---

## 7. Worked folder trees — what the user actually sees

Top-level names are the six the owner approved. **Every value below is a real string from the design
document or from the catalogue's own `file_examples`** — the sources are named. The product invents
none of them: 00 is explicit that *"The system does not invent PHYS1401, UChicago, Spring 2026, or
PVA/RDP; those names emerge from validated facts, user-confirmed groups, and accepted labels."*

### 7.1 Academics — `def.subject-work-record@1` default order

Every path in this tree except the `Georgetown Prep` and `Continuing Education` lines is quoted
verbatim from 00.

```
Academics/
├── Columbia/                                    ← school           (00, 18 occurrences)
│   ├── 2026-Spring/                             ← term             (00's own path spelling)
│   │   ├── BUSIB 4300/                          ← subject
│   │   │   ├── Syllabus/                        ← work_type
│   │   │   ├── Homework/
│   │   │   └── Lectures/
│   │   ├── PHYS1401/
│   │   │   ├── Homework/                        ← 00: "Academics/Columbia/2026-Spring/PHYS1401/Homework"
│   │   │   └── General/                         ← 00's scoped fallback, NOT a global Unsorted
│   │   └── General/                             ← "clearly part of Academics/Columbia/2026-Spring
│   │                                               but has no recoverable work type"
│   └── 2025-Spring/
│       └── PHYS1401/Homework/
└── Georgetown Prep/                             ← 00 §5.8: "may remain shallow because it
                                                    contains only a handful of files"
```

**The same recipe, two levels shallower, for a different row.** `academic.continuing-education` omits
`term` at runtime because no semester exists to fill it:

```
Academics/
└── Coursera/                                    ← school (the provider)
    └── Machine Learning/                        ← subject
        ├── Completion Certificate/              ← work_type
        └── Course Handout/
```

**What the canvas warns about here, before the user commits (V2/V3, §5.9):** the `2025-Spring`
branch has one course and that course has one work type — a two-level chain that produces one child
each time. The canvas states the counts and recommends flattening; it does not delete the levels.

### 7.2 Applications — `def.addressee-packet@1`, both candidate orders side by side

```
DEFAULT  ord.addressee-cycle-kind                 ALTERNATIVE  ord.cycle-kind-addressee
Applications/                                     Applications/
├── UChicago/                                     ├── 2026/
│   └── 2026/                                     │   ├── Personal Statement/
│       ├── Supplemental Essays/                  │   │   ├── (one reusable essay family)
│       ├── Forms and Portal Records/             │   │   └── ...
│       └── Supporting Materials/                 │   ├── Application Form/
├── Columbia/                                     │   └── Recommendation Form/
│   └── 2026/                                     └── 2025/
└── Shared Application Materials/
```

Both are 00's. The left is `Applications/UChicago/2026/Supplemental Essays` and the three-way split
*"essay drafts go to Essays; checklists and portal screenshots go to Forms and Portal Records;
transcripts, resumes, and certificates go to Supporting Materials."* `Shared Application Materials`
is 00's own branch for the transcript that belongs to several packets and to none.

**The right-hand order is for the shape the left-hand one breaks on** — one applicant, many sponsors,
one file each. Under the left order that user gets a shelf of one-file folders, which is exactly what
00 tells the canvas to warn about.

**And the flat one, `def.purpose-packet@1`, for the set that has no addressee at all:**

```
Applications/
└── Chinese University Application Materials/     ← 00's own instance, an existing user folder
    ├── Transcript.pdf                                adopted rather than rebuilt
    ├── Personal Statement.docx
    ├── Resume.pdf
    ├── ID.jpg
    └── Certificate.jpg
```

### 7.3 Research — three definitions under one root

```
Research/
├── PVA-RDP/                                     ← project   (00, 6 occurrences)
│   ├── Manuscripts and Figures/                 ← 00's own label for this neighbourhood
│   ├── Nature Methods/                          ← venue     [def.submission-to-venue, OPTIONAL —
│   │   ├── Under Review/                           opens only when a second venue appears]
│   │   └── Response to Reviewers/
│   ├── Dataset/                                 ← artifact_type  [def.research-lineage]
│   │   ├── Raw/                                 ← stage
│   │   └── Cleaned/
│   └── Ethics/                                  ← artifact_type  [def.subject-work-record.third-party]
│       ├── Approval Letter/
│       └── Consent Forms/                       ⚠ see Judgment Call 5(d)
├── Chen Lab/                                    ← lab   [def.subject-work-record; the lab leads
│   └── Protocols/                                  because a standing SOP has no project]
└── Reading/                                     ← [def.reading-shelf]
    ├── Literature Paper/
    └── Preprint/
```

Two things to look at. **`Chen Lab` and `PVA-RDP` are siblings at the same level** — the lab-first
row and the project-first rows produce an uneven tree, and 00 requires exactly that: *"The canvas
must support uneven depth because real file trees are not and should not be perfectly symmetrical."*
**`Nature Methods` is drawn dotted in the canvas** — it is the optional level `41` §4-C asked to
default off, and it opens only when a manuscript reaches a second venue.

**What has no home and will look wrong:** a conference folder reads `ASCB 2026` as one string rather
than `ASCB/2026`, because the research schema has no time field and the occurrence year has to live
inside the venue value. That is **Judgment Call 5(a)** and it changes a real folder name.

### 7.4 Finance — `def.issuer-record@1`, and the one time-first exception

```
Finance/                                          [shown as a PROTECTED area; 00: "a Finance or
├── Chase/                    ← institution        Identity proposal may be visible as a protected
│   ├── Checking/             ← account_type       area, but the product should avoid showing
│   │   ├── Statement/        ← record_type        sensitive filenames or sending their contents
│   │   └── Transaction Export/                    to cloud services by default"]
│   └── Credit Card/
│       └── Statement/
├── ADP/                      ← [def.issuer-period-record]
│   ├── 2025/                 ← tax_year
│   │   └── Pay Statement/
│   └── 2026/
├── 2025/                     ← [def.period-scoped-filing — the ONE time-first finance branch]
│   ├── Return as Filed/
│   ├── Payer Forms/
│   └── General/              ← where a donation receipt with no year fact lands. See JC 5(b).
└── Mortgage/                 ← [def.loan-kind-record — account_type leads, NOT the institution,
    ├── Servicing Statement/     because servicing transfers would split one loan across issuers]
    └── Closing Packet/
```

`Chase` and `ADP` are from the catalogue's own `file_examples` (`Chase Statement 2026-03.pdf`,
`ADP Pay Statement Mar 2026.pdf`), not invented here.

**Note what is NOT in this tree.** No account holder, no account number, no address, no amount. The
row is blunt about it: *"Amounts, household-income values, and applicant identifiers are search-and-
review material only. They may never become a folder level."*

### 7.5 Photos — the time-first exception, and the two rows that reverse it

```
Photos/
├── 2026/                     ← capture_year   [def.capture-time-events — 00: "a Photos template
│   ├── Japan Trip 2025/      ← event             may define year → event"]
│   └── General/
├── 2025/
├── Screenshots/              ← media_type     [def.capture-kind-led — media_type leads because
│   ├── 2026/                    it is the only fact a screenshot reliably has]
│   └── 2025/
├── Scans/                    ← [def.capture-kind-led.document]
│   └── 2026/
└── Grandparents' Albums/     ← event          [def.capture-time-events.third-party, REVERSED order:
    ├── 1970s/                ← capture_year      "a capture_year level at the top would collect
    └── 1980s/                                     prints under the year somebody digitized them"]
```

**The most important thing in this tree is the folder that is not here.** `Scans/` is drawn dotted
because `photos.scanned-documents`' most common outcome is **deferral**: a scanned tax statement
lands in `Finance/`, a photographed homework page lands under its course, and `media_type = scan`
stays a search fact. Whether a `Scans` branch should exist at all for the captures nothing claimed
is **Judgment Call 5(e)**, and it decides where several hundred of a real user's files live.

Second: `Photos/2026/Japan Trip 2025/` puts the year in the folder name **and** in the trip name.
`travel.trip-photos` flags exactly that and drops the year level, producing instead:

```
Photos/
└── Japan Trip 2025/          ← event      [def.occasion-place]
    ├── Kyoto/                ← location
    └── Tokyo/
```

### 7.6 Code — the shallowest trees in the launch set, deliberately

```
Code/
├── graphify/                 ← project  [def.subject-work-record]
│   ├── Notebook/             ← artifact_type
│   ├── Model Checkpoint/
│   └── Metrics Log/
├── Second Brain/             ← project  [def.preserved-root — ONE dimension, deliberately:
│                                "Existing folders must not be automatically flattened, renamed,
│                                 or reorganized simply because a template would produce a
│                                 different structure"]
└── dotfiles/                 ← repository  [def.container-artifact]
    ├── Shell Configuration/
    └── Editor Configuration/
```

**And the branch the launch set refuses to build.** `code.software-project` and
`code.scratch-prototypes` carry `refuse_node: true` and an empty order. A repository root with a
`package.json` beside `src/` is structure 00 tells the engine to leave alone: *"reject descendants of
software project roots."* It is represented on the canvas and it is not re-filed. **`Code/` will
therefore look emptier than a developer expects, and that is correct.**

---

## 8. Judgment calls — the owner's, flagged rather than resolved

Each names what I chose, what the alternative is, and what it costs.

### JC 1 · Does a different data subject force a different definition? — **the biggest one**

**Chosen:** yes. §4.0 Rule B. It is what makes the count 29 rather than 21.

**Why it is forced rather than preferred:** `TemplateApplicability` — the per-schema, per-context
row — has **no privacy field**. The only homes for privacy in the built records are
`TemplateFragment.privacy_floor` and `TemplateDefinition.sensitivity_policy_ref`. `37` §4.3's
judgment was that direction-of-exposure should live on the applicability row; **that judgment is not
expressible in the record as built.**

**The three ways out:**
- **(a) as drafted** — 29 definitions. Cannot under-protect. Cost: eight definitions carry one row
  each purely because of exposure, and the reuse story reads thinner than it is.
- **(b) shape only** — 21 definitions, one policy per shape family. `def.subject-work-record` then
  serves 11 rows across 3 schemas instead of 7. Cost: one `sensitivity_policy_ref` would have to
  cover both `research.reading-library` (`sensitivity: none`) and `academic.teaching` (other
  people's grades) — it must either over-restrict one or under-restrict the other.
- **(c) add a privacy field to `TemplateApplicability`** — a P10 record change, parallel to the
  `candidate_orders` amendment `41` §4.1 asked for and got. It would give 21 definitions **and**
  per-context privacy. It is the right answer if the owner is willing to reopen the record.

**My recommendation: (c) if the record can be reopened, (a) if it cannot.** Not (b).

**Worth knowing:** `sensitivity_policy_ref` is stored but **not gated** — C7 reads
`TemplateFragment.privacy_floor`, not the policy ref. So under (a) the split buys *reviewability*,
not enforcement. Enforcement would need the floor on a fragment, which brings back the
over-restriction problem. This is a genuine seam and it is not mine to close.

### JC 2 · The composition path derives order from fragments, so 19 carrier fragments exist

**Chosen:** author 19 single-context "carrier" fragments (§3.3), each honestly marked as a carrier
rather than a reuse claim.

**Why:** §3.4(a) and (b), verified by running the code. A definition with no fragment raises; a
definition-local dimension sorts last and ties.

**The alternative, and it is cleaner:** let `TemplateDefinition` carry its own `relative_order` for
definition-local dimensions, and let a fragmentless definition supply its own privacy floor. That
deletes all 19 carriers and leaves the 3 shared fragments as the only fragments — which is what the
word "fragment" was meant to mean. It is a specific, bounded P10 amendment.

**Cost of doing nothing:** the shared/carrier distinction lives only in prose, and a later reader
counting fragments will report "22 shared recipes" when the evidence supports 3.

### JC 3 · Ten authored candidate orders

**Chosen:** author them, and flag every one (§4.8).

**Alternatives:** ship them `publication_state: draft` while the attested order is `published`; or
ask P10 to relax the two-order rule where only one order is attested.

**Cost of doing nothing:** the interface offers ten alternatives whose rationale is mine, presented
beside orders that rows argued from real corpora. The user cannot tell which is which.

### JC 4 · `code.dotfiles-environment` — propose a destination, or represent and leave in place?

The row asks directly: *"a dotfile is read by a tool from a fixed absolute location, so MOVING it
breaks the machine. This template may be one whose correct default is represent-and-leave-in-place
rather than propose-a-destination."* 00 allows that posture **for residual templates** and says
nothing about domain templates.

**I did not resolve it.** D10 is drafted as an ordinary destination-proposing definition. If the
answer is leave-in-place, D10 needs a disposition the definition record does not currently carry
(`RESIDUAL_DISPOSITIONS` has `leave-in-place`, but on nodes, not definitions).

### JC 5 · Five places where the recommendation stops one level short of the material

None may be fixed by inventing a field — `_CONTRACT.md`: *"Do not invent fields to make the gate
green."* All five are schema questions wearing template clothes.

| | Gap | What the user sees |
|---|---|---|
| **(a)** | research has no time field | Conference folders read `ASCB 2026`, not `ASCB/2026`. `research.conference-presentation`: *"does a conference occurrence stay a venue value, or does the Research schema owe a time field?"* |
| **(b)** | a tax packet's supporting documents carry no `tax_year` of their own | Under D16's year-first order, **most of a real filing's supporting material has no legal branch** and lands in a scoped `General` or in review. `finance.tax-filings` states it and refuses to resolve it. |
| **(c)** | research has no organization key for a funder | `research.grants-funding` cannot offer the sponsor level a three-agency holder navigates by. |
| **(d)** | no field names the person a record is *about* | Hits four rows: `k12-schooling`, `homeschool`, `iep-accommodation-plans`, `k12-admission`. A two-child household cannot keep two packets apart. And the fix is privacy-loaded: *"Adding it makes person-shaped folders for minors a product-proposed default."* |
| **(e)** | `photos.scanned-documents`' most common outcome is deferral | Does a `Photos/Scans` branch exist for the captures nothing claimed, or does `media_type` stay a search fact with every resolved capture living in the domain that claimed it? *"the answer changes where several hundred of someone's real files live."* |

**All five are recorded in the rows' own `open_question` fields. None is new. None is mine to close.**

### JC 6 · Two rows named `travel.*` surface under Finance and Photos

`travel.bookings-confirmations` binds `finance`; `travel.trip-photos` binds `photos`. Under the six
approved top-level names, a user's flight confirmations appear under **Finance** and their trip
photos under **Photos**, and the trip that connects them exists only as an accepted group.
`travel.bookings-confirmations` says so plainly: *"the Finance schema cannot express it… it cannot
encode trip then record type."*

**Options:** accept it (the trip is a group and the canvas can surface a group as a branch); add a
seventh top-level `Travel` that draws from two schemas; or answer `ROSTER.md` NJ-R1a-2 — *"does
travel deserve a small schema using existing canonical fields such as `event`, `location`,
`record_type`, and `capture_year`?"* The third is the one the rows keep asking for.

---

## 9. What this draft cannot do

1. **It ships nothing.** P10's compiler does not exist; no ratified catalogue record has been turned
   into a runtime `TemplateFragment`, `TemplateDefinition` or `TemplateApplicability`. The publication
   boundary stands: *"P10 runtime code must not import [`planning/domains/`] Markdown or draft JSON."*
2. **`is_safety_domain` is still absent from `finance.json`, `identity.json` and `medical.json`.**
   Only `legal.json` carries it. Re-verified today. A compiler reading these files would treat
   finance as an ordinary domain. The information exists under a second name — all four carry
   `launch: "safety"` — so the repair is small, but **it is not mine and it is not made here.**
3. **Privacy floors are placeholders.** `TemplateFragment.privacy_floor` values are P7's vocabulary,
   injected per deployment. This draft writes the symbol `baseline` and assigns no handling class —
   `_CONTRACT.md` rule 5 reserves that vocabulary and this draft respects it.
4. **`detection_signal_refs` are references, not patterns.** R2 owns the regexes and gazetteers.
   No pattern is written here.
5. **237 template rows remain gated** on schemas with no live fields. Seventeen of the twenty-three
   schemas declare zero. The largest recipe in the whole corpus — `matter_anchor › artifact_kind`,
   51 rows across 10 domains, zero reversals — cannot bind at launch. That is wave 2 and it is
   bigger than this wave.
6. **The per-schema split of the 54, for anyone checking the arithmetic:** academic 11 · code 3 ·
   college_applications 5 · finance 18 · photos 9 · research 8. The three refused rows sit on `code`
   (2) and `research` (1), which is why those two schemas carry more template rows than bindings.
   §1.3 and §5 agree row-for-row, and the appendix regenerates both.

---

## Appendix — reproduction

Run at commit `8c5f650` on branch `build/p6-p7-first-packages`. Every number in this document comes
out of one of these.

```bash
cd "/Users/jy/GRAPH AGENT"

# §1 — the 54, the six schemas, the 30 live fields, and the legality check
python3 - <<'PY'
import json,glob
nodes={}
for f in sorted(glob.glob('planning/domains/nodes/*.json')):
    d=json.load(open(f)); nodes[d['id']]=d
schemas={i:d for i,d in nodes.items() if d['kind']=='schema'}
live={i:[x['field'] for x in d['fields']] for i,d in schemas.items()}
SIX=sorted(i for i in live if live[i])
print('nodes',len(nodes),'schemas',len(schemas),'templates',
      sum(1 for d in nodes.values() if d['kind']=='template'))
print('field-declaring schemas:',SIX)
print('live fields:',sum(len(live[s]) for s in SIX))
rows=[d for d in nodes.values() if d['kind']=='template' and d['schema_id'] in SIX]
bind=[d for d in rows if not d.get('refuse_node')]
print('rows on the six:',len(rows),'refusing:',len(rows)-len(bind),'BINDABLE:',len(bind))
bad=[(d['id'],t) for d in bind
     for t in d['template']['dimension_order']
     if t not in {x['field'] for x in schemas[d['schema_id']]['fields']
                  if x['destination_eligible']}]
print('illegal dimension tokens:',len(bad))
PY

# §2.1 — the 32 role sequences
python3 - <<'PY'
import json,glob,collections
ROLE={'work_type':'artifact_kind','artifact_type':'artifact_kind','record_type':'artifact_kind',
 'application_document_type':'artifact_kind','project':'subject_anchor','subject':'subject_anchor',
 'institution':'issuing_org','target_university':'addressed_org','venue':'addressed_org',
 'term':'cycle_period','application_cycle':'cycle_period','school':'holder_institution',
 'lab':'holder_institution','capture_year':'capture_time','event':'occasion_anchor',
 'account_type':'account_kind','repository':'repository_instance','stage':'lifecycle_stage',
 'media_type':'capture_kind','tax_year':'scope_period','purpose':'purpose_anchor','location':'place'}
SIX=['academic','code','college_applications','finance','photos','research']
seq=collections.defaultdict(list)
for f in sorted(glob.glob('planning/domains/nodes/*.json')):
    d=json.load(open(f))
    if d['kind']=='template' and d['schema_id'] in SIX and not d.get('refuse_node'):
        seq[tuple(ROLE[t] for t in d['template']['dimension_order'])].append(d['id'])
print('distinct role sequences:',len(seq),'rows:',sum(len(v) for v in seq.values()))
PY

# §3.4 — the three facts about the built code, verified by running it
PYTHONPATH=src python3 - <<'PY'
from tree_design.templates import TemplateFragment, merge_fragment_constraints
rank=lambda f:{'baseline':0,'protected':1}[f]
try: merge_fragment_constraints([], privacy_rank=rank)
except Exception as e: print('(a)',type(e).__name__)
F=lambda i,r,o,p: TemplateFragment(fragment_id=i,fragment_version=1,roles=r,relative_order=o,
    imports=(),optional_roles=p,metadata_only_roles=(),allowed_values={},
    privacy_floor='baseline',provenance=('x','y'))
sa=F('frag.subject-then-artifact',('subject_anchor','artifact_kind'),
     (('subject_anchor','artifact_kind'),),())
m=merge_fragment_constraints([sa],privacy_rank=rank)
pos={r:i for i,r in enumerate(m.ordered_roles)}
print('(b)',' > '.join(sorted(['subject_anchor','artifact_kind','addressed_org'],
      key=lambda r:pos.get(r,len(pos)))))
hi=F('frag.holder-affiliation-prefix',('holder_institution','subject_anchor'),
     (('holder_institution','subject_anchor'),),('holder_institution',))
cp=F('frag.cycle-then-artifact',('cycle_period','artifact_kind'),
     (('cycle_period','artifact_kind'),),('cycle_period',))
print('(c)',' > '.join(merge_fragment_constraints([sa,hi,cp],privacy_rank=rank).ordered_roles))
PY

# §9.2 — the safety flag, still absent on three of the four
for s in finance identity medical legal; do
  python3 -c "import json;d=json.load(open('planning/domains/nodes/$s.json'));\
print('$s', d.get('is_safety_domain','ABSENT'), d.get('launch'))"
done
```
