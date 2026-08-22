# finance.tax-filings — lab notes

Roster row: `kind: template`, `schema_id: finance`, `launch: safety`, `parent_id: null` (never authored — PR-5: R1b does not write browse parents).
Output: [`finance.tax-filings.json`](finance.tax-filings.json). Result: **node kept** (`refuse_node: false`).

---

## Sources actually used

- `planning/00-database-agent-product-design.md` — read in full. Every quoted span in the node file
  was grep-verified against it before it was written, then re-verified mechanically after writing
  (47 quoted spans, 0 failures). No numeric threshold appears anywhere in the node.
- `planning/domains/_CONTRACT.md` — entry shape; rules 5 (sensitivity is `00`'s phrase only),
  9 (D4: jurisdiction is a value, never a field name), 12 (`uses_schema`/`schema_id`, a template
  never copies the field list), 14 (closed edge vocabulary).
- `planning/domains/CONNECTION.md` + `CONNECTION-EXAMPLES.md` — binding. Fixture 8 (insurance:
  one field vocabulary, three templates) is the shape this row follows; fixture 4 (passport →
  Protected Records) is the safety fallthrough shape; fixture 6 (`HW 3.pdf`) is the grouping
  firewall this template's hardest file example turns on.
- `planning/prompts/ALIGNMENT.md` — work types are values; a template exists only when the
  organizational situation differs.
- `planning/domains/roster.json` — confirmed id, kind, schema, neighbours; every edge target below
  was checked against the roster's 83 `domain_id`s mechanically.
- `planning/domains/canonical_fields.json` — the four Finance keys plus `account_holder` as
  referenced by `finance.json`. No new key minted.
- `planning/domains/nodes/finance.json` — the schema node. It already records that
  `tax_year` is destination-eligible but deliberately excluded from the schema's default order,
  and names *this* row as where year-first belongs. This node is the discharge of that sentence.
- `src/evidence_shape/vocabulary.py` `SOURCE_TYPES` — every `source_type` used is a member.
- `planning/01-product-design-structured.md` — used only as a locator for the finance/safety
  passages; nothing was asserted from it that `00` does not say.

## The node test — why this is a node and not padding

Against `finance.personal-records`, the schema's default template, all three of the node test's
criteria differ (CONNECTION §2 requires only one):

| | `finance.personal-records` | `finance.tax-filings` |
|---|---|---|
| recommended order | `institution` → `account_type` → `record_type` | `tax_year` → `record_type` |
| primary detection signal | a labelled statement-period slot beside a labelled balance | a labelled **tax-year** slot beside a return/year-end-form structure |
| privacy posture | protected area, per-record | protected **packet** — a filing concentrates identification, income totals and dependants' names into one accepted group |

The two also collide hard on one evidence item (institution + amount + year-shaped token), which
is why `collides_with finance.personal-records` carries the longest `signal` in the file. If a
future merge decides these are one node, the thing that has to go is the year-first order, not the
detection signals — and that is what the `open_question` is about.

## Files considered and rejected

- **`Chase Statement 2026-03.pdf`** — kept only as a *named counter-fixture* inside `never_alone`,
  not as a file example. A monthly statement inside a calendar year is `finance.personal-records`
  material; putting it in this node's examples would have been the padding move.
- **`1099-INT 2025.pdf`, `Tax2025.zip`, `ADP Pay Statement Mar 2026.pdf`** — already fixtures on
  `finance.json`. Rather than restate them I wrote near-neighbours that carry *new* failure modes:
  `W-2 2025 - Acme Corp.pdf` (the career one-evidence-item collision), `tax-2024-filing.zip` (a
  manifest with members belonging to *three other* templates), `Pay Statement Mar 2026.pdf`
  (rewritten so the tempting signal is the **year-to-date withholding column**, which the schema
  node does not mention).
- **A blank downloadable form** (`form-1040-blank.pdf`) — considered and dropped as an example
  because it is genuinely uninteresting: no year, no identification, no packet. It survives as the
  justification for the `Independent Records` fallthrough.
- **A tax-software licence receipt** — that is `finance.receipts-expenses`/`subscriptions`
  material, and including it would have been the "looks like mine because the word tax appears"
  error this template most needs to avoid.
- **A crypto exchange's year-end gains report** — real, but it belongs to
  `finance.crypto-assets` first and reaches this template through packet membership; adding it
  here would have duplicated that node's work.
- **A `.ics` filing-deadline reminder** — deliberately excluded. A calendar entry is a
  `SOURCE_TYPE`, and a deadline reminder is not a tax record; including it would have re-run
  slice 14's calendar-as-domain bug from the other direction.

## proposed_fields — none, and why that is the right answer

`proposed_fields: []`. The four inherited keys carry this situation completely:

- `tax_year` — the scope. It is the whole reason this template differs from its schema's default.
- `record_type` — every work type in the list is a **value** of it, jurisdiction-specific form
  names included (D4). This is where the temptation to mint was strongest and it was refused: a
  `w2_tax_year`, a `form_type`, or a `jurisdiction` field would each be the one-way move
  `_CONTRACT` rule 9 names. Nothing about a foreign filing needs a field the domestic one lacks —
  what it needs is R5's catalogue for another jurisdiction, which is a *values* problem.
- `institution` — the payer or issuing authority, in the issuer role.
- `account_type` — declared by the schema, referenced here, and marked **metadata_only** for this
  situation rather than dropped: a filing is not per-account, so a level for it would be empty for
  most members. That is P10's per-dimension mechanism (CONNECTION §6), not a narrowing of the
  schema.

`account_holder` is referenced in three `facts_legal` lists. It is **`finance.json`'s recorded
proposal, not a new one from this row** — I did not re-mint it and did not re-open its question,
because a person-name field on a safety domain is a shared-vocabulary decision. Its unresolved
joint-filer behaviour (a return with two named filers) is the reason it appears in the node's
`open_question` only by reference.

## Neighbours considered that did NOT get an edge

- **`identity.core-documents`** — the strongest *conceptual* neighbour: a return and a payer form
  both carry taxpayer identification in labelled slots. It got **no** `collides_with` because the
  pair is not a mutex — it is genuinely the `also_holds_with` case, and that edge is schema-only
  (CONNECTION §5). The finance↔identity join is already authored on `finance.json`; this row
  points at it in `also_holds_with_note` and marks the affected examples `also_schema: "identity"`.
- **`medical.personal-health-records`** — medical-expense receipts retained as deductions are real,
  but the discriminator is the same one `finance.receipts-expenses` already carries, and the
  finance↔medical schema join exists. A third edge here would be noise.
- **`finance.loans-mortgage`**, **`finance.student-financial-aid`**, **`academic.coursework`** —
  each contributes a *member* to a filing packet (a mortgage-interest statement, an aid record, a
  tuition statement) but none is confusable with a filing *document*. They are represented instead
  where they belong: inside the `tax-2024-filing.zip` example's `must_not_conclude` (membership
  erases neither side's facts) and, for the tuition case, in `role_split institution ↔ school`.
- **`travel.bookings-confirmations`** — a business-travel receipt reaches a filing through
  `finance.receipts-expenses`; a direct edge would be a second path for one confusion.
- **`photos.screenshot-captures`** — the e-filing screenshot is covered by `photos` as
  `also_schema` on the example and by the existing `finance`↔`photos` schema join. The screenshot
  template already collides with `finance.receipts-expenses`; a second finance template collision
  would duplicate it.
- **`legal.leases-agreements`** — an executed agreement is `legal.personal-legal-matters`' seam
  with this row only when it is a *dispute*; a lease is not tax material at all.

The roster's `must_consider_neighbors` are the **schema** ids `career` and `legal`. Because
`collides_with` joins same-kind pairs only, both are honoured at template level:
`career.employment-records` and `legal.personal-legal-matters`. `finance.payroll-received` was
added as the third career-facing edge because it is where the pay-statement confusion actually
lives.

## Where I followed CONNECTION over the dispatch prompt

Two places, both noted in the node file itself:

1. **`also_holds_with` is empty.** The prompt's output shape offers the key and its edge table
   describes the abstract/application case, but CONNECTION §5 scopes the edge to schema↔schema.
   Fixture 8 confirms it: the finance↔medical edge is drawn between *schemas* even though the
   fixture is about a template. The joins are recorded on `finance.json`; this row references them
   in `also_holds_with_note` rather than asserting them a second time.
2. **`parent_id` stays `null`.** PR-5: R1b never authors it.

## The one place I extended `00` and said so

Year-first. `00` writes the opposite default for this kind of material — *"For document and record
domains, project, function, or subject usually comes before time because putting year first
scatters related work across calendar folders"* — and licenses exactly one exception by name,
photos. The node's `template.why` states the argument for extending it (a tax year is the record's
own scope, not a calendar bucket over it, so a filing cannot be scattered by its own year), marks
the reasoning as mine, and the row carries `provenance: inference` for that reason. It is not
hidden inside a `design_cite`.

