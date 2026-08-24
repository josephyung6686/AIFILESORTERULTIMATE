# `construction_property.snagging-defects` — lab notes (R1b, deepened to J-DEPTH)

Row kind: **template**. Schema: `construction_property`. Launch: **placeholder** (`fields: []`).
Absorbs the legacy row `cons.snagging` (ROSTER.md §4 + Appendix A). Verdict: **kept, not refused —
but on ONE leg of the node test rather than the three the gist pass implied, and the two failing legs
are now written down.**

**Status of this pass.** The row existed at the retired gist depth: a 29KB JSON whose key set was
house-correct and whose quotations were machine-verified, and a 4.3KB memo. The JSON was **verified
and extended, not discarded** — see *What was preserved, what was added*. The memo is replaced.

**The dispatch warned that this row may not survive, and instructed that refusing would be a success.
It survives, and this pass is unusually confident about that, for a reason that did not exist when
the gist row was written: the family's spine has since been deepened, has re-run its own node test,
and has DEMOTED the defects tracker out of its own activation evidence and conceded it here by
name.** The challenge that made this row look precarious was answered from the other side. What this
pass does instead of defending the row's existence is **narrow the grounds it stands on**, which is
the honest half of the same work.

---

## Sources actually used

### Binding local sources

- `planning/00-database-agent-product-design.md` — the only document quoted. Every quotation in the
  JSON was machine-verified verbatim on the previous pass and re-verified this pass. Quotations in
  this memo come from three kinds of source and each kind was checked separately — see **Audits**.
  The `00` spans doing real work here:
  - the table sentence, which licenses reading this row's central structure out of cells rather than
    prose: *"Tables matter because resumes, forms, applications, invoices, and administrative
    documents often place their most useful information in cells rather than body paragraphs."*
  - the abstention sentence for conflicting signals, which is this row's operating instruction on its
    load-bearing collision: *"conflicting signals should lead to abstention rather than an invented
    classification"*, and its companion *"Correct abstention is a successful outcome because the
    product’s goal is reliable organization, not maximum file movement."*
  - the purpose-coherence sentence, which is what makes *one defect* a legitimate group whose members
    share no content: *"The documents are content-incoherent but purpose-coherent."*
  - the sparse-file rule, which this row needs badly because half its members are photographs with
    nothing in the filename: *"The graph does not automatically copy those missing facts onto sparse
    files."*
  - the multi-role-token warning — the family's constitutional sentence, read across to a postal
    address: *"A university name alone should not create a group because Columbia can appear as an
    authoring school, course provider, target institution, employer, research venue, or merely a
    cited organization."*
  - the dimension-order rule and the parent-context rule, for `template.why`: *"For document and
    record domains, project, function, or subject usually comes before time because putting year
    first scatters related work across calendar folders."* and *"a parent dimension should provide
    the context required to understand the child"*.
  - the corpus sentence, for `sensitivity_why`: the corpus *"can include identity documents, account
    statements, tax records, medical information, legal records, credentials, private correspondence,
    GPS metadata, employment materials, and educational records"*.
  - the privacy-ordering sentence that opens both `recognition` blocks: *"Privacy policy must be
    enforced before content reaches any model or external connector."*
  - the evidence-hygiene sentences behind five `never_alone` entries — the extension, PDF-metadata,
    download-session, no-EXIF and archive rules — quoted in full in the JSON and not repeated here.
  - the six residual definitions, quoted in full in `falls_through_to`.
- `planning/domains/_CONTRACT.md` — rules 1–3 (provenance, no fabricated quotes, **no invented
  numbers**), 8 (snake_case; a dimension may only branch on a declared field), 10 (no field rows on a
  placeholder schema), 11–15 (`kind`, closed edge vocabulary).
- `planning/domains/CONNECTION.md` — §2 node test (argued leg by leg below), §3 **activation ≠
  grouping, browse-only parent**, §4 activation ordering (step 2 never-alone, step 5 protective
  ordering), §5 closed edge vocabulary (`also_holds_with` is **schema ↔ schema only**, which is why
  the three new co-holdings name schemas), §9 failure modes, PR-6.
- `planning/prompts/ALIGNMENT.md` — *"would only repeat its schema’s fields and dimension_order"* … *"it is the schema’s default
  template."*
- `planning/domains/canonical_fields.json` — confirmed `work_type`, `client`, `our_firm`, `project`,
  `location` and `event` exist, and that **nothing holds the property or the plot**. **No key
  minted.**
- `planning/overnight/council/DECISION-BRIEF.md` — D1 (as narrowed), D6, PR-6, J-IND taken as
  ratified and not re-debated. J-DEPTH (2026-08-24) overrules J-IND's gist clause and is why this
  memo exists. The `Depth: GIST` header is removed; the label is retired.
- `planning/domains/roster.json` — every `collides_with` and `also_holds_with` target resolved
  mechanically against `nodes[].domain_id`.

### Neighbours read in full before writing, and not rewritten

- **`construction_property.research.md` (the deepened schema anchor, 42KB)** — the measuring stick.
  It states the default template this row must differ from, names the family's four default
  structures, and **names this row by id as one that may turn out to be a `work_type` value on a
  sibling rather than a row of its own.** That sentence is the reason this pass re-ran the test from
  scratch instead of confirming the gist verdict.
- **`construction_property.construction-project.research.md` (deepened, 38KB)** — the spine, and the
  row the dispatch says this one was tested against on thin reasoning. Read in full. It **reverses**
  its gist claim to the defects tracker and concedes it here. See the next section.
