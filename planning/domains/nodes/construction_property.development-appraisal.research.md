# construction_property.development-appraisal — gist research memo

Depth: GIST
Row: `construction_property.development-appraisal` · kind `template` · schema `construction_property`
· launch `placeholder` · absorbs the legacy row `prop.development-appraisal`.

## Node test

Passes on detection signals. The distinctive structure is not "a spreadsheet about a building" —
that would fail — but the **residual appraisal's backwards arithmetic**: end value less costs, fees,
finance and required profit, solving for what the land is worth. Nothing else on the roster computes
in that direction. The **schedule of accommodation** (unit types × areas × values) and the
**peak-debt cashflow** are the second and third structures, and both pair with the first.

Its dimension recommendation also differs from the schema default in one specific way worth
recording: the second level is the **exercise** (acquisition / viability / funding / review), not
the document function, because the same model file recurs across exercises and the exercise is what
distinguishes the copies.

## Why the money is explicitly not the signal

This row's entire content is money, so `never_alone` opens by disqualifying money: a figure, a
period column series, a spreadsheet `source_type`, a yield and a profit percentage all count for
nothing on their own. The landed `business_operations.budget-forecast` situation produces the same
column shape, and that collision is stated as the row's first edge — the construction face of the
`NJ-J-IND-3` fork the landed `business_operations` row already records.

## The hardest real case in this row

**Sensitivity runs.** A developer keeps ten files that are near-identical by content and different
in meaning by one assumption cell. `00`'s duplicate and near-duplicate machinery is correct about
the bytes and unhelpful about the intent, and `00`'s own warning that a content-hash match supports
deduplication review while a filename match alone does not cuts both ways here. This row records the
problem for P9 and invents no mechanism.

## Files considered and rejected

- A land registry title and a searches pack for the same site: real in an acquisition folder, but
  their evidence is title apparatus, which is `construction_property.sale-purchase`'s (not mine).
- A JV or partnership agreement behind a scheme: the instrument is protected legal material, and
  `legal.leases-agreements` and `finance.cap-table-equity` already state the equity-instrument line.
- An investment valuation of a standing income-producing building: shares the yield vocabulary but
  is `construction_property.survey-valuation`'s (not mine). Recorded as an LLM-hard case rather than
  claimed.

## Neighbours considered that did NOT get an edge

- `finance.small-business-bookkeeping` — a developer's actual ledger. No shared evidence item with
  an appraisal; the ledger has transactions and this row has assumptions.
- `government.planning-application` — a viability assessment is submitted to an authority, and the
  file example carries an application reference. No collision edge, because the two are genuinely
  both on disjoint evidence rather than mutually exclusive, and the building-control row (mine)
  already states the applicant-side boundary.
- `business_operations.strategy-plan` — an investment case is close, but the landed schema-level
  `business_operations` collision on the `construction_property` schema row already covers it.

## proposed_fields

None. This row is the family's strongest argument for **reusing canonical `project`** rather than
minting `instruction` (NJ-CP-2): a development scheme is a project by any ordinary reading, and a
new key here would be a synonym. Recorded in `open_question` for R1c.

## NEEDS-JOSEPH (this node only)

- **NJ-J-IND-3, construction face** — forward-looking money about a scheme: finance,
  `business_operations`, or the property family? This row asserts the third, on the *subject* rather
  than the money.
- **Near-duplicate sensitivity sets** — recorded for P9, no mechanism invented.
- Inherits **NJ-CP-1**, **NJ-CP-2** (and argues for the reuse side of NJ-CP-2).
