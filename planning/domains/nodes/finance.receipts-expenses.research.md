# finance.receipts-expenses — lab notes (R1b)

Roster row: `kind: template`, `schema_id: finance`, `launch: safety`, `provenance: inference`,
`file_kind_owner: ["email"]`, `must_consider_neighbors: [photos]`,
`must_consider_residuals: [Receipts and Confirmations]`.
Verdict: **node accepted** (`refuse_node: false`).

## Sources used

- `planning/00-database-agent-product-design.md` — read in full. Every span in quote marks in the
  node JSON was grep-verified against this file before it was written; a scripted re-check after
  writing reported **48 quoted spans, 0 missing**. Two were repaired during that pass: the
  consulting role-split sentence needed `00`'s curly apostrophe (`the author’s firm`), and
  `'delivery notice'` was a value of mine sitting inside quote marks — de-quoted, because a value
  in quote marks reads as a citation.
- `planning/01-product-design-structured.md` — §7.3 only (the residual library table, to confirm
  the nine names' spelling). `00` wins; nothing was taken from 01 that 00 does not say.
- `planning/domains/_CONTRACT.md` (entry shape, rules 8/11–15), `planning/prompts/ALIGNMENT.md`,
  `planning/domains/CONNECTION.md`, `planning/domains/CONNECTION-EXAMPLES.md` (fixture 8 is this
  schema's: three insurance situations, one finance vocabulary — the same discipline this node
  follows).
- `planning/domains/roster.json` (id, kind, schema, neighbour ids), `canonical_fields.json`,
  `src/evidence_shape/vocabulary.py` (`SOURCE_TYPES`).
- Landed neighbour nodes, read to align edges and **not** rewritten:
  `finance.json` (my schema), `photos.screenshot-captures.json`, `photos.scanned-documents.json`,
  `photos.camera-events.json`.

## Node test — why this is not the Finance schema's default template

The schema's default (`finance.json`) recommends `institution → account_type → record_type` and
runs on a **labelled account-record structure**: statement period, balance, account descriptor.
Three things differ here, and any one of them would carry the row:

1. **Detection signals.** This template's anchor is a **transaction** structure — a seller in a
   positionally weighted zone, an order-or-transaction identifier, item rows, a labelled total.
   No account structure appears on a receipt, and the roster gives this row the `email`
   source type, which the default template never sees.
2. **Recommended dimensions.** `account_type` is **dropped, not reordered** — `finance.json`'s own
   e-receipt example already records that "a one-off retail purchase belongs to no account", so
   the level would open a tree slot no fact can fill. That leaves two levels, and the honest
   default is shallower still (see below).
3. **Privacy rule.** The default template's characteristic fallthrough is Protected Records, whose
   members "must not cause filenames or content to be exposed in model prompts". This template's
   characteristic fallthrough is **Receipts and Confirmations**, an ordinary residual whose members
   `00` explicitly puts through the residual review dossier. Same safety domain, narrower rule.

## Dimension order — the reasoning I did not take a shortcut on

`institution → record_type`. `institution` leads by `00`'s parent-dimension rule (a delivery notice
is unintelligible until the seller is known); `record_type` is the leaf.

`tax_year` is destination-eligible on the schema and deliberately **absent**: a purchase date is
not a tax year, and `00`'s rule for record domains is that project/function/subject comes before
time. Year-first is `finance.tax-filings`, a different situation on this same schema.

I nearly recommended one level (`institution` alone) or no branch at all, and the node records that
as the honest fallback rather than hiding it: most of this material is the isolated kind `00` sends
to a residual, and `00` requires the canvas to warn when a level "creates a large number of tiny
folders" and to "recommend flattening when a dimension does not materially improve retrieval".
A per-seller × per-record-type split of a real receipt pile is mostly one-file folders.

## proposed_fields — none, deliberately

`proposed_fields: []`. Two candidates were considered and rejected:

- **`merchant`.** Rejected. `institution` is canonically "the financial or record-issuing
  institution a record belongs to"; on a receipt the merchant **is** the issuer. Minting a synonym
  is the 574's defining failure, and `00`'s rule is that values are created at runtime while fields
  are not invented automatically.
- **a payment-institution counterpart** (the bank behind the card tail, the processor block).
  Rejected as a field, **recorded as this node's `open_question`** instead. The tension is real and
  is exactly `00`'s role-separation case: on a statement the bank is `institution` and the merchant
  is content; on a receipt the merchant is `institution` and the bank is content — one key
  inverting between two templates on one schema. Whether that needs a canonical counterpart is a
  shared-vocabulary decision, not a template's.