- **`construction_property.progress-photos`** (JSON + memo) — read in full precisely because a snag
  list is often photographs with annotations. **Its argument is accepted here without amendment and
  is not contradicted;** this row is careful to claim nothing that resembles it. See the section on
  it below.
- **`construction_property.variation-claim`** (JSON + memo) — the load-bearing collision, already
  stated reciprocally in the same words on both rows. Re-read this pass; unchanged.
- **`construction_property.timesheet.json`** and **`construction_property.compliance-certificate.json`**
  — the family's two refusals, read in full as the dispatch instructed, as the standard this row had
  to clear. The **compliance-certificate** refusal in particular is the one this row had to survive:
  see *Why this row is not the compliance-certificate refusal wearing a table*.
- **`construction_property.inventory-inspection`** and **`construction_property.subcontract`** — both
  already name this row in their own `collides_with`. Their wording is adopted, not re-authored.
- **`finance.household-property`** (landed, full depth) — read for the professional/householder seam,
  which this pass **applies** rather than re-draws, and which produced the one reversal below.

### A source that does not exist, and it matters

`00` **never names this world.** Its template-library sentence lists *"academic programs, university
applications, recruiting processes, client engagements, research workflows, financial records,
travel, legal matters, creative projects, software repositories, personal administration, and photo
collections"* — construction is absent. So `design_cite` is `null`, `provenance` is `proposal`, and
every `collides_with` entry is `provenance: inference`. `00` supplies the machinery — extraction,
activation, never-alone, residuals, dimension order — and this family supplies the situation. No
quotation below is offered as design authority for the situation itself.

---

## The challenge the dispatch named, and what happened to it

The gist row recorded a collision with `construction_property.construction-project` **deliberately**,
because its own node test asked whether it was merely a `work_type` of the project's lifecycle. The
dispatch is right that the gist reasoning was thin: it asserted three differences and did not test
them against a spine that had not yet been written.

The spine has now been written, and it did the work from its own side. Its deepening pass demoted
**five** of its eight structural detection signals out of its activation evidence and conceded them
to the siblings that own them. One of the five is this row's:

> *"`construction_property.snagging-defects` exists and owns the defects tracker, and it recorded the
> collision **deliberately** because its own node test asked whether it was merely a `work_type` of
> this row"* … *"the defects half of the completion triple"* is **withdrawn**.

And in its JSON, in its own words:

> *"The sibling recorded this collision deliberately because its own node test asked whether it is
> merely a work_type of this row; it is not, and this row concedes the point. Its line, adopted
> unchanged: a defects-liability period, a re-issue sequence with a status column and activity AFTER
> practical completion support the sibling; anything inside the construction period supports this
> row. The practical-completion certificate itself stays here, being the boundary event rather than
> something after it."*

**Two consequences, and they pull in opposite directions.**

1. **The `work_type` challenge is settled, and not by this row's own enthusiasm.** The competing row
   examined the same bytes and gave them up. That is the strongest evidence available in a system
   where `00` never names the world, because it is the one form of evidence that cannot be
   self-serving.
2. **It settles less than it looks like it settles.** A concession establishes *which of two rows
   owns a structure*; it does not establish that the structure earns a row at all. Both rows could be
   wrong together. So the node test below is run on this row's own merits, against the **schema
   anchor's default template**, exactly as if the concession had not happened — and its verdict is
   narrower than the gist's.

**One line the spine drew that this row accepts and did not previously state clearly enough:** the
practical-completion certificate itself is the **project row's**, being the boundary event. This row
claims the outstanding-works schedule appended to it, not the certificate. The gist memo left this
"ambiguous on purpose"; the ambiguity is now resolved, in the spine's favour, and the fixture
`Practical completion certificate - Oakfield.pdf` in this row's JSON says so.

---

## The node test, all three legs, argued

CONNECTION.md §2: a template row exists only when its **detection signals**, its **recommended
dimensions**, or its **privacy rules** differ from its schema's default template. Any one leg
suffices. The gist memo answered a *different* question — it argued lifecycle, detection and version
behaviour — and two of those three are not legs of the test at all. They are restated below where
they belong: as corroboration, not as legs.

The default template, quoted from the deepened schema anchor so the comparison is checkable:

> **`property` or site → `instruction` (the job, the letting, the scheme, the block) → document
> function**, with a period level only where the situation *genuinely cycles*. **Not time-first.**

And the anchor's four default detection structures, which are what a sibling's leg 1 must add to:
the **title block**, the **measured-works table**, the **`to date, less previously certified`
valuation arithmetic**, and the **apportionment schedule**.

### Leg 1 — detection signals of its own. **PASSES.** This is the whole row.

The candidate is the **defect-register structure**: a table whose columns read item number, location
(plot, room, level or grid reference), a description of what is wrong, a responsible trade, a raised
date, a target date, a status, and a closed or verified date, with **one row per fault**.

Three things have to be true for that to count, and each is tested rather than asserted.

**(a) It is a fifth structure, not one of the anchor's four.** A defect register is not a title
block (no sheet border, no revision designator, no governed status word on a drawing), not a
measured-works table (its rows are faults, not described works with quantities and rates), not a
valuation (no cumulative arithmetic, no previously-certified subtraction), and not an apportionment
schedule (its rows are faults, not units bearing a percentage share). The four family structures are
about **what was agreed, built and paid for**; this one is about **what is wrong and who has to come
back**. `00`'s table sentence licenses reading it — *"Tables matter because resumes, forms,
applications, invoices, and administrative documents often place their most useful information in
cells rather than body paragraphs."* — and nothing in the anchor claims it.

