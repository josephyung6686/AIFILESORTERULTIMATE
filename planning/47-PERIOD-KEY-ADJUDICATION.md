# 47 — PERIOD KEY ADJUDICATION

**Status: PROPOSAL. Nothing is adopted. No `src/` file and no `planning/domains/**.json` was edited by this pass.**
Approval is the product owner's alone.

**Corpus pinned at HEAD `8c5f650`.** Every number below was re-derived by this pass against that
commit, not carried forward from the dispatch brief. See §0 for a correction the re-derivation
forced.

---

## 0. Numbers re-derived, and one correction

| Claim | Re-derived value |
|---|---|
| `planning/domains/nodes/*.json` rows | **358** (335 `template`, 23 `schema`) |
| Rows with `refuse_node: true` | **44** |
| Schemas declaring live `fields` | **6** — `academic`, `code`, `college_applications`, `finance`, `photos`, `research` |
| **Total live fields (the whole binding ceiling)** | **30 — not 31** |
| Rows carrying `proposed_fields` | **87** |
| Distinct proposed keys / seconding instances | **80 / 170** |
| `canonical_fields.json` entries | **37** |
| Canonical keys containing `period` | **none** |

**The correction.** The brief said 31 live fields. It is **30**. `finance` declared five fields
when this session began and declares four now: `institution`, `account_type`, `tax_year`,
`record_type`. Another agent moved `account_holder` from `fields` into `proposed_fields` in commit
`b2dbb08` ("audit: record the schema-vocabulary divergence, north star, and fix account_holder")
**while this pass was running** — I observed 5 at 22:24 and 4 at 22:31 from the same path. The
corpus is live under multiple writers. Re-derive before quoting; do not trust this document's
counts after the next commit touching `planning/domains/nodes/`.

**The second correction is to the brief's framing, and it enlarges the question.** The brief named
three spellings and 21 rows. There are **five spellings across 23 proposing rows**, and the two
extra spellings both explicitly ask to be merged into whatever wins:

| Spelling | Proposal instances | Distinct rows | Schemas |
|---|---|---|---|
| `fiscal_period` | 12 | 12 | `business_operations` (9), `law_practice` (2), `nonprofit` (1) |
| `reporting_period` | 6 | 6 | `resource_operations` (4), `manufacturing` (2) |
| `record_period` | 3 | 3 | `finance` (2), `retail_hospitality` (1) |
| `planning_period` | 1 | 1 | `manufacturing` (1) |
| `aid_year` | 1 | 1 | `finance` (1) |
| **Total** | **23** | **23** | **7 schemas** |

No row proposes two of them. Five of the 23 are **schema** rows (`business_operations`,
`law_practice`, `nonprofit`, `resource_operations`, `retail_hospitality`); the other 18 are templates.

**And the true demand is far larger than 23.** A further **13 rows raise the concept in
`open_question` without minting anything**, obeying the contract's "do not resolve a question that
is Joseph's". Counting prose mentions anywhere in the row, **48 rows across 9 schemas already name
one of the five spellings**:

`business_operations` 12 · `resource_operations` 9 · `law_practice` 8 · `manufacturing` 5 ·
`finance` 4 · `retail_hospitality` 4 · `nonprofit` 3 · `hr` 2 · `construction_property` 1

This is not a 21-row tidiness problem. It is the largest single field-shaped hole in the catalogue,
and `business_operations` says so in those words: *"four rows in this family want `fiscal_period`
and none can have it, which is the clearest field-shaped hole this pass found."*

---

## 1. The 23 rows, and the exact period concept each needs

Quotations are from each row's `why_no_existing_key` / `why_no_existing_key_works` unless marked.

### 1.1 `fiscal_period` — 12 rows

**`business_operations`** (schema — the originating mint)
> "The management calendar of an organisation is a real recurring dimension and no canonical key
> holds it. `tax_year` is the finance schema's STATUTORY filing year and carries a jurisdiction's
> meaning; an entity's fiscal year routinely does not coincide with it, and reusing the key would
> quietly assert that it does. `term` is academic, `application_cycle` is applications,
> `capture_year` is photos, `creation_date` is when the bytes were made rather than which period
> the content is ABOUT."

Concept: **a management calendar round**. Example `FY2026, Q3 FY26, the 2026-27 planning round`.

**`business_operations.budget-forecast`** — the row that wants it most.
> "SECONDING, NOT MINTING… What it adds is a THIRD-PARTY CONFLICT in front of R1c that the schema
> row could not see… One concept, two spellings, proposed independently by two families that
> contest the same workbook, is exactly the bug D6 exists to prevent."

Concept: **the planning round a budget/forecast/actuals cycle belongs to**. This row is the source
of the brief's framing and it is correct on the facts.

**`business_operations.compliance-audit`** — seconds, then weakens itself.
> "for this row the key is real but secondary… this row's dominant cycle is NOT the fiscal calendar
> — a certification runs initial, surveillance, surveillance, recertification, joined by a
> certificate number across periods… R1c should weigh this row's vote for the key below
> budget-forecast's and board-governance's."

Concept: **an audit plan year** — but its real axis is a certification cycle, which is not a period.

**`business_operations.contract-administration`** — seconds *against its own interest*.
> "NOT this row's proposal… Its periods are CONTRACT periods — a term running from a commencement
> date to an expiry date, a notice window measured backwards from that expiry, a service-level
> quarter defined by a schedule. Those cycle on the agreement's own anniversary and routinely
> straddle two fiscal years, so filing a renewal notice under a fiscal period would separate it
> from the expiry it answers."

