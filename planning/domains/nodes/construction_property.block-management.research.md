# `construction_property.block-management` — lab notes (J-IND row deepened to J-DEPTH)

Depth: J-DEPTH
Row: `construction_property.block-management` · kind `template` · schema `construction_property`
· launch `placeholder` · `fields: []` · absorbs the legacy row `prop.block-management`
(ROSTER.md §4 → `13-trades-property-logistics.json`).

This memo replaces a 4.3KB gist memo. The gist memo's arguments were sound and are **preserved**,
not re-phrased; what follows adds the sections the gist standard skipped. The audit of exactly what
changed is the last section.

---

## Sources actually used

### Binding local sources

- `planning/00-database-agent-product-design.md` — every quotation below was grep-matched verbatim
  against it before writing. Nothing is paraphrased-as-quoted.
- `planning/prompts/ALIGNMENT.md`; `planning/domains/CONNECTION.md` (the §2 node test, and PR-6);
  `planning/domains/_CONTRACT.md` (rules 3, 9, 10, 15); `planning/domains/canonical_fields.json`.
- `planning/overnight/council/DECISION-BRIEF.md` — D1 as narrowed, D4, J-IND. Ratified; not
  re-debated here.
- `planning/domains/dispatch/RESEARCH-BRIEF.md` and `DEEPEN-ADDENDUM.md`.

### Neighbours read in full before writing, and not rewritten

- **`construction_property.research.md`** (schema anchor, J-DEPTH, 43KB) — the row this one must
  differ from. It states the family's default template explicitly, which makes this row's node test
  checkable rather than rhetorical. It also names this row's primary structure, the apportionment
  schedule, as one of the four structures that make the *schema itself* detectable.
- **`construction_property.commercial-lease.research.md`** (J-DEPTH, 38KB) — **it names this row
  directly**, twice, and both statements are adopted rather than re-derived. See "Consistency with
  `commercial-lease`" below.
- **`construction_property.service-charge.research.md`** — the closest sibling on the roster, and
  the one that raised the merge question NJ-CP-17 *about this row*. Its collision was one-way until
  this pass; it is now reciprocated.
- **`construction_property.tenancy-management.research.md`** — the third row in the "ongoing life of
  a building" cluster. It routes ground-rent and service-charge demands *away* from itself; that
  routing is honoured and not contradicted.
- **`finance.hoa-residents-association.research.md`** (landed launch row, full depth, 26KB) — the
  load-bearing seam. Read in full, including its external artifact reality checks and its NJ-hoa-1,
  before a single word of the boundary was written.
- `construction_property.compliance-certificate.json` and `.timesheet.json` — the family's two
  refusals, read as the standard this row had to clear.
- `business_operations.organisational-records.json` — read for refusal quality, per the brief.

### A source that is not available, and it matters

`00` **never names this world.** Its template-library sentence lists *"academic programs, university
applications, recruiting processes, client engagements, research workflows, financial records,
travel, legal matters, creative projects, software repositories, personal administration, and photo
collections"*. Block management is absent, as is all of commercial property. Consequently
`design_cite` is `null`, `provenance` is `proposal`, and **every** `collides_with` entry on this row
carries `provenance: inference`. `00` supplies the machinery — detection, grouping, residuals,
privacy ordering, the observation/fact firewall — and this row supplies the situation. Where the
memo below asserts something `00` does not say, it is marked as inference.

---

## What this row is, in one paragraph

Running a multi-occupied building **on behalf of the people who own it**, under an appointment. The
work leaves a record with an unusual property: it is *about a building* and *addressed to dozens of
households at once*. The budget is split between units by a fixed share; the demands go out against
that split; the year is reconciled against certified accounts; the block is insured as one asset with
a schedule of units behind it; the contractors are engaged for communal parts nobody individually
owns; the statutory safety regime repeats annually on the whole structure; the major works are
consulted on before they can be charged; and around all of it runs a correspondence keyed to unit
numbers — arrears, breaches, consents, sublets. The anchor is a **building under an appointment with
a per-unit apportionment**.

---

## The node test, all three legs, argued

CONNECTION.md §2: a template row exists only where its **detection signals**, its **recommended
dimensions**, or its **privacy rules** differ from its schema's default template. The schema anchor
states that default in terms this row can be measured against:

> **`property` or site → `instruction` (the job, the letting, the scheme, the block) → document
> function**, with a period level only where the situation *genuinely cycles* (a service-charge
> year, a rent-review cycle). **Not time-first.**

