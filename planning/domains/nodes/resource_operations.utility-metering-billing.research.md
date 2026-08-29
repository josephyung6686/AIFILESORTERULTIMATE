# resource_operations.utility-metering-billing — research memo (R1b, J-DEPTH)

Date: 2026-08-27
Roster row: `kind: template` · `schema_id: resource_operations` · `launch: placeholder`
Legacy coverage: `util.metering-billing` (ROW)

## Verdict

**Keep provisionally; do not refuse.** The strongest charge is real: the `resource_operations`
schema default already names a utility meter-read or settlement export, and the Finance template
`finance.subscriptions-utilities` already owns utility statements and usage records on the
customer-account side. A child row called merely *utility billing* would therefore fail the node
test and should be refused.

The narrower row survives on a relation neither default states completely: the supplier- or
network-operator-side audit chain **service point → meter/register → reading provenance and
quality → consumption derivation → tariff/rate version → billing run → exception/rebill**. A
customer bill may be the rendered output of that chain, but supplier custody is not inferred from
the bill's appearance. A raw meter file may be an input, but it does not activate this template
until its own evidence connects it to billing or an accepted billing workflow. This is a
provisional survival because R1c may still rule that the chain is a `work_type` family on the
resource schema default or that billing belongs wholly to Finance.

The row is field-less. `fields`, `proposed_fields` and executable `dimension_order` are all empty.
No supply-point, meter, customer, tariff, reading, quantity or exception key is minted.

## Authority stack and method

Read and applied:

- `planning/domains/dispatch/RESEARCH-BRIEF.md`, including the 2026-08-24 J-DEPTH override.
- The complete stamped output of
  `python3 planning/domains/dispatch/make_prompt.py resource_operations.utility-metering-billing`.
- `planning/prompts/ALIGNMENT.md` and the authoritative
  `planning/00-database-agent-product-design.md`. `planning/01-product-design-structured.md` was
  used only as a locator; `00` wins.
- `planning/domains/CONNECTION.md`, `CONNECTION-EXAMPLES.md` and `_CONTRACT.md`, especially the
  node test, activation/grouping firewall, closed edge vocabulary and schema-only
  `also_holds_with` rule.
- `planning/domains/canonical_fields.json`, `planning/domains/roster.json`, `ROSTER.md` section 4
  and Appendix A, and `src/evidence_shape/vocabulary.py`.
- `planning/overnight/council/DECISION-BRIEF.md`: D1–D6, J-IND and J-DEPTH are carried as ratified.
- The landed `resource_operations` schema JSON and memo, and the launch-depth
  `identity.core-documents` JSON and memo as structural/depth calibration.
- Existing neighbour material was checked without editing it: the `engineering`, `government`
  and `business_operations` anchors; `engineering.commissioning-handover`;
  `business_operations.corporate-regulatory-filings`; `finance.subscriptions-utilities`; and
  `construction_property.inventory-inspection`. The renewable-generation sibling exists in the
  roster but had no landed node file at inspection time.
- The superseded legacy `util.metering-billing` row in
  `planning/domains/13-trades-property-logistics.json`. Its concrete distinction among supply
  point, meter, supplier, reading, reading type, period and tariff was treated as research debt,
  not as authority to recreate seven private fields.

No jurisdiction's identifier format, tariff law, market role vocabulary, threshold, form number,
statistic or detector regex is claimed. The named files below are fixture-grade document forms and
the recognition conclusions are marked inference/proposal, not statutory assertions.

## J-DEPTH node test — all three legs

### 1. Detection signals differ from the schema default

The `resource_operations` default is broad and relational: authorised source/site, operating
unit/asset, measured output or environmental performance, and reporting period. It explicitly
recognises utility meter-read and settlement exports. That default legitimately takes a clean
meter interval export or meter register even when there is no billing.

