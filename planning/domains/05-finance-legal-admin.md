# Domain catalogue — finance, legal, tax and administration

Supercategory: `finance-legal-admin`  
Slice: 05  
Entries: 38 — 1 design, 12 inference, 25 proposal  
Contract: [`_CONTRACT.md`](_CONTRACT.md) · Source of truth: [`00-database-agent-product-design.md`](../00-database-agent-product-design.md)

## How to read this file

- **Double quotes are verbatim quotations** from the source of truth and nothing else. Every one is checked by a literal substring test at build time; a quotation that does not appear in the source fails the build. Where a claim is mine rather than the design's it is written as plain prose with no quote marks.
- **Single quotes are pattern literals** — tokens a recogniser looks for in a document — following the convention in the contract's own worked example.
- `reliability_ceiling` uses §3.13's six states only. `direct` means a labeled field, a document title or explicit metadata. `validated` means a rule found a pattern **and** passed a context check, so every `validated` field has a matching `recognition.deterministic` line that could actually confirm it. `llm_supported` means the value needs language interpretation and therefore cannot be produced without the model route.
- `sensitivity` is §2.9's phrase `potentially sensitive` and nothing more. No handling class is assigned anywhere in this file; handling classes are P7's (§8.4).
- No thresholds, no scores, no counts, no retention periods. Digits appear only inside `example` values, which are data in the same way the contract's own `BUSIB 4300` is.

## Two findings that apply to the whole slice

**1 — Jurisdiction is undecided, and this slice cannot be finished without it.** The design states no jurisdiction anywhere. Tax years, tax document names, entity types, insolvency and probate procedures, court party labels, bank-identifier labels and immigration routes are all jurisdiction-defined, and several of them are not translations of one another but genuinely different objects. Every entry here is written functionally and carries an explicit `jurisdiction` field wherever neutrality does not reach. That keeps the catalogue honest but leaves the deterministic recognisers thinner than they could be, because no per-jurisdiction gazetteer can be built until the scope question is answered. It is raised as an `open_question` on `fin.financial-records` and sharpened on the six entries where neutrality genuinely fails: tax filing, tax supporting documents, business formation, wills and estates, immigration, and insolvency.

**2 — Every entry in this slice is `potentially_sensitive`, and that is the finding rather than a failure to discriminate.** §3.15: "Finance, identity, medical, and legal material should be implemented first as safety domains, meaning the system detects and protects them before any cloud or automated placement decision is allowed." This slice *is* that sentence. §8.4's description of the corpus names "identity documents, account statements, tax records, medical information, legal records, credentials" — which covers essentially every entry below. The consequence is load-bearing rather than cosmetic: §8.4 requires privacy policy to be enforced **before** content reaches any model, so the model route is unavailable by default across this whole supercategory, and every field whose ceiling is `llm_supported` will frequently resolve to `unknown` rather than to a weaker value. P6 records that as `privacy_withheld`, not as an abstention. Domains here should be designed to work off their `direct` and `validated` fields alone.

## Index

| id | name | provenance | time first |
|---|---|---|---|
| `fin.financial-records` | Financial records (branch root) | design | no |
| `fin.bank-account` | Personal banking and deposit accounts | inference | no |
| `fin.investment-brokerage` | Investment and brokerage accounts | inference | no |
| `fin.retirement-account` | Retirement and pension accounts | inference | no |
| `tax.filing` | Tax filing (per year, per jurisdiction, per filing entity) | inference | no |
| `tax.supporting-documents` | Tax supporting documents | inference | no |
| `fin.receipts-expenses` | Receipts and personal expenses | inference | yes |
| `biz.expense-report` | Expense reports and reimbursement claims | proposal | no |
| `biz.invoice-issued` | Invoices issued (receivable) | inference | no |
| `biz.invoice-received` | Invoices received (payable) | inference | no |
| `biz.bookkeeping` | Small-business bookkeeping and accounts | proposal | no |
| `biz.payroll-employer` | Payroll (employer side) | proposal | no |
| `corp.business-formation` | Business formation and corporate records | proposal | no |
| `corp.shareholder-captable` | Shareholder and cap-table records | proposal | no |
| `corp.fundraising-investor` | Fundraising and investor materials | proposal | no |
| `fin.loan-mortgage` | Loans and mortgages | inference | no |
| `fin.credit` | Credit accounts and credit files | inference | no |
| `fin.insurance` | Insurance policies and claims | proposal | no |
| `legal.contracts` | Contracts and agreements (general) | inference | no |
| `legal.lease` | Leases and tenancies | proposal | no |
| `legal.litigation-dispute` | Litigation and disputes | proposal | no |
| `legal.wills-trusts-estates` | Wills, trusts and estates | proposal | no |
| `legal.power-of-attorney` | Powers of attorney and delegated authority | proposal | no |
| `corp.regulatory-filings` | Regulatory filings and returns | proposal | no |
| `corp.compliance-audit` | Compliance and audit | proposal | no |
| `admin.licences-permits` | Licences, permits and registrations | proposal | no |
| `legal.ip-registration` | Intellectual property registrations | proposal | no |
| `admin.immigration` | Immigration and residence paperwork | inference | no |
| `legal.court-records` | Court and tribunal records | proposal | no |
| `legal.notarised-documents` | Notarised, sworn and apostilled documents | proposal | no |
| `legal.debt-collection` | Debt collection and enforcement | proposal | no |
| `legal.bankruptcy-insolvency` | Bankruptcy and insolvency | proposal | no |
| `fin.charitable-giving` | Charitable giving | proposal | yes |
| `fin.grants-received` | Grants and awards received | proposal | no |
| `admin.subscriptions-recurring` | Subscriptions and recurring billing | proposal | no |
| `admin.warranties` | Warranties and product registrations | proposal | no |
| `biz.procurement-po` | Procurement and purchase orders | proposal | no |
| `biz.vendor-management` | Vendor and supplier management | proposal | no |

---

## `fin.financial-records` — Financial records (branch root)

Financial material that carries an institution and a record type but no more specific sub-domain — the Finance and Administration branch itself.

**Provenance:** **design** — a design sentence names this domain or its fields

**Cite:** §3.11 "Finance files may use institution, account type, tax year, and record type."; §5.3 "the proper structure for coursework is different from the proper structure for applications, research, photo events, and financial records"; §5.1 names "Finance and Administration" among the typical initial top-level branches

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `institution` | string | First Direct | `validated` | §3.11 names institution as a Finance field. §3.8 separates it from the holder: "A finance document may mention an account holder and an issuing bank." |
| `account_holder` | string | J. Yung | `validated` | §3.8 names the role pair directly: "A finance document may mention an account holder and an issuing bank." — the holder and the institution are different fields, not two instances of one organisation field |
| `account_type` | string | current account | `validated` | §3.11 names account type as a Finance field |
| `record_type` | string | statement | `validated` | §3.11 names record type as a Finance field; it is the work-type analogue for this branch |
| `tax_year` | string | 2025-26 | `validated` | §3.11 names tax year as a Finance field. The value shape is jurisdiction-dependent (a calendar year in some jurisdictions, a split year in others) — see the open question |
| `statement_period` | date range | 2025-04-06 to 2025-05-05 | `direct` | §3.13 direct: read from a labeled form field. §3.10 requires the explicit-regex path, never fuzzy parsing |
| `currency` | string | GBP | `direct` | §3.11 permits "several additional fields used only for search, privacy protection, explanation, or later review"; currency is a search and explanation field, not a folder dimension |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.4, §3.5):

- an institution name matched on a word boundary co-occurring with an account-type or record-type term — 'statement' | 'account number' | 'opening balance' | 'closing balance' | 'sort code' | 'routing number' | 'IBAN' | 'BSB'
- a labeled statement-period field ('statement period' | 'for the period' | 'period ending') co-occurring with an institution name

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- a scanned or photographed financial document whose institution appears only in a logo region and whose record type must be read from prose
- a file whose only financial signal is a body paragraph describing an arrangement, with no labeled field anywhere

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10):

- a currency amount — the single most over-firing pattern in this slice; it needs an institution name or a labeled period beside it
- a bare four-digit year — §3.10 is explicit that file names and documents "frequently contain numbers that look like years but are course identifiers, version numbers, build numbers, ZIP codes, or other unrelated values"
- a long digit string — an account number, a reference, an ISBN and a phone number are indistinguishable by shape
- an institution name alone: a bank appears as a payee, an employer, a sponsor, a landlord's agent and a merely cited organisation

### Work types

`statement`, `transaction export`, `confirmation letter`, `notice of change`, `correspondence`

### Grouping reasons (§4)

- one account across one statement year
- one institution's correspondence about one arrangement

### Template (§5)

`institution → account type → year`

Time first: **no**

§5.5: "a parent dimension should provide the context required to understand the child" — an account type is only meaningful once the institution is known, and a period is only meaningful once the account is. §5.5 also: "For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders.", which keeps the year last

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| tax.supporting-documents | the same statement is a banking record and a tax support document; the distinguishing signal is a tax-year label or an issuer statement that the document is produced for tax purposes, not the statement itself | §3.11 "One file may hold facts from more than one domain without losing information" — the file legitimately carries both sets of facts and the catalogue must not force a choice |
| fin.loan-mortgage | a bank statement submitted inside a mortgage application is still a bank statement; the loan packet's claim on it comes from purpose, not from content | §3.9 "The documents are content-incoherent but purpose-coherent." |
| biz.bookkeeping | for a sole trader the same account is personal and business at once; nothing in the document distinguishes them and the entity split is a user fact, not a document fact | §3.8 "The system must separate roles that happen to contain the same entity type" |

### Sensitivity

`potentially_sensitive` — §2.9's phrase "potentially sensitive" is the only marking made here. §3.15: "Finance, identity, medical, and legal material should be implemented first as safety domains, meaning the system detects and protects them before any cloud or automated placement decision is allowed." — this slice sits inside that sentence, so the conservative direction is the correct one. The handling CLASS is P7's (§8.4) and is not set.

### Open question — Joseph's call, unresolved

> Which jurisdictions does this product support at launch? The design states no jurisdiction anywhere. Tax year shape, tax document names, entity types, insolvency vocabulary, probate vocabulary, court party labels and bank-identifier labels all differ by country, and every domain in this slice inherits the answer. This catalogue is written jurisdiction-neutrally and carries an explicit `jurisdiction` field wherever neutrality is not achievable, but neutrality is a holding position, not a decision. SECOND, RELATED: §3.15 says finance and legal ship first as safety domains — detect and protect — while §5.7 lists financial records and legal matters among the template library's coverage. This catalogue supplies both halves. Joseph decides whether the folder-template half is live at launch or held behind the safety half.

---

## `fin.bank-account` — Personal banking and deposit accounts

Records produced by holding a deposit account at an institution — statements, transaction exports, opening and closing paperwork.

**Provenance:** **inference** — extends a design-named domain; the cite supports the extension, not the whole entry

**Cite:** extends §3.11's Finance row "Finance files may use institution, account type, tax year, and record type." and §3.8's role pair "A finance document may mention an account holder and an issuing bank."; §8.4 names "identity documents, account statements, tax records, medical information, legal records, credentials" among the corpus this product handles

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `institution` | string | Banco Santander | `validated` | §3.11 Finance field; §3.8 separates it from the holder |
| `account_holder` | string | J. Yung | `validated` | §3.8: "A finance document may mention an account holder and an issuing bank." — this is the design's own worked role split for this exact document type |
| `account_type` | string | savings | `validated` | §3.11 Finance field |
| `account_identifier` | string | ****4471 | `direct` | §3.13 direct: a labeled form field. Usually partially masked in the document itself; §8.4 keeps the raw value local |
| `statement_period` | date range | 2025-09-01 to 2025-09-30 | `direct` | a labeled period field; §3.10's explicit-regex path |
| `record_type` | string | statement | `validated` | §3.11 Finance field |
| `currency` | string | EUR | `direct` | §3.11's search-and-explanation allowance |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.4, §3.5):

- a statement-period label ('statement period' | 'for the period' | 'period ending') together with an account-type term and an institution name matched on a word boundary
- a balance-pair label ('opening balance' AND 'closing balance') together with an institution name
- an account-identifier label ('account number' | 'IBAN' | 'sort code' | 'routing number' | 'BSB' — the label set is jurisdiction-specific) together with a holder name block

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- a statement whose institution is present only as a logo and whose account type must be read from a product name in prose
- correspondence about an account that never states an account type in a labeled field

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10):

- a currency amount
- a masked account number on its own — the mask pattern appears in card receipts, payroll files and invoices alike
- an institution name in a payee or transaction line: §3.7's warning applies, "It should use word-boundary matching rather than substring matching.", and a bank appearing inside a transaction row is not the account's institution
- a bare year

### Work types

`statement`, `transaction export`, `account opening pack`, `closure letter`, `standing instruction`, `interest certificate`

### Grouping reasons (§4)

- one account across one statement year
- one account-opening packet across its forms and identity attachments

### Template (§5)

`institution → account → year`

Time first: **no**

§5.5: "a parent dimension should provide the context required to understand the child". A statement period means nothing until the account is known. §5.5's ordering rule keeps the year last: "For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders."

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| tax.supporting-documents | an interest certificate is issued by the bank and consumed by a filing; it carries both an institution and a tax year and belongs to both domains at once | §3.11 "One file may hold facts from more than one domain without losing information" |
| fin.loan-mortgage | statements gathered as affordability evidence for a loan application; the loan packet's claim rests on the purpose of the collection, not on the statements' content | §3.9 "The documents are content-incoherent but purpose-coherent." |
| biz.bookkeeping | sole-trader accounts are legitimately both personal and business; no document-level signal separates them | §4.9 "members carry irreconcilable course, institution, project, term, or purpose facts" — a business/personal split asserted without evidence is exactly such a fact |
| fin.investment-brokerage | cash-management accounts held at a broker look like deposit accounts; the distinguishing signal is a holdings or trade-confirmation block, not the institution | §3.7 "it should require both a minimum score and a minimum margin over the second-best candidate before it fills a facet" |

### Sensitivity

`potentially_sensitive` — §2.9's phrase "potentially sensitive" is the only marking made here. §3.15: "Finance, identity, medical, and legal material should be implemented first as safety domains, meaning the system detects and protects them before any cloud or automated placement decision is allowed." — this slice sits inside that sentence, so the conservative direction is the correct one. The handling CLASS is P7's (§8.4) and is not set.

---

## `fin.investment-brokerage` — Investment and brokerage accounts

Records produced by holding investments through a broker, custodian or fund platform — valuations, trade confirmations, corporate-action notices.

**Provenance:** **inference** — extends a design-named domain; the cite supports the extension, not the whole entry

**Cite:** extends §3.11's Finance row "Finance files may use institution, account type, tax year, and record type."; §3.8's "A finance document may mention an account holder and an issuing bank." supplies the role split between custodian and holder

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `institution` | string | Vanguard | `validated` | §3.11 Finance field; the custodian or platform, in the issuing-institution role of §3.8 |
| `account_holder` | string | J. Yung | `validated` | §3.8's holder role |
| `account_type` | string | stocks and shares ISA | `validated` | §3.11 Finance field. The value vocabulary is jurisdiction-specific — see the root entry's open question |
| `account_identifier` | string | ACCT-88213 | `direct` | §3.13 direct: a labeled form field |
| `statement_period` | date range | 2025-01-01 to 2025-12-31 | `direct` | a labeled period field |
| `record_type` | string | trade confirmation | `validated` | §3.11 Finance field |
| `tax_year` | string | 2025 | `validated` | §3.11 Finance field; present on the tax slips brokers issue, absent from routine valuations |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.4, §3.5):

- a holdings or valuation term ('portfolio valuation' | 'holdings' | 'units held' | 'cost basis' | 'book cost') together with an institution name matched on a word boundary
- a trade term ('trade confirmation' | 'contract note' | 'settlement date' | 'consideration') together with an account-identifier label
- a corporate-action term ('dividend' | 'rights issue' | 'stock split' | 'distribution') together with a labeled account and a period

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- a platform export whose column headers are the only structure and whose account type must be read from a product name
- a fund factsheet saved beside real holdings, where nothing distinguishes marketing material from a personal record

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10):

- a ticker-shaped uppercase token — §3.7's boundary rule is the whole defence here, and a three-letter ticker collides with ordinary words and initials
- a currency amount
- a percentage
- an institution name — a fund house is named in factsheets, news clippings and research notes that are not the user's records

### Work types

`valuation statement`, `trade confirmation`, `contract note`, `corporate-action notice`, `annual tax slip`, `transfer instruction`, `fund factsheet`

### Grouping reasons (§4)

- one account across one statement year
- one transfer or account-move packet across its instruction, confirmation and closing valuation

### Template (§5)

`institution → account → year`

Time first: **no**

§5.5: "a parent dimension should provide the context required to understand the child". A valuation is only meaningful once the account is known

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| fin.retirement-account | a pension wrapper is held on the same platform and produces the same valuation shape; the distinguishing signal is a retirement-scheme term, not the institution | §3.7 "it should require both a minimum score and a minimum margin over the second-best candidate before it fills a facet" |
| tax.supporting-documents | broker-issued tax slips carry a tax year and are consumed by a filing | §3.11 "One file may hold facts from more than one domain without losing information" |
| corp.shareholder-captable | shares in a private company held directly are cap-table material, not brokerage material; the distinguishing signal is an issuing entity and a share class rather than a custodian | §3.8 "The system must separate roles that happen to contain the same entity type" |

### Sensitivity

`potentially_sensitive` — §2.9's phrase "potentially sensitive" is the only marking made here. §3.15: "Finance, identity, medical, and legal material should be implemented first as safety domains, meaning the system detects and protects them before any cloud or automated placement decision is allowed." — this slice sits inside that sentence, so the conservative direction is the correct one. The handling CLASS is P7's (§8.4) and is not set.

---

## `fin.retirement-account` — Retirement and pension accounts

Records produced by membership of a retirement scheme — member statements, projections, contribution records, transfer paperwork.

**Provenance:** **inference** — extends a design-named domain; the cite supports the extension, not the whole entry

**Cite:** extends §3.11's Finance row "Finance files may use institution, account type, tax year, and record type."; the employer-sponsor role follows §3.8's "The system must separate roles that happen to contain the same entity type"

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `institution` | string | Nest | `validated` | §3.11 Finance field: the scheme administrator or provider |
| `scheme_name` | string | Group Personal Pension Plan | `direct` | §3.13 direct: a document title or labeled field; distinct from the provider because one provider runs many schemes |
| `account_type` | string | defined contribution | `validated` | §3.11 Finance field. The vocabulary is strongly jurisdiction-specific — see the root entry's open question |
| `member_identifier` | string | MBR-40217 | `direct` | §3.13 direct: a labeled form field |
| `employer_sponsor` | string | Halden Bio Ltd | `validated` | §3.8: the sponsor is a distinct role from the provider and from the member. It must not become a folder level on its own — §3.8 "A folder should not become a collection point for everything produced by the same person or organization" |
| `statement_period` | date range | 2025-04-06 to 2026-04-05 | `direct` | a labeled period field |
| `record_type` | string | member statement | `validated` | §3.11 Finance field |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.4, §3.5):

