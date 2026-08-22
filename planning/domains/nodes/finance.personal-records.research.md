# finance.personal-records — lab notes (R1b)

Node: `finance.personal-records`, `kind: template`, `uses_schema`/`schema_id: finance`, `launch: safety`.
Verdict: **authored, not refused** — but it was the closest call available, and the reasoning is below.

## Sources actually used

- `planning/00-database-agent-product-design.md` — read in full. Every span this node puts inside
  quote marks was grep-matched against this file before it was written (51 quoted spans, 0 misses).
  No section numbers are asserted of `00`; it has none.
- `planning/01-product-design-structured.md` — read only §3.11 (domain-scoped schemas), §3.15
  (launch scope / safety domains) and §7.3 (the residual nine), as locators for material already
  read in `00`. `00` wins on every point; nothing here rests on `01` alone.
- `planning/domains/_CONTRACT.md`, `planning/domains/CONNECTION.md`,
  `planning/domains/CONNECTION-EXAMPLES.md` (fixture 8 — insurance as three templates on one
  finance vocabulary — is the shape this whole finance shelf follows).
- `planning/prompts/ALIGNMENT.md`.
- `planning/domains/roster.json` — my row, the Finance schema row, and the sixteen sibling
  templates on `schema_id: finance`; every edge id below was checked against it mechanically.
- `planning/domains/canonical_fields.json` — the four finance keys plus the universals. No new key
  was minted or referenced.
- `planning/domains/nodes/finance.json` — the Finance **schema** node, already landed. This was the
  decisive input: it already carries the fields, the schema-level recognition, the schema-level
  `also_holds_with` / `collides_with` set, and a `template.dimension_order`.
- `src/evidence_shape/vocabulary.py` — `SOURCE_TYPES`; all eleven file examples and the
  `file_kinds` list check out against it.

## The node test — why this row survives, stated honestly

The refusal clause is: a template whose **detection signals, dimension order and privacy rules** are
identical to its schema's default template is not a node.

Two of the three are identical, and I did not manufacture a difference to hide it:

- **Dimension order: identical.** `institution → account_type → record_type`, the same order
  `finance.json` already recommends. I considered adding `tax_year` as a level to create a
  difference and rejected it: most account records carry no labelled tax-year slot, so the level
  would open a branch the facts cannot fill — the exact defect `_CONTRACT.md` rule 8 describes, and
  the thing `00` warns about when a level "produces only one child". It is recorded as an
  **optional branch pattern** under `record_type` (a template's own vocabulary per `00`'s
  "optional branch patterns" clause) and nothing more.
- **Privacy rules: identical.** Safety domain, local-only, protected area, P7 before any model
  path. One sharper case is noted in `sensitivity_why` — voided checks, direct-deposit forms and
  unmasked exports are `00`'s "credentials" reading rather than the ordinary statement reading —
  but that is a note, not a different rule.
- **Detection signals: genuinely different, and this is what carries the row.** The schema row's
  `recognition` is the **union** over every finance situation — statements, ledgers, e-receipts,
  archive manifests, tax-year slots — because activation must admit all of them and outputs schema
  ids only. A template's signals must **discriminate this situation from its sixteen siblings on
  the same schema**, a question the schema row structurally cannot answer. That is what
  `recognition` and the nine `collides_with` entries below are, and the whole of what they are.

If R1c disagrees and folds this row into the schema's default template, nothing else breaks: no
field, no canonical key and no residual name depends on this id. That is the honest fallback, and I
would rather flag it here than pad the row.

## Files considered and rejected

- `Chase Statement 2026-03.pdf`, `1099-INT 2025.pdf`, `Offer Letter - Summer Analyst.pdf`,
  `Columbia Tuition Statement Fall 2026.pdf`, `Explanation of Benefits.pdf`, `Expenses 2026.xlsx`,
  `eStatement_protected.pdf` — all already worked in `finance.json`. Re-running them here would
  have produced a longer file and no new information. I built a disjoint set instead, and used
  `Mortgage Statement Mar 2026.pdf` as the collision fixture precisely because it is the case the
  schema row does **not** cover: a file that matches this situation's structure slot for slot and
  still belongs to a sibling.
- A calendar item (`.ics`) — rejected. No statement-shaped account record arrives as a calendar
  event; the plausible one (a payment-due reminder) carries no institution slot, no balance and no
  account descriptor, so it would activate nothing and the example would only restate
  CONNECTION-EXAMPLES fixture 5.
- A contacts file (`.vcf`) — rejected for the same reason plus `00`'s own rule that address-book
  data stays privacy-protected rather than a proposal basis. It is referenced once inside a
  `must_not_conclude` on the retailer email, which is where it actually bites.
