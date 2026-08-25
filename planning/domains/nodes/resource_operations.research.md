# resource_operations — research memo (R1b, J-DEPTH)

Date: 2026-08-25  
Roster row: `kind: schema`, `schema_id: resource_operations`, `launch: placeholder`.

## Verdict

**Keep the schema as a proposal; do not refuse it.** The defensible anchor is not the very broad
industry label in the roster hint. It is the operator-side relation **authorised source/site →
operating unit or asset → measured output/environmental performance → reporting period**. That
relation appears across extraction, generation, utilities, agriculture, forestry and fisheries and
does not fit another schema's default without changing the meaning of its fields.

This is a deliberately provisional survival. If R1c decides that manufacturing's proposed `site`,
`asset`, a widened `product`, a neutral period and global `record_type` already express the whole
relation, then the honest result is to merge this recognition grammar into manufacturing and refuse
the separate schema. The one plainly unshared role is `operating_authority`: the permit, tenure,
quota, concession or connection under which a source is operated. `fields` and
`template.dimension_order` therefore remain empty under PR-6; all six candidate keys are proposals.

## Sources and method

Binding local sources used:

- `planning/domains/dispatch/RESEARCH-BRIEF.md` and the output of
  `python3 planning/domains/dispatch/make_prompt.py resource_operations`.
- `planning/00-database-agent-product-design.md`, authoritative for all quoted product claims.
- `planning/01-product-design-structured.md`, consulted only as a locator; `00` wins.
- `planning/prompts/ALIGNMENT.md`, `_CONTRACT.md`, `CONNECTION.md`, and
  `CONNECTION-EXAMPLES.md` for observation/fact separation, node test, placeholder rule, closed
  edge vocabulary, grouping firewall, and residual names.
- `planning/domains/roster.json` for assignment and edge endpoint existence.
- `planning/domains/canonical_fields.json` for the exact universal keys and existing domain keys.
- `src/evidence_shape/vocabulary.py` for the closed `SOURCE_TYPES` vocabulary.
- `planning/overnight/council/DECISION-BRIEF.md` for ratified D1, D4, D6 and J-IND; these are not
  re-debated.
- Landed schema rows `manufacturing`, `engineering`, `construction_property`, `government`, and
  `business_operations`, plus the roster's `logistics` assignment, for reciprocal seams. No
  neighbour was edited.

No external statistics, thresholds, regulatory assertions or gazetteer contents are claimed. The
named files and slot structures below are ordinary operational document forms used as bottom-up
fixtures, not claims that one jurisdiction uses a particular mandated form.

## J-DEPTH: the first eight concrete files

These eight are the minimum collision-bearing set; the JSON adds an archive and a sparse image.

1. **`ML-2048_Monthly-Production-Return_2026-06.xlsx`** (`spreadsheet`). A header labels lease,
   holder, mine and reporting month. Rows distinguish ore mined, waste, feed and saleable output,
   with units and declaration status. This is the clean source-to-volume structure. Legal now:
   exact universals only — `file_type`, `creation_date`, `language`, `duplicate_family`,
   `version_family`, `sensitivity_status`. Proposed later: site, authority, output stream, period,
   record type. The filename's year/month does not prove a period and quantities do not become
   folder facts. Inactive residual: Review Later.

2. **`Water-Abstraction-Licence-WA-73.pdf`** (`text_document`). It carries issuer, labelled licence
   identifier, holder, authorised point, dates, activity and a conditions schedule. It proves a
   credible authority structure but not current operation; the same bytes belong in the
   government's issuer-side case and the operator's authority series for different reasons. An
   issuer name alone settles neither side. Inactive residual: Independent Records.

3. **`SCADA_Meter-MP-7812_2026-06.csv`** (`spreadsheet`). Interval start/end, meter identity,
   import/export, unit and substitution flags are explicit, while customer name and invoice total
   are absent. It is operational metering rather than a utility bill. The file may join an accepted
   meter group, but it must not receive the site from a neighbouring statement. Inactive residual:
   Review Later.

4. **`Outfall-3_Water-Quality_June-2026.pdf`** (`text_document`). Sampling point, parameter,
   method, result, unit, referenced condition, limit and exceedance response are joined. This is
   operator environmental-compliance evidence; a regulator may legally hold the same bytes as
   surveillance evidence. The analyst's signature does not make the laboratory the operator.
   Inactive residual: Independent Records.

5. **`Field-12_Harvest-Register_2025-26.xlsx`** (`spreadsheet`). Farm/field, crop, operation date,
   harvested weight, moisture and store destination are labelled; seed/treatment inputs occupy
   different roles from output. `lot` does not make this manufacturing, and the store destination
   does not make it logistics. Inactive residual: Review Later.

6. **`WT-04_Gearbox-Replacement-Work-Order.pdf`** (`text_document`). Asset, failure, parts,
   downtime and returned-to-service status make this manufacturing maintenance evidence. A site
   header and turbine vocabulary do not make it resource_operations. It may also join an accepted
   operating-asset series, but the work order by itself is the collision fixture that the resource
   node must reject. Inactive residual: Independent Records.