This child requires the additional *calculation lineage*. At least one own-file structure must
connect readings to bill or settlement consequences: read source/quality to accepted consumption;
accepted consumption to an effective tariff/rate version; or billing-run input to controls,
exceptions, cancellations and replacement output. `Meter-Reads_SP-10482_2026-07.csv` is therefore
not enough by itself. `Bill-Calculation-Trace_SP-10482_2026-07.pdf` is enough because labelled
blocks connect the register reads, multiplier, consumption, rate version, charge components,
billing run and replacement-bill state.

That is not an extension-based distinction and not a list of work-type words. It is a different
evidence graph inside one file or bounded packet. The negative rule is as important as the
positive: supplier, service address, meter serial, usage and amount due are all never-alone.

### 2. Recommended dimensions differ from the schema default

The anchor's researched default is held in prose as
`site → operating_authority → output_stream → reporting_period → record_type`, with an asset-led
alternative for utilities and generation. That is suitable across mines, farms, forests, wells,
generation assets and environmental returns.

This situation's narrower recommendation is
`site/service point → reporting_period → record_type`, inserting `asset/meter` only when one
service point genuinely carries multiple meters/registers. `operating_authority` and
`output_stream` are omitted: in a supplier billing corpus they tend to repeat, and forcing them
creates one-child levels. Raw customer/account identifiers, readings, quantities, tariffs and
exception codes do not become folder dimensions. This is not time-first. The exact design sentence
used in JSON is: **"For document and record domains, project, function, or subject usually comes
before time because putting year first scatters related work across calendar folders."**

The order is non-executable today because the placeholder schema declares no fields. That is not
smoothed over: `dimension_order` remains empty, and R1c must license any reusable anchor proposals
before P10 can compile the recommendation.

### 3. Privacy differs from the schema default

Generic resource operations can be commercially or infrastructure sensitive. This child adds a
different and frequent join: customer or tenant identity + service address + account/meter
identifier + granular consumption + payment/dispute/exception state. The same interval series that
is an ordinary production measurement at schema level can reveal household occupancy or a
business's operating pattern when joined to a named service point. The row therefore remains
`potentially_sensitive`, asks recognition to use labelled structures and minimum excerpts, and
routes customer-linked packets to Protected Records when no deeper group is accepted.

This is not a handling class; P7 owns that vocabulary. No raw identifier, quantity, tariff or
customer name is proposed as a destination field.

### Node-test conclusion

The row clears all three legs only in its narrow form: meter-to-charge detection, service-point
then period/document-function recommendation, and customer-usage privacy. If R1c finds that these
are already the resource default's normal work types and privacy rules, refusal is the required
outcome. The row does not survive merely because the legacy catalogue contained it.

## Bottom-up file set

The JSON carries thirteen full observation/fact fixtures. The decisive set is:

1. **`Billing-Run_Control-Totals_2026-07.xlsx`** (`spreadsheet`). Rows join account/service-point
   references to reading state, consumption, tariff version, charge, exception and run controls.
   This is the clearest internal supplier fixture. Legal facts are universals only; no resource
   field exists yet. A run month in the filename does not become a reporting period.

2. **`Meter-Reads_SP-10482_2026-07.csv`** (`spreadsheet`). Stable service point, meter, register,
   timestamps, reads, units, sources and validation states appear, but no tariff or bill-run link
   survives. It can join a billing group without copying the group's account, supplier or period.
   Alone it is schema-default metering or Review Later, not this child.

3. **`Bill-Calculation-Trace_SP-10482_2026-07.pdf`** (`text_document`). Labelled previous/current
   reads, multiplier, consumption, tariff version, effective dates, charges, billing run and
   replacement state form the full chain. It still does not prove legal correctness of the rate
   or calculation.

4. **`Rebill-Case_BR-8871.pdf`** (`text_document`). The packet contrasts estimated and corrected
   reads, records an approval and cites the cancelled and replacement bills. A dispute does not
   prove the customer is right, and a correction does not prove meter fault.

5. **`Your meter read was accepted.eml`** (`email`). Native message fields and the body provide
   a submitted read and acceptance state. It is a useful group member and a Receipts and
   Confirmations candidate, but it does not independently expose the full meter-to-bill chain.

