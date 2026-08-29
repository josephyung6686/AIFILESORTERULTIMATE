# 07 — Law and legal practice (the professional side)

- **supercategory**: `law-legal-practice`
- **authored**: 2026-08-21
- **entries**: 43 — 40 proposal · 3 inference
- **contract**: [`_CONTRACT.md`](_CONTRACT.md) · **source of truth**: [`../00-database-agent-product-design.md`](../00-database-agent-product-design.md)
- **generated from** `07-law-legal-practice.json`. Edit the JSON, not this file.

## Scope

Legal PRACTICE: the work product of practitioners and legal functions. Personal and business legal ADMIN — a household's or company's own contracts, wills, leases, court copies and dispute files — is slice 05's (`05-finance-legal-admin`). Slice 05 owns the party's own file; this slice owns the practitioner's. The mover is a practice-side signal — a matter reference, a fee-earner or counsel signature block, practice letterhead, an engagement letter. Absent one, this slice ABSTAINS and 05 wins. This is 05's own specialisation rule applied across the seam: 'the more specific domain wins where its own fields populate'.

## Design basis

Everything this slice may lean on. The design names **no** legal domain and **no** legal fact field, so every entry below is an addition and is marked as one.

- §3.15 — “Finance, identity, medical, and legal material should be implemented first as safety domains, meaning the system detects and protects them before any cloud or automated placement decision is allowed.” This is the only sentence in the design that says anything about legal material as a domain. It says legal is DETECTED and PROTECTED, not that it has a schema. Every entry here is therefore an addition.
- §5.7 — the template library should cover “client engagements, research workflows, financial records, travel, legal matters”. Named as situations; no fields stated for any of them.
- §4.9 — “Rare but sensitive files such as passports, visas, and legal documents may be surfaced as protected records even when they do not meet a normal group-size threshold.”
- §8.4 — the corpus can include “identity documents, account statements, tax records, medical information, legal records, credentials, private correspondence, GPS metadata, employment materials, and educational records”.
- §3.8 — the only FIELD names in this slice the design supplies literally: “such as authored_by and target_school, or our_firm and client.” and “A consulting document may mention the author’s firm and the client organization.”
- P6 SPEC, Deferred — 'Identity, medical, legal fact-schema fields | §3.15 (safety domains) | Named as safety domains; no fields stated anywhere.' P6's Done-means item 2 requires that legal acquire NO field rows at launch. Nothing in this catalogue may be loaded into P6's `fields` table without an authored schema change (§3.12: fields are never created at runtime).

## Jurisdiction

Authored jurisdiction-neutrally at the SCHEMA level and only there. Court naming, case-identifier formats, filing-type names, party designations, procedural stage names, discovery devices, production numbering, admission and licensing bodies, and land and IP registries all differ by country and often by court within one country. No entry hard-codes an identifier pattern, a court gazetteer or a stage enum; every jurisdiction-bound vocabulary item is confined to `work_types` and `recognition` and is marked where it appears. Whether the library ships one neutral family with `jurisdiction` as a fact field or per-jurisdiction variants is Joseph's call and is raised in law.matter-file's open_question, with sharper forms of the same question under law.motions-and-briefs, law.depositions, law.jury-materials and law.ediscovery-production.

## Privilege

NO privilege field, flag or value exists anywhere in this slice, and none may be added from this file. Privilege is a legal determination about a specific document in a specific context; a 'privileged and confidential' legend does not create it and its absence does not negate it. 'Privilege log' appears once, as a `work_type` in law.document-review — the name of a real artefact, not a status assigned to anything. Whether the system may record an OBSERVATION that a legend is present, and whether P7's §8.4 handling-class vocabulary needs a class for privileged material, are two open questions carried in law.document-review and are Joseph's, not this catalogue's.

## Handling classes

None assigned. `sensitivity` uses §2.9's phrase `potentially_sensitive` and nothing more; handling classes are P7's under §8.4. Contract rule 5: a catalogue that assigns one is inventing P7's vocabulary.

## Boundary with slice 05 — finance and legal admin

Slice 05 owns the party's own file; this slice owns the practitioner's. The mover is a practice-side signal — a matter reference, a fee-earner or counsel signature block, practice letterhead, an engagement letter. Absent one, this slice ABSTAINS and 05 wins. This is 05's own specialisation rule applied across the seam: 'the more specific domain wins where its own fields populate'.

- **reconciled**: 2026-08-21, against the published 05-finance-legal-admin.json. Every `legal.*`, `corp.*`, `biz.*` and `admin.*` id in this file's `collides_with` is one of 05's real ids and was checked against it.
- **not duplicated**: No entry here re-covers a party's own record. Client-money / trust ledgers were left unwritten for the same reason (see law.time-and-billing's open_question).

| Seam |
|---|
| law.matter-file ↔ legal.litigation-dispute (the primary seam) |
| the court family ↔ legal.court-records |
| law.ip-prosecution ↔ legal.ip-registration |
| law.immigration-casework ↔ admin.immigration |
| law.corporate-secretarial ↔ corp.business-formation |
| law.regulatory-submission ↔ corp.regulatory-filings |
| law.compliance-programme ↔ corp.compliance-audit |
| law.contract-negotiation / law.transactional-deal ↔ legal.contracts |
| law.estates-administration ↔ legal.wills-trusts-estates |
| law.time-and-billing ↔ biz.invoice-received |

## Index

| # | id | Name | Provenance | Sensitivity | Open question |
|---|---|---|---|---|---|
| 1 | `law.matter-file` | Matter and case file | inference | potentially_sensitive | yes |
| 2 | `law.client-intake` | Client intake and instructions | inference | potentially_sensitive | yes |
| 3 | `law.conflicts-check` | Conflicts screening and information barriers | proposal | potentially_sensitive | — |
| 4 | `law.engagement-terms` | Engagement letters, retainers and scope | inference | potentially_sensitive | — |
| 5 | `law.time-and-billing` | Time recording and legal billing | proposal | potentially_sensitive | yes |
| 6 | `law.matter-correspondence` | Matter correspondence and attendance notes | proposal | potentially_sensitive | — |
| 7 | `law.limitation-and-diary` | Deadlines, limitation dates and court diary | proposal | potentially_sensitive | — |
| 8 | `law.pleadings` | Pleadings and originating process | proposal | potentially_sensitive | — |
| 9 | `law.court-filing-record` | Filing, service and docket records | proposal | potentially_sensitive | yes |
| 10 | `law.motions-and-briefs` | Interlocutory applications and written submissions | proposal | potentially_sensitive | yes |
| 11 | `law.orders-and-judgments` | Orders, judgments and directions | proposal | potentially_sensitive | — |
| 12 | `law.appeals` | Appeals and the appellate record | proposal | potentially_sensitive | — |
| 13 | `law.discovery-requests` | Discovery and disclosure requests and responses | proposal | potentially_sensitive | — |
| 14 | `law.document-review` | Document review work product | proposal | potentially_sensitive | yes |
| 15 | `law.ediscovery-production` | Electronic productions | proposal | potentially_sensitive | yes |
| 16 | `law.evidence-exhibits` | Evidence and exhibits | proposal | potentially_sensitive | yes |
| 17 | `law.depositions` | Depositions and pre-trial examinations | proposal | potentially_sensitive | yes |
| 18 | `law.witness-statements` | Witness statements, affidavits and declarations | proposal | potentially_sensitive | — |
| 19 | `law.expert-materials` | Expert evidence and instructions | proposal | potentially_sensitive | yes |
| 20 | `law.trial-preparation` | Hearing and trial preparation | proposal | potentially_sensitive | yes |
| 21 | `law.jury-materials` | Jury selection and jury-facing materials | proposal | potentially_sensitive | yes |
| 22 | `law.hearing-transcripts` | Hearing transcripts and the record of proceedings | proposal | potentially_sensitive | — |
| 23 | `law.settlement` | Settlement negotiation and settlement instruments | proposal | potentially_sensitive | — |
| 24 | `law.adr` | Mediation and arbitration | proposal | potentially_sensitive | yes |
| 25 | `law.legal-research` | Legal research and authorities | proposal | potentially_sensitive | yes |
| 26 | `law.opinions` | Opinions and formal advice | proposal | potentially_sensitive | — |
| 27 | `law.knowhow-precedents` | Precedent bank and know-how | proposal | none | yes |
| 28 | `law.transactional-deal` | Transactional deal file | proposal | potentially_sensitive | — |
| 29 | `law.due-diligence` | Due diligence and disclosure | proposal | potentially_sensitive | — |
| 30 | `law.closing-binder` | Signing, closing and completion | proposal | potentially_sensitive | — |
| 31 | `law.contract-negotiation` | Contract drafting and negotiation work product | proposal | potentially_sensitive | — |
| 32 | `law.corporate-secretarial` | Corporate secretarial and entity records | proposal | potentially_sensitive | — |
| 33 | `law.regulatory-submission` | Regulatory filings and submissions | proposal | potentially_sensitive | — |
| 34 | `law.compliance-programme` | Compliance programme materials | proposal | potentially_sensitive | — |
| 35 | `law.investigation` | Investigations | proposal | potentially_sensitive | yes |
| 36 | `law.ip-prosecution` | Intellectual property prosecution | proposal | potentially_sensitive | — |
| 37 | `law.immigration-casework` | Immigration casework | proposal | potentially_sensitive | — |
| 38 | `law.family-law` | Family law matters | proposal | potentially_sensitive | — |
| 39 | `law.criminal-defence` | Criminal defence files | proposal | potentially_sensitive | — |
| 40 | `law.estates-administration` | Estates administration | proposal | potentially_sensitive | — |
| 41 | `law.conveyancing` | Property conveyancing | proposal | potentially_sensitive | — |
| 42 | `law.bar-admission-cle` | Admission, licensing and continuing legal education | proposal | potentially_sensitive | yes |
| 43 | `law.pro-bono` | Pro bono and publicly funded work | proposal | potentially_sensitive | yes |

---

## Entries

### 1. `law.matter-file` — Matter and case file

The file of one engagement — the matter — under which a practice opens, works and closes work for one client.

**provenance** `inference` — §5.7 “client engagements, research workflows, financial records, travel, legal matters” — the design names these as situations the template library should cover and states no fields for any of them.

**Schema**

