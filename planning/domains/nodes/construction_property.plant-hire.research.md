# construction_property.plant-hire — lab notes (template row)

**Depth: J-DEPTH** (R1b deepening pass, 2026-08-25). Full argument for a narrow placeholder; not an implementation licence or field proposal.

## Sources and comparison set

Read in the required order: `RESEARCH-BRIEF.md`, `DEEPEN-ADDENDUM.md`, the stamped assignment, `ALIGNMENT.md`, `00-database-agent-product-design.md`, `01-product-design-structured.md`, `_CONTRACT.md`, `CONNECTION.md`, `CONNECTION-EXAMPLES.md`, `canonical_fields.json`, the roster and `src/evidence_shape/vocabulary.py`.

Required comparisons: the J-DEPTH `construction_property` schema anchor; `construction_property.materials-delivery`; `business_operations.procurement-sourcing`; and every landed row found by searching for plant/equipment hire, off-hire and rental equipment, including `construction-project`, `trade-job` and `subcontract`. `construction_property.procurement-sourcing` was checked and is absent, so no argument is attributed to it.

The design rules used here are verbatim: “Raw evidence is not yet a fact.” “The system may create new values when it sees a new course, project, company, university, or event, but it should not invent new fields automatically.” “Templates use validated facts to create folder proposals, and the user edits and freezes those proposals into an approved destination tree.” “The graph is used as a context-assembly mechanism rather than an automatic label-propagation system.” “A model that cannot cite sufficient evidence must return unknown.” These license the observation/fact split and forbid copying a site, asset or supplier from one group member onto another. They license no plant-specific field, threshold or detector expression.

## The charge against existence

The dispatch charge is serious: plant hire may be procurement/logistics whose only distinction is an equipment `work_type`, or generic construction paperwork whose only distinction is a site destination. Both would be values, not structure. If that were all the draft had, refusal would be mandatory.

These things do **not** buy a row:

- `excavator`, `telehandler`, `generator`, `plant` and `equipment` are nouns and prospective values.
- A fleet/serial number is an identifier. It may assemble context but does not show hire, charge or site instruction.
- Inspection, service and breakdown records exist for owned plant. Their genres are not hire evidence.
- A delivery ticket is the same handover shape used by materials delivery and logistics. A machine instead of bricks is not structural.
- A construction-site address selects context. The same temporary-equipment lifecycle exists at factories and events.
- An equipment-hire quotation is pre-award sourcing and may never produce a hire.

After stripping those away, one relationship remains: an identified asset and contract enter an **on-hire** state under a continuing time charge, and an operative **off-hire instruction or acknowledgement** ends it. The start/stop pair binds otherwise heterogeneous agreements, dockets, inspections, breakdowns, collections and claims. The row survives only on that lifecycle, never on industry nouns.

## Node test against the construction/property default

The schema anchor gives the default as **property/site → instruction → document function**, not time-first, and warns that ordinary document nouns and work types do not earn siblings. Because the schema has no fields, every template has `fields: []` and `dimension_order: []`; prose cannot become legal facts.

### Leg 1 — detection signals: passes, narrowly

The signal is not the phrase `off hire`. It is the paired structure:

1. An agreement/on-hire confirmation identifies contract and asset, recurring rate or minimum period, and start/delivery.
2. A later instruction or acknowledgement quotes that contract/asset and requests collection or records off-hire.
3. Periodic charges reconcile to the interval between those events.

This start, continuing charge and stop relationship differs from the default job-document lifecycle. A construction instruction may produce a contract and final account, but it does not ordinarily place a reusable asset into a billable state that continues until a stop instruction is received. The gist's useful insight was therefore right but incomplete: an **off-hire notice word** is not magic; the **paired state transition** is the fingerprint.

This answers the work-type charge. Agreement, certificate, claim and collection ticket are document-function values. None fires alone. Co-membership becomes meaningful only when direct evidence ties each to the same time-charged hire. A photo or certificate may join a candidate group without receiving an invented hire fact because “The graph is used as a context-assembly mechanism rather than an automatic label-propagation system.”

Leg 1 fails if implementation reduces it to equipment words plus dates, fleet number plus site, or `Off-hire.pdf` without a referenced hire. The JSON now states those temptations in `never_alone` and adds reconciliation explicitly.

### Leg 2 — dimensions: unavailable; gist claim withdrawn

The gist claimed **asset × period** as a distinct dimension structure. It is not legal here. The schema declares no field rows; asset and hire period are not canonical here; `dimension_order` must remain empty. This pass withdraws dimensions as a reason the row stands.

Prose can still record a future choice: a construction-side corpus wants site/job → individual hire → stage, while a hire firm wants asset → successive hires. That is a filing-habit conflict, not node evidence. No `asset`, `fleet_number`, `hire_period`, `supplier` or `off_hire_date` proposal is minted to rescue this leg.

