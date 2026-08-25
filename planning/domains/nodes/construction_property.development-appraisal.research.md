# `construction_property.development-appraisal` — lab notes (template row, deepened to J-DEPTH)

Depth: J-DEPTH (replacing the retired `Depth: GIST` header of the first pass).

Row kind: **template**. Schema: `construction_property`. Launch: **placeholder** (`fields: []`).
Absorbs the legacy row `prop.development-appraisal` (ROSTER.md Appendix A).
Verdict: **kept, not refused** — on one strong leg, one honest leg, and one leg that fails and is
said to fail.

**Status of this pass.** The row was written once under the retired `Depth: GIST` label. That draft
was verified-but-shallow: its JSON key set was house-correct, its quotations were machine-verified,
its `recognition` block was already unusually well argued, and its central insight — *the money is
not the signal; the backwards arithmetic is* — is correct and is preserved verbatim in substance.
What it lacked was the node test argued leg by leg, the files-considered-and-rejected section, a
two-way collision fixture, and the reciprocal `finance` seam. This pass **deepened rather than
rewrote.** Nothing that was already right was changed for the sake of change; see *What was
preserved, what was added* at the end. **One thing the gist draft asserted is qualified here** — its
claim that the row's dimension recommendation "differs from the schema default" is weaker than it
looked, and leg 2 now says so rather than banking it.

---

## Sources actually used

### Binding local sources

- `planning/00-database-agent-product-design.md` — the only document quoted, and every quotation in
  this memo and in the JSON was grep-verified back out of it verbatim with `grep -c -F` (see
  **Audits**). The spans that did the work on this row:
  - the abstention sentence, which this row needs more than most of its siblings because its
    material is money and money is never-alone here: *"Correct abstention is a successful outcome
    because the product’s goal is reliable organization, not maximum file movement."*
  - the table sentence, which licenses reading the residual block and the accommodation schedule out
    of cells at all: *"Tables matter because resumes, forms, applications, invoices, and
    administrative documents often place their most useful information in cells rather than body
    paragraphs."*
  - the dedup sentence, which cuts **both ways** on the sensitivity set and is this row's hardest
    real problem: *"A content-hash match supports deduplication review; a filename match alone does
    not."*
  - the multi-role-token warning, the family's constitutional sentence, read across from a
    university name to a **site address** and to a **developer's name**: *"A university name alone
    should not create a group because Columbia can appear as an authoring school, course provider,
    target institution, employer, research venue, or merely a cited organization."*
  - the dimension-order rule: *"For document and record domains, project, function, or subject
    usually comes before time because putting year first scatters related work across calendar
    folders."*
  - the recommendation sentence, which keeps the prose order below a recommendation:
    *"The system recommends an order based on the domain template, but the user can reverse, remove,
    add, or flatten dimensions."*
  - the purpose-coherence sentence, which is what holds a bid pack together across incoherent
    content: *"The documents are content-incoherent but purpose-coherent."*
  - the sparse-file rule, needed here because half this row's real files are an untitled `Cashflow.xlsx`
    in a folder named after a site: *"The graph does not automatically copy those missing facts onto
    sparse files."*
  - the finance field sentence, which is the whole of the `finance` seam's evidence base:
    *"Finance files may use institution, account type, tax year, and record type"*.
  - the safety sentence, which decides who wins when the seam is unsettled: *"Finance, identity,
    medical, and legal material should be implemented first as safety domains"*.
  - the privacy-enforcement sentence, quoted as the precondition on every detection entry:
    *"Privacy policy must be enforced before content reaches any model or external connector."*
  - the residual-library definitions, for all five `falls_through_to` entries.
- `planning/domains/_CONTRACT.md` — rules 1–3 (provenance, no fabricated quotes, **no invented
  numbers**, which is why no percentage, hurdle rate or cost-per-area figure appears anywhere here),
  8 (a dimension may only branch on a declared field), 10 (no field rows on a placeholder schema),
  11–15 (`kind`, closed edge vocabulary).
- `planning/domains/CONNECTION.md` — §2 node test (applied leg by leg below), §4 activation
  (step 2 never-alone, step 5 protective ordering), §5 closed edge vocabulary (`collides_with` is
  same-kind; a template may not author `also_holds_with`), §6 field identity, PR-1, PR-6.
- `planning/prompts/ALIGNMENT.md` — *"would only repeat its schema’s fields and dimension_order"* …
  *"it is the schema’s default template."*
- `planning/domains/canonical_fields.json` — confirmed `project`, `work_type`, `client`, `our_firm`,
  `location`, `institution` exist with the roles relied on here, and that **nothing holds a
  property**. **No key minted, no variant proposed.**
- `planning/overnight/council/DECISION-BRIEF.md` — D1 (as narrowed), D6, PR-6, J-IND taken as
  ratified. J-DEPTH (2026-08-24) overrules J-IND's gist clause; this memo is written to the
  launch-row standard.

