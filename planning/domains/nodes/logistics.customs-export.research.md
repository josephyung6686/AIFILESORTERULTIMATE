# Customs, export and trade compliance — R1b research memo

**Depth: J-DEPTH**

## Scope and authority

This memo owns only `logistics.customs-export`. The stamped assignment identifies a `kind: template`
on `schema_id: logistics`; `parent_id` is null and browse-only. The logistics anchor is a PR-6
placeholder schema with `fields: []` and proposed `consignment`, `carrier`, `asset`, `site` and
`record_type` keys awaiting R1c. This template does not copy or mint fields: its JSON has empty
`fields`, empty `proposed_fields`, and an empty serialized dimension order. The conditional customs
recommendation is retained in prose for R1c.

Sources read before writing were:

- `planning/domains/dispatch/RESEARCH-BRIEF.md` and the stamped output of
  `python3 planning/domains/dispatch/make_prompt.py logistics.customs-export`;
- `planning/prompts/ALIGNMENT.md`, `planning/00-database-agent-product-design.md`,
  `planning/01-product-design-structured.md`, `planning/domains/_CONTRACT.md`, and
  `planning/domains/CONNECTION.md`;
- `planning/domains/roster.json`, `planning/domains/canonical_fields.json`, and
  `src/evidence_shape/vocabulary.py`;
- `planning/domains/nodes/logistics.json` as the schema anchor and landed
  `identity.core-documents` exemplar for depth, privacy and edge discipline;
- landed logistics shipment, fleet, driver and warehouse siblings for boundaries and JSON idiom.

The design does not name customs/export as an independent schema or template. This row is a
proposal extending the named Logistics situation. The following quotations from
`planning/00-database-agent-product-design.md` were checked verbatim:

- “Every file will be treated as a record with many facts, rather than forcing it into one
  permanent category.”
- “The engine should treat the file extension as a routing signal rather than an assumption about
  meaning,”
- “Archives should be inspected without being unpacked to disk.”
- “A session should never be treated as proof of topic, and it should not carry the same
  confidence as a hash match or a directly extracted document fact.”
- “For document and record domains, project, function, or subject usually comes before time
  because putting year first scatters related work across calendar folders.”
- “Independent Records may live under Personal/Independent Records and hold standalone
  certificates, notices, confirmations, forms, and PDFs that have a durable purpose but no broader
  group.”
- “Review Later may hold files whose meaning is partly understood but whose final location requires
  a future decision.”
- “Protected Records may represent sensitive isolated material such as passport scans, medical
  documents, account statements, visas, legal forms, or credentials; it should normally remain
  local-only and must not cause filenames or content to be exposed in model prompts.”

The customs-specific structures, context vocabulary and cross-domain boundaries below are
inferences from the logistics anchor and named record forms, not claims that `00` names a customs
catalogue.

## Node test

The row is retained provisionally because its evidence, recommendation and privacy posture differ
from the logistics default.

**Signals.** The anchor recognizes goods in custody: consignor/consignee/carrier roles, quantity,
places, times and acknowledgement, plus fleet, dispatch and warehouse records. Customs/export
requires an authority-facing control relation: one movement or consignment is joined to declarant,
importer/exporter, commodity classification, origin, customs procedure, valuation, licence or
preference evidence and a hold/release status. A bill of lading, commercial invoice, packing list,
country name, port or customs word alone cannot activate it.

**Dimensions.** The logistics default is carrier or counterparty -> consignment/container ->
record_type, with vehicle, depot or working-day variants. Customs is consignment/movement-led ->
record_type, with carrier or site optional only where explicit and useful. Declarant/importer/
exporter roles, jurisdiction, commodity code, origin, procedure, duty and release status are values
or search evidence. Jurisdiction is not a field. Since the anchor has no legal fields at launch, the
JSON stores no dimensions.

**Privacy.** Declarations expose tax registrations, importer/exporter identities, product
composition, tariff strategy, declared values, origin suppliers, controlled-goods destinations,
licences and trade routes. This is concentrated commercial and regulatory exposure, so the template
is `potentially_sensitive`; no P7 handling class is assigned and no identifier, value, origin or
route becomes a default destination dimension.

The strongest objection is that a customs declaration is just another shipment `record_type`. The
row survives because declaration/control evidence governs permission, duty, export control and
release, while ordinary shipment evidence governs custody and movement. The same packet may carry
both perspectives on disjoint sections. If a corpus has only transport documents, purchase invoices
or generic border vocabulary with no declaration/control structure, the row should be refused and
those files should remain with shipment, procurement or a residual.

## Bottom-up file set

