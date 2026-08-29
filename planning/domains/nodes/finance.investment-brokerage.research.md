# finance.investment-brokerage — lab notes (R1b)

Date: 2026-08-22
Roster row: `kind: template`, `schema_id: finance`, `launch: placeholder`, `parent_id: null`.
Output: [`finance.investment-brokerage.json`](finance.investment-brokerage.json).

## Sources actually used

- `planning/00-database-agent-product-design.md` — read in full. Every quoted span in the node
  file was `grep -F`-verified against this file **before** it was written; the two verification
  runs covered 47 spans and all returned OK. No span is paraphrased inside quote marks.
- `planning/domains/_CONTRACT.md` — entry shape, rules 1–15 (R0 delta).
- `planning/domains/CONNECTION.md` — node test (§2), no schema inheritance (§3), activation shape
  (§4), closed edge vocabulary (§5), field identity (§6), four owners (§7), PR-2 / PR-5 / PR-6 /
  PR-8.
- `planning/prompts/ALIGNMENT.md` — templates are organizational situations; work types are values.
- `planning/domains/roster.json` — confirmed my id, kind, `schema_id: finance`, neighbours
  (`legal`), residual (`Protected Records`), and the full sibling list. Every `collides_with`
  target below was checked against this file's ids.
- `planning/domains/canonical_fields.json` — the four Finance keys plus `school` (used only on the
  academic co-activation fixture). No key was minted; `proposed_fields` is empty.
- `src/evidence_shape/vocabulary.py` — `SOURCE_TYPES` checked mechanically against every
  `file_examples[].source_type` and against `file_kinds.source_types`.
- Landed neighbour nodes read so edges align rather than conflict: `nodes/finance.json` (the
  schema row) and `nodes/finance.personal-records.json` (the one landed sibling template). The
  sibling had already authored a `collides_with` edge **at** this id; the node file reciprocates
  it with the same discriminating evidence stated from this side.
- `planning/01-product-design-structured.md` — **not** read. Everything the prompt cites it for
  is stated in `00`, which the alignment contract makes the authority; opening the 1,912-line
  rendering would have added no fact and risked quoting a section number as if `00` contained one.

## Did this row survive the node test?

Yes, and narrowly — the reasoning is recorded in `node_test_note` in the JSON rather than
assumed. CONNECTION §2's template test is disjunctive: **detection signals, recommended
dimensions, or privacy rules** must differ from the schema's default template.

- **Privacy rules: identical.** Safety domain, local-only, protect before any model path (PR-2).
  No difference, and inventing one would have been the padding failure.
- **Recommended dimensions: the same order** — `institution → account_type → record_type`. I
  considered inverting to `account_type → institution` and rejected it (below).
- **Detection signals: genuinely different, and that is the whole licence.** The Finance schema
  row's `recognition` is the *union* across every finance situation, because activation outputs
  schema ids and must admit statements, ledgers, e-receipts, archive manifests and tax-year slots
  alike. A template's signals must **discriminate** this situation from seventeen siblings on the
  same schema — a question the schema row structurally cannot express. The discriminators here are
  three structures no sibling produces: a labelled **holdings/positions table** (security
  identifier + quantity + market value), a **trade-date/settlement-date pair** with a buy/sell
  action label, and a **cost-basis** structure (acquisition/disposition dates beside proceeds and
  cost basis). Everything in `recognition` and `collides_with` is that discrimination and nothing
  else.

Two things the row adds that the schema row does not carry, both `00`-licensed optional branch
patterns rather than new dimensions: a `tax_year` **leaf under** `record_type` for the year-scoped
subset that carries its own labelled tax-year slot, and an `account_type`-above-`institution`
inversion for a continuing retirement account whose custodian changed.

## The dimension order I rejected, and why

The tempting move was `account_type → institution → record_type`: a "Roth IRA" is intelligible
without naming the custodian, which weakens `00`'s parent-dimension argument that carried
`institution` to the front on the sibling row. I rejected it as the default for two reasons.
First, `00`'s rule is about the **child** being unintelligible without the parent, and
`record_type = statement` still is: it is a statement *from someone*. Second, and decisively,
inverting would have been a change made so the row looked different from its sibling rather than
because the material asked for it — which is the padding failure this pass exists to avoid. It is
recorded as an **optional branch pattern** with the one condition that actually motivates it (a
custodian transfer), which is what `00` means by a branch offering "the dimensions that are
actually present in its member groups".

