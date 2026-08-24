# construction_property.building-control — gist research memo

Depth: GIST
Row: `construction_property.building-control` · kind `template` · schema `construction_property`
· launch `placeholder` · absorbs the legacy row `cons.building-control`.

## Node test

Passes on detection signals, clearly. Two structures are unique to it on this schema: the
**authority-decision structure** (issuing body + application reference + decision word + numbered
conditions, all four together) and the **condition-number-against-application-reference** pair that
runs discharge. The **stage-inspection** record is a third. None of these is a document type and
none is shared with a sibling row.

It also differs from the schema's default on dimensions, in the opposite direction from
`construction-project`: this row is **property-first**, following the family default deliberately,
because a site's regulatory history outlives every job, applicant and owner, and it is what a future
purchaser searches for. `construction-project` reverses to job-first; both are recorded so the
two parallel agents on this schema can see that the reversal is a per-row judgement with a stated
reason, not drift.

## The boundary that actually matters: side, not topic

The `government.planning-application` collision is a **side** collision. The authority's copy and
the applicant's copy of a decision notice are byte-comparable; the application reference is on both
and discriminates nothing. The edge names role evidence as the discriminator and, where role does
not settle, calls for abstention on both sides — `00`'s own position that correct abstention is a
successful outcome. That is authored one-way here; the government rows owe the reciprocal, and R1c
should collect it.

## Its relationship to the row I refused

`construction_property.compliance-certificate` is refused (see that file). Part of its coverage —
the authority's own **completion / final certificate** — lands here, because it is issued by the
authority under an application reference and shares this row's structure. The other part — an
*installer's* declaration against a scheme — lands on `finance.household-property` as a work-type
value on the householder's side, and inside a job file on the professional side. Both routes are
stated in the refusal.

## Files considered and rejected

- Party-wall awards and notices: adjacent and real, but the apparatus is a surveyor's award between
  two private owners, not an authority decision. No row on my list owns it; recorded for R1c.
- Fire-safety and building-safety case files: a large real world, but the roster gives block
  management its own row (mine) and site health-and-safety another (not mine).
- Council tax and business rates letters: same letterhead, different world entirely — used here as
  the negative example `Council letter.pdf` that makes the never-alone concrete.

## Neighbours considered that did NOT get an edge

- `legal.personal-legal-matters` — an enforcement notice or an appeal can become a dispute. No edge
  authored, because the discriminating evidence (a proceeding, a tribunal caption) is stated on the
  legal side already, and duplicating it one-way would add noise rather than a join.
- `business_operations.compliance-audit` — organisational compliance evidence overlaps, but the
  schema row already carries the `business_operations` collision at family level.

## proposed_fields

None. The row relies on the schema row's `property` proposal (NJ-CP-1). An application-reference key
was considered and **not** proposed: it is a short structured token in the same space as case,
matter and claim references across the roster, so it would be a weak field with a `possible` ceiling
and no destination value, and the schema row's `instruction` proposal already covers the container
concept if R1c takes it.

## NEEDS-JOSEPH (this node only)

- **NJ-CP-6** — side-undecidable authority documents: abstain on both sides rather than defaulting.
  Authored one-way here; the `government.*` rows owe the reciprocal.
- **Jurisdiction scoping**, recorded not asked: D4 already settles that jurisdiction is a value.
  This is simply the row where a single-jurisdiction gazetteer bites hardest, and R4 should know it.
- Inherits **NJ-CP-1**.