The JSON records fourteen concrete files. `observations` are raw evidence; `facts_legal` is limited
to universal facts because the logistics schema's domain fields are deferred. Customs values and
roles are not silently asserted. A screenshot, email, calendar entry or scan can join an accepted
movement group but does not inherit its consignment, origin or classification facts.

### Declarations, classification and origin

* `Export-Declaration_MRN-GB-2026-0411.pdf` (`text_document`, `.pdf`) contains labelled movement
  reference, exporter/importer/declarant roles, commodity lines, classification, origin, procedure,
  declared value and release status. It is the strongest native declaration anchor. The filename does
  not prove any of those values, and the declarant is not automatically the exporter or carrier.

* `Import-Entry-Summary_MRN-2026-0411.xlsx` (`spreadsheet`, `.xlsx`) separates entry reference,
  importer of record, procedure, tariff code, origin, customs value, duty/tax calculations, broker
  fees, release and amendment status. It may also carry Finance facts, but a monetary cell is not a
  finance account fact by itself.

* `Certificate-of-Origin_CO-7741.pdf` (`text_document`, `.pdf`) labels exporter, consignee, goods,
  origin criterion and attesting issuer, with invoice/movement reference. It is origin evidence but
  not itself a customs release; an attestation does not prove authenticity beyond its own role.

* `HS-Classification-Ruling_8481.80.pdf` (`text_document`, `.pdf`) identifies goods, classification
  rationale, issuing authority reference, effective scope and product characteristics. It does not
  describe one delivery event; the number in the filename is not enough to activate customs.

* `Export-Licence-and-End-User-Statement.docx` (`text_document`, `.docx`) labels exporter, controlled
  goods, destination, end user, licence conditions and validity. This is an export-control candidate
  only with its movement/control relation; a business licence or unrelated government permit is a
  false positive.

### Broker, movement and warehouse records

* `Customs-Broker-Entry-Confirmation.eml` (`email`, `.eml`) has movement reference, broker and
  importer roles, commodity lines, duty estimate, requested documents and declaration/origin
  attachments. A draft instruction is not an accepted declaration. Email addresses and contents are
  potentially sensitive.

* `Customs-Portal-Release-Screenshot.png` (`image`, `.png`) shows a portal status panel with partial
  movement reference, release state and authority heading; commodity, origin and declarant fields
  are obscured. Pixels and screen metadata do not prove release authenticity, and absent EXIF does
  not prove screenshot origin.

* `Scanned-Customs-Declaration_MRN-2026-0411.pdf` (`ocr`, `.pdf`) yields partial declarant, procedure,
  origin and release headings plus stamps and handwritten amendments; movement and tariff identifiers
  are unreadable. OCR is possible evidence, not direct evidence for unreadable fields.

* `Customs-Entry-Packet_MRN-2026-0411.zip` (`archive`, `.zip`) has a manifest listing declaration,
  invoice, packing list, origin certificate, export licence and broker release email, including an
  amendment and original. It is not unpacked. No one status or origin fact is copied to every member.

* `Customs-Commodity-Lines_MRN-2026-0411.xml` (`code_structured`, `.xml`) contains structured party
  qualifiers, declaration reference, goods lines, procedure, origin, value, duty and release codes.
  XML is only a format clue; each code needs its labelled role.

* `Warehouse-Import-Receipt-and-Customs-Hold.xlsx` (`spreadsheet`, `.xlsx`) records pallets, bins,
  quantities and receipt times, with hold/release columns referencing a movement but no tariff,
  origin or declarant fields. Warehouse custody is the principal reading; a hold word alone is not
  customs activation.

* `Border-Inspection-Appointment.ics` (`calendar`, `.ics`) proposes a border inspection with
  organizer, location, attendees and recurrence metadata but no declaration or result. Calendar
  source type and title are never-alone clues.

### Commercial and collision fixtures

* `Commercial-Invoice-and-Packing-List_INV-7741.pdf` (`text_document`, `.pdf`) combines goods,
  packages, weight, price, origin and incoterm around a consignment but contains no declaration
  reference or authority status. It can be shipment/procurement/finance evidence and may support
  customs only when the declaration/control relation is independently present.

* `Import-Purchase-Order-and-Duty-Estimate.pdf` (`text_document`, `.pdf`) contains buyer/supplier,
  goods, price and delivery terms, with a duty estimate based on a commodity code but no authority
  reference, declaration or release. It belongs to procurement or Finance unless customs evidence is
  separately established.

The set covers labelled forms, ambiguous prose and invoices, native text, spreadsheets,
structured-data, email, calendar, archive, image and OCR. Contact exports have no legitimate role in
this template: `.vcf` remains privacy-protected contact material. Presentation, audio/video or
opaque broker databases may join a movement group, but source type alone never activates customs.

## Recognition and abstention

