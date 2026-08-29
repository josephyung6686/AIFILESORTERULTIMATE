# manufacturing.warranty-claim — R1b research memo

## Sources and authority

This row was researched against `planning/00-database-agent-product-design.md`, `planning/01-product-design-structured.md`, `planning/prompts/ALIGNMENT.md`, `planning/domains/CONNECTION.md`, `planning/domains/CONNECTION-EXAMPLES.md`, `planning/domains/_CONTRACT.md`, `planning/domains/canonical_fields.json`, `planning/domains/roster.json`, `src/evidence_shape/vocabulary.py`, and the ratified decisions in `planning/overnight/council/DECISION-BRIEF.md`. The manufacturing schema and the landed `identity.core-documents` row supplied the schema boundary and current object-form edge idiom. `finance.crypto-assets.research.md` supplied the J-DEPTH calibration, not manufacturing facts.

The governing design principle is observation before fact. A filename containing `RMA`, a photographed crack, a serial-shaped token, a refund, or the word warranty is an observation. It is not by itself a warranty claim, a confirmed product defect, entitlement, root cause, shipment, or folder path. The file's own labelled structure must establish the role. Group context retrieves sparse members for review but does not copy a claim number, claimant, product, failure mode, entitlement or lot onto them.

No external numeric rate, threshold, time window, regulatory rule or jurisdictional form was introduced. This template does not require a catalogue of warranty statutes to distinguish its files. Its bottom-up reality is established by ordinary controlled artifacts whose roles are explicit in their own labels: claim intake, return authorization, returned-unit receipt, teardown analysis, decision record and field-return register.

## Node test — all three legs

The row survives. It is not saved merely because `warranty claim` appears in the manufacturing schema's broad work world.

First, detection differs. The manufacturing default recognizes repeatable transformation and control tied to product, lot, asset or internal quality event. A warranty claim is a post-transfer transaction. Its discriminating chain starts with an in-service allegation and entitlement question, continues through authorization and custody of a returned unit, and ends in investigation and settlement. Factory inspection can reject a part before it leaves the line; an internal NCR can exist without any claimant; a maintenance work order can restore an asset without deciding coverage. None has the same role chain.

Second, recommended dimensions differ. The schema's researched default is branch-shaped: product then batch/lot then record type for production, site then asset then record type for maintenance, or quality event then record type for controlled deviations. This row makes the claim/quality event the necessary binder and treats batch/lot as optional evidence learned later. Conditional on R1c promoting the schema proposals, the recommendation is `product -> quality_event -> record_type`. The machine-readable order remains empty because the schema currently declares no fields. That is contract compliance, not missing research.

Third, privacy differs in kind. An internal traveller exposes operational data. A warranty packet can join personal contact and address details, proof of purchase, unique unit identifiers, photographs inside a home or workplace, an allegation about unsafe performance, internal admissions about cause, supplier responsibility and monetary settlement. The row therefore requires redaction-aware protection before any external model or connector sees content. It proposes no claimant, serial or amount destination.

The strongest objection is that warranty claim is only a `work_type`. It would be, if this were one form. It is instead a multi-file transaction: intake, label, receipt, photographs, teardown, decision, correspondence and corrective links have different document types but must remain one reviewable case. That differing multi-file grouping and quality-event-first filing rule is the reason the template exists.

## Concrete file corpus

Ten fixtures were retained.

1. `WC-2026-0142 Claim Intake - AX410.pdf` is the labelled happy case. It distinguishes reported symptom from an empty coverage-decision slot, so it tests whether the agent refuses to turn allegation into finding or blank into approval.
2. `RMA-77194_Return_Authorization.pdf` establishes authorization, not dispatch or receipt. Its return-to address must not become a manufacturing site.
3. `UPS Return Label RMA-77194.pdf` is deliberately sparse. It can join the accepted claim group through a labelled reference, but carrier grammar owns the movement and the label does not prove that movement happened.
4. `RMA-77194_Received_Condition_01.jpg` is the image/OCR case and a true Photos co-reading. The handwritten RMA card can support association; depicted damage cannot establish defect or cause.
5. `FA-77194 AX410 Teardown Report.pdf` is the investigation fixture. Its separate reported-symptom, as-received, method, finding and conclusion sections prevent allegation/finding collapse. The conclusion explicitly leaves root cause undecided.
6. `Warranty Decision WC-2026-0142 - replacement approved.pdf` proves authorization, not delivery and not necessarily manufacturing fault.
7. `Field Returns Register 2026-Q2.xlsx` spans many cases and products. The whole workbook cannot receive one `quality_event`, which is why the optional aggregate branch omits that level.
8. `FW RMA-77194 photos and receipt.eml` tests native email and attachment discipline. Attachment names are context; each member must be opened before its facts are asserted.
9. `RMA-77194_packet.zip` is the mixed archive. Its manifest is inspected without extraction. One encrypted member remains unknown; member filenames cannot donate their facts to the archive or one another.
10. `Order 88421 - 30 day returns policy.pdf` is the collision/abstention fixture. A merchant order plus generic policy is a receipt/retail record, not a product failure case.

