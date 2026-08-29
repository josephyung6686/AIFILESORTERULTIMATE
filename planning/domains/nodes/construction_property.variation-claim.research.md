# construction_property.variation-claim — research notes

Depth: J-DEPTH. Placeholder row (J-IND, deepened under the 2026-08-24 ratification). Absorbs legacy
id `cons.variation-claim` (ROSTER.md Appendix A).

**Verdict: kept, not refused** — but on a narrower base than the gist row claimed, and with one of
its three node-test legs conceded away. The three charges the dispatch put are answered one at a
time below, and the second of them (`work_type` of the spine) is answered largely by evidence this
row did not generate.

**Status of this pass.** The row was written once under the retired `Depth: GIST` label. It was a
verified-but-shallow draft: the JSON key set was house-correct, its quotations were machine-verified,
and its arguments were sound. This pass **deepened rather than rewrote**. See *What changed in this
pass* at the end, which is written to be checkable against the JSON line by line.

---

## Sources actually used

### Binding local sources

- `planning/00-database-agent-product-design.md` — the only document quoted as design authority.
  Every `“…”` span in the node file was re-verified with `grep -F` this pass (see **Audits**). The
  spans that do real work here:
  - the purpose paragraph, which is this row's constitutional text and which the gist pass used only
    for its most famous sentence: *"Purpose must be a first-class facet."*, *"The documents are
    content-incoherent but purpose-coherent."*, *"Purpose may be supported strongly by an existing
    user-created folder name or explicit language in a form or portal."*, and the sentence that
    disqualifies the folder from doing more than that: *"It is a purpose clue and a review aid, not a
    basis for automatic semantic propagation."*
  - the purpose-packet procedure, **new to this pass and the most important addition in it** — 00
    asks *"whether the files plausibly serve one shared workflow, whether the group is
    purpose-coherent despite topic diversity, which members appear to be supporting materials rather
    than unrelated records, and whether any member conflicts with the proposed purpose"*. That last
    clause is the mechanism the gist memo said did not exist. See *The bundle problem, narrowed*.
  - the abstention apparatus, which this row leans on harder than any sibling because its central
    determination is genuinely undecidable: *"conflicting signals should lead to abstention rather
    than an invented classification"*, *"Conflicting evidence should actively suppress nodes."*, the
    two-condition acceptance rule — *"the best legal destination must reach a minimum support
    threshold and must exceed the next-best destination by a meaningful margin"* — and
    *"Correct abstention is a successful outcome because the product’s goal is reliable organization,
    not maximum file movement."*
  - the table sentence, which licenses reading this row's two fingerprint tables:
    *"Tables matter because resumes, forms, applications, invoices, and administrative documents
    often place their most useful information in cells rather than body paragraphs."*
  - the sparse-file rule, which is the whole of this row's grouping discipline: *"The graph does not
    automatically copy those missing facts onto sparse files."*
  - the email extractor sentence, which is why the unlabelled go-ahead email is a legitimate fixture
    rather than a rhetorical one: *"Email formats such as EML, MBOX, MSG, and exported mail archives
    should yield sender, recipients, subject, sent date, thread identifiers, message body, attachment
    names, and reply-chain context, while treating addresses and message content as potentially
    sensitive."*
  - the safety-domain sentence, which decides the `legal` seam: *"Finance, identity, medical, and
    legal material should be implemented first as safety domains"*, with *"One file may hold facts
    from more than one domain without losing information."*
  - the dimension-order rule and its recommendation clause, and the residual-library definitions for
    all six `falls_through_to` entries.
- `planning/domains/CONNECTION.md` — §2 node test, §3 activation ≠ grouping and the browse-only
  parent, §4 step 2 (never-alone) and step 9 (the grouping firewall), §5 closed edges and invariant 2,
  §9 failure mode 2 (work types as nodes), PR-6.
- `planning/domains/_CONTRACT.md` — rules 1–3, 5, 6, 8, 10, 11–15.
- `planning/prompts/ALIGNMENT.md` — *"would only repeat its schema's fields and dimension_order"* …
  *"it is the schema's default template."*
- `planning/domains/canonical_fields.json` — checked. **Nothing holds a change, a variation, a claim,
  a notice, or a contract.** No key minted; three existing proposals seconded instead.
- `planning/overnight/council/DECISION-BRIEF.md` — D1 (as narrowed), D6, PR-6, J-IND taken as ratified.
- `planning/domains/roster.json` — every edge id confirmed to exist (audit below).

### Neighbour files read in full before writing, and not rewritten

- **`construction_property.research.md`** (the deepened schema anchor, 43KB) — read first, as the
  addendum requires. Its default template and its four default detection structures are what this
  row's node test is measured against, and they are quoted below so the comparison is checkable.
- **`construction_property.construction-project.json` + memo** (the spine, 45KB/38KB) — the row this
  charge (b) says this one is a `work_type` of. It conceded the numbered instruction to this row in
  its own deepening pass. Its wording is adopted, not re-authored.
- **`construction_property.timesheet.json` + memo** (a landed REFUSAL) — read in full because its
  routing depends on this row. See *The load this row is carrying for a refusal*.
- **`construction_property.snagging-defects.json` + memo** (52KB, deepened) — the load-bearing
  collision, and the sibling that was tested as a `work_type` of the spine exactly as this row is.
  Its answer is studied below and one of its cautions is adopted verbatim in substance.
