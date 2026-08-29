# construction_property.subcontract — research notes

Depth: J-DEPTH. Placeholder row (J-IND, deepened under the ratified J-DEPTH standard of 2026-08-24).
Absorbs legacy id `cons.subcontract` (ROSTER.md Appendix A).

**Verdict: the row STANDS — but not for the reason the gist pass gave.** The gist memo rested the
whole node on "the statutory payment cycle … exists nowhere else in this catalogue". That claim is
**false**, and this pass reverses the *reasoning* while upholding the *verdict*. See
*The gist pass's central claim, and why it does not survive* below. The row survives on two other
legs, argued in full.

---

## Sources actually used

### Binding local sources

- `planning/00-database-agent-product-design.md` — authoritative. Every quotation in this memo and in
  the JSON was grep-matched verbatim against this file before writing. No paraphrase is presented as
  a quote.
- `planning/domains/CONNECTION.md` — the node test (§2), `also_holds_with` vs `collides_with`,
  activation ≠ grouping, browse-only parent (§3), closed edges (§5), PR-6.
- `planning/domains/_CONTRACT.md` — rules 5, 8, 10, 11–15. Rule 10/15 is why `dimension_order` is
  empty here and why the tree recommendation is held as prose.
- `planning/prompts/ALIGNMENT.md`, `planning/domains/roster.json`,
  `planning/domains/canonical_fields.json` (37 keys, all `design` provenance — **none minted here**).
- `planning/overnight/council/DECISION-BRIEF.md` — D1 (as narrowed), D6, PR-6, J-IND taken as
  ratified and not re-debated; J-DEPTH overrules J-IND's gist clause, which is why this pass exists.

### The schema anchor, read first

`construction_property.research.md` (43KB, J-DEPTH). This row's node test is measured against the
paragraph that memo publishes as **the default template every sibling must differ from**:

> **`property` or site → `instruction` (the job, the letting, the scheme, the block) → document
> function**, with a period level only where the situation *genuinely cycles* (a service-charge year,
> a rent-review cycle). **Not time-first.**

Two of the schema memo's instructions bind this row directly and are obeyed below:

- *"`variation`, `snagging`, `dilapidations`, `retention`, `preliminaries`, `certificate`, `drawing`,
  `schedule`, `survey`, `valuation` and `report` are **values of `work_type`**, not rows."*
  `retention` appears in that list. **This row therefore may not claim retention as its node.**
- *"Reversing is not a difference that earns a node."* This row does not claim the reversal.

### The family spine, read second

`construction_property.construction-project.research.md` (38KB, J-DEPTH). The dispatch asks first
whether this row is merely part of that row's lifecycle. **The spine itself answers no, in writing,
and it demoted itself to make room:**

> Similarly `variation-claim` owns the numbered instruction, `site-diary` owns the dated daily
> record, and `subcontract` owns the works package. The gist row claimed all of them.

and, in its own reciprocal table:

> | `construction_property.subcontract` | the enquiry, order, competence evidence and payment cycle of
> engaging another firm | the head contract those packages deliver |
> `Sub-contract order 2431-08 groundworks.pdf` |

That is a landed J-DEPTH neighbour ceding this territory explicitly and naming the shared fixture.
This pass adopts its wording rather than re-authoring it, and names the **same bytes** on this side.

### Landed neighbours read before writing, and not rewritten

- `construction_property.final-account.json` — the most dangerous neighbour, and it had **already
  written this row's discriminator on its own side**. Adopted verbatim below.
- `legal.leases-agreements.json` + memo (52KB / 24KB, J-DEPTH) — the load-bearing cross-schema seam.
- `construction_property.timesheet.json` — a landed **refusal** whose reasoning is directly on point.
- `construction_property.compliance-certificate.json` — the family's other refusal; the model for
  what refusing well looks like, including `falls_through_to` routing.
- `business_operations.contract-administration.json`, `.vendor-management`, `.procurement-sourcing`.
- `construction_property.site-health-safety`, `.variation-claim`, `.plant-hire`, `.quote-estimate`,
  `.materials-delivery`, `.snagging-defects`.
- `business_operations.organisational-records.json` — the refusal standard.

**Five siblings independently name this row in their own `collides_with`, and four of the five reach
for the same discriminator without coordinating.** `plant-hire`: *"an engagement to carry out works,
with insurances and competence evidence, supports the subcontract row"*. `quote-estimate`: *"an ORDER
framing with an engagement, insurances and competence evidence supports the subcontract row"*.
`site-health-safety` and `construction-project` say the same thing in their own words. That
convergence is evidence, not decoration: the family has already agreed, in five separately-authored
files, that **engagement-plus-competence-evidence** is what identifies this situation. It is not what
the gist memo argued, and it is what this pass argues.

