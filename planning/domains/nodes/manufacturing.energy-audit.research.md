# Research memo — `manufacturing.energy-audit`

Date: 2026-08-27
Depth: J-DEPTH
Output: `planning/domains/nodes/manufacturing.energy-audit.json`
Roster row: template on the fieldless `manufacturing` schema, `parent_id: null`, `launch: placeholder`
Legacy coverage: `hse.energy-audit` (ROSTER.md Appendix A)

## Result

**Accept**, with three proposed fields routed to R1c (one new key, two reuses) and four NEEDS-JOSEPH items. The row survives the charge because its anchor is a **surveyed energy boundary plus a measured baseline plus the opportunity apparatus sized against that baseline** — an object that is not a product lot, not a single maintained asset's work order, not a utility supplier's bill, and not a statutory emissions-scheme return. That is not a `work_type` value on the manufacturing schema, and it is not the schema's default template: it recommends a different first-branch shape, a different validation family, and a privacy posture centred on process-intensity disclosure rather than on public-register bimodality.

## The charge — the strongest case that this row should not exist

I ran the charge before writing anything. Eight attacks, in descending order of force.

**1. It is a `work_type` value, not a node.** The manufacturing schema's `work_types[]` already contains *"site HSE inspection, permit, risk assessment or incident record"*, and its one-liner already names "site HSE records". If an energy audit is just another HSE document kind, this row is a category label wearing a template's clothes — precisely the 574's failure.

*Defeated, but only partly.* The schema entry is real and I do not dispute that the *words* energy and audit can appear as document-kind values. What it misses is that an energy survey is a **container that other documents are filed against**: interval meter exports, lighting inventories, combustion tests, thermal images and an ECM register are five different document kinds that are unintelligible except as evidence against one baseline of one energy system. `00`'s own rule for dimension order is the test: *"a parent dimension should provide the context required to understand the child"*. A `work_type` value cannot be that parent. What the schema entry correctly shows is why `never_alone` forbids activating on the bare words.

**2. It duplicates the schema's default template.** The manufacturing anchor's `template.why` recommends `product → batch_lot → record_type` and `site → asset → record_type`. If this row's recommendation is the second of those, it is the default.

*Defeated on evidence.* `Compressed air system - baseline and ECM register.xlsx` has no product and no lot. Filed under `site → asset` it would have to attach to whichever compressor happens to be tagged — and the baseline is a distribution-and-end-use system that spans many assets. The proposed order `site → energy_system → reporting_period → record_type` shares only `site` and the leaf `record_type` with the default maintenance branch; the middle levels are not the schema's `asset`. That is a genuine template difference and the strongest single leg of the node test.

**3. It duplicates `manufacturing.environmental-compliance`, which has already landed.** That row already holds meter readings, fuel consumption and a GHG workbook, and its own edge and NJ-MEC-3 name this id as the reciprocal.

*Defeated, and pre-argued by the neighbour itself.* That row's edge says the statutory-scheme frame (registration, organisational boundary, verification opinion) is theirs and consumption profiling, efficiency measures, payback and savings are mine, naming `2026 GHG inventory - Scope 1 and 2 - Plant 2.xlsx`. I have mirrored it exactly (same fixture, same discriminator, coexistence when both structures are present) and recorded NJ-MEA-1 as the joint open question rather than inventing a third carbon row.

**4. It duplicates `resource_operations.utility-metering-billing` or `finance.subscriptions-utilities`.** Meter CSVs and electricity bills are already claimed elsewhere.

*Defeated by custody and purpose.* The resource-operations row is the supplier-side metering and billing operation; the finance utilities row is the account and charges record. This row is the **operator-side survey** that consumes quantities inside an energy boundary. The collision fixtures are deliberate: `Plant 2 - 15min interval kWh - Meter M-17 - 2025.csv` (survey vs settlement) and `Electricity bill - Plant 2 - Feb 2026.pdf` (bill vs baseline). Interval columns alone, and a plant name plus kWh on a bill, activate neither side of the survey.

