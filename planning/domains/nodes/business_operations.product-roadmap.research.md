# business_operations.product-roadmap — lab notes (template row)

**Depth: GIST** (J-IND). Honest map, not deep per-industry research. Not padded.

## Sources

`00-database-agent-product-design.md` (all quotations machine-verified verbatim), `ALIGNMENT.md`,
`_CONTRACT.md`, `CONNECTION.md`, `CONNECTION-EXAMPLES.md`, `roster.json`, `canonical_fields.json`,
`DECISION-BRIEF.md` (J-IND, D1, PR-6), `ROSTER.md` §4 + Appendix A line 830. Reference standard for
depth, idiom and key set: the landed `clinical_practice.*` files. Paired row:
`business_operations.product-requirements` (Appendix A line 831), researched by the same agent.

## The pair question

Kept as two rows, not merged. The full argument and the comparison table are in
`business_operations.product-requirements.research.md` and are not repeated here; the `open_question` on
both JSON rows states the case in identical terms so neither row can be read alone. The short form: the
detection signals differ decisively, the neighbour sets differ, and the two rows have **opposite
relationships to time** — a roadmap belongs to a period and expires, a specification belongs to a feature
and does not.

## What it is for, and what it holds

Sequencing product work across a horizon and telling an audience about it. Roadmap decks and timeline
views, planning exports, prioritisation models, release plans and scope definitions, dependency maps,
release notes and changelogs, release announcements, replanning records, and superseded roadmaps.

## Node test — passes, on the horizon

The anchor is the **horizon plus the audience**. The distinctive detection signal is structural: **time as
an axis of the document**, not as a date on it — a grid of periods against themes, or a now/next/later
board. The forward-looking-statements disclaimer is a second signal that appears in this situation and
almost nowhere else in the corpus.

## Two things about this row that no sibling has

1. **It expires.** Last quarter's roadmap is structurally identical to this quarter's and is no longer
   true. Every other row in this family produces documents that stay true. This is recorded in the
   `never_alone`/`needs_llm` sections, in a dedicated file example (`Roadmap 2024 - OLD.pptx`), and as the
   reason `Review Later` is an authored fallthrough.
2. **The safe version and the unsafe version look the same.** An internal roadmap and its customer-facing
   cut share themes, layout and often a filename stem, and only a disclaimer or an audience marking
   separates them. Both are in the file examples deliberately, and the customer-cut example explicitly
   warns against treating the pair as one version family — that would be a real error with a disclosure
   consequence, not a filing nicety.

On `time_first`: recorded **false**, which is the honest narrower claim. The product must come before the
period, or two products' roadmaps interleave in every quarter folder. Within the product, time *is* the
right next level — and that is a statement about dimension order, not about `time_first`.

## Legacy ids absorbed

`ops.product-roadmap` (ROW, ROSTER.md Appendix A line 830).

## Files considered and rejected

- **`PRD - saved views.md`** — kept as the collision fixture against the paired row, deliberately given a
  single target-release mention so the fixture tests the right thing.
- **`Project plan - migration.xlsx`** — kept as the second fixture, and the reason a Gantt-shaped chart
  is listed in `never_alone`.
- **A marketing campaign calendar** — same timeline shape, different situation; covered by the
  `never_alone` entry rather than given a fixture.
- **A public status page export** — considered and dropped as too instrument-specific for gist depth.

## proposed_fields

**None.** PR-6 forbids field rows on this schema.

## Neighbours considered that did NOT get an edge

- **`business_operations.budget-forecast`** — roadmaps and forecasts are both period-axis documents, but
  the strategy edge already carries the horizon confusion.
- **`engineering.stage-gate-review`** — gated development plans; the `project-delivery` edge covers the
  schedule confusion adequately at gist depth.
- **`creative.content-marketing`** — carried through the release-announcement file example rather than as
  an edge, since the confusion is about one work type rather than the situation.

## NEEDS-JOSEPH

- **NJ-BO-10 · One product-management row, or two?** Stated identically on
  `business_operations.product-requirements`; see that memo for the argument.
- **NJ-BO-12 · Should a superseded roadmap be treated differently from an old version?** Everywhere else
  in this catalogue an older version is simply an earlier member of a version family. Here it is
  something stronger — a document that once stated intentions and now states none. Whether the product
  should mark that, and whether `Review Later` is the right destination for expired plans, is a real
  question about how the version-family universal behaves and it is not this row's to settle.