---

## The gist pass's central claim, and why it does not survive

The gist memo said (quoted verbatim from the draft this pass replaces; recoverable at `git show HEAD:planning/domains/nodes/construction_property.subcontract.research.md`):

> The **statutory payment cycle**. […] That produces a document pair — application and answering
> notice — that exists nowhere else in this catalogue.

**This is wrong on two counts, and it is wrong against files that were already on disk.**

1. **`construction_property.final-account` holds exactly that pair**, and says so in its own
   `recognition.deterministic`: *"a payment-notice structure: a notice naming the sum the issuer
   considers due and the basis on which that sum was calculated"*, and *"a pay-less or withholding
   notice: the same contract and valuation reference, a LOWER sum than the one applied for … which makes the pair a structural unit"* The application/notice pair is that row's fingerprint at the head-contract
   level. Two rows cannot both be recognised by the same structure being unique to them.
2. **The schema anchor claims the underlying arithmetic at *schema* level**, in its own leg 2:
   *"The `to date, less previously certified` shape … exists in this world and, as far as this pass
   could establish, nowhere else in the catalogue."* A signal the schema claims for itself is by
   construction part of the **default template**, and CONNECTION.md §2 asks how a row **differs from
   the default**. Claiming the schema's own signal as your row's difference is claiming nothing.

Stating the disagreement explicitly, as the deepening addendum requires: **I am reversing the gist
memo's argument.** The payment cycle is real, it is genuinely peculiar to this industry, and it does
belong in `recognition.deterministic` here — as a *supporting* structure that places a file in this
**family**. It cannot carry the node on its own, because the family already owns it twice over.

What the payment cycle *does* contribute here is **direction**, and that contribution is licensed by
the neighbour rather than asserted — see leg 1.3.

---

## The node test, all three legs, argued

CONNECTION.md §2: a template row exists only when its **detection signals**, its **recommended
dimensions**, or its **privacy rules** differ from its schema's default template. Any one leg
suffices. All three are examined, and one of them is reported as **failing**.

### Leg 1 — detection signals of its own — **PASSES**, on two structures the family leaves unclaimed

Four candidate structures were tested. Two carry the leg; two only support it.

**1.1 The pre-appointment competence and standing pack. — carries the leg.**

A purpose-coherent bundle assembled *about a counterparty firm, before it is allowed to start*:
employer's and public liability certificates with limits and expiry dates, accreditation or
membership certificates, a completed health-and-safety pre-qualification questionnaire, a tax or
employment-status verification record, sometimes a collateral warranty or parent company guarantee.

Why this is a *structure* and not a document-type list: its members are **individually unremarkable
and collectively diagnostic**, which is `00`'s own named pattern — *"The documents are
content-incoherent but purpose-coherent."* An insurance certificate on its own is a finance record.
An accreditation certificate on its own is a certificate. **Assembled about one firm as a condition
precedent to engaging it, they are a fitness-to-engage file, and no other row in this catalogue holds
that assembly.** `site-health-safety` holds hazard matrices, permits and briefing registers — safety
apparatus about *the works*. `finance.insurance-corporate` holds *the holder's own* policies.
`business_operations.vendor-management` is the nearest genuine rival and is edged reciprocally below.

The decisive property, and it is an unusual one: **this pack is about a third party's corporate
standing, held by someone who is not that party.** Nothing else on this schema is *about another firm
rather than about a building*. That is a different subject class, not a different document type.
Provenance: **inference**, argued from the named real document types, not quoted from `00`.

**1.2 The engagement-failure sequence. — carries the leg.**

A back-charge or contra-charge record — a deduction against a named counterparty's account with a
description, a cost build-up and a notice of intention to deduct — and, beyond it, a notice to remedy
within a period, a warning of determination, and a final account of works completed by others.

This is **not** the payment cycle and it must not be conflated with it. `final-account` owns the
dispute *about a sum*: its pay-less notice is *"a written allegation of defective or incomplete work
against a named counterparty"* in its own words. What is unclaimed here is the apparatus for
**ending the relationship**: remedy periods, determination warnings, and the arithmetic of having
someone else finish the work. `snagging-defects` owns defects after practical completion;
`variation-claim` owns claims upward against the employer; neither owns termination of an engagement
downward. Provenance: **inference**.

**1.3 Direction — the holder as payer. — supports, does not carry, and is licensed by the neighbour.**

`final-account` wrote this row's discriminator on its own side before this pass ran:

> Payment applications and payment notices run down the chain in exactly the same form, so the firm's
> own application to its client and its subcontractor's application to it are structurally identical
> documents. The discriminating evidence: which agreement the reference names - a subcontract or
> order reference with the firm as payer supports the subcontract row; the main contract reference
> with the firm as payee supports this row. **A valuation number alone discriminates neither.**

That is adopted here **unchanged and reciprocally**. Note what it actually licenses: the *reference*
— which agreement is named — plus the *role* the holder occupies. It does **not** license reading
direction from the document shape, and it explicitly kills the valuation number as a discriminator.
Direction is therefore a `needs_llm` determination, and it is recorded as one.

**1.4 The package comparison. — supports, does not carry.**

A table of several *rival firms* against one common scope, with prices, qualifications, exclusions
and a recommendation. Tempting, and the gist memo listed it. But `construction-project` claims *"The award sequence."* … *"An invitation to tender, a tender report, a letter of intent, and a letter of acceptance"* as **its** leg-1 structure. A package comparison is that structure one level down the
chain. The difference is *whose award*, which is direction again (1.3), not a new shape. Kept as a
signal; **not** counted toward the leg. Honest note: the *tabular* comparison of N firms column-wise
does differ from a prose tender report, but that is a formatting difference and `_CONTRACT` will not
let a format be a node — the standing dispatch prompt's own rule, *"those are values and `SOURCE_TYPES`, not nodes"*

**Verdict on leg 1: passes, on 1.1 and 1.2.** Narrower than the gist claimed, and honestly so.

### Leg 2 — recommended dimensions of its own — **PASSES**, and this is the strongest leg

The schema default roots the tree at **`property`**. This row is the one situation on the schema
where **the property is not the root, and frequently is not present at all.**

The subject of this row is a **counterparty firm**, and a firm's records cut *across* properties:

- Insurance and accreditation certificates expire on **the firm's** calendar, not the project's. One
  certificate is demanded on every live project simultaneously.
- A retention schedule is kept **per firm across projects** — the fixture `Retention schedule
  2026.xlsx` in this row's JSON is one sheet spanning several projects, and its `must_not_conclude`
  says so.
- An approved-subcontractor record, a performance history and a contra-charge ledger all key on the
  firm and would be shredded by a property-first tree.

So the honest recommendation here is **counterparty firm → engagement (package on a project) →
document function**, with the property appearing *inside* the engagement level rather than above it —
and, for the compliance half, **not appearing at all**.

Three things must be said about that, or the leg is dishonest:

1. **This is not the licensed reversal.** The schema memo permits `instruction`-before-`property` for
   one-job-one-address rows and warns that *"Reversing is not a difference that earns a node."* This
   row is not reversing the two default levels; it is **introducing a level the default does not
   contain** — the firm — which is orthogonal to the property and which the default tree has no slot
   for. That is a different kind of departure and it is the one CONNECTION.md §2 is asking about.
2. **It is a recommendation, not a filesystem.** *"The system recommends an order based on the domain
   template, but the user can reverse, remove, add, or flatten dimensions."*
3. **`template.dimension_order` is empty anyway**, by binding contract: a dimension may only branch on
   a field the same entry's schema declares, and `construction_property` declares none (D1 as
   narrowed, PR-6, `_CONTRACT` rules 10 and 15). A dimension naming an undeclared field opens a tree
   level no fact could ever fill. **The prose above is the recommendation for the pass that may
   license fields; it is not shipped as a tree.** This is why `proposed_fields` seconds `organization`
   rather than minting a subcontractor key — see below.
4. **Not time-first**, despite a monthly cycle. *"For document and record domains, project, function,
   or subject usually comes before time because putting year first scatters related work across
   calendar folders."* A month-first tree would scatter one package's running account across two
   calendar years and break the continuity that makes it checkable — the same reasoning
   `final-account` gives, and it is not contradicted here.

**Verdict on leg 2: passes cleanly.**

### Leg 3 — privacy rules of its own — **DOES NOT CARRY THE NODE**, and this pass says so

The material here is another firm's price, margin, insurance limits, accreditation status, failures
and back-charges, plus — where the subcontractor is a sole trader — that individual's tax deduction
statements and competence cards. `00`'s corpus sentence names those categories: the corpus *"can
include identity documents, account statements, tax records, medical information, legal records,
credentials, private correspondence, GPS metadata, employment materials, and educational records"*.