- A cheque-book register scan and a passbook photo — real, but they add nothing beyond
  `voided_check.jpg` (credentials in the clear) and the OCR path already exercised twice.
- A `.qfx`/`.ofx` bank export as a full example — kept only as an extension example. Its evidence
  story is identical to the CSV export, and one unlabelled-export example is enough to carry
  `group_without_copying_facts`.

## proposed_fields

**None, deliberately.** Three temptations, all refused:

1. `account_holder` — genuinely required by `00` ("A finance document may mention an account holder
   and an issuing bank"), and already proposed on the **schema** row, which is where it belongs. A
   template proposing the same key again would give R1c two proposals for one field.
2. A period-year / statement-year key, to make the very common "year folder under each account"
   habit expressible. Refused and escalated as this node's `open_question` instead: it changes the
   shared vocabulary, and it changes `tax_year`'s meaning for the `finance.tax-filings` sibling.
   Minting it here to make a familiar folder shape work is the overnight pass's failure mode
   exactly.
3. An employer/counterparty key for the direct-deposit form (the employer is not the issuing
   institution). Refused: the career schema is a field-less placeholder (PR-6), so there is no
   canonical key to `role_split` against. The tension is recorded in that file example's
   `must_not_conclude`, where it is a refusal rather than a new column.

## Neighbours considered that did NOT get an edge

- **`finance` (the schema itself)** — no edge. `uses_schema` is the join, carried by `schema_id`;
  `collides_with` joins same-kind pairs only, so a template cannot collide with a schema.
- **`also_holds_with`: empty, by contract.** CONNECTION.md §5 restricts it to schema↔schema. The
  co-activations this material really produces (medical on an EOB, academic on a tuition bill,
  legal on an executed agreement, identity on a tax form, photos on a photographed record) are
  already authored on `finance.json`. Per file, they appear here as `also_schema` on the examples —
  `legal` on the account-opening packet, `career` on the direct-deposit form, `photos` on the
  screenshot and the voided cheque.
- **`identity.core-documents`** — considered for the voided-cheque / unmasked-routing case and
  rejected as a *collision*: the two are not confusable given the same evidence item. A cheque is
  not a government credential; what it needs is protection, which the safety flag and
  `falls_through_to Protected Records` already deliver. Adding a collision edge would have been an
  edge asserting a confusion that does not exist.
- **`finance.household-property`, `finance.vehicle-records`, `finance.hoa-residents-association`,
  `finance.student-financial-aid`, `finance.crypto-assets`, `finance.small-business-bookkeeping`,
  `travel.bookings-confirmations`, the three insurance situations** — all siblings, none given an
  edge. Their confusions with this situation are either mediated by a sibling I did name (an HOA
  dues notice confuses with `finance.subscriptions-utilities` before it confuses with an account
  statement) or genuinely absent (a wallet export and a chequing statement share no labelled
  structure). Nine collision edges is what the evidence supports; sixteen would have been
  decoration.
- **`photos.scanned-documents`** — rejected in favour of `photos.screenshot-captures`. A scanned
  statement is the same document by another route and is not a competing *situation*; the
  screenshot is, because the capture properties are all that is left when the OCR is thin.
- **`role_split`: empty.** It lives between canonical field keys (CONNECTION.md §§5–6), and both
  splits this material needs (`institution`↔`school`, `institution`↔`target_university`) are
  already recorded on the schema row.

## Reciprocity note

`collides_with` reciprocity is R1c's merge job, per the dispatch prompt. Nine sibling/neighbour rows
now owe this id a reciprocal edge: `finance.receipts-expenses`, `finance.payroll-received`,
`finance.tax-filings`, `finance.investment-brokerage`, `finance.loans-mortgage`,
`finance.subscriptions-utilities`, `career.employment-records`, `legal.leases-agreements`,
`photos.screenshot-captures`.

## Contract-vs-prompt conflicts encountered

One, resolved in CONNECTION.md's favour as instructed and recorded in the node itself: the dispatch
prompt's edge table offers `also_holds_with` and `role_split` to any node, while CONNECTION.md §5
restricts `also_holds_with` to schema↔schema and puts `role_split` in the canonical field list. Both
are empty here for that reason, each with a `_note` key saying so, so the emptiness cannot be read
as an author who forgot.

## NEEDS-JOSEPH (this node only)

- **NJ-fin-pr-1 · Does an account-records branch get a year level, and filled from what?**
  Carried verbatim as this node's `open_question`. The three answers are three different products:
  (a) statements stay flat under `record_type` and the series is a P9 group, which is what this row
  recommends; (b) `tax_year` widens to mean "the year a record covers", which changes the field for
  the `finance.tax-filings` sibling too; (c) a new period-year canonical key. This is a decision
  about someone's real filing habits and about the shared field vocabulary — not a template's to
  make, and not one I resolved.
