# construction_property.agency-listing — gist research memo

Depth: GIST
Row: `construction_property.agency-listing` · kind `template` · schema `construction_property`
· launch `placeholder` · absorbs the legacy row `prop.listing`.

## Node test

Passes on detection signals **and** on privacy rules — the only row in my set to pass on two legs.

- **Signals:** the marketing-particulars structure (price line + room schedule with dimensions +
  branding, co-occurring), the portal-export record with a marketing status vocabulary, the
  agency-instruction terms of business, and the viewing/feedback and offer structures. None is
  shared with a sibling.
- **Privacy:** genuinely different from the schema default, in kind rather than in degree. The
  working material is photographs of the inside of strangers' homes and the names, phone numbers
  and affordability of applicants who never bought anything. The schema's default posture covers
  commercial confidentiality; this row's material is third-party *personal* data as its normal case.

## The dimension recommendation, and one prohibition

Property → instruction → function, following the family default. The instruction level exists
because one property is marketed repeatedly — the 2019 letting and the 2026 sale are different
files about the same flat.

The prohibition is the useful part: **never an applicant level.** `00` is direct that a folder
should not become a collection point for everything produced by the same person or organization, and
an applicant folder would additionally put a named private individual into a folder name.

## Files considered and rejected

- Anti-money-laundering ID checks on a buyer: real in every agency file and squarely identity-safety
  material. Not used as an example, because including it would have invited this row to describe
  handling that is P7's and the identity placeholder's.
- Tenancy agreements and deposit protection records: the instrument is `legal.leases-agreements`'s
  and the ongoing tenancy is `construction_property.tenancy-management`'s (not mine).
- Board and signage orders: transactional, and adequately covered by the receipts residual.

## Neighbours considered that did NOT get an edge

- `creative.commissioned-shoot` — a property photographer's own engagement. Considered seriously and
  rejected: the discriminating evidence is the *brief and deliverable* apparatus on the creative
  side, which is that row's to state, and a one-way edge from here would pre-empt it. Recorded.
- `business_operations.go-to-market` — marketing material in general. No edge: the shared evidence
  item would be "branding", which is not an evidence item at all.
- `finance.receipts-expenses` — advertising invoices. Covered by the receipts residual.

## proposed_fields

None. `property` (schema row, NJ-CP-1) is what this row needs and it is proposed there. An applicant
or listing-reference key was considered and deliberately **not** proposed: an applicant is a person
and would be a field the row's own privacy argument forbids from ever becoming a destination, and a
listing reference is a short token in a crowded token space.

## NEEDS-JOSEPH (this node only)

- **NJ-CP-7** — third-party applicants: forbidding an applicant *dimension* is not the same as
  protecting applicant *data*. Same substitute-mechanism gap as NJ-CP-4 and the landed
  `business_operations` row, in its sharpest form.
- Inherits **NJ-CP-1**.
