# Domain catalogue — business operations, HR, strategy and management

Supercategory: `business-operations-hr`  
Slice: 11  
Entries: 45 — 1 design, 7 inference, 37 proposal  
Contract: [`_CONTRACT.md`](_CONTRACT.md) · Source of truth: [`00-database-agent-product-design.md`](../00-database-agent-product-design.md)

## How to read this file

- **Curly double quotes are verbatim quotations** from the source of truth and nothing else. Every one is checked by `check.py`, which normalises whitespace and requires the span to appear in the design; a quotation that does not appear fails the build. Where a claim is mine rather than the design's it is written as plain prose with no quote marks.
- **Single quotes are pattern literals** — tokens a recogniser looks for in a document — following the convention in the contract's own worked example.
- `reliability_ceiling` uses §3.13's six states only. `direct` means a labeled field, a document title or explicit metadata. `validated` means a rule found a pattern **and** passed a context check, so every `validated` field has a matching `recognition.deterministic` line that could actually confirm it. `llm_supported` means the value needs language interpretation and cannot be produced without the model route. `possible` means a useful but insufficient clue.
- `sensitivity` is §2.9's phrase and nothing more. **No handling class is assigned anywhere in this file**; handling classes are P7's (§8.4). Employee-relations, compensation and DEI material makes assigning one tempting, and the temptation is noted rather than acted on.
- No thresholds, no scores, no counts. Digits appear only inside `example` values, which are data in the same way the contract's own `BUSIB 4300` is.
- Cross-slice references name another catalogue's entry id where that file exists, and name the slice in prose where it does not yet.

## Three findings that apply to the whole slice

**1 — Business vocabulary is the most generic vocabulary in the corpus, and most of this slice's recognition therefore has to be refused rather than written.** Every domain in this catalogue contains projects, plans, reviews, reports, quarters, drafts and final versions. A rule keyed on any of those claims the whole corpus, and §3.3 says of rules that “They are the precision and safety layer” — so a slice that over-claims here does not merely misfile its own material, it destroys every other slice's precision. The consequences, stated plainly:

- **Words refused outright as anchors, with the slices they would claim:** `project` (§3.11 assigns it to *Research* files and to *Code* files; `pers.creative-project` and `soft.source-project` are named domains) · `review` (`res.peer-review-author`, `res.peer-review-referee`, `soft.code-review-artifact`, `hr.performance-cycle`, a book review, a literature review) · `report` and `status` and `update` (a lab report, an audit report, a credit report, a medical report, a bug report) · `plan` (a lesson plan, a treatment plan, `res.data-management-plan`, a floor plan, a meal plan) · `program`/`programme` (`acad.undergraduate-program` and `acad.graduate-program` are named domains) · `portfolio` (`acad.arts-jury-portfolio`, an investment portfolio, a designer's portfolio) · `case` (`law.matter-file`, a clinical case, a test case, a support case) · `interview` (a research interview, a job interview, a clinical interview, an exit interview) · `survey` (`res.survey-instrument`, a customer survey, a land survey) · `training` (model training, athletic training, `soft.training-material`) · `subject` (§3.11 assigns it to *Academic* files; the education slice has forty entries) · `certificate` (a birth certificate, a share certificate, a TLS certificate, a certificate of incorporation) · `policy` (`fin.insurance` and `pers.insurance`, a privacy policy, a school policy) · `onboarding` (employee, customer, vendor and product onboarding — four homes in one corpus) · `pipeline` (`soft.data-pipeline`, a sales pipeline, a recruiting pipeline) · `client` (a client library and client-side code in every developer's corpus) · `engagement` (a consulting engagement and an employee engagement survey — a homonym *inside this slice*) · `equity` (`corp.shareholder-captable`; home equity) · `turnover` (revenue in the finance slice, attrition here — a straight inversion) · `incident` (`soft.incident-postmortem`, a support case, a workplace injury) · `health` (the entire health slice).
- **Shapes refused as anchors.** §2.9 says presentations “should yield slide titles, text boxes, speaker notes where available, hyperlinks, embedded tables, and slide-level page boundaries” and spreadsheets “should yield workbook or file metadata, sheet names, column headers, visible cell values, table-like regions, formulas only when useful, and dates or identifiers from labeled cells”. A board deck, a strategy deck, a QBR deck, a training deck and a lecture deck are one format; a budget, a risk register, a headcount plan, a scorecard, a cap table and a pipeline report are one shape. Format is never a domain signal in this slice.
- **Tokens refused as anchors.** `Q1`–`Q4`, `H1`, `FY26`, `2026` — §3.10 warns that documents “frequently contain numbers that look like years but are course identifiers, version numbers, build numbers, ZIP codes, or other unrelated values”, and a fiscal or quarter token additionally collides with the education slice's academic-term patterns, which §3.10 says need dedicated patterns of their own. `draft`, `final`, `v2`, `FINAL FINAL` — §3.1 makes version family a *universal* file fact, so these carry no domain information at all. `confidential` — a sensitivity marking present on legal, finance, HR and vendor material alike.
- **Organisation names, refused as anchors everywhere.** §4.9 states the rule for universities and the reasoning transfers exactly: “A university name alone should not create a group because Columbia can appear as an authoring school, course provider, target institution, employer, research venue, or merely a cited organization” — and it names *employer* among the readings. A company name in a working corpus is an employer, a client, a supplier, a competitor, a partner, an investor, a letterhead on a received document and a cited example, and the non-subject readings are the majority.
- **Person names, refused as anchors and as folder levels.** §3.8 “It should avoid using authorship or creator identity as a destination dimension”, and §5.7 requires the engine to validate that a proposed template “does not repeat a parent dimension, create meaningless one-child levels, exceed practical depth limits, use an author or organization merely as a collector”. No template in this slice has a per-person level, which in the HR entries is a protection and not merely tidiness.
- **What is left.** The deterministic rules that survive are short and heavily corroborated, and they lean on four things: an explicit REFERENCE (a requisition, case, tender, contract, project or engagement code — §3.13 `direct`, and the only genuinely strong evidence in the slice); a DOCUMENT-CONTROL block; a distinctive multi-part STRUCTURE (present-and-apologies plus resolutions; objective plus key-result plus owner columns; what-went-well plus what-did-not); and a low-frequency phrase (`certificate of incorporation`, `right to work`, `permit to work`, `objectives and key results` written out in full). Everything else is in `needs_llm` or `never_alone`, and this slice's recall will be correspondingly low. That is the correct trade: §3.6 says “A model output that is useful but too weak to establish a fact may remain a possible clue for review; it must not quietly become a folder proposal or an asserted file property”.

**2 — The personal/professional boundary is unresolved and mostly undecidable from the document.** One person's Documents folder holds their employer's strategy deck, a client's brief and their own household budget. The pairs that are genuinely identical in shape: an operating budget and a household budget · a departmental minute and a residents'-association minute · an employer's onboarding pack and a new joiner's own copy of it · a compensation model and the user's own salary letter · a business trip's itinerary and a holiday's · an employer's training certificate and the learner's · a recruiting pipeline and a jobseeker's application tracker · a performance review written and one received. In every pair the discriminating fact is *whose role the user occupies*, which §3.8 makes expressible — “such as authored_by and target_school, or our_firm and client” — but does not make readable. This catalogue's answer is a `our_role` field on the branch root marked `llm_supported`, plus a requirement for an employer, client or reference anchor on the individual entries; that is a conservative default that will decline real work material rather than claim real personal material. The question is raised on `ops.business-records` and sharpened on `ops.operating-plan-budget`, `ops.meeting-record`, `ops.business-travel` and `hr.employee-relations`.

**3 — Four entries here are the same domain the career slice also authored, and three catalogues now model client engagements.** This is a merge problem, not a recognition one. `hr.job-requisition` / `career.employer-job-requisition`, `hr.recruiting-pipeline` / `career.employer-candidate-packet`, `hr.interview-panel` / `career.employer-interview-scorecard` and `hr.offer-package` / `career.employer-offer-approval` cover the same artifacts and key on the same requisition id; `ops.client-engagement`, `career.consulting-engagement` and `studio.client-engagement` all answer §5.7's single phrase 'client engagements'. §3.6's requirement “that each fact or label belongs to an allowed domain schema” cannot arbitrate a file whose facts belong to two allowed schemas — it passes validation in both and is placed twice. Each pair is written into `collides_with` so the duplication is visible rather than latent, and the decision is raised as an open question on `hr.job-requisition` and `ops.client-engagement`. Separately, roughly a third of the remaining entries have an exact MIRROR in the career slice — the offer issued and the offer received, the review written and the review received, the handbook published and the handbook signed — where the documents are byte-identical and only whose corpus they sit in differs. No `hr.personnel-file` entry exists here, because a per-employee folder is precisely what §3.8's “It should avoid using authorship or creator identity as a destination dimension” warns against; that omission is flagged as an open question on `hr.employee-relations` rather than resolved by silence.

## Index

| id | name | provenance | sensitivity | time first |
|---|---|---|---|---|
| `ops.business-records` | Organisational records (branch root) | proposal | none | no |
| `ops.strategy-plan` | Strategy and planning documents | proposal | none | no |
| `ops.board-governance` | Board and governance meeting materials | proposal | sensitive | no |
| `ops.okr-goals` | Goals, OKRs and scorecards | proposal | none | no |
| `ops.operating-plan-budget` | Operational budgeting and forecasting | proposal | none | no |
| `ops.business-case` | Business cases and investment proposals | proposal | none | no |
| `ops.meeting-record` | Meeting agendas, minutes and notes | proposal | sensitive | no |
| `ops.status-report` | Status and progress reporting | proposal | none | no |
| `ops.internal-comms` | Internal communications | proposal | sensitive | no |
| `ops.project` | Project delivery artifacts | inference | none | no |
| `ops.programme-portfolio` | Programme and portfolio management | proposal | none | no |
| `ops.retrospective-postmortem` | Retrospectives, post-mortems and lessons learned | proposal | none | no |
| `ops.risk-register` | Risk registers and risk management | proposal | none | no |
| `ops.business-continuity` | Business continuity and crisis planning | proposal | sensitive | no |
| `ops.policy-handbook` | Policies, handbooks and codes | proposal | none | no |
| `ops.process-documentation` | Process and procedure documentation | proposal | none | no |
| `ops.facilities-workplace` | Facilities and workplace management | proposal | none | no |
| `ops.business-travel` | Business travel administration | inference | sensitive | no |
| `ops.sourcing-rfp` | Sourcing events, tenders and bid evaluation | proposal | none | no |
| `ops.contract-administration` | Contract administration and obligation management | proposal | none | no |
| `ops.client-engagement` | Client engagements and professional-services delivery | design | sensitive | no |
| `ops.customer-success` | Customer success and account management | proposal | none | no |
| `ops.support-operations` | Customer support operations | proposal | sensitive | no |
| `ops.partnerships-bd` | Partnerships and business development | proposal | none | no |
| `ops.market-competitive-research` | Market and competitive research | proposal | none | no |
| `ops.pricing` | Pricing and commercial terms | proposal | none | no |
| `ops.product-roadmap` | Product roadmaps and release planning | proposal | none | no |
| `ops.product-requirements` | Product requirements and specifications | proposal | none | no |
| `ops.user-research` | User and customer research | inference | sensitive | no |
| `ops.go-to-market` | Go-to-market and launch planning | proposal | none | no |
| `hr.org-design-headcount` | Organisation design and headcount planning | proposal | sensitive | no |
| `hr.job-requisition` | Job requisitions and role definitions | inference | none | no |
| `hr.recruiting-pipeline` | Recruiting pipeline and candidate tracking (employer side) | inference | sensitive | no |
| `hr.interview-panel` | Interview panels, scorecards and hiring decisions | inference | sensitive | no |
| `hr.offer-package` | Offers and hiring approvals (employer side) | inference | sensitive | no |
| `hr.onboarding` | Onboarding programmes | proposal | sensitive | no |
| `hr.offboarding` | Offboarding, exits and terminations | proposal | sensitive | no |
| `hr.training-lnd` | Training and learning development | proposal | sensitive | no |
| `hr.performance-cycle` | Performance management cycles | proposal | sensitive | no |
| `hr.engagement-survey` | Employee engagement and listening surveys | proposal | sensitive | no |
| `hr.compensation-planning` | Compensation and benefits planning | proposal | sensitive | no |
| `hr.workforce-analytics` | Workforce analytics and people reporting | proposal | sensitive | no |
| `hr.dei-program` | Diversity, equity and inclusion programmes | proposal | sensitive | no |
| `hr.employee-relations` | Employee relations cases | proposal | sensitive | no |
| `hr.health-safety` | Workplace health and safety administration | proposal | sensitive | no |

## `ops.business-records` — Organisational records (branch root)

Material produced by or for an organisation that carries an organisation and a document type but no more specific operational sub-domain — the working-life branch itself.

**Provenance:** **proposal** — new here; the design names nothing like it

**Cite:** No design sentence names a business, work or operations branch. §5.1's list of typical initial top-level branches names Academics, Applications, Research, Career, Personal Records, Finance and Administration, Photos and Captures, Code and Projects and Media — Career is the only one that touches working life, and it is the person's side of it. §3.15 “Other domains remain placeholders until user demand and corpus evidence justify detailed templates” and §5.7 “expand the library as recurring user needs and corpus evidence justify additional coverage” are what permit this addition; the branch itself is new here. §5.1 also warns that “The exact labels should reflect the user’s vocabulary rather than a universal corporate taxonomy”, so the label is a placeholder, not a name to impose.

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `organisation` | string | Northwind Logistics | `validated` | the organisation the document belongs to. §3.8 “The system must separate roles that happen to contain the same entity type” — the same company name may be the user's employer, a client, a supplier or a merely cited firm, and this field means the first of those only |
| `our_role` | string | employer | `llm_supported` | which side of the relationship the user's copy sits on. §3.8's worked pair is “such as authored_by and target_school, or our_firm and client” — the role, not the name, is what makes the fact placeable, and reading it usually requires prose |
| `org_unit` | string | Operations | `validated` | department, team or function. Distinct from the organisation because a document is normally owned by a unit inside it; §3.12 “The system may create new values when it sees a new course, project, company, university, or event, but it should not invent new fields automatically”, so unit names are values |
| `document_type` | string | memo | `validated` | the work-type analogue for this branch, read from a document-control block or a title, never from the file format |
| `business_period` | string | FY2026 | `possible` | a fiscal label is not a date. §3.10 requires that “Date candidates should be identified with explicit regular expressions and then parsed without fuzzy matching”, and fiscal-year shapes vary by organisation, so this stays a clue unless a labeled period field carries it |
| `document_owner` | string | Head of Operations | `direct` | §3.13 direct: a labeled 'document owner' or 'approved by' field. §3.8 “It should avoid using authorship or creator identity as a destination dimension” — this is metadata and search only, never a folder level |
| `classification_label` | string | Internal | `direct` | §3.13 direct: the organisation's own marking, read from a labeled field or a header. §3.11 permits “several additional fields used only for search, privacy protection, explanation, or later review”; this is an explanation field. It is NOT a handling class — that is P7's (§8.4) and is not set here |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.3, §3.5):

- a document-control block — two or more of 'document owner' | 'version history' | 'approved by' | 'review date' | 'document reference' | 'supersedes' — co-occurring with an organisation name matched on a word boundary in a title or header position (§3.7's positional weighting)
- an organisation's own classification marking ('internal use only' | 'commercial in confidence' | 'restricted — internal') co-occurring with an organisation name AND a document-type term in the title

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- an untitled deck or memo whose organisation appears only in a logo region and whose function must be read from prose
- deciding our_role — whether the named company is the user's employer, their client, their supplier or a firm merely discussed — which is a reading of the document's stance, not a pattern
- a document that is plainly organisational but belongs to none of the specific sub-domains below, which is exactly the case this root exists to hold

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10, §4.9):

- an organisation name. §4.9 states the rule for universities and the reasoning transfers exactly: “A university name alone should not create a group because Columbia can appear as an authoring school, course provider, target institution, employer, research venue, or merely a cited organization” — a company appears as employer, client, supplier, competitor, partner, letterhead of a received document and cited example, and in a working person's corpus the non-subject readings are the majority
- 'confidential' — it appears in the footer of legal, finance, HR and vendor material alike, and is a sensitivity signal rather than a domain signal
- 'internal' | 'draft' | 'final' | 'v2' | 'FINAL' — §3.1 makes version family a universal file fact, not a domain fact, and these tokens carry no domain information at all
- a file format. §2.9 says presentations “should yield slide titles, text boxes, speaker notes where available, hyperlinks, embedded tables, and slide-level page boundaries” and spreadsheets “should yield workbook or file metadata, sheet names, column headers, visible cell values, table-like regions, formulas only when useful, and dates or identifiers from labeled cells” — a board deck, a strategy deck, a QBR deck and a lecture deck are one format and four domains
- a person's name — §3.8 “It should avoid using authorship or creator identity as a destination dimension”

### Work types

`memo`, `deck`, `one-pager`, `briefing note`, `register or tracker`, `internal template`, `working spreadsheet`

### Grouping reasons (§4)

- one organisation across the internal documents the user holds for it
- one document-control lineage across its versions and supersessions
- one function's working papers where no project, cycle or matter binds them more tightly

### Template (§5)

`organisation → function → document type`

Time first: **no**

§5.5: “a parent dimension should provide the context required to understand the child”. A function is only meaningful once the organisation is known. §5.5 also: “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders” — this branch is the record case, so no time level appears at all. §5.9 warns that a level should not be added when “It should warn when a level produces only one child, repeats a concept already expressed in the parent, creates excessive depth, or creates a large number of tiny folders”, and for a single-employer corpus the organisation level is exactly that; it should collapse.

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| career.employment-contract | the sharpest boundary in this whole slice. The same employer name sits on the user's contract (career) and on the operating plan they wrote at work (here). What separates them is whether the user is the SUBJECT of the document or one of its authors or administrators; nothing in the document's format says which | §3.8 “The system must separate roles that happen to contain the same entity type” — subject-of and author-of are the two roles that must be split here |
| pers.household-admin | a household is an organisation with a document type too. The separating signal is a registered entity name or an org-unit label; a household document has neither | §4.9 “A university name alone should not create a group because Columbia can appear as an authoring school, course provider, target institution, employer, research venue, or merely a cited organization” |
| fin.financial-records | the finance slice owns anything carrying an institution and a record type. This root claims only organisational material with no financial record type | §3.11 “One file may hold facts from more than one domain without losing information” |
| soft.design-doc-rfc | an engineering design doc has a document-control block and an organisation too. The separating signal is a technical artifact reference — a repository, service or interface name | §3.11 “Code files may use project, repository, programming language, and artifact type” |

### Sensitivity

`none` — Nothing §2.9 names as potentially sensitive attaches to an organisational document as such. The sub-domains that do carry it — employee relations, compensation, recruiting, support records — mark themselves, and §3.1's many-facts model keeps that a fact on the file rather than an inheritance down the branch. No handling class is assigned; that is P7's (§8.4).

### Open question — Joseph's call, unresolved

> TWO questions, both of which every entry in this slice inherits. FIRST — whose organisation is it? One person's Documents folder holds their employer's strategy deck, a client's brief, a supplier's quotation and their own household budget, and §3.8's our_firm/client discipline names the problem without deciding it. For most of this slice the discriminator is not in the document: an operating budget and a household budget are the same spreadsheet, and a performance review the user received and one they wrote are the same form. Does the product ask the user once for their own organisation and role — making it a user fact the way §4's user-approved folder is — or does it try to read the role per file and accept that it will often return unknown? SECOND — does §2.9's 'potentially sensitive' reach COMMERCIAL confidentiality, or only personal data? §8.4's corpus list is entirely personal: “identity documents, account statements, tax records, medical information, legal records, credentials, private correspondence, GPS metadata, employment materials, and educational records”. A pre-announcement board pack, an unsigned term sheet and a customer list are not personal data but are exactly the material a user would not want in a cloud prompt. This catalogue marks sensitivity on personal-data grounds only and leaves the commercial question to Joseph, because widening §2.9's phrase would silently widen P7's scope.

---

## `ops.strategy-plan` — Strategy and planning documents

Documents that set direction for an organisation or unit over a stated horizon — strategy papers, annual plans, and the analysis behind them.

**Provenance:** **proposal** — new here; the design names nothing like it

**Cite:** No design sentence names strategy. §5.7's list of what the template library should cover is “covering common organizational situations such as academic programs, university applications, recruiting processes, client engagements, research workflows, financial records, travel, legal matters, creative projects, software repositories, personal administration, and photo collections” — strategy is not in it. §3.15 “Other domains remain placeholders until user demand and corpus evidence justify detailed templates” permits the addition.

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `organisation` | string | Northwind Logistics | `validated` | the organisation whose direction is being set; §3.8's role discipline keeps it distinct from any competitor or partner named inside the same document |
| `org_unit` | string | EMEA Sales | `validated` | a strategy is usually a unit's, not a company's, and the unit is the level that distinguishes two otherwise identical plans |
| `planning_horizon` | string | FY2026-FY2028 | `possible` | the horizon is what makes a strategy document a strategy document rather than a status report, but it is stated in prose as often as in a labeled field, so it stays a clue |
| `plan_cycle` | string | FY2026 annual plan | `validated` | the recurring planning round the document belongs to. This is the grouping key, and it is only validated when a cycle label sits beside a planning term |
| `document_type` | string | strategy paper | `validated` | strategy paper, annual plan, operating plan, situation analysis, strategic option paper |
| `approval_status` | string | approved by the executive team | `llm_supported` | whether the plan is a proposal or the adopted one. Usually a sentence, not a field, and the difference matters more than any other fact here |
| `strategic_theme` | string | cost to serve | `llm_supported` | §3.11 permits “several additional fields used only for search, privacy protection, explanation, or later review”; themes are a search aid and must not become branches, because they are the model's paraphrase rather than a stated value |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.3, §3.5):

- a strategy-artifact term ('strategic plan' | 'strategy paper' | 'operating plan' | 'three-year plan' | 'strategic priorities') in a TITLE position (§3.7's positional weighting) co-occurring with an organisation or org-unit name matched on a word boundary AND a stated horizon or planning-cycle label
- a named strategy framework used as a section heading ('SWOT' | 'PESTLE' | 'Porter's five forces' | 'strategic options') co-occurring with an organisation name — the framework names are rare enough to carry weight, but only with the organisation beside them

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- a deck titled only with a year or a codename whose strategic character has to be read from its content
- separating a strategy paper from the business case that proposes one option inside it, which is a judgement about the document's scope
- approval status, which is almost always a sentence in a covering note

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10, §4.9):

- 'strategy' | 'plan' | 'planning'. 'Plan' is the single most over-subscribed word in a personal corpus: a lesson plan, a training plan, a data management plan (the research slice has a domain for it), a treatment plan, a business continuity plan, a floor plan, a meal plan and a project plan are all 'plans'. A rule keyed on it claims the corpus
- 'vision' | 'mission' | 'objectives' | 'priorities' | 'goals' — corporate boilerplate that also appears in a school prospectus, a grant application and a personal journal
- a fiscal-year token such as 'FY26' or 'FY2026'. §3.10 is explicit that documents “frequently contain numbers that look like years but are course identifiers, version numbers, build numbers, ZIP codes, or other unrelated values”, and a fiscal label is a year-shaped token with an organisation-specific meaning
- an organisation name — §4.9 “A university name alone should not create a group because Columbia can appear as an authoring school, course provider, target institution, employer, research venue, or merely a cited organization”
- a deck format. §2.9 says presentations “should yield slide titles, text boxes, speaker notes where available, hyperlinks, embedded tables, and slide-level page boundaries” and nothing in that shape distinguishes a strategy deck from a sales deck, a board deck or a lecture deck

### Work types

`strategic plan`, `annual or operating plan`, `situation or market analysis`, `strategic option paper`, `planning workshop output`, `strategy summary deck`, `cascade or communication pack`

### Grouping reasons (§4)

- one planning cycle across its analysis, drafts, decision papers and final plan
- one org unit's plan across the versions that led to the adopted one

### Template (§5)

`organisation → planning cycle → document type`

Time first: **no**

§5.5: “a parent dimension should provide the context required to understand the child”. A planning cycle label such as an annual plan is only meaningful once the organisation is known, and a document type is only meaningful once the cycle is. The cycle level is time-shaped but it is a named round rather than a calendar year, so §5.5's “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders” is respected rather than broken: nothing here is filed by capture date.

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| ops.business-case | a strategy paper sets direction; a business case argues for one investment. A strategy document that contains a costed option with a recommendation is both, and the option-appraisal structure is the only separating signal | §3.11 “One file may hold facts from more than one domain without losing information” |
| ops.okr-goals | goals appear inside strategy documents. What separates an OKR artifact is a scored, owner-attributed, period-bounded list; a strategy's goals are prose | §3.7 “It should rank candidate matches instead of accepting the first match” |
| ops.operating-plan-budget | an operating plan is a strategy document in narrative and a budget in its annexes; the distinguishing signal is a cost-centre-labelled numeric table, not the title | §3.11 “One file may hold facts from more than one domain without losing information” |
| gov.policy-development | a public body's strategy and a company's use one vocabulary. A public authority, a statutory duty or a consultation stage routes a file to the government slice | §3.8 “The system must separate roles that happen to contain the same entity type” |
| res.research-project | a research strategy or a lab's five-year plan uses identical vocabulary. The research slice's fields — “Research files may use project, stage, artifact type, lab, and venue” — are the discriminator, and a business strategy has none of them | §3.11 “Research files may use project, stage, artifact type, lab, and venue” |

### Sensitivity

`none` — Strategy material carries no category §2.9 names. It is very often commercially confidential, which is not the same thing — see the commercial-confidentiality question raised on `ops.business-records`. No handling class is assigned here; that is P7's (§8.4).

---

## `ops.board-governance` — Board and governance meeting materials

The recurring governance cycle of a board or committee — its notices, papers, packs, minutes and resolutions.

**Provenance:** **proposal** — new here; the design names nothing like it

**Cite:** No design sentence names board or governance material. §5.7's list “covering common organizational situations such as academic programs, university applications, recruiting processes, client engagements, research workflows, financial records, travel, legal matters, creative projects, software repositories, personal administration, and photo collections” does not include it. §3.15 “Other domains remain placeholders until user demand and corpus evidence justify detailed templates” permits the addition. Note that the finance slice's `corp.business-formation` already claims the CONSTITUTIONAL instruments — certificates, articles, statutory registers and the resolutions that constitute — and the law slice's `law.corporate-secretarial` claims the company-secretarial function; this entry is the recurring MEETING cycle only.

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `body` | string | Board of Directors | `validated` | the board or committee itself — audit committee, remuneration committee, trustee board. This is the grouping key and it is what distinguishes two identically shaped packs |
| `entity` | string | Northwind Logistics Ltd | `validated` | the entity the body governs; §3.8's role discipline keeps it distinct from any subsidiary or counterparty named in the papers |
| `meeting_date` | date | 2026-03-12 | `direct` | §3.13 direct: a labeled meeting-date field on a notice or minute. §3.10's explicit-regex path applies — “Date candidates should be identified with explicit regular expressions and then parsed without fuzzy matching” |
| `agenda_item_reference` | string | Item 7 | `direct` | §3.13 direct: a labeled item number on a board paper. It is what binds a paper to its minute and is the strongest structural link in this domain |
| `document_type` | string | board minute | `validated` | notice, agenda, board paper, pack, minute, resolution, action log |
| `decision_status` | string | approved | `llm_supported` | whether an item was approved, deferred, noted or rejected. It is the fact a user actually searches for and it lives in a sentence |
| `attendee_role` | string | non-executive director | `validated` | §2.9 says calendar formats “should yield event title, start and end time, location, organizer, attendees, and recurrence metadata”, and a minute carries a present/apologies block. §3.8 “It should avoid using authorship or creator identity as a destination dimension” — the ROLE is the useful fact; the person's name is metadata and never a folder level |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.3, §3.5):

- a governance-minute structure — a 'present' or 'apologies' block co-occurring with a 'resolved that' | 'it was agreed' | 'quorum' clause AND a named body
- a board-paper header block — an item-number label co-occurring with a named body AND a meeting date label
- a notice term ('notice of meeting' | 'notice of annual general meeting' | 'convened') co-occurring with a named body and an entity name matched on a word boundary

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- a paper written for a board that names neither the body nor the meeting, identifiable only from its audience and register
- decision status, which is a reading of the minute's language
- distinguishing a board pack's constituent paper from the same analysis circulated to the management team, where only the intended audience differs

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10, §4.9):

- 'board' — a whiteboard, a dashboard, an onboarding pack, a mood board, a surfboard photo and a kanban board all contain it, and §3.7 “It should use word-boundary matching rather than substring matching” does not save a token whose whole-word uses are themselves ambiguous
- 'minutes' — it is also a unit of time, and 'meeting minutes' exists for a PTA, a residents' association, a student society and a lab group; the education slice's `acad.student-organization` and the personal slice's `pers.membership` both hold minutes that look identical
- 'agenda' — see above, and it is also the ordinary English word
- 'resolution' — it is a screen resolution, an image resolution and a new year's resolution
- 'committee' | 'chair' | 'quorum' — quorum is the strongest of the three and still appears in club constitutions
- an entity name — §4.9 “A university name alone should not create a group because Columbia can appear as an authoring school, course provider, target institution, employer, research venue, or merely a cited organization”

### Work types

`notice of meeting`, `agenda`, `board paper`, `board pack`, `minute`, `written resolution`, `action log`, `committee report`, `conflicts declaration`

### Grouping reasons (§4)

- one meeting across its notice, agenda, papers, pack, minute and action log — §3.9's “The documents are content-incoherent but purpose-coherent” describes this exactly: a finance paper, a risk paper and an HR paper in one pack share no topic and one purpose
- one body across a governance year

### Template (§5)

`body → meeting date → document type`

Time first: **no**

§5.5: “a parent dimension should provide the context required to understand the child”. A paper is meaningless without its meeting and a meeting is meaningless without its body. This is one of the few entries in the slice where a date level is right and yet “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders” is still honoured — the date sits under the body, not above it, because a user looks for the March board meeting, never for March.

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| corp.business-formation | that entry already claims board minutes and written resolutions as constitutional records. The separating signal is whether the document constitutes something — an appointment, a share issue, an article change — or merely records a recurring meeting. A resolution appointing a director is theirs; a minute noting the monthly numbers is this one's. Deferred to on everything constitutional | §3.11 “One file may hold facts from more than one domain without losing information” |
| law.corporate-secretarial | the company-secretarial function produces the same notices and registers. That entry is the practitioner acting for an entity; this one is the entity's own governance cycle | §3.8 “The system must separate roles that happen to contain the same entity type” |
| ops.meeting-record | a board meeting is a meeting. The separating signal is a governance structure — a quorum or resolution clause, a constituted body, a formal notice. Without one it is a management meeting and belongs to the general entry | §3.7 “It should rank candidate matches instead of accepting the first match” |
| npo.governance | a charity board, a students' union and a residents' association produce structurally identical minutes, including the present block and the resolutions. What separates them is a registered entity and an officer structure — and a small charity or club has both, so the boundary genuinely fails there | §4.9 “A university name alone should not create a group because Columbia can appear as an authoring school, course provider, target institution, employer, research venue, or merely a cited organization” |

### Sensitivity