- **`construction_property.final-account.json`**, **`.quote-estimate.json`**,
  **`.site-diary.json`**, **`.subcontract.json` + memo**, **`.materials-delivery.json`**,
  **`.drawings-revisions.research.md`**, **`.site-health-safety.research.md`** — all read for the
  seams they state on their side. Where a neighbour had already stated a line, its wording is
  adopted unchanged.
- `business_operations.organisational-records.json` — the refusal standard, read because refusing was
  a live possibility here until leg 1 held.

### A source that does not exist, and it matters

`00` **never names this world.** Its template-library sentence lists *"academic programs, university
applications, recruiting processes, client engagements, research workflows, financial records,
travel, legal matters, creative projects, software repositories, personal administration, and photo
collections"* — construction is absent. So `design_cite` is `null`, `provenance` is `proposal`, and
every `collides_with` entry is marked `provenance: inference`. `00` supplies the machinery; this
family supplies the situation. No quotation below is offered as design authority for the situation.

---

## What this row is, in one paragraph

Everything else in this family records **what was agreed, built, delivered or paid**. This row
records **the argument about what changed and who bears it**. Two properties follow from that and
nothing else in the catalogue has both. First it is **notice-bound**: contracts create rights that
die if the paper is late, so a document here is often written for no reason except to exist before a
deadline, and it says so on its own face. Second it is **adversarial and prospective**: the file is
made now to be produced later against a named opponent, which means its author is writing for a
reader who will attack it. Those two properties are what produce the row's tables, its privacy
posture, and its defining artefact — the bundle of otherwise unrelated files held together by one
argument.

---

## The three charges the dispatch put

### Charge (b), taken first because the others depend on it: "a `work_type` value inside `construction-project`'s lifecycle"

This is the strongest charge and it is **answered from the other side of the seam**, which is the
only form of evidence in this system that cannot be self-serving.

The spine was deepened after this row's gist pass, and in that pass it **demoted five of its own
eight structural detection signals** and conceded them to the siblings that own them. One of the
five is this row's. In the spine's own memo:

> *"Similarly `variation-claim` owns the numbered instruction, `site-diary` owns the dated daily
> record, and `subcontract` owns the works package. The gist row claimed all of them."*

And in the spine's JSON, in the entry that names this row:

> *"The instruction is intelligible only above the job, and that tempts this row to claim it. It must
> not. The discriminating evidence: a numbered instruction, a confirmation of verbal instruction, an
> extension-of-time or loss-and-expense submission and the dispute bundle they become support the
> sibling; the contract they vary supports this row."*

The spine also demoted the general principle into a `never_alone` on itself: **being the parent
DIMENSION of a document is not activation on it.** A variation browses under its job; the row that
owns the variation activates.

**But the concession settles less than it looks like it settles, and this row will not pretend
otherwise.** `snagging-defects` made exactly this point when it received the same concession, and
its caution is adopted here: a concession establishes *which of two rows owns a structure*; it does
not establish that the structure earns a row at all. **Both rows could be wrong together.** So the
node test below is run on this row's own merits against the schema anchor's default template, as if
the concession had never happened. The concession is corroboration in the argument's margin, not a
leg of it.

### Charge (a): "a `work_type` value inside the lifecycle" — the general form

The schema anchor states the family rule in the single sentence it calls the most important one for
a sibling author:

> *`variation`, `snagging`, `dilapidations`, `retention`, `preliminaries`, `certificate`, `drawing`,
> `schedule`, `survey`, `valuation` and `report` are **values of `work_type`**, not rows.*

**`variation` is named on that list, first.** This row is therefore under the family's own
explicit suspicion and it has to clear a bar the anchor set against it by name. The clearing argument
is not that `variation` is a special word — it is that this row's node claim is **not** about the word
`variation` at all. The word appears in the row's title for want of a better one. What the row claims
is the **notice-bound adversarial situation**, of which a variation order is one member and an
early-warning notice, an extension-of-time submission, a Scott schedule and an adjudication bundle
are others — and those last four are not `work_type` values of anything else in this family. A row
whose membership is exhausted by one `work_type` value would fail; this row's membership is a
*purpose*, and 00 is explicit that purpose is a different axis from type: *"Topic answers what a file
is about, while purpose answers what the file was for."*

### Charge (c): "its content splits between `quote-estimate` (pricing) and `final-account` (settlement), leaving nothing of its own"

This is the sharpest charge and it is the one that would have refused the row. It is answered by
**taking the split seriously and seeing what is left standing.**

- **The pricing half genuinely does look like `quote-estimate`.** A variation quotation is a priced
  schedule with quantities, rates, a validity period and an acceptance line — that row's structure
  exactly. But that row states its own anchor, and its anchor excludes this: its situation is a
  **PROSPECT**, *"at the moment a quote is written there is no job, no contract and no job number to
  file it under, and most quotes never acquire one."* A variation quotation has a job, a contract and
  an instruction number above it. It is an adjustment to an agreed sum, not an offer to form one.
  The split fails on that row's own stated boundary.
- **The settlement half genuinely does look like `final-account`.** But that row also states its own
  side, and states it as a boundary rather than a takeover: *"an instruction number with a narrative
  of entitlement, a contractual clause cited and a cause-and-effect argument supports the variation
  row; the reconciliation of the whole contract sum with amounts already certified supports this
  row."* The boundary is **agreement**. A final account is what a settled change becomes. A change
  that is refused, disputed, adjudicated or abandoned never reaches an account at all — and those
  are the majority of this row's files.
