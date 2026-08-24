# R1b research — `finance.hoa-residents-association`

Date: 2026-08-22
Assignment: one `kind: template` row on the `finance` schema
Outcome: **keep the node** (`refuse_node: false`)
Owned outputs: this memo and `finance.hoa-residents-association.json` only

## Binding sources read

- `planning/00-database-agent-product-design.md`, read in full. It is authoritative for the
  observation/fact boundary, Finance fields, role separation, bounded model use, grouping
  firewall, editable templates, residual names and privacy posture.
- The relevant extraction, fact, grouping, tree, residual and privacy renderings in
  `planning/01-product-design-structured.md`. They were used only as locators; `00` wins.
- `planning/prompts/ALIGNMENT.md`, `planning/domains/_CONTRACT.md`,
  `planning/domains/CONNECTION.md` and `planning/domains/CONNECTION-EXAMPLES.md`, including the
  schema/template node test, set-valued activation, closed edge vocabulary, schema-only
  `also_holds_with`, browse-only parent and grouping firewall.
- `planning/26-research-dispatch-state.md`, the current R1b workflow, the exact stamped output of
  `make_prompt.py finance.hoa-residents-association`, and the D2, D6 and J-IND ratifications in
  `planning/overnight/council/DECISION-BRIEF.md`.
- The exact roster row, all Finance roster rows, relevant Legal and Photos neighbours,
  `planning/domains/canonical_fields.json`, `planning/domains/nodes/finance.json`, and the closed
  `SOURCE_TYPES` in `src/evidence_shape/vocabulary.py`.
- Landed or currently visible neighbouring node drafts, read but not changed:
  `finance.personal-records`, `finance.receipts-expenses`, `finance.small-business-bookkeeping`,
  `finance.insurance-corporate`, `finance.household-property`, and
  `finance.subscriptions-utilities`. The last two already carry concrete collision stubs toward
  this id. They were untracked/current workspace drafts during this pass, so R1c must recheck
  reciprocity against whatever versions finally land rather than treating them as authority.

## External artifact reality checks

These are primary sources used only to establish real record shapes. They do not override the
product design, establish a universal jurisdiction rule, supply legal advice, or justify any
retention period or numeric threshold in the node.

- California Civil Code [section 5200](https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=CIV&sectionNum=5200.)
  currently defines association records broadly enough to include interim financial statements,
  general ledgers, contracts, tax returns, reserve records, agendas and minutes, membership lists,
  governing documents, election materials, invoices, receipts and bank statements. This is strong
  evidence that the roster's mix of financial, administrative and governance files is a real
  resident-held corpus rather than an invented category.
- California Civil Code [section 5300](https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=CIV&sectionNum=5300.)
  establishes a concrete annual-budget-report artifact with operating-budget and reserve content.
  [Section 4765](https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=CIV&sectionNum=4765)
  establishes association architectural-review decisions, and
  [section 5855](https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=CIV&sectionNum=5855.)
  establishes written violation/hearing and post-decision notifications. The node generalizes only
  their document structures.
