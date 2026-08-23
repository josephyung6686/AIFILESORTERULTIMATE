# business_operations.board-governance — lab notes (template row)

**Depth: GIST** (J-IND). Honest map, not deep per-industry research. Not padded.

## Sources

Same authority stack as `business_operations.research.md`; all quotations machine-verified verbatim
against `00-database-agent-product-design.md`. Landed siblings read for key set and idiom:
`clinical_practice.case-conference.json` (the closest analogue — a meeting-anchored row on a
field-less schema), `business_operations.json`. Legacy row absorbed per `ROSTER.md` Appendix A line
806: `ops.board-governance` (ROW).

## What it is for, and what it holds

The recurring cycle of a **constituted body** — a board, a committee, a trustee body, a members'
meeting — running under terms of reference and producing a decision record with standing outside the
room. It holds notices, numbered packs and their papers, minutes in draft and approved states,
written resolutions, attendance and quorum records, conflict declarations, terms of reference,
delegated-authority matrices, statutory register extracts, proxy and voting records, and the chair's
and secretary's correspondence.

## Node test — passes, on the constitution

The anchor is the **body and its cycle**, not the meeting and not the topic. Detection signals differ
from every sibling: a papers index with decision/noting markers, a quorum statement, an
`IT WAS RESOLVED` operative clause, a written resolution with no agenda at all. Privacy rules differ
too — a routine pack carries a remuneration appendix, a finance appendix and a legal memo behind one
cover page, which is an aggregation problem no ordinary meeting note has. Dimensions do not differ,
and cannot, for the family-wide PR-6 reason.

The boundary that had to be drawn carefully is against the sibling `business_operations.meeting-record`.
The discriminator adopted is **constitution, not vocabulary**: terms of reference, quorum, and a
resolution with standing. A leadership team that writes "minutes" and "actions" is the meeting-record
row's, and that is stated on both the collision and the `Leadership team meeting notes` fixture.

## Files considered and rejected

- **`Board minutes template.docx`** — kept as the collision fixture. Complete structure, no record.
  This is the tempting false file for the row.
- **`Leadership team meeting notes`** — kept as the second fixture, against the meeting-record sibling.
- **A remuneration committee benchmarking report** — real and in scope, but it is a market-research
  artifact wearing a governance subject; left as a `work_type`-adjacent case rather than an example.
- **A published listed-company annual report** — considered and dropped: it is the output of the
  governance cycle made public, and belongs with reading material once published.
- **A shareholders' agreement** — dropped here; it is an instrument, and `finance.cap-table-equity`
  and the legal family own it.

## proposed_fields

**None** — deferred to the schema row's `organization` and `fiscal_period` proposals. This row wants
`fiscal_period` (an annual governance calendar) and a body concept, and deliberately mints neither.

## Neighbours considered that did NOT get an edge

- **`hr.compensation-planning`** — remuneration committee papers are genuinely both. Left unedged
  because the material only crosses when it names individuals, which the schema row already states as
  the `hr` boundary, and doubling it here would not add a discriminator.
- **`finance.cap-table-equity`** — a share-allotment resolution touches it. Stated instead through the
  `corporate-regulatory-filings` collision, which is where the same document actually travels.
- **`business_operations.risk-register`** — a board risk report. Same shape reason as above; not
  tripled at gist depth.

## NEEDS-JOSEPH

- **NJ-BO-4 · Is a constituted BODY an acceptable branch anchor in v1?** It is what a company
  secretary files by and it is not a vanity collector, but a folder named for a remuneration or audit
  committee discloses in the filesystem namespace that the material exists and what it concerns. The
  provisional posture is a shallow, user-approved body level with no automatic depth.
- Carries **NJ-J-IND-4** (third-party-confidential material with no safety flag) and **NJ-BO-1**
  (`fiscal_period`) by inheritance from the schema row.
