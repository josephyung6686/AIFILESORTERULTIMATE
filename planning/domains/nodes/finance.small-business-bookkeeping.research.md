# finance.small-business-bookkeeping — lab notes (R1b)

Roster row: `kind: template`, `schema_id: finance`, `launch: placeholder`,
`provenance: inference`, `file_kind_owner: [spreadsheet]`.

Verdict: **node accepted** (`refuse_node: false`). It is useful as a placeholder for later P10
template fitting and, today, as a precise discriminator over Finance-safety evidence. It does not
turn safety activation into permission to build or use a deep folder tree.

## Sources used

### Binding local sources

- `planning/00-database-agent-product-design.md` — read in full. It is the authority for the
  observation/fact split, the four Finance fields, schema activation, grouping firewall, template
  order, residual library, and privacy posture. Every span attributed to `00` in the finished JSON
  is mechanically checked with fixed-string `rg` before this row is reported.
- `planning/01-product-design-structured.md` — read only as the numbered locator the dispatch
  permits: extraction (§2.1–2.9), facts and domain schemas (§3.1–3.15), grouping (§4.1–4.10), tree
  templates (§5.1–5.12), residuals (§7.1–7.4), and privacy (§8.4). Nothing unique to `01` was used;
  `00` wins.
- `planning/domains/_CONTRACT.md`, `planning/prompts/ALIGNMENT.md`,
  `planning/domains/CONNECTION.md`, and `planning/domains/CONNECTION-EXAMPLES.md` — read in full.
  These supplied the template node test, closed edges, schema-only `also_holds_with`, browse-only
  `parent_id`, field identity, safety split, and worked activation/grouping joins.
- `planning/overnight/council/DECISION-BRIEF.md` — the ratification index plus D2 and D6 were read;
  J-IND was carried as binding. The row uses snake_case, leaves P7 handling classes unwritten, and
  preserves its rostered placeholder launch.
- `planning/domains/roster.json` — confirmed this exact id, kind, schema, launch, neighbours,
  residual, inherited keys, and spreadsheet ownership. `planning/domains/canonical_fields.json`
  confirmed all referenced keys and exposed the important client/our_firm seam. The exact
  `SOURCE_TYPES` came from `src/evidence_shape/vocabulary.py`.
- Landed nodes consulted for alignment, never edited: `finance.json`,
  `finance.personal-records.json`, `finance.receipts-expenses.json`,
  `finance.tax-filings.json`, `career.consulting-client-engagement.json`, and `legal.json`.
  Three reciprocal collision signals were already waiting for this row: receipts/expenses,
  tax filings, and consulting/client engagement.

No deferred catalogue was consumed. The node names bookkeeping context terms and structural rule
families; it writes no detector regex, organization gazetteer contents, jurisdiction values, or
score.

### External artifact reality checks

These sources were used only to confirm that the concrete files and internal structures are real.
They do not override the product design, and no external wording is quoted or attributed to `00`.