**(b) The distinguishing pair is LOCATION beside STATUS, and neither half survives alone.** This is
the sharpest thing the gist row said and it is preserved. A status column alone is the most generic
vocabulary in the catalogue. A location column alone is an inventory, a schedule of condition, an
asset register, a fire-door register or a room data sheet — that entry is **new to this pass** in
`never_alone`, because the gist row named the pair as a fingerprint without disqualifying either
half, and a fingerprint whose halves are not disqualified is an assertion. What makes the pair this
row's and not a generic issue log is the **third** column: a **responsible TRADE** and a **physical
place inside a building**. `business_operations.project-delivery` owns the generic issue log with a
component and an assignee; the discriminator is that this row's assignee is a plasterer and this
row's component is a room.

**(c) The lifecycle markers are real signals, not a mood.** A **defects-liability or rectification
period that is RUNNING** — evidenced by dated activity after a stated completion date — is
structure, not sentiment. **New to this pass**, and against the gist row's interest: the period
*stated in a document* is **never-alone**, because it is a contract term printed in the contract
particulars, the subcontract order and the collateral warranty long before any defect exists. Only a
period with dated activity inside it is evidence. The gist row read "a defects-liability period" as a
signal flatly; that was too generous and it is corrected.

**Verdict on leg 1: passes.** It passes on a table structure the family does not otherwise have, and
it would fail if the structure were stripped to a numbered statused list — which is exactly why *"an
item-numbered table alone"* has been in this row's `never_alone` from the first pass.

### Leg 2 — recommended dimensions. **FAILS as a distinguishing leg.**

Available only as prose: `dimension_order` is `[]` **by contract, not by judgement** (`_CONTRACT`
rules 10 and 15, PR-6), because a dimension may only branch on a field the same entry's schema
declares and this schema declares none.

The row's recommendation, held as prose in `template.why`, is: **site or project → plot or unit →
defect phase → the register and its photographs together.** Set beside the default — **property or
site → instruction → document function** — that is the default with a **plot sub-level inserted** and
phase standing in for function. It is not a reversal, and it is not a different axis.

The gist memo did not claim leg 2, and it was right not to. This pass states the failure explicitly
because the addendum requires the test argued leg by leg rather than the passing legs listed. Two
honest observations that do **not** rescue it:

- The **plot** level is the one place the row genuinely wants something the default does not provide,
  because item 44 exists on every plot on a development and is meaningless without one — which is
  `00`'s own reason for putting a course above a homework number, *"a parent dimension should provide
  the context required to understand the child"*. But a plot is a **sub-division of the property
  level**, not a new dimension, and no canonical key holds either (NJ-CP-1).
- **Not time-first**, for the family's reason and one of its own: a single defect's life crosses
  months, and a register's re-issues are **versions, not periods**. `00`: *"For document and record
  domains, project, function, or subject usually comes before time because putting year first
  scatters related work across calendar folders."* That is agreement with the family, not difference
  from it.

Whatever lands stays a recommendation: *"The system recommends an order based on the domain template,
but the user can reverse, remove, add, or flatten dimensions."*

### Leg 3 — privacy rules. **FAILS as a distinguishing leg.**

The row sets `potentially_sensitive` on two grounds — a residential defect file names an occupant and
catalogues everything wrong with the home they live in, and a defect register names individual
tradespeople as responsible for failures — and `00`'s corpus sentence covers the category the moment
either appears.

**Both grounds are the schema's, not this row's.** The anchor already sets `potentially_sensitive`
for all 27 siblings on three grounds, and the first of them is *the material names a real person's
home and who is in it*, with the observation that *the exposed party is usually not the user*. This
row is not stricter than its schema. `construction_property.site-health-safety` is stricter — the
`timesheet` refusal records it operating under a privacy posture the schema anchor calls stricter than
this schema's default — and this row is not that row. No P7 handling class is assigned here; that is P7's.

The second ground, **named tradespeople recorded as responsible for failures**, is the only candidate
for a row-specific posture, and this pass declines to claim it. A defect register is not an
employment record and the harm is diffuse; asserting a stricter posture on it would be inventing a
distinction to win a leg the row does not need. It is recorded as NJ-CP-SNAG-3 instead.

### Overall

**Kept, on leg 1 alone.** One leg is all §2 requires, and claiming two or three would be the
unsourced confidence the brief forbids. This is the same shape as the deepened spine's own verdict,
which also survives on leg 1 with legs 2 and 3 recorded as failing — and it is filed as
NJ-CP-SNAG-4, because if R1c judges single-leg rows insufficient on a field-less schema, this row and
several siblings fall together.

**What the gist memo argued, and where each argument now sits:**

| Gist claim | Status now |
|---|---|
| **Lifecycle** — activity after practical completion, on a project everyone else considers finished | **Not a leg of §2.** Kept as *corroboration for leg 1* — it is what makes the running-defects-period signal legible, and it is what the spine conceded on. Downgraded from an independent argument. |
| **Detection signals** — a LOCATION column beside a STATUS column | **Leg 1, and now the whole row.** Strengthened by the fifth-structure comparison against the anchor's four; weakened by disqualifying each half alone. |
| **Version behaviour** — more near-duplicate files than any other row in the schema | **Not a leg of §2 either**, and the gist memo half-knew this, writing that it would have refused had only that third point been true. Re-inspected and demoted further: `duplicate_family` and `version_family` are **universal** facts that every row carries, and *carrying more of a universal is not a different detection signal.* Kept in `grouping_reasons`, removed from the node argument. |

