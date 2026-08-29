# construction_property.timesheet — research notes

Depth: J-DEPTH. Placeholder row (J-IND). Absorbs legacy id `trade.timesheet`.

**Outcome: `refuse_node: true`, preserved and deepened.** The legacy id names a form shape, not one
organizational situation. This pass proves every escape route with concrete, reciprocal fixtures,
separates employer-side from employee-received payroll, and records stale neighbour edges for R1c.

## Authority and rows read

I read `00-database-agent-product-design.md`, `ALIGNMENT.md`, `CONNECTION.md`,
`CONNECTION-EXAMPLES.md`, `_CONTRACT.md`, `canonical_fields.json`, `roster.json`, the stamped
assignment, and the deepened `construction_property` schema anchor. I also read
`construction_property.site-diary`, `.variation-claim`, `.site-health-safety`, `.subcontract`,
`.final-account`, `.plant-hire`, `.trade-job`, `finance.payroll-received`, and every landed row found
by searching for `construction_property.timesheet`. `hr.payroll-benefits-administration` is rostered
but has not landed; its employer-side obligation therefore remains explicit merge debt.

The schema default is project/property context before `work_type`, never time-first. Its family rule
is decisive: document labels such as variation, drawing, certificate, valuation, and timesheet are
values unless their situation has different signals, dimensions, or privacy rules. The anchor
restates this refusal's lesson: **a shared table shape is not a situation.**

## Refusal in one sentence

Once purpose-bearing bytes are read, a construction “timesheet” is a labour allocation return,
contractual daywork substantiation, a site-safety attendance/induction register, employer payroll,
employee-received pay, or a firm-to-firm labour charge. Each has a receiver. What remains is an
undecidable grid of names and hours and must abstain, not become a seventh situation. The design is
explicit: “conflicting signals should lead to abstention rather than an invented classification”
and “A model that cannot cite sufficient evidence must return unknown.”

## Node test, leg by leg

### 1. Detection signals — fails

The candidate signal is a table of people, dates, and hours. It occurs in every routed fixture:

- `Labour allocation w-c 09-03-26.xlsx`: operative/trade rows, dated hours, cost code, and plant
  standing-time tab. Those bytes make it the numeric half of `site-diary`.
- `Daywork sheet 018 - signed by CA.pdf`: the same labour shape plus a described extra, instruction
  reference, and the other side's countersignature. Those bytes make it contractual evidence
  tendered in support of a paid change; `variation-claim` names the identical fixture.
- `Induction register - March 2026.xlsx`: names, employers, dates, signatures, site heading, and
  induction topic. The serial register and safety purpose make it `site-health-safety`; that row
  names the identical fixture.
- `Payroll timesheet import - March.csv`: people and hours plus rates, overtime multipliers, tax
  reference, and payroll-period header. That is employer-side HR apparatus.
- `Employer payroll register - March 2026.xlsx`: multiple employees plus labelled gross, tax,
  deductions, and net for one payroll period. It is not `finance.payroll-received`, whose landed
  memo distinguishes an individual's received statement from the holder's multi-employee run.
- `ADP Pay Statement - 15 August 2026.pdf`, on `finance.payroll-received`: separate employer and
  employee roles, labelled interval, and gross-to-net table. That is employee-received pay.

The discriminators belong to the receivers. Remove them and only `timesheet.jpg` remains: a grid,
two names, a week ending, and no site, rate, signature, or purpose. Its honest route is Review Later.
The engine must “treat the file extension as a routing signal rather than an assumption about meaning”,
and “A session should never be treated as proof of topic”. Filename, extension, folder,
adjacency, and download session cannot repair absent purpose.

Role ambiguity is an inference grounded in the design's example: “A university name alone should not create a group because Columbia can appear as an authoring school, course provider, target institution, employer, research venue, or merely a cited organization.” Likewise a name in an
hours grid may be employee, subcontractor operative, agency worker, visitor, or sole trader. The
quotation is not misrepresented as being about labour.

### 2. Recommended dimensions — fails

The row has `fields: []` by PR-6 and cannot manufacture `site`, `week`, `worker`, `trade`,
`cost_code`, or `pay_period`. Its empty `dimension_order` is required. Even hypothetically, site →
week → timesheet is `site-diary` with a leaf renamed; pay-period organization belongs to HR/Finance;
variation-reference organization belongs to `variation-claim`; induction registers belong to the
safety situation. Combining those incompatible orders would be a giant form, not a template.

