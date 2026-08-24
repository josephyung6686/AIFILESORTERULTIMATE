# construction_property.subcontract — research notes

Depth: GIST. Placeholder row (J-IND). Absorbs legacy id `cons.subcontract` (ROSTER.md Appendix A).

## Sources used

- `planning/00-database-agent-product-design.md` — all quotations grep-matched verbatim before writing.
- `CONNECTION.md` (node test §2, closed edges §5, PR-6), `_CONTRACT.md` (rules 5, 8, 10, 11–15),
  `ALIGNMENT.md`, `roster.json` (collisions checked mechanically).
- Landed neighbours read and reciprocated: `business_operations.contract-administration` — which already
  names THIS row in its own `collides_with`, so the pair is reciprocal by construction — plus
  `legal.leases-agreements`, `finance.household-property`, `business_operations.organisational-records`.

## What makes this a node

The **statutory payment cycle**. A subcontract is not merely a contract with a builder: it runs on an
application answered by a notice within a period, where silence has a defined and expensive consequence.
That produces a document pair — application and answering notice — that exists nowhere else in this
catalogue, and it produces a calendar that is legally sharp rather than administratively convenient.
That is a detection signal and a dimension recommendation both, so the node test passes on two grounds
before privacy is even considered.

## Files considered and rejected

- **A materials purchase order.** Kept as the load-bearing fixture and routed to
  `construction_property.materials-delivery`. Supply rhymes with subcontract and has none of the machinery.
- **Employer's/public liability certificates.** Kept, but explicitly NOT claimed exclusively: the file
  example records that it is simultaneously `finance.insurance-corporate`'s document, this row's
  engagement condition and `site-health-safety`'s pre-qualification evidence.
- **Collateral warranties and parent company guarantees.** Kept as work_types; they are executed
  instruments and the legal safety schema's protective ordering applies, noted via `also_schema: "legal"`
  on the order example.
- **Labour-only timesheets from a subcontractor.** Rejected — see `construction_property.timesheet`,
  which this agent refused; the pay reading routes to `hr.payroll-benefits-administration` and the
  contractual reading to this row's applications.

## proposed_fields

None. Schema declares no field rows (D1 as narrowed, PR-6). Prose candidates: a project key, a
package key, a counterparty-firm key, and the directional role (applying vs assessing). Not minted.

## Neighbours considered that did NOT get an edge

- `legal` / `finance` (schemas) — real, expressed as `also_schema` on the order and CIS file examples,
  because `also_holds_with` joins schemas only and this is a template row.
- `hr.onboarding-offboarding` — considered for the competence/verification pack; rejected because a
  subcontractor is a firm, not an employee, and treating the two the same is precisely the error that
  employment-status paperwork exists to prevent.
- `logistics.shipment` — rejected; delivery evidence belongs to `materials-delivery`, already edged.

## NEEDS-JOSEPH

- **NJ-CP-SUB-1 · The directional role.** Reciprocal with `business_operations.contract-administration`
  (buy vs sell), `construction_property.survey-valuation` (transaction side) and
  `construction_property.site-health-safety` (authored vs submitted). Four rows now independently want
  one key. One proposal at R1c, not four variants.
- **NJ-CP-SUB-2 · Firm-level compliance evidence versus project branches.** Insurances and accreditations
  expire on the subcontractor's calendar and are demanded on every project. Stated reciprocally with
  `construction_property.site-health-safety`: neither row should silently copy a certificate into a
  project branch, and where the correct home is is a filing decision rather than an evidence one.
