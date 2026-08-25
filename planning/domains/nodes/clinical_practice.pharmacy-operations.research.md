# clinical_practice.pharmacy-operations — J-DEPTH research

**Depth: J-DEPTH** (deepened 2026-08-25).
**Verdict: STANDS, but not as “everything a pharmacy keeps.”**
**Anchor: regulated medicine custody and supply accountability, not pharmacy as a business.**
**Fields: `[]`; proposed fields: `[]`; no canonical keys minted.**
**Safety: potentially sensitive; dispensing files can identify many third-party patients.**
**Audit order: JSON first, then this memo.**

## Verdict and correction of scope

This row survives the full node test only after narrowing the shallow draft's practical inventory.
Its defensible situation is a dispensary's regulated custody-and-supply record set: per-item dispensing
evidence, accountable-drug running balances and reconciliations, witnessed destruction, recall
quarantine or return action, and payer or regulator returns whose unit is medicine supplied.

The legacy hint—“Running a pharmacy: dispensing records, inventory, controlled-substance
accountability, and formulary management”—is too broad as activation logic. Ordinary inventory is
`retail_hospitality.stocktake` or `logistics.warehouse-ops`; purchase orders are
`retail_hospitality.supplier-order`; competitive sourcing is
`business_operations.procurement-sourcing`; generic operating records are
`clinical_practice.practice-administration`; published formularies and instructions are
`clinical_practice.protocol-guideline`; medication entries in one accumulating patient record are
`clinical_practice.patient-chart`. Medicine is a product value in the first four and subject matter in
the next two. Neither role alone licenses this row.

The discriminating inference is a medicine-specific custody chain: received/supplied entries with a
running balance; controlled schedule; named supply event; witness or second-signature slot; or batch
tied to reconciliation, quarantine, return, or witnessed destruction. A bare product, quantity,
batch, expiry date, temperature, supplier, pharmacy name, or regulatory word is never-alone evidence.

## Authority and method

I used the stamped prompt from `make_prompt.py`, `RESEARCH-BRIEF.md`, `DEEPEN-ADDENDUM.md`,
`ALIGNMENT.md`, `00-database-agent-product-design.md`, `_CONTRACT.md`, `CONNECTION.md`,
`CONNECTION-EXAMPLES.md`, `canonical_fields.json`, `roster.json`, and
`src/evidence_shape/vocabulary.py`. I compared the deepened `clinical_practice` anchor and the landed
`patient-chart`, `practice-administration`, and `protocol-guideline` siblings, plus retail stocktake,
supplier-order, procurement-sourcing, warehouse operations, finance bookkeeping, and malpractice.

The JSON's design quotations were checked against `00`, including:

- “Privacy policy must be enforced before content reaches any model or external connector.”
- “Protected material should not be included in cloud-model prompts by default, should not display
  raw content in general group summaries, and should not be moved automatically without a user policy
  that explicitly permits it.”
- “the normal scan should never extract archive contents to the filesystem”
- “The graph does not automatically copy those missing facts onto sparse files.”
- “For document and record domains, project, function, or subject usually comes before time because
  putting year first scatters related work across calendar folders.”

All pharmacy-specific conclusions are marked or understood as inference from named document
structures. No jurisdictional retention period, statutory threshold, legal conclusion, or score is
invented.

## Schema default

The `clinical_practice` default is a protected, accumulating practitioner-side record about one
subject: authored observations, decisions, actions, and follow-up. It is a field-less safety
placeholder. This row inherits no domain fields and cannot recommend field-based dimensions.

Pharmacy accountability differs in primary unit. A chart accumulates around one subject. A custody
register accumulates around a product and balance; recall action around a batch; a dispensing return
around a period and supplied items. Some lines name patients, but the record is not organized as one
patient's longitudinal chart. That mixed regulated-operational structure cannot be reduced honestly
to either a patient chart or generic business inventory.

## Node test, leg by leg

### Detection signals — passes

The default recognizes one subject's encounters, assessment, plan, order, result, and follow-up. This
row recognizes custody and supply accountability. Strong fixtures are a per-product register with
received, supplied, balance, witness, and reconciliation columns; a dispensing label with product,
strength, form, quantity, directions, and checked-by slots; witnessed destruction; and a periodic
dispensing return tied to a payer scheme.

