# business_operations.project-delivery — lab notes (template row)

**Depth: GIST** (J-IND). Honest map of what this filing world is for, not deep per-industry research.
Not padded.

## Sources

`planning/00-database-agent-product-design.md` (all quotations machine-verified verbatim against the
file), `planning/prompts/ALIGNMENT.md`, `planning/domains/_CONTRACT.md`,
`planning/domains/CONNECTION.md`, `planning/domains/canonical_fields.json`,
`planning/domains/roster.json`, `planning/overnight/council/DECISION-BRIEF.md` (D1–D6, J-IND treated
as ratified and not re-argued), `planning/domains/ROSTER.md` §4 and Appendix A (lines 811, 813, 814).
Landed siblings read for key set and idiom: `business_operations.json` (the schema row),
`business_operations.it-asset-inventory.json`, `clinical_practice.case-conference.json`.
Legacy rows absorbed per Appendix A: `ops.project` (ROW), `ops.status-report` (FOLD),
`ops.programme-portfolio` (FOLD).

## What it is for, and what it holds

Someone has a bounded piece of work with a start, an intended end and an owner, and needs to say what
it is, when it will happen, what could stop it, and how it is going. The row holds charters and terms
of reference, plans and schedules (including proprietary scheduling binaries), RAID and decision logs,
recurring status reports, steering-group packs, change requests, portfolio roll-ups, and closure and
acceptance records.

## Node test — passes

The anchor is a **bounded effort**, and the detection signal that carries it is a schedule with a
**dependency column** plus a **scope-and-out-of-scope pair** — neither of which appears on any standing
cycle in this family. The template order also differs sharply: this is the row where project-then-
function-then-period is least doubtful, because 00's own parent-before-child rule applies to a week-14
status report exactly as it applies to Homework 3.

## Files considered and rejected

- **A test plan / QA sign-off** — real and common, but its anchor is the thing being tested, not the
  effort; it earns a `work_type` value at most.
- **A resource or capacity plan naming people against costs** — kept as a `work_type`, not as a file
  example, and flagged in `sensitivity_why` as the member that reaches hr's posture. At gist depth one
  privacy carve-out is enough.
- **A Jira/backlog export** — rejected as an example because it is indistinguishable from the support
  and software-project exports; it survives as the `code.software-project` collision signal.
- **`Kitchen renovation plan.xlsx`** — kept deliberately as the collision fixture. Full schedule shape,
  zero organisational anchor.

## proposed_fields

**None.** The natural anchor for this row is `project`, which is **already a canonical key** (shared by
the research and code schemas), so there is nothing to mint — the row would reuse it if D1's deferral
were ever lifted. `fiscal_period`, which the reporting-period level would want, is **already proposed
by the schema row** and adjudicated at R1c; duplicating the proposal here would put one concept in two
places, which is the 574 failure in miniature. This row therefore writes an empty `proposed_fields` and
records the endorsement in prose instead.

## Neighbours considered that did NOT get an edge

- **`finance.small-business-bookkeeping`** — a project budget tracker touches it, but the collision runs
  through `business_operations.budget-forecast`, which is a sibling's row. Not tripled.
- **`hr.org-design-headcount`** — a resource plan is arguably both; left unedged at gist depth rather
  than guessed, and flagged below.
- **`academic`** — a student group project is the same shape with no organisation. The household fixture
  already carries the no-organisation lesson; a second one would be padding.

## NEEDS-JOSEPH

- **NJ-BO-PD-1 · Where does a PORTFOLIO roll-up sit in a project-first tree?** The roster folded
  `ops.programme-portfolio` here on the ground that a roll-up is the same record one altitude up. That is
  right about the situation and awkward about the shape: a dashboard naming twenty projects has no single
  project anchor. Either the roll-up sits at the branch root above the project level, or it is honestly a
  separate row. Recorded in `open_question`; R1c should decide.
- **NJ-BO-PD-2 · Resource plans and hr.** A staffing or capacity plan names individuals against costs and
  utilisation. It is a delivery artifact by purpose and a workforce record by content. No edge was
  authored; R1c should decide whether the pair with `hr.org-design-headcount` is real.
- Inherits the schema row's **NJ-J-IND-3** (where an organisation's money lives) by reference; not
  restated as an edge here because this row's money is a management view rather than an account.
