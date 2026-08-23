# construction_property.sale-purchase — lab notes (template row)

**Depth: GIST** (J-IND). Honest map, not deep per-industry research. Not padded.

## Sources

`00-database-agent-product-design.md` (quotations machine-verified verbatim), `ALIGNMENT.md`,
`_CONTRACT.md`, `CONNECTION.md`, `roster.json`, `canonical_fields.json`, `DECISION-BRIEF.md`
(J-IND, D1, PR-6), `ROSTER.md` §4 → `13-trades-property-logistics.json` (line 920). Neighbours read
in full first, as the dispatch brief required: `finance.household-property` (whose `work_types`
already include *purchase closing record* and *sale closing record*) and `legal.leases-agreements`
(whose collision signals against `finance.household-property` this row deliberately reuses
word-for-word in shape, so the three rows describe one seam the same way).

## What it is for, and what it holds

One transaction in progress. Title register copies and plans, searches, property information and
fittings forms, pre-contract enquiries and replies, the contract through its drafts and its
execution, a survey and a mortgage offer supplied in, identity and source-of-funds evidence
gathered under an anti-money-laundering duty, the completion statement, the transfer, the tax
return, and the registration confirmation that closes it.

## Node test — passes, on the pack and its dissolution

1. **Signals differ:** *stage vocabulary tied to one address* — offer accepted, enquiries raised,
   exchange, completion — is a fingerprint that exists only while a transaction is running. So is
   the title-and-search bundle (machine-generated documents with reference numbers that no
   household produces for itself), and the property questionnaire, which is a form whose questions
   are about a *building* rather than a person.
2. **Dimensions differ:** property → transaction → **stage**, and stage earns its place because a
   member's meaning changes with it: the same contract text is a draft before exchange and the deal
   after it.
3. **Privacy differs, and more sharply than anywhere else on this schema:** the pack is the most
   concentrated pile of protected material a private person ever assembles.

The row's real distinguishing property is that **the group dissolves**. It is purpose-coherent and
content-incoherent while it runs, and afterwards a handful of members graduate to a permanent
property record and the rest become dead paper.

## Legacy id absorbed (ROSTER.md §4)

`prop.sale-purchase` (ROW), 1:1.

## The hardest thing about this row — stated reciprocally, as the brief required

**The seam with `finance.household-property` is a seam in time, not in content.** That row already
claims closing records, and it is right to. The same transfer, register copy and completion
statement are working papers of a live matter on Tuesday and a homeowner's permanent record a
decade later, and *nothing in the documents announces the change*. This row therefore claims the
**live transaction** (stage vocabulary, open enquiries, unexpired searches, two represented sides)
and concedes the permanent residue. The collision is authored in those terms and the unresolved
half is `NJ-CP-13`.

**The second seam: the mortgage offer has three legitimate homes** — `finance.loans-mortgage` (the
borrower's debt), `construction_property.mortgage-brokering` (the broker's file), and this pack.
All three collisions are authored, and the fixture says so on its face rather than picking one.

**The third: this row is the only one on the schema written from a *transaction's* side rather than
a party's.** That is a genuine structural oddity and it is recorded in `open_question`, because if
it is wrong the row splits between `legal.practice-matter-file` and `finance.household-property`
and does not survive.

## Files considered and rejected

- **`AML - passport and bank statements.pdf`** — kept, with `also_schema: "identity"`, because it is
  the fixture where protection must precede any placement reasoning.
- **`Buildings insurance schedule`** — kept as the collision fixture: bought *because* of the
  purchase, belonging to neither this row nor the transaction group.
- **A removals quotation** — rejected: a service purchase, `Receipts and Confirmations` handles it.
- **An estate agent's particulars PDF** — rejected here; `construction_property.agency-listing` owns
  it and gets the collision instead.
- **A leasehold management pack / seller's LPE1-style form** — real and common on a flat sale, and
  deliberately routed to `construction_property.service-charge` (which this same agent authored) via
  that row's own resale-pack handling, rather than doubled here at gist depth.

## proposed_fields

**None.** PR-6 forbids field rows on this schema. Candidate dimensions (property, transaction,
stage) are prose in `template.why` for R1c. *Stage* would be a new concept for the canonical list;
argued, not minted.

## Neighbours considered that did NOT get an edge

- **`finance.tax-filings`** — the transaction tax return is a filing, but it is a member of the pack
  and jurisdiction-specific; a **value** question under D4, not an edge.
- **`identity.credentials-passwords`** — conveyancing portals issue credentials; too thin.
- **`business_operations.contract-administration`** — a sale contract is not an ongoing obligations
  register; no seam worth authoring.

## NEEDS-JOSEPH

- **NJ-CP-13 · When does a transaction stop being a transaction?** Which members of a completed pack
  graduate to `finance.household-property`, and whether a completed pack moves or stays. Stated
  reciprocally: this row's collision names the discriminator from this side and concedes the
  permanent residue; `finance.household-property` already names the property address as evidence
  that counts for neither. Joseph's, because the answer is about how long a person wants to keep
  dead paper, not about anything in the files.
- **NJ-CP-14 · Whose row is this?** Every other `construction_property` row is written from a
  professional's side. This one is written from the transaction's. If that is rejected, the row
  splits to `legal.practice-matter-file` and `finance.household-property` and should be retired
  rather than rewritten.