7. **`North-Quarry-Plant-Layout_RevC.dwg`** (`design_creative`). Project, drawing number, revision,
   status and designer occupy a controlled title block. Quarry vocabulary and depicted plant do not
   change the document's role: it is controlled design definition in engineering, not an operating
   production record. Inactive residual: Unsupported or Encrypted when content cannot be read.

8. **`June-Ore-Shipments.csv`** (`spreadsheet`). Consignment, vessel, load/discharge ports, mass and
   bill-of-lading reference define movement and custody. Commodity plus mass is tempting but false
   resource evidence; no mine, authority, production unit or reconciliation exists. This belongs to
   logistics. Inactive residual: Independent Records.

The two extra ugly cases are `Environmental-Monitoring-Packet.zip`, whose manifest spans two sites
and periods and therefore cannot donate one site's facts to every member, and `IMG_4821.jpg`, a
gauge photograph with camera facts but no readable asset/site evidence. The latter can legally hold
Photos facts — `capture_year`, `location`, `people`, `camera_information`, `media_type` — but no
resource-operation fact. It may group without copying facts and falls through to One-Off Images.

## Node test, argued on all three legs

### Detection signals

The schema's deterministic core is relational. A labelled permit identifier alone is inadequate;
it needs holder, authorised area/source, activity and conditions. A quantity table alone is
inadequate; it needs distinct source, output, transfer/loss/stock roles and a reporting period. A
monitoring result alone is inadequate; it needs site/sampling point, parameter/method/unit and the
authority condition or operational control it tests. A meter series needs service-point identity,
interval, direction/value/unit and quality flags.

Manufacturing's strongest signals instead join product, batch/lot, sequential transformation,
inspection, release or quality event. Engineering joins design item, revision/baseline,
requirements and verification. Logistics joins consignment, custody and origin/destination.
Construction joins property/site to a bounded professional instruction or works contract.
Government joins an applicant/regulated party to issuer-side review, decision, inspection or
enforcement. Resource operations survives because the same evidence cannot be described by any one
of those default relations.

### Recommended dimensions

The researched default, held only in prose until R1c licenses keys, is:

`site → operating_authority → output_stream → reporting_period → record_type`

The asset-led alternative is `site → asset → record_type` for metering, generation, integrity and
maintenance records. This is branch-shaped on purpose. A farm field or forest compartment may be
the operational source itself and need no asset level; a utility meter may need an asset and no
commodity level. Time is never first. The exact design sentence used in JSON is: **"For document
and record domains, project, function, or subject usually comes before time because putting year
first scatters related work across calendar folders."** Quantities, units, coordinates, permit
conditions and measured environmental values are content/search evidence, never destination
dimensions.

### Privacy posture

This material can expose reserves and production rates, critical-infrastructure identity and
layout, meter/service-point identifiers, precise resource and vessel locations, environmental
exceedances, concession terms and farm operations. That differs from generic project-delivery
records and justifies `potentially_sensitive`; it does not authorize a handling class. No raw
quantity, coordinate, permit condition or monitoring result is proposed as a destination field.
Sparse photographs and unreadable engineering formats remain local under their ordinary safety
rules rather than being classified from an industrial-looking filename.

## Proposed fields and alternatives

The proposal has six keys; there are no authored field rows.

- `site`: exact reuse of manufacturing's proposal. It is the place the record is about, not Photos'
  capture `location`. A downstream sample can document North Quarry while being captured elsewhere.
- `operating_authority`: the distinct role — permit, licence, lease, tenement, concession, quota or
  connection agreement held by the operator. Government holds the issuer-side case; the role split
  is explicit.
- `asset`: exact reuse of manufacturing's proposal for the enduring well, pit, generator, feeder,
  pump, vessel or meter. It is optional in area-led branches.
- `output_stream`: proposed because manufacturing `product` is too narrow for abstraction,
  generation, standing timber, catch and metered service. R1c should widen one neutral key if that is
  semantically honest, never ship both as synonyms.
- `reporting_period`: the period the measurements are about. It is not `creation_date`, `tax_year`,
  academic `term`, Photos `capture_year`, or necessarily business `fiscal_period`. A globally
  neutral period key may be better and should replace, not accompany, this proposal.
- `record_type`: reuse the canonical Finance spelling. If its current role is finance-only, define
  one global document-function key rather than minting a resource-specific variant.

The tempting seventh field, measured quantity/volume, was rejected. A number and unit are important
content and may be cited in an explanation, but raw time-series values and production volumes are
high-cardinality, sensitive, revision-prone and unsuitable folder dimensions. The schema is proven
by the **structure linking roles**, not by storing every cell as a catalogue facet.

## Reciprocal boundaries and collision fixtures

### Manufacturing

Resource operations must not steal `WT-04_Gearbox-Replacement-Work-Order.pdf`: asset, failure,
parts, downtime and release-to-service are manufacturing maintenance. Manufacturing must not steal
`ML-2048_Monthly-Production-Return_2026-06.xlsx`: it has no product/batch transformation; it
reconciles an authorised source to measured extracted output. The same asset history may legally
join both schemas, hence `also_holds_with` as well as the collision.

### Engineering

