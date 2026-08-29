# logistics.last-mile-pod — R1b lab notes

Date: 2026-08-27
Roster row: `kind: template` · `schema_id: logistics` · `launch: placeholder`
Legacy coverage: `delivery.proof-of-delivery` (ROW)

## Verdict

**Keep provisionally; do not refuse.** This row is the final handover situation for one parcel or
consignment: delivery or attempted-delivery event, recipient/safe-place outcome, event time and
place, signature/scan/PIN/photo proof, package condition and exception or return status. A doorstep
photograph, address, tracking number, signature or delivery appointment alone is not enough.

The strongest refusal charge is that the `logistics` schema and `logistics.shipment` already cover
consignments, carrier status, delivery receipts and claims. That charge would win if this row only
renamed proof-of-delivery as a work type. It survives narrowly because last-mile evidence has a
different decisive relation: a final stop's recipient or safe-place outcome and event proof, often
captured by a driver app, signature/PIN, geofence or doorstep image. The upstream consignment dossier
can remain broad; this row makes the final handover leg reviewable even when the origin, customs and
full carrier chain are absent. R1c should refuse if a complete shipment template already owns all
final-mile-specific evidence and no distinct privacy or dimension rule remains.

No field or executable dimension is authored. D1/PR-6 leave logistics proposals undecided, and this
template does not copy or mint them. No template-level `also_holds_with` is authored; the intended
coactivation questions are recorded for R1c.

## Authority stack and method

Repository material read:

- `planning/domains/dispatch/RESEARCH-BRIEF.md`, including full J-DEPTH.
- Complete stamped output of `python3 planning/domains/dispatch/make_prompt.py logistics.last-mile-pod`.
- `planning/prompts/ALIGNMENT.md` and authoritative `planning/00-database-agent-product-design.md`.
- `planning/domains/_CONTRACT.md`, `planning/domains/CONNECTION.md` and
  `planning/domains/CONNECTION-EXAMPLES.md` for node testing, fact/observation separation,
  grouping, residuals and closed edge shape.
- `planning/domains/roster.json`, `planning/domains/ROSTER.md`,
  `planning/domains/canonical_fields.json`, and `src/evidence_shape/vocabulary.py`.
- `planning/overnight/council/DECISION-BRIEF.md` for D1–D6, J-IND and J-DEPTH.
- Logistics schema anchor `logistics.json` and memo, `logistics.shipment` where available, and the
  landed-depth `identity.core-documents` pair for archive/OCR/privacy idiom.
- Existing same-kind boundaries: `logistics.shipment`, `logistics.route-dispatch`,
  `logistics.fleet-vehicle`, `retail_hospitality.returns-warranty`,
  `business_operations.customer-account-management`, `manufacturing.production-record`, and
  `photos.scanned-documents`. No other node was edited.

Official sources verify recurring final-mile record structures only; they do not license product
fields, recipient identity, location inference, delivery validity or legal conclusions:

- [GOV.UK — Transport documentation](https://www.gov.uk/government/publications/how-to-trace-weigh-and-distribute-fish-products/transport-documentation)
  distinguishes a transport document from a landing declaration and describes destination, seals,
  receipts and movement after landing. It supports the custody/receipt boundary.
- [UNECE — CMR consignment notes](https://unece.org/DAM/trans/doc/2019/wp24/III.2_CMR_ECMR_RH_30Oct2019.pdf)
  describes a consignment note as evidence of carriage and a basis for loss or delay claims. It
  supports the upstream shipment collision without making a signature alone proof of final delivery.
- [GOV.UK — Goods vehicle operator licensing guide](https://www.gov.uk/guidance/goods-vehicle-operator-licensing-guide)
  distinguishes vehicle/driver compliance and maintenance records from shipment handover evidence.
- [GOV.UK — Drivers' hours and tachographs](https://www.gov.uk/guidance/drivers-hours-goods-vehicles/4-tachograph-rules)
  describes driver activity and vehicle telemetry records, grounding the fleet/route boundary.

No external source is represented as product-design authority. No geofence radius, delivery deadline,
recipient-resolution rule, carrier API schema or identifier regex is embedded here.

## J-DEPTH node test — all three legs

### Leg 1 — detection differs from the logistics default

The logistics schema describes goods in custody, including consignments, proof of delivery, vehicle,
driver, dispatch, depot and customs records. A child row must not simply collect all delivery words.
Its positive evidence must connect one parcel/consignment to a final-mile attempt or handover and an
acknowledgement/outcome: recipient or safe-place status, delivery event, signature/PIN/scan/photo,
and package condition or exception where applicable.

That relation is present in a completed driver-app JSON, signed receipt, locker release, safe-place
email, damage-at-door report and bounded POD archive. A carrier status export without final-mile
semantics can join a group but does not activate alone. A calendar appointment is a plan. A doorstep
image with a barcode but no event reference is a photograph. The discriminating object is the final
handover event, not an extension or the word POD.

### Leg 2 — recommended dimensions differ from the schema default

The schema's default spans shipment, customs, fleet, route, warehouse and POD situations. Conditional
on R1c promoting schema proposals, this row's useful order is **consignment/parcel → delivery event
or record type**, with route or collection point only when that is the subject. Recipient names,
addresses, coordinates, safe-place details and driver identity are not default dimensions: they are
privacy-sensitive roles and can be stale, shared or wrong.

`dimension_order` is therefore empty. The schema declares no legal fields, and this row does not mint
`parcel`, `recipient`, `delivery_event`, `geofence` or `attempt_status`. It is not time-first. The
exact design sentence is, “For document and record domains, project, function, or subject usually
comes before time because putting year first scatters related work across calendar folders.” The
parcel or consignment makes its attempt and proof documents intelligible; timestamps remain evidence
of events rather than path levels.

### Leg 3 — privacy and security differ from the default

Last-mile records concentrate home/work addresses, names, signatures, PINs, doorstep images,
geolocation, delivery schedules, safe-place instructions, driver identifiers and package contents.
They can reveal a person's routine or a business's inventory and access points. The row is therefore
`potentially_sensitive`; P7 owns handling classes, redaction and local/cloud policy.

Custody and purpose are also ambiguous. The same POD may be kept by a carrier, retailer, marketplace,
recipient, returns team, warehouse or customer-service system. A delivery image may be Photos, a
damage exhibit or a final-mile proof. Grouping can retrieve a bounded packet but must not copy parcel,
recipient, address or delivery facts from an anchor to sparse members.

### Node-test conclusion

Keep only as a narrow and reversible final-handover template. R1c should refuse if all final-mile
proof is already a record type under `logistics.shipment`, and no distinct final-event recognition,
dimension or privacy rule survives.

## Bottom-up file corpus

The JSON carries thirteen concrete fixtures. Since logistics is field-less, positive files list only
universal facts; parcel, consignment, recipient, carrier and event conclusions remain observations or
R1c proposals.

1. **`POD_Consignment-CN-4021.jpg`** (`image`) — doorstep parcel, app overlay, partial reference and
   camera EXIF; exact recipient/status/address are not fully legible. EXIF is camera evidence, not
   delivery location or acceptance.
2. **`Driver-App-Completed_CN-4021.json`** (`code_structured`) — parcel, route stop, event time,
   status, recipient/driver scan state, location evidence and exception code. It has no embedded photo,
   so package condition remains unknown.
3. **`Recipient-Signature_CN-4021.pdf`** (`text_document`) — parcel reference, delivered time/place,
   recipient role, package count, signature, status and damage/shortage boxes. Signature authenticity
   and ownership remain unproved.
4. **`Failed-Attempt_CN-4021.eml`** (`email`) — native message fields, attempt reason, reattempt
   window and collection-point instruction. It proves a message/workflow, not a later delivery.
5. **`Locker-Release_CN-4021.csv`** (`spreadsheet`) — locker/collection point, release scan, code
   status, pickup time and collection state. A code alone does not identify a recipient.
6. **`Damage-at-Door_CN-4021.pdf`** (`text_document`) — final-handover package condition, seal,
   shortage, photo references and separate claim status. Allegation and carrier liability remain
   distinct.
7. **`Scanned-POD_CN-4021.pdf`** (`ocr`) — OCR-poor parcel reference, recipient/attempt labels,
   date, signature and partial safe-place note. Scanner metadata is not custody evidence.
8. **`Last-Mile-Events_CN-4021.csv`** (`spreadsheet`) — many parcel rows with stop sequence,
   attempt/delivery/return events, timestamps, geofences and exception codes. One row's facts never
   propagate to another.
9. **`Delivery-Archive_CN-4021.zip`** (`archive`) — manifest of label, route event, doorstep image,
   signature, failed attempt and damage claim; inspected without unpacking and no member facts copied.
10. **`Delivery-Appointment_CN-4021.ics`** (`calendar`) — planned window and address with organizer,
    attendee and times. It is not a completed handover.
11. **`Parcel-Return-Label_CN-4021.pdf`** (`text_document`) — carrier, parcel, origin/destination
    and barcode prepared for return. It does not prove a failed attempt or actual return.
12. **`Pallet-At-Warehouse.jpg`** (`image`) — carrier label and pallet in a warehouse, with EXIF but
    no final recipient or delivery event. This is a One-Off Image unless joined by own evidence.
13. **`Shipment-Status-Screenshot_CN-4021.png`** (`image`) — OCR-visible carrier status page with
    parcel reference, attempted/delivered wording and a clipped timestamp, but no recipient or
    acknowledgement. It can support Temporary Screenshots or Review Later; the screenshot itself is
    not a completed POD.

The set covers labelled forms, native structured payloads, email/calendar, OCR scans, photographs,
screenshots, archives, sparse route data, locker and safe-place outcomes, claims and cross-domain
returns/manufacturing/Photos cases.

## Collisions and reciprocal boundaries

Every JSON collision uses exactly `{domain, signal, provenance}`. Each signal names the same fixture
bytes and explains both directions; R1c must land reciprocal edges or remove a pair:

- **`logistics.shipment` — SAME FIXTURE BYTES:** `Recipient-Signature_CN-4021.pdf`. This row wins
  when final-handover event, recipient/attempt status and delivery proof are central; shipment wins
  when the same bytes are one member of a full origin-to-destination consignment dossier. A signed
  page alone cannot establish the upstream movement.
- **`logistics.route-dispatch` — SAME FIXTURE BYTES:** `Delivery-Appointment_CN-4021.ics`. This row
  wins for completed final-mile proof; route-dispatch wins for planned driver/vehicle/stop sequence
  and run performance. An appointment alone proves neither execution nor receipt.
- **`logistics.fleet-vehicle` — SAME FIXTURE BYTES:** `Driver-App-Completed_CN-4021.json`. This row
  wins for parcel final-mile outcome; fleet-vehicle wins for vehicle/driver identity, licensing,
  telematics or operator compliance. A driver or vehicle identifier does not prove a delivery.
- **`retail_hospitality.returns-warranty` — SAME FIXTURE BYTES:** `Parcel-Return-Label_CN-4021.pdf`.
  This row wins for failed-delivery/refusal/return event; Retail/Hospitality wins for customer return
  authorization, refund/replacement and product disposition. A return label alone proves neither.
- **`business_operations.customer-account-management` — SAME FIXTURE BYTES:**
  `Failed-Attempt_CN-4021.eml`. This row wins for parcel attempt and delivery event; Business Operations
  wins for the customer complaint/service interaction when shipment is incidental. A recipient message
  alone cannot choose the workflow.
- **`manufacturing.production-record` — SAME FIXTURE BYTES:** `Damage-at-Door_CN-4021.pdf`. This row
  wins for final delivery condition and carrier handover; Manufacturing wins for incoming product/lot
  inspection or quarantine disposition. A condition note does not decide where damage occurred.
- **`photos.scanned-documents` — SAME FIXTURE BYTES:** `Scanned-POD_CN-4021.pdf`. This row wins when
  OCR recovers parcel, final-mile event and acknowledgement; Photos wins when the scan is retained as
  a document image without a delivery relation. OCR or a signature-like mark alone is insufficient.

## Neighbours considered but not edged

- **Business Operations generally** — customer service and complaints can contain delivery events;
  the specific customer-account edge captures this collision without making all correspondence a
  mutex.
- **Retail/Hospitality generally** — returns, refunds and order fulfilment overlap final-mile events;
  the specific returns-warranty fixture is enough.
- **Manufacturing generally** — incoming quality and transport damage share condition language; the
  production-record fixture captures that boundary.
- **`logistics.customs-export`** — customs declaration is upstream movement evidence, not final-mile
  proof unless a bounded packet separately carries the final event; no same-byte fixture was needed.
- **`logistics.warehouse-ops`** — warehouse receipt/put-away can precede last-mile delivery, but no
  recipient or final handover evidence is present in a warehouse-only record.
- **`logistics.driver-compliance`** — driver hours, tachograph and licence records are compliance
  dossiers; a driver-app delivery event is not automatically a driver-compliance file.
- **`photos.camera-events`** — doorstep photos may activate Photos on camera facts, but the final-mile
  POD relation is the sharper object; no broad image collision is added.

## Files considered and rejected from activation

- **Standalone doorstep, pallet or package photo** — Photos or One-Off Images; no parcel/event
  relation in the image's own evidence.
- **Tracking number or status-only export** — retrieval clue or Review Later until final-mile event,
  parcel identity and outcome are joined.
- **Address, delivery window or calendar booking** — plans and ambiguous roles, not completed receipt.
- **Signature, PIN, barcode or QR image** — generic acknowledgement artifact without parcel/event role.
- **Freight invoice, purchase order or order confirmation** — commercial transaction, not final handover.
- **Warehouse goods-in or manufacturing inspection** — another custody/quality event unless final
  delivery proof is independently present.
- **Return label alone** — prepared movement, not proof of failed delivery, recipient refusal or return.
- **Unreadable/encrypted archive or clipped screenshot** — Unsupported/Review Later; filename and
  extension cannot establish a POD.
- **Vehicle/driver/tachograph file** — Fleet/driver compliance; identity of the delivery actor is not
  evidence that a parcel was handed over.

## Intended coactivation for R1c (not authored in JSON)

The template deliberately leaves `also_holds_with` empty. A POD image or signature can independently
support Photos; a return label can support Retail/Hospitality; a failed-delivery message can support
Business Operations; an incoming damage form can support Manufacturing; and a full transport packet
can support `logistics.shipment`. R1c should decide whether P9 grouping and per-file `also_schema`
observations suffice or whether a schema-level relationship is warranted. Shared addresses, tracking
tokens, signatures or carrier brands are not enough for coactivation.

## NEEDS-JOSEPH

1. **NJ-LOG-POD-1 — field identity and dimensions.** Should this row reuse logistics' proposed
   `consignment`, `carrier`, `asset`, `site` and `record_type`, or is a neutral final-mile-event key
   required? The useful projection is consignment/parcel → delivery event/record type, but PR-6 blocks
   local field decisions.
2. **NJ-LOG-POD-2 — sibling split.** Should a signed or photographed POD be mutex with
   `logistics.shipment`, or may the same bytes activate both complete consignment and final-mile
   templates when their evidence roles are independently present?
3. **NJ-LOG-POD-3 — cross-schema coactivation.** Delivery images, return labels, failed-attempt emails
   and incoming-damage forms may support Photos, Retail/Hospitality, Business Operations and
   Manufacturing. Should P9 represent that coactivation, or must a user choose custody/purpose?
   This template authors no `also_holds_with` edge.
4. **NJ-LOG-POD-4 — recipient/address policy.** Which local policy governs redaction and whether
   recipient, address, PIN and geolocation observations may be shown in review surfaces? The catalogue
   sets only potentially_sensitive.
5. **NJ-LOG-POD-5 — validation catalogues.** R2/R4 must settle deployment-specific parcel,
   consignment, locker, geofence and carrier-event validation. No regex, address inference, legal
   delivery threshold or recipient identity is asserted here.

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
