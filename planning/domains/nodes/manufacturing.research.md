# Manufacturing, quality and maintenance — R1b research memo

Depth: J-DEPTH

## Verdict

Keep the schema as a placeholder anchor, but do not promote any field yet. The row passes the schema node test because its smallest useful fact set is not a respelling of Engineering, Business Operations, Construction/Property or Logistics. The decisive facts are the controlled physical output (`product`), the recurring genealogy unit (`batch_lot`), the maintained/control object (`asset`), the operating facility (`site`), and the controlled exception (`quality_event`). `record_type` is needed as the leaf but is already canonical with a Finance-specific role, so its reuse is explicitly an adjudication question.

This is not an industry-category claim. A firm name, NAICS-like label, factory photograph, product name, purchase order or word such as “quality” cannot activate it. The evidence must show a recurring transformation or control cycle. Production records join an input lot to operations and an output lot; inspection joins requirements to actual measurements and disposition; maintenance joins an enduring asset to performed work and return-to-service; quality systems join an affected lot or asset to containment, investigation, action and closure. Those structures are the reason to keep the schema.

The row remains `launch: placeholder`, `fields: []`, and `dimension_order: []` under PR-6. The proposals record what R1c must adjudicate; they do not authorize extraction.

## Sources and authority used

I used `planning/00-database-agent-product-design.md` as the authority for observation-versus-fact separation, small active schemas, labelled-slot/direct evidence, extension-as-routing, archive inspection, residual behavior, privacy-before-model handling, abstention, and the rule that grouping does not copy facts. I used `planning/01-product-design-structured.md` only as a numbered rendering, with `00` controlling. I used `planning/prompts/ALIGNMENT.md`, `planning/domains/_CONTRACT.md`, `planning/domains/CONNECTION.md`, `planning/domains/CONNECTION-EXAMPLES.md`, `planning/domains/canonical_fields.json`, `planning/domains/roster.json`, and `src/evidence_shape/vocabulary.py` for the node contract, key vocabulary, edge vocabulary, roster identities and source types.

I compared the landed `construction_property.json` and `business_operations.json` schema anchors for placeholder idiom and reciprocal boundaries. I compared `business_operations.organisational-records.json` for refusal quality. Engineering and Logistics roster rows were available as assigned neighbours but their node files had not landed when this memo was authored; this memo therefore states recommendations for reciprocity rather than pretending their wording already agrees.

The key design discipline used throughout is exact: “The system may create new values when it sees a new course, project, company, university, or event, but it should not invent new fields automatically.” The row therefore keeps batch-record, calibration-certificate, work-order and nonconformance names as work-type values. It also observes: “A session should never be treated as proof of topic”, and the general document-order rule: “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders.”

## Bottom-up file evidence

`BPR_AX410_L240817-03.pdf` is the strongest positive fixture. A real batch production record or traveller carries a labelled product/part identity, batch/lot identity, sequential operations, planned and actual quantities, operator/date signoffs and release approval. The filename is weak; the structured co-occurrence is strong. Legal proposed facts are product, batch_lot and record_type. Customer, supplier and path remain unknown.

`Lot genealogy L240817-03.xlsx` maps incoming material lots and quantities through operations into one output lot. It proves why `batch_lot` is not just a document number: the value is the join key across otherwise different records and supports recall-oriented retrieval. A logistics packing list may repeat the same lot bytes, so lot alone does not decide the schema. Consume/output-operation columns support manufacturing; carrier/ship-to/custody columns support logistics.

`Final inspection AX410 lot L240817-03.csv` has characteristic, limit, measured-result, instrument and disposition columns. This is manufacturing quality evidence because it records actual conformance of a controlled output. A drawing tolerance table with no actual measurement belongs to Engineering; an external laboratory report with no holder-side acceptance context may be an independent record. A pass/fail cell never fires alone.

`NCR-2026-041 cracked housing.pdf` is an OCR fixture. Labelled NCR identifier, affected lot, requirement-versus-observed condition, containment, disposition and approval create the event structure. The defect title does not establish root cause. The same file may also be Engineering if it includes an actual revision request and design rationale; that is multi-schema evidence, not a first-match collision.