- a retirement-scheme term ('pension' | 'retirement plan' | 'superannuation' | 'scheme member' | 'annual benefit statement' | 'contribution history') together with a provider name matched on a word boundary
- a member-identifier label together with a scheme name in a document title
- a projection term ('projected retirement income' | 'illustration' | 'at your selected retirement age') together with a provider name

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- an employer benefits pack in which the pension section is one part of a mixed document
- a transfer discussion in correspondence with no labeled scheme field anywhere

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10):

- a currency amount
- an age or a retirement year
- an employer name — it also carries a career-domain reading, and §3.8 forbids making an organisation a collector
- the word 'pension' in a filename with no provider or member field beside it

### Work types

`annual member statement`, `projection or illustration`, `contribution record`, `transfer pack`, `nomination of beneficiaries`, `scheme rules`

### Grouping reasons (§4)

- one scheme across its annual statements
- one transfer packet across its discharge forms, illustrations and confirmations

### Template (§5)

`provider → scheme → year`

Time first: **no**

§5.5: "a parent dimension should provide the context required to understand the child". A member statement is meaningless before the scheme is known, and the scheme before the provider

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| fin.investment-brokerage | same valuation shape, same provider in many cases; only a retirement-scheme term separates them | §3.7 "it should require both a minimum score and a minimum margin over the second-best candidate before it fills a facet" |
| career.retirement-records | an employer-sponsored scheme document is also an employment benefit record. The career slice owns the employment relationship; this entry owns the scheme record | §3.8 "The system must separate roles that happen to contain the same entity type" |
| legal.wills-trusts-estates | a nomination of beneficiaries is both a scheme form and an estate-planning instrument | §3.11 "One file may hold facts from more than one domain without losing information" |

### Sensitivity

`potentially_sensitive` — §2.9's phrase "potentially sensitive" is the only marking made here. §3.15: "Finance, identity, medical, and legal material should be implemented first as safety domains, meaning the system detects and protects them before any cloud or automated placement decision is allowed." — this slice sits inside that sentence, so the conservative direction is the correct one. The handling CLASS is P7's (§8.4) and is not set.

---

## `tax.filing` — Tax filing (per year, per jurisdiction, per filing entity)

The return itself and everything the filing entity submitted or received for one tax year in one jurisdiction.

**Provenance:** **inference** — extends a design-named domain; the cite supports the extension, not the whole entry

**Cite:** extends §3.11's Finance row, which names tax year directly: "Finance files may use institution, account type, tax year, and record type."; §8.4 names "identity documents, account statements, tax records, medical information, legal records, credentials" among the corpus

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `tax_year` | string | 2025-26 | `validated` | §3.11 names tax year as a Finance field — the one field in this domain the design supplies. §3.10 governs the extraction: "Date candidates should be identified with explicit regular expressions and then parsed without fuzzy matching" |
| `jurisdiction` | string | United Kingdom | `validated` | the design states no jurisdiction anywhere, so the domain cannot be written without carrying it as a fact. Recognised from a named revenue authority, not inferred from a form's shape |
| `filing_entity` | string | J. Yung | `validated` | §3.8's role discipline: the entity the return is FOR is distinct from the preparer who produced it and from the authority that receives it |
| `filing_role` | string | individual | `validated` | individual, joint, business, trust or estate — the return means something different in each case; the value vocabulary is jurisdiction-specific |
| `return_type` | string | personal income tax return | `validated` | described functionally, never by a jurisdiction's form name — see the open question |
| `filing_status` | string | submitted | `direct` | §3.13 direct: a labeled field or a submission receipt; draft, submitted, amended, assessed |
| `submission_date` | date | 2026-01-14 | `direct` | §3.13 direct: a labeled date field on a receipt or acknowledgement |
| `preparer` | string | Merton & Co | `validated` | §3.8: the preparer is metadata, not a destination dimension — "It should avoid using authorship or creator identity as a destination dimension." |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.4, §3.5):

- a tax-year label ('tax year' | 'year of assessment' | 'fiscal year' | 'income year') together with a return or filing term ('return' | 'declaration' | 'assessment' | 'filed on' | 'submission receipt')
- a named revenue authority matched on a word boundary together with a taxpayer-identifier label and a year label
- an acknowledgement term ('submission receipt' | 'acknowledgement of receipt' | 'reference number') together with a revenue-authority name

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- an accountant's covering letter that discusses the filing without a labeled year field
- a scanned return whose jurisdiction must be read from the layout and language rather than a named authority
- a document that is a draft of a return but is titled only with a client name

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10):

- a bare four-digit year — §3.10 is explicit that file names and documents "frequently contain numbers that look like years but are course identifiers, version numbers, build numbers, ZIP codes, or other unrelated values"
- a currency amount
- a taxpayer-identifier string — its shape is jurisdiction-specific and collides with other reference numbers
- the word 'tax' in a filename: it appears in invoices, payslips, receipts and property documents
- a revenue-authority name alone — it appears in guidance notes, news clippings and unrelated correspondence

### Work types

`return`, `computation`, `submission receipt`, `assessment or notice`, `amendment`, `payment or refund record`, `authority correspondence`

### Grouping reasons (§4)

- one tax year for one filing entity in one jurisdiction — the packet is defined by that triple, not by the year alone
- one amendment cycle across its original return, amended return and revised assessment

### Template (§5)

`filing entity → jurisdiction → tax year → document type`

Time first: **no**

§5.5's ordering rule reads "For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders.", and a tax return looks like the counter-example because its year is constitutive rather than incidental. It is still not the root dimension: the same year exists for every entity and every jurisdiction the user files in, so a year-first tree merges unrelated filings. Placing the year INSIDE entity and jurisdiction satisfies §5.5's other rule, "a parent dimension should provide the context required to understand the child" — a tax year is only interpretable once you know whose filing and whose tax system it belongs to. `time_first` is therefore false, but only just, and a single-entity single-jurisdiction user should be offered the flattened tax-year-first variant; §5.9 requires the interface to show what each split would create.

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| tax.supporting-documents | a document from an adjacent year is the standing hazard: a statement issued in one calendar year reports the previous tax year, and a prior-year return is routinely attached to a current filing. A tax-year packet must not absorb a document carrying a conflicting tax year without evidence — the direct analogue of §4.8's institution rule | §4.8: "an application packet does not silently absorb a document with a conflicting target institution"; §4.9's "A course code alone should not merge different semesters" is the same rule stated for groups |
| biz.bookkeeping | the accounts that feed a business return are bookkeeping output and filing input at once; the accounting period and the tax year frequently differ, and equating them is a silent error | §4.9 "members carry irreconcilable course, institution, project, term, or purpose facts" |
| corp.regulatory-filings | a return is a filing with an authority; the distinguishing signal is a tax-year label, since a regulatory filing carries a filing period instead | §3.7 "it should require both a minimum score and a minimum margin over the second-best candidate before it fills a facet" |

### Sensitivity

`potentially_sensitive` — §2.9's phrase "potentially sensitive" is the only marking made here. §3.15: "Finance, identity, medical, and legal material should be implemented first as safety domains, meaning the system detects and protects them before any cloud or automated placement decision is allowed." — this slice sits inside that sentence, so the conservative direction is the correct one. The handling CLASS is P7's (§8.4) and is not set.

### Open question — Joseph's call, unresolved

> Which jurisdictions' tax vocabularies are in scope at launch, and does the product recognise more than one at a time for one user? Everything concrete about this domain — form names, the shape of a tax year, taxpayer-identifier patterns, what counts as a return — is jurisdiction-specific. This entry is written functionally and carries `jurisdiction` as a fact rather than encoding any country's forms, which keeps it honest but leaves the deterministic recognisers thinner than they could be. A gazetteer of revenue authorities and form names can only be built once the answer is known.

---

## `tax.supporting-documents` — Tax supporting documents

Third-party documents produced for, or gathered to support, a filing — issuer certificates, income summaries, deduction evidence.

**Provenance:** **inference** — extends a design-named domain; the cite supports the extension, not the whole entry

**Cite:** extends §3.11's tax year field "Finance files may use institution, account type, tax year, and record type."; §8.4 names "identity documents, account statements, tax records, medical information, legal records, credentials" among the corpus this product handles

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `tax_year` | string | 2025 | `validated` | §3.11 Finance field; the field that binds the document to a filing |
| `jurisdiction` | string | Canada | `validated` | carried explicitly for the reason given on tax.filing |
| `issuing_institution` | string | Assiniboine Credit Union | `validated` | §3.8: "A finance document may mention an account holder and an issuing bank." — the issuer is a distinct role from the taxpayer |
| `taxpayer` | string | J. Yung | `validated` | §3.8's holder role, kept separate from the issuer |
| `document_category` | string | interest certificate | `validated` | functional categories only — income summary, interest or dividend certificate, withholding certificate, deduction evidence, contribution receipt. Never a jurisdiction's form name |
| `related_filing` | string | 2025 personal return, Canada | `possible` | §3.13 possible: the link to a filing is usually an inference from a matching year and taxpayer, not a stated fact. §3.6 forbids a weak clue becoming an asserted property |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.4, §3.5):

- an issuer tax-statement label ('for tax purposes' | 'tax statement' | 'certificate of interest' | 'statement of income' | 'withholding') together with a tax-year label
- a tax-year label together with an issuing-institution name matched on a word boundary and a taxpayer-identifier label

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- a receipt kept specifically as deduction evidence, where nothing on the document says so and the intent lives only in where the user filed it
- an issuer letter that describes a taxable event in prose with no labeled category

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10):

- a bare year
- an institution name
- a currency amount
- the phrase 'tax' in a filename — §3.7's boundary discipline applies, and a filename token is a weak position by §3.7's "a value in a filename or document title carries more meaning than the same value in a footer"

### Work types

`issuer certificate`, `income summary`, `withholding statement`, `contribution receipt`, `deduction evidence`, `valuation for tax purposes`

### Grouping reasons (§4)

- one tax year for one taxpayer, across every issuer that produced a document for it
- one issuer across the years it has produced certificates

### Template (§5)

`filing entity → tax year → document category`

Time first: **no**

the packet is purpose-defined — §3.9: "The documents are content-incoherent but purpose-coherent." — so it follows the filing's own dimensions rather than the issuers'. §3.8's "A folder should not become a collection point for everything produced by the same person or organization" is why the issuing institution is not the first level

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| tax.filing | the same document is support for the return and part of the return packet; the year conflict rule applies in both directions | §4.8 "an application packet does not silently absorb a document with a conflicting target institution" |
| fin.bank-account | an interest certificate is a banking record first and a tax document second. The design's answer is that it is both: neither domain may strip the other's facts | §3.11 "One file may hold facts from more than one domain without losing information" |
| fin.receipts-expenses | a receipt claimed as a deduction is simultaneously a personal purchase record and a tax document. The distinguishing signal is a claim, which lives in the user's intent and not in the receipt | §3.9 "Purpose may be supported strongly by an existing user-created folder name or explicit language in a form or portal" |
| fin.charitable-giving | a donation receipt that states its deductibility is a giving record and a tax document at once | §3.11 "One file may hold facts from more than one domain without losing information" |

### Sensitivity

`potentially_sensitive` — §2.9's phrase "potentially sensitive" is the only marking made here. §3.15: "Finance, identity, medical, and legal material should be implemented first as safety domains, meaning the system detects and protects them before any cloud or automated placement decision is allowed." — this slice sits inside that sentence, so the conservative direction is the correct one. The handling CLASS is P7's (§8.4) and is not set.

### Open question — Joseph's call, unresolved

> Same jurisdiction question as tax.filing, sharpened: `document_category` is written as a functional vocabulary precisely so that no country's form names are baked in. If Joseph wants recognisers strong enough to name an issuer document on sight, the catalogue needs a per-jurisdiction form gazetteer, and that is a scope decision rather than an authoring one.

---

## `fin.receipts-expenses` — Receipts and personal expenses

Transactional records of individual purchases — receipts, order confirmations, delivery notes, refunds.

**Provenance:** **inference** — extends a design-named domain; the cite supports the extension, not the whole entry

**Cite:** extends §7.3's residual template, which names the material exactly: "Receipts and Confirmations may hold isolated invoices, delivery confirmations, booking records, boarding passes, purchase receipts, event tickets, and similar transactional documents."

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `merchant` | string | Muji | `validated` | §3.8's issuer role. It must not become a destination dimension on its own — §3.8: "A folder should not become a collection point for everything produced by the same person or organization" |
| `purchase_date` | date | 2025-11-03 | `direct` | §3.13 direct: a labeled date field; §3.10's explicit-regex path |
| `order_identifier` | string | ORD-77120491 | `direct` | §3.13 direct: a labeled form field |
| `payment_method` | string | card ****2201 | `direct` | §3.13 direct: a labeled field. §8.4 keeps the raw value local; the field exists for §3.11's "several additional fields used only for search, privacy protection, explanation, or later review" |
| `total_amount` | string | 42.60 GBP | `direct` | §3.13 direct: a labeled total field. Search and explanation only — an amount is never a folder level |
| `item_or_category` | string | office supplies | `llm_supported` | §3.5: reading a category out of line items is language interpretation, so it cannot exceed llm_supported, and §3.6's citation requirement applies |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.4, §3.5):

- a receipt term ('receipt' | 'order confirmation' | 'thank you for your order' | 'subtotal' | 'VAT' | 'sales tax' | 'total paid') together with a merchant name matched on a word boundary
- an order-identifier label together with a labeled purchase date and a labeled total

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- a photographed till receipt where OCR yields a merchant name and little else
- an order confirmation email whose merchant appears only in the sender address

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10):

- a currency amount — the canonical over-firing pattern for this domain
- a merchant name — merchants appear in marketing mail, newsletters and unrelated correspondence
- a date
- a long digit string standing in for an order number

### Work types

`receipt`, `order confirmation`, `delivery note`, `refund or credit note`, `booking confirmation`, `ticket`

### Grouping reasons (§4)

- one purchase across its confirmation, receipt and delivery note
- one refund cycle across the original receipt and the credit note

### Template (§5)

`year → merchant`

Time first: **yes**

the exception to §5.5's usual order. §5.5 prefers subject before time for record domains, but an isolated receipt has no project, function or subject to lead with, and §3.8 forbids making the merchant a collector: "A folder should not become a collection point for everything produced by the same person or organization". Time is the only dimension that both exists and discriminates, which is why §7.3 keeps this material in a flat residual template rather than a deep tree. `time_first` is true here and this is the one entry in the slice where it is.

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| §7.3 residual template 'Receipts and Confirmations' | this domain and that residual template hold the same documents. The difference is not content: §7.2's residual templates are safe broad destinations for files with no reliable deeper association, so a receipt that belongs to an expense report, a warranty or a tax claim leaves the residual template and joins its packet | §7.3: "Receipts and Confirmations may hold isolated invoices, delivery confirmations, booking records, boarding passes, purchase receipts, event tickets, and similar transactional documents." |
| tax.supporting-documents | a receipt claimed as a deduction. The claim is the user's, not the receipt's | §3.9 "Purpose may be supported strongly by an existing user-created folder name or explicit language in a form or portal" |
| biz.expense-report | receipts attached to a claim are content-incoherent with the claim form and purpose-coherent with it | §3.9 "The documents are content-incoherent but purpose-coherent." |
| admin.warranties | the receipt is the proof of purchase a warranty depends on; the same file is both | §3.11 "One file may hold facts from more than one domain without losing information" |
| pers.travel-record | §7.3's own list puts booking records, boarding passes and event tickets in this material, and all three also read as travel records | §7.3: "Receipts and Confirmations may hold isolated invoices, delivery confirmations, booking records, boarding passes, purchase receipts, event tickets, and similar transactional documents." |

### Sensitivity

`potentially_sensitive` — §2.9's phrase "potentially sensitive" is the only marking made here. §3.15: "Finance, identity, medical, and legal material should be implemented first as safety domains, meaning the system detects and protects them before any cloud or automated placement decision is allowed." — this slice sits inside that sentence, so the conservative direction is the correct one. The handling CLASS is P7's (§8.4) and is not set.

---

## `biz.expense-report` — Expense reports and reimbursement claims

A claim submitted by a person to an organisation for costs incurred, with its supporting receipts.

**Provenance:** **proposal** — new here; no design sentence names it

**Cite:** no design sentence names this domain. §3.15 "Other domains remain placeholders until user demand and corpus evidence justify detailed templates." and §5.7 "expand the library as recurring user needs and corpus evidence justify additional coverage" are what permit the addition; the domain itself is new here.

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `claimant` | string | J. Yung | `validated` | §3.8's role discipline: the claimant, the approver and the paying organisation are three roles, not three organisation values |
| `organisation` | string | Halden Bio Ltd | `validated` | the paying entity; kept out of the folder root by §3.8's "A folder should not become a collection point for everything produced by the same person or organization" |
| `claim_period` | date range | 2025-10-01 to 2025-10-31 | `direct` | a labeled period field |
| `report_identifier` | string | EXP-2025-1188 | `direct` | §3.13 direct: a labeled form field |
| `approval_status` | string | approved | `direct` | §3.13 direct: a labeled status field or an approval stamp |
| `cost_centre_or_project` | string | PVA/RDP | `validated` | the charge code; frequently the only link between a claim and a project |
| `currency` | string | USD | `direct` | §3.11's search-and-explanation allowance |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.4, §3.5):

- an expense-claim term ('expense report' | 'expense claim' | 'reimbursement' | 'per diem' | 'mileage claim') together with a claimant or approver name field
- a report-identifier label together with a labeled claim period and a labeled approval status

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- a spreadsheet of costs with no claim header, where only the column semantics identify it as a claim
- an email thread approving a claim in prose

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10):

- a currency amount
- an employer name
- a date range
- the word 'expenses' in a filename

### Work types

`claim form`, `attached receipts`, `approval record`, `reimbursement advice`, `policy exception note`

### Grouping reasons (§4)

- one claim across its form, its receipts and its approval — a purpose-coherent packet
- one claimant across one reporting period

### Template (§5)

`organisation → year → claim`

Time first: **no**

§5.5: "a parent dimension should provide the context required to understand the child". A claim identifier is meaningless before the paying organisation is known. §5.4's Career row is the nearest design-sanctioned precedent for an organisation-led order: "a Career template may define company → role or recruiting cycle → document type"

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| fin.receipts-expenses | the receipts are members of both; the claim's purpose does not erase their standing as purchase records | §3.9 "The documents are content-incoherent but purpose-coherent." |
| career.employment-contract | a claim is an artefact of an employment relationship. The career slice owns the relationship; this entry owns the claim | §3.8 "The system must separate roles that happen to contain the same entity type" |
| biz.bookkeeping | on the employer's side the same claim is a ledger entry with a cost centre | §3.8 "The system must separate roles that happen to contain the same entity type" |

