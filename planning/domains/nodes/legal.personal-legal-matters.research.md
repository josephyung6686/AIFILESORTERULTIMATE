# `legal.personal-legal-matters` — R1b research notes

Date: 2026-08-22

Roster row: `kind: template` · `schema_id: legal` · `launch: safety`

Owned output: [`legal.personal-legal-matters.json`](legal.personal-legal-matters.json)

## Outcome

The row is retained, with a deliberately narrower job than the broad Legal schema.

- The broad `legal` schema recognizes and protects executed instruments, proceedings, notarized
  records and counsel correspondence.
- This template recognizes the organizational situation in which a person holds those materials
  as a party, recipient, signer, appellant, claimant, respondent or otherwise directly involved
  individual in their own dispute or proceeding.
- A court caption or notary block is enough to trigger protective detection through the existing
  R2 rules. It is **not** enough to select this personal-matter template. The narrower selection
  requires direct holder-role or holder-facing service/correspondence evidence.
- The Legal schema is field-less under D1/PR-6. This template therefore writes no case number,
  party, court, matter, status, outcome, deadline, jurisdiction, representative, instrument kind,
  amount or branch label. It recommends no folder dimensions.

That holder-facing discriminator makes this a real template rather than a copy of the Legal
schema's default. It also creates meaningful boundaries against estate planning, ordinary signed
agreements and professional law-practice files.

## Authority read

The following sources were read directly before authoring the row.

- `planning/00-database-agent-product-design.md` — read in full, all 286 physical lines. It is the
  authority for observations versus facts, safety launch, local-first privacy, grouping without
  propagation, template recommendations, controlled residuals and the field/path separation.
- `planning/01-product-design-structured.md` — the complete relevant renderings for evidence and
  extractors, facts and schema activation, grouping, tree design, residual review, and privacy.
  It was used only as a locator; `00` wins.
- `planning/prompts/ALIGNMENT.md`, `planning/domains/_CONTRACT.md`,
  `planning/domains/CONNECTION.md`, and `planning/domains/CONNECTION-EXAMPLES.md` — read in full.
- `planning/overnight/council/DECISION-BRIEF.md` — ratified D1, D2, D4 and D6, plus the detailed D1,
  D4 and D6 reasoning. The relevant consequences are: no Legal field rows; no P7 handling-class
  vocabulary on this row; `jurisdiction` is a value and never a field or dimension; canonical
  keys are snake_case.
- `planning/domains/roster.json` — exact stamped assignment, every authored edge endpoint, the
  complete Legal template family and the required Finance/Identity/Protected Records checks.
- `planning/domains/canonical_fields.json` — all canonical keys. There is no Legal matter, party,
  court, case reference, proceeding role, status, outcome, deadline or legal document-kind key.
- `src/evidence_shape/vocabulary.py` — the closed `SOURCE_TYPES` list and reliability boundary.
- Landed `legal.json` and `legal.research.md` — the field-less safety schema and its broad
  recognition rules.
- Every landed template that already pointed at this row:
  `academic.homeschool`, `academic.k12-schooling`,
  `finance.hoa-residents-association`, `finance.insurance-corporate`,
  `finance.insurance-personal`, `finance.tax-filings`, and
  `identity.core-documents`. Their exact signals were reconciled rather than merely copied.
- Relevant no-edge research from `identity.immigration-visa`,
  `medical.personal-health-records`, `medical.dependant-child-health`,
  `career.credentials-licenses`, `academic.iep-accommodation-plans`,
  `applications.k12-admission`, `finance.loans-mortgage`,
  `finance.investment-brokerage`, `finance.vehicle-records`,
  `finance.household-property`, `finance.cap-table-equity`,
  `research.manuscript-publication`, and `photos.messenger-export`.

## Current primary-source research

External research was limited to official courts, court services and professional standards. It
was used to verify document **shape**, privacy load and custody distinctions—not to encode legal
effect, give legal advice, choose a jurisdiction, or import jurisdiction-specific fields.

