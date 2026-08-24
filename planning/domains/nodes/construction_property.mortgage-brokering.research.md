# construction_property.mortgage-brokering — lab notes (template row)

**Depth: GIST** (J-IND). Honest map, not deep per-industry research. Not padded.

## Sources

`00-database-agent-product-design.md` (quotations machine-verified verbatim), `ALIGNMENT.md`,
`_CONTRACT.md`, `CONNECTION.md` (§4 step 5, the safety split), `roster.json`,
`canonical_fields.json`, `DECISION-BRIEF.md` (J-IND, D1, PR-6), `ROSTER.md` §4 →
`13-trades-property-logistics.json` (line 929). Neighbours read first:
`finance.household-property`, `finance.payroll-received`, `identity.core-documents`,
`legal.leases-agreements`, and the roster hints for `finance.loans-mortgage` and
`legal.practice-matter-file`.

## What it is for, and what it holds

Holding someone else's finances in order to borrow for them. Fact finds, client agreements and
initial disclosures, evidence checklists, the client's payslips, bank statements, deposit evidence
and identity documents, credit reports and search consents, affordability and criteria assessments,
lender comparisons, submission packs, decisions in principle, offers, suitability letters, declined
case notes, and the adviser's own procuration-fee statements.

## Node test — passes, on the fact find and the checklist

1. **Signals differ:** the **fact find** — a single form that inventories a household's entire
   financial life in labelled slots — exists nowhere else in this catalogue. The **evidence
   checklist** is the second fingerprint, and it is a shape rather than a topic: *somebody chasing
   documents from somebody else*, with received and outstanding columns.
2. **Dimensions differ:** client → case → stage.
3. **Privacy rules differ, and this is the strongest leg.** Not because of the subject matter but
   because of **ownership**: almost every document belongs to somebody other than the person whose
   machine it sits on.

## Legacy id absorbed (ROSTER.md §4)

`prop.mortgage-brokering` (ROW), 1:1.

## The hardest thing about this row

**The documents cannot tell you whose they are.** A payslip, a bank statement and a passport scan
are byte-identical whether they are the subject's own records (`finance.payroll-received`,
`identity.core-documents`) or an adviser's copies. The row's answer is that the discriminator is
never the document — it is the *apparatus around it*: a fact find, a checklist, a client agreement,
a suitability letter, a commission disclosure. That is written into `never_alone` explicitly and
into three collisions, all in ownership terms.

**The second hardest: the mortgage offer's three homes.** `finance.loans-mortgage` (the borrower's
debt), this row (the broker's case), `construction_property.sale-purchase` (the conveyancing pack).
The fixture states all three on its face; the collisions are authored in every direction.

**A trap avoided deliberately:** the `template.why` records the practice-shaped order (client →
case → stage) *and* refuses to endorse building it, because a client-first tree puts private
individuals' names in folder names over their own identity documents. `00`'s safety posture and the
row's natural filing habit genuinely conflict, and the row says so rather than picking.

## Files considered and rejected

- **`Procuration fees - Q1.csv`** — kept as the collision fixture, to stop the row annexing the
  adviser's own revenue into a client folder.
- **`Scan_ID_and_utility.jpg`** — kept, with `also_schema: "identity"`, as the protect-before-place
  fixture.
- **A lender criteria guide PDF** — rejected: generic marketing, no case.
- **A credit report** — folded into `work_types` rather than given its own fixture; at gist depth the
  payslip fixture already carries the ownership argument.
- **A commercial or bridging finance case** — the same situation at a different scale; noted in
  `proposed_context_terms` rather than doubled.

## proposed_fields

**None.** PR-6 forbids field rows on this schema, and here the prohibition is doing real work rather
than being a formality: the obvious candidate keys for this row (client, case, borrowing purpose)
would be destination dimensions over third-party protected material, and minting them before the
safety posture is decided would be the wrong order. Argued in `template.why`, not minted.

## Neighbours considered that did NOT get an edge

- **`finance.investment-brokerage`** — a different regulated advice world with the same file shape;
  the `legal.practice-matter-file` collision already carries the "regulated adviser's client folder"
  problem at gist depth.
- **`career.*`** — employment evidence appears, but as a client's supplied document, covered by the
  `finance.payroll-received` edge.
- **`construction_property.development-appraisal`** — development finance is adjacent; too thin here.

## NEEDS-JOSEPH

- **NJ-CP-15 · Is this row on the right schema?** Nothing in the file is about a building; it is
  about a household's money, and the material belongs to two of `00`'s four safety domains
  (finance, identity). The roster put it on `construction_property` and the row is written there, in
  a protection-first posture, so that moving it to the finance family would change only the schema
  pointer and lose no research. Recorded rather than silently resolved, because moving a row across
  schemas is not this agent's call.
- **NJ-CP-16 · Should a client-first tree be built at all over third-party financial material?** The
  practice order and `00`'s safety posture point opposite ways. Stated reciprocally with
  `identity.core-documents` and `finance.loans-mortgage`, both of which hold the same documents from
  the subject's side.