### Sensitivity

`potentially_sensitive` — §2.9's phrase "potentially sensitive" is the only marking made here. §3.15: "Finance, identity, medical, and legal material should be implemented first as safety domains, meaning the system detects and protects them before any cloud or automated placement decision is allowed." — this slice sits inside that sentence, so the conservative direction is the correct one. The handling CLASS is P7's (§8.4) and is not set.

---

## `biz.invoice-issued` — Invoices issued (receivable)

Invoices the user or the user's entity raised against a customer, and the payment records that close them.

**Provenance:** **inference** — extends a design-named domain; the cite supports the extension, not the whole entry

**Cite:** §2.4 names the document type among those whose information sits in tables: "resumes, forms, applications, invoices, and administrative documents often place their most useful information in cells"; §3.8 supplies the role pair as "our_firm and client"

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `counterparty` | string | Arden Labs | `validated` | §3.8 names this exact role pair: "our_firm and client". The customer is the `client` role |
| `our_entity` | string | Yung Consulting Ltd | `validated` | §3.8's `our_firm` role. Holding both roles is what makes direction recoverable |
| `invoice_number` | string | INV-2025-0148 | `direct` | §3.13 direct: a labeled form field |
| `issue_date` | date | 2025-11-30 | `direct` | §3.13 direct: a labeled date field |
| `due_date` | date | 2025-12-30 | `direct` | §3.13 direct: a labeled date field |
| `direction` | string | issued | `validated` | derived from which party occupies the `our_firm` role. It is a rule conclusion, not a document field, and it is the single fact that separates this domain from its mirror |
| `payment_status` | string | paid | `direct` | §3.13 direct: a labeled status field or a stamped remittance |
| `currency` | string | GBP | `direct` | §3.11's search-and-explanation allowance |
| `engagement_reference` | string | MSA-ARD-2024 | `validated` | the contract or purchase order the invoice bills against, where the invoice names it |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.4, §3.5):

- an invoice-number label ('invoice no' | 'invoice number' | 'invoice #' | 'facture' | 'rechnung' | 'factura') together with a 'bill to' or 'sold to' block naming a counterparty
- an invoice-number label together with a 'from' or letterhead block whose entity matches the user's own entity gazetteer — this pairing, not the invoice pattern alone, is what establishes direction
- a remittance term ('remittance advice' | 'payment received' | 'paid in full') together with a matching invoice-number label

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- an invoice with no explicit bill-to block, where the parties must be read from a letterhead and a body paragraph
- a scanned invoice whose direction is legible only from context the OCR flattens

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10):

- a currency amount
- a long digit string standing in for an invoice number
- a company name — the same company appears as customer, supplier and merely cited party
- the word 'invoice' in a filename: it is present on both sides of the relationship and carries no direction

### Work types

`invoice`, `credit note`, `statement of account`, `remittance advice`, `dunning letter`, `timesheet or backup schedule`

### Grouping reasons (§4)

- one customer across one billing year
- one engagement across its invoices, credit notes and remittances

### Template (§5)

`counterparty → year → document type`

Time first: **no**

§3.8 forbids authorship as a dimension but the counterparty is not authorship — it is the client role, the analogue of §5.4's target institution and of "authored_by and target_school". §5.4's Career row establishes the precedent that an organisation may lead a branch: "a Career template may define company → role or recruiting cycle → document type". §5.5 then keeps the year second: "For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders."

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| biz.invoice-received | the mirror image, and the hardest collision in this slice. The two domains hold documents that are byte-similar and semantically opposite. Direction is recoverable only from which party sits in the `our_firm` role, so a corpus with no entity gazetteer cannot separate them by rule at all | §3.8: "The system must separate roles that happen to contain the same entity type", "A consulting document may mention the author’s firm and the client organization" |
| biz.bookkeeping | every issued invoice is also a ledger entry | §3.11 "One file may hold facts from more than one domain without losing information" |
| legal.contracts | an invoice referencing an engagement is evidence of the contract's performance but is not the contract | §4.8 forbids a model inventing "a date, project, purpose, or membership that the dossier does not support" |
| biz.procurement-po | from the supplier's side the customer's purchase order arrives in the same folder as the invoice raised against it | §3.9 "The documents are content-incoherent but purpose-coherent." |

### Sensitivity

`potentially_sensitive` — §2.9's phrase "potentially sensitive" is the only marking made here. §3.15: "Finance, identity, medical, and legal material should be implemented first as safety domains, meaning the system detects and protects them before any cloud or automated placement decision is allowed." — this slice sits inside that sentence, so the conservative direction is the correct one. The handling CLASS is P7's (§8.4) and is not set.

---

## `biz.invoice-received` — Invoices received (payable)

Invoices and bills a supplier raised against the user or the user's entity, and the payments that settle them.

**Provenance:** **inference** — extends a design-named domain; the cite supports the extension, not the whole entry

**Cite:** §2.4 names the document type: "resumes, forms, applications, invoices, and administrative documents often place their most useful information in cells"; §3.8 supplies the role pair as "our_firm and client"

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `counterparty` | string | Rowan Print Services | `validated` | §3.8's supplier-side counterparty; the `client` role reversed |
| `our_entity` | string | Yung Consulting Ltd | `validated` | §3.8's `our_firm` role — the bill-to party here |
| `invoice_number` | string | R-2025-8841 | `direct` | §3.13 direct: a labeled form field |
| `issue_date` | date | 2025-11-12 | `direct` | §3.13 direct: a labeled date field |
| `due_date` | date | 2025-12-12 | `direct` | §3.13 direct: a labeled date field |
| `direction` | string | received | `validated` | the mirror of the issued case; derived from which party occupies the bill-to role |
| `payment_status` | string | outstanding | `direct` | §3.13 direct: a labeled status field |
| `purchase_order_reference` | string | PO-4471 | `validated` | the order the bill matches, where the invoice names it |
| `currency` | string | GBP | `direct` | §3.11's search-and-explanation allowance |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.4, §3.5):

- an invoice-number label together with a 'bill to' block whose entity matches the user's own entity gazetteer
- a supplier letterhead or 'from' block naming a counterparty, together with an invoice-number label and a payment-terms term ('payment terms' | 'due on receipt' | 'payable within')
- a purchase-order-reference label on an invoice, together with a matching order in the user's own procurement records

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- a utility or service bill with an unusual layout and no bill-to label
- a supplier statement listing several invoices where the direction must be read from the covering text

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10):

- a currency amount
- a long digit string
- a supplier name
- the word 'invoice' or 'bill' in a filename — direction is not in the word

### Work types

`supplier invoice`, `utility bill`, `credit note`, `supplier statement`, `payment confirmation`, `dispute correspondence`

### Grouping reasons (§4)

- one supplier across one billing year
- one purchase across its order, delivery note and invoice

### Template (§5)

`counterparty → year → document type`

Time first: **no**

mirror of biz.invoice-issued and for the same reasons: §5.4's "a Career template may define company → role or recruiting cycle → document type" licenses the organisation-led order and §5.5's "For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders." keeps the year second

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| biz.invoice-issued | the mirror; see that entry. A tree that puts both under one Invoices branch will interleave money owed with money due, which is the failure this split exists to prevent | §3.8 "The system must separate roles that happen to contain the same entity type" |
| admin.subscriptions-recurring | a recurring service bill is both a payable invoice and a subscription record; the distinguishing signal is a renewal or plan term, not the invoice shape | §3.7 "it should require both a minimum score and a minimum margin over the second-best candidate before it fills a facet" |
| fin.receipts-expenses | for an individual with no entity, a bill received and a receipt are the same category and the `our_entity` role is empty | §7.3 "Receipts and Confirmations may hold isolated invoices, delivery confirmations, booking records, boarding passes, purchase receipts, event tickets, and similar transactional documents." |
| biz.procurement-po | the three-way match — order, delivery, invoice — is one purpose-coherent packet split across two domains | §3.9 "The documents are content-incoherent but purpose-coherent." |

### Sensitivity

`potentially_sensitive` — §2.9's phrase "potentially sensitive" is the only marking made here. §3.15: "Finance, identity, medical, and legal material should be implemented first as safety domains, meaning the system detects and protects them before any cloud or automated placement decision is allowed." — this slice sits inside that sentence, so the conservative direction is the correct one. The handling CLASS is P7's (§8.4) and is not set.

---

## `biz.bookkeeping` — Small-business bookkeeping and accounts

The periodic accounting record of a business entity — ledgers, trial balances, management and statutory accounts.

**Provenance:** **proposal** — new here; no design sentence names it

**Cite:** no design sentence names this domain. §3.15 "Other domains remain placeholders until user demand and corpus evidence justify detailed templates." and §5.7 "expand the library as recurring user needs and corpus evidence justify additional coverage" are what permit the addition; the domain itself is new here.

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `business_entity` | string | Yung Consulting Ltd | `validated` | the entity the books belong to; distinct from the accountant who prepared them, per §3.8 |
| `accounting_period` | date range | 2025-01-01 to 2025-12-31 | `direct` | §3.13 direct: a labeled period field. Deliberately distinct from tax year, which frequently differs |
| `report_type` | string | profit and loss | `validated` | profit and loss, balance sheet, trial balance, general ledger, aged debtors or creditors, cash flow |
| `accounting_basis` | string | accrual | `llm_supported` | §3.5: usually stated in a notes paragraph rather than a labeled field, so it needs interpretation and cannot exceed llm_supported |
| `preparer` | string | Merton & Co | `validated` | §3.8: metadata, not a destination dimension — "It should avoid using authorship or creator identity as a destination dimension." |
| `source_system` | string | Xero | `direct` | §3.13 direct: an export header or document footer; useful for §3.11's "several additional fields used only for search, privacy protection, explanation, or later review" |
| `currency` | string | GBP | `direct` | §3.11's search-and-explanation allowance |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.4, §3.5):

- a financial-statement title ('profit and loss' | 'income statement' | 'balance sheet' | 'trial balance' | 'general ledger' | 'aged debtors') together with a labeled period and an entity name
- an accounting-export header ('account code' AND 'debit' AND 'credit') together with an entity name matched on a word boundary

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- a spreadsheet that is plainly a ledger but carries no title row
- an accountant's working file whose entity must be read from a covering note

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10):

- a currency amount
- a company name
- a date range
- a column header such as 'debit' on its own — accounting words appear in templates, tutorials and unrelated spreadsheets

### Work types

`profit and loss`, `balance sheet`, `trial balance`, `general ledger export`, `aged debtors or creditors`, `management accounts`, `statutory accounts`, `bank reconciliation`

### Grouping reasons (§4)

- one entity across one accounting period
- one year-end close across its draft, adjusted and final accounts — a version family

### Template (§5)

`business entity → accounting period → report type`

Time first: **no**

§5.5: "a parent dimension should provide the context required to understand the child". A trial balance is only interpretable once the entity and the period are known. §5.5's "For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders." argues for entity before period, which is what this order does

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| tax.filing | the accounts feed the return, and the accounting period and the tax year frequently differ. Treating them as one dimension silently misfiles a year of work | §4.9 "members carry irreconcilable course, institution, project, term, or purpose facts" |
| corp.regulatory-filings | statutory accounts are simultaneously a bookkeeping product and a document filed with a registry | §3.11 "One file may hold facts from more than one domain without losing information" |
| fin.bank-account | for a sole trader the personal account IS the business account; the split is a user decision with no document-level evidence | §4.9 "members carry irreconcilable course, institution, project, term, or purpose facts" |
| biz.invoice-issued | every invoice on either side is also a ledger entry here | §3.11 "One file may hold facts from more than one domain without losing information" |
| biz.invoice-received | every invoice on either side is also a ledger entry here | §3.11 "One file may hold facts from more than one domain without losing information" |

### Sensitivity

`potentially_sensitive` — §2.9's phrase "potentially sensitive" is the only marking made here. §3.15: "Finance, identity, medical, and legal material should be implemented first as safety domains, meaning the system detects and protects them before any cloud or automated placement decision is allowed." — this slice sits inside that sentence, so the conservative direction is the correct one. The handling CLASS is P7's (§8.4) and is not set.

---

## `biz.payroll-employer` — Payroll (employer side)

The payroll run an employer produces — registers, remittances and employer filings, as distinct from any one employee's payslip.

**Provenance:** **proposal** — new here; no design sentence names it

**Cite:** no design sentence names this domain. §3.15 "Other domains remain placeholders until user demand and corpus evidence justify detailed templates." and §5.7 "expand the library as recurring user needs and corpus evidence justify additional coverage" are what permit the addition; the domain itself is new here.

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `employer_entity` | string | Halden Bio Ltd | `validated` | §3.8: the employer role, distinct from the employee role and from the payroll bureau |
| `pay_period` | date range | 2025-11-01 to 2025-11-30 | `direct` | §3.13 direct: a labeled period field |
| `payroll_run_identifier` | string | RUN-2025-11 | `direct` | §3.13 direct: a labeled form field |
| `jurisdiction` | string | Ireland | `validated` | payroll obligations and remittance vocabulary are jurisdiction-defined; carried as a fact rather than assumed |
| `document_type` | string | payroll register | `validated` | register, remittance, employer return, year-end summary, pension or benefit schedule |
| `payroll_provider` | string | Bright Pay | `direct` | §3.13 direct: an export header; §3.8 keeps it out of the folder dimensions |
| `employee_count_scope` | string | all employees | `possible` | §3.13 possible: whether a run covers the whole payroll or a subset is usually inferable rather than stated |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.4, §3.5):

- a payroll term ('payroll register' | 'payroll journal' | 'gross to net' | 'employer contribution' | 'payroll run') together with an employer name matched on a word boundary and a labeled pay period
- a remittance term ('employer remittance' | 'payroll tax remittance' | 'contribution submission') together with a named authority and a period label

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- a spreadsheet export whose payroll nature is visible only in the column semantics
- a benefits schedule that mixes payroll and HR content

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10):

- a currency amount
- an employer name
- a person's name — a payroll register is full of them and none identifies the domain
- a period label

### Work types

`payroll register`, `payroll journal`, `remittance record`, `employer return`, `year-end summary`, `starter or leaver record`

### Grouping reasons (§4)

- one employer across one payroll year
- one run across its register, journal and remittance

### Template (§5)

`employer entity → payroll year → period`

Time first: **no**

§5.5: "a parent dimension should provide the context required to understand the child". A pay period is meaningless before the employer is known. Payroll is the one sub-domain here where periods genuinely nest inside a year

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| career.payroll | the career slice owns the employee side. A payslip is an employment record about one person; this entry is the employer's run covering everyone. They look alike, they are not the same domain, and the register carries a document-level signal the payslip does not: multiple employees | §3.8 "The system must separate roles that happen to contain the same entity type" |
| biz.bookkeeping | the payroll journal is a ledger posting as well as a payroll artefact | §3.11 "One file may hold facts from more than one domain without losing information" |
| tax.filing | employer returns are filings; the distinguishing signal is a pay period rather than a tax year | §3.7 "it should require both a minimum score and a minimum margin over the second-best candidate before it fills a facet" |

### Sensitivity

`potentially_sensitive` — §2.9's phrase "potentially sensitive" is the only marking made here. §3.15: "Finance, identity, medical, and legal material should be implemented first as safety domains, meaning the system detects and protects them before any cloud or automated placement decision is allowed." — this slice sits inside that sentence, so the conservative direction is the correct one. The handling CLASS is P7's (§8.4) and is not set. A payroll register additionally concerns people other than the user, which §8.4's boundary discussion covers and P7 must weigh.

---

## `corp.business-formation` — Business formation and corporate records

The constitutional record of a legal entity — formation documents, governing instruments, registers and board decisions.

**Provenance:** **proposal** — new here; no design sentence names it

**Cite:** no design sentence names this domain. §3.15 "Other domains remain placeholders until user demand and corpus evidence justify detailed templates." and §5.7 "expand the library as recurring user needs and corpus evidence justify additional coverage" are what permit the addition; the domain itself is new here.

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `entity_name` | string | Halden Bio Ltd | `validated` | the entity the record constitutes; §3.8 keeps it distinct from the registry and from any officer |
| `entity_type` | string | private company limited by shares | `validated` | written functionally, because the value vocabulary is entirely jurisdiction-defined — see the open question |
| `jurisdiction_of_incorporation` | string | England and Wales | `validated` | constitutive for this domain; an entity exists only in a jurisdiction |
| `registry_identifier` | string | 12894471 | `direct` | §3.13 direct: a labeled form field on a registry document |
| `formation_date` | date | 2021-03-08 | `direct` | §3.13 direct: a labeled date field on a certificate |
| `document_type` | string | articles of association | `validated` | certificate, constitution or articles, shareholder or operating agreement, register, board minute, resolution |
| `registered_office` | string | 44 Gray's Inn Road, London | `direct` | §3.13 direct: a labeled address field |
| `officer` | string | J. Yung, director | `validated` | §3.8's role discipline: an officer is a role on the entity, not an author |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.4, §3.5):

- an entity-suffix token matched on a word boundary ('Ltd' | 'LLC' | 'Inc' | 'GmbH' | 'Pty Ltd' | 'S.A.' | 'B.V.' — a jurisdiction-specific set) together with a formation term ('certificate of incorporation' | 'articles of association' | 'operating agreement' | 'registered office' | 'company number')
- a named registry together with a registry-identifier label and an entity name
- a governance term ('board minute' | 'written resolution' | 'quorum' | 'resolved that') together with an entity name

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- a constitution or shareholders' agreement whose entity appears only in a recital paragraph
- board papers that discuss a decision without a resolution header

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10):

- a company name — §3.7's boundary rule is the defence, and a company appears as counterparty, employer, supplier and cited party far more often than as the subject of its own constitution
- a registry number — its shape is jurisdiction-specific and collides with other reference numbers
- an entity suffix alone: 'Ltd' appears in every letterhead the user has ever received
- a date

### Work types

`certificate of incorporation`, `articles or constitution`, `shareholder or operating agreement`, `statutory register`, `board minute`, `written resolution`, `officer appointment or resignation`

### Grouping reasons (§4)

- one entity across its constitutional documents
- one board meeting across its papers, minute and resolutions

### Template (§5)

`entity → document type → year`

Time first: **no**

§5.5: "a parent dimension should provide the context required to understand the child". A resolution is only meaningful once the entity is known, and constitutional documents are consulted by kind rather than by year — §5.5's "For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders." applies with unusual force here

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| corp.shareholder-captable | a shareholders' agreement and a share register are constitutional records and cap-table records at once | §3.11 "One file may hold facts from more than one domain without losing information" |
| corp.regulatory-filings | the same document exists as a signed instrument and as a filed copy; the filing carries a submission reference the instrument does not | §3.7 "it should require both a minimum score and a minimum margin over the second-best candidate before it fills a facet" |
| legal.contracts | an operating or shareholders' agreement is a contract by form and a constitutional document by function | §3.11 "One file may hold facts from more than one domain without losing information" |

