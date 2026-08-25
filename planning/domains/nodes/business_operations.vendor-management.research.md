# business_operations.vendor-management — lab notes (template row)

**Depth: J-DEPTH** (R1b deepening, 2026-08-25).

Verdict: **keep the node, narrowly** (`refuse_node: false`). The surviving distinction is not
“a supplier” or “an ongoing relationship”; it is a reusable buy-side governance apparatus.

## Sources and method

Read before editing: `planning/00-database-agent-product-design.md`, the structured rendering,
ALIGNMENT, `_CONTRACT`, CONNECTION and its examples, canonical fields, roster, vocabulary, and the
ratified decision brief. The stamped prompt came from `python3
planning/domains/dispatch/make_prompt.py business_operations.vendor-management`. The required
schema anchor `business_operations.research.md` was read first. Comparisons were then made against
`business_operations.procurement-sourcing.research.md`,
`business_operations.partnerships-bd.research.md`,
`business_operations.contract-administration.research.md`, and
`finance.small-business-bookkeeping.research.md` (the accounts-payable/finance boundary). None was
edited. The gist draft was treated as verified but shallow; its sound fixtures and empty fields were
preserved while its verdict was retested.

Every quotation attributed to `00` below is exact. Everything else is identified as an inference.
No external source supplies a threshold, retention rule, detector, or legal conclusion.

## Governing constraints

Role cannot itself be the node:

> “The system must separate roles that happen to contain the same entity type.”

and:

> “The agent should model these as distinct facets, such as authored_by and target_school, or
> our_firm and client.”

Therefore supplier/customer/partner/prospect labels cannot distinguish four templates. If this row
survived only because an organisation is on the buying side, it would be refused.

An organisation must not become a collector:

> “A folder should not become a collection point for everything produced by the same person or
> organization.”

The deepened schema anchor generalises that into a never-alone rule: entity name, business word, and
document shape each need a structure-plus-labelled-slot pair. `Meridian/` may be a convenient user
branch, but its existence is not activation evidence.

Unlike files may still form a purpose packet:

> “The documents are content-incoherent but purpose-coherent.”

But membership does not manufacture facts:

> “The graph does not automatically copy those missing facts onto sparse files.”

Thus an onboarding form, certificate, DDQ, scorecard, and remediation plan may form one accepted
governance group, while a nearby invoice or MSA does not acquire relationship facts merely because
it names the same company.

## What survives after the role objection

The gist phrase “supplier as an ongoing relationship” was too broad. It would take every invoice,
purchase order, contract, message, and meeting for a frequent counterparty. The narrower inferred
anchor is a **reusable buy-side governance apparatus**: an established supplier has a register entry
or supplier identifier, an internal owner or approval state, standing evidence with review/expiry
state, and later performance, remediation, or exit state.

- **Reusable** excludes one quote, order, and negotiation.
- **Buy-side** states posture but never proves it; holder-side evidence remains required.
- **Governance apparatus** means maintained state, not supplier vocabulary.
- **Established** separates the row from procurement and BD pursuits.
- **Standing evidence** means continued eligibility is tracked; a certificate alone is insufficient.
- **Performance/remediation/exit state** separates relationship governance from contract deadlines
  and payment processing.

No one file needs every element. A populated supplier register may anchor a validated group. Yet
the register cannot copy a supplier role onto an invoice, and an isolated certificate remains
unknown without its own evidence or a validated grouping decision.

## Node test, leg by leg

The business-operations default is:

> the **organisational unit or entity** *only where the corpus genuinely spans more than one* →
> the **governance body, project, contract, or account** the material belongs to → the **fiscal
> period** → the **document function**. Not time-first.

Because this template has `fields: []`, its JSON dimension order must remain empty.

### Leg 1 — detection: passes narrowly

“Vendor management” alone would be merely a function value. The distinct structures are:

1. a populated supplier register with supplier identifier, relationship owner/approver, status,
   and review or evidence-expiry state;
2. an onboarding approval joining legal/remittance slots to internal approval and enabled/blocked
   state;
3. a standing-evidence tracker joining required evidence type to received, expiry, and review state;
4. a performance scorecard joining one supplier to agreed measures, actions, owners, and
   remediation state;
5. an offboarding tracker joining access/payment/service shutdown tasks to owners and completion.

These are not merely work-type names. Each maintains state across the life of a counterparty, and
each pairs structure with labelled slots. `00` supports the evidentiary importance of that structure:

> “Tables matter because resumes, forms, applications, invoices, and administrative documents
> often place their most useful information in cells rather than body paragraphs.”

