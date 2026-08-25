# `construction_property.quote-estimate` — research notes (R1b deepening)

**J-DEPTH — deepened 2026-08-25.** Kind: template. Launch: placeholder. `fields: []`.
**Verdict: kept, not refused, but narrowed.** The node is not licensed by the words *quote* or
*estimate*, and not by the existence of a construction price. It stands only for a bounded
**pre-contract enquiry lifecycle**: a site-specific scope is offered or budgeted before work and
before an operative job/instruction exists, it may be revised, and it ends in acceptance, rejection
or silence. A procurement comparison, contract variation, valuation, delivery note and invoice may
contain the same construction subject and value; those states are distinguished structurally below
or the system must abstain.

---

## Sources actually used

### Binding local sources

- `planning/00-database-agent-product-design.md`, the only source quoted as design authority. The
  load-bearing spans are: *“The engine should treat the file extension as a routing signal rather than an assumption about meaning”*;
  *“Tables matter because resumes, forms, applications, invoices, and administrative documents often place their most useful information in cells rather than body paragraphs.”*;
  *“A model that cannot cite sufficient evidence must return unknown.”*;
  *“The documents are content-incoherent but purpose-coherent.”*;
  *“The graph is used as a context-assembly mechanism rather than an automatic label-propagation system.”*;
  and *“The system recommends an order based on the domain template, but the user can reverse, remove, add, or flatten dimensions.”*
- `planning/prompts/ALIGNMENT.md`; `planning/domains/CONNECTION.md`,
  `CONNECTION-EXAMPLES.md`, and `_CONTRACT.md`. These supply the schema/template separation, the
  node test, activation/grouping firewall, closed edges, placeholder constraint, and the rule that a
  template dimension can name only a declared schema field.
- `planning/domains/canonical_fields.json`. No canonical key holds an enquiry, quotation state,
  offer validity or price revision. This template does not mint any.
- `planning/domains/roster.json` and `ROSTER.md` §4 / Appendix A. They confirm this row absorbs
  legacy `trade.quote-estimate` one-for-one and confirm every authored edge target.
- `src/evidence_shape/vocabulary.py` for exact `SOURCE_TYPES`; and
  `planning/overnight/council/DECISION-BRIEF.md` for D1, D6, PR-6 and J-IND. J-DEPTH supersedes the
  old gist instruction; PR-6 still requires `fields: []`.

### Anchor and neighbours read before writing

- `construction_property.json` and `.research.md`, the schema anchor. Its default is
  **property/site → instruction → document function**, period only for a genuine cycle, not
  time-first. Its default recognition includes a measured-works table. Therefore neither a site,
  measured works nor money can distinguish this sibling by itself.
- `business_operations.procurement-sourcing`: bounded competition, solicitation, evaluation and
  award. Its reciprocal edge names this row and `Scan_20260212_quote.jpg` says one non-competitive
  trade quote is not a sourcing event.
- `construction_property.variation-claim`: pricing inside an operative contract, keyed by a numbered
  instruction/variation and often a time consequence. It owed this row a reciprocal on
  `Quotation for VO 17 - revised drainage.pdf`.
- `construction_property.final-account`: cumulative money under contract — application,
  certification, retention and reconciliation. Its reciprocal identifies percentage-complete and
  previously-certified arithmetic.
- `construction_property.materials-delivery`: order-to-arrival paper trail. Its structure is
  dispatch/receipt evidence, not a price offered before commitment.
- `finance.small-business-bookkeeping`: invoice, tax, payment terms, posting and ledger state, the
  principal invoice neighbour named by search.
- `finance.household-property`: receiving custody of builders' prices about the holder's home. The
  same PDF exists on both sides; custody and purpose, not text alone, draw the seam.
- `finance.insurance-personal`, `finance.vehicle-records`, and `finance.loans-mortgage`, found by the
  required quote/estimate search. Their estimates are claim, service-visit or financing artefacts.
  They receive no JSON edge because their structural anchors prevent a same-kind template contest;
  the no-edge reasoning appears below.

No external source was needed. Product design and landed reciprocal neighbours decide the catalogue
boundary; this memo does not pretend trade practice is design authority.

---

## The charge, answered directly

### Quote/estimate may be only a document type

Correct. `quotation`, `estimate`, `budget price`, `tender return` and `revised quotation` are values
of `work_type`. None can create a template. If this row meant *documents whose heading says Quote*,
it would fail: the schema default already holds measured-work documents and already recommends
document function beneath property and instruction.

The surviving object is the **enquiry**, not the document label. Before acceptance, there may be no
instruction/job level: only a requested scope, the pricing party, and successive offers. Many
enquiries never become instructions. That absence is not itself a signal, but it matters when paired
with positive offer structure: validity or estimate qualifier, scope/exclusions, acceptance mechanism,
and no work-performed or payment-due evidence.