**5. It is a lifecycle stage.** "What would reduce consumption" is the improvement stage after monitoring.

*Defeated.* A stage ends. A surveyed energy system does not: the 2025 baseline sits beside the 2027 re-baseline under the same boundary, and the ECM register is a living list, not a closing tick. A stage-shaped row would have put `reporting_period` first; this row puts it leaf-adjacent and sets `time_first: false`, citing `00`: *"For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders."*

**6. It is never-alone evidence — an organisation name or a standard number.** "ENERGY STAR", "ISO 50001", an ESCO letterhead.

*Conceded and encoded, not defeated.* Correct, and why `never_alone` names the utility, the ESCO, the consultancy, the certification body and the standard designation together. `ISO 50001-2018 Energy management systems - downloaded.pdf` is the deliberate false friend: possessing the text is not evidence of running a survey.

**7. It is a medium or format node.** Spreadsheets of kWh, thermal JPEGs, zip deliverable packs.

*Defeated.* Every deterministic signal is a relation among labelled slots — boundary plus baseline plus measurement; measure plus savings plus payback; meter identity plus quantity used as baseline evidence. Extensions and `SOURCE_TYPES` are explicitly never-alone, matching `00`'s format-is-not-a-domain discipline.

**8. It is a row defined by the absence of something.** "Energy" as the residue of sustainability paper no other row wanted.

*Defeated by positive structures.* None of the deterministic signals is "not a permit" or "not a work order". Each is a positive apparatus. Files that lack that apparatus are rejected below, not absorbed.

**Verdict: accept.** Had only attacks 1 and 4 survived I would have refused and routed coverage to the manufacturing default plus Independent Records / Receipts and Confirmations. Attack 2's failure is what makes the row real; attack 3's reciprocal with environmental-compliance is what keeps it from stealing that row's job.

## The node test, argued in three legs

CONNECTION.md §2's test is that a template exists only where its **detection signals**, **recommended dimensions**, or **privacy rules** differ from its schema's default. All three differ; any one would have sufficed.

**Leg 1 — detection signals.** The schema default fires on a transformation or control cycle: traveller/genealogy structure, characteristic-versus-tolerance inspection tables, event-identifier-plus-disposition structure, asset-plus-failure-code work orders, and HSE inspection/permit/incident structures tied to harm or authorised release. None of those appears in `Plant 2 - ASHRAE Level II energy audit - 2026-03.pdf`, in `Compressed air system - baseline and ECM register.xlsx`, or in `Lighting inventory - Warehouse A - survey 2026-02.xlsx`. This row fires instead on boundary-plus-baseline-plus-measurement, on ECM rows with savings and payback, on interval data used as baseline evidence, and on end-use inventories that feed an opportunity register. The schema default would miss all four; this row would miss every traveller and every NCR. The signal sets are close to disjoint above the shared `record_type` leaf.

**Leg 2 — recommended dimensions.** Set out under attack 2. `energy_system` does not exist in the schema's proposal set; `reporting_period` is reused from environmental-compliance as a subject here rather than a timestamp. Both remain unserialised (`dimension_order: []`) because the schema declares no canonical fields under PR-6; the recommendation is held as prose in `template.why`.

**Leg 3 — privacy rules.** The schema default's posture is uniform commercial confidentiality plus worker names. This row's distinctive risk is **process-intensity disclosure**: load profiles, specific energy consumption and leak-loss estimates can reveal operating schedules and commercially valuable savings pathways. It is not the environmental-compliance bimodal case (self-incriminating exceedance versus public register). The added rule is narrower: utility-account and meter identifiers stay account-adjacent observations; author and auditor names never become destinations — *"It should avoid using authorship or creator identity as a destination dimension."* The row assigns no handling class; P7 owns that.

## Bottom-up file set