- The U.S. Courts [AO 440 summons](https://www.uscourts.gov/sites/default/files/ao440.pdf) carries
  the court heading, plaintiff/defendant roles, civil-action reference, defendant-facing response
  instruction, clerk signature and a separate proof-of-service section. This corroborates the
  caption + party roles + holder-facing service structure in the deterministic rules.
- The federal [Pro Se 1 civil complaint form](https://www.alsd.uscourts.gov/sites/alsd/files/forms/ProSe1Form.pdf)
  carries the court and case block, plaintiff and defendant roles, party contact sections,
  jurisdiction basis, allegations, relief and signature/certification. It also demonstrates why a
  completed personal filing may contain addresses and third-party details that must never become
  folder labels.
- HMCTS's [N1 claim-form page](https://www.gov.uk/government/publications/form-n1-claim-form-cpr-part-7)
  and current form show claim, claimant/defendant, amount, particulars and statement-of-truth
  structures. The official page also distributes an uncompleted reusable form. That is the basis
  for the blank-form negative: labelled legal fields without populated holder or matter evidence
  are not a personal legal matter.
- The Hong Kong Judiciary's [District Court forms](https://www.judiciary.hk/en/court_services_facilities/dcf.html)
  and [writ of summons](https://www.judiciary.hk/doc/en/court_services_facilities/dc/dc_form1.pdf)
  expose a different form vocabulary but the same high-level structure: named court, civil-action
  reference, parties in opposing roles, defendant-facing service/response language and registry
  issuance. The Judiciary's District Court guidance says forms may be completed in Chinese or
  English. This supports a jurisdiction-injected caption vocabulary and rejects a universal
  English-label list on the node.
- The U.S. District Court for Oregon's official
  [CM/ECF user manual](https://ord.uscourts.gov/index.php/filing-and-forms/cm-ecf/user-manual)
  describes the Notice of Electronic Filing as a generated email notice. It enumerates case name
  and number, filing party, document number, judge, docket text, recipients, non-electronic service
  recipients and attached-document links. That directly supports the native-email fixture while
  also showing why recipient addresses and docket text are protected observations rather than
  Legal facts.
- HMCTS's [civil-court-forms privacy notice](https://www.gov.uk/government/publications/privacy-notice-for-civil-court-forms/privacy-notice-for-civil-court-forms)
  says civil forms may collect names, addresses, contact details, economic circumstances,
  sensitive personal background and information about other people, including children. That
  supports local-first handling for whole matter bundles, not just obvious identity attachments.
- PACER's official [redaction FAQ](https://pacer.uscourts.gov/help/faqs/do-federal-courts-redact-information-case-files)
  says filers are responsible for redaction. This is an important negative: public availability,
  a court stamp or apparent redaction cannot be treated as proof that a downloaded filing is
  non-sensitive or safe for a cloud prompt.
- The American Bar Association's [Standard 5.5 on case files](https://www.americanbar.org/groups/legal_aid_indigent_defense/resource_center_for_access_to_justice/standards-and-policy/updated-standards-for-the-provision-of-civil-legal-aid/standard-5-5-on-case-files/)
  describes professional case files as containing a chronology of interviews and adversary
  contacts, written correspondence, pleadings, legal memoranda, research, task plans, time records
  and closing memoranda inside a case-management system. That is positive practice-file evidence,
  not generic legal-document evidence, and supplies the sharp boundary with
  `legal.practice-matter-file`.
- The Law Society's [file-closure management guidance](https://www.lawsociety.org.uk/topics/business-management/file-closure-management)
  independently treats a practice file as an operational object with matter completion, billing,
  asset return, retention and risk-review steps. This reinforces that a professional file is not
  selected merely because a lawyer authored a document.

## Existing R2 rules consumed

This row genuinely consumes three existing entries from
`planning/deferred-catalogues/08-sensitivity-detector/01-detector-rules.json`:

- `det-legal-court-filing` — protects a court-caption document when heading-position caption
  evidence co-occurs with case-structure labels.
- `det-legal-notarized-instrument` — protects a populated notarial or attestation block and rejects
  blank templates, advertisements and a signature line alone.
- `saf-legal-activation` — turns independently supported Legal activation into protection and
  explicitly rejects the word `agreement` alone.

The node cites only those rule-family ids and their semantic role. It does **not** copy their
label lists, injected count slots, regular expressions, jurisdiction extension slot, protected
boolean or handling-class ceiling. The latter are P7/R5 data and are outside this row. The
`legal_caption_gazetteer` remains injected by the chosen jurisdiction pack; this row authors no
court-name or law-firm gazetteer.

The distinction between the first rule and this template is intentional:

```text
court-caption detector fires  -> protect the file
direct holder relation exists -> personal-legal-matters may be selected
holder relation absent         -> keep protected, but template remains unknown
```

That sequence handles the unavoidable public-judgment false positive toward over-protection
rather than toward exposure or invented personal involvement.

## Files researched bottom-up

The JSON carries twenty-three concrete fixtures. The important coverage decisions are summarized
here.

- `Complaint - Lee v Northstar Retail Ltd.pdf` — native PDF with court/caption/party/signature
  structure and direct holder role. Only universal facts are legal.
- `Summons and Complaint - served scan.pdf` — no text layer, OCR recovery, service block. OCR does
  not establish service effectiveness or a live response period.
- `Notice of Electronic Filing - Lee v Northstar.eml` — native mail slots plus NEF structure.
  Source type and sender domain never suffice.
- `Letter from Counsel - Re Deposit Claim.docx` — explicit holder addressee and matter reference.
  Letterhead, privilege footer and creator metadata never suffice.
- `Demand for Deposit Refund.docx` — unlabelled operative prose; bounded local interpretation or
  `unknown`, never a deterministic dispute verdict.
- `Small Claims Evidence Index.xlsx` — labelled evidence-index structure. Rows do not create facts
  on the workbook or on linked files.
- `Hearing Notice - Claim HKSCT-Example.ics` — content can support the situation; calendar format
  cannot.
- `Case Bundle - Tenancy Deposit Dispute.zip` — manifest-only inspection with mixed members and a
  holder-facing anchor; never unpacked and never a fact-propagation source.
- `Screenshot - Tribunal Portal - Filing Accepted.png` — positive screen-origin evidence plus OCR;
  missing EXIF and a status badge do not establish either screenshot origin or current status.
- `Affidavit - Deposit Dispute - notarized.pdf` — populated jurat plus matter relationship. It does
  not prove truth, authenticity or admissibility.
- `Settlement Agreement and Release - Claim 88213.pdf` — genuine Finance/Legal co-activation and
  the item-level collision with personal and corporate insurance.
- `Order Granting Name Change.pdf` — genuine Identity/Legal co-activation and the reciprocal
  collision with `identity.core-documents`.
- `Notice of Assessment Appeal - Tax Tribunal.pdf` — Finance labels and contested-proceeding
  structure in one file; authority, reference, amount and deadline decide neither side alone.
- `HOA Lien Demand and Hearing Notice.pdf` — association enforcement plus a live contested legal
  step; an ordinary cure notice remains the HOA template's.
- `Custody Order - School Enrollment and Records.pdf` — Academic content and a court order in one
  file; school/child/year observations are not Legal facts.
- `Immigration Appeal Decision.pdf` — Identity/Legal co-activation, not a template mutex and not a
  reason to clone the College Applications `purpose` field.
- `Professional Board Disciplinary Hearing Notice.pdf` — Career/Legal co-activation; a board name,
  credential number or allegation does not establish status or discipline.
- `Last Will and Testament - signed.pdf` — protected Legal instrument but negative for this
  template; `legal.estate-planning` is sharper without proceeding evidence.
- `Residential Lease Agreement - executed.pdf` — protected Legal instrument but negative for this
  template; `legal.leases-agreements` is sharper without dispute evidence.
- `Practice Matter Export - Client Example-0087.zip` — professional custody and practice-only
  operational members make `legal.practice-matter-file` sharper.
- `Published Judgment - Public Interest Case.pdf` — R2 may protect it, but no holder relation means
  personal involvement remains unknown; Reading Inbox is the broad non-matter option.
- `Blank N1 Claim Form.pdf` — official labelled structure with no populated holder/matter evidence;
  Independent Records rather than invented litigation.
- `encrypted-case-materials.7z` — metadata only; filename never activates Legal or this template;
  Unsupported or Encrypted is the controlled residual.

Across all fixtures, `facts_legal` contains only universal canonical keys. No fixture writes a
folder path. Files with Finance, Identity, Academic, Career or Photos evidence use `also_schema`
to show independent schema activation; the template itself keeps `also_holds_with: []`, because
that edge is schema-to-schema only.

## Proposed fields and dimensions

`fields`, `proposed_fields`, `template.dimension_order` and `role_split` are all empty.

This is not a missing-research shortcut. It is the ratified field boundary:

- `institution` is the financial or record-issuing institution in the Finance vocabulary. It
  cannot be repurposed for a court, tribunal, law firm or regulator.
- `record_type` is the Finance enum. It cannot become a generic legal-document kind.
- `client` is the target side of the `our_firm` role split. It is not a party-of-record field and
  does not describe an individual holding their own papers.
- `purpose` remains College Applications-scoped under CONNECTION PR-1. No legal clone is minted.
- `event` is the Photos capture-event field. A hearing is not a photo event.
- `jurisdiction` is barred by ratified D4 as a field or destination dimension.
- Matter reference, party role, court, status, outcome, deadline, representative and instrument
  kind have no canonical key. This row records the need in `open_question`; it does not reverse D1
  through `proposed_fields`.

`work_types` is therefore a descriptive coverage vocabulary for the researcher and future field
decision. It is not a stored field, a set of child nodes or a licence to write values today.

The empty `dimension_order` is also the privacy recommendation. A path segment bearing a matter,
opponent or document kind can disclose the branch on a shared screen even when every member file is
protected. Launch recognition should unlock protection and a reviewable group, not a deep tree.

## Collision reconciliation

### Landed reciprocals preserved

The following seven landed template rows already authored `collides_with` edges to this id. Every
one is reciprocated in the JSON with a positive discriminator and a list of shared observations
that decide neither side.

- `academic.homeschool` — education-authority compliance filing versus court/tribunal proceeding.
- `academic.k12-schooling` — enrolled-student record versus proceeding or operative order.
- `finance.hoa-residents-association` — routine association enforcement versus filed, contested or
  representative-led legal matter.
- `finance.insurance-corporate` — coverage/claim-register structure versus dispute resolution or
  proceeding structure.
- `finance.insurance-personal` — carrier claim/estimate structure versus personal proceeding or
  dispute-and-execution structure.
- `finance.tax-filings` — tax-year/assessment structure versus tribunal, party-role and contested
  proceeding structure.
- `identity.core-documents` — document proving bearer/civil status versus legal proceeding and
  operative order.

Two inbound edges were intentionally tightened rather than repeated literally. An attorney
letterhead is never sufficient for either the Homeschool or HOA collision, and a statutory citation
alone is never sufficient for K-12. The reciprocal signals require the larger document structure.

### Legal sibling boundaries added

Three roster-valid sibling collisions are authored outward because they define this node's reason
to exist:

- `legal.estate-planning` — a planning/end-of-life instrument without adversarial matter structure
  is the estate situation; a contest, petition, service, hearing or adjudicative order is personal
  matter structure.
- `legal.leases-agreements` — an instrument creating an ongoing consensual obligation is the
  agreement situation; a demand, filed claim, contested proceeding or settlement explicitly
  resolving that dispute is the personal-matter situation.
- `legal.practice-matter-file` — party-facing custody versus professional case-management and
  practice operations. A shared pleading without either custody signal remains unresolved.

Those sibling files had not landed when this row was authored, so R1c must re-check reciprocity
after their owners finish. No sibling's content was invented or edited here.

## Neighbours considered that did not get an edge

- `finance`, `identity`, `academic`, `career`, `medical`, `photos` and `legal` schema ids — a
  template cannot collide with a schema. Schema co-activation belongs on schema rows, and this
  template already uses `legal` through `schema_id`.
- `identity.immigration-visa` — an evidence request, refusal, review or appeal may genuinely
  activate both Identity and Legal. That is co-activation, not a mutex. The immigration appeal
  fixture records `also_schema: identity`.
- `medical.personal-health-records` and `medical.dependant-child-health` — injury evidence,
  consent, custody and healthcare authorization can be part of a legal matter on disjoint
  evidence. The existing Medical/Legal schema relationship is the correct join; estate planning
  is the sharper template for advance directives and powers of attorney.
- `career.credentials-licenses` — board discipline can support Career and Legal at once. A
  credential record and a proceeding are not competing interpretations of one evidence item.
- `academic.iep-accommodation-plans` — a due-process complaint or settlement can be both Academic
  and Legal; the landed research correctly rejects a mutex and leaves schema co-activation to R1c.
- `applications.k12-admission` and `applications.purpose-packet` — a custody order can support an
  application packet, but packet purpose is grouping context and cannot be copied onto the legal
  record. No Applications `purpose` clone is added.
- `finance.loans-mortgage`, `finance.investment-brokerage`, `finance.vehicle-records`,
  `finance.household-property` and `finance.cap-table-equity` — foreclosure orders, releases,
  deeds, title records and equity instruments may activate Finance and Legal. Their own landed
  research either routes the sharper contract boundary to `legal.leases-agreements` or records
  schema co-activation; another broad personal-matter edge would duplicate the same seam.
- `research.manuscript-publication` — a signed publication licence is clearly about a named
  manuscript and venue and belongs at the agreement boundary. The landed row correctly treats the
  risk as a file-level must-not-conclude rather than a mutex here.
- `photos.scanned-documents`, `photos.screenshot-captures` and `photos.messenger-export` — capture
  origin can coexist with Legal content. OCR/document structure governs protection; an attachment
  activates on its own evidence. Origin is not a competing topic.
- `Protected Records`, `Review Later`, `Unsupported or Encrypted`, `Temporary Screenshots`,
  `Reading Inbox` and `Independent Records` — residual names are terminal fallthrough targets, not
  roster nodes and not collision endpoints.

## Files considered and rejected from this template

Several files remain recognized by broader Legal safety or another template but are intentionally
negative for **personal legal matters**:

- a will, trust, power of attorney or advance directive with no dispute or proceeding evidence —
  estate planning;
- a lease, NDA, service agreement, employment agreement or ordinary release with no active dispute
  evidence — leases and agreements;
- a firm matter export containing intake, conflicts, internal work product, time records and
  closing administration — practice matter file;
- a published judgment, case brief, legal article or public docket saved for reading — R2 may
  protect, but no holder relation means no personal-matter selection;
- a blank claim form, affidavit template or notary form — official shape without a populated
  holder/matter relation;
- a law-firm newsletter, lawyer biography, legal-services advertisement or letterhead-only file —
  organization identity without a matter;
- a routine insurance claim, tax assessment, HOA cure notice, school compliance filing, licence
  renewal or immigration status record — the administrative template remains sharper until
  contested-proceeding structure appears;
- court-reporter audio or deposition video without an already-present transcript — `00` gates
  speech-to-text behind explicit privacy and compute policy, so audio metadata alone cannot select
  this template;
- a contact card for counsel or a court clerk — contact data remains privacy-protected and is not a
  folder-proposal basis;
- an encrypted archive with a legal-sounding name — metadata-only and unsupported, not inferred.

## Contract choices and deviations

- The dispatch one-line includes notarized documents. The row does not treat notarization alone as
  a personal matter. It uses R2's notarial detector for broad protection and requires a separate
  holder-facing case, claim, agency or dispute relationship to select this template. This is the
  minimum interpretation consistent with the node test and the Legal siblings.
- The prompt says a template reuses its schema's fields. Here that is an empty reuse, not a licence
  to invent fields. `_CONTRACT.md` rules 10/15 and CONNECTION PR-6 outrank the generic expectation
  that a domain normally has several fields.
- `also_holds_with` is empty because CONNECTION restricts it to schema pairs. The file fixtures'
  `also_schema` values document independent schema activation without creating illegal template
  edges.
- `parent_id` remains null because R1b never authors browse shelving.
- No numeric threshold, score, confidence value, P7 class, regex, court list, legal gazetteer or
  jurisdiction field is present.
- No existing node, roster entry, canonical field, deferred catalogue or source file was edited.

## NEEDS-JOSEPH — this row only

1. **Legal fields after D1.** If the Legal deferral is lifted, which small canonical set is
   legitimate? Matter reference, party role, court/tribunal, counterparty and instrument kind are
   not present today. This row refuses to reuse Finance fields or mint replacements by stealth.
2. **Disclosure through structure.** May a protected legal area ever expose matter, opponent or
   document-kind labels as folder levels, or should Legal remain protected-flat and group-attached
   by default? The files can stay local while their path still leaks the dispute.
3. **Personal versus professional custody.** When a pleading or order is byte-identical in a
   party's own papers and a practitioner's client file and neither direct holder evidence nor
   practice-only operational context survives, must template selection always require user
   confirmation? This row answers yes provisionally by abstaining, but the product policy is
   unratified.