Deterministic recognition uses clusters: movement reference plus party roles, classification, origin,
procedure, value and authority status; licence plus controlled goods/end user; origin certificate
plus goods and movement; ruling plus classification rationale; or hold/release plus declaration
reference. Archive recognition uses its manifest only. A declaration's exact values remain direct or
validated only when labelled slots and rule families support them; no regex, gazetteer or threshold is
invented here.

The `needs_llm` cases are bounded: ambiguous broker prose, invoices without declaration references,
classification versus product codes, export licence semantics, hold/release custody, OCR-poor boxes
and mixed archives. The model receives a compact cited evidence packet after deterministic routing
and must return unknown where authority, role or movement cannot be settled.

The `never_alone` list blocks customs words, country names, ports, tariff-like codes, movement and
container identifiers, authority names, stamps, status words, source types, parent folders, sessions
and invoices. A shipping waybill, purchase order, manufacturing lot record, warehouse hold or
government case may contain all of those tokens. The authority-facing declaration relation is the
discriminator.

## Conditional dimensions and field restraint

`proposed_fields` is intentionally empty. No `customs_movement`, `jurisdiction`, `tariff_code`,
`origin`, `declarant` or `duty` key is minted. Jurisdiction is a value; tariff, origin and status are
record values/search evidence; party roles are not safe collector dimensions. The anchor's
`consignment`, `carrier`, `site` and `record_type` proposals may be reused only after R1c adjudication.

If licensed, the useful order is:

`consignment or movement -> record_type`,

with carrier or site optional only where explicitly tied to the movement and genuinely improving
retrieval. A carrier folder must not collect unrelated customs cases, and a declarant/importer/
exporter folder could expose identity or organization relationships. Time is a leaf for a declaration
series, amendment or post-clearance case, not the leading branch.

## Reciprocal boundaries and collision fixtures

The JSON authors eight same-kind `collides_with` edges. Every item is exactly `{domain, signal,
provenance}`; no bare string, `domain_id`, `id`, `target` or `why` key appears. Every signal explains
both directions and contains `SAME FIXTURE BYTES:` plus a concrete filename. All are
`provenance: inference`, because `00` does not name customs templates. R1c must reconcile reciprocal
edges; adjacent rows may not yet name this newly landed node.

1. **Logistics shipment — `Commercial-Invoice-Packing-List-Bill-of-Lading-and-Customs-Entry.pdf`.**
   Customs owns authority-facing declaration, classification, origin, procedure, value and release;
   shipment owns carrier/party custody, packages, places, vessel and acknowledgement. Port,
   container, commodity or movement number alone decides neither.

2. **Logistics warehouse operations — `Bonded-Warehouse-Entry-and-Customs-Release.xlsx`.** Customs
   owns procedure, hold/release and declaration; warehouse operations owns pallets, bins, quantities,
   receipt, quarantine and physical movements. A bonded location or hold word alone decides neither.

3. **Business corporate regulatory filings — `Annual-Customs-Declaration-and-Compliance-Submission.xlsx`.
   ** Customs owns goods lines, origin, procedure, value, duty and clearance; business operations owns
   obligation, deadline, approval, declaration-control, acknowledgement and penalty trail. A period,
   authority or submission reference alone decides neither.

4. **Business procurement/sourcing — `Import-Purchase-Order-and-Customs-Dossier.pdf`.** Customs owns
   authority-facing declaration, origin, classification, valuation and release; procurement owns
   supplier selection, purchase award, landed-cost comparison and buying approvals. Supplier, price,
   country or commodity code alone decides neither.

5. **Retail/hospitality supplier order — `Restaurant-Import-Customs-and-Supplier-Order.pdf`.**
   Customs owns declaration, origin, tariff, duty and clearance; supplier-order owns hospitality
   buyer order, supplier confirmation, ordered quantities, delivery window and receipt. Food,
   supplier, country or delivery vocabulary alone decides neither.

6. **Manufacturing production record — `Export-Lot-Customs-Packet.pdf`.** Customs owns movement,
   export control, tariff/origin and exit evidence; production owns product/lot genealogy, process
   execution, inspection and manufacturing release. Lot, product code, package or export word alone
   decides neither.

7. **Manufacturing supplier qualification — `Supplier-Origin-Certificate-and-Qualification-Review.pdf`.
   ** Customs owns movement-specific origin and export-control evidence; supplier qualification owns
   supplier capability, approval scope, audit and status. Supplier name, certificate or country alone
   decides neither.

8. **Business contract administration — `Broker-Agreement-and-Customs-Entry-Dispute-Pack.pdf`.**
   Customs owns movement declaration, licence, duty and release; contract administration owns the
   freight, broker or supply agreement's clauses, notices, fees, variations, indemnities, disputes
   and obligation tracking. A signed agreement or broker fee alone decides neither.