`potentially_sensitive` — Board and committee papers routinely carry remuneration decisions, individual appointments and employee-relations matters, and §8.4 names “identity documents, account statements, tax records, medical information, legal records, credentials, private correspondence, GPS metadata, employment materials, and educational records” among the material the local-first posture exists for. §2.9's phrase “treating addresses and message content as potentially sensitive” covers the circulation lists these packs are distributed on. The marking is made on personal-data grounds only; the separate commercial-confidentiality question is on `ops.business-records`. No handling class is assigned; that is P7's (§8.4).

---

## `ops.okr-goals` — Goals, OKRs and scorecards

The period-bounded, owner-attributed goal artifacts an organisation sets and scores against — objectives, key results, targets and scorecards.

**Provenance:** **proposal** — new here; the design names nothing like it

**Cite:** No design sentence names goal-setting. §3.15 “Other domains remain placeholders until user demand and corpus evidence justify detailed templates” permits the addition. It is kept separate from `ops.strategy-plan` because its artifact shape is genuinely different: a scored list with owners and a period, rather than a narrative.

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `goal_period` | string | Q3 FY2026 | `validated` | the cycle the goals are set for. This is the grouping key. It is only validated when a period label sits beside a goal-artifact term — the bare period token is refused below |
| `org_unit` | string | Customer Operations | `validated` | whose goals they are. Company, unit and individual goal sets have the same shape and different meanings, and the unit is what separates them |
| `goal_level` | string | team | `llm_supported` | company, unit, team or individual. Individual goal sets are the sensitive case and the level is usually only readable from context |
| `objective` | string | reduce time to first response | `llm_supported` | §3.11 permits “several additional fields used only for search, privacy protection, explanation, or later review” — objectives are a search aid and must never become folder levels, because they are free text that changes every cycle |
| `owner_role` | string | Head of Support | `direct` | §3.13 direct: a labeled owner column. §3.8 “It should avoid using authorship or creator identity as a destination dimension” — kept as metadata |
| `scoring_status` | string | end-of-cycle scored | `llm_supported` | whether a file is the set, the mid-cycle check or the final score. Three near-identical spreadsheets whose only difference is this |
| `goal_framework` | string | OKR | `validated` | OKR, balanced scorecard, MBO, V2MOM. The framework name is one of the few genuinely low-frequency tokens in this whole slice |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.3, §3.5):

- the expanded framework name ('objectives and key results' | 'balanced scorecard' | 'management by objectives') co-occurring with a period label and an owner or unit column — the expanded form is specific; the acronym alone is not
- a goal-table structure — an 'objective' column heading together with a 'key result' or 'target' column heading and an 'owner' column heading — co-occurring with a period label. §2.9 says spreadsheets “should yield workbook or file metadata, sheet names, column headers, visible cell values, table-like regions, formulas only when useful, and dates or identifiers from labeled cells”, and this is a case where the column headers genuinely carry the domain

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- a goal list written as prose in a deck with no table structure
- goal level — whether a set belongs to a company, a team or one person — which decides whether the file is sensitive and is rarely stated
- distinguishing a goal-setting artifact from the status report that reports against it

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10, §4.9):

- 'KPI' | 'metrics' | 'dashboard' | 'target' — these appear in every operational, financial, clinical, academic and athletic document in a corpus. 'KPI' in particular is a footer word
- 'OKR' as a bare acronym — §3.7 “It should use word-boundary matching rather than substring matching” helps, but the acronym also appears as a product name, a filename abbreviation and a transliteration; the expanded phrase is the safe form
- 'Q1' | 'Q2' | 'Q3' | 'Q4' | 'H1' | 'FY26'. A quarter token is a date-shaped token and §3.10 warns that documents “frequently contain numbers that look like years but are course identifiers, version numbers, build numbers, ZIP codes, or other unrelated values”. Worse, §3.10 also says academic terms require dedicated patterns, so a quarter token collides with the education slice's term patterns as well as with every fiscal document in the finance slice
- 'goals' | 'objectives' — a personal goals list, a treatment goal, a learning objective in a syllabus (the education slice) and a therapy goal (the health slice) all use them

### Work types

`goal set`, `OKR sheet`, `scorecard`, `target register`, `mid-cycle check-in`, `end-of-cycle scoring`, `cascade map`

### Grouping reasons (§4)

- one goal cycle across the set, its check-ins and its final scoring
- one org unit across consecutive goal cycles

### Template (§5)

`org unit → goal period → document type`

Time first: **no**

§5.5: “a parent dimension should provide the context required to understand the child”. A period is only meaningful once you know whose goals they are — every unit has a Q3. §5.5's “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders” puts the unit above the period rather than the reverse.

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| hr.performance-cycle | an individual goal set IS a performance-management artifact, and the two systems usually share one form. The separating signal is a named individual as the goal owner rather than a unit; where that is present the HR entry's sensitivity applies and this one should not claim the file | §3.11 “One file may hold facts from more than one domain without losing information” |
| ops.status-report | a mid-cycle check-in is a status report scored against goals. The separating signal is whether the artifact carries the goal definitions or only reports movement | §3.7 “It should rank candidate matches instead of accepting the first match” |
| ops.strategy-plan | strategy documents contain goals; goal artifacts do not contain strategy. The scored, owner-attributed table is the discriminator | §3.11 “One file may hold facts from more than one domain without losing information” |
| acad.advising | a student learning-goals form and an individual OKR sheet have the same shape. The organisation and unit fields are the only separation, and a self-employed user has neither | §4.9 “A university name alone should not create a group because Columbia can appear as an authoring school, course provider, target institution, employer, research venue, or merely a cited organization” |

### Sensitivity

`none` — A unit or company goal set carries nothing §2.9 names. An INDIVIDUAL goal set does — it is a performance record, and §8.4 names “identity documents, account statements, tax records, medical information, legal records, credentials, private correspondence, GPS metadata, employment materials, and educational records” — but that file belongs to `hr.performance-cycle`, which marks it. §3.1's many-facts model keeps the marking on the file rather than on the branch. No handling class is assigned; that is P7's (§8.4).

### Open question — Joseph's call, unresolved

> Whether an individual's goal sheet is an operations artifact or an HR record is not a property of the document — the same template is used for both, and organisations differ on whether goal attainment feeds pay. This catalogue routes it to `hr.performance-cycle` whenever a named individual is the owner, which is a conservative default rather than a decision. Joseph decides whether that default is right, because it determines whether the file is treated as sensitive.

---

## `ops.operating-plan-budget` — Operational budgeting and forecasting

The forward-looking money plan of a unit or organisation — budgets, forecasts, reforecasts and variance reporting — as a management artifact rather than an accounting record.

**Provenance:** **proposal** — new here; the design names nothing like it

**Cite:** No design sentence names operational budgeting. §3.11 gives Finance the fields institution, account type, tax year and record type — none of which a budget has, which is itself the argument for a separate entry. §3.15 “Other domains remain placeholders until user demand and corpus evidence justify detailed templates” permits it. The finance slice's `biz.bookkeeping` owns the ledger and the actuals; this entry is the PLAN.

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `organisation` | string | Northwind Logistics | `validated` | whose budget it is; §3.8's role discipline keeps it distinct from any supplier or customer named in the lines |
| `cost_centre` | string | OPS-4200 | `direct` | §3.13 direct: a labeled cost-centre or department code. This is the one field that reliably separates an organisational budget from a household one, and it is the reason it is listed |
| `budget_period` | string | FY2026 | `validated` | the fiscal period planned for. Only validated when a period label sits beside a budgeting term; the bare fiscal token is refused below |
| `plan_version` | string | reforecast 2 | `validated` | budget, forecast, reforecast, latest estimate. Several near-identical files differ only by this, and it is normally stated in the title or a labeled cell |
| `currency` | string | EUR | `direct` | §3.13 direct: a labeled currency field or column header. §3.11 permits “several additional fields used only for search, privacy protection, explanation, or later review”; a search and explanation field, not a folder dimension |
| `approval_status` | string | submitted for approval | `llm_supported` | whether a version is a working draft or the approved plan — a sentence in a covering note more often than a field |
| `planning_assumption` | string | headcount held flat | `llm_supported` | §3.11 permits “several additional fields used only for search, privacy protection, explanation, or later review”; assumptions are what a user actually searches a superseded budget for, and they are prose |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.3, §3.5):

- a cost-centre or department code label co-occurring with a budgeting term ('budget' | 'forecast' | 'reforecast' | 'variance to budget' | 'phasing') AND a fiscal-period label — the cost-centre label is doing the real work here
- a variance-table structure — 'budget' and 'actual' and 'variance' as sibling column headings — co-occurring with an org-unit name matched on a word boundary

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- a budget workbook whose only organisational marker is the unit named on a tab
- approval status and plan version where the file name says only a date
- distinguishing a management budget from the accounting close it is compared against, when both live in one workbook

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10, §4.9):

- 'budget'. This is the clearest personal/professional collision in the slice: a household budget, a wedding budget, a project budget, a grant budget (the research slice), a film budget (the creative slice) and a departmental operating budget are one word and six domains. The cost-centre label is the corroboration that makes the rule safe, and without it there is no rule
- a currency amount — the finance slice calls this the single most over-firing pattern in its own material and the same is true here
- 'forecast' — a weather forecast, a sales forecast, a demand forecast and a cash-flow forecast
- a fiscal-year token — §3.10 “frequently contain numbers that look like years but are course identifiers, version numbers, build numbers, ZIP codes, or other unrelated values”
- a spreadsheet with numeric columns. §2.9 says spreadsheets “should yield workbook or file metadata, sheet names, column headers, visible cell values, table-like regions, formulas only when useful, and dates or identifiers from labeled cells”; the shape is shared with every register, tracker and model in the corpus

### Work types

`budget submission`, `approved budget`, `forecast or reforecast`, `variance report`, `budget assumption note`, `cost-centre allocation`, `capital request schedule`

### Grouping reasons (§4)

- one budget period across its submissions, revisions and approved version
- one cost centre across a planning year

### Template (§5)

`organisation → budget period → cost centre`

Time first: **no**

§5.5: “a parent dimension should provide the context required to understand the child”. A cost centre is meaningless outside its organisation and a budget line is meaningless outside its period. This entry is one of the few where the period must sit above the unit rather than below it, because budget files are consulted period-first — the exception is stated rather than assumed, since §5.5's default is “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders”.

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| biz.bookkeeping | a variance report holds the plan and the actuals in one file. The finance slice owns the actuals, the ledger and anything with an account. This entry claims the plan only, and defers on any file whose primary content is a posted transaction | §3.11 “One file may hold facts from more than one domain without losing information” |
| pers.everyday-finance | a household budget spreadsheet and a departmental one are the same artifact. Only the cost-centre or org-unit label separates them, and a freelancer's business budget has neither — see the open question | §3.8 “The system must separate roles that happen to contain the same entity type” |
| res.grant-proposal | a grant budget is a budget with a funder and an award reference. Those two fields are the discriminator and this entry should never claim a file carrying them | §3.11 “Research files may use project, stage, artifact type, lab, and venue” |
| ops.business-case | a business case contains a costed budget as an annex; the case is the argument, the budget is the plan. Where the file is only the annex it belongs here | §3.11 “One file may hold facts from more than one domain without losing information” |

### Sensitivity

`none` — A departmental budget carries no category §2.9 names. A budget at individual-salary granularity does, and that file is `hr.compensation-planning`, which marks it. No handling class is assigned; that is P7's (§8.4).

### Open question — Joseph's call, unresolved

> A sole trader's, freelancer's or founder's budget is simultaneously a household budget and a business one, and no field in the document separates them — the finance slice raises the same problem for bank accounts and reaches the same wall. Whether the product asks the user to declare a business entity once, or accepts that this material is genuinely dual-homed under §4.9's “A file may validly belong to more than one accepted group”, is Joseph's call and it decides whether an operations branch and a personal branch both surface the same file.

---

## `ops.business-case` — Business cases and investment proposals

A costed argument for doing one thing rather than another, put to a decision-maker — options, appraisal, recommendation and the decision on it.

**Provenance:** **proposal** — new here; the design names nothing like it

**Cite:** No design sentence names business cases. §3.15 “Other domains remain placeholders until user demand and corpus evidence justify detailed templates” permits the addition. It is kept separate from strategy and from budgeting because its distinguishing structure — an options appraisal ending in a recommendation — is genuinely recognisable where 'plan' and 'budget' are not.

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `proposal_subject` | string | warehouse management system replacement | `llm_supported` | what is being proposed. Free text and therefore never a folder level, but it is the fact a user searches on |
| `organisation` | string | Northwind Logistics | `validated` | the organisation the case is put to; §3.8's role discipline keeps it distinct from any vendor named among the options |
| `requesting_unit` | string | Distribution | `validated` | who is asking. Two cases for the same investment from different units are different documents |
| `decision_forum` | string | investment committee | `validated` | the body the case goes to. This is what binds a case to a governance meeting and it is normally stated on the cover |
| `case_stage` | string | full business case | `validated` | outline, full, post-implementation review. The staged vocabulary is specific enough to validate when it sits beside an appraisal structure |
| `decision_outcome` | string | approved with conditions | `llm_supported` | whether it was approved, deferred or rejected — almost always a sentence in a minute or a covering note rather than a field on the case itself |
| `appraisal_horizon` | string | five-year | `possible` | §3.11 permits “several additional fields used only for search, privacy protection, explanation, or later review”; a clue that helps explain the file, stated in prose more often than labeled |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.3, §3.5):

- an options-appraisal structure — an 'options considered' | 'do nothing' | 'preferred option' | 'option appraisal' heading co-occurring with a 'recommendation' heading — together with an organisation or decision-forum name. The do-nothing option is close to a signature of this document type
- a staged-case term ('outline business case' | 'full business case' | 'strategic outline case') in a title position co-occurring with an organisation name matched on a word boundary
- a benefits-and-costs structure — a 'benefits realisation' | 'costs and benefits' | 'net benefit' heading co-occurring with a decision-forum or approver label

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- a proposal deck that argues a case without using any of the staged vocabulary
- the decision outcome, which lives in a different document — the minute — and has to be connected across files
- separating a business case from a vendor's proposal arguing the same thing from the other side

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10, §4.9):

- 'proposal'. A grant proposal (research slice), a thesis proposal (education slice), a sales proposal, a marriage proposal and a business case are one word. This is a domain-claiming word and is refused
- 'options' | 'recommendation' | 'justification' — ordinary English
- 'ROI' | 'payback' | 'NPV' — finance vocabulary that appears in investment material, valuation models and coursework alike; the education slice's finance courses are full of it
- 'case' — a legal case (the law slice), a use case, a case study, a test case, a clinical case (the health slice) and a support case (this slice's own `ops.support-operations`). Catastrophic on its own
- an organisation name — §4.9 “A university name alone should not create a group because Columbia can appear as an authoring school, course provider, target institution, employer, research venue, or merely a cited organization”

### Work types

`outline business case`, `full business case`, `options appraisal`, `cost-benefit model`, `approval paper`, `post-implementation review`, `decision record`

### Grouping reasons (§4)

- one proposal across its outline, full case, supporting model and decision
- one decision forum across the cases put to it in a cycle

### Template (§5)

`organisation → proposal → case stage`

Time first: **no**

§5.5: “a parent dimension should provide the context required to understand the child”. A stage label such as 'full' is meaningless without knowing which proposal it is a stage of. §5.5's “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders” keeps any year out of the upper levels, because a case's documents span the decision period and splitting them by calendar year would break the one grouping that matters.

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| ops.board-governance | an approved case is an agenda item, and its approval paper sits inside a board pack. The pack belongs to the governance entry and the case belongs here; §4.9 “A file may validly belong to more than one accepted group” means both claims can stand | §4.9 “A file may validly belong to more than one accepted group” |
| ops.sourcing-rfp | a case that recommends a supplier and a bid evaluation that selects one contain the same analysis. The separating signal is a tender reference and bidder responses, which a business case does not have | §3.7 “It should rank candidate matches instead of accepting the first match” |
| corp.fundraising-investor | an investment case put to an investment committee and a pitch put to investors argue the same way. The finance slice's round label, term sheet and investor fields are the discriminator | §3.8 “The system must separate roles that happen to contain the same entity type” |
| ops.project | an approved case becomes a project charter, often by renaming the file. The charter carries a project identifier and a delivery schedule; the case does not | §3.11 “One file may hold facts from more than one domain without losing information” |

### Sensitivity

`none` — Nothing §2.9 names attaches to an investment argument. A case whose subject is a redundancy programme does carry employment material, and that file also belongs to `hr.org-design-headcount`, which marks it. No handling class is assigned; that is P7's (§8.4).

---

## `ops.meeting-record` — Meeting agendas, minutes and notes

The record of a working meeting — its agenda, the notes taken in it, the decisions reached and the actions assigned.

**Provenance:** **proposal** — new here; the design names nothing like it

**Cite:** No design sentence names meetings as a domain. §2.9 does name the EVIDENCE this domain runs on: calendar formats “should yield event title, start and end time, location, organizer, attendees, and recurrence metadata”, and email formats “should yield sender, recipients, subject, sent date, thread identifiers, message body, attachment names, and reply-chain context”. §3.15 “Other domains remain placeholders until user demand and corpus evidence justify detailed templates” permits the domain itself. Governance meetings are `ops.board-governance`; this entry is every other meeting.

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `meeting_series` | string | Operations weekly | `validated` | the recurring series a meeting belongs to. §2.9 says calendar formats yield recurrence metadata, which is what makes a series a real fact rather than a guess. The series, not the individual meeting, is the durable grouping key |
| `meeting_date` | date | 2026-03-12 | `direct` | §3.13 direct: a calendar start time or a labeled date on a minute. §3.10's explicit-regex path applies — “Date candidates should be identified with explicit regular expressions and then parsed without fuzzy matching” |
| `organiser_role` | string | chair | `direct` | §3.13 direct: §2.9 names organizer among the fields a calendar file yields. §3.8 “It should avoid using authorship or creator identity as a destination dimension” — kept as metadata, never a folder level |
| `attendee_role` | string | supplier representative | `llm_supported` | the ROLE is what makes an attendee list informative — an external supplier in the room changes what the meeting is. §2.9 yields attendees as names; the role behind a name needs interpretation |
| `decision` | string | phase two deferred to the next quarter | `llm_supported` | the fact a user searches minutes for. It is a sentence and it can only be extracted by reading; §3.6 requires the model to cite the exact span |
| `action_owner_role` | string | operations manager | `llm_supported` | who owes what. §3.8 “It should avoid using authorship or creator identity as a destination dimension” keeps this metadata |
| `meeting_subject` | string | depot consolidation | `llm_supported` | §3.11 permits “several additional fields used only for search, privacy protection, explanation, or later review”; a search field. It must not become a branch, because a recurring series covers a different subject every week |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.3, §3.5):

- a minute structure — an 'attendees' or 'present' block co-occurring with an 'actions' | 'action items' | 'decisions' block AND a date label. All three together are what make it a meeting record; any one of them alone is not
- an ICS calendar file, which §2.9 says yields event title, start and end time, organizer and attendees as structured metadata — this is the only case in the domain where the format itself is the evidence
- an agenda structure — a numbered item list co-occurring with a time-allocation column or a per-item owner column AND a named series or date label

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- raw notes typed during a meeting, with no headings, no attendee block and a filename that is only a date
- deciding whether a set of notes records a meeting at all, or is a person thinking alone
- every decision and action, which are sentences
- the meeting series, where a recurring meeting is named differently in every file

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10, §4.9):

- 'meeting' | 'agenda' | 'minutes' | 'notes' | 'sync' | 'standup' | 'catch-up' | '1:1'. This is the widest-firing vocabulary in the slice. A parent-teacher meeting, a lab meeting (research slice), a class session (education slice), a doctor's appointment note (health slice), a residents' association AGM (personal slice), a client call (law slice) and a team standup are one vocabulary and seven domains. 'Notes' alone would claim a large fraction of any real corpus
- a date in a filename. §3.10 “frequently contain numbers that look like years but are course identifiers, version numbers, build numbers, ZIP codes, or other unrelated values” — and even a correctly parsed date says nothing about domain
- an attendee list of personal names — §3.8 “It should avoid using authorship or creator identity as a destination dimension”, and §4.9 warns against grouping “when one high-frequency entity acts as the only bridge”, which a frequent attendee is by definition
- a calendar file on its own. §2.9's ICS fields are reliable metadata but a calendar holds birthdays, flights, medical appointments and school terms alongside work meetings
- 'action items' | 'next steps' | 'follow-up' — these appear at the bottom of every document in every domain

### Work types

`agenda`, `minute`, `raw notes`, `action log`, `pre-read pack`, `decision record`, `calendar invitation`

### Grouping reasons (§4)

- one meeting across its invitation, pre-read, agenda, notes, minute and action log — §3.9's “The documents are content-incoherent but purpose-coherent” is the exact reason a heterogeneous set belongs together here
- one recurring series across a period

### Template (§5)

`organisation → meeting series → meeting date`

Time first: **no**

§5.5: “a parent dimension should provide the context required to understand the child”. A date is meaningless without the series and a series is meaningless without the organisation. This is one of the two entries in the slice where a date is a legitimate leaf, because a meeting genuinely IS its date — but §5.9's warning against a level that “It should warn when a level produces only one child, repeats a concept already expressed in the parent, creates excessive depth, or creates a large number of tiny folders” applies hard: a monthly series produces a folder per meeting, most holding one file, and the date level should usually be dropped.

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| ops.board-governance | a board meeting is a meeting with a quorum. The governance entry takes anything with a constituted body, a formal notice or a resolution clause; this one takes the rest | §3.7 “It should rank candidate matches instead of accepting the first match” |
| npo.residents-association | society, club, PTA and residents'-association minutes are structurally identical to work minutes, down to the present block. The only separator is an employer or client organisation, and for a volunteer committee there is none | §4.9 “A university name alone should not create a group because Columbia can appear as an authoring school, course provider, target institution, employer, research venue, or merely a cited organization” |
| ops.client-engagement | a client meeting note is both a meeting record and an engagement record. The engagement reference is the separating signal and, where present, the engagement should lead | §4.9 “A file may validly belong to more than one accepted group” |
| med.clinician-case-conference | a case conference has attendees, decisions and actions in the same shape. A patient identifier is the discriminator and this entry must never claim a file carrying one | §3.11 “One file may hold facts from more than one domain without losing information” |

### Sensitivity

`potentially_sensitive` — §2.9's phrase applies through the evidence this domain runs on: email formats are to be handled “treating addresses and message content as potentially sensitive”, and a meeting record normally carries a circulation list, an attendee list and, in HR or client meetings, material about named individuals. The marking is conservative and made on personal-data grounds. No handling class is assigned; that is P7's (§8.4).

### Open question — Joseph's call, unresolved

> Meeting records are the clearest case in the slice where the personal and professional shapes are identical: a residents' association AGM minute, a school governor's minute and a departmental minute differ in no readable respect. This entry assumes an employer or client organisation is required and therefore silently declines volunteer and community meetings, pushing them to the personal slice. Joseph decides whether that is right, or whether one meeting domain should span both — which would make the meeting series, not the organisation, the top folder level.

---

## `ops.status-report` — Status and progress reporting

The recurring account a unit, project or supplier gives of where things stand — the report itself, not the work it reports on.

**Provenance:** **proposal** — new here; the design names nothing like it

**Cite:** No design sentence names status reporting. §3.15 “Other domains remain placeholders until user demand and corpus evidence justify detailed templates” permits the addition. It exists as its own entry because a status report about a project is not a project artifact: it has a cadence, a reporting line and a period, and it accumulates faster than anything else in a working corpus.

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `reporting_object` | string | Depot consolidation programme | `validated` | what is being reported on — a project, a unit, a service, a contract. Without this the report has no anchor at all, which is why it leads the template |
| `reporting_period` | string | week ending 2026-03-13 | `validated` | the period covered. Only validated when a period label sits beside a reporting-cadence term |
| `cadence` | string | weekly | `validated` | weekly, monthly, quarterly. The cadence is what makes a series of near-identical files a series |
| `reporting_line` | string | to the programme board | `llm_supported` | who the report goes to. The same facts reported upward and outward are different documents and the audience is normally a sentence |
| `overall_state` | string | amber | `validated` | the summary state a status report exists to carry. A RAG-style label in a labeled cell is one of the few genuinely structured facts in this domain |
| `author_unit` | string | Programme office | `validated` | §3.8 “It should avoid using authorship or creator identity as a destination dimension” — the unit is recorded as metadata, and specifically must not become a collector folder — §5.7 requires the engine to validate that a proposed template “does not repeat a parent dimension, create meaningless one-child levels, exceed practical depth limits, use an author or organization merely as a collector” |
| `escalation` | string | supplier resource shortfall | `llm_supported` | §3.11 permits “several additional fields used only for search, privacy protection, explanation, or later review”; the fact that makes an old status report worth keeping, and it is prose |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.3, §3.5):

- a RAG or status-label structure — a 'RAG status' | 'overall status' | 'health' label with a red/amber/green value — co-occurring with a named reporting object AND a period label
- a report-header block carrying all three of a cadence term ('weekly report' | 'monthly report' | 'period report'), a named reporting object, and a 'period covered' or 'week ending' label
- a progress-table structure — 'planned' and 'actual' and 'next period' as sibling headings — co-occurring with a named reporting object

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- a narrative update email or memo with no headings and no status label
- the reporting line, which is a reading of the audience
- separating a status report from the minute of the meeting that received it, when the minute reproduces the report

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10, §4.9):

- 'report' | 'update' | 'status' | 'progress' | 'weekly' | 'monthly' | 'summary'. There is no corroboration cheap enough to make 'report' safe: a lab report (education slice), a research report, an audit report (finance slice), a credit report, a medical report, a police report, an incident report and a bug report all sit in a normal corpus. This entry deliberately keys on the STATUS LABEL and the named reporting object instead, and accepts lower recall as the price
- 'RAG' | 'red' | 'amber' | 'green' as bare tokens — colour words, and 'RAG' is also a word
- a date range in a filename — §3.10 “frequently contain numbers that look like years but are course identifiers, version numbers, build numbers, ZIP codes, or other unrelated values”
- an organisation name — §4.9 “A university name alone should not create a group because Columbia can appear as an authoring school, course provider, target institution, employer, research venue, or merely a cited organization”
- a recurring filename pattern such as a dated stem. §3.1 makes duplicate and version family a universal file fact; a dated series says a file recurs, not what domain it is in

### Work types

`status report`, `highlight report`, `progress update`, `dashboard export`, `exception report`, `executive summary`

### Grouping reasons (§4)

- one reporting object across a reporting series
- one reporting period across the several reports produced for it

### Template (§5)

`reporting object → cadence → period`

Time first: **no**

§5.5: “a parent dimension should provide the context required to understand the child”. A period folder is meaningless without knowing what is being reported on. §5.5's “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders” is exactly why the reporting object leads — filing status reports by month scatters one project's history across the calendar, which is the failure the sentence describes. §5.9's warning about a level that “It should warn when a level produces only one child, repeats a concept already expressed in the parent, creates excessive depth, or creates a large number of tiny folders” means the cadence level should collapse where only one cadence exists.

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| ops.project | a highlight report is a project artifact by origin and a reporting artifact by function. The separating signal is whether the file defines the work (charter, plan, schedule) or narrates it | §3.11 “One file may hold facts from more than one domain without losing information” |
| ops.okr-goals | a mid-cycle OKR check-in is a status report against goals. Where the file carries the goal definitions it is the goal entry's; where it only carries movement it is this one's | §3.7 “It should rank candidate matches instead of accepting the first match” |
| ops.customer-success | a QBR deck is a status report given outward to a customer. The account reference and the external audience are the separating signals | §3.8 “The system must separate roles that happen to contain the same entity type” |
| res.grant-reporting | a grant progress report has the same cadence shape. The funder and award reference are the discriminator, and this entry must not claim a file carrying them | §3.11 “Research files may use project, stage, artifact type, lab, and venue” |

### Sensitivity

`none` — A status report carries no category §2.9 names. Where one names individuals in a resourcing or performance context the employment-material reading applies and the file also belongs to an HR entry, which marks it. No handling class is assigned; that is P7's (§8.4).

---

## `ops.internal-comms` — Internal communications

Material produced to tell an organisation's own people something — announcements, all-hands material, newsletters and intranet copy.

**Provenance:** **proposal** — new here; the design names nothing like it

**Cite:** No design sentence names internal communications. §2.9 names the evidence: email formats “should yield sender, recipients, subject, sent date, thread identifiers, message body, attachment names, and reply-chain context”. §3.15 “Other domains remain placeholders until user demand and corpus evidence justify detailed templates” permits the domain.

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `organisation` | string | Northwind Logistics | `validated` | the organisation communicating; §3.8's role discipline separates it from any company named inside the announcement |
| `audience` | string | all employees | `llm_supported` | who it was sent to. This is the defining fact of the domain — the same text sent to staff, to customers and to the press is three different documents — and it is stated in prose |
| `communication_type` | string | announcement | `validated` | announcement, newsletter, all-hands deck, intranet article, FAQ, talking points |
| `announcement_subject` | string | office relocation | `llm_supported` | §3.11 permits “several additional fields used only for search, privacy protection, explanation, or later review”; a search field only. It changes with every message and must never become a branch |
| `send_date` | date | 2026-03-02 | `direct` | §3.13 direct: §2.9 names sent date among the fields an email format yields |
| `sender_role` | string | chief operating officer | `llm_supported` | the role behind the sender. §3.8 “It should avoid using authorship or creator identity as a destination dimension” — metadata only, and §2.9 requires the address itself be handled as sensitive |
| `campaign` | string | relocation communications | `possible` | several messages about one thing form a campaign, but the link is usually an inference from subject and timing rather than a stated fact — §3.13 possible is the honest ceiling |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.3, §3.5):

- an all-staff address pattern in a salutation ('Dear colleagues' | 'Dear all' | 'Hi everyone' | 'Team,') co-occurring with an organisation name matched on a word boundary AND a sender-role signature block
- an internal-communication artifact term ('all-hands' | 'town hall' | 'staff briefing' | 'internal announcement' | 'talking points') co-occurring with an organisation name
- a newsletter structure — an issue label together with a masthead carrying an organisation name

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- an untitled message whose internal audience must be read from register and content
- audience, which is the domain's defining fact and is almost never a field
- separating an internal announcement from the external press release that says the same thing in different words

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10, §4.9):

- 'announcement' | 'update' | 'newsletter' | 'bulletin' | 'FAQ'. A school newsletter (education slice), a club newsletter (personal slice), a product release note (software slice) and a residents' bulletin all match
- an email file. §2.9 gives email a rich evidence shape, but a mailbox holds personal correspondence, receipts, medical letters and school notices in the same format — and §2.9 requires those be handled “treating addresses and message content as potentially sensitive”
- 'team' | 'everyone' | 'colleagues' as bare tokens
- an organisation name — §4.9 “A university name alone should not create a group because Columbia can appear as an authoring school, course provider, target institution, employer, research venue, or merely a cited organization”
- 'confidential — internal' — a classification marking, not a domain marking

### Work types

`announcement`, `all-hands deck`, `newsletter issue`, `intranet article`, `FAQ or Q&A`, `talking points`, `change-communication pack`

### Grouping reasons (§4)

- one announcement across its draft, final, deck, FAQ and follow-up
- one campaign across the messages that make it up

### Template (§5)

`organisation → communication type → year`

Time first: **no**