- **What is left after both halves are removed is not a residue; it is the row.** The instruction
  itself, the confirmation of verbal instruction, the RFI whose answer changed the works, the
  early-warning notice, the delay notification, the extension-of-time submission with its programme
  analysis, the loss-and-expense build-up, the Scott schedule, the without-prejudice offer, the
  adjudication referral, and the bundle. **None of those is a price and none is a settlement.** The
  charge assumed this row is about money. It is about **entitlement**, and money is one of two
  currencies it deals in — the other is **time**, which neither `quote-estimate` nor `final-account`
  handles at all.

That last observation is what converts the charge into leg 1's strongest evidence: the pairing of a
money column with a **time-effect** column is the thing no sibling table has.

---

## The node test, all three legs, argued

CONNECTION.md §2: a template row exists only when its **detection signals**, its **recommended
dimensions**, or its **privacy rules** differ from its schema's default template. Any one leg
suffices. The gist memo answered all three with a verdict per leg; this pass argues them, and one of
the three **does not survive**.

The default template, quoted from the deepened schema anchor so the comparison is checkable:

> **`property` or site → `instruction` (the job, the letting, the scheme, the block) → document
> function**, with a period level only where the situation *genuinely cycles*. **Not time-first.**

And the anchor's four default detection structures, which are what a sibling's leg 1 must **add to**:
the **title block**, the **measured-works table**, the **`to date, less previously certified`
valuation arithmetic**, and the **apportionment schedule**.

### Leg 1 — detection signals of its own. **PASSES. This is the row.**

Four candidate structures, each tested against the anchor's four rather than asserted.

**(i) The variation register: money beside TIME-EFFECT beside DISPUTE STATUS.** A table whose columns
read variation number, description, originating instruction or RFI, a quoted or agreed value, **a
time effect in days**, a status (submitted, agreed, disputed, rejected) and a date, with running
totals of agreed and disputed sums at the foot.

Tested against the anchor's four: it is not a title block (no sheet border, no revision designator);
not a measured-works table (its rows are *changes*, not described works with quantities and rates);
not a valuation (no cumulative arithmetic, no previously-certified subtraction); not an apportionment
schedule (its rows are changes, not units bearing a percentage share). Tested against the sibling
tables: a snagging register has location and trade and **no money and no time**; a final account has
additions and omissions and **no dispute status**; a risk register has likelihood and mitigation and
**no agreed value**. The *triple* is the fingerprint.

**This pass added the disqualification the gist row omitted.** The gist memo named the triple as a
fingerprint without disqualifying its parts, and a fingerprint whose parts are not disqualified is an
assertion, not a signal. A **status column alone** is now `never_alone` in the JSON: it is the most
generic vocabulary in the catalogue and it appears identically on a snagging list, an issue log, an
RFI tracker, a risk register and a support queue. A currency figure alone and a numbered reference
alone were already disqualified. All three parts are now individually worthless and only the triple
counts.

**(ii) The self-timing notice.** A dated letter or form citing a clause, stating an event, and
**asserting its own timeliness** — served within a stated number of days of becoming aware. This is
the strongest single signal in the row and it survives every test this pass could put to it: a
document that argues about *when it was written* exists because a right dies if it is late, and
nothing else in the catalogue writes that sentence. It is marked as inference; 00 names no such
document, and the claim is that no other structure in *this catalogue* competes, not that none exists
in the world.

**(iii) The Scott schedule — added this pass.** One row per disputed item; a column for the claimant's
case; a column for the respondent's case; **a third column headed for the adjudicator and left
empty.** Every other table in this catalogue is written by one side for its own purposes. A table
that *reserves a column for a third party who has not decided yet* is structurally unlike all of
them, and it is the clearest possible expression of what this row is: a document made now to be
handed to someone who will judge it later. The gist row had the term in `proposed_context_terms` and
never turned it into a signal.

**(iv) The daywork sheet — added this pass, and it was a genuine hole.** See the next section.

**Verdict on leg 1: passes**, and it would pass on (ii) and (iii) even if (i) were given away.

### Leg 2 — recommended dimensions of its own. **PASSES, but narrowly, and it is conditional.**

The recommendation, held as prose because `template.dimension_order` is empty by binding contract
(a dimension may only branch on a field its schema declares, and this schema declares none):

> the contract or job → **the change or claim itself, as its own container** → the document function
> inside it (origin, quotation, notice, submission, response, outcome).

The middle level is the difference from the default. The anchor's default puts **document function**
directly under the instruction; this row inserts a level the default does not have, and the insertion
is **forced by the artefact rather than chosen for tidiness**: this row's defining object is a
*bundle* of files that share no content, held together by one argument. A function-first tree files
the notice with the notices, the diary extract with the diaries and the quotation with the
quotations — scattering precisely the files whose only relationship is the argument. That is a
different dimension recommendation from the default and it is CONNECTION.md §2's second ground.

**Two honest weaknesses, neither smoothed:**

1. **The anchor warns that a reversal earns nothing** — *"Reversing is not a difference that earns a
   node"*. This row is not claiming a reversal; it is claiming an **inserted level**. That is a
   different claim and it is the only reason this leg stands. If R1c reads an inserted level as a
   species of reordering, this leg falls and the row survives on leg 1 alone.
