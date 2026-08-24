# R1b research — `finance.household-property`

Date: 2026-08-22
Assignment: one `kind: template` row on the `finance` schema
Outcome: **keep the node** (`refuse_node: false`)
Owned outputs: this memo and `finance.household-property.json` only

## Binding sources read

- `planning/00-database-agent-product-design.md`, read in full. It is authoritative for the
  observation/fact boundary, the Finance field set, grouping firewall, template behaviour,
  residual names and privacy posture.
- The relevant extraction, fact, grouping, tree, residual and privacy renderings in
  `planning/01-product-design-structured.md`. They were used only as locators; `00` wins.
- `planning/domains/_CONTRACT.md`, `planning/prompts/ALIGNMENT.md`,
  `planning/domains/CONNECTION.md` and `planning/domains/CONNECTION-EXAMPLES.md`, including the
  schema/template node test, set-valued activation, closed edge vocabulary, browse-only parent,
  schema-only `also_holds_with`, and grouping firewall.
- `planning/26-research-dispatch-state.md`, the current R1b workflow, the stamped output of
  `make_prompt.py finance.household-property`, and the D2/D6/J-IND ratifications in
  `planning/overnight/council/DECISION-BRIEF.md`.
- The exact roster row, all relevant neighbour rows, `planning/domains/canonical_fields.json`,
  and the closed `SOURCE_TYPES` in `src/evidence_shape/vocabulary.py`.
- Landed local nodes used for alignment: `finance`, `finance.personal-records`,
  `finance.receipts-expenses`, `finance.loans-mortgage`, `finance.insurance-personal`,
  `finance.tax-filings`, `legal`, and the prior `finance.small-business-bookkeeping` output.
  The loans and personal-insurance nodes already carry reciprocal collision stubs toward this row.

## External artifact reality checks

These sources establish real document shapes only. No retention period, legal conclusion,
jurisdiction rule, form-number taxonomy or filing advice was copied into the node.