Two file examples list `account_holder` in `facts_legal`. That key is **proposed on the schema**
(`finance.json`'s `proposed_fields`), not yet canonical; I reference it rather than re-proposing it,
so R1c resolves it in one place.

## Files considered and rejected

- **A bank statement full of merchant rows.** Kept, but as the *collision fixture* pointing at
  `finance.personal-records`, not as this template's material.
- **A utility bill / subscription renewal notice.** Rejected as an example — it is
  `finance.subscriptions-utilities`. Kept only as a collision entry, with the service-period slot
  named as the discriminator; the renewal receipt is the genuine boundary case and abstention is
  the correct outcome there.
- **A pay stub, a 1099-shaped payer form, an EOB.** All already fixtures on `finance.json` or on
  `finance.payroll-received` / `finance.insurance-healthcare`. Not re-used.
- **A `.ics` for a delivery window, a `.vcf` for a seller.** Rejected outright: `SOURCE_TYPES` are
  not domains (CONNECTION-EXAMPLES fixture 5), and `00` keeps contact data privacy-protected rather
  than a proposal basis. Neither appears in `file_kinds`.
- **A charitable-donation acknowledgement as its own example.** Folded into the `tax_year`
  deterministic signal instead — it is the one receipt shape that legitimately carries a labelled
  tax-year slot, and it did not need a twelfth-and-a-half fixture to say so.

The twelve that survived cover the ugly cases the prompt asks for: labelled form
(`Invoice - Bright Plumbing - March 2026.pdf`) vs unlabelled prose
(`Appointment Confirmation - Dr Reyes.eml`); OCR of the same thing twice
(`receipt_2026-03-02.jpg` photographed, `Screenshot 2026-06-11 at 09.02.44.png` captured); an
archive packet read from its manifest (`expenses-q1-receipts.zip`); mail
(`Your order confirmation - Uniqlo.eml`, `Your package has been delivered.eml`); a look-alike that
belongs to a neighbour (`Visa Statement May 2026.pdf`); a file that is legitimately two schemas
(`receipt_2026-03-02.jpg` — finance and photos on disjoint evidence); and the sparse
`HW 3`-shaped case (`IMG_0455.jpg` — an illegible slip that sits in a capture session with legible
receipts and takes **no** fact from them, `group_without_copying_facts: true`).

## Edges

- **`collides_with`** (template ↔ template, per CONNECTION §5): `photos.screenshot-captures` and
  `photos.scanned-documents` **reciprocate edges those two nodes already authored at me** — I
  matched their discriminators rather than inventing new ones. Added:
  `finance.personal-records` (the sharpest, because same vocabulary),
  `travel.bookings-confirmations`, `finance.subscriptions-utilities`,
  `finance.small-business-bookkeeping`. Every target is a roster id (verified against
  `roster.json`).
- **`also_holds_with`: empty, on purpose.** CONNECTION §5 restricts it to **schema ↔ schema**, and
  `finance.json` already carries `also_holds_with: photos` for exactly the photographed-receipt
  case. Writing it again on a template row would be a second vocabulary for one join. Where a file
  legitimately holds two schemas, this node says so in `file_examples[].also_schema` instead.
- **`role_split`**: one entry, `institution ↔ client` at `career.consulting-client-engagement` — the
  reimbursable expense receipt names the vendor that was paid and the client that will be billed,
  two roles on one entity type. `00` gives the firm/client pair; the vendor/client reading is mine,
  marked `inference`.
- **`parent_id`: null, never authored** (PR-5 — R1b cannot see the shelf).
- **`shares_field`**: never authored (derived).

## Neighbours considered that got no edge

- **`photos.camera-events`** — a photo of a table with a bill in frame is tempting, but the
  discriminator is already fully carried by the `photos.scanned-documents` edge (paper geometry vs
  scene), and a third photos edge would restate it. `IMG_0455.jpg` covers the abstention case.
- **`finance.tax-filings`** — not a collision. A deductible receipt inside a filing packet is
  **multi-membership** (a P9 group), which `00` licenses directly ("A file may validly belong to
  more than one accepted group"). Recorded in `grouping_reasons`, not as an edge.
- **`finance.insurance-healthcare`** — a co-pay receipt sits near it, but the discriminating
  structure (claim number, date of service, plan-paid) is the EOB's, already fixtured on
  `finance.json`. The protected subset is carried by the `Protected Records` fallthrough instead.
- **`career.employment-records`** — the offer-letter-with-a-compensation-figure trap is already the
  `finance` schema's collision fixture with `career`; repeating it at template level would be
  noise. My `never_alone` carries the money-figure rule that makes it fail here too.
- **`identity`, `legal`, `medical`** — schema-level safety joins, already on `finance.json`. A
  template row may not author `also_holds_with` at all.

## Where this prompt and CONNECTION.md disagreed

The dispatch prompt's edge table describes `also_holds_with` as usable on this row ("One file may
legally carry both schemas"). CONNECTION §5 says schema ↔ schema **only**. **CONNECTION wins**
(stated in the prompt's own last line), so the list is empty and the two-schema facts live in
`file_examples[].also_schema`.

Minor shape note: the prompt's JSON skeleton puts three keys in `recognition`, and mentions
`proposed_context_terms` without placing it. `finance.json` nests it inside `recognition`; 22 of
the 25 landed nodes that carry it put it at top level. I followed the majority (top level) so R1c
merges one shape, and flag the split here.

## NEEDS-JOSEPH (this node only)

- **NJ-recexp-1 · The merchant/payment-institution double role.** A card-paid receipt names two
  organizations in two roles and this schema has one key for both, and the key **inverts** between
  this template and `finance.personal-records` (receipt: merchant is `institution`; statement: bank
  is `institution`, merchant is content). Does the shared vocabulary get a counterpart key, or does
  `institution` stay a per-template reading with the processor left unextracted? Carried verbatim
  in the node's `open_question`. It compounds the schema's already-open `account_holder` question —
  both are about the same paragraph of `00`, and they should be answered together.