2. **No key holds the inserted level.** Neither the canonical fields nor any of the family's three
   proposals name *the change itself*. This row refuses to mint one — a construction-flavoured
   variant is the defect D6 exists to kill — so the recommendation cannot presently be built from a
   declared field even after D1's deferral lifts. Raised as open question (3) and as NJ-CP-VAR-3.

**Verdict on leg 2: passes, conditionally**, and the condition is recorded rather than hidden.

### Leg 3 — privacy rules of its own. **CONCEDED. This leg does not stand alone, and the gist row was too confident.**

The gist memo asserted this leg flatly. It does not survive scrutiny in the form it was given.

The schema's default posture is already `potentially_sensitive`, on three grounds the anchor states:
the material names a real person's home and who is in it; 00's corpus sentence names categories this
family carries as a matter of course; and the exposed party is usually not the user. This row's
material sits inside all three. **Setting the same catalogue value the schema already sets is not a
difference**, and the catalogue offers only `none` and `potentially_sensitive`, so there is no
stronger value to reach for. Handling classes are P7's and this row assigns none.

What is genuinely different is a matter of **kind of harm rather than degree**, and it is stated as
inference in `sensitivity_why`: the harm from exposing a without-prejudice offer or an internal
assessment of an opponent is **the loss of the claim itself**, not embarrassment or identity risk.
That is a real distinction and it is why the row's primary residual is Protected Records rather than
Independent Records. But it is a distinction the *catalogue cannot currently express*, and a
difference the schema has no vocabulary for is not yet a difference in the schema's rules.

**Verdict on leg 3: this row does not claim it.** It is recorded as a P7 input, not as a leg.

**Overall: kept, on leg 1 cleanly and leg 2 conditionally.** The gist row's three-of-three is
**reversed to two-of-three**, and the reversal is stated here because the addendum requires that a
disagreement be argued rather than performed silently.

---

## The load this row is carrying for a refusal

`construction_property.timesheet` is a **landed refusal**, and part of its reasoning is a routing
into this row. In its own words:

> *"A SIGNED DAYWORK SHEET, countersigned by the client's agent, is contractual evidence that extra
> work was done at cost — its purpose is to be produced in support of a change, which is
> construction_property.variation-claim's situation."*

**The gist row could not hold it.** The word `dayworks` appeared in `proposed_context_terms` and
nowhere else: no signal, no fixture, no `work_type` value. A refusal was routing coverage to a row
that had not written down how to recognise what it was being sent. That is now fixed, and it is the
most consequential repair in this pass:

- a **daywork-sheet structure** is a deterministic signal, and the signal is stated in the form the
  refusal itself implied: not "a table of hours" (which the refusal correctly disqualified as
  never-alone — *"a table of names against hours"* is equally a rota, a payroll import, a
  billable-hours export and a care-visit log) but **the countersignature by the other side together
  with a reference to a described extra.** The sheet is not a record of who worked; it is evidence
  tendered to someone who must pay.
- **`Daywork sheet 018 - signed by CA.pdf`** — the refusal's own fixture bytes, named identically on
  this row.
- a `work_type` value, marked as routed.
- a **`never_alone` on the countersignature alone**, because a signature from the other side also
  appears on a delivery note, a snagging sign-off, an induction register, a handover acceptance and a
  payment certificate.
- a `must_not_conclude` refusing **the pay reading** on that fixture. Hours against named individuals
  route to `hr.payroll-benefits-administration` and `finance.payroll-received` under a stricter
  posture, exactly as the refusal said. Taking the pay reading here would silently re-create the row
  that refusal killed, which is the one way this row could break a landed argument.

The refusal's routing now lands somewhere that can hold it. Had leg 1 failed, that routing would have
had to be re-pointed — see *If this row had refused* below, which states the consequence even though
it did not happen.

---

## Files considered and rejected

The brief's test: a row that only lists what it holds has not been researched. Named tempting false
positives, and the discriminator for each. The gist memo's four correct rejections are preserved with
attribution and the rest are new.

