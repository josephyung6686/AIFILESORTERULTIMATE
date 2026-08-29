# `business_operations.budget-forecast` — lab notes (template row, deepened to J-DEPTH)

Row kind: **template** on `business_operations`. Launch: **placeholder** (`fields: []`).
Verdict: **kept, not refused** — but the verdict is narrower than the gist draft's, and the
narrowing is the substance of this pass.

**Status of this file.** The row was first written under the retired J-IND *gist* standard and
carried a 3.8KB memo against a 27KB JSON. J-DEPTH (ratified 2026-08-24) overrules the gist clause.
The JSON was **verified-but-shallow, not untrusted** — its quotations were machine-checked verbatim,
its key set matched the landed siblings, and its arguments, where it made any, were sound — so it
was **deepened by five surgical edits, not rewritten**. Every one of the gist draft's positions is
either preserved verbatim or explicitly argued against by name. Nothing was silently reversed.
The itemised list is under *Salvage and deepening* at the end.

---

## Sources actually used

### Binding local sources

- `planning/00-database-agent-product-design.md` — the only document quoted, throughout, verbatim.
  The spans that did real work on **this** row, and what each decided:
  - the **universal-facts sentence** — *"The product should have a small shared set of universal
    file facts, such as file type, creation date, language, duplicate family, version family, and
    sensitivity status."* — and its companion, that a file can be *"a member of a version family"*
    among its other facts. These two spans are the load-bearing evidence for this row's hardest
    question, the budget-versus-forecast split, argued in full below.
  - the **hash-versus-filename rule** — *"A content-hash match supports deduplication review; a
    filename match alone does not."* — and the collision policy that may *"retain the newer file
    while placing an older version into a version family review"*. This row's corpus is where
    `FINAL`, `v7` and `(2)` are densest and lie most often, so this sentence became a new
    `never_alone` entry in this pass.
  - the **table sentence** — *"Tables matter because resumes, forms, applications, invoices, and
    administrative documents often place their most useful information in cells rather than body
    paragraphs."* — the licence for reading a budget/forecast/actual/variance column set at all.
  - the **schema-activation sentence** — *"It should then activate domain-specific schemas only
    when the evidence indicates that a domain is plausible."* — with its enumeration, which is where
    *"Finance files may use institution, account type, tax year, and record type"* comes from. Note
    what that list does **not** contain: a period key that is not a tax year. That absence is why
    `fiscal_period` exists as a proposal and why `tax_year` must not be stretched to cover it.
  - the **topic/purpose distinction** — *"Topic answers what a file is about, while purpose answers
    what the file was for."* — the only test that separates a real submission from a blank template,
    a downloaded model, or an MBA exercise, all of which are structurally identical to the real
    thing with values removed.
  - the **abstention sentence** — *"Correct abstention is a successful outcome because the
    product's goal is reliable organization, not maximum file movement."* — invoked here more often
    than on most rows, because the sole-trader case and the management/custodial fork genuinely do
    not resolve on many real files.
  - the **multi-role token sentence** — *"A university name alone should not create a group because
    Columbia can appear as an authoring school, course provider, target institution, employer,
    research venue, or merely a cited organization."* — read across to a **company** name as an
    **inference**, and marked as inference wherever used. This is the sentence the schema anchor
    generalised into the never-alone principle this row must apply.
  - the **collector prohibition** — *"A folder should not become a collection point for everything
    produced by the same person or organization."*
  - the **dimension-order rule** — *"For document and record domains, project, function, or subject
    usually comes before time because putting year first scatters related work across calendar
    folders."* — which is the rule this row is most tempted to break, because it is *made* of
    periods. It does not break it; `time_first: false` stands.
  - the **purpose-coherence sentence** — *"The documents are content-incoherent but
    purpose-coherent."* — the licence for the planning-round group.
  - the **sparse-file rule** — *"The graph does not automatically copy those missing facts onto
    sparse files."*
  - the **abstention-under-model rule** — *"A model that cannot cite sufficient evidence must return
    unknown."*
  - the residual definitions, for all five fallthroughs this row uses.
- `planning/domains/_CONTRACT.md` — rules 1–3 (provenance, no fabricated quotes, no numbers), 6
  (residuals stay out of this namespace), 8 (a dimension may only branch on a declared field), 10
  and 15 (no field rows on a placeholder schema), 11–14 (`kind`, closed edge vocabulary).