§5.5: “a parent dimension should provide the context required to understand the child”. A communication type is meaningful only once the organisation is known. This is one of the few entries where a year is a reasonable leaf, because internal comms have no other durable grouping — a campaign is usually short-lived and §5.9 would flag a per-campaign level as one that “It should warn when a level produces only one child, repeats a concept already expressed in the parent, creates excessive depth, or creates a large number of tiny folders”.

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| pers.correspondence | the personal slice owns the user's own mail. An all-staff announcement arriving in a personal mailbox is both; the salutation and the sender role are what separate a broadcast from a letter | §3.8 “The system must separate roles that happen to contain the same entity type” |
| ops.policy-handbook | a policy change is announced and then published. The announcement is here; the policy document with its effective date and version control is there | §3.7 “It should rank candidate matches instead of accepting the first match” |
| media.ad-campaign | an internal campaign uses the same design assets as an external one. The audience is the only separator and the asset files themselves do not carry it | §3.9 “The documents are content-incoherent but purpose-coherent” |
| hr.onboarding | welcome and induction communications are internal comms produced by the HR programme; where an employment-lifecycle term is present the HR entry should lead | §3.11 “One file may hold facts from more than one domain without losing information” |

### Sensitivity

`potentially_sensitive` — §2.9 requires that email formats be handled “treating addresses and message content as potentially sensitive”, and this domain's primary artifact is a message with a distribution list. Announcements about restructures and departures are also employment material, which §8.4 names among “identity documents, account statements, tax records, medical information, legal records, credentials, private correspondence, GPS metadata, employment materials, and educational records”. The marking is conservative. No handling class is assigned; that is P7's (§8.4).

---

## `ops.project` — Project delivery artifacts

The documents that define, schedule and control one bounded piece of work — charter, plan, schedule, RAID log and closure.

**Provenance:** **inference** — extends a domain the design does name

**Cite:** The design names `project` as a fact field, but only for other domains: §3.11 says “Research files may use project, stage, artifact type, lab, and venue” and “Code files may use project, repository, programming language, and artifact type”. §4.5 names “one course, project, application, recruiting process, photo event, or submission packet”, which makes a project a legitimate organizing reason. §5.5 says “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders”, naming project as a leading dimension for record domains. Extending that named field and organizing reason to business project delivery is the inference; no design sentence names a business project domain.

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `project` | string | Depot consolidation | `validated` | the project itself. §3.12 “The system may create new values when it sees a new course, project, company, university, or event, but it should not invent new fields automatically” — project names are values, discovered from files. This field is deliberately the same NAME as the research and code slices' field and a different domain's instance of it, which is the collision this entry has to manage |
| `project_identifier` | string | PRJ-2026-014 | `direct` | §3.13 direct: a labeled project code. Where an organisation uses one this is by far the strongest fact in the domain and the only reliable way to separate two projects with similar names |
| `phase` | string | delivery | `validated` | initiation, planning, delivery, closure. The staged vocabulary is what makes a plan file placeable |
| `project_role` | string | project manager | `direct` | §3.13 direct: a labeled role in a document-control block. §3.8 “It should avoid using authorship or creator identity as a destination dimension” |
| `milestone` | string | site cutover | `validated` | a named, dated commitment. It is the fact schedules and reports both key on |
| `delivery_organisation` | string | Northwind Logistics | `validated` | whose project it is; §3.8's role discipline keeps it distinct from a delivery partner named in the same plan |
| `project_status` | string | closed | `llm_supported` | whether the project is live or finished — which decides whether its folder is working material or an archive, and it is stated in prose |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.3, §3.5):

- a project-control artifact term ('project charter' | 'project initiation document' | 'RAID log' | 'work breakdown structure' | 'lessons learned log' | 'project closure report') co-occurring with a named project or a project-identifier label
- a project-identifier label ('project code' | 'project ref' | 'PRJ') co-occurring with a milestone or phase label — the identifier alone is a bare reference and is refused below
- a schedule structure — 'task' and 'start' and 'finish' and 'predecessor' or '% complete' as sibling column headings — co-occurring with a named project

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- a plan written as prose with no control artifacts and only a project name in the title
- project status, which decides archival treatment and is a reading
- deciding which of several similarly named workstreams a document belongs to when no identifier is present
- separating a business project from a research project or a software project when the vocabulary is shared, which is the normal case

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10, §4.9):

- 'project'. This is the most over-subscribed field name in the entire catalogue: §3.11 assigns `project` to Research files AND to Code files, the personal slice has `pers.creative-project`, the software slice has `soft.source-project` and `soft.scratch-prototype`, and the education slice has coursework projects. A rule keyed on the word 'project' claims five other slices' material outright. It is refused here without a control artifact beside it
- 'plan' | 'timeline' | 'schedule' | 'milestone' | 'deliverable' | 'scope' — every one of them is ordinary English and appears in study plans, treatment plans, wedding schedules and research milestones
- 'phase' — §3.11's Research schema uses `stage`, and phase is its synonym; a clinical trial has phases too (health slice)
- 'RAID' | 'risk' | 'issue' | 'dependency' as bare tokens — RAID is also a storage term, which puts it directly in the software slice's path
- a Gantt-shaped spreadsheet. §2.9 says spreadsheets “should yield workbook or file metadata, sheet names, column headers, visible cell values, table-like regions, formulas only when useful, and dates or identifiers from labeled cells” and a schedule shares its shape with a budget, a register and a tracker
- an organisation name — §4.9 “A university name alone should not create a group because Columbia can appear as an authoring school, course provider, target institution, employer, research venue, or merely a cited organization”

### Work types

`project charter or PID`, `project plan`, `schedule`, `RAID or risk log`, `change request`, `highlight report`, `closure report`, `lessons learned log`, `benefits tracker`

### Grouping reasons (§4)

- one project across its charter, plan, schedule, logs, reports and closure — §4.5 names “one course, project, application, recruiting process, photo event, or submission packet”, and this is the business instance of it
- one milestone across the documents produced for it

### Template (§5)

`project → phase → document type`

Time first: **no**

§5.5: “a parent dimension should provide the context required to understand the child” — a phase label is meaningless without the project. §5.5's “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders” names project first explicitly, which makes this the design's own recommended order rather than a choice made here. §5.8's “The product should not force every branch to use the full template or have the same number of levels” matters particularly: a small project should stay a single folder.

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| res.research-project | the research slice owns `project` as a §3.11 field with stage, artifact type, lab and venue beside it. Where any of those are present this entry must not claim the file. Where a business project and a research project genuinely coincide — a funded delivery project inside a university — nothing separates them | §3.11 “Research files may use project, stage, artifact type, lab, and venue” |
| soft.source-project | the software slice owns `project` with repository and programming language beside it. A repository marker is decisive and this entry defers to it | §3.11 “Code files may use project, repository, programming language, and artifact type” |
| pers.creative-project | a personal renovation or creative project produces charters, plans and budgets too. The delivery organisation and project identifier are the separators, and a home project has neither | §4.9 “A university name alone should not create a group because Columbia can appear as an authoring school, course provider, target institution, employer, research venue, or merely a cited organization” |
| ops.programme-portfolio | a project inside a programme is reported at both levels and the same document appears in both folders. The programme reference is the separating signal | §4.9 “A file may validly belong to more than one accepted group” |
| eng.engineering-project | a fifth claimant on `project`: the engineering slice's branch root takes anything carrying a project or product identity in a physical-engineering context. A discipline, drawing, CAD or bill-of-materials reference routes a file there | §3.11 “One file may hold facts from more than one domain without losing information” |
| ops.client-engagement | a project delivered for a client is both. The engagement or matter reference should lead, because a client's material must stay together for confidentiality reasons that outrank tidiness | §3.8 “such as authored_by and target_school, or our_firm and client” |

### Sensitivity

`none` — Project control documents carry no category §2.9 names. A resourcing plan naming individuals is employment material and belongs to `hr.org-design-headcount`, which marks it. No handling class is assigned; that is P7's (§8.4).

### Open question — Joseph's call, unresolved

> Should there be ONE `project` domain across the whole catalogue rather than one per slice? §3.11 already gives `project` to Research and to Code, this entry adds a business instance, and the personal slice has its own. §3.12 says “The system may create new values when it sees a new course, project, company, university, or event, but it should not invent new fields automatically” — so the field is shared and only the SCHEMA around it differs. Either the product has one project domain whose neighbouring fields vary, or it has four domains that will compete for every file containing the word. This catalogue cannot resolve it alone because the answer changes four slices; it is Joseph's.

---

## `ops.programme-portfolio` — Programme and portfolio management

The layer above individual projects — programme definition, portfolio prioritisation, cross-project dependencies and PMO reporting.

**Provenance:** **proposal** — new here; the design names nothing like it

**Cite:** No design sentence names programme or portfolio management. §3.15 “Other domains remain placeholders until user demand and corpus evidence justify detailed templates” permits it. It is separated from `ops.project` because its unit of account is a set of projects, and a portfolio document that named only one project would be a project document.

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `programme` | string | Network transformation | `validated` | the programme or portfolio itself — the grouping key |
| `constituent_projects` | list of strings | Depot consolidation; Fleet renewal | `llm_supported` | the set the programme covers. It is what makes the file a programme document rather than a project one, and it is usually read from a table or prose rather than a labeled field |
| `portfolio_cycle` | string | FY2026 portfolio review | `validated` | the prioritisation round. Only validated beside a portfolio-artifact term |
| `governance_body` | string | programme board | `validated` | the body the programme reports to — the link to `ops.board-governance` |
| `dependency` | string | fleet renewal depends on depot cutover | `llm_supported` | §3.11 permits “several additional fields used only for search, privacy protection, explanation, or later review”; dependencies are the reason programme documents exist and they are prose or a matrix |
| `pmo_function` | string | programme management office | `validated` | which office produced it. §3.8 “It should avoid using authorship or creator identity as a destination dimension” — metadata; §5.7 requires the engine to validate that a proposed template “does not repeat a parent dimension, create meaningless one-child levels, exceed practical depth limits, use an author or organization merely as a collector” |
| `prioritisation_status` | string | approved for delivery | `llm_supported` | whether a project in the portfolio is funded, paused or dropped — the fact a user actually needs and a sentence |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.3, §3.5):

- a portfolio-artifact term ('portfolio review' | 'programme board pack' | 'prioritisation matrix' | 'benefits map' | 'dependency map' | 'programme definition document') co-occurring with a named programme or two or more named projects
- a multi-project table — a project-name column together with a status or RAG column and a sponsor or owner column — carrying more than one distinct named project, co-occurring with an organisation or programme name

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- a deck that reports across projects without naming a programme
- prioritisation status and dependencies, both of which are readings
- deciding whether a document is a programme artifact or the largest project's own reporting

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10, §4.9):

- 'programme' | 'program'. 'Program' is a software artifact (software slice), a broadcast programme, a degree programme (education slice — `acad.undergraduate-program` and `acad.graduate-program` are literally named that), a training programme and a conference programme. The education-slice collision alone makes a bare rule unusable
- 'portfolio'. An investment portfolio (finance slice), an artist's or designer's portfolio (creative slice), a student portfolio (education slice's `acad.arts-jury-portfolio`) and a career portfolio all match. Two other slices have domains named after it
- 'PMO' | 'roadmap' | 'prioritisation' — thin acronyms and ordinary words
- a project-name column on its own — that shape is shared with a resource plan, a budget and a risk register
- an organisation name — §4.9 “A university name alone should not create a group because Columbia can appear as an authoring school, course provider, target institution, employer, research venue, or merely a cited organization”

### Work types

`programme definition`, `portfolio review pack`, `prioritisation matrix`, `dependency map`, `benefits map`, `PMO standard or template`, `cross-project report`, `stage gate assessment`

### Grouping reasons (§4)

- one programme across its definition, reviews and cross-project reporting
- one portfolio cycle across the papers produced for it

### Template (§5)

`programme → portfolio cycle → document type`

Time first: **no**

§5.5: “a parent dimension should provide the context required to understand the child”. A cycle is meaningless without the programme. §5.5's “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders” keeps the cycle below the programme, so a programme's history stays together.

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| ops.project | a stage gate assessment is produced by the programme and about the project; both claims are real. The count of distinct named projects in the document is the practical separator | §4.9 “A file may validly belong to more than one accepted group” |
| ops.board-governance | a programme board pack is a board pack. Where a governance structure — notice, quorum, resolutions — is present the governance entry leads | §3.7 “It should rank candidate matches instead of accepting the first match” |
| acad.undergraduate-program | the education slice's domains are spelled 'program' and share the token completely. An academic programme carries a school, term or course; this one carries projects. Nothing weaker separates them | §3.11 “Academic files may use school, term, course, instructor, and work type” |
| ops.status-report | PMO reporting is status reporting done across projects. The multi-project scope is the separator, and a single-project report belongs to the reporting entry | §3.7 “It should rank candidate matches instead of accepting the first match” |

### Sensitivity

`none` — Nothing §2.9 names attaches to portfolio material. Resourcing detail at named-individual level is employment material and belongs to `hr.org-design-headcount`. No handling class is assigned; that is P7's (§8.4).

---

## `ops.retrospective-postmortem` — Retrospectives, post-mortems and lessons learned

The structured look back at a completed piece of work or a failure — what happened, why, and what changes as a result.

**Provenance:** **proposal** — new here; the design names nothing like it

**Cite:** No design sentence names retrospectives. §3.15 “Other domains remain placeholders until user demand and corpus evidence justify detailed templates” permits the addition. The software slice's `soft.incident-postmortem` already owns the technical-incident case; this entry is the delivery and organisational one.

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `subject_of_review` | string | Depot consolidation phase one | `validated` | the project, release, event or period being looked back on — the anchor without which a retrospective is a set of loose opinions |
| `review_type` | string | project retrospective | `validated` | retrospective, post-mortem, lessons learned, after-action review, wash-up |
| `review_date` | date | 2026-04-02 | `direct` | §3.13 direct: a labeled date. Distinct from the period reviewed, which is a separate fact |
| `finding` | string | supplier onboarding started too late | `llm_supported` | the substance. Every finding is a sentence and §3.6 requires the model cite the exact span |
| `corrective_action` | string | add a supplier readiness gate | `llm_supported` | what changes. This is the fact that makes the document worth retaining and it is prose |
| `participating_unit` | string | Delivery team | `validated` | whose retrospective it was. §3.8 “It should avoid using authorship or creator identity as a destination dimension” — participants are metadata |
| `severity_context` | string | following a failed cutover | `possible` | §3.11 permits “several additional fields used only for search, privacy protection, explanation, or later review”; whether the review follows a failure or a normal completion changes how it should be treated, and it is usually an inference |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.3, §3.5):

- a retrospective structure — two or more of 'what went well' | 'what did not go well' | 'what we would do differently' | 'start, stop, continue' | 'lessons learned' — co-occurring with a named subject of review
- an after-action term ('post-mortem' | 'after-action review' | 'wash-up' | 'lessons learned log') in a title position co-occurring with a named project, release or event
- a five-whys or root-cause structure — a 'root cause' heading together with a 'contributing factors' or 'timeline' heading — co-occurring with a named subject and a review date

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- informal retro notes captured as a bulleted list with no headings
- every finding and corrective action
- deciding whether a review is organisational or technical, which is what routes it between this entry and the software slice's incident entry

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10, §4.9):

- 'retro' | 'retrospective' — 'retro' is a design and fashion style, which puts it straight into the creative slice, and 'retrospective' is an exhibition type
- 'post-mortem' — literally a medical and forensic term; the health slice's material uses it in its original sense
- 'lessons' | 'review' | 'debrief'. 'Review' is the single worst token available: a performance review, a code review (software slice), a peer review (research slice — two domains are named after it), a design review, a book review, a product review, a literature review and a portfolio review are all 'reviews'
- 'root cause' | 'five whys' | 'what went well' as isolated phrases without a named subject — these are template boilerplate and appear in blank templates the user downloaded and never filled in
- 'incident' — the software slice owns technical incidents and `hr.health-safety` owns workplace ones; the word alone routes to neither

### Work types

`retrospective notes`, `post-mortem report`, `lessons learned log`, `after-action review`, `root-cause analysis`, `corrective action plan`

### Grouping reasons (§4)

- one subject of review across its notes, report and corrective actions
- one team across a series of retrospectives

### Template (§5)

`subject of review → review type → date`

Time first: **no**

§5.5: “a parent dimension should provide the context required to understand the child”. A retrospective is only findable through the thing it reviews. §5.5's “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders” keeps the date last, and §5.9's warning about a level that “It should warn when a level produces only one child, repeats a concept already expressed in the parent, creates excessive depth, or creates a large number of tiny folders” means the review-type level should usually collapse — most subjects have exactly one retrospective.

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| soft.incident-postmortem | the software slice owns technical incident post-mortems and this entry must not claim them. The separating signal is a technical artifact reference — a service, alert, deployment or repository. A retrospective on a failed office move has none | §3.11 “Code files may use project, repository, programming language, and artifact type” |
| hr.health-safety | a workplace incident investigation shares the root-cause structure exactly. An injured person, a regulator reference or a reportable-incident term routes it to the HR entry, which is marked sensitive; this entry must defer rather than absorb it | §3.8 “The system must separate roles that happen to contain the same entity type” |
| ops.project | a closure report contains lessons learned. Where the file is the closure report it is the project's; where it is a standalone review it is this one's | §3.11 “One file may hold facts from more than one domain without losing information” |
| qual.failure-analysis-rca | the engineering slice owns why one specific thing broke — the technical investigation and its evidence. A product, component or physical failure mode routes a file there; an organisational or delivery failure routes it here | §3.7 “It should rank candidate matches instead of accepting the first match” |
| corp.compliance-audit | a findings register and a corrective action record appear in both. An auditor, a framework or a certificate reference routes the file to the finance slice | §3.7 “It should rank candidate matches instead of accepting the first match” |

### Sensitivity

`none` — A delivery retrospective carries no category §2.9 names. One that attributes failure to named individuals is employment material — §8.4 lists “identity documents, account statements, tax records, medical information, legal records, credentials, private correspondence, GPS metadata, employment materials, and educational records” — and where that is the document's substance it belongs to `hr.employee-relations`, which marks it. No handling class is assigned; that is P7's (§8.4).

---

## `ops.risk-register` — Risk registers and risk management

The maintained inventory of things that could go wrong for an organisation, unit or project, with owners, treatments and review dates.

**Provenance:** **proposal** — new here; the design names nothing like it

**Cite:** No design sentence names risk management. §3.15 “Other domains remain placeholders until user demand and corpus evidence justify detailed templates” permits the addition. It is separated from a project's RAID log because an enterprise or unit risk register outlives every project in it and is maintained on its own cycle.

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `risk_scope` | string | Group operational risk | `validated` | whose register it is — enterprise, unit, project, supplier. Two registers differ by nothing else |
| `risk_category` | string | operational | `validated` | operational, financial, regulatory, strategic, health and safety. Categories are stated in a labeled column and are the one structural fact here |
| `risk_owner_role` | string | Head of Distribution | `direct` | §3.13 direct: a labeled owner column. §3.8 “It should avoid using authorship or creator identity as a destination dimension” — metadata |
| `treatment` | string | dual-source the cutover contractor | `llm_supported` | what is being done about it. Prose in a cell |
| `review_date` | date | 2026-06-30 | `direct` | §3.13 direct: a labeled next-review column. §3.10's explicit-regex path applies |
| `register_version` | string | Q1 FY2026 refresh | `validated` | a register is republished each cycle and the versions are otherwise indistinguishable |
| `risk_status` | string | open | `validated` | open, mitigated, closed, accepted — a labeled column value |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.3, §3.5):

- a risk-table structure — a 'risk' or 'risk description' column heading together with an 'owner' column heading and a 'mitigation' | 'treatment' | 'control' column heading — co-occurring with a named scope or organisation. §2.9 says spreadsheets “should yield workbook or file metadata, sheet names, column headers, visible cell values, table-like regions, formulas only when useful, and dates or identifiers from labeled cells”, and the three headings together are what carry the domain
- a risk-management artifact term ('risk register' | 'risk appetite statement' | 'risk management framework' | 'heat map') co-occurring with an organisation or unit name matched on a word boundary

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- a narrative risk assessment written as prose
- treatments, which are sentences
- deciding whether a register is enterprise, project or supplier scope when the file names none

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10, §4.9):

- 'risk'. Clinical risk and risk factors (health slice), investment risk and risk warnings (finance slice), risk of bias (research slice), security risk (software slice) and risk assessment for a school trip (education slice) all match. It is a five-slice word
- 'likelihood' | 'impact' | 'severity' | 'mitigation' | 'control' — all appear in clinical, security and safety documents
- 'register' — a share register (finance slice), a statutory register, an attendance register (education slice) and a cash register
- 'heat map' — also a data-visualisation artifact (software and research slices)
- a scored table. §2.9's spreadsheet shape covers risk registers, scorecards, budgets and prioritisation matrices identically
- an organisation name — §4.9 “A university name alone should not create a group because Columbia can appear as an authoring school, course provider, target institution, employer, research venue, or merely a cited organization”

### Work types

`risk register`, `risk assessment`, `risk appetite statement`, `heat map or matrix`, `control description`, `risk review minute`, `escalated risk paper`

### Grouping reasons (§4)

- one register across its periodic refreshes
- one risk scope across register, assessments and escalation papers

### Template (§5)

`risk scope → register version → document type`

Time first: **no**

§5.5: “a parent dimension should provide the context required to understand the child”. A version is meaningless without knowing whose register it versions. §5.5's “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders” keeps the cycle below the scope so a register's history reads as one thing.

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| corp.compliance-audit | that entry's own recognition names 'risk register' inside a compliance-register rule. The separating signal is a framework, standard or auditor — a compliance register exists to evidence a standard, a risk register does not. Where a framework is named, the finance slice leads | §3.11 “One file may hold facts from more than one domain without losing information” |
| ops.project | a project RAID log is a risk register with a project scope. The project identifier routes it to the project entry; a register with no project belongs here | §3.7 “It should rank candidate matches instead of accepting the first match” |
| hr.health-safety | a workplace risk assessment is a risk register about people. A regulator reference, a hazard vocabulary or a named worker routes it to the HR entry | §3.8 “The system must separate roles that happen to contain the same entity type” |
| eng.risk-analysis-fmea | the engineering slice owns structured analysis of how a design or process can fail — FMEA, HAZOP, fault tree. An analysed item, a failure mode or a design reference routes a file there; an organisational risk with an owner and a treatment belongs here | §3.7 “It should rank candidate matches instead of accepting the first match” |
| soft.security-finding-report | a security risk register uses the same columns. A vulnerability identifier, asset or CVSS-style reference routes it to the software slice | §3.11 “Code files may use project, repository, programming language, and artifact type” |

### Sensitivity

`none` — A risk register carries no category §2.9 names. Registers that describe named individuals as risks — key-person or conduct risks — are employment material and should be treated under `hr.employee-relations`. No handling class is assigned; that is P7's (§8.4).

---

## `ops.business-continuity` — Business continuity and crisis planning

Plans and exercises for keeping an organisation running through disruption — continuity plans, recovery arrangements, crisis playbooks and their tests.

**Provenance:** **proposal** — new here; the design names nothing like it

**Cite:** No design sentence names business continuity. §3.15 “Other domains remain placeholders until user demand and corpus evidence justify detailed templates” permits the addition. It is separate from `ops.risk-register` because a continuity plan is an operational instruction set rather than an inventory, and separate from the software slice's runbooks because its scope is the organisation rather than a service.

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `organisation` | string | Northwind Logistics | `validated` | whose continuity is planned for; §3.8's role discipline separates it from a recovery supplier named in the plan |
| `business_function` | string | Order fulfilment | `validated` | the function the plan protects. A continuity plan is written per function and that is the grouping key |
| `disruption_scenario` | string | loss of primary depot | `llm_supported` | what is planned against. Stated in prose and it is what a user searches for |
| `recovery_objective` | string | restore despatch within one working day | `llm_supported` | the commitment the plan makes. It is normally a labeled objective but the value is prose, and §3.3 forbids the catalogue holding the numeric target as a value in any case |
| `plan_version` | string | 2026 revision | `validated` | continuity plans are revised annually and versions are otherwise identical |
| `exercise_date` | date | 2026-05-14 | `direct` | §3.13 direct: a labeled exercise or test date, which distinguishes a test record from the plan |
| `invocation_status` | string | not invoked | `possible` | §3.11 permits “several additional fields used only for search, privacy protection, explanation, or later review”; whether a plan was ever used is usually an inference from a separate log |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.3, §3.5):

- a continuity-artifact term ('business continuity plan' | 'business impact analysis' | 'disaster recovery plan' | 'crisis management plan' | 'incident response plan' | 'continuity exercise') co-occurring with an organisation or business-function name matched on a word boundary
- a continuity structure — an 'invocation' or 'escalation' heading together with a 'recovery time objective' or 'critical functions' heading — co-occurring with an organisation name
- an exercise record — an 'exercise objectives' or 'exercise scenario' heading together with a labeled exercise date and a named plan

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- an emergency contact and instruction sheet with no continuity vocabulary
- disruption scenarios and recovery objectives, both prose
- separating an organisational continuity plan from a technical disaster-recovery runbook when one document does both

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10, §4.9):

- 'continuity' | 'recovery' | 'crisis' | 'emergency' | 'contingency'. Emergency and recovery belong to the health slice in their ordinary senses; a personal emergency contact sheet and a financial contingency both match
- 'BCP' | 'DR' | 'RTO' | 'RPO' — thin acronyms; 'DR' is also a title abbreviation and puts the rule straight into the health slice
- 'incident response' — the software slice owns this phrase for security and service incidents
- 'plan' — see `ops.strategy-plan`; the word claims the corpus
- an organisation name — §4.9 “A university name alone should not create a group because Columbia can appear as an authoring school, course provider, target institution, employer, research venue, or merely a cited organization”

### Work types

`business continuity plan`, `business impact analysis`, `crisis playbook`, `call tree or contact sheet`, `exercise scenario`, `exercise report`, `invocation log`, `recovery arrangement with a supplier`

### Grouping reasons (§4)

- one business function across its impact analysis, plan and exercise records
- one exercise across its scenario, observations and report

### Template (§5)

`organisation → business function → document type`

Time first: **no**

§5.5: “a parent dimension should provide the context required to understand the child”. A plan is only meaningful once the function it protects is known. §5.5's “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders” keeps the revision year out of the upper levels, because a continuity plan is consulted by function under pressure and never by year.

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| soft.runbook-operational-doc | a disaster-recovery runbook is a continuity artifact and a technical one. A service, system or infrastructure reference routes it to the software slice; an organisational function routes it here | §3.11 “Code files may use project, repository, programming language, and artifact type” |
| hr.health-safety | evacuation and emergency procedures sit in both. A hazard, a regulator or an injury vocabulary routes them to the HR entry | §3.8 “The system must separate roles that happen to contain the same entity type” |
| ops.risk-register | a business impact analysis is risk analysis. The separating signal is that continuity material prescribes actions under a scenario, where a register inventories and scores | §3.7 “It should rank candidate matches instead of accepting the first match” |
| ops.process-documentation | a crisis playbook is a procedure. It belongs here because its trigger is a disruption; a procedure with a routine trigger belongs there | §3.11 “One file may hold facts from more than one domain without losing information” |

### Sensitivity

`potentially_sensitive` — Call trees and contact sheets are the substance of this domain and they are lists of personal phone numbers and home addresses. §2.9's phrase is applied on that basis — the design uses it for contact material, noting that contact formats such as VCF should normally be privacy-protected rather than used to create folder proposals. No handling class is assigned; that is P7's (§8.4).

---

## `ops.policy-handbook` — Policies, handbooks and codes

Documents that state binding rules for an organisation's people — policies, employee handbooks, codes of conduct and their acknowledgements.

**Provenance:** **proposal** — new here; the design names nothing like it

**Cite:** No design sentence names policy documents. §3.15 “Other domains remain placeholders until user demand and corpus evidence justify detailed templates” permits the addition. It is a single entry rather than one per policy area because the artifact shape — a governing body, an applicability statement, an effective date and version control — is identical across them and the subject is a value, not a domain.

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `issuing_organisation` | string | Northwind Logistics | `validated` | who the policy binds; §3.8's role discipline separates it from a regulator or standards body cited inside it |
| `policy_subject` | string | remote working | `validated` | what the policy is about. It is a VALUE, not a domain — §3.12 “The system may create new values when it sees a new course, project, company, university, or event, but it should not invent new fields automatically” is the reason this catalogue does not carve one entry per policy area |
| `effective_date` | date | 2026-01-01 | `direct` | §3.13 direct: a labeled effective-from field. It is the fact that distinguishes the live policy from four superseded ones with the same title |
| `policy_version` | string | v4 | `direct` | §3.13 direct: a labeled version field in a document-control block. Note this is the DOCUMENT's own stated version, not the filename's — §3.1 makes version family a universal file fact and the two disagree constantly |
| `applies_to` | string | all UK employees | `llm_supported` | the scope statement. It is what makes a policy findable and it is a sentence |
| `approving_body` | string | executive committee | `validated` | who approved it — the link to governance and the signal that separates a policy from a draft |
| `acknowledgement_status` | string | signed by the employee | `llm_supported` | a signed acknowledgement is a different document from the policy, and belongs with the person's employment record rather than with the policy library — see the collision below |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.3, §3.5):

- a policy-control block — two or more of 'effective date' | 'policy owner' | 'review date' | 'version' | 'supersedes' | 'approved by' — co-occurring with a policy-artifact term ('policy' | 'code of conduct' | 'handbook' | 'standard' | 'procedure') in a TITLE position (§3.7's positional weighting)
- an applicability statement ('this policy applies to' | 'scope of this policy' | 'who this applies to') co-occurring with an issuing organisation name matched on a word boundary
- a handbook structure — a contents list carrying three or more distinct policy-subject headings — co-occurring with an organisation name

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- a one-page rule sheet with no control block
- applicability, which decides whether a policy is the user's own or one they merely hold
- separating a policy from the guidance note that explains it and from the training deck that teaches it

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10, §4.9):

- 'policy'. An insurance policy (finance and personal slices both have insurance domains), a privacy policy (software slice), a school policy (education slice), a government policy (research slice) and a returns policy all match. The finance slice's `fin.insurance` and the personal slice's `pers.insurance` would both be claimed outright by a bare rule — this is the single most damaging false-positive available in my slice and the reason the control block is mandatory here
- 'handbook' — a course handbook (education slice), a lab handbook (research slice), an owner's handbook for an appliance (personal slice's `pers.household-inventory`)
- 'code' — source code (software slice), a building code, a dress code, a discount code
- 'standard' | 'procedure' | 'guideline' — the research slice has `res.protocol-sop` and the health slice has `med.clinical-protocol-guideline`; both would be claimed
- 'effective date' alone — contracts, insurance policies and leases all carry one
- an organisation name — §4.9 “A university name alone should not create a group because Columbia can appear as an authoring school, course provider, target institution, employer, research venue, or merely a cited organization”

### Work types

`policy document`, `employee handbook`, `code of conduct`, `standard`, `guidance note`, `policy summary`, `acknowledgement form`, `policy register`

### Grouping reasons (§4)

- one policy subject across its versions and supersessions
- one handbook edition across its constituent policies
- one policy refresh cycle across the documents reissued in it

### Template (§5)

`issuing organisation → policy subject → version`

Time first: **no**