## NEEDS-JOSEPH — this node only

**NJ-tax-1 · Does an accepted filing packet fill `tax_year` on a supporting document that has no
tax-year slot of its own?** The grouping firewall says no (*"The graph does not automatically copy
those missing facts onto sparse files"*). This template turns that into a concrete product
consequence rather than a principle: under a `tax_year`-first order, a donation receipt, a
medical-expense receipt or a childcare invoice has **no legal branch**, so most of a real filing's
supporting material lands in a scoped `General` branch or in review instead of under its year.
Three possible answers, none of which R1b may pick: (a) a *user-confirmed* packet membership is
itself the licence for a `user_confirmed` `tax_year` fact — which is the one reliability state
that does not violate the firewall; (b) the recommended order keeps an explicit scoped fallback
level under each year; (c) year-first is wrong for this situation and the row collapses toward
`finance.personal-records`. Carried in the node's `open_question`.

**NJ-tax-2 · Are two `tax_year` values from different jurisdictions comparable?** Where a tax year
is not the calendar year, one filer's `2024` and another's `2024-25` are different spans written
in one field. `00` keeps the raw observation and lets a resolver normalise, but nobody has decided
what the normalised form of this field is. Small, but it is a *values-table* decision that a
year-first template makes visible immediately — and it must not be answered by minting a
jurisdiction field (D4).
