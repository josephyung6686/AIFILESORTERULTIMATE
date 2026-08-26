# Research memo — `manufacturing.environmental-compliance`

Date: 2026-08-26
Depth: J-DEPTH
Output: `planning/domains/nodes/manufacturing.environmental-compliance.json`
Roster row: template on the fieldless `manufacturing` schema, `parent_id: null`, `launch: placeholder`

## Result

**Accept**, with three proposed fields routed to R1c and four NEEDS-JOSEPH items. The row survives the charge because its anchor is an **externally issued authorisation and the release points its conditions name** — an object that outlives every product, spans every asset, and is created by a party other than the holder. That is not a `work_type` value on the manufacturing schema, and it is not the schema's default template: it recommends a different first dimension, a different validation rule family, and a materially different privacy posture (the same bytes are simultaneously commercially damaging and publicly registered).

## The charge — the strongest case that this row should not exist

I ran the charge before writing anything. Six attacks, in descending order of force.

**1. It is a `work_type` value, not a node.** The manufacturing schema's own `work_types[]` already contains *"site HSE inspection, permit, risk assessment or incident record"*. If a permit is a value of `work_type`, this row is a category label wearing a template's clothes — precisely the 574's failure.

*Defeated, but only partly.* The schema entry is real and I do not dispute it; what it misses is that a permit is not only a document kind, it is a **container that other documents are filed against**. A monitoring return, a laboratory certificate, a custody form, a CEMS export and a variation application are five different document kinds that are unintelligible except as evidence against one numbered condition of one instrument. `00`'s own rule for dimension order is the test: *"a parent dimension should provide the context required to understand the child"* is stated there as a practical rule, and the permit is that parent. A `work_type` value cannot be a parent dimension. What the schema entry does correctly show is that the *word* "permit" is a value — which is why the node's `never_alone` list forbids activating on it.

**2. It duplicates the schema's default template.** The manufacturing anchor's `template.why` recommends two branch shapes: `product → batch_lot → record_type` for production and quality, and `site → asset → record_type` for maintenance and calibration. If this row's recommendation is the second of those, it is the default.

*Defeated on evidence.* It is neither. `EPR-AB1234 - Quarterly Monitoring Return Q2 2026 - Outfall 001.xlsx` has no product, no lot, and no asset. Filed under `site → asset` it would have to attach to whichever machine happens to vent to the stack — and several machines do. Filed under `product → batch_lot` it would scatter, because an outfall discharges continuously across every lot the plant makes. The proposed order `authorisation → emission_point → reporting_period → record_type` shares no level with either default shape above `record_type`. That is a genuine template difference and it is the strongest single leg of the node test.

**3. It duplicates `government.environmental-regulation`, which has already landed.** That row holds permits and monitoring returns. Two rows holding the same document types is duplication.

*Defeated, and pre-argued by the neighbour itself.* That row's own edge against me says: *"An operator's compliance folder and a regulator's site file contain the identical permit copy, the identical monitoring return, and the identical laboratory certificate."* It resolves the split by **custody role**, not by document type, and names the discriminating fixture. I have mirrored it exactly (same fixture, same discriminator, same Review Later abstention) and additionally recorded it as a `role_split`, because this is the textbook case: same entity, different field keys, each side holding one role.

**4. It is a lifecycle stage.** "The periodic proof that the permitted limits were kept" is the closing stage of a control cycle. Stages are not nodes.

*Defeated.* A stage ends. An authorisation does not: it is varied, transferred, surrendered and renewed over decades, and the return for Q2 2026 sits beside the return for Q2 2019 under the same conditions. A stage-shaped row would have had `reporting_period` first; this row explicitly puts it near the leaf and sets `time_first: false`, citing `00`: *"For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders."*

**5. It is never-alone evidence — an organisation name.** "Environment Agency", "EPA", "UKAS" are organisation names, and `00` forbids an institution name as sole proof.