Concept: **an obligation anniversary**. Explicitly says it would not branch on the key.

**`business_operations.corporate-regulatory-filings`** — the sharpest warning in the corpus.
> "The periods on this row are not one thing. A statutory accounts period, a VAT quarter, a
> confirmation-statement AS-AT DATE and a registry event date are four different temporal objects,
> and only the first two are fiscal periods at all — **a confirmation statement has no period, it
> has an instant.** If `fiscal_period` lands as a single key, this row will be the one that most
> often has to abstain from writing it while still holding a date-shaped token, and that is the
> correct outcome rather than a gap. What this row will NOT do under any circumstance is write
> `tax_year`."

Concept: **the period a return answers for**, plus three temporal objects that are not periods.

**`business_operations.facilities-workplace`**
> "a PPM programme year and an inspection cycle are periods of a maintenance calendar, and their
> boundaries are set by service intervals and certificate validity, which no statutory year
> governs. A five-yearly electrical condition report and an annual gas check share a site and share
> no period."

Concept: **a maintenance-calendar period**. Dissents on ceiling — see §4.

**`business_operations.it-asset-inventory`**
> "a licence reconciliation and a stocktake are period artefacts of a management calendar, and a
> renewal or true-up date is set by a subscription term rather than by any statutory year."

Concept: **the management period a stocktake belongs to**. Warns its characteristic token is a
machine export timestamp (`intune_device_export_20260301.csv`), "a capture timestamp for a snapshot
and not a fiscal period at all."

**`business_operations.risk-register`**
> "the review cadence (quarterly register review, annual continuity test) is a real period fact of
> a management calendar that no statutory year governs."

Concept: **a review cadence**. Dissents on ceiling: "the most common date token on this row's files
is a NEXT-REVIEW date, which is prospective — it names a period the file is not from."

**`business_operations.support-operations`** — seconds with a scope doubt.
> "a support desk reports on an OPERATIONAL period — a week, a month, a rolling thirty days — far
> more often than on a fiscal one, and the recurring artifact here is `tickets_export_2026-05.csv`,
> not an FY-labelled deck. **If `fiscal_period` lands as a strictly fiscal key, this row will need a
> period concept it does not have**; it does NOT mint one here, because a monthly-operational
> variant would be exactly the synonym the contract forbids."

Concept: **an operational reporting month**. This row is a direct vote against the *name*.

**`law_practice`** (schema)
> "REUSE. Ten rows already propose `fiscal_period`; this is an eleventh use case, not an eleventh
> key. The billing month of a time export, the period of a disbursement ledger, the retention year
> on a closure record are content periods, not capture dates… Raised only so that the
> time-and-billing template author reuses it rather than minting `billing_period`."

Concept: **a content period**. Its `preferred_resolution`: "R1c adjudicates once for the roster."

**`law_practice.time-and-billing`**
> "REUSE, NOT A MINT, and this row is the use case the schema's own entry was raised for… A bill
> covers a stated period of work, a time export is cut by period, and a disbursement ledger is
> closed by period; that period is a CONTENT period."

Concept: **a billing period**. Mints nothing — explicitly refuses `billing_period`.

**`nonprofit`** (schema)
> "REUSE. Nine rows already propose `fiscal_period`… the nonprofit cycles — a grant period of
> performance, an appeal, a membership year, a restricted fund's carry-forward — are content
> periods… Note explicitly: **a GRANT period frequently does not align with the association's
> financial year**, which is one of the few places this family's period differs in kind."

Concept: **a grant period of performance**. Asks that if the key is adopted, "its definition permit
a named non-calendar award or appeal period, or that the misalignment be recorded so a later
`grant_period` proposal is not mistaken for a synonym mint."

### 1.2 `reporting_period` — 6 rows

**`resource_operations`** (schema)
> "No canonical key expresses the period the measured operation is ABOUT. `creation_date` is when
> bytes were created, `tax_year` is statutory finance, `term` is academic, `capture_year` is photos,
> and business_operations proposes `fiscal_period` for management cycles. This key covers daily
> production, monthly regulatory returns, crop years and metering intervals. **R1c should consider a
> globally neutral period key rather than proliferating period synonyms.**"

Concept: **the period a measured operation is about**. Example `June 2026 / crop year 2025-26 /
settlement interval 14:00-14:30` — note this row already proposes a **sub-daily** value.

**`resource_operations.grid-connection`**
> "SECOND the resource_operations schema's neutral period proposal. It applies only to recurring
> connection-compliance, curtailment or modification evidence after energisation."

**`resource_operations.mining-operations`**
> "SECONDING, NOT MINTING… A production month, extraction year, survey campaign or rehabilitation
> reporting year is not filesystem `creation_date`, Finance `tax_year`, Academic `term` or Photos
> `capture_year`."

**`resource_operations.oil-gas-operations`**
> "SECONDING, NOT MINTING… A drilling-report week and a production month are not filesystem
> `creation_date`, Finance `tax_year`, Academic `term` or Photos `capture_year`."

**`manufacturing.environmental-compliance`**
> "No canonical key names the interval an obligation covers… This key must carry the covered
> interval taken from a labelled Reporting Period, Monitoring Period, Return Period or Quarter slot,
> not the file date."
> `note_for_r1c`: "**If R1c prefers one global period key, this row will adopt it rather than retain
> a manufacturing-only synonym.**"

