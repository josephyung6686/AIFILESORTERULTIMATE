# `business_operations.contract-administration` — lab notes (template row, deepened to J-DEPTH)

**Depth: J-DEPTH.** Deepening pass over a verified gist draft. The gist verdict — the row stands —
is **affirmed, not reversed**, but it is affirmed on a *narrower and better* discriminator than the
gist gave, and the gist's own load-bearing sentence about the notice-date column is corrected in one
respect (§ *The gist pass's central claim, and where it was too strong*). Nothing that was right was
rewritten for the sake of rewriting.

The dispatch put two charges to this row and both are answered in full below, honestly, with the
concession each deserves:

- **(a) Is this `legal`'s material wearing a business label?** — § *The load-bearing seam*.
- **(b) Is this a `work_type` — the activity of administering, not a filing world?** — § *Leg 1*,
  and § *The activity charge*.

And the dispatch's trap is accepted outright and written into the JSON: **if the only discriminator
were that a company rather than a person holds the contract, this row would fail.** That is an
organisation name, it is constitutionally never-alone in this family, and it cannot activate a row.
It is now `recognition.never_alone[2]` so that no downstream reader can mistake it for support.

---

## Sources actually used

### Binding local sources

- `planning/00-database-agent-product-design.md` — authoritative. **Every curly-quoted span in the
  JSON and in this memo was machine-verified verbatim against it** (25 spans, whitespace- and
  smart-quote-normalised, zero failures). Quotations from sibling *node* files are given in straight
  quotes with the file named, so the two can never be confused.
- `planning/domains/_CONTRACT.md` (rules 6, 10, 15), `planning/domains/CONNECTION.md` (§2 node test,
  §3 browse-only parent / activation ≠ grouping, §4 activation, §5 invariant 2, §9 failure mode 6),
  `CONNECTION-EXAMPLES.md` (fixture 5, the `.ics` case).
- `planning/domains/canonical_fields.json` — no key minted here.
- `planning/domains/roster.json` — every edge id below was checked to exist as a `domain_id`. All
  ten collision targets and the one `role_split` target resolve.
- `planning/prompts/ALIGNMENT.md`; `planning/overnight/council/DECISION-BRIEF.md` (D1 as narrowed,
  D6, J-IND/J-DEPTH); `ROSTER.md` §4 + Appendix A line 823.

### The schema anchor, read first

`business_operations.research.md` (46KB, deepened). Three things in it govern this row, and one of
them is close to dispositive:

1. **Its leg-2 detection argument names this row's structure as one of four the family owns, and
   assigns it here explicitly.** Signal shape 4, verbatim from that memo:

   > **The post-signature obligation register.** A schedule of renewal dates, notice periods and
   > counterparties that *manages* instruments rather than being one. `legal` owns the instrument;
   > nobody else owns the register.

   That is the schema row, written at full depth after reading `legal`, independently reaching the
   same seam this row needs. It is not proof — a schema row cannot license its own sibling — but it
   means the row is not inventing a discriminator to save itself.

2. **The default template**, which this row must differ from, verbatim:

   > the **organisational unit or entity** *only where the corpus genuinely spans more than one* →
   > the **governance body, project, contract, or account** the material belongs to → the **fiscal
   > period** → the **document function**. Not time-first.

   Note the word **contract** in that second level. The default template already *contemplates* this
   row's anchor. That cuts against the row on the dimensions leg, and § *Leg 2* concedes it.

3. **The never-alone principle for all 24 siblings**, verbatim:

   > **No sibling may rest its activation on an entity name, a business vocabulary word, or a
   > document shape alone.** Each of the three is never-alone here. Every detection signal a sibling
   > writes must pair a **structure** with a **labelled slot**. If a proposed row cannot name such a
   > pair, it is not a node — it is the schema's default template, or a residual wearing a domain's
   > clothes.

   Applied literally in § *Leg 1*: every deterministic signal on this row is restated as a
   structure-plus-labelled-slot pair, and the two that could not be so restated were struck.

Also from the anchor, and binding on this row: **no row in this family may claim
`provenance: "design"` for the existence of its situation.** This row is `proposal` with
`design_cite: null`, and that is not a formality — see § *00 never mentions a contract*.

### The family's refusal, read on the assumption this row was heading the same way

`business_operations.organisational-records.json`. Its `refuse_reason` was read in full before this
row's node test was written. Its three-leg failure is the template against which this row's three
legs are measured, and its corollary — *keeping a row to preserve a legacy id is the 574's mistake*
— was taken seriously rather than nodded at. The honest position after doing so: **this row is
closer to that refusal than any sibling except `vendor-management`, and it survives on one structure
rather than on a comfortable margin.** Said plainly rather than smoothed.

### The `legal` rows, read because `legal` owns contracts

`legal.leases-agreements.json` and `legal.practice-matter-file.json`, both landed at full depth.
Neither was rewritten and nothing below contradicts either.

### The sibling that already settled this exact charge

`construction_property.subcontract.research.md` (42KB, just deepened). It defended a contract row
next to `legal` and its reasoning is **followed, not diverged from** — see § *The load-bearing seam*,
which adopts its instrument-versus-running-apparatus formula and its per-evidence-item mutex, and
inherits its reciprocity debt as one debt with a third creditor.

### Siblings whose files travel with contracts

`business_operations.vendor-management.json`, `.procurement-sourcing.json`,
`.customer-account-management.json`. All three already name this row in their own `collides_with`
and all three give the **same** discriminator for it — the obligations register, notice dates and
renewal correspondence. Those reciprocals were read before this row's were written, and one
disagreement was found and is recorded rather than papered over (§ *Reciprocal boundaries*).

---

## What this row is for, and what it holds

Running a contract **after** it is signed. The register of what is in force, the obligations and
service levels it created, the notice and renewal dates that must be diarised, the variations that
amend it, the performance reports that test it, and the correspondence that manages it to expiry.

Absorbs the legacy row `ops.contract-administration` (ROW, `ROSTER.md` Appendix A line 823).
`ops.client-engagement` folded to `career.consulting-client-engagement`, **not here**; that boundary
is respected by an authored collision rather than quietly reclaimed.

---

## 00 never mentions a contract — and this matters

A grep of `00-database-agent-product-design.md` for *contract*, *agreement*, *renewal*,
*counterparty*, *vendor* and *supplier* returns three hits and **not one of them is about this
subject**: the acceptance-contract sense of §6.10, a `vendor` directory in the scan-exclusion list
(node_modules, .git, venv, …), and nothing else. 00 names *"legal matters"* and *"client
engagements"* in its template-library sentence and stops there.

Two consequences, both taken:

- **`provenance: "proposal"`, `design_cite: null`.** The situation is an inference from the family
  anchor. Every *mechanism* this row invokes — tables, purpose coherence, abstention, residuals,
  never-alone, the recommendation-not-a-rule clause — is `design` and quoted verbatim. The
  *existence of the situation* is not, and the JSON says so.
- **No 00 sentence can be leaned on to settle the seam with `legal`.** The seam had to be argued
  from the neighbours' own files, which is what § *The load-bearing seam* does.

---

## The node test, all three legs, argued

CONNECTION §2, verbatim: *"A **template** row exists only if its detection signals, recommended
dimensions, or privacy rules differ from its schema's default template."* Three legs; the row needs
one to carry it and gets exactly one.

### Leg 1 — detection signals of its own — **PASSES**, and it is the only leg that carries the row

The family principle requires a **structure paired with a labelled slot**. Restating each signal in
that form is a real test, not a formality, and it killed two candidates:

| Structure | Labelled slot that completes it | Owned elsewhere? |
|---|---|---|
| a table with **one row per agreement** | a **notice-date** column, plus a contract reference and an **internal contract owner** | no |
| obligations extracted into rows | a **clause reference** per row, plus a responsible party and a frequency | no |
| a formal letter | a **labelled clause reference** + an **effective date** + a delivery method + a served-on block | no |
| an amending instrument | a **parent-agreement reference and date** + a numbered amendment sequence + its own execution block | contested — see below |
| a periodic performance table | a **service-credit / remedy column referring back to a schedule** | contested — see below |
| a one-page precis | labelled slots for parties, term, value, notice, governing law | no |

**Two candidates struck in this pass, because they are structure without a slot:**

- *"contract vocabulary in a document"* — agreement, term, renewal, counterparty, SLA. This is the
  family's "business vocabulary word alone" and it was already in `never_alone`; it is not promoted.
- *"a parties block naming two organisations"* — this is the dispatch's trap. It is a structure with
  a labelled slot and it still cannot fire, because the slot names **two** entities in **two** roles
  and the document never says which side the filesystem is on. Now written into `never_alone` in
  those words.

**The two contested rows.** The amendment structure and the performance table are both claimed
elsewhere — `legal.leases-agreements` lists *"amendment, addendum or variation"* and *"renewal or
extension"* among its own `work_types`, and `vendor-management` owns supplier scorecards. Neither is
therefore load-bearing here, and the JSON's new file example
`Deed of variation - 14 Bridge Street - signed.pdf` is precisely the case where the amendment
structure fires for the **wrong** row. **What is left after conceding both is the register.**

**So the row's node reduces to one structure**, and it is worth stating that starkly:

> A **portfolio table over many agreements**, carrying a **notice-date column** and an **internal
> contract owner** — a structure that exists because someone must *manage* instruments they are not
> reading, and which the instrument itself, by construction, can never contain.

That is enough. 00 licenses reading it — *"Tables matter because resumes, forms, applications,
invoices, and administrative documents often place their most useful information in cells rather
than body paragraphs."* — and no other row on the roster produces it. It is a thin node, not a fat
one, and the JSON's `open_question` says so.

### Leg 2 — recommended dimensions of its own — **DOES NOT CARRY THE ROW**, and this pass says so

`template.dimension_order` is **empty by contract**: a dimension may only branch on a field the same
entry's schema declares, and `business_operations` declares none (D1 as narrowed, `_CONTRACT` rules
10 and 15, CONNECTION PR-6). So this leg cannot be *tested* on the JSON as it stands, and the
recommendation is held as prose for whoever answers the schema row's open question.