| File | Why it is **not** this row's evidence |
|---|---|
| `Change order 12 - line 3 guarding.pdf` *(gist; kept as fixture)* | Structurally identical — numbered, priced, time-affecting, approved. The anchors separate it: a machine, a line, a part number, a specification revision. `engineering.change-order`. |
| `Plot 14 snagging list rev 3.xlsx` *(gist; kept as the load-bearing fixture)* | A status-and-trade fault list with **no money and no time consequence** is `construction_property.snagging-defects`'. Reciprocated word-for-word on both rows. |
| A payment notice or pay-less notice *(gist)* | Notice-bound and adversarial, and rejected anyway: its anchor is a **payment cycle**, not a change to the works. `construction_property.subcontract` and `.final-account`. |
| A programme or Gantt chart *(gist)* | Appears here only as a claim appendix, and the appendix relationship must not transfer ownership. The spine owns the programme situation. |
| `Valuation 07 - application for payment.xlsx` *(new)* | The `to date, less previously certified` arithmetic is `final-account`'s, and it is one of the schema anchor's four **default** structures — so it could not distinguish this row even if it were unclaimed. |
| `Site diary 2026-03-14.pdf` *(gist; kept as fixture)* | The diary's own record, serving this row's purpose. Citation in a bundle index is not a fact writer. `construction_property.site-diary`. |
| A quotation for new works with a validity period *(new)* | `construction_property.quote-estimate`, on **its** stated anchor: a prospect with no job to file it under. See charge (c). |
| A delivery note recording a shortage *(new)* | `construction_property.materials-delivery`, adopting its own wording: the contemporaneous record of what arrived is its; the assertion of entitlement built on it is this row's. |
| A revised drawing sheet issued because of an instruction *(new)* | `construction_property.drawings-revisions`, in its words: *"that is an issue, and it is on the register"*. The sketch travelling **with** the instruction is the contested bytes. |
| An internal risk register with owners and likelihood columns *(new)* | `business_operations.risk-register`. The discriminator is **service**: a register is prudent, a notice is a condition precedent. Fixture kept on the other side of the line. |
| An insurance claim for the same storm, argued from the same photographs *(gist, in JSON)* | `finance.insurance-corporate`, a safety schema, whose protective ordering runs first. Policy number, insurer and loss adjuster versus contract clause and entitlement in days. |
| A public-sector variation under a procurement regime *(gist)* | Rejected as an edge. The discriminating evidence (a contracting authority, a published notice) already separates it through `business_operations.contract-administration`'s existing edge; duplicating it adds shelving, not evidence. |
| A warranty claim on an installed product *(gist)* | The word "claim" collides, the evidence does not. The collision that matters is captured on `construction_property.snagging-defects`. |
| A construction-law textbook chapter, an adjudication case summary, a published note on time bars *(new)* | Reading Inbox. **Complete vocabulary overlap, zero evidence overlap** — the clearest demonstration that this row is not detected by its nouns. |
| A blank standard-form notice template stamped with a contractor's PDF metadata *(new)* | Reference Clips. *"PDF metadata should be treated as supporting evidence, not as truth"* — one template stamps the same firm on every blank form it ever generated. |
| A CIS return, a site payroll run, an operative's hours *(new)* | `finance` and `hr`, per the `timesheet` refusal's routing, which this row honours in full including the parts that route **away** from it. |

---

## The collision fixtures, in both directions

The addendum requires a file that would wrongly fire this row **and** a file that must not be lost
*to* it.

**Inbound — would wrongly fire this row: `Change order 12 - line 3 guarding.pdf`.** Numbered, priced,
carrying a lead-time effect, approved by signature. It satisfies the variation-register triple in
prose form and it sits in a folder of engineering paperwork. It is **not** this row's, and what
discriminates it is the *anchor set*: a machine, a production line, a part number, a specification
revision — and the absence of a site, a contract clause and a construction instruction role.
`engineering.change-order` exists on the roster and holds it. The reciprocal is owed from that side.

**Inbound, second and harder — `Early warning 06 - crane oversail licence.pdf`, added this pass.**
A numbered notice describing a risk that has caused no loss yet, with a mitigation and a request to
meet, and **no cost or time figure at all.** It has none of the money apparatus this row is usually
recognised by, which is precisely why it is instructive: it is still this row's, because it is
**addressed and dated for service under a clause**. Its mirror — an internal risk register entry
saying the same thing in the same words, kept by the firm for itself with no addressee — is
`business_operations.risk-register`'s. The same sentence, twice, in two rows.

**Outbound — must not be lost to this row: `Site Diary - Oakfield Rd - 2026-03-14.pdf`.** It is cited
by page number in an extension-of-time submission's appendix index; it sits in a folder called
`Oakfield claim/appendices/`; and it is one of hundreds of identical siblings that belong to
`construction_property.site-diary`. **Purpose may be read from that folder; ownership may not.** 00
supplies both halves: *"Purpose may be supported strongly by an existing user-created folder name or
explicit language in a form or portal."* and *"It is a purpose clue and a review aid, not a basis for
automatic semantic propagation."* This pass turned that into a `never_alone` entry — citation in a
bundle index, or membership of a claim folder, never activates this row — because it is the trap this
row is structurally likeliest to spring.

**Outbound, second — `Plot 14 snagging list rev 3.xlsx`.** The load-bearing collision, and the same
bytes are named on `construction_property.snagging-defects` with the same reading in both files.

---

## Reciprocal boundaries, both directions

Every entry was read on the neighbour's side **first**. Where the neighbour had already stated the
line, its wording is adopted rather than re-authored, and no line is contradicted.