**`manufacturing.energy-audit`**
> "REUSE of the proposal already argued on `manufacturing.environmental-compliance`, not a new
> spelling. No canonical key names the interval a baseline or survey covers."
> `note_for_r1c`: "**Prefer one global period key shared with environmental-compliance rather than
> minting `audit_period` or `baseline_period`.**"

### 1.3 `record_period` — 3 rows

**`finance.payroll-received`** — the only proposer on a schema with live fields.
> "A pay statement normally identifies the interval whose earnings it reports, and that interval is
> the strongest distinction between a recurring payroll record and an offer, bank credit, annual tax
> form or account statement. `creation_date` is the timestamp of this file version, not the interval
> covered. `tax_year` is the tax role of a financial record, not a fortnightly or monthly pay
> period. **The broader `record_period` key is the same cross-record proposal already made by
> `finance.subscriptions-utilities`; it avoids minting a private `pay_period` synonym and leaves R1c
> one shared proposal to adjudicate.**"

Concept: **a pay period**. Example `2026-08-01 to 2026-08-15`. `destination_eligible: false`.

**`finance.subscriptions-utilities`** — the originating mint of this spelling.
> "A recurring record commonly labels the interval it covers, and that interval is the anchor that
> separates a service statement from a one-off receipt and one cycle from the next… **The broader
> name `record_period` is proposed instead of a private `billing_period` key because the same gap
> appears in account statements, coverage periods and other record series.**"

Concept: **a billing/service cycle**. Example `2026-07-14 to 2026-08-13`. `destination_eligible: false`.

**`retail_hospitality`** (schema) — refuses `fiscal_period` on the merits.
> "REUSE, NOT A MINT. `record_period` is already proposed by `finance.payroll-received` and
> `finance.subscriptions-utilities` for the bounded window a record covers, and a trading day or
> trading week is exactly that shape. **This row explicitly does NOT propose `fiscal_period` — the
> nine rows that want it want an ACCOUNTING period, and a trading day is an operational one;
> conflating them is how a till reconciliation would be mistaken for a management account.**"

Concept: **a trading period**. Raises the sub-daily caution answered in §2.3.

### 1.4 `planning_period` — 1 row

**`manufacturing.production-planning`**
> "No canonical field expresses the planning horizon or bucket the schedule is ABOUT. `creation_date`
> is byte metadata, `version_family` identifies versions, and `batch_lot` is produced quantity rather
> than a horizon. This proposal covers weekly, monthly, quarterly or rolling horizons; **R1c may
> replace it with one neutral period key.**"

Concept: **a planning horizon**. `NJ-PLAN-1` asks the merge question directly.

### 1.5 `aid_year` — 1 row

**`finance.student-financial-aid`**
> "Aid records repeatedly identify an aid, award, or academic funding period such as 2026-27.
> `tax_year` is the source year for tax information and can differ from the period being funded;
> `application_cycle` is scoped to College Applications and does not describe later disbursement or
> servicing records; `term` is scoped to Academic and may cover only part of an annual award."
> `note`: "**If R1c finds the same need in insurance, benefits, subscriptions, or grants, it should
> consider a broader shared period key rather than mint several near-synonyms.**"

Concept: **an award year**.

### 1.6 The 13 rows that want it and minted nothing

These do not appear in the 23 and must not be double-counted, but they are demand:

`business_operations.board-governance` ("this row's annual governance cycle wants [it] and…
SECONDS rather than minting a variant") · `finance.small-business-bookkeeping` ("Does the shared
vocabulary gain a destination-eligible `reporting_period` key…?") · `construction_property` ·
`construction_property.service-charge` · `government.emergency-management` ·
`resource_operations.farm-records` · `resource_operations.fisheries-catch` ·
`resource_operations.utility-metering-billing` · `retail_hospitality.ecommerce-ops` ·
`retail_hospitality.food-safety` · `retail_hospitality.menu-recipe-costing` ·
`retail_hospitality.pos-reporting` · `manufacturing.production-planning` (open_question `NJ-PLAN-1`)

Note `finance.small-business-bookkeeping` carries an **empty** `proposed_fields`. The brief was
right that it raises `reporting_period` — it does so in `open_question` only, deliberately:
"`proposed_fields` stays empty because one template must not settle either shared-schema decision by
minting a private field."

---

## 2. One key, two, or three?

### 2.1 Recommendation: **ONE key**, plus one hard exclusion rule. The collision is real.

The test this catalogue actually applies is not semantic tidiness. It is three questions: does one
rule family fill them, do they occupy the same tree position, and is the negative space identical.
All three answer yes, and the third answers yes *verbatim*.

**(a) One rule family.** Every one of the 23 names the same rule SHAPE: a period-shaped token in, or
beside, a **labelled period slot**. Only the slot *labels* differ — `finance.payroll-received` reads
"Pay Period, Period Beginning/Ending, From/To"; `manufacturing.environmental-compliance` reads
"Reporting Period, Monitoring Period, Return Period or Quarter"; `resource_operations.mining-operations`
reads "Reporting Period, Production Month, Extraction Year, Survey Date or Return Year";
`retail_hospitality` reads "Trading date, Business date, Week ending, Service, Session";
`manufacturing.production-planning` reads "Planning Horizon, Schedule Period, Requirement Period, MRP
Run Horizon or Bucket". A slot-label list is a **value-side gazetteer**, which is R2/R6's property.
`00` settles that this is not a reason for separate fields: *"The system may create new values when it
sees a new course, project, company, university, or event, but it should not invent new fields
automatically. Fields define the long-term organization language of the product; values are the
changing, user-specific content."*

**(b) One tree position.** All 23 independently reach *never first* or *never a folder level*, and
**21 of the 23 quote the same `00` sentence verbatim** somewhere in the row to get there — *"For
document and record domains, project, function, or subject usually comes before time because putting
year first scatters related work across calendar folders."* (The two that do not are
`resource_operations.grid-connection` and `finance.student-financial-aid`, which reach the same
conclusion in their own words.)
Nineteen propose `destination_eligible: true`-but-not-first; the two that propose `false`
(`finance.payroll-received`, `finance.subscriptions-utilities`) do so because per-cycle folders
fragment a history, which is a *narrowing of the same position*, not a different one. §3 shows the
contract already has the mechanism for that narrowing.