`CAPA-2026-012 effectiveness review.docx` joins problem statement, root cause, action, owner, due date, verification and closure. This is the closest Business Operations collision because generic action trackers carry the same owner/due/status columns. The quality-event identifier and controlled containment/effectiveness structure are the discriminator. A project tracker called “CAPA actions” without those structures is not enough.

`Calibration certificate CNC-07 2026.pdf` carries asset and serial slots, as-found/as-left results, a traceability reference, dates and due date. It supports the asset branch. The laboratory issuer is not the manufacturing site; `2026` is not a tax year; “certificate” is not a record type by itself. A vendor invoice for the calibration is a transaction record until the performed calibration result is present.

`WO-8814 CNC-07 spindle alarm.xml` shows why `code_structured` is plausible without becoming a Code schema. Labelled work-order, equipment, failure, performed-work and returned-to-service fields support manufacturing maintenance. XML is only routing. A software issue with the same word “spindle” and an issue number remains Code/Engineering or residual depending on its own evidence.

`Line 2 shift log 2026-08-17.xlsx` provides repeated output, scrap, downtime, changeover and operator/shift rows for an identified line. It supports recurring operations rather than one project. It may not contain a lot; grouping it beside batch records must not manufacture a lot fact for it.

`Release packet L240817-03.zip` is the archive case. Its manifest lists a batch record, inspection result, deviation and release certificate sharing a lot token. The archive may be proposed to the lot group, but unread members yield no extracted facts. The design requires archives to be inspected without unpacking to disk. If encrypted, it falls to Unsupported or Encrypted rather than being guessed from the filename.

`PO 45001982 - AX410 castings.pdf` is the procurement collision fixture and a rejection. Buyer/supplier blocks, PO number, prices and delivery terms say a commercial order occurred. A part name does not say the holder manufactured it. Without received-lot acceptance, production execution or equipment-control evidence this is Business Operations/procurement or Receipts and Confirmations, not manufacturing.

`ECN-1042 housing wall thickness.pdf` is the Engineering collision fixture and a rejection. From/to revision slots, design-change rationale and affected drawing support Engineering. It is not manufacturing merely because a part will eventually be made. Manufacturing begins where the file records actual execution, measurement, lot disposition or controlled asset work. If an NCR embeds this ECN, both can hold on separate evidence.

`Defect photo IMG_8841.jpg` is the sparse-image fixture. A cracked metal housing is visually plausible but does not establish product, lot, site, asset or quality event. EXIF remains Photos evidence. P9 may group the image beside an NCR without copying the NCR number or lot onto the image. Missing GPS or EXIF proves nothing about screenshot status.

`Site safety inspection Plant 2.pdf` carries a labelled facility/area plus hazard, control, action and closeout fields. It can be manufacturing site HSE and Business Operations at once. A generic corporate safety policy is Business Operations; an office fit-out snag or building compliance inspection can be Construction/Property. The controlled plant/line/asset context is what keeps this fixture here.

Other considered real file families were a bill of materials, setup sheet, sanitation record, line-clearance checklist, certificate of analysis, concession, material-review-board decision, complaint investigation, preventive-maintenance schedule, spare-parts register, permit to work, incident investigation, competence matrix and machine-export alarm history. They remain work-type values, never child schemas.

## Full node test

The field-set leg passes. Generic `project`, `stage` and `artifact_type` cannot express one stable product across recurring lots; one asset across many work orders; or one nonconformance across containment, investigation and effectiveness evidence. Business Operations’ proposed `organization` and `fiscal_period` also cannot do so. Logistics needs shipment/custody movement rather than transformation genealogy. Construction/Property’s proposed property/instruction pairing is about a site or building under professional instruction; it does not distinguish the recurring production lot or controlled machine.

The detection leg passes. The row has structures that its neighbours do not use as defaults: input-lot-to-output-lot genealogy, planned-versus-actual operation execution with signoffs, specification-versus-measurement inspection tables, as-found/as-left calibration results, and NCR/CAPA disposition/closure structures. A product name, factory name, document word, extension or number never suffices.

The default-template leg passes provisionally even though the contract requires an empty `dimension_order`. No single generic project/operations template fits the three retrieval anchors. Production records are product → lot → record function. Maintenance is site → asset → record function. Quality events are event → record function. This is one schema because the fact allow-list is shared and files cross the branches; they are optional branch patterns, not three child schemas. Time is a leaf or search fact, not the primary organizer.

