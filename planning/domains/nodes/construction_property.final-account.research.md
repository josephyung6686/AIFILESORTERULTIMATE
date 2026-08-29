# construction_property.final-account — deep research memo

Depth: J-DEPTH. Placeholder row (J-IND, deepened under the 2026-08-24 ratification).

## Verdict

**The node stands, but only as the whole contract-payment settlement lifecycle.** It does not stand
for a document called `Final Account`, construction money generally, or merely the last state of
`construction_property.construction-project`. Its distinct process is:

`application → valuation/certification → notice or pay-less notice → payment with retention →
staged release → final reconciliation`.

Each step answers the preceding step, the figures are cumulative, and the closing balance depends
on amounts previously certified. The branch root and an accounting ledger do not share that state
machine. The final account stays here because it settles the cycle arithmetically; it does not earn
a second node. This sharpens, rather than reverses, the gist draft.

## Sources and method

Read `RESEARCH-BRIEF.md`, `DEEPEN-ADDENDUM.md`, and the output of
`python3 planning/domains/dispatch/make_prompt.py construction_property.final-account`; then
`ALIGNMENT.md`, `00-database-agent-product-design.md`, `_CONTRACT.md`, `CONNECTION.md`,
`CONNECTION-EXAMPLES.md`, `canonical_fields.json`, `roster.json`, and the deepened
`construction_property.research.md` schema anchor. Compared the JSON and memos for
`construction_property.construction-project`, `variation-claim`, `quote-estimate`,
`business_operations.contract-administration`, `procurement-sourcing`,
`finance.small-business-bookkeeping`, and `finance.receipts-expenses`.

Quotation marks below contain exact spans from `00`; unquoted industry descriptions are named-file
evidence or marked inference. No external legal rule is required for the node verdict.

## What it holds

The row holds applications for payment, interim valuation build-ups, certificates, payment and
pay-less notices, retention statements and release requests, final certificates, draft and agreed
final accounts, priced day-work substantiation, and settlement correspondence. Its positive
fixture, `Valuation 07 - application for payment.xlsx`, starts with work valued to date, deducts
what was previously certified, deducts retention, and derives the current sum. `Interim Certificate
No 7.pdf` answers it with a certified sum. `Pay Less Notice - Valuation 07.pdf` answers with a lower
sum and reasons. `Final Account - draft 3.xlsx` reconciles the original sum, adjustments, prior
certificates, retention and balance.

The same amount can later appear in an invoice, posting and remittance without making those files
one situation. Purpose and apparatus decide: “Topic answers what a file is about, while purpose answers what the file was for.”

## Node test

### Detection differs

The schema default is mixed construction/property material and declares no domain fields. Its
family-wide rule prevents an address, firm, document-type word or amount activating a child. This
row instead requires a conjunction: cumulative gross valuation, labelled prior certification,
retention held or released, a numbered cycle, answer relationships among application/notice/
certificate, or whole-contract reconciliation. A percentage, money total, certificate, the word
`final`, a source type, or a job name never suffices.

The spreadsheet structure is valid observation because “Tables matter because resumes, forms, applications, invoices, and administrative documents often place their most useful information in cells rather than body paragraphs.” It is detection only: `fields` remains empty.

The branch root activates on award/particulars, programme, practical completion and handover. It
explicitly demotes valuation and final-account apparatus here. Shared fixture: `Valuation 07 -
application for payment.xlsx`. Its contract reference corroborates browse membership there; its
cumulative cycle activates here. Neither side copies a project fact to a sparse file: “The graph does not automatically copy those missing facts onto sparse files.”

### Recommended dimensions differ

The binding JSON answer is `dimension_order: []`, since the schema licenses no field rows. Held in
prose only, the eventual recommendation is contract/job → settlement stage → valuation cycle. A
bare `07` is meaningless across contracts: “The recommendation should follow the practical rule that a parent dimension should provide the context required to understand the child.” It is not
time-first; a calendar hierarchy would split a running account, contrary to “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders.” This process-state view differs from the general
project view and Finance's institution/account/record-type view.

### Privacy differs