| Field | Type | Ceiling | Example | Why this field, in this domain |
|---|---|---|---|---|
| `matter` | string | `validated` | Hale v Brant Holdings | The practice's own name for the engagement. Extends the §5.7 situation 'client engagements'; the design states no field. Validated because the matter name normally appears in a header or footer beside a matter reference, not in prose. |
| `matter_reference` | string | `validated` | 10432-0007 | A client-number/matter-number pair is the identifier every downstream artefact in this supercategory carries. It is only a fact when practice context corroborates it — see recognition.deterministic — because the same shape is an invoice, order, ticket or policy number. |
| `client` | string | `validated` | Brant Holdings Ltd | §3.8 names this field literally: “such as authored_by and target_school, or our_firm and client.” The design gives it no domain; the field name is the design's. |
| `our_firm` | string | `validated` | Ferris & Oyelaran LLP | §3.8: “A consulting document may mention the author’s firm and the client organization.” The two must not collapse into one organisation facet. §3.8 also settles that it is never a destination dimension: “It should avoid using authorship or creator identity as a destination dimension.” |
| `practice_area` | string | `llm_supported` | employment | Rarely stated on the document; usually inferable only from what the work is about. §3.5 places exactly this kind of conclusion with the LLM, and §3.6 requires a cited span before it becomes a fact. |
| `jurisdiction` | string | `llm_supported` | the courts of one named country or state | Load-bearing for this whole supercategory: court naming, identifier format and procedure differ by jurisdiction, so a downstream rule that does not know the jurisdiction cannot safely read a case identifier. Capped at `llm_supported` rather than `validated` on purpose — no court gazetteer is authored here (see this entry's open_question), so no deterministic rule can confirm it and contract rule 4 forbids claiming otherwise. law.opinions is the one entry that may claim `validated`, because a formal opinion states its governing law in a slot. |
| `responsible_lawyer` | string | `possible` | the fee-earner named in a signature block | Useful for search and explanation, never for placement. §3.8: “A folder should not become a collection point for everything produced by the same person or organization.” |

**Recognition**

| | |
|---|---|
| **deterministic** — pattern *plus* corroborating context | • a client-matter reference pattern co-occurring with practice-side context such as 'our ref' \| 'your ref' \| 'matter' \| 'engagement' \| 'fee earner' \| a client-account or disbursement line<br>• a matter name in the form '<party> v <party>' co-occurring with a named court or tribunal AND a case identifier — the party pair alone is not enough<br>• a practice letterhead or signature block naming a firm, together with a separately named client organisation in an addressee or 'client' slot (§3.8's two-facet split) |
| **needs LLM** | • a document that plainly belongs to one engagement but names it only in prose — 'further to your instructions'<br>• deciding whether an unlabelled advice note belongs to the matter it discusses or to the practice's know-how library<br>• reading the practice area from the substance of the work when no label states it |
| **never alone** | • a bare 'v' or 'vs' between two capitalised words — a fixture list, a film title and a comparison table all match<br>• a client or organisation name alone (§4.9: “A university name alone should not create a group”)<br>• the words 'matter', 'case' or 'file' alone<br>• a reference-number-shaped string with no practice context<br>• legal terminology alone — a terms-of-service PDF, a lease, a compliance slide deck and a news article all carry it |

**Work types** — engagement letter · matter opening form · file note · attendance note · advice note · matter status report · closing letter · file inventory

**Grouping reasons** — one matter for one client · several matters sharing one client where the client is the only shared spine · documents produced in one phase of one matter

**Template** — `client → matter → work phase → document type`  (time first: no)

> §5.5: “a parent dimension should provide the context required to understand the child”. A document type such as a witness statement is meaningless until the matter is known, and a matter number is ambiguous until the client is known. §5.5 also: “putting year first scatters related work across calendar folders”.

**Collides with**

| Domain | Signal that separates them | Design cite |
|---|---|---|
| `legal.contracts` | the same contract is legal-practice work product when it carries a matter reference or a fee-earner signature block, and a party's own record when it carries only the executing parties. Where a file is only the party's own copy, this domain DEFERS to slice 05. | §4.8 “an application packet does not silently absorb a document with a conflicting target institution” |
| `acad.course-enrollment` | a law student's file carries a course code plus academic context and no matter reference. §3.5's course rule fires and this domain must not. | §3.5 “becomes a course fact only when the engine finds a course-code pattern together with academic context” |
| `legal.litigation-dispute` | THE PRIMARY SEAM. 05's entry is the party's own working file about their own dispute and carries a `counsel_or_adviser` field — the adviser is a value in it. This entry is the adviser's file, in which the party is the `client`. Same dispute, two corpora, opposite roles. Slice 05 owns the party's own file; this slice owns the practitioner's. The mover is a practice-side signal — a matter reference, a fee-earner or counsel signature block, practice letterhead, an engagement letter. Absent one, this slice ABSTAINS and 05 wins. This is 05's own specialisation rule applied across the seam: 'the more specific domain wins where its own fields populate'. | — |

**Sensitivity** — `potentially_sensitive`. §2.9's phrase, applied here because §3.15 says 'Finance, identity, medical, and legal material should be implemented first as safety domains, meaning the system detects and protects them before any cloud or automated placement decision is allowed.' No handling class is assigned; handling classes are P7's (§8.4).

**Open question — Joseph's call, unresolved**

> Does the domain library ship ONE jurisdiction-neutral legal-practice family with `jurisdiction` as a fact field, or per-jurisdiction variants of each domain? Court names, case-identifier formats, filing-type names, party designations and procedural stage names differ by country and by court within one country. This catalogue is authored jurisdiction-neutrally at the schema level and confines jurisdiction-bound vocabulary to `work_types` and `recognition`, but a jurisdiction-neutral rule cannot recognise a local filing type, and a per-jurisdiction family multiplies the library. Joseph's call.

---

### 2. `law.client-intake` — Client intake and instructions

What a practice collects before it agrees to act — who the client is, what they want, and the identity evidence behind it.

**provenance** `inference` — §5.7 “client engagements, research workflows, financial records, travel, legal matters”

**Schema**

| Field | Type | Ceiling | Example | Why this field, in this domain |
|---|---|---|---|---|
| `prospective_client` | string | `direct` | the person or organisation named on an intake form | An intake form is a labeled form field, which §3.5 puts in the `direct` band: “Deterministic extractors create direct facts when the information comes from a reliable, explicit source, such as a content hash, EXIF timestamp, a document title, or a labeled form field.” |
| `client` | string | `validated` | Brant Holdings Ltd | §3.8 names the field. Distinct from `prospective_client` because intake may not result in an engagement, and a file that stops at intake must not acquire a client fact. |
| `instruction_summary` | string | `llm_supported` | what the prospective client has asked the practice to do | Prose only. §3.5 assigns exactly this to the LLM, and §3.6 requires the cited span to exist before it becomes a fact. |
| `intake_stage` | string | `validated` | enquiry received \| conflicts cleared \| declined \| engaged | Only when the document states it in a labeled slot or a decision line. A stage inferred from filename order is a clue, not a fact. |
| `our_firm` | string | `validated` | the practice receiving the enquiry | §3.8's second facet; needed here so an intake pack addressed TO a practice is not read as produced BY it. |

**Recognition**

| | |
|---|---|
| **deterministic** — pattern *plus* corroborating context | • an intake or new-client form whose labeled fields include a prospective client AND a description of the instructions or the sought work<br>• an identity-verification pack (identity document image plus proof of address) co-occurring with a practice's own reference or an intake form in the same bounded session |
| **needs LLM** | • an unstructured first email or letter of instruction with no form and no reference<br>• distinguishing an enquiry the practice declined from one it took on, where only the tone differs |
| **never alone** | • an identity document on its own — that is the identity safety domain, not legal practice<br>• the words 'instructions', 'enquiry' or 'new client' alone<br>• a contact record or vCard (§2.9 says a VCF “should normally be privacy-protected rather than used to create folder proposals”) |

**Work types** — enquiry record · intake form · letter of instruction · identity verification record · source-of-funds record · decline letter

**Grouping reasons** — one intake episode for one prospective client · an intake pack whose members are content-incoherent but purpose-coherent (§3.9)

**Template** — `client → intake episode → document type`  (time first: no)

> §5.5's rule — a document type such as 'proof of address' is meaningless until the person it belongs to is known. Depth stops at three: §5.9 warns against a level that 'produces only one child'.

**Collides with**

| Domain | Signal that separates them | Design cite |
|---|---|---|
| `pers.identity-document` | the identity documents inside an intake pack are identity material in their own right. §4.9 already covers them: “Rare but sensitive files such as passports, visas, and legal documents may be surfaced as protected records even when they do not meet a normal group-size threshold.” Intake claims the pack, not the passport. | §4.9 “Rare but sensitive files such as passports, visas, and legal documents may be surfaced as protected records” |
| `law.conflicts-check` | conflicts screening happens inside intake; the artefacts differ. A conflict search report names counterparties the client is adverse to, which an intake form does not. | — |

**Sensitivity** — `potentially_sensitive`. §2.9's phrase. Intake packs routinely carry identity documents, which §4.9 names among 'passports, visas, and legal documents'. No handling class is set here (§8.4 is P7's).

**Open question — Joseph's call, unresolved**

> §3.8's `our_firm` / `client` pair presumes an external adviser. In an in-house legal function the 'client' is a business unit of the same company and there is no external client to name, so intake, conflicts and billing either collapse or change meaning. Does an in-house corpus reuse this family with `client` bound to an internal business unit, or is it a separate domain family?

---

### 3. `law.conflicts-check` — Conflicts screening and information barriers

The record of checking whether a practice may act, and of the barriers put in place when it may act only conditionally.

**provenance** `proposal`

**Schema**

| Field | Type | Ceiling | Example | Why this field, in this domain |
|---|---|---|---|---|
| `client` | string | `validated` | the party the practice would act for | §3.8's field. A conflicts record is meaningless without the side being checked. |
| `screened_party` | string | `direct` | a counterparty, related entity or beneficial owner run through the search | A conflict search report lists searched names as labeled rows; §3.5 puts a labeled slot in the `direct` band. This is a role distinct from `client` — §3.8 requires roles that share an entity type to be separate fields. |
| `conflict_outcome` | string | `validated` | cleared \| cleared with barrier \| not cleared | Stated as a decision line on the report. If it is not stated, it must not be inferred from the absence of results. |
| `matter_reference` | string | `validated` | 10432-0007 | Links the check to the engagement it cleared. Same corroboration requirement as law.matter-file. |

**Recognition**

| | |
|---|---|
| **deterministic** — pattern *plus* corroborating context | • a search report listing multiple party names together with a clearance or decision line and a practice reference<br>• an information-barrier or ethical-wall memo naming two matters or two client sides within one practice |
| **needs LLM** | • an email exchange that resolves a conflict question in prose with no form and no decision line<br>• recognising that a list of company names is a conflicts search rather than a marketing list or a due-diligence entity list |
| **never alone** | • a list of company names — a CRM export, a due-diligence entity list and a conflicts search all look alike<br>• the words 'conflict' or 'conflicts' alone; the word appears in contract-drafting ('conflict of terms'), IT and HR documents<br>• the phrase 'information barrier' alone |

**Work types** — conflict search report · conflict waiver letter · information barrier memo · clearance record · engagement decline record

**Grouping reasons** — one clearance episode for one prospective matter · all checks recorded against one client

**Template** — `client → matter → document type`  (time first: no)

> §5.5's context rule: a waiver letter is only interpretable once the matter it waives for is known.

**Collides with**

| Domain | Signal that separates them | Design cite |
|---|---|---|
| `law.due-diligence` | both produce lists of entity names. Due diligence lists the target's entities and cites a data room; a conflicts search lists names against the practice's own client database and cites a clearance outcome. | — |

**Sensitivity** — `potentially_sensitive`. §2.9's phrase. A conflicts record can disclose that a practice was approached about a matter it never took, and names parties adverse to a client. No handling class is set here.

---

### 4. `law.engagement-terms` — Engagement letters, retainers and scope

The instrument that creates the engagement and states its scope, its fee basis and who is retained.

**provenance** `inference` — §5.7 “client engagements, research workflows, financial records, travel, legal matters”

**Schema**

| Field | Type | Ceiling | Example | Why this field, in this domain |
|---|---|---|---|---|
| `client` | string | `validated` | the retaining party | §3.8's field. The engagement letter is where `client` is stated most explicitly of anywhere in the corpus. |
| `our_firm` | string | `validated` | the retained practice | §3.8's paired field, which the design requires be kept distinct from the client rather than merged into one organisation facet. |
| `scope_of_work` | string | `llm_supported` | the work the practice agrees to perform | Written as prose under a scope heading. §3.5 assigns prose interpretation to the LLM; §3.6 requires the cited span to exist. |
| `fee_basis` | string | `llm_supported` | hourly \| fixed \| contingent \| capped \| conditional | Stated in a fees clause, but usually as prose rather than a labeled slot — 'charged on an hourly basis' is language, not a field, so §3.5 puts it with the LLM and §3.6 requires the cited span. The VALUE vocabulary is jurisdiction-bound: some bases are permitted in one jurisdiction and not another, so the field is neutral and values are corpus-derived (§3.12: “The system may create new values when it sees a new course, project, company, university, or event, but it should not invent new fields automatically.”). |
| `engagement_date` | date | `direct` | the date the letter is dated or countersigned | A dated signature block is a labeled slot. §3.10 governs the extraction: “Date extraction should be deliberately narrow.” |

**Recognition**

| | |
|---|---|
| **deterministic** — pattern *plus* corroborating context | • a letter or agreement whose headings include a scope-of-work clause AND a fees clause AND names a practice and a client as the two parties<br>• a countersigned terms-of-business document carrying a practice reference |
| **needs LLM** | • a short instruction email that functions as the retainer with no headings<br>• a variation letter that changes scope without repeating it, where the change is only meaningful against the original |
| **never alone** | • the words 'retainer', 'engagement' or 'terms of business' — 'engagement' is also a marketing and HR word, and 'retainer' appears in ordinary supplier contracts<br>• a signature block alone<br>• a fee schedule alone — that is a billing artefact, not an engagement instrument |

**Work types** — engagement letter · retainer agreement · terms of business · scope variation letter · fee agreement · termination of retainer letter

**Grouping reasons** — the engagement instrument together with its variations and its termination · one client's engagement terms across several matters

**Template** — `client → matter → document type`  (time first: no)

> §5.5's context rule. A scope variation is only readable against the matter it varies. §5.8 applies: a single-letter engagement should stay flat rather than acquire the full depth.

**Collides with**

| Domain | Signal that separates them | Design cite |
|---|---|---|
| `legal.contracts` | an engagement letter IS a contract. It belongs here when the practice is a party AND the document scopes legal services; a client's own copy of its engagement letter with its lawyers is that client's record and DEFERS to slice 05. | — |
| `law.time-and-billing` | both carry fee language. The engagement instrument states the basis; a bill states amounts actually charged for a period. | — |

**Sensitivity** — `potentially_sensitive`. §2.9's phrase. §8.4 names 'legal records' among the material a highly personal corpus can contain. No handling class is set here.

---

### 5. `law.time-and-billing` — Time recording and legal billing

The record of time recorded against a matter and the bills, narratives and disbursements produced from it.

**provenance** `proposal`

**Schema**

| Field | Type | Ceiling | Example | Why this field, in this domain |
|---|---|---|---|---|
| `matter_reference` | string | `validated` | 10432-0007 | A bill or time export without a matter reference cannot be placed; it is the join key for the whole supercategory. |
| `client` | string | `validated` | the billed party | §3.8's field. Distinct from the payer, who may be a third party — a separate role §3.8 would require as its own field if the corpus shows it. |
| `billing_period` | string | `validated` | a stated period on the bill | Read from a labeled period line, not parsed from filenames. §3.10: “Date extraction should be deliberately narrow.” |
| `record_type` | string | `validated` | time entry export \| fee note \| disbursement schedule \| write-off record | Determined by the document's own structure — a time export has fee-earner/date/narrative/units columns; a fee note has a total and a payment instruction. §3.11 already uses `record_type` as a Finance field name, deliberately reused rather than renamed. |
| `fee_earner` | string | `possible` | the timekeeper named in an export column | Search and explanation only. §3.8: “It should avoid using authorship or creator identity as a destination dimension.” |

**Recognition**

| | |
|---|---|
| **deterministic** — pattern *plus* corroborating context | • a spreadsheet or export whose column headers combine a timekeeper, a date, a narrative and a time unit, together with a matter reference (§2.9 gives P4 “sheet names, column headers, visible cell values”)<br>• an invoice or fee note carrying a matter reference AND a practice's own reference, as distinct from an ordinary supplier invoice |
| **needs LLM** | • a narrative-only work record with no matter reference, where the matter is identifiable from the narrative text<br>• separating a client bill from a supplier invoice the practice received on the same matter |
| **never alone** | • an invoice — the corpus is full of them and almost none are legal bills<br>• a spreadsheet with hours in it — timesheets exist in every profession<br>• a currency amount or a tax line<br>• the word 'billing' alone |

**Work types** — time entry export · draft bill · fee note · invoice · disbursement schedule · billing narrative · write-off record · fee estimate

**Grouping reasons** — one bill with its supporting time export and disbursement schedule · all billing for one matter · one billing period across a client's matters

**Template** — `client → matter → billing period → document type`  (time first: no)

> §5.5: “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders.” Period sits third — below the matter, above the document type — because a bill is only comparable within its matter.

**Collides with**

| Domain | Signal that separates them | Design cite |
|---|---|---|
| `biz.invoice-received` | the client's own copy of a legal bill is one of that client's invoices and DEFERS to the finance slice. It belongs here only when the file is the practice's own billing record — a time export, a draft bill, a write-off. | — |
| `career.payroll` | both are timesheets. This domain requires a matter reference; an employment timesheet has none. | — |

**Sensitivity** — `potentially_sensitive`. §2.9's phrase. A billing narrative describes what was done on a matter in detail and can be more revealing than the work product itself. No handling class is set here.

**Open question — Joseph's call, unresolved**

> Client-money / trust-account ledgers were deliberately NOT given an entry in this slice. They are regulated practice records with a real claim to this supercategory, but they are also account records, which §8.4 names (“account statements”) and the finance slice owns. Does client money belong to the finance slice, to this one, or to both with a primary-home convention under §6.9?

---

### 6. `law.matter-correspondence` — Matter correspondence and attendance notes

Letters, emails and notes of calls and meetings exchanged in the course of one matter.

**provenance** `proposal`

**Schema**

| Field | Type | Ceiling | Example | Why this field, in this domain |
|---|---|---|---|---|
| `matter_reference` | string | `validated` | 10432-0007 | Correspondence is the highest-volume material in a matter file and the least self-describing; without the reference there is nothing to place it by. |
| `correspondent` | string | `direct` | the other side's practice, the court, the client, a third party | §2.9 has the email extractor yield “sender, recipients, subject, sent date, thread identifiers”. A sender is a labeled slot, so `direct` per §3.5. |
| `correspondent_role` | string | `llm_supported` | opposing practice \| court \| client \| expert \| third party | §3.8 requires roles, not just entity types: “The agent should model these as distinct facets” Which role an organisation occupies in this matter is an interpretation, not a slot. |
| `correspondence_date` | date | `direct` | the sent or letter date | §2.9's email extractor yields 'sent date' as a labeled header; §3.10's narrow parsing applies. |

**Recognition**

| | |
|---|---|
| **deterministic** — pattern *plus* corroborating context | • an email or letter carrying an explicit 'our ref' / 'your ref' pair, which is a practice-side convention rather than a general business one<br>• a note headed as an attendance note, telephone note or meeting note that also carries a matter reference<br>• a letter addressed between two named practices about a matter identified by a case or matter identifier |
| **needs LLM** | • an email thread with no reference where the matter is only identifiable from the subject matter discussed<br>• distinguishing correspondence that is itself the advice from correspondence that merely transmits a document |
| **never alone** | • an email — §2.9 already treats mail generically; being email says nothing about a matter<br>• the presence of a practice name in a signature — practices send marketing and administrative mail too<br>• the words 'without prejudice' or 'confidential' alone: they are used loosely in ordinary business email and are not proof of a matter |

**Work types** — letter · email · attendance note · telephone note · meeting note · file note · enclosure schedule

**Grouping reasons** — one thread on one matter · correspondence with one correspondent across a matter · an exchange whose members are content-incoherent but purpose-coherent (§3.9)

**Template** — `client → matter → correspondent role → document type`  (time first: no)

> §5.5's context rule. Correspondent role is worth a level only when a matter has several sides; §5.9 requires warning 'when a level produces only one child', so a two-party matter should stay flatter.

**Collides with**

| Domain | Signal that separates them | Design cite |
|---|---|---|
| `law.matter-file` | attendance notes sit in both. Treat correspondence as the sub-file of the matter, not a rival to it; the split matters only if the user chooses to branch on it. | — |
| `pers.correspondence` | §8.4 names “private correspondence” as its own category of sensitive material. Personal mail from a lawyer's own account is not matter correspondence unless a matter reference or a named matter corroborates it. | §8.4 “identity documents, account statements, tax records, medical information, legal records” |

**Sensitivity** — `potentially_sensitive`. §2.9's phrase, which §2.9 applies to email directly: it requires 'treating addresses and message content as potentially sensitive'. No handling class is set here.

---

### 7. `law.limitation-and-diary` — Deadlines, limitation dates and court diary

The dated obligations of a matter — the dates a step must be taken by, and the record that they were diarised.

**provenance** `proposal`

**Schema**

| Field | Type | Ceiling | Example | Why this field, in this domain |
|---|---|---|---|---|
| `matter_reference` | string | `validated` | 10432-0007 | A deadline with no matter is unplaceable and unactionable. |
| `deadline_type` | string | `validated` | the named step a date attaches to | Read from the document's own label. The VALUE vocabulary is heavily jurisdiction-bound — the names of steps and the rules that generate them differ by court — so the field is neutral and values are corpus-derived. |
| `due_date` | date | `direct` | the stated date | Read from a labeled date slot in a timetable, order or calendar entry; §2.9's ICS extractor yields “event title, start and end time”. §3.10's narrow parsing applies and no date is computed. |
| `issuing_authority` | string | `validated` | the court, tribunal or body that set the date | Distinguishes a court-imposed date from an internal target — different consequences, so §3.8's roles principle makes them different values of a stated field rather than one blurred 'date'. |

**Recognition**

| | |
|---|---|
| **deterministic** — pattern *plus* corroborating context | • a timetable or directions table pairing named procedural steps with dates, appearing alongside a case identifier<br>• an ICS calendar entry (§2.9) whose title carries a matter reference or a case identifier<br>• a diary or limitation record listing a matter reference against a single controlling date |
| **needs LLM** | • a letter that states a deadline in prose and nowhere else<br>• recognising that a date table is a court timetable rather than a project plan |
| **never alone** | • a date, a date range, or a table of dates — §3.10 exists precisely because “file names and documents frequently contain numbers that look like years”<br>• a calendar file — most calendar entries are not legal deadlines<br>• the word 'deadline' or 'due' alone |

**Work types** — directions timetable · limitation record · diary entry · reminder letter · hearing notice · key dates schedule

**Grouping reasons** — all dated obligations of one matter · one procedural timetable and the correspondence confirming it

**Template** — `client → matter → document type`  (time first: no)

> §5.5's rule against time-first for record domains applies with unusual force here: a folder tree keyed on due dates would scatter one matter's obligations across the calendar and would go stale the moment a date moved.

**Collides with**

| Domain | Signal that separates them | Design cite |
|---|---|---|
| `law.orders-and-judgments` | a court order often IS the timetable. The order is the instrument; the diary record is the practice's derived note of it. Both may cite the same dates. | — |

**Sensitivity** — `potentially_sensitive`. §2.9's phrase; a deadline schedule names the matter and its posture. No handling class is set here.

---

### 8. `law.pleadings` — Pleadings and originating process

The documents that state each side's case to the court and define what the proceeding is about.

**provenance** `proposal`

**Schema**

| Field | Type | Ceiling | Example | Why this field, in this domain |
|---|---|---|---|---|
| `case_identifier` | string | `validated` | the identifier the court assigns the proceeding | A case identifier is a strong identifier but a weak pattern: its FORMAT differs by jurisdiction and by court, and a same-shaped string is an invoice or policy number elsewhere. It becomes a fact only with the corroboration in recognition.deterministic. |
| `court` | string | `validated` | the named court or tribunal | Read from the caption or heading block. The gazetteer of court names is jurisdiction-specific and is not authored here — see law.matter-file's open_question. |
| `party` | string | `validated` | a named party to the proceeding | Read from the caption's party block, never from a name appearing in the body. §3.7's “positional weighting” is the mechanism: a caption is not a footer. |
| `party_role` | string | `validated` | the designation the caption gives a party | §3.8 requires roles as distinct facets. The role VOCABULARY is jurisdiction-bound (the words for a claiming and a defending party differ by system and by proceeding type), so the field is neutral and values are corpus-derived. |
| `pleading_type` | string | `validated` | the document's own self-description in its title block | Pleadings name themselves in a title block, which is the most reliable slot on the document. The names are jurisdiction-bound and are not enumerated here. |
| `jurisdiction` | string | `llm_supported` | the legal system the proceeding sits in | Usually implicit in the court name rather than stated. Required so a downstream reader knows which identifier format and vocabulary applies. |

**Recognition**

| | |
|---|---|
| **deterministic** — pattern *plus* corroborating context | • a case-identifier pattern co-occurring with a named court AND a party block — the three together, never the identifier alone. This is §3.5's model applied: the identifier is the pattern, the court and party block are the corroborating context<br>• a document title block naming a pleading type together with a caption containing two or more party designations<br>• a court filing stamp or seal region (from OCR per §2.7) co-occurring with a case identifier |
| **needs LLM** | • a draft pleading with the caption not yet completed<br>• a pleading in a language or system whose caption conventions the rules do not cover<br>• distinguishing a real pleading from a precedent copy of one held in a know-how library |
| **never alone** | • a case-identifier-shaped string with no court and no party block<br>• a party name — §4.9's principle transfers directly: 'A university name alone should not create a group'<br>• a statute or case citation — these appear in academic essays, journalism and terms of service<br>• the words 'claim', 'complaint', 'defence' or 'petition' alone<br>• a date |

**Work types** — originating document · statement of case · answer or defence · counterclaim · reply · amended pleading · particulars · list of issues

**Grouping reasons** — all pleadings in one proceeding · one pleading with its amendments and drafts as a version family (§2.9) · pleadings sharing a case identifier across parties

**Template** — `client → matter → proceeding → document type`  (time first: no)

> §5.5's context rule. A 'proceeding' level is only worth creating when one matter carries more than one proceeding; §5.9 requires the interface to warn when 'a level produces only one child', so most matters should collapse it.

**Collides with**

| Domain | Signal that separates them | Design cite |
|---|---|---|
| `law.knowhow-precedents` | a precedent bank holds pleadings that are real in form and dead in fact. The distinguishing signal is a live case identifier and a filing stamp; a precedent typically has placeholders or a redacted caption. | — |
| `acad.course-enrollment` | a law student's mooting bundle contains a pleading-shaped document with a fictitious caption. The course code plus academic context wins (§3.5); this domain must abstain. | §3.5 “becomes a course fact only when the engine finds a course-code pattern together with academic context” |
| `legal.court-records` | 05's entry claims a document 'when it is issued or sealed' and holds it as the party's copy of the formal record. This entry claims the practice's drafting and filing of it. A sealed copy in a non-practitioner corpus is 05's. | — |

**Sensitivity** — `potentially_sensitive`. §2.9's phrase. Pleadings name parties and allegations; §8.4 names 'legal records' among the material the corpus can contain. Publicness varies by jurisdiction and by proceeding, which is exactly why no handling class is assigned here (§8.4 is P7's).

---

### 9. `law.court-filing-record` — Filing, service and docket records

The evidence that a document was lodged with a court and reached the other side — receipts, stamped copies, docket extracts and proofs of service.

**provenance** `proposal`

**Schema**

| Field | Type | Ceiling | Example | Why this field, in this domain |
|---|---|---|---|---|
| `case_identifier` | string | `validated` | the identifier on the receipt or docket line | The join key between a filing record and the document it evidences. Same corroboration requirement as law.pleadings — never the pattern alone. |
| `court` | string | `validated` | the receiving court or registry | A filing record is issued BY a court, so the court is a labeled slot on it rather than an inference. |
| `filed_document_type` | string | `validated` | what was lodged, as the record names it | Read from the record's own description line, which is a different and often more reliable slot than the filed document's own title. |
| `filing_date` | date | `direct` | the date of lodgement or the stamp date | A filing stamp or receipt timestamp is a labeled slot, so `direct` per §3.5. §3.10's narrow parsing applies and no deadline is computed from it. |
| `served_party` | string | `direct` | the party a proof of service names as served | Proofs of service are structured forms with a served-party slot. §3.8 makes this a distinct role from `party`. |

**Recognition**

| | |
|---|---|
| **deterministic** — pattern *plus* corroborating context | • an electronic filing confirmation or receipt carrying a case identifier AND a court or registry name AND a timestamp<br>• a page bearing a court filing stamp or seal recovered by OCR (§2.7), together with a case identifier elsewhere on the same page<br>• a proof-of-service or certificate-of-service form whose labeled fields include the served party, the method and the date |
| **needs LLM** | • a screenshot of a filing portal with no machine-readable text beyond OCR, where the portal must be recognised as a court system rather than a generic web page — §3.5 gives exactly this example, that the LLM may “determine that an OCR”d screenshot is an application portal rather than a generic image'<br>• a foreign-language registry receipt |
| **never alone** | • a receipt or confirmation email — the corpus is full of them<br>• a stamp-shaped image region: OCR mistakes seals, watermarks and 'DRAFT' overlays for each other<br>• a tracking or courier number<br>• the word 'filed' — it is also an ordinary English past participle |

**Work types** — filing receipt · stamped filed copy · docket extract · case summary from a registry · proof of service · certificate of service · rejection or deficiency notice

**Grouping reasons** — a filed document with its receipt and its proof of service · all filing records for one proceeding · one filing episode as a bounded session (§3.9 — a session is a purpose clue and never proof)

**Template** — `client → matter → proceeding → document type`  (time first: no)

> §5.5's context rule; a receipt is meaningless away from what it evidences. Deliberately the same order as law.pleadings so a filed document and its receipt land adjacent rather than in parallel trees.

**Collides with**

| Domain | Signal that separates them | Design cite |
|---|---|---|
| `law.pleadings` | a stamped filed copy is BOTH the pleading and the filing evidence. §6.9's shared-material policy governs: 'The user“s frozen tree should therefore include a policy for shared material: a shared branch, a primary-home convention, a reference or alias convention, or mandatory review.” | §6.9 “The user’s frozen tree should therefore include a policy for shared material” |
| `legal.court-records` | 05 holds the party's copy of court-issued documents including fee records and notices. This entry holds the practice's filing and service evidence. Slice 05 owns the party's own file; this slice owns the practitioner's. The mover is a practice-side signal — a matter reference, a fee-earner or counsel signature block, practice letterhead, an engagement letter. Absent one, this slice ABSTAINS and 05 wins. This is 05's own specialisation rule applied across the seam: 'the more specific domain wins where its own fields populate'. | — |

