# business_operations.product-requirements — lab notes (template row)

**Depth: GIST** (J-IND). Honest map, not deep per-industry research. Not padded.

## Sources

`00-database-agent-product-design.md` (all quotations machine-verified verbatim), `ALIGNMENT.md`,
`_CONTRACT.md`, `CONNECTION.md`, `CONNECTION-EXAMPLES.md`, `roster.json`, `canonical_fields.json`,
`DECISION-BRIEF.md` (J-IND, D1, PR-6), `ROSTER.md` §4 + Appendix A line 831. Reference standard for
depth, idiom and key set: the landed `clinical_practice.*` files. Paired row:
`business_operations.product-roadmap` (Appendix A line 830), researched by the same agent, with the
merge question stated identically on both.

## The pair question, answered honestly

The dispatch brief flagged `product-requirements` and `product-roadmap` as possibly **one world**. The
merge case is genuine: in a small team they are the same folder, the same authors, and often the same
document; and under PR-6 the node test's **dimensions leg cannot distinguish them at all**, because both
`dimension_order` arrays are empty by contract.

**Both rows are kept.** The node test is met on its first leg — detection signals — and the signals are
not close:

| | requirements | roadmap |
|---|---|---|
| anchor | a feature, with a scope | a horizon, with an audience |
| distinctive structure | an explicit **non-goals / out-of-scope** section; requirement identifiers; given-when-then | time as a structural **axis**; now/next/later; a forward-looking disclaimer |
| lifetime | stays true after the quarter | **expires**, and is superseded |
| nearest neighbours | `engineering.requirements-specification`, `code.software-project`, `user-research` | `project-delivery`, `strategy-plan`, `go-to-market` |

The last two rows of that table are what convinced me: they have different neighbour sets and opposite
relationships to time, which is not what one situation under two names looks like. The merge case is not
dismissed — it is recorded as the `open_question` on **both** rows in identical terms, so neither can be
read alone, and as **NJ-BO-10**.

## What it is for, and what it holds

Specifying what a product should do and why, for one bounded piece of work: the requirements document,
user stories and acceptance criteria, the scope boundary, annotated mockups, open questions, and the
decision records that closed them.

## Files considered and rejected

- **`H1 roadmap.pptx`** — kept as the collision fixture against the paired row.
- **`Requirements specification - Rev C.pdf`** — kept as the second fixture: shall-statements with
  verification methods are engineering, not product.
- **A competitor teardown used as background** — belongs to `market-research`; not claimed.
- **A test plan** — considered; folded into the acceptance-criteria example rather than given its own,
  since at gist depth the traceability story is the same one.

## proposed_fields

**None.** PR-6 forbids field rows on this schema.

## Neighbours considered that did NOT get an edge

- **`manufacturing.work-instruction`** — specifications for making a thing; the engineering edge already
  carries the requirement-document confusion.
- **`academic.coursework`** — student project specs share the shape; too thin to author, and the schema
  boundary is obvious from context terms.
- **`business_operations.support-operations`** — knowledge-base articles describe product behaviour, but
  the audience difference is unambiguous.

## NEEDS-JOSEPH

- **NJ-BO-10 · One product-management row, or two?** Stated above and identically on
  `business_operations.product-roadmap`. Decision input: if the fields pass (D1's opening) never happens,
  two rows whose only *demonstrated* difference is detection signals is a thinner justification than a
  merged row would need to overturn, and the pair should be re-examined then.
- **NJ-BO-11 · Screenshots taken from production.** Mockups and specification illustrations are routinely
  captured from live systems and carry real user data while looking exactly like design files. That is a
  privacy question about a class of file rather than about this row's boundaries, and it is stated here
  because this is where such files accumulate. Reciprocally relevant to `creative.uiux-product-design`.