**(c) Identical negative space — the decisive evidence.** Twenty-three rows, in seven schemas, wrote
by different authors, ran the *same elimination and got the same answer*: not `creation_date` (byte
time), not `tax_year` (statutory), not `term` (academic), not `capture_year` (photos), not
`application_cycle` (applications). `resource_operations`, `manufacturing.environmental-compliance`,
`resource_operations.mining-operations` and `resource_operations.oil-gas-operations` write that list
in nearly the same word order. That is not three concepts independently discovered. **That is one
hole, found 23 times.**

And the rows themselves converge on one definition, in one sentence, across five families:

- `business_operations` — "which period the content is **ABOUT**"
- `resource_operations` — "the period the measured operation is **ABOUT**"
- `manufacturing.production-planning` — "the planning horizon or bucket the schedule is **ABOUT**"
- `law_practice` and `nonprofit` — "**content periods**, not capture dates" (identical wording)
- `retail_hospitality` — "the trading period a record **covers**"
- `finance.subscriptions-utilities` — "the interval it **covers**"
- `manufacturing.environmental-compliance` — "the interval an obligation **covers**"

**One concept: the bounded period the file's content is about, as opposed to when its bytes were made.**

### 2.2 The corpus's own two non-members — do NOT merge these

The brief asked whether the collision is illusory. For 23 rows it is not. But the corpus contains two
period-adjacent keys that **must stay out**, and in both cases their own authors already drew the line:

**`people_cycle`** — proposed by `hr` (schema) and seconded by `hr.compensation-planning`,
`hr.onboarding-offboarding`, `hr.training-development`. Four instances. `hr` names and refuses
`fiscal_period` explicitly:
> "`fiscal_period` is a business_operations proposal for a management calendar, `tax_year` is
> statutory, `term` is academic, and `creation_date` says when bytes were made rather than which
> onboarding, review, survey, pay, or consultation cycle they serve. **This is purpose-bearing
> process identity, not generic time.**"

A "2026 graduate intake" or "September 2026 intake" answers *which instance of a recurring process*,
not *what interval the content covers*. `hr.onboarding-offboarding` proves it: its value can be "the
2026-11-14 leaver event for one named individual" — an event identity whose date is only a label.
Merging would put an onboarding checklist and an oil-field production return on one folder level.
**Keep separate.**

**`trading_occasion`** — proposed by `retail_hospitality` (schema) and seconded by
`retail_hospitality.supplier-order`. The same author who proposes `record_period` drew this cut
deliberately, in one sentence:
> "`fiscal_period` and `record_period` are PERIODS, and **a period cannot hold a party size, a
> counted quantity or a room-night; they answer when, this key answers which occasion.**"

**Keep separate.** A booking, a stock count, a PO and a function are dated occurrences carrying a
counted quantity. A period carries nothing.

`capture_date` (`photos.camera-events`, `creative.raw-photo-catalogue`) and `lifecycle_stage`
(`engineering`) were also checked and are not members — the first is a capture timestamp, the second
a maturity gate.

### 2.3 Two open NEEDS-JOSEPH items that this cut answers for free

**`NJ-RH-5` / `NJ-POS-2` — may the period key be sub-daily?** `retail_hospitality` raised it because
"both existing proposals of `record_period` are multi-day ranges"; `retail_hospitality.pos-reporting`
restates it as a concrete requirement for "a breakfast service, a lunch sitting, a morning till
session, a night-club close that crosses midnight."

Answerable from the corpus without widening anything. **Yes, the key is already sub-daily** —
`resource_operations`'s own proposed example is `settlement interval 14:00-14:30`. Its author could
not see `retail_hospitality`'s question and vice versa. **And the service session `pos-reporting`
wants is not a period at all** — a dinner service has covers, so by `retail_hospitality`'s own test it
is a `trading_occasion`. The period key carries the interval; the occasion key carries the session.
Neither key stretches.

**`NJ-EC-2` — may it be an arbitrary export window?** `retail_hospitality.ecommerce-ops` wants "an
arbitrary user-chosen date RANGE with no operational meaning, because whoever pulled the report chose
the dates." **No.** That is the same object `business_operations.it-asset-inventory` warns about —
"a machine-generated EXPORT date… a capture timestamp for a snapshot and not a fiscal period at all."
An export window is a property of the *extraction act*, not of the content. It is excluded by rule 5
in §4. `ecommerce-ops` loses its proposed second dimension; that is the correct outcome and the row
already calls the alternative "survivable."

