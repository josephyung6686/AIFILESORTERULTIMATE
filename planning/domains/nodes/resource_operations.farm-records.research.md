# resource_operations.farm-records — research memo (R1b, J-DEPTH)

Date: 2026-08-27
Roster row: `kind: template` · `schema_id: resource_operations` · `launch: placeholder`
Legacy coverage: `agri.farm-records` (ROW)

## Verdict

**Keep provisionally; do not refuse.** The row describes a real organizational situation: the
operator-side record of running a holding through a crop or livestock season. A crop plan, herd
register, treatment log, yield return, claim support and assurance response are not merely generic
resource outputs; they join a biological production unit to husbandry/input activity, seasonal
production and traceability. That relation is narrower than the resource_operations anchor's
general authorized-source, operating-unit, measured-output and environmental-performance grammar.

The survival is conditional. `resource_operations` is intentionally a PR-6 fieldless placeholder,
so this row writes no fields and no executable dimensions. R1c should collapse it if farm-specific
field/block, crop/livestock-unit and seasonal husbandry signals are judged to be only values of the
default's work types. The row is not retained merely to rescue the legacy id.

## Authority stack and method

Read and applied:

- `planning/domains/dispatch/RESEARCH-BRIEF.md`, including the 2026-08-24 J-DEPTH requirement.
- The complete stamped output of
  `python3 planning/domains/dispatch/make_prompt.py resource_operations.farm-records`.
- `planning/prompts/ALIGNMENT.md` and authoritative `planning/00-database-agent-product-design.md`.
  `planning/01-product-design-structured.md` was used only as a locator; `00` wins.
- `planning/domains/CONNECTION.md`, `CONNECTION-EXAMPLES.md` and `_CONTRACT.md`, especially the
  node test, activation/grouping firewall, closed edge vocabulary and template-only prohibition
  on `also_holds_with`.
- `planning/domains/canonical_fields.json`, `planning/domains/roster.json`, `ROSTER.md` section 4
  and Appendix A, and `src/evidence_shape/vocabulary.py`.
- `planning/overnight/council/DECISION-BRIEF.md`: D1–D6, J-IND and J-DEPTH are treated as ratified.
- The landed `resource_operations` schema and its research memo, the landed
  `resource_operations.utility-metering-billing` sibling, and the launch-depth
  `identity.core-documents` exemplar for key set, abstention and evidence depth.
- The landed neighbour anchors and rows for `engineering.commissioning-handover`,
  `engineering.process-plant-design`, `government.grant-programme-administration`,
  `government.permit-licensing`, `government.environmental-regulation`,
  `business_operations.compliance-audit`, `business_operations.corporate-regulatory-filings`,
  and `resource_operations.renewable-generation` where available.
- `business_operations.organisational-records.json` was read as the refusal-quality exemplar;
  its residual/never-alone reasoning is used here to keep a generic farm label from becoming a
  node if the specific biological-production relation disappears.

No jurisdiction-specific subsidy rule, animal-identification format, veterinary rule, assurance
standard, pesticide threshold, environmental limit, acreage statistic, market value, detector regex
or confidence score is claimed. The named files are fixture-grade examples of recurring record
structures; the conclusions are inference/proposal, not legal or regulatory authority.

## Design evidence and quote discipline

The direct design anchors are deliberately narrow:

- `00` says, **“Every file will be treated as a record with many facts, rather than forcing it into
  one permanent category.”** Farm evidence therefore remains a set of observations and separately
  validated facts, not a category label copied to every member of a holding's neighbourhood.
- `00` says, **“A session should never be treated as proof of topic, and it should not carry the same
  confidence as a hash match or a directly extracted document fact.”** A portal download, inspection
  visit or fieldwork batch can support review and grouping only.
- `00` says, **“For document and record domains, project, function, or subject usually comes before
  time because putting year first scatters related work across calendar folders.”** The farm prose
  recommendation is holding/field or herd before season.
- `00` says, **“The system recommends an order based on the domain template, but the user can reverse,
  remove, add, or flatten dimensions.”** The empty JSON order is therefore a contract consequence,
  not a frozen farm path.
- For image evidence, `00` says, **“However, the system must not mistake the absence of EXIF for proof
  that an image is a screenshot.”** A crop photograph can be a camera file, a scan or a messenger
  derivative; its farm role requires content or accepted-group evidence.