### It may be procurement or finance with construction merely a value

Correct again. A builder's quote in an RFQ file is procurement evidence; an invoice for the same
scope is bookkeeping; an adjuster's repair estimate is an insurance-claim member. A site address and
construction vocabulary cannot rescue this row. The anchor says its professional/householder seam is
not document type, address, money, trade or format. This row uses **state-bearing structures**:

- **offer:** scoped price + validity/acceptance mechanism + no work-to-date or payment demand;
- **indicative budget:** explicit estimate/budget qualifier + assumptions/exclusions or subject-to
  survey/opening-up language;
- **procurement response:** solicitation reference + return instructions/deadline, and at event level
  competing responses/evaluation/award;
- **variation/claim:** existing contract/job + numbered instruction/variation + quantified cost or
  time consequence;
- **valuation/final account:** work executed to date + less previously certified/retention +
  certification or reconciliation;
- **delivery:** dispatched/received quantities + deliver-to/received-by/shortage evidence;
- **invoice:** invoice number + tax/payment terms + present demand or ledger/posting context.

If bytes do not show enough to choose among these states, *“A model that cannot cite sufficient evidence must return unknown.”*
Construction nouns and a currency amount do not make an enquiry.

---

## Node test — all three legs against the schema default

### Leg 1 — detection signals: **passes, narrowly and structurally**

The schema's measured-works table is not this row's fingerprint. Quantity, unit, rate and amount with
preliminaries or provisional sums appear before tender, during variation pricing and at final
account. This row adds a state-transition surface the default does not require:

1. Positive offer shape: scoped works, validity or price-held-open wording, a means to accept or
   instruct, and no evidence of payment now or work already measured.
2. Positive indicative-budget shape: approximate/budget wording paired with assumptions, exclusions
   or survey/opening-up contingency. A total merely labelled *estimate* is insufficient.
3. Revision family before commitment: same site/scope/reference, changed total or inclusions,
   supersession wording, and still no operative instruction. Revision letters alone are universal
   version evidence, not template evidence.
4. Options surface: mutually exclusive priced specifications for one proposed scope, offered for
   selection. Options inside an awarded variation remain `variation-claim` because the live contract
   and instruction outrank this reading.

Absence conditions never activate alone. They suppress false states only after positive offer/budget
evidence exists. *No invoice number* does not make a random spreadsheet a quote.

### Leg 2 — recommended dimensions: **passes in prose, but cannot yet be built**

The anchor says property/site → instruction → document function. Here the instruction does not yet
exist. The practical order is:

> property/site or enquiry subject → enquiry/prospect → offer state → revision/document function.

The inserted object is the enquiry; the working retrieval question is whether its price is open,
superseded, accepted or declined. It is not time-first: year-first could separate a December offer
from its January revision, exactly the family that must remain together.

`template.dimension_order` remains empty. The schema declares no fields, and contract rule 8 forbids
opening a dimension no fact can fill. No key holds `enquiry` or `offer_state`; this prose is a
recommendation for R1c, not an illicit schema. This leg establishes a real difference but does not
pretend the placeholder can instantiate it.

### Leg 3 — privacy rules: **does not distinguish the node**

Quotes can contain a private home address, client contacts, proprietary rates, margin and competitor
pricing. Internal cost build-ups are especially sensitive because the client-facing total may match
while margin rows must never be shared. But the schema anchor already has the same
`potentially_sensitive` posture and custody problem. This row assigns no handling class and claims no
separate protective ordering. Privacy matters, but is not an independent reason for the node.

**Overall:** kept on leg 1, supported by a genuine leg-2 difference unbuildable under PR-6. If R1c
rejects enquiry/state as a template distinction and treats it only as grouping metadata, this row
should be refused rather than retained as a document-type shelf.

---

## Concrete files, including ugly cases

The JSON supplies the observation/fact split. These cases explain what each proves and rejects.

1. **`Quotation Q-2261 - 14 Marsh Lane - kitchen extension.pdf`** — labelled offer with scope,
   exclusions, validity, acceptance and deposit-on-acceptance. The deposit request is not a present
   invoice; acceptance remains unknown.
2. **`Quotation Q-2261 rev C.pdf`** — changed scope and superseded note. It joins the enquiry without
   copying property/client facts. *Rev C* alone activates nothing.
3. **`Budget estimate - subject to survey.docx`** — indicative budget, contingent and
   assumption-led. It is not a firm offer or insurance estimate merely because both say estimate.
4. **`Cost plan - Marsh Lane - INTERNAL.xlsx`** — inward collision. Labour cost, trade price, margin
   and contingency build the client total but do not prove an offer. Without client-facing structure
   it falls to Protected Records or Review Later.