The JSON carries observations, allowed facts, prohibited conclusions, coactivation notes and inactive residuals. This memo records why each fixture exists.

1. `Plant 2 - ASHRAE Level II energy audit - 2026-03.pdf` — full survey deliverable: boundary, baseline, opportunities.
2. `Compressed air system - baseline and ECM register.xlsx` — system-scoped baseline plus opportunity apparatus; also business_operations when programme-tracker slots appear.
3. `Plant 2 - 15min interval kWh - Meter M-17 - 2025.csv` — meter quantities as baseline evidence; collides with resource_operations settlement use of the same shape.
4. `Lighting inventory - Warehouse A - survey 2026-02.xlsx` — end-use inventory feeding ECMs; collides with construction site-survey on the word survey.
5. `Boiler B-3 combustion efficiency test 2026-03-12.pdf` — measured efficiency for a named system; collides with maintenance work orders on the same boiler identity.
6. `Steam trap survey - Plant 2 - Route 4.xlsx` — condition-and-action survey with leak-loss estimates.
7. `Plant 2 energy balance Sankey - baseline 2025.xlsx` — site total allocated across end uses for one baseline period.
8. `2026 GHG inventory - Scope 1 and 2 - Plant 2.xlsx` — the reciprocal fixture with environmental-compliance; verification tab versus savings tab.
9. `RE Plant 2 energy audit findings - compressed air.eml` — correspondence that names site, system and attachments without manufacturing implementation facts.
10. `FLIR_8841_steam_header.jpg` — thermal image; Photos coactivation; alone it is One-Off Images.
11. `Plant 2 energy audit deliverables - Mar 2026.zip` — bounded packet; manifest read without unpacking.
12. `Electricity bill - Plant 2 - Feb 2026.pdf` — collision/false friend; Receipts and Confirmations / finance utilities.
13. `WO-9102 Boiler B-3 burner cleaning.xml` — maintenance false friend on the same asset identity.
14. `ISO 50001-2018 Energy management systems - downloaded.pdf` — standard-text false friend; Reading Inbox.
15. `Commissioning report - AHU-4 performance test.pdf` — handover performance false friend; engineering.commissioning-handover.
16. `LED retrofit proposal - Acme Lighting.pdf` — vendor-brochure false friend; Reading Inbox.

Ugly cases covered: labelled forms, free-text email, OCR-poor needs_llm, images, archives, calendars (recognised as a source type even when no dedicated fixture carries the whole load), collision fixtures, multi-schema artifacts, and unreadables.

## Files considered and rejected

A row that only lists what it holds has not been researched.

- **`Electricity bill - Plant 2 - Feb 2026.pdf`** — carries kWh, a plant name and a period. Carries charges and amount due, no boundary, no ECM. Proves a purchase. Routes to Receipts and Confirmations: *"isolated invoices, delivery confirmations, booking records"*.
- **`WO-9102 Boiler B-3 burner cleaning.xml`** — same boiler identity as the combustion test. Work-order execution without efficiency/baseline/ECM structure. Belongs to `manufacturing.maintenance-work-order`.
- **`ISO 50001-2018 ... downloaded.pdf`** — standard designation is never-alone. Reading Inbox or `engineering.standards-library` territory; not evidence of a survey.
- **`LED retrofit proposal - Acme Lighting.pdf`** — claimed savings without a measured site baseline. Sales literature.
- **`Commissioning report - AHU-4 performance test.pdf`** — one-time design-versus-actual at handover. Not a multi-period baseline survey.
- **`EPR-AB1234 - Quarterly Monitoring Return Q2 2026 - Outfall 001.xlsx`** — environmental-compliance's own fixture. Result-versus-permitted-limit against a release point. I do not claim it.
- **`Site safety inspection Plant 2.pdf`** — manufacturing schema HSE fixture. Hazard/control/action without energy boundary or baseline. Stays with the schema default / HSE cluster.
- **`Calibration certificate CNC-07 2026.pdf`** — instrument as-found/as-left. Not an energy baseline. Stays with calibration-record.
- **A home Energy Performance Certificate.** Residential property evidence; needs_llm notes the ambiguity and this row does not absorb it by default.
- **A live utility-portal account or building-management system.** A source system, not a file node. A bounded export with a readable manifest is represented; connector ingestion is a later security decision.
- **Password-protected audit packs.** Represented without forcing inspection; Unsupported or Encrypted.