- The 2025 Florida Statutes [section 720.303](https://www.flsenate.gov/Laws/Statutes/2025/0720.303)
  lists bylaws, declarations, rules, minutes, member and parcel rosters, insurance, contracts,
  detailed member assessment accounts, financial reports, ballots and proxies as official records.
  It also describes protected web or app access to association documents. This grounds the owner
  statement, ballot, portal and archive fixtures while demonstrating why resident records can be
  privacy-dense.
- Washington [RCW 64.34.372](https://app.leg.wa.gov/RCW/default.aspx?cite=64.34.372)
  lists budgets, receipts and expenditures, minutes, owner contacts and votes, governing documents,
  architectural-approval materials, enforcement-decision materials, insurance and notices. It also
  distinguishes association records from a managing agent's custody, supporting the manager versus
  association role seam.
- Washington [RCW 64.90.640](https://app.leg.wa.gov/RCW/default.aspx?cite=64.90.640)
  shows a signed resale certificate containing unit assessments, delinquency, fees, reserve and
  budget material, insurance, violations, governing documents and recent minutes. That supports a
  genuinely mixed Finance/Legal/property fixture without flattening all attached facts onto the
  certificate or its siblings.
- AppFolio's current [Homeowners Online Portal overview](https://www.appfolio.com/help/owner-portal)
  documents dues payments, account ledgers, payment confirmations, architectural reviews, secure
  shared documents, board packets and association calendars in a real management portal. This
  validates the screenshot, email and calendar sources while reinforcing that the platform and
  management company are not necessarily the association itself.
- The IRS [Form 1120-H instructions](https://www.irs.gov/instructions/i1120h) confirm that an
  association can have an explicit tax-year record. This supports the narrow boundary: `tax_year`
  may be legal on an actual labelled tax return, but a budget year, assessment period, meeting date
  or reserve-study date is not silently converted into that field.

## Node test

The proposal survives without padding.

### Detection differs from Finance's default

The Finance schema default detects institution-issued account records through account descriptors,
statement or billing periods, balance pairs and transaction rows. This situation additionally and
distinctively detects:

- an association-to-member assessment account;
- special-assessment and board-action notices;
- governing documents with membership, assessment, voting and property-use clauses;
- association meeting minutes with quorum, motions and votes;
- adopted budgets, reserve schedules and reserve studies;
- architectural applications and decisions;
- violation, hearing and enforcement notices; and
- resale certificates that combine account, governance, reserve and status disclosures.

An HOA token, management-company name, address, amount or word `assessment` is explicitly
insufficient. The two same-schema negative fixtures make this test concrete: a metered water bill
with the same unit address belongs to subscriptions/utilities, and a public property-tax assessment
belongs to household/property.

### Recommended dimensions differ

Finance defaults to `institution -> account_type -> record_type`. This row recommends
`institution -> record_type`, with `institution` carrying the explicitly named association as the
roster directs.

`account_type` is omitted because a unit, lot or parcel is a property relationship, not a kind of
financial account, and most resident corpora have one relationship per association. It remains an
optional user-added level only when the record itself labels materially distinct member,
assessment or ledger account types. `tax_year` is omitted because association records usually use
meeting dates, fiscal periods, assessment periods, policy terms and effective dates rather than a
tax-year role. The order remains shallow and editable.

### Privacy differs in concentration, not authority

This is still Finance's `potentially_sensitive` posture; the row does not invent a P7 handling
class. The concentration is unusually broad: exact unit and property addresses, resident contacts,
owner balances and payments, ballots and proxies, signatures, architectural plans, alleged
violations, access information, and resale or lien-risk material can occur in one relationship.
That supports redacted labels, local-first extraction and protected fallthroughs. It does not let
the template classify, move or expose the files by itself.

## Bottom-up file fixtures

The JSON carries twenty-two concrete files; this is the compact audit view.

1. **`Annual Assessment Statement - Unit 4B.pdf`** — `text_document`; association, owner, unit,
   explicitly labelled assessment account, charges, payments and balance. `institution` is the
   association, not the management footer. The statement year is not `tax_year`. Protected Records.
2. **`Special Assessment Notice - Roof Replacement.pdf`** — `text_document`; board action,
   project, owner/lot, apportioned charge and installments. Special assessment is a charge, not
   `account_type`. Independent Records.
3. **`HOA Payment Receipt - 2026-04-01.eml`** — `email`; management sender acting on behalf of the
   association, member account, transaction and remaining balance. Without the relationship it is
   an isolated receipt. Receipts and Confirmations.
4. **`Declaration of Covenants Conditions and Restrictions - Recorded.pdf`** — `text_document`;
   recorded declaration, association/community definitions, membership, assessments, restrictions
   and execution. Finance and Legal activate on different evidence. Protected Records.
5. **`Bylaws - Oak Ridge HOA.pdf`** — `text_document`; adopted governance articles, membership,
   board, voting and assessment clauses. Certifying officers are not account holders. Independent
   Records.
6. **`Board Meeting Minutes - 2026-06-18.pdf`** — `text_document`; association, board/quorum,
   agenda, motions, votes and adopted result. The meeting date is not a tax year. Independent
   Records.
7. **`2026 Adopted Budget and Reserve Schedule.xlsx`** — `spreadsheet`; reporting entity,
   operating-budget and reserve sheets, assessment income and expense categories. Budget accounts
   are not `account_type`; the manager or frequent vendor is not institution. Protected Records.
8. **`Reserve Study - Final 2025.pdf`** — `text_document`; prepared-for association, consultant,
   common-component inventory, costs and funding analysis. The association and authoring
   consultant stay in different roles. Independent Records.
9. **`Architectural Change Request - Patio - Approved.pdf`** — `text_document`; association,
   committee, applicant, unit, work description and signed decision. The attached plans cannot
   inherit approval facts. Also Legal; Protected Records.
10. **`Violation Notice - Balcony Storage.pdf`** — `text_document`; agent acting for association,
    member/unit, rule citation, allegation, cure and hearing. An allegation is not a proven outcome;
    later lien or court facts do not propagate. Also Legal; Protected Records.
11. **`Annual Meeting Proxy and Ballot - 2026.pdf`** — `text_document`; association meeting,
    member/unit, proxy, choices and signature. Votes and signatures remain protected; the election
    year is not `tax_year`. Also Legal.
12. **`Resale Certificate - Unit 4B - Signed.pdf`** — `text_document`; association certification,
    unit and seller, assessment balances, fees, reserves, budget, insurance, violations and
    attached/referenced governance material. Sibling facts do not propagate. Also Legal.
13. **`Owner Portal - Account Balance.png`** — `ocr`; screenshot-origin evidence plus OCR of the
    explicit association, owner account, unit, charges and balance. The platform and manager do not
    become institution. Also Photos; Temporary Screenshots if the account reading fails.
14. **`IMG_9034.HEIC`** — `image`; camera facts and an unreadable bulletin. It can join a meeting
    packet only as a sparse member and receives no Finance fact from neighbours. Also Photos;
    One-Off Images.
15. **`HOA_Documents.zip`** — `archive`; mixed association-shaped member names visible only in the
    manifest. The container gets no dominant association, member or year from member names and is
    not unpacked. Review Later.
16. **`Oak Ridge HOA Annual Meeting.ics`** — `calendar`; structured summary, schedule, venue,
    management organizer and agenda link. Calendar syntax alone is not a financial record; the
    association role comes from content. Independent Records.
17. **`water_bill_unit_4B.pdf`** — `text_document`; provider, service address, meter, usage, rate
    plan and period. This is the subscriptions/utilities collision and must not become an HOA file
    from the address or recurring amount. Protected Records.
18. **`County Property Tax Statement - Unit 4B - Tax Year 2025.pdf`** — `text_document`; public
    authority, parcel, assessed value and explicit tax year. This is the household/property
    collision; assessment vocabulary does not make it association dues. Protected Records.
19. **`association_notice_scan.pdf`** — `ocr`; cropped NOTICE, unit and date, with no recoverable
    issuer or subject. It may join a review group without receiving association or record-type
    facts. Review Later.
20. **`Resident_Portal_Download.zip`** — `opaque_binary`; encrypted, filename-only and without a
    manifest. Only universal facts are legal; neighbours do not rescue it. Unsupported or
    Encrypted.
21. **`Condominium Master Insurance Certificate.pdf`** — `text_document`; carrier, producer,
    association as named insured, policy rows, limits and term. It belongs to corporate insurance;
    the association name and portal provenance do not make institution invert from carrier to
    association. Protected Records.
22. **`Understanding Condo Association Rules.pdf`** — `text_document`; general consumer article
    with fictional examples and no holder, adopted instrument or completed decision. Dense HOA
    vocabulary does not activate the template. Reading Inbox.

The set covers labelled forms and prose, spreadsheets, OCR screenshot and sparse scan, a camera
image, email, calendar, archive manifest, encrypted binary, same-schema neighbours, cross-schema
files, a tempting reading-material false positive, and explicit grouping without fact copying.

## Fields and proposal discipline

`fields` is empty because this is a template and must reuse the Finance schema rather than copy it.
The inherited legal keys are `institution`, `account_type`, `tax_year` and `record_type`, plus
universal fields. The Finance schema's existing `account_holder` proposal is used in fixtures where
an owner or member is explicitly labelled; it remains destination-ineligible and is not re-proposed
by this row.

`proposed_fields` is deliberately empty.

- The current `finance.household-property` draft already proposes `property`. This row seconds the
  underlying need for multi-property residents, but duplicating the proposal would create two
  private versions of one join handle. Until R1c accepts a shared key, unit, lot and property labels
  remain observations and accepted-group anchors.
- No private `association`, `community`, `unit`, `assessment_type`, `meeting_year`, `fiscal_year`,
  `violation_status` or `manager` field is minted. Association is the roster-directed reading of
  `institution`; document functions are values of `record_type`; the manager/producer remains an
  observation while the role question is open.
- `account_type` is legal only for an explicit member, assessment or ledger account descriptor. A
  unit, lot, voting class, assessment category or budget account is not silently coerced into it.
- `tax_year` is legal only for an explicit tax-year slot on an actual tax record. The IRS source
  proves that such an artifact can exist; it does not turn every annual record into one.

## Recognition and grouping firewall

Deterministic recognition requires a completed relationship or governance structure, not a topic
word. The `never_alone` list covers association vocabulary, association and manager names,
addresses, unit/lot tokens, money, assessment/meeting/governance words, bare years, formats,
folders and sessions, sparse captures, missing EXIF and unreadable filenames.

The model cases are bounded role and coherence questions: association versus agent or producer,
operative record versus generic material, OCR role ambiguity, address role, packet purpose,
manager correspondence, association budget versus holder bookkeeping, and unfamiliar-language
structures. Unknown is the valid outcome.

Grouping keeps distinct, reviewable packets for one association relationship, one member account,
one meeting, one architectural request, one enforcement matter, one special-assessment project,
one portal or records-request export, and duplicates or versions. Multi-membership remains visible.
The image, sparse scan, archive, attached plan, contractor proposal and later legal correspondence
are all firewall cases: membership does not create `institution`, `account_holder`, `record_type`,
`account_type` or `tax_year` on a file that lacks its own evidence.

## Dimensions and work types

The current order is `institution -> record_type`; `time_first` is false. The association provides
the context needed to interpret the leaf. `account_type` is optional only where it splits explicit
accounts, and `tax_year` is optional only for explicit tax records. A one-association corpus should
flatten `institution`; a multi-property corpus stays group-led until the shared property proposal
is adjudicated.

The work types are values, not child nodes: assessment statements, dues/payment notices and
receipts, special assessments, declarations/covenants, bylaws/articles, rules/policies/resolutions,
meeting notices/agendas/minutes, budgets and reserve records, architectural requests/decisions,
violations/hearings/enforcement notices, election material, resale certificates/status disclosures,
and correspondence.

## Edges authored

All eight collision endpoints are same-kind roster templates:

- `finance.household-property` — reciprocal with the current draft: association governance and
  member-assessment structure versus acquisition, title, public tax, inspection and improvement.
- `finance.subscriptions-utilities` — reciprocal with the current draft: association dues and
  governance versus metered service, usage, rate plan or subscription lifecycle.
- `finance.personal-records` — member-assessment account versus financial-institution deposit/card
  account; balance and identifier slots alone cannot choose.
- `finance.receipts-expenses` — continuing association/member-account receipt versus isolated
  seller/order transaction.
- `finance.small-business-bookkeeping` — association reporting entity and governance context versus
  the holder's own operating books; board-member possession is not business ownership.
- `finance.insurance-corporate` — association master policy with carrier-policy structure versus an
  association-issued administrative/governance record. This fixture exposes the same-schema
  `institution` role inversion sharply.
- `legal.leases-agreements` — operative instrument clauses and execution versus association
  account/governance/admin structure. A governing document may also activate Legal on disjoint
  evidence.
- `legal.personal-legal-matters` — routine association enforcement process versus lien,
  collection, attorney, court, settlement or contested-proceeding structure.

`also_holds_with` is empty because CONNECTION restricts it to schema pairs. The landed Finance
schema already carries Finance/Legal and Finance/Photos joins. File fixtures use `also_schema` for
actual Legal and Photos co-activations. `role_split` is empty because it can only connect canonical
keys; this row cannot create an `association` key merely to express its open tension.

`parent_id` remains null because R1b does not author browse shelving. The two reciprocal-looking
edges toward current neighbour drafts must be rechecked in R1c because those drafts were not a
binding contract during this pass.

## Neighbours considered without an edge

- **`finance` and `legal` schemas** — `schema_id` and schema-level co-activation are the correct
  joins. A template cannot collide with its own schema, and authored `also_holds_with` is not a
  template edge.
- **`photos.screenshot-captures` and `photos.scanned-documents`** — capture origin and OCR document
  content can both be true on disjoint evidence. Treating them as mutex would erase the intended
  Finance/Photos join; the screenshot and camera fixtures use `also_schema` instead.
- **`finance.tax-filings`** — an association tax return from a records request is genuinely a tax
  filing and may also join the association corpus. Explicit form/tax-year structure is not
  confusable with routine dues, minutes or governing records, so multi-membership is enough.
- **`finance.cap-table-equity`** — board minutes, elections and budgets share governance words, but
  share, option, grant, capitalization and valuation structures are independently discriminating.
  A board title or officer name alone already fires neither node.
- **Contacts (`.vcf`)** — a management-office or board contact is an address-book record, not an
  association document. The contact source type remains privacy-protected and is not listed as a
  plausible file kind here.
- **Residual templates** — they are broad fallback homes, not collision endpoints. The required
  Independent Records residual and seven concrete additional fallthroughs use the closed names.

## Files considered and rejected or bounded

- Property listings, real-estate advertisements and generic buyer guides can name an HOA, dues and
  restrictions without establishing the holder's association relationship.
- Blank covenant, bylaws, architectural-request, meeting-minutes, budget and violation templates do
  not fire. Filled role-bearing structure and a completed record function matter.
- Newsletters, social-event flyers and amenity announcements are not automatically Finance records.
  A durable official notice may land only when the association and administrative function are
  evidenced; general reading stays broad.
- Utility bills and public property-tax statements remain their sibling Finance situations despite
  sharing the unit address, recurrence, amount or assessment vocabulary.
- A master insurance certificate remains an insurance record when carrier-policy structure is the
  document's own shape. Portal placement and association named-insured text do not invert
  `institution`.
- A management-company contact card, maintenance chat, vendor proposal, law-firm letter, generic
  reserve article or consumer association guide is not absorbed from one organization name.
- Sparse photographs and cropped scans may join accepted matters but keep only their own facts.
  Missing EXIF does not prove screenshot origin.
- Encrypted portal downloads remain metadata-only and manually attachable; filenames and session
  neighbours cannot infer their purpose.

## NEEDS-JOSEPH (this node only)

- **NJ-hoa-1 — association role and future property order.** The roster says `institution` holds
  the association; the canonical role says financial or record-issuing institution. A manager,
  portal, lawyer, accountant, reserve consultant or insurer often produces the artifact. This row
  uses the association only when its relationship role is explicit and leaves the producer as an
  observation, but R1c must decide whether that is a valid record-belongs-to reading or whether a
  canonical `association` key is required. If `property` is accepted, Joseph must also choose
  `association -> property -> record_type` versus `property -> association -> record_type` for a
  multi-property holder. Until then the recommendation stays `institution -> record_type`.
- **NJ-hoa-2 — whole relationship or Finance-only subset.** The roster expressly includes
  covenants, minutes and violations, so this proposal treats the whole association relationship as
  one Finance-backed organizational situation and co-activates Legal on operative or contested
  evidence. Joseph should confirm that product boundary, or narrow the node to assessments and
  administration while making governing and enforcement files primarily Legal. The answer changes
  which branch is visually primary, not the observation/fact firewall or safety posture.

## Validation evidence

- `jq empty` passes, and row-specific assertions cover exact metadata, template shape, no copied
  fields, no private proposal, the distinct destination-eligible dimension order, closed source
  types, canonical/legal facts, roster-resolving same-kind collisions, schema-resolving
  `also_schema` values and closed residual names.
- Twenty-two file examples are present. They include explicit false positives, Legal and Photos
  co-activation, unsupported data, and four `group_without_copying_facts: true` firewall cases.
- Every attributed design span in the JSON was checked as a fixed string against
  `planning/00-database-agent-product-design.md`: **23 checked, 0 misses**. The first pass caught
  and corrected one punctuation drift before this finished audit.
- Numeric and vocabulary scans found no confidence score, cutoff, ranking weight, handling class,
  invented source type, authored `shares_field`, duplicate collision endpoint or folder-path fact.
- The legacy `planning/domains/check.py` baseline remains **14 files, 574 entries, 566 in-file
  problems; 574 unique ids and 0 cross-file problems**. As recorded in dispatch state, it does not
  scan `nodes/`; the row-specific assertions above are the evidence for this output.
- Scoped status shows exactly the two assigned paths as newly written, and the trailing-whitespace
  scan is empty for both. No roster, canonical field, contract, checker, source, specification or
  neighbouring node was edited.