**Sensitivity** — `potentially_sensitive`. §2.9's phrase. A proof of service carries a served party's address. No handling class is set here.

**Open question — Joseph's call, unresolved**

> Should a court or case identifier ever become a folder LEVEL? One dispute can carry several identifiers — a first-instance number, an appeal number, a registry reference — and they change as the case moves. A tree keyed on identifier splits one dispute; a tree keyed on the matter keeps it together but loses the identifier as a navigation handle. §5.4 says a template “defines the dimensions that are meaningful for one type of material”, and this is a dimension the design does not settle.

---

### 10. `law.motions-and-briefs` — Interlocutory applications and written submissions

Documents asking a court to decide something short of the final outcome, and the written argument supporting them.

**provenance** `proposal`

**Schema**

| Field | Type | Ceiling | Example | Why this field, in this domain |
|---|---|---|---|---|
| `case_identifier` | string | `validated` | the identifier in the caption | Same rule as law.pleadings: a strong identifier with a jurisdiction-dependent format that is only a fact when a court and a party block corroborate it. |
| `court` | string | `validated` | the court asked to decide | Read from the caption block. Needed because the same dispute can generate applications in more than one court. |
| `relief_sought` | string | `llm_supported` | what the applying party asks the court to order | Stated as prose in a prayer or conclusion. §3.5 assigns this to the LLM; §3.6 requires the cited span to exist in stored evidence before it becomes a fact. |
| `moving_party` | string | `validated` | the party bringing the application | §3.8's roles principle: the party bringing an application is a different facet from `party` generally, and the same organisation can be both across a matter. |
| `submission_type` | string | `validated` | the document's own self-description | Read from the title block. The vocabulary is jurisdiction-bound and is deliberately NOT enumerated here — the word for a written submission differs by system, and one common word means two different documents in two systems (see this entry's open_question). |

**Recognition**

| | |
|---|---|
| **deterministic** — pattern *plus* corroborating context | • a case-identifier pattern with a court name AND a party block AND a title block naming an application or submission type<br>• a document containing both a table of authorities section heading and a caption with a case identifier<br>• a certificate-of-compliance or word-count block co-occurring with a case identifier — a court-imposed formality that ordinary documents do not carry |
| **needs LLM** | • reading what relief is actually sought when the prayer is discursive<br>• distinguishing a submission filed in the proceeding from a draft the practice never filed<br>• a submission whose caption conventions the rules do not cover |
| **never alone** | • a table of case citations — law review articles, textbooks, student essays and journalism all carry them<br>• the word 'motion', 'application', 'submission' or 'brief' — 'brief' in particular denotes different documents in different systems and is an ordinary English adjective<br>• a legal argument structure<br>• a statute reference |

**Work types** — notice of application · written submission · supporting affidavit or declaration · table of authorities · responding submission · reply submission · draft order

**Grouping reasons** — an application with its supporting evidence and the responding submission · all submissions in one proceeding · one submission with its drafts as a version family (§2.9's “duplicate and version-family signals”)

**Template** — `client → matter → proceeding → application → document type`  (time first: no)

> §5.5's context rule; a responding submission is unreadable except against the application it answers. §5.8 applies — 'The product should not force every branch to use the full template' — so a matter with one application should collapse the application level.

**Collides with**

| Domain | Signal that separates them | Design cite |
|---|---|---|
| `law.legal-research` | a research memo and a submission both marshal authorities. A submission carries a caption and asks a court for something; a memo advises a reader and asks nobody for anything. | — |
| `acad.course-enrollment` | a moot or seminar submission looks identical in form. §3.5's course rule takes precedence when a course code and academic context are present. | §3.5 “becomes a course fact only when the engine finds a course-code pattern together with academic context” |

**Sensitivity** — `potentially_sensitive`. §2.9's phrase. §8.4 names 'legal records' among the corpus's sensitive material. No handling class is set here.

**Open question — Joseph's call, unresolved**

> The word 'brief' is a false friend across jurisdictions — in some systems it names the written argument filed with an appellate court, in others it names the instructions a solicitor sends to counsel, which is a completely different domain with a different schema. Should the catalogue avoid the word entirely (as this entry does), or carry per-jurisdiction `work_types` vocabularies keyed on the `jurisdiction` fact? Same question as law.matter-file's, in its sharpest form.

---

### 11. `law.orders-and-judgments` — Orders, judgments and directions

What the court decided or directed — the instruments that bind the parties and reset the matter's posture.

**provenance** `proposal`

**Schema**

| Field | Type | Ceiling | Example | Why this field, in this domain |
|---|---|---|---|---|
| `case_identifier` | string | `validated` | the identifier in the caption | The join key to the proceeding. Corroboration requirement as in law.pleadings. |
| `court` | string | `validated` | the deciding court | An order is issued BY a court, so the court name is a header slot rather than an inference. Also determines the identifier format for everything else in the proceeding. |
| `decision_date` | date | `direct` | the date the order or judgment bears | A dated seal or hand-down line is a labeled slot, so `direct` per §3.5. §3.10 governs parsing; no consequential deadline is computed from it. |
| `decision_type` | string | `validated` | how the instrument describes itself | Read from the title block. Names differ by jurisdiction and by court, so values are corpus-derived rather than enumerated. |
| `deciding_judge` | string | `possible` | the judge or panel named in the header | Search and explanation only. §3.8: “A folder should not become a collection point for everything produced by the same person or organization.” |

**Recognition**

| | |
|---|---|
| **deterministic** — pattern *plus* corroborating context | • a court seal or hand-down block recovered by OCR (§2.7) co-occurring with a case identifier AND a party block<br>• a title block naming an order, judgment or directions instrument, together with a court name and a case identifier<br>• an ordering or operative section — a numbered directions list following a decision heading — inside a document that also carries a case identifier |
| **needs LLM** | • a draft order circulated between the parties before it was made, which is formally identical but not yet an order<br>• an unreported decision distributed as plain text with the header stripped<br>• reading the practical effect of a decision when the operative part is discursive |
| **never alone** | • the words 'order', 'judgment', 'ruling' or 'decision' — every one is an ordinary business word<br>• a numbered list of directions<br>• a case citation — a reported judgment cited inside an essay, a news article or a textbook is not this matter's order<br>• a seal-shaped image region: OCR confuses seals, logos and watermarks |

**Work types** — order · judgment · reasons for decision · directions · consent order · sealed order · draft order · note of an oral ruling

**Grouping reasons** — all orders in one proceeding · an order with the application that produced it and the submissions behind it · a judgment with its reasons and its consequential orders

**Template** — `client → matter → proceeding → document type`  (time first: no)

> §5.5's context rule. Consciously NOT keyed on decision date despite these being the most date-defined documents in the supercategory — §5.5: 'putting year first scatters related work across calendar folders', and one proceeding's orders belong together.

**Collides with**

| Domain | Signal that separates them | Design cite |
|---|---|---|
| `law.legal-research` | a judgment held as an AUTHORITY (someone else's case, kept because it is useful law) and a judgment held as an INSTRUMENT (this matter's own order) are the same document type in two domains. The matter's case identifier is what separates them. | — |
| `law.limitation-and-diary` | an order that sets a timetable is both the instrument and the source of the diary dates. | — |
| `legal.court-records` | an order is court-issued, which is exactly 05's claim. In a practitioner corpus it also belongs to the matter; in a party's corpus it is 05's alone and this entry must not fire. | — |

**Sensitivity** — `potentially_sensitive`. §2.9's phrase. Whether a given order is public varies by jurisdiction and by proceeding type, and some are expressly restricted — which is why no handling class is assigned here (§8.4 is P7's).

---

### 12. `law.appeals` — Appeals and the appellate record

The challenge to a decision and the compiled record and submissions that carry it to a higher court.

**provenance** `proposal`

**Schema**

| Field | Type | Ceiling | Example | Why this field, in this domain |
|---|---|---|---|---|
| `appeal_identifier` | string | `validated` | the identifier the appellate court assigns | §3.8's roles principle applied to identifiers: the appeal number and the first-instance number are two different values in two different roles, and collapsing them loses which court a document belongs to. |
| `lower_case_identifier` | string | `validated` | the identifier of the decision under appeal | The only reliable link between the appeal file and the matter it came from. Appellate documents normally state both in the caption. |
| `appellate_court` | string | `validated` | the court hearing the appeal | Read from the caption. The appellate structure and its naming are jurisdiction-specific and are not enumerated here. |
| `decision_under_appeal` | string | `llm_supported` | the order or judgment being challenged | Often described in prose rather than identified. §3.6 requires the model's cited span to exist before this becomes a fact. |
| `appeal_stage` | string | `validated` | the stage the document belongs to, as stated | Appeals have distinct stages with distinct paperwork; the stage is normally on the face of the document. Stage names are jurisdiction-bound and are corpus-derived. |

**Recognition**

| | |
|---|---|
| **deterministic** — pattern *plus* corroborating context | • a caption carrying TWO case identifiers together with a court name naming an appellate body — the two-identifier pattern is close to unique to appeals<br>• a title block naming a notice of appeal or an appellate submission alongside a case identifier<br>• an appeal record or transcript index co-occurring with a case identifier and page or tab numbering |
| **needs LLM** | • an appeal document whose caption shows only the new identifier, where the underlying matter must be recognised from the facts recited<br>• deciding whether a bundle is the appeal record or the first-instance trial bundle re-used |
| **never alone** | • the word 'appeal' — it is an ordinary English word and also names an unrelated fundraising document<br>• a second reference number on a document<br>• a table of contents with tab numbers — every bundle has one |

**Work types** — notice of appeal · permission or leave application · appellant's submission · respondent's submission · appeal record or bundle · transcript index · appellate judgment

**Grouping reasons** — one appeal from one decision · an appeal together with the first-instance material it reproduces · successive appeals in one dispute

**Template** — `client → matter → appeal → document type`  (time first: no)

> §5.5's context rule. The appeal sits UNDER the matter rather than beside it, because the design's principle is that a parent supplies the context to read the child, and an appeal is unreadable without the dispute it comes from.

**Collides with**

| Domain | Signal that separates them | Design cite |
|---|---|---|
| `law.trial-preparation` | an appeal record physically reproduces trial-bundle documents. §6.9's shared-material policy governs which copy has the primary home. | §6.9 “The user’s frozen tree should therefore include a policy for shared material” |
| `law.orders-and-judgments` | the decision under appeal lives in both files. Its home is the proceeding that produced it; the appeal file holds a copy. | — |

**Sensitivity** — `potentially_sensitive`. §2.9's phrase; the appeal file reproduces the whole matter. No handling class is set here.

---

### 13. `law.discovery-requests` — Discovery and disclosure requests and responses

The formal demands each side makes for the other's documents and information, and the answers given.

**provenance** `proposal`

**Schema**

| Field | Type | Ceiling | Example | Why this field, in this domain |
|---|---|---|---|---|
| `case_identifier` | string | `validated` | the identifier in the caption | Discovery paperwork is captioned like a pleading and joins to the proceeding by the same key. |
| `requesting_party` | string | `validated` | the party demanding | §3.8's roles requirement is acute here: the same organisation is the requesting party in one document set and the responding party in another, and one merged `party` field would make the file unreadable. |
| `responding_party` | string | `validated` | the party answering | The paired role. Kept separate for the reason §3.8 gives for `our_firm` and `client`. |
| `request_set` | string | `validated` | the identifier of one numbered set of requests | Requests come in numbered sets and responses answer a set item by item; without the set, a response cannot be matched to its request. |
| `discovery_instrument_type` | string | `validated` | how the document names itself | Discovery devices and their names are among the most jurisdiction-bound vocabulary in this whole supercategory — several common devices do not exist at all in some systems. The field is neutral; values are corpus-derived. |

**Recognition**

| | |
|---|---|
| **deterministic** — pattern *plus* corroborating context | • a captioned document containing a numbered request series AND a party-to-party demand or response structure<br>• a response document whose numbering mirrors a request set, with objection or answer text under each number<br>• a disclosure list or index of documents carrying a case identifier |
| **needs LLM** | • an informal request made by letter that functions as discovery<br>• distinguishing a genuine objection from a partial answer where the response text is discursive |
| **never alone** | • a numbered question list — surveys, audits, questionnaires and RFP responses all match<br>• the word 'discovery' or 'disclosure' — both are common in business, product and finance documents<br>• the word 'request'<br>• an index of documents |

**Work types** — request set · response to requests · objections · disclosure list · document index · certification of completeness · meet-and-confer correspondence

**Grouping reasons** — a request set with its response and any objections · all discovery in one proceeding · discovery directed at one party across sets

**Template** — `client → matter → proceeding → party direction → document type`  (time first: no)

> §5.5's context rule, with one addition specific to this domain: 'party direction' — requests we made versus requests made of us — is the dimension practitioners actually navigate by, and without it a folder mixes the two sides of every exchange. §5.9's warning applies where a matter has only one direction.

**Collides with**

| Domain | Signal that separates them | Design cite |
|---|---|---|
| `law.document-review` | a disclosure list is produced BY document review. The list is an instrument served on the other side; the review record is internal work product and stays internal. | — |
| `law.ediscovery-production` | the response promises documents; the production delivers them. Different artefacts, different schemas — the production carries range identifiers and custodians, the response does not. | — |
| `legal.litigation-dispute` | 05 lists 'disclosure bundle' among its work types, held as the party's copy. The request-and-response instruments and their numbering are this entry's. | — |

**Sensitivity** — `potentially_sensitive`. §2.9's phrase. Discovery material is other people's documents held under an obligation, which is precisely the case §3.15 protects: “Finance, identity, medical, and legal material should be implemented first as safety domains” No handling class is set here.

---

### 14. `law.document-review` — Document review work product

The internal record of reading a document population and deciding what each document is and what happens to it.

**provenance** `proposal`

**Schema**

| Field | Type | Ceiling | Example | Why this field, in this domain |
|---|---|---|---|---|
| `matter_reference` | string | `validated` | 10432-0007 | Review work product is almost never self-describing; the matter reference is usually the only thing on it that identifies the engagement. |
| `review_population` | string | `validated` | the named set of documents under review | Populations are named in review platform exports as a labeled column or export header; the name is the join key between a coding report and the documents it describes. |
| `review_batch` | string | `validated` | the identifier of one assigned batch | Batches are the unit of work; a coding report without its batch cannot be reconciled. |
| `coding_field` | string | `direct` | a decision column recorded against each document | A review export is a spreadsheet; §2.9 has the spreadsheet extractor yield “sheet names, column headers, visible cell values”. A column header is a labeled slot, so `direct`. The catalogue records that the column EXISTS and what it is called — it does not evaluate what a coding value means. |
| `reviewer` | string | `possible` | the person a batch is assigned to | Search and explanation only. §3.8: “It should avoid using authorship or creator identity as a destination dimension.” |

**Recognition**