`account_type` does carry more weight in this situation than anywhere else on the Finance schema —
one custodian holding a taxable account, a traditional retirement account, a Roth retirement
account and an employer plan for one person are four different tax containers — so it stays a
level here even where the sibling row suggests flattening it away for a single-account household.

## Files considered and rejected

- **`Portfolio.numbers` / a net-worth tracker spreadsheet.** Rejected: like the schema row's
  `Expenses 2026.xlsx`, it *references* many institutions and belongs to none. It is a ledger the
  holder maintains, not a record a custodian issued — the `finance.small-business-bookkeeping` /
  personal-ledger shape, and here it would have taught the wrong thing about `institution`.
- **A fund prospectus or an annual report PDF.** Rejected: it names a fund company, carries
  holdings tables, and is **reading material about a security**, not a record of an account. It is
  `Reading Inbox` residual material, and including it would have blurred the one discriminator
  (a custodian account) the whole row rests on. Its danger is recorded instead as the
  never-alone rule about a custodian/fund-family name alone.
- **A dividend-reinvestment mailing that is pure marketing.** Rejected as indistinguishable from
  the prospectus case at evidence level.
- **A bank statement showing a securities-transfer debit.** Rejected: it is the
  `finance.personal-records` sibling's file, already fixtured there.
- **A `.ofx`/`.qfx` download with no readable header.** Kept only as an extension in `file_kinds`,
  not as an example — it would have restated `positions_export.csv`'s lesson (no issuer ⇒ no
  `institution`) without adding one.
- **A brokerage statement photographed with a phone.** Rejected as an example because it would
  have duplicated the schema row's `IMG_9931.jpg` capture/finance also-holds lesson verbatim;
  `image` stays in `file_kinds` as plausible, and the OCR path is covered by the app screenshot
  and by `confirm_0212.pdf`.

Thirteen examples were kept. The prompt's "ugly cases" checklist is covered: labelled form
(statement, confirmation), unlabelled prose (the adviser-letter case, in `needs_llm`), OCR of the
same thing (app screenshot, cropped scan), archive packet with mixed members
(`retirement_plan_enrollment.zip`), mail (`Contribution received for tax year 2025.eml`), a
**collision fixture that looks like ours and is not** (`Stock Option Grant Agreement.pdf`, and a
second one, `exchange_transactions_2025.csv`), and a file that is legitimately **also** another
schema (`Composite Tax Statement 2025.pdf` with identity;
`529 Plan Statement Fall 2026.pdf` with academic; `retirement_plan_enrollment.zip` with legal).

## The sparse-file case

`confirm_0212.pdf` is this domain's `HW 3.pdf`. A cropped scan whose OCR yields a symbol, a
quantity and the word "Confirmation", with the letterhead band cut off. Its strongest mutual
retrieval neighbours are the accepted statement series and the readable confirmation from the same
date. It carries `group_without_copying_facts: true` and **no** `institution` fact: `00` —
"The graph does not automatically copy those missing facts onto sparse files." Activation ≠
grouping is stated on the app screenshot too, which may join the account neighbourhood without
inheriting the statement's facts.

## proposed_fields

**None.** The one gap this material genuinely has — a continuing account's identity across a
custodian transfer — is written up as `open_question`, not minted. `institution` is defined as the
issuer role; a transfer ends one issuer's series and begins another's, so a decade-old retirement
account splits into two branches under the recommended order and the P9 group that spans the
transfer has no dimension to sit on. The three candidate answers are three different products and
one of them (minting an account-identity key) is a change to the shared field table, which
CONNECTION §6 puts outside a template row's authority. Minting a key so a familiar folder shape
becomes expressible is exactly the move that produced 2,295 private field names in the overnight
pass.

`account_holder` is referenced (in `facts_legal` on four fixtures) but **not** re-proposed: the
Finance schema row already proposes it and already carries the open question about whether it
becomes canonical. Re-proposing it from a template row would have created a second, drifting copy
of one question.

## Neighbours considered that got no edge, and why