But **that is the schema's posture, not a departure from it.** The schema anchor's own leg 3 already
rests on *"The exposed party is usually not the user, and cannot consent"*. This row exposes a
different party — a counterparty business rather than an occupier — for the *same* reason, at the
*same* catalogue value (`potentially_sensitive`). A different victim is not a different rule.

The `timesheet` refusal is the controlling precedent and it is followed rather than dodged: it found
its privacy posture genuinely different from the schema's, and concluded *"that is an argument for
routing the material AWAY from here, not for a node."* The same discipline applies here in a milder
form. Where a file's dominant reading is a sole trader's personal tax record, `finance`'s protective
ordering runs first and this row does not claim it outright — which is exactly what the JSON's
`CIS statement March 2026.pdf` fixture already says.

**Verdict on leg 3: does not carry.** Recorded as a fail so the row's real support is legible.

### Overall

**Kept, on legs 1 and 2.** The row would still stand if leg 3 were struck out entirely, which is the
test of whether the other two are real.

---

## Is this row `legal`'s material wearing a construction label? — the load-bearing seam

The dispatch is right that this is the sharpest challenge: a subcontract is a contract, and `legal`
already owns contracts at full depth. `legal.leases-agreements` was read in full before this section
was written, and **nothing below contradicts it.**

**What that row actually claims**, in its own `one_line`:

> A person or small team's own agreement records: leases, service and employment agreements, and the
> amendments, schedules, signing evidence, renewals and termination records around them. This safety
> template detects and protects an executed-agreement lifecycle.

Two constraints fall straight out of that sentence:

- **"the holder's own agreement"** — the holder is a **party**. That is satisfied by a subcontract:
  the contractor is a party to it. So this does not separate the two rows.
- **"an executed-agreement lifecycle"** — the *instrument* and the paperwork of its execution,
  amendment, renewal and termination.

**What separates them is the same thing `legal.leases-agreements` uses to separate itself from every
one of its other fifteen neighbours: instrument versus running apparatus.** Its own repeated formula,
across `finance.household-property`, `finance.hoa-residents-association` and
`finance.subscriptions-utilities` respectively:

> Party recitals, covenants, grant of occupancy, consideration and execution support this agreement
> situation; issuer plus receipt, inventory, inspection, tax or improvement structure supports
> finance.household-property.

> Party recitals, reciprocal obligations and an execution block creating or amending duties support
> this situation; member-account, governance, meeting or routine association-administration structure
> supports finance.hoa-residents-association.

> Party recitals, continuing obligations and execution support this agreement situation; service or
> account identifier plus covered period, usage, billed amount or account state supports
> finance.subscriptions-utilities.

**Read across, in that row's own idiom, and the seam draws itself:**

| Evidence | Reading |
|---|---|
| party recitals, reciprocal obligations, numbered clauses and an **execution block** — the signed subcontract instrument, its deed of variation, its collateral warranty, its parent company guarantee | **`legal.leases-agreements`** — an executed-agreement lifecycle. `legal` is a safety domain and its protective ordering runs first. |
| the **running apparatus** around that instrument — the enquiry, the comparison, the competence and insurance pack, the numbered applications, the assessments, the notices, the retention ledger, the contra-charges | **this row** |
| an address, a firm name, a money figure, a signature block | **neither.** *"A signature block alone counts for neither"* is that row's own phrasing, four times over. |

**The consequence, stated as a per-evidence-item mutex rather than a file-level winner:** the
subcontract order PDF is legitimately named on both sides. This row's JSON already carries
`also_schema: "legal"` on `SC-044 Meridian Groundworks - order.pdf` and routes it to **Protected
Records** when inactive; that stands and is now argued rather than asserted. **The same bytes are
named on both sides**, per the deepening addendum's requirement.