| | |
|---|---|
| **deterministic** — pattern *plus* corroborating context | • a spreadsheet whose column headers combine a per-document identifier with review decision columns AND that carries a matter reference — the identifier column alone is not enough<br>• a review platform export whose header block names a workspace or population together with a matter reference<br>• a batch assignment or reviewer productivity report carrying both a population name and a matter reference |
| **needs LLM** | • a review protocol written as prose with no structure to key on<br>• distinguishing a review coding sheet from an ordinary document inventory or asset register |
| **never alone** | • a spreadsheet with an ID column — inventories, asset registers, bug trackers and mailing lists all match<br>• the word 'review' — it is one of the most overloaded words in any corpus<br>• the words 'responsive', 'relevant' or 'privileged' appearing as column headers: a header naming a legal concept is evidence about the SPREADSHEET, never a determination about any document, and this catalogue records no such determination (see this entry's open_question) |

**Work types** — review protocol · coding sheet or export · batch assignment record · quality control report · review log · document index · privilege log

**Grouping reasons** — one review population across its batches and reports · all review work product for one matter · a protocol with the coding output it governed

**Template** — `client → matter → review population → document type`  (time first: no)

> §5.5's context rule. A coding export is meaningless outside the population it codes, and populations rarely span matters.

**Collides with**

| Domain | Signal that separates them | Design cite |
|---|---|---|
| `law.ediscovery-production` | review decides what is produced; production is what was delivered. A production log carries a delivered range and a delivery date; a coding sheet carries decisions and no delivery. | — |
| `law.discovery-requests` | as above — the served list versus the internal record. | — |

**Sensitivity** — `potentially_sensitive`. §2.9's phrase. Review work product describes other parties' documents in detail and is internal by nature. No handling class is set here.

**Open question — Joseph's call, unresolved**

> PRIVILEGE. A privilege log is a real, named work-product artefact and this entry lists it as a `work_type`. Nothing in this catalogue asserts that any file IS privileged, and no `privileged` field, flag or value is defined anywhere in this slice — deliberately. Privilege is a legal determination made by a lawyer about a specific document in a specific context; a document bearing a 'privileged and confidential' legend is not thereby privileged, and a privileged document often bears no legend at all. A wrong assertion is harmful in both directions. Joseph's calls, and they are two: (1) may the system record an OBSERVATION that a document bears a privilege legend — which is a fact about the text, not about the document's status — while still asserting nothing about privilege? (2) Does P7's handling-class vocabulary (§8.4) need a class for legal-professional-privilege material, given that §8.4's five classes are about personal sensitivity and privilege is a different axis entirely? Question (2) is a P7 vocabulary question and is not answered here.

---

### 15. `law.ediscovery-production` — Electronic productions

A delivered set of documents with its numbering, its load files and the record of what went out to whom.

**provenance** `proposal`

**Schema**

| Field | Type | Ceiling | Example | Why this field, in this domain |
|---|---|---|---|---|
| `production_identifier` | string | `validated` | the name or number of one delivered set | Productions are the unit that is delivered, tracked and disputed; the identifier is stated on the cover letter and the load file. |
| `production_range` | string | `validated` | the first and last document identifier in the set | The range is the only durable link between a delivered file and the production it came in. The NUMBERING CONVENTION is jurisdiction- and vendor-specific — one widely used stamping convention is a common-law practice convention, not a universal one — so the field is neutral and the pattern is not hard-coded here. |
| `custodian` | string | `direct` | the person or system a document was collected from | A load file carries a custodian column, which is a labeled slot, so `direct` per §3.5. §3.8's roles rule matters: a custodian is not an author and not a party. |
| `producing_party` | string | `validated` | the party delivering the set | Distinct role from `receiving_party`; a matter file holds sets going in both directions and merging them is the most likely serious error in this domain. |
| `production_date` | date | `direct` | the delivery date on the cover letter | A dated cover letter is a labeled slot. §3.10's narrow parsing applies. |

**Recognition**

| | |
|---|---|
| **deterministic** — pattern *plus* corroborating context | • a load file — a delimited data file whose columns pair a per-document identifier with a custodian and a native or image path — co-occurring with a matter reference or case identifier<br>• a production cover letter naming a production identifier AND a document-identifier range AND a receiving party<br>• a directory of images or natives whose filenames are a contiguous stamped identifier series, together with a load file in the same set |
| **needs LLM** | • a production delivered with no cover letter, where the set must be recognised from the load file alone<br>• deciding whether an inbound set is a production from the other side or the practice's own outbound copy |
| **never alone** | • a delimited data file — §2.9 routes CSV and TSV generically and most of them are not load files<br>• a directory of sequentially numbered files — scanners, cameras and exports all produce these<br>• a stamped-looking identifier on one page with no load file and no cover letter<br>• the word 'production' — it means manufacturing, media and deployment in the same corpus |

**Work types** — production cover letter · load file · image set · native set · production log · clawback or replacement notice · production index

**Grouping reasons** — one production as a delivered set — cover letter, load file, and payload · all productions between one pair of parties · a production with the replacement set that superseded it (§2.9's version-family signals)

**Template** — `client → matter → party direction → production → document type`  (time first: no)

> §5.5's context rule. Direction before production, because an inbound and an outbound set with adjacent identifiers must never sit in one folder. §5.9's live feedback matters here: a production can hold very large numbers of files and a per-document level would create “a large number of tiny folders”.

**Collides with**

| Domain | Signal that separates them | Design cite |
|---|---|---|
| `law.document-review` | review produces the decision, production produces the delivery. Distinguished by the load file and the cover letter. | — |
| `law.evidence-exhibits` | a produced document later used as an exhibit acquires a second identifier. Both identifiers are facts about the same file; §6.9's shared-material policy decides its home. | §6.9 “The user’s frozen tree should therefore include a policy for shared material” |

**Sensitivity** — `potentially_sensitive`. §2.9's phrase. A production is another party's document population held under an obligation, frequently including personal data of people who are not parties. No handling class is set here.

**Open question — Joseph's call, unresolved**

> Document-identifier stamping conventions are jurisdiction- and vendor-specific, and the best-known one is a common-law practice convention rather than a universal standard. Should the catalogue carry a per-jurisdiction pattern list for production numbering, or refuse patterns entirely and require the corroborating load file in every case (which is what this entry currently does)? Refusing patterns is safer and will miss loose stamped pages that arrive without their load file.

---

### 16. `law.evidence-exhibits` — Evidence and exhibits

The material a party puts before a decision-maker, and the identifiers and schedules that let it be referred to.

**provenance** `proposal`

**Schema**

| Field | Type | Ceiling | Example | Why this field, in this domain |
|---|---|---|---|---|
| `exhibit_identifier` | string | `validated` | the label an exhibit is referred to by | The exhibit label is how the document is referenced in every transcript, submission and order that follows. Labelling conventions are jurisdiction-bound, so the field is neutral and values are corpus-derived. |
| `case_identifier` | string | `validated` | the identifier of the proceeding | Without it an exhibit label is ambiguous — labels restart in every proceeding. |
| `tendering_party` | string | `validated` | the party putting the material forward | §3.8's roles principle. Which side tendered an exhibit is usually more useful for retrieval than what the exhibit is. |
| `underlying_document_type` | string | `llm_supported` | what the exhibit is when read as an ordinary document | An exhibit can be anything — a contract, a photograph, a message thread, a spreadsheet. §3.11's multi-domain rule applies directly: the same file may hold this domain's facts AND the facts of whatever the underlying document is, and neither is dropped. |
| `exhibit_source` | string | `validated` | the witness statement or production the exhibit is attached to | Exhibits are almost always attached to something. The attachment is the link that makes an exhibit interpretable. |

**Recognition**

| | |
|---|---|
| **deterministic** — pattern *plus* corroborating context | • an exhibit cover sheet or stamp — an identifier plus an attesting line — recovered from the page or by OCR (§2.7), together with a case identifier<br>• an exhibit schedule or index pairing labels with document descriptions, carrying a case identifier<br>• a document whose first page is an exhibit marker page and whose remainder is an unrelated document type |
| **needs LLM** | • an exhibit whose cover sheet was lost, where only a reference elsewhere identifies it<br>• recognising which of several attached documents a schedule entry refers to |
| **never alone** | • the word 'exhibit' — trade shows, museums and marketing decks use it constantly<br>• a single capital letter or short label on a page<br>• an attachment or appendix marker — ordinary reports use these<br>• a photograph, contract or message export: being evidentiary is a role, not a document type |

**Work types** — exhibit · exhibit cover sheet · exhibit schedule or index · bundle index · chain of custody record · evidence log · authenticity certificate

**Grouping reasons** — all exhibits to one witness statement · an exhibit schedule with the exhibits it lists · the evidence tendered by one party in one proceeding

**Template** — `client → matter → proceeding → tendering party → exhibit`  (time first: no)

> §5.5's context rule; an exhibit label is meaningless outside its proceeding and its side. §5.9 governs the last level — an exhibit-per-folder split creates 'a large number of tiny folders' and should usually be flattened.

**Collides with**

| Domain | Signal that separates them | Design cite |
|---|---|---|
| `legal.contracts` | an exhibited contract is simultaneously a contract and an exhibit. §3.11 settles the fact layer — both sets of facts are preserved — and §6.9 settles the placement. | §3.11 “One file may hold facts from more than one domain without losing information.” |
| `pers.photo-event` | an exhibited photograph still carries EXIF and still belongs to the Photos domain's fact schema. The exhibit marker is what adds this domain, and it does not remove the other. | — |
| `legal.court-records` | 05 lists 'exhibit' among its work types. Same rule: without a practice-side signal this entry abstains. | — |

**Sensitivity** — `potentially_sensitive`. §2.9's phrase. Exhibits are frequently third parties' personal material. No handling class is set here.

**Open question — Joseph's call, unresolved**

> Should `exhibit_identifier` be destination-eligible — i.e. may an exhibit label become a folder level? It is the handle practitioners navigate by, but labels are short, restart per proceeding, and are re-assigned when a bundle is repaginated, so a tree keyed on them goes stale. §5.4 leaves “which dimensions are optional, which ones are metadata only” to the template author, and this one is genuinely undecided.

---

### 17. `law.depositions` — Depositions and pre-trial examinations

The file of one out-of-court examination of one witness — the notice, the transcript, the exhibits and the corrections.

**provenance** `proposal`

**Schema**

| Field | Type | Ceiling | Example | Why this field, in this domain |
|---|---|---|---|---|
| `deponent` | string | `direct` | the person examined | A transcript's caption block states the deponent in a labeled slot, so `direct` per §3.5. §3.8's roles rule keeps this distinct from `party` — a deponent is often not a party. |
| `examination_date` | date | `direct` | the date on the transcript cover | Stated on the cover page as a labeled slot. §3.10's narrow parsing applies. Needed because one witness is often examined over several days and the volumes must stay ordered. |
| `case_identifier` | string | `validated` | the identifier in the caption | Joins the examination to its proceeding; transcripts are captioned like pleadings. |
| `volume` | string | `direct` | the volume or day of a multi-session examination | Stated on the cover page. Without it a multi-day transcript set silently reorders. |
| `examining_party` | string | `validated` | the party conducting the examination | §3.8's roles principle; determines whose work product the surrounding preparation is. |

**Recognition**

| | |
|---|---|
| **deterministic** — pattern *plus* corroborating context | • a transcript cover page pairing a deponent name with a date AND a case identifier, followed by page-and-line numbered body text — the page/line structure is close to unique to this genre<br>• a notice or subpoena document naming a witness, a date and a place of examination, carrying a case identifier<br>• an errata or correction sheet whose rows pair page and line references with changes |
| **needs LLM** | • a rough or uncertified transcript delivered without a cover page<br>• matching a video or audio file to the examination it records when only the filename connects them<br>• distinguishing an examination transcript from a court hearing transcript where both use page-and-line numbering |
| **never alone** | • page-and-line numbering alone — screenplays, some legislative records and some published transcripts share it<br>• the word 'transcript' — podcast, interview, lecture and meeting transcripts are all common<br>• a person's name<br>• an audio or video file: §2.9 permits speech-to-text “only under an explicit privacy and compute policy”, and a media file with no accompanying transcript is not evidence of an examination |

**Work types** — notice of examination · subpoena · transcript · rough transcript · errata sheet · exhibit set · video or audio recording · summary or digest

**Grouping reasons** — one witness's examination across its volumes, exhibits and errata · all examinations in one proceeding · a transcript with its digest and the submissions that cite it

**Template** — `client → matter → proceeding → deponent → document type`  (time first: no)

> §5.5's context rule, with deponent as the natural spine: an errata sheet and an exhibit set are only interpretable against the witness they belong to. Volume is ordering within the document type, not a folder level — §5.9 warns against levels that produce one child.

**Collides with**

| Domain | Signal that separates them | Design cite |
|---|---|---|
| `law.hearing-transcripts` | both are transcripts with page-and-line numbering. The examination transcript names a deponent and a place outside court; a hearing transcript names a court and a judge. | — |
| `law.witness-statements` | both are one witness's evidence. A statement is composed and signed; an examination transcript is a verbatim record taken by a third party. Different schemas, same witness — a strong grouping reason, not a merge. | — |

**Sensitivity** — `potentially_sensitive`. §2.9's phrase. A transcript is a named individual's testimony, often about third parties. Whether it is confidential varies by jurisdiction and by protective order, which is why no handling class is assigned here.

**Open question — Joseph's call, unresolved**

> The deposition is a common-law discovery device with no direct equivalent in several major legal systems, and the systems that do have pre-trial witness examination give it different names, different roles and different paperwork. Does this entry stay as one jurisdiction-neutral 'examination of a witness outside court' domain — which is what the schema above attempts — or split per system? Same axis as law.matter-file's open_question, and this is the entry where a neutral abstraction is hardest to defend.

---

### 18. `law.witness-statements` — Witness statements, affidavits and declarations

A witness's own account, composed and formally attested, put forward as that witness's evidence.

**provenance** `proposal`

**Schema**

| Field | Type | Ceiling | Example | Why this field, in this domain |
|---|---|---|---|---|
| `witness` | string | `direct` | the person whose account it is | Named in the title block and the attestation line — labeled slots, so `direct` per §3.5. Distinct from the author: these are frequently drafted by the practice and remain the witness's evidence (§3.8's roles rule). |
| `case_identifier` | string | `validated` | the identifier in the caption | Joins the statement to its proceeding. A statement taken before proceedings begin will not have one, which is itself informative. |
| `statement_type` | string | `validated` | how the document names itself | The attestation form and its name are jurisdiction-bound — the available forms differ by system and the difference has legal consequences. The field is neutral; values are corpus-derived and the catalogue does not equate them. |
| `statement_date` | date | `direct` | the date of signature or attestation | A dated attestation block is a labeled slot. §3.10's narrow parsing applies. |
| `statement_number` | string | `validated` | which statement this is from this witness in this proceeding | One witness commonly makes several; without the ordinal the set silently collapses into a version family that it is not. |

**Recognition**

| | |
|---|---|
| **deterministic** — pattern *plus* corroborating context | • a title block naming a witness and a statement or attestation type, together with a case identifier AND a signed attestation block at the end<br>• a numbered-paragraph document ending in an attestation or truth-statement line, carrying a case identifier<br>• a statement of truth or attestation clause co-occurring with a witness name in the title |
| **needs LLM** | • an unsigned draft statement with no caption<br>• distinguishing a witness statement from an expert report where both are numbered-paragraph attested documents — the distinguishing content is the author's basis for speaking<br>• a proof of evidence or interview note that was never turned into a statement |
| **never alone** | • numbered paragraphs — reports, policies, specifications and minutes all use them<br>• a signature block<br>• the word 'statement' — bank statements, press statements and mission statements share it<br>• the word 'declaration' — it also names customs, tax, conformity and interest declarations |

**Work types** — witness statement · affidavit · declaration · statutory declaration · proof of evidence · draft statement · exhibit bundle to a statement · statement of truth page

**Grouping reasons** — one witness's statements and their exhibits · all witness evidence in one proceeding · a statement with its drafts as a version family (§2.9's “duplicate and version-family signals”)

**Template** — `client → matter → proceeding → witness → document type`  (time first: no)

> §5.5's context rule with witness as the spine, matching law.depositions so that one witness's statement and examination sit adjacent rather than in parallel trees.

**Collides with**

| Domain | Signal that separates them | Design cite |
|---|---|---|
| `law.depositions` | same witness, different genre. See that entry. | — |
| `law.expert-materials` | an expert report is an attested numbered-paragraph document too. The expert's report states qualifications and an opinion basis; a lay statement states what the witness perceived. | — |
| `legal.notarised-documents` | 05's cross-cutting attestation entry claims affidavits and sworn statements, and says the underlying domain is the real owner. Agreed: attestation is a property of the document, not a competing domain, and where the underlying document is a party's own the file is 05's. | — |

**Sensitivity** — `potentially_sensitive`. §2.9's phrase. A witness statement is a named person's account, frequently about third parties and frequently including their address or personal details. No handling class is set here.

---

### 19. `law.expert-materials` — Expert evidence and instructions

The instructions to an expert, the expert's report and the material behind it.

**provenance** `proposal`

**Schema**

| Field | Type | Ceiling | Example | Why this field, in this domain |
|---|---|---|---|---|
| `expert` | string | `direct` | the named expert | Named on the report's title page and in the declaration — labeled slots. §3.8's roles rule keeps `expert` distinct from `authored_by`: an expert is a role in a matter, not merely the author of a file. |
| `expertise_field` | string | `llm_supported` | the discipline the expert speaks to | Stated in a qualifications section as prose. §3.6 requires the cited span before it becomes a fact. |
| `instructing_party` | string | `validated` | the party that instructed the expert | §3.8's roles principle, and the single most consequential field in this domain: which side an expert speaks for determines how everything they wrote is read. |
| `case_identifier` | string | `validated` | the identifier of the proceeding | Joins the report to the matter. A report prepared before proceedings may not have one. |
| `report_number` | string | `validated` | first, supplemental, joint | Experts produce sequences of reports that respond to each other; without the ordinal a supplemental report is misread as a draft of the first. |

**Recognition**

| | |
|---|---|
| **deterministic** — pattern *plus* corroborating context | • a report containing BOTH a qualifications or CV section AND an expert's duty or declaration section, together with a case identifier<br>• a letter of instruction naming an expert, a discipline and a question to be answered, carrying a matter reference<br>• a joint statement or joint memorandum naming two or more experts and the issues they agree and disagree on |
| **needs LLM** | • an academic-looking report with no declaration section, where only the content shows it was prepared for a proceeding<br>• separating the expert's own underlying research materials from the report they support<br>• reading the discipline from the substance when the qualifications section is a bare CV |
| **never alone** | • a CV — the corpus is full of them, and §3.15 already places career material elsewhere<br>• a technical or scientific report: this is the collision that matters most, because a research artifact and an expert report are the same genre of document<br>• the word 'expert' — it appears in marketing, training and job descriptions<br>• a bibliography or reference list |

**Work types** — letter of instruction · expert report · supplemental report · joint statement · expert CV · underlying data or working papers · expert's declaration · cross-examination outline

**Grouping reasons** — one expert's instructions, report and supporting material · opposing experts' reports on one issue · a report with the joint statement that followed it

**Template** — `client → matter → proceeding → expert → document type`  (time first: no)

> §5.5's context rule with the expert as spine, because instructions, report and working papers are one body of work by one person and separating them by document type first would scatter it.

**Collides with**

| Domain | Signal that separates them | Design cite |
|---|---|---|
| `res.research-project` | an expert report IS a research artifact by content and a litigation document by purpose. §3.9 is the governing distinction: “Topic answers what a file is about, while purpose answers what the file was for.” The expert's duty declaration and the case identifier are the purpose evidence; without them, slice 03 should win. | §3.9 “Topic answers what a file is about, while purpose answers what the file was for.” |
| `law.witness-statements` | both attested; different basis for speaking. See that entry. | — |
| `legal.litigation-dispute` | 05 lists 'expert report' among its work types. A party's copy of the report is 05's; the instruction letter, working papers and joint statement are practice work product and are this entry's. | — |

**Sensitivity** — `potentially_sensitive`. §2.9's phrase. Expert material in medical, psychological and forensic disciplines carries exactly the content §8.4 names — 'medical information' — inside a legal document. No handling class is set here.

**Open question — Joseph's call, unresolved**

> An expert report is simultaneously a research artifact (research slice) and litigation work product (this slice). §3.11 preserves both fact sets, but placement needs one answer. Does the expert's duty declaration plus a case identifier make purpose win over topic, or should such files always be surfaced under §6.9's shared-material policy rather than placed? The design settles the fact layer and leaves the placement rule to the tree.

---

### 20. `law.trial-preparation` — Hearing and trial preparation

The compiled and working material a practice takes into a hearing — bundles, chronologies, outlines and running orders.

**provenance** `proposal`

**Schema**

| Field | Type | Ceiling | Example | Why this field, in this domain |
|---|---|---|---|---|
| `case_identifier` | string | `validated` | the identifier of the proceeding | Preparation material is internal and mostly untitled; the case identifier printed in the bundle header is often the only reliable anchor. |
| `hearing_event` | string | `validated` | the hearing the material was prepared for | A matter has several hearings and each generates its own bundle. Without this field the sets merge and the wrong bundle is taken to the wrong hearing — a distinction the tree must preserve. |
| `hearing_date` | date | `direct` | the listed date | Stated on the bundle cover or listing notice as a labeled slot. §3.10's narrow parsing applies; nothing is computed from it. |
| `bundle_part` | string | `direct` | the named part or volume of a multi-volume bundle | Stated on the cover and in the index. Needed because bundle parts are separately paginated and reorder silently without it. |
| `preparing_party` | string | `validated` | the side that compiled the material | §3.8's roles principle; a bundle received from the other side is a different artefact from one the practice compiled, even when the contents overlap. |

**Recognition**

| | |
|---|---|
| **deterministic** — pattern *plus* corroborating context | • a bundle index — a table pairing tab or page references with document descriptions — carrying a case identifier<br>• a paginated composite PDF whose first pages are an index and whose body is several unrelated document types, with a case identifier in the header<br>• a chronology or dramatis personae table naming parties and dated events, alongside a case identifier |
| **needs LLM** | • a cross-examination outline or skeleton note with no header, where only the content shows what hearing it was for<br>• recognising that an untitled composite PDF is a hearing bundle rather than a merged scan |
| **never alone** | • a composite PDF with an index — reports, manuals and compiled scans all match<br>• the word 'bundle' — it names software packages, product offers and shipping units<br>• a chronology or timeline table<br>• page or tab numbering |

**Work types** — hearing bundle · bundle index · core bundle · chronology · dramatis personae · cross-examination outline · opening note · closing note · running order · reading list

**Grouping reasons** — all material prepared for one hearing · a bundle with its index and its supplementary parts · the practice's working notes for one hearing

**Template** — `client → matter → proceeding → hearing → document type`  (time first: no)

> §5.5's context rule; an opening note is meaningless except against the hearing it opens. Hearing is the level that matters most here and the one most often missing from a naive tree.

**Collides with**

| Domain | Signal that separates them | Design cite |
|---|---|---|
| `law.evidence-exhibits` | a bundle contains exhibits, pleadings, statements and orders as copies. The bundle is a compiled artefact in its own right; its constituent copies are duplicates of files that have their own homes. | — |
| `law.appeals` | an appeal record reproduces the trial bundle. See law.appeals. | — |

**Sensitivity** — `potentially_sensitive`. §2.9's phrase. A hearing bundle is the whole matter in one file, so it inherits the sensitivity of everything inside it. No handling class is set here.

**Open question — Joseph's call, unresolved**

> A bundle physically CONTAINS copies of documents that each have their own home. Is that a §6.9 shared-material case — “a shared branch, a primary-home convention, a reference or alias convention, or mandatory review” — or a §2.9 duplicate-family case, since the bundle is one new file rather than the same file in two places? The design settles neither, and the answer decides whether a bundle's contents are ever unpacked.

---

### 21. `law.jury-materials` — Jury selection and jury-facing materials

Material used to select a jury and material put before one — questionnaires, instructions, verdict forms and the notes around them.

**provenance** `proposal`

**Schema**

| Field | Type | Ceiling | Example | Why this field, in this domain |
|---|---|---|---|---|
| `case_identifier` | string | `validated` | the identifier of the proceeding | Joins the material to its trial. Jury material is otherwise close to anonymous. |
| `jury_document_type` | string | `validated` | how the document names itself | Read from the title block. The document set differs sharply by jurisdiction — some systems have no civil jury at all, and the selection process ranges from an extensive questionnaire to nothing — so the field is neutral and values are corpus-derived. |
| `hearing_event` | string | `validated` | the trial the material belongs to | Matches law.trial-preparation so jury material files adjacent to the bundle prepared for the same trial. |
| `proposing_party` | string | `validated` | the side that proposed an instruction or form | §3.8's roles principle. Proposed and given instructions differ, and which side proposed one is the point of keeping it. |

**Recognition**

| | |
|---|---|
| **deterministic** — pattern *plus* corroborating context | • a numbered set of instruction texts, each headed as an instruction and carrying a case identifier<br>• a verdict form — a question-and-answer structure with signature and dating lines for a foreperson — carrying a case identifier<br>• a juror questionnaire whose labeled fields include a juror number, together with a case identifier |
| **needs LLM** | • selection notes and impressions written informally with no header<br>• distinguishing a proposed instruction from the one actually given where both are in the file |
| **never alone** | • the word 'jury' — it appears in awards, competitions, design contests and journalism<br>• a numbered instruction list — training material, assembly guides and policies all match<br>• a questionnaire<br>• a form with signature lines |

**Work types** — juror questionnaire · voir dire outline · proposed jury instructions · given instructions · verdict form · jury note · selection chart · juror research file

**Grouping reasons** — all jury material for one trial · competing proposed instructions on one issue · selection material from one selection session

**Template** — `client → matter → proceeding → hearing → document type`  (time first: no)

> §5.5's context rule, and deliberately identical to law.trial-preparation so that a user who never separates jury material from the rest of trial prep gets one coherent branch rather than two half-filled ones (§5.9's warning about levels that produce one child).

**Collides with**

| Domain | Signal that separates them | Design cite |
|---|---|---|
| `law.trial-preparation` | jury material is a subset of trial preparation in most practices and a separate workstream in a few. Whether it deserves its own branch is a §5.3 vertical-pass decision the user makes, not one this catalogue makes. | — |

