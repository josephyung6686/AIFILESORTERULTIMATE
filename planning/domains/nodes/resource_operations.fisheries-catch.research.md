# resource_operations.fisheries-catch — R1b lab notes

Date: 2026-08-27
Roster row: `kind: template` · `schema_id: resource_operations` · `launch: placeholder`
Legacy coverage: `fish.catch-records` (ROW)

## Verdict

**Keep provisionally; do not refuse.** This is not a fishery-industry label and it is not a list of
document extensions. It is the operator-side **vessel/voyage → effort and area → species-level
catch → landing or transhipment → quota/compliance reconciliation** situation. The concrete records
below repeatedly join those roles. A species name, vessel number, quota word, landing port, map or
sales note by itself remains a clue or a different domain.

The strongest refusal charge is that the `resource_operations` schema already names fisheries,
vessels, quota, harvest/landing records and source-to-volume reconciliation. That charge is valid
if this row means only `technology = fishing` or a work-type list. It survives narrowly because its
positive files have a distinctive trip-centred evidence graph and a different provisional
projection: vessel and voyage context first, then record function, with species/stock and quota
usually searchable evidence rather than permanent folder levels. It also has a sharper privacy and
custody seam: an identical licence, observer report, catch certificate or transport document can be
operator-held, regulator-held or buyer-held. If R1c finds those distinctions are adequately handled
by the schema default and values, it should refuse this row and retain the residual fallthroughs.

The row intentionally writes no fields, no executable dimensions and no template-level coactivation
edge. D1/PR-6 leave the `resource_operations` schema field-less until R1c adjudicates its proposals;
the memo records the intended coactivation questions for R1c rather than minting local keys.

## Authority stack and sources used

Binding repository material read:

- `planning/domains/dispatch/RESEARCH-BRIEF.md`, including the ratified J-DEPTH requirement.
- The complete stamped output of `python3 planning/domains/dispatch/make_prompt.py resource_operations.fisheries-catch`.
- `planning/prompts/ALIGNMENT.md` and `planning/00-database-agent-product-design.md` (the latter
  wins when the prompt and alignment wording differ).
- `planning/domains/_CONTRACT.md`, `planning/domains/CONNECTION.md` and
  `planning/domains/CONNECTION-EXAMPLES.md` for node testing, grouping versus activation, the
  closed edge vocabulary, and the template/schema split.
- `planning/domains/roster.json`, `planning/domains/ROSTER.md`,
  `planning/domains/canonical_fields.json`, and `src/evidence_shape/vocabulary.py` for endpoint,
  canonical-key and exact `SOURCE_TYPES` checks.
- `planning/overnight/council/DECISION-BRIEF.md` for D1–D6, J-IND and J-DEPTH.
- The landed `resource_operations` schema JSON and memo for the broad operating-source anchor and
  its six R1c proposals.
- `identity.core-documents.json` and `identity.core-documents.research.md` as the landed
  launch-depth exemplar. No identity files or any other node files were edited.
- Existing same-kind neighbours were read as boundary references: `government.permit-licensing`,
  `government.environmental-regulation`, `business_operations.corporate-regulatory-filings`,
  `engineering.drawing-package`, and `logistics.shipment`.

Official sources were used only to verify that the named records and role combinations are real;
they do not license product fields, jurisdiction-specific detector patterns, quotas, thresholds or
legal conclusions:

- [FAO CWP — Logbooks and VMS](https://www.fao.org/cwp-on-fishery-statistics/handbook/capture-fisheries-statistics/logbooks-and-vms/en/)
  describes logbooks as catch-and-effort records and says they are normally integrated with
  landings declarations and sales notes. It also names vessel, trip, gear, landing port, quantity
  and landing/transhipment date as typical logbook entries.
- [Marine Management Organisation — Record your catch](https://www.gov.uk/guidance/record-your-catch)
  documents a real catch-record workflow for vessel owners and skippers, including trip details,
  live weight, species subject to limits, fishing area and submission timing.
- [GOV.UK — Fishing activity and landings data collection](https://www.gov.uk/guidance/fishing-activity-and-landings-data-collection-and-processing)
  distinguishes vessel-by-trip logbook data from landing declarations and describes cross-checks
  against satellite tracking, auction/merchant records and surveillance.
- [GOV.UK — ELSS reports](https://www.gov.uk/government/publications/how-to-report-fishing-activities-using-an-electronic-logbook-software-system/elss-reports)
  names departure, fishing activity, discards, catch-on-entry/exit, return-to-port, landing,
  transhipment and relocation reports, supporting the event vocabulary without making report codes
  sufficient on their own.
- [GOV.UK — Quota use statistics](https://www.gov.uk/government/statistical-data-sets/quota-use-statistics)
  shows weekly/monthly quota-uptake spreadsheets organized around allocations and catches/landings;
  the public table is also a counterexample to assuming that every quota workbook is operator-held.
- [GOV.UK — Transport documentation](https://www.gov.uk/government/publications/how-to-trace-weigh-and-distribute-fish-products/transport-documentation)
  distinguishes post-landing transport documents from landing declarations and catch records,
  supporting the logistics boundary.

No external source is quoted as product design. No jurisdiction's species-code list, area gazetteer,
vessel identifier grammar, reporting deadline or quota rule is embedded in the node.

## J-DEPTH node test — all three legs

### Leg 1 — detection signals differ from the schema default

The resource schema's default is an operator record joining an authorised source/site or authority,
an operating unit, measured output/environmental performance and a period. It deliberately covers
many physical-resource situations. A clean vessel track, licence, quota table, fish-market invoice
or environmental survey can therefore be relevant without proving fisheries catch.

This row adds a trip-centred relation: the same own-file evidence must connect a vessel to a voyage
or fishing operation, effort/area, species and retained/discarded quantity, and then to landing,
transhipment, quota uptake or an inspection/reconciliation outcome. A logbook with vessel, trip,
gear, area, species and quantity is positive. A VMS export with only position/time is not. A quota
ledger with allocation and remaining balance is not actual catch without a vessel/catch/landing
join. A transport document may cite the originating vessel and landing but remains Logistics unless
its own bytes are part of the operator's catch chain. The distinction is relational, not a work-type
word or file extension.

### Leg 2 — recommended dimensions differ from the schema default

The anchor memo's provisional schema order is `site → operating_authority → output_stream →
reporting_period → record_type`, with an asset-led alternative. For this row, a useful future
projection is **operating/landing context → vessel or asset → voyage/period → record type**. A
species/stock or quota dimension may be offered only when a corpus has multiple stable values that
improve retrieval; species, weight, area coordinates and gear remain content/search evidence by
default. A licence or quota identifier should not be forced into every branch because the same
voyage can involve multiple entitlements and because issuer-side custody is ambiguous.

`dimension_order` is therefore `[]` in JSON. The schema declares no legal fields, and writing
`vessel`, `voyage`, `species` or `landing_port` as local proposals would reverse PR-6. This is not
time-first. The design's exact applicable sentence is: “For document and record domains, project,
function, or subject usually comes before time because putting year first scatters related work
across calendar folders.” A voyage/record-function parent makes a landing declaration or discard
report intelligible; year-first would split one vessel's operating history.

### Leg 3 — privacy and custody differ from the default

The generic schema already warns that resource operations can expose concessions, coordinates,
reserves and production. Fisheries adds vessel and crew identity, precise fishing positions, gear
and effort patterns, quota balances, commercially sensitive catch/landing volumes, observer or
enforcement allegations, and credentials or submission identifiers. Those values can reveal a
person's movements or a business's regulated/commercial activity. The catalogue consequently sets
`potentially_sensitive` and keeps raw records local under P7 policy; it assigns no handling class.

Custody is a second safety boundary. `Fishing-Vessel-Licence-FV-2048.pdf`,
`Observer-Trip-07_Report.pdf`, `Quota-Uptake_Vessel-VS123_2026.xlsx` and
`Fish-Transport-Document_Lot-L-771.pdf` can be byte-identical across an operator archive,
government case, buyer traceability file or logistics packet. Grouping may retrieve them together,
but it must not copy a vessel, trip, species or quota fact from one member to another.

### Node-test conclusion

Keep only as the narrow, reversible template described above. Refusal is required if R1c determines
that vessel-and-voyage recognition, asset-led dimensions and privacy/custody rules are not materially
different from the resource default. The legacy id is not a reason to retain a node.

## Bottom-up file corpus

The JSON carries thirteen concrete fixtures. Each separates observations from facts. Because
`resource_operations` has no approved fields, positive files list only universal facts; the absence
of a domain fact is deliberate.

1. **`Trip-2026-07-14_Electronic-Logbook.xml`** (`code_structured`) — Structured vessel, trip,
   departure/return, gear, area, species, retained/discarded, quantity and submission slots. A
   filename date is not automatically the reporting period; a submitted status does not prove
   accuracy or legality.
2. **`Landing-Declaration_LD-8821.pdf`** (`text_document`) — Labelled originating vessel, landing
   port/date, species presentation, landed weights, weighing and submission sections. A form does
   not by itself prove the landing happened or reconcile to catch.
3. **`Quota-Uptake_Vessel-VS123_2026.xlsx`** (`spreadsheet`) — Allocation, stock/area, uptake,
   balance, transfer and approval sheets. It may be authority-held and does not turn allocation
   into actual landed catch.
4. **`VMS-Track_VS123_Trip-07.csv`** (`spreadsheet`) — Vessel positions and timestamps but no
   species, gear, catch or landing columns. It can join a voyage group without donating catch facts.
5. **`Observer-Trip-07_Report.pdf`** (`text_document`) — Vessel/trip, gear deployment, sampling,
   observed composition, retained/discarded categories, estimates and review outcome. An estimate
   or allegation is not the vessel declaration or a confirmed infringement.
6. **`Catch-Record-App-Screenshot.png`** (`image`) — OCR-visible electronic form with clipped vessel,
   trip, species, weights and status. It can support protected review and a screenshot residual;
   missing EXIF is not screenshot proof and visible status is not authenticity.
7. **`Signed-Catch-Logbook_Page-18_scan.pdf`** (`ocr`) — Handwritten logbook page with partial OCR,
   signature/stamp and gaps. Unknown is required where vessel/trip/quantity labels cannot be cited.
8. **`Transhipment-Declaration_VS123_to_VS455.eml`** (`email`) — Native mail headers plus body or
   attachment manifest naming donor/receiver, event, position/port, species and transferred amounts.
   Transmission is not acceptance, and attachment facts remain separate until extracted.
9. **`Voyage-Catch-Packet_Trip-07.zip`** (`archive`) — Manifest of logbook, VMS, landing, weighing,
   quota and receipt members. It is read without unpacking; member facts are never copied globally.
10. **`Fishing-Vessel-Licence-FV-2048.pdf`** (`text_document`) — Issuer, vessel, conditions,
    validity and permitted activity, but no catch event. This is the government collision fixture.
11. **`Fish-Transport-Document_Lot-L-771.pdf`** (`text_document`) — Product lot, boxes, vehicle,
    origin/destination, species/weights and seals after landing. It is the Logistics collision
    fixture; transported product weight is not silently catch weight.
12. **`Marine-Habitat-Survey_Transect-04.pdf`** (`text_document`) — Vessel and coordinates appear
    as fieldwork metadata, while the report is habitat sampling rather than commercial catch. This
    is a government/environmental false positive.
13. **`Fishing-Vessel-Engine-Maintenance-Report.pdf`** (`text_document`) — Vessel asset, engine
    serial, work order, parts and technician sign-off, with no trip or catch. This is the Engineering
    collision fixture.

### Sparse, archive and cross-schema behavior

The screenshot, email, VMS file and archive can be members of an accepted voyage group without
receiving facts from its anchor logbook. This follows the design's observation/fact firewall. The
design states: “A session should never be treated as proof of topic,” so an upload/download session
or portal thread is only retrieval evidence. The `Voyage-Catch-Packet_Trip-07.zip` manifest likewise
cannot establish each member's vessel, period or species. The screenshot can also activate Photos on
its own image facts; that is intended coactivation, not a fisheries collision.

## Collisions and reciprocal boundaries

The JSON uses only the required edge shape `{domain, signal, provenance}`. Every signal names the
same fixture bytes and states both directions; R1c must make the reciprocal entries land or remove a
pair:

- `government.permit-licensing` — **SAME FIXTURE BYTES:**
  `Fishing-Vessel-Licence-FV-2048.pdf`. Fisheries requires operator-side linkage to voyage/catch or
  entitlement use; Government wins for issuer-side application, approval, renewal, conditions or
  enforcement. A licence alone is neither a catch event nor proof of operator custody.
- `government.environmental-regulation` — **SAME FIXTURE BYTES:**
  `Observer-Trip-07_Report.pdf`. Fisheries wins for vessel-trip catch/effort/observer evidence;
  Government wins for regulator surveillance, protected-species, habitat or enforcement evidence.
  An observation or allegation cannot become a declared catch automatically.
- `business_operations.corporate-regulatory-filings` — **SAME FIXTURE BYTES:**
  `Quota-Uptake_Vessel-VS123_2026.xlsx`. Fisheries wins for operator entitlement-to-catch/landing
  uptake; Business Operations wins for a company's submitted statutory return or filing-control
  record. Neither custody role can be inferred from a workbook alone.
- `engineering.drawing-package` — **SAME FIXTURE BYTES:**
  `Fishing-Vessel-Engine-Maintenance-Report.pdf`. Fisheries wins only when joined to the accepted
  operating packet; Engineering wins for controlled technical drawings, revisions or maintenance
  design evidence. Vessel identity alone never activates fisheries.
- `logistics.shipment` — **SAME FIXTURE BYTES:**
  `Fish-Transport-Document_Lot-L-771.pdf`. Fisheries wins for originating-voyage/landing/catch
  reconciliation; Logistics wins for post-landing custody, vehicle, seals, destination and
  consignment movement. Product weight remains transport evidence unless independently reconciled.

## Neighbours considered but not edged

- **`engineering` schema generally** — considered because fishing vessels and gear have technical
  records. The sharper same-kind `engineering.drawing-package` edge captures the collision; a broad
  schema edge would conflate all vessel engineering with catch operations.
- **`government` schema generally** — considered because quota, licences, observers and enforcement
  are often government-held. The two specific same-kind templates above separate issuer licensing
  from environmental/surveillance custody; no broad government edge is invented.
- **`business_operations` schema generally** — considered because operators submit returns and may
  keep quota ledgers. `business_operations.corporate-regulatory-filings` is the specific filing
  boundary; ordinary internal operations are not automatically a collision.
- **`logistics` schema** — considered because landed fish move through transport and first sale. The
  specific `logistics.shipment` fixture captures post-landing movement; a generic logistics edge is
  unnecessary.
- **`resource_operations.utility-metering-billing` and `resource_operations.renewable-generation`**
  — adjacent resource templates but no direct shared fixture in this row. A generic measured
  quantity or interval is not enough to collide; future concrete same-bytes evidence can be handled
  in R1c.

## Files considered and rejected from activation

- **Generic seafood invoice or auction sales note** — may share species and weight, but without an
  own vessel/voyage/catch chain it is Finance or Logistics evidence.
- **Fishing vessel licence or quota allocation alone** — permission/allocation is not performed
  fishing or landed catch; use the government collision boundary.
- **AIS/VMS movement-only export** — movement cannot establish fishing effort, species or catch.
- **Marine-biology survey or fish-stock assessment** — species and coordinates are scientific
  observations, not an operator's vessel catch record.
- **Aquaculture husbandry, feed or tank-growth log** — remains another production situation unless
  an explicit licensed harvest and landing relation connects it to this row.
- **Vessel engine, gear-design or repair packet** — engineering evidence; asset identity does not
  copy a trip or catch fact.
- **Fish transport, customs or catch-certificate buyer packet** — Logistics/Government/Finance may
  own it; the same bytes can co-occur with fisheries only after custody and originating catch are
  independently evidenced.
- **Calendar trip reminder, portal session, email thread or archive filename** — retrieval clues,
  never sole activation evidence.
- **Screenshot, photograph or scanned page with a fish image or word** — Photos/Temporary Screenshots
  or Review Later unless OCR or native structure preserves the vessel-trip-catch relation.

## Intended coactivation for R1c (not authored in JSON)

This template deliberately leaves `also_holds_with` empty. A catch certificate, landing declaration,
quota spreadsheet or transport packet may carry both an operator fisheries fact set and an
independently evidenced Government, Logistics, Finance or Business Operations situation. R1c should
decide whether that is represented only through P9 groups and per-file `also_schema` observations,
or whether a future schema-level `also_holds_with` relationship is warranted. The same bytes and
custody role must be shown before a second schema is activated; a shared species, port or vessel
string is not enough.

## NEEDS-JOSEPH

1. **NJ-FISH-1 — field identity and dimension depth.** Should fisheries reuse the resource schema's
   proposed `site`, `operating_authority`, `asset`, `output_stream`, `reporting_period` and
   `record_type`, with vessel/voyage as values, or should R1c select one neutral global role? The
   useful fisheries order is context → vessel → voyage/period → record type, but PR-6 prevents this
   row from deciding fields.
2. **NJ-FISH-2 — catch-certificate coactivation.** When identical catch-certificate or transport
   bytes are held by an operator and a buyer/importer, should P9 grouping represent the dual purpose,
   or should a future Logistics/Finance template own an explicit schema relationship? Both sides of
   the custody boundary must be stated before any automatic placement.
3. **NJ-FISH-3 — validation catalogues.** R2/R4 must choose deployment-specific species/FAO-code,
   fishing-area and vessel-identifier validation families. This row intentionally supplies no
   jurisdiction, regex, code list, quota threshold or reporting deadline.
4. **NJ-FISH-4 — aquaculture scope.** Should explicit licensed aquaculture harvest and landing
   records remain under this capture-fisheries template, use a separate future template, or fall
   through to the resource default? The JSON allows only the narrow explicit relation and does not
   treat aquaculture vocabulary alone as activation.

## Self-verification

- Both assigned output paths were absent at start and are the only paths added.
- JSON parses with `python3 -m json.tool` (run after authoring).
- Every `file_examples.source_type` is in the exact `SOURCE_TYPES` vocabulary.
- `fields` and `proposed_fields` are empty as required by PR-6; no field or dimension is authored.
- Every collision is an object with exactly `domain`, `signal`, `provenance`; signals are reciprocal
  in meaning and name `SAME FIXTURE BYTES`.
- `also_holds_with` has no entries; intended coactivation is recorded here for R1c only.
- Every edge endpoint is present in `planning/domains/roster.json`; residuals use named library
  destinations.
- Quotes from `00` were checked byte-for-byte; no fabricated quote is used.
- A final scoped diff and repository status check are required before handoff.
