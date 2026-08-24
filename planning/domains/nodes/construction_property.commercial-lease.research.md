# construction_property.commercial-lease — gist research memo

Depth: GIST
Row: `construction_property.commercial-lease` · kind `template` · schema `construction_property`
· launch `placeholder` · absorbs the legacy row `prop.commercial-lease`.

## Node test

Passes on detection signals. The two decisive structures are the **schedule of condition** (a dated
room-by-room photographic record made expressly to limit a future liability) and the
**dilapidations schedule** (breaches × covenant reference × remedy × costed sum, with a response
column). Neither exists anywhere else on the roster, and neither is an instrument. The rent-review
memorandum, the licence, the lease-event date schedule and the lease-defined recharge are four more.

Its dimension recommendation also carries one negative worth having: **no period level**. This
situation is event-driven, not cyclical — the opposite of `block-management`, which is the only row
in my set that does recommend one. Its dates are a diary, not a folder structure.

## The boundary the dispatch pointed me at, stated reciprocally

`legal.leases-agreements` landed first, is a **safety** template, and already names the
tenancy-packet fixture. The split written here is:

- **The instrument** — party recitals, covenants, grant of occupancy, consideration, execution —
  is the landed row's, and it protects first.
- **The apparatus that runs the tenancy after grant** — schedule of condition, rent review,
  licence, recharge, dilapidations, lease-event diary — is this row's.
- **Premises address, rent amount and a signature block count for neither.** That is the landed
  row's own vocabulary, adopted deliberately so the two edges read as one boundary rather than two
  opinions. Its `never_alone` on a bare execution block is likewise adopted unchanged.

The lease itself therefore appears here only as a file this row **reads dates and proportions out
of** — the file example says exactly that and hands ownership to the legal side.

## The collision most likely to fire on a real corpus

Not the legal one — `business_operations.facilities-workplace`. Most people holding these files are
the **tenant**, and a tenant organisation's premises record and its workplace record live in the
same folder. The discriminator authored is lease-management versus workplace-management, and a
premises address is on both.

## Files considered and rejected

- Rates and utility accounts for the premises: real, and already claimed by
  `finance.subscriptions-utilities`, whose landed edges state the service-address discriminator.
- Fit-out drawings and contract papers: `construction-project` and `drawings-revisions` (both mine)
  own them; the licence-to-alter example points at them without claiming them.
- Business rates appeals and lease renewal proceedings: a proceeding is `legal`'s.

## Neighbours considered that did NOT get an edge

- `construction_property.tenancy-management` (residential, not mine) — the closest neighbour of all,
  and deliberately **not** given an edge from here, because the reciprocal has to be authored on
  that row and a one-way edge would prejudge how it draws the residential line. Raised instead as
  **NJ-CP-9** so R1c can pair them.
- `finance.cap-table-equity` / `legal.estate-planning` — the landed `legal.leases-agreements` row
  already carries both against the agreement family; duplicating them here would be noise.

## proposed_fields

None. `property` (schema row, NJ-CP-1) is the key this row needs. A tenancy or lease-reference key
was considered and not proposed: the schema row's `instruction` proposal already covers the
container concept, and minting a second one would be exactly the near-duplicate defect D6 exists to
kill.

## NEEDS-JOSEPH (this node only)

- **NJ-CP-9** — commercial versus residential letting. Drawn here on the covenant regime; a small
  mixed-portfolio landlord's corpus crosses it constantly. Reciprocal owed on
  `construction_property.tenancy-management`.
- **Lease-event diary** — a schedule of dates held to be diarised may be a P10/P11 concern rather
  than a filing situation. Kept as a work type and a detection structure; nothing claimed about
  diarising.
- Inherits **NJ-CP-1**.