That is a **narrowing**, not a reversal. The gist verdict — this is a node — stands. Its stated
grounds do not.

---

## Why this row is not the `compliance-certificate` refusal wearing a table

The dispatch pointed at the family's two refusals as the standard, and one of them is a direct threat
to this row. `compliance-certificate` was refused because its candidate signal, stripped, reduced to
**a document-type word plus an address** — and *both halves are constitutionally never-alone on this
schema*, so it would have been a row that never fires (CONNECTION §4 step 2).

Run the same reduction here. Strip *"snagging"*, *"defect"*, *"punch list"* and *"outstanding
works"* — all of them are `work_type` values and all four are already in this row's `never_alone`.
Strip the address, for the same reason. **What is left is not nothing**: it is a table whose rows are
individual faults and whose columns pair a physical place inside a building with a rectification
status and a responsible trade. A structure survives the strip, which is precisely what did not
survive it for the certificate.

The `timesheet` refusal supplies the other half of the test, and it is the harder one: *"a shared
table shape is not a situation."* That refusal split into three because its three contents belonged
to three existing rows. **Run the same split on this row and it does not come apart.** The
pre-completion list, the handover schedule, the defects-period register and the close-out are the
*same tracker at four points in its life* — the same items, the same numbering, the same file
re-issued. There is no sibling to hand each piece to; they are one document with a status column
changing. That is the difference between a table shape and a situation.

**This row would refuse if either test went the other way, and the tests are recorded so a reviewer
can re-run them.**

---

## `progress-photos` — the sibling this row must not contradict, and does not

The dispatch is right that a snag list is often **photographs with annotations**, and that
`progress-photos` earned its row on the claim that *a `work_type` value cannot carry a different
detection method; only a template can*. That claim is the family's best piece of reasoning, the
deepened spine accepts it unchanged, and the landed `creative.raw-photo-catalogue` row agreed with it
too. This row does not touch it.

**How this row differs, stated carefully.**

`progress-photos` is recognised by **capture metadata, rhythm and place** — a *different detection
method* from the family's documentary default. **This row makes no such claim.** This row is
recognised by **document structure**, exactly like every other row on the schema. Its leg 1 is the
register table. Its photographs are **grouped members of a register, never its activation evidence.**

That distinction is now written into the JSON in three places rather than left to this memo:

- a new `never_alone` entry stating that a defect photograph's **membership in a site walk** is not
  evidence for this row, and that a photograph enters here through an **item number** or through
  **membership in an accepted register** — never through capture metadata, a GPS cluster or a
  work-hours rhythm;
- a new reciprocal `collides_with` entry that **adopts the sibling's own wording** rather than
  re-authoring it: *"a measure, a marker or a caption identifying a fault, or membership in an
  accepted defect list, supports the snagging row; a record of the state of the works supports this
  row"*;
- a new fixture, `IMG_2231.HEIC` — the sibling's own bytes — carried here as a file that **must not
  be lost to this row**.

**Nothing in this row's argument depends on photographs**, and that is the cleanest way to state the
non-contradiction: if every photograph were removed from the corpus, leg 1 would be untouched. If the
register were removed, this row would have nothing. `progress-photos` is the exact inverse. Two rows
whose evidence is disjoint in that way are not competing for the same node.

The one direction that *is* genuinely contested is a single annotated frame with an item number
scrawled on it and no register in the folder. It goes to **One-Off Images** — *"One-Off Images may
live under Photos/One-Off Images and hold images with no event, project, reference collection, or
photo-family association."* — and that is stated on this side so the sibling can check it.

---

## Files considered and rejected

The brief's own test: a row that only lists what it holds has not been researched.