*Conceded and encoded, not defeated.* This is correct and it is why the node's `never_alone` list names the regulator, the accredited laboratory, the consultancy **and** the certification body together. A laboratory letterhead is the single most tempting false activator in this world, and it identifies the tester, never the holder of the obligation.

**6. It is a row defined by the absence of something.** "Compliance" often means "the residue of regulatory paper that no other row wanted".

*Defeated by the positive structures.* Every deterministic signal in the node is a positive relation between labelled slots — a condition number binding a substance to a limit to a release point; a return row pairing a measured result with the limit for that parameter; a three-party custody chain with waste codes; an averaging period beside a validity flag. None of them is "not covered elsewhere".

**Verdict: accept.** Had only attacks 1 and 4 survived I would have refused and routed the coverage to the manufacturing default plus Independent Records. Attack 2's failure is what makes the row real.

## The node test, argued in three legs

CONNECTION.md §2's test is that a template exists only where its **detection signals**, **recommended dimensions**, or **privacy rules** differ from its schema's default. All three differ; any one would have sufficed.

**Leg 1 — detection signals.** The schema default fires on a transformation or control cycle: traveller/genealogy structure, characteristic-versus-tolerance inspection tables, event-identifier-plus-disposition structure, asset-plus-failure-code work orders. None of those appears in `EPR-AB1234 - Quarterly Monitoring Return Q2 2026 - Outfall 001.xlsx`, in `Environmental Permit EPR-AB1234 - variation notice - Schedule 3 conditions.pdf`, or in `Consignment note ABC123-00042 - hazardous waste.pdf`. This row fires instead on numbered-condition-to-limit-to-release-point binding, on result-versus-permitted-limit pairing, on sample-point-rather-than-product custody, and on the three-party waste chain. The schema default would miss all four; this row would miss every traveller and every calibration certificate. The signal sets are close to disjoint above the shared `record_type` leaf.

**Leg 2 — recommended dimensions.** Set out under attack 2 above. `authorisation` and `emission_point` do not exist anywhere in the schema's proposal set, and `reporting_period` is a subject here where elsewhere in manufacturing it would be a timestamp. Both remain unserialised (`dimension_order: []`) because the schema declares no canonical fields under PR-6; the recommendation is held as prose in `template.why`, which is the only contract-compliant form.

**Leg 3 — privacy rules.** The schema default's posture is uniform commercial confidentiality plus worker names. This row's posture is genuinely bimodal and that is unusual enough to be worth a node on its own: an exceedance self-notification is legally consequential and can be self-incriminating, while the permit it cites is typically on a public register. The rule this row adds is **public availability of the instrument is not proof that the local packet is low-sensitivity** — the operator's own returns, internal audit findings and incident narratives are not made public by the permit being public. The row assigns no handling class; P7 owns that.

## Files considered and rejected

A row that only lists what it holds has not been researched. These were tempting and are not this row's evidence.

