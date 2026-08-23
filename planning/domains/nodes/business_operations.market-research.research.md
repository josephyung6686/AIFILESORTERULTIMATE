# business_operations.market-research — lab notes (template row)

**Depth: GIST** (J-IND). Honest map, not deep per-industry research. Not padded.

## Sources

`00-database-agent-product-design.md` (all quotations machine-verified verbatim), `ALIGNMENT.md`,
`_CONTRACT.md`, `CONNECTION.md`, `CONNECTION-EXAMPLES.md`, `roster.json`, `canonical_fields.json`,
`DECISION-BRIEF.md` (J-IND, D1, PR-6), `ROSTER.md` §4 + Appendix A lines 828–829. Reference standard for
depth, idiom and key set: the landed `clinical_practice.*` files.

## What it is for, and what it holds

Investigating a market — its size, segments, competitors and what it will pay — to inform a commercial
decision. Sizing models, competitive matrices and competitor profiles, pricing analyses, purchased
analyst reports, survey and panel summaries, captured price exports, and the findings deck the whole
thing was built to produce.

## Node test — passes, on purpose rather than content

The anchor is the **commercial question**: this work has a commissioner, a deadline and a
recommendation, and it stops when the decision is made. That distinguishes it from `research` (anchored
on a project and a publication) and from `business_operations.user-research` (anchored on evidence from
named participants under consent). The most distinctive detection signal is structural rather than
topical: **several named companies on one axis of a matrix**, which is a shape essentially unique to
this row. Privacy rules differ in a narrow but real way — pricing scenarios are the organisation's own
confidential position, and purchased analyst reports carry redistribution licences in their own footers.

## Legacy ids absorbed (ROSTER.md Appendix A)

`ops.market-competitive-research` (ROW, line 828) and `ops.pricing` (FOLD, line 829). The fold is
recorded but not accepted uncritically; see NJ-BO-9.

## Files considered and rejected

- **`Interview notes - P07.docx`** — kept as the collision fixture against `user-research`, and it is
  the one confusion in this row with a **privacy** consequence rather than only a filing one.
- **`Industry outlook - saved article.pdf`** — kept as the second fixture: saved reading is not analysis.
- **A customer segmentation built from the organisation's own CRM data** — real, and it sits astride
  this row and `user-research` in a way gist depth cannot settle; left out rather than guessed.
- **A win/loss analysis** — genuinely between this row and `partnerships-bd`; the `partnerships-bd` row
  lists it as a work type, so it is not claimed here.

## proposed_fields

**None.** PR-6 forbids field rows on this schema.

## Neighbours considered that did NOT get an edge

- **`government.statistical-programme`** — official statistics are a source for this row, not a
  confusion about it.
- **`finance.investment-brokerage`** — equity research and market research share shape and vocabulary,
  but the finance schema is a safety domain and mixing an ordinary business row into that boundary at
  gist depth would be guessing at a posture question, not describing one.
- **`nonprofit.advocacy-campaign`** — campaign research; too thin to author.

## NEEDS-JOSEPH

- **NJ-BO-9 · Was the pricing fold right?** Pricing *strategy* is built on the same competitor and
  willingness-to-pay analysis and belongs here. But the pricing pile a real organisation keeps is often
  mostly **rate cards, quotation templates, discount approval records and customer price lists** — with
  no analysis in them at all — which belong nearer `go-to-market` or `contract-administration`. This row
  deliberately does not claim those. If a user's pricing folder is mostly rate cards, the fold was wrong
  and a separate row is the honest fix.