| Neighbour | This row must not take | The neighbour must not take | Shared fixture |
|---|---|---|---|
| `construction_property.snagging-defects` *(states its side; identical words both ways)* | a location, a responsible trade, a status column, a re-inspection history | a numbered instruction reference, a quantified cost-and-time consequence, an approval or notice | `Plot 14 snagging list rev 3.xlsx`; `VO-017 - upgrade to kitchen worktop.pdf` — genuinely both where both sets are present, and **abstention is the outcome** |
| `construction_property.construction-project` *(states its side; conceded to this row)* | the contract the instructions vary — the award sequence, the particulars block, the programme, the handover envelope | numbered instructions, CVIs, EOT and loss-and-expense submissions, dispute bundles | `AI 014 - relocate soil stack.pdf` — corroboration there, activation here |
| `construction_property.final-account` *(states its side)* | the reconciliation of the whole contract sum with amounts already certified; retention; the settlement statement | an instruction number with a narrative of entitlement, a clause cited, a cause-and-effect argument | a schedule of additions and omissions, which appears in both files |
| `construction_property.quote-estimate` *(does NOT yet state its side — reciprocal owed)* | a price written when there is no job, no contract and no job number to file it under | a price inside a live contract, against an instruction number, adjusting an agreed sum | `Quotation for VO 17 - revised drainage.pdf`; and its own work_type *"acceptance or instruction to proceed"*, which is its acceptance event on a new enquiry and this row's variation inside a running one |
| `construction_property.site-diary` *(states its side)* | an unaddressed daily entry in an unbroken run | a numbered variation or claim reference, a quantified consequence, an addressed notice | `Site Diary - Oakfield Rd - 2026-03-14.pdf` |
| `construction_property.subcontract` *(states its side)* | the subcontract order reference, the application, the statutory payment notice, the downward cascade | the main-contract instruction; the claim made upward against the employer | `AI 014 - relocate soil stack.pdf` cascading down as a subcontract variation |
| `construction_property.materials-delivery` *(states its side)* | the contemporaneous record of what arrived | an assertion of entitlement with a narrative and a cost consequence | a delivery note recording a shortage |
| `construction_property.drawings-revisions` *(states its side in prose; JSON reciprocal owed)* | the revised sheet, its revision designator, its status word, the transmittal register | the numbered instruction, the CVI, the change submission built on it | a sketch attached to an architect's instruction |
| `business_operations.risk-register` *(reciprocal owed)* | an internal register with owners, likelihood and mitigation and **no addressee** | a notice addressed and dated for service under a clause, whose lateness forfeits a right | `Early warning 06 - crane oversail licence.pdf` |
| `business_operations.contract-administration` *(landed; names `subcontract` for the adjacent reason)* | a general contract register and a renewal calendar | a site, a works package, a programme impact, a statutory construction notice regime | a signed agreement with a change log |
| `law_practice.evidence-exhibits` *(reciprocal owed)* | a matter reference, a paginated exhibit convention, a solicitor's framing | a party's own claim file | `Adjudication bundle - Oakfield - vol 2.zip` |
| `law_practice.settlement` *(new this pass; reciprocal owed)* | an engagement, a client identified as someone other than the holder, a practitioner's file convention | a party's own commercial position on its own contract | `WP - settlement proposal.docx` |
| `finance.insurance-corporate` *(reciprocal owed)* | a policy number, an insurer, a loss adjuster, a claim reference | a contract clause, an entitlement in days, a head-of-claim build-up | the same storm's photographs and diary pages |
| `engineering.change-order` *(reciprocal owed)* | a machine, a line, a part number, a specification revision | a site, a contract clause, a construction instruction role | `Change order 12 - line 3 guarding.pdf` |

Where a reciprocal is marked **owed**, the neighbour has not yet stated the line and this row cannot
write on its file. **R1c owes those seven reciprocals**; the fixture bytes are named on this side so
each can be checked rather than asserted.

---

## The bundle problem, narrowed

This is where the pass materially changed a conclusion, so it is stated separately.

The gist memo said: *"This row asserts no new mechanism and relies on the existing firewall; whether
that is sufficient when a bundle folder is scanned as a folder is worth a decision before P9 builds
grouping."* That was too pessimistic, and it under-read `00`.

**00 does supply a mechanism**, and it contains the exact clause this row needs. The purpose-packet
procedure asks *"whether the files plausibly serve one shared workflow, whether the group is
purpose-coherent despite topic diversity, which members appear to be supporting materials rather than
unrelated records, and whether any member conflicts with the proposed purpose"* — and **the last
clause disposes of the nastiest case this row records**, which is that claim bundles *deliberately*
import comparator files from **other contracts** to argue by contrast. Those are members that
conflict with the proposed purpose, and 00 already asks the question that catches them.

**What remains genuinely open is narrower**, and it is worth Joseph's decision before P9:

1. Is a bundle **folder**, scanned as a folder, read as a purpose clue only — which is all 00's two
   sentences permit — or is it allowed to become a group root?
2. May an index file's **citations** be used as retrieval at all? Retrieval is not propagation, and
   00 distinguishes them; but an index that names four hundred files is an unusually powerful
   retrieval instrument pointed at four hundred files this row does not own.

Both are recorded as NJ-CP-VAR-2, replacing the gist's broader and vaguer version of it.

---

## proposed_fields

**No key minted.** Three entries, all **seconds** of proposals that already exist, following
`construction_property.subcontract`'s practice so R1c adjudicates each once rather than per sibling.
Each carries this row's own datum for the adjudication:

- **`property`** — seconded, with a datum that runs *against* a naive reading: this is a row where
  `property` is often the wrong root. A variation is anchored to a **contract** far more reliably than
  to an address, and a multi-plot instruction carries several properties or none. That is an argument
  against assuming `property` is always the first dimension, not against the key.
- **`instruction`** — seconded, with the family's most specific datum, which cuts both ways. In
  favour: a variation number is meaningless without its contract, and VO 17 exists on every job — 00's
  own reason for putting a course above a homework number, *"a parent dimension should provide the
  context required to understand the child"*. Against relying on it alone: **this row needs a
  container below the instruction and no key holds it.**
- **`organization`** — seconded (originating on `business_operations`), with what is probably the
  strongest datum in the family: this is the row where custody changes the **meaning**, not merely
  the shelf. A claim submission and a claim response are the same document family with the roles
  reversed; the letterhead is often a consultant's rather than a party's; the same adjudication
  bundle exists in both parties' hands. Which side the holder is on is the fact this row most wants
  and least reliably has. `destination_eligible: false` is followed unchanged — the need here is a
  search and privacy need, not a folder need, which is consistent with FALSE.

