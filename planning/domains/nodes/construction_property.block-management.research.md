# construction_property.block-management — gist research memo

Depth: GIST
Row: `construction_property.block-management` · kind `template` · schema `construction_property`
· launch `placeholder` · absorbs the legacy row `prop.block-management`.

## Node test

Passes on detection signals and on dimensions.

- **Signals:** the **apportionment schedule** — rows are the *units of one building*, columns are a
  share and a demanded amount — is the row's primary structure and exists nowhere else on the
  roster. It is the shape of splitting one building's cost between many owners. The service-charge
  cycle (budget → demands → reconciliation), the reserve fund, the statutory consultation notice
  sequence, and the block-wide recurring compliance regime are four more.
- **Dimensions:** this is the only row in my set that recommends a **period level**, and only under
  one branch — the service-charge year, because that branch genuinely cycles annually and nothing
  else here does.

## The boundary the dispatch pointed me at

`finance.hoa-residents-association` landed first and is the **residents' own side**. This row is the
**professional appointment side**. The edge is written as its explicit reciprocal, using the landed
row's own discriminator vocabulary: a building name, a unit, an assessment amount and a set of
minutes count for *neither*; the discriminator is the management agreement, the fee, the agent's
letterhead, and the direction of the demand.

`legal.leases-agreements` keeps the instrument. This row reads the **apportionment percentage inside
the lease** without owning the lease — the file example says so explicitly.

## The prohibition worth recording

**Never a unit level.** A unit is a household, and a unit folder puts a real person's home address
into a folder name for the convenience of filing their arrears. An agent would reasonably want the
opposite, because their working life is unit-keyed. That conflict is real, it is between usability
and `00`'s collector prohibition, and it is raised as Joseph's rather than resolved here.

## Where the refused certificate row's coverage lands here

Recurring block compliance evidence — fire risk assessments, fire door inspections, asbestos
registers, lift examinations, water hygiene records — is route (c) of the
`compliance-certificate` refusal. This row carries them as `work_types` and as a grouping reason
("one compliance regime across its recurrences"), which is the honest form: they are a *repeating
regime for a building*, not a one-off declaration.

## Files considered and rejected

- Right-to-manage and tribunal applications: real and common, but the apparatus is a proceeding and
  `legal.personal-legal-matters` and the practice rows own disputes. Referenced only through the
  arrears example's `also_schema`.
- Ground rent demands: adjacent, but they belong to the freeholder's investment record rather than
  to management, and no row on my list owns that cleanly. Recorded for R1c.
- Utility bills for communal supplies: covered by the receipts residual and by
  `finance.subscriptions-utilities`, whose landed edges already state the service-address boundary.

## Neighbours considered that did NOT get an edge

- `business_operations.facilities-workplace` — an organisation occupying its own premises. The
  schema row already carries the `business_operations` collision at family level, and the specific
  confusion (a facilities contractor versus a communal contractor) is thin enough that a fifth edge
  would be noise.
- `finance.subscriptions-utilities` — the landed row already states the service-address
  discriminator against property records generally; repeating it one-way adds nothing.

## proposed_fields

None. `property` (schema row, NJ-CP-1) is the key this row needs; a unit key was considered and
deliberately not proposed, for the reason above.

## NEEDS-JOSEPH (this node only)

- **NJ-CP-8** — the resident *director*: holds both roles legitimately, and the appointment
  discriminator fails on their corpus. Co-activation or abstention, never a silent pick. Reciprocal
  owed on `finance.hoa-residents-association`.
- **Unit as a destination dimension** — usability versus `00`'s collector prohibition. Joseph's.
- Inherits **NJ-CP-1**.