### 2.4 The one genuinely different temporal object — and why it is still not a second key

Six rows warn that their characteristic date token is **prospective** — a date the file *points at*,
not a period the file *belongs to*:

- `business_operations.facilities-workplace` — "a NEXT-DUE date… **A rule family that read a next-due
  date as a fiscal period would file a February 2026 certificate under 2027.**"
- `business_operations.risk-register` — "a NEXT-REVIEW date, which is prospective — it names a period
  the file is not from."
- `business_operations.contract-administration` — notice windows measured backwards from expiry.
- `business_operations.corporate-regulatory-filings` — "a confirmation statement has no period, it has
  an instant."
- `business_operations.compliance-audit` — a certification cycle "joined by a certificate number
  across periods," not by a period.
- `finance.subscriptions-utilities` — "a due date or a renewal date does not fill it."

They are right, and this is a real second temporal object. **It is still not a second key**, for two
reasons drawn from the corpus rather than from preference:

1. **No row proposed one.** Under the standing rule against minting, that ends it here.
2. **The corpus already REFUSED the node built on it.** `law_practice.deadlines-diary` carries
   `refuse_node: true`: *"There is no deadlines world to file. A limitation date, a service date, a
   listing date and a completion date are DATE-TYPE VALUES carried in a column of a register whose
   rows are matters… What is left over… is the word `deadline`, which names a temporal attribute of
   an obligation rather than a body of files — and which `00` never uses, in any form, anywhere."*

The correct treatment is an **exclusion rule on the one key** (rule 4 in §4), not a second column.
That exclusion is also precisely what the `possible` dissenters asked for — see §4.

### 2.5 What would make this a wrong merge, and why it does not apply

A wrong merge is worse than a duplicate: it would put two unrelated concepts on one folder level. The
merge here would be wrong if the members had different rule families, different tree positions, or
different negative spaces. They have none of those. The two things that genuinely *would* have been
wrong merges — `people_cycle` and `trading_occasion` — are excluded above, on their own authors'
arguments. **The three-way collision the brief describes is real and is one concept; the illusory part
is only that it is three-way. It is five-way.**

---

## 3. Canonical spelling

### 3.1 Recommendation: **`record_period`**

Losing spellings, to be recorded as `aliases` on the canonical row so they cannot be re-minted:
**`fiscal_period`**, **`reporting_period`**, **`planning_period`**, **`aid_year`**.

`canonical_fields.json` already has the mechanism and states its purpose: *"Aliases are strings that
must NOT become new keys."* `CONNECTION.md` §6: *"There are no field aliases: two spellings of a field
key are two columns, which is the defect D6's ratification exists to kill."* Recording the four losers
as aliases is how the file records a killed spelling.

### 3.2 Why not `fiscal_period`, despite 12 votes

**(a) The count is an artefact of one family seconding its own schema.** Nine of 12 are
`business_operations` rows seconding the `business_operations` schema row. It spans 3 schemas;
`reporting_period` and `record_period` span 2 each. Nobody wins on breadth, and the corpus warns
against the volume reading — `business_operations.contract-administration`: *"This row is NOT one of
those four and **should not be counted as support for the key by volume**."*