5. **`Scan_20260212_quote.jpg`** — photographed handwritten trade quote. OCR may reveal a total and
   validity, but uncertain handwriting keeps extracted detail possible. Procurement uses the same
   bytes and hands a solitary non-competitive trade quote here.
6. **`Priced BoQ return - Phase 2 groundworks.xlsx`** — dangerous overlap. Tender reference and
   return deadline support procurement; a direct offer with no bounded event may support this row.
   The numbers do not decide.
7. **`RE_ quote for the loft - go ahead.eml`** — acceptance lives in a reply. It may close the
   enquiry and start a job group; the product does not decide legal contract formation.
8. **`Quotation for VO 17 - revised drainage.pdf`** — rejected when VO 17 is an instruction under
   an existing contract. It is `variation-claim`'s shared fixture.
9. **`Valuation 07 - application for payment.xlsx`** — rejected: percentage-complete/to-date,
   previous certificates and retention mean `final-account`.
10. **`INV-2291.pdf`** — rejected: invoice number, tax, terms and payment demand mean bookkeeping or
    Receipts and Confirmations. It is not a quote whose state changed.
11. **`DN-448120 - Marsh Lane.pdf`** — rejected: dispatched/received quantities, deliver-to and
    receipt signature mean `materials-delivery`. State-bearing slots decide.
12. **`Tender submission.zip`** — covering letter, priced schedule, programme and qualifications.
    Archive membership transfers no member's meaning. A formal solicitation makes the packet
    procurement; unreadable members remain Unsupported or Encrypted.
13. **`Three builders - loft comparison.xlsx`** — homeowner comparison supports
    `finance.household-property`; contractor-side supplier comparison may be sourcing. It is not this
    row merely because every cell is a quote.
14. **`Loss adjuster repair estimate - claim 44821.pdf`** — rejected: insurer, claim number and date
    of loss form an insurance claim. Construction is the subject value, not the situation.

The list exceeds the minimum because this row's difficulty is rejecting adjacent prices, not naming
happy-path quotations.

---

## Files considered and rejected

| Tempting file | Why it is not this row's evidence |
|---|---|
| Merchant price list/catalogue | No site-specific scope, offer validity or enquiry; reference or supplier-order context. |
| Blank quotation template | Reusable form with no live scope; reference material, not enquiry evidence. |
| Internal rate card | Pricing policy, not offer; `business_operations.go-to-market` owns policy structure. |
| `Pricing model v4.xlsx` | Numbers/scenarios cannot distinguish procurement, budget, market research or cost plan. |
| Lender's *mortgage quote* | Financing terms anchored by lender, principal/rate/repayment; `finance.loans-mortgage`. |
| Motor repair estimate | Vehicle service-visit member under `finance.vehicle-records`. |
| Insurance adjuster estimate | Claim number/date-of-loss/insurer; insurance schema. |
| Variation quotation | Existing contract plus instruction; `construction_property.variation-claim`. |
| Interim valuation/final account | Cumulative work-to-date, previous certification, retention; `final-account`. |
| Delivery note/POD | Arrival, receipt and shortage state; `materials-delivery`. |
| Invoice/deposit receipt | Present payment demand or confirmation; bookkeeping/residual. |
| CRM export of open quotes | Management view over many enquiries; closer to go-to-market/account management. |

---

## Collision fixture in both directions

**Inbound false fire — `Quotation for VO 17 - revised drainage.pdf`.** It has *Quotation*, revised
works, quantities, rates and total. This row rejects it when the same bytes show VO 17, an existing
contract/job and cost/time effect against an instruction. `variation-claim` takes that adjustment.
Conversely it must reject Q-2261 where no contract/instruction exists and new works are offered with
validity and acceptance.

**Outbound file not to lose — `Quotation Q-2261 rev C.pdf`.** Procurement must not absorb it without
a bounded solicitation/competition; final-account must not absorb measured rows without work-to-date
arithmetic; bookkeeping must not absorb a total without payment demand; materials-delivery must not
absorb merchant/site tokens without dispatch or receipt. Those negative boundaries preserve the
enquiry lifecycle.

---

## Reciprocal boundaries