### Sensitivity

`potentially_sensitive` — §2.9's phrase "potentially sensitive" is the only marking made here. §3.15: "Finance, identity, medical, and legal material should be implemented first as safety domains, meaning the system detects and protects them before any cloud or automated placement decision is allowed." — this slice sits inside that sentence, so the conservative direction is the correct one. The handling CLASS is P7's (§8.4) and is not set.

### Open question — Joseph's call, unresolved

> Entity types, registry identifier shapes and the names of constitutional documents are wholly jurisdiction-defined, and unlike tax there is no functional vocabulary that covers them cleanly — a private company limited by shares, an LLC and a GmbH are not the same object described differently. This entry names entity type and jurisdiction as facts and refuses to pick a country's vocabulary. Which registries the product recognises is Joseph's call and gates any real gazetteer.

---

## `corp.shareholder-captable` — Shareholder and cap-table records

Who owns what in an entity — share registers, certificates, grants, vesting records and cap-table snapshots.

**Provenance:** **proposal** — new here; no design sentence names it

**Cite:** no design sentence names this domain. §3.15 "Other domains remain placeholders until user demand and corpus evidence justify detailed templates." and §5.7 "expand the library as recurring user needs and corpus evidence justify additional coverage" are what permit the addition; the domain itself is new here.

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `issuing_entity` | string | Halden Bio Ltd | `validated` | §3.8: the issuer role, distinct from the holder role |
| `holder` | string | Arden Ventures LP | `validated` | §3.8's counterpart role; the two must not collapse into one organisation field |
| `security_class` | string | Series A preferred | `validated` | the class the instrument concerns |
| `instrument_type` | string | share certificate | `validated` | register, certificate, option grant, warrant, convertible instrument, cap-table snapshot |
| `issue_date` | date | 2024-06-11 | `direct` | §3.13 direct: a labeled date field |
| `authorising_reference` | string | Board resolution 2024-06-04 | `validated` | the resolution or consent that authorised the issue, where the instrument names it |
| `snapshot_date` | date | 2025-12-31 | `direct` | §3.13 direct: a labeled date on a cap-table export; a cap table is only true as of a date |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.4, §3.5):

- an equity term ('ordinary shares' | 'preferred stock' | 'share certificate' | 'option grant' | 'vesting commencement' | 'cap table' | 'fully diluted') together with an issuing entity name matched on a word boundary
- a register term ('register of members' | 'stock ledger') together with an entity name and a holder column

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- a spreadsheet that is plainly a cap table but has no title and identifies the entity only in a tab name
- a grant letter whose class must be read from prose

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10):

- a percentage — an ownership percentage is the classic over-firing pattern here and appears in every commercial document
- a share count
- a company name
- the word 'shares' — it appears in brokerage records, news and unrelated correspondence

### Work types

`register of members`, `share certificate`, `option grant`, `warrant`, `convertible instrument`, `cap-table snapshot`, `shareholder consent`

### Grouping reasons (§4)

- one entity across its ownership record
- one financing event across the instruments it issued

### Template (§5)

`entity → security class → year`

Time first: **no**

§5.5: "a parent dimension should provide the context required to understand the child". A certificate is meaningless before the entity is known, and a class before the entity. §3.8's "A folder should not become a collection point for everything produced by the same person or organization" is why the holder is not a level — a folder per shareholder is exactly the collector pattern the design forbids

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| corp.fundraising-investor | a financing round produces both a subscription agreement and the instruments it issues; the round is the purpose-coherent packet and the instruments are the constitutional consequence | §3.9 "The documents are content-incoherent but purpose-coherent." |
| career.equity-compensation | an employee option grant is compensation as much as it is a cap-table instrument. The career slice owns the employee's own copy; this entry owns the issuer's record | §3.8 "The system must separate roles that happen to contain the same entity type" |
| corp.business-formation | the register of members sits in both | §3.11 "One file may hold facts from more than one domain without losing information" |
| fin.investment-brokerage | privately held shares are cap-table material; publicly held ones are brokerage material. Same word, different domain | §3.7 "it should require both a minimum score and a minimum margin over the second-best candidate before it fills a facet" |

### Sensitivity

`potentially_sensitive` — §2.9's phrase "potentially sensitive" is the only marking made here. §3.15: "Finance, identity, medical, and legal material should be implemented first as safety domains, meaning the system detects and protects them before any cloud or automated placement decision is allowed." — this slice sits inside that sentence, so the conservative direction is the correct one. The handling CLASS is P7's (§8.4) and is not set.

---

## `corp.fundraising-investor` — Fundraising and investor materials

Material produced to raise money into an entity and to report back to those who provided it.

**Provenance:** **proposal** — new here; no design sentence names it

**Cite:** no design sentence names this domain. §3.15 "Other domains remain placeholders until user demand and corpus evidence justify detailed templates." and §5.7 "expand the library as recurring user needs and corpus evidence justify additional coverage" are what permit the addition; the domain itself is new here.

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `entity` | string | Halden Bio Ltd | `validated` | the entity raising; §3.8 keeps it distinct from the investor |
| `round_label` | string | Series A | `validated` | the round or stage the material belongs to; the closest thing this domain has to a project dimension |
| `investor` | string | Arden Ventures LP | `validated` | §3.8's counterparty role. Never a folder level on its own — "A folder should not become a collection point for everything produced by the same person or organization" |
| `document_type` | string | term sheet | `validated` | term sheet, convertible or subscription instrument, diligence pack, pitch deck, investor update, closing set |
| `document_date` | date | 2024-05-02 | `direct` | §3.13 direct: a labeled date field or a document title |
| `round_status` | string | closed | `llm_supported` | §3.5: whether a round closed is read from prose and correspondence, not a labeled field, so it cannot exceed llm_supported |
| `reporting_period` | date range | 2025-07-01 to 2025-09-30 | `direct` | for investor updates: a labeled period field |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.4, §3.5):

- a fundraising term ('term sheet' | 'subscription agreement' | 'convertible note' | 'SAFE' | 'pre-money' | 'post-money' | 'investor update') together with an entity name matched on a word boundary
- a round label ('seed' | 'Series A' | 'bridge') together with an entity name AND a fundraising term — the round label alone is far too weak
- a diligence term ('data room' | 'due diligence request list') together with an entity name

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- a pitch deck with no round label, where the fundraising purpose is legible only from the ask slide
- an investor update written as an ordinary email

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10):

- a currency amount
- a percentage
- a round label such as 'seed' or 'Series A' — 'seed' in particular collides with unrelated vocabulary and §3.7's boundary rule does not save it
- an investor or fund name

### Work types

`pitch deck`, `term sheet`, `subscription or convertible instrument`, `diligence pack`, `closing set`, `investor update`, `cap-table model`

### Grouping reasons (§4)

- one round across its deck, term sheet, diligence pack and closing set — a purpose-coherent packet
- one investor across the updates sent to them

### Template (§5)

`entity → round → document type`

Time first: **no**

§5.5: "a parent dimension should provide the context required to understand the child". A term sheet is meaningless before the round, and the round before the entity. The round is this domain's project dimension, which is what §5.5's "For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders." asks for

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| corp.shareholder-captable | the closing set issues the instruments; the round is the packet and the instruments are the record | §3.9 "The documents are content-incoherent but purpose-coherent." |
| legal.contracts | a subscription agreement is a contract by form; the distinguishing signal is a round label and a fundraising term | §3.7 "it should require both a minimum score and a minimum margin over the second-best candidate before it fills a facet" |
| fin.grants-received | non-dilutive funding arrives as an award rather than an investment; a user who treats both as fundraising will file them together | §4.9 "members carry irreconcilable course, institution, project, term, or purpose facts" |

### Sensitivity

`potentially_sensitive` — §2.9's phrase "potentially sensitive" is the only marking made here. §3.15: "Finance, identity, medical, and legal material should be implemented first as safety domains, meaning the system detects and protects them before any cloud or automated placement decision is allowed." — this slice sits inside that sentence, so the conservative direction is the correct one. The handling CLASS is P7's (§8.4) and is not set.

---

## `fin.loan-mortgage` — Loans and mortgages

Borrowing arrangements and their lifecycle — applications, agreements, schedules, statements and redemption.

**Provenance:** **inference** — extends a design-named domain; the cite supports the extension, not the whole entry

**Cite:** extends §3.11's Finance row "Finance files may use institution, account type, tax year, and record type." — a loan is an account type held at an institution; §3.8's "A finance document may mention an account holder and an issuing bank." supplies the lender and borrower split

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `lender` | string | Nationwide | `validated` | §3.8's issuing-institution role |
| `borrower` | string | J. Yung | `validated` | §3.8's holder role; on a joint loan there is more than one |
| `loan_identifier` | string | MTG-88213004 | `direct` | §3.13 direct: a labeled form field |
| `product_type` | string | residential mortgage | `validated` | mortgage, personal loan, student loan, business loan, overdraft facility |
| `origination_date` | date | 2022-09-30 | `direct` | §3.13 direct: a labeled date field |
| `secured_asset` | string | 18 Bellfield Road | `validated` | the property or asset the loan is secured on, where the document names it; absent for unsecured borrowing |
| `jurisdiction` | string | United Kingdom | `validated` | consumer-credit vocabulary and disclosure documents are jurisdiction-defined |
| `record_type` | string | annual statement | `validated` | §3.11's Finance record type field |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.4, §3.5):

- a loan term ('loan agreement' | 'mortgage deed' | 'promissory note' | 'amortisation schedule' | 'redemption statement' | 'facility letter') together with a lender name matched on a word boundary
- a loan-identifier label together with a labeled repayment or balance field and a lender name
- a security term ('charge' | 'secured on' | 'collateral') together with a property or asset description and a lender name

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- an offer pack whose product type must be read from prose
- correspondence about arrears where the loan is identified only by a customer reference

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10):

- a currency amount
- an interest percentage
- a bank name
- a long digit string

### Work types

`application pack`, `offer or facility letter`, `agreement or deed`, `amortisation schedule`, `annual statement`, `arrears notice`, `redemption statement`

### Grouping reasons (§4)

- one loan across its whole life
- one application packet across the evidence gathered for it — a purpose-coherent packet

### Template (§5)

`lender → loan → year`

Time first: **no**

§5.5: "a parent dimension should provide the context required to understand the child". A statement is meaningless before the loan is known, and the loan before the lender

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| fin.bank-account | the statements, payslips and identity documents assembled for a loan application remain what they are; the packet's claim is purpose, and §4.8's rule against silent absorption applies to them exactly as it does to an application packet | §4.8: "an application packet does not silently absorb a document with a conflicting target institution" |
| legal.contracts | a loan agreement is a contract; the distinguishing signal is a lender role and a loan identifier | §3.7 "it should require both a minimum score and a minimum margin over the second-best candidate before it fills a facet" |
| legal.debt-collection | a defaulted loan migrates into collection and the same identifier appears in both | §3.11 "One file may hold facts from more than one domain without losing information" |
| fin.credit | a revolving facility sits between the two; the distinguishing signal is an amortisation schedule | §3.7 "it should require both a minimum score and a minimum margin over the second-best candidate before it fills a facet" |

### Sensitivity

`potentially_sensitive` — §2.9's phrase "potentially sensitive" is the only marking made here. §3.15: "Finance, identity, medical, and legal material should be implemented first as safety domains, meaning the system detects and protects them before any cloud or automated placement decision is allowed." — this slice sits inside that sentence, so the conservative direction is the correct one. The handling CLASS is P7's (§8.4) and is not set.

---

## `fin.credit` — Credit accounts and credit files

Revolving credit and the records that describe a person's or entity's creditworthiness.

**Provenance:** **inference** — extends a design-named domain; the cite supports the extension, not the whole entry

**Cite:** extends §3.11's Finance row "Finance files may use institution, account type, tax year, and record type."; §8.4 names "identity documents, account statements, tax records, medical information, legal records, credentials" among the corpus

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `issuer_or_bureau` | string | Experian | `validated` | §3.8's issuing-institution role, covering both card issuers and reporting bureaux |
| `account_holder` | string | J. Yung | `validated` | §3.8's holder role |
| `product_type` | string | credit card | `validated` | §3.11's account type field, specialised |
| `account_identifier` | string | ****3390 | `direct` | §3.13 direct: a labeled and usually masked form field |
| `statement_period` | date range | 2025-10-15 to 2025-11-14 | `direct` | §3.13 direct: a labeled period field |
| `report_date` | date | 2026-01-08 | `direct` | for credit files: the date the file was pulled, which is the only date that makes it interpretable |
| `record_type` | string | statement | `validated` | §3.11's Finance record type field |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.4, §3.5):

- a credit-product term ('credit card statement' | 'minimum payment' | 'credit limit' | 'available credit' | 'cash advance') together with an issuer name matched on a word boundary
- a credit-file term ('credit report' | 'credit file' | 'credit reference agency' | 'search footprint') together with a named bureau and a labeled report date

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- a card statement whose issuer appears only in a logo region after OCR
- correspondence about a limit change with no labeled account field

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10):

- a currency amount
- a masked card number — the mask pattern is shared with receipts and payroll files
- a credit score value
- an issuer name

### Work types

`statement`, `credit agreement`, `limit-change notice`, `credit report`, `dispute correspondence`, `closure confirmation`

### Grouping reasons (§4)

- one card account across one statement year
- one credit-file pull across the report and the disputes raised on it

### Template (§5)

`issuer → account → year`

Time first: **no**

§5.5: "a parent dimension should provide the context required to understand the child", matching the deposit-account order for the same reason

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| fin.bank-account | issuer, statement shape and masked identifier are all shared; only the credit-product vocabulary separates them | §3.7 "it should require both a minimum score and a minimum margin over the second-best candidate before it fills a facet" |
| fin.receipts-expenses | a card statement enumerates purchases that also exist as individual receipts | §3.11 "One file may hold facts from more than one domain without losing information" |
| legal.debt-collection | an unpaid card account becomes a collection matter under the same identifier | §3.11 "One file may hold facts from more than one domain without losing information" |

### Sensitivity

`potentially_sensitive` — §2.9's phrase "potentially sensitive" is the only marking made here. §3.15: "Finance, identity, medical, and legal material should be implemented first as safety domains, meaning the system detects and protects them before any cloud or automated placement decision is allowed." — this slice sits inside that sentence, so the conservative direction is the correct one. The handling CLASS is P7's (§8.4) and is not set.

---

## `fin.insurance` — Insurance policies and claims

Cover arranged with an insurer, the documents that evidence it, and the claims made under it.

**Provenance:** **proposal** — new here; no design sentence names it

**Cite:** no design sentence names this domain. §3.15 "Other domains remain placeholders until user demand and corpus evidence justify detailed templates." and §5.7 "expand the library as recurring user needs and corpus evidence justify additional coverage" are what permit the addition; the domain itself is new here.

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `insurer` | string | Aviva | `validated` | §3.8's issuing-institution role |
| `policyholder` | string | J. Yung | `validated` | §3.8's holder role; distinct from the insured person or item where they differ |
| `policy_number` | string | POL-4471-22 | `direct` | §3.13 direct: a labeled form field |
| `cover_type` | string | buildings and contents | `validated` | written functionally; cover names are market- and jurisdiction-specific |
| `policy_period` | date range | 2025-06-01 to 2026-05-31 | `direct` | §3.13 direct: a labeled period field |
| `insured_subject` | string | 18 Bellfield Road | `validated` | the property, vehicle, person or activity covered; distinct from the policyholder |
| `claim_reference` | string | CLM-99120 | `direct` | §3.13 direct: a labeled form field; present only on claim documents |
| `claim_status` | string | settled | `direct` | §3.13 direct: a labeled status field |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.4, §3.5):

- a policy-number label ('policy no' | 'policy number' | 'certificate of insurance') together with an insurer name matched on a word boundary and a cover term ('cover' | 'coverage' | 'premium' | 'excess' | 'deductible' | 'sum insured')
- a claim term ('claim reference' | 'claim number' | 'loss adjuster' | 'notification of loss') together with an insurer name and a policy-number label
- a schedule term ('policy schedule' | 'statement of fact' | 'insured perils') together with a labeled policy period

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- a renewal quotation that never labels its cover type
- claim correspondence that identifies the policy only by the insured address

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10):

- a long alphanumeric identifier
- a currency amount
- an insurer name in a payee line — insurers appear as payees, sponsors and cited organisations
- a date range

### Work types

`policy schedule`, `certificate of insurance`, `policy wording`, `renewal notice`, `claim notification`, `loss adjuster report`, `settlement letter`

### Grouping reasons (§4)

- one policy across its renewals — a version family in §3.11's sense
- one claim across its notification, evidence and settlement

### Template (§5)

`cover type → insurer → policy year`

Time first: **no**

cover type leads rather than insurer because users change insurer and keep the cover: §5.5 asks for "For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders." and the subject of an insurance file is what is covered, not who underwrote it that year. §3.8's "A folder should not become a collection point for everything produced by the same person or organization" points the same way.

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| med.insurance-claim-eob | a health claim carries clinical content. §3.15 names medical as its own safety domain; the clinical material is not this entry's to hold and must not be pulled into a finance branch | §3.15: "Finance, identity, medical, and legal material should be implemented first as safety domains, meaning the system detects and protects them before any cloud or automated placement decision is allowed." |
| pers.travel-record | travel insurance is a travel record and an insurance record at once | §3.11 "One file may hold facts from more than one domain without losing information" |
| legal.litigation-dispute | a contested claim becomes a dispute and acquires a matter and a forum | §3.11 "One file may hold facts from more than one domain without losing information" |
| admin.warranties | an extended warranty is sold as a product and behaves like a policy; the distinguishing signal is an insurer and a policy number rather than a manufacturer and a serial number | §3.7 "it should require both a minimum score and a minimum margin over the second-best candidate before it fills a facet" |

### Sensitivity

`potentially_sensitive` — §2.9's phrase "potentially sensitive" is the only marking made here. §3.15: "Finance, identity, medical, and legal material should be implemented first as safety domains, meaning the system detects and protects them before any cloud or automated placement decision is allowed." — this slice sits inside that sentence, so the conservative direction is the correct one. The handling CLASS is P7's (§8.4) and is not set.

---

## `legal.contracts` — Contracts and agreements (general)

Bilateral written agreements and their lifecycle — drafts, negotiation, execution, amendment — where no more specific contract domain applies.

**Provenance:** **inference** — extends a design-named domain; the cite supports the extension, not the whole entry

