# logistics.shipment — R1b lab notes

**Depth: J-DEPTH**

Date: 2026-08-27
Roster row: `kind: template` · `schema_id: logistics` · `launch: placeholder`
Legacy coverage: `shipment.freight-consignment` (ROW)

## Verdict

**Keep provisionally; do not refuse.** This row is the one-consignment custody dossier: consignor,
carrier and consignee roles; goods/packages; place of taking over and delivery; transport or customs
controls; handover; proof of delivery; and loss, damage, delay or shortage exceptions. It is not a
file-extension bucket and it is not activated by a tracking number, address, carrier brand, purchase
order or invoice alone.

The strongest refusal charge is that the `logistics` schema already names consignments, waybills,
packing lists, proof of delivery, customs documents, vehicles, warehouses and dispatch. That charge
would win if this row merely listed shipping work types. It survives narrowly because the positive
files form one custody chain for one described movement across heterogeneous records. The schema
default's siblings split by fleet, customs, route, warehouse and last-mile situations; this row keeps
the consignment itself as the intelligible subject and distinguishes the party roles on the same
document. If R1c decides a single logistics default already covers that relation, refusal is required.

No field or executable dimension is authored. D1/PR-6 leave `consignment`, `carrier`, `asset`, `site`
and `record_type` proposals in the schema anchor; this template does not copy or mint them. No
template-level `also_holds_with` is authored; intended coactivation appears below for R1c.

## Authority stack and method

Repository material read:

- `planning/domains/dispatch/RESEARCH-BRIEF.md`, including the full J-DEPTH override.
- Complete stamped output of `python3 planning/domains/dispatch/make_prompt.py logistics.shipment`.
- `planning/prompts/ALIGNMENT.md` and authoritative `planning/00-database-agent-product-design.md`.
- `planning/domains/_CONTRACT.md`, `planning/domains/CONNECTION.md` and
  `planning/domains/CONNECTION-EXAMPLES.md` for evidence/fact separation, grouping, residuals,
  node testing and closed edge vocabulary.
- `planning/domains/roster.json`, `planning/domains/ROSTER.md`,
  `planning/domains/canonical_fields.json`, and `src/evidence_shape/vocabulary.py`.
- `planning/overnight/council/DECISION-BRIEF.md` for D1–D6, J-IND and J-DEPTH.
- Logistics schema anchor `logistics.json` and its memo, and the landed-depth
  `identity.core-documents` pair for JSON idiom, OCR/archive abstention and privacy handling.
- Existing same-kind boundaries: `business_operations.procurement-sourcing`,
  `retail_hospitality.supplier-order`, `manufacturing.production-record`,
  `logistics.route-dispatch`, `logistics.last-mile-pod`, `logistics.customs-export`, and
  `logistics.fleet-vehicle`. No other node was edited.

Official sources verify recurring transport record structures only; they do not license product
fields, carrier identity, legal status or jurisdiction-specific rules:

- [UNECE — CMR consignment notes](https://unece.org/DAM/trans/doc/2019/wp24/III.2_CMR_ECMR_RH_30Oct2019.pdf)
  describes a consignment note as evidence of the carriage contract and lists its role in claims for
  loss or delay. It supports the consignor/carrier/consignment fixture without treating a CMR number
  alone as activation evidence.
- [UN/CEFACT eCMR model](https://service.unece.org/trade/uncefact/publication/Transport-Logistics/eCMR/HTML/04286.htm)
  defines a consignment as a separately identifiable collection of goods moving from one consignor
  to one consignee under one transport contract. This supports the consignment-as-subject boundary.
- [GOV.UK — Transport documentation](https://www.gov.uk/government/publications/how-to-trace-weigh-and-distribute-fish-products/transport-documentation)
  distinguishes transport documents from landing declarations and describes seals, destination and
  first-sale movement, grounding the post-handover custody fixture.
- [GOV.UK — Goods vehicle operator licensing guide](https://www.gov.uk/guidance/goods-vehicle-operator-licensing-guide)
  documents vehicle maintenance, operator licensing, tachograph and compliance records. It supports
  the fleet-vehicle boundary; this row does not infer a fleet fact from a route or delivery document.
- [GOV.UK — Drivers' hours and tachographs](https://www.gov.uk/guidance/drivers-hours-goods-vehicles/4-tachograph-rules)
  describes driving, rest, availability, speed and distance data as tachograph records. It supports
  separating a driver/vehicle compliance record from one consignment's custody evidence.

No external source is represented as product-design authority. No numeric threshold, customs code,
carrier catalogue, transport-law conclusion or identifier regex is embedded here.

## J-DEPTH node test — all three legs

### Leg 1 — detection differs from the logistics default

The logistics anchor is broad: goods in somebody's custody, movement from one place to another,
carrier/vehicle/driver licensing, dispatch, customs and depot storage. The child must not be another
industry or document-type label. It requires one **described movement** with party roles, goods or
packages, handover, origin/destination and an acknowledgement or status trail.

A positive CMR, bill of lading, packing list, POD, claim or bounded packet contains that chain. A
freight invoice has money but no custody handover. A calendar run plan has intended times but no
completed receipt. An address, tracking number, carrier name, customs word or pallet photograph can
join a group but cannot activate alone. The defining evidence graph is the custody subject and
handover, not extension or a work-type word.

### Leg 2 — recommended dimensions differ from the schema default

The schema's default is intentionally shared across shipment, customs, fleet, route and warehouse
templates. Conditional on R1c promoting the schema proposals, this row's useful order is **custody
context (only if genuinely multi-carrier or multi-depot) → consignment/container → record type**.
Carrier is a counterparty and should not become a collector folder by default; consignee and delivery
address are role-bearing evidence and should not be path dimensions. Vehicle, depot or working day
belong to fleet/warehouse/dispatch branches when they are the subject.

`dimension_order` is therefore empty because no logistics field is legal yet. The schema's
`consignment`, `carrier`, `asset`, `site` and `record_type` proposals are not repeated in this
template. This is not time-first. The exact design sentence is, “For document and record domains,
project, function, or subject usually comes before time because putting year first scatters related
work across calendar folders.” One movement's booking, customs declaration, waybill, delivery proof
and claim commonly cross dates and must remain retrievable together.

### Leg 3 — privacy and security differ from the default

The generic logistics schema covers movement and custody, but this row concentrates addresses,
recipient names, delivery schedules, drivers, vehicle identifiers, package contents, customs values,
seal numbers, route status and claims. A shipment dossier can expose a person's home delivery,
business inventory, security-sensitive route or commercially confidential cargo. The node is therefore
`potentially_sensitive`; P7 owns handling classes, redaction and local/cloud policy.

The same bytes can also be held by shipper, carrier, broker, consignee, warehouse, customs authority
or buyer. A submitted customs XML may be a Government case or a movement member. A goods-received
form may be Manufacturing incoming quality or Logistics custody. Grouping is allowed only with cited
evidence and does not copy party, consignment, quantity or delivery facts across members.

### Node-test conclusion

Keep only as the narrow one-consignment custody template. R1c should refuse if the corpus contains
only isolated invoices, addresses, tracking exports and delivery documents already owned by the
route, customs, fleet, warehouse or POD siblings, with no cross-document consignment relation.

## Bottom-up file corpus

The JSON carries thirteen concrete fixtures. Since the logistics schema is field-less, positive files
list universal facts only; consignment, carrier, asset, site and document-function conclusions remain
observations or R1c proposals.

1. **`CMR_2026-04-11_DE-HK.pdf`** (`text_document`) — consignor/consignee/carrier role boxes,
   goods, packages, weight, origin/destination and receipt condition. Declared value is not amount due.
2. **`BL_MAEU5512884.pdf`** (`text_document`) — bill of lading with shipper, consignee/notify,
   vessel/voyage, container/seal, cargo, condition and endorsement sections. A bill number does not
   prove title or customs release.
3. **`Packing-List_PO-7714.xlsx`** (`spreadsheet`) — package rows, marks, contents, quantities and
   net/gross weights, with shipment parties. The PO reference does not prove dispatch.
4. **`POD_Consignment-CN-4021.jpg`** (`image`) — signed receipt, pallet labels and partial exception
   mark. EXIF captures the camera, not necessarily delivery location; signature alone is insufficient.
5. **`Delivery-Exception_CN-4021.pdf`** (`text_document`) — carrier/receiver roles, delivered-at
   event, shortage/damage observations and separate claim status. Damage timing and payment remain
   unknown.
6. **`Export-Declaration_MRN-7781.xml`** (`code_structured`) — movement reference, declarant,
   commodity lines, origin, procedure, value and release/submission state. Submission is not release
   or delivery.
7. **`Carrier-Status-Feed_CN-4021.csv`** (`spreadsheet`) — booked/collected/in-transit/held/
   delivered events and timestamps, without package description or independent receipt. It can join
   a consignment group but cannot prove verified delivery alone.
8. **`Scanned-Waybill_CN-4021.pdf`** (`ocr`) — OCR-poor waybill with partial parties, packages,
   destination and handwritten damage note. Scanner metadata is not a transport party.
9. **`Shipment-Packet_CN-4021.zip`** (`archive`) — manifest for booking, CMR, packing list,
   declaration, carrier events, POD and claim correspondence; inspected without unpacking and no
   member facts propagated.
10. **`Driver-Run-Sheet_2026-04-11.ics`** (`calendar`) — planned collection/delivery sequence,
    addresses, vehicle, driver and times. No completed handover or acknowledgement is present.
11. **`Goods-Received_NCR-118.pdf`** (`text_document`) — factory receiving quantity, lot/part
    condition and quarantine/disposition, with a carrier reference. Incoming quality is the central
    role, not necessarily the carrier handover.
12. **`Fish-Transport-Document_Lot-L-771.pdf`** (`text_document`) — post-landing fish lot,
    species/weight, vehicle, origin/destination and seal, citing vessel and landing. Transport weight
    is not silently rewritten as catch.
13. **`Tooling-Shipping-Manifest_T-2048.pdf`** (`text_document`) — tool crate, carrier, seal,
    origin/destination and tracking, with no receiving acceptance. It is the Manufacturing tooling
    collision fixture and Logistics movement evidence.

This set covers labelled forms, structured XML/CSV/XLSX, OCR scans, screenshot/image evidence,
email-like custody workflows through the recognition rules, calendar plans, archives, customs,
claims, warehouse receipt, multimodal movement and cross-domain collisions. A contact export is not a
plausible shipment source in this corpus; no `.vcf` fixture is invented.

## Collisions and reciprocal boundaries

Every JSON collision uses exactly `{domain, signal, provenance}`. Each signal names the same fixture
bytes and explains both directions; R1c must land reciprocal edges or remove a pair:

- **`business_operations.procurement-sourcing` — SAME FIXTURE BYTES:**
  `Packing-List_PO-7714.xlsx`. Logistics wins for package-level custody, carrier handover and
  origin/destination; Business Operations wins for sourcing, award or purchase support. A PO
  reference does not make a completed shipment.
- **`retail_hospitality.supplier-order` — SAME FIXTURE BYTES:**
  `Packing-List_PO-7714.xlsx`. Logistics wins for the carrier movement; Retail/Hospitality wins for
  supplier order and replenishment workflow. A packing list alone cannot decide whether the buyer's
  order or the carrier custody is central.
- **`manufacturing.production-record` — SAME FIXTURE BYTES:**
  `Goods-Received_NCR-118.pdf`. Logistics wins for handover, package condition or delivery exception;
  Manufacturing wins for incoming lot/part disposition and production-control status. A consignment
  reference does not convert an NCR into a POD.
- **`resource_operations.fisheries-catch` — SAME FIXTURE BYTES:**
  `Fish-Transport-Document_Lot-L-771.pdf`. Logistics wins for post-landing vehicle, seal, destination
  and consignment custody; Fisheries wins when the same bytes are retained in an originating vessel,
  trip, landing and catch reconciliation. Transport weight is not catch by default.
- **`logistics.route-dispatch` — SAME FIXTURE BYTES:**
  `Driver-Run-Sheet_2026-04-11.ics`. Shipment wins for actual consignment collection/delivery and
  custody; route-dispatch wins for a working-day plan of driver, vehicle, ordered stops and run
  performance. A calendar booking proves neither completed shipment nor route execution.
- **`logistics.last-mile-pod` — SAME FIXTURE BYTES:**
  `POD_Consignment-CN-4021.jpg`. Shipment wins for the whole movement; last-mile-POD wins when
  doorstep proof, recipient/attempt status and final-mile exception are central. A signature or camera
  location alone cannot choose the scope.
- **`logistics.customs-export` — SAME FIXTURE BYTES:**
  `Export-Declaration_MRN-7781.xml`. Shipment wins when customs is one member of a movement dossier;
  customs-export wins when declaration, classification, declarant and release/compliance status are
  central. A movement reference does not prove physical delivery.
- **`logistics.fleet-vehicle` — SAME FIXTURE BYTES:**
  `Driver-Run-Sheet_2026-04-11.ics`. Shipment wins for consignment/drop sequence and goods custody;
  fleet-vehicle wins for vehicle identity, licensing, inspection, maintenance or operator records.
  A vehicle/driver name in a route plan is not a fleet lifecycle record.
- **`manufacturing.tooling-fixture` — SAME FIXTURE BYTES:**
  `Tooling-Shipping-Manifest_T-2048.pdf`. Shipment wins for crate, carrier, seal, destination and
  post-dispatch movement; tooling wins when tool condition, receiving acceptance and life history are
  central. Tracking is not tool acceptance.

## Neighbours considered but not edged

- **Business Operations generally** — procurement, vendor and contract records can contain carrier,
  supplier and delivery references. The specific procurement-sourcing edge is sufficient; a broad
  business edge would mutex every commercial shipment.
- **Retail/Hospitality generally** — supplier ordering, e-commerce and returns can contain packing
  and delivery documents. `retail_hospitality.supplier-order` is the sharper buyer-side boundary;
  customer-service or store records are not direct same-evidence collisions here.
- **Manufacturing generally** — receiving and tooling records overlap movement. The specific
  production-record and tooling edges capture the fixtures; a generic manufacturing edge would make
  all inbound goods mutually exclusive with Logistics.
- **`logistics.warehouse-ops`** — considered for goods-in, put-away and pick records. No warehouse
  fixture was required beyond `Goods-Received_NCR-118.pdf`; a warehouse population row is distinct
  unless custody in the depot is the central evidence.
- **`logistics.driver-compliance`** — considered for driver hours and entitlement. The run-sheet
  fixture carries a planned driver role but no compliance record; fleet/route boundaries are sharper.
- **Finance** — freight invoices, duties and declared values can be coactivated, but no finance edge
  is added because the custody fixture is the discriminating object and an invoice alone is rejected.

## Files considered and rejected from activation

- **Freight invoice, purchase order or quote** — commercial transaction; no custody handover or
  delivered goods structure.
- **Carrier tracking number or status-only export** — useful retrieval clue, but no goods/party role or
  independent acknowledgement; remains Review Later unless joined to a bounded consignment dossier.
- **Standalone address or delivery appointment** — addresses have multiple roles and appointments are
  plans, not completed movement.
- **Packing list with prices, tax and order totals** — may be Procurement/Retail or Finance; package
  rows alone do not prove carrier custody.
- **Customs policy, tariff publication or government case** — Government/customs context without
  physical movement; a declaration inside a movement packet is the narrower collision case.
- **Vehicle licence, tachograph or driver-hours record** — Fleet/driver compliance, not one goods
  consignment.
- **Pallet, seal or doorstep photograph without own reference** — Photos or Review Later; EXIF,
  barcode and signature-like marks are not sufficient.
- **Warehouse put-away or cycle-count report** — Warehouse operations unless it also documents a
  consignment handover with goods and acknowledgement.
- **Unreadable/encrypted shipping archive** — Unsupported or Encrypted; filename and extension cannot
  rescue a missing custody structure.

## Intended coactivation for R1c (not authored in JSON)

The template deliberately leaves `also_holds_with` empty. A packing list, customs declaration,
goods-received note or fish transport document may independently support Business Operations,
Retail/Hospitality, Government, Manufacturing or Fisheries alongside Logistics. R1c should decide
whether P9 grouping and per-file `also_schema` observations are sufficient or whether a future
schema-level relationship is warranted. A shared address, carrier, PO, species or tracking token is
not enough; each schema needs its own role-bearing evidence.

## NEEDS-JOSEPH

1. **NJ-LOG-SHIP-1 — field identity and dimensions.** Should this row reuse the logistics proposals
   `consignment`, `carrier`, `asset`, `site` and `record_type`, and should carrier be destination-
   eligible or only a role/search facet? The useful projection is context → consignment → record type,
   but PR-6 prevents local field decisions.
2. **NJ-LOG-SHIP-2 — sibling split.** Should one consignment dossier remain distinct from last-mile
   POD, customs-export and route-dispatch when identical submitted bytes occur in each workflow, or
   should custody role select one mutex template? The answer must preserve both evidence and role.
3. **NJ-LOG-SHIP-3 — receiving and order coactivation.** Packing lists and goods-received files can
   support Manufacturing, Retail/Hospitality and Business Operations as well as Logistics. Should P9
   represent that coactivation, or must a user choose a custody owner before placement? This template
   authors no `also_holds_with` edge.
4. **NJ-LOG-SHIP-4 — customs and carrier custody.** When a customs declaration is submitted by a
   broker or carrier, which party's role is authoritative for the Logistics versus Government /
   customs template? A declaration reference alone cannot answer this.
5. **NJ-LOG-SHIP-5 — validation catalogues.** R2/R4 must settle deployment-specific consignment,
   container, vehicle, customs and carrier identifiers. No regex, tariff code, jurisdiction or legal
   deadline is asserted here.

## Self-verification

- Both assigned paths were absent before authoring and are the only paths added by this task.
- JSON parses with `python3 -m json.tool` after authoring.
- Every fixture source type is in the exact fourteen-member `SOURCE_TYPES` vocabulary.
- `fields`, `proposed_fields` and `template.dimension_order` are empty under PR-6; no local field is
  minted.
- Every collision is exactly `{domain, signal, provenance}`; every signal names `SAME FIXTURE BYTES`
  and explains both directions.
- `also_holds_with` has no entries; intended coactivation is recorded here for R1c only.
- Collision endpoints are roster-valid and residual destinations use the named residual library.
- The two quoted design sentences were checked byte-for-byte against `00`; no fabricated quote is
  used.
- Final scoped whitespace/diff and repository-status checks are required before handoff.