| Neighbour | This row must not take | Neighbour must not take | Shared fixture/discriminator |
|---|---|---|---|
| `business_operations.procurement-sourcing` | solicitation, competing bids, evaluation, award | solitary pre-contract trade offer | priced BoQ; tender reference/return instructions versus direct enquiry |
| `construction_property.variation-claim` | price adjusting contract under instruction | offer before job/contract exists | `Quotation for VO 17`; existing contract + VO + cost/time |
| `construction_property.final-account` | valuation, certification, retention, reconciliation | open offer before performance | priced schedule; validity versus work-to-date/previous certificates |
| `construction_property.materials-delivery` | order/dispatch/receipt/shortage evidence | price held before arrival | merchant quote then `DN-448120`; state slots decide |
| `finance.small-business-bookkeeping` | invoice, tax, terms, demand, posting | offer without present demand | `INV-2291` versus Q-2261 |
| `construction_property.trade-job` | actual labour/material/site attendance | enquiries that never become jobs | accepted Q-2261 is hinge; both groups, no copied facts |
| `finance.household-property` | homeowner comparison about own home | pricing party's prospect/revisions | same builder PDFs; custody/purpose |
| `construction_property.subcontract` | operative order, engagement, lifecycle | unaccepted subcontractor price | supplier quote before selection versus award |
| `construction_property.development-appraisal` | land/residual value, finance, feasibility | priced scope offered to perform works | scheme model versus client offer |
| `retail_hospitality.supplier-order` | catalogue replenishment/stock | specific proposed site works | merchant lines; stock lifecycle versus site scope |

All JSON targets exist in the roster. New reciprocal debts authored here are `variation-claim` and
`materials-delivery`; their files were not edited.

---

## Neighbours considered without an edge

- **`finance.insurance-personal` / `.insurance-corporate`** — repair estimates overlap by subject,
  but claim number, insurer and date-of-loss make the situation independently evident. Cross-schema
  subject overlap is not a same-kind template mutex.
- **`finance.vehicle-records`** — repair estimate is a work type within a vehicle service visit.
  Vehicle identity and authorization distinguish it; *estimate* alone is forbidden.
- **`finance.loans-mortgage`** — a financing illustration is anchored by lender, principal, rate,
  repayment and security. Construction is use of funds, not the situation.
- **`business_operations.budget-forecast`** — unlabeled cost spreadsheets collide, but procurement
  already authors the `Pricing model v4.xlsx` seam and this row routes its private cost plan to
  Protected Records/Review Later. Another edge would overclaim the outward offer.
- **`business_operations.go-to-market`** — rate cards, templates and packaging policy are rejected;
  policy-versus-offer structure is clear and no shared fixture needs mutex.
- **`legal.leases-agreements`** — an accepted quote may help form a contract, but that legal
  conclusion is not made here. Construction and legal readings can coexist on separate evidence;
  templates cannot author schema-only `also_holds_with`.

---

## `proposed_fields`

**None.** PR-6 requires `fields: []`, and this template cannot copy schema fields. Candidate concepts
are `enquiry` and `offer_state`; `version_family` already exists universally and must not be respelled.
The first two remain NEEDS-JOSEPH alternatives rather than minted keys. Therefore
`template.dimension_order` is empty.

---

## NEEDS-JOSEPH

- **NJ-QE-1 · Enquiry as destination dimension or P9 group?** Mint/reuse a field makes leg 2
  buildable but adds a global key; group-only avoids a key but prevents branching on the defining
  object; refusing the row leaves offers as schema-default `work_type` and loses the pre-job family.
- **NJ-QE-2 · Where does an accepted quote live?** Keep it with revisions, move it into the job, or
  expose one file through both accepted groups without duplication. Each preserves a different
  retrieval history; the third depends on P9/P11.
- **NJ-QE-3 · Does custody select the template over identical bytes?** Contractor-issued quote here;
  homeowner-received comparison in `finance.household-property`. Custody matches practice but varies
  proposals by holder; bytes-only erases the seam.
- **NJ-QE-4 · Are inbound supplier/subcontractor prices members of the outbound enquiry group?** Yes
  keeps build-up coherent; no prevents procurement/materials absorption. Linking as context without
  copying facts is the middle course recommended but not decided here.

---

## What changed in this pass

The gist draft's central insight — at quotation time there may be no job — was preserved. Its
overconfidence was removed: privacy no longer claims a distinct node-test leg, and measured works are
conceded to the schema default. The node stands narrowly on positive offer/budget state plus the
pre-instruction enquiry lifecycle.

The memo now includes the anchor default, leg-by-leg test, offer/budget/claim/invoice distinctions,
fourteen concrete cases, false positives, collision fixtures in both directions, and reciprocal
boundaries. JSON gained `variation-claim` and `materials-delivery` collisions and expanded open
questions. No fields or keys were added; no neighbour file was edited.

---

## Verification performed

- JSON parsed with `python3 -m json.tool`.
- Top-level key set compared to anchor and required neighbours.
- `fields`, `proposed_fields`, and `dimension_order` are empty; no key minted.
- Every `source_type` checked against `SOURCE_TYPES`; edge targets checked in roster; residuals checked
  against the nine-name library.
- Every design quotation in memo and JSON checked as an exact substring of `00`.
- Header contains `J-DEPTH`; memo ends with verification; JSON/memo verdict, proposal list, collision
  claims, open questions and changed-file claims agree.
- Only `construction_property.quote-estimate.json` and this memo were changed by this agent.
