# construction_property.quote-estimate — lab notes (template row)

**Depth: GIST** (J-IND). Honest map, not deep per-industry research. Not padded.

## Sources

`00-database-agent-product-design.md` (quotations machine-verified verbatim), `ALIGNMENT.md`,
`_CONTRACT.md`, `CONNECTION.md`, `roster.json`, `canonical_fields.json`, `DECISION-BRIEF.md`
(J-IND, D1, PR-6), `ROSTER.md` §4 → `13-trades-property-logistics.json` (line 904). Reference
standard: the landed `business_operations.*` files. Neighbours read first:
`business_operations.procurement-sourcing` (which already authored a collision *against* this id,
and whose `Scan_20260212_quote.jpg` fixture explicitly hands trade quotes here),
`finance.household-property`, `legal.leases-agreements`.

## What it is for, and what it holds

Pricing work that has not happened. Quotations with validity periods and acceptance lines,
estimates that explicitly refuse to be quotations, priced schedules and bill-of-quantities returns,
the internal cost plan the client-facing number was built from, the merchant and subcontractor
prices collected to build it, revisions, and the email that accepted or killed it.

## Node test — passes, and the argument is specifically about *when*

The dispatch warning was right to flag this row: a quote could be a `work_type` value inside
`construction_property.trade-job`. It is not, for one concrete reason. **At the moment a quote is
written there is no job.** There is no job number, no contract, no site file — only an address and
an enquiry — and the large majority of quotes never acquire any of those. Filing them as documents
of a job means filing them under a parent that does not exist, which is precisely the failure
`00`'s parent-dimension rule warns about from the other direction. The three legs then hold:

1. **Signals differ:** a *validity period* plus an *acceptance mechanism* plus the *absence of a
   payment demand* is a fingerprint no other row in the family has. So is the estimate qualifier
   ("subject to survey") — a document that states its own unreliability.
2. **Dimensions differ:** a quote wants a **status** level (open / accepted / declined) that a job
   has no use for, because the live question about a quote is whether it is still alive.
3. **Privacy differs:** the internal build-up behind a quote is margin data, and it must not travel
   with the client-facing PDF.

## Legacy id absorbed (ROSTER.md §4)

`trade.quote-estimate` (ROW), 1:1.

## The hardest thing about this row

**Two documents that look identical and must never be confused: the quote and the cost plan
behind it.** Same totals, same job, one is for the client and one discloses margin. The row
authors it as a fixture (`Cost plan - Marsh Lane - INTERNAL.xlsx`) with `Protected Records` as its
fallthrough rather than trying to separate them by filename, because the only reliable signal is
the presence of a margin or contingency row and the absence of a letterhead.

**The second hardest: the address.** A postal address appears on the letterhead, the site line and
the client line of the same page. It is in `never_alone` and it is the reason this whole schema
needs the professional/householder seam stated explicitly rather than inferred.

## Files considered and rejected

- **`Scan_20260212_quote.jpg`** — kept deliberately: `procurement-sourcing` already routed this
  exact fixture here, and the two rows now agree.
- **`INV-2291.pdf`** — kept as the bookkeeping collision fixture, shared with
  `construction_property.final-account` so the family reads consistently.
- **A price-list PDF from a builders' merchant** — rejected: a catalogue is not an offer for
  specific works; `retail_hospitality.supplier-order` gets the collision instead of a fixture.
- **A finance-agreement quote for the same works** — rejected here, belongs with the finance family.
- **A CRM pipeline export listing open quotes** — rejected as too instrument-specific for gist depth.

## proposed_fields

**None.** PR-6 forbids field rows on this schema. The candidate dimensions (enquiry/site, status,
revision) are recorded in `template.why` as prose for R1c, not minted as keys — and *status* in
particular would be a new concept for the canonical list, so it is deliberately left as an argument
rather than a proposal.

## Neighbours considered that did NOT get an edge

- **`construction_property.agency-listing`** — an estate agent's valuation of a property is also a
  pre-transactional price, but it prices an asset, not works; the seam is with
  `construction_property.survey-valuation` and belongs to that agent's row.
- **`business_operations.partnerships-bd`** — a builder's quote *is* their business development, but
  the `procurement-sourcing` edge already carries the buyer/seller mirror at gist depth.
- **`career.*`** — no seam.

## NEEDS-JOSEPH

- **NJ-CP-3 · Does the accepted quote move, or stay?** It is the job's founding document *and* the
  last of a revision series. The row's answer — reachable from both, duplicated into neither —
  defers to P9/P11 and to `00`'s shared-material policy. Reciprocally stated: the collision on
  `construction_property.trade-job` names the discriminator from this side, and that row should
  name it from the other.
- **NJ-CP-4 · The professional/householder seam.** A builder's quote and the householder's copy of
  the same PDF are the same bytes with different purposes. This row is authored from the pricing
  party's side; `finance.household-property` holds the receiving side. Both edges are written, but
  which tree a *single* physical file ends up in is Joseph's.