**Cite:** extends §3.15's "Finance, identity, medical, and legal material should be implemented first as safety domains, meaning the system detects and protects them before any cloud or automated placement decision is allowed." and §5.7's list of areas the template library should cover, which names "financial records, travel, legal matters"

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `counterparty` | string | Arden Labs | `validated` | §3.8 names this exact role pair for professional documents: "A consulting document may mention the author’s firm and the client organization", and "our_firm and client" |
| `our_entity` | string | Yung Consulting Ltd | `validated` | §3.8's `our_firm` role; without both roles the agreement's sides are indistinguishable |
| `agreement_type` | string | master services agreement | `validated` | NDA, services agreement, supply agreement, licence, settlement, assignment |
| `effective_date` | date | 2024-04-01 | `direct` | §3.13 direct: a labeled date field or an execution block |
| `term_end` | date | 2027-03-31 | `validated` | read from a term clause; a rule can find it beside a term heading but it is rarely a labeled field |
| `governing_law` | string | England and Wales | `validated` | read from a governing-law clause, which is a standard heading and therefore rule-findable |
| `execution_status` | string | executed | `validated` | draft, under negotiation, executed. Determined by the presence of a completed signature block, not asserted from a filename |
| `agreement_reference` | string | MSA-ARD-2024 | `direct` | §3.13 direct: a labeled form field where the agreement carries one |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.4, §3.5):

- a contract clause heading ('governing law' | 'entire agreement' | 'term and termination' | 'limitation of liability' | 'confidentiality') together with a named party block ('between' AND 'and', or a parties recital)
- an execution term ('in witness whereof' | 'signed for and on behalf of' | 'executed as a deed') together with two party names
- an amendment term ('amendment no' | 'variation agreement' | 'deed of variation') together with a reference to a parent agreement

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- an unlabeled document whose contractual nature is legible only from its obligations
- a redline whose parties appear only in tracked changes
- a summary or term-sheet email that stands in for an agreement

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10):

- a company name — the single most over-firing pattern for this domain, since companies appear as counterparties, cited third parties, employers and addressees
- a date
- the word 'agreement' in a filename — it names templates, guidance notes and policy documents as often as executed contracts
- a signature-looking image region with no party block

### Work types

`draft`, `redline or comparison`, `executed copy`, `signature page`, `amendment or variation`, `schedule or exhibit`, `termination notice`, `NDA`

### Grouping reasons (§4)

- one agreement across its drafts and its executed copy — §3.11's universal version family made concrete
- one counterparty across the agreements held with them

### Template (§5)

`counterparty → agreement → version`

Time first: **no**

the counterparty is not authorship. §3.8 forbids the collector pattern — "A folder should not become a collection point for everything produced by the same person or organization" — but a counterparty is the role §3.8 itself names as `client`, the direct analogue of §5.4's target institution, and §5.4's Career row establishes that an organisation may lead a branch: "a Career template may define company → role or recruiting cycle → document type". Version last, because §5.5's "a parent dimension should provide the context required to understand the child" makes a draft meaningless before the agreement it drafts.

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| career.employment-contract | an employment contract is a contract by form and an employment record by function. The career slice owns it; this entry must not absorb it, and the distinguishing signal is an employee role rather than a counterparty role | §3.8 "The system must separate roles that happen to contain the same entity type" |
| legal.lease | a lease is a contract. The specialisation rule is that the more specific domain wins where its own fields populate — a property address and a landlord/tenant role pair | §3.7 "it should require both a minimum score and a minimum margin over the second-best candidate before it fills a facet" |
| fin.loan-mortgage | a loan agreement is a contract with a lender role | §3.7 "it should require both a minimum score and a minimum margin over the second-best candidate before it fills a facet" |
| biz.vendor-management | the master services agreement is the anchor document of a vendor relationship and sits in both | §3.11 "One file may hold facts from more than one domain without losing information" |
| legal.ip-registration | an assignment or licence of a registered right is a contract and a chain-of-title document | §3.11 "One file may hold facts from more than one domain without losing information" |

### Sensitivity

`potentially_sensitive` — §2.9's phrase "potentially sensitive" is the only marking made here. §3.15: "Finance, identity, medical, and legal material should be implemented first as safety domains, meaning the system detects and protects them before any cloud or automated placement decision is allowed." — this slice sits inside that sentence, so the conservative direction is the correct one. The handling CLASS is P7's (§8.4) and is not set.

---

## `legal.lease` — Leases and tenancies

Agreements granting occupation of property, and the records generated over their term.

**Provenance:** **proposal** — new here; no design sentence names it

**Cite:** no design sentence names this domain. §3.15 "Other domains remain placeholders until user demand and corpus evidence justify detailed templates." and §5.7 "expand the library as recurring user needs and corpus evidence justify additional coverage" are what permit the addition; the domain itself is new here.

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `property_address` | string | 18 Bellfield Road, Flat 2 | `direct` | §3.13 direct: a labeled premises field. The subject of the domain — leases are consulted by property, not by counterparty |
| `landlord` | string | Bellfield Estates Ltd | `validated` | §3.8's role discipline; the grantor role |
| `tenant` | string | J. Yung | `validated` | the grantee role; both must be held or the lease's sides collapse |
| `lease_term` | date range | 2025-07-01 to 2026-06-30 | `direct` | §3.13 direct: labeled commencement and expiry fields |
| `lease_type` | string | residential assured shorthold | `validated` | written functionally; tenancy categories are strongly jurisdiction-defined |
| `jurisdiction` | string | England and Wales | `validated` | landlord and tenant law is local law; carried as a fact |
| `deposit_reference` | string | TDS-8841207 | `direct` | §3.13 direct: a labeled field where a deposit scheme reference exists |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.4, §3.5):

- a tenancy term ('lease agreement' | 'tenancy agreement' | 'landlord' | 'tenant' | 'demised premises' | 'rent commencement' | 'quiet enjoyment') together with a property address
- a property address together with a labeled term-commencement date and a rent-frequency term ('per calendar month' | 'per annum')
- an inventory or condition term ('schedule of condition' | 'check-in report' | 'inventory') together with a property address

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- a licence or lodging arrangement that avoids tenancy vocabulary entirely
- correspondence about a tenancy that names the property only by a flat number

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10):

- an address — addresses appear on every letter the user has ever received, and §3.7's positional rule is the only thing that makes one meaningful
- a currency amount
- a person's name
- the word 'lease' in a filename — it also names vehicle and equipment finance

### Work types

`lease or tenancy agreement`, `renewal or extension`, `inventory and condition schedule`, `rent statement`, `notice to quit or vacate`, `deposit protection record`, `correspondence`

### Grouping reasons (§4)

- one property across one tenancy
- one tenancy across its agreement, inventory, renewals and notices

### Template (§5)

`property → tenancy → document type`

Time first: **no**

§5.5: "a parent dimension should provide the context required to understand the child". A renewal is meaningless before the tenancy, and the tenancy before the property. Property leads rather than landlord because landlords change and the property does not — §3.8's "A folder should not become a collection point for everything produced by the same person or organization" points the same way

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| legal.contracts | a lease is a contract; this entry claims it only when a property address and a landlord/tenant role pair both populate | §3.7 "it should require both a minimum score and a minimum margin over the second-best candidate before it fills a facet" |
| fin.receipts-expenses | rent receipts and deposit returns are transactional records as well as tenancy records | §3.11 "One file may hold facts from more than one domain without losing information" |
| pers.home-tenure | utilities, insurance and maintenance for the same property gather around the address rather than the lease; the personal slice owns the property as a life area | §3.8 "The system must separate roles that happen to contain the same entity type" |
| fin.loan-mortgage | for an owner-landlord the same address carries a mortgage and a lease at once, in opposite roles | §3.8 "The system must separate roles that happen to contain the same entity type" |

### Sensitivity

`potentially_sensitive` — §2.9's phrase "potentially sensitive" is the only marking made here. §3.15: "Finance, identity, medical, and legal material should be implemented first as safety domains, meaning the system detects and protects them before any cloud or automated placement decision is allowed." — this slice sits inside that sentence, so the conservative direction is the correct one. The handling CLASS is P7's (§8.4) and is not set.

---

## `legal.litigation-dispute` — Litigation and disputes

A contested matter and the working file built around it, from pre-action correspondence to resolution.

**Provenance:** **proposal** — new here; no design sentence names it

**Cite:** no design sentence names this domain. §3.15 "Other domains remain placeholders until user demand and corpus evidence justify detailed templates." and §5.7 "expand the library as recurring user needs and corpus evidence justify additional coverage" are what permit the addition; the domain itself is new here.

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `matter_name` | string | Yung v Bellfield Estates | `validated` | the user's or the adviser's name for the matter; the dimension the working file organises around |
| `initiating_party` | string | J. Yung | `validated` | §3.8's role discipline. The label for this role is jurisdiction-specific — claimant, plaintiff, petitioner, applicant — so the field is named by function |
| `responding_party` | string | Bellfield Estates Ltd | `validated` | the mirror role; respondent, defendant |
| `forum` | string | County Court at Central London | `validated` | the court, tribunal or arbitral body; absent while a dispute is pre-action |
| `case_number` | string | K1QZ4471 | `direct` | §3.13 direct: a labeled form field on issued documents |
| `matter_stage` | string | pre-action | `llm_supported` | §3.5: stage is read from what the correspondence is doing, not from a labeled field, so it cannot exceed llm_supported |
| `counsel_or_adviser` | string | Merton Legal LLP | `validated` | §3.8: an adviser is metadata — "It should avoid using authorship or creator identity as a destination dimension." |
| `jurisdiction` | string | England and Wales | `validated` | procedure, party labels and document names are all local |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.4, §3.5):

- a case-caption pattern (two party names separated by 'v' or 'v.' on a title line) together with a forum name matched on a word boundary AND a case-number label — all three, because the caption pattern alone is worthless
- a pre-action term ('letter before action' | 'without prejudice' | 'pre-action protocol' | 'notice of dispute') together with two named parties
- a procedural term ('statement of case' | 'particulars of claim' | 'defence' | 'witness statement' | 'disclosure' | 'skeleton argument') together with a matter or case reference

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- a dispute conducted entirely in correspondence with no procedural vocabulary
- an adviser's advice note that discusses a matter without naming a forum

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10):

- the token 'v' or 'v.' — it appears in filenames, version markers, sports fixtures and comparisons, and is the worst over-firing pattern in this slice
- a case-number-shaped string
- a person's or company's name
- the phrase 'without prejudice' in isolation — it appears in ordinary commercial negotiation

### Work types

`pre-action correspondence`, `statement of case`, `witness statement`, `disclosure bundle`, `expert report`, `order or judgment`, `settlement agreement`, `costs schedule`

### Grouping reasons (§4)

- one matter across everything generated for it — the archetypal purpose-coherent packet
- one hearing across its bundle, skeleton and resulting order

### Template (§5)

`matter → stage → document type`

Time first: **no**

§5.5: "a parent dimension should provide the context required to understand the child". A witness statement is meaningless before the matter. Matter is this domain's project dimension, which is exactly what §5.5's "For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders." asks a record domain to lead with

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| legal.court-records | the working file and the court's own issued record overlap on orders and judgments. The distinguishing signal is issuance — a sealed or stamped document belongs to the court record as well | §3.11 "One file may hold facts from more than one domain without losing information" |
| legal.contracts | the disputed agreement is an exhibit in the matter and remains a contract in its own right; a matter folder must not swallow the contract archive | §4.8 "an application packet does not silently absorb a document with a conflicting target institution" — the same rule against silent absorption |
| legal.debt-collection | a collection escalating to proceedings crosses from one domain into the other under the same reference | §3.11 "One file may hold facts from more than one domain without losing information" |
| fin.insurance | a contested insurance claim is simultaneously a claim record and a dispute | §3.11 "One file may hold facts from more than one domain without losing information" |

### Sensitivity

`potentially_sensitive` — §2.9's phrase "potentially sensitive" is the only marking made here. §3.15: "Finance, identity, medical, and legal material should be implemented first as safety domains, meaning the system detects and protects them before any cloud or automated placement decision is allowed." — this slice sits inside that sentence, so the conservative direction is the correct one. The handling CLASS is P7's (§8.4) and is not set.

---

## `legal.wills-trusts-estates` — Wills, trusts and estates

Instruments disposing of property on death or into trust, and the administration of an estate.

**Provenance:** **proposal** — new here; no design sentence names it

**Cite:** no design sentence names this domain. §3.15 "Other domains remain placeholders until user demand and corpus evidence justify detailed templates." and §5.7 "expand the library as recurring user needs and corpus evidence justify additional coverage" are what permit the addition; the domain itself is new here.

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `instrument_type` | string | will | `validated` | will, codicil, trust deed, letter of wishes, deed of variation, grant of representation |
| `testator_or_settlor` | string | M. Yung | `validated` | §3.8's role discipline: the person disposing |
| `executor_or_trustee` | string | J. Yung | `validated` | the administering role; distinct from both the disposing party and the beneficiaries |
| `beneficiary` | string | J. Yung | `validated` | the receiving role. Never a folder level — §3.8: "A folder should not become a collection point for everything produced by the same person or organization" |
| `execution_date` | date | 2019-11-02 | `direct` | §3.13 direct: a labeled date field in an attestation block |
| `estate_reference` | string | Estate of M. Yung | `validated` | the estate the administration concerns |
| `jurisdiction` | string | Scotland | `validated` | succession law and the vocabulary of administration differ sharply even within one country — see the open question |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.4, §3.5):

- a testamentary term ('last will and testament' | 'testator' | 'executor' | 'revoke all former wills') together with a named individual and an attestation block ('signed by' AND 'in the presence of')
- a trust term ('trust deed' | 'settlor' | 'trustee' | 'beneficial interest' | 'letter of wishes') together with a named settlor and a trust name
- an administration term ('grant of probate' | 'letters of administration' | 'confirmation' | 'estate account' | 'inheritance tax account') together with a deceased person's name

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- a draft will circulated for comment with no attestation block
- correspondence about an estate that identifies it only by a family name

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10):

- a person's name
- a date
- an attestation-shaped signature region
- the word 'estate' — it names property agents, developments and addresses far more often than deceased estates

### Work types

`will or codicil`, `trust deed`, `letter of wishes`, `grant of representation`, `estate accounts`, `asset schedule`, `deed of variation`, `adviser correspondence`

### Grouping reasons (§4)

- one estate across its administration
- one instrument across its drafts and its executed copy

### Template (§5)

`estate or trust → instrument → version`

Time first: **no**

§5.5: "a parent dimension should provide the context required to understand the child". A codicil is meaningless before the will it amends, and the will before the estate it concerns

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| legal.power-of-attorney | both are personal instruments about the same person, executed together and stored together, but a power of attorney operates during life and a will after death — an important distinction to lose | §3.8 "The system must separate roles that happen to contain the same entity type" |
| legal.notarised-documents | these instruments are routinely witnessed or notarised; notarisation is a property of the document, not a competing domain | §3.14 keeps facts separate from the tree, so an attestation is a fact and not a folder |
| tax.filing | an estate is a filing entity in its own right and produces returns under its own reference | §3.11 "One file may hold facts from more than one domain without losing information" |
| pers.identity-document | a death certificate is an identity document and an estate document at once | §7.3: "Protected Records may represent sensitive isolated material such as passport scans, medical documents, account statements, visas, legal forms, or credentials" |

### Sensitivity

`potentially_sensitive` — §2.9's phrase "potentially sensitive" is the only marking made here. §3.15: "Finance, identity, medical, and legal material should be implemented first as safety domains, meaning the system detects and protects them before any cloud or automated placement decision is allowed." — this slice sits inside that sentence, so the conservative direction is the correct one. The handling CLASS is P7's (§8.4) and is not set.

### Open question — Joseph's call, unresolved

> Succession vocabulary is not merely translated between jurisdictions — probate, confirmation, letters of administration and civil-law equivalents are different procedures producing different documents, and some jurisdictions have forced heirship rules with no common-law analogue. This entry names the instrument functionally and carries `jurisdiction`, which is as far as neutrality reaches. Whether the product attempts this domain at all before the jurisdiction question is settled is Joseph's call.

---

## `legal.power-of-attorney` — Powers of attorney and delegated authority

Instruments by which one person authorises another to act for them, and the records of their registration and use.

**Provenance:** **proposal** — new here; no design sentence names it

**Cite:** no design sentence names this domain. §3.15 "Other domains remain placeholders until user demand and corpus evidence justify detailed templates." and §5.7 "expand the library as recurring user needs and corpus evidence justify additional coverage" are what permit the addition; the domain itself is new here.

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `donor` | string | M. Yung | `validated` | §3.8's role discipline: the person granting authority. Called donor, principal or grantor depending on jurisdiction |
| `attorney_or_agent` | string | J. Yung | `validated` | the person receiving authority |
| `authority_scope` | string | property and financial affairs | `validated` | financial, health and welfare, general or limited. The categories are jurisdiction-defined and the field is named by function |
| `effective_date` | date | 2020-02-14 | `direct` | §3.13 direct: a labeled date field or an attestation block |
| `registration_reference` | string | OPG-7741208 | `direct` | §3.13 direct: a labeled field where a registering authority exists |
| `instrument_status` | string | registered | `direct` | §3.13 direct: a labeled status field or a registration stamp |
| `jurisdiction` | string | England and Wales | `validated` | these instruments are creatures of local statute |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.4, §3.5):

- a delegation term ('power of attorney' | 'attorney-in-fact' | 'lasting power of attorney' | 'enduring power of attorney' | 'mandate to act') together with two named parties and an attestation block
- a registration term ('registered by' | 'certificate provider' | 'office of the public guardian' — jurisdiction-specific) together with an instrument reference
- a revocation term ('deed of revocation' | 'revoke the power') together with a reference to a parent instrument

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- an authority granted inside a broader agreement rather than as a standalone instrument
- correspondence relying on an authority without naming the instrument

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10):

- a person's name
- the word 'authority' — it names regulators, councils and permissions far more often
- an attestation-shaped region
- a date

### Work types

`instrument`, `registration confirmation`, `certificate of capacity`, `revocation deed`, `third-party acceptance record`, `adviser correspondence`

### Grouping reasons (§4)

- one donor across the instruments granted and revoked
- one instrument across its execution, registration and acceptance by institutions

### Template (§5)

`donor → authority scope → version`

Time first: **no**

the donor leads because the instrument is about them, not because they authored it — §3.8's "It should avoid using authorship or creator identity as a destination dimension." is about creator identity, and a donor is the subject role. §5.5's "a parent dimension should provide the context required to understand the child" makes a registration meaningless before the instrument it registers.

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| legal.wills-trusts-estates | executed in the same appointment, stored in the same envelope, and operating at opposite ends of a life | §3.8 "The system must separate roles that happen to contain the same entity type" |
| med.advance-directive | a health-and-welfare authority or advance directive touches clinical decision-making; §3.15 gives medical its own safety domain and this entry does not claim that content | §3.15: "Finance, identity, medical, and legal material should be implemented first as safety domains, meaning the system detects and protects them before any cloud or automated placement decision is allowed." |
| legal.notarised-documents | notarisation and certificate-provider steps are attestations on this instrument, not a separate filing | §3.14 keeps facts separate from the tree |
| corp.business-formation | a corporate authority to act — a delegation of signing power — reads identically but concerns an entity rather than a person | §3.8 "The system must separate roles that happen to contain the same entity type" |