### Leg 3 — privacy: real, but not independently distinctive

The row is correctly `potentially_sensitive`: dockets identify drivers, examinations identify competent persons, claims make allegations and phone images may carry GPS. `00` says the corpus “can include identity documents, account statements, tax records, medical information, legal records, credentials, private correspondence, GPS metadata, employment materials, and educational records.” It also says: “Protected material should not be included in cloud-model prompts by default, should not display raw content in general group summaries, and should not be moved automatically without a user policy that explicitly permits it.”

But these protections are not unique: materials deliveries have signers/GPS, timesheets have workers, progress photos have GPS and subcontracts have named personnel. The gist called privacy different; this pass narrows that claim. Privacy constrains handling but does not buy the node.

### Verdict

**Stands, on leg 1 only.** This is not a construction-site equipment category; it is the start/stop lifecycle of a temporarily supplied asset under continuing charge. If R1c rejects that structure as insufficient on a field-less schema, refusal is correct: site-held material falls into `construction_property.construction-project`, competitive material into `business_operations.procurement-sourcing`, movements into delivery/logistics, and isolated files into residuals. No field should be created to save it.

## Bottom-up corpus

The JSON holds eleven concrete files across text, spreadsheet, email, image, OCR and archive. Not all activate the row.

- `Hire agreement - 3T excavator - H-88213.pdf`: labelled start half; cannot prove the end.
- `Off-hire OH-4471.pdf`: formal stop half; cannot prove charging actually ceased.
- `RE_ Off hire excavator H-88213.eml`: ugly real stop case where instruction/acknowledgement live only in mail.
- `Hire dockets - week 14.xlsx`: repeating charges; operator names do not turn it into a labour timesheet.
- `Thorough examination - MEWP 22118.pdf`: follows the asset across hires and proves the asset/site conflict; alone it is not hire evidence.
- `Scan_pre-use_checks_tower.jpg`: OCR/initials case; ticks are observations, not a safety judgment.
- `IMG_3390.jpg`: inbound collision; damage claim, inspection or progress photography remain unresolved.
- `Damage recharge - H-88213.pdf`: allegation and demand, not proof of fault.
- `Hire statement - account 20114 - March.pdf`: bookkeeping collision; quoted contract references do not transfer hire facts.
- `RFQ comparison - 3T excavator hire.xlsx`: outbound procurement fixture; competition/evaluation occur before any on-hire state.
- `plant_pack_H-88213.zip`: manifest-only mixed archive; its name does not assign one domain/site to every member.

All examples keep universal facts only, forbid folder paths and use `group_without_copying_facts: true`: a group may be coherent while an individual certificate, photo or statement lacks direct hire evidence.

## Files considered and rejected

- **Owned-plant service history:** same serial and defects, no counterparty/rate/hire state; belongs to asset inventory.
- **Operator competence card:** identity/safety credential; packet membership does not make it a hire record.
- **Fuel delivery note:** `materials-delivery` owns it; what consumes fuel does not change delivery structure.
- **Telematics export:** hours/GPS may support service, utilization or dispute; without contract and paired events it is instrument data.
- **Supplier brochure/rate card:** prices/models are not an engagement.
- **Plant insurance certificate:** may belong to owner, hire pack, finance or legal; alone it proves no hire.
- **Haulier collection ticket:** consignment movement is logistics unless bytes also anchor it to hire lifecycle.
- **Progress photo containing an excavator:** the tempting false positive; plant is ubiquitous on sites.
- **Subcontract quotation including labour and plant:** promised works belong to `subcontract`; plant is a cost component.
- **Retail tool-rental receipt:** one-off transaction with no dossier falls to Receipts and Confirmations.

## Reciprocal boundaries and collision fixtures

### Procurement sourcing ↔ plant hire

Shared bytes: `RFQ comparison - 3T excavator hire.xlsx`, then an award reference repeated later.

This row rejects solicitation, competing offers, evaluation and award as its organizing purpose. `business_operations.procurement-sourcing` should not absorb later asset-specific dockets, inspections, breakdowns and off-hire merely because they quote the award. Competition/selection points to procurement; an entered, time-charged lifecycle points here. The JSON adds this as an R1c recommendation; the neighbour was not edited.

### Materials delivery ↔ plant hire

Shared bytes: the excavator delivery/collection ticket, shaped like a signed delivery note. This row rejects fuel, spares and consumables merely because they support plant. Materials delivery should reject the wider hire dossier merely because it contains handover. Ordered-versus-delivered quantities support materials; asset identity plus continuing charge and off-hire supports this row. A lone machine ticket remains ambiguous/residual. This aligns with the landed row routing `Fuel delivery - red diesel - 950L.pdf` away from plant hire.

