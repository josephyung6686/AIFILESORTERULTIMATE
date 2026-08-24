# construction_property.snagging-defects — research notes

Depth: GIST. Placeholder row (J-IND). Absorbs legacy id `cons.snagging` (ROSTER.md Appendix A).

## Sources used

- `planning/00-database-agent-product-design.md` — all quotations grep-matched verbatim before writing.
- `CONNECTION.md` (node test §2, closed edges §5, PR-6), `_CONTRACT.md` (rules 8, 10, 11–15),
  `ALIGNMENT.md`, `roster.json` (collision targets checked mechanically).
- Landed siblings for idiom: `business_operations.contract-administration`,
  `business_operations.organisational-records`; neighbours `finance.household-property`,
  `legal.leases-agreements` read for the seam.

## The node test, applied honestly (the brief asked)

The challenge was: is this just a `work_type` value of `construction-project`? **It is a node**, and the
argument is not that snagging is important — importance is not the test — but that three specific things
differ from the project row's default:

1. **Lifecycle.** Almost everything in this row happens AFTER practical completion, during a defects
   liability period, on a project that every other row considers finished. A register still being
   re-issued eleven months after handover cannot sit inside a container whose own lifecycle has ended.
2. **Detection signals.** The register's fingerprint — a LOCATION column beside a STATUS column, one row
   per fault — exists in no other construction document. Nothing about the project row's default
   detection would find it.
3. **Version behaviour.** This row generates more near-duplicate files than any other in the schema: the
   same register exported weekly with one column changing. That is a distinct handling shape, and it is
   the row where 00's universal `duplicate_family` and `version_family` facts carry most of the weight.

Had only the third been true I would have refused. All three is comfortably a node.

## Files considered and rejected

- **A software issue export.** Kept as a fixture because its structural match is near-total and it proves
  why "a numbered statused list" sits in `never_alone`.
- **A tenancy check-out report.** Kept as a fixture and routed to `construction_property.inventory-inspection`
  — same shape, different obligation (a deposit, not a construction contract).
- **The practical completion certificate itself.** Left ambiguous on purpose: the certificate is the
  boundary event, this row claims the outstanding-works schedule appended to it, and the certificate most
  plausibly belongs to `construction_property.construction-project`.
- **Operating and maintenance manuals / building manuals.** Rejected: handover material, but reference
  documentation rather than a fault tracker. Not claimed here.

## proposed_fields

None. Schema declares no field rows (D1 as narrowed, PR-6). Prose candidates for the schema row: a
site/project key, a plot-or-unit key (this row wants it more than any other), and a defect-phase key.
Not minted.

## Neighbours considered that did NOT get an edge

- `hr.employee-relations` — a defect register naming a repeatedly-responsible tradesperson has a real
  employment consequence; rejected because no shared evidence item exists at the document level and the
  edge would have been consequence, not confusion.
- `finance.household-property` — a homeowner's snag list of their own new house is that row's material
  too, but the household row's anchor is money and ownership, and no evidence item is shared.
- `legal.personal-legal-matters` — a defects dispute becomes one eventually; topical, not evidential.

## NEEDS-JOSEPH

- **NJ-CP-SNAG-1 · Defect or variation.** Stated reciprocally with `construction_property.variation-claim`
  in the same words on both rows: the same item is a defect on one party's paper and a paid variation on
  the other's, in good faith on both sides. The product should recognise both and abstain. What is
  Joseph's is whether a genuinely-both file is offered in two places or held in one.
- **NJ-CP-SNAG-2 · Residential defect files and the occupant.** A snagging file for someone's home is a
  catalogue of what is wrong with where they live. This row routes those members protectively; whether
  that is strong enough is a privacy decision about real people rather than an evidence question.