- **`COA - AX410 lot L240817-03 - finished goods.pdf`** — the collision fixture, carried in `file_examples` deliberately so the discriminator is testable. Byte-for-byte the same certificate skeleton as the effluent certificate: laboratory letterhead, analyte, method, result, limit of detection, accreditation identifier, authorising signature. The only discriminator is the labelled slot — **Product and Batch** versus **Sample Point**. Analyte names discriminate nothing (a metals suite is run on both effluent and alloy), accreditation numbers discriminate nothing, and the word "pass" discriminates nothing. Belongs to `manufacturing.inspection-record`.
- **`Invoice 88421 - effluent sampling and analysis - Q2.pdf`** — carries the words effluent, analysis, sampling and a quarter. Carries no sample point, no result, no limit, no permit reference. Proves a purchase. Routes to Receipts and Confirmations, which `00` defines as holding *"isolated invoices, delivery confirmations, booking records"*.
- **`Site safety inspection Plant 2.pdf`** — the manufacturing schema anchor's own fixture. Hazard/control/action table, responsible role, closeout. I do not claim it: nothing in it names a release, a receiving medium or an authorisation. It stays with the schema default and the HSE cluster.
- **`ECN-1042 housing wall thickness.pdf`** — an engineering change with an environmental rationale is still an engineering change. Revision from/to plus design rationale is `engineering.change-order`; a permit condition would have to be cited as the design duty before this row has anything to hold.
- **`Environmental Statement - Mill Lane redevelopment - Chapter 8 Air Quality.pdf`** — named by `government.environmental-regulation` in its planning boundary. Rejected here for the same reason it is rejected there: it is prospective assessment submitted to *obtain* a consent. This row begins where an authorisation already exists and something is being measured against it. I take no edge to `government.planning-application`, because the gov row already owns that seam and a third claimant on the same bytes would make the mutex unresolvable.
- **A downloaded copy of an ISO 14001 or a reference method standard.** A standard designation is `never_alone`. A bound copy of a published standard is `engineering.standards-library` or Reading Inbox; possessing the text is not evidence of operating a system under it.
- **A safety data sheet.** Substance names, hazard codes, disposal guidance — every trigger word this row has, and no obligation, no release point, no measurement. It is supplier reference material about a purchased chemical.
- **A consignee's permit reference on a consignment note.** Explicitly listed in that fixture's `must_not_conclude`. The receiving facility's permit is not the holder's authorisation, and this is the exact never-alone case a bare permit-shaped token would trip.
- **An instrument-vendor binary export from a gas analyser.** Represented, not opened; the filename cannot manufacture an emission point. Unsupported or Encrypted.
- **A live regulator portal account or an environmental-data system.** A source system, not a file node. A bounded export with a readable manifest is represented (`EPR-AB1234 - annual return pack 2025.zip`); connector ingestion is a later security decision.

## Reciprocal boundaries

Every neighbour below is stated in both directions, and each names the same fixture on both sides.

| Neighbour | This row holds | Neighbour holds | Shared fixture |
|---|---|---|---|
| `government.environmental-regulation` | operator custody: prepared-by operator role, covering submission, no receipt slot | authority custody: date-received, receiving officer, officer assessment, issued instrument | `EPR-AB1234 - Quarterly Monitoring Return Q2 2026 - Outfall 001.xlsx` — the neighbour's own named fixture, adopted unchanged |
| `manufacturing.inspection-record` | certificate whose labelled slot is a **sample point** and a receiving medium | certificate whose labelled slot is a **product and batch** with a specification and a release disposition | the certificate-of-analysis pair, both carried as file examples |
| `manufacturing.hse-incident` | harm or potential harm to **air, water or land**, assessed against an authorisation | harm or potential harm to a **person at work**, assessed against occupational duties | one spill: the discharge notification is mine, the chemical-burn report with injury classification is theirs |
| `manufacturing.energy-audit` | statutory scheme frame — registration reference, organisational boundary, reporting period, verification opinion | consumption profiling, efficiency measures, payback, savings | `2026 GHG inventory - Scope 1 and 2 - Plant 2.xlsx`, whose verification tab and savings tab support opposite sides and legitimately coexist |
| `logistics.customs-export` | producer's duty-of-care record: waste codes, producer site, period register | the movement: carrier instruction, routing, border formalities, delivery proof | `Consignment note ABC123-00042 - hazardous waste.pdf`, held by producer here and by carrier there |
| `business_operations.compliance-audit` | findings citing an **environmental** obligation, release or waste duty | audits of organisational controls generally, including inseparable integrated systems | an integrated-management-system surveillance report — this row activates per-finding and abstains on the report as a whole |

The `government.environmental-regulation` boundary is additionally written as a `role_split`, because it is the only one where the same entity type is held by two parties in two roles rather than two different things being confused.

