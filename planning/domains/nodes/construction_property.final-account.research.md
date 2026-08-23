# construction_property.final-account — lab notes (template row)

**Depth: GIST** (J-IND). Honest map, not deep per-industry research. Not padded.

## Sources

`00-database-agent-product-design.md` (all quotations machine-verified verbatim against the file),
`ALIGNMENT.md`, `_CONTRACT.md`, `CONNECTION.md`, `roster.json`, `canonical_fields.json`,
`DECISION-BRIEF.md` (J-IND, D1, PR-6), `ROSTER.md` §4 → `13-trades-property-logistics.json`
(line 919). Reference standard for depth, idiom and key set: the landed
`business_operations.*` files, in particular `procurement-sourcing` and the refusal in
`organisational-records`. Neighbour files read before writing: `finance.household-property`,
`legal.leases-agreements`, `business_operations.procurement-sourcing` (whose
`construction_property.quote-estimate` collision this family must answer reciprocally).

## What it is for, and what it holds

Money as the **contract** sees it. A construction contract does not pay by invoice; it pays by a
repeating cycle in which the working party applies for a *cumulative* valuation, the paying side
issues a notice or a certificate stating what it considers due, retention is withheld against a
two-stage future release, and at the end the whole contract is reconciled into one agreed final
account of additions and omissions. The row holds applications for payment and their build-ups,
payment and pay-less notices, interim and final certificates, retention statements and release
requests, draft and agreed final accounts, loss-and-expense summaries, priced day-work
substantiation, and the settlement letter that closes it.

## Node test — passes, on the cycle

Three legs, checked honestly:

1. **Detection signals differ from the schema's default.** The cumulative-minus-previously-certified
   arithmetic exists in no other document in this catalogue. Neither does a two-stage retention
   release, nor a pay-less notice, which is a document that can only exist in answer to another
   specific document. That is a real structural fingerprint, not a name.
2. **Recommended dimensions differ.** The contract's payment stream is a running account and wants
   contract → stage → valuation number; the schema's document-shaped default does not.
3. **Privacy rules differ.** A valuation build-up is a disclosure of margin and of a
   subcontractor's confidential rates; a pay-less notice is an allegation against a named party.
   That is a different privacy posture from a drawing or a site diary.

The honest counter-argument — that a "final account" is a *document type* inside
`construction_property.construction-project` — is recorded, and it is why the row is named for the
whole cycle rather than for the closing document. A single final account with no valuations behind
it is one file; the periodic cycle is the situation.

## Legacy id absorbed (ROSTER.md §4)

`cons.final-account` (ROW), 1:1. Nothing else folded in.

## The hardest thing about this row

**Which side of the cycle the file is on.** The application and the certificate carry nearly the
same numbers; one is a request and one is a certification, and in a small firm's folder both are
just "valuation 07". The row solves it the way `procurement-sourcing` solves its mirror problem —
by naming the discriminating *apparatus* (who signs, whether the sum is certified or demanded)
rather than anything about the totals. The same problem recurs one link down the chain, which is
why `construction_property.subcontract` gets a collision whose signal is *which agreement the
reference names*, not *what the document looks like*.

## Files considered and rejected

- **`INV-2291.pdf`** — kept, as the collision fixture. A demand for payment is bookkeeping even on
  a construction job.
- **`IMG_2201_daywork_week12.jpg`** — kept, as the OCR/handwriting fixture and the seam with
  `construction_property.timesheet`.
- **A bank remittance CSV** — rejected: it is a statement line, and `finance.small-business-bookkeeping`
  owns it outright with no ambiguity worth a fixture.
- **An adjudication referral notice** — real, and genuinely downstream of a pay-less notice, but it is
  a dispute document; left to `legal.personal-legal-matters` / the legal family rather than authored
  thinly here at gist depth.
- **A fluctuations index extract** — too instrument-specific for gist depth.

## proposed_fields

**None.** PR-6 forbids field rows on this schema, and proposing dimension fields here would
prejudge the `construction_property` schema pass that a parallel agent owns. The prose in
`template.why` records what the fields would have to be (contract/project, payment stage,
valuation number) so R1c can adjudicate without re-deriving it.

## Neighbours considered that did NOT get an edge

- **`finance.tax-filings`** — construction payment regimes carry tax deduction at source in some
  jurisdictions, which would make a deduction statement a tax document; jurisdiction-specific and
  therefore a *value* question (D4), not an edge.
- **`business_operations.customer-account-management`** — a client's payment behaviour is an
  account-management concern, but the valuation documents themselves are not; too thin.
- **`logistics.*`** — no seam.

## NEEDS-JOSEPH

- **NJ-CP-1 · Where does the contract's money end and the ledger's money begin?** For a main
  contractor, valuation and invoice are two systems; for a two-person firm they are one act
  performed monthly, and splitting them halves one folder. Stated reciprocally: this row's
  `collides_with` on `finance.small-business-bookkeeping` names the discriminator from this side,
  and the same question is the open_question on this node. Joseph's to draw, because it depends on
  how big the user's jobs are, not on anything in the documents.
- **NJ-CP-2 · Final account as its own row?** A quantity surveyor files the closing account apart
  from the interim cycle. This row keeps them together on the ground that the arithmetic is
  continuous. Recorded rather than silently resolved.
