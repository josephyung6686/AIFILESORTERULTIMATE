# business_operations.partnerships-bd — lab notes (template row)

**Depth: J-DEPTH.** Deepened from the retired gist draft (2026-08-25). The gist draft's facts and
arguments were preserved; what it lacked — the node test argued leg by leg, the rejected files, a
two-directional collision fixture, reciprocal boundaries, and the settlement of the three-row
counterparty question — is added here. A "what changed" section closes the memo.

## Sources

`00-database-agent-product-design.md` (every quotation below machine-verified verbatim, with line
numbers recorded during the pass), `ALIGNMENT.md`, `_CONTRACT.md`, `CONNECTION.md` §2, §4 step 2, §5
and the edge table at §238, `CONNECTION-EXAMPLES.md`, `roster.json`, `canonical_fields.json`,
`DECISION-BRIEF.md` (J-IND, D1, PR-6), `ROSTER.md` §4 + Appendix A line 827.

Read before writing, and **not edited**:

- `business_operations.research.md` — the deepened schema anchor. Its default-template paragraph and
  its never-alone principle for all 24 siblings are the two things this row is measured against.
- `business_operations.organisational-records.json` — the family's refusal, read first on the
  dispatch's assumption that this row might be heading the same way. It is not, and the reason is
  argued below; but the refusal turns out to be the decisive argument in the *other* direction too
  (see "the merged row would be the refused row").
- `business_operations.customer-account-management.research.md` and `.vendor-management.research.md`
  — the two siblings organised around another organisation.
- `business_operations.contract-administration.json` — being deepened in parallel; its boundary with
  this row is restated reciprocally below and its file is not touched.
- `business_operations.product-requirements.research.md` — read for its method, not its content: it
  settled a pair question that had been carried as an identical `open_question` on two rows, on the
  principle that *a question stated identically on two rows is a well-documented deferral, not an
  answer*. The three-row question here is settled the same way.
- `finance.cap-table-equity.json` — read because a fundraising term sheet is one of this row's named
  instruments pointed at the wrong counterparty; a new reciprocal edge follows.

## What it is for, and what it holds

*(Preserved from the gist draft, verified.)* Pursuing a commercial relationship that does not exist
yet — a prospect, a partner, an alliance, a reseller, a piece of new work being bid for. Prospect and
partner profiles, pitch decks, proposals and statements of work, commercial offers, NDAs, letters of
intent, memoranda of understanding and term sheets, partner-programme material, bid responses,
pipeline exports, pursuit meeting notes, and win/loss reviews.

Legacy id absorbed: `ops.partnerships-bd` (ROW, `ROSTER.md` Appendix A line 827).

---

## The node test, argued leg by leg

CONNECTION §2: a template row exists only when its **detection signals**, its **recommended
dimensions**, or its **privacy rules** differ from its schema's default template. The schema anchor
adds the family rule this row is unusually exposed to:

> **No sibling may rest its activation on an entity name, a business vocabulary word, or a document
> shape alone.** Each of the three is never-alone here. Every detection signal a sibling writes must
> pair a **structure** with a **labelled slot**.

### Leg 1 — detection signals. **PASSES**, and it is the leg that carries the row.

The dispatch's warning (a) is correct as far as it goes: a partnership is named by the other
organisation, and an organisation name cannot activate anything. `00`'s stop rules say it twice, in
two independent registers. Once about groups formed on a name:

> "A university name alone should not create a group because Columbia can appear as an authoring
> school, course provider, target institution, employer, research venue, or merely a cited
> organization."

and once, more damagingly for this row, about groups held together by a counterparty at all:

> "when one high-frequency entity acts as the only bridge"

is listed among the conditions under which the system "should not form a supported group". A folder
of `Meridian-*.pdf` is precisely one high-frequency entity acting as the only bridge. **If the
counterparty name were this row's evidence, the row would be `organisational-records` with a sales
vocabulary, and it would deserve the same refusal.**

It is not this row's evidence. Three structures activate it, each pairing a structure with a labelled
slot as the family rule demands, and none of them is an entity name:

1. **The pipeline** — a table with one row per pursuit, whose load-bearing columns are *stage*,
   *expected close date*, *weighted value* and *probability*. This is a register of things that **do
   not exist yet**, and no other row in this family has one. `00` licenses reading it as structure
   rather than prose: *"Tables matter because resumes, forms, applications, invoices, and
   administrative documents often place their most useful information in cells rather than body
   paragraphs."*