### Sensitivity

`potentially_sensitive` — §2.9's phrase "potentially sensitive" is the only marking made here. §3.15: "Finance, identity, medical, and legal material should be implemented first as safety domains, meaning the system detects and protects them before any cloud or automated placement decision is allowed." — this slice sits inside that sentence, so the conservative direction is the correct one. The handling CLASS is P7's (§8.4) and is not set.

---

## `corp.regulatory-filings` — Regulatory filings and returns

Documents an entity or person is required to submit to an authority or registry, and the authority's responses.

**Provenance:** **proposal** — new here; no design sentence names it

**Cite:** no design sentence names this domain. §3.15 "Other domains remain placeholders until user demand and corpus evidence justify detailed templates." and §5.7 "expand the library as recurring user needs and corpus evidence justify additional coverage" are what permit the addition; the domain itself is new here.

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `filing_entity` | string | Halden Bio Ltd | `validated` | §3.8's role discipline: the entity that files, distinct from the authority that receives |
| `authority` | string | Companies House | `validated` | the regulator or registry; the receiving role |
| `filing_type` | string | annual confirmation statement | `validated` | written functionally; the names are registry-specific |
| `filing_period` | date range | 2025-01-01 to 2025-12-31 | `direct` | §3.13 direct: a labeled period field. Deliberately not tax year — that field belongs to tax.filing and equating them misfiles both |
| `submission_date` | date | 2026-01-19 | `direct` | §3.13 direct: a labeled date field on a receipt |
| `submission_reference` | string | SUB-2026-004471 | `direct` | §3.13 direct: a labeled form field; the fact that distinguishes a filed copy from the underlying instrument |
| `jurisdiction` | string | United Kingdom | `validated` | a regulator exists only within a jurisdiction |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.4, §3.5):

- a named authority or registry matched on a word boundary together with a filing term ('annual return' | 'confirmation statement' | 'filed with' | 'submission receipt' | 'notice of filing') and a labeled period
- a submission-reference label together with a named authority and a labeled submission date
- a regulatory-correspondence term ('notice of' | 'direction' | 'penalty notice' | 'request for information') together with a named authority and an entity name

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- a filing prepared but not submitted, where only prose distinguishes a draft from a filed copy
- authority correspondence whose subject filing must be inferred from context

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10):

- an agency or authority name — authorities are cited in guidance, news and unrelated correspondence
- a reference number
- a year
- the word 'return' — it names delivery returns, tax returns and product returns

### Work types

`prepared filing`, `filed copy`, `submission receipt`, `authority notice or decision`, `penalty or enforcement notice`, `request for information`, `correction filing`

### Grouping reasons (§4)

- one entity across one filing year with one authority
- one filing across its preparation, submission and acknowledgement

### Template (§5)

`filing entity → authority → filing period`

Time first: **no**

§5.5: "a parent dimension should provide the context required to understand the child". A period is meaningless before the authority whose calendar it belongs to, and the authority before the entity that files. §5.5's "For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders." keeps the period last

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| tax.filing | a tax return is a filing with a revenue authority. The distinguishing signal is a tax-year label; a regulatory filing carries a filing period instead, and the two frequently differ | §4.9 "members carry irreconcilable course, institution, project, term, or purpose facts" |
| corp.business-formation | the filed copy and the signed instrument are the same document with different provenance; only a submission reference separates them | §3.7 "it should require both a minimum score and a minimum margin over the second-best candidate before it fills a facet" |
| corp.compliance-audit | a regulator's information request is a filing artefact and a compliance artefact | §3.11 "One file may hold facts from more than one domain without losing information" |
| admin.licences-permits | a licence application is filed with an authority and produces a licence; the filing and the resulting permission are different documents | §3.8 "The system must separate roles that happen to contain the same entity type" |

### Sensitivity

`potentially_sensitive` — §2.9's phrase "potentially sensitive" is the only marking made here. §3.15: "Finance, identity, medical, and legal material should be implemented first as safety domains, meaning the system detects and protects them before any cloud or automated placement decision is allowed." — this slice sits inside that sentence, so the conservative direction is the correct one. The handling CLASS is P7's (§8.4) and is not set.

---

## `corp.compliance-audit` — Compliance and audit

Evidence that an entity meets an external standard or internal control obligation, and the reviews that test it.

**Provenance:** **proposal** — new here; no design sentence names it

**Cite:** no design sentence names this domain. §3.15 "Other domains remain placeholders until user demand and corpus evidence justify detailed templates." and §5.7 "expand the library as recurring user needs and corpus evidence justify additional coverage" are what permit the addition; the domain itself is new here.

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `subject_entity` | string | Halden Bio Ltd | `validated` | §3.8: the entity being examined, distinct from the examiner |
| `auditor_or_assessor` | string | Merton Assurance | `validated` | the examining role. §3.8 keeps it out of the folder dimensions — "A folder should not become a collection point for everything produced by the same person or organization" |
| `framework_or_standard` | string | ISO 27001 | `validated` | the standard, regime or policy the review tests against; the subject dimension of this domain |
| `audit_period` | date range | 2025-01-01 to 2025-12-31 | `direct` | §3.13 direct: a labeled period field |
| `report_type` | string | management letter | `validated` | audit report, management letter, finding or non-conformity, corrective action, certificate, evidence pack |
| `certificate_reference` | string | CERT-27001-8841 | `direct` | §3.13 direct: a labeled form field on a certificate |
| `finding_status` | string | closed | `direct` | §3.13 direct: a labeled status field in a findings register |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.4, §3.5):

- an audit term ('audit report' | 'management letter' | 'non-conformity' | 'corrective action' | 'control objective' | 'statement of applicability') together with a named auditor and a labeled period
- a named standard matched on a word boundary together with a certification term ('certificate of registration' | 'scope of certification' | 'surveillance audit')
- a compliance-register term ('risk register' | 'control matrix' | 'evidence reference') together with an entity name and a period

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- an internal review memo that never names a framework
- an evidence pack whose contents identify the control only by an internal code

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10):

- a standard number on its own — a bare numeric standard reference collides with every other identifier in the corpus
- the token 'SOC' — it collides with ordinary words and §3.7's boundary rule alone does not rescue it
- a company name
- the word 'audit' — it names financial audits, internal reviews and website audits alike

### Work types

`audit report`, `management letter`, `findings register`, `corrective action record`, `certificate`, `evidence pack`, `policy document`

### Grouping reasons (§4)

- one framework across one audit cycle
- one finding across its raising, remediation and closure

### Template (§5)

`framework → audit cycle → document type`

Time first: **no**

§5.5: "a parent dimension should provide the context required to understand the child". A finding is meaningless before the cycle, and the cycle before the framework. Framework is this domain's subject dimension, which §5.5's "For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders." asks to lead

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| corp.regulatory-filings | an audit performed because a regulator requires it produces documents that are both | §3.11 "One file may hold facts from more than one domain without losing information" |
| biz.bookkeeping | a statutory financial audit is an accounts artefact and an audit artefact; the distinguishing signal is an auditor role | §3.7 "it should require both a minimum score and a minimum margin over the second-best candidate before it fills a facet" |
| career.continuing-education | individual compliance training certificates are career records about a person, not entity-level compliance evidence. The career slice owns them | §3.8 "The system must separate roles that happen to contain the same entity type" |
| biz.vendor-management | supplier due-diligence questionnaires are compliance evidence and vendor-lifecycle records at once | §3.11 "One file may hold facts from more than one domain without losing information" |

### Sensitivity

`potentially_sensitive` — §2.9's phrase "potentially sensitive" is the only marking made here. §3.15: "Finance, identity, medical, and legal material should be implemented first as safety domains, meaning the system detects and protects them before any cloud or automated placement decision is allowed." — this slice sits inside that sentence, so the conservative direction is the correct one. The handling CLASS is P7's (§8.4) and is not set.

---

## `admin.licences-permits` — Licences, permits and registrations

Permissions granted by an authority to a person, entity, premises, vehicle or activity, and their renewal record.

**Provenance:** **proposal** — new here; no design sentence names it

**Cite:** no design sentence names this domain. §3.15 "Other domains remain placeholders until user demand and corpus evidence justify detailed templates." and §5.7 "expand the library as recurring user needs and corpus evidence justify additional coverage" are what permit the addition; the domain itself is new here.

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `issuing_authority` | string | Transport for London | `validated` | §3.8's issuing role |
| `holder` | string | J. Yung | `validated` | §3.8's holder role |
| `licence_type` | string | private hire operator licence | `validated` | written functionally; permission regimes are wholly local |
| `licence_number` | string | PHO-4471-22 | `direct` | §3.13 direct: a labeled form field |
| `issue_date` | date | 2024-08-01 | `direct` | §3.13 direct: a labeled date field |
| `expiry_date` | date | 2029-07-31 | `direct` | §3.13 direct: a labeled date field. Recorded as a fact about the document; the catalogue states no policy about acting on it |
| `licensed_subject` | string | 18 Bellfield Road | `validated` | the premises, vehicle, person or activity permitted; distinct from the holder |
| `jurisdiction` | string | United Kingdom | `validated` | a permission exists only where an authority grants it |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.4, §3.5):

- a permission term ('licence' | 'license' | 'permit' | 'certificate of registration' | 'authorisation') together with a named issuing authority matched on a word boundary and a labeled holder
- a licence-number label together with labeled issue and expiry dates and an authority name
- a renewal term ('renewal notice' | 'application to renew' | 'valid until') together with a licence-number label

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- a permission granted by letter with no licence number
- a scanned card whose authority is legible only from a logo

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10):

- an identifier string
- an expiry-looking date — §3.10's warning applies: numbers that look like years frequently are not
- an authority name
- the word 'licence' — it names software licences and content licences at least as often

### Work types

`licence or permit document`, `application`, `renewal notice`, `conditions schedule`, `inspection report`, `variation or surrender`

### Grouping reasons (§4)

- one permission across its issue, renewals and variations
- one licensed subject across the permissions attached to it

### Template (§5)

`licensed subject → licence type → year`

Time first: **no**

§5.5: "a parent dimension should provide the context required to understand the child". A renewal is meaningless before the permission, and the permission before what it permits. Subject leads rather than authority because authorities are reorganised and the licensed thing is not

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| pers.identity-document | a driving licence is an identity document before it is a permission, and §7.3's Protected Records template names that material: "Protected Records may represent sensitive isolated material such as passport scans, medical documents, account statements, visas, legal forms, or credentials". This entry does not claim identity documents | §4.9: "Rare but sensitive files such as passports, visas, and legal documents may be surfaced as protected records" |
| corp.regulatory-filings | the application is a filing and the licence is its outcome; they are different documents with different fields | §3.8 "The system must separate roles that happen to contain the same entity type" |
| legal.ip-registration | a trademark registration is a registration but not a permission; the distinguishing signal is a rights registry rather than a licensing authority | §3.7 "it should require both a minimum score and a minimum margin over the second-best candidate before it fills a facet" |
| legal.contracts | a software or content licence is a contract and shares the word; nothing else about it matches this domain | §3.7 "It should use word-boundary matching rather than substring matching." |

### Sensitivity

`potentially_sensitive` — §2.9's phrase "potentially sensitive" is the only marking made here. §3.15: "Finance, identity, medical, and legal material should be implemented first as safety domains, meaning the system detects and protects them before any cloud or automated placement decision is allowed." — this slice sits inside that sentence, so the conservative direction is the correct one. The handling CLASS is P7's (§8.4) and is not set.

---

## `legal.ip-registration` — Intellectual property registrations

Registrable rights and the record of obtaining and maintaining them — applications, grants, renewals and assignments.

**Provenance:** **proposal** — new here; no design sentence names it

**Cite:** no design sentence names this domain. §3.15 "Other domains remain placeholders until user demand and corpus evidence justify detailed templates." and §5.7 "expand the library as recurring user needs and corpus evidence justify additional coverage" are what permit the addition; the domain itself is new here.

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `rights_holder` | string | Halden Bio Ltd | `validated` | §3.8: the applicant or proprietor role, distinct from the inventor or author and from the registry |
| `registry` | string | EUIPO | `validated` | the granting office; the issuing role |
| `right_type` | string | trademark | `validated` | patent, trademark, registered design, plant variety, registered copyright where one exists |
| `application_number` | string | EM018994471 | `direct` | §3.13 direct: a labeled form field |
| `registration_number` | string | 018994471 | `direct` | §3.13 direct: a labeled form field, distinct from the application number and issued later |
| `filing_date` | date | 2024-02-19 | `direct` | §3.13 direct: a labeled date field |
| `priority_date` | date | 2023-08-30 | `direct` | §3.13 direct: a labeled date field; the fact that makes the family coherent |
| `territory` | string | European Union | `validated` | a right exists per territory, and one invention becomes many registrations |
| `status` | string | registered | `direct` | §3.13 direct: a labeled status field on a registry document |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.4, §3.5):

- a registry term ('patent application' | 'trademark application' | 'registered design' | 'notice of allowance' | 'office action' | 'priority date') together with a named office matched on a word boundary and an application-number label
- an application-number label together with a labeled filing date and a named applicant
- a maintenance term ('renewal fee' | 'annuity' | 'maintenance fee') together with a registration-number label

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- an invention disclosure or draft specification with no registry involvement yet
- an attorney letter that identifies the case only by an internal docket reference

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10):

- a long digit string — application and registration numbers are indistinguishable by shape from every other reference in the corpus
- an office name
- a product or brand name
- a date

### Work types

`application`, `specification or drawings`, `office action`, `response`, `grant or registration certificate`, `renewal record`, `assignment`, `opposition record`

### Grouping reasons (§4)

- one right across its prosecution history
- one priority family across the territories it was filed in

### Template (§5)

`right → territory → document type`

Time first: **no**

§5.5: "a parent dimension should provide the context required to understand the child". An office action is meaningless before the right it concerns. Territory second because one right becomes many national registrations and each has its own file

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| res.patent-disclosure | an invention disclosure, a draft specification and the paper describing the same work are research artefacts; §3.11 gives Research its own fields and that slice owns the project-linked material | §3.11 "One file may hold facts from more than one domain without losing information" |
| legal.contracts | assignments and licences of a registered right are contracts and chain-of-title documents at once | §3.11 "One file may hold facts from more than one domain without losing information" |
| legal.litigation-dispute | an opposition or infringement action is a dispute with a forum, not a prosecution step | §3.7 "it should require both a minimum score and a minimum margin over the second-best candidate before it fills a facet" |
| admin.licences-permits | both are registrations from an office, and neither is the other | §3.7 "it should require both a minimum score and a minimum margin over the second-best candidate before it fills a facet" |

### Sensitivity

`potentially_sensitive` — §2.9's phrase "potentially sensitive" is the only marking made here. §3.15: "Finance, identity, medical, and legal material should be implemented first as safety domains, meaning the system detects and protects them before any cloud or automated placement decision is allowed." — this slice sits inside that sentence, so the conservative direction is the correct one. The handling CLASS is P7's (§8.4) and is not set. Unpublished applications and invention disclosures are confidential until publication, which is why this entry is not marked none despite granted rights being public record.

---

## `admin.immigration` — Immigration and residence paperwork

Applications for permission to enter, remain, work or naturalise, and the decisions and documents that result.

**Provenance:** **inference** — extends a design-named domain; the cite supports the extension, not the whole entry

**Cite:** §4.9 names the material directly: "Rare but sensitive files such as passports, visas, and legal documents may be surfaced as protected records"; §7.3's Protected Records template names "Protected Records may represent sensitive isolated material such as passport scans, medical documents, account statements, visas, legal forms, or credentials"

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `applicant` | string | J. Yung | `validated` | §3.8's role discipline; distinct from any sponsor and from a dependant |
| `destination_jurisdiction` | string | Canada | `validated` | the country whose permission is sought. This domain is inherently two-jurisdiction and cannot be written with a single jurisdiction field |
| `nationality_jurisdiction` | string | United Kingdom | `validated` | the applicant's nationality, which determines route eligibility. Kept as a separate field for exactly the reason §3.8 gives: two values of the same entity type in different roles |
| `route_or_category` | string | skilled worker | `validated` | written functionally; route names are entirely destination-specific |
| `application_reference` | string | APP-2025-88412 | `direct` | §3.13 direct: a labeled form field |
| `decision_status` | string | granted | `direct` | §3.13 direct: a labeled status field on a decision letter |
| `sponsor` | string | Halden Bio Ltd | `validated` | the employer, institution or family member supporting the application; a distinct role |
| `validity_period` | date range | 2026-01-05 to 2029-01-04 | `direct` | §3.13 direct: labeled dates on a permission document |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.4, §3.5):

- an immigration term ('visa' | 'residence permit' | 'leave to remain' | 'immigration' | 'biometric residence' | 'sponsor licence' | 'petition') together with a named applicant and an application-reference label
- a decision term ('decision letter' | 'grant of' | 'refusal of' | 'right of appeal') together with a named immigration authority
- a supporting-evidence term ('certificate of sponsorship' | 'confirmation of acceptance' | 'proof of maintenance') together with an applicant name

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- an evidence bundle whose documents individually belong to banking, employment and education and are gathered only by purpose
- adviser correspondence discussing a route with no reference number

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10):

- a country name
- a passport-number-shaped string
- a date
- the word 'application' — the applications slice owns university applications and the two words are identical

### Work types

`application form`, `supporting evidence bundle`, `sponsor document`, `biometric or appointment record`, `decision letter`, `permission document`, `appeal or review record`

### Grouping reasons (§4)

- one application across its form, evidence and decision — a purpose-coherent packet whose members are content-incoherent
- one applicant across a sequence of permissions

### Template (§5)

`applicant → destination jurisdiction → application → document type`

Time first: **no**

§5.5: "a parent dimension should provide the context required to understand the child". Evidence is meaningless before the application, and the application before the destination whose rules define it. The parallel with §5.6's application packets is exact

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| acad.college-application | a study visa attaches to a university application and the two packets share evidence. §4.8's rule against absorbing a document with a conflicting target institution is the direct analogue: an immigration packet must not absorb a document naming a different destination or institution | §4.8: "an application packet does not silently absorb a document with a conflicting target institution" |
| pers.identity-document | passports and biometric cards are identity documents that immigration paperwork depends on; §4.9 already treats them as protected records in their own right | §4.9: "Rare but sensitive files such as passports, visas, and legal documents may be surfaced as protected records" |
| pers.travel-visa-entry | visas and entry records read as travel history | §3.11 "One file may hold facts from more than one domain without losing information" |
| career.work-authorization | a sponsorship certificate is an employment artefact and an immigration artefact | §3.11 "One file may hold facts from more than one domain without losing information" |

### Sensitivity

`potentially_sensitive` — §2.9's phrase "potentially sensitive" is the only marking made here. §3.15: "Finance, identity, medical, and legal material should be implemented first as safety domains, meaning the system detects and protects them before any cloud or automated placement decision is allowed." — this slice sits inside that sentence, so the conservative direction is the correct one. The handling CLASS is P7's (§8.4) and is not set. §4.9 names visas explicitly among the material that may be surfaced as a protected record regardless of group size.

