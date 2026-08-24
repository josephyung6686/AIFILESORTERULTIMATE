# construction_property.site-health-safety — research notes

Depth: GIST. Placeholder row (J-IND). Absorbs legacy id `cons.method-statement-ra` (ROSTER.md Appendix A).

## Sources used

- `planning/00-database-agent-product-design.md` — all quotations grep-matched verbatim before writing.
- `CONNECTION.md` (node test §2, closed edges §5, PR-6), `_CONTRACT.md` (rules 5, 8, 10, 11–15),
  `ALIGNMENT.md`, `roster.json` (every collision target checked mechanically against the node list).
- Landed siblings for idiom and reciprocal boundaries: `business_operations.contract-administration`,
  `business_operations.organisational-records`, `finance.household-property`, `legal.leases-agreements`,
  `career.employment-records`.

## What this row is, argued

The node test is passed on **privacy rules** first and detection signals second, which is unusual in
this family and worth stating plainly. Every other construction row holds commercial material about
organisations; this one holds medical and identity material about *individuals who are usually not the
holder* — an injured operative, a subcontractor's labourer, a visitor. That is a materially different
privacy posture from the schema's default, which is one of the three grounds CONNECTION.md §2 accepts.

Its detection signals are independently distinct: the **likelihood / severity / residual triple** in a
hazard matrix appears in no other document in this family, and the **issue-time / hand-back-time pair**
on a permit appears nowhere else at all.

## Files considered and rejected

- **Office fire risk assessment.** Kept as a file example precisely because it defeats the row's own
  fingerprint — the matrix is identical. Routed to `business_operations.facilities-workplace`.
- **Generic downloaded RAMS templates.** Not records. Routed to Reference Clips and recorded as the
  row's primary false-positive family; a template pack with placeholders proves nothing was assessed.
- **Insurance certificates** (employer's and public liability). Considered: they travel with safety packs
  constantly. Rejected as this row's, because their anchor is a policy and an insurer —
  `finance.insurance-corporate`'s world. They appear here only as members of a submitted pack.
- **Asbestos surveys.** Rejected into `construction_property.site-survey`: a refurbishment/demolition
  asbestos survey is a pre-works investigation of a building, and its safety consequence is downstream.
  Noted in that row instead.

## proposed_fields

None, and deliberately. The schema declares no field rows (D1 as narrowed, PR-6). The candidates this
row would want — a site/project key, a task or package key, and the authored-versus-submitted role —
are recorded in prose in `open_question` and belong to one schema-level proposal at R1c, not to a
template minting variants.

## Neighbours considered that did NOT get an edge

- `medical` (schema) — a real relationship, but `also_holds_with` joins **schemas only** and this is a
  template row, so the correct expression is `also_schema: "medical"` on the two people-bearing file
  examples plus the protective routing. Recorded here so R1c does not read the empty
  `also_holds_with` as a claim that no medical overlap exists.
- `identity` (schema) — same treatment, via the competence-card example.
- `legal.personal-legal-matters` — an injury claim eventually becomes one, but no shared discriminating
  evidence item exists at the document level, so an edge would have been topic similarity.
- `resource_operations.*` and `logistics.driver-compliance` — genuinely similar safety regimes; rejected
  because their discriminating anchors (a well, a mine, a vehicle) do not appear on this row's files,
  and adding the edges would have been taxonomy rather than evidence.

## NEEDS-JOSEPH

- **NJ-CP-HS-1 · Where incident records live.** Stated reciprocally: this row claims incident reports as
  its own situation, and simultaneously concedes that the medical safety schema's protective ordering
  runs first on any file naming an injured person, so the file is detected here and *protected there*.
  What is not decided is whether the eventual folder home is inside the site branch or outside it.
  That is a retention and access decision about real people and is Joseph's, not this row's.
- **NJ-CP-HS-2 · The authored-versus-submitted role.** Reciprocal with
  `construction_property.subcontract`: a subcontractor's safety pack is that row's engagement evidence
  and this row's hazard evidence, and neither can say from the document alone which side of the
  transaction the filesystem belongs to. `business_operations.contract-administration` records the same
  hole for buying versus selling; one canonical proposal should serve all three.
