# construction_property.timesheet — research notes

Depth: GIST. Placeholder row (J-IND). Absorbs legacy id `trade.timesheet` (ROSTER.md Appendix A).

**Outcome: `refuse_node: true`.** Per the brief, a refusal with an argued reason is a success. The
dispatch message flagged this row as likely to collide with the landed `career.*` rows and the `hr`
schema and warned it might not stand as a property-world row at all. It does not.

## Sources used

- `planning/00-database-agent-product-design.md` — quotations grep-matched verbatim before writing.
- `CONNECTION.md` §2 (the node test), §4 step 2 (never-alone), §9 failure mode 2 (work types as schemas),
  PR-6; `_CONTRACT.md` rules 8, 10, 11–15; `ALIGNMENT.md`.
- `roster.json` — confirmed the receiving rows exist: `hr.payroll-benefits-administration`,
  `finance.payroll-received`, `law_practice.time-and-billing`, and the three construction siblings.
- Landed `career.*` node files read as instructed, in particular `career.employment-records`, whose
  one_line explicitly claims the job's whole tenure including "the recurring pay" material — it already
  holds the individual's side of this coverage.
- Landed `business_operations.organisational-records` read as the model for what a good refusal looks like.

## Why it is refused, in short

The full argument is in `refuse_reason` in the node file. The short form:

A construction timesheet is not one situation, it is four documents sharing a table shape:

| Real document | Its purpose | Row that already owns it |
|---|---|---|
| Signed daywork sheet, countersigned by the CA | evidence for a paid change | `construction_property.variation-claim` |
| Site attendance / induction / fire roll | statutory record of who is on site | `construction_property.site-health-safety` |
| Labour allocation sheet, hours by trade and cost code | the numeric half of the daily record | `construction_property.site-diary` (listed in its `work_types`) |
| Hours × rates, deductions, payroll period | paying someone | `hr.payroll-benefits-administration` / `finance.payroll-received` |

What is left has **no detection signal of its own** (a table of names against hours is never-alone —
it is equally a rota, a payroll import, a billable-hours export and a care-visit log), **no dimension
order** distinct from the diary's (site → week → timesheet is the diary's tree with one leaf renamed),
and a **privacy posture that belongs to another schema**. That last point is the one worth stating
carefully: the row's posture *does* differ from `construction_property`'s default, which is one of
the node test's three grounds — but it differs by being **hr's posture**. Differing because the
material belongs somewhere else is an argument for routing, not for a node. Filing employee pay data
under a construction branch, between the quotes and the drawings, is the outcome the refusal prevents.

## Files considered and rejected

Eight are kept in `file_examples`, all chosen to demonstrate the refusal rather than to pad it. The
emblematic one is `timesheet.jpg`: a photographed grid of hours with two names and a week-ending date,
honestly ambiguous between four situations, whose correct outcome is abstention. The two deliberate
outsiders — a legal billable-hours export and a shift rota — both match the row's only candidate signal
perfectly and belong to entirely different schemas, which is the clearest demonstration available that
the signal was never a signal.

## proposed_fields

None, and none would have helped. A `cost_code` or `site` key would not rescue the row: those tokens are
the discriminator *between* the existing rows, and they are recorded as such on the collisions of
`construction_property.site-diary` and `hr.payroll-benefits-administration`.

## Where the coverage went (reciprocally stated)

- `construction_property.site-diary` — claims the labour allocation sheet as the site reading, lists it
  in `work_types`, and carries a collision with `hr.payroll-benefits-administration` naming the
  discriminant (rates and a payroll period versus a site or cost-code column).
- `construction_property.site-health-safety` — claims attendance, induction and roll-call registers.
- `construction_property.variation-claim` — claims the signed daywork sheet.
- `construction_property.subcontract` — claims the agency/labour-supply timesheet on its billing reading.
- `hr.payroll-benefits-administration` and `finance.payroll-received` — the pay reading, with the
  stricter posture, on the employer and receiving sides respectively. Neither has landed yet; this memo
  states the claim so whoever writes them can reciprocate.

## NEEDS-JOSEPH

- **NJ-CP-TS-1 · The sole trader's own hours.** The one thing the refusal may throw away: a one- or
  two-person firm recording hours per job for its own pricing and invoicing is neither a payroll run nor
  a site diary. `construction_property.trade-job` holds the job; `hr.payroll-benefits-administration`
  presumes an employer. If that gap is real it wants a NEW narrow row, which a single node agent may not
  mint. Recorded for R1c.
- **NJ-CP-TS-2 · Reciprocity owed.** `hr.payroll-benefits-administration` and `finance.payroll-received`
  have not landed. This refusal routes coverage to them; the corresponding collisions on their side are
  owed and are not this agent's to write.