And it states the trap every sibling on this schema must clear:

> *`variation`, `snagging`, `dilapidations`, `retention`, `preliminaries`, `certificate`, `drawing`,
> `schedule`, `survey`, `valuation` and `report` are **values of `work_type`**, not rows.*

`schedule`, `certificate` and `report` are on that list by name, and this row's `work_types` are
thick with all three. **A row cannot be earned by holding schedules, certificates and reports.**
Everything below is written knowing that.

### Leg 2 first, because it is the leg the row actually stands on

Four structures, and the first is the one that matters.

**1. The apportionment schedule.** Rows are the *units of one building*; columns are a percentage or
fractional share and a demanded amount; the shares sum across the building and the amounts sum to a
budget for it. This is not this row's invention — the schema anchor names it as one of the **four
structures that make the whole schema detectable**, alongside the title block, the measured-works
table and the `to date, less previously certified` shape:

> The apportionment schedule. Rows that are units or leaseholders *within one building*, columns
> that are a percentage share and a demanded amount, attached to a budget for that building. A
> share-of-a-fixed-asset table is structurally unlike a customer ledger or a payroll run.

`00` licenses reading it — *"Tables matter because resumes, forms, applications, invoices, and
administrative documents often place their most useful information in cells rather than body
paragraphs."* What makes the table *this row's* rather than any other money table's is the
**denominator**: it is a fixed asset split between co-owners, so the rows are exhaustive of a
physical thing. A customer ledger's rows are whoever bought something; a payroll run's rows are
whoever is employed; both are open sets. A block's unit schedule is closed by the building.

**2. The staged consultation sequence.** A notice of intention describing proposed works to all
leaseholders, an invitation to make observations within a stated period, and a subsequent notice of
estimates with contractor quotations attached. What makes this a structure and not a letter is that
it is a **precondition on spending**: the notices exist because the cost cannot be apportioned until
the consultation has run. Nothing else on the roster has a document series whose purpose is to make
a later charge lawful. (Inference. `00` does not discuss consultation and no jurisdiction rule is
asserted — under `_CONTRACT` rule 9 and D4 the statutory particulars are **values**, never keys.)

**3. The block-wide recurring compliance regime.** Fire risk assessment, fire door and alarm
inspection, asbestos register, lift examination, water hygiene, emergency lighting — covering the
*whole building*, on a repeating cycle, each year's copy sitting beside the previous three. This is
the structure that most distinguishes the row from every sibling, because **it is a regime rather
than a document**, and it is precisely the coverage the family's `compliance-certificate` refusal
routed here (route (c) of that refusal). A single fire risk assessment is a report; a fire risk
assessment *with its three predecessors, for one address, in sequence* is a compliance regime, and
only a template can carry a detection method that depends on recurrence. The schema anchor already
ratified that principle for `progress-photos`: *"a `work_type` value cannot carry a different
detection method; only a template can."* The identical argument runs here.

**4. The agency recital.** New in this pass, and it exists to answer the dispatch's warning. See the
next section, which is the hardest thing in this memo.

**Verdict on leg 2: passes**, on (1) and (3) principally. (2) is real but jurisdiction-shaped and
is not leaned on. (4) is a discriminator against one specific neighbour rather than a general signal.

### Leg 1 — recommended dimensions

Two differences from the family default, one positive and one negative.

- **A SERVICE-CHARGE YEAR level, under one branch only.** The family default grants a period level
  "only where the situation *genuinely cycles*", and this branch does: a budget is set for a named
  accounting year, demands are issued against it, and the year is closed with certified accounts
  comparing budget to actual. That is a closed loop with a name. It applies to the service-charge
  branch and **nowhere else in this row** — compliance recurs but does not reconcile; insurance
  renews but does not reconcile; works are projects. So the year level is a *branch-local* level,
  which is itself a departure from a family default that speaks of the tree as a whole. **A small
  factual point inherited from `service-charge` and worth keeping: a service-charge year frequently
  does not run to the calendar.** It is a named accounting period, not a date, which is also why a
  bare 4-digit number is especially misleading here.
- **NEVER a UNIT level, explicitly.** This is the negative, and negatives are the rarer and more
  useful kind of difference. A unit is a **household**. A unit level writes a real person's home
  address into a directory name that other software indexes, for the convenience of filing their
  arrears. An agent would reasonably want the opposite, because their entire working life is
  unit-keyed. This row declines to recommend it and says plainly that the conflict is real: it is
  usability against `00`'s collector prohibition, and it is Joseph's, not this row's. The sibling
  `tenancy-management` reached the identical conclusion about a tenant's name (NJ-CP-TEN-3), from a
  different direction, which is corroboration rather than coordination.
