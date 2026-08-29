# R1b lab notes — `resource_operations.grid-connection`

Date: 2026-08-27
Assignment: `kind: template` · `schema_id: resource_operations` · `launch: placeholder`
Result: **keep the node** (`refuse_node: false`), field-less and dimension-less pending R1c.

## Verdict and strongest objection

Keep this template, but keep its scope narrow: it is the **connecting customer's electricity-grid
relationship**, not every file about an energy project and not every utility-network contract. Its
anchor is:

`installation/site + connecting customer + network operator + connection point/capacity + staged permission to connect or remain connected`

The strongest charge is that this is only a list of work types beneath the broad
`resource_operations` default, or a generic contract/construction project decorated with electricity
words. That charge fails on evidence. The resource schema default normally requires a recurring
operating relation: authorised source/site, asset, measured output or environmental performance and
reporting period. A connection application or executable offer has no output series yet, but it does
carry a relationship the default never requires: applicant/customer, network operator, point of
connection, requested or agreed capacity, offer/acceptance apparatus and continuing conditions.
After energisation, that same reference persists into modifications and compliance evidence even
after the construction project has closed. Conversely, a monthly interval export or utility bill can
be genuine resource-operation evidence without saying how the installation acquired or retains a
connection.

This is not a claim that every network industry shares the grammar. The absorbed legacy id is
`energy.grid-connection`, and the primary evidence reviewed is electricity-specific. The broader
word *network* in the roster name does not license gas, water, district heat or telecom coverage.
NJ-GRID-1 leaves that scope fork explicit.

## Authority stack and method

Binding repository sources read:

- `planning/domains/dispatch/RESEARCH-BRIEF.md` and the complete stamped output of
  `python3 planning/domains/dispatch/make_prompt.py resource_operations.grid-connection`.
- `planning/00-database-agent-product-design.md`, authoritative for product claims and quotations.
- `planning/01-product-design-structured.md`, used as a locator only; `00` wins.
- `planning/prompts/ALIGNMENT.md`, `planning/domains/_CONTRACT.md`,
  `planning/domains/CONNECTION.md`, and `planning/domains/CONNECTION-EXAMPLES.md` for the node
  test, observation/fact split, grouping firewall, placeholder rules, edge vocabulary and residuals.
- `planning/overnight/council/DECISION-BRIEF.md` for D1–D6, J-IND and J-DEPTH. J-DEPTH overrules
  the stamped prompt's retired gist clause.
- `planning/domains/roster.json` and `planning/domains/ROSTER.md` for the exact row, absorbed
  `energy.grid-connection` coverage, neighbour ids and NJ-J-IND-2.
- `planning/domains/canonical_fields.json` and `src/evidence_shape/vocabulary.py` for exact field
  and source-type vocabulary.
- the landed `resource_operations` schema JSON and memo, plus the full landed JSON for
  `engineering.commissioning-handover`, `government.permit-licensing`, and
  `business_operations.contract-administration`. The commissioning row already names this row and
  binds the reciprocal fixture bytes used below. No neighbour was edited.
- `identity.core-documents` JSON and memo as the landed launch-depth calibration row.

Primary external sources were used to verify recurring document **structures**, not to import a
jurisdiction, regex, threshold, legal conclusion or current status into the catalogue:

- [NESO Connections Portal](https://www.neso.energy/industry-information/connections/connections-portal)
  confirms that connecting customers apply for agreements, monitor applications and milestones,
  and access signed contract documents in one portal relationship.
- [NESO Connections Offer Process](https://www.neso.energy/industry-information/connections/connections-offer-process)
  supplies the observed pre-application → submission → offer → review/signing → continuing
  engagement lifecycle and distinguishes a modification application from a new application.
- [NESO Your Connections Journey](https://www.neso.energy/industry-information/connections/your-connections-journey)
  names project size/capacity, project type, fuel type, connection-point location, timescale,
  technical information, modification forms and Energisation Operational Notification as recurring
  connection-journey evidence.
- [National Grid Electricity Distribution Post-Acceptance Guidance](https://connections.nationalgrid.co.uk/post-acceptance-guidance)
  verifies the observed Letter of Acceptance, milestones, site-specific Connection Agreement,
  import/export capacity, ownership-boundary diagrams, works/consents and pre-energisation agreement
  structures.
- [Energy Networks Association G99 overview](https://www.energynetworks.org/assets/images/Resource%20library/G99%20Type%20A%20Summary%20Guide%202020.pdf)
  and [EREC G99](https://www.energynetworks.org/assets/images/Files/ENA_EREC_G99_Issue_1_Amendment_9_%282022%29.pdf)
  verify Installation Documents, site compliance/commissioning test forms, commissioning programmes,
  DNO witness context and the generator/installer-to-DNO relationship. This row does not encode the
  documents' deadlines, form numbering rules or edition-specific requirements.
- [UK Power Networks witness-testing guidance](https://library.ukpowernetworks.co.uk/library/en/Connectionsquotations/Customerresponsibilities/3.15-g59-witness-testing/)
  confirms that installation/commissioning evidence and operational notifications are distinct
  recurring artifacts. The catalogue infers no permission to operate from appearance of a form.

No statistic, confidence score, threshold, operator gazetteer, form-validity rule, legal effect or
jurisdiction-specific identifier pattern is asserted.

## Node test — all three legs

### 1. Detection differs from the schema default

The schema default joins an operating site/authority/asset to measured output or environmental
performance over a period. This row's decisive evidence is a **connection lifecycle**, and it can
exist before the asset produces or consumes anything:

- an application needs customer, site, operator, point/capacity request and persistent reference;
- an offer needs the same parties/reference plus offered interface, works, charges, acceptance and
  milestone apparatus;
- an agreement needs a continuing site-specific relationship, operational boundary and permitted
  import/export terms;
- commissioning evidence must cite that connection relation, not merely an installed tag;
- an operational notification records the connection's permission/status, while a proposed email
  window proves nothing;
- modifications trace back to the parent agreement and alter its capacity, date, technology, point
  or terms.

No single word, form, signature, capacity figure, diagram, meter point or network-operator name can
do that work. The relation is distributed across labelled roles.

### 2. Recommended dimensions differ

The schema's prose default is
`site → operating_authority → output_stream → reporting_period → record_type`, with an asset-led
alternative. This row's conditional order is:

`site → operating_authority → asset → record_type`

Here `operating_authority` is the connection application/agreement relationship, and `asset` is the
interface point, bay, feeder, meter point or protection unit. `output_stream` appears only if import
and export arrangements genuinely split, and `reporting_period` only beneath recurring compliance
or modification evidence. The application, offer, acceptance, agreement, operational notification
and modification are values of `record_type`, not child nodes.

The order is not time-first. Application date, offer date, acceptance date, milestone date,
commissioning date, energisation date and notification date are different events in one continuing
relationship. Leading with calendar time would scatter the exact packet a connection reference is
meant to retrieve. The serialized order remains empty because the schema declares no field rows.

### 3. Privacy differs

The schema default already warns about production, coordinates, meter identifiers and infrastructure.
This row adds a dossier that can be sensitive **before operation begins**: requested/agreed capacity,
exact point of connection, queue and readiness evidence, reinforcement scope, costs and securities,
land-rights evidence, single-line and ownership-boundary diagrams, protection settings, compliance
results, operational-notification conditions and named technical contacts. A recognized connection
pack should use bounded excerpts; diagrams, settings and access details remain local. This is the
catalogue value `potentially_sensitive`, not a P7 handling class.

## Bottom-up concrete file set

The JSON contains the complete observation/fact split. These are the first eight load-bearing files:

1. **`Connection Application - Solar Farm A - CONN-2048.xlsx`** (`spreadsheet`). Customer, site,
   network operator, reference, requested import/export capacity, technology, preferred point and
   target date occupy labelled slots. It proves an application structure, not acceptance, capacity
   reservation or an agreed point. Current legal facts are universal; schema candidates are
   explicitly conditional on R1c. Inactive: Review Later.

2. **`CONN-2048 Data Registration Code submission v3.xlsx`** (`spreadsheet`). A connection cover
   sheet anchors plant, fault, reactive, protection and metering tabs to the application. Without
   that cover relation it is an engineering workbook. Revision v3 does not prove accepted baseline.
   Inactive: Review Later.

3. **`Connection Offer - CONN-2048 - Solar Farm A.pdf`** (`text_document`). Parties, point,
   offered capacity, works, reinforcement assumptions, charges, conditions, validity, acceptance
   and milestones form the offer. It does not prove execution or present capacity. Inactive:
   Independent Records.

4. **`Letter of Acceptance and Payment - CONN-2048 - signed.pdf`** (`text_document`). It cites the
   offer/reference and carries signatory, countersignature and payment/security apparatus. A visible
   signature does not prove authenticity, payment or that prerequisites were met. Inactive:
   Independent Records.

5. **`Executed Connection Agreement CA-SS03-2048.pdf`** (`text_document`). Parties, site,
   interface, maximum import/export capacity, operational boundary and continuing conditions make
   this the strongest holder-side instrument. It may also be administered as a contract only when
   a register, obligation tracker or notice calendar independently proves that schema. Inactive:
   Protected Records.

6. **`SLD Solar Farm A to SS-03 - Rev P4.dwg`** (`design_creative`). This is the first collision
   fixture: design item, revision, status and designer make controlled engineering definition. A
   labelled point of connection on the diagram does not prove submission, acceptance, installation
   or energisation. Inactive: Unsupported or Encrypted.

7. **`G99 Installation Document and Site Compliance Tests - SS-03.pdf`** (`text_document`). The
   generator/installer, DNO, facility, connection reference, protection-test rows and declaration
   create connection-commissioning evidence. The form cannot prove compliance, safety or permission
   to operate. It can also carry engineering installed-instance evidence independently. Inactive:
   Protected Records.

8. **`Final Operational Notification - CONN-2048 - 2026-06-30.pdf`** (`text_document`). Operator,
   customer, facility, reference, notification status, permitted scope, conditions and referenced
   compliance documents are explicit. It does not prove continuing validity or actual output.
   Inactive: Independent Records.

The ugly cases deepen the set:

- **`RE Energisation window and witness attendance - SS-03.eml`** is the exact reciprocal
  collision fixture already authored by `engineering.commissioning-handover`. It proposes a window
  and names witnesses but proves neither energisation nor attendance. A group may attach it without
  copying site, asset or event facts.
- **`Modification Application - Capacity Increase - CONN-2048.xlsx`** requests a change; it does
  not prove acceptance or supersession.
- **`Connections Portal Export - CONN-2048.zip`** exposes one connection-reference manifest with
  mixed stages and an encrypted member. The manifest is inspected without unpacking, and no member
  inherits another's facts.
- **`Electricity Bill June 2026 - MPAN 1200000000000.pdf`** is the tempting meter-shaped false
  positive. Supplier, billing period, consumption and amount due make billing/receipt evidence; a
  meter-point identifier does not recreate the connection lifecycle.

## Files considered and rejected

- **`Budget Estimate - Solar Farm A.pdf`** — an indicative study with no executable acceptance
  apparatus is not a connection offer; it may be a project reference or Review Later.
- **`Grid Capacity Map Screenshot.png`** — public or portal network-capacity information is a
  reference capture unless one application/reference relation is independently present.
- **`SLD Solar Farm A to SS-03 - Rev P4.dwg`** — controlled engineering definition, rejected above.
- **`Substation SS-03 Construction Programme.xlsx`** — a schedule, cost and contractor plan is
  business project delivery or construction unless the connection-agreement relation is explicit.
- **`Cable Easement - East Field.pdf`** — land rights may support a connection but are not the
  connection agreement itself; construction/property/legal evidence remains independently true.
- **`Electricity Bill June 2026 - MPAN 1200000000000.pdf`** — billing, not connection acquisition.
- **`SCADA Export - SS-03 - June.csv`** — post-energisation operational metering belongs to the
  resource schema default or the utility-metering template; no application/offer is reconstructed.
- **`Protection Relay Settings - SS03 Rev C.xlsx`** — engineering/operational technical evidence
  until a connection reference and operator approval/condition tie it to this situation.
- **`Connection Agreement template - blank.docx`** — a precedent/reference form with blank parties
  and site is Reference Clips, not a live connection.
- **`Grid Code.pdf`** — a standard or publication is Reading Inbox/Reference Clips unless a bounded
  file cites a particular condition; a standard title never activates this row.
- **`Planning Permission - Solar Farm A.pdf`** — issuer-side land-use permission is government or
  construction/property evidence, not proof of a network connection.
- **`Energisation Permit to Work.pdf`** — an internal switching/safe-work authorization is not an
  operational notification from the network counterparty.

## Reciprocal boundaries and same-byte fixtures

### Engineering commissioning and handover

The reciprocal edge is binding and uses the same bytes on both sides:
**`RE Energisation window and witness attendance - SS-03.eml`**.

- This row owns the connection reference, network-operator counterparty, connection point/capacity
  and permission/status evidence for the supply.
- `engineering.commissioning-handover` owns installed-instance tags, reconciliation to controlled
  design, witnessed acceptance and transfer to the operating party, whether or not a network is
  involved.

The email's proposed window proves neither event. A single package can independently prove both,
but CONNECTION §5 forbids template-level `also_holds_with`; R1c must lift/adjudicate the intended
schema coactivation. The JSON edge is exactly `{domain, signal, provenance}` and names both
directions plus the same fixture bytes.

### Government permit and licensing

Potential shared bytes: **`Executed Connection Agreement CA-SS03-2048.pdf`** where a public body is
also the network counterparty.

- This row must not steal the deciding authority's application, representations, determination,
  register, inspection or adverse-power case.
- `government.permit-licensing` must not steal a private or public network operator's customer-side
  agreement merely because its terms are mandatory or its letterhead looks official.

The landed government row expressly says possession of a permit/licence certificate does not prove
issuer-side custody. A network operator is not government by name. No collision edge is authored:
once role is required, the two activation structures are distinguishable, and the closest government
row does not reciprocate this template. The custody distinction is recorded as `role_split`.

### Business contract administration

Same fixture bytes: **`Executed Connection Agreement CA-SS03-2048.pdf`**.

- This row owns the agreement as evidence of one site's right and conditions to connect.
- `business_operations.contract-administration` owns the portfolio apparatus that runs signed
  contracts: multi-agreement register with notice dates/internal owner, clause-referenced obligation
  tracker, notice calendar, service-credit or renewal machinery.

That neighbour's own never-alone rule rejects an executed agreement by itself. Therefore the same
instrument can support this row without colliding at activation; administration needs additional
evidence. The role split is recorded, no unreciprocated collision edge is manufactured.

### Construction/property

Same fixture bytes: **`Connection Offer - CONN-2048 - Solar Farm A.pdf`** when it includes a priced
schedule of connection works.

- This row owns network/customer relationship, point/capacity, acceptance and enduring connection
  terms.
- construction/property owns the bounded works at a site: contract parties, work package, design,
  programme, valuation, practical completion and defects.

Connection works can occur inside the offer, but electricity vocabulary does not turn every works
pack into this row, and a works schedule does not erase the network relationship. No edge is added
because the closest landed construction row had no existing reciprocal seam and the relation is
settled by independently evidenced structures.

### Utility metering/billing sibling

Same fixture bytes: **`Electricity Bill June 2026 - MPAN 1200000000000.pdf`**.

- This row must reject it: meter point, billing period and consumption do not prove application,
  offer, agreement or operational notification.
- `resource_operations.utility-metering-billing` must not absorb the executed connection agreement
  merely because it names the same meter point and capacity; that template should require a
  read/consumption/charge series.

The sibling node had not landed at inspection time, so no silent assertion or edge is authored.
R1c should reconcile the boundary when both rows exist.

### Renewable generation sibling

Same fixture bytes: **`G99 Installation Document and Site Compliance Tests - SS-03.pdf`**.

- This row owns the DNO/customer connection relation and operational-notification consequence.
- `resource_operations.renewable-generation` should own recurring generation availability, output,
  curtailment and operating performance after connection.

The same commissioning form may support both situations on separate evidence, but the renewable
generation sibling had not landed and template coactivation cannot be authored here. R1c owns it.

## Proposed fields — exact list and objections

`fields` stays empty. This template seconds, but does not mint variants of, the six proposals already
on the `resource_operations` schema:

1. **`site`** — installation site, not Photos capture `location`. It is optional and flattened in a
   one-site corpus.
2. **`operating_authority`** — connection application/agreement reference and continuing terms. The
   hard question is whether the schema intended this proposal to cover private network agreements as
   well as public permits and tenures (NJ-GRID-2).
3. **`asset`** — connection point, bay, feeder, meter point, substation interface or protection
   installation; never a drawing number or arbitrary tag.
4. **`output_stream`** — at most import/export/bidirectional service distinction. No local
   `connection_type` synonym is minted, and raw capacity is never a folder value.
5. **`reporting_period`** — only recurring compliance/modification evidence; never an offer or
   energisation date and never first.
6. **`record_type`** — application, offer, agreement, notification, modification and related values.
   This seconds the schema's proposed reuse of canonical Finance spelling; R1c must globalize the
   role or replace it once, not mint `connection_document_type`.

No `connection_stage` field is proposed. Application, offer, acceptance, energisation and
modification are document functions or workflow states already expressible as `record_type` values;
minting a private stage key would recreate the synonym problem. Capacity, voltage, coordinates,
protection values, charges, queue status and notification conditions are important content/search
evidence but are high-cardinality, sensitive, mutable or legally qualified and unsuitable as default
destination dimensions.

## Recognition abstention boundary

Deterministic recognition is relational. A connection application needs roles plus a point/capacity
request. An offer needs executable acceptance apparatus. An agreement needs a continuing interface
and conditions. Commissioning and notifications need the same connection reference plus operator
and interface roles. A modification must trace to the parent agreement.

Never-alone items include electricity/network vocabulary, operator names, references, sites,
substations, meter points, capacity/voltage, diagrams, signatures, standards, form numbers,
witness columns, parent folders, source types and portal/download sessions. This implements the
design's observation/fact firewall: filenames and extracted slots are evidence; no path, legal
effect, current compliance, accepted capacity or energisation event appears unless its own evidence
supports it. Sparse email/calendar/image members can join an accepted group without copying site,
agreement, asset, capacity or event facts.

## Neighbours considered without an edge

- **`government.permit-licensing`** — role split, described above; an issued holder copy and an
  issuer-side continuing-permission case are distinguishable once custody/authority action is
  required.
- **`business_operations.contract-administration`** — one executed agreement does not satisfy that
  row's portfolio register/obligation-calendar grammar.
- **`construction_property.construction-project`** — priced network works can coexist with connection
  terms, but bounded works and continuing network relationship are separately evidenced.
- **`engineering.electrical-schematic`** — a single-line diagram is controlled design definition;
  it activates this row only when the application/agreement relation is also on the bytes or in an
  accepted, non-copying group.
- **`resource_operations.utility-metering-billing`** and
  **`resource_operations.renewable-generation`** — roster-valid siblings, not landed at inspection
  time. Their post-connection measured-series defaults differ from this connection lifecycle. R1c
  must audit the same-byte seams once those files land.
- **Finance** — fees, securities, invoices and ordinary bills may carry independent Finance facts,
  but the file set presented no unresolved same-evidence mutex that justified another template edge.
- **Legal** — connection agreements are legal instruments, but this placeholder template cannot
  author schema coactivation and the safety placeholder's independent activation remains available.

Only `engineering.commissioning-handover` gets a collision edge because it already authored the
reciprocal exact-byte seam and the same energisation/witness evidence genuinely competes at
activation. Extra topic-similarity edges would weaken the closed vocabulary.

## Template-level coactivation held for R1c

CONNECTION §5 allows `also_holds_with` only schema ↔ schema, never template ↔ template. Therefore
`also_holds_with` is deliberately empty. R1c should adjudicate or lift these intended cases at schema
level, using independently evidenced relations:

- resource operations + engineering for a commissioning pack that proves both connection status and
  installed-instance transfer;
- resource operations + business operations for an agreement plus genuine contract-register or
  obligation-management apparatus;
- resource operations + construction/property for a connection offer/agreement that also serves as
  a bounded works contract at a site;
- resource operations + government for a public authority's deciding case and the holder/operator's
  retained terms;
- resource operations + Finance for fees, securities or billing records that independently satisfy
  Finance.

No file receives one relation merely because the other is present.

## NEEDS-JOSEPH

1. **NJ-GRID-1 — electricity only or all networks.** The absorbed legacy row and all verified
   fixtures are electricity-specific. Options: (a) keep the row electricity-grid-specific and
   clarify the display name; (b) broaden only after gas/water/heat/telecom fixtures demonstrate the
   same roles; (c) split those networks into future templates if their detection/privacy differs.
   Current provisional rule is (a).
2. **NJ-GRID-2 — scope of `operating_authority`.** Does the schema proposal include a private
   connection agreement/application reference, or only permit/tenure/quota/concession roles? Options:
   widen one neutral continuing-authority key, keep the key public-authority-specific and refuse this
   dimension, or adjudicate a genuine role split. No local synonym is minted.
3. **NJ-GRID-3 — identifiers as destinations.** A connection reference materially joins the whole
   lifecycle, but a branch label can reveal a live project or infrastructure relationship. Options:
   destination-eligible by default, metadata-only by default, or policy/template-dependent with a
   redacted display label. JSON seeds true only as a proposal with flatten/protection warnings.
4. **NJ-GRID-4 — schema coactivation with engineering.** The reciprocal template collision says one
   package may independently prove both relations, while CONNECTION forbids template
   `also_holds_with`. R1c must confirm the existing resource_operations ↔ engineering schema
   coactivation is the intended lift and ensure the P6/P8 discriminator reads this row's `signal`.

## Claims and self-audit

The row claims only an evidence-backed electricity-connection situation. It does not claim a
jurisdiction's mandatory form set, deadlines, current engineering recommendation, legal effect,
operator list, threshold, regex, capacity rule, authenticity or final tree. External sources support
recurring structures only. Work types remain values.

`fields` and serialized `dimension_order` are empty. The exact proposed-fields list is `site`,
`operating_authority`, `asset`, `output_stream`, `reporting_period`, `record_type`, all seconding the
schema rather than minting variants. Every source type is in `SOURCE_TYPES`. Every edge endpoint is
roster-valid. `collides_with` contains one exact `{domain, signal, provenance}` object; its signal
states Direction one, Direction two, and the same fixture bytes already named by the landed reciprocal
row. `also_holds_with` is empty. Fallthroughs use named residuals. No file example writes a folder
path as a fact, and sparse files explicitly group without copying facts.