§5.5: “a parent dimension should provide the context required to understand the child”. A version is meaningless without the policy subject. §5.5's “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders” is why the effective year is not a level: a user looks for the remote-working policy and then for the current version of it, never for 2024's policies.

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| fin.insurance | the finance slice's `fin.insurance` and the personal slice's `pers.insurance` both own a domain whose central artifact is called a policy. The word is shared completely and the separating signal is an insurer, premium or cover schedule on their side, and an issuing employer plus an applicability statement on this one | §3.8 “The system must separate roles that happen to contain the same entity type” |
| career.onboarding-paperwork | the same PDF sits in the HR department's policy library and in an employee's own records. Nothing in the file distinguishes the two copies; only whose folder it is in does, and §5.10 says “Existing folders must not be automatically flattened, renamed, or reorganized simply because a template would produce a different structure” | §3.8 “The system must separate roles that happen to contain the same entity type” |
| res.protocol-sop | a standard operating procedure carries an identical control block. A laboratory, clinical or instrument vocabulary routes it to those slices | §3.11 “Research files may use project, stage, artifact type, lab, and venue” |
| law.compliance-programme | a compliance policy is drafted by the legal function and issued by the organisation. Where a regulator, statute or legal-advice framing is present the law slice leads | §3.7 “It should rank candidate matches instead of accepting the first match” |
| gov.policy-development | the government slice owns the working papers by which a public body develops a policy POSITION — options papers, impact assessments, consultation. That is policy in the public-policy sense; this entry is policy in the internal-rulebook sense, and the word is the same word | §3.8 “The system must separate roles that happen to contain the same entity type” |
| ops.process-documentation | a policy says what must be true; a procedure says how to do it. Many documents do both and the boundary is genuinely soft; the presence of step-numbered instructions is the practical test | §3.11 “One file may hold facts from more than one domain without losing information” |

### Sensitivity

`none` — A published policy is the least sensitive thing in this slice — it is written to be circulated. A SIGNED ACKNOWLEDGEMENT is different: it is employment material naming an individual, which §8.4 lists among “identity documents, account statements, tax records, medical information, legal records, credentials, private correspondence, GPS metadata, employment materials, and educational records”, and it belongs with `hr.onboarding` or the career slice rather than in the policy library. No handling class is assigned; that is P7's (§8.4).

---

## `ops.process-documentation` — Process and procedure documentation

Instructions for how work is actually done — standard operating procedures, work instructions, process maps and internal how-to material.

**Provenance:** **proposal** — new here; the design names nothing like it

**Cite:** No design sentence names process documentation. §3.15 “Other domains remain placeholders until user demand and corpus evidence justify detailed templates” permits the addition. The research slice's `res.protocol-sop`, the health slice's `med.clinical-protocol-guideline` and the software slice's `soft.runbook-operational-doc` already own the same artifact inside their own contexts; this entry is the business-process one and defers to all three.

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `process_name` | string | Goods inward receipting | `validated` | the process documented. It is the grouping key and it is what a user searches for |
| `owning_function` | string | Warehouse operations | `validated` | which function owns the process. §3.8 “It should avoid using authorship or creator identity as a destination dimension” — the function, not the author |
| `document_type` | string | standard operating procedure | `validated` | SOP, work instruction, process map, checklist, how-to, RACI |
| `process_version` | string | v2.1 | `direct` | §3.13 direct: a labeled version in a control block, distinct from the filename's version token |
| `system_referenced` | string | warehouse management system | `validated` | the tool the procedure operates. It is the strongest corroborating signal available and often the only thing that makes a bare step list placeable |
| `effective_date` | date | 2026-02-01 | `direct` | §3.13 direct: a labeled effective-from field |
| `step_count_scope` | string | end-to-end receipting | `llm_supported` | §3.11 permits “several additional fields used only for search, privacy protection, explanation, or later review”; the boundary of what the procedure covers, which is prose. No count is held as a value — §3.3's rule that this catalogue carries no numbers |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.3, §3.5):

- a step-numbered instruction structure — a numbered or 'Step 1' sequence of imperative instructions — co-occurring with a named process or system AND a document-control block
- a procedure-artifact term ('standard operating procedure' | 'work instruction' | 'process map' | 'RACI') in a title position co-occurring with an owning function or organisation name matched on a word boundary
- a swimlane or flow structure — role labels used as lane headings together with a decision diamond or 'if...then' branch vocabulary — co-occurring with a named process

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- a how-to written as prose with no numbered steps
- deciding whether a step list is a business procedure, a laboratory protocol, a clinical guideline or a technical runbook — the four are indistinguishable by shape and only the vocabulary inside separates them
- process scope, which is prose

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10, §4.9):

- 'process' | 'procedure' | 'SOP' | 'workflow' | 'how to' | 'guide' | 'checklist' | 'instructions'. A recipe is a numbered instruction list (personal slice's `pers.recipe-meal`), so is an assembly manual, a lab protocol, a clinical guideline, an exam rubric and a software install guide. 'SOP' is the most specific of them and still belongs to the research slice by name
- a numbered step structure on its own — this is the shape, and the shape is shared by every instruction ever written
- 'v2' | 'v2.1' | 'final' — §3.1's version family is a universal file fact and carries no domain information
- a flowchart or diagram file — a format, not a domain
- an organisation name — §4.9 “A university name alone should not create a group because Columbia can appear as an authoring school, course provider, target institution, employer, research venue, or merely a cited organization”

### Work types

`standard operating procedure`, `work instruction`, `process map`, `checklist`, `RACI matrix`, `training aid`, `job aid`, `process change note`

### Grouping reasons (§4)

- one process across its map, procedure, checklist and job aids
- one function's procedure set across a review cycle

### Template (§5)

`owning function → process → document type`

Time first: **no**

§5.5: “a parent dimension should provide the context required to understand the child”. A procedure is found through the process and the process is found through the function that owns it. §5.5's “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders” keeps versions and dates out of the folder structure entirely, which is right here because only the current version is normally wanted.

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| res.protocol-sop | the research slice owns the laboratory protocol and its version control is if anything stricter. A reagent, instrument, sample or lab reference routes a file there and this entry must not claim it | §3.11 “Research files may use project, stage, artifact type, lab, and venue” |
| med.clinical-protocol-guideline | a clinical pathway is a step-numbered procedure. Any clinical vocabulary routes it to the health slice, whose sensitivity treatment must not be lost by mis-routing | §3.8 “The system must separate roles that happen to contain the same entity type” |
| soft.runbook-operational-doc | an operational runbook is a procedure for a service. A service, host, alert or command-line reference routes it to the software slice | §3.11 “Code files may use project, repository, programming language, and artifact type” |
| hr.training-lnd | a job aid is training material and a procedure at once. Where the file is built around a learner and a completion record it is the training entry's | §3.11 “One file may hold facts from more than one domain without losing information” |
| mfg.work-instruction | the engineering slice owns the controlled instruction that tells an operator how to perform one operation, templated product then operation. A product, operation or manufacturing vocabulary routes a file there and this entry must not claim it | §3.7 “It should rank candidate matches instead of accepting the first match” |
| pers.recipe-meal | a recipe is a numbered instruction list with ingredients. Only the domain vocabulary separates them, which is exactly why a bare step-list rule is refused above | §4.9 “A university name alone should not create a group because Columbia can appear as an authoring school, course provider, target institution, employer, research venue, or merely a cited organization” |

### Sensitivity

`none` — Procedure documentation carries no category §2.9 names. A procedure that embeds credentials or access instructions does, and the software slice's `soft.configuration-and-secrets` is the right home for that content. No handling class is assigned; that is P7's (§8.4).

---

## `ops.facilities-workplace` — Facilities and workplace management

The physical workplace as an administered thing — premises, space, maintenance, access and the services that keep a site running.

**Provenance:** **proposal** — new here; the design names nothing like it

**Cite:** No design sentence names facilities. §3.15 “Other domains remain placeholders until user demand and corpus evidence justify detailed templates” permits the addition. The finance slice's `legal.lease` owns the tenancy instrument; this entry is the running of the space, not the right to occupy it.

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `site` | string | Bermondsey depot | `validated` | the premises. This is the grouping key and it is the one fact that reliably distinguishes otherwise identical facilities documents |
| `organisation` | string | Northwind Logistics | `validated` | the occupier; §3.8's role discipline separates it from the landlord, the managing agent and every contractor named in the same file |
| `facility_service` | string | planned maintenance | `validated` | cleaning, security, maintenance, catering, reception, waste. The service is the second dimension and it is normally stated |
| `contractor` | string | Meridian FM | `validated` | the supplier delivering the service. §3.8's role discipline is essential here — the contractor and the occupier are both companies on the same page |
| `asset_or_space` | string | Loading bay 3 | `validated` | the room, zone or plant item. It is what maintenance and space records key on |
| `service_date` | date | 2026-04-08 | `direct` | §3.13 direct: a labeled service, inspection or visit date |
| `occupancy_scope` | string | second floor, forty desks | `llm_supported` | §3.11 permits “several additional fields used only for search, privacy protection, explanation, or later review”; space-planning detail is prose and a plan drawing, and no count is held as a value |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.3, §3.5):

- a facilities-artifact term ('planned preventive maintenance' | 'facilities management' | 'space plan' | 'building handbook' | 'permit to work' | 'access request' | 'service schedule') co-occurring with a named site or premises address
- a maintenance record structure — an asset or plant identifier label together with a service date label and a contractor name matched on a word boundary
- a site-services term ('cleaning schedule' | 'waste transfer note' | 'security patrol log' | 'meter reading') co-occurring with a named site

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- a floor plan or drawing whose site is written only in a title block
- occupancy and space-planning intent, which is prose
- separating a workplace-services record from the lease obligation that requires it

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10, §4.9):

- 'facilities' | 'building' | 'office' | 'site' | 'workplace'. 'Office' is also a software suite and a filename fragment; 'site' is a website (software slice), an archaeological site (research slice) and a construction site
- an address. A premises address and a home address have the same shape, which puts every facilities rule directly into the personal slice's household material — and §8.4 treats addresses as material to keep local
- 'maintenance' — software maintenance, vehicle maintenance (personal slice's `pers.vehicle`), equipment maintenance (research slice)
- 'access' | 'badge' | 'key' — 'access' is an authorisation concept in the software slice and a database product name
- a contractor's company name — §4.9 “A university name alone should not create a group because Columbia can appear as an authoring school, course provider, target institution, employer, research venue, or merely a cited organization”, and a facilities contractor appears as a supplier on an invoice far more often than as the subject of a facilities record

### Work types

`space plan`, `floor plan or drawing`, `maintenance schedule`, `service report`, `permit to work`, `access or badge record`, `inspection certificate`, `utility or meter record`, `office move plan`

### Grouping reasons (§4)

- one site across its plans, services, inspections and records
- one contracted service across a service year
- one office move across its plan, layouts and communications

### Template (§5)

`site → facility service → year`

Time first: **no**

§5.5: “a parent dimension should provide the context required to understand the child”. A service record is meaningless without knowing which site it is for. §5.5's “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders” puts the year last, and here it genuinely earns a level because service records recur annually and accumulate; §5.9's warning about a level that “It should warn when a level produces only one child, repeats a concept already expressed in the parent, creates excessive depth, or creates a large number of tiny folders” applies to the site level for a single-site organisation.

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| legal.lease | the lease creates the right to occupy and is theirs. A service charge statement is arguably both — it arrives under the lease and describes facilities services. A landlord and a demised-premises clause route it to the lease entry | §3.11 “One file may hold facts from more than one domain without losing information” |
| pers.home-tenure | a home is a premises with maintenance records, meter readings and contractor invoices. Only an employer organisation separates them, and for a home-based business there is none | §3.8 “The system must separate roles that happen to contain the same entity type” |
| soft.it-asset-inventory | desks, phones and laptops appear in both a facilities inventory and an IT asset register. A serial number with a hardware or software configuration routes it to the software slice | §3.11 “Code files may use project, repository, programming language, and artifact type” |
| hr.health-safety | inspections, permits to work and incident locations sit in both. A hazard, a regulator or an injured person routes the file to the HR entry | §3.8 “The system must separate roles that happen to contain the same entity type” |

### Sensitivity

`none` — Facilities records carry no category §2.9 names as such. Access and badge records naming individuals are employment material — §8.4 lists “identity documents, account statements, tax records, medical information, legal records, credentials, private correspondence, GPS metadata, employment materials, and educational records” — and a premises address in a home-working context is a home address. Where either is the file's substance it belongs to an HR entry or the personal slice, which mark it. No handling class is assigned; that is P7's (§8.4).

---

## `ops.business-travel` — Business travel administration

Travel undertaken for work as an administered thing — authorisation, booking, itinerary and the trip record on the employer's side.

**Provenance:** **inference** — extends a domain the design does name

**Cite:** Travel is one of the domains the design names: §5.7's list is “covering common organizational situations such as academic programs, university applications, recruiting processes, client engagements, research workflows, financial records, travel, legal matters, creative projects, software repositories, personal administration, and photo collections”, and §7.3 names a residual template holding transactional records including boarding passes. Extending that named domain to the EMPLOYER side — authorisation, policy compliance and the trip as a cost — is the inference. No design sentence names business travel.

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `traveller_role` | string | field engineer | `llm_supported` | the role, not the person. §3.8 “It should avoid using authorship or creator identity as a destination dimension” — a traveller name must never become a folder level, and §4.9 warns against grouping “when one high-frequency entity acts as the only bridge”, which a frequent traveller is |
| `trip_purpose` | string | depot commissioning visit | `llm_supported` | §3.9 makes purpose a first-class facet, and purpose is the ONLY thing that distinguishes a business trip from a personal one when the itinerary looks identical |
| `organisation` | string | Northwind Logistics | `validated` | who authorised and pays. This is the discriminator against the personal travel domain |
| `authorisation_reference` | string | TRV-2026-0412 | `direct` | §3.13 direct: a labeled travel-authorisation or request number. Where an organisation uses one this is the strongest fact in the domain |
| `destination` | string | Rotterdam | `validated` | where. Shared with the personal travel domain and useless on its own |
| `travel_dates` | date range | 2026-04-08 to 2026-04-11 | `direct` | §3.13 direct: labeled departure and return fields on an itinerary. §3.10's explicit-regex path applies |
| `cost_centre` | string | OPS-4200 | `direct` | §3.13 direct: a labeled cost-centre code, which alongside the authorisation reference is what makes the trip an organisational record rather than a personal one |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.3, §3.5):

- a travel-authorisation term ('travel request' | 'travel authorisation' | 'trip approval' | 'travel booking request') co-occurring with an organisation name AND a cost-centre or approver label
- a corporate booking artifact — a booking reference label together with a named travel management company or corporate booking tool AND an employer name matched on a word boundary
- a travel-policy compliance marker ('within policy' | 'policy exception approved' | 'lowest logical fare') co-occurring with a traveller and an organisation

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- an itinerary or boarding pass with no employer marker at all, where the only signal that the trip is business is the destination matching a client or site
- trip purpose, which §3.9 makes central and which is almost never stated on the travel document itself

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10, §4.9):

- an itinerary, a boarding pass, a hotel confirmation or a flight number. These are the personal slice's `pers.travel-record` material by default and §7.3's residual library already names a template for isolated booking records. Nothing in a boarding pass says whether the trip was for work
- a destination or an airport code — §3.7 “It should use word-boundary matching rather than substring matching” does not help when the token is a three-letter code that collides with initials and abbreviations
- a date range — §3.10 “frequently contain numbers that look like years but are course identifiers, version numbers, build numbers, ZIP codes, or other unrelated values”
- a traveller's name — §3.8 “It should avoid using authorship or creator identity as a destination dimension”
- 'travel' | 'trip' | 'conference' — the education slice has `acad.conference-travel-student` and the research slice has conference material; both would be claimed

### Work types

`travel request or authorisation`, `itinerary`, `booking confirmation`, `visa or entry support letter`, `trip report`, `travel policy exception`, `travel expense summary`

### Grouping reasons (§4)

- one trip across its authorisation, bookings, itinerary and report — §3.9's “The documents are content-incoherent but purpose-coherent” is exactly this case, since a flight, a hotel and a meeting agenda share no topic
- one traveller's trips within a period, for expense reconciliation only

### Template (§5)

`organisation → year → trip`

Time first: **no**

§5.5's default is “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders”, and this entry is a deliberate partial exception: a trip is a dated event and its documents are reconciled by period, so the year sits above the trip. It is NOT time-first — the organisation still leads, because the whole point of the domain is separating work trips from the personal travel domain, and §5.5's photo exception (“Photos and capture-based media are the major exception: time often belongs first because capture date is a defining aspect of the material”) does not apply to administrative records.

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| pers.travel-record | the personal slice owns travel and this is a design-named domain, so the burden is on this entry to prove a work trip rather than the reverse. A boarding pass with no employer marker belongs to them. A trip that is half business and half holiday — the common case — is genuinely both | §4.9 “A file may validly belong to more than one accepted group” |
| biz.expense-report | the claim and its receipts are theirs; the authorisation and itinerary are this entry's. The same trip produces both and they should stay linked rather than merged | §3.11 “One file may hold facts from more than one domain without losing information” |
| acad.conference-travel-student | academic and research travel is already covered by two other slices with their own funding and approval artifacts. This entry must not claim a trip carrying a grant, award or student reference | §3.11 “Research files may use project, stage, artifact type, lab, and venue” |
| pers.travel-visa-entry | a business visa support letter is issued by the employer and is an immigration record for the person. The finance slice's `admin.immigration` and the personal slice both have claims | §3.8 “The system must separate roles that happen to contain the same entity type” |

### Sensitivity

`potentially_sensitive` — Travel records carry an individual's movements and §8.4 names GPS metadata among the material that must remain local, alongside “identity documents, account statements, tax records, medical information, legal records, credentials, private correspondence, GPS metadata, employment materials, and educational records”. An itinerary is a location history for a named person. The marking is conservative and made on personal-data grounds. No handling class is assigned; that is P7's (§8.4).

### Open question — Joseph's call, unresolved

> Travel is a design-named domain owned by the personal slice, and this entry deliberately carves the employer's side out of it. The mixed trip — flights booked by the employer, a weekend added at the traveller's own cost, photographs from both — has no defensible split, and §4.9's “A file may validly belong to more than one accepted group” suggests it should simply be two memberships. Whether the product surfaces one trip in two branches, or whether business travel should not be a separate domain at all and should instead be a purpose facet on the personal travel domain, is Joseph's call. It matters because it decides whether a personal holiday can end up in a work folder.

---

## `ops.sourcing-rfp` — Sourcing events, tenders and bid evaluation

The competitive process of choosing a supplier — the requirement issued, the responses received, the evaluation and the award.

**Provenance:** **proposal** — new here; the design names nothing like it

**Cite:** No design sentence names sourcing. §3.15 “Other domains remain placeholders until user demand and corpus evidence justify detailed templates” permits the addition. The finance slice already owns `biz.procurement-po` (the order) and `biz.vendor-management` (the ongoing relationship); this entry is the competitive EVENT that precedes both, which neither covers.

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `sourcing_event` | string | Depot cleaning services tender | `validated` | the event itself. It is the grouping key and it binds documents from many different companies into one purpose-coherent set |
| `tender_reference` | string | RFP-2026-031 | `direct` | §3.13 direct: a labeled tender or RFP number. The single strongest fact here — it appears on the issued document and on every bidder's response, which is what makes the group reliable |
| `buyer_organisation` | string | Northwind Logistics | `validated` | who is buying; §3.8's role discipline is critical because every bidder's name is also a company on the same pages |
| `bidder` | string | Meridian FM | `validated` | a responding supplier. §3.8 “The system must separate roles that happen to contain the same entity type” — buyer and bidder are two roles for one entity type and confusing them inverts the whole domain |
| `event_stage` | string | evaluation | `validated` | requirement, clarification, response, evaluation, award, standstill, debrief |
| `submission_deadline` | date | 2026-03-20 | `direct` | §3.13 direct: a labeled deadline field |
| `award_outcome` | string | awarded to Meridian FM | `llm_supported` | who won. It is stated in a letter, in prose, and it is what a user searches the folder for |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.3, §3.5):

- a sourcing-artifact term ('request for proposal' | 'invitation to tender' | 'request for quotation' | 'request for information' | 'statement of requirements' | 'evaluation criteria') co-occurring with a tender-reference label OR a submission-deadline label
- a bid-response header — a tender reference co-occurring with a bidder name matched on a word boundary AND a response or submission term
- an award or standstill letter — an award vocabulary ('notification of award' | 'unsuccessful bidder' | 'standstill period' | 'debrief') co-occurring with a tender reference

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- a supplier's unsolicited proposal that is not part of a tender at all
- award outcome, which is a sentence in a letter
- separating a bid evaluation from the business case that used the same options analysis

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10, §4.9):

- 'RFP' | 'RFQ' | 'RFI' | 'ITT' | 'tender' | 'bid'. The acronyms are thin: 'RFI' is also a radio-frequency interference term and a request-for-information in litigation (law slice), 'bid' is an auction and an advertising term. §3.7 “It should use word-boundary matching rather than substring matching” helps but does not make an acronym unambiguous
- 'proposal' — see `ops.business-case`; a grant proposal and a thesis proposal both match
- 'evaluation' | 'scoring' | 'criteria' — the research slice's evaluation material and the education slice's marking rubrics both match
- a supplier's company name — §4.9 “A university name alone should not create a group because Columbia can appear as an authoring school, course provider, target institution, employer, research venue, or merely a cited organization”, and in a sourcing event the same company is a bidder in one file and a mere reference in another
- a deadline date — §3.10 “frequently contain numbers that look like years but are course identifiers, version numbers, build numbers, ZIP codes, or other unrelated values”

### Work types

`statement of requirements`, `RFP or ITT pack`, `clarification log`, `bidder response`, `evaluation matrix`, `moderation record`, `award letter`, `regret or debrief letter`, `standstill notice`

### Grouping reasons (§4)

- one sourcing event across the requirement, every bidder's response, the evaluation and the award — §3.9's “The documents are content-incoherent but purpose-coherent” describes it exactly, since responses from four different companies share no author and one purpose
- one bidder across the documents they submitted to one event

### Template (§5)

`sourcing event → stage → bidder`

Time first: **no**

§5.5: “a parent dimension should provide the context required to understand the child”. A bidder folder is meaningless outside its event — the same supplier bids for several — and a response is meaningless without knowing the stage. §5.5's “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders” keeps the year out entirely: a tender spans months and splitting it by calendar year would break the one group that matters. §5.9 warns against a level that “It should warn when a level produces only one child, repeats a concept already expressed in the parent, creates excessive depth, or creates a large number of tiny folders”, so a single-bidder event should collapse the bidder level.

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| biz.procurement-po | the award becomes a purchase order and the two documents cross-reference. The finance slice owns anything with a PO number, a delivery note or a three-way match; this entry stops at the award | §3.11 “One file may hold facts from more than one domain without losing information” |
| biz.vendor-management | a due-diligence questionnaire appears in both a tender and an onboarding pack. A vendor code or a vendor-master reference routes it to the finance slice; a tender reference routes it here | §3.7 “It should rank candidate matches instead of accepting the first match” |
| legal.contracts | the contract that follows an award is theirs. This entry holds the tender documents that become its schedules, which is a genuine ambiguity for the incorporated statement of requirements | §3.11 “One file may hold facts from more than one domain without losing information” |
| res.grant-proposal | a competitively assessed funding call has the same shape as a tender, right down to the evaluation criteria — but with the user on the RESPONDING side. A funder and award reference route it to the research slice | §3.8 “The system must separate roles that happen to contain the same entity type” |
| gov.procurement-tender | the government slice owns a public body's competitive purchase, with the same notice, bids, evaluation and award. A public-body buyer, a published notice reference or a statutory procedure routes a file there | §3.7 “It should rank candidate matches instead of accepting the first match” |
| ops.partnerships-bd | when the user's own organisation is the BIDDER rather than the buyer, this entry's roles invert and the material is business development. That is a different domain and this one must not claim it — see the open question | §3.8 “such as authored_by and target_school, or our_firm and client” |

### Sensitivity

`none` — Tender material carries no category §2.9 names. It is commercially confidential during the process, which is the separate question raised on `ops.business-records`. No handling class is assigned; that is P7's (§8.4).

### Open question — Joseph's call, unresolved

> This entry is written from the BUYER's side. The same corpus, for a supplier-side user, contains the mirror image — the RFPs they respond to and the bids they submit — and every field inverts: their bidder becomes our organisation, their tender reference is someone else's. §3.8's “such as authored_by and target_school, or our_firm and client” names the role discipline that makes this expressible but does not say whether one domain with a role field or two domains is right. This catalogue routes supplier-side bidding to `ops.partnerships-bd`, which is a compromise rather than a decision, and it is Joseph's call because it determines whether a consultancy's proposal library and a buyer's tender file are one branch or two.

---

## `ops.contract-administration` — Contract administration and obligation management

Running a contract after it is signed — the register, the obligations, the renewal and notice dates, and the correspondence that manages them.

**Provenance:** **proposal** — new here; the design names nothing like it

**Cite:** No design sentence names contract administration. §3.15 “Other domains remain placeholders until user demand and corpus evidence justify detailed templates” permits the addition. The finance slice's `legal.contracts` and the law slice's `law.contract-negotiation` own the INSTRUMENT — drafts, redlines, executed copies, amendments. This entry deliberately claims none of that: it is the operational layer that tracks what the signed instrument requires.

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `contract_reference` | string | CON-2024-118 | `direct` | §3.13 direct: a labeled contract reference. It is the link back to the instrument and the strongest fact in the domain |
| `counterparty` | string | Meridian FM | `validated` | the other side; §3.8 “such as authored_by and target_school, or our_firm and client” is the exact pattern — our entity and the counterparty are two roles for one entity type |
| `our_entity` | string | Northwind Logistics Ltd | `validated` | our side, kept as a separate field for the same reason |
| `obligation` | string | quarterly service review | `llm_supported` | what the contract requires someone to do. It is the substance of this domain and it is always prose |
| `key_date` | date | 2026-09-30 | `direct` | §3.13 direct: a labeled renewal, notice, break or expiry date. §3.10's explicit-regex path applies — “Date candidates should be identified with explicit regular expressions and then parsed without fuzzy matching” |
| `date_type` | string | notice deadline | `validated` | renewal, expiry, break, notice, review. A date without its type is useless and the type is normally a labeled column |
| `administration_status` | string | renewal decision outstanding | `llm_supported` | §3.11 permits “several additional fields used only for search, privacy protection, explanation, or later review”; the state a user needs and a sentence |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.3, §3.5):

- a contract-register structure — a contract-reference column heading together with a counterparty column heading and a renewal, expiry or notice-date column heading
- an obligation-tracking term ('obligations register' | 'contract register' | 'renewal calendar' | 'notice period' | 'break option' | 'service credit') co-occurring with a contract reference label AND a counterparty name matched on a word boundary
- a contract-management correspondence marker ('notice of renewal' | 'notice to terminate' | 'variation request' | 'service credit claim') co-occurring with a contract reference

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- an obligation extracted from a clause rather than a register — which is reading a contract, not matching a pattern
- administration status, which is prose
- deciding whether a letter is contract administration or the start of a dispute, which changes the slice it belongs to

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10, §4.9):

- 'contract' | 'agreement' | 'terms'. The finance slice has `legal.contracts` and the law slice has three contract domains; an employment contract belongs to the career slice; terms and conditions appear on every receipt. This entry must never win on the word alone
- 'renewal' | 'expiry' | 'notice' — an insurance renewal (finance and personal slices), a subscription renewal (`admin.subscriptions-recurring` in the finance slice), a passport expiry (personal slice's `pers.identity-document`), a notice period in an employment letter
- a counterparty name — §4.9 “A university name alone should not create a group because Columbia can appear as an authoring school, course provider, target institution, employer, research venue, or merely a cited organization”
- a date column — §3.10 “frequently contain numbers that look like years but are course identifiers, version numbers, build numbers, ZIP codes, or other unrelated values”
- 'SLA' | 'service credit' — the software slice's service-level material uses the same terms

### Work types

`contract register`, `obligations register`, `renewal calendar`, `notice letter`, `variation request`, `service credit claim`, `contract review record`, `contract summary sheet`

### Grouping reasons (§4)

- one contract across the administrative records generated over its life
- one renewal cycle across the review, decision and notice

### Template (§5)

`counterparty → contract → document type`

Time first: **no**

§5.5: “a parent dimension should provide the context required to understand the child”. A notice letter is meaningless without knowing which contract it serves. §5.5's “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders” keeps years out, because a contract's administrative history is one thread and a calendar split would cut it. §5.7 requires the engine to validate that a proposed template “does not repeat a parent dimension, create meaningless one-child levels, exceed practical depth limits, use an author or organization merely as a collector” — a live risk here: the counterparty level must be the contracting party, not merely every company that appears

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| legal.contracts | deferred to on the instrument itself. The separating signal is that this entry's files reference a contract without being one — a register row, a calendar entry, a notice letter. Any executed instrument, redline or signature page is theirs | §3.11 “One file may hold facts from more than one domain without losing information” |
| law.contract-negotiation | the law slice owns negotiation as practitioner work. This entry starts after signature | §3.8 “The system must separate roles that happen to contain the same entity type” |
| biz.vendor-management | a supplier contract register and a vendor master are near-identical tables. A vendor code or onboarding pack routes it to the finance slice; a contract reference and an obligation route it here. The boundary is thin and both claims are often true | §3.7 “It should rank candidate matches instead of accepting the first match” |
| admin.subscriptions-recurring | a software subscription renewal is contract administration at small scale. The finance slice's entry has the payment side and should lead where a charge is present | §3.11 “One file may hold facts from more than one domain without losing information” |

### Sensitivity

`none` — Contract administration records carry no category §2.9 names. Where a contract is an employment one its administration is employment material — §8.4's “identity documents, account statements, tax records, medical information, legal records, credentials, private correspondence, GPS metadata, employment materials, and educational records” — and belongs to the career slice or `hr.offer-package`. No handling class is assigned; that is P7's (§8.4).

---

## `ops.client-engagement` — Client engagements and professional-services delivery

Work done for a paying client by a firm — the engagement as the organising unit, with its scope, deliverables, working papers and closing report.

**Provenance:** **design** — a design sentence names this domain or its fields

**Cite:** §5.7 names this domain in the design's own list of what the template library should cover: “covering common organizational situations such as academic programs, university applications, recruiting processes, client engagements, research workflows, financial records, travel, legal matters, creative projects, software repositories, personal administration, and photo collections” — the phrase 'client engagements' appears there verbatim. §3.8 names its two defining fields and the role discipline they require: “A consulting document may mention the author’s firm and the client organization”, and the field pair “such as authored_by and target_school, or our_firm and client”. This is the one entry in this slice whose domain AND fields are both named by design sentences.

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `client` | string | Harbourline Group | `validated` | §3.8 names this field: “such as authored_by and target_school, or our_firm and client”. The client is the organisation the work is FOR, and §3.8's whole point is that it must not be conflated with the firm doing it |
| `our_firm` | string | Castellan Advisory | `validated` | §3.8 names this field in the same pair. Recording it separately is what makes a document placeable when both names appear on every page |
| `engagement` | string | Operating model review | `validated` | the engagement itself — the unit of organisation. §4.5 names “one course, project, application, recruiting process, photo event, or submission packet” and an engagement is the professional-services instance of a project |
| `engagement_reference` | string | ENG-2026-007 | `direct` | §3.13 direct: a labeled engagement or job code. Where a firm uses one it is decisive, because client names recur across many engagements |
| `deliverable_type` | string | final report | `validated` | proposal, engagement letter, workplan, working paper, interim deliverable, final report, closing note |
| `engagement_phase` | string | fieldwork | `validated` | scoping, fieldwork, reporting, closure — the staged vocabulary a professional-services file follows |
| `client_contact_role` | string | client finance director | `llm_supported` | §3.8 “It should avoid using authorship or creator identity as a destination dimension” — the role is useful, the name is metadata, and §2.9 requires contact material be privacy-protected rather than used to build folders |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.3, §3.5):

