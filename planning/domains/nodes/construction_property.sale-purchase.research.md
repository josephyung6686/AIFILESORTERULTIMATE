# construction_property.sale-purchase — lab notes (template refusal)

**Depth: J-DEPTH** (deepened 2026-08-25). This pass reverses the gist draft's keep verdict.

## Verdict

**REFUSE.** Residential sale and purchase does not survive the cross-family node test as a
`construction_property` template. While active, the pack is a conveyancing legal matter: engagement,
identity checks, title, searches, enquiries, contract, completion, transfer, tax submission and
registration. In the buyer's or seller's own corpus, the lasting subset is an acquisition or disposal
record already held by `finance.household-property`. Property is the subject; buyer and seller are
party roles; transaction stage is document function. None is a distinct construction/property
structure.

The refusal does not deny the group. A conveyancing pack is strongly purpose-coherent, and a file may
belong to that accepted group while keeping its own Legal, Finance, Identity or survey reading. The
design is explicit: “A file may validly belong to more than one accepted group”. A useful group is not
automatically a catalogue template.

## Sources actually used

- `planning/00-database-agent-product-design.md`, the only source quoted as design.
- `planning/prompts/ALIGNMENT.md`, `planning/domains/CONNECTION.md`,
  `planning/domains/CONNECTION-EXAMPLES.md`, `planning/domains/_CONTRACT.md`,
  `planning/domains/canonical_fields.json`, `planning/domains/roster.json`, and the stamped assignment.
- `construction_property.research.md`, the deepened family anchor.
- `construction_property.mortgage-brokering`, whose refusal supplies the cross-family method;
  `construction_property.survey-valuation` and `construction_property.tenancy-management`, whose
  professional structures show what can genuinely remain on this family.
- `finance.household-property`, `finance.loans-mortgage`, `legal.practice-matter-file`,
  `legal.personal-legal-matters`, and `legal.leases-agreements`, both JSON and research where landed.
- The pre-existing sale-purchase JSON and gist memo, preserved where factual and reversed only where
  the conclusion failed.

No detector catalogue, jurisdiction rule, threshold, retention rule or field key was added.

## What the shallow draft got right

The draft accurately described the bytes. A transaction pack can contain a memorandum of sale,
official title copies and plan, searches, property questionnaires, fittings forms, enquiries and
replies, contract drafts, a survey, mortgage offer, identity and source-of-funds evidence, completion
statement, transfer, tax confirmation and registration confirmation. It correctly said that a property
address, person name, title number, price, generic document word, extension and download session are
never sufficient. The design's exact rule remains: “A session should never be treated as proof of topic, and it should not carry the same confidence as a hash match or a directly extracted document fact.”

It was also right about protection. A passport and bank statements must not wait for organization:
“A scanned passport, tax statement, medical document, authentication key, or account record should enter a protected state immediately.” It was right to keep `fields: []`, propose no fields, and route
exposed material to Protected Records.

The error was treating a coherent pack and its stages as a second template on a property-industry
schema. Those signals detect conveyancing. They do not establish that conveyancing belongs to
`construction_property` rather than Legal, and the owner's residue is already Finance coverage.

## The schema default and the cross-family charge

The construction/property anchor's default is property or site → instruction → document function,
with a period only where the situation cycles; not time-first. The gist draft proposed property →
transaction → stage. That is not a distinct variation. A conveyancing transaction is the Legal matter
or accepted group; searches, enquiries, contract and completion are document-function or stage values.
Replacing *instruction* with *transaction* merely renames the same middle level. More importantly, the
actual organizing relation is legal: two sides exchange operative instruments and professional
undertakings to change title. The property supplies the matter subject, not a second schema.

The deletion test is decisive. Remove *property*, *buyer* and *seller*. What remains is a client matter
with identity checks, due diligence, enquiries, drafted and executed instruments, financial completion,
submissions and closing. That is Legal matter structure. Restore the owner's custody after closing and
the lasting title/closing/tax records become household Finance. The removed words were a subject and
party roles, not node-bearing structure.

This is the same error exposed by the mortgage-brokering refusal. There, property was collateral and
broker was intermediary role; here, property is matter subject and buyer/seller are party roles. A role
may matter deeply to grouping and retrieval without licensing an industry template.

## Node test, all three legs

### Leg 1 — detection signals: fails as a distinct construction/property template

The draft's signals are real, but they are conveyancing signals:

- A memorandum of sale identifies parties, property, price and representatives. It opens or indexes a
  matter; it does not prove a construction/property schema.
- Official title entries, title plan and searches are due-diligence inputs to the Legal transaction.
  A person can also retain them as household property records.
- Seller questionnaires and replies to enquiries are party assertions exchanged before contract.
- Draft, approved and executed contracts are version/status values of an operative legal instrument.
- Transfer, undertaking, completion statement and registration confirmation are closing records.
- Identity and source-of-funds checklists are protection-critical compliance material inside the
  matter, not construction/property evidence.