Coactivation (`also_holds_with`, not collisions): `manufacturing.quality-management-system` for an integrated manual whose clauses are simultaneously both systems' governing text; `engineering.process-plant-design` for an abatement design basis that cites a permit condition as its design duty; `business_operations.corporate-regulatory-filings` for a verified emissions report that is both a scheme return and a component of an annual filing.

**Neighbours deliberately left unedged.** `government.planning-application` — the gov row already owns that seam; a third claimant would make it unresolvable. `engineering.product-certification` — that row already recorded, in its own memo, that it left this boundary unedged "to avoid a third claimant on declaration-shaped files"; I reciprocate by not adding one. A product environmental declaration is about the article placed on the market; a permit is about the site operating. `construction_property.compliance-certificate` — an asbestos survey or contaminated-land report on a property under a professional instruction is theirs; the same substance in an operating plant's waste stream is mine, but the two do not compete over the same bytes often enough to earn a mutex at placeholder depth. `manufacturing.safety-case` — a major-accident-hazard demonstration is a different obligation with a different receiving object; if landed sibling research shows a true same-bytes mutex, R1c can add it.

## The collision fixture, isolated

If only one thing from this memo is carried into review, it should be this pair:

```
COA 26-11884 - Outfall 001 composite - 2026-06-30.pdf     → this row
COA - AX410 lot L240817-03 - finished goods.pdf           → manufacturing.inspection-record
```

Identical letterhead, identical analyte/method/result/LOD/accreditation structure, identical signature block, frequently the same laboratory on the same day. **The discriminator is one labelled slot: Sample Point versus Product and Batch.** Nothing else in either document separates them. This is why the node forbids activating on a laboratory name, an accreditation number, an analyte, a method reference or a pass word, and why `emission_point` carries a `validated` ceiling requiring cross-check against a release-point table rather than accepting a bare identifier.

## Proposed fields — justification and what was rejected

`fields: []` is correct: the manufacturing schema declares none under PR-6 and D1's deferral, and a template may not mint what its schema lacks. Three candidates go to R1c, additive to the schema anchor's six (`product`, `site`, `batch_lot`, `asset`, `quality_event`, `record_type`), which I do not re-propose.

- **`authorisation`** — no canonical key names an externally issued instrument carrying numbered conditions. `institution` is a financial issuer; `project` is bounded work; `record_type` names the document not the permission. The schema's `site` cannot substitute: one site holds several authorisations with different conditions, points and calendars, and one installation permit may cover several buildings. `validated` ceiling, gazetteer-free — the rule family is *labelled permit/licence/consent slot plus a numbered-condition structure or an issuing-authority block*. No regex, no threshold.
- **`emission_point`** — `location` is the Photos capture role (a photograph of Outfall 001 may be taken from the opposite bank), and `asset` is the maintained item. The argument for a distinct key: several assets vent through one stack, an outfall has no maintenance history or asset tag, and a monitoring borehole produces no output at all. The honest counter-argument — a stack *is* a maintained item — is recorded as NJ-MEC-2 rather than smoothed away.
- **`reporting_period`** — `term` is academic, `tax_year` is fiscal, `capture_year` is Photos, and `creation_date` is when the file was made, which for a return is routinely a *different* period from the one it reports. `possible` ceiling only: a filename token like "Q2 2026" is ambiguous with a financial quarter and a version.