## Reciprocal boundaries

Every neighbour below is stated in both directions, naming the same fixture on both sides.

| Neighbour | This row holds | Neighbour holds | Shared fixture |
|---|---|---|---|
| `manufacturing.environmental-compliance` | consumption profiling, ECM, payback, savings vs baseline | statutory/scheme frame: registration, boundary, verification opinion | `2026 GHG inventory - Scope 1 and 2 - Plant 2.xlsx` — neighbour's named fixture, adopted unchanged |
| `manufacturing.maintenance-work-order` | measured efficiency/intensity against a surveyed system | asset work order with task, labour, returned-to-service | combustion test beside `WO-9102 Boiler B-3 burner cleaning.xml` |
| `resource_operations.utility-metering-billing` | operator-side baseline use of meter quantities | supplier-side settlement and billing operations | `Plant 2 - 15min interval kWh - Meter M-17 - 2025.csv` |
| `finance.subscriptions-utilities` | does not activate on a bill | account, charges, amount due | `Electricity bill - Plant 2 - Feb 2026.pdf` |
| `engineering.commissioning-handover` | multi-period baseline and ECM analysis | design-versus-actual handover acceptance | `Commissioning report - AHU-4 performance test.pdf` |
| `business_operations.compliance-audit` | energy-review findings citing baseline/SEU/ECM | organisational-control audit as a whole | ISO 50001 surveillance report — activate per-finding, abstain on the whole |
| `construction_property.site-survey` | end-use energy inventory feeding ECMs | property/works survey under a professional instruction | `Lighting inventory - Warehouse A - survey 2026-02.xlsx` |

Schema-level `also_holds_with` (schema ↔ schema only, per CONNECTION.md): `engineering`, `business_operations`, `finance`, `resource_operations`, `photos`. Template-level coexistence with `manufacturing.environmental-compliance` is recorded on the GHG file example's `also_schema` and in the collides_with signal's coexistence clause — not as `also_holds_with`, because that edge is schema-only.

## Fields and dimensions

`fields: []` and `template.dimension_order: []` are intentional under PR-6. `time_first` is false.

Proposed for R1c:

- **`energy_system`** — new; argued above; NJ-MEA-2 records the fold-into-`asset` alternative.
- **`reporting_period`** — reuse of environmental-compliance's proposal; do not mint `audit_period` / `baseline_period`.
- **`record_type`** — reuse of the manufacturing schema's contested proposal (NJ-MFG-1 / NJ-MEA-4).

Rejected candidates:

- `project` — Research/Code scoped; turning every survey into a project recreates the 574.
- `purpose` — currently scoped to College Applications under the canonical record.
- `institution` — financial issuer role; a utility name is never-alone here.
- `location` — Photos capture role; a thermal image may be captured off the system it documents.
- `asset` alone as the only system key — fails the multi-asset compressed-air case; retained only where a single boiler is both the maintained item and the surveyed system (see combustion-test `facts_legal`).
- `authorisation` — environmental-compliance's key; an energy audit is not an externally issued instrument.

## Recognition boundary

Strong evidence combines a labelled boundary or system, a baseline period, and measured consumption or an opportunity apparatus sized against that baseline. Weak evidence remains weak in combination when it lacks that apparatus: energy words, organisation names, standard numbers, meter numbers, savings percentages, folder names, download sessions, and extensions do not activate alone. A filename can retrieve a candidate for local review but cannot create a site or system fact. *"A session should never be treated as proof of topic"*.

## Deliberate nonedges