- [IRS — What kind of records should I keep](https://www.irs.gov/businesses/small-businesses-self-employed/what-kind-of-records-should-i-keep)
  confirms that small operations keep business books such as journals and ledgers alongside
  invoices, paid bills, receipts, deposit evidence, and other supporting documents. Its legal and
  retention guidance is jurisdiction-specific and was deliberately not encoded.
- [U.S. Small Business Administration — Manage your business](https://www.sba.gov/counseling/manage-your-business/)
  confirms balance sheets, revenue/expense accounting, accounts receivable, and accounts payable
  as ordinary small-business finance structures. Again, this was an artifact check, not a rules
  source.
- [Xero — Recording accounting transactions](https://www.xero.com/us/guides/record-accounting-transactions/)
  and [Xero — Bank reconciliation](https://www.xero.com/us/guides/how-to-do-bank-reconciliation/)
  corroborate the debit/credit ledger shape, trial balance, statements, invoice/receipt inputs,
  and the book-balance-versus-bank-statement comparison used in the fixtures.
- [Intuit — Accounts receivable aging report](https://quickbooks.intuit.com/learn-support/en-us/help-article/accounts-receivable-reports/run-accounts-receivable-aging-report/L4N7PC2hg_US_en_US)
  confirms the real report family behind the aging fixture. [Intuit — QuickBooks file types](https://quickbooks.intuit.com/learn-support/en-us/help-article/banking/file-types-extensions-used-quickbooks-desktop/L3vuO2X4c_US_en_US)
  confirms `.qbb` as a backup and `.qbw` as a company file. Their extensions remain routing clues
  only and never prove the node.

## Node test — why this is not the Finance default

The Finance schema default is institution-first account records: institution, then account type,
then record type. Its anchors are institution-issued statements, labelled periods and balances,
and account descriptors. This row differs on every clause of the disjunctive test:

1. **Detection differs.** The rich anchor is a holder-maintained working system: populated
   journal/ledger columns, a trial-balance pair, a book-versus-bank reconciliation, an invoice
   series, or a receivables/payables report. An institution-issued statement can join the
   reconciliation packet but does not become the working book.
2. **Recommended dimensions differ.** `record_type → account_type`; function first, with account
   optional and flattenable. `institution` is omitted because the same ledger refers to many
   banks, vendors, and customers. `tax_year` is omitted because the ordinary scope is a reporting
   month, quarter, or fiscal range, not necessarily a labelled tax year.
3. **Privacy differs in concentration.** One general ledger or company backup aggregates many
   counterparties and accounts. An unreadable proprietary backup stays local and represented; it
   is not sent to a model to discover what it is.

The row therefore passes without inventing a field or mistaking an industry name for a node.

## Bottom-up file set

The JSON carries fifteen complete fixtures. Each names a legal `SOURCE_TYPE`, raw observations,
legal facts, forbidden conclusions, multi-schema status, grouping firewall, and residual home.
The set was chosen before writing recognition rules:

- `General Ledger - Blue Finch Studio - 2026 Q2.xlsx` — a populated chart/journal/ledger bundle;
  legal `record_type`, but no institution from row frequency and no tax year from the period.
- `Management Accounts - Blue Finch Studio - June 2026.xlsx` — trial balance plus profit/loss,
  balance-sheet and cash-flow sheets; the as-of date is not `tax_year`.
- `INV-1048 - Blue Finch Studio to Acme.pdf` — labelled issued invoice; the client stays an
  observation under today’s Finance allow-list and the engagement group never copies it.
- `Bill - North Star Hosting - 2026-06.pdf` — labelled vendor bill; issuer and `record_type` are
  legal, but an isolated bill remains a transaction rather than a books branch.
- `Bank Reconciliation - Operating Account - June 2026.xlsx` — bank balance versus book balance
  with outstanding items; the collision against an institution-issued statement is explicit.
- `Expense Report - June - Maya Chen.xlsx` — claimant, business-purpose column, expense rows,
  approval and receipt links; the column label does not legalise the Applications-scoped
  `purpose` field and linked receipts inherit nothing.
- `Accounts Receivable Aging - 2026-06-30.xlsx` — customer/invoice/due/status/balance columns;
  customers are counterparties, not the file’s `institution`.
- `Invoice 1048 is overdue.eml` — structured mail and attachment slots; mail is a source type, not
  proof, and invoice grouping copies no facts.
- `Screenshot 2026-07-03 at 10.14.22.png` — OCR of a receivables dashboard with positive
  screen-origin evidence; Finance and Photos may both hold on disjoint evidence.
- `2026-Q2-books.zip` — a mixed manifest read without extraction; membership is proposed from the
  manifest while member facts remain on members.
- `BlueFinch_2026-06-30.qbb` — proprietary opaque backup; universal facts only, manual attachment
  eligible, and Unsupported or Encrypted when no approved extractor exists.
- `IMG_7712.jpg` — sparse photographed receipt beside an expense packet; Photos facts survive,
  Finance facts remain absent, and `group_without_copying_facts` is true.
- `Consulting Agreement - Acme - executed.pdf` — the career/legal collision: parties, fees and
  payment language, but no invoice or ledger structure.
- `Tax estimate worksheet.xlsx` — the tax-filings collision: labelled tax-year/summary structure,
  no ongoing transaction system.
- `Bookkeeping Practice Set - Chapter 4.xlsx` — the tempting structural false positive. It has
  populated journals and ledgers but explicit course/assignment/sample-data evidence, so the
  bookkeeping template must not fire from table shape alone.

This covers labelled form versus unlabelled data, OCR, screenshot, archive, mail, opaque binary,
the sparse `HW 3`-style grouping case, a neighbour collision, and a legitimate two-schema capture.

## Recognition discipline

The rule family is structural rather than lexical. A filled accounting workbook must show a
coherent system of labelled sheets/columns and transaction values; an invoice must expose issuer
and recipient roles plus its billing structure; a reconciliation must compare book and bank
balances. No number of money-shaped values, organization names, accounting product names, or file
extensions can substitute for that evidence.

Grouping is intentionally stronger than per-file fact writing. An expense report can anchor sparse
receipts; an invoice can join a client engagement; a bank statement can join a reconciliation.
Those relationships are membership records. They do not create business use, client, reporting
period, account, or record type on a sparse member.

## Fields and `proposed_fields`

`fields: []` and `proposed_fields: []` are deliberate.

- The template reuses only `institution`, `account_type`, `tax_year`, and `record_type`; copying
  them here would violate `uses_schema`.
- `merchant` and `vendor` were rejected as keys. On a received bill, the vendor is the explicit
  record issuer and the existing `institution` role can hold it. New synonyms would recreate the
  overnight catalogue’s vocabulary failure.
- `client` and `our_firm` already exist canonically. The issue is schema reference, not field
  invention: Finance references neither, Career is still field-less, and `our_firm` is correctly
  destination-ineligible. The row records an `institution ↔ client` role-split finding and asks
  whether Finance may reference `client`; it does not edit the canonical list.
- `account_holder` is already proposed once, on `finance.json`. This template neither duplicates
  nor widens that proposal.
- An operational reporting period is genuinely missing: `tax_year` is too narrow,
  `creation_date` is a filesystem fact, `term` is academic, and `application_cycle` is scoped.
  I considered `reporting_period` and did **not** propose it here. `finance.personal-records`
  already records the same seam, and one template must not mint a shared field simply to make a
  familiar year/month tree expressible.

## Dimension order

Recommended `record_type → account_type`, `time_first: false`.

`record_type` makes the child intelligible: General Ledger, Sales Invoices, Vendor Bills,
Reconciliations, Expense Reports, Receivables, and Financial Statements are the working functions.
`account_type` is optional beneath the function only when the file has a real account function or
bank-account kind. A whole-ledger workbook spans the chart and correctly flattens before that
level.

Two tempting levels are excluded:

- `institution` would fragment a working book by every organization mentioned and would often put
  the holder’s own operation in the authorship/collector position.
- `tax_year` would mislabel monthly, quarterly, and fiscal reporting periods. A real labelled tax
  year belongs to the tax-filings situation; otherwise the period stays a group label until the
  vocabulary question is answered.

This is a placeholder recommendation over a safety domain, not a path and not an automatic tree.

## Edges

- `collides_with` carries five same-kind roster ids. Three reciprocate landed edges:
  `finance.receipts-expenses`, `finance.tax-filings`, and
  `career.consulting-client-engagement`. `finance.personal-records` adds the statement-versus-
  reconciliation discriminator. `legal.leases-agreements` is the specific same-kind legal
  neighbour for agreement-versus-invoice structure; the broader `legal` schema cannot be the
  endpoint of a template collision.
- `also_holds_with: []` is required by CONNECTION: it is schema-to-schema only. The landed
  `finance.json` already carries the Finance joins. `file_examples[].also_schema` expresses the
  Photo and Legal examples without authoring a duplicate edge.
- `role_split` records the `institution ↔ client` finding next to the consulting neighbour. It is
  not a canonical edit; `canonical_fields.json` remains untouched.
- Fallthrough includes the roster-required Independent Records plus Receipts and Confirmations,
  Review Later, Protected Records, Unsupported or Encrypted, Temporary Screenshots, and One-Off
  Images. Each is one of the nine closed residual names and each has a concrete fixture.
- `parent_id` stays null and browse-only. `shares_field` is derived and absent.

## Neighbours considered that received no edge

- **`career` schema** — wrong kind for `collides_with`, and template rows may not author
  `also_holds_with`. The concrete consulting template carries the useful edge instead.
- **`legal` schema** — same kind mismatch. Finance/Legal collision and co-activation already live
  on the two schema rows; this template adds only the specific `legal.leases-agreements` mutex.
- **`photos.screenshot-captures` / `photos.scanned-documents`** — no template collision was added.
  A photographed receipt or dashboard capture legitimately keeps Photos and Finance schema facts;
  the landed Finance schema already carries that join, while the sparse image fixture abstains.
- **`academic.coursework`** — the practice-set fixture is a strong false positive, but a completed
  accounting assignment can legitimately carry Academic and Finance readings on disjoint evidence.
  Course/assignment/sample markers are conflicts and grouping inputs rather than a mutex edge here.
- **`finance.subscriptions-utilities`** — a recurring service bill has its own period/account
  structure, but it can still be a supporting member of the operation’s books. The vendor-bill
  fixture deliberately excludes recurring slots; no second edge was needed.
- **`finance.payroll-received`** — that roster row is income/payroll received by a person. An
  employer-side payroll register is a different role and highly sensitive; this node does not
  absorb it merely because it can appear in a ledger.
- **`finance.cap-table-equity`** — ownership instruments and cap tables have a distinct structure;
  a balance-sheet equity row is content inside the books, not evidence that the workbook is an
  equity-paperwork template.

## Files considered and rejected

- `.qfx`, `.ofx`, `.iif`, and native accounting-database variants were not assigned a
  `SOURCE_TYPE`; P5 owns that routing choice. `.csv` supplies the structured export fixture and
  `.qbb` supplies the honest metadata-only backup fixture.
- A billing-reminder `.ics` was rejected. Calendar is a source type, not a domain, and a payee,
  amount, and due date in an event do not distinguish an invoice reminder from a personal bill.
- A customer or vendor `.vcf` was rejected. Contact data is privacy/search material and should
  not become a folder proposal.
- Payroll registers, employee tax records, and contractor identity forms were rejected from the
  core examples. They raise separate employer-side and identity/privacy roles and would let a
  bookkeeping placeholder swallow a high-risk neighbour without a roster decision.
- Blank invoice templates, sample company files, and classroom ledger exercises were rejected as
  positive examples. One survives explicitly as the adversarial false fixture.

## Where the dispatch prompt and CONNECTION differ

The prompt’s edge summary can be read as permitting `also_holds_with` on any row because one file
may carry both schemas. CONNECTION limits authored `also_holds_with` to schema pairs. CONNECTION
wins, so this template’s list is empty and the file examples point at the already-authored schema
joins.

The assignment says `launch: placeholder` while Finance is a safety schema. Both are retained:
this row is a placeholder template, and its files still receive the Finance protection gate. A
placeholder does not erase safety; safety does not silently promote the template to launch-full.

## NEEDS-JOSEPH (this node only)

- **NJ-sbb-1 — client on an issued invoice.** `client` and `our_firm` are already canonical, but
  Finance references neither and Career’s field rows are deferred. May Finance reference the
  existing destination-eligible `client` key for this template, with `our_firm` remaining
  metadata-only, or must the billed client stay only an observation/group role until Career
  lands? Widening `institution` to both issuer and recipient is not an acceptable third answer.
- **NJ-sbb-2 — operational reporting period.** Do monthly, quarterly, and fiscal reporting ranges
  gain one shared destination-eligible `reporting_period` field, or remain accepted-group labels
  with record-type-only branches? `tax_year` must not be widened silently, and this row does not
  mint the key while the same seam is already open on `finance.personal-records`.

## Validation evidence

- `jq empty` passes. Identity, kind, schema, launch, refusal state, empty template fields,
  `parent_id: null`, non-empty `never_alone`, and `file_kinds.never_alone: true` all pass explicit
  `jq -e` assertions.
- Fifteen file examples are present. Every `facts_legal` key resolves to
  `canonical_fields.json`; both dimensions resolve to destination-eligible Finance fields; and
  the two role-split keys are canonical.
- Every collision target resolves to a `kind: template` roster row. Every `also_schema` resolves
  to a roster schema. Every example and file-kind source type belongs to the closed P5 vocabulary.
  Every fallthrough target is one of the nine residual names.
- `IMG_7712.jpg` explicitly passes the sparse-file assertion with
  `group_without_copying_facts: true`. No `facts_legal` value contains a path, no authored
  `shares_field` exists, and the template copies no Finance field rows.
- A fixed-string `rg` pass extracted and checked every ASCII-single-quoted design span in the
  finished JSON: **22 checked, 0 misses** against `planning/00-database-agent-product-design.md`.
  The research memo carries no attributed quotation of its own.
- Searches found no numeric threshold, confidence score, or authored P7 handling class in the
  node. A trailing-whitespace scan is empty for both assigned files; `git diff --no-index
  --check` emits no whitespace errors (its nonzero status is the expected content-diff status for
  new untracked files).
- `python3 planning/domains/check.py` reports the recorded legacy baseline unchanged:
  **14 files, 574 entries, 566 pre-existing in-file problems; 574 unique ids, 0 cross-file
  problems**. As the dispatch state warns, that gate does not scan `nodes/`; the row-specific
  assertions above are the evidence for these outputs.
- Output scope is exactly the two assigned, newly written paths. No roster, canonical-field,
  contract, checker, source, spec, or neighbouring node was edited.