| File | Why it is **not** this row's evidence |
|---|---|
| `Sprint 14 bug export.csv` *(kept in the JSON as a collision fixture)* | The structural match is near-total — id, component, summary, assignee, priority, status, resolved. Discriminator: **no physical place and no trade.** It is `business_operations.project-delivery`'s, and it is the reason *"an item-numbered table alone"* is never-alone. |
| `Check-out report - 14 Oakfield Rd.pdf` *(kept)* | A located, photographed, costed fault list. `construction_property.inventory-inspection`'s, and that row states the line itself: *"defects to be RECTIFIED by a builder, with a close-out column, supports the snagging row; condition recorded to be compared later, with no expectation of rectification, supports this row."* Adopted, not re-authored. |
| `Practical completion certificate - Oakfield.pdf` *(kept, and re-read this pass)* | **The gist memo left this deliberately ambiguous; the ambiguity is now resolved against this row.** The certificate is the boundary event and belongs to `construction_property.construction-project`, which says so in its own words. This row claims the **outstanding-works schedule appended to it**, not the certificate. |
| `Snagging schedule - Block C - rev 2.xlsx` *(added this pass)* | Not rejected — **added**, because the spine names it as the shared fixture on its own side and this row was not carrying it. It is this row's, and the head-contract reference on the sheet is the project row's context, not its claim. |
| `Reactive repairs log - Marsh Court - 2026.xlsx` *(added this pass — the third collision fixture)* | Every structural signal this row has is satisfied and it is still not this situation. See below. |
| `Snag list - our new house.xlsx` *(added this pass — the outbound collision fixture)* | A householder's own list of their own home. See below. |
| `IMG_2231.HEIC` *(added this pass)* | `progress-photos`' own bytes. Capture metadata is not this row's evidence. |
| **Operating and maintenance manuals, building manuals** | *(Preserved from the gist memo; still right.)* Handover material, but **reference documentation, not a fault tracker.** They ride in the same pack and share the same folder; they have no items, no statuses and nothing to close. The pack itself is the spine's *completion-and-handover envelope*, which the spine kept as one of its four surviving structures. |
| **A maintenance work order / planned-maintenance schedule** | `manufacturing.maintenance-work-order`. The gist memo named the defects-versus-maintenance separation in `needs_llm` and gave it no edge; that gap is closed this pass. Discriminator: **an obligation that expires** versus an upkeep regime that does not. |
| **A block manager's reactive repairs log** | `construction_property.block-management`. Same table, no closing obligation. New edge this pass. |
| **A homeowner's own snag list of their own new house** | `finance.household-property`, absent an instruction. **This reverses a gist no-edge call** — see the reversal below. |
| **A CIS return, a site payroll run, an operative's timesheet** | `finance`, `hr`, and the family's own `timesheet` **refusal**, which routed dayworks to `variation-claim` and attendance to `site-health-safety`. A defect register names trades; that does not make employment paperwork this row's, and contradicting a landed refusal would be the worse error. |
| **A fire-door inspection register / condition survey** | `construction_property.site-survey`. A located, statused, item-numbered table — and its purpose is to **record condition**, not to compel rectification under a contract. This is the closest structural near-miss in the family and it is why the location column alone was disqualified this pass. |
| **A construction-defects textbook chapter, a guidance note on rectification periods** | Reading Inbox — *"papers, articles, reports, and saved PDFs that appear to be reading material but have no active research, course, or project association."* Full vocabulary overlap, zero evidence overlap. |
| **A `.zip` snagging-platform export** | Kept as a fixture and **not opened**: *"the normal scan should never extract archive contents to the filesystem."* Membership in it proves nothing about a member — and membership in a download session proves less still: *"A session should never be treated as proof of topic"*. |
| **An insurance claim photograph of water damage** | `finance` / an insurance row. Identical bytes to a defect close-up. Discriminator: a policy number and a claim reference against an item number and a register. Not given an edge — the confusion is at fixture level and `never_alone`'s *"an annotated photograph alone"* already carries it. |

---

## The collision fixture — in both directions, as the addendum requires

**Inbound (a file that would wrongly fire this row): `Reactive repairs log - Marsh Court - 2026.xlsx`.**

It satisfies **every structural signal this row has**: one row per fault, a flat number in a location
column, a contractor in a responsible-party column, a status column, dates raised and attended, and a
sheet re-issued as a version family. On the leg-1 test as stated it fires cleanly.

**And it is not this situation, because nothing in it closes.** There is no completion date, no
defects period with an end, no retention, no making-good certificate. It is a perpetual upkeep log
kept under a standing management appointment, which is `construction_property.block-management`'s.
**The discriminator is the expiring obligation, not the table** — which is the `timesheet` refusal's
lesson (*"a shared table shape is not a situation"*) turned around and applied in this row's favour
rather than against it. This fixture is the reason leg 1 had to be argued as a *structure plus a
running period* rather than a structure alone.

**Outbound (a file that must not be lost *to* this row): `Snag list - our new house.xlsx`.**

A buyer's own room-by-room list of faults in the house they have just bought, with a status column
they keep themselves. It is a defect register by structure and it belongs to the landed
`finance.household-property` row, which claims a householder's own record of their own home and lists
inspection, warranty and completion certificates among its own `work_types`. The schema anchor's seam
is **INSTRUCTION** and this pass applies it rather than re-drawing it: a job or contract reference, a
responsible-trade column, a defects period running under a contract and a re-inspection history
support this row; an owner's own file with no instruction around it supports the landed row. **An
address selects neither.**

**A third fixture runs across a seam this row shares with its spine:**
`Snagging schedule - Block C - rev 2.xlsx` carries a **head-contract reference**. This row owns it —
the spine conceded — and this row still may not read the contract reference as its own evidence, nor
write a job fact onto a photograph that merely shares the folder. *"The graph does not automatically
copy those missing facts onto sparse files."* Owning a situation is not a licence to extract a fact.

**The same bytes are named on both sides** in every case — the block log runs inbound from
`block-management`, the buyer's list outbound to `finance.household-property`, the Block C schedule
across the spine seam, and `IMG_2231.HEIC` across the `progress-photos` seam — which is what makes
the reciprocals checkable rather than asserted.

---

## Reciprocal boundaries, both directions

Every entry was read on the neighbour's side **first**. Where a neighbour had already stated the
line, its wording is adopted rather than re-authored, and no line is contradicted.