- `manufacturing.hse-incident` — harm to a person is not an energy survey; the spill-versus-efficiency seam is already owned by environmental-compliance ↔ hse-incident.
- `manufacturing.calibration-record` — as-found/as-left on an instrument is not a site energy baseline; no same-bytes mutex found that needs a new edge beyond the schema default.
- `engineering.process-plant-design` — design bases without a measured baseline stay engineering; coactivation when an ECM attaches design bytes is already covered under schema `also_holds_with: engineering`.
- `logistics` — named in the stamped assignment; no same-evidence mutex found. Meter quantities that move with a shipment are logistics custody, not this row, and do not share a competing fixture with an energy survey in the researched set.

## External artifact research

Used only to establish that the artifact shapes occur in real practice. They do not import legal rules, thresholds or compliance outcomes into the node.

- ASHRAE procedures for commercial building energy audits describe Level I/II/III survey depth, baseline development and opportunity identification as ordinary professional deliverables.
- ISO 50001 energy-review practice describes significant energy uses, energy performance indicators and baselines as EnMS artifacts — supporting the energy-review fixture shape, not a conclusion that possessing the standard text is evidence of operating a system.
- Utility interval-data and combustion-efficiency test sheets are ordinary operator-held records; supplier bills remain transactional.

No retention period, savings guarantee, regulatory outcome or handling class is derived from these sources.

## NEEDS-JOSEPH

1. **NJ-MEA-1 (joint NJ-MEC-3)** — Discriminator between this row and `manufacturing.environmental-compliance`: (a) statutory-scheme frame versus efficiency/baseline frame, as both rows now argue; (b) a reciprocal split written only on one side; (c) a separate carbon/GHG row (not recommended — topic word, not filing world).
2. **NJ-MEA-2** — Is `energy_system` distinct from manufacturing `asset`, or should R1c fold system boundaries into asset with a role qualifier?
3. **NJ-MEA-3** — One global `reporting_period` shared with environmental-compliance, or a differently named baseline-year key?
4. **NJ-MEA-4** — Inherits NJ-MFG-1 on whether Finance `record_type` widens to a global document-function key.

## Recommendations for R1c (no neighbour edits made)

- `manufacturing.environmental-compliance` already carries the reciprocal GHG edge; no change required beyond confirming NJ-MEC-3 ↔ NJ-MEA-1.
- `manufacturing.maintenance-work-order` should carry the boiler identity collision in the opposite direction, naming the same two fixtures.
- `resource_operations.utility-metering-billing` (CODEX-owned id — do not edit from this pass) should eventually carry the reciprocal meter-CSV edge.
- I edited no file other than my own two. I did not touch CODEX manufacturing ids (`manufacturing.production-planning`, `manufacturing.work-instruction`, `manufacturing.tooling-fixture`, `manufacturing.quality-management-system`).

## Self-verification

- `python3 -m json.tool` parses the node cleanly.
- Every `00` span in quote marks was grep-verified verbatim before writing (session clause; year-first clause; parent-dimension clause; authorship-destination clause; Independent Records / Receipts and Confirmations / Review Later residual definitions; multi-domain facts sentence; EXIF-absence clause).
- Every `file_examples.source_type` is drawn from `SOURCE_TYPES`.
- Every edge target is a roster id or a `00` §7.3 residual name.
- Every `collides_with` / `also_holds_with` entry is a `{domain, signal}` object; signals use the SAME FIXTURE BOTH SIDES form; `also_holds_with` is schema ↔ schema only.
- `fields: []`, `dimension_order: []`, `time_first: false`, no thresholds, no handling classes, no invented counts; sensitivity is `potentially_sensitive` only.
- No file example writes a folder path as a fact; thermal image and archive carry `group_without_copying_facts: true`.
- `never_alone` includes cases tempting false files actually trip: organisation/standard names (ISO download), utility bill, bare meter CSV without survey context, maintenance WO on the same boiler.