**Sensitivity** — `potentially_sensitive`. §2.9's phrase. Juror questionnaires and selection research contain private information about named individuals who are not parties. No handling class is set here.

**Open question — Joseph's call, unresolved**

> This domain does not exist in large parts of the world, and where it exists it varies enormously — civil juries in some systems and not others, extensive selection procedures in some and none in others, and juror information that is restricted in some jurisdictions and open in others. Should a domain that is inapplicable to most corpora ship in the library at all, or activate only when a `jurisdiction` fact indicates a jury system? §3.11's rule — a schema activates 'when the evidence indicates that a domain is plausible' — is a per-file test, not a per-corpus one, and this is the clearest case where a per-corpus gate might be needed instead.

---

### 22. `law.hearing-transcripts` — Hearing transcripts and the record of proceedings

The verbatim record of what happened in front of a court or tribunal, and the indexes into it.

**provenance** `proposal`

**Schema**

| Field | Type | Ceiling | Example | Why this field, in this domain |
|---|---|---|---|---|
| `case_identifier` | string | `validated` | the identifier in the transcript caption | Transcripts are captioned like pleadings and join to the proceeding by the same key. |
| `court` | string | `validated` | the court or tribunal sitting | Distinguishes a hearing transcript from an out-of-court examination transcript, which is otherwise formally identical. |
| `hearing_date` | date | `direct` | the sitting date | Stated on the cover as a labeled slot. §3.10's narrow parsing applies. Load-bearing here because multi-day hearings produce one file per day and the days must stay ordered. |
| `hearing_day` | string | `direct` | which day of a multi-day hearing | Stated on the cover. Without it, day 2 and day 12 sort as though they were versions of one document. |
| `transcript_status` | string | `validated` | rough \| uncertified \| certified \| corrected | Stated on the cover or in a certificate. Different statuses of the same day are NOT a version family in the ordinary sense — a rough and a certified transcript are both authoritative for different purposes — and merging them loses that. |

**Recognition**

| | |
|---|---|
| **deterministic** — pattern *plus* corroborating context | • a page-and-line numbered transcript whose cover page names a court AND a case identifier AND a sitting date<br>• a transcriber's certificate block co-occurring with a case identifier<br>• a transcript index or key-passage index citing page and line references, carrying a case identifier |
| **needs LLM** | • a rough transcript delivered as plain text with no cover page<br>• an audio recording of a hearing where only a transcript would identify it — §2.9 permits speech-to-text “only under an explicit privacy and compute policy”<br>• distinguishing a hearing transcript from an examination transcript when the cover is missing |
| **never alone** | • page-and-line numbering<br>• the word 'transcript'<br>• a court name appearing in body text — judgments, articles and textbooks name courts constantly<br>• a date |

**Work types** — daily transcript · rough transcript · certified transcript · transcriber's certificate · transcript index · key passages note · audio recording

**Grouping reasons** — all days of one hearing · a transcript with the index and notes citing it · successive statuses of one day's record

**Template** — `client → matter → proceeding → hearing → document type`  (time first: no)

> §5.5's context rule; matches law.trial-preparation so a hearing's bundle and its transcript live under the same hearing node. Day is ordering within the type, not a level — §5.9 warns against levels that create many tiny folders.

**Collides with**

| Domain | Signal that separates them | Design cite |
|---|---|---|
| `law.depositions` | formally near-identical. The court name and the judge are what separate them. | — |
| `legal.court-records` | 05 lists 'transcript' among its work types. A transcript a party holds is 05's; this entry needs a matter and a practice-side signal. | — |

**Sensitivity** — `potentially_sensitive`. §2.9's phrase. Openness of a hearing record varies by jurisdiction and by proceeding, and some hearings are closed entirely. No handling class is set here.

---

### 23. `law.settlement` — Settlement negotiation and settlement instruments

The offers, the exchanges and the agreement that ends a dispute without a decision.

**provenance** `proposal`

**Schema**

| Field | Type | Ceiling | Example | Why this field, in this domain |
|---|---|---|---|---|
| `matter_reference` | string | `validated` | 10432-0007 | Settlement material often deliberately omits the case identifier; the practice's own reference is usually all that remains. |
| `settling_parties` | string | `validated` | the parties to the agreement | The signing parties can differ from the litigating parties — a parent, an insurer or a guarantor may sign — which is why §3.8's roles rule requires this to be its own field rather than reusing `party`. |
| `settlement_stage` | string | `validated` | offer \| counter-offer \| agreed terms \| executed agreement | The stage is on the face of the document and is the whole meaning of the file: an offer and an executed agreement have opposite consequences and identical wording. |
| `settlement_date` | date | `direct` | the execution date | A dated execution block is a labeled slot. §3.10's narrow parsing applies. |
| `case_identifier` | string | `validated` | the proceeding being settled, where stated | Present on consent orders and discontinuance documents; frequently absent from the private agreement itself. |

**Recognition**

