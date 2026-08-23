# business_operations.compliance-audit — lab notes (template row)

**Depth: GIST** (J-IND). Honest map, not deep per-industry research. Not padded.

## Sources

Same authority stack as `business_operations.research.md`; all quotations machine-verified verbatim
against `00-database-agent-product-design.md`. Landed siblings read for key set and idiom:
`business_operations.json`, `code.software-project.json`, `construction_property.compliance-certificate.json`
(where landed). Legacy rows absorbed per `ROSTER.md` Appendix A line 543 (`corp.compliance-audit`, ROW)
and line 685 (`soft.tech-compliance-evidence`, FOLD — "control evidence is gathered for an audit").

## What it is for, and what it holds

Evidence that an entity meets an external standard or an internal control obligation, and the reviews
that test it. Certificates and statements of applicability, control descriptions and their evidence
artifacts, internal and external audit reports, findings and corrective-action logs, evidence-request
(PBC) lists, attestation registers, management responses, remediation plans and closure evidence.

## Node test — passes, but it is a PURPOSE row and says so

The anchor is a **control and the assessment that tested it**. Detection signals are genuinely
distinct — the finding structure (reference, severity, response, owner, target date) and the
evidence-request list appear in no other situation in the family.

The honest weakness, stated in the row's own `open_question`: most of its *members* are other rows'
artifacts. An access-review export, a backup log, a training record and a signed policy become
compliance evidence only because someone gathered them for an assessment. That is exactly `00`'s
purpose-versus-topic separation and exactly its content-incoherent-but-purpose-coherent group, so the
row is licensed — but it depends on that separation holding at scale more than any sibling does. If
NJ-3 (the scope of `purpose`) resolves narrowly, this row loses its anchor.

The `soft.tech-compliance-evidence` fold was inherited from the roster and is real but seamed: the
same configuration file is repository content and audit evidence at once. That is recorded as a
`collides_with` against `code.software-project` and flagged for R1c rather than accepted silently.

## Files considered and rejected

- **`ISO 27001-2022 standard.pdf`** — kept as the collision fixture. The published standard is not
  conformity to it; this is the tempting false file.
- **`Food hygiene inspection report.pdf`** — kept as a second fixture, against
  `retail_hospitality.food-safety`: a statutory sector inspection has the finding shape exactly.
- **`Supplier security questionnaire - completed`** — kept because it is the clean case of one
  document being two rows' evidence depending on which side the holder is on.
- **A financial statement audit file** — left as a `collides_with` against `finance.tax-filings`
  rather than an example; the word *audit* covering two families is stated once, not twice.
- **A GDPR record of processing** — real and in scope, but it is a register and would have duplicated
  the risk-register confusion; dropped at gist depth.

## proposed_fields

**None** — deferred to the schema row. This row would want a standard-or-framework concept and an
assessment-occurrence concept; both are noted in prose in `template.why` and neither is minted.

## Neighbours considered that did NOT get an edge

- **`government.professional-regulator`** and **`government.environmental-regulation`** — an
  authority's inspection record. Left unedged because the which-side-is-the-holder discriminator is
  already carried by the `corporate-regulatory-filings` sibling and by the schema row's `government`
  collision; tripling it adds nothing.
- **`manufacturing`** quality-system rows — same shape, same reason.
- **`nonprofit.standards-body`** — a standards body's own material rather than conformity to it;
  noted, not edged.

## NEEDS-JOSEPH

- **NJ-BO-6 · This row's licence depends on NJ-3 (`purpose` scope).** If purpose is narrowed, fold
  this row into `business_operations.risk-register` plus `business_operations.policy-handbook`.
- **NJ-BO-7 · Confirm the `soft.tech-compliance-evidence` fold.** It is defensible and it leaves a real
  seam with `code.software-project`. R1c should confirm rather than inherit.
- Carries **NJ-J-IND-4** by inheritance: an open finding describes a live weakness in an entity that is
  often not the user, and no safety flag reaches it.