Time cannot rescue it. The schema anchor applies: “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders.”

### 3. Privacy rules — difference points away

Named attendance, rates, deductions, tax references, and employee identifiers are more sensitive
than the commercial default. That is real but routes away from this schema. The corpus “can include identity documents, account statements, tax records, medical information, legal records, credentials, private correspondence, GPS metadata, employment materials, and educational records”.
Employer payroll belongs under HR; employee-received payroll under Finance; named induction and
ambiguous pay-bearing sheets use Protected Records when no situation safely activates.

A privacy difference caused by material belonging to another schema is not a licence to keep an
otherwise empty construction template. The JSON retains `potentially_sensitive` so refusal cannot
lower protection.

## Route matrix — the charged material is not stranded

| Fixture | Positive discriminator | Route | Receiver refuses back |
|---|---|---|---|
| `Labour allocation w-c 09-03-26.xlsx` | cost code, site reading, plant standing time; no pay apparatus | `construction_property.site-diary` | rates, deductions, tax reference, payroll header |
| `Daywork sheet 018 - signed by CA.pdf` | described extra + other-side countersignature | `construction_property.variation-claim` | unsigned allocation; person-pay purpose |
| same sheet once priced | valuation reference, rates, claimed sum | `construction_property.final-account` | unpriced hours without account context |
| `Induction register - March 2026.xlsx` | induction topic + serial signature register | `construction_property.site-health-safety` | diary mention; contractual daywork |
| employer payroll register | multi-person payroll period + gross/deductions/net | `hr.payroll-benefits-administration` | site allocation and employee-received pay; reciprocal pending |
| employee pay statement | labelled payer/recipient + interval + gross-to-net | `finance.payroll-received` | multi-person register; hours without issued calculation |
| agency timesheet | firm order/application/charge vs person-pay structure | `subcontract` or HR; abstain if unresolved | neither infers status from signature/agency word |
| plant-hire docket | one asset + hire period + charge per asset/day | `construction_property.plant-hire` | personnel allocation/pay purpose |
| `timesheet.jpg` | none | Review Later; Protected Records if sensitive | no invented facts |

Thus dayworks do not disappear into an hours bucket; allocations do not become payroll because they
name people; induction registers do not become diaries because they are dated; and payroll does not
become construction because workers happened to be on a site.

## Reciprocal collision boundaries

**Site diary.** The identical fixture is `Labour allocation w-c 09-03-26.xlsx`. This refusal sends
site/cost/plant there; that row sends rates/deductions/payroll period to HR. A daily narrative that
mentions labour stays diary evidence; a standalone payroll register does not.

**Variation claim / final account.** The identical fixture is `Daywork sheet 018 - signed by CA.pdf`.
`variation-claim` requires the described extra plus other-side countersignature and rejects pay.
Once priced and tied to a valuation, `final-account` can hold substantiation. This is a lifecycle
boundary among unpriced allocation, entitlement evidence, and priced account evidence—not a reason
to resurrect this row.

`final-account.json` still collides with the refused id and says unpriced material belongs here.
That is stale: it routes to `site-diary`, `variation-claim`, or Review Later. This memo preserves the
load-bearing refusal sentences cited by neighbours and records NJ-CP-TS-3; it does not edit them.

**Health and safety.** The identical fixture is `Induction register - March 2026.xlsx`. A signature
list alone is never-alone; induction/toolbox/safety topic plus serial site register makes the safety
reading. That row rejects dayworks and site payroll. Conversely, a diary page merely reporting an
induction remains a diary; the register does not.

**HR / Finance.** Employer-side `Employer payroll register - March 2026.xlsx` carries multiple
people and payroll apparatus and routes to HR. Employee-side `ADP Pay Statement - 15 August
2026.pdf` carries one recipient's issued statement and routes to Finance. Finance expressly rejects
timesheets/hours logs without issued pay calculation and the holder's multi-employee register. The
gist wording that both payroll fixtures were HR and Finance is narrowed: one receiver per role.

**Subcontract / plant hire.** An agency sheet may be a firm charge or person-pay evidence; approval
does not settle employment status. `subcontract` requires order/application/notice evidence and
already calls the undecided fixture an abstention. `plant-hire` is one asset and a charge run per
asset/day; operator identity is incidental. `plant-hire.json` also points at this refused id as if it
owned personnel hours; correct routes are `site-diary`, HR, or Review Later (NJ-CP-TS-4).