These are structures, not extensions and not synonyms for “medical.” They separate the dispensary
record from the same product names in a chart, monograph, price list, invoice, warehouse sheet, or
lecture. The old draft was too permissive when “a batch-and-expiry table” supported activation.
Batch/expiry appears throughout retail and logistics. The JSON now requires medicine accountability
and an action—reconciliation, quarantine, return, witnessed denaturing, controlled schedule, or named
supply. Temperature alone likewise says only that something was monitored.

### Privacy rules — passes

The schema default is already potentially sensitive; no new sensitivity class is claimed. The
exposure shape differs. A chart is normally one subject's record. A dispensing export is often a
period-shaped table containing many subjects, medicines, prescribers, and dates. One file can expose
a population, while a single product can imply a condition. A register cover sheet that resembles
inventory does not make patient-naming rows administrative.

Accordingly, generic summaries must not echo content, archive manifests can raise a protected
hypothesis without extraction, and a spreadsheet is not low risk because each cell is small. The JSON
uses only `potentially_sensitive`; it does not invent a P7 handling class.

### Dimensions — unavailable by contract

In practice this record set wants function first—register, dispensing, recalls, returns—then product,
batch, or period. That differs from subject-first chart filing. But `clinical_practice` declares no
fields, so `dimension_order` must remain `[]`. Writing `function`, `medicine`, `batch`, or `period`
would mint keys and violate D1/PR-6. The useful order remains prose, not a fake fact.

### Overall

STANDS. Detection and exposure differ materially from the default. If R1c interprets the node test as
requiring all three legs rather than any material difference, refuse this row until the schema has
licensed dimensions; that genuine fork is NJ-CP-12.

## Concrete files and collision fixtures

### `CD register - schedule 2 - 2026 Q1.pdf`

`text_document`: per-product received/supplied/balance columns, witness slots, closing reconciliation,
and patient names on supply lines. Only universal facts are legal. No discrepancy, product, patient,
schedule, or path fact may be written. Positive anchor; inactive residual Protected Records.

### `dispensing_export_202603.csv`

`spreadsheet`: headers date, patient, product, quantity, prescriber, dispensed-by; many subjects. Its
per-item supply structure supports the situation, not CSV. It must not derive a prescriber identity
from a dominant name or copy one row's facts. This is the bulk-sensitivity fixture; residual Protected
Records.

### `IMG_3390.jpg`

`ocr`: a camera photograph of a dispensing label; EXIF is present; OCR yields person, product,
strength, directions, and date. Photos may also hold from EXIF on their own evidence. Neither schema
borrows facts. It must not become a screenshot. Inactive image residual One-Off Images, with content
still protected.

### `Class 2 recall - batch 7742K.eml`

`email`: regulator reference, batch, action date, attachment, distribution list. Alone it may be a
published notice and Independent Record. It supports this row only when its own bytes or an accepted
group show local quarantine, reconciliation, return, or destruction. Batch is not a schema fact.

### `fridge temps Feb 2026.xlsx`

`spreadsheet`: daily readings, initials, excursions. It must not activate from a Pharmacy folder. The
same bytes fit food safety, laboratory cold chain, facilities, or warehouse operations. It supports
this row only when it identifies medicine stock plus accountable dispensing or recall context.

### `near miss log Q1.docx`

`text_document`: wrong-strength selections caught during checking, staff initials, action column. A
routine periodic near-miss log supports dispensary quality context; it proves no malpractice, fault,
harm, or negligence. A named complaint, claim, indemnity reference, or regulator case favors the
incident row. Residual Protected Records.

### `inspection evidence pack.zip`

`archive`: manifest names register scans, SOPs, training records, self-assessment. Member paths may be
inspected but not extracted. The pack raises a protected accountability hypothesis because register
scans may identify people; it must not turn every member into pharmacy operations. SOP remains
guideline; training matrix may be practice administration.

### `wholesaler invoice 884210.pdf` — looks like this row and is not

`text_document`: product, pack, quantity, price, supplier, total, payment terms; no recipient,
directions, balance, or regulated-supply action. Supplier-order or bookkeeping owns it. Drug names,
batch, and pharmacy letterhead do not change that. Residual Receipts and Confirmations.

### `BNF chapter 4 - CNS.pdf` — medicines without operation

