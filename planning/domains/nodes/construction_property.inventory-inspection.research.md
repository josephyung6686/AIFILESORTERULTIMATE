# construction_property.inventory-inspection — lab notes (template row)

**Depth: GIST** (J-IND). Honest map, not deep per-industry research. Not padded.

## Sources

`00-database-agent-product-design.md` (quotations machine-verified verbatim), `ALIGNMENT.md`,
`_CONTRACT.md`, `CONNECTION.md`, `roster.json`, `canonical_fields.json`, `DECISION-BRIEF.md`
(J-IND, D1, PR-6), `ROSTER.md` §4 → `13-trades-property-logistics.json` (line 922). Neighbours read
before writing: `legal.leases-agreements`, `finance.household-property`, `photos.camera-events`.

## What it is for, and what it holds

Proving a moment. Check-in inventories and schedules of condition, check-out comparison reports,
interim visit notes, embedded photographic appendices, meter and key records, deposit deduction
schedules and the disputes about them, commercial dilapidations schedules, and the schedule of
condition taken of a *neighbour's* property before adjacent works begin.

## Node test — passes, on the room-then-element grid and on the pair

1. **Signals differ:** the repeating room-heading-then-element-grading grid, each row carrying a
   condition and a cleanliness value with a thumbnail, exists nowhere else in this catalogue. Second
   signal, stranger and just as reliable: a **deadline to object** printed on the face of the
   document. Third: a meter serial paired with a photograph of a dial.
2. **Dimensions differ:** property → tenancy → inspection event, with the tenancy level load-bearing
   in a way no sibling needs.
3. **Privacy differs sharply:** this is a photographic tour of the inside of a home, and the exit
   report is an itemised allegation attached to withheld money.

The row also has a property no sibling has: **its documents are useless alone.** A check-in exists
solely to be compared with a check-out. That makes the *pair* the unit, and it is authored as the
row's first `grouping_reason`.

## Legacy id absorbed (ROSTER.md §4)

`prop.inventory-inspection` (ROW), 1:1.

## The hardest thing about this row

**Room photographs are ambiguous and the metadata never helps.** An inventory shoot, a marketing
shoot, moving-day snapshots, an insurance record and progress photography all produce indoor bursts
from one phone in one hour. The row's answer is that nothing in EXIF distinguishes them — only the
report, the gradings, or an accepted group does — which is why "a photograph of a room alone" is in
`never_alone` and why `construction_property.agency-listing` gets a collision whose discriminator is
*how the room is lit and framed*, not any file property.

**The second hardest: the address.** Same problem as `quote-estimate`, and worth stating the same
way in both rows — subject, correspondence, letting and inspector's-office addresses all print
identically.

## Files considered and rejected

- **`Tenancy agreement - 14 Marsh Lane.pdf`** — kept as the collision fixture, routed to
  `legal.leases-agreements` (safety side) with `construction_property.tenancy-management` named as
  the professional file. The three-corner seam is stated in one place so it can be checked.
- **`Schedule of condition - 8 Fell Road - pre-works.pdf`** — kept deliberately, because it is the
  fixture that proves the row is *not* merely a letting row.
- **`Property photos - Marsh Lane.zip`** — kept as the marketing/inventory ambiguity fixture.
- **An EPC certificate** — rejected: a rated assessment on a regime, not a condition comparison;
  `construction_property.compliance-certificate` is nearer.
- **A home-contents insurance photo schedule** — rejected: same mechanism, different world, and
  `finance.insurance-personal` owns it; noted so the omission is deliberate.

## proposed_fields

**None.** PR-6 forbids field rows on this schema. Candidate dimensions (property, tenancy,
inspection event and type) are prose in `template.why` for R1c. Flag for R1c: *tenancy* would be a
new concept for the canonical list and is deliberately argued rather than minted.

## Neighbours considered that did NOT get an edge

- **`finance.hoa-residents-association`** — block inspections exist there, but the seam runs through
  `construction_property.block-management` and that agent's row is the right place for it.
- **`legal.personal-legal-matters`** — a deposit dispute that reaches a tribunal becomes a legal
  matter; the boundary is real but downstream, and the `Review Later` fallthrough handles the
  in-progress case without a thin edge.
- **`medical.*`, `identity.*`** — no seam, despite the row's high sensitivity.

## NEEDS-JOSEPH

- **NJ-CP-11 · Letting row, or condition-proving row?** The row covers the pre-works schedule of
  condition and commercial dilapidations alongside the letting check-in, on the ground that the
  *mechanism* unites them and the tenancy does not. If Joseph reads it narrowly as a letting row,
  the pre-works schedule needs a home and `construction_property.site-survey` is the only candidate;
  the `survey-valuation` collision is authored so that reading stays available without a rewrite.
- **NJ-CP-12 · May a frozen tree separate the check-in from the check-out?** The row says it should
  never happen; a year-first tree does it automatically, and the product cannot forbid the user from
  building one. Recorded rather than silently resolved.