The pack differs from broad Legal in matter type, not in a structure the landed Legal rows lack.
`legal.practice-matter-file` already organizes professional matters; `legal.personal-legal-matters`
already protects holder-facing legal matters; `legal.leases-agreements` owns the operative-instrument
reading. A future Legal conveyancing template might survive if tested against Legal's default, but that
is a different roster decision. Moving the present row without retesting would not cure duplication.

### Leg 2 — recommended dimensions: fails

The apparent order property → transaction → stage cannot be expressed because the schema declares no
fields. It also adds no stable concept:

- `property` is the subject of the matter and household record.
- `transaction` is the matter/group, not necessarily a file fact.
- buyer and seller are roles on opposite sides of the same transaction.
- `stage` is represented by document functions such as searches, enquiries, contract and completion.

One owner may buy and later sell the same property. One conveyancer may hold hundreds of matters. One
contract appears on both sides. One title copy can be downloaded outside any transaction. No ordering
turns those facts into a distinct construction/property template. The group can be shown by matter or
transaction without creating folder facts, consistent with: “The graph does not automatically copy those missing facts onto sparse files.”

### Leg 3 — privacy rules: fails as a difference

The pack is potentially sensitive and aggregation sharpens the risk: passport, address proof, bank
statements, source-of-funds explanation, mortgage offer, client-account references and private
correspondence may sit together. But Legal and Finance are already safety domains. The design says:
“Finance, identity, medical, and legal material should be implemented first as safety domains”. Their
rows already require protection before deep organization and prohibit casual model exposure.

The transaction group needs strict protection, but it does not possess a privacy rule that differs from
the safety schemas which own its evidence. A duplicate row cannot be justified by restating them.

**Overall: three failures. `refuse_node: true`.**

## Reciprocal boundaries and neighbour recommendations

Because the row is refused, the JSON authors no collision edges. These are routing recommendations for
surviving neighbours, not claims that the refused node can activate.

### Legal conveyancing / matter coverage

Route the active professional file to Legal where holder relation and matter structure support it:
client engagement, matter reference, two represented sides, due diligence, enquiries, drafted and
executed instruments, undertakings, completion and registration. Legal must not infer that every title
copy or property form belongs to an active matter; an isolated owner-held record can stand in Finance
or a residual.

Shared bytes: `Property information form - completed.pdf` and `RE_ enquiries - reply to Q14
boundary.eml`. Their assertions and undertakings are Legal matter evidence. They must not become
verified property facts merely because the address repeats.

### `finance.household-property`

Route the owner's retained acquisition/disposal record here: title and registration evidence,
completion/closing statement, transaction-tax confirmation, purchase or sale closing record, and
related ownership records. Household-property must not absorb a law firm's entire working matter or
third-party identity pack merely because the client bought a home.

Shared bytes: `Official copy - title register - AB123456.pdf` and `Completion statement.pdf`. In a
professional matter they are Legal working records; in the owner's archive they are lasting household
records. Custody and accepted group context may distinguish the views, but the bytes do not announce
when the matter dissolves.

### `finance.loans-mortgage` and refused mortgage-brokering

The mortgage offer is the borrower's Finance lending record and may also join the conveyancing group.
The loan row must not take the contract, searches and transfer merely because the advance funds the
price. The refused brokering label contributes no third template; a broker-held offer remains Finance
and may join a broker case group.

Shared bytes: `Mortgage offer - 14 Marsh Lane.pdf`. Multi-group membership is sufficient; no
neighbourhood may copy debt facts onto other transaction members.

### `construction_property.survey-valuation`

Survey/valuation holds the professional opinion where reliance structure, basis, inspection date and
certification support it. Legal may hold the same report as an input in the transaction group.
Survey/valuation must not absorb title, searches and contract; Legal must not erase the report's
professional-instruction reading.

Shared bytes: `Residential Appraisal Report - 42 Oak Street.pdf` or a mortgage valuation supplied into
the purchase pack. The intended lender or buyer is a role; report structure remains the discriminator.

### `construction_property.tenancy-management`

A leasehold resale pack can contain service-charge statements, building insurance, arrears replies and
management-company forms. Those are tenancy/block-management lifecycle records supplied into the Legal
sale matter. Sale grouping must not convert ongoing management records into transaction-native
documents; management must not take the transfer and contract.

Shared bytes: a resale management pack and its service-charge statement. Membership in a sale bundle
does not erase the ongoing management reading.

### Agency listing and instruments

Marketing particulars, floorplans, viewing feedback and offer negotiation remain agency-listing
material. The memorandum of sale can bridge agency and Legal groups. The executed contract, transfer
and lease remain Legal instruments; an address and signature do not turn every instrument into a
property-industry template.

## Collision fixtures, both directions

**Would wrongly fire the refused row:** `Official copy - title register - AB123456.pdf`. It contains a
property address, title number, proprietor and charge entries, but it may have been downloaded years
after any sale. The title number identifies land across transactions. Without a live matter or accepted
transaction group, it routes to `finance.household-property` in an owner's corpus or Independent
Records.