`text_document`: monographs, publisher, edition, population-level instruction. Protocol/guideline or
Reading Inbox owns it. Product-name density must not activate this row; no supply, balance, recipient,
quarantine, or destruction exists.

### `repeat medicines review - Alice.pdf` — must not be lost to this row

`text_document`: one subject, active medications, adherence discussion, assessment, and plan in an
accumulating note. Patient-chart owns it even if authored by a pharmacist. Professional title and
medicine vocabulary do not turn a chart entry into custody. This is the reverse collision fixture.

### `Pharmacy wholesaler RFP evaluation.xlsx`

`spreadsheet`: requirements, bidder responses, weighted evaluation, due diligence, award. Its
lifecycle is requirement-to-response-to-evaluation-to-award: procurement-sourcing. Medicine and
regulator clauses may be pervasive but do not evidence actual custody.

### `DC-04 medicine pick-face count.xlsx`

`spreadsheet`: warehouse locations, pallets, pick faces, on-hand and allocated quantities, batch and
expiry. Without register, named supply, dispensing return, recall action, or witnessed destruction,
warehouse-ops owns it. Medicine is a product value.

### `responsible pharmacist rota September.xlsx`

`spreadsheet`: staff, shifts, premises, leave, coverage. Practice administration owns it. This row is
supported only if the same record opens or closes an accountable dispensing interval and ties the
role to custody. Job title alone is never enough.

## Reciprocal boundaries

### Patient chart ↔ pharmacy operations

One subject's medication history, adherence, assessment, and plan remain chart material even when a
pharmacist authored it. A per-product register, running balance, multi-subject dispensing export, or
payer return remains operational even when rows name patients. Competing bytes: `repeat medicines
review - Alice.pdf` versus one row of `dispensing_export_202603.csv`. Subject-centered versus
custody/supply-centered accumulation discriminates; drug plus date does not.

### Protocol/guideline ↔ pharmacy operations

`BNF chapter 4 - CNS.pdf`, formulary monograph, and SOP version instruct future conduct. A supply,
balance, quarantine, return, or destruction record evidences conduct. A substitution list remains
guidance until a requested-to-supplied mapping records an operational decision. Version/review
metadata favors guideline; dated custody action favors operations.

### Practice administration ↔ pharmacy operations

Rota, premises certificate, training matrix, continuity plan, generic checklist, and ordinary SOP are
administrative. A responsible-pharmacist log tied to an accountable dispensing interval or an
inspection return containing reconciliation supports this row. Competing bytes: `responsible
pharmacist rota September.xlsx` and the corresponding page in `inspection evidence pack.zip`.

### Retail stocktake ↔ pharmacy operations

Counted, expected, variance, product, pack, and value remain stocktake—even in a pharmacy. Running
balance, controlled schedule, witness, named supply, or accountable destruction favors this row.
Competing bytes: `DC-04 medicine pick-face count.xlsx` and `CD register...`. Batch and expiry alone do
not discriminate.

### Retail supplier order ↔ pharmacy operations

Purchase order, confirmation, allocation, goods received, invoice, and credit note remain buying
stock. Custody begins only where evidence records accountability after receipt—register entry,
reconciliation, quarantine, return, or destruction. Competing bytes: `wholesaler invoice 884210.pdf`
and its hypothetical attached register receipt. Product and wholesaler identity discriminate neither.

### Procurement/sourcing ↔ pharmacy operations

RFP, response, evaluation, due diligence, award, and framework are supplier selection. Actual receipt,
custody, supply, return, and dispensing claim are downstream operations. Competing bytes: `Pharmacy
wholesaler RFP evaluation.xlsx` and the later delivery/register record. Regulatory clauses occur in
both and do not discriminate.

### Warehouse operations ↔ pharmacy operations

Storage location, pallet, bin, pick, despatch, and ordinary cold-chain monitoring favor logistics.
Accountable register, named patient supply, controlled schedule, witnessed destruction, or dispensing
return favors this row. Competing bytes: `DC-04...` and `fridge temps...`. Temperature and batch/expiry
alone discriminate neither.

### Finance/bookkeeping ↔ pharmacy operations

Invoice totals, payment terms, tax treatment, ledger posting, remittance, and close are finance.
Per-item medicine supply tied to a dispensing scheme supports this row. A reimbursement remittance may
legitimately support both organizational readings; later grouping and placement must not erase either.