These are the only direct product-design quotations used in the JSON. Farm-specific structure,
collisions and field recommendations are marked as inference or proposal, and are not smuggled into
`design_cite`.

## J-DEPTH node test — all three legs

### 1. Detection signals differ from the schema default

The `resource_operations` anchor is intentionally wide. It joins an authorized source or site,
operating unit or asset, measured output and environmental performance over a period. Its default
can reasonably recognize a production return, environmental record, meter series or operational
register across many resource industries. A generic `Farm Production Return.xlsx` may therefore be
the default template's work type unless the evidence shows what makes it biological farm operation.

This row's additional relation is a biological production unit plus its husbandry or cultivation
cycle. `Farm-12_Crop-Plan_2026.xlsx` has field/block, crop/variety, rotation, sowing, input and
harvest relations; `Herd-Register_Red-Hill_2026.xlsx` joins animal or group identifiers to movement
and treatment events; `Field-12_Soil-and-Fertiliser-Log.csv` joins an input to a field, crop and
application activity. A quantity column, a farm name, a crop word or a season token without those
labelled relationships is not enough.

The row also recognizes the operator side of farm claims and assurance work when the claim or audit
contains production evidence: eligible fields or animal groups, declared activity, supporting maps,
traceability, corrective operation and closeout. The funder lifecycle, issuing authority's permit
case and generic audit programme belong to neighbours even when they reuse the same farm name and
period. This positive/negative pair is what keeps the row from becoming a synonym for “anything in
a farm folder.”

### 2. Recommended dimensions differ from the schema default

