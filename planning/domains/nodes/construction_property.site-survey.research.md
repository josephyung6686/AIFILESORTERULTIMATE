# construction_property.site-survey — research notes

Depth: GIST. Placeholder row (J-IND). Absorbs legacy id `cons.site-survey` (ROSTER.md Appendix A).

## Sources used

- `planning/00-database-agent-product-design.md` — all quotations grep-matched verbatim before writing.
- `CONNECTION.md` (node test §2, closed edges §5, PR-6), `_CONTRACT.md` (rules 8, 10, 11–15),
  `ALIGNMENT.md`, `roster.json` (collision targets checked mechanically).
- Landed siblings for idiom and boundaries: `business_operations.contract-administration`,
  `business_operations.organisational-records`, `finance.household-property`, `legal.leases-agreements`.

## The site-survey vs survey-valuation question, argued explicitly

The dispatch brief asked for an explicit argument either way. **They are two worlds, and I keep both.**

The tempting reading is that they are one world under two names, because both are "a professional
looking at a building". That reading fails the moment you ask what the deliverable IS:

- A site survey's deliverable is **measured data** — coordinates, levels, dimensions, strata, sample
  registers. It has no addressee. It is an **input to design**, and it is consumed by drawings,
  quantities and setting-out. Its file forms are unlike anything else in the catalogue: a four-thousand
  row coordinate CSV, a point cloud, a scan registration report.
- A survey/valuation's deliverable is **an opinion** — a figure, a condition rating, a recommendation.
  It is addressed to a named party, carries a purpose (for lending, for purchase, for insurance), and
  carries a limitation-of-liability or reliance clause because someone will act on it and may sue. It
  is an **input to a transaction**, and it is consumed by a lender, a buyer or an insurer.

That difference shows up in all three of the node test's grounds at once: different detection signals
(coordinate structure and datum notes vs an addressee, ratings and a reliance clause), different
recommended dimensions (site → survey type → date vs property → transaction/purpose → report), and
different privacy postures (geometry vs a named buyer, a lender and a price). Two rows.

The genuinely hard middle case is a **structural engineer's inspection report**, which measures and
then opines. The rule recorded on both rows: where a document carries an addressee, a purpose and a
reliance clause, the opinion reading wins, because that is what the document is FOR — 00's own
topic-versus-purpose distinction. It is written reciprocally into both nodes' `collides_with`.

## Files considered and rejected

- **Proposed general-arrangement drawings.** Kept as the primary collision fixture and routed to
  `construction_property.drawings-revisions`. Same practice, same title block, one word different.
- **Home survey / Level 2 report.** Kept as the second fixture and routed to `survey-valuation`.
- **EPC certificates.** Considered here (a surveyor visits and measures). Rejected: an EPC is a
  registered certificate with a rating and an expiry, which is `compliance-certificate`'s shape, and it
  also travels with tenancy compliance. Not claimed by this row.
- **Land Registry title plans and searches.** Rejected: conveyancing material, `law_practice.conveyancing`
  and `construction_property.sale-purchase`. A title plan is a legal boundary record, not a measured survey.

## proposed_fields

None. Schema declares no field rows (D1 as narrowed, PR-6). Prose candidates for the schema row:
a site/property key, a survey-date key (unusually load-bearing here — a survey's claim is that it was
true on a day), and a survey-type key. Not minted.

## Neighbours considered that did NOT get an edge

- `photos` (schema) — real overlap on the existing-condition image set, expressed as
  `also_schema: "photos"` on that file example rather than as an edge, because `also_holds_with` joins
  schemas only and this is a template row.
- `finance.household-property` — a homeowner keeps survey reports, but the household row's anchor is the
  property as a financial asset; the edge that matters there is with `survey-valuation`, not this row.
- `manufacturing.inspection-record` — similar measurement-and-record shape; rejected because no shared
  discriminating evidence item exists (a part number and a drawing tolerance versus a datum and a level).

## NEEDS-JOSEPH

- **NJ-CP-SURV-1 · As-built surveys.** Reciprocal statement: this row claims the PRE-works measured
  survey and explicitly does not claim the AS-BUILT record survey, which most plausibly belongs with
  `construction_property.construction-project`'s handover material. The two deliverables are byte-for-byte
  the same kind of file, so no detection signal can separate them; only the project timeline can, and
  activation may not read group membership. Someone owning the project row must state the other half.
- **NJ-CP-SURV-2 · Asbestos surveys.** Claimed here as a pre-works investigation, but they are also a
  standing duty-holder compliance record that outlives the works. Stated reciprocally with
  `construction_property.site-health-safety` and `construction_property.compliance-certificate`: this row
  claims the survey deliverable; the ongoing management-plan reading is not claimed here.