Rejected outright: minting a manufacturing-only synonym for `record_type` (the schema anchor already contests its Finance scope at NJ-MFG-1, and this row inherits rather than answers that); `purpose` (canonically scoped to College Applications); `stage` (a research workflow field, and a permit is not a stage); `event` (an exceedance is tempting, but the schema anchor's `quality_event` proposal and a possible global `case` key are already before R1c — reusing a pending proposal beats minting a variant); a `regulator` key (an organisation name is never-alone evidence and must never become a destination dimension).

## Grouping without copied facts

Group boundaries are one authorisation, one release point, one reporting period, one sample identifier, one waste stream, one exceedance. Membership creates nothing. Three fixtures carry `group_without_copying_facts: true` for exactly this reason: `CEMS hourly export - stack A2 - 2026-06.csv` has no permit reference in it and must join a permit packet without acquiring one as a fact; `IMG_9042.jpg` may sit beside an exceedance file without becoming evidence of it; `EPR-AB1234 - annual return pack 2025.zip` is read from its manifest and never unpacked to disk to improve classification. `00`'s activation-versus-grouping distinction is load-bearing here — a sparse file joins the neighbourhood without this row firing on it.

## NEEDS-JOSEPH

1. **NJ-MEC-1 — one global `authorisation` key, or per-schema synonyms?** Permits and licences also anchor `government.permit-licensing`, `construction_property.building-control` and `logistics.driver-compliance`. *Alternatives:* (a) mint one canonical `authorisation` reused by all four, accepting that its validation context differs per schema; (b) let each schema keep a private key, accepting four near-synonyms. This row prefers (a) and will adopt whatever R1c mints.
2. **NJ-MEC-2 — is `emission_point` distinct, or `asset` with a role qualifier?** *Alternatives:* (a) a distinct key, on the grounds that several assets share one stack and an outfall has no maintenance history; (b) fold into `asset` with a role qualifier, on the grounds that a stack is a maintained, inspected item and two keys for one physical thing invites drift. Not settleable from the design docs.
3. **NJ-MEC-3 — the GHG/energy seam.** The same meter bytes serve a statutory emissions return and an efficiency study. *Alternatives:* (a) the statutory-scheme frame (registration, boundary, verification opinion) is the discriminator, as proposed here; (b) a reciprocal split written on `manufacturing.energy-audit` instead; (c) carbon reporting is pulled out to its own row, which this memo does **not** recommend — it would be a topic word, not a filing world.
4. **NJ-MEC-4 — `record_type` reuse.** Inherited unresolved from the schema anchor's NJ-MFG-1. This row does not answer it.

## Recommendations to R1c (no cross-row edits made)

- `government.environmental-regulation` may wish to add the reciprocal `role_split` this row wrote; its own edge already contains the substance under `collides_with`, so no change is required.
- `manufacturing.inspection-record` should carry the certificate-of-analysis collision in the opposite direction, naming the same two fixtures.
- `manufacturing.energy-audit` should carry the GHG-inventory boundary; NJ-MEC-3 is jointly theirs.
- `manufacturing.hse-incident` should carry the one-spill-two-files boundary.

I edited no file other than my own two.

## Self-verification

- `python3 -m json.tool` parses the node cleanly.
- All five `00` spans in quote marks grep back verbatim with exactly one match each (lines 45, 95, 120 ×3): the session clause, the year-first clause, and the Independent Records / Receipts and Confirmations / Review Later residual definitions.
- Every `file_examples.source_type` is drawn from `SOURCE_TYPES`; `spreadsheet`, `text_document`, `ocr`, `email`, `image`, `calendar`, `archive` all appear.
- Every edge target is a roster id (`government.environmental-regulation`, `manufacturing.inspection-record`, `manufacturing.hse-incident`, `manufacturing.energy-audit`, `logistics.customs-export`, `business_operations.compliance-audit`, `manufacturing.quality-management-system`, `engineering.process-plant-design`, `business_operations.corporate-regulatory-filings`, `business_operations.risk-register`) or a `00` §7.3 residual name.
- `fields: []`, `dimension_order: []`, `time_first: false`, no thresholds, no handling classes, no counts, sensitivity is `potentially_sensitive` only.
- No file example writes a folder path as a fact; three carry `group_without_copying_facts: true`.
- `never_alone` includes cases a tempting false file actually trips: the accredited-laboratory name (tripped by `COA - AX410 lot...`), the bare permit-shaped token (tripped by the consignee's reference on the consignment note), and the invoice case (tripped by `Invoice 88421`).