- **`legal.leases-agreements`** — the seam the sibling row uses for an account agreement. Here the
  legal-side document is a *designation* or a *trust registration*, not a lease or a bilateral
  agreement, so the edge went to `legal.estate-planning` instead. `legal` was my one
  `must_consider_neighbors` entry and it is discharged there.
- **`legal.personal-legal-matters`** — a court order dividing a retirement account is genuinely
  both, but its discriminating evidence is a case caption and a court, which is a *schema*-level
  co-activation already authored as `finance ↔ legal` `also_holds_with` on the schema row. Adding
  a template collision would have restated it in the wrong place.
- **`career.employment-records`** — the employer-plan seam. Folded into
  `finance.payroll-received`, which is where the actual confusable *document* (a pay statement's
  deferral line) lives. Two edges for one seam would have been decoration.
- **`finance.insurance-personal`** — annuity and variable-life contracts hold sub-accounts and look
  like this material. Left off deliberately: PR-8 puts insurance on the Finance vocabulary as
  separate situations, and I could not name a **discriminating evidence item** honestly without
  inventing contract-document structure I have no design basis for. Recorded here rather than
  guessed into the file.
- **`finance.household-property`, `finance.vehicle-records`, `travel.bookings-confirmations`** —
  no shared evidence item; no edge.
- **`photos.camera-events`** — the photographed-document path exists, but the confusable capture is
  the *screenshot*, so the edge went to `photos.screenshot-captures` only.
- **Residual `Receipts and Confirmations`** — considered and **rejected** as a fallthrough, even
  though a trade confirmation is literally a confirmation and `00`'s definition names
  "isolated invoices, delivery confirmations, booking records, boarding passes, purchase receipts,
  event tickets, and similar transactional documents". Every document in this situation names an
  account and a holder, and `00` puts "account statements" inside `Protected Records`. Routing
  them to a transactional residual would move protected material out of the protected area to
  satisfy a word match. `Protected Records` is the roster's `must_consider_residuals` entry and it
  is where they go.

## Contract-vs-prompt conflicts, resolved as instructed

- The dispatch prompt's output sketch shows `falls_through_to` as bare residual **names** and
  gives no object shape for `collides_with` / `role_split`. `_CONTRACT.md` rule 6 and rule 14 use
  `{"residual_template": …}` / `{"domain": …, "signal": …}`, `check.py` accepts both shapes for
  `falls_through_to`, and the landed sibling uses the objects. **CONNECTION/_CONTRACT wins**
  (prompt's own precedence line); the file uses the object form with a `why` and a `provenance`
  on each.
- The prompt says "D6 is unset". The orchestrator's binding context records D6 and D2 as
  **ratified**: snake_case keys, the academic key is `subject`. Followed as ratified. Nothing in
  this row turns on it — all four Finance keys are already snake_case.
- The prompt's `role_split` slot vs CONNECTION §5/§6, which puts `role_split` between **canonical
  field keys**, not between nodes. Left empty with a note, matching the sibling: the two splits
  this material needs are already on the schema row, and the one this situation adds (a security
  **issuer** inside a holdings row vs the **custodian** that issued the record) has no canonical
  counterpart key to split against, so it is recorded in `must_not_conclude` instead of minted.
- `also_holds_with` is empty because CONNECTION §5 restricts it to schema↔schema pairs. The
  co-activations are recorded per file in `also_schema`.

## NEEDS-JOSEPH (this node only)

**NJ-brokerage-1 · Does a continuing account keep one identity across a custodian transfer, and
what fills the branch if it does?** Full statement in the node's `open_question`. Summary: under
the recommended `institution`-first order, one retirement account held across a transfer becomes
two branches, and the accepted group spanning the transfer has no dimension to sit on. (a) leave
it as a P9 group and no folder level — what the row recommends today; (b) make the
`account_type`-first inversion the default for retirement accounts, which loads `account_type`
with an identity it was not defined to carry and would merge two same-type accounts at two
custodians; (c) mint an account-identity key on the shared field table, which is a decision about
the product's vocabulary and needs its own rule for a masked account tail that changes at
transfer. Not resolved here; no field proposed.

Related but **already open elsewhere and deliberately not re-raised**: whether `account_holder`
becomes canonical (finance schema row), and whether a record-period year level is allowed at all
(`finance.personal-records` row). This node's question is distinct from both — it is about the
*account's* continuity, not about a person or a year.
