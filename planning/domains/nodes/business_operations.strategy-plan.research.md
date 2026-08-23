# business_operations.strategy-plan — lab notes (template row)

**Depth: GIST** (J-IND). Honest map, not deep per-industry research. Not padded.

## Sources

Same authority stack as `business_operations.project-delivery.research.md`; all quotations
machine-verified verbatim against `00-database-agent-product-design.md`. Landed siblings read for key
set and idiom: `business_operations.json`, `business_operations.it-asset-inventory.json`. Legacy rows
absorbed per `ROSTER.md` Appendix A lines 805, 807, 809: `ops.strategy-plan` (ROW), `ops.okr-goals`
(FOLD), `ops.business-case` (FOLD).

## What it is for, and what it holds

An organisation or unit decides where it is going over a named span and writes the argument down. The
row holds strategy papers and multi-year plans, annual and operating plans, objectives and OKR sets,
business cases and options appraisals, the strategic analysis behind them (SWOT, PESTLE, scenarios,
sizing models), benefits maps, offsite outputs, target-operating-model papers, and the cascade decks
built to communicate all of it.

## Node test — passes

The anchor is a **planning horizon** and the distinguishing shape is **argument**: an options-appraisal
structure with a do-nothing baseline and a single recommendation, or a horizon-bearing objectives set
with measures and owners. Every neighbour in this family either *schedules* (delivery), *accounts*
(budget), or *records a meeting* (governance). This row recommends. Its dimension order also differs in a
specific way: it is the family's most defensible case for putting a **planning round** high, though still
not at the root.

## Files considered and rejected

- **`Phoenix project plan.xlsx`** — kept as the first collision fixture: an objectives tab inside a
  schedule does not make a schedule a strategy.
- **`Our 5 year plan.docx`** — kept as the second fixture, and the one with real stakes: a household's
  private plan has the identical horizon-and-goals shape, and filing it in a work branch is the concrete
  harm.
- **`Market sizing model.xlsx`** — kept as a three-way ambiguity example rather than resolved, because
  the three candidate rows are owned by three different agents in this pass.
- **An annual report or a published competitor strategy** — rejected as a file example and routed to the
  Reading Inbox instead; the row's anchor is custody of one's *own* plan. Recorded as an open question
  because the market-research reading is genuinely competing.
- **A pitch deck to investors** — considered and left out: its purpose is fundraising, and the finance
  side (`finance.cap-table-equity`) is a landed row belonging to another agent.

## proposed_fields

**None.** `fiscal_period` — the key this row wants most, for the planning round — is **already proposed on
the schema row** with a full argument and marked `adjudicate: R1c`. Restating it here would put one concept
in two places. `organization` likewise. Nothing else this row needs is unheld: a horizon is a value of the
period key, and objectives are content rather than a folder dimension.

## Neighbours considered that did NOT get an edge

- **`nonprofit`** — a charity's strategic plan and its trustees' annual report are the same situation with a
  different regulator. The confusion is about *entity type*, not about evidence, so no edge; the schema row
  already carries the `nonprofit` collision.
- **`academic`** — a departmental strategy and a university plan exist, but the shape is identical to the
  organisational one and adds nothing.
- **`business_operations.go-to-market`** — a launch plan shares the horizon vocabulary. Left to the sibling
  agent that owns that row to state, rather than authored one-way from here into a row I do not own.

## NEEDS-JOSEPH

- **NJ-BO-SP-1 · Should OKRs and goals have stayed folded here?** The fold is right at entity and team level
  and wrong at individual level, where the same workbook becomes a performance record under
  `hr.performance-cycle` — and the cascade means one file often holds both, tab by tab. Stated reciprocally
  against the hr row; R1c should settle it, because the resolution decides whether someone's personal
  objectives can sit under a corporate planning branch.
- **NJ-BO-SP-2 · Another organisation's strategy.** This pass routes a collected competitor plan to the
  Reading Inbox rather than activating this row. The market-research reading is defensible and this row
  should not decide it alone.
- Inherits the schema row's **NJ-J-IND-3** (where an organisation's money lives) by reference: a business
  case is a financial model with a narrative, and the boundary with `business_operations.budget-forecast`
  depends on that unresolved answer.
