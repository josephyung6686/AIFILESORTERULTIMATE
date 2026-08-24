# finance.cap-table-equity — lab notes (R1b)

Date: 2026-08-22
Roster row: `kind: template`, `schema_id: finance`, `launch: placeholder`, `parent_id: null`.
Output: [`finance.cap-table-equity.json`](finance.cap-table-equity.json).

## Sources actually used

### Binding local sources

- `planning/26-research-dispatch-state.md` and
  `planning/domains/dispatch/r1b-swarm.workflow.js` — read first as assigned. They establish the
  resumable R1b state, the one-row ownership boundary, and the current wrapper hierarchy.
- `planning/domains/dispatch/make_prompt.py finance.cap-table-equity` — generated the stamped
  assignment that supplied the exact row metadata, node test, research procedure, output shape,
  and done-when checks.
- `planning/00-database-agent-product-design.md` — read in full, including evidence extraction,
  observations versus facts, domain-scoped fields, grouping, template design, residuals, and the
  privacy/operations layer. Every design phrase attributed to `00` in either output file was
  checked with `rg -F` against this file before drafting and is re-audited below.
- `planning/01-product-design-structured.md` — read only the generated prompt's relevant
  rendering sections: 3.1–3.15, 4.3–4.10, 5.3–5.9, 7.1–7.9, and 8.4. It was used only as a
  locator and cross-check; `00` wins.
- `planning/prompts/ALIGNMENT.md` — templates are organizational situations, work types are
  values, one file can keep several facts, and a template that merely repeats the Finance default
  fails the node test.
- `planning/domains/_CONTRACT.md` — entry shape, snake_case ratification, template field reuse,
  and R0's closed edge vocabulary.
- `planning/domains/CONNECTION.md` and `planning/domains/CONNECTION-EXAMPLES.md` — binding node
  test, browse-only `parent_id`, activation/grouping firewall, schema-only `also_holds_with`,
  same-kind collisions, residual names, Finance safety split, and the worked-file invariants.
- `planning/overnight/council/DECISION-BRIEF.md` — ratified D6, D2, and J-IND. D6 fixes
  snake_case; D2 keeps handling classification in P7 rather than this row; J-IND confirms that a
  placeholder still receives useful gist-level research rather than hollow coverage.
- `planning/domains/roster.json` — confirmed the row, `uses_schema` relationship expressed here
  as `schema_id: finance`, required neighbours `legal` and `career`, required residual Protected
  Records, and every authored edge endpoint.
- `planning/domains/canonical_fields.json` — confirmed the four inherited Finance keys and their
  meanings. No key was minted. The Finance schema's existing `account_holder` proposal was read
  from the landed schema node and is referenced, not duplicated.
- `src/evidence_shape/vocabulary.py` — mechanically checked every `source_type` against the
  fourteen-member `SOURCE_TYPES` vocabulary.
- Landed or currently visible neighbour nodes: `nodes/finance.json`,
  `nodes/finance.personal-records.json`, `nodes/finance.investment-brokerage.json`,
  `nodes/career.employment-records.json`, `nodes/legal.json`, `nodes/career.json`, and the
  currently visible `nodes/finance.insurance-corporate.json` draft. Three already named this row
  in a collision; this row reciprocates them. The insurance file is one of dispatch state's
  untrusted partials and belongs to another workstream, so its edge is aligned but explicitly
  left for R1c to re-check after that owner finishes.
- Committed history: `git log` identifies `a6395f6` as the dispatch-state commit that landed the
  61-row R1b baseline and recorded this row as missing. No earlier version of either owned output
  file exists to salvage.

### External, bottom-up reality checks

External sources establish that the listed files and labelled structures are real. They do not
override product design, create canonical fields, or supply any activation threshold.