- an engagement-artifact term ('engagement letter' | 'statement of work' | 'scope of services' | 'engagement code' | 'working papers' | 'deliverable acceptance') co-occurring with a client name matched on a word boundary AND a distinct firm name in a separate role block — the two names in two roles are what §3.8 requires and what makes the rule safe
- an engagement-reference label co-occurring with a client name and a deliverable term
- a client-report front matter block — a 'prepared for' line naming one organisation together with a 'prepared by' line naming a different one

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- a deliverable that carries the client's branding and no firm marker, which is the normal output of a well-run engagement
- deciding which of two named organisations is the client and which is the firm when no role block exists — §3.8 names this as the problem and it is genuinely a reading
- separating an engagement's working papers from the client's own internal documents collected during it

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10, §4.9):

- 'client'. In the software slice 'client' is a program that talks to a server, and client libraries, client IDs and client-side code are everywhere in a developer's corpus — a bare rule on this word would claim thousands of source files. The law slice also owns `law.client-intake` and the health slice has clinician-patient material described the same way
- 'engagement'. Within THIS slice it means two different things — a consulting engagement and `hr.engagement-survey` — and outside it, social-media engagement and a betrothal. It is the clearest single illustration of why business vocabulary cannot anchor rules
- a company name in a title — §4.9 “A university name alone should not create a group because Columbia can appear as an authoring school, course provider, target institution, employer, research venue, or merely a cited organization” states the reason exactly, and a consulting corpus contains client names, target names, competitor names and comparator names on the same slide
- 'deliverable' | 'workplan' | 'findings' | 'recommendations' — every consultancy document has all four and so does every audit, dissertation and inspection report
- 'prepared for' alone — it appears on tenders, grant applications and student submissions

### Work types

`proposal`, `engagement letter or statement of work`, `workplan`, `working papers`, `interim deliverable`, `final report`, `presentation pack`, `closing note`, `client data received`

### Grouping reasons (§4)

- one engagement across its proposal, letter, workplan, papers and report — §3.9's “The documents are content-incoherent but purpose-coherent” is the reason a model, a deck and an interview note belong together
- one client across the engagements delivered for them

### Template (§5)

`client → engagement → deliverable type`

Time first: **no**

§5.5: “a parent dimension should provide the context required to understand the child” — an engagement is meaningless without its client and a deliverable is meaningless without its engagement. §5.5's “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders” puts the client first and no year anywhere, which matters more here than anywhere else in the slice: a client's material must stay together, and a calendar split would scatter one engagement across two folders. §5.4 supplies the precedent for an organisation leading a branch — “a Career template may define company → role or recruiting cycle → document type”.

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| law.matter-file | a legal matter IS a client engagement and the law slice models it in detail. This entry defers entirely where a matter reference, court, statute or legal-advice framing is present; it claims only non-legal professional services | §3.8 “The system must separate roles that happen to contain the same entity type” |
| ops.project | an engagement is a project with a client. Where a client and a firm appear in two distinct role blocks the engagement should lead, because confidentiality follows the client | §3.11 “One file may hold facts from more than one domain without losing information” |
| ops.sourcing-rfp | a proposal to a client is a bid, and a client's RFP sits at the start of an engagement file. Where the user's organisation is responding, the proposal belongs here; where it is issuing, it belongs there | §3.8 “such as authored_by and target_school, or our_firm and client” |
| res.research-agreement | contract research for an industrial sponsor has both a client and a project. The research slice's stage, lab and venue fields are the discriminator | §3.11 “Research files may use project, stage, artifact type, lab, and venue” |
| career.consulting-engagement | a third entry for the same domain: the career slice models a delivered piece of work for a client where the firm and the client are separate parties, templated client then engagement then deliverable — which is this entry's template exactly. §3.8's role pair is cited by both | §3.8 “such as authored_by and target_school, or our_firm and client” |
| studio.client-engagement | and a fourth: the creative slice models client work templated client then project then deliverable then round. Its discriminator is a creative brief and a revision round; this entry's is an engagement letter and working papers. The overlap is nonetheless substantial | §3.11 “One file may hold facts from more than one domain without losing information” |
| med.practice-administration | an accountancy, architecture or clinical practice runs client engagements with the same shape under other slices' vocabularies; this entry should not claim files carrying their domain terms | §3.8 “The system must separate roles that happen to contain the same entity type” |

### Sensitivity

`potentially_sensitive` — Client working papers routinely contain the client's own employment, financial and personal material — §8.4's corpus list is “identity documents, account statements, tax records, medical information, legal records, credentials, private correspondence, GPS metadata, employment materials, and educational records” and an engagement file regularly holds several of those categories belonging to a third party. §2.9's phrase is applied on that basis. It is also the clearest case of the commercial-confidentiality question raised on `ops.business-records`. No handling class is assigned; that is P7's (§8.4).

### Open question — Joseph's call, unresolved

> Client data received during an engagement is the sharpest privacy problem in this slice: it is a THIRD PARTY's personal and financial material sitting in the user's corpus, and none of the protections are about the user at all. §8.4 requires privacy be enforced before content reaches a model, and “Paths, complete extracted text, OCR output, file hashes, image EXIF, GPS, user edits, group memberships, and raw sensitive values should remain local”. Whether client-received data should be a distinct domain with its own treatment — rather than a work type inside this one — is Joseph's call, and it is the decision most likely to be regretted if made implicitly. SECOND: this domain is authored THREE times across the catalogue — here, as `career.consulting-engagement` and as `studio.client-engagement` — with near-identical templates. §5.7 names client engagements once; three entries answer it. Which one owns non-creative, non-freelance professional services is a merge decision, not a recognition problem.

---

## `ops.customer-success` — Customer success and account management

Managing an existing customer relationship after the sale — account plans, business reviews, adoption tracking and renewal preparation.

**Provenance:** **proposal** — new here; the design names nothing like it

**Cite:** No design sentence names customer success. §5.7 names “covering common organizational situations such as academic programs, university applications, recruiting processes, client engagements, research workflows, financial records, travel, legal matters, creative projects, software repositories, personal administration, and photo collections” and 'client engagements' is the nearest listed situation, but a consulting engagement is delivered work with a scope and an end, where an account relationship is continuous — so this is an addition rather than an extension. §3.15 “Other domains remain placeholders until user demand and corpus evidence justify detailed templates” permits it.

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `account` | string | Harbourline Group | `validated` | the customer organisation. §3.8's role discipline separates the customer from our own entity and from any partner named in the same review |
| `account_identifier` | string | ACC-4471 | `direct` | §3.13 direct: a labeled account or CRM reference. Decisive where present because customer names collide with supplier and partner names in the same corpus |
| `relationship_stage` | string | renewal preparation | `validated` | onboarding, adoption, expansion, renewal, at-risk, churned |
| `review_period` | string | Q1 FY2026 | `validated` | the period a business review covers. Only validated beside a review-artifact term; the bare quarter token is refused below |
| `account_owner_role` | string | customer success manager | `direct` | §3.13 direct: a labeled owner field. §3.8 “It should avoid using authorship or creator identity as a destination dimension” — never a folder level; §5.7 requires the engine to validate that a proposed template “does not repeat a parent dimension, create meaningless one-child levels, exceed practical depth limits, use an author or organization merely as a collector” |
| `renewal_date` | date | 2026-11-30 | `direct` | §3.13 direct: a labeled renewal or anniversary date |
| `health_state` | string | at risk | `llm_supported` | §3.11 permits “several additional fields used only for search, privacy protection, explanation, or later review”; the judgement a success function exists to make, and it is a sentence or a colour in a deck |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.3, §3.5):

- a customer-review artifact term ('quarterly business review' | 'QBR' | 'account plan' | 'success plan' | 'executive business review' | 'adoption review') co-occurring with a named account or an account-identifier label
- an account-identifier label co-occurring with a renewal or contract-anniversary date label AND a customer name matched on a word boundary
- a success-plan structure — a 'desired outcomes' or 'success criteria' heading together with an 'adoption' or 'usage' heading — co-occurring with a named customer

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- a review deck carrying only the customer's logo and a quarter in the title
- health state, which is the substance and is a judgement
- separating a customer business review from an internal status report about the same account

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10, §4.9):

- 'customer' | 'account' | 'client'. 'Account' is a bank account (finance slice owns several domains built on it), a user account (software slice) and an email account; the collision with `fin.bank-account` is total on that word alone
- 'QBR' | 'business review' — 'review' is the worst token in the slice, as set out on `ops.retrospective-postmortem`
- a quarter token such as 'Q1' — §3.10 “frequently contain numbers that look like years but are course identifiers, version numbers, build numbers, ZIP codes, or other unrelated values”, and it collides with fiscal, academic and calendar quarters simultaneously
- a customer's company name — §4.9 “A university name alone should not create a group because Columbia can appear as an authoring school, course provider, target institution, employer, research venue, or merely a cited organization”: in a working corpus the same company is a customer in one file, a supplier in another and a competitor in a third
- 'renewal' | 'churn' | 'onboarding' — 'onboarding' collides with `hr.onboarding`, with the finance slice's vendor onboarding and with software product onboarding, all within one corpus

### Work types

`account plan`, `quarterly business review deck`, `success plan`, `adoption or usage report`, `escalation record`, `renewal proposal`, `reference or case-study consent`, `handover note`

### Grouping reasons (§4)

- one account across its plans, reviews and escalations
- one review period across the material prepared for it

### Template (§5)

`account → year → document type`

Time first: **no**

§5.5: “a parent dimension should provide the context required to understand the child”. Everything here is meaningless outside its account. §5.5's “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders” puts the account first; the year earns a level below it only because account material recurs on a cadence and accumulates for years. §5.9's warning about a level that “It should warn when a level produces only one child, repeats a concept already expressed in the parent, creates excessive depth, or creates a large number of tiny folders” means the year should collapse for a short relationship.

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| ops.client-engagement | a professional-services firm has both — an account relationship and discrete engagements inside it. The engagement reference routes a file to the engagement entry; a review with no engagement scope belongs here | §3.11 “One file may hold facts from more than one domain without losing information” |
| ops.status-report | a QBR is a status report pointed outward. The external audience and the account reference are the separators | §3.8 “The system must separate roles that happen to contain the same entity type” |
| ops.support-operations | an escalation exists as a support case and as an account event. A case or ticket reference routes it to support; an account plan context routes it here | §3.7 “It should rank candidate matches instead of accepting the first match” |
| ops.contract-administration | renewal dates sit in both a contract register and an account plan. The contract reference is the separator | §3.11 “One file may hold facts from more than one domain without losing information” |

### Sensitivity

`none` — Account management material carries no category §2.9 names. Where a review embeds a customer's user list or contact data, §2.9's requirement that contact formats be privacy-protected rather than used to create folder proposals applies to that content. No handling class is assigned; that is P7's (§8.4).

---

## `ops.support-operations` — Customer support operations

Running support for customers — case and ticket records, service-level reporting, knowledge-base content and escalation procedures.

**Provenance:** **proposal** — new here; the design names nothing like it

**Cite:** No design sentence names support operations. §3.15 “Other domains remain placeholders until user demand and corpus evidence justify detailed templates” permits the addition. The software slice's `soft.helpdesk-ticket` owns INTERNAL IT support and `soft.issue-ticket-export` owns engineering issue trackers; this entry is the customer-facing function and the boundary between them is thin — see the collision.

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `case_reference` | string | CASE-118402 | `direct` | §3.13 direct: a labeled case or ticket number. Without it a support record is unplaceable, which is why it leads the recognition |
| `customer_organisation` | string | Harbourline Group | `validated` | who raised it. §3.8's role discipline separates the customer from our own support organisation |
| `support_channel` | string | email | `validated` | email, portal, telephone, chat. §2.9 gives email its structured evidence shape, and a support mailbox export is the most common form this domain takes |
| `case_state` | string | resolved | `validated` | open, pending, escalated, resolved, closed — a labeled field in every ticketing export |
| `service_level_target` | string | priority two response | `validated` | the SLA class claimed. §3.3 forbids the catalogue holding the numeric target itself; the class label is the fact |
| `resolution` | string | configuration corrected on the customer's tenant | `llm_supported` | the substance and always prose |
| `product_or_service` | string | despatch portal | `validated` | what the case is about — the link to product material and the second grouping dimension |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.3, §3.5):

- a case-reference label ('case number' | 'ticket ID' | 'reference' in a support header) co-occurring with a case-state field AND a customer organisation name matched on a word boundary
- a ticket-export structure — case reference, opened date, state and requester as sibling column headings — which §2.9's spreadsheet evidence shape (“should yield workbook or file metadata, sheet names, column headers, visible cell values, table-like regions, formulas only when useful, and dates or identifiers from labeled cells”) makes readable
- a service-level reporting term ('service level report' | 'SLA performance' | 'first response time' | 'backlog by priority') co-occurring with a named customer or service

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- a support email thread with no case reference in the subject
- resolution text, which is prose
- deciding whether a ticket is a customer support case, an internal IT request or an engineering issue — three domains across two slices with one artifact shape

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10, §4.9):

- 'ticket' | 'case' | 'issue' | 'support' | 'incident'. A concert ticket and a flight ticket (personal slice), a legal case (law slice), a clinical case (health slice), a use case, a test case, an issue of a journal (research slice) and a software issue (software slice) all match. This is a five-slice collision on four separate words
- 'priority' | 'P1' | 'severity' — the software slice's incident material uses the same labels
- 'resolved' | 'closed' | 'open' — state words shared with every tracker in every domain
- an email file — §2.9 requires email be handled “treating addresses and message content as potentially sensitive” and a mailbox holds every domain at once
- a customer name — §4.9 “A university name alone should not create a group because Columbia can appear as an authoring school, course provider, target institution, employer, research venue, or merely a cited organization”

### Work types

`case record`, `ticket export`, `SLA or service report`, `escalation record`, `knowledge-base article`, `macro or canned response`, `support playbook`, `customer communication log`

### Grouping reasons (§4)

- one case across its correspondence, attachments and resolution
- one customer across a reporting period's cases
- one product area across the knowledge-base content written for it

### Template (§5)

`product or service → document type → period`

Time first: **no**

§5.5: “a parent dimension should provide the context required to understand the child”. Individual cases are too numerous to be folders — §5.9 warns against a level that “It should warn when a level produces only one child, repeats a concept already expressed in the parent, creates excessive depth, or creates a large number of tiny folders” and a per-case level is that failure at scale — so the durable dimensions are the product and the artifact type, with exports filed by period. §5.5's “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders” keeps the period last.

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| soft.helpdesk-ticket | the software slice owns internal IT support. The separating signal is whether the requester is an employee of the user's own organisation or an external customer — which a ticket export record does not state. This is the thinnest boundary in the slice and it will misroute | §3.8 “The system must separate roles that happen to contain the same entity type” |
| soft.issue-ticket-export | an escalated support case becomes an engineering issue and the two exports look identical. A repository, component or build reference routes it to the software slice | §3.11 “Code files may use project, repository, programming language, and artifact type” |
| ops.customer-success | an escalation is a support case and an account event. The case reference routes it here | §3.7 “It should rank candidate matches instead of accepting the first match” |
| soft.user-documentation | a knowledge-base article is user documentation. Where the artifact is published product documentation rather than support-authored content the software slice leads; in practice one team writes both | §3.11 “One file may hold facts from more than one domain without losing information” |

### Sensitivity

`potentially_sensitive` — Support records are correspondence with named individuals and routinely carry their contact details, account identifiers and, in attachments, whatever the customer sent. §2.9 requires email material be handled “treating addresses and message content as potentially sensitive”, and §8.4 requires that “Paths, complete extracted text, OCR output, file hashes, image EXIF, GPS, user edits, group memberships, and raw sensitive values should remain local”. The marking is made on personal-data grounds — the personal data is a third party's, not the user's. No handling class is assigned; that is P7's (§8.4).

---

## `ops.partnerships-bd` — Partnerships and business development

Building commercial relationships that are not yet customers — partner development, alliances, outbound proposals and the pursuit of new work.

**Provenance:** **proposal** — new here; the design names nothing like it

**Cite:** No design sentence names partnerships or business development. §3.15 “Other domains remain placeholders until user demand and corpus evidence justify detailed templates” permits the addition. It also absorbs the supplier-side mirror of `ops.sourcing-rfp` — proposals the user's organisation SUBMITS — which is a compromise flagged as an open question on that entry.

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `counterparty_organisation` | string | Vellum Systems | `validated` | the other organisation. §3.8 “such as authored_by and target_school, or our_firm and client” — recording our side separately is what keeps a partnership file from becoming a pile of company names |
| `our_entity` | string | Northwind Logistics Ltd | `validated` | our side, for the same reason |
| `relationship_type` | string | reseller partnership | `validated` | reseller, referral, technology alliance, joint venture, prospect, pursuit |
| `pursuit_stage` | string | proposal submitted | `validated` | qualification, discovery, proposal, negotiation, won, lost. The stage is what distinguishes several near-identical documents about the same organisation |
| `pursuit_reference` | string | PUR-2026-088 | `direct` | §3.13 direct: a labeled opportunity or pursuit code where a CRM is in use |
| `outcome` | string | not progressed | `llm_supported` | won, lost, stalled. It is what a user searches an old pursuit for and it is a sentence |
| `partnership_scope` | string | Benelux distribution | `llm_supported` | §3.11 permits “several additional fields used only for search, privacy protection, explanation, or later review”; the shape of the deal, in prose |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.3, §3.5):

- a partnership-artifact term ('memorandum of understanding' | 'partner agreement' | 'referral agreement' | 'letter of intent' | 'heads of terms' | 'joint go-to-market') co-occurring with two distinct organisation names in separate party roles
- a pursuit-tracking term ('opportunity' | 'pursuit' | 'pipeline stage' | 'win theme' | 'bid/no bid') co-occurring with a named counterparty AND a stage label
- an outbound-proposal front block — a 'prepared for' line naming a prospect together with a 'prepared by' line naming our entity AND a validity or expiry statement

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- an exploratory deck or note about a company that may be a partner, a competitor or an acquisition target — a distinction that only prose carries
- outcome, which usually lives in a later email rather than the document
- separating business development material from marketing collateral reused inside it

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10, §4.9):

- 'partner' | 'partnership'. A law firm partner and a limited partnership (law and finance slices), a domestic partner (personal slice), a research partner and a training partner all match
- 'pipeline'. A sales pipeline, a recruiting pipeline (`hr.recruiting-pipeline`, in this very slice), a CI/CD pipeline and a data pipeline (`soft.data-pipeline` is a named domain) — the software slice would be claimed outright
- 'opportunity' | 'lead' | 'prospect' | 'deal' — 'lead' is also a metal, a verb and a role; 'deal' appears in the law slice's `law.transactional-deal`
- 'MOU' | 'LOI' | 'heads of terms' — closer to specific, but these are legal instruments and the law slice has the stronger claim on the executed versions
- a company name — §4.9 “A university name alone should not create a group because Columbia can appear as an authoring school, course provider, target institution, employer, research venue, or merely a cited organization”, which names 'merely a cited organization' as one of the readings, and a BD corpus is mostly companies cited in passing

### Work types

`partner or prospect research note`, `capability deck`, `outbound proposal`, `memorandum of understanding`, `heads of terms`, `pursuit plan`, `win/loss review`, `partner enablement pack`

### Grouping reasons (§4)

- one counterparty across the material produced while pursuing them
- one pursuit across its qualification, proposal, negotiation and outcome

### Template (§5)

`counterparty organisation → pursuit → document type`

Time first: **no**

§5.5: “a parent dimension should provide the context required to understand the child”. A proposal is meaningless without knowing who it went to. §5.5's “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders” keeps years out because a pursuit spans them. §5.7 requires the engine to validate that a proposed template “does not repeat a parent dimension, create meaningless one-child levels, exceed practical depth limits, use an author or organization merely as a collector” — the counterparty level must be a party to a relationship, not every organisation the corpus mentions, which is exactly the trap here.

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| ops.sourcing-rfp | the same tender is a buying event for one organisation and a pursuit for the other. Which entry claims a file depends entirely on which side the user is on, and the document does not say | §3.8 “such as authored_by and target_school, or our_firm and client” |
| corp.fundraising-investor | an investor pitch and a partner pitch are the same deck with a different audience. A round label, term sheet or investor vocabulary routes it to the finance slice | §3.8 “The system must separate roles that happen to contain the same entity type” |
| law.transactional-deal | an executed MOU or partner agreement is an instrument and belongs to those entries. This one holds the pursuit around it | §3.11 “One file may hold facts from more than one domain without losing information” |
| ops.market-competitive-research | research on a company is done both to compete with it and to partner with it, and the note is the same note. Only the surrounding purpose separates them | §3.9 “The documents are content-incoherent but purpose-coherent” |

### Sensitivity

`none` — Business development material carries no category §2.9 names. It is commercially sensitive before announcement, which is the separate question raised on `ops.business-records`. No handling class is assigned; that is P7's (§8.4).

---

## `ops.market-competitive-research` — Market and competitive research

Investigation of a market, its customers and its competitors, done to inform a commercial decision rather than to produce knowledge.

**Provenance:** **proposal** — new here; the design names nothing like it

**Cite:** No design sentence names market research. Research IS a design-named domain, but §3.11 gives it the fields “Research files may use project, stage, artifact type, lab, and venue” — project, stage, artifact type, lab and venue — and a market study has none of them, which is why this is an addition rather than an extension of that domain. §3.15 “Other domains remain placeholders until user demand and corpus evidence justify detailed templates” permits it.

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `market` | string | UK third-party logistics | `validated` | the market studied. This is the grouping key and it is what makes a competitor profile findable |
| `subject_organisation` | string | Vellum Systems | `validated` | the company profiled. §3.8's role discipline is essential: this is the SUBJECT of the study, not its author and not our own entity |
| `study_type` | string | competitor profile | `validated` | market sizing, competitor profile, customer segmentation, win/loss analysis, landscape scan |
| `source_type` | string | published industry report | `validated` | first-party research, purchased report, public sources. It decides whether the file may be shared and whether it is even the user's to keep |
| `study_date` | date | 2026-02-15 | `direct` | §3.13 direct: a labeled publication or as-at date. Market research decays and the date is the fact that says whether it is still usable |
| `commissioning_unit` | string | Strategy | `validated` | who asked for it. §3.8 “It should avoid using authorship or creator identity as a destination dimension” — metadata |
| `finding` | string | two entrants took share in the mid-market | `llm_supported` | §3.11 permits “several additional fields used only for search, privacy protection, explanation, or later review”; findings are prose and never folder levels |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.3, §3.5):

- a market-research artifact term ('market sizing' | 'total addressable market' | 'competitive landscape' | 'competitor profile' | 'market share analysis' | 'win/loss analysis') co-occurring with a named market or a named subject organisation
- a purchased-report front matter block — a research house name together with a licence or 'single user licence' statement AND a publication date label
- a battlecard structure — a competitor name heading together with 'strengths' and 'how we win' or 'objection handling' headings

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- a saved article or downloaded PDF whose market-research character has to be read from content
- distinguishing research done to compete with a company from research done to partner with or acquire it — identical documents, different purposes
- findings, which are prose

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10, §4.9):

- 'research'. The research slice is an entire design-named domain built on the word and has forty entries; a bare rule here would claim all of them. This entry must always carry a market or commercial vocabulary beside it
- 'analysis' | 'study' | 'report' | 'insights' | 'landscape' — ordinary words shared with academic, clinical and financial material
- 'market' — a stock market (finance slice), a farmers' market, a marketing document, a job market
- a competitor's company name — §4.9 “A university name alone should not create a group because Columbia can appear as an authoring school, course provider, target institution, employer, research venue, or merely a cited organization” names 'merely a cited organization', and a competitor profile is a document about a company the user has no relationship with, which is the hardest case of all
- 'TAM' | 'SAM' | 'SOM' | 'CAGR' — thin acronyms that also appear in finance coursework

### Work types

`market sizing model`, `competitor profile`, `battlecard`, `purchased industry report`, `customer segmentation`, `win/loss analysis`, `landscape scan`, `primary research summary`

### Grouping reasons (§4)

- one market across the studies made of it
- one competitor across the profiles and battlecards written about them

### Template (§5)

`market → study type → year`

Time first: **no**

§5.5: “a parent dimension should provide the context required to understand the child”. A competitor profile is only meaningful inside its market. The year earns a level here where it does not elsewhere in the slice, because market research is superseded rather than amended and a user genuinely asks how old it is — but §5.5's “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders” still puts it last.

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| res.reading-library | the research slice owns research. A saved industry PDF and a saved academic paper are the same artifact in a Downloads folder. Project, stage, lab and venue route a file to that slice; a market or competitor vocabulary routes it here, and where neither is present the file belongs to their reading-library entry | §3.11 “Research files may use project, stage, artifact type, lab, and venue” |
| ops.user-research | customer segmentation is market research and user research at once. The separating signal is whether the subject is a market or a product's users | §3.11 “One file may hold facts from more than one domain without losing information” |
| ops.partnerships-bd | a company profile serves competition and partnership equally; only purpose separates them | §3.9 “The documents are content-incoherent but purpose-coherent” |
| ops.pricing | competitor price benchmarking sits in both. A price list or a pricing model routes it to the pricing entry | §3.7 “It should rank candidate matches instead of accepting the first match” |

### Sensitivity

`none` — Market research carries no category §2.9 names. Purchased reports are frequently licence-restricted, which is a distribution constraint rather than a sensitivity one and is not something this catalogue can express. No handling class is assigned; that is P7's (§8.4).

---

## `ops.pricing` — Pricing and commercial terms

How a product or service is priced — price lists, rate cards, discount structures, pricing models and approvals.

**Provenance:** **proposal** — new here; the design names nothing like it

**Cite:** No design sentence names pricing. §3.15 “Other domains remain placeholders until user demand and corpus evidence justify detailed templates” permits the addition. It is separated from the finance slice's invoice and bookkeeping domains because a price list is a forward commercial decision, not a transaction record.

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `offering` | string | Despatch portal — standard tier | `validated` | what is priced. It is the grouping key and it is what distinguishes two rate cards |
| `price_list_version` | string | 2026 rate card | `validated` | price lists are reissued and superseded, and the version is the fact that says which one applied when |
| `effective_date` | date | 2026-01-01 | `direct` | §3.13 direct: a labeled effective-from field. It is what makes an old price list evidence rather than clutter |
| `currency` | string | GBP | `direct` | §3.13 direct: a labeled currency field or column header. §3.11 permits “several additional fields used only for search, privacy protection, explanation, or later review” |
| `pricing_model` | string | per-seat subscription | `validated` | list, tiered, usage-based, per-seat, time and materials. The model is the structural fact |
| `discount_authority` | string | regional director | `llm_supported` | who may approve a departure from list. §3.8 “It should avoid using authorship or creator identity as a destination dimension” — a role, never a folder level |
| `approval_status` | string | approved for the current year | `llm_supported` | whether a pricing document is a proposal or the live one, which is a sentence |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.3, §3.5):

- a pricing-artifact term ('price list' | 'rate card' | 'pricing schedule' | 'discount matrix' | 'list price' | 'pricing approval') co-occurring with a named offering AND an effective-date or version label
- a rate-card structure — an offering or SKU column together with a unit-of-measure column and a price column — co-occurring with a currency label and an organisation name matched on a word boundary

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- a pricing model workbook whose purpose has to be read from its assumptions tab
- approval status and discount authority, both prose
- separating an internal price list from a quotation issued to one customer, which carries the same numbers

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10, §4.9):

- 'price' | 'pricing' | 'cost' | 'rate' | 'quote'. A shopping receipt (personal slice), a quotation received from a supplier (finance slice's `biz.procurement-po`), an insurance quote, an exchange rate and a heart rate all match
- a currency amount — the finance slice names this as the single most over-firing pattern in its own material and it is worse here, because a price list is nothing but currency amounts
- 'discount' | 'tier' | 'SKU' — 'tier' is also an analysis tier in this very product
- a spreadsheet of numbers — §2.9's spreadsheet shape (“should yield workbook or file metadata, sheet names, column headers, visible cell values, table-like regions, formulas only when useful, and dates or identifiers from labeled cells”) is shared with budgets, models and registers
- an effective date — leases, insurance policies and contracts all carry one

### Work types

`price list or rate card`, `pricing model`, `discount matrix`, `pricing approval`, `quotation template`, `commercial terms sheet`, `price change notification`

### Grouping reasons (§4)

- one offering across its successive price lists
- one pricing decision across its model, approval and published list

### Template (§5)

`offering → price list version → document type`

Time first: **no**

§5.5: “a parent dimension should provide the context required to understand the child”. A version is meaningless without knowing what it prices. §5.5's “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders” keeps the effective year out of the upper levels, because a user looks for an offering's price history as one thread.

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| biz.invoice-issued | an invoice applies a price; the price list sets it. Anything with an invoice number, a payment term or a tax line is the finance slice's | §3.11 “One file may hold facts from more than one domain without losing information” |
| biz.procurement-po | a supplier's quotation is a price list from the other side. The buyer/seller role is the separator and §3.8's role discipline is what expresses it | §3.8 “The system must separate roles that happen to contain the same entity type” |
| ops.go-to-market | pricing is a launch decision and appears inside GTM packs. Where the file is the rate card itself it belongs here | §3.7 “It should rank candidate matches instead of accepting the first match” |
| ops.partnerships-bd | a partner rate card and a customer rate card differ only in audience | §3.9 “The documents are content-incoherent but purpose-coherent” |

### Sensitivity

`none` — Pricing material carries no category §2.9 names. Customer-specific discount schedules are among the most commercially sensitive documents an organisation holds, which is the separate question raised on `ops.business-records`. No handling class is assigned; that is P7's (§8.4).

---

## `ops.product-roadmap` — Product roadmaps and release planning

The forward plan for a product — themes, sequenced releases and the communications built from them.

**Provenance:** **proposal** — new here; the design names nothing like it

**Cite:** No design sentence names product management. §3.11 gives Code files “Code files may use project, repository, programming language, and artifact type” — project, repository, programming language and artifact type — which is the software slice's territory and not a roadmap's. §3.15 “Other domains remain placeholders until user demand and corpus evidence justify detailed templates” permits this addition.

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `product` | string | Despatch portal | `validated` | the product. It is the grouping key for this and for `ops.product-requirements`, and it is what ties both to the software slice's repositories |
| `roadmap_horizon` | string | FY2026 H1 | `validated` | the period covered. Only validated beside a roadmap-artifact term |
| `theme` | string | self-service onboarding | `llm_supported` | the grouping a roadmap uses instead of features. Prose, and never a folder level, because themes are renamed every cycle |
| `release` | string | 2026.2 | `validated` | the named release a roadmap item targets. This is the join to the software slice's release notes |
| `roadmap_audience` | string | customer-facing | `llm_supported` | internal, customer-facing, board. The same roadmap exists in three edited versions and the audience is the only difference — it decides whether the file may be shared |
| `commitment_level` | string | planned, not committed | `llm_supported` | §3.11 permits “several additional fields used only for search, privacy protection, explanation, or later review”; whether a roadmap item is a commitment matters commercially and is always hedged in prose |
| `product_owner_role` | string | product manager | `direct` | §3.13 direct: a labeled owner field. §3.8 “It should avoid using authorship or creator identity as a destination dimension” |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.3, §3.5):