- `planning/domains/CONNECTION.md` — §2 node test, §4 activation (step 2 never-alone; step 5
  protective ordering, which decides this row's `finance` seam), §5 closed edge vocabulary and
  **invariant 1**, which licenses carrying both `collides_with` and `also_holds_with` to the same
  neighbour when the collision names discriminating evidence. §6 field identity, which is what makes
  `fiscal_period`-versus-`reporting_period` a defect rather than a nicety.
- `planning/domains/canonical_fields.json` — confirmed **no** canonical key holds a management
  period. **No key minted here**; the schema row's proposal is seconded, not varied.
- `planning/overnight/council/DECISION-BRIEF.md` — D1 (as narrowed), D6, PR-2, PR-6 taken as
  ratified and not re-debated.
- `ROSTER.md` Appendix A — this row absorbs one legacy id, `ops.operating-plan-budget` (ROW).
  One id, not a cluster; that matters to the fold question below.

### The schema anchor, read first and applied explicitly

`business_operations.research.md` (46KB, J-DEPTH) is this row's measuring stick. Three of its
statements bind here and each is answered explicitly rather than gestured at:

1. **The default template paragraph.** *"the organisational unit or entity only where the corpus
   genuinely spans more than one → the governance body, project, contract, or account the material
   belongs to → the fiscal period → the document function. Not time-first."* This row must differ
   from **that**, not from a generic notion of the family. It does — see leg 2.
2. **The no-sibling-may-claim-time-first rule.** *"A budget year, a board year and a filing year are
   all content periods, not capture dates. A sibling claiming `time_first: true` is claiming the
   photos exception without the photos evidence."* This row is the family's most tempting
   time-first candidate and **does not claim it**. `time_first: false` holds and the prose
   recommendation deliberately puts the unit above the period.
3. **The never-alone principle, applied to this row.** *"No sibling may rest its activation on an
   entity name, a business vocabulary word, or a document shape alone. Every detection signal a
   sibling writes must pair a **structure** with a **labelled slot**."* Applied literally below.

### Landed neighbours read before writing, and not touched

`finance.json`, `finance.small-business-bookkeeping.json` + memo, `finance.cap-table-equity.json` +
memo, `finance.research.md`, `business_operations.strategy-plan.json`,
`business_operations.risk-register.json`, `business_operations.organisational-records.json` (the
family's exemplary refusal), `construction_property.json` (for the shared `organization` proposal).

---

## Applying the never-alone principle to this row, literally

The schema anchor's rule: **structure + labelled slot, or it is not a signal.** This row's eight
deterministic entries were audited against it in this pass. Each pairs a structure with a slot:

| Structure | Labelled slot it must pair with |
|---|---|
| period column series × budget/forecast/actual/variance column set over line items | the column headers themselves, *and* the **absence** of an account-number-and-balance header |
| several files/sheets of one model differing by scenario or round label | a labelled scenario or round slot (base / downside / submitted / approved) |
| circulated submission template | a labelled unit-or-cost-centre slot **and** a labelled period slot **and** a deadline instruction |
| variance prose keyed to line items | a favourable/adverse marker or a named cost centre per paragraph |
| assumptions block feeding a calculated schedule | input cells visibly separated from formula cells |
| email round-instruction | a labelled subject slot naming a round or period + an attachment-name slot |
| parent folder naming a round, period or cost centre | **never alone** — explicitly a plausibility raiser, only once a structure above is present |

And the ten `never_alone` entries are the honest half. The three that matter most here:

- **A fiscal-year-shaped token alone** (`FY26`, `2026-27`) is the single most tempting signal this
  row has, and it appears identically on statutory returns, academic years, contract terms, sports
  seasons and football-club accounts.
- **A company gazetteer hit alone.** The *Columbia* sentence read across to a company, as inference:
  a company name appears as employer, customer, supplier, competitor, regulator, and as the
  letterhead of a document merely *about* the holder.
- **A filename version or finality token alone** — new in this pass, and the row's sharpest
  self-restraint. *"A content-hash match supports deduplication review; a filename match alone does
  not."* `FY26 budget v7 FINAL (2).xlsx` looks like a version family and may be three unrelated
  workbooks a person renamed.

---

## The node test, all three legs, argued

CONNECTION §2's **template** test: a template row exists only when its **detection signals**,
**recommended dimensions**, or **privacy rules** differ from its schema's default template. The
dimensions leg is unavailable to all 24 siblings equally under D1-as-narrowed and PR-6, so the row
must carry legs 1 and 3, and it must carry them against the anchor's default paragraph specifically.

### Leg 1 — detection signals distinct from the schema's default

**Passes, and this is the row's strongest leg.** The anchor's four family-level signal shapes are
the governance cycle, the controlled-document header, the management-financial table, and the
post-signature obligation register. Two of the four are irrelevant here. The third — *"a
budget/forecast/actual/variance column set over line items, with no account-number-and-balance
header"* — is, in the anchor's own words, the family's signal, and the anchor states it in this
row's vocabulary because this is the row it was written for.

That is a real risk to leg 1 and it must be faced rather than skipped: **if this row's only signal
is the family's own third signal, it is the default template and it should refuse.** Two structures
save it, and neither belongs to any other sibling:

1. **The round structure.** A budget is not a document, it is a *circulation*: an instruction with a
   deadline, a blank template with a labelled unit slot, N filled returns from N units, a
   consolidation, a challenge exchange, an approval. The template travels out blank and comes back
   filled, so **both states exist in one real corpus** and the blank one is a false positive for
   itself. No other sibling has an artifact that is evidence in one state and a Reference Clip in
   the other. This is genuinely a distinct detection problem, not a distinct topic.
2. **The scenario/round versioning structure.** Base / upside / downside, or v1 / submitted /
   approved, as *parallel* rather than *superseding* copies. This is the row where the universal
   `version_family` fact does the most work — and, as argued below, it does that work **as a
   universal fact**, which is a constraint on this row rather than a licence for it.

The variance-commentary structure — prose paragraphs keyed to line items with a favourable/adverse
marker — is a third, and it is the one shape here that is not a table at all.

### Leg 2 — recommended dimensions

**Unavailable, and honestly reported as unavailable.** `dimension_order` is `[]` by contract; a
dimension may only branch on a field the same schema declares, and this schema declares none.
The prose recommendation — unit or cost centre → planning round or fiscal period → document
function — **is not materially different** from the anchor's default paragraph with its middle level
specialised. This row does **not** claim leg 2, and no sibling should claim it while D1's deferral
stands. Recording that as a non-claim is more useful to R1c than dressing the same order up as a
difference.

The one thing this row does add is a **temptation resisted**: the period is the level a finance user
reliably asks for first, and putting it first would scatter one planning round across calendar
folders exactly as `00` describes. `time_first: false`.

### Leg 3 — privacy rules distinct from the schema's default

**Passes, on a difference of kind rather than degree.** The family's default posture is
`potentially_sensitive` because the exposed party is often a third party. This row narrows that to
something sharper and more mechanical:

- **The transition happens at one column.** A cost-centre budget is impersonal; add a name column
  and it is `hr` material about identified employees. A headcount model with a redundancy scenario
  names individuals in a document that is confidential *to them* and often unannounced. The family's
  posture is "usually third-party confidential"; this row's is "**impersonal until a specific column
  appears, then strictly protected**", and that is an operational rule the default does not state.
- **The unannounced-plan case.** A forecast that reveals a closure, a raise round, or a redundancy
  programme is confidential in a way a policy handbook is not — its harm is in the *timing* of
  disclosure, not the content. `Protected Records` is in `falls_through_to` for exactly this.
- The row assigns **only** the catalogue value `potentially_sensitive`, carries **no**
  `is_safety_domain` (that flag stays with `00`'s four), and sets **no** P7 handling class.

**Overall: kept.** Leg 1 passes on the round and scenario structures; leg 2 is explicitly not
claimed; leg 3 passes.

---

## The row-specific question 1: is a budget and a forecast one situation or two?

The dispatch is right to press this and the gist draft did not answer it. **This row holds them as
one situation, and the argument is a design one, not a convenience.**

A budget is agreed once and fixed. A forecast is revised repeatedly. That is a real difference in
*authority*, and it is tempting to read it as two nodes. It is not, for two reasons:

1. **The revision sequence is a universal fact, not a domain fact.** `00` puts *"duplicate family,
   version family, and sensitivity status"* in the **small shared set of universal file facts**,
   computed for every file regardless of which schema activates, and says a file may be *"a member
   of a version family"* alongside its domain facts. A row whose only discriminator is "this one has
   successors and that one does not" would be minting a node out of a fact the product already
   computes for free. That is the 574's mistake wearing a new costume: a label promoted to a node.
2. **The evidence does not separate them anyway.** A reforecast and the budget it revises share the
   same workbook, the same column set, the same units, the same period labels and usually the same
   file lineage. The only reliable discriminator is a labelled `Approved` / `Submitted` / `Forecast
   v3` slot — which is a **value**, and values are `work_type` entries, not nodes. Both are already
   in `work_types` ("approved budget", "forecast or reforecast"), which is where they belong.

**The cost of not splitting, stated rather than smoothed:** a fixed approved budget carries
organisational *authority* that a working reforecast does not, and one situation cannot express
that. If a downstream consumer ever needs authority-versus-draft as a first-class distinction, the
right fix is a `work_type` value plus the universal `version_family`, **not** a second node. Filed
as **NJ-BF-1**.

## The row-specific question 2: is a company budget distinguishable from a household budget?

The dispatch's test: *if the only discriminator is that a company made it, that is an organisation
name, which the never-alone principle says cannot activate a row on its own.* Correct, and the
answer is uncomfortable in exactly one case.

`Household budget 2026.xlsx` and a unit budget are **structurally identical**: labelled period
columns, a plan/actual pair, a line-item row set, totals. `finance` already carries *"budget sheet"*
in its own `work_types`, and `finance.small-business-bookkeeping` names *"a personal budget"* among
the things a bare spreadsheet might be. So what discriminates is **not** the entity name — the
never-alone principle forbids that — but the **row set and the surrounding furniture**:

- rent, groceries, utilities, a single named holder, no approver → the personal side;
- cost centres or department codes, headcount lines, a budget-holder slot, a submission deadline, an
  approval line, N unit returns around it → this row.

That is a structure-plus-labelled-slot pair, so it satisfies the principle. **But it fails for a
sole trader**, where the household budget and the business budget are genuinely one file with one
row set and no approver, because there is nobody to approve to. This is not an exotic edge case in a
personal-file product; freelancers are a large part of the intended corpus. The provisional posture
is **abstention**, not a guess — *"Correct abstention is a successful outcome because the product's
goal is reliable organization, not maximum file movement."* Filed as **NJ-BF-3** (renumbered from
the gist draft's NJ-BO-5, which the deepened schema anchor has since reassigned to the buying-side
role key — the collision is noted so R1c does not merge two unrelated items).

---

## Files considered and rejected

The dispatch's test: *a row that only lists what it holds has not been researched.* Ten fixtures are
carried in the JSON. These are the tempting files that are **not** this row's evidence, and what
discriminates each.

| File | Why it is **not** this row's evidence |
|---|---|
| `Budget submission template - blank.xlsx` (**carried as a fixture, deliberately**) | Complete structure — units, periods, variance columns, an approval line — and not one value. Every deterministic signal this row owns fires on it. *"Topic answers what a file is about, while purpose answers what the file was for."* It was for *collecting* a plan, not stating one. **Reference Clips.** Kept as a fixture rather than rejected because a real corpus contains the blank and the filled copy side by side. |
| `Household budget 2026.xlsx` (**carried as a fixture**) | See above. Kept because the honest admission is worth more than a clean row. |
| `Management accounts - March 2026.pdf` (**carried as a fixture**) | One PDF holding a budget-comparison column set (management, this row) *and* a balance sheet with an accountant's compilation note (custodial, `finance.small-business-bookkeeping`). The fixture exists to hold NJ-J-IND-3 open in a file rather than in prose. |
| A **downloaded FP&A model** or a three-statement model from a training site | Richer than most real budgets, with driver blocks and scenario switches. Purpose, not topic, again: nobody's plan. **Reference Clips.** |
| A **saved industry benchmark report** ("SaaS metrics 2026") | Dense in exactly this row's vocabulary — run rate, forecast, variance — and belonging to nobody's planning round. **Reading Inbox** at family level. |
| An **MBA budgeting exercise** or a case-study pack | Identical structure with values, in an academic context. `academic` fires on its own evidence; this row must not fire on business words. No edge — the discriminator is the academic context term, which is `academic`'s to detect. |
| A **grant budget** | Real, and a genuine collision — a grant budget *is* a period-scoped line-item plan. But its anchor is an **award**, not a planning round, and the situation belongs to `research.grants-funding` and `nonprofit.grant-reporting`. Deliberately **not claimed** and deliberately **not edged**: `finance.research.md` already reached the same conclusion independently, calling a grant budget *"a `project`-anchored research artifact whose money content is the never-alone figure, so no edge."* Two rows reaching the same verdict separately is worth recording. |
| A **project cost report** | Left as a `collides_with` against `business_operations.project-delivery` rather than a fixture. A project identifier with milestones and a status structure is that row's; a unit-and-round structure is this one's. |
| A **bank statement** with a spending-by-category summary page | Money, categories, a period. But the institution-and-account header is present, which is `finance`'s constitutive evidence and this row's constitutive **absence**. Not a close call — recorded because it is the shape a naive category-based detector would take. |
| An **invoice log** or an AR aging sheet | A grid of money over periods. It reports what *has* happened at transaction grain; `finance.small-business-bookkeeping` names AR aging as its own fixture explicitly. |
| A **payslip** or a personal pay-and-tax summary | An individual's money record. `finance.payroll-received`. Contributes nothing to a unit plan even when filed beside one. |
| A **`.qbb` / accounting-package backup** | Extension-shaped temptation. *"treat the file extension as a routing signal rather than an assumption about meaning"*, and `finance.small-business-bookkeeping` already owns the routing. |
| A **CRM revenue pipeline export** | Forward-looking money, which is genuinely this row's phrase. But it is a system dump at opportunity grain with no unit, no round and no approver — and its interesting members are contacts data. `business_operations.customer-account-management` at best; more honestly a residual. |

---

## The collision fixture, in both directions

### The file that would wrongly fire this row

**`Budget submission template - blank.xlsx`.** Labelled cost-centre column, labelled period columns,
a variance column, an approval line, a deadline in the instruction sheet, a company name on the
sheet header. **Every** deterministic signal this row owns fires. It is not evidence of a plan; it
is evidence that a plan was *requested*.

**What discriminates:** whether the value cells carry commitments. Empty, `[Cost centre]`, or
`0` across the board is a template. That is a `needs_llm` determination and *"A model that cannot
cite sufficient evidence must return unknown."* applies without softening.

**What emphatically does not discriminate:** the company name on the header. *"PDF metadata should
be treated as supporting evidence, not as truth"* — a corporate template stamps the same entity on
every blank form it ever generated, including the ones a former employee kept.

### The file that must not be lost *to* this row

**`Management accounts - March 2026.pdf`**, and — the sharper one — **the workbook that holds a
forecast sheet and a reconciled-actuals sheet**. If this row activates on the forecast sheet and
takes the file, a **custodial accounting record on a safety schema** has been pulled onto a
non-safety one. That is the wrong direction on a protection question. CONNECTION §4 step 5's
protective ordering is the answer: where both are evidenced, `finance` runs first. The new
`also_holds_with` edge to `finance.small-business-bookkeeping` records that the correct outcome is
**both, on disjoint evidence**, not a winner.

### The same bytes, named on both sides

`FY26 budget v7 FINAL (2).xlsx` is named as a fixture here **and** by the deepened
`business_operations` schema anchor as its finance-seam fixture, with the same discriminator
(absence of the institution header). The two sides agree.
`Management Accounts - Blue Finch Studio - June 2026.xlsx` is `finance.small-business-bookkeeping`'s
own fixture; this row's `Management accounts - March 2026.pdf` is deliberately the same document
type from the other side. Neither file's memo contradicts the other.

---

## Reciprocal boundaries, both directions

The `finance.*` seam is this row's sharpest because the roster's triage **deliberately folded the
corporate accounting rows onto `finance`**. Each line below was written after reading the
neighbour's own file, and where this row diverges from a landed row it says so.

| Neighbour | This row must **not** take | The neighbour must **not** take | Shared fixture bytes |
|---|---|---|---|
| **`finance`** (landed, SAFETY, 4 fields) | anything carrying an institution-and-account header, a statutory issuer, a double-entry structure, or a personal holder — and, where evidence is unsettled, the file at all: protective ordering means the safety schema wins | a **plan of money that has not happened yet** — a submission, a consolidation, a reforecast, variance commentary — merely because it is money in a spreadsheet | `FY26 budget v7 FINAL (2).xlsx`; `Household budget 2026.xlsx` |
| **`finance.small-business-bookkeeping`** (landed) | journals, ledgers, trial balances, sales invoices, vendor bills, reconciliations, AR aging, accounting-package backups and exports — that row is function-first and owns the working book | the **management layer above the book**: the forecast sheet, the variance narrative, the board finance appendix, the driver model | the workbook holding a forecast sheet **and** a reconciled-actuals sheet — `also_holds_with`, disjoint evidence, one item never counting twice |
| **`finance.personal-records`** | a household or individual budget: rent/groceries rows, a single named holder, no approver | a **unit** budget merely because a personal machine holds it | `Household budget 2026.xlsx`, which for a sole trader is genuinely one file and where **both** must abstain |
| **`finance.cap-table-equity`** (landed) | a share register, an option ledger, a waterfall, a funding-round instrument or a valuation — its anchor is an **ownership stake**, a durable claim, not a period | a **financial model that happens to include a funding assumption** — a cash-flow forecast with a raise in it is a plan, not a cap table | a financial model whose assumptions tab names a raise: the assumption is this row's, the instrument it references is that row's |
| **`business_operations.strategy-plan`** (landed sibling, **two-way**) | an argument comparing options over a multi-year horizon; goals, initiatives, horizons with no line-item comparison. That row's own edge states this and **is accepted verbatim** | a **period-scoped set of line items with variance against actuals** | a business case, which that row names and which is a financial model with a narrative wrapped round it |
| **`business_operations.risk-register`** | a standing likelihood/impact register with owners and review dates. **No edge, and the reason is symmetric:** a downside scenario in a budget is a *number*, a risk register entry is a *governed record*; the register row's own file does not name this row either, and the omission is correct on both sides | a **downside or sensitivity scenario** merely because it models something going wrong | none in common |
| **`business_operations.board-governance`** | a pack index, attendance, resolutions | a **standalone model or commentary** with a period column set | a board pack containing a finance appendix — a real file, not a defect |
| **`business_operations.project-delivery`** | a project identifier with milestones, schedule and status structure | a **unit-and-round** planning cycle | a project cost report |
| **`hr.compensation-planning`** (schema not yet written) | anything naming **individuals**, salary bands, or personal review outcomes — protected before any model path | roles, FTE counts and aggregate cost with no names | one **headcount model** that crosses at the column where names appear; the stricter side wins |
| **`career`** | a document held to evidence the **individual's own** standing or remuneration | the organisation's **population-level** version of the same numbers | a compensation plan; an expense budget versus an expense claim |

**A finding carried forward from the schema anchor and confirmed here:** apart from the sibling
`strategy-plan`, **no landed row names this one**. `finance`, `finance.small-business-bookkeeping`
and `finance.cap-table-equity` were written before this row landed and carry no return edge. Nine of
the ten boundaries above are therefore **authored one-way from this side, and R1c owes the
reciprocals.** That is a catalogue defect, not a judgement about the seams.

### The `finance` "budget sheet" problem, stated plainly

This is the one place where a landed row and this row appear to claim the same thing outright.
`finance.json`'s `work_types` list contains **`"budget sheet"`**. That is a landed safety schema
declaring budget-shaped material as one of its own work types, and it predates this row.

**This row does not contradict it and does not ask for its removal.** The reading offered to R1c,
and now written into `collides_with`: a work type is a **value**, not a node — the dispatch is
explicit that *"work types are values"* — so what `finance` owns through `"budget sheet"` is a
budget sheet that arrives **with finance's own evidence**: an institution header, a statutory
issuer, or a personal holder. A budget sheet arriving with a unit-and-round structure and none of
those is this row's. Where neither is evidenced, `finance` is a safety schema and wins the file.

If R1c disagrees and reads `"budget sheet"` as a claim on the situation itself, then this row should
**fold into `finance`** and the coverage routes there. That outcome is named here rather than
defended against, because it is a defensible reading of a landed row.

---

## Neighbours considered that did **not** get an edge, and why

- **`government.grant-programme-administration`** — a public programme budget is the same tables.
  Unedged: the discriminator (a public grant programme with an issuing authority) is stated at
  family level and adding a per-row edge would duplicate it.
- **`nonprofit.fundraising-donor`** — income forecasting overlaps genuinely. Same reason; the
  owner-type discriminator is the family's.
- **`research.grants-funding`** — a grant budget genuinely collides, but the anchor is an **award**,
  not a planning round. Unedged, and `finance.research.md` independently reached the same verdict
  for the same file. Noted for R1c to confirm rather than asserted.
- **`academic`** — an MBA budgeting exercise is byte-similar. Unedged because the discriminator is
  an academic context term, which is `academic`'s evidence to find, not a seam to negotiate.
- **`code`** — a financial model in a repository. Unedged: the repository root exclusion already
  settles it and this row must not propose re-filing anything inside a preserved repo.
- **`business_operations.vendor-management`** — a procurement spend forecast. Unedged: contract and
  supplier anchors are that row's, and the shared object is the never-alone money figure.

---

## `proposed_fields` — one entry, and it is a seconding

**`fiscal_period`, seconded, not minted.** The dispatch instructed reuse over variants and that is
what happened: the entry copies the schema row's key, type, example, eligibility and reliability
verbatim in substance and adds no synonym. Of the four rows in the family that cycle annually, this
is the one that needs it most — a budget without a period is not a budget.

The entry earns its place by carrying a **conflict the schema row could not see**. The landed
`finance.small-business-bookkeeping` row raises the *identical concept* in its own `open_question`,
under a **different name**, having rejected `tax_year` for the same reason:

> *"Does the shared vocabulary gain a destination-eligible reporting_period key, or do operational
> periods remain group labels with record_type-only branches?"*

One concept, two spellings, proposed independently by two families that contest the same workbook,
is precisely the bug D6 exists to prevent and CONNECTION §6 exists to police. **R1c must adjudicate
`fiscal_period` and `reporting_period` as one question**, and whichever spelling survives must be
used by both families. Filed as **NJ-BF-2**.

**No other field is proposed.** `organization` is the schema row's and `construction_property`'s
joint proposal and is adjudicated there; restating it here would create the same two-proposals
problem this row is complaining about.

## `role_split` — deliberately empty, with a reason

The obvious candidate is *budget holder* versus *finance function*, and it is rejected: `role_split`
requires **field keys** on both sides pointing at a roster neighbour, and neither role has a
canonical key — nor should one be minted, since both are roles **inside** one organisation rather
than the two-party split `00`'s consulting sentence describes. The schema anchor's NJ-BO-5
(buying-side role) is the live version of this question and it is not this row's to answer.

---

## Sparse-file discipline

Four of the ten fixtures carry `group_without_copying_facts`. This row needs the rule badly because
its sparse members are the *normal* case: a workbook named only `v7 FINAL (2)`, an unlabelled tab
of numbers, an attachment stripped from its instruction email, a whiteboard photo of a quarterly
plan. In each, the neighbourhood may legitimately group the file while **no** unit, period or
function fact is written onto it — *"The graph does not automatically copy those missing facts onto
sparse files."* And the download-session rule bites here more than most: budget packs are commonly
pulled from a planning system in one action, and *"A session should never be treated as proof of
topic"*.

Every fixture also carries `"any business_operations fact - the schema declares none"` in
`must_not_conclude`, so the placeholder status is checkable file-by-file.

---

## Salvage and deepening — what was preserved, what was added

**Preserved unchanged** (verified correct, not rewritten):

- the 27-key key set, in the landed sibling order;
- every quotation already in the JSON, re-verified verbatim against `00`;
- `fields: []`, `dimension_order: []`, `time_first: false`, no threshold, no statistic, no P7
  handling class, `refuse_node: false`;
- the eight `deterministic`, seven `needs_llm` and nine `never_alone` entries; the
  `proposed_context_terms`; the 14 `work_types`; the six `grouping_reasons`; all ten `file_examples`
  with their observation/fact splits; the five `falls_through_to` residuals; `file_kinds`;
  `sensitivity` and `sensitivity_why`;
- the six existing `collides_with` entries, including `finance.small-business-bookkeeping` as the
  load-bearing one and `finance.personal-records` for the household case;
- the gist draft's three central positions, all of which survived the deeper test: that the anchor
  is a **planning round for a unit and a period**; that the **absence** of an institution header is
  as discriminating as the presence of a variance column; and that the **sole-trader case is a real
  failure that must be admitted rather than papered over**. None was reversed.

**Added to the JSON — five surgical edits, nothing rewritten:**

1. `one_line` — the retired `Gist-level placeholder (J-IND)` label replaced with *"A PLACEHOLDER
   TEMPLATE ROW written to J-DEPTH"*. Substance unchanged.
2. `recognition.never_alone` — a tenth entry: a **filename version or finality token alone** is not
   proof of a version family, carrying *"A content-hash match supports deduplication review; a
   filename match alone does not."* and the universal-facts sentence. This is the row's answer to
   the budget-versus-forecast question expressed as a detection rule.
3. `collides_with` — a **`finance`** (schema) entry added at the head, reciprocating the landed
   `"budget sheet"` work type explicitly, conceding protective ordering, and naming the fold
   outcome if R1c reads that work type as a claim on the situation.
4. `also_holds_with` — was empty; now carries **`finance.small-business-bookkeeping`** for the
   workbook holding a forecast sheet and a reconciled-actuals sheet, licensed by CONNECTION
   invariant 1 (the collision entry names discriminating evidence) and following the both-edges
   pattern `finance.research.md` already uses for `photos` and `legal`.
5. `proposed_fields` — was empty; now carries **`fiscal_period` as an explicit seconding** of the
   schema row's proposal, whose sole new content is the `reporting_period` spelling conflict with
   the landed bookkeeping row.
6. `open_question` — extended from two items to four, adding NJ-BF-1 (budget/forecast as one
   situation) and NJ-BF-2 (the two spellings).

**Added in this memo** (the deepening proper): the sources section with what each quoted span
decided; the schema anchor's three binding statements answered explicitly; the never-alone principle
applied literally as a structure/slot table; the node test argued leg by leg with **leg 2 explicitly
not claimed**; the full budget-versus-forecast argument from the universal-facts sentence; the
household/sole-trader argument and its admitted failure; a thirteen-row rejected-files table; the
collision fixture in **both** directions with the same bytes named on both sides; ten reciprocal
boundaries; the `finance` `"budget sheet"` problem stated plainly with the fold outcome named; six
neighbours refused an edge with reasons; the `role_split`-is-empty argument; sparse-file discipline;
and this audit trail.

**Where this row is thinner than a launch row, and why:** it absorbs **one** legacy id, it declares
no fields, and it cannot claim the dimensions leg. It has genuinely less to say about field
semantics than `finance.cap-table-equity` does, and it has not been padded to close that gap.

---

## Audits run before returning

- `python3 -m json.tool planning/domains/nodes/business_operations.budget-forecast.json` → parses.
- Key set unchanged and still identical to the landed siblings, in the same order.
- Every quotation newly introduced into the JSON or this memo grep-verified verbatim against
  `00-database-agent-product-design.md` (`grep -cF` = 1 for each). The `reporting_period` quotation
  grep-verified against `finance.small-business-bookkeeping.json`; the `finance` `"budget sheet"`
  work type read directly from `finance.json`; `strategy-plan`'s reciprocal edge quoted from its own
  JSON.
- `fields: []` holds. No canonical key minted — the single `proposed_fields` entry reuses the schema
  row's key and carries `adjudicate: "R1c"`.
- No numeric threshold, statistic or invented file count. The counts stated (one absorbed legacy id;
  ten fixtures; 24 siblings) are read from `ROSTER.md` Appendix A and from the files themselves.
- Every `collides_with` and `also_holds_with` target is a real roster id; every `falls_through_to` is
  one of `00`'s residual names; every `file_examples.source_type` is in P5's fourteen.
- **Files written: exactly two** — `planning/domains/nodes/business_operations.budget-forecast.json`
  and this memo. Nothing else touched.

---

## NEEDS-JOSEPH

- **NJ-J-IND-3 (carried from the schema row; this is the row it breaks).** Where does an
  *organisation's* money live? The statutory/custodial-versus-management split is defensible but was
  drawn by the roster pass, not by `00`. Alternatives and costs: **(a) keep the split** — this row
  stands, but one workbook routinely holds both sides and the seam runs *inside* a file;
  **(b) all organisational money to `finance`** — clean and protective, removes this row, but puts
  forward-looking artifacts under a schema whose four fields (`institution`, `account_type`,
  `tax_year`, `record_type`) cannot describe them; **(c) all organisational money here** — strips
  safety protection from ledgers and returns, the wrong direction on a safety question. *This row's
  recommendation, offered and not taken: (a), with the seam restated as evidence-based (institution
  header present or absent) rather than topic-based.* Sharpened here by the `"budget sheet"` finding
  below.
- **NJ-BF-1 (new) · Is a budget and a forecast one situation or two?** This row says one, treating
  the revision sequence as the universal `version_family` fact. Alternatives: **(a) one row**
  (chosen) — cost is that a fixed approved budget and a working reforecast carry different
  organisational authority and one situation cannot express that; **(b) two rows** — cost is a node
  minted out of a universal fact the product already computes, which is the 574's error; **(c) one
  row plus a first-class authority value on `work_type`** — cheapest fix if (a)'s cost ever bites,
  and it needs no new node.
- **NJ-BF-2 (new) · One concept under two names: `fiscal_period` versus `reporting_period`.** The
  `business_operations` schema row proposes the first; the landed `finance.small-business-bookkeeping`
  row raises the second in its `open_question`, for the same concept, after rejecting `tax_year` for
  the same reason. Two families that contest the same workbook must not carry two spellings. R1c
  must settle it once; this row expresses no preference between the two names, only that there be
  one.
- **NJ-BF-3 (new; renumbered from the gist draft's NJ-BO-5, which the deepened schema anchor has
  since reassigned to the buying-side role key) · The sole-trader case.** For a one-person business
  the household budget and the unit budget are one file, with one row set and no approver because
  there is nobody to approve to. The structure/slot discriminator this row relies on genuinely fails
  there. Alternatives: **(a) abstain** (current posture) — honest, and the file lands in Review
  Later; **(b) let `finance.personal-records` take it by default** — protective and probably right
  more often, but it silently files a business record as a personal one; **(c) ask the user once,
  per corpus, whether they run a business** — the only reading that actually resolves it, and it is
  a product decision, not a catalogue one.
- **NJ-BF-4 (new) · `finance` already claims `"budget sheet"` as a work type.** A landed safety
  schema carries budget-shaped material in its own `work_types` list. This row reads that as a value
  bounded by `finance`'s own evidence and has written the edge accordingly, but the reading is this
  row's inference. If R1c reads it as a claim on the situation, **this row should fold into
  `finance`** and its coverage routes there — named here rather than defended against.
- **NJ-BO-4 (carried) · The reciprocals are missing.** No landed row except the sibling
  `strategy-plan` names this one. Nine of the ten boundaries in this memo are one-way.