6. **`Final Utility Statement - Account 0042.pdf`** (`text_document`). This is the Finance
   collision fixture. Provider/account/period/amount-due structure supports the customer-account
   row; meter reads, multiplier, consumption and tariff calculation support the supplier-side
   operational reading. Rendered bytes do not reveal whose corpus copy this is, so custody cannot
   be guessed.

7. **`Monthly-Metering-Return_2026-07.xlsx`** (`spreadsheet`). Cover, declaration and submission
   receipt support the compelled-filing row; service-point/meter/read-quality detail supports this
   row. It is the exact reciprocal fixture for the already-landed
   `business_operations.corporate-regulatory-filings` edge.

8. **`Bidirectional-Interval-Data_SP-7781_2026-07.csv`** (`spreadsheet`). Import and export
   registers, interval timestamps and quality flags can describe customer supply or renewable
   generation. With neither billing nor generation-asset anchors, it activates neither child and
   goes to Review Later.

9. **`Meter-Accuracy-Test-Certificate_MTR-771.pdf`** (`text_document`). Reference standard,
   procedure, test points, deviations and pass/fail make controlled engineering verification.
   Meter vocabulary and numbers do not make supplier billing; later group membership cannot copy
   that use onto the certificate.

10. **`Tariff-Decision-and-Price-Cap_2026.pdf`** (`text_document`). Authority decision, policy
    analysis and effective date make government/regulatory reference material. It becomes a
    supplier billing input only if an independently evidenced implementation record says so.

11. **`Move-in Meter Reading and Keys.jpg`** (`image`). An inventory heading, property address,
    keys/fobs and tenant acknowledgement make the move-in inspection context. The meter pairs may
    be submitted later, but the image does not prove the supplier accepted them. Photos facts stay
    independent.

12. **`Billing-Cycle-2026-07_Audit-Packet.zip`** (`archive`). The manifest lists read ingestion,
    validation, calculation, controls and rebill members across several service points. It is
    inspected without unpacking and cannot donate one service point's facts to all members.

13. **`service-bills-protected.pdf`** (`opaque_binary`). The filename is the only semantic-looking
    evidence. Encryption defeats activation; the correct outcome is Unsupported or Encrypted.

The set covers labelled and sparse structured data, prose, email, OCR/image, archive and unreadable
formats. It includes the happy chain, three same-byte collisions, grouping without propagation,
multi-schema evidence and explicit abstention.

## Reciprocal boundaries and same-byte collision fixtures

### Finance customer account

**Same bytes:** `Final Utility Statement - Account 0042.pdf`.

- This row may own the meter-to-charge pages: meter/register, previous/current read, read type,
  multiplier, derived consumption, effective tariff and charge calculation.
- `finance.subscriptions-utilities` owns the standing account pages: institution/provider,
  account/service relationship, covered period, amount due, payment and closure/renewal state.

The rendered statement can support both schemas on disjoint structures. This row authors only the
template collision because template-level `also_holds_with` is forbidden. The Finance neighbour
had landed without a reciprocal collision to this then-unwritten row; R1c owes reciprocity and the
schema-level coactivation decision. Shared provider, address, period and amount allocate neither.

### Corporate regulatory filing

**Same bytes:** `Monthly-Metering-Return_2026-07.xlsx`.

- This row owns service-point, meter/register, accepted/estimated/substituted measurement and
  operational total structures.
- `business_operations.corporate-regulatory-filings` owns the compelled return, obligated entity,
  deadline/declaration, submission reference and authority acknowledgement.

That neighbour already names this exact roster id and says site/asset/metered quantity is the
sector discriminator. This row reciprocates without contradicting it and sharpens the same-byte
allocation. A period and authority name count for neither by themselves.

### Renewable generation sibling

**Same bytes:** `Bidirectional-Interval-Data_SP-7781_2026-07.csv`.