Together they cover labelled form, sparse carrier artifact, native image, OCR-visible identifier, technical report, spreadsheet register, email, archive and tempting false purchase evidence. Every source type is in P5's closed vocabulary.

## Recognition and false positives

Deterministic recognition is relational. A claim identity plus product/unit plus reported in-service condition plus claimant/entitlement roles is strong. A return authorization binds that identity to movement instructions but does not prove movement. A received-unit record binds it to custody. A teardown report binds it to investigation only when it distinguishes what was alleged, what arrived, what was done, what was found and what was decided. A register activates from its row grammar, not from its title or a colourful trend chart.

The hard language cases remain LLM-supported and privacy-bounded: allegation versus confirmed finding; warranty versus goodwill or paid repair; shipping damage versus product failure; claimant packet versus supplier recovery; no-fault-found versus incomplete investigation; and multilingual/OCR-poor layouts.

The never-alone list is intentionally aggressive. Warranty and RMA words occur in order pages, policies and filenames. Serial and claim-shaped tokens collide with orders and asset tags. Product and company names occur everywhere. Damage photographs show appearances, not cause. Approval signatures do not say what was approved. Folder names and sessions are context only. Missing EXIF proves nothing about screenshot or claim status.

## Reciprocal boundaries and collision fixtures

Every authored collision uses the exact `{domain, signal, provenance}` object form. Every signal names `SAME FIXTURE BOTH SIDES` because P6 activation step 3 and P8 need the same evidence item and the discriminator that assigns each side.

- `manufacturing.nonconformance-capa`: the shared teardown and linked corrective record. Warranty owns allegation, entitlement, returned-unit custody and settlement. CAPA owns requirement/condition, containment, root cause, action and effectiveness. The temporal/role boundary is field/customer versus internal control event.
- `manufacturing.field-service-report`: the shared service visit. Field service owns performed technician work, site, parts/labour and returned-to-service evidence. Warranty owns entitlement and claim disposition. Repair under warranty can make both relevant, but neither grammar substitutes for the other.
- `engineering.change-order`: the shared ECR citing a field-return trend. Engineering owns from/to design supersession and effectivity. Warranty owns the cases and returned-unit investigations that motivated it.
- `logistics.shipment`: the shared return label and tracking events. Logistics owns movement; warranty owns reason, entitlement and technical result. Issuing a label proves neither dispatch nor receipt.
- `business_operations.support-operations`: the shared support ticket. Support owns queue interaction and resolution history. Warranty requires entitlement/return/investigation structure beyond troubleshooting conversation.
- `retail_hospitality.returns-warranty`: the shared defective-order return request. Retail owns order, policy window, refund/exchange and stock receipt. Manufacturing warranty owns the technical field-return and failure-control chain.
- `construction_property.snagging-defects`: the shared equipment defect register during a warranty/defects period. Construction owns room/plot, trade responsibility, practical-completion context and reinspection. This row owns product/model or serial, entitlement, return and teardown. This reciprocates the already-landed neighbour using the same fixture style.

These are collisions between template situations, not `also_holds_with`. That field is empty because the contract reserves it for schema-to-schema record-template intent. The image fixture records `also_schema: photos` locally without widening the manufacturing schema.

## Files considered and rejected

- A generic warranty terms booklet was rejected. It describes policy but evidences no claim, unit, entitlement decision or performed investigation; it belongs in Reading Inbox or Independent Records according to its use.
- A purchase receipt with a warranty line was rejected. Purchase and coverage offer are commerce evidence, not a failure transaction.
- A change-of-mind merchant return was rejected. Its governing grammar is order, return window and refund/exchange.
- A carrier proof-of-delivery was rejected as standalone claim evidence. It proves a movement event and may join a claim group only through its own reference.
- A service manual and troubleshooting guide were rejected. They describe how to diagnose or repair a product, not an owned case or performed investigation.
- A product recall notice was rejected from the core corpus. It may arise from field trends, but it is population-level notice/action and not proof of any individual warranty claim.
- A factory end-of-line failure was rejected. It belongs to inspection/nonconformance because the unit has not entered service and no claimant or entitlement transaction exists.
- A photograph of a crack, leak or burnt component was rejected unless an identifier in the image or accepted group supports returned-unit membership. Depiction is not defect classification or cause.
- A supplier corrective-action response was rejected as the customer-claim record. It may be linked evidence, but supplier responsibility and corrective method belong to nonconformance/CAPA or vendor-quality handling.
- An insurance claim on damaged goods was rejected. Claim vocabulary is shared; policy/insured/loss/adjuster grammar is not warranty entitlement.

