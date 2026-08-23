# business_operations.vendor-management — lab notes (template row)

**Depth: GIST** (J-IND). Honest map, not deep per-industry research. Not padded.

## Sources

Same authority stack as `business_operations.project-delivery.research.md`; all quotations
machine-verified verbatim against `00-database-agent-product-design.md`. Landed siblings read for key set
and idiom: `business_operations.json` (read closely for the `supplier` field question and for the
`our_firm` / `client` role split it already records), `business_operations.it-asset-inventory.json`
(which carries the reciprocal-facing procurement and contract signals), `finance.insurance-corporate.json`,
`legal.leases-agreements.json`. Legacy row absorbed per `ROSTER.md` Appendix A line 556:
`biz.vendor-management` (ROW).

## What it is for, and what it holds

An organisation deals with the same supplier repeatedly and needs to keep them set up, safe to deal with,
and honest. The row holds onboarding and new-vendor forms, supplier registers and approved-supplier lists,
due-diligence questionnaires and their responses, insurance certificates and credit checks, security and
compliance attestations supplied by the vendor, signed supplier codes of conduct, scorecards and service
reviews, escalation and remediation correspondence, and exit or transition records.

## Node test — passes, and it is the weakest pass of my seven

Stated plainly rather than hidden. The relationship's detection signals *are* distinct from the two rows on
either side — an onboarding form with a remittance block, a supplier register with a relationship owner, a
diligence questionnaire, a scorecard — none of which appears on a solicitation or on an executed instrument.
The dimension order and the privacy caveats differ too. So it passes.

What is uncomfortable is that a real supplier folder contains all three situations at once, and a user asked
to choose would probably want *one* supplier branch. My recommendation, recorded in `open_question`: if R1c
collapses anything in this family, the candidates to merge are **vendor-management and
contract-administration**, not vendor-management and procurement-sourcing — because a sourcing event
genuinely ends, and a relationship and its contract genuinely do not.

## Files considered and rejected

- **`Meridian invoice 2026-0417.pdf`** — kept as the collision fixture. Every supplier relationship generates
  hundreds of invoices, and letting them in would swallow the finance side whole.
- **`Signed MSA - Meridian - executed.pdf`** — kept as the second fixture, and the one that marks the family's
  thinnest boundary. Carries `also_schema: "legal"`.
- **`FW updated bank details - urgent.eml`** — kept deliberately, and it is the single most important example
  in this row. A supplier bank-change instruction is the most impersonated document in commercial life; the
  example exists to state that the product must never write, normalise or act on a payment fact.
- **`Meridian - certificate of insurance 2026-27.pdf`** — kept because it demonstrates the row's own
  `never_alone`: the certificate does not say whether the insured is a supplier or the holder.
- **A supplier NDA** — folded into the legal edge rather than given an example.
- **A sanctions or PEP screening result** — real and in scope; folded into a `work_type` value, since at gist
  depth the credit-check example carries the same lesson.

## proposed_fields

**None, and this is a deliberate refusal.** The obvious candidate is `supplier` — the counterparty-as-vendor
role, which genuinely has no canonical key (00's role split names only `our_firm` and `client`, two of the
three roles in play). But the landed schema row already states, in its `organization` justification, that
"`supplier` is proposed on the contract-administration template rather than smuggled in here." That template
belongs to another agent in this pass. Proposing the same key from two rows would produce exactly the
duplicate-vocabulary failure the contract warns about. So this row **endorses that proposal in prose and mints
nothing**, and records the three-role gap in `open_question` and below.

**Checked after that row landed:** `business_operations.contract-administration.json` writes
`proposed_fields: []` — it did not carry `supplier` either. So the key the schema row said was owed
elsewhere is currently proposed by **nobody**. That is a real gap for R1c and it is flagged as NJ-BO-VM-2
below rather than fixed here, because minting it unilaterally from the row that was told not to is exactly
the failure mode the schema row was guarding against.

## Neighbours considered that did NOT get an edge

- **`business_operations.facilities-workplace`** — facilities suppliers (cleaning, maintenance) are managed this
  way. Same situation, different category; a category is a value.
- **`hr.training-development`** — a training provider is a supplier. Same reasoning.
- **`logistics`** — carriers and 3PLs are the archetypal managed suppliers. Left unedged at gist depth because the
  confusion is about *which* supplier, not about evidence.
- **`government`** — public procurement diligence is heavily regulated and the shape is the same. The regulation
  attaches to the sourcing event, which is the sibling's row, so no edge from here.

## NEEDS-JOSEPH

- **NJ-BO-VM-1 · Is the three-way split one row too many?** Stated above with a recommendation rather than left
  open-ended: merge toward contract-administration if anything merges. Also stated reciprocally in
  `collides_with` on both sides of the sourcing / contract boundary.
- **NJ-BO-VM-2 · The third role has no key.** 00 gives `our_firm` and `client`. Vendor management needs the
  *counterparty-as-supplier* role, and account management needs the same document read from the other side. This
  row endorses the `supplier` proposal the schema row assigned to the contract-administration template rather
  than duplicating it — **but that row landed with no proposed fields at all, so the key is presently proposed by
  no one.** R1c must assign it to exactly one row, or decide the role stays unheld.
- **NJ-BO-VM-3 · Which side of the relationship is the holder on?** A single QBR deck, scorecard or onboarding
  pack frequently does not say. Stated reciprocally against `business_operations.customer-account-management`.
- **NJ-BO-VM-4 · Payment-fact handling.** A bank-change instruction is a fraud vector, not merely confidential
  material. This row states that the product must not write or act on a payment fact found in one; whether that
  needs a mechanism beyond the protected state is a P7 question flagged here because this row is where it bites
  hardest.