### Open question — Joseph's call, unresolved

> This domain has two jurisdictions per file — nationality and destination — and the launch-scope question the root entry raises has no single-country answer here at all. Beyond scope, there is a decision only Joseph can make: whether nationality and immigration status may be stored as facts at all, given §8.4's data-minimising posture. They are the most consequential attributes in the corpus and the domain cannot function without them.

---

## `legal.court-records` — Court and tribunal records

Documents issued by or filed with a court or tribunal, held as the formal record rather than as a party's working file.

**Provenance:** **proposal** — new here; no design sentence names it

**Cite:** no design sentence names this domain. §3.15 "Other domains remain placeholders until user demand and corpus evidence justify detailed templates." and §5.7 "expand the library as recurring user needs and corpus evidence justify additional coverage" are what permit the addition; the domain itself is new here.

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `forum` | string | Employment Tribunal, Manchester | `validated` | the issuing court or tribunal |
| `case_number` | string | 2404471/2025 | `direct` | §3.13 direct: a labeled form field; the identifier the record is organised by |
| `party` | string | J. Yung | `validated` | §3.8's role discipline; party labels are jurisdiction-specific and the field is named by function |
| `document_type` | string | order | `validated` | order, judgment, pleading, transcript, exhibit, notice of hearing, sealed copy |
| `filing_or_issue_date` | date | 2025-10-22 | `direct` | §3.13 direct: a labeled or stamped date |
| `jurisdiction` | string | England and Wales | `validated` | a court exists only within a jurisdiction |
| `seal_or_stamp_present` | string | sealed | `possible` | §3.13 possible: a seal is an image feature and OCR frequently cannot establish it; the fact that separates an issued record from a draft is therefore usually a clue, not a conclusion |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.4, §3.5):

- a court or tribunal name matched on a word boundary together with a case-number label and a court-document term ('order' | 'judgment' | 'directions' | 'notice of hearing' | 'transcript')
- an issuance term ('it is ordered that' | 'before the honourable' | 'sealed on' | 'filed on') together with a case-number label

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- a scanned order whose court appears only in a letterhead crest
- a transcript with no caption page

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10):

- a case-number-shaped string
- a court name — courts are cited in guidance, articles and unrelated correspondence
- the word 'order' — it names purchase orders and standing orders far more often in this corpus
- a party name

### Work types

`order`, `judgment`, `sealed pleading`, `notice of hearing`, `transcript`, `exhibit`, `court fee record`

### Grouping reasons (§4)

- one case across the record issued in it
- one hearing across its notice, transcript and resulting order

### Template (§5)

`case → document type → date`

Time first: **no**

§5.5: "a parent dimension should provide the context required to understand the child". An order is meaningless before the case. Date last within a document type because a court record is consulted chronologically inside a case, never across cases

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| legal.litigation-dispute | the working matter file and the formal record hold the same orders and judgments. This entry claims a document when it is issued or sealed; the matter file claims everything the party generated | §3.11 "One file may hold facts from more than one domain without losing information" |
| legal.bankruptcy-insolvency | insolvency orders are court records and insolvency records at once | §3.11 "One file may hold facts from more than one domain without losing information" |
| admin.immigration | immigration appeals produce tribunal records under a case number | §3.11 "One file may hold facts from more than one domain without losing information" |
| legal.wills-trusts-estates | a grant of representation is a court-issued document and an estate document | §3.11 "One file may hold facts from more than one domain without losing information" |

### Sensitivity

`potentially_sensitive` — §2.9's phrase "potentially sensitive" is the only marking made here. §3.15: "Finance, identity, medical, and legal material should be implemented first as safety domains, meaning the system detects and protects them before any cloud or automated placement decision is allowed." — this slice sits inside that sentence, so the conservative direction is the correct one. The handling CLASS is P7's (§8.4) and is not set.

---

## `legal.notarised-documents` — Notarised, sworn and apostilled documents

Documents carrying a formal attestation of authenticity or truth — notarisations, affidavits, certifications and apostilles.

**Provenance:** **proposal** — new here; no design sentence names it

**Cite:** no design sentence names this domain. §3.15 "Other domains remain placeholders until user demand and corpus evidence justify detailed templates." and §5.7 "expand the library as recurring user needs and corpus evidence justify additional coverage" are what permit the addition; the domain itself is new here.

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `attesting_officer` | string | R. Okonkwo, Notary Public | `validated` | §3.8's role discipline: the notary, commissioner or authorised officer |
| `signatory` | string | J. Yung | `validated` | the person whose act or statement is attested |
| `attestation_type` | string | notarial certificate | `validated` | notarisation, affidavit or sworn statement, certified true copy, apostille, consular legalisation |
| `attestation_date` | date | 2025-05-16 | `direct` | §3.13 direct: a labeled date field in an attestation block |
| `apostille_reference` | string | APO-2025-77410 | `direct` | §3.13 direct: a labeled form field where a legalisation certificate exists |
| `underlying_document_type` | string | power of attorney | `validated` | what was attested. The most important field here, because the attestation is a property of another document and this field is the pointer back to its real domain |
| `jurisdiction` | string | Nigeria | `validated` | notarial and legalisation practice is local, and an apostille only means anything between convention states |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.4, §3.5):

- a notarial term ('notary public' | 'sworn before me' | 'commissioner for oaths' | 'notarial certificate' | 'certified to be a true copy') together with an officer name and a labeled attestation date
- an apostille term ('apostille' | 'convention de la haye' | 'legalisation') together with an issuing-authority name and a certificate reference
- an affidavit term ('i, ... , do solemnly and sincerely declare' | 'affirmed before me') together with a signatory name and an attestation block

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- a scanned attestation page whose officer and date are legible only after OCR of a stamp
- a certified copy where the certification is a marginal annotation

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10):

- a seal-shaped image region — an image feature is not an attestation, and §2.6's caution against reading absence or presence of a signal as proof applies
- a signature-shaped region
- a date
- the word 'certified' — it appears on training certificates, product certifications and marketing material

### Work types

`notarial certificate`, `affidavit or sworn statement`, `certified copy`, `apostille certificate`, `consular legalisation`, `witness attestation`

### Grouping reasons (§4)

- one underlying document across its original, its certified copy and its apostille
- one legalisation chain across the offices it passed through

### Template (§5)

`underlying domain → document → attestation`

Time first: **no**

this domain deliberately does not lead with itself. Notarisation is a property OF a document — a notarised lease is still a lease — and §3.14 keeps facts separate from the tree, so attestation belongs on the file as a fact rather than as a branch. The recommended template therefore nests the attestation under whatever domain the underlying document belongs to. A standalone Notarised Documents branch is offered only where the user has no other home for the material, and §5.7's validation that a template "does not repeat a parent dimension, create meaningless one-child levels, exceed practical depth limits" is the reason: an attestation level almost always produces one-child folders.

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| legal.lease | this is the one cross-cutting entry here. An attestation attaches to leases, powers of attorney, wills, corporate documents, immigration evidence and translations alike, and in each case the underlying domain is the real owner | §3.14 keeps facts separate from the destination tree, which is exactly what makes attestation a fact and not a folder |
| legal.power-of-attorney | this is the one cross-cutting entry here. An attestation attaches to leases, powers of attorney, wills, corporate documents, immigration evidence and translations alike, and in each case the underlying domain is the real owner | §3.14 keeps facts separate from the destination tree, which is exactly what makes attestation a fact and not a folder |
| legal.wills-trusts-estates | this is the one cross-cutting entry here. An attestation attaches to leases, powers of attorney, wills, corporate documents, immigration evidence and translations alike, and in each case the underlying domain is the real owner | §3.14 keeps facts separate from the destination tree, which is exactly what makes attestation a fact and not a folder |
| corp.business-formation | this is the one cross-cutting entry here. An attestation attaches to leases, powers of attorney, wills, corporate documents, immigration evidence and translations alike, and in each case the underlying domain is the real owner | §3.14 keeps facts separate from the destination tree, which is exactly what makes attestation a fact and not a folder |
| write.translation | this is the one cross-cutting entry here. An attestation attaches to leases, powers of attorney, wills, corporate documents, immigration evidence and translations alike, and in each case the underlying domain is the real owner | §3.14 keeps facts separate from the destination tree, which is exactly what makes attestation a fact and not a folder |
| legal.court-records | affidavits are sworn documents and court filings; the distinguishing signal is a case number | §3.7 "it should require both a minimum score and a minimum margin over the second-best candidate before it fills a facet" |
| admin.immigration | certified translations and legalised civil documents are immigration evidence carrying an attestation | §3.11 "One file may hold facts from more than one domain without losing information" |

### Sensitivity

`potentially_sensitive` — §2.9's phrase "potentially sensitive" is the only marking made here. §3.15: "Finance, identity, medical, and legal material should be implemented first as safety domains, meaning the system detects and protects them before any cloud or automated placement decision is allowed." — this slice sits inside that sentence, so the conservative direction is the correct one. The handling CLASS is P7's (§8.4) and is not set.

---

## `legal.debt-collection` — Debt collection and enforcement

The pursuit of an unpaid obligation, from demand through agency referral to enforcement.

**Provenance:** **proposal** — new here; no design sentence names it

**Cite:** no design sentence names this domain. §3.15 "Other domains remain placeholders until user demand and corpus evidence justify detailed templates." and §5.7 "expand the library as recurring user needs and corpus evidence justify additional coverage" are what permit the addition; the domain itself is new here.

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `creditor` | string | Nationwide | `validated` | §3.8's role discipline: the party owed. Distinct from any agency acting for them |
| `debtor` | string | J. Yung | `validated` | the party owing; the user may occupy either role and the domain must not assume |
| `collecting_agency` | string | Marston Recovery | `validated` | a third role that appears part-way through and is often mistaken for the creditor |
| `original_account_reference` | string | ****3390 | `validated` | the account the debt arose on; the fact that links this domain back to fin.credit or fin.loan-mortgage |
| `matter_reference` | string | REC-2025-88410 | `direct` | §3.13 direct: a labeled form field, distinct from the original account reference |
| `stage` | string | formal demand | `validated` | reminder, formal demand, default notice, agency referral, enforcement, settlement |
| `jurisdiction` | string | United Kingdom | `validated` | debt-collection conduct rules and enforcement powers are local |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.4, §3.5):

- a collection term ('demand for payment' | 'default notice' | 'letter before action' | 'arrears' | 'debt recovery' | 'collection agency') together with a creditor or agency name matched on a word boundary and an account or matter reference label
- an enforcement term ('enforcement agent' | 'warrant of control' | 'attachment of earnings' | 'charging order') together with a matter reference
- a settlement term ('full and final settlement' | 'payment arrangement' | 'affordability assessment') together with a creditor name and an account reference

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- an early reminder letter whose tone is the only signal that an account is in arrears
- correspondence disputing a debt that never names the stage

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10):

- a currency amount
- an account reference
- a company name — a collecting agency is a company like any other
- the word 'overdue' or 'reminder' — both appear on ordinary invoices that are simply late

### Work types

`reminder`, `formal demand`, `default notice`, `agency referral`, `payment arrangement`, `enforcement notice`, `settlement confirmation`, `dispute correspondence`

### Grouping reasons (§4)

- one debt across its escalation
- one creditor across the accounts pursued

### Template (§5)

`debt or account → stage → date`

Time first: **no**

§5.5: "a parent dimension should provide the context required to understand the child". A demand is meaningless before the debt it demands. Stage second because the sequence is the substance of this domain

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| fin.credit | the same account reference appears in both, and a collection file must not absorb the account's ordinary statement history | §4.8: "an application packet does not silently absorb a document with a conflicting target institution" — the same rule against silent absorption |
| fin.loan-mortgage | the same account reference appears in both, and a collection file must not absorb the account's ordinary statement history | §4.8: "an application packet does not silently absorb a document with a conflicting target institution" — the same rule against silent absorption |
| biz.invoice-issued | chasing an unpaid receivable is collection from the other side; the user is the creditor rather than the debtor and the roles invert | §3.8 "The system must separate roles that happen to contain the same entity type" |
| legal.litigation-dispute | collection escalating to proceedings crosses the boundary; the distinguishing signal is a forum and a case number | §3.7 "it should require both a minimum score and a minimum margin over the second-best candidate before it fills a facet" |
| legal.bankruptcy-insolvency | a debt proved in an insolvency belongs to both | §3.11 "One file may hold facts from more than one domain without losing information" |

### Sensitivity

`potentially_sensitive` — §2.9's phrase "potentially sensitive" is the only marking made here. §3.15: "Finance, identity, medical, and legal material should be implemented first as safety domains, meaning the system detects and protects them before any cloud or automated placement decision is allowed." — this slice sits inside that sentence, so the conservative direction is the correct one. The handling CLASS is P7's (§8.4) and is not set.

---

## `legal.bankruptcy-insolvency` — Bankruptcy and insolvency

Formal insolvency of a person or entity — the proceeding, its officeholder, and the claims made in it.

**Provenance:** **proposal** — new here; no design sentence names it

**Cite:** no design sentence names this domain. §3.15 "Other domains remain placeholders until user demand and corpus evidence justify detailed templates." and §5.7 "expand the library as recurring user needs and corpus evidence justify additional coverage" are what permit the addition; the domain itself is new here.

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `subject` | string | Halden Bio Ltd | `validated` | the insolvent person or entity; §3.8 keeps it distinct from the officeholder and from creditors |
| `proceeding_type` | string | creditors' voluntary liquidation | `validated` | written functionally, because the procedures themselves differ between jurisdictions rather than merely being named differently |
| `officeholder` | string | Merton Recovery LLP | `validated` | the trustee, administrator, liquidator or practitioner appointed; a distinct role |
| `forum_or_authority` | string | Insolvency Service | `validated` | the court or authority supervising |
| `case_number` | string | CR-2025-004471 | `direct` | §3.13 direct: a labeled form field |
| `commencement_date` | date | 2025-09-12 | `direct` | §3.13 direct: a labeled date field |
| `creditor` | string | Rowan Print Services | `validated` | the claiming role; present on proofs of debt and never a folder level |
| `jurisdiction` | string | England and Wales | `validated` | insolvency is one of the most jurisdiction-bound domains in this slice |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.4, §3.5):

- an insolvency term ('bankruptcy' | 'insolvency' | 'liquidation' | 'administration' | 'proof of debt' | 'creditors meeting' | 'statement of affairs') together with an officeholder or court name matched on a word boundary and a case reference
- an appointment term ('notice of appointment' | 'appointed as' | 'office holder') together with a subject entity name and a labeled date
- a distribution term ('dividend to creditors' | 'final report to creditors') together with a case reference

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- correspondence about a company's difficulties before any formal step
- a report to creditors whose subject is named only in a covering letter

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10):

- a company name
- a case-number-shaped string
- a currency amount
- the word 'administration' — it is the single worst false friend in this slice, since personal administration, business administration and administrative documents all use it

### Work types

`notice of appointment`, `statement of affairs`, `proof of debt`, `creditors' report`, `meeting notice and minutes`, `court order`, `final report and closure`

### Grouping reasons (§4)

- one proceeding across its whole administration
- one creditor's claim across its proof, correspondence and distribution

### Template (§5)

`proceeding → document type → date`

Time first: **no**

§5.5: "a parent dimension should provide the context required to understand the child". A proof of debt is meaningless before the proceeding it is lodged in

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| legal.court-records | insolvency orders are court-issued and belong to both | §3.11 "One file may hold facts from more than one domain without losing information" |
| legal.debt-collection | a debt pursued and then proved in an insolvency moves between the two under the same account reference | §3.11 "One file may hold facts from more than one domain without losing information" |
| corp.business-formation | dissolution and strike-off records are constitutional and insolvency records at once | §3.11 "One file may hold facts from more than one domain without losing information" |
| biz.bookkeeping | a statement of affairs is built from the books and reads like an accounts document | §3.7 "it should require both a minimum score and a minimum margin over the second-best candidate before it fills a facet" |

### Sensitivity

`potentially_sensitive` — §2.9's phrase "potentially sensitive" is the only marking made here. §3.15: "Finance, identity, medical, and legal material should be implemented first as safety domains, meaning the system detects and protects them before any cloud or automated placement decision is allowed." — this slice sits inside that sentence, so the conservative direction is the correct one. The handling CLASS is P7's (§8.4) and is not set.

### Open question — Joseph's call, unresolved

> Insolvency procedures are not translations of one another — a liquidation, a bankruptcy and an arrangement have different documents, different officeholders and different consequences in each jurisdiction, and the word 'bankruptcy' itself means different things in different systems. This entry names the proceeding functionally; whether the product should attempt this domain before jurisdiction scope is fixed is Joseph's call.

---

## `fin.charitable-giving` — Charitable giving

Money or property given to a cause, and the acknowledgements the recipient issues for it.

**Provenance:** **proposal** — new here; no design sentence names it

**Cite:** no design sentence names this domain. §3.15 "Other domains remain placeholders until user demand and corpus evidence justify detailed templates." and §5.7 "expand the library as recurring user needs and corpus evidence justify additional coverage" are what permit the addition; the domain itself is new here.

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `recipient_organisation` | string | Shelter | `validated` | §3.8's issuing role: the donee. Never a folder level on its own — "A folder should not become a collection point for everything produced by the same person or organization" |
| `donor` | string | J. Yung | `validated` | the giving role; may be a person or an entity |
| `donation_date` | date | 2025-12-04 | `direct` | §3.13 direct: a labeled date field |
| `receipt_reference` | string | DON-2025-99401 | `direct` | §3.13 direct: a labeled form field |
| `tax_year` | string | 2025 | `validated` | §3.11's Finance field; present when the receipt is issued for a claim |
| `deductibility_statement` | string | no goods or services were provided | `validated` | the sentence that turns a receipt into a tax document; a rule can find it beside a donation term |
| `giving_type` | string | recurring | `validated` | one-off, recurring, in-kind, legacy |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.4, §3.5):

- a donation term ('donation' | 'charitable contribution' | 'gift aid' | 'registered charity' | 'tax-deductible' | 'no goods or services') together with an organisation name matched on a word boundary and a labeled date
- a receipt-reference label together with a donation term and a named recipient organisation

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- a thank-you letter that acknowledges a gift without a receipt structure
- a sponsorship or fundraising-page confirmation that reads like an ordinary purchase

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10):

- a currency amount
- an organisation name — charities appear in newsletters, appeals and marketing mail
- a bare year
- the word 'donation' in a filename

### Work types

`donation receipt`, `recurring-gift confirmation`, `annual giving summary`, `in-kind gift acknowledgement`, `sponsorship confirmation`, `legacy pledge`

### Grouping reasons (§4)

- one tax year across every recipient — because the claim, not the charity, is what the documents serve
- one recipient across a recurring commitment

### Template (§5)

`tax year → recipient`

