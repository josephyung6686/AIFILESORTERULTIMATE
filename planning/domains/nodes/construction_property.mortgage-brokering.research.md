# construction_property.mortgage-brokering — lab notes (template refusal)

**Depth: J-DEPTH** (deepened 2026-08-25). This pass reverses the gist draft's keep verdict.

## Verdict

**REFUSE.** Mortgage brokering does not survive the cross-family node test as a
`construction_property` template. The files are a borrowing application/advice case already held by
`finance.loans-mortgage`: fact find, evidence request, payslips and statements, affordability work,
lender submission, decision in principle, offer, suitability letter, and completion or decline. A
property is collateral or transaction subject. A broker is an intermediary role. Neither is a distinct
organizational structure.

This is not a claim that the files are unimportant or that the group is unreal. One broker case is a
strong P9 group. The refusal is narrower: the group does not justify a second template on the
construction/property schema. `CONNECTION.md` separates groups from templates, and the design says,
verbatim, “The graph is used as a context-assembly mechanism rather than an automatic
label-propagation system.”

## Sources actually used

- `planning/00-database-agent-product-design.md`, the only source quoted as design.
- `planning/prompts/ALIGNMENT.md`, `planning/domains/CONNECTION.md`,
  `planning/domains/CONNECTION-EXAMPLES.md`, `planning/domains/_CONTRACT.md`,
  `planning/domains/canonical_fields.json`, and `planning/domains/roster.json`.
- `planning/domains/nodes/construction_property.research.md`, the J-DEPTH family anchor.
- `construction_property.sale-purchase` and `construction_property.survey-valuation`, both files.
- `finance.household-property` and `finance.loans-mortgage`, both files. The latter is the
  decisive comparison.
- `career.consulting-client-engagement` and the client/counterparty workflow reasoning in
  `business_operations.customer-account-management` and
  `business_operations.contract-administration`.
- The pre-existing mortgage-brokering JSON and gist memo, preserved where factual and reversed only
  where the node conclusion failed.

No deferred catalogue was consumed. No detector pattern, score, threshold, jurisdiction rule, or
canonical field was invented.

## What the shallow draft got right

The draft accurately named the corpus and its hazards. A broker really does keep a fact find, evidence
checklist, client agreement, identity and address evidence, income evidence, bank statements, deposit
evidence, affordability calculations, lender comparisons, a submission, a decision in principle, an
offer, a suitability letter, and commission records. It also correctly identified the hardest fact:
the same payslip or bank statement may be the subject's own Finance record or a copy held by an
intermediary. The bytes do not reveal custody.

The draft was also right that a lender name, person name, property address, rate, total, extension, and
download session are never sufficient. The design's rule is exact: “A session should never be treated
as proof of topic, and it should not carry the same confidence as a hash match or a directly extracted
document fact.” It was right to keep `fields: []`, propose no canonical keys, and route exposed material
to Protected Records.

What it got wrong was treating those truths as evidence for a second template. They establish a
borrowing case and a protection requirement. The landed Finance row already establishes both.

## The schema default and the cross-family charge

The construction/property anchor states its default in prose:

> property or site → instruction → document function, with a period only where the situation cycles;
> not time-first.

Mortgage brokering does not specialize that shape. Its natural prose order is client → case → stage.
That is not a construction/property variation; it is evidence that the schema assignment is wrong. The
anchor is not the building, site, works, or professional opinion about an asset. It is the application
for credit. The “case” begins before a property is known, survives a change of property, may end after a
decision in principle without any property, and may be a product transfer or remortgage whose operative
work is financial.

The Finance borrowing row already recommends `account_type → record_type`, with institution optional,
because servicing can move between institutions. It expressly covers application and closing packets,
not merely post-completion statements. Its recognition includes a credit-application form with amount,
term, rate, collateral/property, employment, income and assets blocks. Its privacy rule expressly covers
the packet aggregation of identity scans, payslips, bank statements and a co-borrower's material.
Therefore “the loan concerns property” is a subject value, and “a broker holds the packet” is custody.
Neither can bear a second node.

## Node test, all three legs

### Leg 1 — detection signals: fails as a distinct template

The gist draft's strongest candidates were the fact find and evidence checklist. Both are real
structures, but the relevant question is not whether they detect *something*. It is whether they detect
this template in a way different from the schema default and from the already-landed neighbour.

- A fact find with income, expenditure, dependants, employment, credit history and objectives is an
  application/advice stage in the loan lifecycle.
- An evidence checklist chasing payslips, bank statements, identity and deposit proof is the manifest
  of that application packet.
- An affordability assessment and lender comparison are underwriting/advice work around that loan.
- A decision in principle and offer are native loan records.
- A suitability letter explains why the selected borrowing product fits the application.
- A commission statement is the intermediary's business revenue, not a construction/property record.