**(b) Five of its nine `business_operations` seconders say the word "fiscal" misdescribes their own
material.** `contract-administration` (anniversaries "routinely straddle two fiscal years"),
`compliance-audit` ("this row's dominant cycle is NOT the fiscal calendar"), `support-operations`
("If `fiscal_period` lands as a strictly fiscal key, this row will need a period concept it does not
have"), `corporate-regulatory-filings` ("only the first two are fiscal periods at all"),
`facilities-workplace` (boundaries "set by service intervals and certificate validity, which no
statutory year governs"). A key whose majority of seconders disown its name is the wrong name.

**(c) A schema outside the family refuses it on the merits.** `retail_hospitality`: *"conflating them
is how a till reconciliation would be mistaken for a management account."*

**(d) The registry blocker, and it is decisive.** `canonical_fields.json` **already registers
`fiscal_year` as an alias of `tax_year`.** Shipping `fiscal_period` would put `fiscal_year → tax_year`
and `fiscal_period → <new column>` inside one 37-row vocabulary — two fiscal-named strings, one letter
apart, resolving to different columns. That is the D6 defect (*"131 of them the same key spelled two
ways"*) reproduced in the one place the registry already has a fiscal-named string, and it re-opens
the exact `tax_year` conflation these 23 rows spent their entire argument refusing.

### 3.3 Why not `reporting_period`, despite the best cross-schema spread

It is the strongest runner-up: proposed independently by `resource_operations` and `manufacturing`,
named as the preferred spelling by `finance.small-business-bookkeeping`'s `open_question`, and it is
the literal string that appears most often as a *slot label* across the corpus.

But the name asserts an external report, and much of the material has none. A budget forecast reports
to nobody (`business_operations.budget-forecast`). A pay stub is not a report
(`finance.payroll-received`). A crop year is not a reporting period (`resource_operations`). Its own
strongest backer's value is a **"Baseline year 2025"** (`manufacturing.energy-audit`) — which is not a
reporting period either. Both `manufacturing` rows pre-committed to yielding: *"If R1c prefers one
global period key, this row will adopt it rather than retain a manufacturing-only synonym."*

### 3.4 Why `record_period` wins

1. **It asserts the least.** "Fiscal" claims accounting; "reporting" claims an obligation to report;
   "record" claims only that the thing is a record — which is true of every file in this product.
2. **It matches the one formulation all 23 rows converged on** (§2.1c): *the period the content
   covers*. `finance.subscriptions-utilities` chose the name for exactly that reason — "the broader
   name `record_period` is proposed instead of a private `billing_period` key **because the same gap
   appears in account statements, coverage periods and other record series**."
3. **It survives every value in the corpus**: `2026-08-01 to 2026-08-15` (pay), `Q2 2026` (permit
   return), `crop year 2025-26`, `settlement interval 14:00-14:30`, `FY2026` (board pack),
   `Week 12 2026` (trading), `Baseline year 2025` (energy), `2026-27` (aid award),
   `FY2026 Q3 / Week 35 horizon` (planning).
4. **It pairs with the live canonical `record_type`** — one of only 30 live fields, already declared
   on `finance`. "Record type / record period" reads as one matched pair on a fact row and in the
   template branch menu, which is a small but real UX gain.
5. **Two of its three proposers sit on the only claimant schema with live fields** (`finance`), so
   they are the only rows in the whole set that could bind it on day one. See §5.1.

**One caveat, stated so it is not adopted by accident: taking the NAME does not take its proposers'
`destination_eligible: false`.** See §4.1.

### 3.5 My alternative, clearly marked as mine — `covered_period`

**No row proposed this. It is my proposal, not the corpus's, and it is my second choice.**

`record_period`'s weakness is that "record" carries no information in a product where every file is a
record. `covered_period` names the actual discriminator — the period the content *covers*, against
`creation_date`, which is when the bytes were made — and that is the sentence 23 rows independently
wrote (§2.1c). It also reads correctly for every value in §3.4 point 3.

I recommend it **only** if the owner is willing to take a name no row minted. The D6 lesson is that
mints multiply, and `record_period` is already in the corpus's mouth. **Default to `record_period`.**

---

## 4. Where the key lands, and the two disagreements — preserved, not averaged

### 4.1 `destination_eligible` — recommend **TRUE**, and this is not a compromise

Nineteen of 23 proposals say `true`; two say `false` (`finance.payroll-received`,
`finance.subscriptions-utilities`); two are absent (`law_practice.time-and-billing` defers to its
schema, which says `destination_eligible_if_adopted: true`; `retail_hospitality` omits the field).

The `false` camp argues well. `finance.payroll-received`: *"It remains search/grouping metadata and
never a folder level, because one branch per pay cycle would fragment the employer history."*
`finance.subscriptions-utilities`: *"per-cycle branches would fragment the service history into tiny
folders"* — which is `00`'s own warning, *"creates a large number of tiny folders."*

**The contract already resolves this without a second key, and it resolves it in one direction only.**
`CONNECTION.md` §6:
> "**`destination_eligible` is per field**, recorded on the canonical row, with two overrides:
> authorship and creator-identity fields are never destination-eligible…, and **a schema may
> additionally forbid one of its fields as a folder level for its own domain (`metadata_only` on the
> template's dimension entry, P10's mechanism). A field's eligibility is never widened by a schema.**"

Eligibility narrows downward and never widens. So:

- **TRUE on the canonical row** + `metadata_only` on `finance`'s templates → both camps get exactly
  what they argued for.
- **FALSE on the canonical row** → permanently blocks the 19 rows that asked for TRUE, with no
  downstream repair available.

TRUE is the only value that satisfies both. **This is not averaging the disagreement away — it is the
one arrangement in which neither side loses anything.**

Plus one rule every single row demanded independently: **never first, and `time_first` stays false**.
`business_operations.corporate-regulatory-filings` states the cost of breaking it: *"A single filing
occurrence — the prepared return, the receipt, the acknowledgement — is scattered by a year-first tree
even though every member carries the same year."*

### 4.2 `reliability_ceiling` — the disagreement is not a disagreement

Raw tally across the 23: **`validated` 12 · `possible` 5 · `direct` 2 · absent 4.**

Read the `reliability_why` prose rather than the enum and the three camps stop conflicting — they are
describing **three different evidence sources**, each naming the state its own source supports. `00`
defines them as sources, not as a ranking:
> "A **direct** fact was read from a reliable and explicit source, such as a content hash, EXIF
> timestamp, document title, or **labeled form field**. A **validated** fact was found by a
> deterministic rule and **passed contextual checks**… A **possible** fact is a useful but
> insufficient clue."

`manufacturing.energy-audit` writes the whole ladder in one line: *"Direct from a labelled period
slot; possible from a filename token such as 2025 Baseline… Never validated alone."*

**Recommended ceiling ladder — the substance of the field:**

| # | Evidence source | State | Rows that wrote it |
|---|---|---|---|
| 1 | A **labelled period slot** — Pay Period, Period Beginning/Ending, From/To, Reporting Period, Monitoring Period, Return Period, Baseline Period, Business date, Week ending, Production Month, Crop Year, Settlement Interval, Planning Horizon | **`direct`** | `finance.payroll-received`, `finance.subscriptions-utilities`, `manufacturing.energy-audit`, `manufacturing.environmental-compliance` |
| 2 | A **period-shaped token co-occurring with a period-context term in the same labelled block** | **`validated`** | `business_operations` (+6 seconders), `resource_operations` (+3), `retail_hospitality`, `manufacturing.production-planning` |
| 3 | A **bare token** — filename year, sheet name, bare "Q2 2026" | **`possible`**, never higher | every row that mentions it |
| 4 | A **prospective date** — next-due, next-review, expiry, renewal, notice, as-at instant | **must not fill the field** | `facilities-workplace`, `risk-register`, `contract-administration`, `corporate-regulatory-filings`, `subscriptions-utilities` |
| 5 | A **filesystem or export timestamp** | **must not fill the field** | `it-asset-inventory`, `ecommerce-ops` (`NJ-EC-2`) |

**Rows 4 and 5 are the whole of the `possible` dissent, and they are not a lower ceiling — they are an
exclusion rule.** The five dissenters were not arguing the key is weak; they were arguing *their
material's characteristic token is not a period at all*. `business_operations.corporate-regulatory-filings`
says exactly this and calls the result correct: *"this row will be the one that most often has to
abstain from writing it while still holding a date-shaped token, **and that is the correct outcome
rather than a gap**."* With rules 4 and 5 written, the dissent is satisfied and the ceiling is not.

**Single stored value: `validated`.** `_CONTRACT.md` rule 4 requires that a `validated` claim be
backed by a `recognition.deterministic` entry that actually supports it. It is — I verified labelled
period-slot conjuncts inside the deterministic entries of `finance.payroll-received` ("an explicit
pay-period or period-ending slot"), `finance.subscriptions-utilities` ("a labelled billing or service
period"), `manufacturing.environmental-compliance` ("a labelled reporting period"), and
`business_operations.budget-forecast` ("a labelled period slot"). **Flagged for the owner:** whether
`direct` outranks `validated` is a §3.13 states question that is P1's, not this pass's. If `direct` is
the higher state, the stored value should be `direct` — route 1 reaches it. The ladder is the
substance either way; the single enum is a formality.

### 4.3 Where the key lands

| Schema | Live fields today | Rows demanding the key | Lands? |
|---|---|---|---|
| `finance` | **4** (`institution`, `account_type`, `tax_year`, `record_type`) | `payroll-received`, `subscriptions-utilities`, `student-financial-aid`, `small-business-bookkeeping` | **Yes — and it is the only schema that can bind it today.** `metadata_only` on its templates |
| `business_operations` | 0 (PR-6) | 10 | Yes, on PR-6 lift |
| `resource_operations` | 0 (PR-6) | 9 | Yes, on PR-6 lift |
| `manufacturing` | 0 (PR-6) | 5 | Yes, on PR-6 lift |
| `retail_hospitality` | 0 (PR-6) | 4 | Yes, on PR-6 lift |
| `law_practice` | 0 (PR-6) | 3 | Yes, on PR-6 lift |
| `nonprofit` | 0 (PR-6) | 3 | Yes, on PR-6 lift — with `nonprofit`'s misalignment note recorded (§1.1) |
| `construction_property` | 0 (PR-6) | 2 (prose only) | On PR-6 lift, if its own rows ask |
| `hr` | 0 (PR-6) | 0 — wants `people_cycle` instead | **No** (§2.2) |

`nonprofit`'s condition should be honoured verbatim: *"If `fiscal_period` is adopted, this row asks
that its definition permit a named non-calendar award or appeal period, **or that the misalignment be
recorded so a later `grant_period` proposal is not mistaken for a synonym mint**."* The recommended
definition — the bounded period the content covers — permits a named non-calendar award period, so the
condition is met, not deferred.

---

## 5. What breaks if the key is refused

### 5.1 Nothing breaks in folder trees today — and that is a real finding, not a dodge

Of the 23 proposers, **21 sit on field-less placeholder schemas** with `dimension_order: []` under
PR-6. They already have no levels; refusing the key takes nothing from them that PR-6 has not already
taken. The two exceptions are the `finance` templates, and both already work without it:

- `finance.payroll-received` — `dimension_order: ["institution", "tax_year", "record_type"]`;
  its `open_question`: *"This row remains usable either way: the period is not a dimension."*
- `finance.subscriptions-utilities` — `dimension_order: ["institution", "record_type"]`;
  *"If Joseph rejects the field, the recurring interval remains a deterministic activation signal and
  P9 grouping anchor rather than a file fact."*

### 5.2 Nothing breaks in activation either

Every recognition entry cites the period as a **structural slot** — evidence — not as a stored fact. A
deterministic rule can require "a labelled billing or service period" without a canonical column to
put it in. **No row loses activation.** Say this plainly to the owner: refusing the key does not make
any file unrecognisable.

### 5.3 What actually breaks is GROUPING — and `00` licenses the concept there by name

`00` lists the typed relationships in the node-local graph: *"shared validated facts, accepted group
membership, duplicate or version links, derivation links, compatible document type, **matching time
period**, direct references, mutual semantic retrieval, and user-confirmed membership."*

**"Matching time period" is a design-named grouping edge with no field to join on.** That is the
concrete cost, and it falls unevenly.

**Rows that lose their ONLY join — the period IS the anchor and members share no other fact:**

| Row | `grouping_reasons` entry that dies |
|---|---|
| `business_operations.budget-forecast` | "one fiscal period end to end: the budget, the reforecasts, the actuals comparison and the commentary" |
| `business_operations` (schema) | "one fiscal period's close across budgets, actuals, returns and the audit evidence that tested them" |
| `business_operations.support-operations` | "one reporting period: the export, the charts built from it and the commentary written on top — a purpose-coherent set produced on one date" |
| `manufacturing.energy-audit` | "one baseline period across the meter exports and the report that consumes them" |
| `manufacturing.environmental-compliance` | "one reporting period across the return, the certificates supporting it, the covering submission and the acknowledgement" |

These five are the real casualties. Each is a **purpose-coherent, content-incoherent** group — `00`'s
own hardest case (*"The documents are content-incoherent but purpose-coherent"*) — and the period is
the only fact its members share. A budget model, a variance commentary and an actuals extract have no
shared institution, no shared project, no shared document type. Without the period they are five
unrelated files.

**Rows that lose half a join (a co-anchor survives) — degraded, not broken:**

- `law_practice.time-and-billing` — "joined by one exact matter reference **and one stated period**";
  the matter reference survives. Note this row already lists "a shared billing month" among its **NOT**
  grouping reasons, so the period was never the join on its own.
- `finance.subscriptions-utilities` — "for the same labelled account **and covered period**"; the
  account survives.
- `finance.payroll-received` — "one pay-period record across an original statement, correction and
  reissued copy"; `version_family` and content hash survive and the row says so.

**Rows that lose nothing — do not cite these as breakage.** Their joins are elsewhere and they say so:
`business_operations.compliance-audit` ("joined by a standard reference and a certificate number"),
`business_operations.corporate-regulatory-filings` ("joined by a return name and an entity
identifier"), `business_operations.contract-administration` (the instrument),
`business_operations.risk-register` ("a workbook re-saved each quarter is a version family, not four
domains"), `law_practice` (the matter reference).

### 5.4 The text-consistency consequence, whichever way it goes

**48 rows across 9 schemas already name one of the five spellings in prose.** Six write
`record_period` into `grouping_reasons` and `must_not_conclude` as though it exists — e.g.
`finance.payroll-received`: *"Sparse notices may join without inheriting institution, account_holder or
record_period."* Two **refused** rows write `must_not_conclude` entries against it —
`law_practice.deadlines-diary`: *"a fiscal_period or tax_year fact — neither key is declared on this
schema"*; `nonprofit.grant-reporting`: *"a fiscal_period or sponsor fact — those keys are unadjudicated
proposals on the schema."*

- **If refused:** 48 rows are left referencing a fact that will never exist. Each needs its prose
  corrected or the reference will read as a live key to every future author — which is how a killed
  spelling gets re-minted.
- **If adopted as `record_period`:** **43 rows** need a mechanical rename off a losing spelling;
  **6 rows** already use the winning spelling and need no change (`retail_hospitality` appears in
  both, naming `record_period` in its proposal and `fiscal_period` in the sentence refusing it).
  The rename is mechanical — `CONNECTION.md` notes "the fold in `check.py` is the single place spelling
  is enforced and the catalogue re-normalizes mechanically."

---

## 6. My own proposals — clearly marked, none of these came from a row

1. **`covered_period` as an alternative spelling** — §3.5. Second choice. Default to `record_period`.
2. **Record the prospective-date residue without minting a key for it.** Rules 4 and 5 of §4.2 tell
   the period key to refuse next-due, next-review, expiry, notice and as-at dates, and six rows carry
   those as their *characteristic* token. No row proposed a key for them and
   `law_practice.deadlines-diary` was refused for being built on them, so **do not mint one now**. But
   record the residue in the same way `nonprofit` asked for its grant misalignment to be recorded, so
   that a later `due_date` or `next_review` proposal is recognised as a **new concept rather than a
   synonym of the period key** and is not rejected by reflex. Without that note, the D6 gate would
   correctly refuse a legitimate future field.
3. **Adopt the ladder, not just the enum.** §4.2's five-row table is the field's actual definition.
   If only the single `reliability_ceiling` value is carried forward, the exclusion rules that
   reconcile the five dissenters are lost, and `business_operations.facilities-workplace`'s failure
   mode ships: *"a February 2026 certificate [filed] under 2027."*

---

## 7. The decision the owner is being asked to make

**Adopt ONE canonical field, spelled `record_period`**, on `canonical_fields.json`, with:

- **`destination_eligible: true`**, never first, `time_first: false`; `finance` narrows to
  `metadata_only` (§4.1)
- **`reliability_ceiling: validated`**, governed by the five-rule ladder in §4.2
- **`aliases: ["fiscal_period", "reporting_period", "planning_period", "aid_year", "record period"]`**
  so no losing spelling can be re-minted
- landing on `finance` now (the only claimant with live fields) and on `business_operations`,
  `resource_operations`, `manufacturing`, `retail_hospitality`, `law_practice`, `nonprofit` when PR-6
  lifts
- **not** merged with `people_cycle` (`hr`) or `trading_occasion` (`retail_hospitality`) (§2.2)

**Refusing it is a defensible choice** — nothing breaks in activation and nothing breaks in any folder
tree today (§5.1–5.2). The price is five purpose-coherent groups that lose their only join (§5.3), a
`00`-named grouping edge with nothing to join on, and 48 rows left pointing at a fact that will never
exist (§5.4).

**What is not defensible is leaving it open.** Five schema rows have deferred it to this adjudication
by name, two `manufacturing` rows have pre-committed to adopting whatever wins, and every day it stays
open is another chance for a template author to mint `billing_period`, `audit_period`,
`baseline_period` or `grant_period` — the exact failure `law_practice` and both `manufacturing` rows
wrote their proposals to prevent.