- The US Consumer Financial Protection Bureau’s [sample Closing Disclosure and explainer](https://www.consumerfinance.gov/owning-a-home/closing-disclosure/)
  confirms a multi-page acquisition/loan record with borrower, property, loan, escrow, cost and
  transaction tables. Its [closing-document review guide](https://www.consumerfinance.gov/owning-a-home/close/review-documents-before-closing/)
  also distinguishes the Closing Disclosure from the deed and other closing documents. This
  supports the loan-versus-property collision rather than collapsing the whole packet into one
  record type.
- The US Internal Revenue Service’s [Publication 530](https://www.irs.gov/publications/p530)
  identifies purchase contracts, settlement papers, improvement receipts and similar evidence as
  records homeowners actually keep. Its distinction among settlement, appraisal, inspection,
  improvement and repair material supports the heterogeneous property-lifecycle fixtures. The node
  records none of the publication’s tax treatment or retention rules.
- HM Land Registry’s [property-register guide](https://www.gov.uk/get-information-about-property-and-land/search-the-register)
  confirms distinct title-register, title-plan and title-summary artifacts, with title number,
  ownership, tenure, mortgage and boundary information. This is one jurisdiction’s implementation,
  used only to prove that the title fixture and its labelled slots are real.
- The US Federal Trade Commission’s [warranty guidance](https://consumer.ftc.gov/articles/warranties)
  confirms that households keep written warranties together with purchase receipts for major
  appliances. That supports one installed-system group while preserving the receipt/warranty
  distinction.
- UK government guidance on [building work and home repairs](https://www.gov.uk/government/publications/building-work-replacements-and-repairs-to-your-home/building-work-replacements-and-repairs-to-your-home)
  confirms completion or compliance certificates as real improvement artifacts. Again, its legal
  obligations and timing rules were not encoded.
- The UK government’s renting checklist describes a real
  [inventory or check-in report with photographs](https://www.gov.uk/government/publications/how-to-rent/how-to-rent-the-checklist-for-renting-in-england)
  separate from the tenancy agreement. This supports the tenancy-administration versus executed
  lease boundary.
- The New York City Department of Finance’s [property-tax guide](https://www.nyc.gov/assets/finance/downloads/pdf/brochures/class_1_guide.pdf)
  shows a bill structure with property details, market and assessed values, exemptions, a tax
  calculation and payment information. The fixture generalises the structure and retains only an
  explicit labelled tax-year fact.

## Node test

The row passes without padding.

### Detection differs

The Finance default detects institution-issued account records: statement or billing period,
account descriptor, balance pair and transaction table. This situation instead detects a
property-role structure across title/parcel records, acquisition or sale tables, property-tax
assessment rows, completed inspection or appraisal reports, improvement records, regulatory
certificates, installed-system warranties and tenancy condition inventories. A property address
alone is explicitly forbidden because it can be a subject, mailing, issuer, service, comparable or
capture address.

### Recommended dimensions differ

The Finance default is `institution -> account_type -> record_type`. That order is actively harmful
here: one home produces records from registries, assessors, settlement agents, lenders, inspectors,
contractors, manufacturers, insurers and managers. Issuer-first scatters one durable household
subject across many branches. Today the legal recommendation is only `record_type`; the useful
future order is `property -> record_type` if the shared vocabulary accepts `property`. The proposed
key is not smuggled into the current order.

This still has genuine v1 utility. An accepted single-property acquisition, tenancy or improvement
group can be kept whole or split shallowly by `record_type`. A corpus with several properties stays
group-led or flat until the subject key exists, rather than silently merging addresses or abusing
another field.

### Privacy differs in concentration

Property packets expose exact home addresses, owners and tenants, signatures, purchase or assessed
values, defects, boundary or access information, installed-system identifiers, and photographs
with possible GPS. That concentration needs redacted labels and thumbnails in shared interfaces in
addition to Finance’s general local-first safety posture. No P7 handling class is authored.

## Bottom-up file fixtures

The JSON carries seventeen concrete files; this is the compact audit view.

1. **`Closing Disclosure - 42 Oak Street - 2024.pdf`** — `text_document`; borrower, lender,
   subject-property and transaction tables. Legal Finance facts: issuer institution,
   mortgage-shaped `account_type`, `record_type`, universals. The property value remains an
   observation; the date is not `tax_year`. Protected Records if no packet lands.
2. **`Official Copy of Register - Title AB123456.pdf`** — `text_document`; registry issuer,
   title number, property description, ownership, tenure and encumbrance sections. Legal Finance
   facts: institution and record type. It can activate Legal independently. Protected Records.
3. **`Annual Property Tax Bill - Tax Year 2025 - 42 Oak St.pdf`** — `text_document`; explicit tax
   year, parcel, address, assessed values and amount due. Legal facts include `tax_year` only
   because the labelled slot exists; no year inference from the filename. Protected Records.
4. **`Home Inspection Report - 42 Oak Street.pdf`** — `text_document`; completed system-by-system
   report, photographs and inspector certification. It is not an insurance claim or approved
   improvement. Independent Records when isolated.
5. **`Residential Appraisal Report - 42 Oak Street.pdf`** — `text_document`; subject-property,
   comparable and valuation tables, appraiser certification. The appraiser is the issuer; an
   intended lender does not become institution. Independent Records.
6. **`Kitchen Remodel - Bright Plumbing - Invoice 7841.pdf`** — `text_document`; explicit service
   property, job scope, item rows and total. It is also receipt-shaped and therefore carries the
   receipts collision. Receipts and Confirmations when the property reading does not land.
7. **`Home Improvements Log.xlsx`** — `spreadsheet`; filled work, contractor, invoice, permit,
   warranty and receipt-link columns. It aggregates issuers, so no institution is chosen by
   frequency; dates do not become a tax year. Review Later if the purpose remains unresolved.
8. **`Building Regulations Completion Certificate - Loft Conversion.pdf`** — `text_document`;
   authority, application reference, site, completed work and approval result. It may activate
   Legal independently; it is not automatically an agreement. Independent Records.
9. **`Boiler Warranty - SN-R4K8821.pdf`** — `text_document`; manufacturer, installer, serial,
   installation job and warranty administrator in distinct roles. The explicit issuer is used;
   roles are not merged. Independent Records.
10. **`Move-in Inventory and Condition Report - 18 River Court.pdf`** — `text_document`; premises,
    room/item/condition rows, check-in date, photographs and acknowledgement. It is tenancy
    administration, not the lease instrument. Independent Records.
11. **`Rent Receipt - January 2026.eml`** — `email`; structured sender, tenancy reference,
    premises, period, amount and payment status. Month/year text is not a tax year. Receipts and
    Confirmations when isolated.
12. **`property_packet.zip`** — `archive`; title, plan, closing, inspection, appraisal, tax and
    instrument members visible in the manifest without unpacking. The archive can be a packet
    candidate, but neither member facts nor a dominant issuer propagate. Protected Records.
13. **`IMG_6021.HEIC`** — `image`; direct Photos facts from EXIF and no Finance fact. A nearby roof
    report may support reviewable repair-group membership, with
    `group_without_copying_facts: true`. One-Off Images if ungrouped.
14. **`Screenshot 2026-07-12 at 10.44.18.png`** — `ocr`; screenshot signals plus OCR of a
    contractor portal, job reference, service address and completion status. Capture facts and
    Finance facts rest on different evidence. Temporary Screenshots if the work reading fails.
15. **`Lease Agreement - 18 River Court - Signed.pdf`** — `text_document`; parties, premises,
    covenants and execution blocks. It is the mandatory legal collision fixture and deliberately
    receives no Finance field from rent or address text. It may join a tenancy group without fact
    copying. Protected Records.
16. **`Title Deeds.pdf`** — `opaque_binary`; encrypted and filename-only. Only universal facts are
    legal; session neighbours do not rescue it. Unsupported or Encrypted.
17. **`First-Time Home Buyer Guide.pdf`** — `text_document`; the tempting false positive. It is
    general instructional reading with fictional examples and no completed record. Reading Inbox.

## Observations, facts and the proposed field

`fields` is empty because this is a template and must not copy the Finance schema. Every legal
Finance fact in a fixture is one of `institution`, `account_type`, `tax_year` or `record_type`;
universal and independently active Photos fields also resolve canonically. Legal is a field-less
safety placeholder, so Legal co-activation contributes protection and no legal facts today.

### Proposed `property`

`property` is the one proposed destination-eligible string key. Its value is the durable property
subject a record concerns, normally supported by a labelled Subject Property, Premises, Property
Address, Parcel or Title Number slot. A readable user label can later be normalised or redacted; a
filename or prose address remains possible.

No existing key works:

- `institution` is the issuer and changes repeatedly across one property lifecycle.
- `account_type` is a kind of financial account, not the asset that a record concerns.
- `location` is the place where a capture was taken; using it for a document’s subject collapses
  roles and would turn a contractor’s office or comparable property into the household home.
- `project` is the named research/code project field; widening it would blur a real property with
  a temporary improvement project.
- `record_type` identifies the artifact kind but cannot distinguish two homes.

The proposal is not yet a legal fact. It appears in no `facts_legal` list and no
`dimension_order`. R1c should adjudicate whether a property-specific key is clearer than a shared
`asset` key that could also serve vehicle records. An exact address in a destination label is a
privacy choice for P10/user policy, not an automatic display string.

## Recognition and grouping firewall

Deterministic recognition requires a completed structure and a role-labelled property slot, not a
keyword. The `never_alone` list covers addresses, home/property vocabulary, issuers, money, bare
years, formats, folders or sessions, escrow counterparties, sparse photographs, missing EXIF and
unreadable filenames.

LLM cases are bounded interpretations: address-role ambiguity, OCR-damaged instruments,
condition-report type, packet coherence, prose correspondence, unfamiliar jurisdictions and
repair-image membership. The model may abstain and cannot invent a jurisdiction rule, a property
fact or a group member.

The grouping rules explicitly retain:

- one property lifecycle;
- one acquisition or sale packet;
- one improvement project;
- one tenancy period;
- one installed-system warranty/service series;
- duplicates and versions; and
- multi-membership across property, mortgage, legal, receipt and tax-support packets.

Sparse members keep their own facts. The roof photograph, encrypted deed, lease and archive are
all explicit firewall fixtures. Address agreement or retrieval adjacency may support membership;
neither creates `property`, `record_type`, `institution` or `tax_year` on the member.

## Dimensions and work types

The current order is `record_type` only and `time_first` is false. The intended order after field
adjudication is `property -> record_type`. Institution is omitted because issuer-first fragments a
home; account type is omitted because tenancy, ownership, improvement and warranty are not account
types; tax year is omitted because most lifecycle dates are not tax years.

The work-type list contains values only: purchase or sale closing, title or deed, plan or survey,
property-tax or assessment record, appraisal, inspection, improvement invoice/receipt/log,
permit/approval, completion certificate, warranty, tenancy inventory, rent/deposit receipt and
property correspondence. None is a child schema.

## Edges authored

All eight collision endpoints are same-kind roster templates:

- `finance.loans-mortgage` — debt servicing versus property lifecycle; reciprocal already landed.
- `finance.insurance-personal` — coverage/claim structure versus title, inspection and
  improvement structure; reciprocal already landed.
- `finance.receipts-expenses` — the same improvement invoice needs a service-property or job
  structure to cross the boundary.
- `finance.personal-records` — property-assessment bill versus financial-account statement.
- `finance.subscriptions-utilities` — recurring service and usage versus property lifecycle.
- `finance.hoa-residents-association` — association governance/assessment versus general property
  ownership and improvement.
- `finance.vehicle-records` — identical title, inspection, repair and warranty vocabulary,
  separated by parcel/building versus vehicle/odometer structure.
- `legal.leases-agreements` — operative executed lease versus Finance-side tenancy administration.

`also_holds_with` is deliberately empty. CONNECTION restricts that authored edge to schema pairs;
the landed Finance schema already also-holds with Legal and Photos. File fixtures use
`also_schema` to show actual multi-schema files, and template groups may overlap without inventing
a template-level edge. This is the one place the stamped prompt’s generic edge wording is narrower
under CONNECTION, so CONNECTION wins.

`parent_id` remains null because R1b does not author browse shelving. `role_split` remains empty:
the important split is proposed `property` versus canonical Photos `location`, but a role split may
only join canonical keys and this row cannot pre-author the proposal into that graph.

## Neighbours considered without an edge

- **`finance.tax-filings`** — improvement receipts, property-tax bills and settlement records can
  support a later tax packet, but the file is not confused with a filed return merely because it
  is useful evidence. That is overlapping group membership on one schema, not a mutex edge.
- **`legal.personal-legal-matters`** — the schema-level Finance/Legal join already covers deeds,
  regulatory certificates and other operative material; `legal.leases-agreements` is the specific
  template collision required by this row. A generic second template edge would add no new
  discriminator.
- **`photos.camera-events` and `photos.screenshot-captures`** — a property-condition image can
  carry Photos facts and later join a property group. The capture evidence is not mutex with OCR
  property-record evidence, and Finance/Photos already co-activate at schema level.
- **`finance.small-business-bookkeeping`** — a rental-property ledger may become business books
  only with operation-side evidence. A household address or rent line does not establish a
  business; where both accepted groups exist, multi-membership is enough.
- **`finance.tax-filings` and the `Protected Records` residual** are not duplicates: the former is
  a structured filing situation, the latter is an opt-in broad home when no deeper association is
  reliable.

## Rejected or bounded material

- A generic home-buying guide, renovation article, property listing, interior-design mood board or
  mortgage-rate explainer is reading/reference material, not the holder’s property record.
- A blank renovation budget, inspection checklist, lease template or warranty template does not
  fire. Filled slots and a completed record relationship matter.
- A vehicle title, vehicle inspection, car repair invoice or product warranty is handled by the
  vehicle/receipt situations unless parcel/building evidence exists.
- A signed lease stays on the Legal template side even though the tenancy group may surface it
  beside receipts and inventories.
- An isolated contractor or hardware receipt stays with Receipts and Confirmations unless its own
  service-address/job structure or a reviewable property group supports membership.
- Sparse photographs and screenshots remain Photos records; the absence of EXIF never proves a
  screenshot and group adjacency never writes Finance facts.
- Encrypted deeds and closing packets remain metadata-only; filenames and sessions cannot infer
  purpose.

## NEEDS-JOSEPH (this node only)

- **NJ-hp-1 — property or shared asset key.** Should the canonical catalogue accept the proposed
  destination-eligible `property` field, or generalise the requirement into `asset` for property,
  vehicles and perhaps other owned assets? The current keys cannot express the durable subject
  without collapsing issuer, account type, capture location or project. Until answered, the v1
  order remains `record_type` only and property identity stays on accepted groups.
- **NJ-hp-2 — one protected property branch or parallel schema branches.** When an acquisition or
  tenancy packet activates both Finance and Legal on disjoint evidence, should P10 normally show
  one property-centred branch containing protected Legal members, or parallel Finance and Legal
  branches under the shared-material policy? The schema graph supports both, and choosing a
  default decides a real household filing shape.

## Validation evidence

- `jq empty` passes. Explicit assertions pass for the exact id, template kind, Finance schema,
  null parent, placeholder launch, inference provenance, non-refusal, empty copied fields,
  non-empty recognition, `file_kinds.never_alone: true`, and `time_first: false`.
- Seventeen file examples are present. Every `facts_legal` key resolves to
  `canonical_fields.json`; `record_type` is destination-eligible and belongs to the inherited
  Finance set; the proposed `property` key appears in neither `facts_legal` nor
  `dimension_order`.
- Every collision endpoint resolves to a same-kind roster template. Every non-null `also_schema`
  resolves to a roster schema. Every example source type and file-kind source type belongs to the
  closed P5 vocabulary, and every fallthrough value is one of the nine residual names.
- The roof photograph, signed lease, archive and encrypted title fixtures carry the grouping
  firewall. Every example’s negative list names the folder-path prohibition, no fact key contains
  a path, no duplicate edge endpoint exists, and no authored `shares_field` appears.
- A fixed-string `rg` audit extracted every ASCII-single-quoted design span in the finished JSON
  and checked it against `planning/00-database-agent-product-design.md`: **23 checked, 0 misses**.
  This memo carries no attributed quotation of its own; external sources are paraphrased.
- Searches found no injected numeric cutoff, ranking value or authored P7 handling class. A
  trailing-whitespace scan is empty for both files; `git diff --no-index --check` emits no
  whitespace error for either new file.
- `python3 planning/domains/check.py` remains at the recorded legacy baseline: **14 files, 574
  entries, 566 pre-existing in-file problems; 574 unique ids, 0 cross-file problems**. As the
  dispatch state records, that checker does not yet scan `nodes/`; the row-specific assertions
  above are the evidence for this output.
- Scoped status shows exactly the two assigned paths as newly written. No roster, canonical
  field, contract, checker, source, spec or neighbouring node was edited.