## Intended coactivation for R1c (not authored as an edge)

R1c should consider independent coactivation for the same fixture bytes:

- an import entry summary can carry customs declaration facts and Finance duty/account evidence;
- a commercial invoice and packing list can carry shipment custody, procurement and customs support
  when a declaration reference and authority status are present;
- a supplier-origin certificate can carry customs origin evidence and supplier qualification;
- an export lot packet can carry customs exit evidence and manufacturing product/lot genealogy;
- a warehouse customs-hold workbook can carry customs procedure evidence and physical warehouse
  custody rows;
- a portal screenshot or scan can carry image/OCR facts while joining the movement group through
  cited anchors.

This is memo guidance for R1c. `also_holds_with` stays empty because this row is a template and the
closed edge vocabulary restricts that relation to schemas. Group membership cannot copy a movement,
origin, tariff or release fact onto a sparse file.

## Neighbours considered but not edged

`logistics.route-dispatch` was considered for border run sheets and driver arrival times. Its subject
is a working day, vehicle, driver and ordered stops; customs owns declaration/control evidence. The
shipment and warehouse edges are sharper for the actual goods packet.

`logistics.last-mile-pod` was considered for delivery and refusal records after clearance. Proof of
delivery and last-mile exceptions are custody/acknowledgement evidence; a customs release is a
separate authority event. No broad collision edge is needed without a same-file fixture.

`business_operations.vendor-management` was considered for broker and supplier relationships. A
broker or supplier master, performance review or contract is business administration; a movement's
declaration and release are customs. Procurement/sourcing and contract administration cover the
sharper commercial seams.

`retail_hospitality.premises-licensing` was considered because import licences and food permits can
appear in hospitality packets. Premises licensing concerns a venue's operating permission; customs
concerns goods crossing a border. Supplier-order is the more concrete assigned retail collision.

`manufacturing.quality-management-system` was considered for certificates, origin and supplier
quality records. QMS owns system-wide quality governance; customs owns movement-specific authority
and trade-control evidence. Supplier qualification and production record provide the narrower
fixtures.

`government.permit-licensing` and `government.public-authority-record` were considered for customs
authority copies. Government owns issuer-side administration, assessment and enforcement; this row
owns the holder/broker movement dossier. The assigned business and logistics collisions are enough
for this template, and R1c should add a government edge if a reciprocal fixture lands.

## Residual routing and safety

The JSON routes five residual cases. Isolated broker confirmations, duty payments and clearance
emails go to Receipts and Confirmations. Standalone certificates, licences, rulings or notices go to
Independent Records. Ambiguous invoices, drafts, screenshots, OCR scans and mixed packets go to
Review Later. Unreadable portals and protected archives go to Unsupported or Encrypted. Declared
values, tax identifiers, licences and controlled-goods routes may go to Protected Records when no
safe accepted movement group exists. These are residual homes, not additional customs categories.

## Proposed fields, refusal and NEEDS-JOSEPH

`proposed_fields` is `[]`; no canonical field is added or respelled. The row is not refused, but is
conditional. R1c should refuse it if real corpora show only waybills, invoices, packing lists or
generic border vocabulary without a declaration/control relation; shipment, procurement, Finance and
residuals cover that evidence honestly.

NEEDS-JOSEPH items for this node:

- **NJ-CUSTOMS-1:** Should `consignment` remain the sole safe customs parent, or should R1c license a
  neutral movement/case field distinct from shipment custody? A private `customs_movement` key is
  not minted here.
- **NJ-CUSTOMS-2:** Should declarant/importer/exporter roles remain search-only because they can
  become organization/identity collectors, or may user-approved branches expose one role for
  retrieval?
- **NJ-CUSTOMS-3:** When one packet contains customs declaration, shipment custody, purchase order
  and manufacturing lot evidence, should all schemas coactivate independently on disjoint sections,
  or should user policy select one packet owner?

## Self-verification

Both target paths were absent before writing and remain the only paths edited for this assignment;
no commit was made. The JSON parses with `python3 -m json.tool`. It contains fourteen examples; all
example and file-kind source types are in the exact vocabulary in `src/evidence_shape/vocabulary.py`;
all eight collision domains resolve to roster endpoints; each collision object has exactly
`domain`, `signal`, `provenance`, and every signal includes both directions plus `SAME FIXTURE BYTES`.
`fields`, `proposed_fields`, `template.dimension_order` and `also_holds_with` are empty. Residuals
use only the nine named homes. The eight quoted design spans were checked verbatim after whitespace
normalization. No thresholds, handling classes, bare collision strings, fabricated design
quotations, private field keys or paths-as-facts were added.