**Deliberately not minted: a key for the change itself.** It is the row's true second dimension and
nothing holds it. Minting `variation_reference` or `change_id` would be a construction-flavoured
variant of nothing, which is the defect D6's ratification exists to kill. Raised as NJ-CP-VAR-3
instead.

---

## Neighbours considered that did NOT get an edge

- **`legal` as an edge** — the gist row expressed this only as `also_schema` on two fixtures, on the
  reasoning that `also_holds_with` joins schemas and this is a template row. **Reversed this pass**,
  with the reason stated: the landed spine carries four schema-level `also_holds_with` entries on a
  template-kind row, so the family's practice is settled and this row follows it rather than
  diverging. `legal`, `finance` and `business_operations` are now carried, with protective ordering
  noted for the two safety schemas. The `also_schema` markings on the fixtures are unchanged.
- **`government.public-procurement`** *(gist reasoning preserved)* — public-sector variation regimes
  are similar; the discriminating evidence already separates them through
  `business_operations.contract-administration`'s edge. Duplicating it adds shelving, not evidence.
- **`manufacturing.warranty-claim`** *(gist reasoning preserved)* — the word "claim" collides, the
  evidence does not.
- **`construction_property.timesheet`** — a **refused** row cannot be a collision partner; a refused
  row activates on nothing. The relationship is a routing and it is recorded as signals, a fixture, a
  `work_type` and a `must_not_conclude` rather than as an edge.
- **`construction_property.site-health-safety`** — it holds attendance and induction registers and
  says so, and its memo notes that a dayworks sheet *"carries names and hours and would be easy to
  take; taking it would contradict a landed refusal."* Both rows are downstream of the same refusal
  and neither takes the other's half. No edge is needed because the refusal already partitions them.
- **`career`, `academic`** — full vocabulary overlap, zero evidence overlap.
- **`legal.practice-matter-file`** *(landed)* — the seam that matters is with `law_practice.*`, which
  is edged twice. Adding a third to the personal-legal row would reach across a boundary the spine
  has already drawn.

---

## If this row had refused — the consequence, stated because the dispatch asked

It did not refuse. But the dispatch is right that the consequence needs stating, because a landed
refusal depends on this row:

**`construction_property.timesheet`'s routing would break.** Its refusal rests on the claim that a
signed daywork sheet is *"contractual evidence that extra work was done at cost"* whose situation is
this row's. If this row did not exist, that quarter of the timesheet coverage would have nowhere to
go: `site-diary` holds the labour allocation sheet and explicitly not the countersigned extra;
`site-health-safety` holds attendance and explicitly declines the dayworks sheet; the pay reading is
already routed to `hr` and `finance` and taking the contractual reading there would put employment
data under construction, which is the exact outcome the refusal exists to prevent. The plausible
re-pointing would be to `construction_property.final-account` (which owns the account the dayworks
are ultimately priced into) or to Independent Records.

**That re-pointing would be a recommendation to R1c, not an edit this agent makes.** A node agent may
not edit a neighbour's file, and re-pointing a landed refusal is a cross-row change. Recorded here so
the dependency is visible either way.

---

## NEEDS-JOSEPH

- **NJ-CP-VAR-1 · Defect or variation.** *(preserved from the gist pass, unchanged in substance.)*
  Reciprocal with `construction_property.snagging-defects`, same wording on both rows. Both sides
  write their reading down in good faith and the file is genuinely both. Recognise both and abstain —
  *"conflicting signals should lead to abstention rather than an invented classification"*, and 00's
  acceptance rule reaches the same result mechanically, since neither destination can *"exceed the
  next-best destination by a meaningful margin"*. **The decision:** whether a genuinely-both file is
  offered in two places or held in one. Cost of offering twice: the user sees the same file under two
  headings and may not understand why. Cost of holding once: whichever row wins is arbitrary, and the
  arbitrariness is invisible.
- **NJ-CP-VAR-2 · The bundle folder and the index.** *(narrowed this pass; see above.)* 00's
  purpose-packet mechanism covers more than the gist memo credited, including the comparator-file
  case. Two questions remain: whether a bundle folder may become a group root or only a purpose clue,
  and whether an index file's citations may be used as retrieval. **Alternatives:** (a) folder as
  purpose clue only, which is what 00's two sentences literally permit and which costs the user the
  most natural group they have; (b) folder as group root with per-member ownership preserved, which
  is more useful and which risks exactly the propagation 00 forbids. Worth deciding before P9 builds
  grouping.
- **NJ-CP-VAR-3 · No key holds the change.** *(new this pass.)* This row's recommended second
  dimension is the individual variation or claim, and neither the canonical fields nor any of the
  family's three proposals name it. **Alternatives:** (a) mint a key — rejected here as a D6 defect
  and not done; (b) let `instruction` do double duty, which flattens a bundle into a document-function
  shelf and loses the level this row's leg 2 depends on; (c) accept that this row's tree cannot be
  built from declared fields until a key exists, and say so. This row takes (c) and asks R1c to
  choose. **If R1c takes (b), leg 2 of this row's node test falls and the row stands on leg 1 alone**
  — which it does, but the row would be narrower than it is described here.
