# construction_property.construction-project — gist research memo

Depth: GIST
Row: `construction_property.construction-project` · kind `template` · schema `construction_property`
· launch `placeholder` · absorbs the legacy row `cons.project`.

## Node test

Passes on detection signals, which is the leg the test needs. Two structures exist nowhere else on
the roster: the **contract-sum-with-date-for-possession** particulars block, and the
**valuation-against-works-executed-less-previously-certified** payment cycle. Neither is a document
type and neither is a money shape; both are apparatus peculiar to a construction contract. The
completion / defects / making-good triple is a third.

Its dimension recommendation also differs from the schema's default, which the schema row
explicitly licensed: this row is **job-first**, not property-first, because a contract's whole life
is one instruction at one site and a property level above it is the one-child collector level `00`
rejects.

## Why it is the branch root

Every other construction-side row on this schema is unintelligible without it. A drawing revision, a
site diary entry, an instruction number, a valuation number and a snagging item are all *positions
inside a job*. That is `00`'s own reason for putting a course above a homework number, applied to a
different world — and it is a **template dimension order**, never a `parent_id` and never schema
inheritance (CONNECTION §3).

## Files considered and rejected

- A CIS/subcontractor tax return and a site payroll run: real in a builder's folder, but their
  evidence is finance and hr apparatus, not works apparatus.
- A method statement / risk assessment: genuinely this world, but the roster gives it its own row
  (`construction_property.site-health-safety`), which is not mine to pre-empt.
- Plant hire and materials delivery notes: same — `construction_property.plant-hire` and
  `.materials-delivery` own them; both appear here only as residual examples.

## Neighbours considered that did NOT get an edge

- `government.planning-application` — the job file contains condition-discharge correspondence, but
  the authority-decision structure belongs to `construction_property.building-control`, which I also
  own and which states the government boundary. Routing it twice would be duplicate authorship.
- `hr` — site inductions and CSCS-style records name individuals, but the confusable document family
  is the health-and-safety row's, not this one's.
- `creative.architectural-visualisation` — the schema row already carries this collision; repeating
  it here would add nothing.

## proposed_fields

None. This row proposes no key of its own and relies entirely on the schema row's `property` /
`instruction` proposals (NJ-CP-1, NJ-CP-2). Minting a job key here while the schema row proposes one
would be the near-duplicate defect D6 exists to kill.

## NEEDS-JOSEPH (this node only)

- Inherits **NJ-CP-1** and **NJ-CP-2** from `construction_property`.
- **Row-specific, recorded not resolved:** job-first versus property-first for a building that
  receives repeated contracts over decades. This pass chose job-first for this row; a surveyor
  looking back at one building's history would choose the reverse.