- This row needs service-account plus meter-to-charge/billing-run evidence around import or
  consumption values.
- `resource_operations.renewable-generation` needs a generation installation/asset plus production,
  export performance or incentive evidence.

Import/export columns alone are intentionally insufficient. The sibling file had not landed, so
this is an outward reciprocity obligation for R1c, not a claim of current symmetry.

## Tempting false positives rejected

- **Customer utility bill with no calculation lineage.** Finance customer-account material, even
  when it prints a meter serial and usage summary.
- **Meter accuracy or calibration certificate.** Engineering verification; a passed meter at one
  point does not establish later reads or bills.
- **Tariff decision, price-cap publication or regulator guidance.** Government/reference material
  until a supplier implementation record independently connects it to a billing configuration.
- **Move-in inventory or check-out report.** Construction/property evidence; meter readings inside
  a tenancy event do not establish supplier acceptance or billing.
- **Grid-connection offer or meter-installation commissioning sheet.** Connection/handover evidence,
  not a live bill calculation. It may become an asset-group anchor without activating this row.
- **Renewable generation interval export.** Export register and energy unit do not distinguish
  generation from bidirectional customer supply without installation or billing anchors.
- **Bank/card statement with recurring utility merchant line.** The merchant is transaction content,
  not the issuer of a utility service account and not supplier operations.
- **Customer-support complaint that says bill and meter.** `business_operations.support-operations`
  owns the case lifecycle unless a calculation trace, corrected read and rebill evidence activate
  this row independently.
- **Budget, revenue forecast or invoice ledger.** Money rows and a period do not create read-to-charge
  lineage.
- **Commodity-market or tariff-analysis report.** Reading Inbox unless an accepted operational
  workflow exists; topic is not purpose.
- **Meter face photograph.** Photos/One-Off Images or a no-copy group member until the own-file or
  accepted-workflow evidence establishes its role.
- **Encrypted bill pack.** Metadata-only evidence cannot be rescued by a billing-shaped filename.

## Required neighbours considered without an edge

### Engineering

The default engineering boundary is controlled technical definition, verification and handover.
`Meter-Accuracy-Test-Certificate_MTR-771.pdf` is deliberately rejected: requirement/procedure,
reference standard, test points and pass/fail belong to engineering. Conversely, a calculation
trace applying accepted operational reads and a tariff to produce charges is not engineering merely
because it uses equations or an asset identifier. Once these structures are required, the same
evidence item is not ambiguous, so no broad collision with the `engineering` schema or
`engineering.commissioning-handover` is authored. A certificate may join the operated-meter group
without acquiring a billing role.

### Government

`Tariff-Decision-and-Price-Cap_2026.pdf` is the sharpest temptation. Authority letterhead, policy
analysis, legal effect and publication state support government/regulatory custody; this row needs
a supplier implementation, calculation or run-control relation. A public decision held as reference
does not itself become supplier operations, and a bill citing the decision does not become a
government case. The structures are separable, so no template collision is authored. Government's
issuer-side/public-authority role remains independently activatable where its own evidence exists.

### Business operations beyond the filing edge

Support cases, budgets, management forecasts, IT asset registers, vendor contracts and policy
documents can all mention meters, tariffs, suppliers or billing. They do not become this row without
the read-to-charge lineage. Only `business_operations.corporate-regulatory-filings` receives an edge
because the **same metering return bytes** can genuinely carry both compelled-submission and
operational-measure structures. A billing-dispute case may independently activate support operations,
but the case lifecycle and the calculation trace are distinct evidence rather than one signal that
needs mutex allocation.

### Construction/property

`Move-in Meter Reading and Keys.jpg` and tenancy inventories are property-condition events. A
property address, tenant acknowledgement and key/meter block make that purpose. Supplier acceptance,
read-validation or rebill evidence makes this row. Packet membership may connect them but cannot copy
the service point or opening-read role. No edge is added because the own-file structures decide the
seam cleanly.

## Proposed fields — deliberately empty

Full list: `[]`.