| Neighbour | This row must not take | The neighbour must not take | Shared fixture |
|---|---|---|---|
| `construction_property.variation-claim` *(states its side; identical words on both)* | numbered instructions, quantified cost-and-time consequences, approvals and notices, claim bundles | a location, a responsible trade, a status column, a re-inspection history | `VO-017 - upgrade to kitchen worktop.pdf` — genuinely both where both sets are present, and **abstention is the outcome** |
| `construction_property.construction-project` *(states its side; concedes this row)* | anything inside the construction period, and **the practical-completion certificate itself** | defects-liability-period activity, re-issue sequences with status columns, anything after practical completion | `Snagging schedule - Block C - rev 2.xlsx` |
| `construction_property.progress-photos` *(states its side)* | a site walk's captures, capture rhythm, a GPS cluster — **this row has no capture-based claim at all** | a defect close-up that carries a marker, a caption identifying a fault, or membership in an accepted defect list | `IMG_2231.HEIC`; `Snag 044 - kitchen.jpg` |
| `construction_property.inventory-inspection` *(states its side)* | a tenancy, a tenant, a deposit reference, a check-in comparison, condition recorded for later comparison | defects to be rectified by a builder, with a close-out column | `Check-out report - 14 Oakfield Rd.pdf` |
| `construction_property.block-management` **(new this pass)** | a standing management appointment, leaseholder reporting, apportionment, a service-charge year, a perpetual log | a defects period with an end date, a retention release, a making-good certificate | `Reactive repairs log - Marsh Court - 2026.xlsx` |
| `finance.household-property` **(new this pass; landed row, one-way)** | a householder's own record of their own home with no instruction around it | a professional's instructed defects register because the property is a house | `Snag list - our new house.xlsx` |
| `construction_property.final-account` | a valuation number, a retention percentage, a certified sum, the reconciliation | an item list with statuses, because retention is released against it | a retention-release statement citing a de-snag confirmation |
| `construction_property.survey-valuation` | condition ratings, a basis of valuation, a reliance clause | an item-numbered, located, statused list intended to be worked through | `Defects report - 14 Oakfield Rd - independent inspection.pdf` |
| `business_operations.project-delivery` | a component, an assignee, a sprint or milestone — the generic issue log | a physical place inside a building and a responsible trade | `Sprint 14 bug export.csv` |
| `manufacturing.nonconformance-capa` | a part or batch number, a specification clause, a corrective-action methodology | a room, a plot and a trade | a non-conformance register |
| `manufacturing.warranty-claim` | a product serial number, a manufacturer, a warranty policy | a plot, a trade, a contractual defects period | a latent-defect claim on an installed product |
| `manufacturing.maintenance-work-order` **(new this pass)** | an asset identifier, a planned-maintenance schedule, a meter reading, a fault code | a plot or room, a responsible trade, an expiring defects period | a work order against a building service |
| `construction_property.subcontract` *(states its side)* | the enquiry, order, competence evidence and payment cycle of engaging another firm | the defect items that firm has to come back and fix | a back-charge notice against a subcontractor |

The three rows marked *(states its side)* had already authored their halves; those halves are
reproduced above unchanged. **`finance.household-property` landed before this family and does not
name `construction_property` in its own memo — R1c owes that reciprocal**, and the fixture bytes are
named here so it can be checked rather than asserted. `manufacturing.*` rows exist on the roster but
are not yet written; those three seams are authored **one-way** and R1c owes those reciprocals too.

---

## Neighbours considered that did **not** get an edge

*(The first three are preserved from the gist memo, re-tested this pass, and still right. The fourth
is new.)*

- **`hr.employee-relations`** — a defect register naming a repeatedly-responsible tradesperson has a
  real employment consequence. **No edge:** no shared evidence item exists at the document level, and
  the edge would record a *consequence*, not a confusion. This is also the boundary the `timesheet`
  refusal already polices from the other direction, and contradicting it would invalidate a landed
  refusal.
- **`legal.personal-legal-matters`** — a defects dispute becomes one eventually. Topical, not
  evidential. What *is* real is co-activation on the same bytes once a notice or a pre-action letter
  exists, and that is now expressed as `also_holds_with: legal` (schema ↔ schema, per CONNECTION §5)
  rather than as a template-level collision.
- **`government.*`** — a building-control notice about defective work is an authority record;
  `construction_property.building-control` already states the government boundary from the
  applicant's side, and routing it twice would be duplicate authorship.
- **`construction_property.site-diary`** *(new consideration this pass)* — a diary entry records a
  fault being found. **No edge:** the diary is a dated daily record and this row is a tracked list;
  the diary entry is a *citation* of a defect, and citation is not a fact writer. The spine already
  polices this seam from the diary's side.

---

## `also_holds_with` — three co-holdings, and why they are not collisions

New this pass; the gist row had none. CONNECTION §5 makes `also_holds_with` **schema ↔ schema only**,
so all three name schemas, not sibling templates. `00` licenses the mechanism: *"One file may hold
facts from more than one domain without losing information."*