## Field and dimension decisions

`fields: []` and `proposed_fields: []` are deliberate. This template cannot copy the manufacturing schema's proposals. It also cannot mint private variations.

The stable case identifier reuses the schema proposal `quality_event`; a dedicated `claim_number` would reproduce the private-key failure. The physical article uses `product`, and a durable uniquely controlled unit may use `asset` if that proposal survives R1c. `record_type` remains the schema's proposed reuse. `batch_lot` is valuable when a teardown traces the unit to manufacture, but it cannot be copied from neighbouring claims and is not required for this row to activate.

Claimant, claimant organization, contact details, serial number, failure code, warranty status, resolution and settlement amount were not proposed as destination fields. They are either sensitive roles, identifiers that would create one-case directories, controlled values awaiting a shared schema decision, or search facts whose appearance in paths would leak content. The machine order is therefore empty today. The prose recommendation is conditional and honest.

The row is not time-first. Filing by claim year would scatter one product's pattern and would turn administrative intake date into the subject of the record. Time remains searchable and may be used by a user after template editing.

## Neighbours considered without an edge

- `legal.*`: terms, warranties and disputes can become legal instruments or matters, but an executed agreement or pleaded dispute has its own strong structure. No same-fixture ambiguity beyond a clause mentioning warranty was found, so no speculative edge was added.
- `finance.*`: credits, reimbursements and reserves are real consequences, but a claim decision is not a bank/account/tax record. The settlement amount is content, not Finance activation.
- `identity.*`: claimant names, addresses and identifiers create protection needs, not a core-identity document. A slot on another record is not the identity credential itself.
- `photos.*`: handled through `also_schema` on the image fixture. It is a genuine parallel schema reading, not a same-kind template collision this row should widen into an edge.
- `manufacturing.recall-traceability`: a trend may trigger a recall, but population tracing and notification are distinguishable from an individual claim. The files link; their discriminating evidence does not compete.
- `manufacturing.supplier-qualification`: a supplier may receive a chargeback, but qualification evidence assesses or approves the supplier population; it does not adjudicate the returned unit.
- `business_operations.contract-administration`: a warranty clause is contract content; a claim packet is performed product-support evidence. A clause alone never activates this row.

`role_split` stays empty. The most tempting split is claimant/customer versus manufacturer/seller/service provider. No adjudicated canonical field pair licenses those roles, and this one template must not mint them.

## Residual and salvage behavior

Independent technical records fall to `Independent Records`. Bare purchase, label, refund or delivery confirmations fall to `Receipts and Confirmations`. Unassociated damage photographs fall to `One-Off Images`. Personally identifying or settlement-bearing material that needs safety despite uncertain deeper association falls to `Protected Records`. Uninspectable encrypted packets fall to `Unsupported or Encrypted`.

No prior target file existed, so this was not a salvage edit and no live work was overwritten.

## NEEDS-JOSEPH

- **NJ-WARRANTY-1 — remote/no-return warranty decisions.** Option A, recommended: keep them here only when the file independently carries claim identity, entitlement, product-specific diagnostic evidence and disposition. Option B: require a physical return, routing remote decisions to support operations or field service. Option B makes the row name narrower than ordinary warranty operations; Option A needs careful support-ticket discrimination.
- **NJ-WARRANTY-2 — merchant/manufacturer overlap.** Recommended: select by evidence grammar even when the same company performs both roles. Order/policy/refund remains `retail_hospitality.returns-warranty`; returned-unit technical investigation and corrective linkage remains here. The alternative, organization-based ownership, would make identical files classify differently depending on corporate structure.
- **NJ-WARRANTY-3 — quality-event anchor.** The schema's `quality_event` is only proposed. If R1c rejects or replaces it, this row must adopt the shared replacement or retain an empty dimension order. It must not mint `claim_number` privately.

## Self-verification checklist

- Output is limited to `manufacturing.warranty-claim.json` and `.research.md`.
- JSON uses `fields: []`; no canonical or proposed field row was invented.
- Ten concrete fixtures separate observations from legal facts and forbidden conclusions.
- Every collision is object-shaped with `domain`, `signal`, `provenance`; every signal names `SAME FIXTURE BOTH SIDES` and states reciprocal discriminating evidence.
- `also_holds_with` is empty and explicitly treated as schema-to-schema intent.
- No unsupported quote, threshold, confidence score, handling class or folder path is asserted as a fact.
- Open product decisions are explicit NEEDS-JOSEPH items rather than silent guesses.