The legacy row proposed `supply_point`, `meter_identifier`, `supplier`, `reading`, `reading_type`,
`billing_period` and `tariff`. They are not recreated:

- `supply_point` should first be tested against the anchor's proposed `site`; a private synonym is
  exactly the 574 failure.
- `meter_identifier` should first be tested against the anchor's proposed `asset`. Raw identifiers
  are high-cardinality and privacy-loaded, and a folder level per meter is often unusable.
- `supplier` overlaps Finance `institution` but reverses corpus role; R1c must decide whether role
  context is sufficient or a role split is needed. This template does not mint it.
- `billing_period` overlaps the anchor's `reporting_period` and Finance's proposed `record_period`.
  One neutral period key is preferable to three near-synonyms if their roles can be stated honestly.
- `reading`, `reading_type`, `tariff`, quantities, units, multipliers and exception codes are
  decisive evidence and search/audit data but poor destination dimensions. A catalogue field is not
  required merely because a value appears in a calculation.
- `record_type` already exists canonically on Finance and is proposed for reuse by the
  resource_operations anchor. R1c should adjudicate it globally rather than this template restating
  the proposal.

The row therefore votes for reuse of `site`, `asset`, a neutral period and global `record_type`, but
authors none. Its detection grammar works even if all remain raw evidence.

## Template coactivation for R1c — memo only

CONNECTION section 5 makes `also_holds_with` schema↔schema only. This template therefore authors
none. R1c should adjudicate these intended lifts:

- `resource_operations ↔ finance` for `Final Utility Statement - Account 0042.pdf`: independently
  supported meter-to-charge facts and protected account-statement facts.
- `resource_operations ↔ business_operations` for
  `Monthly-Metering-Return_2026-07.xlsx`: independently supported operational metering detail and
  compelled-submission structure.
- No automatic `resource_operations ↔ engineering` lift is requested from a calibration
  certificate; group membership is enough and must not become schema activation.

Unlisted schema pairs remain unasserted, not forbidden. The JSON's empty `also_holds_with` is a
contract requirement, not a claim that no file can carry several schemas.

## NEEDS-JOSEPH

- **NJ-UTIL-1 — custody/role is not always in the bytes.** A rendered bill can be byte-identical in
  the supplier's archive and the customer's Downloads folder. Options: require explicit corpus
  custody/workflow evidence for supplier activation; allow both resource and Finance when distinct
  structures activate; or route every rendered bill to Finance and reserve this row for internal
  calculation/control artifacts. The third is highest precision; the second preserves more facts.
- **NJ-UTIL-2 — child or default work-type family.** The resource anchor already names metering,
  settlement and billing-operation exports. Keep the child only if meter-to-charge detection,
  service-point-first recommendation and customer-usage privacy are material template differences.
  Otherwise refuse it and retain the files under the default plus Finance.
- **NJ-UTIL-3 — identifier/period field decision.** Reuse anchor `site`/`asset` and one neutral
  period/global `record_type`, or license a service-point role. No option should create separate
  `supply_point`, `meter_identifier`, `billing_period` and `record_period` keys if one global role
  works. Raw customer/account/meter identifiers should default out of destinations.
- **NJ-UTIL-4 — schema coactivation.** Lift resource↔Finance and resource↔business_operations for
  the named fixtures, or document why independent activation without an authored
  `also_holds_with` edge is sufficient. Template rows cannot settle this.

## Refusal status and audit claim

Refusal status: **not refused, with an explicit collapse condition.** Refuse at R1c if the only
remaining distinction from the resource default is the value `billing`, or if the only distinction
from Finance is which side happens to hold identical bill bytes. Keep only if the calculation
lineage and privacy/dimension differences remain implementable.

The row claims no jurisdiction rule, no tariff correctness, no billing algorithm, no identifier
regex and no threshold. It claims only that real supplier operating files expose recurring labelled
relations among readings, quality, consumption, rates, runs and corrections, and that those
relations can be distinguished from the named false positives with abstention.