### The schema anchor, read first and applied explicitly

`construction_property.research.md` (J-DEPTH) states the default template this row must differ from:

> **`property` or site → `instruction` (the job, the letting, the scheme, the block) → document
> function**, with a period level only where the situation *genuinely cycles*. **Not time-first.**

It also hands every sibling three rules this row applies literally:

1. **The constitutional never-alone.** A postal address alone, and a firm or practice name alone,
   are never evidence on this schema — the university-name sentence read across. This row adds a
   third of its own: **a money figure alone**, because this row's entire content is money.
2. **Values are not rows.** *"`variation`, `snagging`, `dilapidations`, `retention`, `preliminaries`,
   `certificate`, `drawing`, `schedule`, `survey`, `valuation` and `report` are **values of
   `work_type`**, not rows."* Read across to this row: **`appraisal`, `cost plan`, `cashflow`,
   `sensitivity`, `viability` and `funding pack` are values too.** A row that justified itself by
   listing those document types would have claimed nothing. This row does not.
3. **A shared table shape is not a situation** — the lesson of the family's `timesheet` refusal, and
   the exact charge this row has to answer, below.

### Landed neighbours read before writing, and not touched

- `finance.research.md` + `finance.json` — the landed **safety** schema, four fields, the seam this
  dispatch calls load-bearing. Read in full for its default template (`institution → account_type →
  record_type`, `time_first: false`) and its `work_types` list.