Resource operations must not steal `North-Quarry-Plant-Layout_RevC.dwg`: title block,
revision/status and designed plant make it engineering. Engineering must not steal the SCADA export:
meter identity and operational readings do not define or verify a design item. A commissioning or
verification report can carry both when it cites requirements and records the operating source.

### Logistics

Resource operations must not steal `June-Ore-Shipments.csv`: consignment, vessel, ports and
bill-of-lading reference define custody/movement. Logistics must not steal the monthly production
return merely because it includes stock transfer or sale/export totals; the file's governing
structure is source-to-output reconciliation. No `also_holds_with` schema edge is authored because
the landed logistics schema was not available for reciprocal schema-edge alignment; the collision
is sufficient and R1c owns reciprocity.

### Construction and property

Resource operations must not steal a grid-connection construction pack, planning approval or plant
layout merely because a future operating site is named. Construction_property must not absorb the
recurring operational meter, output and monitoring series after handover. The seam is bounded works
instruction versus enduring authorised operation. No also-holds edge is asserted because the same
file usually changes role across lifecycle rather than carrying both schemas simultaneously.

### Government

The same `Water-Abstraction-Licence-WA-73.pdf` bytes can legally exist in both: government holds the
issuer-side decision/case; resource_operations holds the operator's authority and conditions. The
same reciprocal distinction applies to the monitoring packet: regulator surveillance/enforcement
versus operator compliance. Letterhead cannot settle the role. This is both a collision during
activation and lawful multi-schema membership after evidence establishes both roles.

### Business operations

Resource operations must not steal a sustainability strategy, commodity budget, generic audit or
project plan with no source/site-authority-output relation. Business operations must not steal an
operator's measured production and compliance series merely because management receives it. A
document's governance purpose and its operational subject may coexist, but no schema-level
also-holds edge is asserted without an exact landed reciprocal edge.

## Files considered and rejected

- `Commodity Market Outlook.pdf`: discusses outputs and prices but is Reading Inbox, not evidence of
  operating a source.
- `Solar Farm Investment Case.pptx`: a business_operations plan unless controlled design or actual
  operation evidence appears.
- `Permit Application Draft.docx`: may be construction_property or government case material; an
  application is not an operating authority.
- `Crusher BOM.xlsx`: engineering if design-authoritative, manufacturing/procurement if a build or
  spare-parts list; no source-to-output structure.
- `Utility Bill June.pdf`: Finance/receipt evidence, not operational metering merely because it names
  a meter and consumption.
- `ESG Report 2025.pdf`: publication or business governance unless site-level measured monitoring
  structures and operator role are cited.
- `Mine Closure Concept.pdf`: engineering/planning reference until it joins an authorised site's
  obligation and monitored closure series.
- `Field Photo.jpg`: Photos/One-Off Images unless its own evidence identifies the operating subject;
  neighbourhood may group it but cannot copy site or asset facts.

## Neighbours considered without an edge

Research was considered because resource estimates, ecological studies and trial plots create
knowledge. No edge was authored: a research project/lab/stage/artifact grammar is distinguishable
from recurring operator returns, and an individual study can be handled at template collision level
if later evidence demands it. Finance was considered for royalties, bills and reserve valuations;
the accounting record and the measured operating record are different structures, and the file list
contains no unresolved same-byte fixture requiring an edge. Code was considered for SCADA exports
and control-system configuration; structured operational data is not a software repository, and a
repository root/package structure remains code.

## NEEDS-JOSEPH

- **NJ-RESOURCE-1 — split or operational core.** Should R1c license a shared operational core
  (`site`, `asset`, neutral output/product, neutral period, global `record_type`) across
  manufacturing and resource_operations, leaving `operating_authority` and recognition as the
  distinction, or merge the two schemas? Keep two if authority/source-to-output and privacy are
  materially different schema rules; refuse this node if the difference is only values.
- **NJ-RESOURCE-2 — authority as a destination.** A permit/tenement key materially improves
  retrieval in multi-authority corpora, but a folder name can expose concession or infrastructure
  identifiers. Decide whether `operating_authority.destination_eligible` defaults true, defaults
  false, or is template/policy-dependent. The JSON seeds true with explicit flatten/protection
  warnings; this is not silently settled.

## Claims and self-audit

The schema claims only a proposal: regulated source/site-to-measured-output records have a distinct
activation grammar. It does **not** claim a jurisdiction's form names, regulator list, identifier
regex, thresholds, statistics, field legality or final folder tree. Work types are values.

Contract audit performed after writing JSON: exact universal keys used in file fixtures are
`file_type`, `creation_date`, `language`, `duplicate_family`, `version_family`, and
`sensitivity_status`; the Photos collision uses only landed Photos keys. All `source_type` values are
members of `SOURCE_TYPES`. All edge endpoints are roster ids and all fallthrough targets are named
residuals. `fields` and `dimension_order` are empty. No folder path is written as a fact. The first
eight concrete files include the happy case, labelled permit, metering export, environmental
monitoring, land-based operation, manufacturing collision, engineering collision and logistics
collision; archive and sparse-image cases follow. No neighbour or shared file was edited.
