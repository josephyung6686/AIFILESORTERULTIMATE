# business_operations.partnerships-bd — lab notes (template row)

**Depth: GIST** (J-IND). Honest map, not deep per-industry research. Not padded.

## Sources

`00-database-agent-product-design.md` (all quotations machine-verified verbatim), `ALIGNMENT.md`,
`_CONTRACT.md`, `CONNECTION.md`, `CONNECTION-EXAMPLES.md`, `roster.json`, `canonical_fields.json`,
`DECISION-BRIEF.md` (J-IND, D1, PR-6), `ROSTER.md` §4 + Appendix A line 827. Reference standard for
depth, idiom and key set: the landed `clinical_practice.*` files.

## What it is for, and what it holds

Pursuing a commercial relationship that does not exist yet — a prospect, a partner, an alliance, a
reseller, a piece of new work being bid for. Prospect and partner profiles, pitch decks, proposals and
statements of work, commercial offers, NDAs, letters of intent, memoranda of understanding and term
sheets, partner-programme material, bid responses, pipeline exports, pursuit meeting notes, and win/loss
reviews.

## Node test — passes, on the pursuit

The anchor is the **pursuit**: one counterparty, one opportunity, tracked from first contact to
signature or loss. The distinguishing detection signals are the **pre-contractual instruments** — NDA,
LOI, MOU, term sheet — which exist only in this stage and vanish once a contract is signed, and the
**pipeline structure**, which is a list of pursuits and belongs to no other situation. Privacy rules
differ specifically: a pipeline export discloses who an organisation is talking to and on what terms,
at scale, in one file.

## Legacy ids absorbed

`ops.partnerships-bd` (ROW, ROSTER.md Appendix A line 827).

## The mirror-image problem, stated once for the pair

Every document in a sourcing event exists identically on the selling side. A bid response here is a
supplier response there; a pricing schedule is the same spreadsheet. The reciprocal collision with
`business_operations.procurement-sourcing` is authored on both rows in the same terms, and the
discriminator on both is *possession of the evaluation apparatus* — several suppliers' responses,
scoring matrices, an award to issue — rather than anything about the documents.

## Files considered and rejected

- **`QBR - Northwind - Q1.pptx`** — kept as the collision fixture against `customer-account-management`:
  the deal is already won.
- **`Consulting proposal - Meridian.pdf`** — kept as the second fixture, and it is the row's real
  boundary problem (NJ-BO-8).
- **`contacts_export.vcf`** — kept because 00 is explicit that contact data is privacy-side rather than
  a source of folder proposals, and a contact list is the thing most likely to be mistaken for a
  pipeline.
- **A conference sponsorship pack** — real BD material, but it is marketing spend; left to
  `go-to-market` rather than claimed.
- **An investor pitch deck** — genuinely a pursuit of a different kind; left out because the counterparty
  is capital rather than commerce, and guessing at that boundary is beyond gist depth.

## proposed_fields

**None.** PR-6 forbids field rows on this schema.

## Neighbours considered that did NOT get an edge

- **`business_operations.market-research`** — the edge is authored from the market-research side and
  reciprocity is R1c's; not doubled here beyond that.
- **`creative.client-engagement`** — a creative studio's new-business pursuit; the same reasoning as
  `career.consulting-client-engagement`, which is already authored, and one edge for that confusion is
  enough at gist depth.
- **`retail_hospitality.catering-contract`** — sector-specific instance of the same pursuit; too thin.

## NEEDS-JOSEPH

- **NJ-BO-8 · Person or organisation?** For a company, business development and job-seeking are
  unmistakably different activities. For a freelancer, a consultant or a sole trader they are one
  activity with two vocabularies — the same proposal PDF is a bid on Monday and a job application on
  Tuesday. Filing a person's freelance pitches under a business-operations branch, or a company's
  proposals under a career branch, would each be wrong for somebody. Reciprocally stated:
  `career.consulting-client-engagement` and `career.recruiting` are the two rows on the other side and
  both carry authored collision signals so the question is visible from either direction. Related:
  **NJ-BO-1** on the `it-asset-inventory` row is the same person-versus-organisation line asked about a
  different pile; R1c should treat them together.