- **`legal`** — a defect notification served under a contract, a latent-defect claim, a pre-action
  letter. Legal is a safety domain (*"Finance, identity, medical, and legal material should be
  implemented first as safety domains"*), so **protective ordering applies**: the legal reading
  protects first and this row's reading is additive.
- **`photos`** — an annotated defect photograph carries the `photos` schema's capture facts as well
  as being a register member. Stated only as co-holding; the capture *situation* is
  `progress-photos`' and is not reopened.
- **`finance`** — a close-out confirmation releases retention, so it is a finance record for
  whoever's books it lands in and this row's evidence that the list is finished. The narrower
  competition with `construction_property.final-account` stays a collision and is recorded there.

---

## Sparse-file discipline

Nine of the fourteen fixtures carry `group_without_copying_facts: true`, and this row needs the rule
badly: a defect photograph with `Snag 044` in the filename and nothing else, an unopened `.zip`
export, an app screenshot with no OCR yet, a three-line fault email with no register around it. In
every case the neighbourhood may legitimately group the file while **no** plot, phase or job fact is
written onto it. *"The graph does not automatically copy those missing facts onto sparse files."*

Every fixture also carries *"any construction_property fact — the schema declares no field rows"* in
its `must_not_conclude`, so the placeholder status is checkable file-by-file and not only in the
header.

The one grouping this row is proudest of is also the one that needs the rule most: **one defect** —
the notification, the photographs, the trade's response, the re-inspection and the sign-off. Its
members share no content whatever. *"The documents are content-incoherent but purpose-coherent."*
And the stop rules hold against the obvious abuse: *"when members carry irreconcilable course,
institution, project, term, or purpose facts"* — two plots' registers in one folder do not merge.

---

## `proposed_fields` — the full list

**None, and deliberately so.** The schema declares no field rows (D1 as narrowed, `_CONTRACT` rules
10 and 15, PR-6), and this row proposes no key of its own. It relies entirely on the schema row's two
proposals — `property` (NJ-CP-1) and `instruction`, with `project` reuse offered as the live
alternative (NJ-CP-2) — and on `organization`, which the schema row explicitly defers to
`business_operations`. **This row seconds all three rather than minting variants**, which is the
brief's instruction and D6's whole purpose. `00` is explicit: *"The system may create new values when
it sees a new course, project, company, university, or event, but it should not invent new fields
automatically."*

**One further candidate is named and NOT minted, with its argument, for R1c.** This row wants a
**plot-or-unit** level more than any other row in the family: item 44 exists on every plot on a
development and is unintelligible without one. The honest position is that this is a **sub-division
of `property`**, not a fourth key — so the right adjudication is *does `property` permit a sub-unit?* under NJ-CP-1, **not** a new `plot` key. Minting `plot` beside `property` would be the
near-duplicate defect D6 exists to kill, and minting it while the schema row's own `property`
proposal is unresolved would be minting at the exact moment of maximum convenience — the 574's
original mistake performed knowingly. A **defect-phase** key was also considered and rejected on the
same reasoning: pre-completion / handover / defects-period are **values of `work_type`**, and the
schema anchor names `snagging` itself among the values it warns siblings not to promote.

`proposed_context_terms` (30 entries) is preserved unchanged. These are **proposals**, not `00`'s
floor — `00`'s named context-term floor is the academic one, and this row does not pretend otherwise.

---

## Audits run before returning

- `python3 -m json.tool` on the node → **parses**.
- **Key set compared programmatically against `construction_property.construction-project.json`** (a
  deepened sibling) → **empty symmetric difference**, 27 keys.
- **Every quoted span in the JSON verified verbatim against `00-database-agent-product-design.md`**
  by exact substring match → **25 spans, zero failures**. The two sibling-sourced quotations in the
  JSON are set in single curly quotes, not double, so the `00`-quotation audit stays mechanical.
- **Every quoted span in this memo resolved to a named source**, whitespace-normalised, → **45 spans,
  zero unresolved**: the `00` design doc, `ALIGNMENT.md`, the schema anchor, the deepened spine's
  memo and JSON, `inventory-inspection.json`, `progress-photos.json`, and this row's own JSON. Every
  span attributed to `00` in the prose above resolves to `00`; no sibling's words are presented as
  design authority. Two notes for the next author: `00` uses a **curly apostrophe** in *"the
  product’s goal"* and `ALIGNMENT.md` in *"schema’s"* — the straight-quote forms return zero and are
  fabricated quotes.
- **Every `file_examples.source_type` is in P5's `SOURCE_TYPES`** → clean (14 fixtures; the four new
  ones use `spreadsheet` ×3 and `image`).
- **Every `falls_through_to` and `falls_through_if_inactive` is one of the nine residual names**,
  spelled `00`'s way → clean.
- **Every `collides_with` and `also_holds_with` target resolved against `roster.json`
  `nodes[].domain_id`** → clean (12 collisions, 3 co-holdings; `manufacturing.maintenance-work-order`,
  `construction_property.block-management`, `finance.household-property` and
  `construction_property.progress-photos` all confirmed present).
- `fields: []`, `proposed_fields: []`, `dimension_order: []`, `launch: "placeholder"`,
  `refuse_node: false`; **no canonical key minted, no threshold, statistic, file count or P7 handling
  class anywhere.**
- **Files written: exactly two** — `planning/domains/nodes/construction_property.snagging-defects.json`
  and this memo. No roster edit, no sibling row, no `src/`, no `check.py`.

---

## What was preserved, what was added

**Preserved unchanged** (verified this pass, not rewritten): the entire `recognition.deterministic`
block including its precondition entry and all nine signals; the seven `needs_llm` entries; the ten
original `never_alone` entries; `proposed_context_terms`; `work_types`; the five original
`grouping_reasons`; `template.why` and its prose recommendation, and `time_first: false`;
`file_kinds`; all eight original `collides_with` entries; all six `falls_through_to` entries;
`role_split` (empty); `sensitivity` and `sensitivity_why`; the ten original `file_examples` with
their `observations` and `must_not_conclude` lists; the `proposed_fields` position; and the gist
memo's four rejections and three no-edge calls, all four and all three re-tested and reproduced above
with attribution.

**Narrowed, explicitly** (stated rather than performed silently): the gist memo's node-test argument
claimed three differences. **Two of them are not legs of CONNECTION §2's test and are withdrawn as
arguments** — *lifecycle* is demoted to corroboration for leg 1, and *version behaviour* is demoted
out of the node argument entirely, on the ground that `duplicate_family` and `version_family` are
universal facts and carrying more of a universal is not a different detection signal. The verdict
(node, not refused) stands; its grounds are now **one leg, not three**, and legs 2 and 3 are recorded
as **failing**. Two signal readings were also tightened against this row's interest: a stated
defects-liability period is now never-alone (only a *running* one is evidence), and a location column
alone is now never-alone.

