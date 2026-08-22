# finance.insurance-personal — lab notes (R1b)

Roster row: `kind: template`, `schema_id: finance`, `launch: placeholder`, `parent_id: null`.
Output: `planning/domains/nodes/finance.insurance-personal.json`. No other file written.

## Sources actually used

- `planning/00-database-agent-product-design.md` — read in full. Every quoted span in the node
  file was `grep -F` verified against it **before** being written; the verification run is in the
  session transcript. 00 **never uses the word "insurance"** (grep: 0 hits), which is why the node's
  `provenance` is `inference` and `design_cite` is `null`. What 00 does supply, and what the node
  leans on, is the Finance field sentence, the safety-domain sentence, the template-definition
  sentence, the parent-dimension rule, the narrow-date rule, the never-alone rules, and the nine
  residual definitions.
- `planning/01-product-design-structured.md` — §7.3 only (the residual-name table, to spell the
  nine `00`'s way). The residual **quotations** in the node come from 00, not from 01's table
  rendering; one draft quote was taken from 01's table wording and was corrected to 00's sentence
  before the file was finalized.
- `planning/domains/_CONTRACT.md`, `planning/prompts/ALIGNMENT.md`,
  `planning/domains/CONNECTION.md`, `planning/domains/CONNECTION-EXAMPLES.md`.
- `planning/domains/roster.json` (id, kind, schema_id, neighbours, and every id used on an edge),
  `planning/domains/canonical_fields.json` (field keys; nothing minted).
- `src/evidence_shape/vocabulary.py` — `SOURCE_TYPES`, checked mechanically against every
  `file_examples[].source_type` and against `file_kinds.source_types`.
- Landed neighbours read for edge alignment, not rewritten: `nodes/finance.json` (the schema row,
  including its `account_holder` proposal), `nodes/finance.personal-records.json` (the nearest
  sibling template, for shape and for the collision seams it already authored).

**CONNECTION.md is binding and present.** Two places where its rules beat the dispatch prompt's
looser wording, noted as instructed:

1. `also_holds_with` is **schema-to-schema only** (CONNECTION §5). This is a template row, so
   `also_holds_with` is `[]` — empty by contract, not by omission. The co-activations this
   situation produces (medical on an injury claim, legal on a signed release, identity on a licence
   scan in a policy archive, photos on loss photographs) are already authored on the `finance`
   schema row, and are recorded per file in `file_examples[].also_schema`.
2. `parent_id` is browse-only and R1b never authors it (PR-5). Left `null`.

## The node test — why this is a node and not padding

CONNECTION §2's test is disjunctive: a template row exists if its **detection signals**,
**recommended dimensions**, or **privacy rules** differ from its schema's default template. This row
clears all three, which is unusual among the finance siblings and is the reason it did not get
refused:

- **Dimensions differ.** The finance schema's default is `institution → account_type → record_type`.
  This row recommends `institution → record_type`, with `account_type` demoted to an optional branch
  pattern. The demotion is argued from 00's own one-child and flattening warnings, not from taste:
  most households hold one coverage line per carrier, so a coverage-line level under each carrier
  usually opens a branch with a single child.
- **Signals differ.** The schema row's `recognition` is the *union* across every finance situation,
  because activation outputs schema ids only. This row's signals **discriminate**: the
  declarations pair (policy period + coverage/limit/deductible), the claim triple (claim number +
  date of loss + estimate total), the ID-card shape, and the personal-versus-commercial rule on the
  labelled named-insured slot. None of them fires on a bank statement, a ledger or a tax form.
- **Privacy rules differ.** A personal declarations page concentrates a home address, a vehicle
  identification number and often a licence number on one page; an injury claim carries treatment
  detail; loss photographs carry GPS. That is a sharper posture than the finance schema's general
  "account record" reading, and it is written into `sensitivity_why` rather than asserted as a
  handling class (P7's, never set here).

Had only one of these differed I would still have kept the row; had none differed I would have
refused, as the prompt requires.

## Fixture-8 compatibility

`CONNECTION-EXAMPLES.md` §8 is binding on this node by name. It puts three insurance situations on
one Finance schema (never three schema slugs) and gives `tpl.insurance-personal` a dimension order
of `institution → record_type`. This node matches: one `schema_id`, no minted fields, that exact
dimension order. The `account_type` optional level is added *as* an optional branch pattern —
00's template definition lists "optional branch patterns" as a thing a template owes — not as a
change to the default order.

## Files considered and rejected

Named files I worked through and did **not** put in `file_examples`, with the reason:

- **`renewal.ics`** (a policy-renewal calendar event). Rejected. Fixture 5 already settles it:
  `calendar` is a `SOURCE_TYPE`, and an `.ics` activates only on content. An event titled
  "Renew auto policy" would be a filename-grade clue at best, and including it risked reading as
  format-as-domain. `calendar` is therefore absent from `file_kinds.source_types`.
- **`agent.vcf`** (an insurance agent's contact card). Rejected on 00's own rule that VCF data
  should be privacy-protected rather than used to create folder proposals. Nothing here would have
  been a fact.
- **`Coverage comparison.xlsx`** (a shopping spreadsheet comparing quotes). Rejected, and
  `spreadsheet` was dropped from `file_kinds` with it. It is a quote-shopping artifact with no
  policy number and no period; it is 00's "a spreadsheet with unclear purpose" and belongs to
  residual review, not to this situation. Keeping it would have padded the source-type list.
- **`Benefits Enrollment Guide.pdf`** (an employer's open-enrolment brochure). Rejected as belonging
  to the career/employment seam and, where it is health coverage, to the healthcare sibling. It is
  covered instead as a never-alone case ("a carrier name alone").
- **`Life Insurance Policy.pdf`** as a separate example. Rejected as a duplicate of the declarations
  fixture — it would have exercised the same slots and taught nothing new. Life shows up instead as
  a `work_types` value (beneficiary designation, cash-value statement) and inside the `account_type`
  argument.
- **A bank statement with an insurance premium debit row.** Rejected: the premium is a transaction
  row inside another situation's record. The rule that stops it is already on the sibling
  (`institution` is not a payee read out of a table), and repeating it here would have implied this
  node can claim other situations' files.

Twelve examples were kept, covering the ugly cases the prompt asks for: labelled form vs unlabelled
prose (declarations vs premium-increase letter), an OCR screenshot of the same thing as a document
(ID card), an archive packet with mixed members including one that belongs to another safety domain,
email, an encrypted file, a look-alike that belongs to a neighbour (the commercial certificate, and
the EOB), and a file that is legitimately two domains at once (the settlement release).

## proposed_fields — empty, deliberately

`proposed_fields: []`. Four keys were tempting and each was refused:

- **`policy_number`** — an identifier. It is the group anchor for a policy series, which is a
  `grouping_reasons` entry, not a folder level and not a fact this schema needs. The finance schema
  declares no account-identifier key either, and minting one at template level would put a private
  key on the shared vocabulary. Refused.
- **`claim_number`** — same argument. Recorded instead as a `must_not_conclude` on the adjuster
  estimate, so the refusal is visible in the fixture rather than only in prose.
- **`coverage_line`** — `account_type` already means "the kind of account a financial record belongs
  to". An insurance line *is* the account kind. Minting `coverage_line` would be the
  `course_name`-beside-`subject` failure in finance clothing. Refused.
- **`policy_period`** — the honest gap, and the one I most wanted. There is no canonical field for
  the period a record covers; `tax_year` means the tax year and 00's narrow-date rule forbids
  deriving it from an effective-date range. Minting a period field here would decide a shared-
  vocabulary question from one template row, and the sibling `finance.personal-records` already
  carries the general version of that question in its own `open_question`. Refused and cross-
  referenced there instead.

`account_holder` is referenced in `facts_legal` on several examples. It is **the finance schema
row's** existing proposal, not a new one from this node; re-proposing it would have double-counted.

## Neighbours considered that did NOT get an edge

- **`identity` / `identity.core-documents`.** A licence scan travels inside `insurance.zip` and a
  declarations page can carry a licence number. No `collides_with`: the two are not confusable given
  the same evidence item — a government credential identifying a person and a carrier's coverage
  document are structurally distinct — and the archive case is a *membership* question, handled by
  `also_schema: "identity"` on that file example. `also_holds_with` is unavailable to a template row
  and is already authored finance↔identity on the schema.
- **`finance.tax-filings`.** Considered because premiums can be deductible. No edge: for a household
  that is the corporate/business situation's concern, and nothing in this row's structure resembles a
  labelled tax-year slot with numbered form boxes. Adding the edge would have implied a tax_year
  dimension this row explicitly excludes.
- **`travel.bookings-confirmations`.** Travel insurance was considered as a seam. No edge: a travel
  policy is a policy and lands here on the same signals; a booking confirmation carries an itinerary
  and no coverage-and-period pair. The confusion is not evidence-item-level, which is what
  `collides_with` means after CONNECTION narrowed it.
- **`career.employment-records`.** Employer-provided life or disability coverage sits on this seam.
  No edge from this row: where it is health coverage it is the healthcare sibling's, and the
  employer-name-plus-money item is already governed by the collision the `finance` schema row
  authored against `career`. Adding a template-level duplicate would have been noise.
- **`photos.scanned-documents`.** A phone scan of a paper policy. No edge: that is the same
  document reached through a different capture path, and the discriminating rule is identical to the
  screenshot one already authored against `photos.screenshot-captures`.
- **`legal.leases-agreements`.** A renters certificate is produced *for* a lease. No edge: the
  certificate is issued by a carrier and carries a coverage pair; the lease is a different file. The
  seam is already authored on `finance.personal-records` against the same neighbour, and the
  liability-claim seam that *is* item-level went to `legal.personal-legal-matters` instead.

Ten `collides_with` edges were kept. Every id was checked against `roster.json`
mechanically; none is invented. Reciprocity is R1c's, per the prompt.

## Shape choices a merger should know

- `falls_through_to` uses the **object form** (`residual_template` / `why` / `provenance`), matching
  the nearest landed sibling `finance.personal-records.json`. The `finance.json` schema row uses
  plain strings. R1c will need to normalize one of the two; I followed the closer neighbour so the
  finance template rows are internally consistent.
- No extra top-level keys were added. `finance.personal-records.json` carries four explanatory keys
  (`node_test_note`, `work_types_note`, `also_holds_with_note`, `role_split_note`) that
  `_CONTRACT.md` rule 14 would report as unrecognized on a kind-bearing entry. Rather than repeat
  that risk, the equivalent reasoning lives in this file.
- `role_split: []`. The one role tension this situation surfaces — the **certificate holder** on a
  certificate of insurance, which is the party a document is addressed to rather than its issuer —
  has no canonical counterpart key to split `institution` against. It is recorded as a
  `must_not_conclude` on that file example instead of being minted.
- No numeric thresholds anywhere. Digits appear only inside example filenames and inside quoted 00
  prose.

## NEEDS-JOSEPH (this node only)

**NJ-fin-ins-1 · Carrier-first or coverage-line-first for a household's insurance?**
This row recommends `institution → record_type` with `account_type` optional, following 00's
parent-dimension rule and fixture 8. The competing design is genuinely better for a common case: the
coverage line (auto, home, renters, life) is durable while the carrier changes every time someone
shops around, so `Auto/` above `Carrier/` retrieves better for a household that has switched
insurers twice. Nothing in a file can say which situation a given household is in. Deciding this
sets a real filing shape for someone's records, so it is recorded rather than resolved — and it is
the reason `account_type` was made an optional branch pattern instead of being either promoted to
the default order or dropped.

Two smaller items ride on the same answer and are recorded in the node's `open_question` rather
than acted on: the certificate-holder role has no canonical field, and there is no canonical field
for the period a policy covers (see the `policy_period` refusal above; the general form of that
question is already open on `finance.personal-records`).
