# finance.loans-mortgage — lab notes (R1b)

Date: 2026-08-22
Row: `kind: template`, `schema_id: finance`, `launch: placeholder`, `provenance: inference`.
Output: [`finance.loans-mortgage.json`](finance.loans-mortgage.json).

## Sources actually used

- `planning/00-database-agent-product-design.md` — read in full. Every quotation in the node was
  grep-verified against it before it was written (36 distinct spans; the check script is in the
  session, not committed). **`00` never uses the words loan, mortgage, escrow or amortization** —
  verified by grep. That is why this row is `provenance: inference` and why nothing borrowing-
  specific is dressed as design.
- `planning/domains/_CONTRACT.md` — entry shape; rules 6, 8, 10–15.
- `planning/domains/CONNECTION.md` + `CONNECTION-EXAMPLES.md` — node test (§2), closed edge
  vocabulary (§5), activation ≠ grouping (§4 step 9), PR-2 (safety), PR-6 (field-less
  placeholders), PR-8 (insurance as templates). Fixtures 4 (passport), 5 (`.ics`), 6 (`HW 3.pdf`)
  and 8 (insurance) are the ones this row had to stay compatible with.
- `planning/prompts/ALIGNMENT.md` — work types are values; a template that only repeats its
  schema's default is not a node.
- `planning/domains/roster.json` — confirmed my row and every edge target id.
- `planning/domains/canonical_fields.json` — the four Finance keys; `account_holder` is the
  finance schema row's *proposed* key, referenced here, not re-proposed.
- `src/evidence_shape/vocabulary.py` — `SOURCE_TYPES`.
- Landed neighbours read to align (not rewritten): `finance.json`, `finance.personal-records.json`,
  `finance.tax-filings.json`. `finance.personal-records` already authors a
  `collides_with finance.loans-mortgage` edge with the fixture `Mortgage Statement Mar 2026.pdf`;
  this row reciprocates it with the same fixture and the same discriminator, deliberately.
- Not consulted: `planning/deferred-catalogues/` — this row's recognition consumes no existing
  catalogue. It names rule *families* (organization gazetteer at word boundary, explicit
  tax-year pattern) and writes no gazetteer contents (R4's) and no regex (R2/R6's).

## Why this is a node and not padding

The node test is disjunctive, and this row passes on **two** clauses, which is recorded in
`node_test_note`:

1. **Dimensions differ.** The Finance schema's default and `finance.personal-records` both open on
   `institution`. This situation must not, because **servicing transfers move one loan between
   companies**: originator → purchaser → servicer → second servicer is ordinary, and
   institution-first splits one loan's lifecycle across sibling folders. Recommended:
   `account_type` (which borrowing) → `record_type` (which document), with `institution` offered
   as an *optional* level between them only where a person holds several loans of the same kind.
2. **Detection signals differ.** The discriminator is the amortization structure — a labelled
   principal/interest(/escrow) split against a labelled remaining principal balance, with a loan
   identifier and a borrower block. No other finance situation carries it. A deposit statement has
   a balance and no split; a receipt has a total and neither.
3. (Also true, and the reason the row is worth its own privacy paragraph.) **Privacy differs in
   kind.** An application or closing packet *aggregates* unmasked identification, income,
   employment, other institutions' balances, a property address and a co-borrower's records into
   one bundle. The packet discloses more than any member; a packet-level dossier must never be
   assembled for a cloud call even where one member might have been eligible.

Had only (1) or only (2) held I would still have kept it; had neither held it would have been
`refuse_node: true` as a re-spelling of `finance.personal-records`.

## Files considered and rejected

Kept 15 examples. Rejected on the way:

- **`Rate Sheet - 30yr Fixed.pdf` (lender marketing).** Carries an institution, a rate and loan
  vocabulary, and is a record of nothing. It would have duplicated the work
  `Mortgage Rates Explained.pdf` does in `never_alone`, so it stayed a never-alone entry rather
  than an example.
- **`Credit Report.pdf`.** Lists every loan the person holds. Genuinely tempting, and rejected
  because it belongs to no single loan and would push toward a credit/identity schema this roster
  does not have. Its real home is the finance schema's activation plus identity co-activation;
  giving it an example here would have implied a lifecycle membership it does not have.
- **`Escrow Analysis 2026.pdf`.** Real and common, but it exercises exactly the slots
  `Mortgage Statement Mar 2026.pdf` already exercises plus the insurer/tax-authority seam already
  stated in `collides_with finance.insurance-personal`. Dropped as duplication.
- **`Deed of Trust (recorded).pdf`.** Would have been a third also-legal fixture after
  `Closing Disclosure.pdf` and `Auto Loan Agreement.pdf`. Two is enough to state the seam.
- **`Mortgage payment due.ics`.** Kept as a `never_alone` clause and as a `file_kinds` note rather
  than an example: it demonstrates fixture 5's rule (a `SOURCE_TYPE` is not a domain) but produces
  no facts, and an example whose whole content is "nothing activates" is better said once.
- **A `contacts`/`.vcf` example.** This situation sees loan-officer contact cards, but `00` keeps
  VCF data privacy-protected rather than a proposal basis, so the honest entry is "no facts", and
  `identity.core-documents` already owns that source type on the roster.