Valuations expose rates, preliminaries, margin, subcontract prices and cash position. Pay-less
notices contain allegations; day-work sheets can name workers and hours. “Privacy policy must be enforced before content reaches any model or external connector.” Assertions must not become
defect facts, and “A model that cannot cite sufficient evidence must return unknown.” JSON uses
only `potentially_sensitive`; P7 owns handling. The distinction is material because a drawing can
often be summarized without commercial rates, while a valuation cannot.

## Why it is not merely a terminal project state

The refusal argument would succeed if the row held only `Final Account.pdf`: that is merely a
`work_type`. But the actual series begins during construction and repeats. Each cycle depends on
the prior certified total; retention survives across cycles; the final account closes that series.
The project also contains award, programme, drawings, instructions, diaries, defects and handover,
none of which enters this arithmetic. Thus construction-project is the browse container and this
row is the settlement lifecycle inside it. Inference: practical completion can occur while
retention and account negotiation continue, illustrating why terminal project state is the wrong
organizing model, though chronology is not itself a detector.

## Reciprocal neighbour boundaries

### variation-claim

Same bytes compete: the variations tab in `Final Account - draft 3.xlsx` and `Quotation for VO 17
- revised drainage.pdf`. Variation-claim owns instruction/variation number, notice, entitlement,
clause, cause-and-effect narrative and requested consequence. This row owns reconciliation of the
whole contract after changes become account lines. From that side, an agreed variation remains
change evidence but its price inside a cumulative account does not activate a claim. From this
side, an additions/omissions schedule without original sum, prior certificates, retention and
balance is not a final account. The JSON edge reciprocates the landed neighbour.

### quote-estimate

Same bytes compete: quantities, rates and total. A quote is prospective, with validity and
acceptance and no work-to-date. A valuation is retrospective and cumulative, with measured or
percent-complete work, prior certification and retention. Acceptance does not transform the
original offer into a valuation; an original schedule of rates attached to the account does not
become a new offer. A variation quote inside a live contract belongs primarily to variation-claim
until absorbed into cumulative settlement.

### contract-administration

Same bytes compete: agreement reference, payment clause, notice and deadline. Contract
administration owns the general obligations lifecycle—register, renewal, deliverables, notices,
compliance and amendments. This row owns movement of money through construction settlement states.
A payment clause or contract value alone does not activate this row; a certificate citing the
agreement does not become an obligations register. The contract is context here and the managed
object there.

### procurement-sourcing

Same bytes compete: bill of quantities and pricing schedule. Procurement owns the pre-award
competition—requirement, solicitation, bid instructions, deadline, comparison and award. This row
owns payment under the awarded contract. A tender return is not a valuation without work-to-date,
prior certification and retention. The original bill can substantiate rates later without
reopening procurement. Award is the lifecycle boundary.

### finance.small-business-bookkeeping

This is the sharpest seam. Same bytes compete: client, works, amount, tax lines and payment state.
Bookkeeping owns invoices, bills, postings, ledger accounts, reconciliations, receivables/payables
and reporting periods. This row owns cumulative contractual entitlement and certification. An
invoice number, tax treatment, terms or posting does not activate this row. A certified sum and
retention do not prove posting, invoicing or payment. A remittance may group with a cycle without
activating it.

For a small trade firm one artefact may be both application and invoice. Both memberships may be
valid when supported by disjoint evidence; otherwise abstain. Industry alone never settles it:
“Correct abstention is a successful outcome because the product’s goal is reliable organization, not maximum file movement.”

### finance.receipts-expenses

No direct edge is added. That row owns one transaction-shaped record and routes isolated invoices
and receipts broadly. `INV-2291.pdf` remains Finance or residual material when it is simply a
demand. A receipt can join an accepted valuation group, but without contract-cycle apparatus it
does not activate this row. Conversely a certificate certifies a sum; it does not acknowledge
payment. Bookkeeping is the true structural collision, so adding the broader transaction neighbour
would dilute the graph.

## Concrete files considered and rejected