2. **The pre-contractual instrument** — an NDA, a letter of intent, a memorandum of understanding, a
   term sheet, heads of terms. These exist **only** between first contact and signature. Their
   defining slot is that they bind the parties to *talk* while binding them to nothing else, and they
   are superseded and become dead paper the moment a contract exists.
3. **The outbound proposal** — addressed to a named external organisation, carrying an
   understanding-of-requirements section, a proposed approach, a commercial section, and — the slot
   that does the work — **a validity period**. A validity period is a confession that nothing is
   agreed. Nothing in the post-sale world has one.

Those three are unavailable to every sibling because each is defined by the *absence* of a
relationship, and the family's other rows are all defined by the presence of one. That is a real
difference in evidence, not a difference in topic word — and the schema anchor is explicit that a
topic word would not have been enough: *"What earns those rows their node is a distinct structure …
not the topic word."*

### Leg 2 — recommended dimensions. **UNAVAILABLE**, and I decline to claim it.

`template.dimension_order` is empty by binding contract (PR-6; D1's deferral as narrowed;
`_CONTRACT` rules 10 and 15). No sibling in this family can win this leg, and a row claiming to is
claiming a difference in something that does not exist. The prose recommendation is held for the pass
that may license fields, and it does diverge from the family paragraph in one substantive way:

- The family's order is *organisational unit (conditional) → governance body, project, contract or
  account → **fiscal period** → document function*.
- This row's is *organisational unit (conditional) → **counterparty** → **pursuit or opportunity** →
  document function*, with **no fiscal-period level at all.**

The omission is the honest part of the difference. A pursuit does not belong to a fiscal period; it
crosses them, and it ends when it ends. Putting Q3 above a pursuit that opened in Q2 and closed in Q4
splits one situation across three folders, which is the failure `00` names for time-first orders
generally: *"For document and record domains, project, function, or subject usually comes before time
because putting year first scatters related work across calendar folders."* In a family the anchor
memo describes as *made* of periods, having no period level is a genuine divergence — but it is a
divergence in a dimension nobody may write, so **this leg is scored unavailable, not passed.**

One thing worth recording for R1c, because it is a real tension rather than a tidy answer: the
counterparty level this row wants is the one level `00` is most suspicious of. *"A folder should not
become a collection point for everything produced by the same person or organization."* The escape is
narrow and it is `00`'s own: the counterparty here is not the author but the **target**, and *"the
document’s purpose, project, subject, or target is more informative for placement."* A pricing sheet
built for Meridian is about Meridian; it was not produced by Meridian. That distinction holds, and it
is the only thing that licenses the level. It also means the tree records who the holder has been
talking to — which is exactly what leg 3 is about.

### Leg 3 — privacy rules. **PASSES**, on a ground that is this row's alone.

The family's posture is that the exposed party is usually not the user. `customer-account-management`
sharpens that to third parties' data held inside a relationship. This row's ground is different from
both and is stated here for the first time:

> **A pipeline discloses relationships that do not exist.** Every other file in this family names
> counterparties the holder actually deals with. A pipeline export names organisations the holder
> *wants* to deal with, at the price the holder hopes to charge them, with a number attached saying
> how likely the holder privately thinks each is — and most of those organisations have not agreed to
> anything, several will refuse, and none of them has seen the number. It is a disclosure of intent,
> at scale, in one file, and both parties are harmed by it in opposite directions: the counterparty
> because it is being discussed without its knowledge, the holder because the file states what it
> would concede.

That is not the account row's ground (third-party data lawfully held) and not the vendor row's ground
(payment-fact fraud exposure). It is inference, marked as inference, and it is why the row is
`potentially_sensitive` and why `Protected Records` is a named fallthrough for the pipeline and
contact-export fixtures rather than an afterthought.

`00`'s corpus sentence covers the material — the corpus "can include identity documents, account
statements, tax records, medical information, legal records, credentials, private correspondence, GPS
metadata, employment materials, and educational records" — and the operative limits are `00`'s:
*"Protected material should not be included in cloud-model prompts by default, should not display raw
content in general group summaries, and should not be moved automatically without a user policy that
explicitly permits it."* Enforcement point: *"Privacy policy must be enforced before content reaches
any model or external connector."* This row assigns only the catalogue value
`potentially_sensitive`; handling classes are P7's and none is named here.