Taken together, these signals distinguish a borrowing case from generic Finance. They do not
distinguish brokered borrowing from `finance.loans-mortgage`, because that row already owns application,
closing, servicing and release. Removing the role words *broker*, *adviser* and *client* leaves the same
loan packet. Removing the property address also leaves the same packet. That deletion test is decisive.

### Leg 2 — recommended dimensions: fails

The construction/property default is property/site → instruction → function. The proposed
client → case → stage order is a client-engagement order. It cannot be serialized here anyway because
the schema declares no fields. More importantly, it is not a distinct stable recommendation:

- A single borrower may have several applications.
- One application may involve two borrowers.
- One case may change lender or property.
- One commission statement spans many cases.
- One identity scan may support more than one application but must not inherit old financial facts.

The case reference is useful evidence for grouping, not a canonical organization field. Stage is a set
of `record_type` or work-type values. Client is a counterparty role, and the client/counterparty
neighbours warn that a role word alone is never structure. The product may offer a user-approved group
view, but that does not require a construction/property template.

### Leg 3 — privacy rules: fails as a difference

The material is highly sensitive in ordinary language and correctly uses catalogue value
`potentially_sensitive`. It aggregates third-party identity, employment, income, account, credit and
property information. The design requires that “Privacy policy must be enforced before content reaches
any model or external connector.” It also says: “Protected material should not be included in
cloud-model prompts by default, should not display raw content in general group summaries, and should
not be moved automatically without a user policy that explicitly permits it.”

But the Finance loan row already states the same packet-level hazard: an application or closing packet
can disclose more than each member. Broker custody does not create a new privacy rule. It changes whose
machine holds the file and may change user policy, but P7 handles that policy. A catalogue template must
not mint a duplicate merely to restate protection.

**Overall: three failures. `refuse_node: true`.**

## Required reciprocal boundaries

### finance.loans-mortgage

This refused row must not take a fact find, evidence checklist, application, affordability assessment,
decision in principle, offer, closing disclosure, servicing statement, payoff or release from Finance
because a broker handled it. Finance must not infer that every loan record belongs to a broker case:
the holder's own statement can stand alone.

Shared bytes: `Mortgage offer - 14 Marsh Lane.pdf`. In a borrower's archive it is the holder's loan
record. In a broker's case it is still a Finance loan record and may join the broker case group. Custody
changes group membership, not schema/template identity.

### construction_property.sale-purchase

This refusal must not absorb a conveyancing transaction pack merely because it contains a mortgage
offer or identity evidence. Sale-purchase must not absorb the lending application or suitability
advice merely because the loan funds a purchase.

Shared bytes: `Mortgage offer - 14 Marsh Lane.pdf`. The offer may join both the Finance loan group and
the property transaction group without acquiring facts from either neighbourhood. The design permits
overlap: “A file may validly belong to more than one accepted group”.

### construction_property.survey-valuation

This refusal must not take the professional opinion as its own deliverable. Survey/valuation must not
take the whole loan packet because the valuation names a lender and case reference.

Shared bytes: `Mortgage valuation - case 88213.pdf`. The reliance block, inspection date, basis and
valuer certification support survey/valuation. Its presence on a lender checklist supports membership
in the Finance borrowing case; it does not transform the report into mortgage-brokering evidence.

### finance.household-property

This refusal must not take the householder's title, tax, inspection, appraisal, warranty, improvement
or tenancy-administration records merely because a lender or adviser appears. Household-property must
not take a broker's fact find or advice letter merely because it mentions a home.

Shared bytes: `Residential Appraisal Report - 42 Oak Street.pdf`. It can join a household property
packet and a borrowing packet. The labelled intended lender does not make the lender the report issuer,
and the address alone chooses neither group.

### client and counterparty workflow neighbours

`career.consulting-client-engagement` and the business-operations client/counterparty rows confirm a
general rule: client, customer, supplier, borrower and broker are roles; structure must survive deletion
of the role word. A bounded engagement may be a real group while its professional specialty remains a
value. Mortgage brokering's remaining structure after deletion is the loan lifecycle, already owned by
Finance.

These neighbours must not absorb lending evidence as generic account management. Conversely, Finance
must not claim CRM pipeline reports, revenue forecasts or relationship health records merely because
they name the same borrower. A CRM export is business operations; the attached loan documents are
Finance; an accepted case group can connect them without copying facts.

## Collision fixtures, both directions

**Would wrongly fire the refused row:** `Fact find - Okonkwo - 2026-02.pdf`. It is the shallow draft's
best fingerprint. Yet every labelled block exists to apply for and recommend credit. The discriminator
is not construction/property at all. It routes to `finance.loans-mortgage` and Protected Records.

**Must not be lost to the refused row:** `Mortgage Statement Mar 2026.pdf`, the landed Finance
fixture. Principal, interest, escrow, payment and remaining balance are servicing structure. A broker
might retain a copy, but possession by an intermediary cannot reclassify the record.

**Cross-workflow false positive:** `Client pipeline - Q3.xlsx`. A client name, case status and expected
commission can resemble the broker case index. It is business/account management unless member rows or
attachments carry loan structures. The spreadsheet must not lend its role labels to attachments.