- a roadmap-artifact term ('product roadmap' | 'release plan' | 'now next later' | 'roadmap theme') co-occurring with a named product AND a horizon or release label
- a roadmap structure — three or more period column headings carrying a horizon vocabulary ('now' | 'next' | 'later', or consecutive quarter labels) — co-occurring with a named product

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- a planning deck that is a roadmap in substance without using the word
- audience and commitment level, which are the two facts that matter commercially and are both readings
- separating a product roadmap from a delivery schedule for the same work

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10, §4.9):

- 'roadmap'. A research roadmap, a technology roadmap (software slice), a learning roadmap (education slice), a personal career roadmap and a strategy roadmap all match; the word is borrowed everywhere
- 'release' | 'launch' | 'version' | 'sprint'. The software slice has `soft.release-notes-changelog` and a release is a code artifact there; §3.1 also makes version family a universal file fact
- 'now' | 'next' | 'later' | 'Q1' — column words and a quarter token; §3.10 “frequently contain numbers that look like years but are course identifiers, version numbers, build numbers, ZIP codes, or other unrelated values”
- 'product' — a product review, a product photograph (personal slice's residual One-Off Images case in §7.3), a product manual
- 'theme' — also a visual theme in the creative and software slices

### Work types

`product roadmap`, `release plan`, `roadmap deck`, `theme definition`, `customer-facing roadmap`, `roadmap change note`, `prioritisation input`

### Grouping reasons (§4)

- one product across its successive roadmaps
- one release across the plan, its scope and its communications

### Template (§5)

`product → roadmap horizon → document type`

Time first: **no**

§5.5: “a parent dimension should provide the context required to understand the child”. A horizon is meaningless without the product. §5.5's “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders” keeps the product first so that its planning history reads as one sequence, which is the whole value of keeping superseded roadmaps at all.

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| soft.release-notes-changelog | a release plan and release notes name the same release. The software slice's entry is the record of what shipped; this one is the plan for what will. A repository, build or commit reference routes a file there | §3.11 “Code files may use project, repository, programming language, and artifact type” |
| ops.product-requirements | a roadmap item becomes a PRD and the two are often one document. A requirements structure — user stories, acceptance criteria — routes it to the requirements entry | §3.11 “One file may hold facts from more than one domain without losing information” |
| ops.strategy-plan | a product strategy is both. The roadmap's sequenced, period-columned structure is the separator | §3.7 “It should rank candidate matches instead of accepting the first match” |
| ops.go-to-market | a customer-facing roadmap is a GTM artifact. The audience field is the separator and it is `llm_supported`, so this boundary will be resolved by the model or not at all | §3.9 “The documents are content-incoherent but purpose-coherent” |

### Sensitivity

`none` — Roadmaps carry no category §2.9 names. An unreleased roadmap is commercially sensitive, which is the separate question raised on `ops.business-records`. No handling class is assigned; that is P7's (§8.4).

---

## `ops.product-requirements` — Product requirements and specifications

What a product should do and why — requirements documents, user stories, acceptance criteria and the decisions behind them.

**Provenance:** **proposal** — new here; the design names nothing like it

**Cite:** No design sentence names product requirements. The software slice already owns `soft.technical-specification`, `soft.design-doc-rfc` and `soft.architecture-decision-record`, which are the implementation-side artifacts; this entry is the problem-side one. §3.15 “Other domains remain placeholders until user demand and corpus evidence justify detailed templates” permits it and the boundary is acknowledged as thin below.

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `product` | string | Despatch portal | `validated` | which product. Shared with `ops.product-roadmap` deliberately — they are two artifacts about one thing |
| `feature_or_capability` | string | bulk label printing | `validated` | what is being specified. It is the grouping key and it is normally the document title |
| `requirement_type` | string | functional | `validated` | functional, non-functional, constraint, acceptance criterion |
| `specification_status` | string | approved for build | `validated` | draft, in review, approved, superseded, descoped. It is a labeled field in most templates and it is what separates four versions of one document |
| `stakeholder_role` | string | operations lead | `llm_supported` | whose need the requirement expresses. §3.8 “It should avoid using authorship or creator identity as a destination dimension” — metadata only |
| `linked_artifact` | string | issue tracker epic reference | `direct` | §3.13 direct: a labeled ticket or epic reference. It is the join to the software slice and it is the strongest corroborating signal this domain has |
| `rationale` | string | manual printing is the top support driver | `llm_supported` | §3.11 permits “several additional fields used only for search, privacy protection, explanation, or later review”; the why, which is the part that survives and is prose |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.3, §3.5):

- a requirements-artifact term ('product requirements document' | 'PRD' | 'user story' | 'acceptance criteria' | 'functional requirement' | 'non-functional requirement') co-occurring with a named product or feature
- a user-story structure — an 'as a ... I want ... so that' pattern — co-occurring with an acceptance-criteria heading and a named product
- a requirements table — a requirement-identifier column together with a priority or must/should/could column — co-occurring with a named product

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- a feature description written as a memo with no requirements structure
- rationale, which is the durable part and is prose
- deciding whether a specification is a product requirement or a technical design, which is the boundary with the software slice and is genuinely a judgement about the document's audience

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10, §4.9):

- 'requirements'. Degree requirements and entry requirements (education slice), visa requirements (finance slice's `admin.immigration`), grant requirements (research slice), system requirements and a requirements.txt file (software slice — a literal filename) all match. The last is a genuine filename collision, not a hypothetical one
- 'specification' | 'spec'. The software slice has `soft.technical-specification` and `soft.api-specification`; a spec sheet for a piece of equipment sits in the personal and research slices
- 'PRD' — thin, and it collides with unrelated three-letter tokens; §3.7 “It should use word-boundary matching rather than substring matching” helps but the acronym is not distinctive
- 'user story' | 'epic' | 'backlog' — the software slice's issue-tracker material uses all three
- 'must' | 'should' | 'could' — RFC-style requirement keywords appear in every standard and policy document

### Work types

`product requirements document`, `user story set`, `acceptance criteria`, `feature brief`, `product decision record`, `scope change note`, `prototype or wireframe reference`

### Grouping reasons (§4)

- one feature across its brief, requirements, decisions and acceptance criteria
- one product across the requirements written for it in a period

### Template (§5)

`product → feature or capability → document type`

Time first: **no**

§5.5: “a parent dimension should provide the context required to understand the child”. A requirement is meaningless outside its feature and a feature outside its product. §5.5's “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders” keeps dates out entirely, which is right because a specification is superseded rather than accumulated.

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| soft.technical-specification | the thinnest boundary this entry has. Both describe a system in structured prose with a status field. The practical separator is whether the document reasons about USERS and outcomes or about components and interfaces — and many documents do both. Where a repository, interface, schema or component reference is present the software slice leads | §3.11 “Code files may use project, repository, programming language, and artifact type” |
| soft.issue-ticket-export | user stories live in the tracker and in the PRD. An export routes to the software slice; an authored document routes here | §3.7 “It should rank candidate matches instead of accepting the first match” |
| ops.user-research | requirements cite research findings and often embed them. Where the file's substance is participant evidence it is the research entry's | §3.11 “One file may hold facts from more than one domain without losing information” |
| eng.requirements-specification | the engineering slice owns the document stating what a product, system or component must do and how conformance will be shown. That is a PRD in every respect except that its subject is a physical item; a specified-item, tolerance or verification reference routes a file there | §3.6 “that each fact or label belongs to an allowed domain schema” |
| ops.product-roadmap | a roadmap item and a PRD frequently share a title. The requirements structure is the separator | §3.7 “It should rank candidate matches instead of accepting the first match” |

### Sensitivity

`none` — Requirements documents carry no category §2.9 names. Where one quotes research participants verbatim the personal-data reading applies to that content and `ops.user-research` marks it. No handling class is assigned; that is P7's (§8.4).

---

## `ops.user-research` — User and customer research

Evidence gathered from the people who use a product — interviews, usability sessions, diary studies, surveys and the syntheses built from them.

**Provenance:** **inference** — extends a domain the design does name

**Cite:** Research is a design-named domain and §3.11 gives it “Research files may use project, stage, artifact type, lab, and venue”. This entry extends that named domain to product research, where 'lab' and 'venue' do not apply but project, stage and artifact type do. The research slice's `res.survey-instrument`, `res.qualitative-coding` and `res.human-subjects-consent` are the academic instances of the same artifacts and this entry defers to them wherever their vocabulary appears.

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `study` | string | Bulk printing usability round two | `validated` | the study. §3.11 names `project` and `stage` for research files and a study is the product instance of both |
| `study_method` | string | moderated usability session | `validated` | interview, usability test, diary study, survey, card sort, concept test. §3.11's `artifact_type` for research files is the nearest named analogue |
| `participant_reference` | string | P07 | `direct` | §3.13 direct: a labeled participant code. Note the code, never the name — §8.4 requires that “Paths, complete extracted text, OCR output, file hashes, image EXIF, GPS, user edits, group memberships, and raw sensitive values should remain local” and a participant's identity is exactly that |
| `product` | string | Despatch portal | `validated` | what was studied — the join to `ops.product-requirements` |
| `session_date` | date | 2026-03-04 | `direct` | §3.13 direct: a labeled session date |
| `finding` | string | users did not find the bulk action | `llm_supported` | the substance; prose, and §3.6 requires the model cite the exact span |
| `consent_status` | string | recorded consent held | `validated` | whether consent covers retention and sharing. It is the fact that decides how the file may be treated and it is normally a labeled field on a consent form |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.3, §3.5):

- a research-session artifact term ('discussion guide' | 'usability test plan' | 'interview protocol' | 'research debrief' | 'affinity map' | 'participant screener') co-occurring with a named product or study
- a participant-code pattern co-occurring with a session-date label AND a study or product name — the code alone is refused below
- a consent artifact — a 'consent to record' or 'research participation consent' term co-occurring with a study name and an organisation name matched on a word boundary

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- a raw transcript with no header
- findings and synthesis, which are the point of the domain and entirely prose
- separating product user research from academic human-subjects research, which share every artifact type and differ only in institution and ethics vocabulary

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10, §4.9):

- 'research' — as on `ops.market-competitive-research`, the research slice is forty entries built on this word
- 'interview'. This is the specific hazard here: a job interview (`hr.interview-panel`, in this same slice, and the career slice's candidate side), a journalistic interview, a clinical interview (health slice) and a research interview are one word and four domains — two of them sensitive in different ways
- 'survey' — a land survey, a customer satisfaction survey, an employee engagement survey (`hr.engagement-survey`, again in this slice) and the research slice's `res.survey-instrument`
- a participant code such as 'P07' — a bare alphanumeric token; §3.10 “frequently contain numbers that look like years but are course identifiers, version numbers, build numbers, ZIP codes, or other unrelated values” and this shape collides with page numbers, part numbers and product codes
- 'transcript' — the education slice's `acad.transcript-record` is an academic transcript, a completely different object, and the collision is total on the word
- 'usability' | 'UX' — closer to specific, but they also mark design-craft material in the creative and software slices

### Work types

`discussion guide`, `screener`, `consent form`, `session recording reference`, `transcript`, `notes`, `affinity map or synthesis`, `research report`, `survey instrument`, `survey results`

### Grouping reasons (§4)

- one study across its guide, sessions, transcripts and synthesis
- one product across the studies run on it

### Template (§5)

`product → study → artifact type`

Time first: **no**

§5.5: “a parent dimension should provide the context required to understand the child”. A transcript is meaningless outside its study. §5.5's “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders” keeps session dates below the study, and §5.9's warning about a level that “It should warn when a level produces only one child, repeats a concept already expressed in the parent, creates excessive depth, or creates a large number of tiny folders” means a per-participant level should never be created — which also happens to be the privacy-safe choice.

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| res.human-subjects-consent | the research slice owns the academic instances of every artifact in this entry, with an ethics framework this one does not have. An institution, ethics approval or IRB reference routes a file there and this entry must not claim it — mis-routing would lose their sensitivity treatment | §3.11 “Research files may use project, stage, artifact type, lab, and venue” |
| hr.engagement-survey | an employee survey and a customer survey are the same instrument pointed at different people. The respondent population is the separator and it is rarely stated on the instrument itself | §3.8 “The system must separate roles that happen to contain the same entity type” |
| hr.interview-panel | a recorded interview is a research artifact and a recruiting artifact under the same word. A requisition or candidate reference routes it to the HR entry | §3.8 “The system must separate roles that happen to contain the same entity type” |
| ops.market-competitive-research | segmentation research draws on user research. The subject — a market versus a product's users — is the separator | §3.11 “One file may hold facts from more than one domain without losing information” |

### Sensitivity

`potentially_sensitive` — Transcripts and recordings are a third party's words, held under a consent that usually restricts retention and sharing. §8.4 requires that “Paths, complete extracted text, OCR output, file hashes, image EXIF, GPS, user edits, group memberships, and raw sensitive values should remain local”, and §2.9 requires contact and message material be handled “treating addresses and message content as potentially sensitive”. Recordings also raise §2.9's speech-to-text condition, which the design permits only under an explicit privacy and compute policy. No handling class is assigned; that is P7's (§8.4).

---

## `ops.go-to-market` — Go-to-market and launch planning

The coordinated plan to bring an offering to market — positioning, launch plan, enablement and the readiness checks around a launch date.

**Provenance:** **proposal** — new here; the design names nothing like it

**Cite:** No design sentence names go-to-market planning. §3.15 “Other domains remain placeholders until user demand and corpus evidence justify detailed templates” permits the addition. The creative slice owns the marketing ASSETS produced for a launch; this entry is the plan that commissions them.

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `offering` | string | Despatch portal — bulk printing | `validated` | what is being launched. The grouping key |
| `launch_date` | date | 2026-05-06 | `direct` | §3.13 direct: a labeled launch or general-availability date. It is the fact everything in a GTM folder is organised around |
| `launch_tier` | string | tier two launch | `validated` | the scale of launch, which decides which artifacts exist. A labeled classification in most launch templates |
| `target_segment` | string | mid-market logistics operators | `llm_supported` | who it is for. Prose, and the fact that binds GTM to market research |
| `positioning_statement` | string | the fastest route from order to label | `llm_supported` | §3.11 permits “several additional fields used only for search, privacy protection, explanation, or later review”; the durable output of a launch and always prose |
| `channel` | string | direct sales and partner | `validated` | how it reaches the market — the link to `ops.partnerships-bd` |
| `readiness_status` | string | go | `validated` | go, no-go, conditional. A labeled decision in a readiness review and one of the few structured facts here |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.3, §3.5):

- a launch-artifact term ('go-to-market plan' | 'launch plan' | 'launch readiness' | 'positioning statement' | 'messaging framework' | 'sales enablement pack' | 'launch tier') co-occurring with a named offering
- a readiness structure — a 'go/no-go' or 'launch readiness' heading together with a function-by-function checklist (support, sales, legal, operations) — co-occurring with a launch-date label

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- a launch deck with no launch vocabulary in it
- positioning and segment, both prose
- separating a GTM plan from the marketing campaign brief it commissions

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10, §4.9):

- 'launch'. A product launch, a rocket launch, a book launch, a launch configuration in the software slice and a launch file are one word
- 'GTM' | 'positioning' | 'messaging' — thin acronym and two marketing words that appear in brand, campaign and communications material equally
- 'enablement' | 'readiness' — 'readiness' also appears in continuity, audit and clinical material
- a launch date — §3.10 “frequently contain numbers that look like years but are course identifiers, version numbers, build numbers, ZIP codes, or other unrelated values” and a date alone says nothing
- 'campaign' — the creative slice owns campaign material; an election campaign and a fundraising campaign also match

### Work types

`go-to-market plan`, `positioning and messaging framework`, `launch checklist`, `readiness review`, `sales enablement pack`, `launch communications plan`, `post-launch review`

### Grouping reasons (§4)

- one launch across its plan, positioning, enablement, readiness and post-launch review — §3.9's “The documents are content-incoherent but purpose-coherent” again, since a legal sign-off and a sales deck share no topic
- one offering across its successive launches into new segments

### Template (§5)

`offering → launch → document type`

Time first: **no**

§5.5: “a parent dimension should provide the context required to understand the child”. A readiness checklist is meaningless outside its launch. §5.5's “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders” keeps the launch date inside the launch's name rather than as a level of its own, which is what keeps one launch's material together.

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| media.ad-campaign | a launch commissions creative work and the brief sits in both. The plan is here; the artwork, copy and video are theirs | §3.9 “The documents are content-incoherent but purpose-coherent” |
| ops.product-roadmap | a customer-facing roadmap is a GTM artifact. The audience field decides and it is `llm_supported` | §3.7 “It should rank candidate matches instead of accepting the first match” |
| ops.pricing | pricing is set at launch and the rate card sits in the launch folder. The rate card itself belongs to the pricing entry | §3.11 “One file may hold facts from more than one domain without losing information” |
| ops.internal-comms | launch communications go to staff as well as to market; the audience is the separator | §3.8 “The system must separate roles that happen to contain the same entity type” |

### Sensitivity

`none` — Launch material carries no category §2.9 names. Pre-announcement launch plans are commercially sensitive, which is the separate question raised on `ops.business-records`. No handling class is assigned; that is P7's (§8.4).

---

## `hr.org-design-headcount` — Organisation design and headcount planning

The shape of the workforce as a plan — org charts, structures, headcount and establishment plans, and reorganisation proposals.

**Provenance:** **proposal** — new here; the design names nothing like it

**Cite:** No design sentence names organisation design. §3.15 “Other domains remain placeholders until user demand and corpus evidence justify detailed templates” permits the addition. It is kept separate from `hr.workforce-analytics` because a plan and a measurement are different artifacts with different sensitivity.

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `organisation` | string | Northwind Logistics | `validated` | whose structure it is |
| `org_unit` | string | Distribution | `validated` | the unit designed. It is the grouping key — an org chart is always of something |
| `plan_effective_date` | date | 2026-04-01 | `direct` | §3.13 direct: a labeled effective-from field. It is what distinguishes the current structure from three superseded ones |
| `position_title` | string | regional planner | `validated` | a role in the structure. §3.8 “It should avoid using authorship or creator identity as a destination dimension” is the load-bearing rule here: a structure is made of POSITIONS, and the people occupying them are a separate, sensitive fact |
| `establishment_state` | string | vacant | `validated` | filled, vacant, frozen, proposed. It is the fact that links a structure to a requisition |
| `change_type` | string | reorganisation proposal | `validated` | current state, target state, transition, proposal, consultation |
| `headcount_scope` | string | distribution and planning teams | `llm_supported` | §3.11 permits “several additional fields used only for search, privacy protection, explanation, or later review”; the boundary of a plan is prose. §3.3 forbids this catalogue holding a headcount number as a value |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.3, §3.5):

- an org-design artifact term ('organisation chart' | 'org design' | 'target operating model' | 'establishment list' | 'headcount plan' | 'span of control') co-occurring with a named organisation or unit AND an effective-date or version label
- a position-table structure — a position-title column together with a reporting-line or 'reports to' column and a filled/vacant column — co-occurring with a named unit
- a consultation term ('collective consultation' | 'at-risk pool' | 'selection criteria' | 'redundancy proposal') co-occurring with a named unit — note this variant is the sensitive one and is the reason the whole entry is marked

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- a chart image or drawing whose unit appears only in a title block
- change type, where a document shows a structure without saying whether it is current or proposed — the single most consequential ambiguity in this domain
- headcount scope, which is prose

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10, §4.9):

- 'org chart' | 'organisation' | 'structure' | 'team'. 'Structure' is a data structure (software slice), a molecular structure (research slice) and a building structure; 'team' is a sports team (personal slice)
- 'headcount' | 'FTE' | 'establishment'. 'Establishment' is also a licensed premises and a general noun; 'FTE' appears in every budget in the finance slice
- a hierarchy diagram — a shape, and a family tree (personal slice's `pers.genealogy`), a taxonomy and a decision tree share it exactly
- a list of employee names. §3.8 “It should avoid using authorship or creator identity as a destination dimension”, and §4.9 warns against a group held together “when one high-frequency entity acts as the only bridge” — a manager appearing on every chart is precisely that
- 'reorganisation' | 'restructure' | 'transformation' — the last is corporate filler that appears on a third of business documents

### Work types

`organisation chart`, `target operating model`, `establishment or position list`, `headcount plan`, `reorganisation proposal`, `consultation document`, `selection criteria`, `transition plan`

### Grouping reasons (§4)

- one org unit across its current, target and transition structures
- one reorganisation across its proposal, consultation and final structure

### Template (§5)

`organisation → org unit → plan effective date`

Time first: **no**

§5.5: “a parent dimension should provide the context required to understand the child”. A structure is meaningless without knowing whose it is. §5.5's “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders” puts the effective date last, so a unit's structural history reads in one place rather than being scattered across years.

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| hr.workforce-analytics | a headcount plan and a headcount report use the same table. Forward-looking effective dates and proposed positions route a file here; actuals and trends route it there | §3.7 “It should rank candidate matches instead of accepting the first match” |
| ops.operating-plan-budget | a headcount plan is the people half of a budget and often lives on a tab of the same workbook. A cost-centre-labelled financial table routes the file to the budget entry | §3.11 “One file may hold facts from more than one domain without losing information” |
| hr.job-requisition | a vacant establishment position becomes a requisition. The requisition reference is the separator | §3.7 “It should rank candidate matches instead of accepting the first match” |
| career.layoff-and-severance | an org chart the user appears on is an employment record for them and an HR artifact for the organisation; the file is identical | §3.8 “The system must separate roles that happen to contain the same entity type” |

### Sensitivity

`potentially_sensitive` — Organisation design material at position level names individuals against roles, and reorganisation and consultation documents identify people at risk of losing their jobs. §8.4 names “identity documents, account statements, tax records, medical information, legal records, credentials, private correspondence, GPS metadata, employment materials, and educational records” among the categories the local-first posture exists for. The marking is made on personal-data grounds. No handling class is assigned; that is P7's (§8.4).

---

## `hr.job-requisition` — Job requisitions and role definitions

The employer's definition of a vacancy — the approved requisition, the job description and the advertisement built from them.

**Provenance:** **inference** — extends a domain the design does name

**Cite:** Career and recruiting is a design-named domain and §5.4 gives it a template: “a Career template may define company → role or recruiting cycle → document type”. §5.7 names “covering common organizational situations such as academic programs, university applications, recruiting processes, client engagements, research workflows, financial records, travel, legal matters, creative projects, software repositories, personal administration, and photo collections”, which includes 'recruiting processes', and §4.5 names “one course, project, application, recruiting process, photo event, or submission packet”, which includes a recruiting process as an organizing reason. This entry extends that named domain to the EMPLOYER's side; the candidate's side is the career slice's.

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `requisition_reference` | string | REQ-2026-0142 | `direct` | §3.13 direct: a labeled requisition number. It is the spine of the whole recruiting group and it is what makes an otherwise generic job description placeable |
| `position_title` | string | regional planner | `validated` | the role advertised. §3.8 “It should avoid using authorship or creator identity as a destination dimension” — a role, not a person |
| `hiring_organisation` | string | Northwind Logistics | `validated` | who is hiring. §3.8's role discipline separates the employer from an agency and from a candidate's current employer named in the same folder |
| `org_unit` | string | Distribution | `validated` | where the role sits — the link back to the establishment plan |
| `requisition_status` | string | approved and open | `validated` | draft, approved, open, on hold, filled, cancelled |
| `employment_type` | string | permanent, full time | `validated` | permanent, fixed term, part time, contract |
| `opened_date` | date | 2026-02-10 | `direct` | §3.13 direct: a labeled opening or approval date |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.3, §3.5):

- a requisition-reference label co-occurring with a position title AND a hiring organisation name matched on a word boundary
- a job-description structure — a 'key responsibilities' or 'main duties' heading together with a 'person specification' | 'essential criteria' | 'qualifications required' heading — co-occurring with a named employer
- a job-advertisement block — a 'how to apply' or 'closing date' term together with a named employer and a position title

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- a role description drafted as a memo with no headings
- requisition status, which changes over the life of a file that is not reissued
- separating an employer's job description from the same text pasted into a candidate's own notes, which is the career slice's material

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10, §4.9):

- 'job' | 'role' | 'position' | 'vacancy'. 'Job' is a print job, a batch job and a cron job (software slice); 'position' is a coordinate, a stance and a chess position
- 'job description' — the phrase is also used for the description a person writes of their OWN job in the career slice, and the two documents are word-for-word identical
- 'responsibilities' | 'requirements' | 'qualifications' — see `ops.product-requirements` for why 'requirements' is refused everywhere in this slice
- an employer name — §4.9 “A university name alone should not create a group because Columbia can appear as an authoring school, course provider, target institution, employer, research venue, or merely a cited organization” names 'employer' explicitly among the readings of an organisation name, which makes this entry the design's own worked example of the hazard
- a closing date — §3.10 “frequently contain numbers that look like years but are course identifiers, version numbers, build numbers, ZIP codes, or other unrelated values”

### Work types

`requisition form`, `job description`, `person specification`, `job advertisement`, `approval record`, `recruitment brief`, `agency instruction`

### Grouping reasons (§4)

- one requisition across its approval, description, advertisement and briefing — the requisition reference is the anchor §4.9's stop rules would otherwise require
- one position title across its successive requisitions

### Template (§5)

`hiring organisation → requisition → document type`

Time first: **no**

§5.5: “a parent dimension should provide the context required to understand the child”, and §5.4's own Career row “a Career template may define company → role or recruiting cycle → document type” puts the company first, which this follows. §5.5's “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders” keeps the opening year out, because a requisition's documents span months and would be cut by a calendar level.

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| career.job-posting-collected | the same job description sits in the employer's requisition file and in the applicant's folder beside their CV. Nothing in the document distinguishes the copies; only the surrounding material does | §3.8 “The system must separate roles that happen to contain the same entity type” |
| hr.recruiting-pipeline | the requisition defines the vacancy; the pipeline tracks candidates against it. They share the requisition reference and should stay linked rather than merged | §4.9 “A file may validly belong to more than one accepted group” |
| hr.org-design-headcount | an approved requisition is an establishment decision. The requisition reference is the separator | §3.7 “It should rank candidate matches instead of accepting the first match” |
| career.employer-job-requisition | a straight duplication rather than a boundary: the career slice authored an employer-side requisition entry covering the same artifact, keyed on the same requisition id, and templated as department then requisition id where this one is organisation then requisition. Two catalogue entries competing for one file is the failure §3.6's validator cannot resolve, because both schemas are allowed | §3.6 “that each fact or label belongs to an allowed domain schema” — a fact that belongs to two allowed schemas passes validation twice and is placed twice |
| hr.compensation-planning | a requisition carries a salary range, which is compensation material. Where the range is the document's substance the compensation entry leads | §3.11 “One file may hold facts from more than one domain without losing information” |

### Sensitivity

`none` — A job description and an advertisement are written to be published and carry nothing §2.9 names. The approval record naming an approver and a salary range is employment material — §8.4's “identity documents, account statements, tax records, medical information, legal records, credentials, private correspondence, GPS metadata, employment materials, and educational records” — and is handled by `hr.compensation-planning`. No handling class is assigned; that is P7's (§8.4).

### Open question — Joseph's call, unresolved

> FOUR entries in this catalogue duplicate four in the career slice rather than bordering them. `hr.job-requisition` / `career.employer-job-requisition`, `hr.recruiting-pipeline` / `career.employer-candidate-packet`, `hr.interview-panel` / `career.employer-interview-scorecard` and `hr.offer-package` / `career.employer-offer-approval` describe the same artifacts, key on the same requisition id, and differ only in whether the organisation or the requisition leads the template. This is not a boundary that better recognition would sharpen — it is one domain authored twice, and §3.6 “that each fact or label belongs to an allowed domain schema” cannot arbitrate it, because a fact belonging to two allowed schemas passes validation in both. Either the career slice keeps employer-side recruiting and this catalogue drops these four, or the reverse; the split cannot stand. This slice does not resolve it unilaterally because the two were authored in parallel and neither author has standing over the other. It is Joseph's, and it should be settled at merge.

---

## `hr.recruiting-pipeline` — Recruiting pipeline and candidate tracking (employer side)

The employer's view of who is applying and where they are in the process — pipeline reports, candidate lists, screening records and sourcing activity.

**Provenance:** **inference** — extends a domain the design does name

**Cite:** Career and recruiting is design-named; §5.7's list includes 'recruiting processes' — “covering common organizational situations such as academic programs, university applications, recruiting processes, client engagements, research workflows, financial records, travel, legal matters, creative projects, software repositories, personal administration, and photo collections” — and §4.5 names “one course, project, application, recruiting process, photo event, or submission packet”. This entry extends that named domain to the employer's side. The design's own examples run the other way: §4.5's worked label is a career packet EY Internship Application, which is a CANDIDATE's file.

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `requisition_reference` | string | REQ-2026-0142 | `direct` | §3.13 direct: the vacancy the pipeline is for. Everything here hangs off it |
| `pipeline_stage` | string | second interview | `validated` | applied, screened, interviewing, offer, hired, rejected, withdrawn |
| `candidate_reference` | string | CAND-88213 | `direct` | §3.13 direct: a labeled candidate identifier. The identifier, not the name — §8.4 requires that “Paths, complete extracted text, OCR output, file hashes, image EXIF, GPS, user edits, group memberships, and raw sensitive values should remain local” and a candidate's identity is third-party personal data |
| `source_channel` | string | agency | `validated` | direct, agency, referral, job board. It is the fact recruiting reporting is built on |
| `hiring_organisation` | string | Northwind Logistics | `validated` | who is hiring; §3.8's role discipline separates the employer from a candidate's current employer and from the agency |
| `report_period` | string | February 2026 | `validated` | the period a pipeline report covers |
| `screening_outcome` | string | progressed to interview | `llm_supported` | why someone moved or did not. It is a judgement written in prose about a named person, which is the most sensitive content in this domain |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.3, §3.5):

- a requisition reference co-occurring with a pipeline-stage vocabulary ('applied' | 'screened' | 'shortlisted' | 'offer extended' | 'candidate withdrawn') AND a candidate-count or candidate-list structure
- an applicant-tracking export structure — candidate reference, requisition reference and stage as sibling column headings — which §2.9's spreadsheet evidence shape (“should yield workbook or file metadata, sheet names, column headers, visible cell values, table-like regions, formulas only when useful, and dates or identifiers from labeled cells”) makes readable
- an agency submission block — an agency name together with a requisition reference and a 'submitted candidate' or 'introduction' term

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- a screening note written as an email with no structure
- screening outcomes, which are judgements in prose
- separating an employer's candidate list from a jobseeker's own application tracker, which is the career slice's and has the same columns

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10, §4.9):

- 'pipeline'. `soft.data-pipeline` is a named domain in the software slice, CI/CD pipelines are everywhere in a developer's corpus, and `ops.partnerships-bd` in this very slice has a sales pipeline. Three domains, one word
- 'candidate' — a candidate in an election, a candidate gene (research slice), a candidate match in this product's own vocabulary
- 'applied' | 'screened' | 'shortlisted' | 'rejected' — stage words shared with grant applications (research slice), university applications (education slice) and planning applications
- a list of personal names. §3.8 “It should avoid using authorship or creator identity as a destination dimension” and §8.4 requires personal values stay local; a name list is also the single most over-firing structure in a corpus
- 'recruitment' | 'hiring' | 'talent' — 'talent' is also a creative-industry term

### Work types

`pipeline report`, `candidate list or ATS export`, `screening note`, `agency submission`, `sourcing plan`, `recruitment metrics report`, `interview schedule`

### Grouping reasons (§4)