- **NJ-CP-VAR-4 · Reciprocals owed.** *(new this pass.)* Seven neighbours are edged one-way from this
  side: `construction_property.quote-estimate`, `.drawings-revisions` (prose only, no JSON edge),
  `business_operations.risk-register`, `law_practice.settlement`, `law_practice.evidence-exhibits`,
  `finance.insurance-corporate`, `engineering.change-order`. Fixture bytes are named on this side for
  each so the reciprocal can be checked. Not this agent's to write.

---

## Audits run before returning

- `python3 -m json.tool` on the node → **parses**.
- **Key set compared programmatically** against `construction_property.snagging-defects.json` (a
  deepened J-DEPTH sibling) → **identical, no symmetric difference**.
- **Every `“…”` span re-extracted from the JSON by regex and grep-checked.** 41 distinct quotations.
  37 verified verbatim against `planning/00-database-agent-product-design.md`; the remaining 4 are
  quotations *of neighbour node files*, each verified verbatim with `grep -F` against
  `construction_property.construction-project.json`, `.materials-delivery.json` and
  `.drawings-revisions.research.md` respectively, and each attributed in place.
- **Every edge id checked against `planning/domains/roster.json`** — 14 `collides_with` and 3
  `also_holds_with`, all present. `insurance.claims-handling` and `law_practice.dispute-resolution`
  were considered and are **not on the roster**; neither was used.
- Every `file_examples.source_type` is in `SOURCE_TYPES`. `fields` is empty. `proposed_fields`
  mints nothing. No threshold, statistic or file count invented. No `design_cite` fabricated.
- Files written: **only** `construction_property.variation-claim.json` and this memo. No neighbour
  touched.

---

## What changed in this pass

**Preserved unchanged** (the addendum forbids rewriting what was already right): the row's name and
its central characterisation as adversarial and notice-bound; all nine original `deterministic`
signals including the register triple and the self-timing notice; all seven original `needs_llm`
entries; all ten original `never_alone` entries; the 38 `proposed_context_terms`; the original 17
`work_types`; the original 10 `file_examples` with their observations and `must_not_conclude` lists;
`template.dimension_order` empty with its contract reason and its prose recommendation;
`time_first: false`; all eight original `collides_with` entries with their wording; all six
`falls_through_to` entries; `role_split` empty; `sensitivity` and `sensitivity_why`; and the gist
memo's four correct rejections and three correct no-edge calls, reproduced above with attribution.

**Reversed, explicitly:**

1. **Leg 3 of the node test is conceded.** The gist memo claimed the row passes on all three legs.
   The privacy leg does not stand on its own: the schema's default posture is already
   `potentially_sensitive`, the catalogue offers no stronger value, and setting the same value is not
   a difference. The kind-of-harm distinction is real, is retained in `sensitivity_why` as inference,
   and is recorded as a P7 input rather than a leg. **Three-of-three becomes two-of-three.**
2. **The bundle open question is narrowed rather than restated.** The gist said no mechanism exists
   beyond the firewall. 00 supplies one — the purpose packet, including the conflicting-member clause
   that disposes of imported comparators. The remaining question is smaller and sharper.
3. **`also_holds_with` reversed from empty to three entries.** The gist reasoned that
   `also_holds_with` joins schemas and so could not be used by a template row. The landed spine
   carries four such entries on a template-kind row, settling the family's practice; this row follows
   it rather than diverging silently.

**Added:**

- **the daywork-sheet signal, fixture, `work_type` value, `never_alone` and pay-reading refusal** —
  closing the hole where a landed refusal routed coverage to a row that could not recognise it;
- **the Scott-schedule signal and fixture** — the empty adjudicator's column, which the gist row had
  only as a context term;
- **the purpose-packet `needs_llm` entry** and the matching `grouping_reasons` entry, both quoting
  00's own procedure rather than asserting a new one;
- **three new `never_alone` entries**: a status column alone (which disqualifies a part of the row's
  own fingerprint), citation in a bundle index or membership of a claim folder, and a countersignature
  alone;
- **five new fixtures**: `Daywork sheet 018 - signed by CA.pdf` (the refusal's own bytes),
  `AI 014 - relocate soil stack.pdf` (the spine's and subcontract's shared bytes),
  `Scott schedule - Oakfield - items 1-46.xlsx`, `Quotation for VO 17 - revised drainage.pdf` (the
  contested bytes with `quote-estimate`), and `Early warning 06 - crane oversail licence.pdf` (the
  second inbound collision fixture);
- **six new `collides_with` entries**, four of them adopting the neighbour's own stated wording:
  `construction_property.construction-project`, `.quote-estimate`, `.materials-delivery`,
  `.drawings-revisions`, `business_operations.risk-register`, `law_practice.settlement`;
- **three `proposed_fields` seconds** with this row's own datum for each, minting nothing;
- **eight new context terms**, and a third open question;
- and, in this memo, the node test argued leg by leg against the anchor's quoted default template,
  the three dispatch charges answered separately, a sixteen-row rejected-files table, four collision
  fixtures in both directions, a fourteen-row reciprocal-boundary table marking which seven
  reciprocals are owed, and the refusal-consequence section the dispatch asked for.

**Deliberately not done:** no field minted; no neighbour edited; no threshold invented; no
`design_cite` manufactured for a world `00` never names; and no attempt to rescue leg 3.