- `finance.small-business-bookkeeping.research.md` — landed, full depth, the row that owns the
  **working book**. Its node-test section ("Detection differs… the rich anchor is a holder-maintained
  working system") is the model for how this row states its own difference from a schema default.
- `finance.cap-table-equity.research.md` — landed. Its anchor is an **ownership stake**, a durable
  claim; a funding assumption inside a model is not one.
- `finance.loans-mortgage.research.md` — landed; **serviced** debt with principal, interest and
  payoff slots. This row holds the **request**.
- `finance.household-property.research.md` — landed; the householder's own record of their own home,
  and the source of the family's professional-versus-householder seam.
- `business_operations.budget-forecast.research.md` (deepened to J-DEPTH) — the row this one collides
  with hardest, and the row that authored **NJ-J-IND-3**. Read in full before writing; its
  `finance` boundary table and its *"budget sheet"* finding are accepted here rather than
  re-argued, and this row extends them rather than contradicting them.
- `business_operations.it-asset-inventory.research.md` — read for the **spreadsheet-shape charge**
  and how it was answered. Method borrowed, argument not copied.
- `construction_property.construction-project.research.md` (J-DEPTH, the family spine) — it already
  names this row and states the boundary from its side. This row does not diverge from it by one
  word; the shared reading is reproduced below.
- `construction_property.survey-valuation.research.md` and `construction_property.site-survey.research.md`
  — the *measuring the land vs pricing the asset* argument, applied here as a **third** term.

---

## What this row is, in one paragraph

An appraisal is the **financial case for a scheme that does not exist yet**, made on a site that
does. Its characteristic artifact runs arithmetic *backwards*: take an end value the scheme would
have if built, subtract build cost, professional fees, contingency, finance cost and the return the
developer requires, and whatever remains is what the land is worth. Around that sit a schedule of
accommodation (the unit mix that generates the end value), a period cashflow whose point is the
**peak funding requirement**, sensitivity runs that re-state the whole model against varied
assumptions, and the packs built from all of it — a bid, a viability submission, a funding request.
The anchor is **a scheme on a site, and a set of assumptions that have not happened.**

---

## The hostile reading, stated first

The dispatch is right to press it, and it is stronger here than it was against `it-asset-inventory`.
Stated at full strength:

> *An appraisal is a spreadsheet of numbers about a building. Its two most obvious candidate signals
> are a **company or developer name** and a **spreadsheet of costed lines** — and both are
> individually never-alone: the first by the schema's constitutional rule, the second because
> `business_operations.budget-forecast`, `finance.small-business-bookkeeping` and every other row on
> the roster that touches money produce the same cells. If that is the whole of the row's support,
> it is a row that never fires, and refusing is correct.*

Add the sharper version the family's own `timesheet` refusal supplies: **a shared table shape is not
a situation.** A costed spreadsheet is a table shape. If this row's claim is "a table of money about
a building", it should refuse for exactly the reason `timesheet` did.

**The answer is not that the charge is wrong. It is that the charge describes the *contents* of the
cells and the row is claimed on the *direction of the arithmetic between them*.** The anchor's rule
does not forbid a structure that resembles another; it forbids an **unpaired** one — a structure with
no labelled slot, or a slot with no structure. This row can name that pair, and the pair is not
"money in cells":

- the **structure** is a value-less-costs-less-required-profit chain that **solves for an input**
  (the land price) rather than totalling to an output;
- the **slot** is a residual or land-value line that the chain terminates in, sitting beside a
  scheme description and an accommodation schedule.

A budget totals to a total. A ledger reconciles to a balance. **An appraisal solves for what you can
afford to pay.** That is a different computation, not a different vocabulary — and vocabulary is
what this family is explicitly *not* detected by.

Whether that is enough is leg 1, next. **Two of the three legs pass and one does not**, and saying
which is which is the point of running the test rather than announcing a verdict.

---

## The node test, all three legs, argued

CONNECTION §2: *"A **template** row exists only if its detection signals, recommended dimensions, or
privacy rules differ from its schema's default template."* The legs are disjunctive; one is enough.
Each is argued separately anyway.

### Leg 1 — detection signals. **Passes, and it is the only leg that carries the row.**

Four structures, each a structure paired with a slot, none of them the schema's default template
(title block / measured-works table / `to date, less previously certified` / apportionment schedule),
and none of them a topic word.

1. **The residual chain.** A labelled block running gross development value → build cost →
   professional fees → contingency → finance cost → required profit → **a residual land or site
   value**. The discriminating property is the **direction**: the terminal line is an *input to the
   transaction*, not a total of the rows above it. Nothing else in the catalogue computes in that
   direction — a bill of quantities totals upward, an interim valuation subtracts what was already
   certified from a cumulative claim, a budget compares plan to actual, a ledger reconciles. This is
   marked **inference** (`00` never names this world), and it is exactly the kind of claim R2 could
   turn into a real structural rule. Note what is **not** the signal: the words "residual" or "GDV"
   in a filename, which are context terms and appear in every textbook on the subject.
2. **The schedule of accommodation.** Rows that are **unit types within one scheme**, columns that
   are count, area and value or rent, totalling into the value line of (1). Structurally this is a
   *composition of a thing that does not exist*, and it is unlike the two nearest tables in the
   catalogue: a measured-works table's rows are **works already specified to be done**, and an
   apportionment schedule's rows are **leaseholders in a building that stands**. The tell is that
   the units have areas and values but no occupiers and no addresses of their own.
3. **The peak-funding cashflow.** A period column series over cost and revenue rows carrying a
   **cumulative funding requirement line with a maximum**. The period columns are *not* the signal —
   `budget-forecast` has those, and the JSON's `never_alone` says so outright. The signal is the
   cumulative-and-peaking line, which exists because the question being asked is *how much facility
   do I need to arrange*, a question an operating budget never asks.
4. **The sensitivity set as a structure.** Not one file: **a set of near-identical artifacts that
   differ in a small number of assumption cells and share an accommodation schedule.** This is a
   detection signal at the *group* level rather than the file level, which is unusual on this
   schema, and it is also this row's hardest problem (below).

The **viability submission** and the **funding pack** are deliberately *not* listed as a fifth
structure. They are (1)–(3) wrapped in an addressee and a covering narrative, and claiming them
separately would be claiming a document type.

**Verdict on leg 1: passes**, and it passes on structure rather than on subject matter. It would
fail if stripped to "a costed spreadsheet about a building", and the JSON's `never_alone` list
strips it that way deliberately so the failure mode is written down.

### Leg 2 — recommended dimensions. **Does not pass on its own, and the gist draft overclaimed here.**

The gist draft said the second level being the **exercise** (acquisition / viability / funding /
review) rather than the document function was a difference from the schema default. On a careful
reading of the anchor, that is **weaker than it claimed**, and this pass says so rather than banking
it. The anchor's default is *`property` → `instruction` → document function*. An "exercise" is, on
any fair reading, **an instruction**: an acquisition, a viability submission and a funding round each
have a start, a purpose and an end. So the recommendation here is the schema default with its middle
level given a domain-specific name — and the anchor is explicit that **renaming or reversing levels
earns nothing**: *"Reversing is not a difference that earns a node"*

What *is* genuinely worth recording, and is recorded as prose in `template.why` rather than sold as a
passing leg:

- **Explicitly NOT a level per appraisal version.** The sensitivity set would scatter across ten
  sibling folders that differ by one cell. This is the same argument the family's drawings-revisions
  row makes about revisions, and it is a *constraint on* the default order rather than a departure
  from it.
- **Site-first is unusually well supported here**, because a developer's mental model is site-first
  and because the papers of a scheme that was never built have to survive years of dormancy — but
  the anchor already recommends site-first, so agreeing with it is not a difference.
- **Not time-first**, on `00`'s rule; and whatever lands stays a recommendation.

**Verdict on leg 2: fails.** The row does not need it, and pretending otherwise would have made the
whole test unfalsifiable. Recording the failure is the honest reading of the anchor's own warning.

### Leg 3 — privacy rules. **Passes, on a ground no sibling on this schema has.**

The schema's default privacy posture is stated at the anchor: the material **names a real person's
home and who is in it**, the exposed party is usually not the user, and an address is *locating*
rather than merely identifying. This row's posture is different in **kind**, not in degree:

- **Its confidential content is a negotiating position, not an identity.** An appraisal states what
  a party will pay for a site, what margin they require, and the point at which they walk away.
  Disclosure to the counterparty does not embarrass the holder; **it destroys the position the file
  describes.** That is a distinct harm model from the family's default, and it is why these files
  carry explicit confidentiality legends far more often than a survey or a drawing does.
- **The party at risk is frequently a third party who cannot consent** — a funder, a landowner, a
  joint-venture partner whose own numbers are in the model. The anchor names third-party confidence
  as a schema-level concern; here the third party's *commercial* interest, not their personal data,
  is what is exposed.
- **And the personal-data ground is comparatively thin, which is stated rather than inflated.** The
  one real instance is the comparables schedule, which lists **other people's transacted homes by
  address** — a table in which every row is an address and none of them is the subject.

The combination — high commercial exposure, third-party, thin personal data — is not the schema
default and argues for the cautious setting. `sensitivity: potentially_sensitive`; the handling class
is P7's and is not set here.

**Verdict on leg 3: passes**, independently of leg 1.

**Overall: kept**, on leg 1 and leg 3, with leg 2 recorded as failing.

---

## The `finance` seam, in both directions — this row's load-bearing boundary

The dispatch is right that this is the seam. An appraisal **is** a financial model: cashflows,
residual value, IRR — and the roster's triage **deliberately folded corporate accounting onto
`finance`**, which is also a landed **safety** schema. Four separate lines have to be drawn, and each
was drawn after reading the neighbour's own file.

**The general principle this row asserts, stated once:** `finance`'s four fields are `00`'s own —
*"Finance files may use institution, account type, tax year, and record type"* — and **not one of
them can describe an appraisal.** There is no institution (a lender may be an addressee, but the
model exists before any lender does); no account (nothing has been transacted); no tax year (the
scope is a scheme's programme); and `record_type` would have to carry the whole situation alone.
That is not an argument that `finance` is wrong about money — it is the observation that a **forward
model of an asset that does not exist yet** is not describable in an account-records language. This
row therefore claims it **on the subject** (a scheme on a site), not on the money.

**The reciprocal, which matters more:** the moment any of those four slots is genuinely present —
an institution-and-account header, a statutory issuer, a tax year, a personal holder — the file is
`finance`'s, and where the evidence is unsettled **`finance` wins anyway**, because *"Finance,
identity, medical, and legal material should be implemented first as safety domains"* and
CONNECTION §4 step 5 orders protection first. This row does not ask for an exception.

| `finance` neighbour | This row must **not** take | The neighbour must **not** take | Shared fixture bytes |
|---|---|---|---|
| **`finance`** (landed schema, SAFETY) | anything carrying an institution-and-account header, a statutory issuer, a tax year or a personal holder — and, where the evidence is unsettled, the file at all | a **priced scheme that has not been built**, merely because the file is money in a spreadsheet and the schema's `work_types` list contains *"budget sheet"* | `Kilnfield appraisal v11.xlsx` |
| **`finance.small-business-bookkeeping`** (landed) | journals, ledgers, trial balances, invoices, reconciliations, AR/AP — the developer's **actual book**, which has transactions where this row has assumptions | the **model above the book**: a residual appraisal, a scheme cashflow, a sensitivity run | a developer's workbook holding an appraisal tab **and** a reconciled-actuals tab — disjoint evidence, one item never counting twice |
| **`finance.loans-mortgage`** (landed) | a **serviced** facility: principal, interest, drawdown, statement, payoff, security release — debt that exists and is being repaid | a **request** for a facility built from an appraisal, merely because a lender is named and a figure is stated | `Funding pack - Harbour Works.pdf` |
| **`finance.cap-table-equity`** (landed) | a share register, an option ledger, a waterfall, a JV or partnership **instrument** — its anchor is a durable ownership claim | a **scheme model containing an equity assumption** — a promote or a JV split modelled in a cashflow is an assumption, not an instrument | a scheme model whose returns tab splits profit between partners: the split assumption is this row's, the deed that governs it is that row's and `legal.leases-agreements`' |

**Where this row extends `budget-forecast`'s finding rather than contradicting it.** That row settled
the *"budget sheet"* problem by reading a work type as a **value, not a node**: what `finance` owns
through it is a budget sheet arriving **with finance's own evidence**. This row adopts that reading
unchanged and adds one construction-side datum: *the file that most looks like a finance budget sheet
in a developer's folder — `Cashflow.xlsx` — is the one this row also cannot claim*, because bare
period columns support neither. Both rows abstain on the same bytes, which is the correct outcome:
*"Correct abstention is a successful outcome because the product’s goal is reliable organization, not
maximum file movement."*

**NJ-J-IND-3 reaches this family here.** `budget-forecast` states the fork (statutory/custodial money
to `finance`, forward-looking management money to `business_operations`) and recommends option (a).
This row asserts a **third leg of the same fork**: forward-looking money **about a scheme on a site**
goes to the property family, on the subject rather than on the money. That is an extension of the
fork, not a contradiction of it, and it is filed below with its alternatives and their costs.

---

## Files considered and rejected

The tempting false positives, and what discriminates each. A row that only lists what it holds has
not been researched.

| File | Why it is **not** this row's evidence |
|---|---|
| `Cashflow.xlsx` — period columns over cost and revenue rows, no scheme name anywhere *(kept in the JSON as a fixture, and it is the **inbound collision fixture**)* | See below. Period columns and money are never-alone on **both** sides; **neither this row nor `budget-forecast` fires.** |
| `Comparables - Q1 2026.xlsx` *(kept as a fixture)* | Rows of **other people's** transacted properties. Every row is an address and **none of them is the subject**. It is input evidence, not a scheme record; it groups with a bid by purpose without any property fact being written onto it. |
| `Development appraisal - a practical guide.pdf` *(kept as a fixture)* | A published guide whose worked examples contain **every context term this row lists** and a full residual chain with invented figures. Discriminator: no site, no scheme, no holder involvement. Reading Inbox. This is the single clearest demonstration that context terms are not evidence. |
| An estate agent's **market appraisal** of a house | The word "appraisal" collides outright and means something else: a suggested asking price for a standing property. `construction_property.agency-listing` already claims it and `survey-valuation` already names it as a rejected fixture — this row does not reopen either. |
| An **investment valuation** of a standing income-producing building | Shares the entire yield and capitalisation vocabulary. Discriminator: it prices **an asset that exists and produces income**, from evidence of what it does produce; this row prices **a scheme that does not exist**, from assumptions about what it would. This is the same distinction the family already drew between `site-survey` and `survey-valuation` — *measuring the land vs pricing the asset* — and this row is the **third term**: **pricing a scheme that is not there.** `survey-valuation`'s. Retained in `needs_llm` as a genuinely hard case rather than claimed. |
| A **land registry title, searches pack or contract report** for the same site, sitting in the same acquisition folder | Title apparatus — register entries, plan references, covenant schedules. `construction_property.sale-purchase`'s. Real and adjacent; **no shared discriminating evidence item**, because a residual chain never appears in a title. |
| A **JV or partnership agreement** behind a scheme | An executed instrument with recitals, covenants and an execution block. `legal.leases-agreements`, and legal is a safety domain that protects first. The model's *assumption* about the split is this row's; the deed is not. |
| A **bill of quantities** or a **priced tender return** | Measured quantities against specified works, priced by a contractor to win a job. That is the schema default's measured-works table and it belongs to the tendering/subcontract situations. A **cost plan** is kept here instead, and only because it is elemental rates against a **described** scheme at a stated design stage — there are no measured works to price, which is precisely the discriminator. This is the narrowest call in the memo. |
| An **interim valuation** on a live site | The `to date, less previously certified` shape — the schema default's third structure. `construction-project`'s, and the boundary is tense: executed and certified, not forecast. |
| A **CIS return, a payroll run, or a developer's VAT return** | `finance` and `hr`. Real files in a developer's folder; not evidence of this situation. The family's `timesheet` refusal used exactly this reasoning and the two must stay consistent. |
| A **planning decision notice** for the same scheme | `government`'s applicant-side row and the family's own building-control row. A viability submission is genuinely **both** — it is an appraisal *and* a submission — on disjoint evidence, which is why there is no collision edge and no `also_schema` claim on it beyond what the fixture already carries. |
| A **rendered exterior view** or a marketing render used inside a funding pack | `creative.architectural-visualisation`. The pack is this row's; the image is not, and the appraisal table is what discriminates the pack from a brochure. |
| An **architecture or development-finance textbook chapter**, a market report, an RICS-style guidance note | Reading Inbox — *"papers, articles, reports, and saved PDFs that appear to be reading material but have no active research, course, or project association."* Full vocabulary overlap, zero evidence overlap. |
| `Household budget 2026.xlsx` belonging to a homeowner planning an extension | See the outbound collision fixture below. |

---

## The collision fixture, in both directions

### The file that would wrongly fire this row

**`Cashflow.xlsx`** — a period column series over cost and revenue rows, a cumulative line, no scheme
name, no site address, no accommodation schedule, sitting in a folder named after a site.

Everything about its neighbourhood argues for this row, and **the neighbourhood is exactly what may
not be used**: parent-folder context is a clue that never fires alone, and *"The graph does not
automatically copy those missing facts onto sparse files."* What is actually present — period
columns and money — is never-alone on this row's own list *and* on `budget-forecast`'s. Whether the
cumulative line peaks (this row) or runs to a period total (a budget) is a real discriminator, but it
is a **cell-level reading of an unlabelled sheet**, and this row does not claim it can be made
reliably at detection time.

**Resolution: neither row fires.** The file groups with the scheme by neighbourhood if the group is
otherwise established, carrying `group_without_copying_facts: true`, and falls to **Review Later** —
*"Review Later may hold files whose meaning is partly understood but whose final location requires a
future decision."* Both sides abstain on the same bytes and both say so.

### The file that must not be lost *to* this row

**`Household budget 2026.xlsx`** — a homeowner's spreadsheet planning a loft extension: build cost
lines, a contingency row, a finance cost row, a total, and a quote from a builder pasted in.

It is genuinely tempting: build costs, contingency, finance, a property. It even has three of the
four words this row's context list contains. **It is a householder's own record of their own home**,
which the landed `finance.household-property` row claims, and `business_operations.budget-forecast`
already names these same bytes as the file on which *it* must abstain.

**What discriminates it:** no residual chain (it totals what the work will cost; it does not solve
for what the site is worth), no accommodation schedule (there are no units to sell or let), no
instruction, and the holder is the owner-occupier rather than an instructed party. The family's
professional-versus-householder seam settles it, and this row does not diverge from the anchor's
version of that seam by one word.

### The same bytes, named on both sides

- `Cashflow.xlsx` — named here and readable against `business_operations.budget-forecast`'s own
  period-column argument; **both abstain**.
- `Household budget 2026.xlsx` — named here, and named by `budget-forecast` as its own abstention,
  and owned by `finance.household-property`. **Three rows, one file, one owner.**
- `Kilnfield appraisal v11.xlsx` — named here and offered to `finance` as the file the *"budget
  sheet"* work type must **not** reach for.

---

## Reciprocal boundaries, both directions

| Neighbour | This row must **not** take | The neighbour must **not** take | Shared fixture bytes |
|---|---|---|---|
| **`construction_property.construction-project`** (J-DEPTH, **states its side already**) | works actually executed and certified, from measured quantities — the whole `to date, less previously certified` world | a forecast of a scheme that may never be built, from rates per unit area | a site address and a build-cost figure, **which count for neither** |
| **`business_operations.budget-forecast`** (J-DEPTH) | an organisation's own cost lines by department over a fiscal period, with an approver and a variance-against-actuals column set | a **scheme on a site** with an accommodation schedule and a residual chain | `Cashflow.xlsx`; `Household budget 2026.xlsx` |
| **`construction_property.survey-valuation`** | a **reliance-bearing opinion** on a standing asset: an addressee, a purpose, a basis of valuation, a liability limitation | a **speculative model of a scheme that does not exist**, merely because both use yields | a residual valuation prepared *as* a reliance-bearing report — genuinely both, and the reliance furniture decides which reading leads |
| **`construction_property.agency-listing`** | particulars, a price line, photographs, a portal presentation of a property for a market | an **appraisal computed from assumptions** merely because a site is being sold and the two arrive in one pack | a site sales pack containing both a brochure and an appraisal |
| **`construction_property.sale-purchase`** | title apparatus: register entries, plan references, covenant schedules, the contract report | the **price justification** behind the bid | an acquisition folder holding a title pack and an appraisal — adjacent, sharing **no** evidence item |
| **`finance` and its three landed rows** | — see the finance seam table above — | | |
| **`legal.leases-agreements`** (landed, SAFETY) | the operative instrument: recitals, covenants, consideration, execution block | a **modelled assumption** about a JV split or a ground rent, merely because a deed governs it | a JV deed beside the model that assumes its terms |
| **`business_operations.strategy-plan`** (landed) | a multi-year argument comparing options, with goals, initiatives and horizons and no scheme | a **scheme-specific appraisal** merely because a business case is a financial model with a narrative round it | an investment paper recommending a site acquisition |

**A finding, stated plainly:** of the eight neighbours above, **only `construction_property.construction-project`
names this row back.** `budget-forecast`, the three `finance` rows, `legal.leases-agreements` and
`strategy-plan` were all written before this row was deepened and carry no return edge. Seven of the
eight boundaries are therefore **authored one-way from this side**, and **R1c owes the reciprocals**.
The fixture bytes are named here precisely so the reciprocal can be *checked* rather than asserted.
This is a catalogue defect, not a judgement about the seams.

---

## Neighbours considered that did **not** get an edge, and why

- **`finance.investment-brokerage`** — an IRR and a return metric appear in both. No edge: its anchor
  is a **statement of holdings at an institution**, and an institution-and-account header is
  `finance`'s constitutionally. A return percentage is on this row's never-alone list for the same
  reason. Topical adjacency, no contested evidence item.
- **`government.planning-application`** — a viability submission carries an application reference and
  goes to an authority. **No edge, and the omission is deliberate:** the two readings are genuinely
  simultaneous on **disjoint** evidence (a residual chain; an application reference and a decision
  apparatus), not mutually exclusive. A collision edge would assert a competition that does not
  exist. The family's building-control row already states the applicant-side boundary and this row
  does not duplicate it.
- **`business_operations.risk-register`** — a sensitivity run models things going wrong. No edge, and
  the reason is symmetric with the one `budget-forecast` gives: a downside scenario is a **number**,
  a risk register entry is a **governed record** with an owner and a review date.
- **`academic` / `research`** — development appraisal is a taught subject with a large literature.
  Full vocabulary overlap, zero evidence overlap; the guide fixture carries the lesson instead.
- **`code`** — appraisal software project files and model add-ins exist. A format is a routing signal,
  not a meaning, and no document is confusable.
- **`retail_hospitality`, `nonprofit`, `resource_operations`** — all three develop property. That
  makes them **values of `client`**, not neighbours; naming them would rebuild the industry forest.
- **`identity`** — a funding pack can carry a principal's identity documents for lender KYC. The
  relationship is **protection, not a shared reading**, handled through `sensitivity` and the
  Protected Records fallthrough rather than an edge — the same move the schema row makes.

---

## The hardest real case in this row: the sensitivity set

A developer keeps ten files that are **near-identical by content and different in meaning by one
assumption cell**. `00`'s duplicate machinery is correct about the bytes and unhelpful about the
intent, and its own sentence cuts **both** ways here: *"A content-hash match supports deduplication
review; a filename match alone does not."* The hashes differ, so they are not duplicates; the
filenames differ only by a suffix, so the filenames prove nothing; and the meaning that distinguishes
them lives in cells the product may not promise to read.

The gist draft recorded this and invented nothing. **This pass agrees and still invents nothing.** It
adds only the observation that the set is *also* a detection signal at group level (leg 1, signal 4),
which is a fact about the situation rather than a mechanism. Flagged for P9 as **NJ-DA-1**, with
alternatives stated below rather than smoothed.

---

## Sparse-file discipline

Four of the row's fixtures carry `group_without_copying_facts: true`, and this row needs the rule
badly: its **normal** file is an untitled workbook in a folder named after a site, or a `.zip`
data-room export that cannot be opened. In each, the neighbourhood may legitimately group the file
while **no** scheme, property or instruction fact is written onto it — *"The graph does not
automatically copy those missing facts onto sparse files."*

Every fixture also carries *"any construction_property fact — the schema declares none"* in its
`must_not_conclude`, so the placeholder status is checkable file-by-file and not only in the header.

---

## `proposed_fields` — two secondings and one explicit non-proposal

**No key is minted here.** The dispatch is right that this row must second the family's existing
proposals rather than mint variants, and it does — but with one substantive disagreement it states
openly rather than hiding.

- **`property` — seconded, unchanged, from `construction_property.json`.** This row is a clean
  supporting case: a site outlives every scheme ever appraised on it, and a developer returns to an
  abandoned site's papers years later when it comes round again. Nothing canonical holds it —
  `location` is the photos capture key, `institution` is a finance counterparty, `client` is a party
  not an asset. Adjudicate at **R1c (NJ-CP-1)**, as one decision for the family, not here.
- **`instruction` — NOT seconded, and this row argues the *other* side of the schema row's own
  alternative.** The anchor proposes `instruction` *with a live alternative that R1c should feel free
  to take: reuse the canonical `project`* — and **this row is the strongest single case for taking
  it.** A development scheme is a project by any ordinary reading: it has a name, a start, a
  programme, a budget and an end. Minting `instruction` for it would be shipping a near-duplicate of
  a canonical key, which is the exact defect D6 exists to kill, and `00` is explicit: *"The system may
  create new values when it sees a new course, project, company, university, or event, but it should
  not invent new fields automatically."* This is **not** a contradiction of the anchor — the anchor
  invited it — but it is a disagreement, and it is stated rather than silently omitted.
- **`organization` — NOT this row's proposal.** It is the landed `business_operations` proposal that
  `construction_property` already seconds, and R1c must settle it **once, there, for all three**.
  This row records only the datum that a development scheme routinely has three custodies at once
  (the developer, the funder, the professional advising) and that the same appraisal is a different
  record in each.

`proposed_context_terms` carries the practice vocabulary (`residual land value`, `gross development
value`, `peak debt`, `profit on cost`, `schedule of accommodation`, `sensitivity`, `viability`, …).
These are **proposals**, not `00`'s floor, and the guide fixture exists to prove that every one of
them can appear in a file that is not this row's.

---

## NEEDS-JOSEPH

- **NJ-J-IND-3, the construction face (extends `budget-forecast`'s item, does not contradict it).**
  Where does **forward-looking money about a scheme on a site** live? Alternatives and costs:
  **(a) here, on the property family, claimed on the subject** — *this row's assertion*; the cost is
  that it puts a financial model on a schema that declares no financial fields, and the seam runs
  through a workbook that also holds actuals. **(b) `finance`** — protective and clean, but `00`'s
  four finance fields cannot describe a scheme that has not been transacted, so the material would be
  held without a language to describe it. **(c) `business_operations.budget-forecast`** — coherent
  with the management/custodial split, but it loses the site, which is the one durable thing in the
  situation and the level a practitioner actually returns to. *Recommendation offered and not taken:
  (a), with the seam stated as evidence-based — residual chain and accommodation schedule present, or
  finance's four slots present — rather than topic-based.*
- **NJ-DA-1 (new) · The near-duplicate sensitivity set.** Files near-identical by content and
  distinct by meaning. Alternatives: **(a) treat the set as one version family** — cheap, and wrong,
  because the whole point of the set is that the members are *not* successive versions of one thing;
  **(b) treat each as an independent record** — honest but scatters an exercise across ten entries;
  **(c) a purpose-coherent group** — *"The documents are content-incoherent but purpose-coherent."*
  is the nearest licence `00` gives, but it is written for content-*in*coherent members and these are
  content-*too*-coherent, which is the inverse problem. **No mechanism invented. P9's call.**
- **NJ-DA-2 (new) · Is a cost plan this row's or `construction-project`'s?** The narrowest call in
  the memo. This row takes the **pre-contract** cost plan (elemental rates against a described scheme
  at a stated design stage, no measured works) and leaves everything post-contract to
  `construction-project`. The cost is that the design-stage marker is the only discriminator and it
  is a *label*, not a structure. Alternative: give all cost planning to `construction-project` and
  narrow this row to the appraisal and its packs — cheaper to detect, but it separates the cost
  assumption from the model that consumes it, which is the one thing an appraisal cannot lose.
- **Inherits NJ-CP-1 and NJ-CP-2**, and **argues the reuse side of NJ-CP-2** (see `proposed_fields`).
- **The seven one-way boundaries above.** R1c owes the reciprocals; the fixture bytes are named on
  this side so they can be checked.

---

## Audits run before returning

- `python3 -m json.tool planning/domains/nodes/construction_property.development-appraisal.json` →
  parses.
- **Key set compared programmatically** against the landed `business_operations.budget-forecast.json`
  and `construction_property.construction-project.json` — empty symmetric difference.
- **Every quotation in this memo grep-verified verbatim** against
  `planning/00-database-agent-product-design.md` with `grep -c -F`, each returning exactly one match.
  The quotations already in the JSON were machine-verified on the previous pass and were re-checked.
- **Every `file_examples.source_type` is in P5's `SOURCE_TYPES`**; the two fixtures added this pass
  use `spreadsheet`.
- **Every `falls_through_to` and `falls_through_if_inactive` is one of the nine residual names**,
  spelled `00`'s way.
- **Every `collides_with` target exists in `roster.json`** and every one is `kind: template`
  (CONNECTION §5: a template's collisions are same-kind).
- `fields: []`, `dimension_order: []`, `also_holds_with: []`, no canonical key minted, no threshold,
  statistic, percentage, rate or file count anywhere.
- **Files written: exactly two** — the JSON and this memo. No roster edit, no sibling row, no `src/`,
  no `check.py`.

---

## What was preserved, what was added

**Preserved unchanged** (verified this pass, not rewritten): the entire `recognition` block —
deterministic, `needs_llm`, and the eight-entry `never_alone` list whose opening move (disqualifying
money on a row made entirely of money) is the best thing in the original draft; `work_types`;
`grouping_reasons`; `proposed_context_terms`; `file_kinds`; `template.why` and its prose
recommendation; all five `falls_through_to` entries; `sensitivity` and `sensitivity_why`; and all ten
original `file_examples` with their `must_not_conclude` lists.

**Added this pass:** the node test argued leg by leg, with **leg 2 recorded as failing** where the
gist draft had claimed it; the hostile spreadsheet-shape reading stated at full strength and answered
on *direction of arithmetic* rather than on vocabulary; the four-line **`finance` seam table** in both
directions, extending `budget-forecast`'s *"budget sheet"* finding; the two-way **collision fixture**
(`Cashflow.xlsx` inbound, `Household budget 2026.xlsx` outbound) with both bytes named on both sides;
an eight-row **reciprocal boundary table** and the finding that seven of the eight are one-way; a
thirteen-row **files considered and rejected** table, including the *third term* against
`site-survey` / `survey-valuation`; a **neighbours with no edge** section with the reason for each
omission; **`proposed_fields`** as two secondings plus one open disagreement with the anchor over
`instruction` versus canonical `project`; **NJ-DA-1** and **NJ-DA-2** as new open questions; the
sparse-file section; and the audit list.

**Added to the JSON this pass:** two `file_examples` (`Household budget 2026.xlsx`,
`Extension - builder quotes.xlsx`), four `collides_with` entries
(`finance.small-business-bookkeeping`, `finance.cap-table-equity`,
`construction_property.survey-valuation`, `construction_property.sale-purchase`), the two
`proposed_fields` secondings, a rewritten `one_line` that drops the retired gist label, and
`open_question` restated around NJ-DA-1 / NJ-DA-2.

**Qualified rather than preserved:** the gist draft's leg-2 claim, as described above. Nothing else
was reversed.