Held as prose, honestly measured against the default template: **the difference is small.** The
default's second level is already *"the governance body, project, contract, or account"* — the word
**contract** is in the anchor's own sentence. This row's prose recommendation (counterparty or
contract → agreement reference → document function, with the renewal period only where the corpus
really cycles) is that default with the *contract* alternative selected and one sub-level added.
**Selecting one of four listed alternatives is not a difference.** This leg is conceded.

Two things it does contribute, neither of them a node:

- The parent-context rule bites unusually hard here: an amendment is unintelligible above its parent
  agreement, exactly 00's reason for putting a course above a homework number.
- **Not time-first**, and this row is one of the family's most tempting candidates to break that,
  because everything in it is a date. It does not: 00 grants the exception to capture-based media,
  and a contract term is a content period. Also *"For document and record domains, project,
  function, or subject usually comes before time because putting year first scatters related work
  across calendar folders."* And whatever eventually lands stays a recommendation — *"The system
  recommends an order based on the domain template, but the user can reverse, remove, add, or
  flatten dimensions."*

### Leg 3 — privacy rules of its own — **DOES NOT CARRY THE ROW**, and this pass says so

The row is `potentially_sensitive` and assigns no P7 handling class. The temptation is to claim a
distinct posture from the fact that contracts contain their own confidentiality clauses and that the
exposed party is usually not the user. **The second half is real and the first is not a rule.**