**Where I diverge, and I say so openly rather than silently:** `legal.leases-agreements` does not name
`construction_property` anywhere in its own file — it landed before this family. The seam above is
therefore **stated from one side only**, in that row's own vocabulary, and **R1c owes the
reciprocal**. Filed as NJ-CP-SUB-3. `construction_property.construction-project` records the identical
debt in identical terms (*"`finance.household-property` and `legal.leases-agreements` landed before
this family and do not name `construction_property` in their own memos. R1c owes those two
reciprocals"*), so this is one debt with two creditors, not two debts.

---

## Is this row a document type inside `construction-project`'s lifecycle?

**No, and the spine says so itself** — see *The family spine, read second* above. Three further
reasons, so the answer does not rest on deference alone:

1. **A `work_type` value cannot carry a different tree level.** The schema memo's own decisive move
   for `progress-photos` was that *"a `work_type` value cannot carry a different detection method;
   only a template can."* The identical argument runs on dimensions: the firm-level root in leg 2 is
   a *tree* difference, and a value of `work_type` inside a project-rooted tree cannot produce it.
   The compliance half of this row has **no project at all**, and a value cannot be a level.
2. **The two rows activate on different subjects.** `construction-project` is recognised by
   possession-and-completion, a contract sum, a programme and a handover envelope — all *about the
   works*. This row's carrying structures (1.1, 1.2) are *about a firm*.
3. **CONNECTION.md §3 already answers the intuition that pulls the other way.** A subcontract file
   *does* belong to the job in the **browse** sense. The parent is browse-only and **activation ≠
   grouping**. Belonging to a project folder is not evidence of being the project row's material —
   which is exactly the demotion `construction-project` performed on itself.

---

## Files considered and rejected

Named false positives, with the reason each is not this row's evidence. Preserved entries from the
gist pass are marked; the rest are new.

| File | Why it is not this row's evidence |
|---|---|
| A materials purchase order — `PO 3311 - 40no lintels.pdf` *(preserved; the load-bearing fixture)* | Supply rhymes with subcontract and has none of the machinery. Line items, quantities, a delivery address and payment on invoice → `construction_property.materials-delivery`. |
| An operated-plant hire agreement | `plant-hire` states its own side: *"the supply of a machine at a rate supports this row"*, an engagement to carry out works supports this one. One clause apart in reality, and the discriminator is adopted from that row rather than re-authored. |
| The holder's **own** EL/PL certificates | `finance.insurance-corporate`. This row holds insurance *about someone else, as a condition*. The `must_not_conclude` on the certificate fixture already says *"that this is the holder's own insurance"*. |
| A subcontractor's RAMS or method statement *(preserved)* | `site-health-safety`, reciprocally. Arrives in the same pack; a hazard matrix, permit or briefing register is that row's evidence. |
| A labour-only timesheet from a subcontractor *(preserved)* | `construction_property.timesheet` was **refused**. The pay reading routes to `hr.payroll-benefits-administration` and `finance.payroll-received`; the contractual reading to this row's applications; the dayworks reading to `variation-claim`. That refusal's routing is honoured unchanged. |
| An **agency** timesheet | Named on the refused `timesheet` row as *"a supply-of-labour billing document, which is `construction_property.subcontract`'s payment cycle on one reading and `hr.payroll-benefits-administration`'s on the other"*. Genuinely undecided; abstention is the correct outcome, not a guess. |
| A main-contract interim certificate | `final-account`, on the payee side. The discriminator is the neighbour's own (1.3). |
| A main-contract architect's instruction | `variation-claim`. The cascade downward into a subcontract variation is real and edged, but the instruction itself is that row's. |
| A signed subcontract deed with nothing around it | `legal.leases-agreements`, per the seam above, under `legal`'s protective ordering. |
| An approved-supplier list with performance scores | `business_operations.vendor-management`, unless a works package and a site are present. |
| A blank standard subcontract form or a published notice template | **Reference Clips.** Not a record of an engagement; a form. This is a genuine and common false positive in a contractor's corpus and the gist pass did not name it. |
| A CIS monthly statement *(preserved)* | Not rejected, but **not claimed outright**: a tax deduction statement is a finance record and `finance`'s protective ordering runs first. |
| A payroll run for site operatives | `hr` and `finance` — the schema memo's own rejected-files entry, and it must stay consistent with the `timesheet` refusal. |

---

## The collision fixture, named — in both directions

**Direction A — a file that would wrongly fire this row.**

`PO 3311 - 40no lintels.pdf`. A purchase order for goods: line items, quantities, a delivery address,
payment on invoice terms. It has an order number, a counterparty firm, a site address, a money
figure and a signature — **every never-alone token this row lists, all at once, and none of the
machinery.** What discriminates: **no application/notice pair, no retention, no works package, and a
delivery address rather than a scope.** It routes to `construction_property.materials-delivery`,
with **Receipts and Confirmations** as its residual. Its `group_without_copying_facts` is `false` in
the JSON, deliberately: it must not be pulled into a package group.

**Direction B — a file that must not be lost *to* this row.**

`Sub-contract order 2431-08 groundworks.pdf` — the fixture `construction-project` names on its own
side, reproduced here byte-identically so the pair can be checked rather than asserted. It is a
subcontract order **and** a main-contract delivery record **and** an executed instrument. Three rows
have a claim:

- **This row** activates on the engaging side — the order framing, the package, the competence
  conditions, the payment terms flowing down.
- **`construction-project`** reads *the head-contract reference on it* and nothing else. Its wording:
  *"The head-contract reference is what this row reads."*
- **`legal.leases-agreements`** takes the executed instrument, and takes it **first**, because
  `legal` is a safety domain.

Per-evidence-item mutex, not a file-level winner. What none of the three may do is copy a fact:
`must_not_conclude` on this fixture already forbids concluding *"which of the two named firms the
filesystem belongs to"*, and that is the whole difficulty in one line.

---

## Reciprocal boundaries, both directions

Every neighbour's own file was read **first**. Where the neighbour had already stated the line, its
wording is adopted rather than re-authored, and **no line below contradicts a landed one**.

| Neighbour | This row must not take | The neighbour must not take | Shared fixture |
|---|---|---|---|
| `construction_property.final-account` *(states its side; adopted verbatim)* | the head-contract valuation cycle with the holder as **payee**; the main-contract reconciliation | the subcontract-referenced application with the holder as **payer**; the competence pack | `Valuation 07 - application for payment.xlsx`; `Application 07 - Meridian Groundworks - Oakfield.pdf` |
| `construction_property.construction-project` *(states its side; adopted verbatim)* | the head contract, the award sequence, the programme, the handover envelope | the enquiry, order, competence evidence and payment cycle of engaging another firm | `Sub-contract order 2431-08 groundworks.pdf` |
| `construction_property.variation-claim` *(states its side)* | the main-contract instruction; the claim against the employer | the subcontract order reference, the application, the payment notice | `AI 014 - relocate soil stack.pdf` cascading down as a subcontract variation |
| `construction_property.site-health-safety` *(states its side)* | the hazard matrix, the permit, the briefing register | the order, the application, the notice | the RAMS-and-insurance pack, `meridian-pack.zip` |
| `construction_property.materials-delivery` | line items, quantities, delivery notes, payment on invoice | the application/notice pair, retention, the works package | `PO 3311 - 40no lintels.pdf` |
| `construction_property.plant-hire` *(states its side; adopted)* | the supply of a machine at a rate | an engagement to carry out works with insurances and competence evidence | an operated-hire agreement, which is one clause from each |
| `construction_property.quote-estimate` *(states its side; adopted)* | an unaccepted price the holder **received or sent** with no order | an order framing with an engagement, insurances and competence evidence | `RE_ price for the groundworks - ok to proceed.eml` |
| `construction_property.snagging-defects` | defects-liability activity after practical completion | a subcontractor's back-charge for its own remedial failure | a snag list attributed to one trade |
| `business_operations.contract-administration` *(states its side; adopted verbatim)* | a general commercial contract register and renewal calendar | a site, a works package, a valuation number, a statutory payment-notice reference | a signed agreement with a change log |
| `business_operations.procurement-sourcing` | a general requirement, an evaluation matrix, an award letter with **no site** | back-to-back main-contract terms, a works package, a site | `Package comparison - groundworks.xlsx` |
| `business_operations.vendor-management` | an approved-supplier list, a scorecard, an expiry tracker with no works package | the pre-appointment pack held **as a condition of one engagement at one site** | an insurance-expiry tracker |
| `finance.insurance-corporate` | the holder's **own** policies and certificates | a certificate held about **another firm** as an engagement condition | `EL and PL certificates - Meridian.pdf` |
| `finance.small-business-bookkeeping` | the invoice, the ledger posting, the tax treatment | the application that precedes the invoice, and the retention that is not yet a debt | a remittance advice |
| `legal.leases-agreements` *(landed first; does not name this family — see NJ-CP-SUB-3)* | the executed instrument, its execution evidence, its deed of variation, its termination record | the enquiry, comparison, competence pack, applications, notices, retention ledger and contra-charges | `SC-044 Meridian Groundworks - order.pdf` |
| `hr.payroll-benefits-administration` | hours, rates and deductions for the purpose of paying a person | a firm-to-firm engagement, which is not employment | an agency timesheet, which counts for neither without more |

### Neighbours considered that did **not** get an edge

- **`hr.onboarding-offboarding`** *(preserved from the gist pass, and it was right)* — considered for
  the competence pack; rejected because a subcontractor is a **firm**, not an employee, and treating
  the two alike is precisely the error that employment-status paperwork exists to prevent.
- **`logistics.shipment`** *(preserved)* — delivery evidence belongs to `materials-delivery`.
- **`legal` / `finance` as schemas** *(preserved)* — real, but expressed as `also_schema` on the order
  and CIS fixtures, because `also_holds_with` joins **schemas** and this is a template row. That is
  why `also_holds_with` is `[]` and it is not an omission.

---

## Sparse-file discipline

The commonest real subcontract in small works is `RE_ price for the groundworks - ok to proceed.eml`
— a price in a thread and a one-line acceptance, with no order, no terms and no reference. The row
must **not** manufacture an engagement from it. Its `must_not_conclude` says so directly: *"whether a
contract exists is not the product's question"*, and it routes to **Review Later**. *"A model that
cannot cite sufficient evidence must return unknown."* *"Correct abstention is a successful outcome
because the product's goal is reliable organization, not maximum file movement."*

The same discipline governs the two structural traps this row is unusually exposed to:

- **The folder-name trap.** A whole subcontractor folder pulled from a document portal is one
  download session, and *"A session should never be treated as proof of topic, and it should not
  carry the same confidence as a hash match or a directly extracted document fact."*
- **The template-metadata trap.** One contractor's order template, filled in by ten different firms,
  carries the same PDF producer and company string throughout: *"PDF metadata should be treated as
  supporting evidence, not as truth."*

---

## `proposed_fields`

**No canonical key is minted.** All three entries are **seconds of proposals the family already
made**, per the dispatch's instruction to second rather than mint variants. The arguments below are
this row's own contribution to those proposals, for R1c to weigh — they are not new keys.

- **`property`** — seconded from `construction_property`. This row's datum for R1c is a **negative**
  one and it cuts against a naive reading: **this is the sibling where `property` is least often the
  right root.** The compliance half of the row has no property at all. That does not argue against
  the key; it argues against `destination_eligible` being read as "always first".
- **`instruction`** — seconded from `construction_property`, including its live alternative (reuse
  canonical `project`). This row's datum: a **works package** is an instruction that is *not* a
  project and *is* nested inside one. If R1c takes the `project`-reuse option, that nesting is where
  it will hurt first.
- **`organization`** — seconded from `business_operations`, **and R1c must settle it once, there, for
  all rows.** This row's datum is the sharpest available: the whole of leg 2 wants a counterparty-firm
  level, and `client` and `our_firm` between them cannot express it — the subcontractor is neither.
  `construction_property`'s `role_split` already records that *the contractor role has no key*; this
  row records the same gap from the other end and **mints nothing**, because minting on a schema that
  declares no fields, at the exact moment it is most convenient, is the 574's original mistake
  performed knowingly. *"The system may create new values when it sees a new course, project,
  company, university, or event, but it should not invent new fields automatically."*

`fields` is `[]`. `proposed_context_terms` carries the practice vocabulary (`application for
payment`, `pay less notice`, `previously certified`, `retention`, `contra charge`, `back to back`,
`works package`, `CIS`, …) as **proposals**, not `00`'s floor.

---

## NEEDS-JOSEPH

- **NJ-CP-SUB-1 · The directional role.** *(preserved from the gist pass, and now with a fourth
  claimant.)* Which side of the engagement the holder is on has no canonical key, and this row is
  where the hole bites hardest because the entire payment machinery is directional — an application
  is something you send **or** something you answer. `business_operations.contract-administration`
  records the same hole as buying-versus-selling; `construction_property.survey-valuation` as
  transaction-side; `construction_property.site-health-safety` as authored-versus-submitted; and
  `construction_property.final-account` has now written payer-versus-payee into its own
  `collides_with`. **Five rows independently want one key. One proposal at R1c, not five variants.**
  *Alternatives and costs:* (a) mint a `role` key — cheap, but it is a fact about the holder rather
  than about the file, which no other canonical key is; (b) leave it to `needs_llm` per row —
  free, but five rows then each carry an unresolved determination and can disagree; (c) let
  `organization` plus `our_firm` imply it — no new key, but it is an inference and would be silently
  `possible` at best. This row recommends (b) until `organization` is settled, then revisit.

- **NJ-CP-SUB-2 · Firm-level compliance evidence versus project branches.** *(preserved.)* A
  subcontractor's insurances and accreditations expire on **the firm's** calendar and are demanded on
  **every** project. Stated reciprocally with `construction_property.site-health-safety`: neither row
  should silently copy a certificate into a project branch. *Alternatives and costs:* (a) file at
  firm level and reference from projects — correct, but the product has no reference mechanism and
  `00` does not license inventing one; (b) copy into each project branch — *"eleven copies of one
  certificate and no idea which is current"*, the gist memo's own phrase and it is right; (c) leave
  the pack ungrouped in **Independent Records** — safe, loses the pack's purpose-coherence. This is
  a filing decision rather than an evidence one, and it needs Joseph, not another row.

- **NJ-CP-SUB-3 · The `legal` reciprocal is owed. — NEW in this pass.** `legal.leases-agreements`
  landed at J-DEPTH before this family and names no `construction_property` row. The instrument /
  running-apparatus seam above is therefore **stated from one side only**, in that row's own
  vocabulary and deliberately not contradicting it. `construction_property.construction-project`
  records the identical debt. **One reciprocal, owed by R1c, covering both.** *Alternatives:* (a)
  R1c adds the edge on the `legal` side using the fixture `SC-044 Meridian Groundworks - order.pdf`
  named here — preferred; (b) leave it one-sided — the two schemas then disagree silently about who
  takes a signed subcontract, which is exactly the failure reciprocal edges exist to prevent.

- **NJ-CP-SUB-4 · Is the pre-appointment pack a *group* or a *situation*? — NEW.** Leg 1.1 rests on
  the pack being an assembly whose members are individually unremarkable. `00` licenses that
  reading — *"The documents are content-incoherent but purpose-coherent"* — but the sentence is
  written about an application submission, not this. If R1c reads purpose-coherence as a **grouping**
  mechanism only, and not as a **detection** signal, leg 1 loses its stronger half and rests on 1.2
  alone. The row would probably still stand; it would stand much more narrowly. Flagged rather than
  smoothed.

---

## Audits run before returning

- `python3 -m json.tool` on the JSON — parses.
- Every quotation in this memo and in the JSON grep-matched verbatim against
  `planning/00-database-agent-product-design.md` or against the named neighbour file. No paraphrase
  presented as a quote.
- Key set compared against `construction_property.final-account.json` and
  `construction_property.construction-project.json` — identical.
- `fields: []`; `proposed_fields` contains only seconds, no minted key; `canonical_fields.json`
  checked for each.
- Every neighbour named in `collides_with` opened and read on its own side; no landed wording
  contradicted, and where wording existed it was adopted rather than re-authored.
- Files written: only `construction_property.subcontract.json` and `.research.md`.

---

## What was preserved, what was added

**Preserved unchanged**, because it was right:

- The verdict (`refuse_node: false`).
- The whole of `recognition` — deterministic structures, the `needs_llm` determinations, and the
  ten-entry `never_alone` list, which is the best thing in the gist draft.
- All ten `file_examples`, their observations, `facts_legal`, `must_not_conclude` and residual
  routing — including the deliberate `group_without_copying_facts: false` on the collision fixture.
- The six `falls_through_to` residuals and their design quotations.
- `work_types`, `grouping_reasons`, `proposed_context_terms`, `sensitivity_why`.
- Both original NEEDS-JOSEPH items, and the rejections of `hr.onboarding-offboarding` and
  `logistics.shipment`.
- The existing eight `collides_with` edges.

**Reversed, with the reason given** *(the addendum requires this be explicit)*:

- **The gist memo's central argument.** "The statutory payment cycle … exists nowhere else in this
  catalogue" is contradicted by `final-account`'s own `recognition.deterministic` and by the schema
  anchor's own leg 2. The `one_line` and the second `recognition.deterministic` entry are corrected
  in the JSON to stop claiming uniqueness. **The verdict is unchanged; the reasoning under it is
  replaced.**

**Added:**

- The node test argued leg by leg, with **leg 3 reported as failing** rather than padded into a pass.
- Leg 1 rebuilt on two structures the family actually leaves unclaimed (1.1, 1.2), with 1.3 and 1.4
  demoted to supporting and the reason given for each demotion.
- Leg 2 as the strongest leg, and the argument for why the firm-level root is *not* the licensed
  reversal.
- The `legal.leases-agreements` seam, drawn in that row's own idiom, in both directions, with the
  same fixture bytes named on both sides — and the one-sidedness declared as NJ-CP-SUB-3.
- The `construction-project` question answered with the spine's own self-demotion quoted.
- A 13-row rejected-files table (five preserved, eight new).
- The collision fixture in **both** directions, with `Sub-contract order 2431-08 groundworks.pdf`
  reproduced byte-identically from the neighbour's side.
- A 15-row reciprocal boundary table, adopting six neighbours' existing wording.
- A sparse-file discipline section, and the folder-name and template-metadata traps.
- `proposed_fields` populated with three **seconds** and this row's own datum for each.
- `role_split` filled.
- NJ-CP-SUB-3 and NJ-CP-SUB-4; NJ-CP-SUB-1 extended to five claimants; alternatives and costs added
  to all four.

**Not added, deliberately:** no new canonical key, no threshold, no file count, no statistic, no
detector regex, no gazetteer content, no P7 handling class, and no `is_safety_domain` flag.
