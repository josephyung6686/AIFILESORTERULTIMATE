# business_operations.risk-register — lab notes (template row)

**Depth: GIST** (J-IND). Honest map, not deep per-industry research. Not padded.

## Sources

Same authority stack as `business_operations.project-delivery.research.md`; all quotations
machine-verified verbatim against `00-database-agent-product-design.md`. Landed siblings read for key
set and idiom: `business_operations.json`, `business_operations.it-asset-inventory.json`. Legacy rows
absorbed per `ROSTER.md` Appendix A lines 816 and 817: `ops.risk-register` (ROW),
`ops.business-continuity` (FOLD).

## What it is for, and what it holds

An organisation keeps a written list of what could go wrong, who owns each item, what is being done
about it and when it will next be looked at — and, because of that list, keeps plans for the things it
cannot prevent. The row holds risk registers and scoring worksheets, appetite and tolerance statements,
heat maps and committee risk papers, business impact analyses, continuity and disaster-recovery plans,
crisis procedures and call trees, and continuity test and exercise reports.

## Node test — passes

The anchor is a **living register with no end date**. The detection shape — likelihood and impact as
*separate* columns beside a treatment and a review date, plus an inherent-versus-residual pair — is
close to unique, and the appetite statement has no analogue anywhere else in the family. Dimension order
also differs from every sibling in one specific way: this row is emphatically **not** a dated series, so
a period level would fragment a single continuously maintained artifact.

## Files considered and rejected

- **`RAID log.xlsx`** — kept as the primary collision fixture. It is deliberately the *same file* used as
  an example on `business_operations.project-delivery`, seen from the other side; the two rows state the
  same discriminator (scope and lifespan) in opposite directions, which is the reciprocity CONNECTION.md
  asks for.
- **`Fire risk assessment - Unit 4.pdf`** — kept as the second fixture. It is called a risk assessment
  outright, and it is statutory duty-of-care material belonging to `hr.workplace-health-safety`.
- **An information-security risk treatment plan** — real and common, left as a `compliance-audit`
  collision signal rather than a third fixture; at gist depth two fixtures carry the lesson.
- **A pandemic or scenario playbook** — folded into the continuity `work_type` values rather than given
  its own example.

## proposed_fields

**None.** No concept this row needs is both unheld and arguable only from here. The scope anchor
(organisation or unit) is the schema row's proposed `organization`, already adjudicated at R1c; the
review cadence would use the schema row's proposed `fiscal_period`. Minting a `risk_category` key was
considered and **rejected**: categories are *values*, exactly as 00's work types are values, and a
category-per-key would be the 574 failure at field level.

## Neighbours considered that did NOT get an edge

- **`legal.personal-legal-matters`** — litigation risk sits in registers, but the edge would be about
  content rather than shape. Rejected as thin.
- **`government`** — public-body risk registers are published and statutory. Same shape, different
  publication regime; not an evidence confusion, so no edge.
- **`medical` / `clinical_practice`** — a clinical risk register is a real thing and shares the table
  exactly. Left unedged **deliberately**: those rows carry a protective posture and this pass should not
  author an edge that could be read as pulling clinical material toward an operations branch. Flagged
  below instead.

## NEEDS-JOSEPH

- **NJ-BO-RR-1 · Should business continuity have stayed folded here?** The roster's reason (continuity is
  the register's treatment side) is analytically right and organisationally often false — different owner,
  different place, plan-shaped rather than register-shaped. This pass kept the fold on detection grounds
  and recorded the doubt in `open_question`.
- **NJ-BO-RR-2 · The personal/household version.** A person's what-to-do-if list has this shape and no
  organisational anchor. Filing it under a work branch would be wrong, and the row does not resolve it.
- **NJ-BO-RR-3 · Clinical and safety registers.** No edge was authored to `clinical_practice` or `medical`
  because doing so unilaterally risks pulling protected material toward this row. R1c should decide whether
  the pair is stated, and if so, state it from the protected side first.