- **The exposed party is usually not the user** is true here — a counterparty's pricing, an employee
  named as a signatory, a customer's terms. But the schema anchor already claims exactly this as the
  *family's* leg-3 ground: *"The exposed party is usually not the user. This is the distinguishing
  fact and it is an inference, not a design claim."* Inheriting the family's own distinguishing fact
  is not differing from it.
- **A confidentiality clause inside the document** is content, not a privacy rule, and reading it as
  one would be the product asserting a legal conclusion — which the JSON already forbids elsewhere
  (*"a legal effect of the product's own from the letter; whether valid notice was given is not the
  product's question"*).

So the posture is the family's, unchanged: *"Privacy policy must be enforced before content reaches
any model or external connector."* and *"Protected material should not be included in cloud-model
prompts by default, should not display raw content in general group summaries, and should not be
moved automatically without a user policy that explicitly permits it."* Where this row and a
`legal` safety row both fire, **the stricter side wins** and the material is offered under Protected
Records.

### Overall

**Kept, on leg 1 alone.** Legs 2 and 3 are conceded in this pass — the gist draft implied more
support from them than they give. One structure, argued, is enough under CONNECTION §2's "or", but
the margin is thin and NJ-BO-CA-3 records it.

---

## The gist pass's central claim, and where it was too strong

The gist wrote:

> The single most characteristic detection signal is the **notice-date column** in a register table —
> it appears in no other family's tables.

**Substantially right, and corrected in one respect.** `vendor-management`'s landed JSON describes
its own supplier register as carrying *"a spend band and a review date"*. A **review date** is a
date column in a register table in this family. It is not a notice date — a review date is a
relationship cadence the holder sets and can miss; a notice date is a contractual deadline the
holder cannot — but the gist's "appears in no other family's tables" was one word too broad. The
corrected claim, and the one the row now rests on:

> A **notice date** and an **internal contract owner** in the same table as a **contract reference**
> appear in no other family's tables. A bare date column in a register does not discriminate.

This is now the new file example `Supplier register.xlsx`, which fires the register structure and
belongs to the neighbour.

---

## The load-bearing seam — is this `legal`'s material wearing a business label?

**No, and the answer follows `construction_property.subcontract` deliberately rather than
inventing a second formula.** That row defended the identical charge and its move was to read
`legal.leases-agreements`' own repeated discriminator formula and apply it across. This row does the
same, because two sibling rows facing the same creditor with two different formulas would be worse
than one shared one.

**What `legal.leases-agreements` claims, in its own `one_line`:**

> A person or small team's own agreement records: leases, service and employment agreements, and the
> amendments, schedules, signing evidence, renewals and termination records around them. This safety
> template detects and protects an executed-agreement lifecycle; the fieldless Legal schema
> authorizes no agreement facts and no deep destination tree.

Read strictly, that sentence is **more aggressive than the gist draft assumed**. It does not stop at
the instrument. It claims *"renewals and termination records"* and its `work_types` list includes
"amendment, addendum or variation", "renewal or extension", and "termination, cancellation or
non-renewal notice". **The renewal notice is claimed by `legal` too.** The gist draft's "the
instrument stays with legal, the administration is ours" was therefore too clean, and this pass
narrows the claim accordingly.

**Two constraints fall out of that sentence, exactly as they did for `subcontract`:**

- *"the holder's own agreement"* — the holder is a **party**. A supplier contract satisfies that.
  **This does not separate the two rows**, and it is why "a company holds it" fails as a
  discriminator.
- *"an executed-agreement lifecycle"* — singular. The instrument and the paperwork of *its* own
  execution, amendment, renewal and termination.

**That singular is the seam.** `legal.leases-agreements`' unit is **one agreement and everything
around it**. This row's unit is **many agreements and the apparatus that manages them at once**. Read
across into that row's own idiom — its formula, repeated verbatim across three of its own
collisions, is *"Party recitals, continuing obligations and execution support this agreement
situation; [structure X] supports [neighbour]"*:

| Evidence | Reading |
|---|---|
| party recitals, reciprocal obligations, numbered clauses, defined terms, a governing-law clause and an **execution block** — the signed MSA, its deed of variation, its termination letter | **`legal.leases-agreements`** — an executed-agreement lifecycle. `legal` is a safety domain; its protective ordering runs first. |
| a **portfolio register** over many agreements with a **notice-date column** and an **internal contract owner**; an obligation tracker keyed to **clause references**; a service-credit report; a contract abstract produced to run the thing | **this row** |
| a counterparty name, a money figure, a date-shaped token, or a signature block | **neither.** *"A signature block alone counts for neither"* — that row's own phrasing, four times over, adopted here unchanged. |

**Stated as a per-evidence-item mutex, not a file-level winner.** `MSA - Acme Ltd - executed.pdf` is
legitimately named on both sides: this row's JSON carries it with `also_schema: "legal"` and routes
it to **Protected Records** when inactive. **The same bytes are named on both sides**, per the
addendum's requirement, and in the other direction
`Deed of variation - 14 Bridge Street - signed.pdf` is the file that must not be lost **to** this row.

**Where the seam is written from one side only, said openly.** `legal.leases-agreements` landed
before this family and names no `business_operations` row anywhere in its own file. R1c owes the
reciprocal — **NJ-BO-CA-2**. This is the *same* debt `construction_property.subcontract` records
(*"R1c owes the reciprocal. Filed as NJ-CP-SUB-3"*) and that
`construction_property.construction-project` records in identical terms. **One debt, three
creditors**, and it should be settled once.

---

## The activity charge — is "contract administration" a `work_type`?

The dispatch's second charge, and the more dangerous one. It is a real risk: the row's *name* is a
gerund, and a gerund names an activity. Three reasons it is nevertheless a node, none of which rests
on deference:

1. **A `work_type` value cannot carry a different detection method; only a template can.** This is
   the `business_operations` family's own decisive move, and `construction_property`'s
   (*"a `work_type` value cannot carry a different detection method; only a template can"*, used
   there to demote `progress-photos`). The register table is a different *detection method* from
   reading an instrument's recitals — a table-cell read versus a body-prose read, 00's own two
   channels. A value inside `legal`'s template cannot produce that.
2. **The artifacts outlive the activity and have their own shape.** The row does not activate on
   anyone administering anything. It activates on a table with a notice-date column, which exists as
   a durable object whether or not anyone is currently administering. This is the same reason
   "budget" is a row and "budgeting" would not be.
3. **The name is admittedly bad, and the JSON now says what the row actually is.** The `one_line`
   was amended in this pass to lead with the portfolio structure rather than the activity, and to
   state explicitly that the organisation-holds-it reading is *not* the discriminator.

**The concession:** several of this row's `work_types` — "notice letter", "amendment, variation, or
change order", "executed agreement or counterpart" — are genuinely values that `legal` also lists.
They are kept as values here because a value may appear in two templates' enums; that is what values
are. They are not evidence for the row, and none of them appears in `recognition.deterministic` as a
standalone signal.

---

## Files considered and rejected

Preserved from the gist pass, with two additions and one promotion:

- **`NDA template - mutual.docx`** with tracked changes — kept as a file example and a collision
  fixture. A template and a redline are negotiation artifacts. Falls through to **Reference Clips**,
  which 00 defines for *"material that is useful for later retrieval but does not belong to a
  current project"*.
- **`Employment contract - J Okafor - signed.pdf`** — kept. The shape matches perfectly and the
  counterparty is a person; the employee's own record and the employer's people record both have
  better claims, and the stricter side wins.
- **`PO-2026-0331.pdf`** — kept, because it is honestly three rows at once (procurement's output,
  this row's call-off evidence, an accounting document) and the row should not pretend otherwise.
- **An insurance certificate held under a contract** — real, kept as a `work_type` rather than a file
  example, because `finance.insurance-corporate` has landed and owns the artifact. That row's own
  formula (labelled Named Insured, Policy Number, Policy Period and coverage tables) is not
  contested here.
- **A signing-platform audit trail / certificate of completion** — considered and rejected as a
  signal. It is a receipt of *execution*, which is the instrument's own lifecycle;
  `legal.leases-agreements` lists "signing certificate or audit report" in its `work_types` and is
  right to. The row keeps the archive and receipt fallthroughs for the bundles these arrive in.
- **NEW — `Supplier register.xlsx`** — promoted from "not considered" to the row's sharpest collision
  fixture, and the reason the gist's central claim was narrowed. See § *The gist pass's central
  claim*.
- **NEW — `Deed of variation - 14 Bridge Street - signed.pdf`** — added as the reverse-direction
  fixture the addendum requires: the file that must not be lost **to** this row.
- **A contract-management SaaS export (CSV) of a register** — considered as a distinct example and
  rejected as a duplicate of `Contract register - live agreements.xlsx`; it adds a source but no new
  discrimination, and adding it would be padding.

---

## The collision fixture, named — in both directions

**Fires this row and must not:** `Supplier register.xlsx`. One row per supplier, an internal owner, a
status, a spend band, a review date. It has the register *structure*, the internal-owner slot, and a
date column — three of the four things this row looks for. **What discriminates it:** no contract
reference and no notice date; the date it does carry is a *review* date, a cadence rather than a
deadline. It is `business_operations.vendor-management`'s, and that row's own JSON describes exactly
this table. Named on both sides.

**Must not be lost to this row:** `Deed of variation - 14 Bridge Street - signed.pdf`. An amending
instrument with a parent-agreement reference, a numbered variation, and an execution block — this
row's amendment structure, complete. **What discriminates it:** it is one individual's own tenancy
paper with no register, no diary and no portfolio around it. `legal.leases-agreements`, a safety
template; stricter side wins; **Protected Records** when this row does not fire.

**And the file that is honestly both:** `MSA - Acme Ltd - executed.pdf`, carried with
`also_schema: "legal"`, named identically on both sides of the seam.

---

## Reciprocal boundaries, both directions

Ten collisions are now authored. The four that matter, each stated in both directions, each checked
against the neighbour's own landed file:

**↔ `business_operations.vendor-management`** — the family's thinnest pair, and both rows say so in
the same words. That row's own signal reads: *"an executed instrument with clauses, schedules and
signature pages, plus the obligations register, notice dates and renewal correspondence that run it,
supports contract administration; the counterparty's own standing - diligence, insurance,
performance, exit - supports this row."*

> **Divergence, stated openly rather than silently reversed.** That sentence gives *"an executed
> instrument with clauses, schedules and signature pages"* to **this** row. **This row declines it.**
> The instrument is `legal.leases-agreements`' — see the seam above — and accepting the gift would
> put this row in direct conflict with a landed safety row. The half of that sentence this row does
> accept, and reciprocates exactly, is *"the obligations register, notice dates and renewal
> correspondence that run it"*. Against `vendor-management` the boundary is therefore: a **contract
> reference and a clause reference** support this row; a **supplier identifier, a bank-detail block,
> a diligence questionnaire or a review date** support that one. `vendor-management`'s file is not
> edited; the divergence is recorded here and in NJ-BO-CA-3 for R1c.

**↔ `business_operations.procurement-sourcing`** — the boundary is the signature, and both sides
already say so identically. That row: *"executed signature blocks, an obligations register, notice
periods and renewal dates support contract administration; the competition that preceded signature
supports this row."* Reciprocated unchanged, with the same one-word narrowing: a solicitation
reference, a bid deadline, a clarification log or an evaluation matrix support procurement; anything
whose reference points *backwards* to an executed agreement supports this row. **Same bytes named on
both sides:** `PO-2026-0331.pdf`, carried in this row's file examples with *"which row owns it: a
purchase order is procurement's output, this row's call-off evidence, and an accounting document at
once"*.

**↔ `business_operations.customer-account-management`** — that row: *"a notice clause, a register
entry and a formal letter support contract administration; an account plan, a usage record and an
internal renewal recommendation support this row."* Reciprocated verbatim in substance. The seam is
**obligation versus relationship** on the same renewal date, and both rows name the renewal
spreadsheet as the shared object.

**↔ `construction_property.subcontract`** — sector-statutory versus general-commercial. A site, a
works package, a valuation number, or a **statutory payment-notice** reference supports that row; a
general commercial register and notice calendar supports this one. That row's file is not
contradicted: it argues the same instrument-versus-apparatus seam against the same creditor, and this
row adopts its formula rather than competing with it.

Six further collisions — `legal.leases-agreements`, `legal.practice-matter-file` (new),
`law_practice.contract-negotiation`, `government.public-procurement`,
`career.consulting-client-engagement`, `business_operations.compliance-audit` (new) — are argued in
the JSON with the same both-directions discipline.

---

## Neighbours considered that did **not** get an edge

- **`retail_hospitality.catering-contract`, `retail_hospitality.supplier-order`,
  `logistics.shipment`** — sector instances of the same situation. Left unedged: the
  `construction_property.subcontract` collision already carries the sector-statutory-regime
  discriminator once, and repeating it three times would be volume, not coverage.
- **`finance.subscriptions-utilities`** — a personal subscription is a contract with a renewal date
  and is structurally near-identical, and `legal.leases-agreements` already draws that seam from its
  own side (*"Party recitals, continuing obligations and execution support this agreement situation;
  service or account identifier plus covered period, usage, billed amount or account state supports
  finance.subscriptions-utilities"*). Not edged from here, because the discriminator that would
  apply is whose-record-is-it, and this row must not lean on that. Noted for R1c.
- **`finance.small-business-bookkeeping`** — a vendor invoice under a contract. Not edged: the
  invoice is not this row's evidence at all, and `legal.leases-agreements` already carries that seam
  (*"invoice identifier, line-item table, due slot and payment-status or reconciliation structure
  support finance.small-business-bookkeeping"*).
- **`hr.onboarding-offboarding`** — the employment-contract case. Handled inside the row's own file
  example (`Employment contract - J Okafor - signed.pdf`) rather than as an edge, because this row
  never wins it and an edge would imply a contest.
- **`business_operations.risk-register`** — a register with likelihood/impact scoring columns is a
  different table, and the schema anchor already assigns that structure there. No overlap once both
  are read as structures rather than as the word "register".

---

## `proposed_fields` — two seconds, no mints

**No key is minted here.** Both entries are seconds of the `business_operations` schema row's own
proposals, so R1c settles each once across the family rather than per sibling.

- **`organization`** — seconded, with this row's own datum, which is **negative and worth having**:
  the custody question is hardest here, because a parties block yields two entity names of equal
  prominence and no role marker. `organization` as proposed would name whose drawer the file is in
  and would still not tell a supplier contract from a customer contract. Seconded as useful, flagged
  as insufficient.
- **`fiscal_period`** — seconded **weakly**, with the objection stated. This row is not one of the
  four annually-cycling rows whose need the schema row's argument rests on. Its periods are
  *contract* periods running on the agreement's own anniversary and routinely straddling two fiscal
  years, so filing a renewal notice under a fiscal period would separate it from the expiry it
  answers. Seconded for the family, declined as a level here.

**The hole that is named and deliberately not filled:** the **supplier / buy-side** role has no
canonical key. 00's pair is `our_firm` / `client`, from *"A consulting document may mention the
author's firm and the client organization."* — the professional-services reading. A buy-side
register's counterparty is a **third** role. This is the clearest place in the family where a
`supplier` key would be proposed and this row deliberately does not mint one; a near-duplicate of a
canonical key is the defect D6 exists to kill. It is recorded as a `role_split` entry instead —
the same shape `construction_property.subcontract` uses for its own three-party failure. **One hole,
two witnesses.**

---

## Sparse-file discipline

`HW 3.pdf`'s analogue here is a bare `Notice.pdf` or `Renewal.docx` in a counterparty folder, and 00's
rule is followed exactly: *"The graph does not automatically copy those missing facts onto sparse
files."* Such a file may join a P9 group without this row activating from its filename — CONNECTION
§3's activation ≠ grouping — and eight of the twelve file examples carry
`group_without_copying_facts: true` for that reason.

The stop rules apply as written, and one bites unusually hard here: *"when members carry
irreconcilable course, institution, project, term, or purpose facts"*. Two counterparties' files in
one contracts folder do not merge, and a counterparty name is precisely the *"one high-frequency
entity acting as the only bridge"* the same sentence forbids. The `Contract register` example is the
row's own worst offender — it spans many contracts, which is a real reason it may join **no** group,
and the JSON says so.

Where nothing settles, abstention: *"A model that cannot cite sufficient evidence must return
unknown."*

---

## NEEDS-JOSEPH

- **NJ-BO-CA-1 · The buying-side role has no canonical key.** Widen `client`, mint `supplier`, or
  rely on `organization`? This row seconds `organization` and records that it would not close the
  hole. For R1c. (Renamed from the gist's NJ-BO-8; same question, and it now travels with
  `construction_property.subcontract`'s identical three-party finding.)
- **NJ-BO-CA-2 · The `legal` reciprocal is owed.** `legal.leases-agreements` claims *"renewals and
  termination records"* and lists renewal, variation and termination notices in its own
  `work_types`, and names no `business_operations` row. The seam above is written from one side.
  **Same debt, three creditors** — `construction_property.subcontract` and
  `construction_property.construction-project` record it too. Settle once.
- **NJ-BO-CA-3 · Is this row's single surviving structure enough, and is `vendor-management`
  genuinely separate?** Two halves of one question. This pass conceded legs 2 and 3 and narrowed
  leg 1 to the notice-date-plus-contract-owner register. The row passes CONNECTION §2 on that, but
  with the thinnest margin of any row in this family. If R1c judges the margin too thin, the correct
  outcome is to refuse this row and route the register to `vendor-management` with the coverage
  falling through to **Review Later** and **Independent Records** — the alternatives and their cost
  are stated rather than smoothed. The cost of refusing: the register, the obligation tracker and the
  notice calendar have no home, and `legal` explicitly declines a deep destination tree for them.
  (Supersedes the gist's NJ-BO-9, which asked the second half only.)

---

## Audits run before returning

- `python3 -m json.tool` — **parses.**
- **25 curly-quoted spans machine-verified verbatim** against `00-database-agent-product-design.md`
  (whitespace- and smart-quote-normalised) — **zero failures.** One span quoting a *sibling node
  file* rather than 00 was converted from curly to attributed prose so the two can never be
  confused.
- **Key set compared field-by-field against `construction_property.subcontract.json`** (a landed
  J-DEPTH row in the same schema-family shape) — **identical, same order.**
- Every `collides_with.domain` and `role_split.other_domain` resolves to a `roster.json`
  `domain_id` — **11/11.**
- Every `falls_through_to.residual_template` is one of 00 §7.3's nine names — **6/6.**
- Every `file_examples.source_type` and every `file_kinds.source_types` entry is in
  `src/evidence_shape/vocabulary.py`'s `SOURCE_TYPES` — **12/12 and 9/9.**
- `fields: []`, `launch: "placeholder"`, `refuse_node: false`; no canonical key minted; no threshold,
  statistic, confidence score, file count or handling class anywhere.
- No file written outside the two assigned paths.

---

## What changed in this pass

**Preserved unchanged** (the gist draft was verified, and it was right about most things): the
situation and its `one_line`'s substance; all nine deterministic signals; all seven `needs_llm`
entries; the nine original `never_alone` entries; the 33 `proposed_context_terms`; the 14
`work_types`; the six `grouping_reasons`; the empty-by-contract `dimension_order` with its prose
recommendation; all ten original `file_examples`; the eight original collisions; all six
`falls_through_to` entries and their quotations; `sensitivity` and its reasoning; and the decision
not to mint a `supplier` key.

**Added or changed:**

- **`one_line`** — now leads with the portfolio structure and states explicitly that
  organisation-versus-person is *not* the discriminator.
- **Two `never_alone` entries** answering the dispatch's two charges directly: the
  organisation-holds-it trap, and the administrative-verb-as-node trap.
- **The node test argued leg by leg**, with **legs 2 and 3 conceded** — the gist implied support
  from both. The row now rests on leg 1 alone, and says so.
- **The gist's central claim narrowed**: "a notice-date column appears in no other family's tables"
  → "a notice date *and an internal contract owner* alongside a *contract reference*", after
  `vendor-management`'s review-date column was found.
- **Two new file examples**, both required by the addendum: `Supplier register.xlsx` (fires wrongly)
  and `Deed of variation - 14 Bridge Street - signed.pdf` (must not be lost to this row).
- **Two new collisions**: `legal.practice-matter-file`, `business_operations.compliance-audit`.
- **The `legal.leases-agreements` collision rewritten** in that row's own idiom, following
  `construction_property.subcontract`'s formula deliberately, with the reciprocity debt named.
- **Two `proposed_fields` seconds** where the gist had none — `organization` and `fiscal_period`,
  each carrying this row's own datum, and the second one carrying an objection.
- **A `role_split` entry** where the gist had none, recording the three-party role failure.
- **A divergence from `vendor-management` stated openly** rather than silently reversed: this row
  declines the instrument that row's collision text hands it.
- **`open_question` expanded** from two to three, the third being the reciprocity debt.
- **New sections**: 00-never-mentions-a-contract; the activity charge; the collision fixture in both
  directions; sparse-file discipline; the audit log; this section.

**This memo is at the lower end of the J-DEPTH band, and that is deliberate.** The honest finding of
this pass is that the row survives on *one* structure rather than on a broad case, and inflating the
memo would misrepresent how thin that is. What could have been padded — a fourth sector collision,
a duplicate register example, a restatement of the family posture already stated in the anchor — was
cut for that reason.