| | |
|---|---|
| **deterministic** — pattern *plus* corroborating context | • a document containing a release or discharge clause AND a payment or consideration clause AND a matter reference<br>• an offer letter carrying a settlement-privilege or negotiation legend together with a matter reference or case identifier<br>• a consent order or discontinuance document carrying a case identifier |
| **needs LLM** | • an email exchange in which an offer is made and accepted with no formal document<br>• distinguishing a settlement agreement from an ordinary commercial contract, where the release clause is the only structural difference<br>• identifying which of several exchanged drafts is the executed version when none is signed |
| **never alone** | • a release clause — commercial contracts, employment agreements and licence terms all carry them<br>• a negotiation or privilege legend on a letter: the legend is text on the page and does not establish any legal status (see law.document-review's open_question)<br>• the word 'settlement' — it also means a payment settlement, a housing settlement and a geographic settlement<br>• a payment amount |

**Work types** — offer letter · counter-offer · settlement agreement · release · consent order · discontinuance notice · tomlin-style schedule · settlement summary to client

**Grouping reasons** — one negotiation from first offer to executed agreement · the agreement with the consent order that implemented it · drafts of one agreement as a version family (§2.9's “duplicate and version-family signals”)

**Template** — `client → matter → document type`  (time first: no)

> §5.5's context rule. Deliberately shallower than the litigation domains: a settlement is a single episode of a matter and §5.8's uneven-depth allowance applies — “The product should not force every branch to use the full template”.

**Collides with**

| Domain | Signal that separates them | Design cite |
|---|---|---|
| `legal.contracts` | a settlement agreement is a contract, and a party's own signed copy is that party's record. It belongs here when it carries a matter reference or resolves an identified proceeding; otherwise it DEFERS. | — |
| `law.adr` | a mediated settlement is produced inside an ADR process. The agreement is this domain; the mediation process record is that one. | — |
| `legal.litigation-dispute` | 05 lists 'settlement agreement' among its work types. The negotiation apparatus — offers, counter-offers, drafts under a matter reference — is this entry; a party's executed settlement is 05's. | — |

**Sensitivity** — `potentially_sensitive`. §2.9's phrase. Settlement terms are frequently subject to confidentiality obligations owed to a third party, which is a reason to protect the file and not a reason for this catalogue to assign a class. No handling class is set here.

---

### 24. `law.adr` — Mediation and arbitration

A dispute resolved outside the courts — the appointment, the submissions, the process record and the award or outcome.

**provenance** `proposal`

**Schema**

| Field | Type | Ceiling | Example | Why this field, in this domain |
|---|---|---|---|---|
| `reference_identifier` | string | `validated` | the case number an institution assigns | Institutional references have their own formats, distinct from court identifiers, and an ad hoc process may have none at all — so this is a separate field from `case_identifier` rather than a reuse of it. |
| `forum` | string | `validated` | the institution administering the process, or ad hoc | The forum determines the rules, the vocabulary and the document set. It is normally named on the face of every document in the reference. |
| `process_type` | string | `validated` | mediation \| arbitration \| expert determination \| adjudication | These processes have different structures and different outcomes, and merging them makes the file unreadable. Availability and naming differ by jurisdiction and by contract, so values are corpus-derived. |
| `neutral` | string | `direct` | the arbitrator, tribunal or mediator | Named in the appointment document and the award header — labeled slots. §3.8's roles rule keeps this distinct from `deciding_judge` and from `authored_by`. |
| `party` | string | `validated` | a party to the reference | Read from the header block. Party designations differ from litigation designations in most rules sets, which is why the vocabulary is not shared with law.pleadings. |

**Recognition**

| | |
|---|---|
| **deterministic** — pattern *plus* corroborating context | • a document header naming an arbitral or mediation institution AND a reference identifier AND two or more parties<br>• an appointment or terms-of-reference document naming a neutral and the parties who appointed them<br>• an award document whose structure pairs a reasons section with a numbered dispositive section, carrying an institutional reference |
| **needs LLM** | • an ad hoc process with no institution and no reference, identifiable only from the correspondence<br>• distinguishing a mediation position paper from a litigation submission, which it closely resembles<br>• recognising an arbitration clause dispute inside ordinary contract correspondence |
| **never alone** | • the word 'arbitration' or 'mediation' — arbitration clauses appear in ordinary commercial contracts and terms of service that no dispute has ever touched<br>• an institution's name appearing in a contract clause<br>• the word 'award' — it also means a prize, a grant and a contract award<br>• the word 'neutral' |

**Work types** — notice of arbitration · response · terms of reference · appointment document · statement of case · position paper · procedural order · award · mediation agreement · settlement reached at mediation

**Grouping reasons** — one reference from notice to award · all documents before one tribunal · an award with the enforcement or challenge material that followed

**Template** — `client → matter → reference → document type`  (time first: no)

> §5.5's context rule. 'Reference“ rather than ”proceeding' because the identifier and forum differ from the court family, and a matter can run a court proceeding and an arbitration at the same time — which the tree must keep apart.

**Collides with**

| Domain | Signal that separates them | Design cite |
|---|---|---|
| `law.pleadings` | arbitral submissions are pleading-shaped. The institutional reference and the absence of a court name are the distinguishing signals. | — |
| `law.settlement` | see that entry — the mediated agreement versus the mediation process record. | — |

**Sensitivity** — `potentially_sensitive`. §2.9's phrase. Most arbitration is private and many rules sets impose confidentiality on the parties, which makes the file sensitive as a matter of fact. No handling class is set here.

**Open question — Joseph's call, unresolved**

> Arbitral confidentiality is a real obligation owed to a counterparty rather than a privacy interest of the corpus owner, and §8.4's handling classes run from 'Public or low sensitivity' to “Highly sensitive or credential-bearing” and are all framed around personal sensitivity. Is an obligation owed to someone else an axis P7's vocabulary needs, or does it collapse into the existing classes? This is a P7 vocabulary question raised here, not answered here.

---

### 25. `law.legal-research` — Legal research and authorities

The record of finding out what the law is — memoranda, research notes, and the authorities collected to support them.

**provenance** `proposal`

**Schema**

| Field | Type | Ceiling | Example | Why this field, in this domain |
|---|---|---|---|---|
| `research_question` | string | `llm_supported` | the question the memorandum answers | Stated as prose under an issue or question heading. §3.5 places this squarely with the LLM; §3.6 requires the cited span to exist. |
| `matter_reference` | string | `validated` | 10432-0007 | Matter-specific research belongs to its matter. Its ABSENCE is the signal that the file belongs to the know-how library instead — see law.knowhow-precedents. |
| `jurisdiction` | string | `llm_supported` | the legal system researched | The most important field in this domain and rarely stated in a slot. Research answering a question under one system is actively misleading if filed as though it answered it under another. |
| `legal_topic` | string | `llm_supported` | the area of law addressed | Prose interpretation. The value vocabulary is corpus-derived; §3.12: “The system may create new values when it sees a new course, project, company, university, or event, but it should not invent new fields automatically.” |
| `authority` | string | `possible` | a cited case, statute or instrument | Held for search and explanation, never for placement. A file must not be placed by what it cites: §3.8's principle that a folder must not become 'a collection point' applies to cited authorities as much as to authors. |

**Recognition**

| | |
|---|---|
| **deterministic** — pattern *plus* corroborating context | • a memorandum whose heading block pairs an issue or question line with a conclusion or advice line, carrying a matter reference<br>• a dense citation-bearing document co-occurring with a matter reference AND practice-side context such as a fee-earner block or an 'our ref' line<br>• a saved authority — a judgment, statute extract or database print — filed alongside a memorandum carrying the same matter reference |
| **needs LLM** | • an untitled research note with no matter reference<br>• distinguishing research prepared for a matter from reading kept out of interest<br>• reading which jurisdiction the research addresses when it is implicit in the authorities cited |
| **never alone** | • case or statute citations — this is the single largest false-positive source in the whole supercategory. Law review articles, textbooks, student essays, journalism, policy papers, compliance training and terms of service all cite law heavily and none of them is legal-practice work product<br>• the word 'memorandum' — it names internal business notes of every kind<br>• a legal database export or watermark<br>• the words 'held', 'pursuant to', 'notwithstanding' |

**Work types** — research memorandum · research note · authority extract · case digest · statute extract · research trail or search log · comparative note

**Grouping reasons** — a memorandum with the authorities collected for it · all research on one matter · research on one question across matters

**Template** — `client → matter → legal topic → document type`  (time first: no)

> §5.5's context rule. Topic sits below matter because research is done FOR a matter; the know-how domain inverts this deliberately, which is the clearest structural difference between the two.

**Collides with**

| Domain | Signal that separates them | Design cite |
|---|---|---|
| `law.knowhow-precedents` | the same memorandum becomes know-how when it is de-identified and kept for reuse. A matter reference is what keeps it here. | — |
| `acad.course-enrollment` | a law student's research essay is citation-dense and issue-structured. §3.5's course rule wins where a course code and academic context are present, and this domain must abstain rather than compete. | §3.5 “becomes a course fact only when the engine finds a course-code pattern together with academic context” |
| `res.research-project` | legal scholarship is research, not practice. Absence of a matter reference plus presence of academic apparatus should route it away from this slice. | — |

**Sensitivity** — `potentially_sensitive`. §2.9's phrase. A research memorandum states a client's legal position and its weaknesses. No handling class is set here.

**Open question — Joseph's call, unresolved**

> Citation identifier patterns are already catalogued for the research slice (`planning/deferred-catalogues/06-citation-identifier-patterns`), which covers DOI, ISBN, URL and author-year forms. Legal citation is a separate and jurisdiction-specific system — case citations, statute references and law-report abbreviations differ by country and have no cross-system standard. Should legal citation be added to catalogue 06, kept as a separate per-jurisdiction catalogue, or refused entirely on the ground that a citation is `possible` here and never placement-bearing?

---

### 26. `law.opinions` — Opinions and formal advice

A formal, addressed statement of legal position that a client or a third party is entitled to rely on.

**provenance** `proposal`

**Schema**

| Field | Type | Ceiling | Example | Why this field, in this domain |
|---|---|---|---|---|
| `client` | string | `validated` | the addressee entitled to rely | §3.8's field. An opinion is addressed, and the addressee is the point — reliance is what distinguishes it from a research memorandum. |
| `our_firm` | string | `validated` | the practice giving the opinion | §3.8's paired field. An opinion received FROM another practice is a different artefact from one the practice gave, and merging them would be a serious error. |
| `opinion_subject` | string | `llm_supported` | the question opined on | Prose. §3.6 requires the cited span before it becomes a fact. |
| `opinion_date` | date | `direct` | the date the opinion bears | A dated signature block is a labeled slot. §3.10's narrow parsing applies. Load-bearing because an opinion speaks as at its date. |
| `jurisdiction` | string | `validated` | the law opined on | Formal opinions state the governing law explicitly, usually in a scope or assumptions section, which makes this one of the few places the jurisdiction is a readable slot rather than an inference. |

**Recognition**

| | |
|---|---|
| **deterministic** — pattern *plus* corroborating context | • an addressed letter containing an assumptions or qualifications section AND an opinion or conclusion section, on practice letterhead<br>• a document with a stated reliance or addressee-limitation clause together with a practice signature block<br>• a counsel's opinion carrying an instructing-practice reference and a set of instructions attached |
| **needs LLM** | • advice given in an ordinary letter or email with no formal structure<br>• distinguishing a formal opinion from a research memorandum where neither is labelled<br>• recognising a draft opinion that was never given |
| **never alone** | • the word 'opinion' — it names reviews, editorials, survey responses and audit opinions<br>• practice letterhead — practices send marketing and administrative letters on it<br>• the phrase 'in our view'<br>• an assumptions section |

**Work types** — opinion letter · counsel's opinion · instructions to counsel · advice note · reliance letter · draft opinion · qualifications schedule

**Grouping reasons** — an opinion with the instructions that produced it · successive opinions on one question · all opinions given to one client

**Template** — `client → matter → document type`  (time first: no)

> §5.5's context rule; kept shallow because an opinion is a small, discrete deliverable and §5.8 allows a branch to stay flat where the extra levels would each hold one file.

**Collides with**

| Domain | Signal that separates them | Design cite |
|---|---|---|
| `law.legal-research` | a memorandum informs the practice; an opinion is given to a recipient who may rely on it. The addressee and the reliance language are the signals. | — |
| `law.transactional-deal` | a transaction opinion is a closing deliverable and belongs to the deal's closing set as well as here. | — |

**Sensitivity** — `potentially_sensitive`. §2.9's phrase. An opinion states a considered legal position and its qualifications. No handling class is set here.

---

### 27. `law.knowhow-precedents` — Precedent bank and know-how

Reusable material kept for the next matter rather than for the one it came from — model documents, clauses, checklists and standing notes.

**provenance** `proposal`

**Schema**

| Field | Type | Ceiling | Example | Why this field, in this domain |
|---|---|---|---|---|
| `precedent_type` | string | `validated` | the kind of reusable document | Know-how is organised by what a document IS, since by definition it belongs to no matter. Read from the title or a know-how header. |
| `legal_topic` | string | `llm_supported` | the area the precedent serves | Prose interpretation. This is the primary retrieval dimension for the whole domain, which is why it sits above document type in the template. |
| `jurisdiction` | string | `llm_supported` | the system the precedent is drafted for | A precedent used under the wrong system is worse than no precedent. Rarely stated; usually inferable only from the drafting. |
| `precedent_version` | string | `validated` | the version or last-reviewed marker | Know-how goes stale, and a superseded precedent that looks current is the characteristic failure of a precedent bank. §2.9's “duplicate and version-family signals” apply directly. |
| `source_matter` | string | `possible` | the matter the precedent was derived from, where recorded | Kept at `possible` on purpose. A precedent derived from a real matter should NOT be pulled back into that matter's folder by this field, and a value here must never drive placement — see this entry's open_question. |

**Recognition**

| | |
|---|---|
| **deterministic** — pattern *plus* corroborating context | • a document containing drafting placeholders — bracketed or bracketed-and-capitalised insertion markers — in a document type that is otherwise a finished instrument<br>• a drafting note or guidance-note structure interleaved with clause text<br>• a know-how header block naming a topic and a review or version marker, with no matter reference |
| **needs LLM** | • a real executed document kept as a model with the names left in<br>• distinguishing a firm precedent from a published model form or an industry standard document<br>• reading the topic and the jurisdiction from the drafting alone |
| **never alone** | • placeholder brackets — templates of every kind use them, including invoices and letters<br>• the words 'template', 'precedent' or 'model' — 'precedent' also means a prior decision, which is a different thing entirely, and 'template' is universal<br>• absence of a matter reference: most files in a corpus have none<br>• a checklist |

**Work types** — model document · clause bank · drafting note · checklist · standard form · practice note · training note · know-how memorandum

**Grouping reasons** — a precedent with its drafting notes · all know-how on one topic · successive versions of one precedent as a version family

**Template** — `legal topic → precedent type → document type`  (time first: no)

> The one domain in this slice with NO client and NO matter level, which is the whole point of it. §5.5's rule still governs — topic is the context that makes a clause bank interpretable — but the spine is subject rather than engagement.

**Collides with**

| Domain | Signal that separates them | Design cite |
|---|---|---|
| `law.matter-file` | a precedent derived from a real matter carries that matter's fingerprints. The absence of a live matter reference plus the presence of placeholders should keep it here; a stray retained reference must not drag it back. | — |
| `law.pleadings` | precedent pleadings are pleading-shaped with dead captions. See law.pleadings. | — |
| `legal.contracts` | 05's 'NDA' and standard-form work types can be indistinguishable from a precedent. Placeholders and the absence of a counterparty are what keep a file here; a party's own template of its NDA is 05's. | — |

**Sensitivity** — `none`. A properly de-identified precedent carries no client or personal content. This is the only entry in the slice not marked potentially_sensitive, and the marking is conditional on the de-identification actually having happened — an imperfectly redacted precedent is a matter document and should be recognised as one.

**Open question — Joseph's call, unresolved**

> A precedent is often a de-identified copy of a real matter document, so a content-similarity signal will pull the two together and §2.9's duplicate/version-family logic may treat them as versions of one file. Does the product need an explicit rule that a know-how copy is never grouped with its source matter, and if so is that a grouping stop rule (§4.9 already lists stop rules) or a placement rule? Getting this wrong leaks a client document into a library that is shared across the practice.

---

### 28. `law.transactional-deal` — Transactional deal file

The file of one transaction — the parties, the structure, the documents that make it happen and the record of getting there.

**provenance** `proposal`

**Schema**

| Field | Type | Ceiling | Example | Why this field, in this domain |
|---|---|---|---|---|
| `deal_name` | string | `validated` | the name or code the transaction is run under | Transactions are almost always given a working name that appears on every document, and it is frequently a code name that reveals nothing — which makes it a reliable key precisely because it is arbitrary. |
| `matter_reference` | string | `validated` | 10432-0007 | Joins the deal to the engagement. A deal may run across several matters and several practices. |
| `transaction_type` | string | `llm_supported` | the kind of transaction | Rarely labelled; read from the principal document. The vocabulary is partly jurisdiction-bound and values are corpus-derived. |
| `deal_party` | string | `validated` | a principal to the transaction | Read from an execution or parties block. §3.8's roles rule is acute here — a party may be buyer, seller, lender and guarantor across one deal's documents. |
| `party_side` | string | `llm_supported` | which side of the transaction a party sits on | The side is what makes the file navigable and is almost never stated as a label; it is read from the role a party takes in the operative documents. |
| `signing_status` | string | `validated` | draft \| agreed form \| execution version \| executed | The single most consequential field in transactional work: a draft and an execution version are textually near-identical and legally opposite. Usually stated in a header or footer marker. |

**Recognition**

| | |
|---|---|
| **deterministic** — pattern *plus* corroborating context | • a document with a parties block AND an execution block, carrying a deal name or matter reference in a header or footer<br>• a document status marker in a header or footer — a draft, agreed-form or execution-version legend — together with a deal name<br>• a document list or checklist naming the deal and enumerating the instruments required to complete it |
| **needs LLM** | • reading the transaction type and each party's side from the operative documents<br>• identifying which of a series of near-identical drafts was the one executed, when no marker distinguishes them<br>• recognising that a code-named document set is one transaction |
| **never alone** | • a contract — the corpus is full of contracts and almost none belong to a legal practice's deal file<br>• an execution block or signature page<br>• a code name — project code names are used for products, campaigns and reorganisations too<br>• the words 'agreement', 'party', 'consideration' |

**Work types** — term sheet · principal agreement · ancillary agreement · disclosure letter · board approvals · conditions checklist · document list · signing agenda · deal timetable

**Grouping reasons** — one transaction across all its instruments · one instrument across its drafts as a version family · documents produced at one stage of one deal

**Template** — `client → deal → workstream → document type`  (time first: no)

> §5.5's context rule with 'deal' where the litigation domains have 'proceeding'. §5.5's second rule is what rules out a date-first tree — 'putting year first scatters related work across calendar folders' — and a deal's drafts span months.

**Collides with**

| Domain | Signal that separates them | Design cite |
|---|---|---|
| `legal.contracts` | the deal file is the ADVISER's file; the executed contract in a party's own records is that party's. A file with drafts, checklists and a document list is this domain; a lone executed PDF with no surrounding apparatus DEFERS. | — |
| `law.contract-negotiation` | negotiation work product is a phase of a deal. Where a practice runs contract negotiation as a standing function rather than per-deal, that domain stands alone. | — |

**Sensitivity** — `potentially_sensitive`. §2.9's phrase. A live deal file is commercially confidential and often price-sensitive. No handling class is set here.

---

### 29. `law.due-diligence` — Due diligence and disclosure

The examination of what is being bought or lent against, and the counterparty's formal disclosure of what is wrong with it.

**provenance** `proposal`

**Schema**

| Field | Type | Ceiling | Example | Why this field, in this domain |
|---|---|---|---|---|
| `deal_name` | string | `validated` | the transaction the diligence serves | Diligence output is meaningless outside its transaction and is normally headed with the deal name. |
| `target` | string | `validated` | the entity or asset examined | §3.8's roles rule: the target is not the client and is often not a party to the practice's engagement at all. Merging it into `client` would be the characteristic error here. |
| `diligence_workstream` | string | `validated` | the area examined | Diligence is run in parallel workstreams that produce separate reports and separate data-room folders; the workstream is normally the document's own heading. |
| `data_room_reference` | string | `direct` | the index reference of a reviewed document | Data-room indexes are numbered structures and the reference is a labeled slot, so `direct` per §3.5. It is the only durable link between a report finding and the document behind it. |
| `disclosure_reference` | string | `validated` | the warranty a disclosure is made against | A disclosure schedule is meaningless except against the numbered warranty it qualifies; the pairing is the document's structure. |

**Recognition**

| | |
|---|---|
| **deterministic** — pattern *plus* corroborating context | • a report whose section structure follows named diligence workstreams AND that cites indexed document references<br>• a data-room index — a numbered hierarchical document list — carrying a deal or target name<br>• a disclosure schedule whose rows pair a numbered warranty reference with disclosure text<br>• a requests list paired with a responses column, headed with a target name |
| **needs LLM** | • a diligence summary written as prose with no workstream headings<br>• distinguishing a diligence report from an audit, a valuation or a technical assessment of the same target<br>• recognising a data-room export whose index was not included |
| **never alone** | • a numbered hierarchical file index — every large document set has one<br>• the words 'due diligence' — the phrase is used loosely in procurement, hiring and vendor management<br>• a company name<br>• a findings or issues list<br>• the word 'disclosure' — it also names financial and regulatory disclosure, which are different domains |

**Work types** — diligence request list · diligence report · red flag report · data room index · data room export · disclosure letter · disclosure schedule · diligence findings log · vendor diligence report

**Grouping reasons** — one diligence exercise across its workstreams · a report with the data-room documents it cites · a disclosure letter with its schedules and the warranties they answer

**Template** — `client → deal → diligence workstream → document type`  (time first: no)

> §5.5's context rule; a finding is unreadable outside its workstream and its deal. Matches law.transactional-deal's first two levels deliberately so diligence sits inside the deal rather than beside it.

**Collides with**

| Domain | Signal that separates them | Design cite |
|---|---|---|
| `law.conflicts-check` | both produce entity lists. See law.conflicts-check. | — |
| `law.ediscovery-production` | a data room and a production are both large indexed document sets delivered between parties. The production has a load file and party direction; the data room has a hierarchical index and a target. | — |
| `law.transactional-deal` | diligence is a workstream of a deal; it is a separate domain because its schema — target, workstream, index reference — is genuinely different from the deal's. | — |

**Sensitivity** — `potentially_sensitive`. §2.9's phrase. A data room routinely contains a target's employment records, contracts and account information — material §8.4 names directly, held about people and entities who are not the corpus owner's clients. No handling class is set here.

---

### 30. `law.closing-binder` — Signing, closing and completion

The act of completing a transaction and the compiled record of what was signed and delivered.

**provenance** `proposal`

**Schema**

| Field | Type | Ceiling | Example | Why this field, in this domain |
|---|---|---|---|---|
| `deal_name` | string | `validated` | the transaction completed | The binder exists only as the record of one deal; without the deal name it is an unattributable stack of signed documents. |
| `completion_date` | date | `direct` | the date completion occurred | Stated on the binder cover and the completion certificate as a labeled slot. §3.10's narrow parsing applies. Unusually load-bearing here: the completion date is the identity of the event. |
| `binder_item_reference` | string | `direct` | the tab or item number in the index | A binder index is a numbered structure, so the reference is a labeled slot per §3.5. It is how every later query into the binder is phrased. |
| `delivery_status` | string | `validated` | delivered \| outstanding \| waived | A completion checklist states this per item, and it is the difference between a closed deal and one with open obligations. |
| `signing_status` | string | `validated` | execution version \| executed | Carried over from law.transactional-deal deliberately, so an execution version and the executed original are never merged into a version family. |

**Recognition**

| | |
|---|---|
| **deterministic** — pattern *plus* corroborating context | • a binder or bible index pairing tab numbers with document titles, headed with a deal name and a completion date<br>• a completion or closing checklist whose rows pair required deliverables with a status column, headed with a deal name<br>• a compiled PDF whose bookmarks reproduce a numbered document list and whose members are executed instruments |
| **needs LLM** | • a stack of signed PDFs delivered without an index<br>• distinguishing an execution version circulated for signature from the signed original returned |
| **never alone** | • a compiled PDF with bookmarks<br>• signature pages<br>• the word 'closing' — it names accounting periods, sales cycles and shop hours<br>• a numbered document index |

**Work types** — completion checklist · signing agenda · closing binder or bible · binder index · executed instrument · certificate of completion · post-completion undertakings list · funds flow statement

**Grouping reasons** — one completion event and everything delivered at it · a binder with the deal file it completes · outstanding post-completion items across a deal

**Template** — `client → deal → document type`  (time first: no)

> §5.5's context rule, kept shallow because the binder's own index already supplies the internal ordering and reproducing it as folders would create exactly the “large number of tiny folders” §5.9 warns about.

**Collides with**

| Domain | Signal that separates them | Design cite |
|---|---|---|
| `law.transactional-deal` | the binder is the deal file's terminal artefact, and every document in it also exists as a deal draft. §6.9's shared-material policy governs which copy is the primary home. | §6.9 “a shared branch, a primary-home convention, a reference or alias convention, or mandatory review” |
| `legal.contracts` | the client's own copy of the binder is that client's record. The practice's compiled binder with its checklist apparatus is this domain; a client's lone executed set DEFERS. | — |

**Sensitivity** — `potentially_sensitive`. §2.9's phrase. A binder contains executed originals, signatures and often account details — §8.4 names 'account statements' among the corpus's sensitive material. No handling class is set here.

---

### 31. `law.contract-negotiation` — Contract drafting and negotiation work product

The legal function's record of getting a contract agreed — playbooks, marked-up drafts, issue lists and approvals.

**provenance** `proposal`

**Schema**

| Field | Type | Ceiling | Example | Why this field, in this domain |
|---|---|---|---|---|
| `counterparty` | string | `validated` | the organisation on the other side of the draft | §3.8's roles rule; the counterparty is the spine practitioners navigate contract work by, and it is not the client and not the author. |
| `contract_type` | string | `llm_supported` | the kind of agreement being negotiated | Read from the operative provisions rather than a label. Values are corpus-derived per §3.12. |
| `draft_round` | string | `validated` | which exchange a draft belongs to | Negotiation produces long chains of near-identical files. Round is what makes them a sequence rather than an undifferentiated version family, and it is normally in the filename or a footer. |
| `markup_origin` | string | `validated` | which side marked up this draft | The single most useful fact in a negotiation folder and the easiest to lose. §3.8's roles rule again — it is a role, not authorship metadata. |
| `issue` | string | `llm_supported` | an open point tracked across the negotiation | Issue lists are prose tables. §3.6 requires the cited span before an issue becomes a fact. |
| `approval_status` | string | `validated` | the internal approval a deviation carries | Playbook-driven negotiation records deviations and who approved them; stated in a labeled slot on the approval record. |

**Recognition**

| | |
|---|---|
| **deterministic** — pattern *plus* corroborating context | • a contract document containing tracked-change or comment metadata (§2.3's DOCX structure) together with a counterparty name in a footer or filename convention<br>• an issues or open-points list pairing clause references with positions taken by each side<br>• a playbook document pairing standard positions with fallback positions per clause |
| **needs LLM** | • a clean redraft with the tracked changes accepted, where the round is only recoverable from the covering email<br>• distinguishing a negotiation draft from a template and from an executed contract<br>• reading which side proposed a change when the markup is anonymised |
| **never alone** | • tracked changes — every collaborative document has them<br>• a contract document: this is the loudest false positive in the slice, because every corpus contains employment contracts, leases, terms of service and supplier agreements that no legal function ever negotiated<br>• the word 'draft'<br>• a clause-numbered structure |

**Work types** — playbook · standard form · first draft · marked-up draft · clean redraft · issues list · negotiation note · deviation approval · signature-ready version

**Grouping reasons** — one contract across its negotiation rounds as a version family (§2.9's “duplicate and version-family signals”) · all contracts with one counterparty · a playbook with the negotiations it governed

**Template** — `counterparty → contract → document type`  (time first: no)

> §5.5's context rule with counterparty as the spine, because in-house contract work is not organised by matter and often has no matter at all. Round is ordering within the contract, not a level: §5.9 warns against 'a large number of tiny folders'.

**Collides with**

| Domain | Signal that separates them | Design cite |
|---|---|---|
| `legal.contracts` | slice 05 owns a contract as a party's own record — the signed lease, the supplier agreement. This domain owns the NEGOTIATION APPARATUS around it: playbooks, marked-up rounds, issue lists, deviation approvals. A file with only an executed contract and no apparatus DEFERS to slice 05. | — |
| `law.transactional-deal` | a deal's drafts are negotiation work product too. Where a code-named transaction exists, the deal domain is the better home; this domain covers standing contract work with no deal. | — |

**Sensitivity** — `potentially_sensitive`. §2.9's phrase. Negotiation work product records the positions a party was prepared to concede. No handling class is set here.

---

### 32. `law.corporate-secretarial` — Corporate secretarial and entity records

The constitutional and decision-making record of a legal entity — constitution, registers, minutes and resolutions.

**provenance** `proposal`

**Schema**

| Field | Type | Ceiling | Example | Why this field, in this domain |
|---|---|---|---|---|
| `entity` | string | `validated` | the company or other body the record belongs to | The organising spine of the whole domain. A group corpus holds dozens of entities and a minute filed against the wrong one is worse than a lost minute. |
| `entity_identifier` | string | `validated` | the registration number in the entity's home registry | The only unambiguous entity key, since names repeat and change. Formats are registry-specific and jurisdiction-bound, so the field is neutral and no pattern is authored here. |
| `record_type` | string | `validated` | the kind of constitutional record | Read from the title block. §3.11 already uses `record_type` as a Finance field name and it is reused rather than renamed. |
| `meeting_date` | date | `direct` | the date of the meeting or resolution | Minutes and resolutions are dated in a labeled header slot. §3.10's narrow parsing applies. |
| `decision_body` | string | `validated` | the board, a committee, or the members | Different bodies have different powers and their records must not merge. Stated in the header of every minute. |

**Recognition**

| | |
|---|---|
| **deterministic** — pattern *plus* corroborating context | • a minute document whose header pairs an entity name with a meeting date AND a decision body, followed by resolution or noting text<br>• a written resolution containing an entity name, a resolution number or heading, and a signature or consent block<br>• a statutory register — a table of officers, members or charges — headed with an entity name and registration number |
| **needs LLM** | • a draft minute circulated before approval<br>• distinguishing board minutes from ordinary management meeting minutes, which look identical<br>• recognising which entity in a group a resolution belongs to when only a trading name is used |
| **never alone** | • meeting minutes — every organisation produces them and almost none are board minutes<br>• the words 'resolution', 'board' or 'register' — all are ordinary business words, and 'resolution' also means screen resolution and dispute resolution<br>• a company name<br>• a signature block |

**Work types** — constitution or articles · board minutes · shareholder or member minutes · written resolution · statutory register · officer appointment record · share record · filing confirmation · entity summary

**Grouping reasons** — one entity's constitutional record · one meeting with its agenda, papers and minutes · a group's entities as a related set

**Template** — `entity → record type → document type`  (time first: no)

> §5.5's context rule with entity as the spine and NO client level, because corporate secretarial work is organised by the entity whose record it is even when a practice keeps it for a client. §5.5's rule against time-first applies with full force — a constitutional record is a continuous history, not a series of years.

**Collides with**

| Domain | Signal that separates them | Design cite |
|---|---|---|
| `corp.business-formation` | a company's own corporate records are that company's business records. This domain applies where the material is maintained as a legal-function or company-secretarial record; a business owner's own copy of their incorporation certificate DEFERS to slice 05. | — |
| `law.regulatory-submission` | registry filings are both entity records and regulatory submissions. The filing confirmation belongs here; the substantive regulatory application belongs there. | — |

**Sensitivity** — `potentially_sensitive`. §2.9's phrase. Registers carry officers' and members' personal details and addresses. No handling class is set here.

---

### 33. `law.regulatory-submission` — Regulatory filings and submissions

What is submitted to a regulator or public authority, and what comes back.

**provenance** `proposal`

**Schema**

| Field | Type | Ceiling | Example | Why this field, in this domain |
|---|---|---|---|---|
| `regulator` | string | `validated` | the authority the submission goes to | The domain's spine. Regulators are jurisdiction-specific bodies and the gazetteer of them is not authored here — see law.matter-file's open_question. |
| `submission_reference` | string | `validated` | the reference the authority assigns | Formats are per-regulator, so the pattern is not hard-coded; the reference becomes a fact through the corroboration in recognition.deterministic. |
| `submitting_entity` | string | `validated` | the entity on whose behalf the submission is made | §3.8's roles rule: the submitting entity is frequently the client, sometimes a group member, and never the practice — three distinct roles that must not merge. |
| `submission_type` | string | `validated` | the regime or form the submission is made under | Read from the form header. Regimes and their forms are jurisdiction-bound and values are corpus-derived. |
| `submission_date` | date | `direct` | the date of lodgement or the receipt date | A receipt or acknowledgement carries a labeled timestamp. §3.10's narrow parsing applies and no deadline is computed. |

**Recognition**

| | |
|---|---|
| **deterministic** — pattern *plus* corroborating context | • a completed authority form — labeled fields plus a form identifier in a header or footer — together with a named authority<br>• an acknowledgement or receipt from a named authority carrying a submission reference<br>• a covering letter addressed to a named authority citing a regime and a reference |
| **needs LLM** | • a substantive submission written as a narrative document with no form structure<br>• distinguishing a regulatory submission from a grant application, a tender or a licence renewal notice<br>• recognising a foreign authority by name alone |
| **never alone** | • a completed form — the corpus is full of forms of every kind<br>• an authority's name appearing in body text: compliance training, news articles and terms of service name regulators constantly<br>• the word 'regulatory' or 'compliance'<br>• a reference number |

**Work types** — application form · notification · covering letter · supporting submission · acknowledgement or receipt · authority correspondence · information request · decision or approval · annual return

**Grouping reasons** — one submission with its supporting material and the authority's response · all submissions to one regulator for one entity · a submission with the internal approvals behind it

**Template** — `client → entity → regulator → submission → document type`  (time first: no)

> §5.5's context rule. Regulator before submission because a regime's vocabulary only makes sense once the authority is known. §5.8's uneven depth applies — a single-submission matter should collapse the last two levels.

**Collides with**

| Domain | Signal that separates them | Design cite |
|---|---|---|
| `law.corporate-secretarial` | registry filings sit in both. See that entry. | — |
| `law.compliance-programme` | a programme document describes what the organisation does; a submission is what it told an authority. Very different consequences, similar vocabulary. | — |
| `corp.regulatory-filings` | 05's entry is the same act from the submitting entity's side and carries `filing_entity`, `filing_period` and `submission_reference`. This entry claims the advising practice's file — the supporting submission, the drafts, the authority correspondence run under a matter. Slice 05 owns the party's own file; this slice owns the practitioner's. The mover is a practice-side signal — a matter reference, a fee-earner or counsel signature block, practice letterhead, an engagement letter. Absent one, this slice ABSTAINS and 05 wins. This is 05's own specialisation rule applied across the seam: 'the more specific domain wins where its own fields populate'. | — |

**Sensitivity** — `potentially_sensitive`. §2.9's phrase. Submissions frequently contain financial and personal information about the submitting entity and named individuals. No handling class is set here.

---

### 34. `law.compliance-programme` — Compliance programme materials

The standing apparatus by which an organisation tries to stay compliant — policies, training, monitoring and attestations.

**provenance** `proposal`

**Schema**

| Field | Type | Ceiling | Example | Why this field, in this domain |
|---|---|---|---|---|
| `programme_area` | string | `llm_supported` | the risk area the material addresses | Read from the substance; policy titles are frequently generic. §3.6 requires the cited span before it becomes a fact. |
| `owning_entity` | string | `validated` | the organisation the programme belongs to | Distinguishes an organisation's own programme from a counterparty's policy received during diligence — the same document type with the opposite meaning. |
| `policy_version` | string | `validated` | the version or effective-date marker | A superseded policy that looks current is this domain's characteristic failure. §2.9's “duplicate and version-family signals” apply. |
| `material_type` | string | `validated` | policy \| procedure \| training \| monitoring record \| attestation | These have very different audiences and retention profiles and are routinely mixed in one folder. |
| `effective_date` | date | `direct` | the stated effective or review date | Stated in a labeled control block on most policies. §3.10's narrow parsing applies. |

**Recognition**

| | |
|---|---|
| **deterministic** — pattern *plus* corroborating context | • a document control block — pairing a version, an owner and an effective or review date — inside a document whose title names a policy or procedure<br>• an attestation or acknowledgement record pairing named individuals with a policy version and a date<br>• a monitoring or testing record pairing control descriptions with testing outcomes, headed with an owning entity |
| **needs LLM** | • training material with no control block, where only the content shows it is compliance training rather than general onboarding<br>• distinguishing an organisation's own policy from a policy received from a counterparty or downloaded as a market example |
| **never alone** | • the word 'compliance' — it appears in engineering, accessibility, tax and product contexts constantly<br>• a policy document: HR, IT and security policies dominate most corpora and none of them is legal-function work product<br>• a training deck: this is the hazard this entry exists to name — compliance training is deliberately written in legal vocabulary and will match any rule keyed on legal words alone<br>• a legal citation inside a policy |

**Work types** — policy · procedure · code of conduct · training material · attestation record · monitoring or testing record · risk assessment · gap analysis · programme review

**Grouping reasons** — one programme area across its policy, training and monitoring · successive versions of one policy · an attestation cycle as a bounded set

**Template** — `entity → programme area → material type`  (time first: no)

> §5.5's context rule with no client or matter level, because a compliance programme is a standing function rather than an engagement. Where an external practice advises ON a programme, that advice belongs to law.opinions or law.matter-file instead.

**Collides with**

| Domain | Signal that separates them | Design cite |
|---|---|---|
| `career.continuing-education` | compliance training a person COMPLETED is that person's career record; compliance training an organisation MAINTAINS is this domain. A completion certificate naming an individual should route to slice 02. | — |
| `law.investigation` | a programme failure produces an investigation. The programme document is standing; the investigation is an episode. | — |
| `law.due-diligence` | a counterparty's policies collected in diligence are diligence material, not the corpus owner's programme. `owning_entity` is what separates them. | — |
| `corp.compliance-audit` | 05's entry is entity-level compliance EVIDENCE and audit — auditor, framework, audit period. This entry is the standing programme apparatus: policy, training, monitoring, attestation. They meet where an audit tests a programme, and 05's row already says an audit a regulator required produces documents that are both. | — |

**Sensitivity** — `potentially_sensitive`. §2.9's phrase. Attestation and monitoring records name individuals and record their conduct. Policies themselves are frequently not sensitive at all, which is why the marking sits at the domain level and the actual handling decision stays with P7 (§8.4).

---

### 35. `law.investigation` — Investigations

A bounded enquiry into what happened — the plan, the evidence collected, the interviews and the findings.

**provenance** `proposal`

**Schema**

| Field | Type | Ceiling | Example | Why this field, in this domain |
|---|---|---|---|---|
| `investigation_reference` | string | `validated` | the practice's or organisation's own reference for the enquiry | Investigations are frequently run without a case identifier and with deliberately uninformative names; the reference is often the only reliable key. |
| `commissioning_party` | string | `validated` | who instructed the investigation | §3.8's roles rule, and consequential: an investigation commissioned by a board, by a regulator or by a counterparty are three different things with three different postures. |
| `investigation_scope` | string | `llm_supported` | the question the enquiry was set to answer | Stated in a terms-of-reference document as prose. §3.6 requires the cited span. |
| `workstream` | string | `validated` | a strand of the enquiry | Investigations run parallel strands — document collection, interviews, forensic analysis — that produce separate outputs. |
| `interviewee_role` | string | `llm_supported` | the role a person had in the events, not their name | Deliberately a ROLE field rather than a person field. §3.8 requires roles as distinct facets, and an investigation file is the place where naming individuals as a folder dimension would do the most harm — §3.8: “A folder should not become a collection point for everything produced by the same person or organization.” |

**Recognition**

| | |
|---|---|
| **deterministic** — pattern *plus* corroborating context | • a terms-of-reference document pairing a commissioning party with a stated scope, carrying a matter or investigation reference<br>• an interview memorandum whose header pairs an interviewee designation with a date and an attendee list, under a common investigation reference<br>• a findings or report document whose structure pairs allegations or issues with conclusions, under an investigation reference |
| **needs LLM** | • material collected during an investigation that carries no investigation marking at all<br>• distinguishing an investigation interview memorandum from an HR grievance record or a journalist's interview notes<br>• reading the scope from a covering email when no terms of reference exist |
| **never alone** | • the word 'investigation' — it names product, security, medical and journalistic work<br>• interview notes<br>• a findings or issues list<br>• an allegation-shaped sentence |

**Work types** — terms of reference · investigation plan · collection log · interview memorandum · forensic report · chronology · findings report · remediation plan · regulator update

**Grouping reasons** — one investigation across its workstreams · interview material from one enquiry · a findings report with the evidence it cites

**Template** — `client → investigation → workstream → document type`  (time first: no)

> §5.5's context rule. Workstream before document type because an interview memorandum and a forensic report belong to different strands and mixing them destroys the enquiry's shape.

**Collides with**

| Domain | Signal that separates them | Design cite |
|---|---|---|
| `law.matter-file` | an investigation is usually opened as a matter. It has its own entry because its schema — commissioning party, scope, workstream — is genuinely different, not because it sits outside the matter. | — |
| `law.document-review` | investigations run document review. Same work product, different purpose — §3.9's distinction: “Topic answers what a file is about, while purpose answers what the file was for.” | §3.9 “Topic answers what a file is about, while purpose answers what the file was for.” |

**Sensitivity** — `potentially_sensitive`. §2.9's phrase. An investigation file records allegations about named individuals, frequently before anything is established, and §4.9's protection principle applies: “Rare but sensitive files such as passports, visas, and legal documents may be surfaced as protected records even when they do not meet a normal group-size threshold.” No handling class is set here.

**Open question — Joseph's call, unresolved**

> Investigation files are the strongest case in this slice for a protection posture stronger than the general legal safety domain — they record unproven allegations about identified people, and §8.4's classes are framed around the corpus owner's own sensitivity rather than third parties'. Whether P7's vocabulary needs a class for material that is sensitive about SOMEONE ELSE is a P7 question raised here and not answered here. It applies equally to law.family-law, law.criminal-defence and law.immigration-casework.

---

### 36. `law.ip-prosecution` — Intellectual property prosecution

Obtaining and maintaining registered rights — applications to an IP office, the office's objections and the responses.

**provenance** `proposal`

**Schema**

| Field | Type | Ceiling | Example | Why this field, in this domain |
|---|---|---|---|---|
| `ip_office` | string | `validated` | the office the application is before | The domain's spine. One invention or mark is prosecuted before many offices simultaneously and the files must not merge. |
| `application_number` | string | `validated` | the number the office assigns | Formats are per-office and the same right carries a different number in every office, which is why this is a validated field with office corroboration and never a bare pattern match. |
| `family_reference` | string | `validated` | the practice's own reference tying related filings together | The only thing that links one right's filings across offices. Usually the practice's own docket reference rather than any official number. |
| `right_type` | string | `validated` | patent \| trade mark \| design \| other registered right | Different rights have different procedures and different documents; the type is on the face of every office communication. |
| `applicant` | string | `validated` | the entity in whose name the right is sought | §3.8's roles rule: applicant, inventor and owner are three roles that frequently name different people and are routinely conflated. |
| `prosecution_stage` | string | `validated` | the stage the document belongs to | Prosecution is a long sequence of exchanges and the stage is stated on each office communication. Stage names are office-specific and values are corpus-derived. |

**Recognition**

| | |
|---|---|
| **deterministic** — pattern *plus* corroborating context | • an office communication whose header pairs a named IP office with an application number AND an applicant name<br>• a specification document containing both a claims section and an abstract, together with an application or docket reference<br>• a docket or renewals report pairing family references with office deadlines |
| **needs LLM** | • a draft specification before filing, with no application number<br>• distinguishing prosecution material from IP litigation and from IP licensing, which share vocabulary and parties<br>• recognising an office communication in an unfamiliar language |
| **never alone** | • the words 'patent', 'trade mark' or 'copyright' — they appear in product documentation, marketing, terms of service and academic writing<br>• a claims-and-abstract structure: a scientific paper has an abstract too<br>• an application-number-shaped string<br>• a priority date |

**Work types** — draft specification · filed application · office action or examination report · response to office action · grant or registration certificate · renewal record · assignment · docket report · search or watch report

**Grouping reasons** — one right's family across offices · one office's file from filing to grant · an office action with the response it drew

**Template** — `client → right family → ip office → document type`  (time first: no)

> §5.5's context rule with the family above the office, so one invention's national filings stay together rather than being scattered across office folders — the same reasoning §5.5 gives for keeping a course above its work types.

**Collides with**

| Domain | Signal that separates them | Design cite |
|---|---|---|
| `res.patent-disclosure` | an invention disclosure and a draft specification are research artifacts by content. The office, the application number and the claims structure are the practice-side evidence; without them slice 03 should win. | — |
| `law.regulatory-submission` | an IP office is an authority and a filing is a submission. This domain exists separately because its schema — family, right type, prosecution stage — is genuinely different and its files are long-running. | — |
| `legal.ip-registration` | near-total overlap by document type — 05 lists application, office action, response, grant, renewal, assignment. 05 owns them as the rights holder's record; this entry owns the prosecuting practice's docket, with the family reference across offices as its distinguishing field. Where there is no practice-side signal, 05 wins. | — |

**Sensitivity** — `potentially_sensitive`. §2.9's phrase. Unpublished applications are commercially confidential and their premature disclosure has consequences. No handling class is set here.

---

### 37. `law.immigration-casework` — Immigration casework

An application or claim made on a person's behalf to an immigration authority, and the evidence assembled for it.

**provenance** `proposal`

**Schema**

| Field | Type | Ceiling | Example | Why this field, in this domain |
|---|---|---|---|---|
| `applicant` | string | `validated` | the person the application is for | The spine of the file. §3.8's roles rule keeps the applicant distinct from a sponsor and from the client, who are frequently three different people or an employer. |
| `immigration_authority` | string | `validated` | the authority the application is made to | Determines the route vocabulary, the form set and the identifier format — none of which is authored here because all of it is jurisdiction-specific. |
| `application_route` | string | `validated` | the route or category applied under | Stated on the form. Route names and their meanings differ completely between countries and change often, so values are corpus-derived and this catalogue equates none of them. |
| `case_reference` | string | `validated` | the reference the authority assigns | Formats are authority-specific; corroboration is required as in every other identifier field in this slice. |
| `sponsor` | string | `validated` | the employer, institution or family member supporting the application | §3.8's roles requirement. The sponsor is frequently the paying client while the applicant is the subject — a distinction that must survive into the fact layer. |

**Recognition**

| | |
|---|---|
| **deterministic** — pattern *plus* corroborating context | • a completed authority application form — form identifier plus labeled applicant fields — together with a named immigration authority<br>• an authority decision or acknowledgement letter carrying a case reference and an applicant name<br>• a supporting-evidence bundle index listing identity, status and relationship documents, under a common case reference |
| **needs LLM** | • a personal statement or narrative account prepared for an application<br>• distinguishing a legal practice's casework file from an individual's own copies of their immigration paperwork<br>• recognising an authority in an unfamiliar jurisdiction |
| **never alone** | • a passport, visa or identity document — §4.9 already treats these as protected records in their own right and they belong to the identity safety domain, not to this one<br>• a travel document or boarding pass<br>• the word 'visa' — it also names a payment network<br>• a foreign address or nationality |

**Work types** — application form · supporting statement · evidence bundle · sponsor documentation · authority correspondence · decision letter · appeal or review notice · biometrics or appointment record

**Grouping reasons** — one application for one applicant — a purpose-coherent packet in exactly §3.9's sense, “content-incoherent but purpose-coherent” · a family's linked applications · an application with the decision and any challenge to it

**Template** — `client → applicant → application → document type`  (time first: no)

> §5.5's context rule. Applicant sits above application because one person may make several over years and their history is the useful unit. Note the tension with §3.8's rule against person-as-collector: this is a case where the person IS the subject rather than the author, which §3.8's own wording distinguishes.

**Collides with**

| Domain | Signal that separates them | Design cite |
|---|---|---|
| `pers.identity-document` | the identity documents inside an immigration file are identity material in their own right. §4.9: “Rare but sensitive files such as passports, visas, and legal documents may be surfaced as protected records even when they do not meet a normal group-size threshold.” | §4.9 “Rare but sensitive files such as passports, visas, and legal documents may be surfaced as protected records” |
| `pers.travel-visa-entry` | an individual organising their own immigration paperwork is not running a casework file. Absence of a practice reference and a matter should route it to the personal side. | — |
| `admin.immigration` | near-total overlap. 05 owns the applicant's own paperwork and already carries `applicant`, `route_or_category`, `application_reference` and `sponsor`. This entry claims only a practice's casework file. Slice 05 owns the party's own file; this slice owns the practitioner's. The mover is a practice-side signal — a matter reference, a fee-earner or counsel signature block, practice letterhead, an engagement letter. Absent one, this slice ABSTAINS and 05 wins. This is 05's own specialisation rule applied across the seam: 'the more specific domain wins where its own fields populate'. | — |

**Sensitivity** — `potentially_sensitive`. §2.9's phrase. Immigration files combine identity documents, family details and frequently accounts of persecution or hardship — §8.4's “identity documents” and “medical information” both routinely appear. No handling class is set here; see law.investigation's open_question.

---

### 38. `law.family-law` — Family law matters

Proceedings and agreements about relationships, children and the financial consequences of a family breaking down.

**provenance** `proposal`

**Schema**

| Field | Type | Ceiling | Example | Why this field, in this domain |
|---|---|---|---|---|
| `case_identifier` | string | `validated` | the identifier of the proceeding | Joins the file to its proceeding where one exists; much family work is done without any proceeding at all. |
| `family_matter_type` | string | `validated` | the kind of family matter | Read from the document's own heading. The available proceedings and their names differ profoundly by jurisdiction — some categories do not exist in some systems — so values are corpus-derived and none is equated here. |
| `party` | string | `validated` | an adult party to the matter | Read from a caption or an agreement's parties block. |
| `child_subject` | string | `possible` | a child the proceedings concern, where named | Deliberately capped at `possible` and NEVER destination-eligible. A folder named after a child would put a minor's name into a directory listing, a search index and every UI surface. §3.8's rule against person-as-collector is reinforced here by §8.4's requirement that protected material 'should not display raw content in general group summaries'. |
| `financial_scope` | string | `llm_supported` | the financial issues in the matter | Prose. §3.6 requires the cited span before it becomes a fact. |

**Recognition**

| | |
|---|---|
| **deterministic** — pattern *plus* corroborating context | • a captioned family-court document pairing a case identifier with a named family court or division<br>• a financial disclosure form — labeled income, asset and liability fields — filed under a case identifier<br>• an agreement whose operative provisions concern arrangements for children or division of family assets, carrying a matter reference |
| **needs LLM** | • correspondence and statements with no caption, where the subject matter is the only signal<br>• distinguishing a family agreement from an ordinary commercial one<br>• recognising a family matter conducted entirely by email |
| **never alone** | • the words 'divorce', 'custody', 'separation' — they appear in journalism, fiction, counselling material and personal correspondence<br>• a financial statement — §8.4's “account statements” belong to the finance domains unless a case identifier corroborates<br>• names of family members<br>• a marriage or birth certificate: those are identity documents (§4.9) before they are anything else |

**Work types** — application or petition · financial disclosure form · statement · consent or separation agreement · parenting plan · court order · expert or welfare report · correspondence

**Grouping reasons** — one family matter across its documents · the financial strand of a matter as a set · an agreement with the order that made it binding

**Template** — `client → matter → issue strand → document type`  (time first: no)

> §5.5's context rule, with 'issue strand' rather than any person-based level — see the `child_subject` field's reasoning. §5.9's scoped General branch is the right fallback for uncategorised material here rather than any label naming an individual.

**Collides with**

| Domain | Signal that separates them | Design cite |
|---|---|---|
| `legal.wills-trusts-estates` | family and estate planning documents overlap in a household's own records. The finance/admin slice owns a person's own will and family paperwork; this domain owns a practice's casework. Where a file is a household's own copy, this domain DEFERS. | — |
| `legal.litigation-dispute` | a person's own divorce paperwork is their personal record. Absence of a practice reference and a matter should route it away from this slice. | — |
| `legal.court-records` | a party's own family-court paperwork is 05's court-records or personal-slice material. This entry requires a practice-side signal. | — |

**Sensitivity** — `potentially_sensitive`. §2.9's phrase, and this is among the strongest cases for it in the whole catalogue: family files combine §8.4's “medical information”, “account statements” and “identity documents” with information about children. No handling class is set here; see law.investigation's open_question.

---

### 39. `law.criminal-defence` — Criminal defence files

Acting for a person accused of an offence — the charge, the prosecution material, the defence case and the outcome.

**provenance** `proposal`

**Schema**

| Field | Type | Ceiling | Example | Why this field, in this domain |
|---|---|---|---|---|
| `case_identifier` | string | `validated` | the identifier of the prosecution | Joins the file to the proceeding. Criminal identifier formats differ from civil ones within the same jurisdiction, which is one more reason no pattern is authored here. |
| `court` | string | `validated` | the court the matter is before | Criminal matters move between courts as they progress and the file must record which stage's court a document belongs to. |
| `charge` | string | `validated` | the offence alleged, as stated on the charging document | Read from the charging document's own text. This catalogue records what the document SAYS is alleged and asserts nothing about the accused. |
| `accused` | string | `possible` | the person charged | Capped at `possible` and never destination-eligible. A folder named after an accused person publishes an allegation in every directory listing; §8.4 requires that protected material “should not display raw content in general group summaries”, and a folder name is the most general summary there is. |
| `procedural_stage` | string | `validated` | the stage the document belongs to | Criminal procedure is stage-driven and the stage is normally stated. Stage names are jurisdiction-bound; values are corpus-derived. |

**Recognition**

| | |
|---|---|
| **deterministic** — pattern *plus* corroborating context | • a charging or indictment document pairing a court, a case identifier and a stated offence<br>• prosecution disclosure material delivered under a case identifier with a schedule of served and unused material<br>• a custody, bail or sentencing document carrying a case identifier and a court name |
| **needs LLM** | • defence working notes with no header<br>• distinguishing prosecution material served on the defence from the defence's own work product<br>• recognising a criminal matter from correspondence alone |
| **never alone** | • offence vocabulary — journalism, fiction, academic criminology and news alerts are full of it<br>• a police reference number<br>• the words 'charge', 'offence', 'arrest'<br>• an identity document |

**Work types** — charging document · prosecution disclosure schedule · served evidence · unused material schedule · defence statement · instructions and proof of evidence · bail application · mitigation · sentencing remarks · outcome record

**Grouping reasons** — one prosecution across its stages · prosecution material as one served set · the defence's own work product as a set

**Template** — `client → matter → procedural stage → document type`  (time first: no)

> §5.5's context rule, with stage rather than any person-based level for the reason given under `accused`. Stage is genuinely how criminal files are worked, which makes the safer choice also the better one.

**Collides with**

| Domain | Signal that separates them | Design cite |
|---|---|---|
| `law.ediscovery-production` | prosecution disclosure is a served document set with a schedule, structurally close to a production. The schedule vocabulary and the absence of a load file distinguish them. | — |
| `legal.litigation-dispute` | an individual's own copies of their case paperwork are their personal records. Absence of a practice reference should route them away from this slice. | — |
| `legal.court-records` | an accused person's own copies of court-issued documents are 05's. This entry requires a practice-side signal. | — |

**Sensitivity** — `potentially_sensitive`. §2.9's phrase. A criminal file records an allegation against an identified person and frequently the personal details of complainants and witnesses. No handling class is set here; see law.investigation's open_question.

---

### 40. `law.estates-administration` — Estates administration

Administering a deceased person's estate — the grant, the assets and liabilities, and the distribution.

**provenance** `proposal`

**Schema**

| Field | Type | Ceiling | Example | Why this field, in this domain |
|---|---|---|---|---|
| `estate` | string | `validated` | the estate being administered | The file's spine. Named on every document in the administration. |
| `grant_reference` | string | `validated` | the reference of the authority to administer | The instrument that authorises everything else in the file. The instrument's name and format are jurisdiction-specific — some systems have no equivalent step at all — so no pattern is authored here. |
| `personal_representative` | string | `validated` | the person or institution administering | §3.8's roles rule: the representative is often the client, sometimes the practice, and is never the deceased — three roles routinely conflated in these files. |
| `estate_stage` | string | `validated` | the stage of the administration | Administration is a defined sequence and the stage is normally stated on the document. Values are corpus-derived because the sequence differs by system. |
| `asset_class` | string | `validated` | the kind of asset a document concerns | Estate files are organised around assets in practice. Read from the document's own subject line or heading. |

**Recognition**

| | |
|---|---|
| **deterministic** — pattern *plus* corroborating context | • a grant or authority document naming an estate and a personal representative, issued by a named court or registry<br>• an estate account — a statement of assets, liabilities and distributions headed with an estate name<br>• correspondence with an asset holder citing an estate name and a grant reference |
| **needs LLM** | • asset correspondence that names only the deceased and no estate reference<br>• distinguishing estate administration from estate PLANNING done during a person's life, which shares vocabulary and parties |
| **never alone** | • a will — a person's own will is estate planning and belongs to the finance/admin slice; a will used in an administration acquires this domain only through the grant and the estate reference<br>• a death certificate — an identity document first (§4.9)<br>• the words 'estate' or 'beneficiary' — 'estate' also names real estate and 'beneficiary' appears in insurance and pensions<br>• an account statement |

**Work types** — grant application · grant of authority · asset schedule · estate accounts · asset holder correspondence · distribution record · beneficiary correspondence · tax return for the estate · final account

**Grouping reasons** — one estate across its administration · asset correspondence by asset class · the accounts with the distributions they record

**Template** — `client → estate → estate stage → document type`  (time first: no)

> §5.5's context rule. Stage rather than asset class at the third level because an administration is worked as a sequence and stage is the dimension that stays meaningful when a file is reopened years later.

**Collides with**

| Domain | Signal that separates them | Design cite |
|---|---|---|
| `legal.wills-trusts-estates` | the lead brief assigns personal wills and estate planning to slice 05, and this domain DEFERS to it for everything done during the person's life. This domain begins at the administration and requires an estate reference or a grant to activate. | — |
| `legal.court-records` | 05 notes that a grant of representation is a court-issued document and an estate document at once. Agreed; this entry claims the practice's administration file built on that grant. | — |

**Sensitivity** — `potentially_sensitive`. §2.9's phrase. Estate files combine §8.4's “account statements” and “identity documents” with a deceased person's affairs and beneficiaries' personal details. No handling class is set here.

---

### 41. `law.conveyancing` — Property conveyancing

Transferring or charging an interest in land — title, searches, contract, completion and registration.

**provenance** `proposal`

**Schema**

| Field | Type | Ceiling | Example | Why this field, in this domain |
|---|---|---|---|---|
| `property` | string | `validated` | the land or premises | The file's spine and the one thing every document in it shares. An address alone is weak; the title reference is what makes it precise. |
| `title_reference` | string | `validated` | the registry's identifier for the title | Land registration systems and their identifier formats are jurisdiction-specific, and some systems are deeds-based with no title number at all. The field is neutral; no pattern is authored here. |
| `transaction_side` | string | `validated` | which side the practice acts for | §3.8's roles rule, and the field that decides how every document in the file is read: a search result means opposite things to a buyer and a seller. |
| `conveyancing_stage` | string | `validated` | the stage the document belongs to | Conveyancing is a strictly sequenced process and stage is how practitioners navigate the file. Stage names are jurisdiction-bound; values are corpus-derived. |
| `completion_date` | date | `direct` | the date the transfer completed | Stated on the completion statement and the transfer as a labeled slot. §3.10's narrow parsing applies. |

**Recognition**

| | |
|---|---|
| **deterministic** — pattern *plus* corroborating context | • a title extract or register copy issued by a named land registry, carrying a title reference<br>• a search result from a named authority citing a property address, filed alongside a matter reference<br>• a transfer or conveyance instrument pairing a property description with parties and an execution block |
| **needs LLM** | • an enquiry reply written as free correspondence<br>• distinguishing a conveyancing file from a landlord's own tenancy paperwork or a homeowner's purchase folder<br>• reading which side the practice acts for when only the correspondence shows it |
| **never alone** | • a property address — the corpus is full of addresses<br>• a lease or tenancy agreement: a party's own lease belongs to the finance/admin slice<br>• a floor plan or survey<br>• the word 'property' — it also names an attribute in code and a characteristic in prose |

**Work types** — title extract · search result · enquiries and replies · draft contract · report on title · mortgage instruction · transfer instrument · completion statement · registration application · post-completion confirmation

**Grouping reasons** — one property transaction across its stages · searches as one bounded set · a chain of linked transactions

**Template** — `client → property → conveyancing stage → document type`  (time first: no)

> §5.5's context rule with the property as the spine, because one client may transact several properties and one property may be transacted repeatedly. §5.5's rule against time-first applies: completion dates would scatter a chain.

**Collides with**

| Domain | Signal that separates them | Design cite |
|---|---|---|
| `legal.lease` | an owner's or tenant's own property paperwork — the signed lease, the mortgage statement — is that person's record and DEFERS to slice 05. This domain requires practice-side apparatus: searches, enquiries, a report on title, a matter reference. | — |
| `law.transactional-deal` | a property transaction inside a larger corporate deal is a workstream of that deal. Where a code-named transaction exists, the deal domain is the better spine. | — |

**Sensitivity** — `potentially_sensitive`. §2.9's phrase. Conveyancing files combine addresses, identity documents and funding details — §8.4's “account statements” and “identity documents” both appear. No handling class is set here.

---

### 42. `law.bar-admission-cle` — Admission, licensing and continuing legal education

A practitioner's own right to practise — admission, licensing, insurance and the education required to keep it.

**provenance** `proposal`

**Schema**

| Field | Type | Ceiling | Example | Why this field, in this domain |
|---|---|---|---|---|
| `admitting_authority` | string | `validated` | the body that admits or licenses | The spine; a practitioner admitted in several places holds parallel obligations to each. Bodies and their names are jurisdiction-specific and are not enumerated here. |
| `practitioner_identifier` | string | `validated` | the number the authority assigns | Formats are per-authority. Corroboration required as elsewhere in this slice. |
| `credential_type` | string | `validated` | admission \| practising certificate \| licence \| insurance | These have different renewal cycles and different consequences on lapse, and are routinely kept in one folder. |
| `compliance_period` | string | `validated` | the reporting period a record counts toward | Continuing-education obligations are period-based and a record filed to the wrong period is effectively lost. Read from the certificate or the return. |
| `activity_title` | string | `direct` | the course, session or activity attended | Named on the completion certificate in a labeled slot, so `direct` per §3.5. |

**Recognition**

| | |
|---|---|
| **deterministic** — pattern *plus* corroborating context | • a completion certificate naming a named accrediting body AND an activity AND a credit or hours value, addressed to a named practitioner<br>• a practising certificate or licence document issued by a named authority carrying a practitioner identifier and a validity period<br>• a compliance return pairing activities with a reporting period, addressed to an authority |
| **needs LLM** | • course materials kept from an activity, with no certificate<br>• distinguishing professional continuing education from ordinary employer training or academic study |
| **never alone** | • a completion certificate — every online course issues one and almost none are accredited legal education<br>• the words 'CLE', 'CPD' or their equivalents alone: the abbreviations are used by many professions<br>• a course name<br>• a professional body's name in body text |

**Work types** — admission record · practising certificate · licence · insurance certificate · completion certificate · compliance return · course materials · renewal correspondence · disciplinary record

**Grouping reasons** — one compliance period's activities and its return · all credentials from one authority · a credential with its renewals as a sequence

**Template** — `admitting authority → credential type → compliance period → document type`  (time first: no)

> §5.5's context rule. This is the one entry in the slice where a period level is clearly right — the obligation IS periodic — but it still sits third, under the authority and the credential, because §5.5 keeps time below function for record domains.

**Collides with**

| Domain | Signal that separates them | Design cite |
|---|---|---|
| `career.professional-license` | slice 02 already has `career.professional-license` AND `career.certification` AND `career.continuing-education` — three entries covering exactly this material from the practitioner's own side. This entry survives only if the admitting-authority spine and the compliance-period structure are worth a legal-specific domain; otherwise it collapses into 02. See the open_question. | — |
| `acad.course-enrollment` | CLE materials look like course materials. §3.5's course rule fires on academic context; accredited professional education has an accrediting body and a compliance period instead, which is the distinguishing signal. | §3.5 “becomes a course fact only when the engine finds a course-code pattern together with academic context” |
| `career.continuing-education` | the direct duplicate. 02's entry owns continuing professional education for any profession; this entry would own only the legally-regulated form of it, keyed on an admitting authority. Weakest entry in this slice on that basis. | — |

**Sensitivity** — `potentially_sensitive`. §2.9's phrase. Licensing and disciplinary records are personal professional records about an identified individual. Most CLE certificates are not sensitive at all, which is again why the actual handling decision is P7's (§8.4) and not this catalogue's.

**Open question — Joseph's call, unresolved**

> This entry is the practitioner's OWN record, not a client's, and slice 02 already publishes `career.professional-license`, `career.certification` and `career.continuing-education` covering the same material. Should it exist here at all? It is retained because the admitting-authority spine and the compliance-period structure are specific to regulated legal practice and 02's entries are profession-neutral, but this is the entry a reviewer is most entitled to delete. Joseph's call: keep as a legal-specific specialisation, or drop and let slice 02 own it.

---

### 43. `law.pro-bono` — Pro bono and publicly funded work

Work done free or under public funding — the eligibility, the funding authority and the reporting that comes with it.

**provenance** `proposal`

**Schema**

| Field | Type | Ceiling | Example | Why this field, in this domain |
|---|---|---|---|---|
| `funding_basis` | string | `validated` | pro bono \| publicly funded \| clinic \| referred | The only field that genuinely distinguishes this domain from law.matter-file, which is why this entry's open_question asks whether it is a domain at all. |
| `funding_authority` | string | `validated` | the body funding or certifying the work | Publicly funded work is administered by jurisdiction-specific bodies with their own references and reporting; pro bono work often has a clearing organisation instead. |
| `funding_reference` | string | `validated` | the certificate or authorisation reference | Authorises the work and bounds it. Formats are authority-specific; corroboration required. |
| `referral_source` | string | `validated` | the clinic, charity or scheme the matter came from | §3.8's roles rule: the referrer is not the client and is frequently the only organisation named on the file. |
| `matter_reference` | string | `validated` | 10432-0007 | Pro bono matters are opened as matters and carry the same spine as everything else in this slice. |

**Recognition**

| | |
|---|---|
| **deterministic** — pattern *plus* corroborating context | • a funding certificate or authorisation from a named funding body carrying a reference and a scope limit<br>• an eligibility assessment form whose labeled fields pair means or merits criteria with an outcome<br>• a scheme or clinic referral form naming a referring organisation and a client |
| **needs LLM** | • a matter run pro bono with nothing on the file saying so<br>• distinguishing a reduced-fee arrangement from genuinely unbilled work |
| **never alone** | • the phrase 'pro bono' — it appears in marketing material, firm brochures, CVs and award submissions far more often than in casework<br>• absence of a bill<br>• a charity's name<br>• an eligibility form |

**Work types** — referral form · eligibility assessment · funding certificate · scope authorisation · funding body correspondence · claim for costs · reporting return · closing report to the scheme

**Grouping reasons** — one funded matter with its authorisation and reporting · all matters from one referral scheme · a reporting period's returns

**Template** — `funding basis → client → matter → document type`  (time first: no)

> §5.5's context rule. The dimension order is deliberately unusual — funding basis first — because that is the only arrangement under which this domain is distinguishable in a tree from law.matter-file, and seeing it written out is what makes the open_question below concrete.

**Collides with**

| Domain | Signal that separates them | Design cite |
|---|---|---|
| `law.matter-file` | this is a matter file with a funding overlay. Every other field is inherited. See the open_question. | — |
| `law.time-and-billing` | publicly funded work has its own costs claims and reporting, which are billing artefacts under a different regime. | — |

**Sensitivity** — `potentially_sensitive`. §2.9's phrase. Eligibility assessments record a person's means and circumstances in detail — §8.4's “account statements” and “medical information” both routinely appear in them. No handling class is set here.

**Open question — Joseph's call, unresolved**

> Is pro bono a DOMAIN or a FACET on law.matter-file? Its schema is law.matter-file's plus a funding basis, a funding authority and a referral source, which is the profile of a facet rather than a domain. It is written as a domain here because the funding paperwork is a genuinely distinct document set with its own authority and its own reporting, but a reviewer could reasonably collapse it. If it collapses, `funding_basis` becomes a field on law.matter-file and the funding documents become work types there. Joseph's call.

---

## Every open question, in one place

18 questions, copied verbatim from the entries above. All are Joseph's; none is resolved here.

**`law.matter-file`**

> Does the domain library ship ONE jurisdiction-neutral legal-practice family with `jurisdiction` as a fact field, or per-jurisdiction variants of each domain? Court names, case-identifier formats, filing-type names, party designations and procedural stage names differ by country and by court within one country. This catalogue is authored jurisdiction-neutrally at the schema level and confines jurisdiction-bound vocabulary to `work_types` and `recognition`, but a jurisdiction-neutral rule cannot recognise a local filing type, and a per-jurisdiction family multiplies the library. Joseph's call.

**`law.client-intake`**

> §3.8's `our_firm` / `client` pair presumes an external adviser. In an in-house legal function the 'client' is a business unit of the same company and there is no external client to name, so intake, conflicts and billing either collapse or change meaning. Does an in-house corpus reuse this family with `client` bound to an internal business unit, or is it a separate domain family?

**`law.time-and-billing`**

> Client-money / trust-account ledgers were deliberately NOT given an entry in this slice. They are regulated practice records with a real claim to this supercategory, but they are also account records, which §8.4 names (“account statements”) and the finance slice owns. Does client money belong to the finance slice, to this one, or to both with a primary-home convention under §6.9?

**`law.court-filing-record`**

> Should a court or case identifier ever become a folder LEVEL? One dispute can carry several identifiers — a first-instance number, an appeal number, a registry reference — and they change as the case moves. A tree keyed on identifier splits one dispute; a tree keyed on the matter keeps it together but loses the identifier as a navigation handle. §5.4 says a template “defines the dimensions that are meaningful for one type of material”, and this is a dimension the design does not settle.

**`law.motions-and-briefs`**

> The word 'brief' is a false friend across jurisdictions — in some systems it names the written argument filed with an appellate court, in others it names the instructions a solicitor sends to counsel, which is a completely different domain with a different schema. Should the catalogue avoid the word entirely (as this entry does), or carry per-jurisdiction `work_types` vocabularies keyed on the `jurisdiction` fact? Same question as law.matter-file's, in its sharpest form.

**`law.document-review`**

> PRIVILEGE. A privilege log is a real, named work-product artefact and this entry lists it as a `work_type`. Nothing in this catalogue asserts that any file IS privileged, and no `privileged` field, flag or value is defined anywhere in this slice — deliberately. Privilege is a legal determination made by a lawyer about a specific document in a specific context; a document bearing a 'privileged and confidential' legend is not thereby privileged, and a privileged document often bears no legend at all. A wrong assertion is harmful in both directions. Joseph's calls, and they are two: (1) may the system record an OBSERVATION that a document bears a privilege legend — which is a fact about the text, not about the document's status — while still asserting nothing about privilege? (2) Does P7's handling-class vocabulary (§8.4) need a class for legal-professional-privilege material, given that §8.4's five classes are about personal sensitivity and privilege is a different axis entirely? Question (2) is a P7 vocabulary question and is not answered here.

**`law.ediscovery-production`**

> Document-identifier stamping conventions are jurisdiction- and vendor-specific, and the best-known one is a common-law practice convention rather than a universal standard. Should the catalogue carry a per-jurisdiction pattern list for production numbering, or refuse patterns entirely and require the corroborating load file in every case (which is what this entry currently does)? Refusing patterns is safer and will miss loose stamped pages that arrive without their load file.

**`law.evidence-exhibits`**

> Should `exhibit_identifier` be destination-eligible — i.e. may an exhibit label become a folder level? It is the handle practitioners navigate by, but labels are short, restart per proceeding, and are re-assigned when a bundle is repaginated, so a tree keyed on them goes stale. §5.4 leaves “which dimensions are optional, which ones are metadata only” to the template author, and this one is genuinely undecided.

**`law.depositions`**

> The deposition is a common-law discovery device with no direct equivalent in several major legal systems, and the systems that do have pre-trial witness examination give it different names, different roles and different paperwork. Does this entry stay as one jurisdiction-neutral 'examination of a witness outside court' domain — which is what the schema above attempts — or split per system? Same axis as law.matter-file's open_question, and this is the entry where a neutral abstraction is hardest to defend.

**`law.expert-materials`**

> An expert report is simultaneously a research artifact (research slice) and litigation work product (this slice). §3.11 preserves both fact sets, but placement needs one answer. Does the expert's duty declaration plus a case identifier make purpose win over topic, or should such files always be surfaced under §6.9's shared-material policy rather than placed? The design settles the fact layer and leaves the placement rule to the tree.

**`law.trial-preparation`**

> A bundle physically CONTAINS copies of documents that each have their own home. Is that a §6.9 shared-material case — “a shared branch, a primary-home convention, a reference or alias convention, or mandatory review” — or a §2.9 duplicate-family case, since the bundle is one new file rather than the same file in two places? The design settles neither, and the answer decides whether a bundle's contents are ever unpacked.

**`law.jury-materials`**

> This domain does not exist in large parts of the world, and where it exists it varies enormously — civil juries in some systems and not others, extensive selection procedures in some and none in others, and juror information that is restricted in some jurisdictions and open in others. Should a domain that is inapplicable to most corpora ship in the library at all, or activate only when a `jurisdiction` fact indicates a jury system? §3.11's rule — a schema activates 'when the evidence indicates that a domain is plausible' — is a per-file test, not a per-corpus one, and this is the clearest case where a per-corpus gate might be needed instead.

**`law.adr`**

> Arbitral confidentiality is a real obligation owed to a counterparty rather than a privacy interest of the corpus owner, and §8.4's handling classes run from 'Public or low sensitivity' to “Highly sensitive or credential-bearing” and are all framed around personal sensitivity. Is an obligation owed to someone else an axis P7's vocabulary needs, or does it collapse into the existing classes? This is a P7 vocabulary question raised here, not answered here.

**`law.legal-research`**

> Citation identifier patterns are already catalogued for the research slice (`planning/deferred-catalogues/06-citation-identifier-patterns`), which covers DOI, ISBN, URL and author-year forms. Legal citation is a separate and jurisdiction-specific system — case citations, statute references and law-report abbreviations differ by country and have no cross-system standard. Should legal citation be added to catalogue 06, kept as a separate per-jurisdiction catalogue, or refused entirely on the ground that a citation is `possible` here and never placement-bearing?

**`law.knowhow-precedents`**

> A precedent is often a de-identified copy of a real matter document, so a content-similarity signal will pull the two together and §2.9's duplicate/version-family logic may treat them as versions of one file. Does the product need an explicit rule that a know-how copy is never grouped with its source matter, and if so is that a grouping stop rule (§4.9 already lists stop rules) or a placement rule? Getting this wrong leaks a client document into a library that is shared across the practice.

**`law.investigation`**

> Investigation files are the strongest case in this slice for a protection posture stronger than the general legal safety domain — they record unproven allegations about identified people, and §8.4's classes are framed around the corpus owner's own sensitivity rather than third parties'. Whether P7's vocabulary needs a class for material that is sensitive about SOMEONE ELSE is a P7 question raised here and not answered here. It applies equally to law.family-law, law.criminal-defence and law.immigration-casework.

**`law.bar-admission-cle`**

> This entry is the practitioner's OWN record, not a client's, and slice 02 already publishes `career.professional-license`, `career.certification` and `career.continuing-education` covering the same material. Should it exist here at all? It is retained because the admitting-authority spine and the compliance-period structure are specific to regulated legal practice and 02's entries are profession-neutral, but this is the entry a reviewer is most entitled to delete. Joseph's call: keep as a legal-specific specialisation, or drop and let slice 02 own it.

**`law.pro-bono`**

> Is pro bono a DOMAIN or a FACET on law.matter-file? Its schema is law.matter-file's plus a funding basis, a funding authority and a referral source, which is the profile of a facet rather than a domain. It is written as a domain here because the funding paperwork is a genuinely distinct document set with its own authority and its own reporting, but a reviewer could reasonably collapse it. If it collapses, `funding_basis` becomes a field on law.matter-file and the funding documents become work types there. Joseph's call.