The privacy leg is not the sole reason the row survives, but it differs materially from a generic public operations pile. Production recipes, tolerances, yields, supplier genealogy, plant layouts, failures and corrective actions may expose trade secrets or security-relevant facility detail. Incident, training and competence records may identify workers. `potentially_sensitive` is therefore warranted, but this memo assigns no P7 handling class.

## Proposed-field analysis

`product` is proposed because no canonical field holds the physical article or formulation repeatedly made. It differs from `project`: a product persists while projects start and end, and one project may launch several products. It differs from `artifact_type`, which names a research/code artifact kind. A labelled Product/Part/Material/SKU slot can support it; prose or item names on a PO remain possible.

`site` is proposed as the subject facility. It is deliberately not Photos `location`: a field image’s capture location and the site an inspection is about can diverge. The same string in two roles is a candidate role split, not evidence that the fields are synonyms. Site should be destination-eligible only when a corpus spans sites; otherwise it is a one-child level to flatten.

`batch_lot` is the strongest proposal and the core proof against refusal. It is not a generic identifier or document reference. It names a production quantity whose shared conditions create genealogy, inspection, release and recall relationships. Validation requires a labelled lot/batch role and manufacturing context; a lot token on a packing list alone stays logistics evidence.

`asset` names enduring controlled equipment. It differs from a project and from camera_information. A local asset register can validate an asset-tag-shaped value in an Equipment/Instrument/Machine slot. The serial number of a purchased component is not automatically this asset.

`quality_event` names the controlled exception that joins NCR/deviation/complaint and CAPA evidence. The proposal is intentionally vulnerable to consolidation. If Legal, HR, Medical, Government or Business Operations establish a global `case` or `event` with the same semantics, R1c should reuse that key rather than retain a manufacturing-flavoured spelling. What cannot be lost is the role: the affected product/lot/asset event, not an ordinary project stage.

`record_type` is not minted. The canonical key exists, but its catalogue role says “the kind of financial record”. Manufacturing needs the same structural leaf. R1c must either widen the canonical role globally or choose a global document-function key once; this row must not silently redefine it or mint `manufacturing_record_type`.

## Reciprocal neighbour boundaries

Engineering versus Manufacturing: the same fixture bytes are `ECN-1042 housing wall thickness.pdf` and `NCR-2026-041 cracked housing.pdf`. Engineering owns intended design, requirements and revision-controlled change. Manufacturing owns actual execution, lot genealogy, measured result, disposition and controlled process/asset state. An affected part number, drawing number or approval signature supports neither side alone. An NCR containing a design-change request can activate both from disjoint sections.

Logistics versus Manufacturing: the same lot appears in `Lot genealogy L240817-03.xlsx`, a packing list and a shipment notice. Consume/output/operation relationships support manufacturing. Ship-from/ship-to, carrier, tracking, custody event and receipt support logistics. A released-lot packet can carry both. Neither side may copy a lot fact to a sparse neighbour merely because the files group.

Business Operations versus Manufacturing: `PO 45001982 - AX410 castings.pdf` and `CAPA-2026-012 effectiveness review.docx` are the shared fixtures. Procurement owns sourcing, supplier comparison, award, order and commercial approval. Manufacturing owns received-lot acceptance, production execution, inspection and control of the produced item or equipment. A CAPA has generic owner/due/status evidence and manufacturing-specific event/containment/effectiveness evidence, so both can hold. A generic tracker does not activate manufacturing.

Construction/Property versus Manufacturing: `Site safety inspection Plant 2.pdf` and an equipment maintenance work order can look identical. Construction/Property owns a property/site under a professional instruction and its built-asset lifecycle; Manufacturing owns an operating plant’s recurring production/control cycle and controlled equipment. An office fit-out snag list belongs to Construction/Property; a line-clearance or machine-return-to-service record belongs here. A building-services asset at a factory is the unresolved centre and should abstain where neither anchor wins.

Resource/operations comparison: the roster has no canonical “resource operations” schema field set that can replace the batch/asset/event facts. Generic resource planning—capacity, staffing, material requirement forecast, budget—belongs to Business Operations unless actual lot consumption, asset execution or quality control appears. A material-requirements spreadsheet is not genealogy merely because it has part numbers and quantities.

## Files considered and rejected