A DDQ, certificate, QBR, or email alone does not establish the apparatus. It needs holder-side
approval/governance evidence or a validated join to the register. Supplier vocabulary never
substitutes for structure.

### Leg 2 — dimensions: does not independently pass

The gist draft overstated this leg. The intuitive order—supplier → lifecycle function → review
period—cannot be serialized: supplier is not canonical, and organisation-first is the collector
risk `00` warns against. It also resembles the schema default (entity/account → function → period).

The parent-context rule still applies:

> “The recommendation should follow the practical rule that a parent dimension should provide the
> context required to understand the child.”

A scorecard is unintelligible without its relationship, but that is a future field/group-label
question, not an independent node-test pass. The user retains control:

> “The system recommends an order based on the domain template, but the user can reverse, remove,
> add, or flatten dimensions.”

It is not time-first:

> “For document and record domains, project, function, or subject usually comes before time because
> putting year first scatters related work across calendar folders.”

### Leg 3 — privacy: passes

The row concentrates third-party contacts, pricing/performance, security disclosures, insurance,
and sometimes bank details. A new-vendor form or bank-change email may combine legal identity,
contacts, remittance data, and internal approval state.

> “Privacy policy must be enforced before content reaches any model or external connector.”

and:

> “A model that cannot cite sufficient evidence must return unknown.”

The row is therefore `potentially_sensitive`, but writes no P7 class and no payment fact. The
bank-change fixture falls to Protected Records when inactive. Fraud-safe treatment is NJ-BO-VM-4.

### Verdict

**Keep, narrowly.** Detection passes on reusable governance-state structures and privacy passes on
concentrated actionable third-party data. Dimensions do not pass. If implementation cannot require
the structures above, refuse the row rather than degrading it to “files mentioning a supplier.”

## Bottom-up fixtures and rejected inferences

The JSON's nine fixtures cover form, register, certificate, questionnaire, invoice, presentation,
instrument, scorecard, and email. Nine are enough; more extensions would be padding.

**`New supplier form - Meridian Logistics.pdf`.** Legal-entity, tax/registration, remittance,
contact, and internal-approval blocks strongly support onboarding governance. The word *supplier*
does not. Rejected: the bank block does not authorize a normalized payment fact or action; the form
may be an unapproved draft or impersonation artifact.

**`Approved supplier list 2026.xlsx`.** Strongest positive: one row per supplier with supplier code,
status, relationship owner, review date, and expired-evidence flag. It directly exhibits the
apparatus. Rejected: table membership does not propagate supplier role to every same-name file; the
filename year is not automatically a fiscal-period fact.

**`Meridian - certificate of insurance 2026-27.pdf`.** It names the insured, policy, covers, limits,
and validity period but not why the holder has it. It is standing evidence only inside an evidenced
supplier diligence context. Rejected: insured party does not equal supplier; this is the primary
collision with `finance.insurance-corporate`.

**`DDQ response - Meridian v2.docx`.** Numbered answers on data protection, subprocessors, vetting,
and financial standing are real diligence material. The same questionnaire may be collected during
a competition or as audit evidence. Rejected: answers do not authorize a compliance conclusion;
version token supports version-family reasoning, not relationship role.

**`Meridian invoice 2026-0417.pdf`.** Primary negative collision. Invoice number, total, tax line,
terms, and PO reference make it transactional accounts-payable evidence. Rejected: named payee does
not activate vendor management. Admitting this file would prove the anchor was only supplier role.

**`QBR - Meridian Q1 2026.pptx`.** Service metrics, issue/actions, roadmap, and two-party attendees
can support periodic governance. Rejected: supplier branding does not settle holder side. To the
buyer this may be vendor management; to the seller it may be customer account management.

**`Signed MSA - Meridian - executed.pdf`.** Parties, clauses, schedules, and signatures make a legal
instrument; obligation tracking may support contract administration. Rejected: execution does not
prove supplier governance. It may join a real-world supplier group without activating this row.

**`Supplier scorecard H1.xlsx`.** A populated supplier identifier, agreed measure, target/actual,
owner, action, and remediation status is a strong positive. Rejected: a blank template, internal
team scorecard, or scorecard without holder side cannot fire from vocabulary alone.

**`FW updated bank details - urgent.eml`.** Kept to test safety, not as a positive anchor. Sender,
recipient, urgent request, attachment, and account details are observations. Rejected: the product
must not infer validity, approval, or a governed lifecycle from this alone.

## Other tempting false files rejected

