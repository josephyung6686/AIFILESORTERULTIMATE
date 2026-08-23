# business_operations.facilities-workplace — lab notes (template row)

**Depth: GIST** (J-IND). Honest map, not deep per-industry research. Not padded.

## Sources

Same authority stack as `business_operations.research.md`; all quotations machine-verified verbatim
against `00-database-agent-product-design.md`. Landed siblings read for key set and idiom:
`business_operations.json`, `finance.household-property.json`, `finance.hoa-residents-association.json`,
and the `construction_property.*` roster rows. Legacy row absorbed per `ROSTER.md` Appendix A line
820: `ops.facilities-workplace` (ROW). Note that `ops.business-travel` folded to
`travel.bookings-confirmations`, not here.

## What it is for, and what it holds

The physical workplace as an **administered** thing. Space records and floor plans, desk and
department allocation, asset and plant registers, planned and reactive maintenance, statutory site
checks (fire, electrical, water, lift, gas), access cards, keys and alarm records, workplace services
and their suppliers, moves and fit-outs, site incident and repair logs.

## Node test — passes, on occupancy

The anchor is a **site and its running record — the occupier's operational view of a building**. That
is what separates it from owning, letting, or constructing the same building, which is the
`construction_property` family's. Detection signals are distinct: the asset-and-next-due-date pairing
in a planned-maintenance schedule, a statutory test certificate with a competent-person identification,
a helpdesk job log with a location slot, and an access register listing holders against zones.

## Two boundaries, both drawn deliberately

**Occupier versus owner** is drawn on **tenure**: a lease, a rent demand, a service-charge
apportionment or a dilapidations schedule is the property family's; the occupier's own plans, asset
register, maintenance schedule and access records are this row's. Defensible, and drawn by this pass —
an owner-occupier holds both sets for one address, and the split then makes two rows for one folder.

**Workplace versus household** is genuinely undecidable for a home-based holder, and in a personal-file
product that may be the majority case, not an edge case. A boiler certificate, an alarm code note and
a floor plan are identical artifacts in a home. The provisional posture is abstention rather than a
guess from the address, and `00`'s own line on abstention as a successful outcome is quoted on the
collision.

**Facilities safety versus employee safety** is drawn on *who is at risk*: a fire risk assessment is
the premises', an accident report is a person's and is `hr`'s under a stricter posture.

## Files considered and rejected

- **`Commercial lease - executed.pdf`** — kept as the tenure fixture.
- **`Boiler service certificate.pdf`** with a residential address — kept as the household fixture; the
  address is the only clue and it is explicitly not decisive.
- **`Alarm and keyholder details.docx`** — kept because it is the row's sharpest sensitivity case:
  authentication material in an otherwise dull row.
- **`IMG_5512.HEIC`** — kept as the photos co-activation and GPS case.
- **A car park permit list / visitor book** — real, folded into the access `work_type` rather than
  given an example.
- **A utility bill** — dropped here: `finance.subscriptions-utilities` has landed and owns it.

## proposed_fields

**None** — deferred to the schema row. This row would want a site concept and an asset concept; both
are held as prose in `template.why` and neither is minted. `location` exists canonically but is the
photos-side capture facet, and asserting it here would be the field-respelling failure the node test
forbids.

## Neighbours considered that did NOT get an edge

- **`construction_property.site-health-safety`** — genuinely close, but the
  `hr.workplace-health-safety` collision already carries the who-is-at-risk discriminator once.
- **`logistics.warehouse-ops`** — a warehouse is a site with plant and inspections. Left unedged; the
  `retail_hospitality.store-operations` collision carries the sector-premises discriminator.
- **`business_operations.risk-register`** — business continuity is site-shaped. Not edged at gist depth.

## NEEDS-JOSEPH

- **NJ-BO-12 · Confirm or replace the TENURE discriminator** against the `construction_property`
  family. It was drawn by this pass and it produces two rows for one owner-occupier's folder.
- **NJ-BO-13 · The home-office case.** Workplace and household are one folder for a home-based holder.
  Provisional posture is abstention; whether a home-office situation deserves its own recognition is
  Joseph's call, and it is not a rare case.
- Carries **NJ-J-IND-4**: access registers and alarm codes are authentication material in a row with no
  safety flag, and the row leans on `Protected Records` to compensate.
