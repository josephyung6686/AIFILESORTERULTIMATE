# business_operations.budget-forecast — lab notes (template row)

**Depth: GIST** (J-IND). Honest map, not deep per-industry research. Not padded.

## Sources

Same authority stack as `business_operations.research.md`; all quotations machine-verified verbatim
against `00-database-agent-product-design.md`. Landed siblings read for key set and idiom:
`business_operations.json`, `finance.small-business-bookkeeping.json`, `finance.personal-records.json`.
Legacy row absorbed per `ROSTER.md` Appendix A line 808: `ops.operating-plan-budget` (ROW).

## What it is for, and what it holds

The forward-looking money plan of an organisational unit, and the running comparison of that plan
against what happened. Budget instructions and blank submission templates, completed unit
submissions, consolidations, approved budgets, forecasts and reforecasts, variance reports and
commentary, headcount and capex models, driver and scenario models, sign-off records.

## Node test — passes, on plan-versus-record

The anchor is a **planning round for a unit and a period** — money that has not happened yet, or money
being explained after the fact. Detection signals are sharp and unusual: the budget / forecast /
actual / variance column set, and — just as discriminating — the *absence* of a bank statement's
institution-and-account header and of a double-entry debit/credit pair. Scenario and round versioning
is a second structure no sibling has.

## Files considered and rejected

- **`Budget submission template - blank.xlsx`** — kept as the collision fixture. Complete structure,
  no plan.
- **`Household budget 2026.xlsx`** — kept as the second fixture. Structurally identical to a unit
  budget; only the row set differs, and for a sole trader it genuinely fails. This is the honest
  admission the row needed.
- **`Management accounts - March 2026.pdf`** — kept deliberately as NJ-J-IND-3's fixture: a budget
  comparison column (management) and a balance sheet with a compilation note (custodial) in one file.
- **A grant budget** — real and in scope, but it is `nonprofit.grant-reporting`'s and
  `research.grants-funding`'s situation; left out rather than claimed.
- **A project cost report** — left as a `collides_with` against `business_operations.project-delivery`
  rather than a file example; at gist depth one fixture per confusion is enough.

## proposed_fields

**None** — deferred to the schema row. This row wants `fiscal_period` more than any other in the
family, and the argument against reusing `tax_year` (an entity's management calendar routinely does
not coincide with a jurisdiction's statutory one) was written on the schema row for exactly this row's
benefit.

## Neighbours considered that did NOT get an edge

- **`government.grant-programme-administration`** — programme budgets are the same tables. Left
  unedged because the discriminator (a public grant programme) is stated at family level.
- **`nonprofit.fundraising-donor`** — income forecasting overlaps. Same reason.
- **`research.grants-funding`** — a grant budget genuinely collides, but the anchor there is an award,
  not a planning round; noted here rather than edged, for R1c to confirm.

## NEEDS-JOSEPH

- **NJ-J-IND-3 (carried; this is the row it breaks)** — where does an organisation's money live? The
  statutory/custodial-versus-management split is defensible and was drawn by the roster pass, not by
  `00`.
- **NJ-BO-1 (carried)** — `fiscal_period` as a canonical key.
- **NJ-BO-5 · The sole-trader case.** For a one-person business the household budget and the unit
  budget are one file, and the row set is the only discriminator. This is not an edge case in a
  personal-file product. The provisional posture is abstention rather than a guess.