- A lone **purchase order** is an order/call-off and may support accounting or contract
  administration; without governance state it is not this row.
- A **vendor bill, AP aging report, or remittance advice** is finance. Invoice/due/posted/paid/balance
  columns do not become a supplier register merely because rows are vendors.
- A **signed NDA or MSA** is a legal instrument; obligation tracking is contract administration.
- A **vendor contact card** is a source type plus personal data, not a governance apparatus.
- `Vendor review.ics` is calendar source type plus never-alone title vocabulary.
- A **generic code-of-conduct** or **blank DDQ** describes possible process, not an actual supplier.
- A **screening result** without subject-role context may concern customer, employee, investor, or
  holder; screening vocabulary does not establish supplier posture.
- A **partner proposal** is pre-relationship pursuit or procurement evidence depending on who holds
  the evaluation apparatus.
- A **supplier-authored QBR retained by the supplier** is customer account management from that
  holder's side. Same bytes, different evidenced posture.
- A **contract-renewal notice** with clause reference, notice window, and obligation deadline is
  contract administration. An internal review date is cadence, not a contractual deadline.

## Collision fixtures in both directions

### Finance/accounts payable

Wrongly fires here: `Meridian invoice 2026-0417.pdf`. Discriminator: invoice number, taxable total,
due/payment state, and posting/payment reference; no relationship owner, evidence expiry, review
action, or remediation state.

Must not be lost to finance: `Approved supplier list 2026.xlsx`. Spend band/remittance setup may
look financial, but approval/status/owner/review state is governance, not transactions or balances.
The entity bytes are identical; maintained table state decides.

### Procurement-sourcing

Wrongly fires here: `PQQ response - ITT-2026-014.docx`. Discriminator: solicitation reference,
deadline, candidate response, competing bids, scoring, and award state mean a selection event.

Must not be lost to procurement: `Supplier scorecard H1.xlsx`. Actual service measures and
remediation actions concern one approved relationship, not candidate comparison. DDQ bytes may join
both groups at different stages without copying event/relationship facts.

### Contract administration

Wrongly fires here: `Contract register - live agreements.xlsx`. Discriminator: agreement reference,
clause/obligation reference, notice date, renewal deadline, and obligation status.

Must not be lost to contract administration: `Approved supplier list 2026.xlsx`. Supplier
identifier, eligibility status, evidence expiry, review cadence, and performance state exist without
a contract reference. Review cadence is not notice deadline.

### Partnerships/BD

Wrongly fires here: a supplier's outbound proposal. Offer, validity, negotiation, pipeline, or
pre-relationship state exists; approved-supplier state does not.

Must not be lost to BD: an approved new-supplier form with internal approval, vendor identifier,
payment enablement, and operating state. Role alone is insufficient in both directions.

## Reciprocal boundaries

**↔ `business_operations.procurement-sourcing`.** Several candidates, solicitation reference,
deadline, evaluation, award/regret → procurement. One established supplier, internal owner,
standing evidence, scorecard, remediation/offboarding → this row. Same bytes: a DDQ/certificate
packet collected during selection and reused after award. This matches the neighbour's
existence/cardinality seam.

**↔ `business_operations.contract-administration`.** Contract identity, obligations, clauses,
notice windows, renewals, termination deadlines → contract administration. Eligibility, evidence
validity, relationship owner, performance, remediation, operational exit → this row. Same bytes: a
renewal spreadsheet with both contractual notice date and internal supplier-review date. The
executed instrument alone belongs to Legal rather than either apparatus. Merge pressure is real,
but a supplier-name merge recreates the refused organisation collector.

**↔ `business_operations.partnerships-bd`.** Opportunity/offer, validity, negotiation, pipeline,
closed-lost → BD. Approved relationship, vendor identifier, governance state, performance history,
managed exit → this row. Same bytes: a proposal containing DDQ answers. The distinction is
relationship existence and structure, never counterparty role.

**↔ `business_operations.customer-account-management`.** Both may contain onboarding, QBRs,
scorecards, renewal work, escalations, and exit. Buyer-side supplier register/remittance approval →
this row; seller-side account number, adoption/usage, success plan, renewal recommendation → customer
account management. Same bytes: `QBR - Meridian Q1 2026.pptx`. Without side evidence, abstain.

**↔ `finance.small-business-bookkeeping` (accounts payable).** Bills, invoices, remittance advice,
payment runs, AP aging, posting, tax treatment, totals, reconciliation → finance. Approval,
eligibility, internal owner, evidence validity, performance/remediation/offboarding → this row. A
supplier master exported from accounting software needs governance columns beyond payment setup;
a supplier register's spend band does not turn it into a ledger.