### Malpractice incident ↔ pharmacy operations

Named complaint, harm allegation, duty-of-candour letter, claim, indemnity reference, or regulator
case supports incident. Periodic near-miss rows caught before supply remain quality-control records.
Same bytes: `near miss log Q1.docx`. `error`, wrong-strength, or initials prove neither fault nor claim.

## Files considered and rejected

- Patient's repeat-prescription slip: holder-side `medical.personal-health-records`.
- Ward medication administration record: patient chart when centered on one patient.
- National formulary or manufacturer monograph: protocol/guideline or Reading Inbox.
- General pharmacy SOP: protocol/guideline, even inside an inspection archive.
- Staff rota/training certificate: practice administration, career, or licensure.
- Wholesaler list, PO, invoice, credit: supplier-order/bookkeeping.
- Wholesaler RFP and award: procurement-sourcing.
- Ordinary count with batch/expiry: stocktake or warehouse operations.
- Cold-room sheet without identified medicine accountability: logistics/facilities/Independent Records.
- Consumer pharmacy receipt: personal finance; merchant type does not activate practitioner practice.
- Veterinary dispensing label: veterinary practice when part of an animal record; this row only for a
  species-independent dispensary accountability record.

## Recognition, fields, and grouping discipline

JSON deterministic entries are observable structures, not statutory conclusions or extraction
licences. With `fields: []`, recognition activates protection and template consideration but writes no
pharmacy-specific facts. OCR of handwriting stays possible until structure is read. Folder, extension,
source type, product name, pharmacy name, batch, and price never fire alone.

Sparse files can join an accepted group without borrowing facts. A recall email can group with
quarantine and return records while retaining its own observations. A label photo can co-activate
photos from EXIF and clinical protection from OCR without copying patient/product facts. An archive
manifest can suggest protected members without extraction.

`proposed_fields` remains empty. Obvious candidates—medicine/product, batch, accountability function,
subject, period—are not licensed for this placeholder schema. Minting them here would let one template
redefine its schema. Desired organization is function before time, with subject only for the exceptional
per-person branch; it stays prose while `dimension_order: []` remains contract-correct.

## Neighbours considered without another edge

`medical.personal-health-records` was considered; the holder/practitioner split is family-wide and the
repeat-prescription rejection states it without duplicating an edge. `career` and `legal` were required
neighbors: career owns an individual's CV/training trajectory; legal owns advice, claims, and formal
matters. A certificate in an inspection pack or a statutory-looking register does not compete on the
same activation bytes. `retail_hospitality.store-operations` was considered; its generic opening,
closing, site, and compliance contest is captured more precisely through practice-administration.

## NEEDS-JOSEPH

### NJ-CP-11 — may a recognized accountability register be moved?

Alternative A: ordinary protected-material rule—no automatic move, but permit an approved plan under
explicit policy. Alternative B: recognized accountability registers are not movable ahead of user
policy; represent/index only. A preserves the general approval model; B avoids interfering with an
external duty. The design does not settle jurisdictional custody, location, retention, or integrity.

### NJ-CP-12 — must a node pass all three legs?

Detection and exposure differ, but field-less `clinical_practice` prevents a dimension difference in
JSON. Alternative A: any material difference licenses a template, so this stands. Alternative B: all
three are mandatory, so refuse until fields exist. Current contract language is provisionally read as A.

### NJ-CP-13 — do bulk dispensing exports co-activate patient chart?

Alternative A: period-shaped multi-patient exports activate this operational template plus protection;
later groups may reference rows without copying facts. Alternative B: each row simultaneously becomes
chart evidence. A avoids exploding one physical table into inferred charts; B preserves a two-role
clinical reading. The design's grouping firewall favors A but does not specify row-level activation.

## What changed in this pass

The prior draft's verified quotations, 27-key shape, residuals, empty fields, and controlled-register
insight were preserved. I replaced the retired GIST label with J-DEPTH; narrowed the node from general
pharmacy operation to regulated medicine custody/supply; removed clinical reviews and ordinary
wholesaler stock/order from work types; tightened batch/expiry recognition; and added reciprocal edges
for supplier-order, procurement-sourcing, warehouse operations, and practice administration. No
neighbor was edited. This memo now argues all node-test legs, names both-direction collision fixtures,
rejects false positives, explains empty dimensions, and surfaces three decision forks.