1. `Valuation 07 - application for payment.xlsx` — positive cumulative spreadsheet fixture.
2. `Interim Certificate No 7.pdf` — positive certificate; certifier authorship is no destination.
3. `Pay Less Notice - Valuation 07.pdf` — positive answer state; reasons are assertions, not facts.
4. `Final Account - draft 3.xlsx` — positive but negotiation status remains unresolved.
5. `Settlement letter - full and final.docx` — closing evidence, not a legal-effects conclusion.
6. `Retention release - second moiety.pdf` — request does not prove release or completion.
7. `IMG_2201_daywork_week12.jpg` — OCR seam with timesheet; handwriting cannot establish hours.
8. `valuation_pack_v07.zip` — manifest raises a candidate packet; members retain their situations.
   “A session should never be treated as proof of topic, and it should not carry the same confidence as a hash match or a directly extracted document fact.”
9. `INV-2291.pdf` — rejected collision fixture: invoice id, tax and terms support Finance.
10. `Quotation for VO 17 - revised drainage.pdf` — variation material until cumulative settlement.
11. `Tender return - measured works.xlsx` — rejected: prospective quote/procurement evidence.
12. `Contract obligations register.xlsx` — rejected: general contract administration.
13. `Bank Reconciliation - Operating Account - June 2026.xlsx` — rejected: accounting apparatus.
14. `Practical Completion Certificate.pdf` — rejected from activation: project boundary event.
15. `Adjudication referral notice.pdf` — rejected: dispute material; no legal merits judgment.

The collision pair is `Valuation 07 - application for payment.xlsx` versus `INV-2291.pdf`. The
former must not be lost to accounting merely because it requests money; the latter must not be
stolen merely because it describes building work.

## Grouping and residuals

One cycle can group application, notice, certificate, pay-less notice and remittance. One contract
can group cycles. Draft accounts form a version family. A pack can group measures, photos and
narratives by purpose: “The documents are content-incoherent but purpose-coherent.” None of this
copies contract, cycle, party or amount facts to sparse members.

- **Independent Records:** “Independent Records may live under Personal/Independent Records and hold standalone certificates, notices, confirmations, forms, and PDFs that have a durable purpose but no broader group.”
- **Receipts and Confirmations:** “Receipts and Confirmations may hold isolated invoices, delivery confirmations, booking records, boarding passes, purchase receipts, event tickets, and similar transactional documents.”
- **Review Later:** “Review Later may hold files whose meaning is partly understood but whose final location requires a future decision.”
- **Unsupported or Encrypted:** “Unsupported or Encrypted may hold—or, more safely, represent without moving—password-protected archives, unreadable documents, damaged files, and unknown formats.”

## Fields, proposals, and non-edges

`fields: []`. `proposed_fields: []`. No canonical key is minted. Contract/job, settlement stage and
valuation cycle remain prose because a child cannot settle its schema's deferred vocabulary.

No new edge to `finance.tax-filings`: deduction records are jurisdictional evidence, not the cycle.
No edge to customer-account-management: debtor follow-up lacks certification apparatus. No broad
legal edge: a settlement may also be legal, but operative effect requires separate evidence. No
logistics edge: delivery evidence may substantiate work but has no shared activation structure.

## NEEDS-JOSEPH

- **NJ-CP-FA-1 — small-trade convergence.** For one dual-purpose application/invoice, choose both
  memberships, bookkeeping preference, or a corpus-level user choice. Both creates duplicate views;
  bookkeeping-only loses the cumulative cycle; construction-only weakens the books.
- **NJ-CP-FA-2 — quantity-surveyor view.** Offer a saved view separating interim cycles from closing
  drafts? A second node is rejected because the arithmetic is continuous.
- **NJ-CP-FA-3 — dual-purpose settlement letter.** Automatic legal co-membership improves retrieval
  but risks implying legal effect; explicit acceptance is safer but hides the seam.

## What changed in this pass

Replaced the retired gist memo; preserved but narrowed the stands verdict to the complete settlement
lifecycle; made the terminal-work-type objection explicit; clarified JSON grouping and the open
question; compared all charged neighbours reciprocally; retained empty `fields`, empty
`proposed_fields`, and empty `dimension_order`; added no weak neighbour edge.