- **Not time-first**, per the family rule and `00`'s own reason — *"putting year first scatters
  related work across calendar folders."* Note the year level above is not a violation: it sits
  *under* property and function, not above them.
- `dimension_order` is `[]` **by binding contract** — a dimension may only branch on a field the
  same entry's schema declares, and `construction_property` declares none (D1 as narrowed,
  `_CONTRACT` rules 10 and 15, CONNECTION PR-6). All of the above is held as prose in
  `template.why` for whoever answers NJ-CP-1. And whatever eventually lands stays a recommendation:
  *"The system recommends an order based on the domain template, but the user can reverse, remove,
  add, or flatten dimensions."*

**Verdict on leg 1: passes**, on the branch-local year level and on the unit prohibition.

### Leg 3 — privacy rules

This leg passes on the **ground**, not on the setting. The setting is `potentially_sensitive`, the
schema default; no P7 handling class is assigned here and `is_safety_domain` is not carried — `00`
names four safety domains and this is not among them.

The family's stated privacy ground is that *the material names a real person's home and who is in
it*: one instruction, one property, one household exposed. **This row's exposure differs in kind.**

- **It is en masse and structural.** A single ordinary working file — the arrears schedule — is a
  list of *every household in one building* and what each of them owes, who has been referred to
  solicitors, and who has breached their lease. The apportionment schedule is a roster of every
  unit. The unit of exposure is a whole population at one postal address, not one client. `00`'s
  corpus sentence covers the material directly: the corpus *"can include identity documents,
  account statements, tax records, medical information, legal records, credentials, private
  correspondence, GPS metadata, employment materials, and educational records"*.
- **The second ground has no analogue in the family default at all.** The compliance half is a
  complete safety, plant and access description of an occupied residential building: where the
  asbestos is, which fire doors failed, how the lift is reached, where the risers run. That is not
  personal data and it is not commercial confidence; it is a third category, and it is material that
  should not leave the machine casually.

Both grounds bite before anything else happens: *"Privacy policy must be enforced before content
reaches any model or external connector."*

**Verdict on leg 3: passes on the ground.** It would be dishonest to claim it passes on the setting,
which is inherited.

**Overall: the row stands**, on three legs, leg 2 strongest.

---

## The hardest thing in this memo: `finance.hoa-residents-association`

The dispatch's warning was exact, and it deserves to be quoted as the standard rather than
paraphrased: *if the only discriminator against `finance.hoa-residents-association` is that a
company does the work rather than the residents, that is an organisation name — never-alone evidence
that cannot activate a row.*

**The warning is correct and the gist draft was on the wrong side of it.** The gist draft drew the
boundary on "the APPOINTMENT: a management agreement, a fee, an agent's letterhead". Two of those
three are names in disguise. A letterhead is an organisation name. A fee attaches to a name. And
this schema's own constitutional never-alone list, inherited from the schema row's reading of `00`
on a university name, disposes of them:

> A university name alone should not create a group because Columbia can appear as an authoring
> school, course provider, target institution, employer, research venue, or merely a cited
> organization.