- one requisition across its pipeline, screening records and reporting
- one recruiting period across the pipeline reports produced for it

### Template (§5)

`hiring organisation → requisition → document type`

Time first: **no**

§5.5: “a parent dimension should provide the context required to understand the child”. Pipeline material is meaningless outside its requisition. §5.9's warning about a level that “It should warn when a level produces only one child, repeats a concept already expressed in the parent, creates excessive depth, or creates a large number of tiny folders” is why there is no per-candidate level — which is also the privacy-safe choice, since a folder named after a rejected applicant would be the worst possible output of this product.

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| career.job-search-campaign | a jobseeker's application tracker and an employer's pipeline report are the same spreadsheet with the roles inverted. The requisition reference and the hiring-organisation role are the only separators, and a small employer's informal list has neither | §3.8 “The system must separate roles that happen to contain the same entity type” |
| hr.interview-panel | an interview schedule sits in both. The scorecard structure routes a file to the panel entry | §3.7 “It should rank candidate matches instead of accepting the first match” |
| hr.job-requisition | they share the requisition reference by design and should stay linked rather than merged | §4.9 “A file may validly belong to more than one accepted group” |
| career.employer-candidate-packet | the same duplication. That entry holds applications received about other people, keyed on requisition id and pipeline stage — which is this entry's schema under another name. Both are marked sensitive, so the risk is duplication rather than exposure | §3.6 “that each fact or label belongs to an allowed domain schema” |
| ops.partnerships-bd | an agency relationship is a supplier relationship; the agency's contract belongs there or to the finance slice's vendor entry, and only their submissions belong here | §3.8 “The system must separate roles that happen to contain the same entity type” |

### Sensitivity

`potentially_sensitive` — Every file in this domain is a record about identified job applicants, including people who were rejected and who never became employees. §8.4 names “identity documents, account statements, tax records, medical information, legal records, credentials, private correspondence, GPS metadata, employment materials, and educational records” among the material the local-first posture exists for, and requires that “Paths, complete extracted text, OCR output, file hashes, image EXIF, GPS, user edits, group memberships, and raw sensitive values should remain local”. §2.9's phrase applies through the contact and correspondence content these records carry. No handling class is assigned; that is P7's (§8.4).

---

## `hr.interview-panel` — Interview panels, scorecards and hiring decisions

The assessment step of recruiting — interview kits, panel composition, scorecards, assessment exercises and the debrief that produces a decision.

**Provenance:** **inference** — extends a domain the design does name

**Cite:** Extends the design-named career and recruiting domain to the employer's assessment step. §5.7's list includes 'recruiting processes' — “covering common organizational situations such as academic programs, university applications, recruiting processes, client engagements, research workflows, financial records, travel, legal matters, creative projects, software repositories, personal administration, and photo collections”. No design sentence names interview assessment specifically.

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `requisition_reference` | string | REQ-2026-0142 | `direct` | §3.13 direct: the vacancy assessed against |
| `candidate_reference` | string | CAND-88213 | `direct` | §3.13 direct: a labeled candidate identifier, never the name |
| `interview_stage` | string | final panel | `validated` | screening call, technical, panel, final. It is what distinguishes several scorecards for one person |
| `interviewer_role` | string | hiring manager | `validated` | §3.8 “It should avoid using authorship or creator identity as a destination dimension” — the role is the useful fact and the interviewer's name must never become a folder level |
| `assessment_criterion` | string | operational judgement | `validated` | the competency scored. A labeled row in every scorecard template. §3.3 forbids this catalogue holding the score itself |
| `recommendation` | string | hire | `validated` | hire, no hire, hold — a labeled decision field on a scorecard |
| `interview_date` | date | 2026-03-11 | `direct` | §3.13 direct: a labeled interview date; §2.9 also yields it from a calendar invitation |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.3, §3.5):

- a scorecard structure — a competency or criterion column together with a rating column and a recommendation field — co-occurring with a requisition or candidate reference
- an interview-kit term ('interview guide' | 'interview kit' | 'competency questions' | 'panel brief' | 'debrief summary' | 'assessment exercise') co-occurring with a requisition reference or a named hiring organisation and a position title
- an interview-schedule structure — a panel-member role list together with time slots and a candidate reference

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- free-text interview notes with no scorecard structure
- the recommendation where it is buried in a paragraph rather than a field
- separating an interview assessment from a performance conversation, which uses the same competency vocabulary and the same form in many organisations

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10, §4.9):

- 'interview'. A research interview (`ops.user-research` in this slice and `res.qualitative-coding` in the research slice), a journalistic interview, a clinical interview (health slice) and an exit interview (`hr.offboarding`, again in this slice). Four domains and two slices, and two of the four are sensitive in different ways — a mis-fire here can put a job applicant's assessment in a research folder
- 'panel' — a solar panel, a control panel, a panel discussion (research slice's conference material), a panel data set
- 'scorecard' — `ops.okr-goals` uses balanced scorecards in this very slice
- 'debrief' — `ops.retrospective-postmortem` uses it too
- 'assessment' — a risk assessment, an educational assessment (education slice), a clinical assessment (health slice)
- a candidate's name — §8.4 requires personal values stay local and §3.8 forbids a person becoming a folder level

### Work types

`interview guide or kit`, `panel brief`, `scorecard`, `assessment exercise`, `candidate work sample`, `debrief record`, `hiring decision record`, `reference check record`

### Grouping reasons (§4)

- one candidate's assessment across the stages they went through, under one requisition
- one requisition across the interview materials designed for it

### Template (§5)

`hiring organisation → requisition → document type`

Time first: **no**

§5.5: “a parent dimension should provide the context required to understand the child”. A scorecard is meaningless outside its requisition. The template deliberately stops above the candidate: §3.8 “It should avoid using authorship or creator identity as a destination dimension” and a folder named after a person who was not hired is the outcome this entry most needs to avoid, which §5.9's warning against a level that “It should warn when a level produces only one child, repeats a concept already expressed in the parent, creates excessive depth, or creates a large number of tiny folders” independently supports.

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| ops.user-research | an interview transcript is a research artifact and a recruiting artifact under one word. A requisition or candidate reference routes it here; a study or participant code routes it there | §3.8 “The system must separate roles that happen to contain the same entity type” |
| hr.performance-cycle | the same competency framework and often the same form is used to assess employees and candidates. A requisition reference is the separator and where it is absent the boundary fails | §3.7 “It should rank candidate matches instead of accepting the first match” |
| career.interview-cycle | the candidate's notes on the same interview are theirs; the panel's scorecard is this entry's. Both may mention the same date and role | §3.8 “The system must separate roles that happen to contain the same entity type” |
| career.employer-interview-scorecard | the same duplication again: structured assessments of named candidates, keyed on requisition id and interview stage. The two entries differ only in whether the organisation or the requisition leads the template | §3.6 “that each fact or label belongs to an allowed domain schema” |
| hr.recruiting-pipeline | an interview schedule is pipeline logistics and panel material at once | §4.9 “A file may validly belong to more than one accepted group” |

### Sensitivity

`potentially_sensitive` — Scorecards are recorded judgements about identified individuals, most of whom are not employees and never will be. §8.4 names “identity documents, account statements, tax records, medical information, legal records, credentials, private correspondence, GPS metadata, employment materials, and educational records” and requires that “Paths, complete extracted text, OCR output, file hashes, image EXIF, GPS, user edits, group memberships, and raw sensitive values should remain local”. Reference checks additionally carry a third party's opinions about a fourth party. No handling class is assigned; that is P7's (§8.4).

---

## `hr.offer-package` — Offers and hiring approvals (employer side)

The employer's act of making an offer — the approval, the offer letter and contract issued, and the pre-employment checks that condition it.

**Provenance:** **inference** — extends a domain the design does name

**Cite:** Extends the design-named career and recruiting domain to the employer's side of the offer. §5.4's Career template “a Career template may define company → role or recruiting cycle → document type” names document type as its leaf, which is what this entry's artifacts are. The received offer — the candidate's copy — is the career slice's.

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `requisition_reference` | string | REQ-2026-0142 | `direct` | §3.13 direct: the vacancy filled |
| `candidate_reference` | string | CAND-88213 | `direct` | §3.13 direct: a labeled identifier, never the name; §8.4 requires personal values stay local |
| `position_title` | string | regional planner | `validated` | the role offered |
| `offer_status` | string | accepted | `validated` | approved, issued, accepted, declined, withdrawn, lapsed |
| `start_date` | date | 2026-05-05 | `direct` | §3.13 direct: a labeled start date. It is the join to `hr.onboarding` |
| `approval_authority` | string | divisional director | `validated` | who signed off the terms. §3.8 “It should avoid using authorship or creator identity as a destination dimension” — a role |
| `pre_employment_check` | string | right to work verified | `validated` | the checks conditioning the offer. Note these are identity and background checks, which is why this entry sits close to the finance slice's identity material |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.3, §3.5):

- an offer-artifact term ('offer letter' | 'offer of employment' | 'conditional offer' | 'offer approval' | 'contract of employment') co-occurring with a hiring organisation name matched on a word boundary AND a position title
- a pre-employment check term ('right to work' | 'DBS' | 'background screening' | 'reference request' | 'pre-employment medical') co-occurring with a requisition or candidate reference
- an offer-approval structure — a proposed-salary or package label together with an approver role and a requisition reference

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- an offer negotiated over email with no formal letter
- offer status, which changes in correspondence rather than on the document
- separating the employer's issued copy from the candidate's received copy, which is the same PDF

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10, §4.9):

- 'offer'. A special offer, a discount offer, an offer on a house (personal slice's `pers.home-tenure`), an offer of a university place (education slice's `acad.college-application`). Four unrelated domains
- 'contract' — see `ops.contract-administration`; the finance and law slices both own contract domains and an employment contract belongs to the career slice on the employee's side
- 'start date' | 'salary' — a salary figure alone is a currency amount, which the finance slice names as its most over-firing pattern
- 'background check' | 'reference' — 'reference' is a citation (research slice), a reference number, a reference library and a job reference
- an employer name — §4.9 “A university name alone should not create a group because Columbia can appear as an authoring school, course provider, target institution, employer, research venue, or merely a cited organization”, which names 'employer' among the readings

### Work types

`offer approval`, `offer letter`, `contract of employment`, `pre-employment check record`, `right-to-work evidence`, `reference request`, `offer withdrawal or lapse note`, `new starter notification`

### Grouping reasons (§4)

- one hire across approval, offer, contract, checks and start notification — §3.9's “The documents are content-incoherent but purpose-coherent” is exactly this: an identity document, a reference letter and a contract share no topic and one purpose
- one requisition across the offers made under it

### Template (§5)

`hiring organisation → requisition → document type`

Time first: **no**

§5.5: “a parent dimension should provide the context required to understand the child”, and §5.4's Career row “a Career template may define company → role or recruiting cycle → document type” gives the design's own order for this material. The template again stops above the individual, for the reason given on `hr.interview-panel`.

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| career.offer-and-negotiation | identical documents. The employer's file and the employee's file hold the same offer letter and the same contract, and only whose corpus it is in distinguishes them | §3.8 “The system must separate roles that happen to contain the same entity type” |
| career.work-authorization | right-to-work evidence IS an identity document — a passport scan or visa. §7.3's Protected Records template names that material: “Protected Records may represent sensitive isolated material such as passport scans, medical documents, account statements, visas, legal forms, or credentials”. Those entries' treatment must win over this one's, and this entry must never cause such a scan to be moved or prompted on | §3.15 “Finance, identity, medical, and legal material should be implemented first as safety domains, meaning the system detects and protects them before any cloud or automated placement decision is allowed” |
| hr.compensation-planning | the offered package is compensation data. Where the salary structure is the substance the compensation entry leads | §3.11 “One file may hold facts from more than one domain without losing information” |
| career.employer-offer-approval | the fourth duplication: an organisation's internal decision to extend an offer and the paperwork that issues it. Identical scope to this entry | §3.6 “that each fact or label belongs to an allowed domain schema” |
| legal.contracts | an employment contract is a contract. The employment vocabulary and the requisition reference route it here | §3.7 “It should rank candidate matches instead of accepting the first match” |

### Sensitivity

`potentially_sensitive` — This domain holds identity evidence, background-check results and an individual's pay, for a named person. §8.4's corpus list is “identity documents, account statements, tax records, medical information, legal records, credentials, private correspondence, GPS metadata, employment materials, and educational records” and this entry touches identity documents and employment materials at once; §7.3's Protected Records template names “Protected Records may represent sensitive isolated material such as passport scans, medical documents, account statements, visas, legal forms, or credentials”. The marking is the strongest this catalogue can make, and no handling class is assigned because that is P7's (§8.4).

---

## `hr.onboarding` — Onboarding programmes

The employer's programme for bringing a new joiner into the organisation — plans, checklists, induction material and the records that show it happened.

**Provenance:** **proposal** — new here; the design names nothing like it

**Cite:** No design sentence names onboarding. §3.15 “Other domains remain placeholders until user demand and corpus evidence justify detailed templates” permits the addition. It is separated from `hr.offer-package` because onboarding runs after the start date and is a programme rather than a transaction.

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `hiring_organisation` | string | Northwind Logistics | `validated` | who is onboarding |
| `position_title` | string | regional planner | `validated` | the role being inducted, which determines the programme content. §3.8 “It should avoid using authorship or creator identity as a destination dimension” |
| `start_date` | date | 2026-05-05 | `direct` | §3.13 direct: a labeled start date; the join to the offer |
| `programme_element` | string | systems access provisioning | `validated` | induction, systems access, mandatory training, buddy assignment, probation review |
| `completion_status` | string | completed | `validated` | a labeled status on a checklist — the fact that makes an onboarding record evidence rather than a template |
| `probation_end_date` | date | 2026-08-05 | `direct` | §3.13 direct: a labeled probation date, which is the fact the whole programme is timed against |
| `induction_owner_role` | string | line manager | `validated` | §3.8 “It should avoid using authorship or creator identity as a destination dimension” — a role |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.3, §3.5):

- an employment-lifecycle onboarding term ('new starter' | 'first day' | 'induction' | 'probation review' | 'onboarding checklist' | 'joiner form') co-occurring with an employer name matched on a word boundary AND a start-date label
- a starter-checklist structure — a task list carrying two or more of 'systems access' | 'equipment issued' | 'mandatory training' | 'policy acknowledgement' — co-occurring with a position title or start date

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- an induction pack that is simply a set of policy documents with a covering note
- completion status, where a checklist has been filled in by hand or by email
- separating an employer's onboarding material from a new joiner's own first-week notes, which belong to the career slice

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10, §4.9):

- 'onboarding'. This word has FOUR unrelated homes in one corpus: employee onboarding (here), customer onboarding (`ops.customer-success`), vendor onboarding (the finance slice's `biz.vendor-management` uses it in its own recognition rule) and product onboarding UX (the software and creative slices). It is the clearest single case of a business word that cannot anchor a rule
- 'induction' — an induction hob, an induction motor, an inductive proof (research slice)
- 'welcome' | 'first day' | 'new starter' — 'welcome' appears in every product email and every course introduction
- 'checklist' — a shape shared with `ops.process-documentation`, `ops.go-to-market` and every clinical and safety domain
- an employer name — §4.9 “A university name alone should not create a group because Columbia can appear as an authoring school, course provider, target institution, employer, research venue, or merely a cited organization”

### Work types

`onboarding plan`, `starter checklist`, `induction pack`, `systems access request`, `equipment issue record`, `buddy or mentor assignment`, `probation review record`, `policy acknowledgement`

### Grouping reasons (§4)

- one joiner's onboarding across its checklist, access, training and probation records
- one role or cohort across the onboarding programme designed for it

### Template (§5)

`organisation → programme element → year`

Time first: **no**

§5.5: “a parent dimension should provide the context required to understand the child”. The template is deliberately built around the PROGRAMME rather than the joiner — §3.8 “It should avoid using authorship or creator identity as a destination dimension”, and a folder per new employee would be both a §5.9 violation (a level that “It should warn when a level produces only one child, repeats a concept already expressed in the parent, creates excessive depth, or creates a large number of tiny folders”) and the least privacy-safe structure available. Individual completion records belong on the person's file, which is the career slice's or the employer's personnel file, not a branch here.

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| career.onboarding-paperwork | a signed policy acknowledgement and an induction pack sit in both files identically | §3.8 “The system must separate roles that happen to contain the same entity type” |
| ops.customer-success | customer onboarding uses the same word and the same checklist shape. An account reference routes it there; an employment-lifecycle term routes it here | §3.8 “The system must separate roles that happen to contain the same entity type” |
| biz.vendor-management | vendor onboarding likewise — that entry's own recognition rule keys on 'vendor onboarding', and a bare onboarding rule here would collide with it directly | §3.7 “It should rank candidate matches instead of accepting the first match” |
| hr.training-lnd | mandatory training at induction is both. The training entry owns the curriculum and the completion record; this one owns the induction plan | §3.11 “One file may hold facts from more than one domain without losing information” |

### Sensitivity

`potentially_sensitive` — Onboarding records identify a named new employee and carry probation outcomes, equipment and access records. §8.4 names “identity documents, account statements, tax records, medical information, legal records, credentials, private correspondence, GPS metadata, employment materials, and educational records”. Systems access records additionally sit close to credential material, which §7.3's Protected Records template names among “Protected Records may represent sensitive isolated material such as passport scans, medical documents, account statements, visas, legal forms, or credentials”. No handling class is assigned; that is P7's (§8.4).

---

## `hr.offboarding` — Offboarding, exits and terminations

The employer's process for someone leaving — resignation and termination records, exit checklists, exit interviews and final arrangements.

**Provenance:** **proposal** — new here; the design names nothing like it

**Cite:** No design sentence names offboarding. §3.15 “Other domains remain placeholders until user demand and corpus evidence justify detailed templates” permits the addition. It is the most sensitive routine domain in this slice and is kept separate from `hr.employee-relations` because most exits are not disputes.

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `employing_organisation` | string | Northwind Logistics | `validated` | the employer |
| `leaver_reference` | string | EMP-4471 | `direct` | §3.13 direct: a labeled employee identifier, never the name; §8.4 requires that “Paths, complete extracted text, OCR output, file hashes, image EXIF, GPS, user edits, group memberships, and raw sensitive values should remain local” |
| `exit_type` | string | resignation | `validated` | resignation, dismissal, redundancy, retirement, end of fixed term, mutual termination. This is the fact that decides how sensitive the file is and it is normally stated |
| `last_working_day` | date | 2026-06-30 | `direct` | §3.13 direct: a labeled leaving date |
| `notice_period_status` | string | worked in full | `validated` | worked, paid in lieu, garden leave — a labeled field on a leaver form |
| `exit_checklist_item` | string | equipment returned | `validated` | access revoked, equipment returned, handover complete, final pay processed |
| `exit_feedback` | string | cited limited progression | `llm_supported` | the substance of an exit interview. Prose about a named person's view of their employer — content that must not leave the device without consent |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.3, §3.5):

- an exit-artifact term ('resignation letter' | 'notice of termination' | 'leaver form' | 'exit checklist' | 'exit interview' | 'garden leave' | 'settlement agreement') co-occurring with an employer name matched on a word boundary AND a leaving-date label
- a leaver-checklist structure — 'access revoked' | 'equipment returned' | 'final pay' as sibling items — co-occurring with an employee reference or a leaving date

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- a resignation sent as an email with no formal letter
- exit type, where a document describes a departure without naming it — and the difference between a resignation and a dismissal is the difference between a routine record and a potentially litigious one
- exit interview feedback, which is prose

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10, §4.9):

- 'exit' | 'leaver' | 'termination' | 'notice'. 'Exit' is a fire exit and a program exit code (software slice); 'termination' is a contract termination (`ops.contract-administration` and the finance slice's `legal.contracts`) and a cable termination; 'notice' is a public notice, a notice period and a notice of meeting (`ops.board-governance` in this very slice)
- 'resignation' — closer to specific, but a resignation from a committee, a club or a board is the personal and governance case
- 'exit interview' — 'interview' again, with the four collisions set out on `hr.interview-panel`
- 'redundancy' — also a technical term for duplicated systems (software slice) and for redundant data
- an employee name — §3.8 “It should avoid using authorship or creator identity as a destination dimension” and §8.4 requires personal values remain local

### Work types

`resignation letter`, `termination notice`, `leaver form`, `exit checklist`, `exit interview record`, `handover note`, `settlement agreement`, `final pay instruction`, `reference issued`

### Grouping reasons (§4)

- one departure across its notice, checklist, handover, interview and final arrangements
- one exit reason across a period, for reporting only

### Template (§5)

`organisation → document type → year`

Time first: **no**

§5.5: “a parent dimension should provide the context required to understand the child”. As with onboarding the template deliberately refuses a per-person level: §3.8 “It should avoid using authorship or creator identity as a destination dimension”, and a folder named after someone who was dismissed is the single worst structure this product could propose. §5.5's “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders” keeps the year last.

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| career.exit-and-offboarding | the resignation letter the user wrote and the copy their employer filed are one document | §3.8 “The system must separate roles that happen to contain the same entity type” |
| hr.employee-relations | a dismissal follows a disciplinary process and a settlement follows a dispute. Where a grievance or disciplinary case reference is present the relations entry leads, because its treatment is stricter | §3.7 “It should rank candidate matches instead of accepting the first match” |
| legal.litigation-dispute | a settlement agreement is a legal instrument and an employment record. The law and finance slices own the instrument; this entry holds the HR process around it | §3.11 “One file may hold facts from more than one domain without losing information” |
| biz.payroll-employer | final pay is a payroll transaction. The finance slice owns anything with a pay period and a payroll run | §3.11 “One file may hold facts from more than one domain without losing information” |

### Sensitivity

`potentially_sensitive` — This domain records the circumstances in which named individuals lost or left their jobs, including dismissals and settlements. §8.4 names “identity documents, account statements, tax records, medical information, legal records, credentials, private correspondence, GPS metadata, employment materials, and educational records” among the categories the local-first posture exists for and requires that “Paths, complete extracted text, OCR output, file hashes, image EXIF, GPS, user edits, group memberships, and raw sensitive values should remain local”. No handling class is assigned; that is P7's (§8.4).

---

## `hr.training-lnd` — Training and learning development

The employer's provision of learning — curricula, course materials, delivery records and the completion and certification evidence they produce.

**Provenance:** **proposal** — new here; the design names nothing like it

**Cite:** No design sentence names workplace learning. Academic files are design-named with the fields “Academic files may use school, term, course, instructor, and work type”, and the education slice owns them; this entry is the employer-provision case, which has a compliance dimension academia does not. §3.15 “Other domains remain placeholders until user demand and corpus evidence justify detailed templates” permits the addition.

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `providing_organisation` | string | Northwind Logistics | `validated` | who provides or requires the training. §3.8's role discipline separates the employer from an external training provider named on the same certificate |
| `subject` | string | Manual handling refresher | `validated` | the course. §3.11 names `subject` as an Academic field and this is the workplace instance of the same field, deliberately reusing it rather than inventing a new one — §3.12 “The system may create new values when it sees a new course, project, company, university, or event, but it should not invent new fields automatically” |
| `training_requirement` | string | mandatory annual | `validated` | mandatory, role-required, development, optional. It is what distinguishes compliance training from professional development and it decides retention |
| `delivery_mode` | string | e-learning | `validated` | classroom, e-learning, on the job, external |
| `completion_date` | date | 2026-02-19 | `direct` | §3.13 direct: a labeled completion date on a certificate or record |
| `expiry_date` | date | 2027-02-19 | `direct` | §3.13 direct: a labeled expiry or renewal date — the fact that makes compliance training trackable at all |
| `learner_reference` | string | EMP-4471 | `direct` | §3.13 direct: a labeled identifier, never the name; §8.4 requires personal values stay local |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.3, §3.5):

- a training-record term ('training record' | 'certificate of completion' | 'competency matrix' | 'training matrix' | 'refresher due' | 'CPD record') co-occurring with a named course AND a completion or expiry date label
- a mandatory-training term ('mandatory training' | 'compliance training' | 'statutory training') co-occurring with an employer name matched on a word boundary
- a course-material header — a named course together with a learning-objective heading and a providing organisation, which distinguishes the MATERIAL from the RECORD

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- a slide deck used to teach something with no course branding
- training requirement, which decides whether a record must be retained and is rarely labeled
- separating employer training material from academic course material, which share every artifact type

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10, §4.9):

- 'training'. Model training and training data (software and research slices), athletic training (personal and health slices), a training plan, driver training and a training shoe. The machine-learning sense alone would claim a large part of a technical corpus
- 'course' — §3.11 assigns `subject` to Academic files and the education slice has forty entries built on it. A bare rule here claims that entire slice
- 'certificate' — a birth certificate and a share certificate (personal and finance slices), a TLS certificate (software slice), a certificate of incorporation (finance slice). Four slices
- 'learning' | 'development' | 'CPD' — 'development' is software development, property development and professional development in one word
- 'module' | 'curriculum' | 'competency' — all shared with the education slice
- an expiry date — a passport, an insurance policy and a domain registration all have one

### Work types

`curriculum or training plan`, `course material`, `e-learning record`, `attendance register`, `certificate of completion`, `training matrix`, `competency framework`, `trainer or provider agreement`

### Grouping reasons (§4)

- one course across its material, delivery records and certificates
- one compliance requirement across the records that evidence it

### Template (§5)

`providing organisation → course → document type`

Time first: **no**

§5.5: “a parent dimension should provide the context required to understand the child”, and §5.4's own Academic template — school then term then course then work type — is the nearest design precedent. §5.5's “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders” keeps completion years out of the upper levels. As elsewhere in this block the template stops above the learner, for the §3.8 reason.

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| acad.credential-certificate | a professional qualification the user earned is an education record for them and a training record for their employer; the certificate PDF is identical. The education slice's school, term and credit fields are the discriminator where present | §3.11 “Academic files may use school, term, course, instructor, and work type” |
| career.continuing-education | the same certificate again, filed a third way. This is one of the clearest three-way personal/professional collisions in the catalogue | §3.8 “The system must separate roles that happen to contain the same entity type” |
| med.clinician-cme | clinical continuing education has its own regulatory framework and the health slice owns it; this entry must not claim files carrying clinical registration vocabulary | §3.8 “The system must separate roles that happen to contain the same entity type” |
| soft.training-material | the software slice has a training-material entry for technical education. A product, tool or repository reference routes a file there | §3.11 “Code files may use project, repository, programming language, and artifact type” |
| ops.process-documentation | a job aid is both training material and a procedure | §3.11 “One file may hold facts from more than one domain without losing information” |

### Sensitivity

`potentially_sensitive` — Completion and competency records identify individuals and are employment material, which §8.4 names among “identity documents, account statements, tax records, medical information, legal records, credentials, private correspondence, GPS metadata, employment materials, and educational records”. Course material itself carries nothing §2.9 names — the split runs through the domain rather than around it, and §3.1's many-facts model is what lets the marking sit on the record files rather than the whole branch. No handling class is assigned; that is P7's (§8.4).

---

## `hr.performance-cycle` — Performance management cycles

The recurring process of setting expectations, reviewing performance and calibrating outcomes for employees.

**Provenance:** **proposal** — new here; the design names nothing like it

**Cite:** No design sentence names performance management. §3.15 “Other domains remain placeholders until user demand and corpus evidence justify detailed templates” permits the addition.

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `employing_organisation` | string | Northwind Logistics | `validated` | the employer running the cycle |
| `review_cycle` | string | FY2026 mid-year review | `validated` | the round. It is the grouping key — every employee's form belongs to one cycle |
| `review_stage` | string | calibration | `validated` | objective setting, mid-year, year-end, calibration, moderation |
| `subject_reference` | string | EMP-4471 | `direct` | §3.13 direct: a labeled employee identifier, never the name; §8.4 requires that “Paths, complete extracted text, OCR output, file hashes, image EXIF, GPS, user edits, group memberships, and raw sensitive values should remain local” |
| `reviewer_role` | string | line manager | `validated` | §3.8 “It should avoid using authorship or creator identity as a destination dimension” — a role |
| `competency_framework` | string | leadership behaviours | `validated` | the framework assessed against, which is a published document and is not itself sensitive |
| `outcome_category` | string | meets expectations | `llm_supported` | the rating band. §3.3 forbids this catalogue holding a rating value; the CATEGORY is a label and reading it from a filled form usually needs interpretation |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.3, §3.5):

- a performance-cycle artifact term ('performance review' | 'appraisal' | 'objective setting form' | 'calibration' | 'moderation session' | 'performance improvement plan') co-occurring with an employer name matched on a word boundary AND a review-cycle or period label
- a review-form structure — an objectives or competency section together with a reviewer-comment section and a rating or outcome field — co-occurring with an employee reference

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- manager notes written as free text ahead of a review
- outcome category, which is the substance and is frequently narrative
- separating a performance conversation from a disciplinary one, which is the difference between this entry and `hr.employee-relations` and is often only clear from tone

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10, §4.9):

- 'performance'. System performance and performance testing (the software slice has `soft.performance-load-test`), fund performance (finance slice), athletic performance (personal slice), a musical performance (creative slice) and supplier performance (the finance slice's `biz.vendor-management` scores it). Five slices
- 'review'. Set out at length on `ops.retrospective-postmortem` — a performance review, a peer review, a code review, a book review, a literature review and a portfolio review
- 'appraisal' — a property appraisal and an options appraisal (`ops.business-case`, in this very slice)
- 'objectives' | 'rating' | 'feedback' — 'feedback' is also an audio and control-systems term
- 'PIP' — a thin acronym that is also a package installer (software slice) and a seed
- an employee name — §3.8 “It should avoid using authorship or creator identity as a destination dimension”

### Work types

`objective setting form`, `self-assessment`, `manager review form`, `calibration pack`, `moderation record`, `performance improvement plan`, `cycle guidance`, `rating distribution report`

### Grouping reasons (§4)

- one review cycle across its guidance, forms, calibration and reporting
- one framework across the cycles it was used in

### Template (§5)

`organisation → review cycle → document type`

Time first: **no**

§5.5: “a parent dimension should provide the context required to understand the child”. A form is meaningless outside its cycle. The template stops above the individual — §3.8 “It should avoid using authorship or creator identity as a destination dimension” — which here is not merely tidy but protective: a per-employee folder of performance ratings is the most damaging structure this catalogue could recommend.

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| career.performance-review | the employee's copy and the manager's copy are the same form. Whose corpus it is in is the only distinction and §5.10 says “Existing folders must not be automatically flattened, renamed, or reorganized simply because a template would produce a different structure” | §3.8 “The system must separate roles that happen to contain the same entity type” |
| ops.okr-goals | individual objectives are both a goal artifact and a performance one. This catalogue routes any named-individual goal set here — see the open question on that entry | §3.11 “One file may hold facts from more than one domain without losing information” |
| hr.employee-relations | a performance improvement plan sits on the boundary: it is a management tool and often the first step of a capability process. Where a formal procedure is invoked the relations entry leads | §3.7 “It should rank candidate matches instead of accepting the first match” |
| hr.compensation-planning | calibration feeds pay decisions and the two packs are often one document | §3.11 “One file may hold facts from more than one domain without losing information” |

### Sensitivity

`potentially_sensitive` — Performance records are recorded judgements about identified employees and directly affect their livelihoods. §8.4 names “identity documents, account statements, tax records, medical information, legal records, credentials, private correspondence, GPS metadata, employment materials, and educational records” and requires that “Paths, complete extracted text, OCR output, file hashes, image EXIF, GPS, user edits, group memberships, and raw sensitive values should remain local”. No handling class is assigned; that is P7's (§8.4).

---

## `hr.engagement-survey` — Employee engagement and listening surveys

Surveys run on an organisation's own workforce — the instrument, the results, and the action planning that follows.

**Provenance:** **proposal** — new here; the design names nothing like it

**Cite:** No design sentence names engagement surveys. The research slice's `res.survey-instrument` owns the academic instance of the same artifact. §3.15 “Other domains remain placeholders until user demand and corpus evidence justify detailed templates” permits this addition.

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `employing_organisation` | string | Northwind Logistics | `validated` | whose workforce was surveyed |
| `survey_wave` | string | 2026 annual engagement survey | `validated` | the wave. It is the grouping key and comparability across waves is the whole point of the domain |
| `survey_scope` | string | all employees, UK and Ireland | `llm_supported` | who was invited. It is prose and it determines whether results are comparable |
| `reporting_unit` | string | Distribution | `validated` | the unit a result set covers. Results are cut by unit and each cut is a separate file |
| `survey_provider` | string | an external survey platform | `validated` | §3.8's role discipline separates the provider from the employer — both are organisations on the same report |
| `question_theme` | string | manager support | `validated` | the theme a question or score belongs to. §3.3 forbids holding a score as a value; the theme is the label |
| `verbatim_comment` | string | a free-text response | `llm_supported` | §3.11 permits “several additional fields used only for search, privacy protection, explanation, or later review”. This is the sensitive content: free-text comments are employees' own words and are frequently re-identifiable in a small team, which is why the whole entry is marked |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.3, §3.5):

- an engagement-survey term ('engagement survey' | 'employee survey' | 'pulse survey' | 'employee net promoter' | 'listening survey') co-occurring with an employer name matched on a word boundary AND a wave or period label
- a survey-report structure — a question-theme column together with a response-rate or score column and a unit breakdown — co-occurring with a named employer and a survey wave
- an action-planning term ('survey action plan' | 'engagement action plan' | 'you said, we did') co-occurring with a survey wave label

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- a results deck with no survey vocabulary in the title
- survey scope, which is prose and decides comparability
- separating an employee survey from a customer survey when the instrument does not name its population

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10, §4.9):