**Reversed, explicitly:** the gist memo's no-edge call on **`finance.household-property`** — it
argued that no evidence item is shared, and a buyer's own snagging list of their own new house is a
shared evidence item and the family's own seam runs straight through it. A reciprocal
`collides_with` entry and the outbound collision fixture were added. The gist memo's deliberate
ambiguity about the **practical-completion certificate** is also resolved, against this row, in
favour of the spine's stated position.

**Added this pass:** three `never_alone` entries (the `progress-photos` non-contradiction, the
location column, the stated-versus-running defects period); four reciprocal `collides_with` entries
(`progress-photos`, `finance.household-property`, `block-management`,
`manufacturing.maintenance-work-order`) and a rewritten `construction-project` entry recording the
spine's concession in its own words; three `also_holds_with` entries where the gist row had none;
four fixtures, including the **inbound and outbound collision fixtures** and the spine's shared
fixture, which this row was not carrying; a browse-versus-activation note in `grouping_reasons`; a
second `open_question` recording the single-leg verdict; a corrected `one_line` that states the row's
grounds and its limits instead of announcing gist depth; and this memo, replacing the 4.3KB gist
note — with the node test argued leg by leg (two legs recorded as failing), the account of the
spine's concession, the `compliance-certificate` and `timesheet` re-runs, the `progress-photos`
section, the rejected-files table, the reciprocal boundary table and the two-way collision fixture.

The `Depth: GIST` header is removed; the label is retired.

**A note on what this row genuinely has less of.** It stands on **one** structure and one leg,
where the schema anchor stands on four structures and three legs; its dimensions and privacy posture
are borrowed from its schema and contribute nothing; and it proposes no field of its own. The length
above is boundary work — twelve neighbours, four collision fixtures, two refusals re-run — not
argument for the row itself, which is short by design: a defect register is a fifth table shape the
family does not otherwise have, and that single fact is the whole case. Its strongest support was
written by the row it was suspected of being a `work_type` of.

---

## NEEDS-JOSEPH (this node only)

- **NJ-CP-SNAG-1 · Defect or variation.** *(Preserved from the gist memo; stated reciprocally with
  `construction_property.variation-claim` in the same words on both rows, and re-verified this pass
  against that row's own memo.)* The same item is a defect on one party's paper and a paid variation
  on the other's, in good faith on both sides. The product should recognise both and abstain:
  *"conflicting signals should lead to abstention rather than an invented classification"*.
  **Alternatives and costs:** *(a) offer a genuinely-both file in two places* — honest, and matches
  the abstention rule; costs a user seeing the same file twice with no explanation of why. *(b) hold
  it in one place with both readings recorded* — tidier tree; costs the loss of the fact that the
  disagreement is the point, which is the single most consequential thing about the file. **This
  row's recommendation, offered not taken: (a).**
- **NJ-CP-SNAG-2 · Residential defect files and the occupant.** *(Preserved.)* A snagging file for
  someone's home is a catalogue of what is wrong with where they live, and the exposed party is
  usually not the holder. This row routes those members protectively (`Protected Records`); whether
  that is strong enough is a privacy decision about real people rather than an evidence question, and
  it is the same gap the schema row files as NJ-CP-4 for third-party personal material generally.
  **They should be answered together.**
- **NJ-CP-SNAG-3 · Named tradespeople recorded as responsible for failures.** *New this pass.* A
  defect register attributes failures to individuals by trade and often by name. This pass **declined
  to claim a stricter privacy posture on it**, because doing so would have manufactured a passing
  leg 3 the row does not need. **Alternatives and costs:** *(a) leave it at the schema default* —
  what this pass did; costs nothing now, and leaves a real attribution risk unremarked. *(b) treat
  attributed-failure material as a stricter class* — principled; costs a posture divergence from the
  schema that only `site-health-safety` currently has, and it would need a rule that distinguishes a
  trade from a person, which R2 owns and this row does not write.
- **NJ-CP-SNAG-4 · Is one passing leg enough on a field-less schema?** *New this pass, and it is the
  question the narrowing creates.* This row passes leg 1 and fails legs 2 and 3, exactly as the
  deepened spine does. The schema anchor's own closing question names this row by id among those that
  *"may then be `work_type` values on a sibling rather than rows of their own."* **Alternatives and
  costs:** *(a) keep it* — the defect register is a fifth structure the family does not otherwise
  have, no sibling claims it, and the spine has formally conceded it; costs a row whose entire
  existence rests on one table shape plus a running period. *(b) fold it into
  `construction-project`* — **now blocked from the other side**: the spine has demoted these signals
  out of its own activation evidence, so folding would require reversing a landed reversal, and the
  post-completion material would sit in a container whose lifecycle has ended. *(c) refuse and route
  to residuals* — `Review Later` and `Independent Records` would hold the material honestly, and the
  cost is that the most re-issued, most version-heavy document family in the schema gets no template
  at all. **This row's recommendation, offered not taken: (a).**
- **Inherits NJ-CP-1 and NJ-CP-2** from the schema row. Without a `property` key — and without an
  answer to whether it permits a plot-or-unit sub-division — this row's recommended order exists only
  as prose, and its leg 2 is unavailable in the JSON at all.
