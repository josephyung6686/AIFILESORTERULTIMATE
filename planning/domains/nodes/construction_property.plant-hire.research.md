# construction_property.plant-hire — lab notes (template row)

**Depth: GIST** (J-IND). Honest map, not deep per-industry research. Not padded.

## Sources

`00-database-agent-product-design.md` (quotations machine-verified verbatim), `ALIGNMENT.md`,
`_CONTRACT.md`, `CONNECTION.md`, `roster.json`, `canonical_fields.json`, `DECISION-BRIEF.md`
(J-IND, D1, PR-6), `ROSTER.md` §4 → `13-trades-property-logistics.json` (line 915),
`src/evidence_shape/vocabulary.py`. Reference standard: the landed `business_operations.*` files.
Neighbours read first: `business_operations.it-asset-inventory` (the owned-asset mirror),
`finance.vehicle-records`, `photos.camera-events`.

## What it is for, and what it holds

A machine on someone else's site for a period. Hire agreements and conditions, on-hire
confirmations, off-hire notices and acknowledgements, weekly dockets and hire statements, statutory
thorough-examination certificates and pre-use check sheets, service and breakdown records, damage
and loss recharge claims, and the delivery and collection tickets for the asset itself.

## Node test — passes, on the off-hire notice

1. **Signals differ, decisively:** the **off-hire notice** — a written instruction whose entire
   purpose is to *stop a charge* — exists nowhere else in this catalogue, and the on-hire/off-hire
   pair is the row's structural fingerprint. Second: the asset identity block (fleet number, serial,
   make/model) binds documents that otherwise share nothing.
2. **Dimensions differ:** the row is keyed on **asset × period**, a pairing no sibling has.
3. **Privacy differs:** operated-hire dockets are labour records, examination certificates are a
   named person's professional judgement, and damage claims are allegations.

The row also has an inverted risk profile worth recording: every other row here fears losing a
document; this one fears *not sending* one, because an unissued off-hire keeps billing.

## Legacy id absorbed (ROSTER.md §4)

`cons.plant-hire` (ROW), 1:1.

## The hardest thing about this row

**Asset-first versus site-first**, and it is unresolvable inside the row. A hire firm and a plant
manager file by fleet number; a site manager files by job. The examination certificate is the case
that proves the conflict is real — it belongs to the *machine* and follows it away to the next
hire, so filing it under this site is filing it under the wrong parent. The row recommends
site → hire → stage because the schema is written from the construction side, and records the
counter-case explicitly as `open_question` and as the two competing `grouping_reasons`.

**The near-miss:** `business_operations.it-asset-inventory` is structurally the same row for owned
assets. The word "hire" in the name is load-bearing — remove the counterparty and the rate and this
row *is* an asset register.

## Files considered and rejected

- **`Hire statement - account 20114 - March.pdf`** — kept as the bookkeeping collision fixture,
  matching the pattern used on `final-account` and `materials-delivery` so the family reads the same.
- **`IMG_3390.jpg`** — kept as the honest ambiguity fixture: a close-up of a broken quick-hitch is a
  claim, an inspection or ordinary progress photography, and only an accepted group decides.
- **An operator competence card scan** — considered and *not* given a fixture: it is an individual's
  credential and belongs to the identity/safety side, not to a hire file; noted here so the omission
  is deliberate rather than an oversight.
- **A fuel delivery note for site plant** — rejected: `construction_property.materials-delivery` owns it.
- **A telematics/hours export** — rejected as too instrument-specific for gist depth.

## proposed_fields

**None.** PR-6 forbids field rows on this schema. Candidate dimensions (site/job, hire = asset +
period, document stage) are prose in `template.why`. Note for R1c: if this schema is ever given
fields, *asset identity* is the strongest candidate this row would argue for, and it is not the
same concept as any existing canonical key — but it is deliberately left as an argument, not minted.

## Neighbours considered that did NOT get an edge

- **`logistics.shipment`** — plant movement between sites is haulage, but the `materials-delivery`
  edge already carries the ticket shape.
- **`construction_property.site-health-safety`** — pre-use checks and examinations are safety records,
  but the `compliance-certificate` edge covers the statutory half at gist depth and that row's own
  agent is better placed to author the safety seam.
- **`retail_hospitality.*`** — equipment hire exists there too; not doubled.

## NEEDS-JOSEPH

- **NJ-CP-7 · Asset-first or site-first?** Two real filing habits, one tree, and a certificate that
  legitimately belongs to the asset rather than the site. Stated reciprocally: the collision on
  `business_operations.it-asset-inventory` names the discriminator from this side. Same shape as
  NJ-CP-5 (who owns the purchase order) — whose habit wins when two real ones conflict is Joseph's.
- **NJ-CP-8 · Does a statutory inspection certificate live here or with compliance?** The row says
  both should retrieve it and neither should own it exclusively; the collision is written that way
  rather than picking a winner.