**↔ `business_operations.risk-register`.** One row per risk with likelihood, impact, treatment,
owner, residual state → risk. One row per supplier with approval/evidence/performance state → here.
Same bytes: a DDQ finding may create a third-party risk and stay in the relationship packet.

**↔ `business_operations.compliance-audit`.** Control identifiers, test procedure, evidence,
finding, assurance, remediation verification → compliance/audit. Collection of third-party
assurance as a condition of dealing → here. Same bytes: SOC report/security attestation; alone it
proves neither supplier role nor holder-side audit purpose.

**↔ `finance.insurance-corporate`.** Holder as insured/policyholder administering its cover →
insurance. Counterparty certificate tracked as standing evidence → here. Same certificate layout;
holder identity against corpus context is required.

**↔ `legal.leases-agreements`.** Rights/obligations in an executed instrument → Legal. Operational
eligibility/performance around an established supplier → here. Same bytes: signed MSA. It may carry
Legal schema facts and join a supplier group, but does not activate this template alone.

## Grouping firewall

The natural accepted group is one governed supplier lifecycle: onboarding approval, acknowledgments,
certificates, DDQ, scorecards, reviews, remediation, offboarding. Permitted reasons include explicit
supplier identifier across the register and artifact, a register row linking an evidence reference,
a bounded diligence round with cover correspondence, version-family evidence, and an offboarding
checklist referring back to the approved record.

Forbidden propagation: an invoice does not acquire governance facts; a certificate does not acquire
supplier role from name match; a QBR does not acquire side from branding; a download session does not
prove topic; a folder name does not activate either contract or vendor management; a bank-change
email does not acquire approval from proximity to an older form.

No group is a valid outcome. A lone certificate, generic scorecard, or invite may remain Independent
Records or Review Later.

## Fields and dimensions

`fields: []` is mandatory: this template uses the field-less placeholder schema.
`proposed_fields: []` is deliberate. The missing buy-side role (`supplier`) is real, but one template
must not mint a family-wide counterparty key while generic-counterparty versus role-specific modelling
is unsettled. This is NJ-BO-VM-2.

Desired future dimensions—supplier/relationship, lifecycle function, review period—remain prose.
No key means no branch. `time_first` stays false.

## Neighbours considered without an edge

- `career`: individual-side engagement; broad schema edge would add little.
- `hr.training-development`: training provider is a supplier category, not another apparatus.
- `business_operations.facilities-workplace`: facilities vendors use the same governance structure;
  service category is a value.
- `logistics`: carrier/3PL is a supplier category; shipments retain their own evidence.
- `government.public-procurement`: statutory procedure belongs to sourcing, not ongoing governance.
- `retail_hospitality.supplier-order`: order structure is already excluded by procurement/finance;
  a category-specific duplicate adds no discriminator.

## NEEDS-JOSEPH

- **NJ-BO-VM-1 · Is the apparatus enough?** Keep only if implementation requires register/onboarding
  state joined to evidence-expiry, performance, remediation, or exit. Refuse into the schema default
  if it would fire from role, name, or a lone DDQ/certificate/scorecard. Recommendation: **keep**.
- **NJ-BO-VM-2 · Buying-side counterparty key.** Choose generic counterparty+role, widen an existing
  key, or define one canonical supplier key once. This row proposes none.
- **NJ-BO-VM-3 · Holder side.** For QBR/scorecard/certificate/onboarding bytes that do not reveal
  buyer, seller, or subject posture, abstain or ask; branding/folder placement is insufficient.
- **NJ-BO-VM-4 · Payment-change handling.** Decide whether bank-change instructions need a dedicated
  fraud-safe state beyond potentially-sensitive protection. This row must never act on them.

## What changed in this pass

- Replaced retired GIST header with explicit `J-DEPTH` in the first eight lines.
- Retested all three node-test legs against the deepened business anchor.
- Narrowed “supplier relationship” to reusable governance state and rejected supplier role/value as
  the distinction.
- Withdrew the claim that dimensions independently pass; preserved `dimension_order: []`.
- Added reciprocal procurement, partnerships/BD, contract, and AP/finance comparisons with same-byte
  fixtures in both directions.
- Expanded false positives, grouping firewall, proposed-field reasoning, and four NEEDS-JOSEPH items.
- Preserved 27 JSON keys, `fields: []`, `proposed_fields: []`, closed edges, and zero neighbour edits.