### Verdict

**Kept. `refuse_node: false`, and the gist draft's verdict is confirmed rather than reversed** — but
on a materially different argument. The gist draft rested the row on "the pursuit" as an anchor,
which is a purpose word and would not have survived the family rule on its own. The row is kept here
on the three structures, on the absence of a fiscal-period level, and on the disclosure-of-intent
privacy ground. Legs 1 and 3 pass; leg 2 is unavailable to the whole family.

---

## The three-row question, settled: pursuit, account and vendor are three worlds

The dispatch asks whether this row, `customer-account-management` and `vendor-management` are one
world under three names, with the counterparty's *role* as the only difference — and whether a role
is a field value rather than a domain. Following `product-requirements`, this is settled here rather
than restated as a matching `open_question` on three rows.

### The objection, stated at full strength

It is a strong objection and `00` appears to support it outright:

> "The system must separate roles that happen to contain the same entity type."

and the same passage: *"A consulting document may mention the author’s firm and the client
organization. … The agent should model these as distinct facets, such as authored_by and
target_school, or our_firm and client."* `00` is saying that a role difference is answered with a
**field**, not with a branch. If prospect / customer / supplier were the whole of the difference
between these three rows, the objection would win, and the correct outcome would be one row with a
role field. **I accept that premise.** Role is a field value. No one of these three rows may rest on
it, and this row does not: its `recognition` names the pipeline, the pre-contractual instrument and
the validity period, and never the counterparty's role.

### Three separations, each checkable against a real file

Reading the two siblings' own files first — `customer-account-management`'s anchor is *"one customer
as an ongoing relationship"* post-sale, with an account plan's stakeholder map, a co-branded periodic
review, a per-customer adoption record and a renewal preparation sheet; `vendor-management`'s is
keeping a supplier *"set up, safe to deal with, and honest"*, with an onboarding form carrying a
remittance block, a supplier register with a relationship owner, a diligence questionnaire and a
scorecard — the separations are:

1. **Whether the relationship exists yet — an existence difference, not a role difference.** The
   siblings' characteristic documents *measure* a relationship and therefore cannot predate one: an
   adoption record needs usage, a scorecard needs performance, a remittance block needs a payee. This
   row's characteristic documents can only exist *before* one: a validity period expires precisely
   because nothing is agreed; an NDA exists to license a conversation that has no contract behind it;
   a pipeline stage is a position on a path toward a relationship. A document that measures a
   relationship and a document that proposes one are not one document with a field flipped.
2. **What the register is a register of.** All three worlds have a table, and that surface similarity
   is most of why they look like one world. The supplier register and the account book list **actual**
   counterparties with actual identifiers — vendor number, account number, remittance detail,
   relationship owner. The pipeline lists **opportunities**, and every column that makes it a
   pipeline describes a future that may not happen: stage, expected close date, weighted value,
   probability. Delete those four columns and the file stops being a pipeline; delete them from a
   supplier register and nothing is lost, because they were never there.
3. **Whether the world has a terminal state that is nothing.** *Closed lost* is a real, common,
   permanent outcome here, and its terminal document is a win/loss review — after which the pursuit
   file set is complete and dead, with no successor object anywhere in the corpus. Neither sibling
   has that: churn and vendor exit both leave an administered wind-down, a final invoice, a
   transition record, an obligation running to expiry. A world half of whose members end in *nothing*
   is not the same world as one whose members end in an obligation.

### The decisive argument: the merged row would be the refused row

This is the part the merge case cannot survive, and it comes from the family's own refusal rather
than from anything this row asserts.

Strip the three rows of the structures argued above — the pipeline, the adoption record, the
scorecard — on the grounds that they are "the same world seen from three angles", and ask what the
merged row's anchor would be. It is *an external organisation the holder has dealings with*. That is
an entity name and nothing else, which is exactly the anchor
`business_operations.organisational-records` was refused for: *"an organisation name is
constitutionally never-alone … A row whose entire support is never-alone evidence can never clear
activation (CONNECTION.md section 4 step 2), so it would be a row that never fires."*