The anchor's provisional prose order is `site → operating_authority → output_stream → reporting_period
→ record_type`, with an asset-led alternative for utilities and generation. Farm records need a
different operational emphasis: `holding/site → field/block or herd/flock → crop, livestock group or
output stream → reporting period → record type`. A field-led branch makes crop applications and
harvest intelligible; a herd-led branch makes treatment, movement and production intelligible.

The recommendation omits authority where it merely repeats across one holding, and does not put
animal tags, chemical rates, coordinates, prices, claim references or quantities into a folder tree.
An asset or lot level is optional for a stable irrigation, storage, feed or traceability subject.
This is a recommendation only, and all arrays remain empty because a template may branch only on
fields its `uses_schema` declares and `resource_operations` currently declares none. R1c may license
the anchor's proposed `site`, `asset`, `output_stream`, `reporting_period` and global `record_type`,
or decide that a neutral biological-unit value is required. This node does not mint a synonym.

Time is not first. A crop year or veterinary visit date is useful evidence, but year-first filing
would scatter one field or herd's record across seasonal folders. The user may reverse, remove, add
or flatten any eventual order.

### 3. Privacy differs from the schema default

Generic resource operations can be commercially or infrastructure-sensitive. Farm records add
frequent, intimate joins: identifiable landholders and farm addresses; field boundaries and GPS;
animal or herd identifiers; veterinary medicines and withdrawal periods; chemical applications;
subsidy eligibility; assurance findings; yield, buyer and production volumes. A sparse animal note or
field photograph may be harmless alone but becomes sensitive inside an accepted holding group.

The JSON therefore marks the row `potentially_sensitive`, keeps raw identifiers, coordinates,
quantities, medicine details and claim references out of proposed destinations, and routes uncertain
or customer/owner-linked material to protected review where appropriate. This is not a P7 handling
class. A local model may be allowed only by the user's policy; a cloud prompt must not receive full
farm packets by default.

### Node-test conclusion

The row clears the test only in the narrow biological-production form: distinct field/block or
herd/flock and husbandry/traceability relations; a holding-first, biological-unit recommendation;
and a privacy posture shaped by land, animal-health, treatment, subsidy and yield joins. If R1c sees
these as ordinary values under the resource default, refusal is correct. The JSON makes that collapse
condition explicit.

## Bottom-up file set

The JSON carries twenty observation/fact fixtures. The decisive set is:

1. **`Farm-12_Crop-Plan_2026.xlsx`** (`spreadsheet`). A labelled holding, field/block, crop,
   season, rotation and planned input/harvest schedule gives the positive cultivation relation.
   Planned rows are not proof that work occurred; the filename is not a crop-year fact.

2. **`Herd-Register_Red-Hill_2026.xlsx`** (`spreadsheet`). Holding, species, group or animal
   identifiers, movement and treatment sheets form the positive livestock relation. An ear-tag
   token cannot establish ownership, current status or a government registry acceptance.

3. **`Field-12_Soil-and-Fertiliser-Log.csv`** (`spreadsheet`). Labelled field, crop, product,
   application date, rate, unit and operator make an input activity, while planned/completed state
   and safety interpretation remain source evidence rather than conclusions.

4. **`Animal-Movement-Declaration_Red-Hill_2026-04-03.pdf`** (`text_document`). A movement form
   joins consignor, destination, species, group identifiers and declaration/receipt roles. It may
   belong to both operator farm operations and a government registry workflow; custody and acceptance
   are unresolved from the bytes alone.

5. **`Harvest-Yield-Return_Field-12_2026.xlsx`** (`spreadsheet`). A cover sheet and rows join a
   holding, field, crop, season, harvested area, loads/lots, weight, grade and destination. It does
   not prove saleability, payment or independent verification.

6. **`Subsidy-Claim_2026_Field-12.pdf`** (`text_document`). Claimant holding, eligible field
   schedule, crop/stewardship activity, claim period, map and declaration are farm-side evidence;
   funder receipt and assessment belong to the government collision side. A claim is not an approval.

7. **`Farm-Assurance-Inspection_Red-Hill_2026-06.pdf`** (`text_document`). Holding, production
   system, inspected fields/animal areas, evidence checklist, findings and corrective action make a
   farm assurance cycle. Certification programme and assessor closure are also business compliance
   evidence; neither side may steal the whole packet.

8. **`Water-Abstraction-Permit_Farm-12.pdf`** (`text_document`). Issuer, permit reference, farm,
   abstraction point and conditions are an authority instrument. It becomes farm operational
   evidence only when joined to completed field use, measured abstraction or compliance work.

9. **`Irrigation-Pump-Commissioning-Pack_Field-12.zip`** (`archive`). The manifest lists an
   as-built layout, pump datasheet, tests, settings and handover certificate. It is a commissioning
   packet first; an operating farm relation requires subsequent field-use or monitoring evidence.

10. **`Crop-Yield-Photos_Field-12_2026-08-17.jpg`** (`image`). Camera EXIF and a field marker or
    harvest scene make a useful possible group member, but not a crop or yield fact. The image can
    independently carry Photos capture facts, and absent EXIF cannot prove screenshot status.

11. **`Vet-Visit-Ewes_2026-04-03.eml`** (`email`). Native sender/recipient slots and the body cite
    a veterinary practice, animal group, date and follow-up. The email may join an accepted herd
    group; it does not prove a diagnosis, treatment outcome or complete medicine register.

12. **`Spraying-Schedule_Field-12.ics`** (`calendar`). A field and planned spray in the event
    summary, with time and organiser, is an intended activity. It is not proof that spraying occurred
    or that a calendar file belongs to farm operations.

13. **`Field-Boundaries_North-Block_2026.geojson`** (`code_structured`). Feature properties join
    field/block identifiers and land-use or crop values to geometry and a survey date. Coordinates
    are evidence, not destination dimensions; legal ownership and current cultivation remain unknown.

14. **`Nutrient-and-Runoff-Compliance-Return_Field-12.xlsx`** (`spreadsheet`). Operator field,
    crop and nutrient/runoff rows appear alongside submission/review slots. The same bytes can hold
    farm operating evidence and an authority environmental return; parameter, unit and exceedance
    words alone decide neither side.

15. **`Farm-Solar-and-Crop-Operations_2026.xlsx`** (`spreadsheet`). Crop and harvest sheets sit
    beside generator/export/availability sheets. It is the same-schema sibling collision fixture:
    agricultural operations and renewable-generation evidence must be resolved per section, not by
    the holding name or an energy column.

16. **`Farm-Records-Export_Red-Hill_2026.zip`** (`archive`). The manifest mixes crop, herd, input,
    harvest, movement and assurance members. It supports bounded group review but cannot donate one
    holding, season or field fact to every member; the archive is inspected without unpacking.

17. **`Irrigation-Layout_RevC_Field-12.dwg`** (`design_creative`). Pipes, valves, pump tags,
    design flow and revision-controlled title-block material are engineering design evidence. A
    field boundary or farm name does not make the drawing an operating irrigation log.

18. **`Crop-Plan-Scan_Field-12.jpg`** (`ocr`). OCR recovers a handwritten field heading, crop,
    planting notes and dates, but the holding and completion relations are incomplete. Partial OCR
    is not validated fact and should go to review unless another accepted anchor resolves it.

19. **`Farm-12_Production-and-Cashflow_FY2026.xlsx`** (`spreadsheet`). Crop/livestock quantities
    coexist with sales, costs, loans and cashflow. It is a multi-schema fixture; the holding name
    does not make every sheet farm operations, Finance or business planning.

20. **`Farm-Portal-Submission-Receipt.bin`** (`opaque_binary`). An opaque or encrypted download has
    only a farm-shaped filename and submission word. It must fall through to Unsupported or Encrypted.

This set covers labelled forms, structured tables, free prose via email, OCR, native and scanned
images, calendar/contact-adjacent material, geospatial data, design files, archives and unreadable
bytes. It includes sparse members, same-byte collisions, independent coactivation candidates and
explicit no-copy boundaries.

## Reciprocal boundaries and same-byte collision fixtures

### Government grant programme administration

**Same fixture bytes:** `Subsidy-Claim_2026_Field-12.pdf`.

- This row owns the applicant-side farm relation: holding, eligible fields or animal groups,
  declared crop/stewardship activity, supporting maps or registers and production evidence.
- `government.grant-programme-administration` owns the funder-side programme: scheme rules,
  application intake, eligibility assessment, award/refusal, payment authorisation, monitoring and
  recovery.

A scheme name, grant reference, holding or claim period allocates neither side. The claim packet may
  carry both relations on disjoint evidence. This template authors only `collides_with`; the intended
  schema coactivation is recorded in the R1c section below.

### Government permit licensing

**Same fixture bytes:** `Water-Abstraction-Permit_Farm-12.pdf`.

- This row owns the operator-side farm workflow only when the permit is joined to field/storage use,
  abstraction measurements, irrigation activity, a completed return or corrective work.
- `government.permit-licensing` owns the issuing-authority instrument: application, decision,
  conditions, effective area, variation, renewal, suspension or revocation.

Authority, permit number, farm address and condition schedule alone do not reveal custody. A farmer's
reference copy is not an authority case, and an authority instrument is not evidence that a field was
irrigated. The same bytes can support both only where both relations are actually present.

### Government environmental regulation

**Same fixture bytes:** `Nutrient-and-Runoff-Compliance-Return_Field-12.xlsx`.

- This row owns the operator's field, crop, nutrient application, soil/runoff measurement and
  corrective-operation evidence.
- `government.environmental-regulation` owns authority-side return intake, permit-condition
  assessment, sampling and enforcement casework.

A determinand, unit, field name, permit reference or exceedance word alone supports neither side. A
farmer's input log does not become authority monitoring, and a regulator's inspection notice does not
become a farm cultivation record merely because both mention the same field.

### Business compliance and audit

**Same fixture bytes:** `Farm-Assurance-Inspection_Red-Hill_2026-06.pdf`.

- This row owns inspected farm production, fields, animals, treatments, traceability and corrective
  operation.
- `business_operations.compliance-audit` owns audit programme, control objective, assessor finding,
  nonconformity, remediation owner, evidence request and closure record.

An assessor, checklist, certification body, finding or renewal date alone does not decide the side.
The farm row must not take a generic internal audit; the business row must not take a field or herd
register merely because an auditor reviewed it.

### Engineering commissioning and handover

**Same fixture bytes:** `Irrigation-Pump-Commissioning-Pack_Field-12.zip`.

- This row owns an operating farm relation only if the installed pump or irrigation asset is tied to
  completed field use, water application, production monitoring or an operating register.
- `engineering.commissioning-handover` owns controlled design identity, inspections/tests, settings,
  as-built records, punch-list closure and system acceptance.

A pump tag, field address, flow value, drawing or handover word alone allocates neither side. Farm
operations must not take the design pack merely because it names a field; engineering must not take a
completed crop or irrigation log merely because it names a commissioned pump.

### Renewable generation sibling

**Same fixture bytes:** `Farm-Solar-and-Crop-Operations_2026.xlsx`.

- This row owns field, crop, livestock, input and harvest relations. A solar installation incidental
  to the holding does not turn crop records into generation records.
- `resource_operations.renewable-generation` owns generator/installation identity, production and
  export intervals, availability, curtailment, incentive and energy-settlement relations.

A solar-farm name, energy quantity, export column, season or site name alone allocates neither side.
Both rows may legitimately hold different evidence from the same workbook, but this row must not
claim generator performance and the generation row must not claim a crop or herd return.

## Files considered and rejected

- **Generic farm account or cashflow workbook.** Finance and business planning structures win when
  costs, loans, accounts, statements or forecasts dominate; a holding name does not activate farm
  operations.
- **Crop commodity market report or price bulletin.** A crop name and yield statistic are topic
  evidence, not one holding's cultivation or harvest record; absent an accepted group, use Reading
  Inbox.
- **Agronomy guide or fertiliser product label.** Instructions and product composition are reference
  material; they are not proof an input was applied to a field.
- **Animal photograph, generic veterinary article or pet record.** Species, breed or a medicine word
  alone does not establish a farm herd, movement or production relation.
- **Livestock transport invoice or warehouse consignment ledger.** A quantity and destination are
  logistics/custody evidence unless the file also joins a holding and animal-group operating record.
- **Authority permit, grant award or public subsidy guidance.** Issuer-side government material is
  not a farmer's operating evidence without an independently evidenced farm workflow.
- **Assurance policy, ISO-style certificate or generic internal audit.** A standard and checklist
  without inspected farm production or traceability belongs to business compliance/reference work.
- **Irrigation design, soil survey or pump calibration certificate.** Engineering definition or
  verification is not a completed farm operation; a later group may connect it without copying facts.
- **Property title, rural lease, boundary survey or development application.** A parcel and rural
  address do not establish cultivation or livestock operation; property/government structures own
  their own relations.
- **Calendar reminder, delivery email or portal receipt.** Communication and session context can help
  P9 grouping but cannot prove completion, acceptance or farm facts on their own.
- **VCF contact export.** A supplier or vet address book is privacy-protected contact material, not
  a farm record; a contact name or organisation is never a farm fact.
- **Encrypted database, proprietary farm-system export or unreadable scan.** Metadata-only indexing
  cannot rescue the template from a farm-shaped filename.

## Neighbours considered without an additional edge

- **`engineering.process-plant-design`** was considered for barns, irrigation, dairy and feed
  systems. The commissioning-pack edge is sharper: design definition and handover already explain
  the shared bytes, while a generic process drawing with no farm operating relation is simply an
  engineering false positive.
- **`business_operations.corporate-regulatory-filings`** was considered for statutory production,
  animal-movement and environmental returns. The government and compliance edges cover the sharper
  issuer/audit boundaries; a return that has both compelled submission and operator measurements may
  coactivate at schema level, but this template does not add a duplicate collision without a named
  fixture.
- **`business_operations.procurement-sourcing`** was considered for feed, seed, machinery and
  fertiliser tenders. Buyer/supplier evaluation is procurement; farm operations begin when the input
  is applied, fed, treated or traced to the holding. The two structures are separable without a broad
  edge.
- **`construction_property.site-survey`** was considered for field boundaries and rural land. A
  survey records observed property/site conditions; this row requires a crop, livestock or husbandry
  relation. The exact boundary is stated in the rejected-file notes rather than a generic collision.
- **`resource_operations.utility-metering-billing`** was considered for irrigation meters and water
  bills. Meter-to-charge lineage is its narrower situation; farm operations may use the resulting
  water record as an input or group member but do not claim billing from a field log.
- **`resource_operations.mining-operations`** and **`resource_operations.forestry-records`** were
  considered for land, harvest and output vocabulary. A crop/animal biological cycle versus mineral
  extraction or woodland management is the discriminator. The rows are sibling values under the
  resource schema; no same-byte fixture was needed for this farm record.

## Proposed fields — deliberately empty

Full list: `[]`. The resource_operations schema declares no field rows under PR-6, and a template
may not invent a second field list or branch on undeclared keys.

The anchor's proposed fields are the only candidates worth carrying forward: `site`, `asset`,
`output_stream`, `reporting_period` and global `record_type`. Farm research shows possible narrower
values—holding, field/block, herd/flock, crop, livestock group, production lot and season—but these
are values/roles to adjudicate, not private keys to mint here. `location` belongs to the Photos
capture-location role, `institution` to Finance's issuer role, and `project` to bounded work; none
should be recycled as a farm synonym without a canonical role decision.

High-cardinality or sensitive evidence stays out of destination fields: animal/ear-tag identifiers,
chemical rates, veterinary details, coordinates, production quantities, buyer names, subsidy
references and assurance findings. `record_type` may eventually be global, but this row does not
restate the anchor proposal. R1c should decide whether a neutral operating-unit field can cover field,
block and herd without erasing the distinction needed for safe grouping.

## Template coactivation for R1c — memo only

The contract restricts `also_holds_with` to schema rows. This template therefore authors an empty
array. R1c should adjudicate the intended independent schema activations:

- **resource_operations ↔ government** for `Subsidy-Claim_2026_Field-12.pdf` when farm production
  evidence and a funder intake/assessment lifecycle both survive in the packet; likewise for a
  permit or animal-movement declaration when operator use and authority case evidence are separate.
- **resource_operations ↔ business_operations** for
  `Farm-Assurance-Inspection_Red-Hill_2026-06.pdf` when farm traceability/corrective operation and
  audit-programme/nonconformity evidence both survive.
- **resource_operations ↔ engineering** for the irrigation commissioning packet only where a
  completed operating relation exists alongside controlled system acceptance; otherwise grouping is
  sufficient and engineering owns the packet.
- **resource_operations ↔ photos** for `Crop-Yield-Photos_Field-12_2026-08-17.jpg` when camera
  capture evidence and independently accepted farm/field evidence coexist. Photos facts remain
  independent and no farm fact is copied from the image's group.

These are intended lifts for R1c, not authored coactivation edges. The JSON's empty
`also_holds_with` is a template contract requirement, not a claim that a file cannot hold multiple
schemas.

## NEEDS-JOSEPH

- **NJ-FARM-1 — template versus default.** Should farm records remain a distinct template once the
  resource anchor is adjudicated, or should crop, livestock, forestry and fisheries situations be
  collapsed into a neutral operating-source template? Keep this row only if biological-unit and
  husbandry/traceability detection, holding-first order and privacy are material differences.
- **NJ-FARM-2 — field vocabulary.** Should R1c reuse `site`, `asset`, `output_stream`,
  `reporting_period` and global `record_type`, or license one privacy-safe field/block or
  biological-unit role? Do not mint `farm`, `field`, `herd`, `crop_year` or `animal_id` as private
  synonyms before that decision.
- **NJ-FARM-3 — coactivation.** Should resource_operations↔government and
  resource_operations↔business_operations be lifted for the named claim/inspection fixtures, or
  should independent evidence records suffice without a schema edge? Template rows cannot settle it.
- **NJ-FARM-4 — sensitive dimensions.** After fields are licensed, should animal identifiers,
  veterinary details, land coordinates, chemical records and subsidy references remain search-only,
  or may a user-confirmed private tree expose selected values?
- **NJ-FARM-5 — sparse media membership.** Should a field photograph, drone layer or calendar item
  join an accepted farm group only through an exact holding/field anchor, or may user-accepted context
  supply membership while the file's own facts remain unknown? Grouping must never copy the group label
  into a file fact.
- **NJ-FARM-6 — claim custody.** When a subsidy or permit PDF is byte-identical in a farmer's folder
  and an authority export, should activation require corpus custody/workflow evidence, allow both
  schemas when their internal structures are present, or route the rendered instrument to government
  and reserve this row for operator logs?

## Refusal condition and audit claim

Refusal status: **not refused, with an explicit collapse condition**. Refuse at R1c if the only
remaining distinction is the value “farm,” a file extension, or an industry label, or if every positive
fixture is already the resource default's generic production/register work type. Keep only if the
biological production-unit relation, recommended holding-first organization and privacy boundary
remain implementable.

The row claims no jurisdictional rule, legal eligibility, animal-health conclusion, treatment safety,
permit validity, assurance outcome, production statistic or destination path. It claims only that
real farm record sets expose recurring labelled relations among holding, field/herd, crop/livestock,
activity, input/output, period, traceability and corrective evidence, and that these relations can be
separated from the named government, engineering, business, finance, logistics and reference files.
