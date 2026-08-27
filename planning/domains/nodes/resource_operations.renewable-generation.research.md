# `resource_operations.renewable-generation` — R1b research memo (J-DEPTH)

Date: 2026-08-27  
Assignment: `kind: template` · `schema_id: resource_operations` · `launch: placeholder`

## Verdict

**Keep narrowly; do not refuse in R1b.** The row is not licensed by the words *renewable*, *solar*
or *wind*, and it is not licensed by a file format or a work type. Its defensible object is the
recurring **installation-and-output-period packet** that joins four roles:

1. an installed generator and its production/export meters;
2. actual generated or exported energy for a stated period;
3. availability, curtailment, downtime or another explanation of lost output; and
4. a settlement, incentive claim or renewable-certificate consequence derived from those same
   readings.

The strongest charge is that this is already the `resource_operations` schema's default. That
anchor explicitly recognizes “a generation or grid-connection record joining plant and unit/meter
identity to dispatch/export intervals, availability, curtailment or outage codes, and energy units”
and lists generation, outage and dispatch records among its work-type values. If this row meant only
`technology = solar | wind | hydro`, refusal would be mandatory: technology is a value, not a node.

The row survives only because the file set below repeatedly adds the **consequence of measured
output**—a settlement, payment claim or certificate register—and because its recommended projection
is shallower than the schema default. A renewable generator ordinarily has one continuing authority
and one output stream (electricity); filing first by those values creates one-child levels. The useful
projection is installation/site, then asset where it materially separates units, then output period,
then record function. This is an applicability-template distinction, not a new fact schema.

This survival is deliberately reversible. If R1c finds that real corpora contain isolated meter
exports and invoices rather than repeated installation-period packets, it should set
`refuse_node: true` and route the material through the `resource_operations` default,
`engineering.commissioning-handover`, `resource_operations.grid-connection`, Finance, and the named
residuals. No data or neighbour depends on manufacturing a renewable category.

## Authority and method

Binding local sources used:

- `planning/domains/dispatch/RESEARCH-BRIEF.md` and the complete stamped output of
  `python3 planning/domains/dispatch/make_prompt.py resource_operations.renewable-generation`.
- `planning/00-database-agent-product-design.md`, authoritative for observation/fact separation,
  extraction, never-alone evidence, privacy, grouping, templates and residuals.
- `planning/01-product-design-structured.md`, used as a locator only; `00` wins.
- `planning/prompts/ALIGNMENT.md`, `planning/domains/_CONTRACT.md`, `CONNECTION.md` and
  `CONNECTION-EXAMPLES.md` for the schema/template node test, activation/grouping firewall, closed
  edge vocabulary, same-evidence collision semantics and schema-only `also_holds_with` rule.
- `planning/overnight/council/DECISION-BRIEF.md` for ratified D1, D4, D6, J-IND and J-DEPTH. D1/PR-6
  keeps this placeholder fieldless; J-DEPTH overrules the stamped prompt's retired gist label.
- `planning/domains/roster.json`, `ROSTER.md`, `canonical_fields.json` and
  `src/evidence_shape/vocabulary.py` for assignment, endpoint existence, canonical keys and the
  closed `SOURCE_TYPES` list. The actual vocabulary includes `contacts`; this row has no contact
  example and therefore does not list it as plausible.
- The complete `resource_operations` schema node and memo, and the landed launch-depth
  `identity.core-documents` pair for depth and JSON idiom.
- Landed neighbour rows `engineering.commissioning-handover`,
  `government.grant-programme-administration`, `business_operations.budget-forecast` and
  `finance.small-business-bookkeeping`, plus `finance.subscriptions-utilities` as a considered
  utility-bill boundary. No neighbour was edited. The roster-valid renewable siblings
  `resource_operations.grid-connection` and `resource_operations.utility-metering-billing`, and
  `manufacturing.energy-audit`, had no landed node file when this row was written; their roster hints
  and relevant landed schema anchors were used, and reciprocity remains R1c's obligation.

External primary/official sources were used to verify that the named records and slot relations are
real, not to import a jurisdiction's thresholds, regexes, tariff rules or field vocabulary:

- [NREL, *Best Practices for Operation and Maintenance of Photovoltaic and Energy Storage Systems*](https://www.nrel.gov/docs/fy19osti/73822.pdf)
  distinguishes high-level production/revenue measures from the more detailed inverter health,
  availability, downtime and grid-interaction evidence needed by O&M providers. It supports the
  performance-report and operational-scorecard fixtures.
- [NREL, *Solar Powering Your Community*](https://www.nrel.gov/docs/fy11osti/47692.pdf) describes
  commissioning as post-installation testing/certification and ties it to monitoring and long-term
  O&M. It supports the commissioning-to-operational-baseline seam; it does not license assuming that
  every commissioning file is an operating record.
- [AEMO, publishing actual intermittent-generator SCADA availability data](https://aemo.com.au/energy-systems/electricity/national-electricity-market-nem/nem-forecasting-and-planning/operational-forecasting/solar-and-wind-energy-forecasting/updates-and-initiatives/publishing-actual-intermittent-generators-availability-data)
  names generator/dispatch-interval data including local limit, turbines or inverters available and
  quality flags. [AEMO's generation-and-load page](https://www.aemo.com.au/energy-systems/electricity/national-electricity-market-nem/data-nem/market-management-system-mms-data/generation-and-load)
  confirms that actual generation is distributed in CSV-shaped data. These sources support the SCADA
  fixture without making a public market file evidence that the corpus holder operates the plant.
- [Ofgem, RO guidance for generators](https://www.ofgem.gov.uk/guidance/renewables-obligation-guidance-generators)
  and the [generator data-submission overview](https://www.ofgem.gov.uk/environmental-and-social-schemes/renewables-obligation-ro/generators)
  verify the recurring operator-side relation among a generating station, output data, evidence of
  meter readings and certificate issuance.
- [Ofgem, REGO submitting data and managing certificates](https://www.ofgem.gov.uk/environmental-programmes/rego/applicants/rego-submitting-data-and-managing-certificates)
  verifies a station/output-period/output-quantity submission and later certificate transfer or
  retirement events. The row uses that relational structure, not a UK-only field enum.
- [Ofgem, FIT guidance for generators](https://www.ofgem.gov.uk/sites/default/files/2024-09/Guidance_for_FIT_Generators_V18.pdf)
  verifies generation/export meter readings, photographic meter verification and the link to
  payment administration. It supports the meter-photo and output-statement fixtures while leaving
  eligibility, accuracy and payment status unknown.

No external source is represented as Joseph's design authority. No numeric threshold, mandated
frequency, jurisdiction-specific certificate type, authenticity test or tariff rule enters JSON.

## J-DEPTH node test — all three legs

### Leg 1: detection signals differ from the schema default

The schema default is deliberately broad: it recognizes an operating source/site, authority or
asset joined to measured output or environmental performance. It must cover a quarry, farm, forest,
fishery, well, utility meter and generator without knowing which industry word appears.

This row adds a narrower relational test. A positive file or packet must identify a generating
installation and output period, carry actual generation/export evidence, and connect that output to
either operational performance/loss or a financial/certificate consequence. The most robust shapes
are:

- generator or unit identity + interval + generated/exported value + unit + quality flag;
- plant identity + actual output + expected output + availability/curtailment/downtime + action;
- accredited station + output period + meter readings + claimed certificate/payment quantity;
- station + period + measured generation + certificate identifier/status + transfer/retirement;
- export meter + settled quantity + tariff/adjustment + settlement amount, where the meter-to-output
  chain governs the record rather than an invoice face alone.

Each is true of a concrete file below. Each can be falsified by deleting one role. Delete actual
output from the performance workbook and it becomes a forecast or investment case. Delete the
network offer and technical conditions from the grid-connection file and it no longer proves a
connection workflow. Delete the invoice face from a PPA invoice and Finance may no longer own it,
but the metered-output annex still supports this row. Delete the metered annex and it is only an
invoice. This deletion test is stronger than renewable vocabulary or extension matching.

### Leg 2: recommended dimensions differ, conditionally

The schema anchor's researched default is:

`site -> operating_authority -> output_stream -> reporting_period -> record_type`

with an asset-led alternative. For this situation, `operating_authority` and `output_stream` are
usually poor default levels: one installation normally has one continuing authority and produces
one output stream, electricity. They add depth without separating files. The useful conditional
order is:

`site -> asset -> reporting_period -> record_type`

For a small installation, flatten further to:

`site -> reporting_period -> record_type`

Asset is useful only when the corpus contains repeated unit-level records: turbine availability,
inverter work, meter verification or generator-unit output. It must flatten where it would create
one folder per device with one file. Time is not first: a year-first tree scatters one installation's
commissioning baseline, meter evidence, performance history, certificate series and settlement
history. Quantity, tariff, price, certificate count, meter serial and performance ratio remain
content/search evidence and never folder dimensions.

This leg is **conditional**, not silently implemented. The schema declares no fields under PR-6, so
`template.dimension_order` is correctly empty. The prose reuses the anchor's proposals and mints no
template-private key.

### Leg 3: privacy rule differs in reason and minimum evidence

The schema is already `potentially_sensitive`, but its general rationale spans concession rights,
reserves, coordinates, environmental breaches and critical infrastructure. Renewable generation has
a more specific compound exposure:

- interval output, availability, local limit, curtailment and outage timing can expose live operating
  state and weaknesses;
- site, generator, inverter, turbine and meter identities can expose physical infrastructure;
- PPA tariffs, expected-versus-actual performance, incentive claims, certificate holdings and
  settlements expose commercial position;
- meter images, portal receipts, invoices and settlement annexes can expose account references,
  bank details or access information.

That changes how much evidence should be surfaced. Header slots, bounded table excerpts and archive
manifests are preferable to full raw exports; bank- or credential-bearing members route locally and
redacted. Public AEMO or certificate data does not lower the posture of private files beside it. The
row still assigns only `potentially_sensitive`; P7 owns handling classes.

## Concrete files — positive, ugly and false

### Positive and mixed fixtures

1. **`PV-17_Commissioning-and-Performance-Test.pdf`** (`text_document`). Installed array, inverter
   and meter identities; witnessed expected-versus-recorded tests; acceptance signatures; and an
   initial-reading/baseline section. Engineering owns the acceptance-and-transfer evidence. This row
   owns the operational baseline only when it is explicit. It does not prove later production,
   continuing compliance or legal acceptance.

2. **`PV-17_Generation_2026-06.csv`** (`spreadsheet`). Generator and inverter identifiers, interval
   bounds, generated/exported energy, units and substitution flags. It is the clean recurring output
   file. The filename date is not the fact; the labelled interval rows are evidence. It must not
   receive site or period from a neighbouring statement.

3. **`PV-17_Export-Meter_Statement_June-2026.pdf`** (`text_document`). Generator/payee and supplier
   roles, generation/export meters, readings, settled quantity, tariff and amount. Generator role
   plus measured-output chain supports this row; customer/service-account usage supports the utility
   sibling; a Finance account structure may independently activate Finance.

4. **`PV-17_Performance-and-Revenue_June-2026.xlsx`** (`spreadsheet`). An Actual Output sheet carries
   generation/export, availability and curtailment; a Revenue Reconciliation sheet carries settled
   quantity and adjustments; a Forecast sheet carries assumptions and variance commentary. The
   workbook is intentionally mixed. Sheet membership does not copy forecast status, actual status or
   period to every sheet.

5. **`PV-17_Incentive-Claim_Q2-2026.pdf`** (`text_document`). Applicant/generator and administrator
   roles, accredited station, meter readings, claimed quantity, declaration and receipt. The same
   bytes are operator-side evidence on one disk and authority-side administration on another.
   Branding and addressee are never enough to decide custody.

6. **`REGO_Output-and-Certificate_Register_2026.xlsx`** (`spreadsheet`). Station, output period,
   measured generation, certificate identifiers/statuses and transfer/retirement events. The file
   shape is real; the row does not claim a certificate is valid, owned or environmentally dispositive.

7. **`WindFarm-WF02_SCADA_Availability_2026-06.csv`** (`spreadsheet`). Generator, dispatch interval,
   local limit, turbines available and quality flag. Availability is not generation; a missing count
   does not prove an outage cause. A public publisher does not become the operator.

8. **`Meter-MP-7812_Reading_2026-06-30.jpg`** (`image`). EXIF capture time plus OCR-visible meter
   reference, digits and unit, but no installation/output-period/submission relation. It may join an
   accepted meter group without receiving those facts. Inactive, it is One-Off Images.

9. **`PV-17_PPA-Settlement-Invoice_June-2026.pdf`** (`text_document`). The invoice face is Finance:
   parties, invoice identifier, line item, terms, amount and bank details. The annex is renewable
   evidence: export meter, output period, settled quantity and tariff. Neither reading erases the
   other; payment and meter validity stay unknown.

10. **`Renewable-Generation-Packet_2026-06.zip`** (`archive`). Its manifest lists commissioning,
    generation, meter image, claim, certificates and settlement, but exposes two meters and two
    periods. The archive is not unpacked, and one member's installation/period cannot propagate to
    the others.

11. **`PV-17 meter-reading reminder.ics`** (`calendar`). A reminder to submit a reading, not a
    reading or submission record. Calendar is a source type, not a renewable domain. It may group as
    context without writing any operational fact.

### Tempting files rejected from this row

- **`Inverter-04_Cleaning-Work-Order.pdf`**: renewable asset vocabulary plus fault, labour and
  return-to-service structure. It is a maintenance/work-order record. Without generation period,
  loss reconciliation or output consequence, this row must not steal it.
- **`Solar-Farm-Investment-Case.pptx`**: proposed capacity, forecast output, forecast revenue,
  scenario assumptions and an approval ask. This is business planning, not evidence that a plant
  exists or produced anything.
- **`Grid-Connection-Offer_PV-17.pdf`**: network applicant/operator roles, connection point, export
  capacity, technical conditions and acceptance slots. It establishes a proposed/accepted network
  relationship, not actual generation or earnings.
- **`PV-17 Array Layout Rev C.dwg`**: a controlled design artifact; engineering owns design item,
  revision/status and technical definition. Solar vocabulary does not change its role.
- **`PV-17 Inverter-04 Replacement Work Order.pdf`**: maintenance execution. It may join an accepted
  outage group without becoming a generation fact or a performance report.
- **`Green Energy Market Outlook.pdf`**: published reading material about renewable generation,
  prices and certificates. It falls to Reading Inbox when no research group exists.
- **`PV Portfolio Forecast FY27.xlsx`**: expected generation and revenue by site with scenario
  assumptions but no actual meter or operating record. Budget/forecast owns it.
- **`Electricity Bill - Workshop - June.pdf`**: customer consumption, service account, tariff and
  amount due. Finance/subscriptions-utilities owns it; a solar credit line does not turn the bill
  into the generator's operating packet.
- **`Meter Inspection Appointment.eml`**: an appointment or proposed visit. Until a reading,
  verification result or submission appears, it proves no output.
- **`public_dispatchSCADA_202606.csv`**: a public market dataset may have genuine generation values,
  but it does not prove the corpus holder operates any generator. It is reference/data unless an
  accepted operator corpus supplies independent custody evidence; grouping cannot activate.

The collision fixture that looks most like this row but is not is
`Solar-Farm-Investment-Case.pptx`: it contains every attractive token—capacity, solar, generation,
revenue, year and performance chart. The discriminator is actuality. Its values are assumptions and
scenarios supporting an approval decision, not meter-derived output from a commissioned installation.

## Proposed fields — deliberately none

`fields: []` is binding because the `resource_operations` schema is a PR-6 placeholder.
`proposed_fields: []` is also deliberate. This template does not need a private renewable key and
must not duplicate the anchor's six proposals:

- `site` for the operating installation/place;
- `asset` for generator, turbine, inverter or meter where unit-level retrieval matters;
- `output_stream` for generated/exported electricity if R1c keeps that role;
- `reporting_period` for the period measurements are about;
- `record_type` for generation report, settlement, claim, certificate register and similar values;
- `operating_authority`, which is real evidence but usually a poor default folder level here.

The tempting additions were rejected:

- `technology`: solar/wind/hydro is a value, usually a one-child level within one installation;
- `scheme` or `incentive_programme`: a programme is a counterparty/authority context and should not
  be minted by one template. It can remain a work-type/grouping observation until multiple schemas
  justify a canonical role-safe key;
- `meter_id`: an asset value, not a new field; raw serials are privacy-loaded folder names;
- `generation_quantity`, `revenue`, `tariff`, `availability`, `curtailment` or `certificate_count`:
  high-cardinality, sensitive, period-dependent values suitable for content/search/explanation, not
  destination dimensions;
- `technology_type`, `certificate_type` and `claim_type`: work-type or output values, not nodes or
  schema keys.

Facts currently legal in examples are only the universal keys supported by their own evidence:
`file_type`, `creation_date`, `language`, `duplicate_family`, `version_family` and
`sensitivity_status`. `download_session` remains a possible universal clue but is never proof of
topic. No file example writes a folder path or a proposed schema field as a current fact.

## Reciprocal boundaries — same bytes, both directions

Every JSON collision uses a roster-valid same-kind endpoint, carries `provenance`, and names the
same fixture bytes in both directions. These are outward R1b arguments; R1c still owes serialized
reciprocity where the neighbour did not already name this row.

### Engineering commissioning and handover

**Same bytes: `PV-17_Commissioning-and-Performance-Test.pdf`.** This row must not steal the witnessed
test sequence, installed-instance reconciliation, acceptance signatures or transfer act: those are
`engineering.commissioning-handover`. Engineering must not steal the initial operating baseline and
later generation/performance section merely because it sits inside the commissioning report. A
pass/fail grid counts for neither side alone.

### Grid connection

**Same bytes: `PV-17_Export-and-Curtailment_June-2026.csv`.** This row owns actual generated/exported
quantities, availability, curtailment and plant-loss roles. `resource_operations.grid-connection`
owns connection reference, network-issued limits, protection/compliance fields and events under the
network agreement. This row must not treat an export limit as actual export; the grid row must not
treat measured output as proof of connection compliance.

### Utility metering and billing operations

**Same bytes: `PV-17_Export-Meter_Statement_June-2026.pdf`.** This row owns the generator/payee side:
generation/export readings reconciled to output and earnings. The utility sibling owns the
supplier/customer service-account side: consumption, service period, tariff and bill. This row must
not capture an ordinary utility bill with a solar-credit line; the sibling must not capture a
generator settlement because it has an amount and meter reference.

### Manufacturing energy audit

**Same bytes: `PV-17_Performance-and-Revenue_June-2026.xlsx`.** This row owns Actual Output and Revenue
Reconciliation: generation, export, availability, curtailment and settled quantity. The audit row
owns a Consumption Baseline and Measures structure: consuming loads, efficiency opportunities,
savings and payback. This row must not steal energy-consumption optimization; the audit must not
steal generation performance. An energy unit or actual-versus-expected chart is neutral.

### Government grant/incentive administration

**Same bytes: `PV-17_Incentive-Claim_Q2-2026.pdf`.** This row owns the generator declaration and
meter/output annex. The government row owns authority-side receipt, review, exception, approval and
payment across applicants. The generator must not acquire government custody from a logo/addressee;
government must not erase the submitted file's operator-side output evidence.

### Business budget and forecast

**Same bytes: `PV-17_Performance-and-Revenue_June-2026.xlsx`.** This row owns measured actual output,
loss and settlement. `business_operations.budget-forecast` owns assumptions, scenario cases,
planning-round approval and plan-versus-actual commentary. This row must not turn forecast into
generation; budget-forecast must not turn the actual meter sheet into a plan.

### Finance bookkeeping

**Same bytes: `PV-17_PPA-Settlement-Invoice_June-2026.pdf`.** This row owns the metered-output annex.
`finance.small-business-bookkeeping` owns the invoice face and account/payment structure and brings
Finance protection. This row must not infer payment or bookkeeping status from an output annex;
Finance must not erase the operational meaning of a settlement annex merely because it is attached
to an invoice.

## Template coactivation — research only, not an edge

`also_holds_with` is empty because CONNECTION §5 limits it to schema↔schema edges. This template row
authors no template-level coactivation. R1c/P10 should nevertheless adjudicate these intended
applicability combinations, recorded here rather than smuggled into JSON:

- `engineering.commissioning-handover` + this row when one commissioning report contains both a
  transfer act and an explicit operational baseline;
- `business_operations.budget-forecast` + this row when one workbook has separately evidenced
  forecast and actual-output sheets;
- `finance.small-business-bookkeeping` + this row when a PPA invoice includes a metered-output annex;
- `government.grant-programme-administration` + this row when identical claim bytes carry both
  applicant output evidence and authority-side review evidence under different custody;
- Photos schema facts + this row for a meter image whose capture evidence and operating submission
  relation are independently supported.

These are not permissions to copy facts or select two paths. They are evidence that later template
composition may need more than one applicability source while each row remains bound to one schema.

## Neighbours considered without an edge

- **`finance.subscriptions-utilities`** was read because a customer utility bill can contain
  generation credit, meter and tariff information. The sharper same-schema sibling is
  `resource_operations.utility-metering-billing`, and Finance's own collision surface already
  covers the customer bill. Adding both would duplicate the same seam. The bill remains an explicit
  rejected file.
- **`research`** was considered for performance studies, resource assessment and forecasting.
  Research organizes knowledge production by project/stage/artifact; this row organizes recurring
  operation by installation/output period. The file set contains no same-byte ambiguity that cannot
  be settled by actual operating readings versus study/forecast structure.
- **`construction_property`** was considered for solar installation, planning approval and practical
  completion. Before acceptance those are construction/engineering records; after acceptance the
  recurring output packet is operational. The sharper boundary is already represented through
  commissioning and grid connection, and no extra same-byte fixture justified another edge.
- **`nonprofit.grant-reporting`** was considered for community-energy grant claims. The relevant
  discriminator is grant recipient versus awarding body, already represented by the government
  administration edge; an operator need not be nonprofit, and organisation type alone is a value.
- **`photos`** was considered for meter, panel, damage and site images. Capture facts may coexist,
  but image origin and operational purpose are independently evidenced and not a template collision.
  The sparse meter image explicitly groups without fact copying.
- **`legal`** was considered for PPAs, land leases, warranties and scheme terms. The agreement creates
  obligations; this row records output/performance under them. A signed PPA may activate Legal on its
  own clauses, but the recurring invoice/settlement seam is more precisely Finance and no template
  edge to a broad legal row is needed.

## NEEDS-JOSEPH / merge questions

1. **NJ-REN-1 — node or schema-default value?** Keep only if the recurring
   generation→availability/loss→payment/certificate packet and asset/period projection materially
   improve P10. Refuse if real corpora contain only generic meter exports plus isolated invoices.
   The refusal route is fully specified above.
2. **NJ-REN-2 — earnings boundary.** When a settlement or incentive claim carries a metered-output
   annex, should P10 select this applicability source, Finance/government, or both? The evidence sets
   remain separate today; template-level coactivation is not authored.
3. **NJ-REN-3 — commissioning cutover.** Does an explicit operational-baseline section make this row
   applicable before the first recurring output period exists, or does engineering retain the whole
   file until post-acceptance data arrives? Current recommendation: require the baseline relation;
   a test/acceptance file alone stays engineering.
4. **NJ-REN-4 — certificate/incentive programme depth.** Is programme/scheme ever a reusable folder
   dimension? Current recommendation: no new field; keep it as record-type/work-type or grouping
   evidence unless several schemas justify a global key.
5. **NJ-REN-5 — asset granularity.** Asset-first helps multi-unit plants and meter histories but can
   produce many tiny folders. Decide whether it is a default, an optional branch, or automatically
   flattened unless the corpus contains repeated per-asset records.
6. **NJ-REN-6 — public/private split.** A public SCADA or certificate dataset can be low-risk while a
   private performance/settlement packet is sensitive. Should P7 classify members independently and
   allow one group to contain both, or should the strictest member govern all previews and template
   fitting for the group? This row recommends per-member protection plus redacted group summaries.

## Refusal and self-audit position

Current refusal status: `refuse_node: false`, with an explicit R1c refusal trigger and complete
fallthrough route. The row makes no claim that renewable technology is a schema, that an output value
is valid, that a certificate establishes ownership, that a claim was accepted, or that a settlement
was paid. It claims only that the recurring relational packet is a useful proposed template.

Mechanical and content checks completed after writing:

- `python3 -m json.tool` parsed the JSON successfully;
- all fourteen file examples use a member of `SOURCE_TYPES`;
- all seven collision endpoints exist in `roster.json`, are `kind: template`, and every collision
  object has exactly `domain` + `signal` + `provenance`;
- all seven collision signals contain `Direction one`, `Direction two` and `Same fixture bytes:`;
- `fields`, `proposed_fields`, `dimension_order` and `also_holds_with` are empty;
- every residual target is one of the nine names and all five residual design citations match a
  verbatim byte span in `00`;
- `git diff --check` for this pair returned no whitespace errors; isolated no-index diff inspection
  showed 565 JSON lines and 440 memo lines before this final audit-note update.

No roster, schema anchor, neighbour, canonical field, source file, test, planning document or git
state is changed by this row.
