# business_operations.procurement-sourcing — lab notes (template row)

**Depth: GIST** (J-IND). Honest map, not deep per-industry research. Not padded.

## Sources

`00-database-agent-product-design.md` (all quotations machine-verified verbatim), `ALIGNMENT.md`,
`_CONTRACT.md`, `CONNECTION.md`, `CONNECTION-EXAMPLES.md`, `roster.json`, `canonical_fields.json`,
`DECISION-BRIEF.md` (J-IND, D1, PR-6), `ROSTER.md` §4 + Appendix A lines 555 and 822. Reference standard
for depth, idiom and key set: the landed `clinical_practice.*` files.

## What it is for, and what it holds

Buying something through a bounded, evidenced process. A requirement is specified and issued, suppliers
respond by a deadline, responses are compared against stated criteria, one is awarded, and a purchase
order commits the money. Solicitation documents, specifications and annexes, pricing schedules, supplier
responses, clarification logs, evaluation matrices and moderation notes, award and regret letters,
purchase orders and their acknowledgements.

## Node test — passes, on the event

The anchor is the **sourcing event** — one requirement, one competition, one award — which is bounded in
a way the ongoing supplier relationship (`vendor-management`) and the signed deal
(`contract-administration`) are not. Detection signals differ decisively: the clarification log
(numbered bidder questions with dated answers issued to all) exists in no other situation in the
catalogue, and the evaluation matrix with suppliers on one axis and weighted criteria on the other is
nearly as distinctive. Privacy rules differ too — most of the file is other organisations' confidential
material held in trust, which is a different kind of sensitivity from personal data.

## Legacy ids absorbed (ROSTER.md Appendix A)

`ops.sourcing-rfp` (line 822) and `biz.procurement-po` (line 555), both ROW. Keeping the solicitation
and the order together is the roster's call and it is defensible — the audit trail from requirement to
order is the thing users want held — but it is also the row's `open_question`; see NJ-BO-7.

## The hardest thing about this row

**Which side of the table the file is on.** The specification, the pricing schedule and the clarification
log are byte-identical in the buyer's folder and in every bidder's folder. Nothing in the content
distinguishes them; only purpose does. This is why `business_operations.partnerships-bd` is authored as
the row's first collision and why the discriminator is stated as *possession of the evaluation
apparatus* — several suppliers' responses side by side, a scoring matrix, an award to issue — rather than
as anything about the documents themselves. The reciprocal edge is authored on the `partnerships-bd`
row in the same terms.

## Files considered and rejected

- **`Meridian invoice 33012.pdf`** — kept as the collision fixture: a demand for payment quoting a PO
  number is still bookkeeping.
- **`Scan_20260212_quote.jpg`** — kept as the second fixture: one quote with no competition is not a
  sourcing event.
- **A framework agreement call-off** — real, common, and genuinely between this row and
  `contract-administration`; left in the collision signal rather than given a fixture, at gist depth.
- **A reverse-auction portal log** — considered and dropped as too instrument-specific for gist depth.

## proposed_fields

**None.** PR-6 forbids field rows on this schema.

## Neighbours considered that did NOT get an edge

- **`nonprofit.grant-reporting`** — grant-funded procurement carries extra evidence duties, but the
  situation is the same one; the government edge already covers regulated procurement.
- **`logistics.*`** — freight tendering is this row in a sector; not doubled at gist depth.
- **`hr.*`** — recruitment agency panels are procurement of a sort; too thin to author.

## NEEDS-JOSEPH

- **NJ-BO-7 · Does the purchase order belong to the event or to the money?** A PO is the last act of a
  competition for a large purchase, but for most small organisations POs are a high-volume
  accounts-payable stream with no competition behind them. Keeping them here follows the roster hint;
  the split point — one-off competitive purchase versus routine reordering — is a real user-specific
  line. Reciprocally stated: `finance.small-business-bookkeeping` and
  `retail_hospitality.supplier-order` are the two rows that would inherit the routine half, and the
  collision signals on both are authored so the question is visible from either side.