So the merge does not simplify the family; it produces a row that cannot fire, and it destroys three
rows that can. Note also what the "one folder per counterparty" intuition would have to merge to be
consistent: **customer-account-management and vendor-management**, which sit on opposite sides of the
money. A merge principle that puts the people who pay you and the people you pay in one row is not
identifying a world; it is identifying a *name*.

### Where the merge case remains real, and why it does not win

It is not dismissed. A real folder called `Meridian/` holds the NDA, the proposal, the signed MSA,
the QBR and the scorecard together, and a user shown five branches for one company would reasonably
ask for one. That is true and it is an argument about **how people store**; the node test is about
**what evidence activates**. `00` already provides the mechanism that makes the storage complaint
answerable without merging rows: *"A file may validly belong to more than one accepted group"*, and
*"One file may hold facts from more than one domain without losing information."* The counterparty
branch a user wants is a **dimension-time** answer — a counterparty level above several situations —
not a roster-time one. It also needs a canonical key that does not exist (below).

**Verdict: three rows, not one.** This row does not recommend absorbing or being absorbed. Reciprocal
consequence for R1c, stated because it follows directly: the *pressure* the merge case identifies is
real and lands on the missing counterparty-role key, so settling that key is now more urgent, not
less. Recorded as NJ-BO-PB-1.

---

## Reciprocal boundaries

Stated in both directions. Where a neighbour has landed, its own file was read first and is not
contradicted; where this row diverges or where the neighbour's file is silent, that is said openly.