Kept because they are the ugly cases the prompt asks for: unlabelled prose
(`Servicing Transfer Notice.pdf`), OCR screenshot (`Screenshot 2026-06-02 …png`), archive packet
(`closing_packet_2026.zip`), mail (`Payment received - confirmation.eml`), encrypted
(`eClosing_docs_protected.pdf`), the sparse `HW 3` analogue (`scan_0042.pdf`), a file that looks
like mine and is the neighbour's (`Lease Agreement - 42 Oak St.pdf`), a file that is also another
schema's (`Closing Disclosure.pdf`, `Auto Loan Agreement.pdf` → legal; `Loan Application -
Signed.pdf`, `closing_packet_2026.zip` → identity), and the calculation-that-is-not-a-record
(`Amortization Practice.xlsx`).

## proposed_fields: none, and why

Three keys were tempting; all three were refused rather than minted.

- **`loan_number`** — it is a *grouping* identifier, not an organization dimension. P9 can anchor a
  loan neighbourhood on it as evidence without it ever becoming a field, and `00` is explicit that
  the system "should not invent new fields automatically".
- **`property_address`** — an address appears on utility bills, leases, insurance declarations,
  delivery receipts and tax notices. Minting a shared-vocabulary key from one template row is the
  574's failure mode in miniature.
- **`loan_kind`** — that is `account_type`, already canonical. A synonym is a second column.

`account_holder` is referenced (it appears in `facts_legal` on several examples) but **not
re-proposed**: it is the finance schema row's open proposal, and duplicating it here would double
a pending decision. The co-borrower question — one holder fact or several on a joint loan — is the
schema row's open question, not a new key.

## Neighbours considered that did not get an edge

- **`finance.receipts-expenses`** — a payment-confirmation email overlaps, but the discriminator is
  already carried by the `finance.personal-records` and `falls_through_to Receipts and
  Confirmations` entries, and a collision edge needs a real evidence-item mutex. Left unasserted;
  "unlisted just means unasserted" (CONNECTION §8).
- **`finance.payroll-received`** — pay stubs ride inside the application packet, but that is
  *multi-membership*, not a mutex: nothing about a pay stub is confusable with a loan record. It is
  recorded as a `grouping_reasons` entry and in `must_not_conclude` on the application example.
- **`career.employment-records`** — the employer name on an application form is a temptation, and it
  is answered by a `never_alone` clause plus a `must_not_conclude` line. A collision edge would
  claim the two document *kinds* are confusable, which they are not.
- **`finance.cap-table-equity`, `finance.small-business-bookkeeping`** — business borrowing exists,
  but a term loan to a company is this template's material by structure; no discriminating evidence
  distinguishes them at the *evidence-item* level, so no edge.
- **`legal.personal-legal-matters`** — a foreclosure or a recorded release touches it. Held back:
  `legal.leases-agreements` already carries the contract seam, and a second legal template edge
  would be asserting a mutex I cannot name discriminating evidence for.
- **`photos.scanned-documents`** — a photographed closing page. The photos seam is stated at schema
  level on `finance.json` (`also_holds_with photos`, `collides_with photos`) and per-file in
  `also_schema`; `photos.screenshot-captures` is already `finance.personal-records`' edge and the
  screenshot fixture here reciprocates nothing new.
- **`also_holds_with`: none authored.** It joins schemas only (CONNECTION §5); this is a template
  row. The finance↔legal, finance↔identity and finance↔photos joins this situation exercises are
  already on `finance.json`, and nothing here asks to add a schema pair.

## Compatibility checks run

- Every `file_examples.source_type` ∈ `SOURCE_TYPES`; every `facts_legal` key resolves to
  `canonical_fields.json` (plus the schema row's proposed `account_holder`); every
  `collides_with.domain` is a roster `domain_id`; every residual name is one of `00`'s nine, in
  `00`'s spelling; `dimension_order` uses only destination-eligible Finance keys; no folder path
  appears as a fact; no threshold, score or handling class appears anywhere.
- `parent_id` is `null` and unauthored (PR-5: R1b never authors it). `shares_field` is absent
  (derived-only). No `related_to`.

## NEEDS-JOSEPH (this node only)

- **NJ-loans-1 · Which loan?** Two mortgages, or two student-loan groups, collapse into one
  `account_type` branch, and the identifiers a person actually uses — the loan number and the
  collateral — are not fields. Three answers: (a) the loan is a P9 group and the folder stays
  coarse (what this row recommends); (b) promote `institution` to a level (which servicing
  transfers break); (c) mint a loan-identity key (a change to the shared field table that one
  template row must not make). Carried in the node's `open_question`.
- **NJ-loans-2 · Packet whole, or split?** Should a closing/application packet be preserved as one
  branch — `00` allows it for a purpose-defined packet — or split by `record_type` like the rest of
  the lifecycle? This is a decision about someone's real filing, with a privacy edge: a packet held
  whole is easier to find and keeps identity scans beside the loan documents.
- **NJ-loans-3 · Does the schema's `account_holder` proposal cover a co-borrower?** A joint loan has
  two holders and one of them may not be the corpus owner. Whether that is one field with several
  values, or a role split, belongs with the schema row's open question, not here — flagged so R1c
  does not resolve it silently while merging.