Time first: **yes**

the second exception to §5.5's usual order in this slice, and for the same reason as receipts: the documents exist to serve a yearly claim, so the year is the function rather than incidental time. §3.8's "A folder should not become a collection point for everything produced by the same person or organization" independently forbids leading with the charity.

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| tax.supporting-documents | a donation receipt stating deductibility is a giving record and a tax document simultaneously — the design's answer is that it keeps both sets of facts | §3.11 "One file may hold facts from more than one domain without losing information" |
| fin.receipts-expenses | a donation processed through a payment provider produces a receipt indistinguishable in shape from a purchase | §3.7 "it should require both a minimum score and a minimum margin over the second-best candidate before it fills a facet" |
| fin.grants-received | same money, opposite direction. A user who is both a donor and a grantee will have both, and only the roles separate them | §3.8 "The system must separate roles that happen to contain the same entity type" |

### Sensitivity

`potentially_sensitive` — §2.9's phrase "potentially sensitive" is the only marking made here. §3.15: "Finance, identity, medical, and legal material should be implemented first as safety domains, meaning the system detects and protects them before any cloud or automated placement decision is allowed." — this slice sits inside that sentence, so the conservative direction is the correct one. The handling CLASS is P7's (§8.4) and is not set.

---

## `fin.grants-received` — Grants and awards received

Non-repayable funding awarded to a person or small entity, and the reporting the award requires.

**Provenance:** **proposal** — new here; no design sentence names it

**Cite:** no design sentence names this domain. §3.15 "Other domains remain placeholders until user demand and corpus evidence justify detailed templates." and §5.7 "expand the library as recurring user needs and corpus evidence justify additional coverage" are what permit the addition; the domain itself is new here.

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `funder` | string | Wellcome Trust | `validated` | §3.8's issuing role |
| `grantee` | string | J. Yung | `validated` | the receiving role |
| `award_reference` | string | GR-2025-88417 | `direct` | §3.13 direct: a labeled form field |
| `programme` | string | Early Career Fellowship | `validated` | the scheme awarded under; this domain's subject dimension |
| `award_period` | date range | 2026-01-01 to 2027-12-31 | `direct` | §3.13 direct: labeled start and end dates |
| `reporting_obligation` | string | annual narrative and financial report | `llm_supported` | §3.5: obligations live in prose in the award letter or terms, so this cannot exceed llm_supported and §3.6's citation requirement applies |
| `award_status` | string | active | `direct` | §3.13 direct: a labeled status field |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.4, §3.5):

- an award term ('grant agreement' | 'award letter' | 'we are pleased to award' | 'grant reference' | 'disbursement schedule' | 'grant conditions') together with a funder name matched on a word boundary and an award-reference label
- a reporting term ('interim report' | 'final report' | 'financial statement of expenditure') together with an award-reference label

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- an award communicated by email with no reference number
- a bursary or prize whose award nature is legible only from prose

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10):

- a currency amount
- a funder name — funders are named in calls for applications, news and other people's acknowledgements
- a date range
- the word 'grant' — it is also a surname and a common verb in contracts

### Work types

`application`, `award letter`, `grant agreement`, `disbursement record`, `interim or final report`, `variation or extension`, `closure confirmation`

### Grouping reasons (§4)

- one award across its application, agreement, disbursements and reports
- one funder across the awards held

### Template (§5)

`funder → award → document type`

Time first: **no**

§5.5: "a parent dimension should provide the context required to understand the child". A report is meaningless before the award, and the award before the funder whose scheme defines it. The award is this domain's project dimension

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| res.research-project | a research grant is a Research-domain object first; §3.11 gives Research the fields project, stage, artifact type, lab and venue, and that slice owns the project-linked material. This entry claims the funding relationship, not the science | §3.11 "One file may hold facts from more than one domain without losing information" |
| acad.scholarship-fellowship | a scholarship is an award to a student and belongs with the education record as much as here | §3.11 "One file may hold facts from more than one domain without losing information" |
| fin.charitable-giving | giving and receiving are the same transaction from opposite roles | §3.8 "The system must separate roles that happen to contain the same entity type" |
| corp.fundraising-investor | non-dilutive funding and investment both fund an entity and a user may file them together | §4.9 "members carry irreconcilable course, institution, project, term, or purpose facts" |

### Sensitivity

`potentially_sensitive` — §2.9's phrase "potentially sensitive" is the only marking made here. §3.15: "Finance, identity, medical, and legal material should be implemented first as safety domains, meaning the system detects and protects them before any cloud or automated placement decision is allowed." — this slice sits inside that sentence, so the conservative direction is the correct one. The handling CLASS is P7's (§8.4) and is not set.

---

## `admin.subscriptions-recurring` — Subscriptions and recurring billing

Ongoing paid services and the renewal, change and cancellation records they generate.

**Provenance:** **proposal** — new here; no design sentence names it

**Cite:** no design sentence names this domain. §3.15 "Other domains remain placeholders until user demand and corpus evidence justify detailed templates." and §5.7 "expand the library as recurring user needs and corpus evidence justify additional coverage" are what permit the addition; the domain itself is new here.

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `vendor` | string | Adobe | `validated` | §3.8's issuing role. Not a folder level on its own — "A folder should not become a collection point for everything produced by the same person or organization" |
| `service_or_plan` | string | Creative Cloud, individual | `validated` | the thing subscribed to; this domain's subject dimension |
| `billing_period` | string | monthly | `validated` | the recurrence, which is what distinguishes this domain from a one-off purchase |
| `renewal_date` | date | 2026-03-11 | `direct` | §3.13 direct: a labeled date field |
| `subscription_identifier` | string | SUB-88213 | `direct` | §3.13 direct: a labeled form field |
| `payment_method` | string | card ****2201 | `direct` | §3.13 direct: a labeled and usually masked field |
| `subscription_status` | string | active | `direct` | §3.13 direct: a labeled status field or a cancellation confirmation |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.4, §3.5):

- a recurring-billing term ('your subscription' | 'renews on' | 'auto-renewal' | 'billing period' | 'next payment' | 'plan') together with a vendor name matched on a word boundary and a labeled date
- a change term ('plan change' | 'upgraded to' | 'cancellation confirmed' | 'subscription cancelled') together with a subscription-identifier label

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- a service email that is a renewal notice in substance but a marketing message in form
- a bill whose recurrence is legible only from a period covered line

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10):

- a currency amount
- a vendor name — vendors send marketing mail constantly and it outnumbers billing mail
- a date
- the word 'plan' — it names project plans, floor plans and business plans

### Work types

`renewal notice`, `subscription invoice`, `plan-change confirmation`, `cancellation confirmation`, `terms update notice`, `usage summary`

### Grouping reasons (§4)

- one subscription across its billing history
- one vendor across the services subscribed to

### Template (§5)

`service → year`

Time first: **no**

shallow deliberately. §5.9 warns against levels that produce one child or a large number of tiny folders, and a per-vendor per-month tree is exactly that. §5.9's "a scoped General or Other branch within a meaningful parent" is the better answer for the long tail of one-off services.

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| biz.invoice-received | a subscription invoice is a payable invoice; the distinguishing signal is a renewal or plan term, not the invoice shape | §3.7 "it should require both a minimum score and a minimum margin over the second-best candidate before it fills a facet" |
| fin.receipts-expenses | each charge also produces a receipt, and §7.3's residual template would hold it | §7.3: "Receipts and Confirmations may hold isolated invoices, delivery confirmations, booking records, boarding passes, purchase receipts, event tickets, and similar transactional documents." |
| legal.contracts | the terms of service accepted on subscribing are a contract, though users rarely file them as one | §3.11 "One file may hold facts from more than one domain without losing information" |

### Sensitivity

`potentially_sensitive` — §2.9's phrase "potentially sensitive" is the only marking made here. §3.15: "Finance, identity, medical, and legal material should be implemented first as safety domains, meaning the system detects and protects them before any cloud or automated placement decision is allowed." — this slice sits inside that sentence, so the conservative direction is the correct one. The handling CLASS is P7's (§8.4) and is not set.

---

## `admin.warranties` — Warranties and product registrations

Manufacturer or retailer promises attached to a purchased item, and the claims made under them.

**Provenance:** **proposal** — new here; no design sentence names it

**Cite:** no design sentence names this domain. §3.15 "Other domains remain placeholders until user demand and corpus evidence justify detailed templates." and §5.7 "expand the library as recurring user needs and corpus evidence justify additional coverage" are what permit the addition; the domain itself is new here.

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `product` | string | Bosch WAT28371 washing machine | `validated` | the item covered; this domain's subject dimension |
| `manufacturer_or_retailer` | string | Bosch | `validated` | §3.8's issuing role; the promisor, distinct from the seller where they differ |
| `serial_number` | string | FD9812 004471 | `direct` | §3.13 direct: a labeled form field; the fact that ties a claim to an item |
| `purchase_date` | date | 2024-03-19 | `direct` | §3.13 direct: a labeled date field, usually on the attached proof of purchase |
| `warranty_end` | date | 2029-03-18 | `validated` | read from a coverage clause. Recorded as a fact about the document; the catalogue states no policy about acting on it |
| `coverage_type` | string | parts and labour | `validated` | what the promise covers |
| `claim_reference` | string | WC-2027-1180 | `direct` | §3.13 direct: a labeled form field on claim documents |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.4, §3.5):

- a warranty term ('warranty' | 'guarantee' | 'covered for' | 'warranty period' | 'proof of purchase required') together with a product or model name and a manufacturer name matched on a word boundary
- a registration term ('register your product' | 'product registration confirmed') together with a serial-number label
- a claim term ('warranty claim' | 'repair authorisation' | 'service reference') together with a serial-number label

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- a manual whose warranty section is one part of a long document
- a retailer email confirming extended cover with no product identifier

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10):

- a serial-number-shaped string
- a model name — model codes collide with part numbers, SKUs and reference codes
- a date
- the word 'guarantee' — it appears in marketing copy on almost every commercial document

### Work types

`warranty document`, `product registration confirmation`, `proof of purchase`, `extended-cover certificate`, `claim record`, `repair or replacement confirmation`

### Grouping reasons (§4)

- one item across its receipt, registration, warranty and claims — a purpose-coherent packet whose members come from different domains
- one claim across its raising and resolution

### Template (§5)

`item → document type`

Time first: **no**

§5.5: "a parent dimension should provide the context required to understand the child". A claim is meaningless before the item. Shallow because most items generate two or three documents and §5.9 warns against a level that creates a large number of tiny folders

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| fin.receipts-expenses | the receipt is the proof of purchase the warranty depends on. The same file is a purchase record and a warranty document, and §3.9's purpose reading is what binds it to the item | §3.9: "The documents are content-incoherent but purpose-coherent." |
| fin.insurance | an extended warranty sold as a product behaves like a policy; the distinguishing signal is an insurer and a policy number rather than a manufacturer and a serial number | §3.7 "it should require both a minimum score and a minimum margin over the second-best candidate before it fills a facet" |
| pers.household-inventory | the item itself is a possession record; this entry claims only the promise attached to it | §3.8 "The system must separate roles that happen to contain the same entity type" |

### Sensitivity

`potentially_sensitive` — §2.9's phrase "potentially sensitive" is the only marking made here. §3.15: "Finance, identity, medical, and legal material should be implemented first as safety domains, meaning the system detects and protects them before any cloud or automated placement decision is allowed." — this slice sits inside that sentence, so the conservative direction is the correct one. The handling CLASS is P7's (§8.4) and is not set.

---

## `biz.procurement-po` — Procurement and purchase orders

The buying process on the purchaser's side — requisition, order, delivery and the match against the supplier's bill.

**Provenance:** **proposal** — new here; no design sentence names it

**Cite:** no design sentence names this domain. §3.15 "Other domains remain placeholders until user demand and corpus evidence justify detailed templates." and §5.7 "expand the library as recurring user needs and corpus evidence justify additional coverage" are what permit the addition; the domain itself is new here.

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `buyer_entity` | string | Halden Bio Ltd | `validated` | §3.8's `our_firm` role on the purchasing side |
| `supplier` | string | Rowan Print Services | `validated` | §3.8's counterparty role |
| `purchase_order_number` | string | PO-4471 | `direct` | §3.13 direct: a labeled form field; the identifier the whole packet matches on |
| `order_date` | date | 2025-10-30 | `direct` | §3.13 direct: a labeled date field |
| `requisition_reference` | string | REQ-2025-881 | `direct` | §3.13 direct: a labeled form field, distinct from the order number and raised earlier |
| `delivery_date` | date | 2025-11-14 | `direct` | §3.13 direct: a labeled date field on a delivery note or goods receipt |
| `cost_centre` | string | R&D | `validated` | the internal charge code; the link to bookkeeping |
| `contract_reference` | string | MSA-ROW-2024 | `validated` | the agreement the order draws down against, where the order names it |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.4, §3.5):

- a purchase-order label ('purchase order' | 'PO number' | 'order number') together with a 'ship to' or 'deliver to' block naming the buyer and a supplier name matched on a word boundary
- a requisition term ('purchase requisition' | 'approval required' | 'requested by') together with a cost-centre label
- a goods-receipt term ('delivery note' | 'goods received' | 'packing list') together with a purchase-order-number label

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- an approval thread in email that functions as the requisition
- a supplier quotation accepted informally in place of an order

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10):

- a long digit string standing in for an order number
- a supplier name
- a currency amount
- the word 'order' — court orders, standing orders and sort-order all collide with it

### Work types

`requisition`, `quotation`, `purchase order`, `order confirmation`, `delivery note or goods receipt`, `goods-return record`, `three-way match record`

### Grouping reasons (§4)

- one order across its requisition, order, delivery note and matched invoice — the three-way match, a purpose-coherent packet
- one supplier across one purchasing year

### Template (§5)

`supplier → year → order`

Time first: **no**

§5.4's Career row establishes the organisation-led order — "a Career template may define company → role or recruiting cycle → document type" — and §5.5's "a parent dimension should provide the context required to understand the child" makes a delivery note meaningless before the order it delivers against

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| biz.invoice-received | the invoice closes the order and the packet spans both domains; the three-way match is the standing reason a procurement folder and a payables folder end up holding each other's documents | §3.9: "The documents are content-incoherent but purpose-coherent." |
| biz.vendor-management | orders are the transactional layer of a vendor relationship whose contractual layer lives there | §3.8 "The system must separate roles that happen to contain the same entity type" |
| legal.contracts | an order that draws down against a framework agreement references a contract it is not | §4.8 forbids inventing a membership the dossier does not support |
| fin.receipts-expenses | for a very small entity an order confirmation and a receipt are the same document | §7.3: "Receipts and Confirmations may hold isolated invoices, delivery confirmations, booking records, boarding passes, purchase receipts, event tickets, and similar transactional documents." |

### Sensitivity

`potentially_sensitive` — §2.9's phrase "potentially sensitive" is the only marking made here. §3.15: "Finance, identity, medical, and legal material should be implemented first as safety domains, meaning the system detects and protects them before any cloud or automated placement decision is allowed." — this slice sits inside that sentence, so the conservative direction is the correct one. The handling CLASS is P7's (§8.4) and is not set.

---

## `biz.vendor-management` — Vendor and supplier management

The relationship with a supplier as an ongoing thing — onboarding, diligence, contractual anchor documents and review.

**Provenance:** **proposal** — new here; no design sentence names it

**Cite:** no design sentence names this domain. §3.15 "Other domains remain placeholders until user demand and corpus evidence justify detailed templates." and §5.7 "expand the library as recurring user needs and corpus evidence justify additional coverage" are what permit the addition; the domain itself is new here.

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `vendor` | string | Rowan Print Services | `validated` | §3.8's counterparty role — the design's own `client` role, reversed |
| `our_entity` | string | Halden Bio Ltd | `validated` | §3.8's `our_firm` role; without it the direction of the relationship is lost |
| `vendor_identifier` | string | VEN-0442 | `direct` | §3.13 direct: a labeled form field in a vendor master record |
| `relationship_stage` | string | active | `validated` | onboarding, active, under review, terminated |
| `category` | string | print and fulfilment | `validated` | the spend category the vendor sits in; the grouping dimension for a large supplier base |
| `review_date` | date | 2025-06-30 | `direct` | §3.13 direct: a labeled date field on a review record |
| `contract_reference` | string | MSA-ROW-2024 | `validated` | the anchor agreement; the pointer into legal.contracts |
| `bank_details_on_file` | string | verified | `possible` | §3.13 possible: whether payment details were verified is usually inferable from a process record rather than stated. §8.4 keeps the details themselves local |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.4, §3.5):

- a vendor-lifecycle term ('vendor onboarding' | 'supplier questionnaire' | 'vendor code' | 'supplier due diligence' | 'vendor master') together with a vendor name matched on a word boundary and the user's own entity name in a distinct role block
- a review term ('supplier performance review' | 'service review' | 'SLA report') together with a vendor identifier label
- an offboarding term ('termination notice' | 'supplier exit' | 'transition plan') together with a vendor name and a contract reference

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- an onboarding thread conducted in email
- a review memo that never names the vendor in a labeled field

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10):

- a company name
- a reference number
- the word 'supplier' or 'vendor' in a filename — it appears on every marketing approach the entity receives
- a date

### Work types

`onboarding pack`, `due-diligence questionnaire`, `master agreement reference`, `vendor master record`, `performance review`, `SLA report`, `termination or exit record`

### Grouping reasons (§4)

- one vendor across the whole relationship
- one review cycle across its questionnaire, evidence and outcome

### Template (§5)

`category → vendor → document type`

Time first: **no**

category leads rather than vendor because a vendor list is long and flat, and §5.9 warns against a level that creates a large number of tiny folders. §3.8's "A folder should not become a collection point for everything produced by the same person or organization" applies to the vendor level too: one folder per supplier is a collector unless the relationship genuinely has substance.

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| legal.contracts | the master agreement is the anchor of this relationship and a contract in its own right; both domains legitimately want it | §3.11 "One file may hold facts from more than one domain without losing information" |
| biz.procurement-po | the relationship layer and the transaction layer, split; orders reference the vendor and the vendor record references the contract | §3.8 "The system must separate roles that happen to contain the same entity type" |
| corp.compliance-audit | supplier due diligence is a compliance artefact and a vendor-lifecycle record at once | §3.11 "One file may hold facts from more than one domain without losing information" |
| biz.invoice-received | payment details held on a vendor record and quoted on an invoice are the same data in two places, and §8.4 keeps the raw value local in both | §8.4 names "identity documents, account statements, tax records, medical information, legal records, credentials" among the material that must not leave the device by default |

### Sensitivity

`potentially_sensitive` — §2.9's phrase "potentially sensitive" is the only marking made here. §3.15: "Finance, identity, medical, and legal material should be implemented first as safety domains, meaning the system detects and protects them before any cloud or automated placement decision is allowed." — this slice sits inside that sentence, so the conservative direction is the correct one. The handling CLASS is P7's (§8.4) and is not set.

---