## Files considered and rejected

- `Shift rota April.xlsx`: planned coverage, not hours worked. Same visual grid.
- `Billable hours export Q1.csv`: people, matters, rates, client billing; legal/business time.
- `Agency worker timesheet - signed - Meridian.pdf`: ambiguous firm charge/person pay until role-
  bearing evidence appears.
- Blank weekly timesheet template: no completed event or relation; reference material.
- “Please approve my hours” email: communication about a missing attachment, not the record.
- Calendar shift and payroll-provider contact card: calendar/contact records, not worked time/pay.
- Password-protected payroll export: universal metadata plus Unsupported or Encrypted.
- Mixed `March labour returns.zip`: inspect members separately; never copy facts across members.
- Priced daywork image: final-account substantiation, not a generic timesheet.

Each rejection removes a tempting interpretation of the shared grid; none pads a positive ontology.

## Residuals and considered non-route

- **Protected Records** for pay, tax, identity, or named attendance whose situation cannot activate.
- **Review Later** for the ambiguous hours photograph.
- **Independent Records** for a durable signed form arriving alone before it can join a claim.
- **Unsupported or Encrypted** for unreadable/password-protected exports.

`Receipts and Confirmations` was considered but not added. A deposit alert or bare payment receipt
may route there, but it is not a timesheet escape route. Employee pay has Finance; firm invoices and
paid confirmations have finance/business situations. Sending ambiguous hours there would invent a
payment event.

## Fields and edges

`fields: []` and `proposed_fields: []` are deliberate. No canonical key is minted. `site`, `worker`,
`trade`, `cost_code`, `rate`, and `pay_period` would mix different schemas rather than rescue this
row. Universal facts in fixtures remain universally legal and are not private fields.

`collides_with` and `also_holds_with` remain empty because a refused row cannot activate as a
partner. Coverage is expressed on receiving rows and residuals, not zombie edges. `role_split` is
empty because it is reserved for canonical field-key roles.

Neighbours considered without a new edge: `business_operations` (rota/project/billable-time
outsiders prove the shape unsafe but have no single receiver); `law_practice.time-and-billing`
(negative collision fixture); `career.employment-records` (employment-history membership does not
copy pay facts); and `construction_property.trade-job` (holds the job envelope but leaves the sole
trader's own unpriced time ledger unresolved).

## NEEDS-JOSEPH / R1c

- **NJ-CP-TS-1 · Sole trader's own job hours.** A tiny firm may keep unpriced hours per job with
  neither payroll apparatus nor principal-contractor diary. Alternatives: extend `trade-job`, create
  a narrow small-trade job-costing situation, or Review Later. Do not reinstate broad `timesheet`.
- **NJ-CP-TS-2 · Employer-side reciprocity.** The HR row is rostered but not landed. It must accept
  employer payroll registers and reject site allocation, employee-received statements, and
  ambiguous agency status. Until then sensitive material falls to Protected Records.
- **NJ-CP-TS-3 · Stale final-account edge.** R1c should replace its collision with this refused id by
  priced substantiation versus `variation-claim`/`site-diary`/Review Later.
- **NJ-CP-TS-4 · Stale plant-hire edge.** R1c should replace its collision with this refused id by
  asset-charge evidence versus `site-diary` allocation / HR pay / Review Later.

If Joseph intends this id to stand, that is a refusal reversal for R1c: choose a narrow situation
and prove a signal and dimension order not already owned. This row does not silently make that choice.

## What changed in this pass

- Preserved the refusal, load-bearing routing sentences, residual quotations, `fields: []`, and no
  canonical keys.
- Replaced the generic fire-roll example with exact `Induction register - March 2026.xlsx` bytes.
- Added `Employer payroll register - March 2026.xlsx` and separated employer HR from employee Finance.
- Added priced-daywork, plant-hire, archive/email/calendar negatives, full residual reasoning, and
  stale-edge merge debts.
- Re-argued all three node-test legs against the deepened schema default and closed daywork, labour
  allocation, induction, and payroll routes reciprocally.

This refusal is shorter than a schema anchor because it has less positive ontology. Its depth is in
complete routing and negative discrimination, not invented fields or signals.