The landed row says the same thing from its own side, and more sharply: it holds that a
management-company footer does not invert who a record belongs to, that a management-office contact
card is not absorbed from one organisation name, and that the manager or producer remains an
**observation** while the role question is open (its NJ-hoa-1). It also cites Washington
[RCW 64.34.372](https://app.leg.wa.gov/RCW/default.aspx?cite=64.34.372) as distinguishing
association records from a managing agent's custody — which establishes that the seam is *real* in
the world, and establishes nothing at all about how to *detect* it in a file.

So the appointment discriminator is retired as the primary. Two structural discriminators replace
it, and both are properties of the document rather than of who holds it.

### Discriminator 1 — the denominator

The two rows' characteristic financial artefacts are **the same table at two different scopes**:

| | this row | `finance.hoa-residents-association` |
|---|---|---|
| characteristic artefact | the apportionment schedule / demand run / arrears schedule | one member's assessment account |
| rows | **every unit of the building** | **one unit** |
| what sums | shares sum across the building; amounts sum to the budget | charges and payments sum to that member's balance |
| direction | issued outward, to all units | received, or held as one's own |

Whole denominator versus single numerator. This is readable in the bytes, requires no name, and is
exactly the shape the schema anchor already identified as the family's own signal. The landed row's
fixture 1 is `Annual Assessment Statement - Unit 4B.pdf` — *"association, owner, unit, explicitly
labelled assessment account, charges, payments and balance"* — and this row now names **those same
bytes** in its own `file_examples` as a thing it must not fire on.

### Discriminator 2 — the agency recital

A **party-role structure**, not a name, and the schema anchor explicitly licenses this class of
evidence: its professional-versus-householder table admits *"a client party in a role slot"* as
evidence of instruction.

A demand or notice that speaks expressly **for and on behalf of** a named landlord or company
occupies **three** roles at once: a client in whose name the document speaks, an appointee who signs
it, and a leaseholder, contractor or insurer it is addressed to. An association issuing in its own
name occupies **two**. The recital is not the agent's name; it is the *grammar of authority*, and it
is present or absent independently of who is named in it.

**Its limit, stated rather than hidden:** it is absent from most of the row's material. A fire risk
assessment has no recital. Neither does an insurance schedule, a contractor quote, or a set of
minutes. So it is decisive **where present** and does no work where absent — a discriminator, not a
gate.

### The honest limit, and why it is a NEEDS-JOSEPH rather than a refusal

**Both discriminators fail on the same corpus.** A residents' management company that self-manages a
single block issues the whole apportionment table itself, in its own name, with no agency recital
anywhere in the folder. On that holder's files these two rows are **not separable by evidence.** The
resident *director* is the acute form of the same problem: they hold the professional record and
their own leaseholder copies inseparably, and both roles are legitimate.

That is not a reason to refuse the row. It is a reason to be explicit that the row's activation is
**conditional on evidence it sometimes does not have**, and that where it does not have it the
correct outcome is co-activation or abstention and never a silent pick — *"Correct abstention is a
successful outcome because the product's goal is reliable organization, not maximum file movement."*
Filed as **NJ-CP-8**, widened from the gist draft's director-only version, with the reciprocal owed
on the landed row.

**What counts for NEITHER row**, stated once so both sides can use it: a building name, a unit
number, an assessment or service-charge amount, a budget, a reserve schedule, a set of minutes, an
association name, a managing agent's name, and — this is the one that surprised the pass — **a
management agreement**, because the association's own contract with its manager is that same
document held on the other side.

---

## Consistency with `commercial-lease`, which named this row directly

`construction_property.commercial-lease` was deepened just before this pass and made two statements
about this row. Both are **adopted unchanged**; neither is re-derived.

**1. On the period level.** It argued a *negative* — that it needs no year level — and used this row
as the contrast:

> The two siblings that share this row's folder — `service-charge` and `block-management` — both
> recommend a year level, and correctly: a service-charge year is a *named accounting period* that
> genuinely cycles. This situation does **not** cycle.

This row's leg 1 above says the same thing from this side, and adds the refinement that side does
not need: the year level here is **branch-local**, applying to the service-charge branch only.
That is a strengthening of its statement, not a divergence from it.

**2. On the apportionment.** It distinguished its own recharge structure from this row's:

> The lease-defined recharge proportion. A service-charge or insurance-rent apportionment for
> **one unit** stated as *the proportion the lease defines*, applied to a landlord's expenditure
> schedule. The proportion's authority is the instrument. This is what separates it from
> `block-management`'s whole-building apportionment schedule, which derives the shares itself.

Adopted exactly. Note that this is the **same distinction** as discriminator 1 against the HOA row,
arrived at independently by a different sibling against a different neighbour — one unit's share
versus the whole table. That convergence is the strongest evidence in this memo that the
discriminator is real rather than convenient.

Its "files considered and rejected" table names the competing item from its side:

> A whole-building service-charge budget with an apportionment schedule across every unit |
> `block-management` and `service-charge`. This row holds the **single unit's** recharge under **its
> own lease's** proportion. Reciprocated; a service-charge line appears in both and decides neither.

**The same bytes, named on both sides:**
`Harbour Works - service charge budget 2026 - apportionment.xlsx`. It is this row's `file_examples`
entry 1 and that row's rejected item. Neither side claims it exclusively.

**One thing to flag, and it is a genuine methodological difference rather than a contradiction.**
`commercial-lease` earned its row by re-examining what its `instruction` level *means* — that a
tenancy is a relationship with a term, not a commissioned job. This row's equivalent move is
different: it re-examines what its **top** level means. The family default's `property` level is a
site that work is done *to*; here the property is a site that is **co-owned by many people at once**,
which is what makes the denominator structure possible in the first place. Same standard, different
level of the tree.

---

## The sibling that could swallow this row: `service-charge`

`construction_property.service-charge` names this row under its own heading *"The hardest thing about this row"* and
raises **NJ-CP-17 — merge with `construction_property.block-management`?** Its collision was written
so the merge stays available; this row's was silent on it until this pass. **The edge is now
reciprocated and the merge is not resolved here.**

The state of the argument, honestly:

- **The two rows share their primary signal.** That sibling's leg 2 rests on *"a cost table split by
  a fixed share per unit"* — the apportionment schedule, this row's primary structure. Neither row
  can be told from the other by that table alone.
- **Each has an independent signal.** That row's is the **estimate-then-reconcile pair**: a budget
  followed by a certified account for the same named accounting year, which no ordinary bill has.
  This row's are the **block-wide recurring compliance regime** and the **unit-correspondence
  ledger**, neither of which that row claims. So both clear the §2 test separately, against the
  schema default, which is the test that actually governs.
- **But the split is by function, and that is not how a holder files.** One agent, one building, one
  year, one folder. The sibling says this plainly and this row agrees rather than defending its own
  territory.

**Verdict: both rows stand under §2, and the merge remains Joseph's.** No research is lost either
way — the merged row would be the union of these two memos. Where a single file is genuinely both,
the budget-with-apportionment being the named case, the correct outcome is **co-activation, not a
pick.**

---

## Reciprocal boundaries, both directions

Five edges in `collides_with`, each stated so it reads the same from both ends.

| Neighbour | This row holds | They hold | Counts for neither |
|---|---|---|---|
| `finance.hoa-residents-association` | the whole apportionment denominator; an outward demand or arrears run; documents with an on-behalf-of recital | one member's assessment account; the owner's own copies, meeting papers and governing documents | building name, unit, amount, budget, reserve schedule, minutes, **and the management agreement** |
| `construction_property.service-charge` | the appointment, contractors and cyclical works, the compliance regime, insurance placement, meetings, unit correspondence | the money cycle: budget → demands → estimate-then-reconcile → certified accounts, balancing charges | the apportionment schedule itself — shared, and the reason NJ-CP-17 exists |
| `business_operations.board-governance` | a meeting about one building's charge, works and compliance, attended by its leaseholders | a meeting about an organisation's own strategy, budget and statutory standing | a quorum, a resolution, a set of minutes |
| `construction_property.construction-project` | consultation notices, observations, apportionment of the cost, reserve-fund drawdown | the contract sum, instructions, valuations against measured works, the final account | the works description; the same roof renewal produces both sets |
| `finance.insurance-corporate` | a whole building with a reinstatement sum and a schedule of units | the agent's own professional indemnity or employers' liability | a carrier name, a policy number, a premium |
| `construction_property.commercial-lease` | the block-wide budget, apportionment and communal compliance regime | one occupier's lease, its rent review, its schedule of condition, its dilapidations | a service-charge line, which appears in both |

`also_holds_with` is empty because CONNECTION restricts it to **schema** pairs and this is a template
row. The genuine cross-schema co-activations are carried as `also_schema` on individual
`file_examples` — `finance` on the budget, the demand and the insurance schedule; `legal` on the
arrears report and the lease; `business_operations` on the AGM minutes. `role_split` is empty
because it can only connect canonical keys, and this row mints none.

---

## The collision fixture, in both directions

**A file that would wrongly fire this row.**
`Annual Assessment Statement - Unit 4B.pdf`. A labelled assessment account for one unit — charges,
payments, a balance — issued by a named association in its own name, with a management company's
footer at the bottom of the page. Every superficial cue points here: a unit, a building, money owed,
a management company. **It is not this row's.** It is one numerator, not the whole denominator; it
carries no agency recital; and the footer is an organisation name that inverts nothing. It belongs
to `finance.hoa-residents-association`, where it is fixture 1. Named on both sides deliberately.

**A file that must not be lost *to* this row.**
`Lease - Flat 12 Harbour Works.pdf`. It is in every block manager's folder; it contains the
apportionment percentage this row's whole budget depends on; and it is **not this row's document.**
`legal.leases-agreements` owns the executed instrument, `legal` is a safety domain and protects
first, and this row *reads the percentage without owning the deed.* The `file_examples` entry says
so in its `must_not_conclude`. The general principle, from the schema anchor's seam table: an
executed instrument with party recitals, covenants, consideration and an execution block is
`legal`'s, whoever is holding it and whatever they use it for.

**A third, because this row's worst failure mode is folder-context leakage.**
`Arrears report.xlsx` with **no building name anywhere in the file** — rows of units, named
leaseholders, balances, ageing, solicitor referral flags. It is unmistakably this situation and it
carries no evidence of *which* building. The `must_not_conclude` forbids taking the building from
the surrounding folder, because folder context never fires alone. And it is the file on which
`00`'s ordering matters most: *"Privacy policy must be enforced before content reaches any model or
external connector."*

---

## Files considered and rejected

The brief's test: a row that only lists what it holds has not been researched.

| File | Why it is **not** this row's evidence |
|---|---|
| `Annual Assessment Statement - Unit 4B.pdf` | **The collision fixture.** One member's own account. `finance.hoa-residents-association`'s fixture 1, named on both sides. |
| `Lease - Flat 12 Harbour Works.pdf` | The operative instrument. `legal.leases-agreements`, and it protects first. This row reads the percentage inside it without owning it. |
| `Scan_demand_flat12.jpg` | A leaseholder's single scanned demand. `service-charge` kept this as its own fixture for exactly this reason: a single received demand must not activate a professional row. Routes to a residual or to the residents' side. |
| `Ground rent demand - Flat 12.pdf` | Arrives in the same envelope as a service-charge demand and is a legally different payment, belonging to the freeholder's investment record. No row on this roster owns that cleanly. Recorded for R1c; `service-charge` recorded the same gap independently. |
| Right-to-manage and tribunal application papers | A **proceeding** is `legal`'s — `legal.personal-legal-matters` and the practice rows. Referenced only through the arrears fixture's `also_schema`. A dispute about a service charge is not a service charge. |
| Communal utility bills — the block's electricity, water, lift line | A **cost heading inside the budget**, not a separate claim on the file. `finance.subscriptions-utilities`, whose landed edges already state the service-address discriminator. A service address is not a demise and is not an appointment. |
| A contractor's quotation for communal cleaning, with no apportionment and no consultation reference | Kept as a `file_examples` entry precisely because it is the near-miss: it has a building address and a price and **nothing else**. An ordinary supplier document; `Receipts and Confirmations`. |
| A fit-out drawing set, or the building contract behind a major works scheme | `drawings-revisions` and `construction-project`. The consultation apparatus is this row's; the sheets have their own title blocks and are their own files. |
| A managing agent's own PI policy, staff payroll, or client-account audit | The agent running *itself* is `business_operations` and `finance`. This row is about the buildings, not the firm. This is the same distinction `business_operations.facilities-workplace` sits on from the other direction. |
| A market report on service-charge benchmarks; a professional guidance note on fire safety | `Reading Inbox` — *"papers, articles, reports, and saved PDFs that appear to be reading material but have no active research, course, or project association."* These accumulate heavily in exactly this folder. |
| A residential AST for one flat inside the block, with its deposit certificate | `tenancy-management`. That row's landed memo routes service-charge material *away* from itself; this row reciprocates by not claiming the letting. A landlord of one flat in a block honestly holds both files, and neither row absorbs the other. |
| A blank budget template, a blank consultation notice, an unfilled apportionment spreadsheet | Nothing is filled in, so no relationship or building is evidenced. The landed HOA row made the same call about blank covenants and minutes templates and it carries over unchanged. |
| A `.vcf` for the block's caretaker or the agent's out-of-hours line | `00` requires contact data be privacy-protected rather than used to create folder proposals. A file-kind signal at most, and not listed among this row's plausible file kinds. |
| A newsletter to residents about the summer barbecue | Real, and in the folder. Not an administrative record of the appointment. General reading stays broad; the landed HOA row reached the same conclusion about amenity announcements. |

---

## Neighbours considered that did **not** get an edge

- **`business_operations.facilities-workplace`** — an organisation occupying its *own* premises. The
  schema row already carries the `business_operations` collision at family level, and the specific
  confusion (a facilities contractor versus a communal contractor) is thin. Preserved from the gist
  draft, whose judgement here was right: a fifth `business_operations`-flavoured edge would be noise.
- **`construction_property.tenancy-management`** — argued above and left as a rejected file rather
  than an edge, because the two rows share **no discriminating evidence item**: a deposit
  certificate and an apportionment schedule cannot be confused with one another. Its own memo
  already routes service-charge demands away, so a two-way edge would restate agreement as conflict.
- **`finance.subscriptions-utilities`** — the landed row already states the service-address
  discriminator against property records generally. Repeating it one-way adds nothing.
- **`nonprofit` / `government.*`** — a residents' company has directors and meetings, and the
  statutory regime shapes the documents heavily, but under D4 and `_CONTRACT` rule 9 jurisdiction is
  a **values** question, not an edge. `service-charge` reached this independently and it holds here.
- **Residual templates** — broad fallback homes, not collision endpoints. Six are named in
  `falls_through_to` using the closed names.

---

## Grouping, and the firewall

Seven accepted groups sit in the JSON. The two that need argument:

**One BUILDING across everything** is this row's primary group and an unusually durable one. The
block outlives every agent, every director and every leaseholder, and its records are physically
handed from agent to agent — which is why the handover pack is a `work_type`. `00` licenses the
mixed membership: *"The documents are content-incoherent but purpose-coherent."* A fire risk
assessment, an insurance schedule, a budget and a set of minutes share no vocabulary, no format and
no author. They share a building.

**One UNIT across its correspondence** is the dangerous group. It is a group *about a household
inside a building*, and it is the reason the row's sensitivity ground is written as it is and the
reason a unit is not a comfortable folder level. The firewall: membership of an accepted group never
creates a fact on a member that lacks its own evidence, and the arrears fixture carries
`group_without_copying_facts: true` for exactly this reason.

The stop rules apply unchanged — *"when members carry irreconcilable course, institution, project,
term, or purpose facts"*. Two blocks' budgets do not merge because the same agent produced both from
the same template. And the duplicate rule matters here more than in most rows, because block
software regenerates identical demand PDFs on every run: *"A content-hash match supports
deduplication review; a filename match alone does not."*

Finally, no group at all is a valid outcome: *"Independent Records may live under Personal/Independent Records and hold standalone
certificates, notices, confirmations, forms, and PDFs that have a durable purpose but no broader
group."*

---

## `proposed_fields` — the full list

**Empty. This row proposes nothing.**

Per the dispatch, the family's existing proposals are **seconded, not re-minted**:

- **`property`** — proposed by the schema row and the key this row most needs. Seconded. It is also
  the key the landed `finance.hoa-residents-association` row seconds from the other side, noting
  that duplicating it *"would create two private versions of one join handle."* Exactly right, and
  the same reasoning stops this row minting one.
- **`instruction`** — proposed by the schema row. Seconded, with one observation for R1c: this row's
  `instruction` is a **standing appointment over a building**, not a job with an end, which is a
  third reading beside `commercial-lease`'s tenancy-as-relationship and the family's job-with-a-term.
  If R1c narrows `instruction` to bounded jobs, this row and `commercial-lease` both lose their
  middle level together.
- **`organization`** — seconded. No `managing_agent`, `association` or `landlord` variant is minted;
  those are role readings of one key and the landed HOA row's NJ-hoa-1 is already open on exactly
  that question.

**A `unit` key was considered and deliberately NOT proposed.** It would be the most natural key in
this world and an agent would use it hourly. It is declined because a unit is a household and the
key would exist chiefly to become a folder level. That is a judgement, it is contestable, and it is
raised as an open question rather than settled here.

Candidate dimensions — building, function, service-charge year — remain **prose** in `template.why`,
with the note that *service-charge year* is a named accounting period and must never be conflated
with a calendar-year key if it ever becomes one.

---

## NEEDS-JOSEPH (this node only)

- **NJ-CP-8 · The seam with `finance.hoa-residents-association`, widened.** Both of this row's
  structural discriminators — the whole denominator and the agency recital — fail together on one
  real corpus: a residents' management company self-managing a single block, which issues the whole
  table in its own name and files no recital anywhere. The resident *director* is the acute form.
  On those corpora the rows are not separable by evidence. **Alternatives:** (a) co-activate and let
  both offer, which is honest but doubles the proposal surface for the holder; (b) abstain and route
  to a residual, which is safe but loses real organisation for a real user; (c) let the presence of
  a *portfolio* of buildings decide, which works for agents and fails for the one-block agent. This
  pass recommends (a) with (b) as the fallback and **rejects** (c) as a corpus-level signal that
  cannot activate a single file. Reciprocal owed on the landed row.
- **NJ-CP-17 · Merge with `construction_property.service-charge`?** Raised by that sibling, seconded
  here. One agent, one building, one folder, split by function only. Both rows clear §2 separately;
  the split is not how a holder files. **Alternatives:** merge into one row whose memo is the union
  of the two, or keep the split and accept that most real folders activate both. No research is lost
  either way.
- **NJ-CP-BM-1 · A unit as a destination dimension, and as a field.** Usability against `00`'s
  collector prohibition. An agent's filing is unit-keyed; a unit is a home address. This row declines
  both the level and the key. **Alternatives:** permit it as a user-added level only, never
  recommended; permit it as an observation that is destination-ineligible; or forbid it outright.
  This pass recommends the second. Joseph's.
- **Inherits NJ-CP-1** — if R1c refuses `property` a canonical key, the schema's own leg 1 loses its
  strongest limb and this row's recommended tree loses its top level.
- **Inherits NJ-CP-4** — no P7 handling class is assigned here, and the compliance half's
  building-security exposure is a *third* category of sensitivity that the family's two grounds do
  not describe. Flagged for whoever sets handling classes.

---

## Audits run before returning

- `python3 -m json.tool` on the JSON: parses.
- Key set compared programmatically against the landed J-DEPTH sibling
  `construction_property.commercial-lease.json`: **identical**, no extra keys, none missing.
- Every `00` quotation in both files grep-matched verbatim against
  `planning/00-database-agent-product-design.md`: all present, each exactly once.
- Quotations from the schema anchor, `commercial-lease` and `service-charge` grep-matched verbatim
  against those files.
- `fields: []` and `proposed_fields: []` confirmed; no canonical key minted anywhere.
- `launch: "placeholder"`, `provenance: "proposal"`, `design_cite: null`, every `collides_with`
  entry `provenance: "inference"` — confirmed, and consistent with `00` never naming this world.
- Files written: **only** `planning/domains/nodes/construction_property.block-management.json` and
  `.research.md`. Nothing else touched.

---

## What changed in this pass

**Preserved unchanged**, because it was right:

- The whole `recognition` block's existing entries, the `never_alone` list, `proposed_context_terms`,
  `work_types`, `grouping_reasons`, `template.why`, `file_kinds`, `falls_through_to`, and nine of
  the ten `file_examples`.
- The **year level under the service-charge branch only** — the gist draft's best call, and the one
  `commercial-lease` later cited approvingly.
- The **unit-level prohibition** and its framing as a usability-versus-collector-prohibition
  conflict that is Joseph's.
- The routing of the refused `compliance-certificate` row's coverage into this row's compliance
  regime, as route (c) of that refusal.
- The `legal.leases-agreements` treatment: this row reads the apportionment percentage inside a
  lease without owning the instrument.
- The four existing collision edges to `board-governance`, `construction-project`,
  `insurance-corporate` and `commercial-lease`.

**Changed, and stated openly rather than silently:**

- **The `finance.hoa-residents-association` discriminator is replaced.** The gist draft rested it on
  "the APPOINTMENT: a management agreement, a fee, an agent's letterhead", which is substantially an
  organisation name and could not have activated the row. It is replaced by the **whole denominator**
  and the **agency recital**, both structural, and the appointment is demoted to a signal that
  locates the situation without deciding the side — because the association holds that same document.
  This is a reversal of a gist-era argument and it is marked as one.
- **NJ-CP-8 is widened** from the resident-director case alone to the whole class of self-managing
  single-block corpora, with alternatives and a recommendation.

**Added:**

- The node test argued leg by leg against the schema anchor's stated default, with a verdict and a
  reason per leg, and leg 3 argued on the *ground* rather than the setting.
- A reciprocal edge to **`construction_property.service-charge`**, which was missing entirely — that
  sibling named this row as its hardest problem and raised NJ-CP-17 one-way. Now two-way.
- An agency-recital deterministic signal and a whole-denominator deterministic signal, each with its
  limit stated.
- The `Annual Assessment Statement - Unit 4B.pdf` negative fixture, naming the landed HOA row's own
  fixture 1 bytes on this side.
- The collision fixture argued in **both** directions, plus a third for folder-context leakage.
- A files-considered-and-rejected table of fourteen entries, up from three.
- The reciprocal-boundaries table covering all six neighbours in both directions.
- The `proposed_fields` section seconding `property`, `instruction` and `organization` with an
  argument, including the observation that this row's `instruction` is a standing appointment rather
  than a bounded job — material for R1c.
- The sources section, the "`00` never names this world" note, the sensitivity ground re-argued as
  en-masse and building-security exposure, NJ-CP-BM-1, and this audit.

**Not padded.** The row had a great deal to say, chiefly because it sits at the intersection of two
live open questions (a landed launch row and a sibling merge proposal) and had answered neither
adequately.