### Owned asset inventory ↔ plant hire

Shared bytes: `Thorough examination - MEWP 22118.pdf`, serial, service and defect history. This row cannot take a certificate solely because the machine is sometimes hired. Inventory cannot take agreement, charge run and off-hire solely because the asset has a serial. Ownership/longitudinal service supports inventory; counterparty, recurring rate and paired hire events support this row.

### Subcontract ↔ plant hire

Shared bytes: operated-plant quotation naming machine, operator, rate, competence and insurance. This row rejects an engagement to complete described works; subcontract rejects bare equipment supply. Promised output/scope supports subcontract; supplied asset, time rate and off-hire support this row. Borderline mixed clauses require abstention.

### Bookkeeping ↔ plant hire

Shared bytes: `Hire statement - account 20114 - March.pdf`. This row rejects account balances/payment demands without lifecycle evidence. Bookkeeping should not absorb operational off-hire and inspections because invoices quote them. The hire can form both groups without fact copying.

### Compliance, timesheets, progress photos and vehicle records

Existing boundaries remain: regime/validity supports compliance; people-hours supports timesheets; state-of-works imagery supports progress photos; ownership/tax/test/insurance supports vehicle records. Hire-period evidence points here. No neighbour was edited; reciprocity remains R1c work.

## Neighbours considered without an edge

- `construction_property.construction-project` is default/fallback, not mutex. If refused, site-held coverage folds there as work-type values.
- `construction_property.trade-job` may use hired tools, but customer-job and asset-hire evidence are not competing signals.
- `site-health-safety` is adjacent to pre-use checks; compliance/timesheet boundaries express the actual ambiguities more precisely.
- Logistics was considered, but no required landed row supplied a safe exact reciprocal id; movement is recorded through materials delivery and prose. No id was guessed.
- Legal was considered because hire conditions are contractual. Legal holds the executed instrument as agreement; this row holds the operational dossier. A template cannot author schema-level `also_holds_with`.
- `role_split` stays empty. Supplier, hirer, owner, operator and examiner are real roles, but a field-less template may not mint keys.

## Fields, work types, dimensions and residuals

`fields: []`, `proposed_fields: []`; no canonical key minted. Work types are values: agreement, on/off-hire, docket, statement, inspection, check, service, breakdown, claim and handover. `dimension_order` remains empty. Site/job → hire → stage is prose only; asset-first/site-first remains open.

The five residuals remain appropriate: Independent Records for durable standalone notices/certificates; Receipts and Confirmations for isolated invoices/confirmations; One-Off Images for ungrouped machine photos; Review Later for ambiguous OCR/dockets/claims; Unsupported or Encrypted for unreadable exports/archives. Residual routing is success when the lifecycle is absent.

## NEEDS-JOSEPH

- **NJ-CP-PH-1 — Is the on-hire/off-hire state transition enough to buy a template on a field-less schema?** Keep the narrow row for explicit open-liability retrieval, or refuse and use construction-project/procurement/delivery/residual coverage. No field under either option.
- **NJ-CP-PH-2 — Asset-first or site-first?** Hire desk retrieves one machine across engagements; site manager retrieves all machines on a job. The inspection certificate follows the asset. One frozen tree cannot serve both without duplication; no dimension is encoded.
- **NJ-CP-PH-3 — When does operated hire become subcontract?** Proposed line is output/scope-of-works versus asset/time-charge. Confirm whether output, off-hire mechanism or multi-group review controls mixed agreements.
- **NJ-CP-PH-4 — Does an inspection certificate join hire, compliance, asset, or all three reviewable groups?** This pass rejects exclusive ownership and fact copying.

## What changed in this pass

JSON was written first. Against the gist draft, actual JSON changes are:

1. Replaced the gist-labelled one-line text with a J-DEPTH definition centered on paired start/stop state transition and rejecting nouns/site destination.
2. Added a hire-period reconciliation deterministic signal.
3. Added `never_alone` rules for construction-site destination and hire/rental/plant/equipment words.
4. Added a `needs_llm` procurement-award versus hire-lifecycle boundary.
5. Added the RFQ comparison and email-only off-hire fixtures.
6. Added an R1c reciprocal recommendation to `business_operations.procurement-sourcing`; no neighbour edited.

The memo also withdraws the prior dimensions leg and narrows privacy from a node-carrying difference to a handling constraint. Verdict is now explicitly leg-1-only.

## Audits

JSON parsed; universal house keys retained; `fields: []`; no proposed fields. All source types were checked against `SOURCE_TYPES`; collision ids against roster; residuals against the design nine. Quoted spans were grepped verbatim from `00`. Every “what changed” claim was cross-checked against JSON. Only the assigned pair changed.

Clean end of memo.