**`business_operations.contract-administration`** *(being deepened in parallel — not edited)*. Its
`one_line` sets the boundary from its side already, and it is a clean one: its anchor is *"a LIVE
OBLIGATION and its calendar — not the negotiation that produced the instrument and not the instrument
itself."* This row states the same seam from the other end: **everything up to and including the
moment of signature is this row's; the register entry, the notice date and the obligation tracker
that the signature creates are that row's.** The same bytes both rows must name: `NDA - Meridian -
executed.pdf`. An executed NDA is simultaneously the opening act of a pursuit and a live contractual
obligation with a term and a governing-law clause, and neither row may resolve it from structure —
P10 chooses from an accepted group. **Divergence to flag, honestly:** that row's `collides_with` list
names `procurement-sourcing`, `vendor-management`, `customer-account-management` and five others, but
**not this row**. The edge is presently one-sided. This row carries it; R1c should ask that row's
author to mirror it or say why not. Recorded as NJ-BO-PB-2.

**`business_operations.customer-account-management`**. Its file draws the line at the sale and this
row agrees with it in matching terms: *pre-sale is this row, post-sale is that one.* The same bytes
both rows must name: an **expansion proposal to an existing customer** — a document carrying a
validity period (this row's slot) addressed to a counterparty with an account number and a usage
history (that row's slots). Both fire, honestly. This is `needs_llm` on this side, and this row's
recommendation is that neither claims it structurally: the two rows are mutex for one *opportunity*,
not for one *counterparty*, and a customer with a live expansion pursuit is both at once.
`also_holds_with` cannot express this — CONNECTION's edge table makes it **schema ↔ schema only** and
these are two templates on one schema — so it is stated in prose here and left to P10.

**`business_operations.vendor-management`**. Reciprocity is easy and worth recording because the row
worried about its own thinness: this row is the buy-side's mirror only in the sense that both involve
counterparties, and there is no real seam. That row's anchor artifacts — onboarding form with a
remittance block, diligence questionnaire, scorecard — cannot exist before a supplier is engaged, and
this row's cannot exist after. **The one contested case is a supplier NDA**, which that row folded
into its legal edge rather than claiming; this row does not claim it either where the holder is the
buyer, because the pursuit was the supplier's, not the holder's. That is the "which side of the
table" question and that row already carries it as NJ-BO-VM-3.

**`business_operations.procurement-sourcing`** *(preserved from the gist draft — its argument was
sound and is kept in its own terms)*. The mirror-image problem: every document in a sourcing event
exists identically on the selling side; a bid response here is a supplier response there, and a
pricing schedule is the same spreadsheet. The discriminator on both rows is **possession of the
evaluation apparatus** — several suppliers' responses, scoring matrices, an award to issue — rather
than anything about the documents themselves. Same bytes both rows name: `PQQ response -
ITT-2026-014.docx`.

**`finance.cap-table-equity`** *(new edge in this pass)*. Read that row's file first: SAFEs,
convertible notes, stock purchase agreements and 409A valuations are its `work_types`. A **fundraising
term sheet** is the pre-contractual instrument for exactly those — and "term sheet" is one of this
row's three named instrument words, so an investor term sheet would fire this row wrongly. The
discriminator is **what is being offered**: this row offers work, goods or a commercial arrangement
for a fee; a fundraising term sheet offers **equity in the holder's own entity**, and its slots say so
— pre-money valuation, liquidation preference, option pool, board seat. Stated reciprocally: a term
sheet whose slots are valuation and preference is the finance row's even though it names a
counterparty and a negotiation; a term sheet whose slots are scope, fee and exclusivity is this row's
even though it is called a term sheet.

**`career.consulting-client-engagement` and `career.recruiting`** *(preserved)*. For an individual,
pitching for work and applying for work are one activity with two vocabularies. Both edges are
authored so the question is visible from either direction; it is the row's oldest open question and
is unchanged (NJ-BO-8).

**`law_practice.contract-negotiation`**, **`business_operations.go-to-market`**,
**`nonprofit.fundraising-donor`** — carried forward from the gist draft unchanged; their
discriminators (a matter reference and privilege; a launch date and positioning; a funder and a
charitable purpose) were checked and stand.

---

## Files considered and rejected

The tempting false positives, and what discriminates each. Several are kept as fixtures in the JSON;
the rest are named here and deliberately not claimed.

| File | Why it is **not** this row's evidence |
|---|---|
| `QBR - Northwind - Q1.pptx` *(kept as the primary collision fixture)* | Adoption charts against a baseline and a renewal date. The deal is already won; `customer-account-management` owns it. This is the fixture in the **wrongly-fires** direction: same counterparty, same deck template, often the same folder. |
| `Consulting proposal - Meridian.pdf` *(kept as the second fixture)* | An individual's own credentials, a day rate, a CV appended. Genuinely undecidable between this row, `career.consulting-client-engagement` and `career.recruiting` — NJ-BO-8. Kept because it is the row's real boundary problem, not despite it. |
| `Term sheet - Series B.pdf` *(kept as a fixture, new this pass)* | A named instrument word pointed at the wrong counterparty. Valuation, preference and board-seat slots make it `finance.cap-table-equity`'s. The **fires-wrongly-on-vocabulary** case. |
| `TechSummit 2026 - attendee list.xlsx` *(kept as a fixture, new this pass)* | Rows of organisations and named contacts — visually a pipeline, and the closest thing in the corpus to one. It has **no stage, no close date and no probability column**, which is the whole discriminator. Nothing here proposes a pursuit. |
| `contacts_export.vcf` *(kept)* | `00` treats contact data as privacy-side rather than as a source of folder proposals, and a contact list is the thing most likely to be mistaken for a pipeline. Protected Records. |
| `Meridian - MSA - executed.pdf` | The moment this document exists the pursuit is over. `contract-administration` and `legal` share it; this row must not follow the counterparty across the signature. |
| A **published model NDA** from a law firm's website | The family's real-versus-exemplar trap in this row's clothes: identical instrument, no party names, no purpose. *"purpose answers what the file was for"* — it was for illustrating an NDA. Reading Inbox. |
| A **university partnership MOU** (institutional research collaboration) | An MOU is one of this row's three instrument classes, and this one is not commercial: the parties are institutions, the object is research, no fee is proposed. `academic` / `research` fires on its own evidence. |
| A **conference sponsorship pack** | Real BD material, but it is marketing spend committed to no counterparty; `go-to-market`'s. |
| A **grant application** | A proposal by shape and by vocabulary; the counterparty is a funder and the framing is charitable. `nonprofit.fundraising-donor`'s, and edged. |
| A **whiteboard photo of a deal funnel** (`IMG_*.HEIC`) | Real capture EXIF, handwriting no extractor has read. Capture-based media; `also_schema: photos`, and **conclude nothing about a pipeline before OCR exists**. `00`: *"the system should not infer a purpose from their filename alone."* |
| A **supplier's inbound proposal** received by the holder | The mirror image at file level: an outbound proposal for its author is an inbound one here. Which side the holder is on is not in the document. Abstain — the family's "side" posture. |

**Collision fixture, both directions**, as the addendum requires:

- **Would wrongly fire this row:** `Term sheet - Series B.pdf` — one of the row's own instrument words
  attached to a fundraising counterparty. Discriminated by the offered thing (equity, not work).
- **Must not be lost *to* this row:** `QBR - Northwind - Q1.pptx` — a counterparty name, a commercial
  deck and a renewal date, all of which this row's vocabulary matches, belonging entirely to
  `customer-account-management`. Discriminated by measurement of an existing relationship.

---

## `proposed_fields`

**None, and the abstention is deliberate rather than empty.**

PR-6 forbids field rows on this schema, and `fields: []` follows from the contract. On
`proposed_fields`, which is not forbidden, this row still mints nothing, for three reasons:

- **`organization`** — seconded, not re-proposed. The schema row proposes it as the custody role with
  `destination_eligible: false` and `reliability_ceiling: "possible"`, and `construction_property`
  seconds the same key so it is adjudicated once. This row agrees with the ceiling and with the
  reason: an entity name is the multi-role token.
- **`fiscal_period`** — **explicitly declined.** Four siblings want this key; this row does not, and
  that is part of leg 2's argument. A pursuit does not have a fiscal period; it has a start, a stage
  and an outcome, and forcing it into a management calendar splits pursuits that cross a year
  boundary. Recording a decline is more useful to R1c than silence.
- **The counterparty-role key** — wanted badly here and **still not minted.** The schema row said
  `supplier` should be proposed on `contract-administration`; `vendor-management` checked and found
  that row landed with `proposed_fields: []`, so the key is presently proposed by nobody.
  `customer-account-management` names the same hole (NJ-BO-9). This row is now the **fourth** row to
  want it and the fourth to decline to mint it, because four rows minting four variants of one key is
  precisely the duplicate-vocabulary failure the contract warns about. R1c must place it on exactly
  one row or decide the role stays unheld. See NJ-BO-PB-1: this row's settlement of the three-row
  question makes it the load-bearing gap in this cluster, because all three surviving rows now
  explicitly refuse to anchor on role, while a user's filing instinct is to file by counterparty.

`proposed_context_terms` carries the pursuit vocabulary (pipeline, qualification, heads of terms,
closed won, closed lost, …). These are proposals, not `00`'s floor — `00`'s named context-term floor
is the academic one, and this row does not pretend otherwise.

---

## Sparse-file discipline

Most fixtures carry `group_without_copying_facts: true`, and the rule matters unusually here because
the row's grouping temptation is the strongest in the family: **one counterparty across several
pursuits over years is a real reason to group, and it is also the fastest route to writing a
relationship fact onto a file that merely names the company.** `00`: *"The graph does not
automatically copy those missing facts onto sparse files."* A folder of a hundred Meridian files may
contain one that says Meridian is a customer; the other ninety-nine still do not say it. And where the
counterparty is the only thing holding a candidate group together, the group should not form at all —
*"when one high-frequency entity acts as the only bridge"* — with *"Sparse groups with no anchor
should be shown only as tentative discovery candidates, if at all."*

The single `group_without_copying_facts: false` fixture is the QBR, and that is correct: it is not
this row's file at all.

---

## Neighbours considered that did NOT get an edge

- **`business_operations.market-research`** — competitor and market material is saved during
  qualification. The edge is authored from the market-research side; not doubled here. Reading Inbox
  already catches the saved-report case.
- **`creative.client-engagement`** — a studio's new-business pursuit. Same reasoning as the two
  `career` edges, which are authored; a third statement of one confusion would be true and useless.
- **`retail_hospitality.catering-contract`** and similar sector rows — sector-specific instances of
  the same pursuit. A sector is a value.
- **`hr`** — named internal owners appear on every pipeline and every pursuit note. Not edged; the
  whose-record-is-it discriminator is the schema row's, and adding a per-row copy would dilute it.

---

## NEEDS-JOSEPH

- **NJ-BO-8 · Person or organisation?** *(carried unchanged from the gist draft — still open, still
  the row's sharpest question.)* For a company, business development and job-seeking are unmistakably
  different activities. For a freelancer, a consultant or a sole trader they are one activity with two
  vocabularies — the same proposal PDF is a bid on Monday and a job application on Tuesday. Filing a
  person's freelance pitches under a business-operations branch, or a company's proposals under a
  career branch, would each be wrong for somebody. Stated reciprocally:
  `career.consulting-client-engagement` and `career.recruiting` both carry authored collision signals,
  so the question is visible from either direction. Related: **NJ-BO-1** on `it-asset-inventory` is
  the same person-versus-organisation line asked about a different pile; R1c should treat them
  together. **Alternatives and costs:** (i) route by holder type — correct for most users, requires a
  setting `00` does not describe; (ii) let both rows fire and let P10 choose — safe, but leaves the
  commonest freelance document permanently ambiguous; (iii) give the pursuit to `career` for
  individuals — clean, and wrong for a one-person company that genuinely sells.
- **NJ-BO-PB-1 · The counterparty-role key, now load-bearing for three rows.** Four rows want it
  (`contract-administration`, `vendor-management`, `customer-account-management`, this one) and four
  decline to mint it. This memo settles that pursuit, account and vendor are three worlds, which makes
  the gap sharper rather than softer: all three now rest on structure and explicitly refuse to anchor
  on role, while the user's filing instinct is a single counterparty branch. **Alternatives:**
  (i) widen `client` to cover all counterparties with a role value — cheapest, and it overloads a key
  `00` defined narrowly; (ii) mint one `counterparty` key with a role value — cleanest, and it is a
  new key on a field-less schema; (iii) leave the role unheld — honest, and it means no counterparty
  dimension is ever proposable. This row recommends (ii) and does not act on it.
- **NJ-BO-PB-2 · A one-sided edge with `contract-administration`.** This row names that row; that row
  does not name this one. Its author is working in parallel and this memo will not edit it. R1c should
  mirror the edge or record why not.
- **NJ-BO-PB-3 · The expansion proposal to an existing customer.** Genuinely both rows' file, and the
  edge type that would express it (`also_holds_with`) is schema-to-schema only, so two templates on
  one schema have no way to say "both". Either P10 carries it, or the contract needs a sibling-level
  co-activation edge. Flagged here because this row is where the case is commonest.

---

## What changed in this pass

**Preserved** (verified, not rewritten): the row's purpose and holdings; the legacy-id absorption; the
mirror-image argument against `procurement-sourcing` in its own terms; the `QBR`, `Consulting
proposal` and `contacts_export` fixtures and the reasons they were kept; NJ-BO-8 verbatim; the whole
`recognition` block, which was already substantive and house-correct; the sensitivity posture; the
`open_question` text.

**Added or changed:**

1. The node test argued **leg by leg** with a verdict per leg, replacing a one-paragraph verdict. The
   row's basis of survival moved from "the pursuit" (a purpose word, which the family rule would not
   have accepted) to three named structures, the absent fiscal-period level, and a privacy ground of
   its own.
2. The never-alone principle applied explicitly, with `00`'s **"one high-frequency entity acts as the
   only bridge"** stop rule introduced — the strongest evidence in the corpus for this row's exposure,
   and it was not in the gist draft.
3. **The three-row question settled**, rather than deferred: pursuit, account and vendor are three
   worlds, on three checkable separations, with the decisive argument being that the merged row would
   be `organisational-records` and would be refused for the same reason. The role-is-a-field-value
   objection is accepted on its own terms and then shown not to reach the rows.
4. **Reciprocal boundaries** written for six neighbours in both directions, including the one-sided
   `contract-administration` edge flagged rather than silently fixed.
5. A **twelve-row rejected-files table**, and a collision fixture in **both** directions.
6. **Two new edges and two new fixtures**: `finance.cap-table-equity` (the fundraising term sheet) and
   the conference attendee list (a pipeline-shaped file with none of a pipeline's columns).
7. `proposed_fields` abstention **argued** — `organization` seconded, `fiscal_period` explicitly
   declined with a reason, the counterparty key declined for the fourth time with the count recorded.
8. Three new NEEDS-JOSEPH items, each with alternatives and costs.

**Not done, and why:** no sibling file was edited, including where this memo says one is missing an
edge; the `open_question` text is unchanged, because a one-sided change would leave paired rows
contradicting each other and R1c owns the pair.

**Length note:** this memo is shorter than the deepened schema anchors. That is the honest size of
the row — it has one strong structural argument, one privacy ground and a well-defined neighbourhood,
and the remaining uncertainty is concentrated in two questions that cannot be settled here. It was not
padded to reach a target.