- Carta Support, [How to download a cap table report](https://support.carta.com/kb/guide/en/how-to-download-a-cap-table-report-m8JbBrvZ4y/Steps/3802667)
  — current exports can be organized by share class or stakeholder and can include summary,
  intermediate, detailed, securities-ledger, option, warrant, and SAFE/convertible tabs, with an
  explicit report-as-of date. This grounded the cap-table workbook fixture.
- Carta Support, [How to export the Equity Plan Report](https://support.carta.com/kb/guide/en/how-to-export-the-equity-plan-report-com7b20nW0/Steps/3724540)
  — the report carries grants, vesting schedules, plan transactions, and participant data. This
  grounded the equity-plan workbook rather than treating every spreadsheet as a ledger.
- Carta Support, [How to download the Open Cap Table Excel Standard](https://support.carta.com/kb/guide/en/how-to-download-the-open-cap-table-excel-standard-ocx-x4mJs6421p/Steps/3747538)
  — confirms a standardized Excel cap-table export is a real file users obtain.
- Open Cap Table Coalition, [Open Cap Table Format documentation](https://open-cap-table-coalition.github.io/Open-Cap-Format-OCF/)
  and [OCF architecture](https://open-cap-table-coalition.github.io/Open-Cap-Format-OCF/explainers/Architecture/)
  — OCF is JSON-based; a package covers issuer, stakeholders, stock classes, plans,
  transactions, valuations, vesting, financings, and document references, with a recommended
  `.ocf.zip` container. This grounded the structured archive case.
- Y Combinator, [SAFE forms and guide](https://www.ycombinator.com/safe#downloads) — confirms
  signed SAFEs are contracts for future equity, documents multiple form variants and the
  separate side-letter pattern, and distinguishes the company and investor roles. It grounded
  the signed SAFE fixture without turning SAFE into a field.
- SEC EDGAR, [Notice of Stock Option Grant, Stock Option Agreement, and Exercise Notice](https://www.sec.gov/Archives/edgar/data/1778922/000162828026004091/exhibit102-sx1a.htm)
  — a recent filed form contains labelled participant, grant number/date, vesting commencement,
  shares, exercise price, option type, expiration, vesting schedule, and exercise-notice slots.
  These are the deterministic labelled-slot family, not a private regex.
- SEC EDGAR, [Restricted Stock Unit Agreement and Grant Notice](https://www.sec.gov/Archives/edgar/data/1294133/000129413326000028/ingn-ex99_1.htm)
  — a recent filed RSU form separates company, participant, grant number/date, units, vesting,
  plan, and execution structure. This grounded the RSU case and its real collision with
  employment records.
- Carta, [A founder's guide to the 409A valuation](https://carta.com/learn/startups/equity-management/409a-valuation/)
  — a real valuation report covers subject company, effective date, enterprise value, equity
  allocation, valuation method, common-stock fair market value, and assumptions; the draft/final
  report and board-approval sequence is also real. This grounded the valuation fixture while
  leaving amounts and dates outside the four-field Finance schema.
- IRS, [Form 15620, Section 83(b) Election](https://www.irs.gov/pub/irs-pdf/f15620.pdf) — the
  official form contains taxpayer, taxable-year, property-transfer, fair-market-value,
  amount-paid, service-recipient, signature, address, and taxpayer-identification slots. It
  grounded both the equity/tax overlap and the immediate privacy posture.

## Did this row survive the node test?

Yes. It is not the Finance default with a more fashionable label.

- **Detection differs materially.** The Finance schema's recognition is a union that gets a file
  into Finance. This template must distinguish one organizational situation from the other
  Finance templates. Cap-table worksheet families, equity-plan ledgers, labelled grant and
  exercise slots, SAFE terms, valuation-report structure, and section 83(b) form structure are
  specific and independently evidenced by the primary/official sources above.
- **Recommended dimensions differ materially.** The Finance default is
  `institution → account_type → record_type`. This row recommends
  `institution → record_type`. A company-wide cap table spans many classes and holders; a SAFE
  and a valuation report are not holder accounts. Requiring `account_type` would create an empty
  or fabricated level. It becomes an optional middle level only when the record itself labels an
  equity plan or holder account.
- **Privacy is not claimed as a novel licence.** It is the same Finance safety posture under PR-2.
  Company-side material happens to expose many stakeholders rather than one holder, so redaction
  must cover rows and summaries, but that is application of `00`, not a new handling class.

This is exactly the placeholder depth J-IND asks for: enough real structure to route and protect
usefully, without pretending that v1 has a fully modelled corporate-securities ontology.

## The organizational situation, bottom up

The roster intentionally names both company-side and holder-side files. The kept corpus shows why
that is useful and why it is also an open seam:

- **Company-side administration:** cap-table snapshots, OCX/OCF exports, equity-plan reports,
  stakeholder/security ledgers, valuation reports, grant approvals, signed financing
  instruments, and data-room packets. One issuer and many holders.
- **Holder-side packet:** the person's grant or award, vesting statement, exercise notice,
  dashboard screenshot, acceptance email, and related tax election. One issuer and usually one
  holder, with a strong career overlap.
- **Shared bridge files:** a formal grant exists in both worlds; a board consent connects grants
  to the company ledger; an exercise connects a holder instrument to an issuance; a SAFE updates
  the cap table and is also a legal contract.

One template can recommend issuer then record type across both, and accepted P9 groups preserve
the separate company and holder perspectives. The row does not silently decide that this is the
best permanent boundary: the split question is in NEEDS-JOSEPH.

## Files kept and ugly-case coverage

Seventeen concrete examples are in the JSON. Together they discharge every research-procedure
case:

- labelled spreadsheet: `Acme_Cap_Table_as_of_2026-06-30.xlsx`;
- standardized structured archive: `Acme_OCF_Export.ocf.zip`;
- multi-holder plan workbook: `2026 Equity Plan Report.xlsx`;
- labelled form/agreement: `RSU Grant Notice - Jordan Lee - Signed.pdf`;
- signed legal/finance dual-use instrument:
  `Post-Money SAFE - Valuation Cap - Northstar Ventures - Countersigned.pdf`;
- valuation report: `Acme 409A Valuation Report - Effective 2026-05-31.pdf`;
- identity-sensitive tax/equity overlap:
  `Form 15620 - Section 83(b) Election - Jordan Lee - Signed.pdf`;
- labelled exercise form: `Exercise Notice - Grant OPT-0174.pdf`;
- structured mail: `Action required - accept your Acme option grant.eml`;
- OCR screenshot: `Screenshot 2026-06-14 at 09.18.42.png`;
- legal co-activation and mixed attachment:
  `Unanimous Board Consent - Equity Grants and FMV Approval.pdf`;
- sparse OCR analogue of `HW 3.pdf`: `vesting_schedule_scan.pdf`;
- career false positive: `Offer Letter - Jordan Lee - Equity Package.pdf`;
- brokerage false positive: `Brokerage Trade Confirmation - ACME.pdf`;
- corporate-insurance false positive: `D&O Insurance Declarations - Acme Robotics.pdf`;
- encrypted packet: `Equity_Data_Room.zip`;
- calendar format that does not activate by format or title:
  `Option Vesting Reminder.ics`.

The mail, calendar, OCR, archive, structured JSON-package, encrypted, and cross-domain cases are
not decoration. They each exercise a distinct boundary in `00`.

## Sparse-file discipline

`vesting_schedule_scan.pdf` is this node's `HW 3.pdf`. OCR recovers a vesting heading, dates,
quantities, and part of a grant identifier, but the issuer, holder, plan, and instrument are
cropped out. It retrieves both an option packet and an unrelated RSU packet. The file can carry
`record_type = vesting schedule` from its own heading and remain an uncertain group member; it
cannot inherit `institution`, `account_type`, `account_holder`, or a complete grant identifier
from either neighbour. The JSON sets `group_without_copying_facts: true` and routes the inactive
case to Review Later.

The dashboard screenshot, board consent, OCF archive, encrypted data room, and calendar reminder
also set `group_without_copying_facts: true` where the packet supplies context but not a fact
writer.

## Field decisions and proposed_fields

`proposed_fields` is deliberately **empty**.

- `institution` is used for the underlying security issuer or subject company. Its canonical
  aliases already include issuer. The cap-table platform, valuation provider, law firm,
  e-signature provider, and brokerage custodian are separate observed roles and never overwrite
  that value.
- `record_type` carries cap table, equity plan report, grant notice, SAFE, valuation report,
  exercise notice, board consent, tax election, and other document/instrument roles as values.
- `account_type` is legal only when the file labels a holder account or an equity plan. It is not
  filled with every share class, instrument acronym, or grant type just to populate a level.
- `tax_year` is legal only from a labelled taxable-year slot. A grant date, vesting date,
  valuation effective date, cap-table as-of date, or filesystem date cannot fill it.
- `account_holder` is not re-proposed. `finance.json` already proposes it, distinguishes it from
  institution, marks it destination-ineligible, and owns the canonical-field question. This row
  uses the exact same proposed key in file examples so R1c sees one proposal, not a synonym such
  as stakeholder, grantee, shareholder, investor, or participant.

Three tempting additions were rejected:

- **`equity_issuer`** — rejected for now because `institution` already has issuer in its canonical
  role. The residual ambiguity on appraiser/platform-authored reports is a role decision for
  Joseph, not permission to create a synonym.
- **`equity_instrument` / `security_class`** — rejected because most organizational value is
  already expressible as `record_type`, while an explicit plan/account can use `account_type`.
  A new field might later be warranted for deep corporate administration, but this placeholder
  row cannot prove that v1 needs it as a destination dimension.
- **`as_of_date`, `effective_date`, or `grant_id`** — rejected as catch-all fields. The dates have
  different meanings and none is `tax_year`; a generic date would collapse the role discipline
  the product requires. A grant identifier is valuable raw evidence and a P9 anchor, but it does
  not yet justify a long-term folder-language field.

The product may create new values at runtime; it may not create a new field merely because an
equity platform exposes a convenient column.

## Dimension order and optional branch patterns

Default: `institution → record_type`.

- **Issuer first:** Cap Table, SAFE, Grant Notice, Exercise Notice, and Valuation Report are
  unintelligible without the company whose equity they concern. Institution means that issuer,
  not the software or professional-services producer.
- **Record type second:** It cleanly separates the recurring document roles across both
  company-side and holder-side packets.
- **Optional account type:** insert `account_type` between them only when the file labels a plan
  or holder account and the split creates useful siblings.
- **Optional tax-year leaf:** only on a labelled tax/election subset; never from operational
  dates.
- **Flattening:** a one-company corpus can flatten institution; a one-grant packet can remain
  flat. Uneven depth is expected.
- **Not time-first:** time does not define this record situation, and the available time field is
  tax-scoped anyway.

No path is stored in a fact or in the row. This is a recommendation the user may reverse, remove,
or flatten before freeze.

## Neighbour decisions

### Edges authored

- **`career.employment-records`** — reciprocal to the landed node. The clean discriminator is a
  promise in an offer/employment letter versus a formally issued grant with its own labelled plan,
  grant, vesting, and execution structure. The landed career node currently narrows the cap-table
  side more aggressively to company-side administration; that conflicts with this roster row's
  explicit inclusion of option grants and equity statements. This row names the evidence-item
  mutex without pretending that a formal employee grant cannot also be a career record. R1c must
  adjudicate the wording and Joseph may split the template.
- **`finance.investment-brokerage`** — reciprocal to the landed node. Custodian account plus
  trade/settlement structure wins there; issuer plan/grant/vesting/exercise structure wins here.
- **`finance.insurance-corporate`** — reciprocal to the currently visible partial. Policy number,
  carrier, period, limits and premium win there; capitalization, grant, issuance, or valuation
  structure wins here. R1c must re-check after the other owner completes the partial.
- **`legal.leases-agreements`** — discharges the legal neighbour at template level. A signature
  and governing-law clause are generic; equity subject matter is this template's evidence.
- **`finance.small-business-bookkeeping`** — prevents a company spreadsheet from becoming a cap
  table merely because it has names, percentages and formulas. Stakeholder/security/issuance
  headers differ from debit/credit/invoice/expense headers.
- **`finance.tax-filings`** — the section 83(b) form is legitimately in both groups; the labelled
  taxable-year evidence belongs to the filing situation, while property-transfer and restricted-
  equity evidence belongs here.
- **`photos.screenshot-captures`** — PNG shape and missing EXIF decide neither side; OCR of a
  labelled grant/ownership screen is the equity evidence.

### Considered but no edge

- **Schema ids `legal` and `career` directly:** forbidden by kind. A template collision must name
  a template; `also_holds_with` is schema-only. Per-file dual activation is recorded through
  `also_schema`, and the Finance schema already carries its legal safety join.
- **`career.recruiting`:** an unsigned offer can belong to recruiting, but
  `career.employment-records` already owns the direct reciprocal seam and adding both would encode
  one distinction twice. The open question records the prospective-versus-employed boundary.
- **`legal.personal-legal-matters`:** too broad. The actual confusable evidence is a signed
  agreement, so the edge goes to `legal.leases-agreements`; a board consent also activates the
  legal schema from its own evidence without needing a topic-similarity edge.
- **`finance.personal-records`:** a holder equity statement is a personal record in ordinary
  speech, but the concrete false file is a brokerage statement, so the edge goes to the
  investment-brokerage template. Broad personal-ness is not an edge.
- **`finance.crypto-assets`:** OCF and digital-asset exports can both be JSON, and token/equity
  instruments can coexist, but source format and the word token are not enough to name one
  discriminating evidence item. No speculative edge was written.
- **`identity.core-documents`:** Form 15620 carries direct identity data, but it is not an identity
  document whose purpose is to establish identity. The identity safety schema may co-activate;
  that is recorded on the file example, not forced into a template collision.
- **Residual `Independent Records`:** rejected. A signed SAFE, cap table, grant, exercise notice,
  valuation report, or tax election is sensitive even when isolated. Protected Records is safer
  and is the roster-required residual.
- **Residual `Receipts and Confirmations`:** rejected. Exercise confirmations and issuance notices
  contain private ownership and compensation data; a lexical match on confirmation must not route
  them out of protection.

## Files considered and rejected from the kept corpus

- **Blank cap-table template downloaded from a blog.** It may be a reference tool, not the user's
  capitalization record. Without issuer data or a populated capitalization structure it belongs
  in Reading Inbox or Reference Clips, not this node.
- **Investor pitch deck with one cap-table or dilution slide.** It discusses capitalization but is
  a fundraising presentation. A slide containing a hypothetical table does not make the deck the
  issuer's durable cap-table record.
- **Public SEC blank form of grant agreement.** It grounded the labelled-slot research, but a blank
  public form in a user's corpus is legal reference material. Only a filled or issuer-specific
  instrument activates this situation.
- **Shareholder contact list / exported address book.** Names and email addresses without security,
  issuance, or ownership structure are contact data. `00` says contact formats "should normally
  be privacy-protected rather than used to create folder proposals."
- **General board minutes.** A company name, directors and signatures are legal/governance
  evidence; only explicit equity, issuance, grant, plan, valuation, or capitalization resolutions
  make the consent relevant here.
- **`cap_table.py` inside a software repository.** Source code that models capitalization remains
  inside the preserved software project. Its variable names do not make it a personal equity
  record.
- **Expense or cash-flow workbook.** Rejected into the bookkeeping collision; its accounting
  headers and running balances differ from stakeholder/security/issuance structure.

## Contract-versus-prompt seams resolved as instructed

- The generated prompt's sketch shows bare strings in `falls_through_to`, while the landed
  template nodes and `_CONTRACT.md` use objects with `residual_template`, rationale, and
  provenance. CONNECTION/_CONTRACT wins; this row uses the object form.
- The prompt's older text says D6 was unset. The wrapper and ratification say snake_case and
  `subject`; the ratification wins.
- The prompt includes an `also_holds_with` slot on every row, but CONNECTION limits that edge to
  schema pairs. This template leaves it empty and records per-file `also_schema` examples.
- Templates may not copy the schema fields. `fields` is empty; proposed-field discussion lives in
  lab notes and `proposed_fields` remains empty.
- `parent_id` is browse-only and R1b does not author it. It remains null.
- D2 means this row says only `potentially_sensitive`; it never authors a handling class or treats
  unreadability as a Finance fact.

## Quotation, vocabulary, and structural audits

- All phrases attributed to `00` were first located with `rg -F`. After drafting, a second audit
  checks every attributed span against `00`; no external source is quoted as product authority.
- Numeric strings in the row are document names, legal section/form identifiers, dates, grant
  identifiers, and concrete filenames. None is a recognition threshold, score, margin, or folder
  count.
- All edge endpoints resolve to roster ids and all residual targets use the nine-name closed list.
- Every source type resolves to `SOURCE_TYPES`; extensions remain never-alone.
- No file example writes a path as a fact.

## NEEDS-JOSEPH (this node only)

### NJ-cap-table-1 — one template or two perspectives?

Does `finance.cap-table-equity` intentionally combine the issuer/company cap-table operation and
the individual's equity-compensation packet? The roster explicitly combines cap tables, option
grants, SAFEs, valuation reports, and equity statements, so this row preserves one useful
placeholder template with `institution → record_type` and optional account type. A split would
produce two genuinely different situations: company capitalization administration (one issuer,
many holders, corporate/legal neighbours) and holder equity records (one holder, strong
employment/brokerage neighbours). The choice affects the collision wording with
`career.employment-records` and the privacy presentation. Recorded, not resolved.

### NJ-cap-table-2 — what exactly does institution mean here?

May `institution` hold the **underlying security issuer or subject company** when a cap-table
platform generated the workbook or an independent appraiser authored the valuation report? This
row says yes because the canonical aliases include issuer and grouping by the software/appraiser
would be useless. If institution is restricted to the document producer, Finance lacks a
destination-eligible issuer/subject-company role and a canonical field decision is required.
No `equity_issuer` synonym was proposed while this role question remains open.

Neither question blocks a useful placeholder node. Both block pretending the current two-level
order is the final deep corporate-equity taxonomy.