- 'survey'. `res.survey-instrument` is a named research-slice domain, `ops.user-research` in this slice runs customer surveys, a land survey and a building survey sit in the personal and finance slices, and a satisfaction survey arrives after every purchase. Four slices
- 'engagement'. Within this slice alone it also means a consulting engagement (`ops.client-engagement`); outside it, social-media engagement and a betrothal. It is the slice's own internal homonym and the best single illustration of the hazard
- 'pulse' — a medical term (health slice) and a signal term
- 'score' | 'response rate' | 'NPS' — NPS is used for customers far more often than employees
- an employer name — §4.9 “A university name alone should not create a group because Columbia can appear as an authoring school, course provider, target institution, employer, research venue, or merely a cited organization”

### Work types

`survey instrument`, `invitation and communications`, `results report`, `unit-level result cut`, `verbatim comment set`, `action plan`, `wave comparison`

### Grouping reasons (§4)

- one survey wave across its instrument, results, cuts and action plan
- one reporting unit across successive waves

### Template (§5)

`organisation → survey wave → reporting unit`

Time first: **no**

§5.5: “a parent dimension should provide the context required to understand the child”. A unit-level cut is meaningless without its wave. §5.5's “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders” puts the organisation first even though the wave is time-shaped, because a wave is a named round rather than a calendar year.

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| res.survey-instrument | the research slice owns surveys as instruments with an ethics framework. An institution, ethics approval or study reference routes a file there | §3.11 “Research files may use project, stage, artifact type, lab, and venue” |
| ops.user-research | customer and employee surveys are the same instrument pointed at different populations, and the population is rarely stated on the instrument | §3.8 “The system must separate roles that happen to contain the same entity type” |
| hr.dei-program | demographic questions and their cuts sit in both; the DEI entry's treatment is stricter and should lead where protected characteristics are the subject | §3.7 “It should rank candidate matches instead of accepting the first match” |
| hr.workforce-analytics | survey results feed people reporting. The analytics entry owns the combined view | §3.11 “One file may hold facts from more than one domain without losing information” |

### Sensitivity

`potentially_sensitive` — Free-text comments are employees' own words about their employer and are routinely re-identifiable in small teams; unit-level cuts of a small unit are effectively individual data. §8.4 names “identity documents, account statements, tax records, medical information, legal records, credentials, private correspondence, GPS metadata, employment materials, and educational records” and requires that “Paths, complete extracted text, OCR output, file hashes, image EXIF, GPS, user edits, group memberships, and raw sensitive values should remain local”. The marking is applied to the whole domain because the aggregate and the individual cannot be reliably separated by a rule. No handling class is assigned; that is P7's (§8.4).

---

## `hr.compensation-planning` — Compensation and benefits planning

How an employer decides what to pay — salary structures, benchmarking, pay review rounds, bonus and benefits design — as distinct from paying it.

**Provenance:** **proposal** — new here; the design names nothing like it

**Cite:** No design sentence names compensation planning. The finance slice's `biz.payroll-employer` owns the payroll RUN — registers, remittances, employer returns — and explicitly distinguishes itself from any one employee's payslip. This entry is the DECISION that precedes payroll. §3.15 “Other domains remain placeholders until user demand and corpus evidence justify detailed templates” permits it.

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `employing_organisation` | string | Northwind Logistics | `validated` | the employer setting pay |
| `review_round` | string | 2026 pay review | `validated` | the annual round. It is the grouping key |
| `pay_structure_element` | string | grade 6 salary band | `validated` | band, grade, scale point, bonus scheme, allowance, benefit. §3.3 forbids this catalogue holding any pay figure as a value; the element is a label |
| `benchmark_source` | string | an external salary survey | `validated` | where the market data came from. §3.8's role discipline separates the benchmarking provider from the employer |
| `population_scope` | string | UK operations population | `llm_supported` | who a decision applies to. It is prose and it determines whether a file is aggregate or individual |
| `approval_body` | string | remuneration committee | `validated` | who signed it off — the link to `ops.board-governance` |
| `effective_date` | date | 2026-04-01 | `direct` | §3.13 direct: a labeled effective-from field |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.3, §3.5):

- a compensation-artifact term ('pay review' | 'salary band' | 'pay structure' | 'salary benchmarking' | 'bonus scheme rules' | 'remuneration policy' | 'total reward statement') co-occurring with an employer name matched on a word boundary AND a round or effective-date label
- a pay-structure table — a grade or band column together with a range or scale column and an effective-date label — co-occurring with a named employer
- a benchmarking report block — a named survey or data provider together with a job-family or grade mapping and a market-position statement

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- a pay proposal written as a paper to a committee with no structure
- population scope, which is what separates an aggregate policy from an individual decision
- separating a compensation planning file from the payroll instruction that implements it

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10, §4.9):

- 'salary' | 'pay' | 'compensation' | 'reward' | 'bonus'. 'Compensation' in the law and insurance sense is damages (law and finance slices); 'reward' is a loyalty scheme; 'bonus' is a game term and a bank bonus; 'pay' is any payment at all
- a currency amount — the finance slice names this as its single most over-firing pattern, and a pay structure is a table of them
- 'benefits' — benefits realisation in a business case (`ops.business-case`, this slice), welfare benefits (finance and personal slices), health benefits (health slice)
- 'grade' | 'band' | 'scale' — an academic grade (education slice), a frequency band, a measurement scale
- 'remuneration' — closer to specific, and still shared with the finance slice's corporate governance material
- an employee name — §3.8 “It should avoid using authorship or creator identity as a destination dimension” and §8.4 requires personal values stay local

### Work types

`pay structure or grading`, `benchmarking report`, `pay review guidance`, `pay review model`, `bonus scheme rules`, `benefits design paper`, `remuneration committee paper`, `total reward statement`

### Grouping reasons (§4)

- one review round across its benchmarking, modelling, guidance and approval
- one pay structure across its successive revisions

### Template (§5)

`organisation → review round → document type`

Time first: **no**

§5.5: “a parent dimension should provide the context required to understand the child”. A model is meaningless outside its round. The template again stops above the individual — §3.8 “It should avoid using authorship or creator identity as a destination dimension” — and here that is the difference between a folder of pay policy and a folder of everybody's salary.

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| biz.payroll-employer | deferred to on everything transactional. A pay period, a payroll run identifier, a remittance or an employer return routes a file there. This entry stops at the decision | §3.11 “One file may hold facts from more than one domain without losing information” |
| career.compensation-record | an individual's pay letter is their employment record and their employer's compensation record. The same document, and both readings are sensitive | §3.8 “The system must separate roles that happen to contain the same entity type” |
| ops.board-governance | remuneration committee papers are governance material and compensation material at once | §4.9 “A file may validly belong to more than one accepted group” |
| ops.operating-plan-budget | a pay review model is a cost model and often sits on a budget tab. The cost-centre label routes it to the budget entry, but where individual salaries are visible this entry's marking must win | §3.11 “One file may hold facts from more than one domain without losing information” |

### Sensitivity

`potentially_sensitive` — Compensation material moves between aggregate structures and individual pay decisions without changing shape, and a pay review model is usually a spreadsheet with one row per named employee. §8.4 names “identity documents, account statements, tax records, medical information, legal records, credentials, private correspondence, GPS metadata, employment materials, and educational records” and requires that “Paths, complete extracted text, OCR output, file hashes, image EXIF, GPS, user edits, group memberships, and raw sensitive values should remain local”. The marking covers the whole domain because no rule can reliably tell the aggregate file from the individual one. No handling class is assigned; that is P7's (§8.4).

---

## `hr.workforce-analytics` — Workforce analytics and people reporting

Measurement of the workforce — headcount, movement, attrition, absence, cost and diversity reporting, and the dashboards built from them.

**Provenance:** **proposal** — new here; the design names nothing like it

**Cite:** No design sentence names workforce analytics. §3.15 “Other domains remain placeholders until user demand and corpus evidence justify detailed templates” permits the addition. It is separated from `hr.org-design-headcount` because that entry plans and this one measures, and their sensitivity differs at the row level rather than the file level.

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `employing_organisation` | string | Northwind Logistics | `validated` | whose workforce is measured |
| `measure` | string | voluntary attrition | `validated` | headcount, joiners, leavers, attrition, absence, cost per head, span of control. §3.3 forbids this catalogue holding the measured value |
| `reporting_period` | string | March 2026 | `validated` | the period measured. Only validated beside a people-reporting term |
| `reporting_unit` | string | Distribution | `validated` | the cut. It is the second dimension and it is what makes a small-unit report effectively individual data |
| `aggregation_level` | string | unit level | `llm_supported` | organisation, unit, team, individual. It is the fact that decides sensitivity and it has to be inferred from the data rather than read from a label |
| `data_source` | string | HR information system export | `validated` | where the numbers came from — the fact that makes a report reproducible |
| `as_at_date` | date | 2026-03-31 | `direct` | §3.13 direct: a labeled as-at or snapshot date, which is distinct from the period and is what makes two reports comparable |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.3, §3.5):

- a people-reporting term ('headcount report' | 'attrition' | 'turnover rate' | 'absence report' | 'people dashboard' | 'workforce report' | 'span of control') co-occurring with an employer or unit name matched on a word boundary AND a period or as-at label
- an HR-system export structure — employee reference, unit and one of joiner date, leaver date or absence type as sibling column headings — which §2.9's spreadsheet shape (“should yield workbook or file metadata, sheet names, column headers, visible cell values, table-like regions, formulas only when useful, and dates or identifiers from labeled cells”) makes readable, and which is the case where this domain is at its most sensitive

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- a people deck that reports movement without using any of the vocabulary
- aggregation level, which decides sensitivity and is a property of the data rather than a label
- separating a people report from an operational report that happens to include headcount

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10, §4.9):

- 'headcount' | 'attrition' | 'turnover'. 'Turnover' is revenue in most of the finance slice — a complete inversion of meaning between two slices for one word, and one of the sharpest false-friend cases in the catalogue
- 'absence' | 'sickness' — the health slice owns sickness material and mis-routing an employee absence report away from the health-adjacent treatment would be the wrong kind of error
- 'dashboard' | 'metrics' | 'analytics' | 'report' — refused everywhere in this slice, for the reasons on `ops.status-report`
- 'diversity' — routed to `hr.dei-program` and refused here
- an employee-reference column — a bare identifier column shape shared with customer, asset and product tables

### Work types

`headcount report`, `movement or attrition report`, `absence report`, `people dashboard`, `workforce cost report`, `HR system export`, `board people pack`, `benchmark comparison`

### Grouping reasons (§4)

- one measure across its reporting periods
- one reporting period across the people reports produced for it

### Template (§5)

`organisation → measure → period`

Time first: **no**

§5.5: “a parent dimension should provide the context required to understand the child”. A period is meaningless without knowing what is measured. §5.5's “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders” puts the measure above the period so a trend reads as one series, which is the only reason to keep old reports at all.

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| hr.org-design-headcount | a headcount plan and a headcount report share every column. Forward-looking effective dates and proposed positions route a file there; an as-at date routes it here | §3.7 “It should rank candidate matches instead of accepting the first match” |
| ops.status-report | people metrics appear inside operational reporting. An HR-system source or an employee-level grain routes the file here, where the sensitivity marking applies | §3.11 “One file may hold facts from more than one domain without losing information” |
| hr.dei-program | diversity reporting is workforce analytics with protected characteristics in it. That entry's treatment is stricter and leads | §3.7 “It should rank candidate matches instead of accepting the first match” |
| biz.payroll-employer | workforce cost reporting draws directly on payroll. A payroll run identifier routes a file there | §3.11 “One file may hold facts from more than one domain without losing information” |

### Sensitivity

`potentially_sensitive` — A workforce report is aggregate until the unit is small or the export is at row level, and both happen constantly — a leavers list for one team is a list of named people who lost their jobs. §8.4 names “identity documents, account statements, tax records, medical information, legal records, credentials, private correspondence, GPS metadata, employment materials, and educational records” and requires that “Paths, complete extracted text, OCR output, file hashes, image EXIF, GPS, user edits, group memberships, and raw sensitive values should remain local”. The marking covers the domain because the aggregate and individual cases cannot be told apart by a rule. No handling class is assigned; that is P7's (§8.4).

---

## `hr.dei-program` — Diversity, equity and inclusion programmes

An organisation's work on the composition and inclusiveness of its workforce — strategy, monitoring, reporting and programme activity.

**Provenance:** **proposal** — new here; the design names nothing like it

**Cite:** No design sentence names DEI. §3.15 “Other domains remain placeholders until user demand and corpus evidence justify detailed templates” permits the addition. It is a separate entry rather than a subject value inside `hr.workforce-analytics` precisely because its data are protected characteristics, and folding it in would hide that.

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `employing_organisation` | string | Northwind Logistics | `validated` | whose programme it is |
| `programme_element` | string | inclusive recruitment | `validated` | strategy, monitoring, reporting, network or resource group, training, target setting |
| `characteristic_category` | string | a monitored characteristic category | `validated` | the dimension monitored, written functionally and deliberately not enumerated — see the open question. §3.3 forbids holding any figure |
| `reporting_obligation` | string | statutory reporting | `validated` | voluntary, statutory, contractual. It decides retention and disclosure and is jurisdiction-defined |
| `reporting_period` | string | 2026 reporting year | `validated` | the period covered |
| `reporting_unit` | string | UK operations | `validated` | the population reported on |
| `action_commitment` | string | revise panel composition guidance | `llm_supported` | §3.11 permits “several additional fields used only for search, privacy protection, explanation, or later review”; commitments are prose and are the durable output |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.3, §3.5):

- a DEI-artifact term ('diversity and inclusion' | 'equality monitoring' | 'inclusion strategy' | 'employee resource group' | 'pay gap report' | 'equality objectives') co-occurring with an employer name matched on a word boundary AND a reporting-period label
- an equality-monitoring form structure — a self-declaration or 'prefer not to say' option together with a monitored-characteristic question set — co-occurring with an employer name. This is the most sensitive artifact in the slice and the rule exists mainly so it can be recognised and protected rather than filed

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- an inclusion strategy written as a general strategy document
- action commitments, which are prose
- separating an employer's DEI reporting from published research on the same subject, which the research slice owns

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10, §4.9):

- 'diversity'. Biodiversity and species diversity (research slice), portfolio diversification (finance slice), diversity of a data set (software slice). Three slices and one word
- 'equality' | 'equity'. 'Equity' means shareholders' equity in the finance slice — `corp.shareholder-captable` is built on it — and home equity in the personal slice. This is a true false friend and a bare rule would claim cap tables
- 'inclusion' — an inclusion criterion in a clinical trial or systematic review (health and research slices), and an inclusion in a document
- 'gender' | 'ethnicity' | 'disability' — these are protected characteristics, and a rule keyed on them would fire on medical records, research data and personal documents. Refused not because they are weak but because firing on them is itself a hazard
- 'ERG' | 'D&I' | 'DEI' — thin acronyms
- an employer name — §4.9 “A university name alone should not create a group because Columbia can appear as an authoring school, course provider, target institution, employer, research venue, or merely a cited organization”

### Work types

`inclusion strategy`, `equality monitoring form`, `diversity report`, `pay gap report`, `resource group material`, `inclusion training material`, `action plan`, `supplier diversity questionnaire`

### Grouping reasons (§4)

- one reporting period across the monitoring, report and action plan
- one programme element across the material produced for it

### Template (§5)

`organisation → programme element → reporting period`

Time first: **no**

§5.5: “a parent dimension should provide the context required to understand the child”. A report is meaningless without knowing which element of the programme it belongs to. §5.5's “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders” keeps the period last. There is deliberately no level below the unit: a folder structure that split by characteristic would be an unacceptable artifact of this product.

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| hr.workforce-analytics | diversity reporting is workforce reporting with protected characteristics. This entry leads wherever a monitored characteristic appears, because its treatment must not be lost | §3.7 “It should rank candidate matches instead of accepting the first match” |
| hr.engagement-survey | engagement surveys carry demographic questions and cut results by them; the two data sets are frequently one file | §3.11 “One file may hold facts from more than one domain without losing information” |
| corp.compliance-audit | statutory pay-gap and equality reporting is regulatory filing as much as HR programme work | §3.11 “One file may hold facts from more than one domain without losing information” |
| res.human-subjects-consent | academic research on diversity uses the same monitoring instruments under an ethics framework; an institution or ethics reference routes a file to the research slice | §3.11 “Research files may use project, stage, artifact type, lab, and venue” |

### Sensitivity

`potentially_sensitive` — Equality monitoring data are protected characteristics of identified people, which is the most sensitive personal data any employer holds. §8.4 names “identity documents, account statements, tax records, medical information, legal records, credentials, private correspondence, GPS metadata, employment materials, and educational records” and requires that “Paths, complete extracted text, OCR output, file hashes, image EXIF, GPS, user edits, group memberships, and raw sensitive values should remain local”. The marking applies to the whole domain, including aggregate reports, because small-population cuts are re-identifying. No handling class is assigned; that is P7's (§8.4).

### Open question — Joseph's call, unresolved

> This entry names `characteristic_category` as a field but deliberately does not enumerate its values. The list of protected or monitored characteristics is jurisdiction-defined and the categories are not translations of one another. More importantly, a catalogue that enumerated them would be instructing the extractor to look for them, and §3.7's conservative-facet-extraction discipline argues against building a gazetteer of characteristics at all. Whether this product should DETECT such material in order to protect it, or should decline to model it and let it fall to §7.3's Protected Records template — “Protected Records may represent sensitive isolated material such as passport scans, medical documents, account statements, visas, legal forms, or credentials” — is Joseph's call, and it is the single most consequential question in this slice.

---

## `hr.employee-relations` — Employee relations cases

Formal processes between an employer and an individual or their representatives — grievances, disciplinaries, capability, investigations and collective consultation.

**Provenance:** **proposal** — new here; the design names nothing like it

**Cite:** No design sentence names employee relations. §3.15 “Other domains remain placeholders until user demand and corpus evidence justify detailed templates” permits the addition. The law slice's `law.investigation` owns investigations conducted as legal work; this entry is the employer's own HR process.

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `case_reference` | string | ER-2026-021 | `direct` | §3.13 direct: a labeled case reference. It is the only safe anchor in this domain, because every other identifier here is a person |
| `case_type` | string | grievance | `validated` | grievance, disciplinary, capability, investigation, appeal, collective consultation, tribunal claim |
| `employing_organisation` | string | Northwind Logistics | `validated` | the employer |
| `case_stage` | string | investigation | `validated` | raised, investigation, hearing, outcome, appeal, closed |
| `subject_reference` | string | EMP-4471 | `direct` | §3.13 direct: an identifier, never a name. §8.4 requires that “Paths, complete extracted text, OCR output, file hashes, image EXIF, GPS, user edits, group memberships, and raw sensitive values should remain local” and this domain is the strongest instance of that requirement in the slice |
| `participant_role` | string | companion | `validated` | complainant, respondent, witness, investigator, companion, representative. §3.8 “The system must separate roles that happen to contain the same entity type” — several people appear in one case in incompatible roles and conflating them would be a serious error |
| `outcome_category` | string | upheld in part | `llm_supported` | the finding. Prose in a letter, and the most consequential sentence in the file |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.3, §3.5):

- an employee-relations artifact term ('grievance' | 'disciplinary hearing' | 'investigation report' | 'notice of hearing' | 'right to be accompanied' | 'capability process' | 'suspension letter') co-occurring with an employer name matched on a word boundary AND a case reference or a hearing-date label
- a case-file header — a case reference co-occurring with a case-stage term and a participant-role label
- a collective-consultation term ('collective consultation' | 'recognised trade union' | 'employee representatives' | 'consultation meeting') co-occurring with an employer name and a consultation-period label

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- correspondence that begins a process without naming it, which is the normal first document in a case
- outcome category, which is a sentence
- distinguishing a performance conversation from a capability process, which is the boundary with `hr.performance-cycle` and is often only visible in the register of the letter

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10, §4.9):

- 'grievance' | 'disciplinary' | 'investigation' | 'hearing' | 'case'. 'Investigation' belongs to the law slice (`law.investigation`), the research slice (an investigation in the scientific sense) and the health slice (a clinical investigation is a TEST); 'hearing' is a court hearing (law slice) and hearing as a sense (health slice); 'case' has the five collisions set out on `ops.business-case`. Every anchor word in this domain is owned by another slice in a different sense
- 'complaint' — a customer complaint (`ops.support-operations`, this slice) and a clinical complaint
- 'suspension' — a vehicle suspension (personal slice) and a suspension of an account
- 'appeal' — a court appeal (the law slice has `law.appeals`) and a charity appeal
- an employee name — §3.8 “It should avoid using authorship or creator identity as a destination dimension”, and in this domain a name in a filename is itself a disclosure
- 'confidential' — present on every document here and on a third of the corpus

### Work types

`case opening record`, `invitation to a hearing`, `investigation report`, `witness statement`, `hearing notes`, `outcome letter`, `appeal record`, `settlement or agreed outcome`, `consultation minute`

### Grouping reasons (§4)

- one case across every document produced in it — the case reference is the anchor §4.9's stop rules require, and without it a case should not be assembled at all
- one collective consultation across its meetings and communications

### Template (§5)

`organisation → case type → case`

Time first: **no**

§5.5: “a parent dimension should provide the context required to understand the child”. A hearing note is meaningless outside its case. The case level uses the case REFERENCE and never a person's name — §3.8 “It should avoid using authorship or creator identity as a destination dimension” is stated as a template rule elsewhere in this catalogue and is a protection here. §5.5's “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders” keeps years out; a case is one thread.

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| law.investigation | an investigation conducted under legal privilege, or a tribunal claim, is the law slice's. Where a solicitor, privilege marking, tribunal or claim reference appears this entry must defer | §3.8 “The system must separate roles that happen to contain the same entity type” |
| hr.performance-cycle | a capability process starts where performance management ends, and a performance improvement plan sits on the line. Where a formal procedure, a hearing or a right to be accompanied is invoked this entry leads | §3.7 “It should rank candidate matches instead of accepting the first match” |
| hr.offboarding | a dismissal produces both a case file and a leaver record | §4.9 “A file may validly belong to more than one accepted group” |
| career.layoff-and-severance | the nearest mirror the career slice offers: it has no grievance or disciplinary domain of its own, so an employee's copy of a dismissal, settlement or severance lands there while their copy of a grievance lands nowhere. Both copies are sensitive and neither slice should hold the other's | §3.8 “The system must separate roles that happen to contain the same entity type” |
| hr.health-safety | an incident investigation may become a disciplinary. The two processes run on one set of facts | §3.11 “One file may hold facts from more than one domain without losing information” |

### Sensitivity

`potentially_sensitive` — This is the most sensitive domain in the slice: allegations, evidence and findings about named individuals, frequently touching health, conduct and, where a claim follows, legal matters. §8.4's corpus list is “identity documents, account statements, tax records, medical information, legal records, credentials, private correspondence, GPS metadata, employment materials, and educational records” and this domain touches employment, legal and sometimes medical material at once; it requires that “Paths, complete extracted text, OCR output, file hashes, image EXIF, GPS, user edits, group memberships, and raw sensitive values should remain local”. §3.15's “Finance, identity, medical, and legal material should be implemented first as safety domains, meaning the system detects and protects them before any cloud or automated placement decision is allowed” describes the posture that should govern it. The marking is the strongest this catalogue can make and no handling class is assigned, because that is P7's (§8.4).

### Open question — Joseph's call, unresolved

> There is no `hr.personnel-file` entry in this catalogue, and there probably should be one somewhere: the employer's per-employee file is the natural home for contracts, pay letters, training records, reviews and case outcomes about one person. This slice deliberately declines to create it, because a per-person folder is exactly what §3.8's “It should avoid using authorship or creator identity as a destination dimension” warns against and because it collides head-on with the career slice, which holds the same documents from the individual's own side. Whether the product should model an employer-held personnel file at all — and if so, which slice owns it — is Joseph's call and it is left open rather than resolved by omission.

---

## `hr.health-safety` — Workplace health and safety administration

The employer's duty of care as an administered function — risk assessments, safe systems of work, incidents, inspections and statutory reporting.

**Provenance:** **proposal** — new here; the design names nothing like it

**Cite:** No design sentence names workplace health and safety. §3.15 “Other domains remain placeholders until user demand and corpus evidence justify detailed templates” permits the addition. The health slice's `med.occupational-health-screening` owns clinical occupational health; this entry is the safety-management function and defers to it on anything clinical.

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `employing_organisation` | string | Northwind Logistics | `validated` | the duty holder |
| `site` | string | Bermondsey depot | `validated` | where. Shared with `ops.facilities-workplace` deliberately — an inspection is of a place |
| `hazard_or_activity` | string | manual handling in the pick face | `validated` | what is assessed. It is the grouping key for assessments and the thing controls attach to |
| `record_type` | string | risk assessment | `validated` | risk assessment, method statement, permit, inspection, incident report, statutory notification, training record |
| `incident_reference` | string | INC-2026-118 | `direct` | §3.13 direct: a labeled incident number, which is the only safe anchor for incident material because the alternative is a person's name |
| `reportable_status` | string | reportable to the regulator | `validated` | whether an incident triggers statutory reporting. It is jurisdiction-defined and it decides retention |
| `review_due_date` | date | 2027-01-15 | `direct` | §3.13 direct: a labeled review or re-inspection date |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.3, §3.5):

- a safety-artifact term ('risk assessment' | 'method statement' | 'safe system of work' | 'permit to work' | 'toolbox talk' | 'accident book' | 'near miss' | 'COSHH assessment') co-occurring with a named site or employer AND a hazard or activity description
- an incident-record structure — an incident reference co-occurring with a date and time label, a location and an injury or damage category
- a statutory-reporting term ('reportable incident' | 'notification to the regulator' | 'improvement notice' | 'prohibition notice') co-occurring with a named employer and a site

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- an incident described in an email with no form
- reportable status, which is a legal judgement and jurisdiction-specific
- separating a safety incident from a security incident (software slice) or an operational one (`ops.retrospective-postmortem`) when the report says only 'incident'

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10, §4.9):

- 'safety' | 'health' | 'incident' | 'accident' | 'hazard'. 'Health' belongs to the health slice entirely — a bare rule here would claim personal medical records, which is the most damaging mis-route available in this catalogue; 'incident' belongs to `soft.incident-postmortem` and to support operations; 'accident' is a motor claim in the personal and finance slices
- 'risk assessment' — `ops.risk-register` in this slice, and clinical risk assessment in the health slice
- 'inspection' — a building inspection, a vehicle inspection (personal slice's `pers.vehicle`), a regulatory inspection (finance slice), a code inspection
- 'injury' | 'first aid' — these route to the health slice by default and this entry must corroborate with an employer and a site before claiming them
- 'permit' — the finance slice has `admin.licences-permits`; a permit to work is a different object entirely
- an injured person's name — §3.8 “It should avoid using authorship or creator identity as a destination dimension” and §8.4 requires personal values stay local; health data attaches to it

### Work types

`risk assessment`, `method statement`, `permit to work`, `inspection record`, `toolbox talk record`, `incident or near-miss report`, `investigation report`, `statutory notification`, `safety policy`, `training and competence record`

### Grouping reasons (§4)

- one hazard or activity across its assessment, controls and reviews
- one incident across its report, investigation, notification and actions
- one site across an inspection cycle

### Template (§5)

`site → record type → year`

Time first: **no**

§5.5: “a parent dimension should provide the context required to understand the child”. A risk assessment is meaningful once its site is known. §5.5's “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders” puts the year last, and it earns a level because safety records are retained on statutory cycles and accumulate. No per-person level exists, for the §3.8 reason and because injury records attach health data to a name.

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| med.occupational-health-screening | an occupational health referral and its report are clinical records about an employee. The health slice owns them and this entry must defer, because their treatment is stricter and losing it would be the worst error available here | §3.15 “Finance, identity, medical, and legal material should be implemented first as safety domains, meaning the system detects and protects them before any cloud or automated placement decision is allowed” |
| ops.facilities-workplace | inspections, permits and site records sit in both. A hazard, an injury or a regulator routes a file here | §3.7 “It should rank candidate matches instead of accepting the first match” |
| ops.risk-register | a safety risk register is both. The hazard vocabulary and the site route it here | §3.11 “One file may hold facts from more than one domain without losing information” |
| hr.employee-relations | an incident investigation can become a disciplinary on the same facts | §4.9 “A file may validly belong to more than one accepted group” |
| hse.incident-record | the engineering slice authored a workplace incident entry — someone was hurt, or nearly was — templated site then year then artifact type, which is this entry's template. Where an industrial site or a manufacturing context is present that entry has the stronger claim, and this one should defer rather than compete | §3.6 “that each fact or label belongs to an allowed domain schema” |
| soft.incident-postmortem | 'incident' means a service outage there and a workplace injury here; the word alone routes to neither | §3.11 “Code files may use project, repository, programming language, and artifact type” |

### Sensitivity

`potentially_sensitive` — Incident and injury records attach health information to named individuals, and §8.4's corpus list “identity documents, account statements, tax records, medical information, legal records, credentials, private correspondence, GPS metadata, employment materials, and educational records” names medical information and employment materials side by side. §3.15 “Finance, identity, medical, and legal material should be implemented first as safety domains, meaning the system detects and protects them before any cloud or automated placement decision is allowed” puts medical material in the safety-domain category, and an injury report is medical material about an employee. No handling class is assigned; that is P7's (§8.4).

---
