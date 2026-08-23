# construction_property.survey-valuation — research notes

Depth: GIST. Placeholder row (J-IND). Absorbs legacy id `prop.survey-valuation` (ROSTER.md Appendix A).

## Sources used

- `planning/00-database-agent-product-design.md` — all quotations grep-matched verbatim before writing.
- `CONNECTION.md` (node test §2, closed edges §5, PR-1, PR-6), `_CONTRACT.md` (rules 5, 8, 10, 11–15),
  `ALIGNMENT.md`, `roster.json` (collision targets checked mechanically).
- Landed neighbours read and reciprocated: `finance.household-property`, `legal.leases-agreements`,
  `business_operations.contract-administration` (idiom), `business_operations.organisational-records`.

## The site-survey vs survey-valuation question (the other half)

Argued in full in `construction_property.site-survey.research.md`; the conclusion is written into both
nodes' `collides_with` in the same words, so the pair is reciprocal. Summary: **two worlds**, separated
by deliverable rather than by subject. This row's deliverable is an opinion someone may RELY on — hence
an addressee, a purpose, a basis and a liability limitation; that row's is measured geometry with no
addressee at all. The middle case (a structural engineer who measures then concludes) resolves to this
row whenever the reliance furniture is present.

## What makes this a node

All three node-test grounds. Signals: the reliance block and the condition-rating table exist nowhere
else in the family. Dimensions: purpose is the natural second level here and in no other construction
row, because the same property, the same surveyor and nearly the same report exist three times for
three audiences. Privacy: a named individual plus an address plus a lender plus a figure is the
sharpest identifying combination in the construction schema.

## Files considered and rejected

- **Estate agent market appraisal.** Kept as a fixture and routed to `construction_property.agency-listing`;
  it imitates this row on purpose, which is precisely why it is written down.
- **EPC.** Rejected: a registered certificate with a rating and an expiry is `compliance-certificate`'s
  shape, not an addressed opinion.
- **Insurance policy schedules.** Rejected to `finance.insurance-personal` / `finance.insurance-corporate`.
  The reinstatement-cost ASSESSMENT is this row's; the policy it feeds is not.
- **Homebuyer's own snagging list.** Rejected to `construction_property.snagging-defects`.

## proposed_fields

None. Schema declares no field rows (D1 as narrowed, PR-6). Prose candidates: a property key, a
purpose-of-report key (blocked by PR-1 — `purpose` stays College-applications-scoped, and this row must
not mint a clone), and the transaction-side role that three rows in this catalogue now independently
want. Recorded in `open_question`, not minted.

## Neighbours considered that did NOT get an edge

- `legal` / `finance` (schemas) — real overlaps, expressed as `also_schema` on the dilapidations and
  mortgage-valuation file examples, because `also_holds_with` joins schemas only and this is a template.
- `government.housing-authority` — considered for statutory disrepair inspections; rejected because no
  shared discriminating evidence item appears on this row's files, only topical adjacency.
- `academic` / `research` — the word "survey" collides, but the collision that matters is captured on
  `construction_property.site-survey` against `business_operations.user-research`, and duplicating it
  here would have been shelving rather than evidence.

## NEEDS-JOSEPH

- **NJ-CP-VAL-1 · The transaction-side role.** Reciprocal with `business_operations.contract-administration`
  (buy vs sell) and `construction_property.site-health-safety` (authored vs submitted). This row does not
  mint a key; it records that the same document is filed by three parties in three roles and that the
  document itself cannot say which one owns the filesystem.
- **NJ-CP-VAL-2 · Purpose as a dimension.** Under PR-1, `purpose` is a College-applications field. This
  row is the clearest non-admissions case of a purpose-coherent situation in the construction family, and
  it is recorded as evidence for NJ-3 rather than resolved here.
- **NJ-CP-VAL-3 · The household seam.** Stated reciprocally with the landed `finance.household-property`:
  a homeowner's survey report is this row's document held for that row's reason. Neither row is wrong;
  the question is which one a homeowner's corpus should propose first, and that is a question about
  someone's real filing life rather than about evidence.