Rejected as sole evidence: purchase orders, requests for quotation, supplier quotations, invoices, packing lists, bills of lading, delivery receipts, generic project plans, engineering drawings, bills of materials with no executed lot, product brochures, factory floor photographs, organization charts, generic safety policies, training slide decks, blank SOP templates, maintenance manuals, equipment catalogues, research laboratory notebooks, software issue trackers, and warranty certificates for household appliances.

Each rejection has a reason. Commercial documents prove procurement or a transaction, not transformation. Shipment documents prove movement, not manufacture. Drawings and ECNs prove intended design, not actual execution. Manuals and blank procedures describe possible work but do not evidence an owned asset or performed cycle. Photographs have content but no role anchor. Laboratory notebooks may use batch and instrument vocabulary for experiments; without production release or controlled output they belong to Research. A household appliance receipt and warranty belong to Finance/household property or a residual, not this professional operating schema.

The primary collision fixture is `PO 45001982 - AX410 castings.pdf`: it looks manufacturing-shaped because it names a manufactured product and quantity, yet it is not manufacturing evidence. The discriminator is the absence of product-lot execution, measurement, release, received-lot acceptance or controlled-asset work. The second is `ECN-1042 housing wall thickness.pdf`: it names the product and a controlled change, yet belongs to Engineering unless actual lot/process evidence appears.

## Neighbours considered without an extra edge

Research was considered because laboratories use batches, instruments, calibration and deviations. No edge was authored beyond the required neighbour set because the stronger first discriminator is purpose and lifecycle: exploratory experiment/notebook/model evidence is Research; repeat production, release and controlled product genealogy is Manufacturing. If research manufacturing or pilot plants prove routinely inseparable, R1c may add reciprocity after inspecting the Research schema.

Photos was considered through the defect-photo fixture. The file may legitimately activate Photos from EXIF and media facts, but the generic schema-to-schema edge would be noisy: most manufacturing files are not photographs, and a photo without its own product/lot/asset evidence does not activate Manufacturing. The file example records `also_schema: photos`; R1c can decide whether a formal edge is useful.

Finance was considered for capital-asset invoices and inventory valuation. A money/account/institution structure activates Finance independently; it does not define the manufacturing situation. No edge was added because Procurement/Business Operations and Logistics are the nearer operational seams.

Legal and Government were considered for regulated quality systems, permits and incident files. An executed legal instrument, enforcement matter or authority decision may co-activate its safety/government schema. The manufacturing structure remains actual lot, asset, site-control or quality-event evidence. Those cross-domain cases are real but not distinctive enough at this schema anchor to add broad edges without the neighbouring rows’ own wording.

## NEEDS-JOSEPH

NJ-MFG-1 — `record_type` scope. Alternative A widens the existing canonical field from Finance-specific wording to a global document-function key reused here and elsewhere. Alternative B preserves the Finance role and introduces one globally named operational document-function key. A private manufacturing synonym is rejected.

NJ-MFG-2 — controlled-event key. Alternative A accepts `quality_event` as a narrow manufacturing key. Alternative B introduces/reuses a global `case` or `event` key across nonconformance, complaint, incident and corrective-action worlds. The schema needs the role, but this row cannot decide global consolidation.

NJ-MFG-3 — site versus location. Alternative A keeps `site` as the facility a record is about and Photos `location` as capture location, with an explicit role split. Alternative B widens `location` to cover both roles, accepting that one file may need two different location values with different semantics. The present proposal prefers A.

NJ-MFG-4 — building-services assets at operating sites. A boiler, lift or fire system at a factory can be an operating asset or property/facilities asset with identical work-order bytes. Alternative A lets the holder’s operational context decide; Alternative B requires explicit production-line/process dependency for Manufacturing and otherwise gives Construction/Property the evidence item. Until settled, ambiguous cases abstain.

## Self-check notes

The JSON object uses the full schema key set and begins with `id`, `kind`, `schema_id`, `parent_id`, `name`, `one_line`, `launch`, and `provenance`. It declares no canonical field rows. Every candidate is in `proposed_fields`, including the explicitly marked reuse of `record_type`. Work types are values. Source types come from the closed vocabulary. Edge domains exist in the roster, and residual names come from the closed residual library. Observations and legal facts are separated in every fixture; no fact is a folder path. No numeric threshold, confidence score, handling class or unauthorized canonical key is asserted.