## Files considered and rejected

The JSON retains concrete fixtures because refusal must be auditable, but none activates this node.

- `Fact find - Okonkwo - 2026-02.pdf` — Finance loan application/advice evidence; protected.
- `Evidence checklist - case 88213.xlsx` — packet manifest and P9 group evidence, not a schema.
- `Payslips Nov-Jan.pdf` — the subject's Finance/employment record copied into a protected packet.
- `DIP - Nationwide - ref 771204.pdf` — loan decision, not an offer and not property practice.
- `Suitability letter - Okonkwo.docx` — advice output about the loan; role/custody do not create a node.
- `Mortgage offer - 14 Marsh Lane.pdf` — Finance loan record and possible sale-purchase group member.
- `Scan_ID_and_utility.jpg` — identity/address evidence protected first; filename and adjacency do not
  activate a domain.
- `submission_pack_88213.zip` — a purpose-coherent Finance packet; inspect manifest without unpacking.
- `Procuration fees - Q1.csv` — intermediary revenue/bookkeeping across cases, never one client case.
- `Mortgage valuation - case 88213.pdf` — survey/valuation deliverable that may join the loan group.
- Generic lender criteria guide — Reading Inbox or Reference Clips; no case.
- Generic mortgage-rate advertisement — Reference Clips; a lender logo and rate prove nothing.
- Conveyancer completion statement — sale-purchase/legal material; may join the transaction group.
- Client CRM export — business operations; names and stages alone cannot activate Finance.
- Password-protected evidence archive — Unsupported or Encrypted or a local protected representation.

This list includes more than eight real files because the refusal turns on where they go, not on an
inability to name material.

## fields and proposed_fields

`fields: []`. Templates do not copy a schema's fields, and construction_property declares none.

`proposed_fields: []`. No canonical key is warranted:

- `client` already exists as a role field elsewhere and would not distinguish borrower from adviser,
  lender, conveyancer or valuer.
- `case` or `case_reference` is a grouping identifier, not necessarily a destination dimension.
- `borrowing_purpose` is a value/purpose observation inside the Finance case.
- `property` is already a pending cross-family question and cannot be minted by a refused row.
- `broker` is a counterparty role, not structure.
- stage maps to document/work-type values; a new field would duplicate `record_type`.

The absence of fields is substantive: no key could rescue the node without encoding the role or subject
value that caused the duplication.

## Residual and coverage routing

The row's coverage is not discarded.

- Loan application, offer and advice material: `finance.loans-mortgage`.
- Householder property lifecycle material: `finance.household-property`.
- Conveyancing transaction material: `construction_property.sale-purchase` and Legal where active.
- Reliance-based valuation reports: `construction_property.survey-valuation`.
- Identity evidence and exposed financial attachments: protection first; Protected Records if no
  reliable deeper association lands.
- Isolated confirmations and commission remittances: Receipts and Confirmations where appropriate.
- Generic guides and marketing: Reading Inbox or Reference Clips.
- Unreadable/password-protected packets: Unsupported or Encrypted.
- A meaningful but unresolved standalone case document: Independent Records or Review Later.

The JSON keeps the existing residual routes and empties authored collisions because a refused node
must not participate as if it could activate.

## NEEDS-JOSEPH

**NJ-CP-MB-1 — retire or re-roster?** Confirm that the legacy label is retired. Moving it to a new
`finance.mortgage-brokering` id would not by itself solve the duplication: the landed
`finance.loans-mortgage` already owns the same lifecycle. A new Finance sibling would be justified
only if intermediary custody is meant to create templates systematically across mortgage, insurance,
investment and other advice. That policy is not in the design.

**NJ-CP-MB-2 — client-first protected views.** Decide whether a user-approved client level may ever be
built over third-party financial evidence. The natural practice view is client → case → stage, but it
discloses relationships and places identity/account material under named people. This refusal neither
endorses nor forbids such a P10/P7 feature; it only says it is not licensed by this construction/property
row.

## What changed in this pass

- Replaced **Depth: GIST** with **Depth: J-DEPTH**.
- Reversed `refuse_node: false` to `true`.
- Tested all three node-test legs against the deepened construction/property anchor and the landed
  Finance lending row.
- Reframed the fact find and checklist as Finance lifecycle structures rather than unique
  construction/property signals.
- Added reciprocal boundaries and shared-byte fixtures for sale-purchase, survey/valuation,
  household-property, lending, and client/counterparty workflows.
- Preserved the correct file inventory, protection analysis, empty fields, and residual coverage.
- Removed collision edges from the refused node and surfaced the two unresolved policy questions.

## Audit

JSON was written before this memo. Verification checks parse, exact key set, empty `fields`, empty
`proposed_fields`, refusal state, source types, residual names, the **Depth: J-DEPTH** header, the
required ending, and consistency between this memo and the JSON.

**End of research memo — construction_property.mortgage-brokering — REFUSED.**