**Must not be lost to the refused row:** `Conveyancing Matter Export - 14 Marsh Lane.zip`. Its manifest
contains engagement, identity checks, searches, enquiries, contract, completion, undertakings and
registration. That is the law firm's matter export. Calling it sale-purchase on a property schema would
erase custody and duplicate Legal.

**Household boundary fixture:** `Buildings insurance schedule - 14 Marsh Lane.pdf`. Completion-adjacent
dates and the same address do not make it a transaction member. It is ongoing insurance/household
material.

## Files considered and rejected from this node

The JSON retains concrete fixtures so refusal is auditable, but none activates this node:

- `Official copy - title register - AB123456.pdf` — owner-held household record or Legal input.
- `Property information form - completed.pdf` — seller assertion in conveyancing, not verified fact.
- `Local authority search - result.pdf` — time-bounded Legal due diligence or standalone record.
- `AML - passport and bank statements.pdf` — Identity/Finance material protected first inside Legal.
- `Completion statement.pdf` — Legal closing record and owner-held household Finance residue.
- `Mortgage offer - 14 Marsh Lane.pdf` — `finance.loans-mortgage`; may join the transaction group.
- `RE_ enquiries - reply to Q14 boundary.eml` — Legal correspondence and party assertion.
- `14 Marsh Lane - conveyancing pack.zip` — mixed Legal matter archive; inspect its manifest.
- `Buildings insurance schedule - 14 Marsh Lane.pdf` — ongoing insurance/household record.
- Estate-agent particulars and viewing sheets — `construction_property.agency-listing`.
- A surveyor's report — `construction_property.survey-valuation`, even when supplied into Legal.
- A leasehold resale pack — tenancy, block-management or service-charge lifecycle supplied into Legal.
- Removals quotation, search-fee receipt or tax payment confirmation — Receipts and Confirmations.
- A generic home-buying guide or market article — Reading Inbox or Reference Clips.

## fields and proposed_fields

`fields: []`. Templates do not copy schema fields, and `construction_property` declares none.

`proposed_fields: []`. No key rescues the node:

- `property` is already a schema-level proposal and remains the matter/record subject.
- `transaction` is an accepted group or Legal matter, not necessarily a file-local fact.
- `buyer` and `seller` are values of a party-role concept, not structures or separate fields.
- `stage` duplicates document-function, `work_type` or Finance `record_type` values.
- `conveyancer` is a professional/counterparty role.
- `purpose` is not licensed for this schema and cannot be cloned to make the row pass.

Every candidate is a subject, role, group identifier or value — exactly the charge this pass tested.

## Residual and coverage routing

- Active conveyancing matter: Legal matter coverage and an accepted transaction group.
- Owner's lasting title, closing, tax and acquisition/disposal records: `finance.household-property`.
- Mortgage application, offer and servicing: `finance.loans-mortgage`.
- Survey or valuation deliverable: `construction_property.survey-valuation`.
- Tenancy, service-charge or resale-management inputs: their management templates, also grouped into
  Legal where supported.
- Identity, source-of-funds and account material: protection first; Protected Records if isolated.
- Durable standalone title/search/form: Independent Records when no stronger association exists.
- Unresolved or collapsed matter fragments: Review Later.
- Password-protected portal export: Unsupported or Encrypted.
- Isolated fees and confirmations: Receipts and Confirmations.

## NEEDS-JOSEPH

**NJ-CP-SP-1 — retire or re-roster under Legal?** A new `legal.conveyancing` template could be
legitimate only if tested against Legal's default and shown to differ in recognition or privacy.
Simply moving this JSON would preserve duplication.

**NJ-CP-SP-2 — buyer/seller views.** Decide whether buyer-side and seller-side are user-approved group
views or eventually one canonical party-role fact. This pass treats them as role values and mints no
keys. Buyer and seller fields would encode positions as structures and repeat the problem elsewhere.

**NJ-CP-SP-3 — completed-group lifecycle.** Decide which records an owner retains after completion and
whether an accepted conveyancing group dissolves, archives or remains intact. Keeping the protected
group, retaining selected records in household property, or offering both views are user/retention
choices, not evidence for a construction/property node.

## What changed in this pass

- Replaced **Depth: GIST** with **Depth: J-DEPTH**.
- Reversed `refuse_node: false` to `true` after the law/finance boundary test.
- Reframed transaction stages as Legal matter/document-function values and buyer/seller as roles.
- Removed collision edges from the refused node; retained neighbour recommendations here.
- Preserved the file inventory, recognition cautions, empty fields, protection and residual routes.
- Added leg-by-leg reasoning, reciprocal boundaries, collision fixtures and explicit alternatives.

## Audit

JSON was written before this memo. Verification checks parse, exact key set, `fields: []`, no invented
keys, refusal state, source types, residual names, exact quotations, header and ending, and agreement
between this memo and the JSON.

**End of research memo — construction_property.sale-purchase — REFUSED.**
