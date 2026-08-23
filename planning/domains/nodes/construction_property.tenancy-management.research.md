# construction_property.tenancy-management — research notes

Depth: GIST. Placeholder row (J-IND). Absorbs legacy id `prop.tenancy` (ROSTER.md Appendix A).

## Sources used

- `planning/00-database-agent-product-design.md` — all quotations grep-matched verbatim before writing.
- `CONNECTION.md` (node test §2, closed edges §5, PR-2/PR-6 on safety ordering), `_CONTRACT.md`
  (rules 5, 8, 9, 10, 11–15 — rule 9 in particular, since this row is jurisdictionally loaded),
  `ALIGNMENT.md`, `roster.json` (collisions checked mechanically).
- Landed neighbours read in full and reciprocated: `finance.household-property`, `legal.leases-agreements`,
  `finance` and `legal` schema rows (for the safety ordering), `business_operations.contract-administration`
  (idiom), `business_operations.organisational-records`.

## The household / legal seam, argued (the brief asked for it reciprocally)

Three rows can claim one tenancy PDF, and each is right about something:

- `legal.leases-agreements` owns the **executed instrument** and protects it. Its landed one_line says
  exactly that: a safety template detecting and protecting an executed-agreement lifecycle.
- `finance.household-property` owns **the household's own property administration**, and its landed
  one_line explicitly reaches "across acquisition, ownership, tenancy, improvement, inspection,
  taxation and warranty records", while keeping operative instruments on the legal side.
- This row owns **running a let property as a regulated relationship with a person living in it** —
  referencing, deposit protection, service of statutory documents, the compliance calendar, the rent
  ledger and the end-of-tenancy reckoning.

The split I recommend, and have written into the node reciprocally rather than silently: the
**occupier's own home** is the household row's; a **property let out**, with a vetted tenant and served
statutory documents, is this row's; the **agreement itself** is always legal's first. Where a household
holds one let flat, all three fire honestly and finance's safety ordering runs first. That last case is
NJ-CP-TEN-1 and is genuinely Joseph's, because it decides where a real person's real filing lives.

## What makes this a node

Signals: the row's fingerprint is not any document but a **co-occurrence** — agreement plus deposit
certificate plus gas record plus electrical report plus energy certificate, all for one address. No
member identifies the row alone (all five exist for owner-occupiers), and the set does. That is an
unusual and honest detection shape and it is stated that way rather than dressed up as a keyword list.
Privacy: the row's default residual is Protected Records rather than its exception, which is true of no
other construction row except site-health-safety.

## Files considered and rejected

- **A commercial lease.** Kept as the collision fixture, routed to `construction_property.commercial-lease`.
- **The check-out report.** Claimed only as purpose; the situation belongs to
  `construction_property.inventory-inspection` and is edged reciprocally.
- **Landlord tax returns and mortgage statements.** Rejected to `finance.*`. The row stops at the ledger.
- **Ground rent and service charge demands.** Rejected to `construction_property.service-charge` and
  `finance.hoa-residents-association`; edged to the latter because they genuinely arrive in a landlord's
  tenancy folder.

## proposed_fields

None. Schema declares no field rows (D1 as narrowed, PR-6). Prose candidates: a property key, a tenancy
key, and a party-role key. Note D4 explicitly here: this row is the most jurisdiction-loaded in the
family (deposit schemes, prescribed forms, licensing regimes all differ by country), and under
`_CONTRACT.md` rule 9 those differences must stay **values**, never field names. No jurisdiction-specific
key is proposed, and none should be.

## Neighbours considered that did NOT get an edge

- `legal` / `finance` / `identity` (schemas) — real and load-bearing, expressed as `also_schema` on four
  file examples, because `also_holds_with` joins schemas only and this is a template row. Recorded so
  R1c does not read the empty `also_holds_with` as a denial.
- `academic.study-abroad` / student housing — considered, rejected as topical.
- `law_practice.conveyancing` — a tenancy is not a conveyance; no shared discriminating evidence item.

## NEEDS-JOSEPH

- **NJ-CP-TEN-1 · The household seam.** Reciprocal with the landed `finance.household-property`.
  Provisional reading recorded above; the one-let-flat case is genuinely undecided.
- **NJ-CP-TEN-2 · The tenant's own copy.** Reciprocal statement so no row silently claims both sides:
  the tenant's file of the same documents is `legal.leases-agreements` plus `finance.household-property`,
  not this row.
- **NJ-CP-TEN-3 · A tenant's name as a folder level.** The natural second dimension writes a private
  individual's name into a directory other software indexes. This row declines to recommend it.
