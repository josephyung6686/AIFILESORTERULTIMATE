# Domain catalogue — trades, construction, property, retail, hospitality, logistics and energy

Supercategory: `trades-property-logistics`  
Slice: 13  
Entries: 56 — 0 design, 16 inference, 40 proposal  
Contract: [`_CONTRACT.md`](_CONTRACT.md) · Source of truth: [`00-database-agent-product-design.md`](../00-database-agent-product-design.md)

## How to read this file

- **Curly double quotes are verbatim quotations** from the source of truth and nothing else. Every one is checked by a literal substring test at build time and a fabricated span fails the build. Where a claim is mine rather than the design's it is written as plain prose with no quote marks.
- **Single quotes are pattern literals** — tokens a recogniser looks for in a document — following the convention in the contract's own worked example.
- `reliability_ceiling` uses §3.13's six states only. `direct` means a labeled field, a document title or explicit metadata. `validated` means a rule found a pattern **and** passed a context check, so every `validated` field below has a matching `recognition.deterministic` line that could actually confirm it. `llm_supported` means the value needs language interpretation and cannot be produced without the model route.
- `sensitivity` is §2.9's phrase `potentially sensitive` and nothing more. No handling class is assigned anywhere in this file; handling classes are P7's (§8.4).
- No thresholds, no scores, no counts, no intervals. Digits appear only inside `example` values, which are data in the same way the contract's own `BUSIB 4300` is.
- **No entry in this slice is `design`.** The design names its exemplars — “The initial release should fully support only the domains required to validate the product on real heterogeneous corpora: academic coursework, college applications, research and lab work, career and recruiting, photos and captures, and code projects.” — and not one domain here is among them. Every entry is therefore `inference` (it extends a design-named domain or a design-named template situation) or `proposal` (it is new).

## Four findings that apply to the whole slice

**1 — The working document and the accounting record are different domains, and this is where the first of the two lives.**
A tradesperson's quote and the finance slice's record of the same transaction are not two views of one thing; they are two objects with different lifecycles. The quote is *pre-transactional*: it is addressed to someone who may never become a customer, it carries a site and a schedule of works and a validity clause, it is revised until it is accepted or abandoned, and it never enters a ledger. The accounting record is *post-transactional*: it carries a sequence number, a tax point, a tax breakdown and a payment-terms block, it is immutable once issued, and it belongs to a period rather than to a job. **The discriminating markers are positive on both sides** — a validity clause and a site address say working document; a sequence number and a tax point say accounting record — which means the engine can separate them by rule rather than by guessing. The same reasoning runs through the whole slice: purchase order and delivery note against supplier invoice; hire contract and off-hire notice against hire invoice; payment application and payment certificate against the invoice raised from them; Z read against the banking posting; meter reading against the utility bill. Where a single file carries both sets of markers, §3.11 is explicit that it keeps both fact sets — “One file may hold facts from more than one domain without losing information.” — and “At the pre-sorting stage, the product does not need to decide which of those perspectives will ultimately determine its physical location.”. The physical path is a separate question and is raised as an open question on `cons.final-account`.

**2 — Capture-based media is everywhere in this slice, and it is almost never time-first.**
Site progress photographs, defect photographs, survey sets, inventory sets, delivery captures, meter photographs, food-safety logs photographed off paper: a large fraction of this material is images. §5.5 grants exactly one exception to the record-domain ordering rule — “Photos and capture-based media are the major exception: time often belongs first because capture date is a defining aspect of the material.” — and the exception is **conditional on its own premise**. It applies where the capture date is what the file is *about*. It does not apply where a photograph was taken *for* something that has its own identity: a defect photograph is about a defect, an inventory photograph is about a tenancy, a survey photograph is about a site. Two entries meet the condition and are marked `time_first: true`; every other capture-bearing entry is justified individually where it sits. §2.6's warning governs all of them — “the system must not mistake the absence of EXIF for proof that an image is a screenshot” — and a great deal of this material arrives through messaging apps with its metadata stripped.

**3 — Reference numbers are the strongest signals here and the most dangerous.**
Job numbers, project numbers, drawing numbers, order numbers, consignment numbers, meter numbers, well identifiers, parcel identifiers, SKUs. Every one of them is a digit-and-letter string that identifies something precisely — and every one shares a shape with three or four others in the same document. §3.5 supplies the only safe model, and this file applies it without exception: a code becomes a fact only “when the engine finds a course-code pattern together with academic context”, and the design's own worked instance names the corroborating terms it requires. Every `recognition.deterministic` line below names the corroborating context, and every bare code appears in `never_alone`. §3.10's warning is live throughout — “The product must not use fuzzy date parsing because file names and documents frequently contain numbers that look like years but are course identifiers, version numbers, build numbers, ZIP codes, or other unrelated values.” — and job numbers are precisely such values.

**4 — Jurisdiction is undecided, and it bites harder here than anywhere.**
Certificate schemes, building-control regimes, licensing regimes, tenure categories, customs and tariff schedules, driver-hours rules, land-parcel identification, extraction and felling permissions, fisheries management areas: all jurisdiction-defined, and several are not translations of one another but genuinely different objects. **This catalogue names no scheme, no standard, no form number, no regime and no statutory interval anywhere.** Inventing one would be worse than leaving a recogniser structural, because a wrong scheme name is a confident false positive on someone's safety or compliance records. The cost is real: these domains can be recognised by document *shape* but not by *name* until the question is answered. It is raised as the primary open question on five entries — `cons.project`, `cons.building-control`, `trade.compliance-certificate`, `hosp.premises-licensing`, `log.customs-export` — and named again on a sixth.

## Index

| id | name | provenance | time first | sensitivity |
|---|---|---|---|---|
| `trade.job` | Trade job (branch root) | inference | no | potentially sensitive |
| `trade.quote-estimate` | Job quotes, estimates and tenders (working document) | inference | no | — |
| `cons.site-survey` | Site surveys and measured surveys | proposal | no | potentially sensitive |
| `cons.project` | Construction project (branch root) | inference | no | — |
| `cons.drawings-revisions` | Drawings, models and revision control | proposal | no | — |
| `cons.subcontract` | Subcontractor engagement and management | inference | no | potentially sensitive |
| `cons.site-diary` | Site diaries and daily reports | proposal | no | — |
| `cons.progress-photos` | Site progress photography | inference | **yes** | potentially sensitive |
| `cons.snagging` | Snagging, defects and handover lists | proposal | no | — |
| `cons.building-control` | Building control, planning and statutory inspection | proposal | no | — |
| `trade.compliance-certificate` | Installation and compliance certificates | proposal | no | — |
| `cons.method-statement-ra` | Health and safety documentation | proposal | no | potentially sensitive |
| `cons.plant-hire` | Plant and equipment hire | proposal | no | — |
| `cons.materials-delivery` | Materials ordering and delivery notes | inference | no | — |
| `trade.timesheet` | Labour timesheets and site attendance | proposal | no | potentially sensitive |
| `cons.variation-claim` | Variations, instructions and claims | proposal | no | — |
| `cons.final-account` | Valuations, retention and final accounts | inference | no | — |
| `prop.sale-purchase` | Residential sale and purchase | inference | no | potentially sensitive |
| `prop.tenancy` | Lettings and tenancy management | inference | no | potentially sensitive |
| `prop.inventory-inspection` | Property inventories and condition inspections | inference | no | potentially sensitive |
| `prop.service-charge` | Service charges and leaseholder accounts | proposal | no | potentially sensitive |
| `prop.block-management` | Block and estate management | proposal | no | potentially sensitive |
| `prop.commercial-lease` | Commercial leases and occupier management | inference | no | potentially sensitive |
| `prop.development-appraisal` | Property development appraisals | proposal | no | — |
| `prop.survey-valuation` | Property surveys and valuations | proposal | no | potentially sensitive |
| `prop.listing` | Estate agency listings and property marketing | proposal | no | — |
| `prop.mortgage-brokering` | Mortgage and property finance brokering | inference | no | potentially sensitive |
| `retail.product-catalogue` | Product catalogue and merchandising | proposal | no | — |
| `retail.stocktake` | Inventory and stock takes | proposal | no | — |
| `retail.supplier-order` | Supplier and wholesale ordering | inference | no | — |
| `retail.pos-reporting` | Point-of-sale and trading reporting | proposal | no | — |
| `retail.ecommerce-ops` | E-commerce operations | proposal | no | potentially sensitive |
| `retail.returns-warranty` | Returns, refunds and warranty claims | proposal | no | potentially sensitive |
| `retail.store-ops` | Store and site operations | proposal | no | potentially sensitive |
| `hosp.menu-recipe-costing` | Menu development and recipe costing | proposal | no | — |
| `hosp.food-safety` | Food safety and hygiene records | proposal | no | potentially sensitive |
| `hosp.premises-licensing` | Premises licensing and permissions | proposal | no | potentially sensitive |
| `event.production` | Event production and delivery | proposal | no | potentially sensitive |
| `hosp.bookings` | Bookings and reservations | inference | no | potentially sensitive |
| `hosp.catering-contract` | Catering contracts and function delivery | proposal | no | potentially sensitive |
| `hosp.guest-feedback` | Guest feedback, reviews and complaints | proposal | no | potentially sensitive |
| `log.shipment` | Freight consignments and shipping documentation | proposal | no | — |
| `log.customs-export` | Customs, export and trade compliance | proposal | no | — |
| `fleet.vehicle` | Fleet and vehicle records | proposal | no | — |
| `fleet.driver-compliance` | Driver records and compliance | proposal | no | potentially sensitive |
| `log.route-dispatch` | Route planning and dispatch | proposal | no | potentially sensitive |
| `log.warehouse-ops` | Warehouse and depot operations | proposal | no | — |
| `log.last-mile-pod` | Last-mile delivery and proof of delivery | inference | **yes** | potentially sensitive |
| `util.metering-billing` | Utility metering and billing operations | inference | no | potentially sensitive |
| `energy.renewable-generation` | Renewable generation records | proposal | no | — |
| `energy.grid-connection` | Grid connection and network agreements | proposal | no | — |
| `energy.oil-gas-ops` | Oil and gas operations | proposal | no | — |
| `mining.ops` | Mining and quarrying operations | proposal | no | — |
| `agri.farm-records` | Agriculture and farm records | proposal | no | — |
| `fish.catch-records` | Fisheries and catch records | proposal | no | — |
| `forest.records` | Forestry and woodland records | proposal | no | — |

`time_first: true`: 2 of 56 — `cons.progress-photos`, `log.last-mile-pod`. 
`potentially_sensitive`: 27 of 56. 
Open questions: 9 — `trade.job`, `cons.project`, `cons.progress-photos`, `cons.building-control`, `trade.compliance-certificate`, `cons.final-account`, `hosp.premises-licensing`, `log.customs-export`, `energy.oil-gas-ops`.

---

## `trade.job` — Trade job (branch root)

One piece of work for one client at one site — the unit a tradesperson quotes, schedules, works, photographs and invoices.

**Provenance:** **inference** — extends a design-named domain or template situation; the cite supports the extension, not the whole entry

**Cite:** Extends §5.7's named template situation “The product should eventually maintain a library of roughly 200–300 domain-specific templates, covering common organizational situations such as academic programs, university applications, recruiting processes, client engagements, research workflows, financial records, travel, legal matters, creative projects, software repositories, personal administration, and photo collections.” — a trade job is the domestic-scale client engagement, and this entry supplies the two halves §3.15 requires of any domain: “Each domain consists of two related definitions: a fact schema describing the information the system may extract from files in that domain, and a folder template describing the small subset of those facts that may become physical folder levels.”

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `job_reference` | string | J-2481 | `validated` | The job number is this domain's strongest identifier and its most over-firing one. §3.5 supplies the only safe model: a code becomes a fact only “when the engine finds a course-code pattern together with academic context” — so a job reference is a fact only beside trade-job language, never on its own. |
| `client` | string | Mr and Mrs Adeyemi | `validated` | §3.8: “The system must separate roles that happen to contain the same entity type.” The client who commissions the work, the occupier who lets the engineer in, the landlord who pays and the supplier who delivers to the same address are four roles, and a trade document routinely names more than one. |
| `site_address` | string | 14 Elm Road, Flat 2 | `validated` | The site is this domain's subject, not its metadata: the same client can hold several sites and the same site can pass between clients. §3.8 keeps it distinct from the client's billing address, which is a different role in the same document. |
| `trade` | string | electrical | `validated` | The working discipline. It is the field that separates two jobs at one address on one day, and it is what makes a certificate, a method statement or a materials list interpretable. |
| `job_status` | string | completed | `llm_supported` | §3.13: “An LLM-supported fact was proposed by a language model from a bounded evidence packet, cited exact supporting text or metadata, and passed deterministic validation.” Status is stated in prose far more often than in a labeled field ('all works now complete', 'awaiting parts'), so a rule cannot reach it safely. |
| `job_dates` | date range | 2026-03-02 to 2026-03-06 | `direct` | §3.13: “A direct fact was read from a reliable and explicit source, such as a content hash, EXIF timestamp, document title, or labeled form field.” §3.10 forbids the fuzzy route: “The product must not use fuzzy date parsing because file names and documents frequently contain numbers that look like years but are course identifiers, version numbers, build numbers, ZIP codes, or other unrelated values.” — a job reference is exactly the kind of number that looks like a year. |
| `work_type` | string | quotation | `validated` | The work-type analogue for this branch, and the level §5.5 says is only meaningful once the job is known. |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.3, §3.5):

- a job-reference pattern co-occurring with trade-job context — 'job no' | 'job ref' | 'works order' | 'call-out' | 'labour and materials' | 'site address' — the pattern alone is never sufficient
- a labeled site-address block ('site address' | 'address of works' | 'property address') co-occurring with a separately labeled client block ('customer' | 'client' | 'bill to'), which is what distinguishes a trade document from a letter that merely has an address on it
- a trade-discipline term matched on a word boundary ('electrical' | 'plumbing' | 'roofing' | 'joinery' | 'plastering' | 'glazing') together with a job reference or a labeled site address

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- a photographed or scanned handwritten job sheet where the reference, the client and the works description sit in one unlabelled block and only prose separates them
- a message or email thread that establishes the job in conversation — 'can you come back and finish the second bedroom' — with no reference anywhere
- a document that names two addresses and states which is the site only in a sentence

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10):

- a bare job reference — the shape of 'J-2481' is indistinguishable from an invoice number, an order number, a part number and a case reference
- a postal address alone: in one trade document an address can be the site, the client's billing address, the supplier's depot and the issuer's registered office
- a person's name alone — §3.8: “It should avoid using authorship or creator identity as a destination dimension.” and the tradesperson's own name is on every document they produce
- a trade word found inside a longer word — §3.7: “It should use word-boundary matching rather than substring matching.” ('gas' inside 'Glasgow', 'tile' inside 'volatile')

### Work types

`quotation`, `job sheet`, `works order`, `site photograph set`, `certificate`, `invoice`, `variation`, `client correspondence`

### Grouping reasons (§4)

- one job at one site for one client, across quote, job sheet, photographs, certificate and invoice
- one client's repeat jobs at one site over time
- one job's document versions — quote v1, v2, v3 — as a version family

### Template (§5)

`client → job → work type`

Time first: **no**

§5.5: “a parent dimension should provide the context required to understand the child” — a work type such as a certificate is meaningless until the job is known, and a job reference is ambiguous until the client or site is. §5.5 also keeps time out of the lead for a record domain: “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders.” A single-site trade business may collapse the client level entirely; §5.8 expects that — “The canvas must support uneven depth because real file trees are not and should not be perfectly symmetrical.”

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| trade.quote-estimate | the quote is one work type inside a job, not a separate branch; it becomes its own domain only when it never converted, because an unconverted quote has no job to sit under | §3.9: “Topic answers what a file is about, while purpose answers what the file was for.” — the quote's purpose is to win the work, the job file's purpose is to record the work |
| cons.project | scale and structure, not subject matter: a job has one client, one site and one trade and needs no phase level; a project has packages, phases and a chain of subcontracts. A file naming a work package or a contract sum belongs to the project domain | §5.8: “each branch should offer the dimensions that are actually present in its member groups and show what each split would create” |
| biz.invoice-issued | THE WORKING-DOCUMENT / ACCOUNTING-RECORD BOUNDARY. The same PDF is a job document and a ledger entry. A job's invoice carries a site address and a schedule of works; the accounting record of it carries a sequence number, a tax point and a tax-year label. The catalogue keeps both fact sets rather than choosing | §3.11: “One file may hold facts from more than one domain without losing information.” and “At the pre-sorting stage, the product does not need to decide which of those perspectives will ultimately determine its physical location.” |
| ops.client-engagement | a professional-services engagement and a trade job are the same commercial shape — a client, a scope, a fee — and differ in that a trade job has a site and a physical work type. The site is the discriminator | §3.9: “Topic answers what a file is about, while purpose answers what the file was for.” |

### Sensitivity

`potentially_sensitive` — §2.9's phrase “while treating addresses and message content as potentially sensitive” is the only marking made here. A domestic job file routinely carries site access credentials — key-safe codes, alarm codes, gate codes — and geotagged photographs of the inside of a private home. §8.4 names both categories in the corpus this product handles: “identity documents, account statements, tax records, medical information, legal records, credentials, private correspondence, GPS metadata, employment materials, and educational records”. The handling CLASS is P7's (§8.4) and is not set.

### Open question — Joseph's call, unresolved

> Is work material in scope at all? The design describes a personal corpus — §8.4 “identity documents, account statements, tax records, medical information, legal records, credentials, private correspondence, GPS metadata, employment materials, and educational records” — and §3.15 names the launch domains as “The initial release should fully support only the domains required to validate the product on real heterogeneous corpora: academic coursework, college applications, research and lab work, career and recruiting, photos and captures, and code projects.”, none of which is a trade. But a sole trader's laptop holds their job files and their personal files in one Documents folder and the product cannot see the difference. Joseph decides whether this whole supercategory is live or is one of the “Other domains remain placeholders until user demand and corpus evidence justify detailed templates.”. SECOND: may a private residential address become a folder label? The site is the natural top dimension for every trades and property domain in this slice, and it is also third-party personal data that will appear in Finder, in Spotlight and in any backup. This catalogue puts the client above the site to keep the address off the top level, but that is a holding position, not a decision.

---

## `trade.quote-estimate` — Job quotes, estimates and tenders (working document)

Priced proposals for work not yet done — the pre-transactional document, revised until it is accepted, declined or forgotten.

**Provenance:** **inference** — extends a design-named domain or template situation; the cite supports the extension, not the whole entry

**Cite:** Extends the Finance schema §3.11 “Finance files may use institution, account type, tax year, and record type.” by contradiction: a quote has no institution, no account and no tax year, which is precisely what distinguishes it from the accounting record of the same transaction. Extends §5.7's “The product should eventually maintain a library of roughly 200–300 domain-specific templates, covering common organizational situations such as academic programs, university applications, recruiting processes, client engagements, research workflows, financial records, travel, legal matters, creative projects, software repositories, personal administration, and photo collections.”

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `client` | string | Northgate Dental Practice | `validated` | §3.8: “The system must separate roles that happen to contain the same entity type.” On a quote the addressee is a prospect, not yet a customer, and the issuer is the tradesperson — the same document names both organisations. |
| `site_address` | string | Unit 4, Northgate Retail Park | `validated` | The works location, which is frequently not the addressee's own address. |
| `quote_reference` | string | Q-1180 | `validated` | §3.5's rule applies unchanged: a reference is a fact only “when the engine finds a course-code pattern together with academic context” — here the corroborating context is quote language, not academic language. |
| `quote_status` | string | accepted | `llm_supported` | Whether a quote converted is almost never a labeled field; it is stated in a covering email or inferred from a later job document. §3.13: “An LLM-supported fact was proposed by a language model from a bounded evidence packet, cited exact supporting text or metadata, and passed deterministic validation.” |
| `validity_period` | date range | valid for 30 days from 2026-02-11 | `direct` | §3.13: “A direct fact was read from a reliable and explicit source, such as a content hash, EXIF timestamp, document title, or labeled form field.” A validity clause is a labeled field and is the single most reliable positive marker that a document is a quote rather than an invoice. |
| `scope_summary` | string | supply and install 12 LED panels, second fix only | `llm_supported` | The schedule of works is prose and its summary requires language interpretation. §3.5 bounds it: “It can only propose facts that belong to the active domain schema, and it must cite exact supporting evidence already extracted from the file.” |
| `quote_total` | string | as printed on the document | `direct` | §3.11 permits “Each domain activates only a small set of relevant fields, usually three to six that may help build a future folder proposal and several additional fields used only for search, privacy protection, explanation, or later review.” — the total is a search and explanation field. It is never a folder dimension and this catalogue holds no value for it. |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.3, §3.5):

- a quote-language term ('quotation' | 'estimate' | 'tender' | 'proposal' | 'we are pleased to quote') in a filename, document title or page-one heading, co-occurring with a priced schedule of works or a labeled validity clause — §2.2 makes the zone matter: “A course code or university name found in a filename, title, or page-one heading is more meaningful than the same text appearing once in a reference list on page eighteen.”
- a validity clause ('valid for' | 'this quotation expires' | 'subject to survey') co-occurring with a client block and a works description — the strongest single positive marker in this domain
- an explicit absence pair: quote language present AND no invoice-number label, no tax-point label and no payment-terms block anywhere in the document

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- a priced document that never uses the word quote and must be read as a proposal from its tense — 'we would install', 'the works would comprise'
- a revision that is a quote for the same works at a new price, where only prose distinguishes it from a variation to an accepted quote
- an email body that is itself the quote, with the price in a sentence and no attachment

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10):

- a currency amount — a price appears on quotes, invoices, statements, purchase orders, delivery notes and price lists alike
- a bare quote reference; the same shape numbers invoices and orders in most small-business software
- the word 'estimate' in prose — it is ordinary English ('a rough estimate of the damage') as well as a document type
- a client name alone — §3.8: “A folder should not become a collection point for everything produced by the same person or organization.”

### Work types

`quotation`, `estimate`, `budget costing`, `tender submission`, `schedule of rates`, `covering letter`, `revised quotation`

### Grouping reasons (§4)

- one enquiry across its quote revisions, as a version family
- one tender across its submission documents — pricing schedule, method statement, references
- all unconverted quotes for one client

### Template (§5)

`client → enquiry or job → revision`

Time first: **no**

§5.5: “a parent dimension should provide the context required to understand the child” — a revision number means nothing without the enquiry it revises. An unconverted quote has no job to live under, which is why this is a domain and not merely a work type. §5.9 warns against the alternative of a per-quote folder: “It should warn when a level produces only one child, repeats a concept already expressed in the parent, creates excessive depth, or creates a large number of tiny folders.”

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| trade.job | a converted quote belongs inside the job file; an unconverted one has nowhere else to go. The converting signal is a later document sharing the client and site and carrying a job reference | §4.9: “A course code alone should not merge different semesters; course packet identity should include a term when it is available.” — the same shape of error: one client's name must not merge two separate enquiries |
| biz.invoice-issued | THE BOUNDARY, stated positively. A quote is pre-transactional: no invoice number, no tax point, no payment-terms block, and a validity clause instead. The accounting record is post-transactional: a sequence number, a tax point, a tax breakdown and a period it falls into. Where a document carries both sets of markers it is a proforma and the finance slice's claim is the stronger one | §3.11: “One file may hold facts from more than one domain without losing information.” |
| cons.variation-claim | a price for extra work on a job already under way is a variation, not a quote; the distinguishing signal is a reference to an existing job or contract that the priced work amends | §4.8: “that each fact or label belongs to an allowed domain schema” |
| ops.sourcing-rfp | two halves of one process held by different parties: the buyer's tender pack and the supplier's tender submission. A file holding evaluation criteria and scored responses is the buyer's; a file holding a priced schedule and a validity clause is the supplier's | §3.8: “The system must separate roles that happen to contain the same entity type.” |

### Sensitivity

`none` — A quote's subject is work, not a person. It carries a client name and a site address as commercial context, and none of §8.4's named categories routinely appears in it. Where a quote sits inside a domestic job file, that job's “while treating addresses and message content as potentially sensitive” marking governs the packet. §8.4's classification is evidence-backed and revisable per file, so a specific quote can still be protected on its own evidence. No handling class is set here; that is P7's.

---

## `cons.site-survey` — Site surveys and measured surveys

The record of what was found at a site before work was designed or priced — measurements, conditions, existing services and the photographs that evidence them.

**Provenance:** **proposal** — new — the design does not name this domain, and nothing here is asserted as the design's

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `site_address` | string | Old Mill House, Bakers Lane | `validated` | The survey's subject. A survey without a site is not a survey. |
| `survey_type` | string | measured building survey | `validated` | What was surveyed and by what method. It is the field that separates a structural inspection, an asbestos survey, a measured survey and a services survey of the same building on the same day. |
| `survey_date` | date | 2026-01-19 | `direct` | §3.13: “A direct fact was read from a reliable and explicit source, such as a content hash, EXIF timestamp, document title, or labeled form field.” A survey is a statement about a moment, so the date is part of its identity rather than filing metadata. §3.10's explicit-regex path only: “The product must not use fuzzy date parsing because file names and documents frequently contain numbers that look like years but are course identifiers, version numbers, build numbers, ZIP codes, or other unrelated values.” |
| `surveyor` | string | R. Okafor | `direct` | Recorded because a survey is signed, not because it is a folder dimension. §3.8: “It should avoid using authorship or creator identity as a destination dimension.” |
| `client` | string | Harrow Estates Ltd | `validated` | §3.8's role separation: the commissioning client, the site owner and the occupier are three roles that a survey report routinely names together. |
| `findings_summary` | string | single-skin rear wall, no cavity insulation | `llm_supported` | The substance of a survey is prose and tables. §3.5 bounds what the model may return: “It can only propose facts that belong to the active domain schema, and it must cite exact supporting evidence already extracted from the file.” |
| `capture_time` | date | 2026-01-19 | `direct` | §2.6: “Camera EXIF, GPS, and capture time can support deterministic photo-event proposals.” — the survey photograph set carries its own EXIF timestamps, which corroborate the report's stated date and can recover it when the report itself is undated. |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.3, §3.5):

- a survey-document term ('site survey' | 'survey report' | 'schedule of condition' | 'measured survey' | 'condition report') in the filename, title or page-one heading, co-occurring with a labeled site address — §2.2: “A course code or university name found in a filename, title, or page-one heading is more meaningful than the same text appearing once in a reference list on page eighteen.”
- a labeled surveyor and survey-date pair co-occurring with a site address block, which is the signature structure of a survey report
- a photograph set whose EXIF GPS clusters at one location within one day, co-occurring with a document naming that address as a site — §2.6: “Camera EXIF, GPS, and capture time can support deterministic photo-event proposals.”

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- a set of photographs and a dimension sketch with no report, where only the content shows this is a pre-works survey and not progress photography
- a report whose survey type must be read from its methodology section because its title says only 'report'
- an OCR'd handwritten measurement sheet

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10):

- the word 'survey' alone — it is also a questionnaire, a land registry term and a market-research artefact
- GPS coordinates alone: §2.6 warns that photograph metadata is a hierarchy of signals, not a conclusion — “The system should therefore use a hierarchy of signals: camera EXIF is strong photo evidence; capture time, GPS, and sensor-shaped dimensions reinforce it; exact display resolutions, PNG format, and software metadata may support a screenshot hypothesis; conflicting signals should lead to abstention rather than an invented classification.”
- a dimension-looking string ('4.2m x 3.1m'), which appears in listings, drawings, delivery notes and product specifications
- a person's name in a document footer — §3.8: “It should avoid using authorship or creator identity as a destination dimension.”

### Work types

`survey report`, `schedule of condition`, `measurement sheet`, `survey photograph set`, `existing-conditions drawing`, `asbestos or services survey`, `site sketch`

### Grouping reasons (§4)

- one survey visit — report, sketches and the photograph set captured the same day at the same location
- successive surveys of one site over time
- a survey and the quote or design it fed

### Template (§5)

`site → survey date → survey type`

Time first: **no**

§5.5: “a parent dimension should provide the context required to understand the child” — a survey type is only interpretable once the site is known. The date sits above the type rather than below it because a site is surveyed repeatedly and two survey types on one visit belong together. Time does not lead: §5.5's capture exception is granted for a reason that does not apply, because the survey's subject is the site and the photographs are its evidence rather than its point — “Photos and capture-based media are the major exception: time often belongs first because capture date is a defining aspect of the material.”

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| cons.progress-photos | both are geotagged photograph sets at one address. The survey set predates the works and shows existing conditions; the progress set is taken during them. The separating signal is a companion document — a survey has a report, progress photography does not | §2.6: “The system should therefore use a hierarchy of signals: camera EXIF is strong photo evidence; capture time, GPS, and sensor-shaped dimensions reinforce it; exact display resolutions, PNG format, and software metadata may support a screenshot hypothesis; conflicting signals should lead to abstention rather than an invented classification.” |
| prop.survey-valuation | a construction site survey measures a building to design or price work on it; a valuation survey prices the building itself for a lender or a buyer. The separating signal is a valuation figure and a lender reference, which a measured survey never carries | §3.9: “Topic answers what a file is about, while purpose answers what the file was for.” |
| prop.inventory-inspection | a schedule of condition for construction and a check-in inventory for a tenancy are the same artefact for different purposes. The separating signal is a tenancy reference or a tenant name | §3.9: “The documents are content-incoherent but purpose-coherent.” |

### Sensitivity

`potentially_sensitive` — §2.9's phrase “while treating addresses and message content as potentially sensitive” and nothing more. A survey photograph set is geotagged to a private address and routinely photographs the inside of an occupied home, including possessions. §8.4 names “identity documents, account statements, tax records, medical information, legal records, credentials, private correspondence, GPS metadata, employment materials, and educational records” — GPS metadata is on that list explicitly. The handling class is P7's and is not set here.

---

## `cons.project` — Construction project (branch root)

A construction contract from award to final account — the container that gives every drawing, instruction, valuation and diary entry its meaning.

**Provenance:** **inference** — extends a design-named domain or template situation; the cite supports the extension, not the whole entry

**Cite:** Extends §5.7's named “The product should eventually maintain a library of roughly 200–300 domain-specific templates, covering common organizational situations such as academic programs, university applications, recruiting processes, client engagements, research workflows, financial records, travel, legal matters, creative projects, software repositories, personal administration, and photo collections.” to the construction case, and supplies both halves §3.15 requires: “Each domain consists of two related definitions: a fact schema describing the information the system may extract from files in that domain, and a folder template describing the small subset of those facts that may become physical folder levels.”

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `project` | string | Riverside Phase 2 | `validated` | The project name is the branch root and the parent §5.5 requires for everything beneath it. |
| `project_number` | string | P-2214 | `validated` | §3.5's model applies exactly: a project number is a fact only “when the engine finds a course-code pattern together with academic context” — here the corroborating context is contract language. Project numbers, order numbers and drawing numbers share a shape. |
| `site_address` | string | Riverside Way, Unit 2-8 | `validated` | Distinct from the project name: one project can run across several addresses and one address can host several projects over years. |
| `client` | string | Meridian Developments | `validated` | §3.8: “The system must separate roles that happen to contain the same entity type.” A construction document names the employer, the contractor, the architect, the engineer and the subcontractor — five organisations, five roles, one document. |
| `contract_type` | string | design and build | `llm_supported` | The procurement route governs what documents can exist. It is stated in prose in the contract particulars rather than in a labeled field. Contract form names are jurisdiction-specific — see the open question. |
| `project_stage` | string | construction | `llm_supported` | Stage names differ by jurisdiction and by professional body, so this is written functionally. §3.5: “It can only propose facts that belong to the active domain schema, and it must cite exact supporting evidence already extracted from the file.” |
| `work_package` | string | M and E | `validated` | The package is the level below the project and above the document, and it is how a large project's file is actually navigated. |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.3, §3.5):

- a project-number pattern co-occurring with construction-contract context — 'the employer' | 'the contractor' | 'contract sum' | 'practical completion' | 'the works' | 'variation' — the number alone is not a fact
- a labeled employer-and-contractor pair, which is the signature of a construction document and appears in no other domain in this slice
- a project name repeated in the filename and in a page-one heading, co-occurring with a work-package or drawing-number reference — §2.2: “A course code or university name found in a filename, title, or page-one heading is more meaningful than the same text appearing once in a reference list on page eighteen.”

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- a document that identifies the project only by an informal site nickname the team uses and no formal name appears anywhere
- correspondence whose project must be inferred from the parties and the works described
- a scanned contract particulars page where the roles are filled in by hand

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10):

- a bare project number — indistinguishable from an order number, a drawing number and a job reference
- a company name — §4.9's warning transfers directly: “A university name alone should not create a group because Columbia can appear as an authoring school, course provider, target institution, employer, research venue, or merely a cited organization.” — a contractor's name appears as employer, contractor, subcontractor, supplier and merely cited party
- a site address, which is shared with every other domain in this slice
- a project name that is also a place name, matched inside a longer string — §3.7: “It should use word-boundary matching rather than substring matching.”

### Work types

`contract`, `programme`, `drawing register`, `specification`, `instruction`, `valuation`, `site diary`, `meeting minutes`, `handover pack`

### Grouping reasons (§4)

- one project across every discipline and document type
- one work package within a project
- one contractual chain — instruction, variation, valuation, final account — for one change

### Template (§5)

`project → work package → document type`

Time first: **no**

§5.5: “a parent dimension should provide the context required to understand the child” — a drawing number, an instruction number and a valuation number are all meaningless outside their project, and a document type is only navigable once the package narrows it. Time is deliberately absent: a project spans years and “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders.” §5.8 allows a small project to collapse the package level — “The canvas must support uneven depth because real file trees are not and should not be perfectly symmetrical.”

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| trade.job | a project has an employer, a contractor and packages; a job has a client and a trade. A file naming a contract sum, a work package or a certified valuation is a project file however small the works | §5.8: “each branch should offer the dimensions that are actually present in its member groups and show what each split would create” |
| prop.development-appraisal | the appraisal precedes and justifies the project and belongs to the developer's investment file, not the construction file. The separating signal is a return metric and a land cost, which a construction contract never states | §3.9: “Topic answers what a file is about, while purpose answers what the file was for.” |
| cons.drawings-revisions | the drawing register is a project artefact but has its own revision discipline and its own identity rules; it is a child domain rather than a competitor | §3.11: “One file may hold facts from more than one domain without losing information.” |
| eng.engineering-project | an engineering project delivers a designed product through stage gates; a construction project delivers a building under a contract. A plant or infrastructure scheme is genuinely both and its file will carry both fact sets | §3.11: “One file may hold facts from more than one domain without losing information.” |

### Sensitivity

`none` — A construction project file's subject is a building and a contract between organisations. None of §8.4's named categories is routine to it. The personnel records that would carry them — inductions, timesheets, subcontractor identity checks — are separate domains in this slice and are marked there. No handling class is set; that is P7's.

### Open question — Joseph's call, unresolved

> Which jurisdictions does this product support at launch? Standard contract forms, procurement routes, stage names, building-control regimes, certificate schemes and retention practice are all jurisdiction-defined, and several are not translations of one another but different objects. This catalogue names no contract form, no stage nomenclature and no certificate scheme anywhere, and writes every such field functionally. That keeps it honest and leaves its deterministic recognisers thinner than they could be, because no gazetteer of form names can be built until the scope question is answered. Joseph's call.

---

## `cons.drawings-revisions` — Drawings, models and revision control

The design information a project is built from, whose identity is a drawing number plus a revision and whose defining risk is building from a superseded sheet.

**Provenance:** **proposal** — new — the design does not name this domain, and nothing here is asserted as the design's

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `project` | string | Riverside Phase 2 | `validated` | Drawing numbers are unique only within a project. §5.5: “a parent dimension should provide the context required to understand the child” — without the project, a drawing number is not an identifier at all. |
| `drawing_number` | string | A-2-104 | `validated` | §3.5's model, applied to the most structured code in this slice: the number is a fact only “when the engine finds a course-code pattern together with academic context” — here the corroborating context is a title block. |
| `revision` | string | Rev C | `validated` | The revision is what makes two byte-different files the same drawing. Without it the version family cannot be built and the superseded-sheet risk is unmanaged. |
| `discipline` | string | structural | `validated` | Architectural, structural, mechanical and electrical drawings share a project and a numbering convention; the discipline is usually encoded in the number's prefix and stated in the title block. |
| `drawing_status` | string | for construction | `validated` | A status stamp — preliminary, for tender, for construction, as built — is a labeled field in a title block and is the field that decides whether the sheet may be built from. |
| `revision_date` | date | 2026-04-08 | `direct` | §3.13: “A direct fact was read from a reliable and explicit source, such as a content hash, EXIF timestamp, document title, or labeled form field.” — a title-block field. §3.10's explicit-regex path only: “The product must not use fuzzy date parsing because file names and documents frequently contain numbers that look like years but are course identifiers, version numbers, build numbers, ZIP codes, or other unrelated values.” |
| `sheet_size` | string | A1 | `direct` | §3.11 permits “Each domain activates only a small set of relevant fields, usually three to six that may help build a future folder proposal and several additional fields used only for search, privacy protection, explanation, or later review.” — a search and explanation field, never a folder dimension. §2.9 makes it reachable: “Design and creative formats such as PSD, AI, SVG, Figma exports, CAD files, and 3D files should at minimum yield filename, format, dimensions or canvas properties, embedded metadata, layers or artboards where accessible, linked asset names, and preview text” |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.3, §3.5):

- a drawing-number pattern co-occurring with title-block context — 'rev' | 'scale' | 'drawn by' | 'checked by' | 'do not scale' | 'for construction' — which is §3.5's rule applied to a title block rather than to a syllabus
- a revision label ('Rev A' | 'Rev B' | 'P01' | 'C02') co-occurring with a drawing number that is otherwise identical between two files, which builds the version family deterministically
- a CAD or model container format co-occurring with a project name in the path or in embedded metadata — §2.9: “Design and creative formats such as PSD, AI, SVG, Figma exports, CAD files, and 3D files should at minimum yield filename, format, dimensions or canvas properties, embedded metadata, layers or artboards where accessible, linked asset names, and preview text”

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- a photographed or marked-up drawing where the title block is illegible and only the content identifies the discipline
- a sketch issued as a drawing with no number, where the project must be read from what is drawn
- a drawing register spreadsheet whose column headings are non-standard and must be interpreted before the rows can be read

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10):

- a bare drawing number — 'A-2-104' has the same shape as a part number, a room number and a specification clause reference
- a revision letter on its own; 'Rev C' identifies nothing without the drawing it revises
- a scale string ('1:50'), which appears on maps, plans, models and product sheets alike
- a CAD file extension — §2.9 requires that an unreadable proprietary format be “recorded as indexed-but-unreadable rather than silently treated as empty”, not that it be assigned a project

### Work types

`general arrangement`, `detail drawing`, `as-built drawing`, `drawing register`, `markup`, `model file`, `sketch issued`

### Grouping reasons (§4)

- one drawing across its revisions, as a version family
- one drawing issue — the set of sheets released together under one transmittal
- one discipline's package within a project

### Template (§5)

`project → discipline → drawing status`

Time first: **no**

§5.5: “a parent dimension should provide the context required to understand the child” — a discipline is meaningless outside its project and a status is meaningless outside its discipline. Revision is deliberately not a folder level: it is a version family, and making it a level would produce exactly what §5.9 warns against — “It should warn when a level produces only one child, repeats a concept already expressed in the parent, creates excessive depth, or creates a large number of tiny folders.”. Time does not lead: “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders.”

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| cons.project | the drawing register is a project artefact; this domain exists separately because the revision identity rule is its own and because drawings arrive in formats §2.9 treats specially | §2.9: “Design and creative formats such as PSD, AI, SVG, Figma exports, CAD files, and 3D files should at minimum yield filename, format, dimensions or canvas properties, embedded metadata, layers or artboards where accessible, linked asset names, and preview text” |
| cons.site-survey | an existing-conditions drawing is a survey output, not a design output. The separating signal is a status stamp: survey drawings carry a survey date, design drawings carry a revision and an issue status | §3.9: “Topic answers what a file is about, while purpose answers what the file was for.” |
| prop.listing | a floor plan drawn for a sales particular is marketing material with a drawing-like appearance. The separating signal is the absence of a title block and the presence of an agent's branding | §4.9: “when one high-frequency entity acts as the only bridge” |
| eng.drawing-package | the engineering slice owns drawing packages for manufactured things; this domain owns them for buildings and sites. The separating signal is in the title block: a project and a site say construction, a part and an assembly say engineering, and a civil-structural package sits in both | §4.8: “that each fact or label belongs to an allowed domain schema” |

### Sensitivity

`none` — Design information about a building carries none of §8.4's named categories as a routine matter. Security drawings for some building types are an exception a user may mark themselves; §8.4's classification is evidence-backed and revisable. No handling class is set here; that is P7's.

---

## `cons.subcontract` — Subcontractor engagement and management

The paperwork of engaging another trade or firm to do part of the works — orders, insurances, competence evidence, payment applications and payment notices.

**Provenance:** **inference** — extends a design-named domain or template situation; the cite supports the extension, not the whole entry

**Cite:** Extends §5.7's “The product should eventually maintain a library of roughly 200–300 domain-specific templates, covering common organizational situations such as academic programs, university applications, recruiting processes, client engagements, research workflows, financial records, travel, legal matters, creative projects, software repositories, personal administration, and photo collections.” to the mirror case: the same engagement seen from the paying side. §3.8 is the load-bearing citation — “The system must separate roles that happen to contain the same entity type.”

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `project` | string | Riverside Phase 2 | `validated` | A subcontract belongs to the works it serves. §5.5: “a parent dimension should provide the context required to understand the child” |
| `subcontractor` | string | Keldon Mechanical Ltd | `validated` | §3.8: “The system must separate roles that happen to contain the same entity type.” On a payment notice the payer, the payee and the certifying party are three roles and all three are company names in the same document. |
| `subcontract_reference` | string | SC-2214-07 | `validated` | §3.5's model: a reference is a fact only “when the engine finds a course-code pattern together with academic context”, the context here being subcontract language. |
| `package` | string | mechanical services | `validated` | What was sublet. It is the field that makes two subcontracts with one firm on one project distinguishable. |
| `competence_evidence_type` | string | public liability insurance certificate | `validated` | Insurance certificates, trade-body registrations and training records are the recurring document types here. Scheme names are jurisdiction-specific and are not named in this catalogue — see the open question. |
| `payment_application_period` | string | application 7 | `direct` | §3.13: “A direct fact was read from a reliable and explicit source, such as a content hash, EXIF timestamp, document title, or labeled form field.” — a labeled field on a payment application, and the field that sequences the whole payment chain. |
| `engagement_status` | string | in progress | `llm_supported` | Stated in correspondence rather than in a labeled field. §3.5 bounds the model: “it may extract only fields allowed by the relevant schema” |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.3, §3.5):

- a subcontract-language term ('subcontract order' | 'payment application' | 'payment notice' | 'pay less notice' | 'retention') co-occurring with two distinct company names in labeled payer and payee roles
- an insurance-certificate structure — a labeled insurer, policy period and limit of indemnity — co-occurring with a named contractor and a project reference
- a subcontract reference pattern co-occurring with a project number in the same document

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- an email chain agreeing a package and a price with no order document
- a certificate whose scheme is named but whose meaning must be read from prose, which is where the jurisdiction question bites hardest
- a document naming three companies where only prose says which is the subcontractor

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10):

- a company name — §4.9's warning transfers: “A university name alone should not create a group because Columbia can appear as an authoring school, course provider, target institution, employer, research venue, or merely a cited organization.”
- a bare reference number
- a policy number or a limit of indemnity — an insurance certificate on its own belongs to whoever is insured, which may be the main contractor, the client or the subcontractor
- the word 'application', which in this slice alone means a payment application, a planning application and a licence application

### Work types

`subcontract order`, `insurance certificate`, `competence record`, `payment application`, `payment notice`, `retention release`, `termination correspondence`

### Grouping reasons (§4)

- one subcontractor on one project across the whole engagement
- one payment cycle — application, notice, certificate, remittance
- one firm's compliance pack across every project it works on

### Template (§5)

`project → subcontractor → document type`

Time first: **no**

§5.5: “a parent dimension should provide the context required to understand the child” — a payment application number is meaningless without the subcontractor, and the subcontractor is meaningless without the project. The compliance pack is the exception that §5.8's uneven depth handles: it belongs to the firm across projects, not to any one project — “The canvas must support uneven depth because real file trees are not and should not be perfectly symmetrical.”. Time does not lead: “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders.”

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| biz.invoice-received | THE BOUNDARY. A payment application is a contractual claim under a subcontract; the invoice that follows it is an accounting record. They carry different numbers, different dates and different consequences, and the application exists whether or not an invoice ever does | §3.9: “Topic answers what a file is about, while purpose answers what the file was for.” |
| trade.job | the same trade firm can be the subcontractor here and the principal in its own job file; the role is a fact about the document, not about the firm | §3.8: “The system must separate roles that happen to contain the same entity type.” |
| cons.method-statement-ra | a subcontractor's method statement arrives inside the engagement pack but belongs to the health and safety domain, which has its own review and expiry discipline | §3.11: “One file may hold facts from more than one domain without losing information.” |
| qual.supplier-qualification | supplier qualification and subcontractor competence evidence are the same pack under two names — insurances, certifications, references, audits. The separating signal is whether the engagement is for works on a site or for goods into a process | §3.9: “Topic answers what a file is about, while purpose answers what the file was for.” |

### Sensitivity

`potentially_sensitive` — §2.9's phrase “while treating addresses and message content as potentially sensitive” only. An engagement pack routinely contains identity and right-to-work documents, individual training and competence records, and bank details for payment. §8.4 names “identity documents, account statements, tax records, medical information, legal records, credentials, private correspondence, GPS metadata, employment materials, and educational records” and §4.9 adds that “Rare but sensitive files such as passports, visas, and legal documents may be surfaced as protected records even when they do not meet a normal group-size threshold.” The handling class is P7's (§8.4) and is not set here.

---

## `cons.site-diary` — Site diaries and daily reports

The day-by-day record of who was on site, what was done, what the weather was and what went wrong — written to be evidence later.

**Provenance:** **proposal** — new — the design does not name this domain, and nothing here is asserted as the design's

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `project` | string | Riverside Phase 2 | `validated` | A diary entry outside its project is unreadable. §5.5: “a parent dimension should provide the context required to understand the child” |
| `report_date` | date | 2026-05-14 | `direct` | §3.13: “A direct fact was read from a reliable and explicit source, such as a content hash, EXIF timestamp, document title, or labeled form field.” — a labeled field, and the whole identity of the record. §3.10's explicit-regex path only: “The product must not use fuzzy date parsing because file names and documents frequently contain numbers that look like years but are course identifiers, version numbers, build numbers, ZIP codes, or other unrelated values.” |
| `author_role` | string | site manager | `direct` | Recorded because a diary is a signed statement, not because it is a folder dimension. §3.8: “It should avoid using authorship or creator identity as a destination dimension.” |
| `weather` | string | heavy rain from 1100 | `direct` | A labeled field on almost every diary form, and the reason diaries are kept: it is the evidence for a delay claim. |
| `labour_on_site` | string | as tabulated on the form | `direct` | §2.3 makes the table reachable: “Tables matter because resumes, forms, applications, invoices, and administrative documents often place their most useful information in cells rather than body paragraphs.” — a diary's labour allocation lives in cells, not prose. This catalogue holds no count. |
| `delay_event` | string | no crane access, tower crane out of service | `llm_supported` | Whether a day contained a compensable delay is an interpretation of prose. §3.13: “An LLM-supported fact was proposed by a language model from a bounded evidence packet, cited exact supporting text or metadata, and passed deterministic validation.” |
| `area_or_package` | string | block B, levels 3-5 | `validated` | Where on site the day's work happened, which is what lets a diary be retrieved against a defect or a claim. |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.3, §3.5):

- a diary-form structure — a labeled date field together with labeled weather and labour fields — which is a signature no other document in this slice has
- a diary-language term ('site diary' | 'daily report' | 'daily site record' | 'day works') in the filename or page-one heading, co-occurring with a project name or number
- a filename carrying an explicit-format date co-occurring with a project name, where sibling files form an unbroken daily run — §3.10 permits this only through explicit patterns

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- a photographed handwritten diary page where the date is legible but the entries must be read
- an email sent each evening that functions as the diary with no form at all
- a diary that records a delay event in prose that must be interpreted before it can be linked to a claim

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10):

- a date in a filename — §3.10 is explicit: “The product must not use fuzzy date parsing because file names and documents frequently contain numbers that look like years but are course identifiers, version numbers, build numbers, ZIP codes, or other unrelated values.”
- the word 'report', which in this slice means a survey report, a site report, a valuation report, a POS report and an inspection report
- a weather description, which appears in diaries, delay notices, claims and correspondence alike
- a run of daily files, which is a session-shaped clue and no more — §3.9: “A session should never be treated as proof of topic, and it should not carry the same confidence as a hash match or a directly extracted document fact.”

### Work types

`site diary`, `daily report`, `weekly progress report`, `delay notice`, `day-works sheet`, `toolbox-talk record`

### Grouping reasons (§4)

- one project's diary across a month or a year, as an unbroken run
- the diaries covering one delay event, retrieved together as evidence
- one week's daily reports and the weekly report that summarises them

### Template (§5)

`project → year → month`

Time first: **no**

§5.5: “a parent dimension should provide the context required to understand the child” — a date is only navigable inside its project, and diaries across projects must not merge. Time therefore leads inside the project but not overall. This is the boundary case for §5.5's exception: a diary is a record of a day, but it is not capture-based media and its date is an attribute rather than its content, so “Photos and capture-based media are the major exception: time often belongs first because capture date is a defining aspect of the material.” does not reach it. §5.8 expects the year level to collapse for a short project — “The canvas must support uneven depth because real file trees are not and should not be perfectly symmetrical.”

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| cons.progress-photos | a photograph attached to a diary entry is diary evidence; a standalone progress set is its own record. The separating signal is whether a diary form exists for the same day | §2.6: “Camera EXIF, GPS, and capture time can support deterministic photo-event proposals.” |
| cons.variation-claim | a diary is contemporaneous and neutral; a claim is a constructed argument that cites diaries. The diaries a claim relies on stay in the diary run and are retrieved, not moved | §3.11: “One file may hold facts from more than one domain without losing information.” |
| trade.timesheet | a diary records who was on site as narrative; a timesheet records hours for payment. The separating signal is a rate, a pay period or an approval signature | §3.9: “Topic answers what a file is about, while purpose answers what the file was for.” |

### Sensitivity

`none` — A diary names individuals present on site, which is ordinary operational record-keeping rather than any of §8.4's named categories. Where a diary records an accident it acquires medical content, and §8.4's classification is evidence-backed and revisable per file for exactly that case. No handling class is set here; that is P7's.

---

## `cons.progress-photos` — Site progress photography

Photographs taken to record what a site looked like on a given day — capture-based media whose date is the record.

**Provenance:** **inference** — extends a design-named domain or template situation; the cite supports the extension, not the whole entry

**Cite:** Extends the design-named Photos domain. §3.11: “Photos may use capture year, event, location, people, camera information, and media type.” and §5.5 grants the capture exception this entry relies on: “Photos and capture-based media are the major exception: time often belongs first because capture date is a defining aspect of the material.”

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `capture_date` | date | 2026-05-14 | `direct` | §3.13: “A direct fact was read from a reliable and explicit source, such as a content hash, EXIF timestamp, document title, or labeled form field.” — an EXIF timestamp is the design's own example of a direct fact, and here it is the record itself rather than metadata about it. §2.6: “Camera EXIF, GPS, and capture time can support deterministic photo-event proposals.” |
| `project` | string | Riverside Phase 2 | `validated` | The site the photographs are of. Recoverable from GPS clustering against a known site address, or from a folder the user already made — §5.10: “A carefully curated existing folder should be treated as a strong expression of user intent.” |
| `site_location` | string | block B, level 4, east elevation | `llm_supported` | Where in the site the frame was taken. Occasionally in an annotation; usually only in the image content. §3.5 bounds the model: “It can only propose facts that belong to the active domain schema, and it must cite exact supporting evidence already extracted from the file.” |
| `gps` | string | as recorded in EXIF | `direct` | §2.6: “Camera EXIF, GPS, and capture time can support deterministic photo-event proposals.” — GPS is what turns an undated pile of images into a site set. It is a fact and a sensitivity, not a folder dimension. |
| `camera_information` | string | as recorded in EXIF | `direct` | §3.11's Photos schema names it: “Photos may use capture year, event, location, people, camera information, and media type.” — it is a search and explanation field and it separates one photographer's set from another's. |
| `media_type` | string | photograph | `validated` | §3.11's Photos schema names media type. §2.6 requires it be earned, not assumed: “the system must not mistake the absence of EXIF for proof that an image is a screenshot” |
| `subject_element` | string | reinforcement before pour | `llm_supported` | What the photograph is of, which is the whole value of a progress set and is only in the pixels. |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.3, §3.5):

- camera EXIF present, with capture timestamps clustered inside one day and GPS clustered at one location that matches a known site address — §2.6: “Camera EXIF, GPS, and capture time can support deterministic photo-event proposals.”
- a burst of images sharing a camera make and model and a contiguous filename sequence, whose GPS falls inside a site already established by another domain
- an existing user-made folder whose name states a project and a date, holding only images — §5.10: “A carefully curated existing folder should be treated as a strong expression of user intent.”

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- a set stripped of EXIF by a messaging app, where only the content shows construction and only the content places it on a site
- deciding whether a set is progress photography, defect photography or a pre-works survey, which is a judgement about why the frames were taken
- an image with a whiteboard or a board in shot whose OCR text carries the date and the site

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10):

- the absence of EXIF — §2.6 is explicit: “the system must not mistake the absence of EXIF for proof that an image is a screenshot” and messaging platforms strip metadata from real photographs
- OCR text density — §2.6: “OCR text density is also not a reliable screenshot detector because receipts, document scans, whiteboards, and photographs of pages can all contain dense text.”
- GPS alone: a photograph taken at a site could be a survey, a defect, a delivery or a personal photograph taken on a lunch break
- a capture date alone, which places an image in time and nowhere else

### Work types

`progress photograph`, `photograph set`, `annotated photograph`, `time-lapse frame`, `drone capture`, `video walkthrough`

### Grouping reasons (§4)

- one visit — one camera, one location, one contiguous span of capture times
- one project's progress record across the whole build
- one element photographed repeatedly as it was built

### Template (§5)

`capture date → area`

Time first: **yes**

TIME FIRST, and this is §5.5's exception used exactly as written: “Photos and capture-based media are the major exception: time often belongs first because capture date is a defining aspect of the material.”. A progress photograph exists to say what the site looked like on a date; strip the date and the file has no content left. The project is NOT listed as a dimension because it is the branch this template is applied inside rather than a level the template creates — §5.4: “The product opens an accepted branch and proposes one or more domain templates based on the groups and facts that already belong inside it.” That is exactly why the flag is true: every dimension this domain itself contributes is subordinate to the capture date. §5.5's “a parent dimension should provide the context required to understand the child” still governs the branch above, so two sites' photographs never merge on a shared day. §2.6 supplies the capture date as a direct fact, so the leading dimension is one the engine can actually populate.

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| cons.site-diary | the diary is the written record of the day and the photographs are the visual one. Both are keyed on project plus date, which is why they retrieve each other and why neither should absorb the other | §3.11: “One file may hold facts from more than one domain without losing information.” |
| cons.snagging | a defect photograph is taken to prove a fault and is numbered against a defect; a progress photograph is taken to prove a state. Absent a defect reference the engine cannot tell them apart from the image alone | §2.6: “The system should therefore use a hierarchy of signals: camera EXIF is strong photo evidence; capture time, GPS, and sensor-shaped dimensions reinforce it; exact display resolutions, PNG format, and software metadata may support a screenshot hypothesis; conflicting signals should lead to abstention rather than an invented classification.” |
| prop.inventory-inspection | both are geotagged interior photograph sets. The separating signal is a companion schedule naming a tenant or a tenancy | §3.9: “Topic answers what a file is about, while purpose answers what the file was for.” |
| pers.photo-event | a tradesperson's phone holds both, and both are time-clustered geotagged sets. §2.6's hierarchy separates them only through content, because the metadata is identical in kind | §2.6: “The system should therefore use a hierarchy of signals: camera EXIF is strong photo evidence; capture time, GPS, and sensor-shaped dimensions reinforce it; exact display resolutions, PNG format, and software metadata may support a screenshot hypothesis; conflicting signals should lead to abstention rather than an invented classification.” |

### Sensitivity

`potentially_sensitive` — §2.9's phrase “while treating addresses and message content as potentially sensitive” only. Every frame carries GPS pinning a private address, and domestic work photographs the inside of someone's home. §8.4 names “identity documents, account statements, tax records, medical information, legal records, credentials, private correspondence, GPS metadata, employment materials, and educational records” — GPS metadata is on that list by name. §8.4 also requires privacy policy to be enforced before content reaches a model, which matters here because the subject_element and site_location fields are the ones that need the model. The handling class is P7's and is not set.

### Open question — Joseph's call, unresolved

> Where does a project's photograph set physically live — under the project, or under Photos? §5.5 pulls both ways for this exact case: “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders.” puts it under the project, while “Photos and capture-based media are the major exception: time often belongs first because capture date is a defining aspect of the material.” is what this domain is. A tradesperson thinks of one job as one folder; a photographer thinks of one shoot as one folder. Joseph decides whether capture-based media inside a work domain stays with its parent record or is drawn out into a capture branch — the answer sets the pattern for every photo-bearing domain in this slice.

---

## `cons.snagging` — Snagging, defects and handover lists

Numbered lists of things that are wrong, each tied to a location and a responsible party, tracked until closed.

**Provenance:** **proposal** — new — the design does not name this domain, and nothing here is asserted as the design's

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `project` | string | Riverside Phase 2 | `validated` | Defect numbering restarts per project, so the project is what makes a defect reference an identifier at all. §5.5: “a parent dimension should provide the context required to understand the child” |
| `unit_or_location` | string | Plot 14, en-suite | `validated` | The addressable location. A snag list for a housing scheme is navigated by plot before anything else, and the plot is what a purchaser recognises. |
| `defect_reference` | string | D-014 | `validated` | §3.5's model: a fact only “when the engine finds a course-code pattern together with academic context”, the corroborating context being defect-list language. |
| `defect_status` | string | closed | `validated` | Open, closed, disputed or rejected is a labeled column on every snag list, and it is the field that decides whether the list is live. |
| `responsible_party` | string | Keldon Mechanical Ltd | `validated` | §3.8: “The system must separate roles that happen to contain the same entity type.” — the party who caused the defect, the party who must fix it and the party who reported it are three roles in one row. |
| `inspection_date` | date | 2026-08-03 | `direct` | §3.13: “A direct fact was read from a reliable and explicit source, such as a content hash, EXIF timestamp, document title, or labeled form field.” §3.10's explicit-regex path only. |
| `defect_description` | string | grout cracked around shower tray | `llm_supported` | The substance is prose written by whoever walked the unit. §3.5: “It can only propose facts that belong to the active domain schema, and it must cite exact supporting evidence already extracted from the file.” |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.3, §3.5):

- a snag-list structure — a table whose columns include a location, a description and a status — co-occurring with defect-list language ('snag' | 'defect' | 'punch list' | 'outstanding works' | 'making good'). §2.3 makes the columns reachable: “Tables matter because resumes, forms, applications, invoices, and administrative documents often place their most useful information in cells rather than body paragraphs.”
- a defect-reference pattern co-occurring with a unit or plot identifier and a status value in the same row
- a photograph set whose filenames carry defect references matching a list held elsewhere in the same folder

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- a photograph with an arrow drawn on it and no list, where the defect must be read from the image
- an email listing complaints in prose that functions as a snag list without being one
- distinguishing a defect from a variation: the same words describe both, and only who pays separates them

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10):

- a bare defect reference — the same shape as a drawing number and a document reference
- a plot or unit number, which is shared with sales, handover, service charge and warranty records for the same building
- the word 'defect', which is also a legal term in the contract and appears in every construction contract regardless of whether defects exist
- a status word such as 'open' or 'closed', which is the single most generic token in this slice

### Work types

`snag list`, `defect schedule`, `handover pack`, `defect photograph`, `making-good certificate`, `close-out report`

### Grouping reasons (§4)

- one unit's defects from first inspection to close-out
- one inspection walk across all units on one date
- one subcontractor's defects across a project

### Template (§5)

`project → unit or location → status`

Time first: **no**

§5.5: “a parent dimension should provide the context required to understand the child” — a defect reference is only unique inside a project and only navigable inside a unit. Status sits last because it changes: making it a higher level would move files as they close, which §8.3 treats as a filesystem mutation rather than as a filing decision. Time does not lead — “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders.” — even though every snag list has an inspection date, because the unit is what anyone searching actually knows.

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| cons.progress-photos | both are geotagged site photograph sets. A defect photograph is numbered against a list; a progress photograph is not. Where no list exists the engine cannot separate them and should abstain | §6.10: “Correct abstention is a successful outcome because the product’s goal is reliable organization, not maximum file movement.” |
| cons.variation-claim | a defect is remedied at the contractor's cost; a variation is paid for. The documents look identical and only the contractual conclusion differs, which is a judgement no rule should make | §3.5: “It can only propose facts that belong to the active domain schema, and it must cite exact supporting evidence already extracted from the file.” |
| prop.inventory-inspection | a check-out schedule listing damage and a snag list listing defects have the same shape. The separating signal is a tenancy or tenant reference against a plot or unit reference | §3.9: “Topic answers what a file is about, while purpose answers what the file was for.” |
| eng.commissioning-handover | handover in engineering commissions a system; handover in construction completes a building. Both close with a defect list and a certificate, and on a plant project they are the same event | §4.8: “that each fact or label belongs to an allowed domain schema” |

### Sensitivity

`none` — A defect list's subject is a building. None of §8.4's named categories is routine. Where a snag list is for an occupied private home the photographs acquire the same exposure as “while treating addresses and message content as potentially sensitive” material and §8.4's evidence-backed, revisable classification covers that per file. No handling class is set; that is P7's.

---

## `cons.building-control` — Building control, planning and statutory inspection

The public-authority side of construction — applications, approvals, conditions, inspection visits and completion sign-off.

**Provenance:** **proposal** — new — the design does not name this domain, and nothing here is asserted as the design's

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `site_address` | string | Old Mill House, Bakers Lane | `validated` | Statutory records are held against a property, not against a contractor, and follow the property when it is sold. |
| `application_reference` | string | as issued by the authority | `validated` | §3.5's model: the authority's reference is a fact only “when the engine finds a course-code pattern together with academic context”, the corroborating context here being authority correspondence. Reference formats are jurisdiction-specific — see the open question. |
| `authority` | string | the local authority named on the document | `validated` | §3.8: “The system must separate roles that happen to contain the same entity type.” — the issuing authority, the applicant, the agent and the owner are four roles a decision notice names together. |
| `consent_type` | string | building regulations approval | `llm_supported` | Consent regimes and their names are jurisdiction-defined and are not enumerated in this catalogue. §3.5 bounds the model: “it may extract only fields allowed by the relevant schema” |
| `decision` | string | approved with conditions | `validated` | The outcome is a labeled field on a decision notice and is what makes the document worth keeping. |
| `decision_date` | date | 2026-02-27 | `direct` | §3.13: “A direct fact was read from a reliable and explicit source, such as a content hash, EXIF timestamp, document title, or labeled form field.” — conditions and appeal periods run from it. §3.10's explicit-regex path only: “The product must not use fuzzy date parsing because file names and documents frequently contain numbers that look like years but are course identifiers, version numbers, build numbers, ZIP codes, or other unrelated values.” |
| `condition_summary` | string | materials to match existing | `llm_supported` | Conditions are numbered prose obligations and must be read, not matched. |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.3, §3.5):

- an authority-decision structure — an authority name, an application reference and a decision word ('approved' | 'refused' | 'granted' | 'conditions') — co-occurring with a site address
- an inspection-record structure: a labeled stage ('foundations' | 'damp-proof course' | 'drainage' | 'final') together with a visit date and an inspector identifier
- a completion or compliance certificate naming a site address and an issuing authority in the same document

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- a scanned historic approval where the authority's letterhead is the only identifying feature
- correspondence about an application that never restates the reference
- deciding which consent regime a document belongs to, which is a jurisdiction question the design does not answer

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10):

- an authority reference pattern — jurisdiction-specific, and its shape collides with case references, licence numbers and account numbers
- an authority name, which appears as regulator, as landlord, as client and as a merely cited body — §4.9: “A university name alone should not create a group because Columbia can appear as an authoring school, course provider, target institution, employer, research venue, or merely a cited organization.”
- the word 'approved', which appears on drawings, invoices, purchase orders and expense claims
- a site address, shared with every other domain in this slice

### Work types

`application`, `decision notice`, `conditions discharge`, `inspection record`, `completion certificate`, `enforcement correspondence`, `plans check`

### Grouping reasons (§4)

- one application from submission to completion certificate
- one property's statutory history across owners and decades
- one condition and the evidence discharging it

### Template (§5)

`property → application → document type`

Time first: **no**

§5.5: “a parent dimension should provide the context required to understand the child” — a decision notice is meaningless without its application and an application is meaningless without its property. The property leads rather than the project because statutory records outlive the project and transfer with the building; this is one of the few domains in this slice where the address genuinely is the subject. Time does not lead: “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders.”

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| trade.compliance-certificate | an authority signs off that works comply with regulation; an installer certifies their own installation. Both are called certificates and both name an address. The separating signal is whether the issuer is a public authority or the firm that did the work | §3.8: “The system must separate roles that happen to contain the same entity type.” |
| prop.sale-purchase | consents and completion certificates are gathered into a conveyancing pack and are then serving a transaction. §3.9 covers the doubling exactly: the pack is purpose-coherent while its members are not | §3.9: “The documents are content-incoherent but purpose-coherent.” |
| cons.project | the statutory file is about the building; the project file is about the contract. A project ends, the building's statutory history does not | §3.11: “One file may hold facts from more than one domain without losing information.” |
| gov.planning-application | the same application from both sides of the counter. The applicant holds a submission and a decision notice; the authority holds a case file with an officer, a recommendation and an internal report that never reaches the applicant. Neither side's file should absorb the other's | §3.8: “The system must separate roles that happen to contain the same entity type.” |

### Sensitivity

`none` — Statutory building records are ordinarily public. None of §8.4's named categories is routine to them. No handling class is set here; that is P7's.

### Open question — Joseph's call, unresolved

> Which jurisdictions, and therefore which consent regimes? This entry names no regime, no form number and no reference format anywhere, because building control, planning, and their equivalents are constituted differently in every jurisdiction and are not translations of one another. That leaves this domain's deterministic recognisers structural rather than lexical — the engine can find an authority-decision shape but cannot match a scheme name. A jurisdiction answer converts most of this domain from a model-dependent read to a rule-validated one. Joseph's call.

---

## `trade.compliance-certificate` — Installation and compliance certificates

An installer's signed statement that a specific installation at a specific address meets a specific standard — the document that has to be produced years later.

**Provenance:** **proposal** — new — the design does not name this domain, and nothing here is asserted as the design's

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `site_address` | string | 14 Elm Road, Flat 2 | `validated` | A certificate is held against the installation, which is held against the address. It outlives the job, the tradesperson and the owner. |
| `installation_type` | string | electrical installation | `validated` | What was certified. It is the field that separates the certificates for one address into readable groups. |
| `certificate_reference` | string | as printed on the certificate | `validated` | §3.5's model: a fact only “when the engine finds a course-code pattern together with academic context”, the corroborating context being certificate language. |
| `issuer` | string | the firm or engineer named on the certificate | `validated` | §3.8: “The system must separate roles that happen to contain the same entity type.” — the certifying engineer, the firm, the registration body and the customer are four roles on one page, and the registration body is the one most often mistaken for the issuer. |
| `issue_date` | date | 2026-03-06 | `direct` | §3.13: “A direct fact was read from a reliable and explicit source, such as a content hash, EXIF timestamp, document title, or labeled form field.” — a labeled field, and the field a renewal is calculated from. |
| `next_due_date` | date | as printed on the certificate | `direct` | A labeled field on most certificate forms. It is recorded, never computed: this catalogue holds no interval, because every interval is jurisdiction-defined and injected. |
| `scheme_or_standard` | string | as named on the certificate | `llm_supported` | Scheme and standard names are jurisdiction-specific and are deliberately not enumerated here. §3.5: “it may extract only fields allowed by the relevant schema” |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.3, §3.5):

- certificate language ('certificate of compliance' | 'installation certificate' | 'safety record' | 'I/we certify that') co-occurring with a labeled installation address and a signature or registration block
- a labeled issue-date and next-due-date pair co-occurring with an installation type, which is the structural signature of a periodic safety certificate
- a registration-body mark or number co-occurring with an installer name and an address — the mark alone identifies the scheme, not the document

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- a photographed certificate where the scheme is a logo and the standard is a small-print reference
- a certificate in a language or format the gazetteer does not cover, which is the ordinary case until the jurisdiction question is answered
- distinguishing a genuine certificate from a quotation that reproduces a certificate template as an example

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10):

- the word 'certificate' — this slice alone has insurance certificates, completion certificates, making-good certificates, certificates of origin, payment certificates and food-hygiene certificates
- a registration or scheme number, which identifies a firm rather than a document
- an address
- a date pair, which appears identically on insurance policies, licences, warranties and tenancy agreements

### Work types

`installation certificate`, `periodic inspection report`, `safety record`, `commissioning record`, `test results sheet`, `minor works certificate`

### Grouping reasons (§4)

- one address's certificates across every installation and every renewal
- one job's certificate set issued at handover
- one certificate and its successors, as a renewal chain

### Template (§5)

`property → installation type → issue date`

Time first: **no**

§5.5: “a parent dimension should provide the context required to understand the child” — an issue date is only meaningful once the installation is known, and the installation only once the property is. The property leads rather than the job because certificates are produced on sale, on letting and on inspection, long after the job file is closed. Time is last: “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders.”, and putting the year first here would scatter one property's safety history across a decade of folders, which is precisely the failure that sentence describes.

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| cons.building-control | self-certification by the installer versus sign-off by an authority. The separating signal is the issuer's nature, not the document's title | §3.8: “The system must separate roles that happen to contain the same entity type.” |
| prop.tenancy | a landlord holds safety certificates as part of the letting file and must produce them to the tenant. The certificate is genuinely both, and the catalogue keeps both fact sets | §3.11: “One file may hold facts from more than one domain without losing information.” |
| trade.job | the certificate is issued from a job and then leaves it: the job file is the tradesperson's, the certificate is the property's | §3.9: “Topic answers what a file is about, while purpose answers what the file was for.” |

### Sensitivity

`none` — A certificate's subject is an installation. It names a customer and an address as context and carries none of §8.4's named categories. No handling class is set here; that is P7's.

### Open question — Joseph's call, unresolved

> Certificate and scheme names are jurisdiction-specific and this catalogue deliberately names none of them — not the schemes, not the standards, not the form numbers, not the renewal intervals. Inventing any of them would be worse than leaving the recogniser structural, because a wrong scheme name is a confident false positive on someone's safety records. Two things follow that Joseph must decide: which jurisdictions are in scope, and whether the product ships a per-jurisdiction certificate gazetteer at all or leaves this domain permanently structural.

---

## `cons.method-statement-ra` — Health and safety documentation

Method statements, risk assessments, inductions, permits and incident records — the documents that say how work will be done safely and what happened when it was not.

**Provenance:** **proposal** — new — the design does not name this domain, and nothing here is asserted as the design's

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `project` | string | Riverside Phase 2 | `validated` | A method statement is written for a specific activity on a specific site. §5.5: “a parent dimension should provide the context required to understand the child” |
| `activity` | string | working at height, roof edge protection | `validated` | What the document covers. It is the field that makes a folder of method statements navigable at all. |
| `document_class` | string | risk assessment | `validated` | Method statement, risk assessment, permit to work, induction record and incident report have different lifecycles and different sensitivities, so the class is a schema field rather than a label. |
| `prepared_by` | string | Keldon Mechanical Ltd | `validated` | §3.8: “The system must separate roles that happen to contain the same entity type.” — the preparing firm, the approving principal contractor and the operatives who signed the briefing are three roles. |
| `review_date` | date | as printed on the document | `direct` | §3.13: “A direct fact was read from a reliable and explicit source, such as a content hash, EXIF timestamp, document title, or labeled form field.” A safety document that is out of review is not a valid document, so this field is the whole point of keeping it. |
| `control_measures` | string | edge protection and harness with restraint lanyard | `llm_supported` | The substance is prose. §3.5: “It can only propose facts that belong to the active domain schema, and it must cite exact supporting evidence already extracted from the file.” |
| `incident_type` | string | as recorded on the report | `llm_supported` | Present only on incident records, and the field that makes those records “while treating addresses and message content as potentially sensitive” where the rest of the domain is not. |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.3, §3.5):

- safety-document language ('method statement' | 'risk assessment' | 'permit to work' | 'safe system of work' | 'site induction') in the filename, title or page-one heading, co-occurring with a project or site reference — §2.2: “A course code or university name found in a filename, title, or page-one heading is more meaningful than the same text appearing once in a reference list on page eighteen.”
- a risk-assessment table structure: labeled hazard, control and residual-risk columns in one table. §2.3: “Tables matter because resumes, forms, applications, invoices, and administrative documents often place their most useful information in cells rather than body paragraphs.”
- a labeled review-date field co-occurring with a preparing-firm block and an activity description

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- a generic template downloaded from a supplier and never filled in, which must be recognised as not being a live document for this project
- an induction record that is a photographed signature sheet
- an incident record written as a narrative email

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10):

- the word 'assessment', which in this slice also means a valuation assessment, a rating assessment and a condition assessment
- the word 'permit', which is also a licence, a planning permit and a parking permit
- a hazard word such as 'asbestos' or 'height' — these appear in surveys, quotes, specifications and correspondence
- a review date, which has the same shape as an expiry date on a certificate, a policy and a licence

### Work types

`method statement`, `risk assessment`, `permit to work`, `site induction record`, `toolbox talk`, `incident report`, `safety file`

### Grouping reasons (§4)

- one activity's safety pack — method statement, risk assessment, permit and briefing record
- one project's safety file assembled for handover
- one firm's generic assessments reused across projects

### Template (§5)

`project → activity → document class`

Time first: **no**

§5.5: “a parent dimension should provide the context required to understand the child” — a control measure is only interpretable once the activity is known. Generic assessments that belong to the firm rather than to any project are the uneven case §5.8 anticipates: “The canvas must support uneven depth because real file trees are not and should not be perfectly symmetrical.”. Time does not lead: a live safety document is current until its review date, so filing it by year would bury the version in force — “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders.”

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| cons.subcontract | safety documents arrive inside an engagement pack. They belong here because their review-and-expiry lifecycle is their own and because incident records inside them are sensitive in a way the rest of the engagement pack is not | §3.11: “One file may hold facts from more than one domain without losing information.” |
| cons.site-diary | a diary records that an induction happened; the induction record is the evidence. The diary is narrative, the record is signed | §3.9: “Topic answers what a file is about, while purpose answers what the file was for.” |
| cons.building-control | both are compliance material and both name authorities. Safety documentation is prospective — how work will be done — and statutory approval is retrospective sign-off that it was | §3.9: “Topic answers what a file is about, while purpose answers what the file was for.” |
| hse.incident-record | the engineering slice owns incident records inside an industrial safety case; this domain owns them on a construction site. The document shape is identical and the regulator differs, which is a jurisdiction question rather than a document one | §4.8: “that each fact or label belongs to an allowed domain schema” |

### Sensitivity

`potentially_sensitive` — §2.9's phrase “while treating addresses and message content as potentially sensitive” only. Induction and training records are employment materials naming individuals, and incident and health-surveillance records carry medical information. §8.4 names both in the corpus this product handles: “identity documents, account statements, tax records, medical information, legal records, credentials, private correspondence, GPS metadata, employment materials, and educational records”. The bulk of the domain — method statements and generic risk assessments — is not sensitive, and §8.4's classification being evidence-backed and revisable is what lets the two live in one domain. No handling class is set here; that is P7's.

---

## `cons.plant-hire` — Plant and equipment hire

Machines and equipment brought onto a site for a period — contracts, off-hire notices, inspection records and damage claims, all keyed on an asset and a hire period.

**Provenance:** **proposal** — new — the design does not name this domain, and nothing here is asserted as the design's

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `hire_supplier` | string | Ashfield Plant Hire | `validated` | §3.8: “The system must separate roles that happen to contain the same entity type.” — the hire company, the hirer and the site the machine went to are three roles in one contract. |
| `asset_description` | string | 3-tonne excavator | `validated` | What was hired. It is the field that makes a hire folder navigable and it is what an inspection record refers to. |
| `asset_identifier` | string | as printed on the hire contract | `validated` | §3.5's model: a plant or serial number is a fact only “when the engine finds a course-code pattern together with academic context”, the corroborating context being hire language. |
| `hire_period` | date range | 2026-04-02 to 2026-04-30 | `direct` | §3.13: “A direct fact was read from a reliable and explicit source, such as a content hash, EXIF timestamp, document title, or labeled form field.” Hire is charged by the day, so the period is the contract's substance and the off-hire date is the single most disputed field in the domain. |
| `site_or_project` | string | Riverside Phase 2 | `validated` | Where the machine went, which is how a hire cost is allocated and how a damage claim is investigated. |
| `hire_status` | string | off-hired | `llm_supported` | On hire, off-hire requested, off-hired and disputed are stated in correspondence rather than in a labeled field. §3.13: “An LLM-supported fact was proposed by a language model from a bounded evidence packet, cited exact supporting text or metadata, and passed deterministic validation.” |
| `inspection_record_type` | string | pre-use inspection | `validated` | Statutory inspection regimes for lifting and access equipment are jurisdiction-defined; this field is written functionally and names no scheme. |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.3, §3.5):

- hire language ('on hire' | 'off hire' | 'hire agreement' | 'hire desk' | 'daily hire rate') co-occurring with an asset description and a labeled period
- a labeled hire-start and hire-end pair co-occurring with a supplier name matched on a word boundary — §3.7: “It should use word-boundary matching rather than substring matching.”
- a plant or serial identifier co-occurring with an inspection or thorough-examination record structure

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- a photographed delivery ticket where the asset is described in shorthand only the hire desk uses
- an email requesting off-hire, which is often the only evidence the hire stopped
- a damage claim that must be read to establish which of several hired assets it concerns

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10):

- a serial or plant number — indistinguishable from a part number, an asset tag and an order number
- a supplier name, which appears as hirer, supplier, payee and merely cited party
- a date range, which has the same shape as an insurance period, a tenancy and a statement period
- the word 'hire', which also appears in recruitment material — §3.7: “It should use word-boundary matching rather than substring matching.”

### Work types

`hire contract`, `delivery ticket`, `off-hire confirmation`, `inspection record`, `damage claim`, `hire invoice`, `rate schedule`

### Grouping reasons (§4)

- one asset's hire from delivery to off-hire, including its inspections
- one project's plant across every supplier
- one supplier's hires across projects, for rate comparison

### Template (§5)

`project → supplier → asset`

Time first: **no**

§5.5: “a parent dimension should provide the context required to understand the child” — an asset identifier is only navigable once the supplier is known, and hire cost belongs to the project that consumed it. Time does not lead even though every hire is a period: “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders.”, and one asset's hire chain would be split across two years by a mid-project renewal.

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| biz.invoice-received | THE BOUNDARY. A hire contract is a working document that governs an asset on a site; the hire invoice is the accounting record of what it cost. The contract exists before, during and after any invoice, and the off-hire dispute is fought on the contract not the invoice | §3.9: “Topic answers what a file is about, while purpose answers what the file was for.” |
| fleet.vehicle | an owned vehicle is a fleet asset with a permanent record; a hired machine is a temporary contract. The separating signal is ownership, which is stated in the hire agreement and nowhere in a fleet file | §3.8: “The system must separate roles that happen to contain the same entity type.” |
| cons.materials-delivery | a delivery ticket for plant and a delivery note for materials have the same shape. The separating signal is that plant is collected again — an off-hire document exists and no materials delivery has one | §3.9: “Topic answers what a file is about, while purpose answers what the file was for.” |
| mro.maintenance-work-order | a hired machine's inspection record and an owned asset's work order describe the same maintenance. The separating signal is ownership: a hire agreement exists for one and not the other | §3.8: “The system must separate roles that happen to contain the same entity type.” |

### Sensitivity

`none` — Hire records concern machines and companies. None of §8.4's named categories is routine. No handling class is set here; that is P7's.

---

## `cons.materials-delivery` — Materials ordering and delivery notes

What was ordered, what actually turned up and what was signed for — the paper trail between a purchase order and a site.

**Provenance:** **inference** — extends a design-named domain or template situation; the cite supports the extension, not the whole entry

**Cite:** Extends §3.11's Finance schema “Finance files may use institution, account type, tax year, and record type.” into its pre-accounting form, and extends §7.3's residual template “Receipts and Confirmations may hold isolated invoices, delivery confirmations, booking records, boarding passes, purchase receipts, event tickets, and similar transactional documents.” which names delivery confirmations as a recognised isolated record type

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `supplier` | string | Brentwood Builders Merchants | `validated` | §3.8: “The system must separate roles that happen to contain the same entity type.” — the supplier, the buyer, the delivery site and the invoice address are four roles on one delivery note. |
| `order_reference` | string | PO-4417 | `validated` | §3.5's model: a purchase-order number is a fact only “when the engine finds a course-code pattern together with academic context”, the corroborating context being ordering language. It is also the key that joins the order, the note and the invoice. |
| `delivery_note_reference` | string | as printed on the note | `direct` | §3.13: “A direct fact was read from a reliable and explicit source, such as a content hash, EXIF timestamp, document title, or labeled form field.” — a labeled field, and distinct from the order reference in every real system. |
| `delivery_date` | date | 2026-04-09 | `direct` | A labeled field. §3.10's explicit-regex path only: “The product must not use fuzzy date parsing because file names and documents frequently contain numbers that look like years but are course identifiers, version numbers, build numbers, ZIP codes, or other unrelated values.” |
| `delivery_site` | string | Riverside Way, gate 2 | `validated` | Where the goods went, which is what allocates the cost and what a shortage claim is made against. |
| `line_items` | string | as tabulated on the note | `direct` | §2.3: “Tables matter because resumes, forms, applications, invoices, and administrative documents often place their most useful information in cells rather than body paragraphs.” and §2.9: “Spreadsheets such as XLSX, XLS, CSV, TSV, ODS, and Numbers exports should yield workbook or file metadata, sheet names, column headers, visible cell values, table-like regions, formulas only when useful, and dates or identifiers from labeled cells.” — the substance of a delivery note is its table, and this catalogue holds no quantity. |
| `discrepancy` | string | two pallets short, signed unchecked | `llm_supported` | Written by hand on the note or in a following email. §3.13: “An LLM-supported fact was proposed by a language model from a bounded evidence packet, cited exact supporting text or metadata, and passed deterministic validation.” |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.3, §3.5):

- delivery language ('delivery note' | 'goods received' | 'advice note' | 'signed for' | 'delivered to') co-occurring with a supplier name and a labeled delivery address
- an order-reference pattern co-occurring with a line-item table and a supplier block, which is the ordering triple
- an order-and-note reference pair appearing in two different files that share a supplier, which builds the order-to-delivery chain deterministically

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- a photograph of a signed paper note whose OCR is partial and whose supplier is only a logo
- a text or email confirming a delivery with no document at all
- distinguishing a proforma order acknowledgement from a delivery note when both list the same lines

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10):

- a bare order or note reference
- a supplier name — §4.9's shape of warning applies: “A university name alone should not create a group because Columbia can appear as an authoring school, course provider, target institution, employer, research venue, or merely a cited organization.”
- a line-item table, which is shared with quotes, invoices, stock takes and price lists
- a delivery address, which is the site address every other domain in this slice also carries

### Work types

`purchase order`, `order acknowledgement`, `delivery note`, `goods received note`, `shortage or damage claim`, `returns note`, `materials schedule`

### Grouping reasons (§4)

- one order from purchase order to goods received note
- one project's materials across every supplier
- one supplier's deliveries in one period, reconciled against a statement

### Template (§5)

`project → supplier → order`

Time first: **no**

§5.5: “a parent dimension should provide the context required to understand the child” — a delivery note number means nothing without the order and the order means nothing without the supplier. Project leads because materials cost is allocated to works, which is the question anyone opens this folder to answer. Time does not lead: “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders.”

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| biz.invoice-received | THE BOUNDARY, at its sharpest. A delivery note proves goods arrived; the invoice claims payment for them; a supplier statement lists the invoices. The three arrive as three separate PDFs from one supplier and look alike. The separating markers are a signature block and a delivery address on the note, and a sequence number, a tax point and a payment-terms block on the invoice | §3.11: “One file may hold facts from more than one domain without losing information.” |
| retail.supplier-order | the same documents, a different consuming domain: retail orders stock for resale and allocates it to a location, construction orders materials and allocates them to works. The separating signal is whether the destination is a site or a store | §3.9: “Topic answers what a file is about, while purpose answers what the file was for.” |
| log.shipment | a delivery note is the buyer's evidence of receipt; a consignment note is the carrier's contract of carriage. They travel together and name the same goods | §3.8: “The system must separate roles that happen to contain the same entity type.” |

### Sensitivity

`none` — Ordering records concern goods and companies. None of §8.4's named categories is routine. No handling class is set here; that is P7's.

---

## `trade.timesheet` — Labour timesheets and site attendance

Who worked, where, for how long, and at what rate — the record that becomes a payroll run and a cost allocation.

**Provenance:** **proposal** — new — the design does not name this domain, and nothing here is asserted as the design's

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `worker` | string | as named on the sheet | `validated` | §3.8's caution applies inverted: normally “It should avoid using authorship or creator identity as a destination dimension.”, but here the worker is the subject of the record rather than its author, which is exactly the role distinction §3.8 asks for. |
| `pay_period` | string | week ending 2026-05-17 | `direct` | §3.13: “A direct fact was read from a reliable and explicit source, such as a content hash, EXIF timestamp, document title, or labeled form field.” — a labeled field, and the unit the whole domain is batched in. |
| `project_or_job` | string | Riverside Phase 2 | `validated` | The cost centre. A timesheet's second purpose is allocating labour to works, which is why the same sheet belongs to a project and to a payroll run. |
| `hours` | string | as tabulated on the sheet | `direct` | §2.3: “Tables matter because resumes, forms, applications, invoices, and administrative documents often place their most useful information in cells rather than body paragraphs.” — hours live in cells. This catalogue holds no number. |
| `employer_or_agency` | string | Keldon Mechanical Ltd | `validated` | §3.8: “The system must separate roles that happen to contain the same entity type.” — direct employee, agency worker and self-employed subcontractor are three statuses that produce identical-looking sheets with different consequences. |
| `approval` | string | approved by site manager | `validated` | An approval signature or an approver field is what turns a submitted sheet into a payable one, and it is a labeled field on almost every form. |
| `engagement_status` | string | agency | `llm_supported` | Whether the worker is employed, agency-supplied or self-employed is rarely a labeled field and drives the sheet's entire downstream treatment. |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.3, §3.5):

- timesheet language ('timesheet' | 'time sheet' | 'week ending' | 'hours worked' | 'start' and 'finish' as column headings) co-occurring with a named worker or a worker identifier
- a labeled week-ending or pay-period field co-occurring with an hours table and an approval field — §2.3: “Tables matter because resumes, forms, applications, invoices, and administrative documents often place their most useful information in cells rather than body paragraphs.”
- a spreadsheet whose sheet names are pay periods and whose column headers include a worker column — §2.9: “Spreadsheets such as XLSX, XLS, CSV, TSV, ODS, and Numbers exports should yield workbook or file metadata, sheet names, column headers, visible cell values, table-like regions, formulas only when useful, and dates or identifiers from labeled cells.”

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- a photographed handwritten sheet where names and hours are legible only in part
- a message stating hours worked that functions as the timesheet
- an aggregated allocation report that must be distinguished from the underlying sheets

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10):

- a person's name — §3.8: “A folder should not become a collection point for everything produced by the same person or organization.”
- an hours-looking number, which appears in quotes, hire records, allocation reports and invoices
- a week-ending date, which is a filing convention shared with rotas, dispatch sheets and production reports
- the word 'hours', which is also opening hours, driving hours and site hours

### Work types

`timesheet`, `attendance record`, `allocation sheet`, `day-works sheet`, `overtime authorisation`, `payroll submission`

### Grouping reasons (§4)

- one pay period's sheets across all workers
- one worker's sheets across a project
- one project's labour allocation across periods

### Template (§5)

`employer → pay period → project`

Time first: **no**

Deliberately NOT worker-first. §3.8: “It should avoid using authorship or creator identity as a destination dimension.” and “A folder should not become a collection point for everything produced by the same person or organization.” — a folder per person is the exact anti-pattern that sentence describes, and it is also the arrangement that spreads employment data across the widest surface. The pay period leads inside the employer because that is the batch the records are produced, approved and paid in; this is the one record domain in the slice where time genuinely sits high, and it still is not first. “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders.” is honoured by keeping the employer above it.

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| cons.site-diary | the diary records presence as narrative; the timesheet records hours for payment. The separating signal is a rate, an approval or a pay period | §3.9: “Topic answers what a file is about, while purpose answers what the file was for.” |
| biz.payroll-employer | THE BOUNDARY. The timesheet is the working input; the payroll run is the accounting output and carries a tax period, statutory deductions and an employer reference. The timesheet exists even when no payroll is run from it | §3.9: “Topic answers what a file is about, while purpose answers what the file was for.” |
| retail.store-ops | a rota is a plan and a timesheet is a record. They use the same names, the same week and often the same spreadsheet, and only the tense separates them | §4.9: “when one high-frequency entity acts as the only bridge” |

### Sensitivity

`potentially_sensitive` — §2.9's phrase “while treating addresses and message content as potentially sensitive” only. A timesheet is employment material naming individuals and frequently carries pay rates and worker identifiers. §8.4 names “identity documents, account statements, tax records, medical information, legal records, credentials, private correspondence, GPS metadata, employment materials, and educational records” — employment materials are on that list by name — and requires privacy policy to be enforced before content reaches any model, which is why this domain is designed to work from its direct and validated fields alone. The handling class is P7's and is not set here.

---

## `cons.variation-claim` — Variations, instructions and claims

Changes to what was agreed and the arguments about who pays for them — the most contested paperwork on any site.

**Provenance:** **proposal** — new — the design does not name this domain, and nothing here is asserted as the design's

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `project` | string | Riverside Phase 2 | `validated` | A variation exists only against a contract. §5.5: “a parent dimension should provide the context required to understand the child” |
| `instruction_reference` | string | AI-023 | `validated` | §3.5's model: an instruction number is a fact only “when the engine finds a course-code pattern together with academic context”, the corroborating context being instruction language. Numbering restarts per project, which is why the project is required. |
| `change_type` | string | variation | `validated` | Instruction, variation, confirmation of verbal instruction, extension-of-time claim and loss-and-expense claim are different objects with different consequences and different evidence. |
| `issued_by` | string | the contract administrator named on the instruction | `validated` | §3.8: “The system must separate roles that happen to contain the same entity type.” — only certain parties may instruct, so who issued it is the field that decides whether it is an instruction at all. |
| `instruction_date` | date | 2026-06-11 | `direct` | §3.13: “A direct fact was read from a reliable and explicit source, such as a content hash, EXIF timestamp, document title, or labeled form field.” Notice periods run from it, which is what makes the date load-bearing rather than incidental. |
| `scope_of_change` | string | additional drainage to plot 14 rear | `llm_supported` | Prose. §3.5: “It can only propose facts that belong to the active domain schema, and it must cite exact supporting evidence already extracted from the file.” |
| `claim_basis` | string | delay caused by late release of information | `llm_supported` | A claim is an argument, and reading it is precisely the interpretation §3.5 reserves for the model. |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.3, §3.5):

- instruction language ('architect's instruction' | 'contract instruction' | 'variation order' | 'confirmation of verbal instruction' | 'change order') co-occurring with a project reference and an issuing party block
- an instruction-reference pattern co-occurring with a labeled instruction date and a scope description
- claim language ('extension of time' | 'loss and expense' | 'notice of delay' | 'relevant event') co-occurring with a project and a contract reference

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- an email that instructs a change without using instruction language, which is how most variations actually start
- distinguishing a variation from a defect, where the same works are described and only liability differs
- a claim narrative whose basis must be read across many pages before it can be classified

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10):

- a bare instruction reference
- the word 'variation', which also means a variation to a lease, a licence variation and a price variation
- the word 'claim', which in this slice means an insurance claim, a warranty claim, a shortage claim and a contractual claim
- a date on its own — §3.10: “The product must not use fuzzy date parsing because file names and documents frequently contain numbers that look like years but are course identifiers, version numbers, build numbers, ZIP codes, or other unrelated values.”

### Work types

`instruction`, `variation order`, `confirmation of verbal instruction`, `delay notice`, `extension-of-time claim`, `loss-and-expense claim`, `quantified assessment`

### Grouping reasons (§4)

- one change from instruction to valuation to final account line
- one claim and every diary, programme and instruction it cites
- one project's instruction register as a numbered run

### Template (§5)

`project → change type → instruction`

Time first: **no**

§5.5: “a parent dimension should provide the context required to understand the child” — an instruction number is unique only within a project, and a claim is only readable once its type is known. Time does not lead: a claim reaches back across the whole contract period and filing it by year would separate it from the events it argues about — “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders.”

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| cons.snagging | a defect is remedied at the contractor's cost; a variation is paid for. The paperwork can be word-for-word identical and only the contractual conclusion differs, which is a judgement the engine must leave to the user | §6.10: “Correct abstention is a successful outcome because the product’s goal is reliable organization, not maximum file movement.” |
| trade.quote-estimate | a price for extra work on a live job is a variation; the same price before any job exists is a quote. The separating signal is a reference to an existing contract or job that the priced work amends | §4.8: “that each fact or label belongs to an allowed domain schema” |
| cons.final-account | variations are the input, the final account is the settlement. The final account restates every variation and so contains their references, which makes it retrieve them and must not make it absorb them | §4.8: “an application packet does not silently absorb a document with a conflicting target institution” |

### Sensitivity

`none` — Contractual change records concern works and companies. None of §8.4's named categories is routine. Where a claim becomes a dispute it acquires legal-record character and §8.4's classification is evidence-backed and revisable for that case. No handling class is set here; that is P7's.

---

## `cons.final-account` — Valuations, retention and final accounts

Interim valuations, certificates and the closing settlement of a contract — money as the contract sees it, before accounting sees it.

**Provenance:** **inference** — extends a design-named domain or template situation; the cite supports the extension, not the whole entry

**Cite:** Extends §3.11's Finance schema “Finance files may use institution, account type, tax year, and record type.” by exception: a valuation has no institution and no account, and its period is a valuation cycle rather than a tax year, which is what makes it a construction record and not a finance one

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `project` | string | Riverside Phase 2 | `validated` | Valuation numbering is per contract. §5.5: “a parent dimension should provide the context required to understand the child” |
| `valuation_number` | string | valuation 11 | `direct` | §3.13: “A direct fact was read from a reliable and explicit source, such as a content hash, EXIF timestamp, document title, or labeled form field.” — a labeled field, and the sequence that orders the whole domain. |
| `valuation_period` | date range | 2026-06-01 to 2026-06-30 | `direct` | A labeled field. §3.10's explicit-regex path only: “The product must not use fuzzy date parsing because file names and documents frequently contain numbers that look like years but are course identifiers, version numbers, build numbers, ZIP codes, or other unrelated values.” |
| `certifying_party` | string | the contract administrator named on the certificate | `validated` | §3.8: “The system must separate roles that happen to contain the same entity type.” — the party who applies, the party who certifies and the party who pays are three roles, and a payment certificate names all three. |
| `account_stage` | string | final account | `validated` | Interim valuation, penultimate certificate, final certificate and final account are distinct stages with distinct consequences, and the stage is stated on the face of the document. |
| `retention_status` | string | half released at practical completion | `llm_supported` | Retention release is described in prose against contract clauses. §3.13: “An LLM-supported fact was proposed by a language model from a bounded evidence packet, cited exact supporting text or metadata, and passed deterministic validation.” |
| `agreed_sum` | string | as stated on the certificate | `direct` | §3.11 permits “Each domain activates only a small set of relevant fields, usually three to six that may help build a future folder proposal and several additional fields used only for search, privacy protection, explanation, or later review.” — a search and explanation field. This catalogue holds no figure. |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.3, §3.5):

- valuation language ('interim valuation' | 'payment certificate' | 'final account' | 'retention' | 'practical completion') co-occurring with a project reference and a certifying-party block
- a labeled valuation-number and valuation-period pair, which is a structure unique to this domain in this slice
- a final-account structure: a contract sum, a schedule of variations and an adjusted total, appearing together in one document

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- a spreadsheet that is the final account with no title, whose stage must be read from its columns
- correspondence agreeing an account in principle, which is often the only record that a settlement happened
- distinguishing a contractor's application from the certificate that answers it when both use the same template

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10):

- a currency amount — the most over-firing pattern in any money-bearing domain
- the word 'certificate' — see the certificate collision list; this slice has at least six kinds
- a valuation number, which shares a shape with an instruction number and an invoice number
- the word 'retention', which is also a records-retention policy term

### Work types

`interim application`, `interim valuation`, `payment certificate`, `pay-less notice`, `final account`, `retention release`, `statement of final account`

### Grouping reasons (§4)

- one valuation cycle — application, valuation, certificate, notice, payment
- one project's valuations as a numbered run to final account
- the final account and every variation it settles

### Template (§5)

`project → account stage → valuation`

Time first: **no**

§5.5: “a parent dimension should provide the context required to understand the child” — a valuation number is meaningless outside its project. Stage sits above the number because interim and final material are consulted for different reasons years apart. Time does not lead: “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders.”, and a contract's valuations must stay in one run rather than split across calendar years.

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| biz.invoice-issued | THE BOUNDARY, in its most confusing form. A payment certificate authorises payment; the invoice raised against it is the accounting record. On many contracts the certificate is the invoice, and the file then genuinely holds both domains' facts — which §3.11 permits rather than forces a choice about | §3.11: “One file may hold facts from more than one domain without losing information.” |
| cons.variation-claim | variations feed the account. The account cites their references and must retrieve them without absorbing them | §4.8: “an application packet does not silently absorb a document with a conflicting target institution” |
| cons.subcontract | the same valuation machinery runs down the contractual chain: the contractor's application to the employer and the subcontractor's application to the contractor look identical and differ only in who is named as payer | §3.8: “The system must separate roles that happen to contain the same entity type.” |

### Sensitivity

`none` — Contract valuations concern works and companies rather than individuals. None of §8.4's named categories is routine. No handling class is set here; that is P7's.

### Open question — Joseph's call, unresolved

> Where does a file that is BOTH a working document and an accounting record physically live? This slice and the finance slice both have a legitimate claim on the same PDF — a payment certificate that is also an invoice, a delivery note reconciled into a purchase ledger, a hire contract behind a hire invoice, a utility bill that is also a meter record. §3.11 settles the FACTS: “One file may hold facts from more than one domain without losing information.” and “At the pre-sorting stage, the product does not need to decide which of those perspectives will ultimately determine its physical location.”. It does not settle the PATH, and §6.9 makes that a policy the user sets rather than a rule the engine applies: the design's own options are a shared branch, a primary-home convention, an alias convention, or mandatory review. Joseph decides which of those is the default for the trades-and-finance overlap, and the answer applies to roughly a dozen entries in this file. There is a second-order consequence: the finance slice marks its domains “while treating addresses and message content as potentially sensitive” and this slice marks many of the same files `none`, so whichever branch wins the path must not be allowed to weaken the marking — §3.15's direction is one-way: “Finance, identity, medical, and legal material should be implemented first as safety domains, meaning the system detects and protects them before any cloud or automated placement decision is allowed.”

---

## `prop.sale-purchase` — Residential sale and purchase

Buying or selling a home — one transaction, one property, two sides, and a pack of documents assembled for a single purpose.

**Provenance:** **inference** — extends a design-named domain or template situation; the cite supports the extension, not the whole entry

**Cite:** Extends §5.7's named “The product should eventually maintain a library of roughly 200–300 domain-specific templates, covering common organizational situations such as academic programs, university applications, recruiting processes, client engagements, research workflows, financial records, travel, legal matters, creative projects, software repositories, personal administration, and photo collections.” where it names legal matters, and is the clearest instance in this slice of §3.9's purpose-coherent packet: “The documents are content-incoherent but purpose-coherent.”

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `property_address` | string | Old Mill House, Bakers Lane | `validated` | The transaction's subject. A conveyancing file is retrieved by address and by nothing else, years later. |
| `transaction_side` | string | purchase | `validated` | §3.8: “The system must separate roles that happen to contain the same entity type.” — buying and selling produce mirror-image packs naming the same parties, and mixing them is this domain's characteristic failure. |
| `matter_reference` | string | as issued by the conveyancer | `validated` | §3.5's model: a matter reference is a fact only “when the engine finds a course-code pattern together with academic context”, the corroborating context being conveyancing language. |
| `counterparty` | string | the other side named in the correspondence | `validated` | §3.8 again: buyer, seller, each side's conveyancer, the lender and the agent are five parties one letter can name. |
| `completion_date` | date | 2026-09-04 | `direct` | §3.13: “A direct fact was read from a reliable and explicit source, such as a content hash, EXIF timestamp, document title, or labeled form field.” — a labeled field, and the event the whole pack is organised around. §3.10's explicit-regex path only. |
| `document_class` | string | searches | `validated` | Contract, searches, enquiries, title, mortgage offer, completion statement — the pack's internal structure, and the level a user navigates once inside it. |
| `tenure` | string | as stated on the title document | `llm_supported` | Tenure categories are jurisdiction-defined and are not enumerated here. §3.5: “it may extract only fields allowed by the relevant schema” |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.3, §3.5):

- conveyancing language ('completion statement' | 'contract for sale' | 'transfer deed' | 'requisitions on title' | 'exchange of contracts') co-occurring with a property address
- a matter-reference pattern co-occurring with a conveyancer's letterhead and a property address in one document
- a search-result structure — an authority name, a property address and a labeled search type — which is a shape unique to this domain

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- an identity or funds document that belongs to the pack only by purpose, which is §3.9's case exactly and is not visible in the document itself
- correspondence that never restates the address or the reference
- a scanned historic deed whose parties and property must be read from prose

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10):

- a property address — every domain in this half of the slice carries one, and a conveyancing pack, a tenancy, a survey and a listing can all name the same house in the same month
- a person's name — §3.8: “It should avoid using authorship or creator identity as a destination dimension.”
- a currency amount
- a conveyancer's name, which is a high-frequency entity across every file they touch — §4.9: “when one high-frequency entity acts as the only bridge”

### Work types

`contract`, `title document`, `search result`, `enquiries and replies`, `mortgage offer`, `completion statement`, `identity and funds evidence`, `correspondence`

### Grouping reasons (§4)

- one transaction on one property from instruction to completion
- one property's transactions across owners over time
- the identity and funds evidence assembled for one completion

### Template (§5)

`property → transaction → document class`

Time first: **no**

§5.5: “a parent dimension should provide the context required to understand the child” — a search result is meaningless without the transaction and a transaction without the property. Property leads rather than date because a house is bought and sold decades apart and the address is what anyone remembers. §3.9 is the reason document class sits last and not first: “The documents are content-incoherent but purpose-coherent.”, so splitting the pack by content before the transaction is known would destroy exactly the coherence that makes it a pack. Time does not lead: “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders.”

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| prop.mortgage-brokering | the mortgage offer sits in both files, and the broker's file is about the borrower while the conveyancing file is about the property. The separating signal is whether the document's addressee is the lender's customer or the property's buyer | §3.8: “The system must separate roles that happen to contain the same entity type.” |
| prop.survey-valuation | a survey commissioned for a purchase is a pack member and a survey record. §3.11 keeps both fact sets rather than forcing a choice | §3.11: “One file may hold facts from more than one domain without losing information.” |
| legal.contracts | a contract for sale is a contract, and the finance-legal slice owns contracts in general. This domain's claim is the transaction; the general claim is the instrument. Where they meet, the transaction is the more useful home because the pack is what a user retrieves | §3.9: “Topic answers what a file is about, while purpose answers what the file was for.” |
| pers.home-tenure | the household slice owns the occupier's own file about their home; this domain owns the transaction that moved it. The separating signal is whether the file is a professional's matter file or a householder's personal record, and for someone buying their own house it is both | §3.8: “The system must separate roles that happen to contain the same entity type.” |

### Sensitivity

`potentially_sensitive` — §2.9's phrase “while treating addresses and message content as potentially sensitive” only. A conveyancing pack routinely contains identity documents, source-of-funds bank statements and legal records — §8.4 names “identity documents, account statements, tax records, medical information, legal records, credentials, private correspondence, GPS metadata, employment materials, and educational records” and §4.9 adds that “Rare but sensitive files such as passports, visas, and legal documents may be surfaced as protected records even when they do not meet a normal group-size threshold.” §3.15's direction governs this whole file: “Finance, identity, medical, and legal material should be implemented first as safety domains, meaning the system detects and protects them before any cloud or automated placement decision is allowed.” The handling class is P7's (§8.4) and is not set here.

---

## `prop.tenancy` — Lettings and tenancy management

One tenancy of one property — agreement, deposit, compliance certificates, rent record, correspondence and the end-of-tenancy reckoning.

**Provenance:** **inference** — extends a design-named domain or template situation; the cite supports the extension, not the whole entry

**Cite:** Extends §5.7's “The product should eventually maintain a library of roughly 200–300 domain-specific templates, covering common organizational situations such as academic programs, university applications, recruiting processes, client engagements, research workflows, financial records, travel, legal matters, creative projects, software repositories, personal administration, and photo collections.” where it names legal matters, and relies on §3.8's role separation throughout: “The system must separate roles that happen to contain the same entity type.”

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `property_address` | string | 14 Elm Road, Flat 2 | `validated` | The let unit. A property is let repeatedly, so the address is the stable parent and the tenancy is the changing child. |
| `tenancy_reference` | string | as issued by the agent | `validated` | §3.5's model: a fact only “when the engine finds a course-code pattern together with academic context”, the corroborating context being tenancy language. |
| `tenant` | string | as named on the agreement | `validated` | §3.8: “The system must separate roles that happen to contain the same entity type.” — tenant, guarantor, landlord, agent and occupier are five roles a tenancy pack names, and the agent's name appears on every page of all of them. |
| `landlord` | string | as named on the agreement | `validated` | The other principal party, and the one whose file this usually is. |
| `tenancy_term` | date range | 2026-07-01 to 2027-06-30 | `direct` | §3.13: “A direct fact was read from a reliable and explicit source, such as a content hash, EXIF timestamp, document title, or labeled form field.” — a labeled field, and what makes two tenancies of one flat separable. §3.10's explicit-regex path only: “The product must not use fuzzy date parsing because file names and documents frequently contain numbers that look like years but are course identifiers, version numbers, build numbers, ZIP codes, or other unrelated values.” |
| `document_class` | string | deposit protection | `validated` | Agreement, deposit, references, compliance certificates, rent statements, notices and end-of-tenancy documents — the pack's internal structure. |
| `tenancy_type` | string | as stated on the agreement | `llm_supported` | Tenancy types and the notices attached to them are jurisdiction-defined and are not enumerated here. §3.5: “it may extract only fields allowed by the relevant schema” |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.3, §3.5):

- tenancy language ('tenancy agreement' | 'the landlord' and 'the tenant' as defined parties | 'deposit protection' | 'rent payable' | 'notice to quit') co-occurring with a property address
- a labeled term-start and term-end pair co-occurring with a rent field and a named tenant block
- a deposit-protection record: a scheme reference, a deposit amount label and a property address in one document

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- correspondence about a tenancy that names neither the reference nor the term
- a reference or credit check that belongs to the pack by purpose and states no tenancy
- distinguishing a renewal from a new tenancy of the same property to the same tenant, which only prose settles

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10):

- a property address — shared with sale, survey, listing, service charge and certificate records for the same flat
- a person's name — §3.8: “A folder should not become a collection point for everything produced by the same person or organization.”
- an agent's name — a high-frequency bridge across every property they manage: “when one high-frequency entity acts as the only bridge”
- a date range, whose shape is shared with insurance, hire and statement periods

### Work types

`tenancy agreement`, `reference and credit check`, `deposit protection record`, `compliance certificate`, `rent statement`, `notice`, `renewal`, `end-of-tenancy correspondence`

### Grouping reasons (§4)

- one tenancy from agreement to end-of-tenancy settlement
- one property's tenancies over time
- the compliance certificates valid during one tenancy

### Template (§5)

`property → tenancy → document class`

Time first: **no**

§5.5: “a parent dimension should provide the context required to understand the child” — a notice is meaningless without the tenancy and a tenancy without the property. Property leads rather than tenant because §3.8 warns against making a person a collector: “A folder should not become a collection point for everything produced by the same person or organization.” — and because a landlord's file is organised by what they own. Time does not lead: “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders.”

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| prop.inventory-inspection | the check-in and check-out inventories belong to this tenancy and are also a photograph-set domain with its own capture discipline. §3.11 keeps both fact sets | §3.11: “One file may hold facts from more than one domain without losing information.” |
| trade.compliance-certificate | a safety certificate is the property's record and the tenancy's obligation. It genuinely doubles, and forcing a single home loses one of the two retrieval routes | §3.11: “One file may hold facts from more than one domain without losing information.” |
| prop.block-management | a leaseholder in a block is a landlord to their own tenant; the block file and the tenancy file name the same flat and different parties | §3.8: “The system must separate roles that happen to contain the same entity type.” |

### Sensitivity

`potentially_sensitive` — §2.9's phrase “while treating addresses and message content as potentially sensitive” only. A tenancy pack routinely contains tenant identity documents, references, credit checks and private correspondence about arrears — §8.4 names “identity documents, account statements, tax records, medical information, legal records, credentials, private correspondence, GPS metadata, employment materials, and educational records”. The handling class is P7's and is not set here.

---

## `prop.inventory-inspection` — Property inventories and condition inspections

A dated photographic record of a property's condition and contents, made so that the state at one moment can be proved against another.

**Provenance:** **inference** — extends a design-named domain or template situation; the cite supports the extension, not the whole entry

**Cite:** Extends the design-named Photos domain — §3.11: “Photos may use capture year, event, location, people, camera information, and media type.” — into a record domain whose evidence is capture-based. §2.6 governs the image half: “The system should therefore use a hierarchy of signals: camera EXIF is strong photo evidence; capture time, GPS, and sensor-shaped dimensions reinforce it; exact display resolutions, PNG format, and software metadata may support a screenshot hypothesis; conflicting signals should lead to abstention rather than an invented classification.”

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `property_address` | string | 14 Elm Road, Flat 2 | `validated` | The subject. An inventory of the wrong flat is worthless, which is why the address is validated and not inferred. |
| `inspection_type` | string | check-out | `validated` | Check-in, interim, check-out and periodic inspections are the same artefact for different moments, and the type is what makes a comparison possible. |
| `inspection_date` | date | 2027-06-28 | `direct` | §3.13: “A direct fact was read from a reliable and explicit source, such as a content hash, EXIF timestamp, document title, or labeled form field.” — the report states it and §2.6 corroborates it from EXIF: “Camera EXIF, GPS, and capture time can support deterministic photo-event proposals.” An inventory whose date is wrong proves the opposite of what it was made for. |
| `tenancy_reference` | string | as issued by the agent | `validated` | What ties the inventory to the letting it evidences, and what separates it from a construction schedule of condition. |
| `inspector` | string | as named on the report | `direct` | Recorded because an inventory is signed evidence. §3.8: “It should avoid using authorship or creator identity as a destination dimension.” |
| `condition_findings` | string | carpet stained, bedroom 2 | `llm_supported` | Captions and prose. §3.5: “It can only propose facts that belong to the active domain schema, and it must cite exact supporting evidence already extracted from the file.” |
| `capture_time` | date | as recorded in EXIF | `direct` | The photographs' own timestamps, which are what make the report evidential rather than assertive. |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.3, §3.5):

- inventory language ('inventory and schedule of condition' | 'check-in report' | 'check-out report' | 'meter readings' as a labeled section) co-occurring with a property address
- a report structure pairing room headings with embedded photographs and condition captions, co-occurring with a labeled inspection date
- an image set whose EXIF capture times cluster inside one visit and whose GPS matches a property already known from a tenancy — §2.6: “Camera EXIF, GPS, and capture time can support deterministic photo-event proposals.”

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- a bare photograph set with no report, where the purpose — inventory, snag, survey or insurance claim — is only in the content
- a set stripped of EXIF by a messaging app, where §2.6's warning bites: “the system must not mistake the absence of EXIF for proof that an image is a screenshot”
- a report whose inspection type is stated only by the tense of its narrative

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10):

- the absence of EXIF — §2.6: “the system must not mistake the absence of EXIF for proof that an image is a screenshot”
- OCR text density on the photographs — §2.6: “OCR text density is also not a reliable screenshot detector because receipts, document scans, whiteboards, and photographs of pages can all contain dense text.”
- a property address
- a room name or a condition word, which appear in listings, surveys, snag lists and insurance claims alike

### Work types

`inventory and schedule of condition`, `check-in report`, `check-out report`, `interim inspection`, `condition photograph set`, `meter reading record`, `deposit deduction schedule`

### Grouping reasons (§4)

- one inspection visit — report plus the photograph set captured the same day at the same address
- the check-in and check-out pair for one tenancy, which only mean anything together
- one property's inspection history across tenancies

### Template (§5)

`property → tenancy → inspection date`

Time first: **no**

NOT time-first, and the reason is worth stating because this domain is capture-based. §5.5's exception is conditional on its own premise — “Photos and capture-based media are the major exception: time often belongs first because capture date is a defining aspect of the material.” — and here the capture date is defining only in relation to a tenancy: a check-out photograph proves nothing until you know which tenancy ended. The property is the durable subject and the tenancy is what makes the date legible, so both outrank it. §5.5's “a parent dimension should provide the context required to understand the child” decides it.

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| cons.progress-photos | both are geotagged interior photograph sets at a private address. The separating signal is a companion report naming a tenancy; progress photography has no report and no tenant | §2.6: “The system should therefore use a hierarchy of signals: camera EXIF is strong photo evidence; capture time, GPS, and sensor-shaped dimensions reinforce it; exact display resolutions, PNG format, and software metadata may support a screenshot hypothesis; conflicting signals should lead to abstention rather than an invented classification.” |
| cons.snagging | a check-out damage schedule and a snag list have the same table shape. The separating signal is a tenancy reference against a plot or unit reference | §3.9: “Topic answers what a file is about, while purpose answers what the file was for.” |
| prop.tenancy | the inventory is a member of the tenancy pack and its own record; it retrieves the tenancy and must not be absorbed into it, because a property's inspection history spans tenancies | §3.11: “One file may hold facts from more than one domain without losing information.” |
| pers.household-inventory | an owner photographing their possessions for insurance and an agent photographing a let flat for a deposit produce the same images of the same rooms. The separating signal is a tenancy reference; without one the engine should abstain | §6.10: “Correct abstention is a successful outcome because the product’s goal is reliable organization, not maximum file movement.” |

### Sensitivity

`potentially_sensitive` — §2.9's phrase “while treating addresses and message content as potentially sensitive” only. An inventory photographs the inside of an occupied home, including a tenant's possessions, and every frame carries GPS. §8.4 names “identity documents, account statements, tax records, medical information, legal records, credentials, private correspondence, GPS metadata, employment materials, and educational records” — GPS metadata is on that list by name. The handling class is P7's and is not set here.

---

## `prop.service-charge` — Service charges and leaseholder accounts

What a leaseholder is asked to pay towards a building's running costs — budgets, demands, accounts and the arguments about them.

**Provenance:** **proposal** — new — the design does not name this domain, and nothing here is asserted as the design's

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `building` | string | Wharf Court | `validated` | The block whose costs are being shared. §5.5: “a parent dimension should provide the context required to understand the child” — a demand is only interpretable once the building is known. |
| `unit` | string | Flat 12 | `validated` | The apportioned unit. It is what turns a building's budget into one person's bill. |
| `charge_year` | string | as stated on the demand | `validated` | Service-charge years are set by the lease and rarely match a calendar or tax year, which is why this is a domain field and not a generic date. |
| `charge_type` | string | estimated on-account demand | `validated` | Budget, on-account demand, balancing charge, reserve-fund contribution and certified accounts are distinct documents in a fixed annual cycle. |
| `managing_agent` | string | as named on the demand | `validated` | §3.8: “The system must separate roles that happen to contain the same entity type.” — freeholder, managing agent, resident association and leaseholder are four roles and a demand names all four. |
| `apportionment_basis` | string | as stated in the lease | `llm_supported` | How the share is calculated is stated in lease prose. §3.5: “It can only propose facts that belong to the active domain schema, and it must cite exact supporting evidence already extracted from the file.” |
| `arrears_status` | string | as stated on the statement | `llm_supported` | The field that makes this domain “while treating addresses and message content as potentially sensitive”, because it is a statement about a named individual's finances. |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.3, §3.5):

- service-charge language ('service charge' | 'on account' | 'balancing charge' | 'reserve fund' | 'sinking fund' | 'ground rent') co-occurring with a unit identifier and a building name
- a labeled charge-year field co-occurring with an apportionment percentage or fraction and a unit identifier
- a certified-accounts structure: a building name, an accounting year and expenditure headings in a table — §2.3: “Tables matter because resumes, forms, applications, invoices, and administrative documents often place their most useful information in cells rather than body paragraphs.”

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- correspondence disputing a charge that never restates the year or the unit
- a budget circulated as a spreadsheet with no covering document
- distinguishing a major-works consultation from an ordinary demand when both attach a cost schedule

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10):

- a currency amount
- a unit identifier such as 'Flat 12' — the most reused string in this domain and shared with tenancy, sale, snagging and inventory records for the same flat
- a building name, which behaves as a high-frequency hub across every document about it: “when one high-frequency entity acts as the only bridge”
- a percentage, which appears in apportionments, interest clauses, discounts and completion statements

### Work types

`budget`, `on-account demand`, `balancing statement`, `certified accounts`, `major-works consultation`, `arrears correspondence`, `reserve-fund statement`

### Grouping reasons (§4)

- one charge year for one building, from budget to certified accounts
- one unit's demands and statements across years
- one major-works project through its consultation and its charges

### Template (§5)

`building → charge year → document type`

Time first: **no**

§5.5: “a parent dimension should provide the context required to understand the child” — a balancing statement is meaningless without its year and a year without its building. This is the one property domain where a year sits second rather than last, because the service-charge year is a closed accounting cycle rather than a filing convenience: every document in a year answers the others. It still is not first — “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders.” — because two buildings' charge years must never merge.

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| prop.block-management | the same agent produces both. Service charge is the money cycle; block management is everything else — insurance, contractors, meetings, compliance. The separating signal is a charge year and an apportionment | §3.9: “Topic answers what a file is about, while purpose answers what the file was for.” |
| fin.financial-records | THE BOUNDARY. A demand is a working document issued under a lease; the leaseholder's payment of it is an accounting entry with a date and an amount and nothing about a building. The demand exists whether or not it is paid | §3.11: “One file may hold facts from more than one domain without losing information.” |
| prop.commercial-lease | commercial service charges follow the same cycle under a different lease regime; the separating signal is the tenure and the parties, not the document shape | §3.8: “The system must separate roles that happen to contain the same entity type.” |

### Sensitivity

`potentially_sensitive` — §2.9's phrase “while treating addresses and message content as potentially sensitive” only. Arrears statements and recovery correspondence are financial statements about named individuals; §8.4 names account statements and private correspondence in “identity documents, account statements, tax records, medical information, legal records, credentials, private correspondence, GPS metadata, employment materials, and educational records”. §3.15's direction applies: “Finance, identity, medical, and legal material should be implemented first as safety domains, meaning the system detects and protects them before any cloud or automated placement decision is allowed.” The handling class is P7's and is not set here.

---

## `prop.block-management` — Block and estate management

Running a building on behalf of its owners — insurance, contractors, compliance, meetings and leaseholder correspondence.

**Provenance:** **proposal** — new — the design does not name this domain, and nothing here is asserted as the design's

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `building` | string | Wharf Court | `validated` | The managed asset, and the only durable parent in this domain: agents change, leaseholders change, the building does not. |
| `management_function` | string | buildings insurance | `validated` | Insurance, contracts, compliance, meetings, correspondence and works are the recurring functions and the level a user navigates. |
| `managing_agent` | string | as named on the document | `validated` | §3.8: “The system must separate roles that happen to contain the same entity type.” — and the agent is the classic high-frequency hub here, appearing on every document about every building they manage. |
| `freeholder_or_rmc` | string | as named on the document | `validated` | Who actually owns or controls the building, which is distinct from who manages it and is the party a leaseholder's rights run against. |
| `policy_or_contract_period` | date range | 2026-04-01 to 2027-03-31 | `direct` | §3.13: “A direct fact was read from a reliable and explicit source, such as a content hash, EXIF timestamp, document title, or labeled form field.” — a labeled field on insurance and maintenance contracts, and the field that says whether cover is current. |
| `compliance_item` | string | fire risk assessment | `validated` | Building-safety obligations are jurisdiction-defined and are written functionally here; the item is the recurring, renewable unit. |
| `meeting_type` | string | annual general meeting | `llm_supported` | Read from the document's own description. §3.5: “it may extract only fields allowed by the relevant schema” |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.3, §3.5):

- block-management language ('managing agent' | 'freeholder' | 'residents management company' | 'communal' | 'demised') co-occurring with a building name
- an insurance-schedule structure — insurer, policy number, period and sum insured — co-occurring with a building name rather than a person or a vehicle
- a meeting-document structure: a labeled meeting type, date and attendee list naming a building or company

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- correspondence about a communal issue that names neither the building nor the agent explicitly
- a contractor quotation that must be recognised as block work rather than a leaseholder's own job
- minutes whose subject matter must be read to be classified

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10):

- a building name — “when one high-frequency entity acts as the only bridge”
- an agent's name, for the same reason and more strongly
- a policy number or a period, shared with vehicle, plant, professional and contents policies
- the word 'communal', which is ordinary English as well as a lease term

### Work types

`insurance schedule`, `maintenance contract`, `compliance assessment`, `meeting minutes`, `leaseholder correspondence`, `contractor quotation`, `section notice`

### Grouping reasons (§4)

- one building's management file across functions
- one policy or contract period across its renewals
- one compliance item across its inspection cycle

### Template (§5)

`building → function → period`

Time first: **no**

§5.5: “a parent dimension should provide the context required to understand the child” — an insurance schedule is meaningless without the building and a renewal without the function. Period sits last: “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders.”, and a building's insurance history should sit in one place rather than be split across a decade of year folders. §3.8 is why the agent is not a level: “A folder should not become a collection point for everything produced by the same person or organization.”

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| prop.service-charge | block management spends the money and service charge collects it. The separating signal is a charge year and an apportionment, which management documents do not carry | §3.9: “Topic answers what a file is about, while purpose answers what the file was for.” |
| prop.commercial-lease | managing a multi-let commercial building uses the same documents under a different lease regime and for different parties | §3.8: “The system must separate roles that happen to contain the same entity type.” |
| cons.project | major works to a block is a construction project with its own contract, drawings and valuations; the block file holds the consultation and the charge, the project file holds the build | §3.11: “One file may hold facts from more than one domain without losing information.” |

### Sensitivity

`potentially_sensitive` — §2.9's phrase “while treating addresses and message content as potentially sensitive” only. Leaseholder correspondence, disputes and arrears discussions are private correspondence about named individuals and §8.4 names that category in “identity documents, account statements, tax records, medical information, legal records, credentials, private correspondence, GPS metadata, employment materials, and educational records”. The insurance and contracting half of the domain is not sensitive; §8.4's classification being evidence-backed and revisable is what lets both live here. No handling class is set; that is P7's.

---

## `prop.commercial-lease` — Commercial leases and occupier management

Leasing business premises — the lease, its rent reviews, its schedules and the dilapidations reckoning at the end.

**Provenance:** **inference** — extends a design-named domain or template situation; the cite supports the extension, not the whole entry

**Cite:** Extends §5.7's “The product should eventually maintain a library of roughly 200–300 domain-specific templates, covering common organizational situations such as academic programs, university applications, recruiting processes, client engagements, research workflows, financial records, travel, legal matters, creative projects, software repositories, personal administration, and photo collections.” where it names legal matters, and §3.8's role separation is what keeps landlord and tenant sides apart: “The system must separate roles that happen to contain the same entity type.”

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `premises` | string | Unit 4, Northgate Retail Park | `validated` | The demised premises. A lease that cannot be tied to a unit is not usable. |
| `lease_party_role` | string | tenant | `validated` | §3.8: “The system must separate roles that happen to contain the same entity type.” — landlord, tenant, guarantor, undertenant and managing agent all appear as defined parties in one document, and which side's file this is changes everything about it. |
| `lease_term` | date range | 2026-01-01 to 2036-12-31 | `direct` | §3.13: “A direct fact was read from a reliable and explicit source, such as a content hash, EXIF timestamp, document title, or labeled form field.” — a labeled field. A commercial lease is a long-lived object and the term is its spine. §3.10's explicit-regex path only: “The product must not use fuzzy date parsing because file names and documents frequently contain numbers that look like years but are course identifiers, version numbers, build numbers, ZIP codes, or other unrelated values.” |
| `lease_event` | string | rent review | `validated` | Rent review, break option, assignment, licence to alter and renewal are dated obligations, and missing one is what this domain exists to prevent. |
| `counterparty` | string | as named in the lease | `validated` | The other principal party, distinct from the agent and from any guarantor. |
| `rent_basis` | string | as stated in the rent schedule | `llm_supported` | Rent and its review mechanism are prose clauses. §3.5: “It can only propose facts that belong to the active domain schema, and it must cite exact supporting evidence already extracted from the file.” |
| `dilapidations_stage` | string | as stated in the schedule | `llm_supported` | Interim, terminal and settled schedules are distinguished in prose and drive very different work. |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.3, §3.5):

- lease language ('the landlord' and 'the tenant' as capitalised defined parties | 'demised premises' | 'rent review' | 'break clause' | 'quiet enjoyment' | 'dilapidations') co-occurring with a premises description
- a labeled term-commencement and term-expiry pair co-occurring with a rent field and a premises block
- a rent-review or break-notice structure: a labeled event, a date and a reference to a lease dated on a stated day

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- a licence or side letter that varies a lease without restating the premises
- a schedule of dilapidations whose stage is only implied by its tense
- deciding which side's file a document belongs to when it is a copy served on both

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10):

- a premises address
- a company name — §4.9's warning transfers exactly: “A university name alone should not create a group because Columbia can appear as an authoring school, course provider, target institution, employer, research venue, or merely a cited organization.”
- the word 'lease', which is also equipment leasing, vehicle leasing and a residential lease
- a date range

### Work types

`lease`, `agreement for lease`, `rent review memorandum`, `break notice`, `licence to alter`, `schedule of dilapidations`, `assignment`, `rent schedule`

### Grouping reasons (§4)

- one lease across its full term including every variation and notice
- one property's leases across successive occupiers
- one lease event — notice, correspondence, memorandum — as a chain

### Template (§5)

`premises → lease → document type`

Time first: **no**

§5.5: “a parent dimension should provide the context required to understand the child” — a break notice is meaningless without its lease and a lease without its premises. Time is deliberately absent from the folder path even though the domain is entirely about dates: a lease spans a decade and its events must sit in one place, which is precisely what “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders.” protects.

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| legal.contracts | the finance-legal slice owns contracts in general. A lease is a contract whose subject is a place, and the place is what makes it retrievable; that is why it earns a property-side domain rather than sitting in the general contracts pile | §3.9: “Topic answers what a file is about, while purpose answers what the file was for.” |
| prop.tenancy | residential and commercial lettings are different regimes with different notices and different protections, and a residential file must never absorb a commercial document or the reverse | §4.8: “an application packet does not silently absorb a document with a conflicting target institution” |
| prop.service-charge | commercial service charge runs under the lease's own machinery; the demand belongs to the charge domain and the clause that authorises it belongs here | §3.11: “One file may hold facts from more than one domain without losing information.” |

### Sensitivity

`potentially_sensitive` — §2.9's phrase “while treating addresses and message content as potentially sensitive” only. A lease is a legal record and §8.4 names legal records in “identity documents, account statements, tax records, medical information, legal records, credentials, private correspondence, GPS metadata, employment materials, and educational records”. §3.15's direction covers it: “Finance, identity, medical, and legal material should be implemented first as safety domains, meaning the system detects and protects them before any cloud or automated placement decision is allowed.” The handling class is P7's and is not set here.

---

## `prop.development-appraisal` — Property development appraisals

The financial case for building something on a site — land cost, build cost, values, finance and the return that decides whether it happens.

**Provenance:** **proposal** — new — the design does not name this domain, and nothing here is asserted as the design's

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `scheme` | string | Bakers Lane, 9 units | `validated` | The proposed development. It is not the same as the site: one site can carry several competing schemes. |
| `site_address` | string | Bakers Lane, land rear of 40-48 | `validated` | The land in question, which is what the appraisal is bought and sold against. |
| `appraisal_version` | string | as labeled on the model | `validated` | Appraisals are re-run constantly and the version is what separates a live case from a dead one. It is a version family, not a folder level. |
| `appraisal_date` | date | 2026-02-04 | `direct` | §3.13: “A direct fact was read from a reliable and explicit source, such as a content hash, EXIF timestamp, document title, or labeled form field.” An appraisal is a snapshot of assumptions and is worthless undated. §3.10's explicit-regex path only. |
| `scheme_mix` | string | as tabulated in the model | `direct` | §2.9: “Spreadsheets such as XLSX, XLS, CSV, TSV, ODS, and Numbers exports should yield workbook or file metadata, sheet names, column headers, visible cell values, table-like regions, formulas only when useful, and dates or identifiers from labeled cells.” — the accommodation schedule lives in cells and is what makes two versions comparable. This catalogue holds no unit count. |
| `appraisal_basis` | string | residual land value | `llm_supported` | The method is stated in prose or implied by the model's structure. §3.5: “It can only propose facts that belong to the active domain schema, and it must cite exact supporting evidence already extracted from the file.” |
| `funding_assumption` | string | as stated in the finance sheet | `llm_supported` | Debt, equity and phasing assumptions are the most-changed inputs and are rarely labeled consistently. |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.3, §3.5):

- appraisal language ('residual value' | 'gross development value' | 'development appraisal' | 'build cost' and 'land cost' as paired headings | 'profit on cost') co-occurring with a site or scheme name
- a spreadsheet whose sheet names include an accommodation schedule and a cashflow, co-occurring with a site name — §2.9: “Spreadsheets such as XLSX, XLS, CSV, TSV, ODS, and Numbers exports should yield workbook or file metadata, sheet names, column headers, visible cell values, table-like regions, formulas only when useful, and dates or identifiers from labeled cells.”
- a labeled appraisal date and version co-occurring with a scheme name, which builds the version family

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- an unlabeled model whose purpose must be read from its structure
- a board paper that contains an appraisal inside a narrative
- distinguishing a developer's appraisal from a lender's or valuer's assessment of the same scheme

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10):

- a currency amount
- a site address — shared with the planning file, the construction file and the eventual sales file for the same land
- a percentage, which appears as a margin, a yield, an interest rate and an apportionment
- the word 'appraisal', which is also a staff appraisal — §3.7: “It should use word-boundary matching rather than substring matching.”

### Work types

`appraisal model`, `cashflow`, `accommodation schedule`, `cost plan`, `board or investment paper`, `sensitivity analysis`, `offer letter`

### Grouping reasons (§4)

- one scheme across its appraisal versions, as a version family
- one site across competing schemes
- one funding submission and the appraisal it was built on

### Template (§5)

`site → scheme → document type`

Time first: **no**

§5.5: “a parent dimension should provide the context required to understand the child” — a cashflow is meaningless without the scheme and a scheme without the site. Version is a family rather than a level, because a folder per version is exactly what §5.9 warns against: “It should warn when a level produces only one child, repeats a concept already expressed in the parent, creates excessive depth, or creates a large number of tiny folders.”. Time does not lead: “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders.”

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| cons.project | the appraisal justifies the build and the project executes it. The separating signal is a return metric and a land cost, which no construction contract states | §3.9: “Topic answers what a file is about, while purpose answers what the file was for.” |
| prop.survey-valuation | a valuation values what exists; an appraisal values what does not exist yet. Both produce a figure for a site and only the tense separates them | §3.9: “Topic answers what a file is about, while purpose answers what the file was for.” |
| corp.fundraising-investor | an appraisal inside an investment pack is serving a fundraise. §3.9's purpose split applies and the file legitimately holds both | §3.9: “The documents are content-incoherent but purpose-coherent.” |

### Sensitivity

`none` — A development appraisal concerns land and money at a scheme level. It is commercially confidential, which is not one of §8.4's named categories, and no handling class is set here; that is P7's.

---

## `prop.survey-valuation` — Property surveys and valuations

A professional opinion on what a building is worth or what is wrong with it, addressed to whoever commissioned it.

**Provenance:** **proposal** — new — the design does not name this domain, and nothing here is asserted as the design's

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `property_address` | string | Old Mill House, Bakers Lane | `validated` | The valued or inspected property. |
| `report_type` | string | homebuyer survey | `validated` | Valuation, condition survey, building survey and specialist inspection are different products with different scopes; report-product names are jurisdiction-specific and are written functionally here. |
| `instructing_party` | string | as named on the report | `validated` | §3.8: “The system must separate roles that happen to contain the same entity type.” — the lender who instructs, the borrower who pays, the surveyor who signs and the owner who is inspected are four roles and a mortgage valuation names all four. |
| `valuation_date` | date | 2026-08-02 | `direct` | §3.13: “A direct fact was read from a reliable and explicit source, such as a content hash, EXIF timestamp, document title, or labeled form field.” A valuation speaks as at a date and nothing else. §3.10's explicit-regex path only: “The product must not use fuzzy date parsing because file names and documents frequently contain numbers that look like years but are course identifiers, version numbers, build numbers, ZIP codes, or other unrelated values.” |
| `surveyor` | string | as named and qualified on the report | `direct` | Recorded because the report is signed and its professional standing matters. §3.8: “It should avoid using authorship or creator identity as a destination dimension.” |
| `valuation_figure` | string | as stated in the report | `direct` | §3.11 permits “Each domain activates only a small set of relevant fields, usually three to six that may help build a future folder proposal and several additional fields used only for search, privacy protection, explanation, or later review.” — a search and explanation field, never a folder dimension. This catalogue holds no figure. |
| `defect_findings` | string | as described in the report | `llm_supported` | The narrative and its risk ratings. §3.5: “It can only propose facts that belong to the active domain schema, and it must cite exact supporting evidence already extracted from the file.” |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.3, §3.5):

- valuation language ('market value' | 'valued at' | 'as at the date of inspection' | 'reinstatement cost') co-occurring with a property address and a signed surveyor block
- a report structure pairing a labeled inspection date, a property address and a professional qualification block
- a lender-instruction structure: a lender name, a case or application reference and a property address in one document

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- a scanned historic report whose type is not stated on its face
- a specialist inspection — damp, timber, structural — that must be recognised as a survey rather than a quotation for the remedial work it recommends
- a report that both values and condemns, where the report type is genuinely mixed

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10):

- a property address
- a currency amount
- a surveyor's or firm's name — §3.8: “It should avoid using authorship or creator identity as a destination dimension.”
- the word 'survey', which in this slice is also a measured survey, an asbestos survey and a customer survey

### Work types

`mortgage valuation`, `homebuyer report`, `building survey`, `reinstatement assessment`, `specialist inspection report`, `valuation for probate or transfer`

### Grouping reasons (§4)

- one property's reports over time
- one transaction's survey and the valuation the lender relied on
- one surveyor's instruction and the report answering it

### Template (§5)

`property → report type → valuation date`

Time first: **no**

§5.5: “a parent dimension should provide the context required to understand the child” — a valuation figure is meaningless without the property and a report type is what makes two reports on one property distinguishable. Date sits last despite being what a valuation speaks as at, because a property is valued rarely and the address is the retrieval key: “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders.”

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| prop.sale-purchase | a survey commissioned for a purchase is a member of that pack and a report in its own right. §3.11 keeps both fact sets | §3.11: “One file may hold facts from more than one domain without losing information.” |
| cons.site-survey | a valuation prices a building; a measured survey dimensions it to design work on it. The separating signal is a valuation figure, which a measured survey never carries | §3.9: “Topic answers what a file is about, while purpose answers what the file was for.” |
| prop.mortgage-brokering | the lender's valuation sits in the broker's file as evidence and in the property's file as a record | §4.9: “A file may validly belong to more than one accepted group” |

### Sensitivity

`potentially_sensitive` — §2.9's phrase “while treating addresses and message content as potentially sensitive” only. A mortgage valuation names the borrower, the lender and a case reference and is a financial document about a named individual's transaction; §8.4 names account statements and legal records in “identity documents, account statements, tax records, medical information, legal records, credentials, private correspondence, GPS metadata, employment materials, and educational records”. The handling class is P7's and is not set here.

---

## `prop.listing` — Estate agency listings and property marketing

The material made to sell or let a property — particulars, photographs, floor plans, portal copy and the offers that come back.

**Provenance:** **proposal** — new — the design does not name this domain, and nothing here is asserted as the design's

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `property_address` | string | 14 Elm Road, Flat 2 | `validated` | The marketed property. |
| `listing_reference` | string | as issued by the agent | `validated` | §3.5's model: a fact only “when the engine finds a course-code pattern together with academic context”, the corroborating context being marketing language. |
| `listing_type` | string | for sale | `validated` | Sale and letting particulars for the same flat are different campaigns with different copy, different photographs and different prices. |
| `marketing_status` | string | under offer | `llm_supported` | Status changes constantly and is usually stated in an email rather than a labeled field. §3.13: “An LLM-supported fact was proposed by a language model from a bounded evidence packet, cited exact supporting text or metadata, and passed deterministic validation.” |
| `asking_price` | string | as stated in the particulars | `direct` | §3.11 permits “Each domain activates only a small set of relevant fields, usually three to six that may help build a future folder proposal and several additional fields used only for search, privacy protection, explanation, or later review.” — a search and explanation field. This catalogue holds no figure. |
| `campaign_period` | date range | 2026-03-10 to 2026-06-02 | `direct` | When the property was on the market, which is what separates two campaigns for one flat. |
| `media_type` | string | photograph | `validated` | §3.11's Photos schema names media type. Listing photography is professionally shot, retouched and stripped of camera EXIF, which is exactly the case §2.6 warns about: “the system must not mistake the absence of EXIF for proof that an image is a screenshot” |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.3, §3.5):

- marketing language ('for sale' | 'to let' | 'guide price' | 'viewing by appointment' | 'EPC rating' where such a rating exists in the jurisdiction) co-occurring with a property address in a filename, title or page-one heading — §2.2: “A course code or university name found in a filename, title, or page-one heading is more meaningful than the same text appearing once in a reference list on page eighteen.”
- a particulars structure: an address heading, a room-by-room description and a floor plan or photograph set in one document
- an agent's listing reference co-occurring with a property address and an asking price

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- a photograph set with no particulars, where only the styling — empty rooms, wide angles, retouching — suggests marketing rather than inventory
- portal copy pasted into a document with no branding
- offer correspondence that names neither the reference nor the address

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10):

- a property address
- an agent's name — a high-frequency hub across every property they market: “when one high-frequency entity acts as the only bridge”
- the absence of camera EXIF on the images — §2.6: “the system must not mistake the absence of EXIF for proof that an image is a screenshot”, and marketing photography is routinely stripped in post-production
- a currency amount

### Work types

`sales particulars`, `letting particulars`, `marketing photograph set`, `floor plan`, `portal listing copy`, `viewing feedback`, `offer correspondence`, `energy or condition rating certificate`

### Grouping reasons (§4)

- one campaign — particulars, photographs, floor plan and portal copy produced together
- one property's campaigns across sales and lettings over years
- one property's offers and the campaign that produced them

### Template (§5)

`property → campaign → media or document type`

Time first: **no**

§5.5: “a parent dimension should provide the context required to understand the child” — a photograph set is only navigable once the campaign is known, and a campaign once the property is. Time does not lead even though a campaign is a period: “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders.”, and one property's marketing history should stay together.

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| prop.inventory-inspection | both are interior photograph sets of the same flat. Marketing photography is styled, wide-angled and usually EXIF-stripped; inventory photography is close, unstyled and geotagged. §2.6's signal hierarchy is what separates them, and it can fail | §2.6: “The system should therefore use a hierarchy of signals: camera EXIF is strong photo evidence; capture time, GPS, and sensor-shaped dimensions reinforce it; exact display resolutions, PNG format, and software metadata may support a screenshot hypothesis; conflicting signals should lead to abstention rather than an invented classification.” |
| prop.sale-purchase | the particulars are the front of a transaction whose file is the conveyancing pack; the campaign exists whether or not a sale follows | §3.9: “Topic answers what a file is about, while purpose answers what the file was for.” |
| cons.drawings-revisions | a marketing floor plan looks like a drawing and is not one: it has no title block, no revision and no discipline | §4.9: “when one high-frequency entity acts as the only bridge” |
| photo.commissioned-shoot | property photography is a commissioned shoot to the photographer and a marketing asset to the agent; the same frames sit in two files under two domains | §4.9: “A file may validly belong to more than one accepted group” |

### Sensitivity

`none` — Listing material is published deliberately and its subject is a property being advertised. None of §8.4's named categories is routine. Viewing feedback and offers name individuals and §8.4's classification, being evidence-backed and revisable, covers those per file. No handling class is set; that is P7's.

---

## `prop.mortgage-brokering` — Mortgage and property finance brokering

Arranging borrowing against property on someone's behalf — the fact find, the evidence pack, the lender submission and the offer.

**Provenance:** **inference** — extends a design-named domain or template situation; the cite supports the extension, not the whole entry

**Cite:** Extends §3.11's Finance schema “Finance files may use institution, account type, tax year, and record type.” to the adviser's side of the same transaction, where the institution is the lender and the account does not exist yet

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `client` | string | as named on the fact find | `validated` | §3.8: “The system must separate roles that happen to contain the same entity type.” — the borrower, the adviser, the lender and the conveyancer are four roles and the submission names all four. |
| `property_address` | string | Old Mill House, Bakers Lane | `validated` | The security. A mortgage case without a property is an agreement in principle and nothing more. |
| `lender` | string | as named on the offer | `validated` | §3.11 names institution as a Finance field, and §3.8 keeps it separate from the borrower: the lender is not the account holder. |
| `case_reference` | string | as issued by the lender or the adviser | `validated` | §3.5's model: a fact only “when the engine finds a course-code pattern together with academic context”, the corroborating context being mortgage-case language. Two references usually exist — the adviser's and the lender's — and they are different fields in practice. |
| `case_stage` | string | offer issued | `llm_supported` | Fact find, decision in principle, full application, valuation, offer and completion are stated in correspondence rather than in a labeled field. §3.13: “An LLM-supported fact was proposed by a language model from a bounded evidence packet, cited exact supporting text or metadata, and passed deterministic validation.” |
| `product_type` | string | as stated on the illustration | `llm_supported` | Product names and regulatory document types are jurisdiction-defined and are not enumerated here. |
| `evidence_class` | string | income evidence | `validated` | Identity, income, bank statements and deposit evidence are the pack's internal structure and are the reason this domain is sensitive throughout. |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.3, §3.5):

- mortgage-case language ('decision in principle' | 'mortgage offer' | 'loan to value' | 'affordability assessment' | 'suitability report') co-occurring with a lender name and a property address
- a lender-offer structure: a lender block, a case reference, a property address and a labeled offer expiry
- a fact-find structure: labeled client, income, expenditure and objectives sections in one document

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- a bank statement or payslip that belongs to the pack only by purpose, which is §3.9's case and is invisible in the document
- correspondence chasing a case that names neither reference
- distinguishing an illustration from an offer when both restate the same product

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10):

- a lender's name, which appears as lender, as an existing account provider on a statement and as a merely cited institution
- a property address
- a currency amount or a percentage
- a client name — §3.8: “A folder should not become a collection point for everything produced by the same person or organization.”

### Work types

`fact find`, `decision in principle`, `suitability report`, `identity evidence`, `income evidence`, `lender submission`, `mortgage offer`, `completion correspondence`

### Grouping reasons (§4)

- one case from fact find to completion, as a purpose-coherent pack
- one client's cases across remortgages over years
- the evidence pack assembled for one lender submission

### Template (§5)

`client → case → evidence class`

Time first: **no**

§5.5: “a parent dimension should provide the context required to understand the child” — income evidence is meaningless outside the case it supports. Client leads here, unusually for this slice, because the adviser's duty and file run to the person rather than to the property; §3.8's warning against a person as a collector is about authorship, not about a client whose file this genuinely is. §3.9 is why evidence class sits last: “The documents are content-incoherent but purpose-coherent.”. Time does not lead: “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders.”

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| prop.sale-purchase | the mortgage offer sits in both files. The broker's file is about the borrower; the conveyancing file is about the property. The offer is genuinely both and §3.11 keeps both fact sets | §3.11: “One file may hold facts from more than one domain without losing information.” |
| fin.bank-account | THE BOUNDARY. A bank statement submitted as income evidence is still a bank statement; the pack's claim on it comes from purpose, not from content — which is the finance slice's own stated position on the same file | §3.9: “The documents are content-incoherent but purpose-coherent.” |
| prop.survey-valuation | the lender's valuation is commissioned inside the case and is also the property's record | §4.9: “A file may validly belong to more than one accepted group” |

### Sensitivity

`potentially_sensitive` — §2.9's phrase “while treating addresses and message content as potentially sensitive” only. The pack is built from identity documents, bank statements and income evidence — §8.4 names “identity documents, account statements, tax records, medical information, legal records, credentials, private correspondence, GPS metadata, employment materials, and educational records” almost item for item — and §3.15's direction governs: “Finance, identity, medical, and legal material should be implemented first as safety domains, meaning the system detects and protects them before any cloud or automated placement decision is allowed.” §8.4 requires privacy policy to be enforced before content reaches any model, so the two fields whose ceiling is llm_supported will frequently resolve to unknown rather than to a weaker value. The handling class is P7's and is not set here.

---

## `retail.product-catalogue` — Product catalogue and merchandising

What is sold and how it is presented — product records, photography, copy, price lists and the range plan behind them.

**Provenance:** **proposal** — new — the design does not name this domain, and nothing here is asserted as the design's

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `product_identifier` | string | SKU-88014 | `validated` | §3.5's model applied to the densest code space in this slice: a SKU is a fact only “when the engine finds a course-code pattern together with academic context”, the corroborating context being catalogue language. SKUs, barcodes and supplier codes share a shape and belong to different owners. |
| `product_name` | string | Harbour Wool Throw, slate | `validated` | The human-readable identity, and the only field that survives a supplier changing its coding. |
| `range_or_collection` | string | Autumn 2026 Home | `validated` | The commercial grouping a product was bought and merchandised in. It is the folder level a buyer actually thinks in. |
| `category` | string | home textiles | `validated` | The taxonomy position, which is stable across seasons where the range is not. |
| `catalogue_version` | string | as labeled on the file | `validated` | Catalogues and price lists are reissued constantly; the version is a family, not a level. |
| `copy_or_description` | string | as written in the product record | `llm_supported` | Marketing copy is prose and must be read to be matched to a product. §3.5: “It can only propose facts that belong to the active domain schema, and it must cite exact supporting evidence already extracted from the file.” |
| `media_type` | string | product photograph | `validated` | §3.11's Photos schema names media type. Product photography is studio work, retouched and EXIF-stripped, so §2.6's warning is directly in play: “the system must not mistake the absence of EXIF for proof that an image is a screenshot” |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.3, §3.5):

- a product-identifier pattern co-occurring with catalogue context — 'SKU' | 'product code' | 'RRP' | 'barcode' | 'pack size' | 'colourway' — never the code alone
- a spreadsheet whose column headers include a product identifier and a price, co-occurring with a range or season name — §2.9: “Spreadsheets such as XLSX, XLS, CSV, TSV, ODS, and Numbers exports should yield workbook or file metadata, sheet names, column headers, visible cell values, table-like regions, formulas only when useful, and dates or identifiers from labeled cells.”
- an image whose filename carries a product identifier that also appears in a catalogue file in the same folder, which links media to record deterministically

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- a studio image with no identifier in its filename, where only the content identifies the product
- copy written for a product with no code anywhere in the document
- distinguishing a range plan from a stock report when both list the same products

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10):

- a bare SKU or barcode — the same digit strings appear in stock takes, orders, invoices, returns and supplier price lists, owned by different parties
- a product name, which recurs across seasons and across competitors
- a currency amount
- the absence of EXIF on an image — §2.6: “the system must not mistake the absence of EXIF for proof that an image is a screenshot”

### Work types

`product record`, `catalogue`, `price list`, `range plan`, `product photograph`, `product copy`, `planogram`, `packaging artwork`

### Grouping reasons (§4)

- one product across its record, photography, copy and packaging
- one range or season as a commercial set
- one catalogue across its versions, as a version family

### Template (§5)

`range or season → category → product`

Time first: **no**

§5.5: “a parent dimension should provide the context required to understand the child” — a product photograph is only findable once the range and category narrow the search, and a SKU is not something a person remembers. Season leads because a range is bought, merchandised and cleared as a unit, and it is a commercial cycle rather than a calendar one, so “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders.” is respected: the leading dimension is a named range, not a year.

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| retail.stocktake | the catalogue says what a product is; a stock take says how many exist in one place on one date. Both are SKU-keyed spreadsheets and only the presence of a location and a count date separates them | §4.9: “when one high-frequency entity acts as the only bridge” |
| retail.supplier-order | a supplier price list and an internal catalogue list the same products under different codes and different owners. §3.8's role separation is the whole answer: the supplier code and the retailer's SKU are different fields | §3.8: “The system must separate roles that happen to contain the same entity type.” |
| retail.ecommerce-ops | the storefront's product data is a copy of the catalogue with channel-specific fields. The separating signal is a channel or store identifier | §3.11: “One file may hold facts from more than one domain without losing information.” |

### Sensitivity

`none` — Catalogue material concerns products. None of §8.4's named categories is routine. No handling class is set here; that is P7's.

---

## `retail.stocktake` — Inventory and stock takes

How much of what is where, counted on a date — and the variance between the count and what the system believed.

**Provenance:** **proposal** — new — the design does not name this domain, and nothing here is asserted as the design's

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `location` | string | Store 07, Harbourside | `validated` | Where the stock was counted. A count without a location is not a count, and it is the dimension that keeps two stores' figures apart. |
| `count_date` | date | 2026-09-30 | `direct` | §3.13: “A direct fact was read from a reliable and explicit source, such as a content hash, EXIF timestamp, document title, or labeled form field.” A stock take is a statement about a moment; the date is the record's identity. §3.10's explicit-regex path only: “The product must not use fuzzy date parsing because file names and documents frequently contain numbers that look like years but are course identifiers, version numbers, build numbers, ZIP codes, or other unrelated values.” |
| `count_type` | string | full count | `validated` | Full count, cycle count, perpetual count and spot check differ in scope and in what a variance means. |
| `product_identifier` | string | SKU-88014 | `validated` | §3.5's model: a fact only “when the engine finds a course-code pattern together with academic context”, the corroborating context being count language. |
| `variance` | string | as tabulated in the report | `direct` | §2.3: “Tables matter because resumes, forms, applications, invoices, and administrative documents often place their most useful information in cells rather than body paragraphs.” and §2.9: “Spreadsheets such as XLSX, XLS, CSV, TSV, ODS, and Numbers exports should yield workbook or file metadata, sheet names, column headers, visible cell values, table-like regions, formulas only when useful, and dates or identifiers from labeled cells.” — the variance is the report's whole point and lives in cells. This catalogue holds no figure. |
| `counted_by` | string | as recorded on the sheet | `direct` | Recorded because a count is attested. §3.8: “It should avoid using authorship or creator identity as a destination dimension.” |
| `count_scope` | string | back-of-house only | `llm_supported` | Scope qualifications are written as notes and change how a variance should be read. |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.3, §3.5):

- count language ('stock take' | 'stocktake' | 'cycle count' | 'inventory count' | 'variance report' | 'shrinkage') co-occurring with a location name and a labeled count date
- a spreadsheet whose column headers pair a product identifier with a counted quantity and a system quantity — §2.9: “Spreadsheets such as XLSX, XLS, CSV, TSV, ODS, and Numbers exports should yield workbook or file metadata, sheet names, column headers, visible cell values, table-like regions, formulas only when useful, and dates or identifiers from labeled cells.”
- a labeled count-date and location pair co-occurring with a product-identifier column

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- a photographed count sheet whose location is written by hand at the top
- an unlabeled spreadsheet whose purpose must be read from its columns
- distinguishing a count from a stock-on-hand report exported the same day

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10):

- a SKU column, which is shared with catalogue, ordering, POS and returns files
- a quantity column, the most generic numeric column in this slice
- a date — §3.10: “The product must not use fuzzy date parsing because file names and documents frequently contain numbers that look like years but are course identifiers, version numbers, build numbers, ZIP codes, or other unrelated values.”
- a location name, which appears in every operational file the store produces

### Work types

`count sheet`, `variance report`, `stock-on-hand report`, `cycle count record`, `write-off record`, `shrinkage analysis`

### Grouping reasons (§4)

- one count event at one location — sheets, report and write-offs together
- one location's counts across a year, as a series
- one variance investigation across the files that evidence it

### Template (§5)

`location → count date → document type`

Time first: **no**

§5.5: “a parent dimension should provide the context required to understand the child” — a variance report is meaningless without the location and the location's counts are only distinguishable by date. Time therefore sits second, not first: this is not capture-based media, and “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders.” means one location's count history stays together rather than being cut across year folders. A single-site retailer collapses the location level, which §5.8 expects: “The canvas must support uneven depth because real file trees are not and should not be perfectly symmetrical.”

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| retail.product-catalogue | both are SKU-keyed spreadsheets. The separating signal is a location and a count date, which a catalogue never carries | §4.9: “when one high-frequency entity acts as the only bridge” |
| log.warehouse-ops | a warehouse count and a store count are the same document type at different nodes; the separating signal is whether the location is a selling location | §3.9: “Topic answers what a file is about, while purpose answers what the file was for.” |
| hosp.menu-recipe-costing | a kitchen stock take counts ingredients against recipes rather than products against a catalogue; the identifier space is different and the two must not merge | §4.8: “that each fact or label belongs to an allowed domain schema” |

### Sensitivity

`none` — Counts concern goods. None of §8.4's named categories is routine. Shrinkage investigations can name individuals and §8.4's evidence-backed, revisable classification covers those per file. No handling class is set; that is P7's.

---

## `retail.supplier-order` — Supplier and wholesale ordering

Buying stock to sell — purchase orders, confirmations, allocations and the goods-in paperwork that closes them.

**Provenance:** **inference** — extends a design-named domain or template situation; the cite supports the extension, not the whole entry

**Cite:** Extends §3.11's Finance schema “Finance files may use institution, account type, tax year, and record type.” into its pre-accounting form, and extends §7.3's “Receipts and Confirmations may hold isolated invoices, delivery confirmations, booking records, boarding passes, purchase receipts, event tickets, and similar transactional documents.” which names delivery confirmations as a recognised record type

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `supplier` | string | Harbour Mills Ltd | `validated` | §3.8: “The system must separate roles that happen to contain the same entity type.” — supplier, buying group, carrier and the retailer's own delivery location are four roles on one order. |
| `order_reference` | string | PO-77120 | `validated` | §3.5's model: a fact only “when the engine finds a course-code pattern together with academic context”, the corroborating context being ordering language. The supplier's own order number is a different field and both appear on the confirmation. |
| `delivery_location` | string | Central DC, bay 3 | `validated` | Where the goods were to go, which is what makes an order reconcilable against a receipt. |
| `order_date` | date | 2026-07-14 | `direct` | §3.13: “A direct fact was read from a reliable and explicit source, such as a content hash, EXIF timestamp, document title, or labeled form field.” §3.10's explicit-regex path only. |
| `delivery_window` | date range | 2026-08-03 to 2026-08-10 | `direct` | A labeled field, and the field every chase email is about. |
| `line_items` | string | as tabulated on the order | `direct` | §2.3: “Tables matter because resumes, forms, applications, invoices, and administrative documents often place their most useful information in cells rather than body paragraphs.” — the order's substance is its table. This catalogue holds no quantity. |
| `order_status` | string | part delivered | `llm_supported` | Stated in correspondence. §3.13: “An LLM-supported fact was proposed by a language model from a bounded evidence packet, cited exact supporting text or metadata, and passed deterministic validation.” |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.3, §3.5):

- ordering language ('purchase order' | 'order confirmation' | 'goods received' | 'advice note' | 'backorder') co-occurring with a supplier name and a line-item table
- an order-reference pattern co-occurring with a labeled delivery location or delivery window
- an order reference appearing in two files that share a supplier — the order and its confirmation — which builds the chain deterministically

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- an emailed order with the lines in the body and no attachment
- a supplier's proforma that must be distinguished from an invoice
- a photographed goods-in sheet annotated by hand

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10):

- a bare order reference
- a supplier name — §4.9's warning transfers: “A university name alone should not create a group because Columbia can appear as an authoring school, course provider, target institution, employer, research venue, or merely a cited organization.”
- a line-item table, shared with quotes, invoices, catalogues, stock takes and delivery notes
- a SKU column

### Work types

`purchase order`, `order confirmation`, `delivery note`, `goods received note`, `backorder report`, `allocation sheet`, `supplier price list`

### Grouping reasons (§4)

- one order from purchase order to goods received
- one supplier's orders in one buying season
- one delivery reconciled across order, note and claim

### Template (§5)

`supplier → season or period → order`

Time first: **no**

§5.5: “a parent dimension should provide the context required to understand the child” — an order reference is only unique inside a supplier and only findable once the buying period narrows it. Supplier leads rather than season because a chase, a dispute or a rebate conversation is always about one supplier. “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders.” keeps the period second and names it as a buying season rather than a calendar year where one exists.

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| biz.invoice-received | THE BOUNDARY. The order commits to buy, the delivery note proves arrival, the invoice claims payment. All three carry the supplier, the lines and often the same reference, and only the invoice carries a sequence number, a tax point and payment terms | §3.11: “One file may hold facts from more than one domain without losing information.” |
| cons.materials-delivery | the same documents for a different consuming domain: stock for resale versus materials for works. The separating signal is whether the destination is a selling location or a site | §3.9: “Topic answers what a file is about, while purpose answers what the file was for.” |
| log.shipment | the carrier's consignment note travels with the supplier's delivery note and names the same goods; they belong to different parties and different domains | §3.8: “The system must separate roles that happen to contain the same entity type.” |

### Sensitivity

`none` — Ordering records concern goods and companies. None of §8.4's named categories is routine. No handling class is set here; that is P7's.

---

## `retail.pos-reporting` — Point-of-sale and trading reporting

What a shop sold and took, cut by day, by till and by department — the operational read of a trading period.

**Provenance:** **proposal** — new — the design does not name this domain, and nothing here is asserted as the design's

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `location` | string | Store 07, Harbourside | `validated` | The trading location. Reports are produced per location and merging two is a straightforward corruption of the numbers. |
| `business_date` | date | 2026-09-12 | `direct` | §3.13: “A direct fact was read from a reliable and explicit source, such as a content hash, EXIF timestamp, document title, or labeled form field.” — a labeled field, and deliberately distinct from a calendar date because a trading day can cross midnight. §3.10's explicit-regex path only: “The product must not use fuzzy date parsing because file names and documents frequently contain numbers that look like years but are course identifiers, version numbers, build numbers, ZIP codes, or other unrelated values.” |
| `report_type` | string | end-of-day summary | `validated` | End-of-day summary, department sales, hourly trade, discount and void report, and cash-up are different reports with different uses. |
| `till_or_terminal` | string | as labeled in the report | `direct` | The device the figures came from, which is what makes a discrepancy investigable. |
| `trading_period` | string | week 37 | `validated` | Retail periods are the trading calendar's own — weeks and periods rather than months — which is why this is a domain field. |
| `takings_summary` | string | as tabulated in the report | `direct` | §2.9: “Spreadsheets such as XLSX, XLS, CSV, TSV, ODS, and Numbers exports should yield workbook or file metadata, sheet names, column headers, visible cell values, table-like regions, formulas only when useful, and dates or identifiers from labeled cells.” — the substance lives in cells. This catalogue holds no figure. |
| `exception_note` | string | as written on the cash-up | `llm_supported` | Explanations for a discrepancy are handwritten or emailed prose. |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.3, §3.5):

- POS-report language ('end of day' | 'Z read' | 'cash up' | 'takings' | 'department sales' | 'voids and refunds') co-occurring with a location or till identifier
- a labeled business-date and location pair co-occurring with a takings or department table — §2.3: “Tables matter because resumes, forms, applications, invoices, and administrative documents often place their most useful information in cells rather than body paragraphs.”
- a run of daily exports sharing a filename pattern and a location, which supports the series but not the domain on its own

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- a photographed till roll whose OCR is partial
- an export with generic column headers whose report type must be read from its structure
- a cash-up discrepancy explained in an email that must be linked to the day it concerns

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10):

- a currency amount
- a date in a filename — §3.10: “The product must not use fuzzy date parsing because file names and documents frequently contain numbers that look like years but are course identifiers, version numbers, build numbers, ZIP codes, or other unrelated values.”
- a run of daily files, which is a session-shaped clue only — §3.9: “A session should never be treated as proof of topic, and it should not carry the same confidence as a hash match or a directly extracted document fact.”
- a location name, shared with every operational file the store produces

### Work types

`end-of-day summary`, `cash-up sheet`, `department sales report`, `hourly trade report`, `voids and refunds report`, `banking record`, `period trading summary`

### Grouping reasons (§4)

- one trading day at one location across its reports
- one trading period or week at one location
- one discrepancy and the reports that evidence it

### Template (§5)

`location → trading period → report type`

Time first: **no**

NOT time-first, and the reason matters because the domain is a daily series. §5.5's exception is granted to capture-based media and these are generated reports, not captures: “Photos and capture-based media are the major exception: time often belongs first because capture date is a defining aspect of the material.” does not reach them. §5.5's “a parent dimension should provide the context required to understand the child” puts location above period because two stores' figures must never merge, and the period is named in the trading calendar rather than the calendar year. A single-site retailer collapses the location level — §5.8: “The canvas must support uneven depth because real file trees are not and should not be perfectly symmetrical.”

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| fin.financial-records | THE BOUNDARY. A Z read is an operational report; the banking entry and the period's revenue posting are accounting records. The Z read exists for the manager on the day and is never itself a ledger entry | §3.9: “Topic answers what a file is about, while purpose answers what the file was for.” |
| retail.store-ops | trading reports and operational records are produced by the same people on the same day at the same location, which makes location plus date a shared bridge and a weak one — §4.9: “when one high-frequency entity acts as the only bridge” | §4.9: “A semantic embedding alone is insufficient.” |
| hosp.bookings | a restaurant's covers report and its till report describe the same evening from different systems; the separating signal is whether the record is of a reservation or of a transaction | §3.9: “Topic answers what a file is about, while purpose answers what the file was for.” |

### Sensitivity

`none` — Trading reports are aggregate figures about a location. Card data on a Z read is truncated by design, and none of §8.4's named categories is routine. Where a voids report is used in an investigation of a named person, §8.4's classification is evidence-backed and revisable per file. No handling class is set; that is P7's.

---

## `retail.ecommerce-ops` — E-commerce operations

Running a storefront — channel listings, order and customer exports, fulfilment records, platform settings and the marketing data behind them.

**Provenance:** **proposal** — new — the design does not name this domain, and nothing here is asserted as the design's

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `channel` | string | own storefront | `validated` | Own site, marketplace and social channels have different data shapes, different identifiers and different obligations, and the channel is the field that keeps them apart. |
| `store_or_account` | string | as named in the export | `validated` | §3.8: “The system must separate roles that happen to contain the same entity type.” — the merchant, the platform, the payment processor and the fulfilment provider are four organisations that all appear in one export's headers. |
| `export_type` | string | orders export | `validated` | Orders, customers, products, payouts and traffic exports are different objects with different sensitivities, and the type decides how the file must be treated. |
| `export_period` | date range | 2026-08-01 to 2026-08-31 | `direct` | §3.13: “A direct fact was read from a reliable and explicit source, such as a content hash, EXIF timestamp, document title, or labeled form field.” Exports are period-scoped and reconciled against a period, which is what makes the range a schema field. |
| `product_identifier` | string | SKU-88014 | `validated` | The join back to the catalogue. §3.5's model: a fact only “when the engine finds a course-code pattern together with academic context”. |
| `platform_artifact` | string | theme template | `validated` | Themes, templates, redirect maps and settings exports are technical artefacts that live in the same folders as the data and must not be treated as data. |
| `campaign` | string | as named in the export | `llm_supported` | Campaign naming is free text set by whoever built it and must be interpreted rather than matched. |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.3, §3.5):

- an export structure whose column headers include an order identifier together with a customer or shipping-address column — §2.9: “Spreadsheets such as XLSX, XLS, CSV, TSV, ODS, and Numbers exports should yield workbook or file metadata, sheet names, column headers, visible cell values, table-like regions, formulas only when useful, and dates or identifiers from labeled cells.”
- channel language ('order number' | 'fulfilment status' | 'payout' | 'refund' | 'basket' | 'checkout') co-occurring with a store or account name
- a platform artefact recognised by its own structure — a theme or template file inside a storefront export bundle — which §1.5 already keeps out of the proposal engine when it sits under a project root

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- a generic CSV whose export type must be read from its columns
- distinguishing a marketing traffic export from an orders export when both are keyed on a date
- a screenshot of a platform admin screen, which §2.7 is the only route into: “A screenshot is always a screenshot of something”

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10):

- an order-number pattern, which collides with invoice, consignment and case references
- a SKU column
- a date range
- a platform name, which appears as the channel, as a payment processor and as a merely cited service

### Work types

`orders export`, `customers export`, `payouts export`, `product feed`, `fulfilment record`, `returns export`, `theme or template file`, `traffic and campaign report`

### Grouping reasons (§4)

- one channel's exports for one period, reconciled together
- one campaign across its brief, creative and performance export
- one storefront's technical artefacts as a project-shaped set

### Template (§5)

`channel → export type → period`

Time first: **no**

§5.5: “a parent dimension should provide the context required to understand the child” — an orders export is meaningless without the channel that produced it, and periods only sort within a type. Period sits last: “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders.”. This domain touches the software slice's territory at the technical-artefact level, where §1.5's exclusion rules already apply before any of this does.

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| retail.product-catalogue | the product feed is a channel copy of the catalogue. The separating signal is a channel identifier and channel-specific fields | §3.11: “One file may hold facts from more than one domain without losing information.” |
| retail.returns-warranty | a returns export is an e-commerce artefact and a returns record. The separating signal is whether the file is a bulk export or a single case | §3.9: “Topic answers what a file is about, while purpose answers what the file was for.” |
| soft.source-project | a storefront theme is code and belongs to the software slice's rules, not to a retail folder template. §1.5's project-root exclusions decide it before this catalogue does | §1.5: “It should also reject descendants of software project roots indicated by files such as package.json, requirements.txt, Cargo.toml, or go.mod.” |

### Sensitivity

`potentially_sensitive` — §2.9's phrase “while treating addresses and message content as potentially sensitive” only. Orders and customers exports are bulk personal data — names, addresses, contact details — and platform settings exports frequently contain API keys and tokens. §8.4 names credentials and private correspondence in “identity documents, account statements, tax records, medical information, legal records, credentials, private correspondence, GPS metadata, employment materials, and educational records” and requires privacy policy to be enforced before content reaches any model, which matters most here because a single file can hold thousands of people's details. The handling class is P7's and is not set.

---

## `retail.returns-warranty` — Returns, refunds and warranty claims

A single item coming back — why, from whom, under what right, and what was done about it.

**Provenance:** **proposal** — new — the design does not name this domain, and nothing here is asserted as the design's

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `case_reference` | string | as issued by the retailer or manufacturer | `validated` | §3.5's model: a fact only “when the engine finds a course-code pattern together with academic context”, the corroborating context being returns language. |
| `original_order_reference` | string | as printed on the receipt or order | `validated` | §3.8: “The system must separate roles that happen to contain the same entity type.” — the order reference, the return reference and the manufacturer's claim reference are three different numbers for one event, and conflating them loses the chain. |
| `product_identifier` | string | SKU-88014 | `validated` | What came back, which is what links the case to the catalogue and to any pattern of failures. |
| `return_reason` | string | faulty on arrival | `llm_supported` | Reasons are free text or a code whose meaning is local, and the distinction between a fault, a change of mind and a mis-pick decides the outcome. §3.13: “An LLM-supported fact was proposed by a language model from a bounded evidence packet, cited exact supporting text or metadata, and passed deterministic validation.” |
| `claim_route` | string | manufacturer warranty | `validated` | Retailer goodwill, statutory right, manufacturer warranty and extended cover are different routes with different evidence, and the route is what makes the file legible later. |
| `case_date` | date | 2026-09-18 | `direct` | §3.13: “A direct fact was read from a reliable and explicit source, such as a content hash, EXIF timestamp, document title, or labeled form field.” §3.10's explicit-regex path only. |
| `resolution` | string | replaced | `validated` | Refunded, replaced, repaired, rejected — a labeled outcome field on almost every returns form. |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.3, §3.5):

- returns language ('return authorisation' | 'RMA' | 'refund' | 'warranty claim' | 'faulty' | 'proof of purchase') co-occurring with a product identifier or an order reference
- a case-reference pattern co-occurring with a labeled resolution field
- a receipt or order document co-occurring in the same folder with a case reference that names it, which links the claim to its purchase deterministically

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- an email complaint that is the claim, with no form and no reference
- a photograph of a fault, where §2.7 is the only route in: “A screenshot is always a screenshot of something”
- distinguishing a warranty claim from a service request when both describe a fault

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10):

- a case or order reference
- a SKU
- the word 'refund', which appears in POS reports, e-commerce exports, bank statements and correspondence
- a receipt image — §7.3's residual template exists precisely because an isolated receipt is often unattachable: “Receipts and Confirmations may hold isolated invoices, delivery confirmations, booking records, boarding passes, purchase receipts, event tickets, and similar transactional documents.”

### Work types

`return authorisation`, `returns form`, `warranty claim`, `proof of purchase`, `fault photograph`, `credit note`, `resolution correspondence`

### Grouping reasons (§4)

- one case from complaint to resolution
- one product's failures across cases, which is what reveals a systemic fault
- one supplier's warranty claims in a period

### Template (§5)

`claim route → case → document type`

Time first: **no**

§5.5: “a parent dimension should provide the context required to understand the child” — the route decides what evidence a case needs, so it is the level that makes a case folder legible. A per-case folder is only worth creating where a case has several documents; a one-document case belongs in the parent, which is §5.9's warning applied: “It should warn when a level produces only one child, repeats a concept already expressed in the parent, creates excessive depth, or creates a large number of tiny folders.”. Time does not lead: “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders.”

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| fin.receipts-expenses | THE BOUNDARY, from the consumer side. A receipt held as proof of purchase for a claim is the same file the finance slice holds as an expense record. §3.9 covers it: the claim pack is purpose-coherent while its members are not | §3.9: “The documents are content-incoherent but purpose-coherent.” |
| retail.ecommerce-ops | a bulk returns export is an operations artefact; a single case is a record. The separating signal is whether the file describes one event or many | §3.9: “Topic answers what a file is about, while purpose answers what the file was for.” |
| trade.compliance-certificate | a warranty on installed work is claimed against the installer, not the retailer, and the certificate is the evidence. The two domains meet on the same appliance | §4.9: “A file may validly belong to more than one accepted group” |

### Sensitivity

`potentially_sensitive` — §2.9's phrase “while treating addresses and message content as potentially sensitive” only. A returns case names a customer, their address and their purchase, and the correspondence is private correspondence — §8.4 names that category in “identity documents, account statements, tax records, medical information, legal records, credentials, private correspondence, GPS metadata, employment materials, and educational records”. The handling class is P7's and is not set here.

---

## `retail.store-ops` — Store and site operations

Running a shop day to day — rotas, opening and closing checks, standards audits, maintenance and the compliance paperwork the site must hold.

**Provenance:** **proposal** — new — the design does not name this domain, and nothing here is asserted as the design's

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `location` | string | Store 07, Harbourside | `validated` | The operating site. Everything in this domain is per-site and merging two sites' records destroys their value. |
| `record_class` | string | standards audit | `validated` | Rota, checklist, audit, maintenance record and compliance certificate have different lifecycles and different sensitivities, and this is the field that separates them. |
| `period` | string | week 37 | `validated` | Operational records batch by week or by trading period rather than by month, which is why the period is a domain field. |
| `responsible_person` | string | as recorded on the record | `direct` | Recorded because the record is attested, not because it is a folder dimension. §3.8: “It should avoid using authorship or creator identity as a destination dimension.” |
| `audit_outcome` | string | as recorded on the audit | `validated` | A labeled result field, and the field that makes an audit worth retrieving later. |
| `maintenance_asset` | string | chiller 2 | `validated` | What was maintained, which is what links a service record to a failure and to a warranty. |
| `action_required` | string | as written in the follow-up | `llm_supported` | Follow-up actions are prose. §3.5: “It can only propose facts that belong to the active domain schema, and it must cite exact supporting evidence already extracted from the file.” |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.3, §3.5):

- operations language ('opening checks' | 'closing checks' | 'rota' | 'store standards' | 'planned maintenance' | 'callout') co-occurring with a location name
- a rota structure: a labeled week together with named staff and shift times in a table — §2.3: “Tables matter because resumes, forms, applications, invoices, and administrative documents often place their most useful information in cells rather than body paragraphs.”
- an audit structure: labeled sections with scored or pass-fail outcomes, co-occurring with a location and a date

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- a photographed paper checklist signed by hand
- an email instructing an action that functions as the operational record
- distinguishing a rota from a timesheet, which use the same names and the same week

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10):

- a location name — the highest-frequency bridge in this domain: “when one high-frequency entity acts as the only bridge”
- a week number or a date
- a person's name — §3.8: “A folder should not become a collection point for everything produced by the same person or organization.”
- a checklist structure, which appears identically in food safety, health and safety, and site inductions

### Work types

`rota`, `opening and closing checklist`, `standards audit`, `maintenance record`, `callout report`, `compliance certificate`, `operational bulletin`

### Grouping reasons (§4)

- one location's records for one period
- one asset's maintenance history across callouts
- one audit and the actions closing it

### Template (§5)

`location → record class → period`

Time first: **no**

§5.5: “a parent dimension should provide the context required to understand the child” — a checklist is meaningless without the site and periods only sort within a class. Location leads because that is the only question anyone asks of this material. Period sits last: “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders.”. §3.8 is why the person is not a level: “A folder should not become a collection point for everything produced by the same person or organization.”

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| trade.timesheet | a rota is a plan and a timesheet is a record of what happened. They share names, weeks and often one spreadsheet, and only the tense separates them | §4.9: “A semantic embedding alone is insufficient.” |
| hosp.food-safety | food-safety checks are operational records with a statutory character and their own retention discipline. The separating signal is a temperature, a probe reading or a named safety procedure | §3.9: “Topic answers what a file is about, while purpose answers what the file was for.” |
| retail.pos-reporting | produced by the same people at the same site on the same day, which makes location plus date a shared and weak bridge | §4.9: “when one high-frequency entity acts as the only bridge” |
| ops.facilities-workplace | the business-operations slice owns facilities and workplace safety as corporate functions across sites; this domain owns them as the daily record of one trading location. The separating signal is whether the document is a policy or a completed check | §3.9: “Topic answers what a file is about, while purpose answers what the file was for.” |

### Sensitivity

`potentially_sensitive` — §2.9's phrase “while treating addresses and message content as potentially sensitive” only. Rotas and staffing records are employment materials naming individuals, and §8.4 names employment materials in “identity documents, account statements, tax records, medical information, legal records, credentials, private correspondence, GPS metadata, employment materials, and educational records”. The maintenance and audit half of the domain is not sensitive; §8.4's classification is evidence-backed and revisable, which is what lets both live here. No handling class is set; that is P7's.

---

## `hosp.menu-recipe-costing` — Menu development and recipe costing

What is on the menu, what goes into it, what it costs to make and what it sells for — plus the allergen information the dish carries.

**Provenance:** **proposal** — new — the design does not name this domain, and nothing here is asserted as the design's

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `menu` | string | Autumn dinner menu | `validated` | The menu a dish appears on. Dishes move between menus and the same dish is costed differently on each. |
| `dish` | string | braised shoulder, root mash | `validated` | The costed unit. It is the field that joins a recipe, a cost sheet, a photograph and an allergen record. |
| `menu_version` | string | as labeled on the file | `validated` | Menus are reprinted constantly; the version is a family rather than a level, and printing an out-of-date allergen sheet is the failure this field prevents. |
| `ingredient` | string | as listed in the recipe | `validated` | The recipe's components, which is what links a dish to a supplier price change. |
| `allergen_information` | string | as recorded on the dish specification | `validated` | A labeled field on a dish specification and the field that makes this domain safety-critical rather than merely commercial. Allergen labelling regimes are jurisdiction-defined and none is named here. |
| `cost_and_margin` | string | as calculated in the cost sheet | `direct` | §2.9: “Spreadsheets such as XLSX, XLS, CSV, TSV, ODS, and Numbers exports should yield workbook or file metadata, sheet names, column headers, visible cell values, table-like regions, formulas only when useful, and dates or identifiers from labeled cells.” — costings live in cells. This catalogue holds no figure. |
| `dish_description` | string | as written for the menu | `llm_supported` | Menu copy is prose written to sell, not to describe. §3.5: “It can only propose facts that belong to the active domain schema, and it must cite exact supporting evidence already extracted from the file.” |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.3, §3.5):

- recipe-costing language ('portion cost' | 'gross profit' | 'yield' | 'recipe card' | 'dish specification' | 'allergen') co-occurring with a dish or menu name
- a spreadsheet whose column headers pair an ingredient with a quantity and a cost, co-occurring with a dish name — §2.9: “Spreadsheets such as XLSX, XLS, CSV, TSV, ODS, and Numbers exports should yield workbook or file metadata, sheet names, column headers, visible cell values, table-like regions, formulas only when useful, and dates or identifiers from labeled cells.”
- a dish-specification structure: a dish name together with a labeled allergen section and a method

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- a menu PDF designed for print, where dishes must be read out of a layout
- a recipe written as prose in a document with no structure
- distinguishing a costed recipe from a purchasing list of the same ingredients

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10):

- an ingredient name, which appears in recipes, orders, stock takes and delivery notes
- a currency amount or a percentage
- a dish name, which recurs across seasons and across venues
- the word 'menu', which is also a software menu — §3.7: “It should use word-boundary matching rather than substring matching.”

### Work types

`menu`, `recipe card`, `dish specification`, `costing sheet`, `allergen matrix`, `dish photograph`, `supplier substitution note`

### Grouping reasons (§4)

- one menu across its dishes, costings and allergen matrix
- one dish across menus and versions
- one costing round triggered by a supplier price change

### Template (§5)

`venue → menu → document type`

Time first: **no**

§5.5: “a parent dimension should provide the context required to understand the child” — a costing sheet is meaningless without the dish's menu and the menu without the venue. Venue leads because a group operates several and their menus differ; a single-site operator collapses it, which §5.8 expects: “The canvas must support uneven depth because real file trees are not and should not be perfectly symmetrical.”. Time does not lead: menus are named seasons rather than dates, and “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders.” applies.

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| retail.stocktake | a kitchen stock take counts ingredients while a retail count counts saleable products; the identifier spaces are different and merging them corrupts both | §4.8: “that each fact or label belongs to an allowed domain schema” |
| hosp.food-safety | the allergen matrix is a commercial document and a safety record. It genuinely doubles and §3.11 keeps both fact sets rather than forcing a choice | §3.11: “One file may hold facts from more than one domain without losing information.” |
| hosp.catering-contract | a function menu is written for one contract and reuses dishes from the standing menu; the separating signal is a client and an event date | §3.9: “Topic answers what a file is about, while purpose answers what the file was for.” |

### Sensitivity

`none` — Menu and costing material concerns dishes and prices. None of §8.4's named categories is routine. Allergen information about a named guest is a different object and lives in the bookings and catering domains, where it is marked. No handling class is set here; that is P7's.

---

## `hosp.food-safety` — Food safety and hygiene records

The daily evidence that food was handled safely — temperature logs, cleaning schedules, delivery checks, traceability and the incident record when something failed.

**Provenance:** **proposal** — new — the design does not name this domain, and nothing here is asserted as the design's

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `site` | string | Harbourside kitchen | `validated` | The premises. Food-safety records are held per premises and are produced to an inspector per premises. |
| `record_class` | string | temperature log | `validated` | Temperature log, cleaning schedule, delivery check, traceability record, training record and incident report are distinct obligations with distinct retention and distinct sensitivity. |
| `record_period` | string | September 2026 | `validated` | Daily records are kept and produced as a month or a period, which is the unit an inspection asks for. |
| `check_date` | date | 2026-09-12 | `direct` | §3.13: “A direct fact was read from a reliable and explicit source, such as a content hash, EXIF timestamp, document title, or labeled form field.” Every entry is a statement about a moment and the date is the record. §3.10's explicit-regex path only: “The product must not use fuzzy date parsing because file names and documents frequently contain numbers that look like years but are course identifiers, version numbers, build numbers, ZIP codes, or other unrelated values.” |
| `corrective_action` | string | as written on the log | `llm_supported` | The entry that matters most is the one recording what was done when a check failed, and it is always handwritten prose. §3.13: “An LLM-supported fact was proposed by a language model from a bounded evidence packet, cited exact supporting text or metadata, and passed deterministic validation.” |
| `responsible_person` | string | as signed on the record | `direct` | Recorded because the log is attested. §3.8: “It should avoid using authorship or creator identity as a destination dimension.” |
| `traceability_reference` | string | as recorded on the delivery check | `validated` | Batch and supplier references recorded at goods-in, which is what makes a recall actionable and is the field that links this domain to ordering. |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.3, §3.5):

- food-safety language ('temperature log' | 'probe check' | 'cleaning schedule' | 'hazard analysis' | 'critical control point' | 'corrective action') co-occurring with a site name
- a log structure: a labeled date column, a reading column and a signature column in one table — §2.3: “Tables matter because resumes, forms, applications, invoices, and administrative documents often place their most useful information in cells rather than body paragraphs.”
- a delivery-check structure pairing a supplier name, a temperature reading and a labeled accept-or-reject outcome

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- a photographed paper log where the readings are handwritten and only some are legible — §2.7 is the only route in: “A screenshot is always a screenshot of something”
- an incident record written as an email
- distinguishing a food-safety cleaning schedule from a general site cleaning record

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10):

- a temperature-looking number
- a checklist structure, which is identical to store operations, health and safety, and induction checklists
- a date — §3.10: “The product must not use fuzzy date parsing because file names and documents frequently contain numbers that look like years but are course identifiers, version numbers, build numbers, ZIP codes, or other unrelated values.”
- a site name

### Work types

`temperature log`, `cleaning schedule`, `delivery check record`, `hazard analysis plan`, `traceability record`, `training record`, `incident report`, `inspection report`

### Grouping reasons (§4)

- one site's records for one month, as the set an inspection would ask for
- one incident and the logs, deliveries and training records around it
- one hazard plan and the daily records that evidence it

### Template (§5)

`site → record class → period`

Time first: **no**

NOT time-first, and this is the closest call in the slice. Every record here is a statement about a day, which pulls toward §5.5's exception — but that exception is granted to capture-based media because “Photos and capture-based media are the major exception: time often belongs first because capture date is a defining aspect of the material.”, and a temperature log is a generated record whose date is an attribute rather than its content. §5.5's “a parent dimension should provide the context required to understand the child” settles it: an inspector asks for one site's logs for a period, so the site leads and the class makes the period legible. Where the log IS a photograph of a paper sheet, the capture date and the recorded date can differ and the recorded date governs.

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| retail.store-ops | both are checklist-shaped daily records at one site. The separating signal is a temperature, a probe reading or a named safety procedure; without one the engine cannot tell them apart | §6.10: “Correct abstention is a successful outcome because the product’s goal is reliable organization, not maximum file movement.” |
| hosp.menu-recipe-costing | the allergen matrix is a safety record and a commercial document, and §3.11 keeps both fact sets | §3.11: “One file may hold facts from more than one domain without losing information.” |
| cons.method-statement-ra | both are safety regimes with plans, records and incidents. The separating signal is the hazard domain: food versus physical work | §4.8: “that each fact or label belongs to an allowed domain schema” |
| qual.inspection-record | both are dated, signed conformity records against a defined limit. The separating signal is the regime: a food hazard plan against a quality management system | §4.8: “that each fact or label belongs to an allowed domain schema” |

### Sensitivity

`potentially_sensitive` — §2.9's phrase “while treating addresses and message content as potentially sensitive” only. Fitness-to-work and illness-exclusion records are health information about named staff, and training records are employment materials — §8.4 names both in “identity documents, account statements, tax records, medical information, legal records, credentials, private correspondence, GPS metadata, employment materials, and educational records”. The temperature and cleaning bulk of the domain is not sensitive; §8.4's classification is evidence-backed and revisable, which is what lets both live here. No handling class is set; that is P7's.

---

## `hosp.premises-licensing` — Premises licensing and permissions

The permissions a venue must hold to trade — applications, grants, conditions, variations, reviews and the notices that go with them.

**Provenance:** **proposal** — new — the design does not name this domain, and nothing here is asserted as the design's

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `premises` | string | Harbourside, 12 Quay Street | `validated` | Licences attach to premises and transfer with them, which is why the premises is the durable parent and the holder is not. |
| `licence_type` | string | as named on the licence | `validated` | Alcohol, entertainment, late-hours, street-trading, gambling and pavement permissions are distinct regimes. Their names are jurisdiction-defined and none is named in this catalogue — see the open question. |
| `licence_reference` | string | as issued by the licensing authority | `validated` | §3.5's model: a fact only “when the engine finds a course-code pattern together with academic context”, the corroborating context being licensing language. |
| `licensing_authority` | string | as named on the licence | `validated` | §3.8: “The system must separate roles that happen to contain the same entity type.” — the authority, the licence holder, the designated supervisor and the applicant's agent are four roles on one grant. |
| `licence_status` | string | granted | `validated` | Applied, granted, varied, suspended, under review and lapsed are labeled states, and the current one is the only thing that matters operationally. |
| `conditions` | string | as attached to the licence | `llm_supported` | Conditions are numbered prose obligations and must be read. §3.5: “It can only propose facts that belong to the active domain schema, and it must cite exact supporting evidence already extracted from the file.” |
| `effective_period` | date range | as stated on the licence | `direct` | §3.13: “A direct fact was read from a reliable and explicit source, such as a content hash, EXIF timestamp, document title, or labeled form field.” — a labeled field, and the field a renewal is calculated from. This catalogue holds no interval. |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.3, §3.5):

- licensing language ('premises licence' | 'licensing authority' | 'designated premises supervisor' | 'licensable activities' | 'representation' | 'review of the licence') co-occurring with a premises address
- a grant structure: an authority block, a licence reference, a premises address and an attached conditions schedule
- an application structure: a labeled applicant, a premises address and a schedule of proposed activities and hours

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- a scanned historic licence whose regime is identifiable only from its letterhead
- correspondence about a representation or objection that never restates the reference
- deciding which licensing regime a document belongs to, which is a jurisdiction question the design does not answer

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10):

- the word 'licence', which in this slice is also a licence to alter, a driver's licence, a software licence and an operator licence
- an authority name — §4.9's warning transfers: “A university name alone should not create a group because Columbia can appear as an authoring school, course provider, target institution, employer, research venue, or merely a cited organization.”
- a reference pattern, jurisdiction-specific and colliding with planning, case and account references
- a premises address

### Work types

`licence application`, `granted licence`, `conditions schedule`, `variation application`, `transfer application`, `review papers`, `notice`, `training record for a required qualification`

### Grouping reasons (§4)

- one premises' licensing history from first application to current grant
- one application from submission to grant, including representations
- one review and the evidence filed for it

### Template (§5)

`premises → licence type → document type`

Time first: **no**

§5.5: “a parent dimension should provide the context required to understand the child” — a conditions schedule is meaningless without its licence and a licence without its premises. Premises leads because licences run with the building and outlast their holders. Time does not lead: a licence in force may be decades old and filing by year would bury the current grant beneath its own history — “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders.”

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| cons.building-control | both are authority permissions attached to a property and both carry authority references. The separating signal is what is permitted: building works versus trading activity | §3.9: “Topic answers what a file is about, while purpose answers what the file was for.” |
| admin.licences-permits | the finance-legal slice owns licences and permits generally; a premises licence earns a hospitality domain because its subject is a venue and it drives that venue's daily operation | §3.9: “Topic answers what a file is about, while purpose answers what the file was for.” |
| prop.commercial-lease | the lease permits use and the licence permits activity; both restrict what can happen at the premises and both are consulted together | §4.9: “A file may validly belong to more than one accepted group” |
| gov.permit-licensing-authority | the same two-sided split: the venue's licence pack against the authority's licensing case file. The separating signal is whether the document was issued or received | §3.8: “The system must separate roles that happen to contain the same entity type.” |

### Sensitivity

`potentially_sensitive` — §2.9's phrase “while treating addresses and message content as potentially sensitive” only. Licence applications routinely carry the personal details of named individuals and, in some regimes, declarations about their history that are legal records — §8.4 names legal records in “identity documents, account statements, tax records, medical information, legal records, credentials, private correspondence, GPS metadata, employment materials, and educational records”. The handling class is P7's and is not set here.

### Open question — Joseph's call, unresolved

> Which jurisdictions, and therefore which licensing regimes? This entry names no regime, no licence class and no form number, because licensing is constituted differently in every jurisdiction and inventing a scheme name would be a confident false positive on someone's trading permissions. That leaves this domain's recognisers structural rather than lexical. Joseph's call, and it is the same call as the one raised on building control and on compliance certificates.

---

## `event.production` — Event production and delivery

Putting on one event — the brief, the plan, the suppliers, the run sheet on the day and the reconciliation afterwards.

**Provenance:** **proposal** — new — the design does not name this domain, and nothing here is asserted as the design's

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `event` | string | Harbour Summer Ball | `validated` | The named event. §4.9's warning about a recurring identifier transfers directly: a name alone must not merge two editions — “A course code alone should not merge different semesters; course packet identity should include a term when it is available.” |
| `edition` | string | 2026 | `validated` | Which running of the event. Together with the name it is the identity; separately neither is. |
| `event_date` | date range | 2026-07-18 to 2026-07-19 | `direct` | §3.13: “A direct fact was read from a reliable and explicit source, such as a content hash, EXIF timestamp, document title, or labeled form field.” §2.9 makes it reachable from a calendar file too: “Calendar formats such as ICS should yield event title, start and end time, location, organizer, attendees, and recurrence metadata.” |
| `venue` | string | Harbourside, 12 Quay Street | `validated` | Where it happened, which is what links the event to licensing, catering and access requirements. |
| `supplier_role` | string | audio-visual | `validated` | §3.8: “The system must separate roles that happen to contain the same entity type.” — client, agency, venue and each supplier are separate roles, and an event brief names all of them in one document. |
| `production_document_class` | string | run sheet | `validated` | Brief, budget, floor plan, run sheet, risk assessment and reconciliation are the recurring artefacts and the level a user navigates. |
| `attendee_requirements` | string | as recorded on the guest list | `llm_supported` | Accessibility and dietary requirements attached to named guests, which is what makes this domain “while treating addresses and message content as potentially sensitive”. |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.3, §3.5):

- event-production language ('run sheet' | 'running order' | 'call time' | 'get-in' | 'get-out' | 'floor plan' | 'event brief') co-occurring with an event name and a date
- an event name co-occurring with an edition marker in a filename, title or page-one heading — §2.2: “A course code or university name found in a filename, title, or page-one heading is more meaningful than the same text appearing once in a reference list on page eighteen.”
- a calendar file whose event title matches a document's event name and whose start and end times bound the production window — §2.9: “Calendar formats such as ICS should yield event title, start and end time, location, organizer, attendees, and recurrence metadata.”

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- a supplier quotation that must be recognised as belonging to an event rather than to a standing arrangement
- a floor plan with no title, where the venue must be read from the drawing
- distinguishing this year's brief from last year's when the document was copied and only partly updated

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10):

- an event name — §4.9: “A course code alone should not merge different semesters; course packet identity should include a term when it is available.” is the same failure with a different noun
- a date, and a recurring annual event makes the date the only thing that separates two otherwise identical files
- a venue name, which appears across licensing, catering, bookings and event files for the same building
- the word 'event', which is also a delay event, a lease event and a calendar event

### Work types

`event brief`, `budget`, `floor plan`, `run sheet`, `supplier contract`, `risk assessment`, `guest list`, `post-event reconciliation`, `event photograph set`

### Grouping reasons (§4)

- one edition of one event across every document and supplier
- one event's editions over years, for comparison
- one supplier across the events they worked

### Template (§5)

`event → edition → document class`

Time first: **no**

§5.5: “a parent dimension should provide the context required to understand the child” — a run sheet is meaningless without the edition and an edition without the event. This is the domain where §4.9's warning is most load-bearing: “A course code alone should not merge different semesters; course packet identity should include a term when it is available.” — the same words with 'edition' for 'term'. Time is second rather than first because the event name is what anyone searches; the edition disambiguates it. Photographs of the event are capture-based and belong to the capture question raised on cons.progress-photos.

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| hosp.catering-contract | catering is one supplier within an event and also a contract in its own right with its own client. The separating signal is whose file it is: the caterer's or the producer's | §3.8: “The system must separate roles that happen to contain the same entity type.” |
| hosp.bookings | a private function is a booking to the venue and an event to the producer. The same evening is two domains from two sides | §3.9: “Topic answers what a file is about, while purpose answers what the file was for.” |
| hosp.premises-licensing | a temporary permission for an event is a licensing document about a venue that exists only because of this event | §4.9: “A file may validly belong to more than one accepted group” |

### Sensitivity

`potentially_sensitive` — §2.9's phrase “while treating addresses and message content as potentially sensitive” only. Guest lists carry names, contact details and accessibility or dietary requirements, the last of which is health information — §8.4 names “identity documents, account statements, tax records, medical information, legal records, credentials, private correspondence, GPS metadata, employment materials, and educational records”. The production half of the domain is not sensitive; §8.4's classification being evidence-backed and revisable is what lets both live here. No handling class is set; that is P7's.

---

## `hosp.bookings` — Bookings and reservations

Who is coming, when, for how many and with what requirements — the reservation record and the confirmation that answers it.

**Provenance:** **inference** — extends a design-named domain or template situation; the cite supports the extension, not the whole entry

**Cite:** Extends §7.3's residual template “Receipts and Confirmations may hold isolated invoices, delivery confirmations, booking records, boarding passes, purchase receipts, event tickets, and similar transactional documents.” which names booking records as a recognised isolated record type, and extends §2.9's calendar extraction: “Calendar formats such as ICS should yield event title, start and end time, location, organizer, attendees, and recurrence metadata.”

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `venue_or_property` | string | Harbourside, 12 Quay Street | `validated` | What was booked. The venue is the parent; the booking is the child. |
| `booking_reference` | string | as issued by the venue or the platform | `validated` | §3.5's model: a fact only “when the engine finds a course-code pattern together with academic context”, the corroborating context being reservation language. |
| `booking_datetime` | date | 2026-07-18 | `direct` | §3.13: “A direct fact was read from a reliable and explicit source, such as a content hash, EXIF timestamp, document title, or labeled form field.” §2.9 makes it reachable from an ICS attachment: “Calendar formats such as ICS should yield event title, start and end time, location, organizer, attendees, and recurrence metadata.” |
| `party_size` | string | as stated on the confirmation | `direct` | A labeled field. This catalogue holds no number. |
| `channel` | string | reservation platform | `validated` | §3.8: “The system must separate roles that happen to contain the same entity type.” — the guest, the venue and the intermediary platform are three parties and the platform's branding usually dominates the document. |
| `guest` | string | as named on the booking | `validated` | The lead booker, distinct from the party and from the payer. |
| `special_requirements` | string | as recorded on the booking | `llm_supported` | Allergies, accessibility and occasion notes are free text, and the first two are health information. |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.3, §3.5):

- reservation language ('booking confirmation' | 'reservation' | 'confirmed for' | 'check-in' and 'check-out' as a labeled pair | 'cancellation policy') co-occurring with a venue name and a date
- a booking-reference pattern co-occurring with a labeled date and party size
- an ICS attachment whose organiser and title match a confirmation document in the same folder — §2.9: “Calendar formats such as ICS should yield event title, start and end time, location, organizer, attendees, and recurrence metadata.”

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- a screenshot of a booking screen, which §2.7 is the only route into: “A screenshot is always a screenshot of something”
- an email thread that arranges a booking without ever producing a confirmation
- distinguishing a personal booking from a business one, which is invisible in the document

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10):

- a booking reference — the same shape as an order number and a case reference
- a date
- a platform's name, which brands the document without owning the booking
- a venue name

### Work types

`booking confirmation`, `reservation record`, `cancellation`, `amendment`, `deposit receipt`, `calendar invitation`, `no-show record`

### Grouping reasons (§4)

- one booking across confirmation, amendment and cancellation
- one date's bookings at one venue, as a service
- one guest's bookings over time

### Template (§5)

`venue → period → booking`

Time first: **no**

§5.5: “a parent dimension should provide the context required to understand the child” — a booking reference is only findable once the venue and the period narrow it. Period sits second because a venue's bookings are consulted by service date; it is not first because two venues' dates must not merge — “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders.”. §7.3 is the honest fallback for an isolated personal booking with no venue file: “Receipts and Confirmations may hold isolated invoices, delivery confirmations, booking records, boarding passes, purchase receipts, event tickets, and similar transactional documents.”

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| fin.receipts-expenses | THE BOUNDARY, and §7.3 already names the overlap: “Receipts and Confirmations may hold isolated invoices, delivery confirmations, booking records, boarding passes, purchase receipts, event tickets, and similar transactional documents.”. A deposit receipt is a booking document and a transaction record. The venue's file wants the booking; the traveller's file wants the receipt | §3.9: “Topic answers what a file is about, while purpose answers what the file was for.” |
| event.production | a private function is a booking to the venue and a production to the organiser; the same evening from two sides | §3.8: “The system must separate roles that happen to contain the same entity type.” |
| hosp.catering-contract | a large booking with a menu and a deposit becomes a function contract; the separating signal is a signed agreement rather than a confirmation | §3.9: “Topic answers what a file is about, while purpose answers what the file was for.” |

### Sensitivity

`potentially_sensitive` — §2.9's phrase “while treating addresses and message content as potentially sensitive” only. A booking record names a guest, their contact details and frequently their allergies or accessibility needs, which is health information — §8.4 names medical information and private correspondence in “identity documents, account statements, tax records, medical information, legal records, credentials, private correspondence, GPS metadata, employment materials, and educational records”. The handling class is P7's and is not set here.

---

## `hosp.catering-contract` — Catering contracts and function delivery

A caterer's engagement for one function — proposal, contract, function sheet, allergen information and the invoice at the end.

**Provenance:** **proposal** — new — the design does not name this domain, and nothing here is asserted as the design's

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `client` | string | Northgate Dental Practice | `validated` | §3.8: “The system must separate roles that happen to contain the same entity type.” — the paying client, the venue, the guest of honour and the agency that introduced the work are four roles. |
| `function` | string | staff summer party | `validated` | The occasion, which is what makes a function sheet legible and what the client calls it. |
| `function_date` | date | 2026-07-18 | `direct` | §3.13: “A direct fact was read from a reliable and explicit source, such as a content hash, EXIF timestamp, document title, or labeled form field.” A function is a single dated delivery and the date is half its identity. |
| `venue` | string | Harbourside, 12 Quay Street | `validated` | Where it is served, which is usually not the client's own premises and drives the whole operational plan. |
| `service_style` | string | as stated on the function sheet | `validated` | Buffet, plated service, canapés and drop-off are different operations with different staffing and different equipment. |
| `menu_agreed` | string | as attached to the contract | `validated` | The dishes committed to, which is the join back to recipe costing and to allergen information. |
| `dietary_requirements` | string | as recorded on the function sheet | `llm_supported` | Requirements attached to named guests, which is what makes this domain “while treating addresses and message content as potentially sensitive” and is written as free text on every function sheet in existence. |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.3, §3.5):

- function-catering language ('function sheet' | 'per head' | 'service style' | 'canapé' | 'covers' | 'final numbers by') co-occurring with a client name and a function date
- a proposal structure pairing a labeled function date, a venue and an agreed menu
- a labeled final-numbers deadline co-occurring with a per-head price, which is a structure unique to this domain

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- an email agreeing a function that never produces a contract
- a menu written for one function that must be distinguished from the standing menu it was drawn from
- a dietary list sent separately from the function sheet, which must be linked to the right function

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10):

- a client name — §3.8: “A folder should not become a collection point for everything produced by the same person or organization.”
- a date
- a venue name, shared with bookings, licensing and event files
- a per-head amount

### Work types

`proposal`, `function contract`, `function sheet`, `agreed menu`, `dietary and allergen list`, `staffing plan`, `equipment list`, `invoice`

### Grouping reasons (§4)

- one function across proposal, contract, sheet and reconciliation
- one client's functions over years
- one venue's functions, for operational planning

### Template (§5)

`client → function → document type`

Time first: **no**

§5.5: “a parent dimension should provide the context required to understand the child” — a function sheet is meaningless without the function and a function without the client. Client leads because repeat business is the caterer's economics and a client's history is what anyone opens the folder for. Time does not lead even though every function is a date: “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders.”

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| event.production | catering is a supplier within an event and a contract of its own. Whose file it is decides which domain owns it | §3.8: “The system must separate roles that happen to contain the same entity type.” |
| hosp.menu-recipe-costing | the agreed menu is drawn from the standing menu and is then a contract term rather than a product; the separating signal is a client and a function date | §3.9: “Topic answers what a file is about, while purpose answers what the file was for.” |
| trade.quote-estimate | the structural twin in another trade: a priced proposal for work not yet done, with a validity clause and no invoice number. The two domains share a shape and nothing else | §3.9: “Topic answers what a file is about, while purpose answers what the file was for.” |

### Sensitivity

`potentially_sensitive` — §2.9's phrase “while treating addresses and message content as potentially sensitive” only. Function sheets carry allergen and dietary requirements attached to named individuals, which is health information — §8.4 names medical information in “identity documents, account statements, tax records, medical information, legal records, credentials, private correspondence, GPS metadata, employment materials, and educational records”. The handling class is P7's and is not set here.

---

## `hosp.guest-feedback` — Guest feedback, reviews and complaints

What guests said afterwards — platform reviews, direct complaints, survey results and the responses that go back.

**Provenance:** **proposal** — new — the design does not name this domain, and nothing here is asserted as the design's

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `venue` | string | Harbourside, 12 Quay Street | `validated` | What the feedback is about. It is the only dimension a group operator can act on. |
| `feedback_channel` | string | review platform | `validated` | §3.8: “The system must separate roles that happen to contain the same entity type.” — the guest, the venue and the platform are three parties, and platform branding dominates the document while the platform owns none of the substance. |
| `feedback_date` | date | 2026-07-20 | `direct` | §3.13: “A direct fact was read from a reliable and explicit source, such as a content hash, EXIF timestamp, document title, or labeled form field.” §3.10's explicit-regex path only. |
| `feedback_type` | string | complaint | `validated` | Review, direct complaint, survey response and compliment are different objects: only one of them requires a reply and a record. |
| `visit_reference` | string | as quoted by the guest | `validated` | A booking or receipt reference quoted in the feedback, which is what makes it investigable rather than merely a sentiment. |
| `issue_summary` | string | as written by the guest | `llm_supported` | Feedback is prose and its classification is exactly the language interpretation §3.5 reserves for the model: “It can only propose facts that belong to the active domain schema, and it must cite exact supporting evidence already extracted from the file.” |
| `resolution` | string | as recorded in the response | `llm_supported` | What was offered and whether it closed the matter, stated in correspondence. |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.3, §3.5):

- feedback language ('review' | 'complaint' | 'we are sorry to hear' | 'rating' | 'guest satisfaction' | 'survey response') co-occurring with a venue name and a visit date
- a survey export whose column headers pair a question with a response and a submission date — §2.9: “Spreadsheets such as XLSX, XLS, CSV, TSV, ODS, and Numbers exports should yield workbook or file metadata, sheet names, column headers, visible cell values, table-like regions, formulas only when useful, and dates or identifiers from labeled cells.”
- a booking or receipt reference quoted in a feedback document that also exists in a bookings file, which links them deterministically

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- a screenshot of a review, which is the ordinary form this material arrives in — §2.7: “A screenshot is always a screenshot of something”
- an email that is a complaint without saying so
- separating a complaint that requires action from an expression of dissatisfaction that does not

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10):

- a venue name
- a rating-looking number
- the word 'review', which in this slice is also a licence review, a contract review and a document review date
- a screenshot's OCR density — §2.6: “OCR text density is also not a reliable screenshot detector because receipts, document scans, whiteboards, and photographs of pages can all contain dense text.”

### Work types

`platform review`, `complaint`, `survey response`, `response letter`, `goodwill record`, `feedback summary report`, `incident record`

### Grouping reasons (§4)

- one complaint from receipt to resolution
- one venue's feedback for a period, as a summary
- one visit's booking, bill and feedback, linked by a reference

### Template (§5)

`venue → feedback type → period`

Time first: **no**

§5.5: “a parent dimension should provide the context required to understand the child” — feedback is only actionable per venue, and complaints and reviews are consulted for different reasons. Period sits last: “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders.”. §7.7's caution applies to the screenshot case that dominates this domain: “An isolated file should normally remain high in the tree because there is no evidence that it deserves a deep project-specific path.”

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| hosp.bookings | feedback quotes a booking reference and belongs to the visit, but bookings are operational and feedback is reputational; they are consulted by different people for different reasons | §4.9: “A file may validly belong to more than one accepted group” |
| retail.returns-warranty | a complaint about a product and a complaint about a stay are the same shape. The separating signal is whether a product identifier or a visit reference is quoted | §3.9: “Topic answers what a file is about, while purpose answers what the file was for.” |
| hosp.food-safety | a complaint alleging illness is a food-safety incident as well as feedback, and it is the case where the domain acquires medical content | §3.11: “One file may hold facts from more than one domain without losing information.” |

### Sensitivity

`potentially_sensitive` — §2.9's phrase “while treating addresses and message content as potentially sensitive” only. Complaints name individuals, quote their correspondence and sometimes describe illness or injury — §8.4 names private correspondence and medical information in “identity documents, account statements, tax records, medical information, legal records, credentials, private correspondence, GPS metadata, employment materials, and educational records”. The handling class is P7's and is not set here.

---

## `log.shipment` — Freight consignments and shipping documentation

One consignment moving from an origin to a destination under a carrier — the documents that travel with the goods and prove what happened to them.

**Provenance:** **proposal** — new — the design does not name this domain, and nothing here is asserted as the design's

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `consignment_reference` | string | as issued by the carrier | `validated` | §3.5's model applied to the strongest identifier in this half of the slice: a consignment number is a fact only “when the engine finds a course-code pattern together with academic context”, the corroborating context being carriage language. Carriers, forwarders and shippers each issue their own reference for the same box. |
| `origin` | string | Felixstowe | `validated` | Where the goods started. §3.8: “The system must separate roles that happen to contain the same entity type.” — the shipper's address, the collection address and the port of loading are three different places that one document names. |
| `destination` | string | Central DC, bay 3 | `validated` | Where they were going, distinct from the consignee's registered office and from the final delivery point. |
| `carrier` | string | as named on the consignment note | `validated` | §3.8 again: carrier, forwarder, shipper and consignee are four parties on one document and the forwarder's branding usually dominates it. |
| `mode` | string | sea freight | `validated` | Sea, air, road and rail carry different documents with different legal effects, and the mode is what makes a document type interpretable. |
| `shipment_dates` | date range | 2026-06-02 to 2026-07-11 | `direct` | §3.13: “A direct fact was read from a reliable and explicit source, such as a content hash, EXIF timestamp, document title, or labeled form field.” — labeled departure and arrival fields. §3.10's explicit-regex path only: “The product must not use fuzzy date parsing because file names and documents frequently contain numbers that look like years but are course identifiers, version numbers, build numbers, ZIP codes, or other unrelated values.” |
| `goods_description` | string | as declared on the note | `llm_supported` | Declared descriptions are terse trade prose and must be read to be matched to an order. §3.5: “It can only propose facts that belong to the active domain schema, and it must cite exact supporting evidence already extracted from the file.” |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.3, §3.5):

- carriage language ('bill of lading' | 'air waybill' | 'consignment note' | 'shipper' and 'consignee' as labeled parties | 'port of loading' | 'gross weight') co-occurring with a consignment reference
- a labeled shipper-and-consignee pair, which is a structure that exists in no other domain in this slice
- a consignment reference appearing in two documents that share a carrier — the note and its tracking record — which builds the chain deterministically

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- a photographed paper consignment note whose OCR is partial and whose carrier is a logo
- an email tracking update that must be matched to a consignment it does not fully reference
- distinguishing a forwarder's house document from the carrier's master document when both restate the same goods

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10):

- a consignment or tracking reference — the single most over-firing pattern in this half of the slice, sharing its shape with order numbers, invoice numbers and case references
- a carrier name, which appears as carrier, as forwarder, as a merely cited service and in every email footer
- a weight or a container-looking code
- a port or city name, which is also an origin, a destination, a company address and a transhipment point

### Work types

`consignment note`, `bill of lading`, `air waybill`, `packing list`, `tracking record`, `arrival notice`, `damage or loss claim`, `freight invoice`

### Grouping reasons (§4)

- one consignment across every document that travelled with it
- one shipment linked to the purchase order it fulfils
- one claim and the consignment documents that evidence it

### Template (§5)

`carrier or route → shipment → document type`

Time first: **no**

§5.5: “a parent dimension should provide the context required to understand the child” — a packing list is meaningless without its consignment, and consignment references are only unique within a carrier. Time does not lead even though shipments are dated events: “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders.”, and a consignment that crosses a year boundary would otherwise be split from its own arrival documents.

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| log.customs-export | customs documents travel with the same consignment and reference the same numbers, but they are a declaration to an authority rather than a contract of carriage. The separating signal is a customs authority or a commodity code | §3.8: “The system must separate roles that happen to contain the same entity type.” |
| retail.supplier-order | the supplier's delivery note and the carrier's consignment note name the same goods and belong to different parties. §3.8's role separation is the whole answer | §3.8: “The system must separate roles that happen to contain the same entity type.” |
| log.last-mile-pod | a consignment note ends at the delivery point where the proof-of-delivery capture begins; the reference is shared and the domains are not | §3.11: “One file may hold facts from more than one domain without losing information.” |

### Sensitivity

`none` — Freight documentation concerns goods and companies. None of §8.4's named categories is routine. A personal-effects shipment is the exception and would carry identity documents; §8.4's classification is evidence-backed and revisable per file for that case. No handling class is set; that is P7's.

---

## `log.customs-export` — Customs, export and trade compliance

Declaring goods to an authority when they cross a border — declarations, origin and licence evidence, and the classification that drives the duty.

**Provenance:** **proposal** — new — the design does not name this domain, and nothing here is asserted as the design's

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `declaration_reference` | string | as issued by the customs authority | `validated` | §3.5's model: a fact only “when the engine finds a course-code pattern together with academic context”, the corroborating context being customs language. Declaration reference formats are jurisdiction-specific and none is named here. |
| `consignment_reference` | string | as issued by the carrier | `validated` | The join back to the shipment, and the field that makes a declaration investigable against what actually moved. |
| `commodity_classification` | string | as declared | `validated` | The tariff classification of the goods. Classification systems are international in structure and national in detail, so this catalogue names no code and no schedule. |
| `origin_country` | string | as declared | `validated` | §3.8: “The system must separate roles that happen to contain the same entity type.” — country of origin, country of dispatch and the exporter's own country are three different declared facts that are routinely conflated. |
| `declarant` | string | as named on the declaration | `validated` | Who made the declaration, which is distinct from the exporter, the importer and the agent acting for either. |
| `declaration_date` | date | 2026-06-02 | `direct` | §3.13: “A direct fact was read from a reliable and explicit source, such as a content hash, EXIF timestamp, document title, or labeled form field.” §3.10's explicit-regex path only. |
| `licence_or_control` | string | as stated on the licence | `llm_supported` | Export controls and licensing regimes are jurisdiction-defined and are written functionally here. §3.5: “it may extract only fields allowed by the relevant schema” |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.3, §3.5):

- customs language ('customs declaration' | 'certificate of origin' | 'commodity code' | 'incoterms' | 'exporter' and 'importer' as labeled parties | 'duty and tax') co-occurring with a declaration or consignment reference
- a commodity-classification pattern co-occurring with a goods description and a declared value in one line
- a certificate-of-origin structure: an issuing chamber or authority, an exporter block and a goods schedule

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- a scanned declaration in a language or format the gazetteer does not cover, which is the ordinary case until the jurisdiction question is answered
- correspondence about a classification dispute
- distinguishing a proforma invoice made for customs from the commercial invoice it was derived from

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10):

- a commodity-code pattern — a digit string whose shape collides with part numbers, account numbers and postal codes
- a country name, which appears as origin, dispatch, destination, the parties' domiciles and merely cited places
- a declaration reference, jurisdiction-specific and shape-colliding
- the word 'export', which is also a data export in the retail and energy domains of this same slice

### Work types

`customs declaration`, `commercial invoice for customs`, `certificate of origin`, `export licence`, `packing list`, `duty and tax calculation`, `compliance correspondence`

### Grouping reasons (§4)

- one declaration and every document supporting it
- one consignment's carriage and customs papers together
- one classification decision across the shipments it governs

### Template (§5)

`jurisdiction or route → shipment → document type`

Time first: **no**

§5.5: “a parent dimension should provide the context required to understand the child” — a certificate of origin is meaningless without the shipment and a declaration reference is only interpretable inside its jurisdiction. Time does not lead: “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders.”, and a retrospective duty query reaches back across years to one shipment.

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| log.shipment | the same consignment, a different audience: the carrier's contract versus the authority's declaration. The separating signal is a customs authority, a commodity code or a duty calculation | §3.8: “The system must separate roles that happen to contain the same entity type.” |
| biz.invoice-issued | THE BOUNDARY, in its trickiest form. A commercial invoice produced for customs is an accounting record and a customs document at once, and the same PDF is filed twice by two different people for two different reasons | §3.11: “One file may hold facts from more than one domain without losing information.” |
| corp.regulatory-filings | the finance-legal slice owns regulatory filings generally; customs declarations earn a logistics domain because they attach to a consignment rather than to an entity's reporting cycle | §3.9: “Topic answers what a file is about, while purpose answers what the file was for.” |

### Sensitivity

`none` — Customs documentation concerns goods, companies and authorities. None of §8.4's named categories is routine. No handling class is set here; that is P7's.

### Open question — Joseph's call, unresolved

> Which jurisdictions? Customs regimes, declaration formats, reference shapes, tariff schedules and export-control lists are all national or bloc-level and are not translations of one another. This catalogue names no code, no schedule, no regime and no form number, which leaves the recognisers structural. Joseph's call, and it is the same call raised on building control, compliance certificates and premises licensing.

---

## `fleet.vehicle` — Fleet and vehicle records

One vehicle across its working life — acquisition, licensing, insurance, servicing, defects, fuel and disposal.

**Provenance:** **proposal** — new — the design does not name this domain, and nothing here is asserted as the design's

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `vehicle_identifier` | string | as printed on the registration document | `validated` | §3.5's model: a registration or chassis identifier is a fact only “when the engine finds a course-code pattern together with academic context”, the corroborating context being vehicle-document language. Registration marks change hands; the chassis identifier does not, and both appear on the same document as different fields. |
| `vehicle_description` | string | 18-tonne curtainside | `validated` | What the vehicle is, which is what makes a service record or a defect report interpretable. |
| `record_class` | string | service record | `validated` | Registration, insurance, inspection, service, defect, fuel and disposal are the recurring classes and the level a user navigates. |
| `operator` | string | as named on the licence | `validated` | §3.8: “The system must separate roles that happen to contain the same entity type.” — the registered keeper, the operator, the lessor and the driver are four roles and a leased vehicle's paperwork names all four. |
| `record_date` | date | 2026-05-06 | `direct` | §3.13: “A direct fact was read from a reliable and explicit source, such as a content hash, EXIF timestamp, document title, or labeled form field.” §3.10's explicit-regex path only: “The product must not use fuzzy date parsing because file names and documents frequently contain numbers that look like years but are course identifiers, version numbers, build numbers, ZIP codes, or other unrelated values.” |
| `next_due_date` | date | as printed on the record | `direct` | A labeled field on inspection and test records. It is recorded, never computed: intervals are jurisdiction-defined and injected, and this catalogue holds none. |
| `defect_or_fault` | string | as reported by the driver | `llm_supported` | Defect reports are written in a cab at the end of a shift. §3.13: “An LLM-supported fact was proposed by a language model from a bounded evidence packet, cited exact supporting text or metadata, and passed deterministic validation.” |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.3, §3.5):

- vehicle-document language ('registration' | 'chassis' | 'odometer' | 'roadworthiness' | 'safety inspection' | 'defect report') co-occurring with a vehicle identifier
- a registration-mark pattern co-occurring with a labeled make, model or chassis field — the mark alone is not a fact
- a service or inspection record pairing a labeled odometer reading with a dated signature block

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- a photographed paper defect sheet completed in a cab
- an invoice for work on a vehicle that names it only by a fleet nickname
- distinguishing a lease document from a purchase document when both describe the same vehicle

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10):

- a registration mark — its shape is jurisdiction-specific and collides with reference numbers and product codes
- an odometer-looking number
- a make and model, which appear in listings, quotations, insurance schedules and price lists
- a date pair, shared with insurance, tenancy, hire and licence periods

### Work types

`registration document`, `insurance schedule`, `safety inspection record`, `service record`, `defect report`, `fuel record`, `lease or purchase document`, `disposal record`

### Grouping reasons (§4)

- one vehicle's whole life across every record class
- one inspection cycle across its records
- one fleet's insurance schedule across its vehicles

### Template (§5)

`vehicle → record class → date`

Time first: **no**

§5.5: “a parent dimension should provide the context required to understand the child” — a service record is meaningless without the vehicle. This is one of the few domains in the slice where the leading dimension is an asset identifier rather than a person or a place, and it works because the identifier is printed on the object and on every document about it. Time sits last: “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders.”, so a vehicle's history stays in one place.

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| fleet.driver-compliance | the vehicle file and the driver file meet on every inspection and every incident and must not merge: one is about an asset and the other is employment and medical material about a person | §3.8: “The system must separate roles that happen to contain the same entity type.” |
| cons.plant-hire | an owned vehicle is a fleet asset; a hired machine is a temporary contract. The separating signal is ownership, stated in the hire agreement | §3.8: “The system must separate roles that happen to contain the same entity type.” |
| fin.insurance | a motor policy is an insurance record and a fleet record. §3.11 keeps both fact sets rather than forcing a choice | §3.11: “One file may hold facts from more than one domain without losing information.” |
| mro.asset-record | a road-registered vehicle and a maintained asset are the same object under two regimes. The separating signal is a registration mark and a roadworthiness obligation, which no plant asset carries | §3.11: “One file may hold facts from more than one domain without losing information.” |
| pers.vehicle | a private car and a fleet vehicle produce identical documents. The separating signal is an operator and a fleet identifier — and a sole trader's van has neither, which makes this the hardest boundary in the domain | §3.8: “The system must separate roles that happen to contain the same entity type.” |

### Sensitivity

`none` — Vehicle records concern assets. None of §8.4's named categories is routine. Where a defect report names its driver it touches employment material, and that half of the material belongs to fleet.driver-compliance where it is marked. No handling class is set here; that is P7's.

---

## `fleet.driver-compliance` — Driver records and compliance

Everything held about a driver because the law requires it — licence, entitlements, medical fitness, driving-hours records, training and infringements.

**Provenance:** **proposal** — new — the design does not name this domain, and nothing here is asserted as the design's

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `driver` | string | as named on the record | `validated` | The subject of the record. §3.8's warning about person-as-collector is about authorship; here the person is genuinely the subject, which is exactly the role distinction §3.8 asks for — “The system must separate roles that happen to contain the same entity type.” |
| `record_class` | string | driving-hours record | `validated` | Licence, entitlement check, medical, hours record, training and infringement are distinct obligations with distinct retention and distinct sensitivity. |
| `operator` | string | as named on the employment record | `validated` | Who the driver drives for, which is what makes a compliance file producible to an authority. |
| `record_period` | date range | 2026-05-01 to 2026-05-28 | `direct` | §3.13: “A direct fact was read from a reliable and explicit source, such as a content hash, EXIF timestamp, document title, or labeled form field.” Hours records are produced as periods, which is what an inspection asks for. §3.10's explicit-regex path only. |
| `entitlement_or_qualification` | string | as printed on the licence | `validated` | What the driver is permitted to drive. Categories and qualification schemes are jurisdiction-defined and none is named here. |
| `expiry_date` | date | as printed on the record | `direct` | A labeled field. It is recorded, never computed; intervals are injected and this catalogue holds none. |
| `infringement` | string | as recorded on the report | `llm_supported` | Infringement reports are generated in local formats and their significance must be read. §3.13: “An LLM-supported fact was proposed by a language model from a bounded evidence packet, cited exact supporting text or metadata, and passed deterministic validation.” |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.3, §3.5):

- driver-compliance language ('driving licence' | 'entitlement' | 'tachograph' | 'driver card' | 'working time' | 'infringement report' | 'driver medical') co-occurring with a named driver and an operator
- a hours-record structure: a labeled driver identifier, a period and a table of daily durations — §2.3: “Tables matter because resumes, forms, applications, invoices, and administrative documents often place their most useful information in cells rather than body paragraphs.”
- a licence-document structure pairing a named holder with a labeled entitlement and expiry block

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- a photographed licence where the entitlement categories are pictograms
- a medical certificate whose scheme and validity must be read from prose
- an infringement export whose column headings are non-standard

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10):

- a person's name — §3.8: “A folder should not become a collection point for everything produced by the same person or organization.”
- a licence-number pattern, jurisdiction-specific and shape-colliding with references and account numbers
- a date pair
- the word 'driver', which is also a software driver — §3.7: “It should use word-boundary matching rather than substring matching.”

### Work types

`licence copy`, `entitlement check`, `medical certificate`, `driving-hours record`, `working-time record`, `training record`, `infringement report`, `induction record`

### Grouping reasons (§4)

- one driver's compliance file as an inspectable set
- one period's hours records across all drivers
- one infringement and the records around it

### Template (§5)

`operator → driver → record class`

Time first: **no**

§5.5: “a parent dimension should provide the context required to understand the child” — an hours record is meaningless without the driver. The driver IS a level here, which is the exception §3.8 permits: “It should avoid using authorship or creator identity as a destination dimension.” forbids a folder of everything a person produced, not a folder of the records held about a person because the law requires them. Operator sits above the driver so that the file can be produced per operating entity. Time does not lead: “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders.”

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| fleet.vehicle | the two files meet on every inspection and incident. Keeping them apart is the point: one is an asset record and the other is employment and medical material about a person | §3.8: “The system must separate roles that happen to contain the same entity type.” |
| trade.timesheet | a driving-hours record and a timesheet both record a person's working time for different purposes — one for legal limits, one for pay — and the same shift produces both | §3.9: “Topic answers what a file is about, while purpose answers what the file was for.” |
| cons.method-statement-ra | induction and training records exist in both domains with the same shape and different regulators | §4.8: “that each fact or label belongs to an allowed domain schema” |

### Sensitivity

`potentially_sensitive` — §2.9's phrase “while treating addresses and message content as potentially sensitive” only, and this is the most strongly marked entry in the slice. The domain is built from identity documents, medical certificates and employment materials about named individuals — §8.4 names “identity documents, account statements, tax records, medical information, legal records, credentials, private correspondence, GPS metadata, employment materials, and educational records” and the whole of that list except tax records applies here. §8.4 requires privacy policy to be enforced before content reaches any model, so the two llm_supported fields will frequently resolve to unknown rather than to a weaker value; this domain should be designed to work from its direct and validated fields alone. The handling class is P7's and is not set.

---

## `log.route-dispatch` — Route planning and dispatch

How a day's work was allocated to vehicles and drivers — plans, manifests, run sheets and the debrief on what actually happened.

**Provenance:** **proposal** — new — the design does not name this domain, and nothing here is asserted as the design's

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `depot` | string | Central DC | `validated` | The operating base. Dispatch is per depot and merging two depots' days destroys the plan's meaning. |
| `operating_date` | date | 2026-09-12 | `direct` | §3.13: “A direct fact was read from a reliable and explicit source, such as a content hash, EXIF timestamp, document title, or labeled form field.” A dispatch record is about one day and nothing else. §3.10's explicit-regex path only: “The product must not use fuzzy date parsing because file names and documents frequently contain numbers that look like years but are course identifiers, version numbers, build numbers, ZIP codes, or other unrelated values.” |
| `route` | string | as labeled on the manifest | `validated` | The named run. Route names recur daily, so the route alone identifies nothing and the route plus the date identify everything. |
| `vehicle_identifier` | string | as allocated on the manifest | `validated` | The join to the fleet record and to any incident on the day. |
| `driver` | string | as allocated on the manifest | `validated` | The join to the driver record, and the reason this domain is “while treating addresses and message content as potentially sensitive”. |
| `stops` | string | as tabulated on the manifest | `direct` | §2.3: “Tables matter because resumes, forms, applications, invoices, and administrative documents often place their most useful information in cells rather than body paragraphs.” and §2.9: “Spreadsheets such as XLSX, XLS, CSV, TSV, ODS, and Numbers exports should yield workbook or file metadata, sheet names, column headers, visible cell values, table-like regions, formulas only when useful, and dates or identifiers from labeled cells.” — a manifest's substance is a table of addresses. This catalogue holds no count. |
| `exception_note` | string | as recorded on the debrief | `llm_supported` | Failures, reattempts and delays are written as free text at the end of a shift. §3.13: “An LLM-supported fact was proposed by a language model from a bounded evidence packet, cited exact supporting text or metadata, and passed deterministic validation.” |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.3, §3.5):

- dispatch language ('manifest' | 'run sheet' | 'route plan' | 'drop sequence' | 'debrief' | 'allocated to') co-occurring with a depot name and an operating date
- a manifest structure: a labeled route and date together with a table of stops and a vehicle allocation — §2.3: “Tables matter because resumes, forms, applications, invoices, and administrative documents often place their most useful information in cells rather than body paragraphs.”
- a route-optimisation export whose column headers pair a stop sequence with an address and a time window

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- a photographed paper run sheet annotated during the shift
- an email reallocating a route mid-day that becomes the operative record
- distinguishing a plan from the record of what was actually driven, which often differ and often share a template

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10):

- a route name — it recurs every day and identifies nothing on its own
- a date in a filename — §3.10: “The product must not use fuzzy date parsing because file names and documents frequently contain numbers that look like years but are course identifiers, version numbers, build numbers, ZIP codes, or other unrelated values.”
- a depot name
- an address list, which is shared with warehouse, delivery, customer and marketing exports

### Work types

`route plan`, `manifest`, `run sheet`, `vehicle and driver allocation`, `debrief`, `exception report`, `optimisation export`

### Grouping reasons (§4)

- one operating day at one depot across plan, manifest and debrief
- one route across a week, for planning
- one exception and the dispatch records around it

### Template (§5)

`depot → operating date → route`

Time first: **no**

NOT time-first, and it is a close call because the whole domain is a daily series. §5.5's exception belongs to capture-based media and these are generated operational records: “Photos and capture-based media are the major exception: time often belongs first because capture date is a defining aspect of the material.” does not reach them. “a parent dimension should provide the context required to understand the child” puts the depot first because two depots' days must not merge, and the date second because a route name means nothing without it. A single-depot operator collapses the top level — §5.8: “The canvas must support uneven depth because real file trees are not and should not be perfectly symmetrical.”

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| log.last-mile-pod | the manifest plans the stops and the proof-of-delivery captures record them. Both are keyed on depot plus date plus route, which makes them retrieve each other and must not make either absorb the other | §3.11: “One file may hold facts from more than one domain without losing information.” |
| retail.store-ops | a rota and a dispatch allocation are both plans naming people against a day, and they are produced from the same kind of spreadsheet | §4.9: “A semantic embedding alone is insufficient.” |
| fleet.driver-compliance | the allocation names the driver and the hours record measures them; the allocation is operational and the hours record is legal | §3.9: “Topic answers what a file is about, while purpose answers what the file was for.” |

### Sensitivity

`potentially_sensitive` — §2.9's phrase “while treating addresses and message content as potentially sensitive” only. A manifest is a list of customers' addresses, and the allocation is employment material naming drivers and tracking their day. §8.4 names employment materials and GPS metadata in “identity documents, account statements, tax records, medical information, legal records, credentials, private correspondence, GPS metadata, employment materials, and educational records”. The handling class is P7's and is not set here.

---

## `log.warehouse-ops` — Warehouse and depot operations

What happened inside the building — goods in, put-away, picking, packing, dispatch and the exceptions that broke the flow.

**Provenance:** **proposal** — new — the design does not name this domain, and nothing here is asserted as the design's

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `facility` | string | Central DC | `validated` | The site. Every record here is per facility and a merged figure is a wrong figure. |
| `operation_class` | string | goods in | `validated` | Goods in, put-away, pick, pack, dispatch, cycle count and returns processing are distinct operations with distinct records. |
| `operating_period` | string | week 37 | `validated` | Operational records batch by shift, day or week rather than by month, which is why this is a domain field. |
| `reference` | string | as issued by the warehouse system | `validated` | §3.5's model: a receipt, pick or dispatch reference is a fact only “when the engine finds a course-code pattern together with academic context”, the corroborating context being warehouse language. |
| `product_identifier` | string | SKU-88014 | `validated` | The join to catalogue, ordering and stock records. |
| `location_code` | string | as printed on the label | `validated` | The bin or bay a unit sits in, which is the field that distinguishes a warehouse record from every other SKU-bearing document in the slice. |
| `exception` | string | as written on the report | `llm_supported` | Damages, shorts and mis-picks are described in free text and their cause is the point of the record. |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.3, §3.5):

- warehouse language ('goods in' | 'put away' | 'pick list' | 'pallet' | 'bay' | 'bin location' | 'dispatch note') co-occurring with a facility name
- a location-code pattern co-occurring with a product identifier and a quantity, which is the structure unique to this domain
- a spreadsheet whose column headers pair a location code with a product identifier — §2.9: “Spreadsheets such as XLSX, XLS, CSV, TSV, ODS, and Numbers exports should yield workbook or file metadata, sheet names, column headers, visible cell values, table-like regions, formulas only when useful, and dates or identifiers from labeled cells.”

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- a photographed damage report from the dock
- an unlabeled export whose operation class must be read from its columns
- distinguishing a warehouse cycle count from a retail stock take when the facility is also a selling location

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10):

- a SKU column
- a location code, whose shape collides with references, part numbers and postal codes
- a facility name
- a quantity

### Work types

`goods received note`, `put-away record`, `pick list`, `packing record`, `dispatch note`, `cycle count`, `damage report`, `productivity report`

### Grouping reasons (§4)

- one facility's records for one period
- one receipt from goods in to put-away
- one exception and the records that explain it

### Template (§5)

`facility → operation class → period`

Time first: **no**

§5.5: “a parent dimension should provide the context required to understand the child” — a pick list is meaningless without the facility and periods only sort within a class. Time sits last: “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders.”. §5.9's warning is live here because the natural instinct is a folder per day, which would produce exactly what it describes: “It should warn when a level produces only one child, repeats a concept already expressed in the parent, creates excessive depth, or creates a large number of tiny folders.”

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| retail.stocktake | a warehouse count and a store count are the same document at different nodes. The separating signal is whether the location is a selling location; a bin location says it is not | §3.9: “Topic answers what a file is about, while purpose answers what the file was for.” |
| log.shipment | the dispatch note ends the warehouse's involvement and begins the carrier's. The reference is shared and the domains are not | §3.8: “The system must separate roles that happen to contain the same entity type.” |
| retail.supplier-order | the goods received note closes the order and opens the warehouse record; it genuinely belongs to both | §3.11: “One file may hold facts from more than one domain without losing information.” |

### Sensitivity

`none` — Warehouse records concern goods and locations. None of §8.4's named categories is routine. Productivity reports naming individuals are the exception and §8.4's classification is evidence-backed and revisable per file. No handling class is set; that is P7's.

---

## `log.last-mile-pod` — Last-mile delivery and proof of delivery

The doorstep record — a photograph, a signature and a timestamp that together prove a parcel arrived where it was meant to.

**Provenance:** **inference** — extends a design-named domain or template situation; the cite supports the extension, not the whole entry

**Cite:** Extends the design-named Photos domain — §3.11: “Photos may use capture year, event, location, people, camera information, and media type.” — into an evidential capture domain, and relies on §5.5's exception: “Photos and capture-based media are the major exception: time often belongs first because capture date is a defining aspect of the material.”

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `capture_time` | date | as recorded in EXIF | `direct` | §3.13: “A direct fact was read from a reliable and explicit source, such as a content hash, EXIF timestamp, document title, or labeled form field.” — an EXIF timestamp is the design's own example. Here it is not metadata about the record, it IS the record: a proof of delivery with no time proves nothing. §2.6: “Camera EXIF, GPS, and capture time can support deterministic photo-event proposals.” |
| `consignment_reference` | string | as printed on the label in frame | `validated` | §3.5's model: the reference is a fact only “when the engine finds a course-code pattern together with academic context”. Frequently recoverable only by OCR of a label in the photograph, which is §2.7's case exactly: “A screenshot is always a screenshot of something” |
| `delivery_location` | string | as recorded by the device | `validated` | Where the capture happened, which is the second half of the proof. §2.6: “Camera EXIF, GPS, and capture time can support deterministic photo-event proposals.” |
| `delivery_outcome` | string | delivered to neighbour | `validated` | Delivered, left in a safe place, handed to a neighbour, refused, not in — a labeled outcome on every scanner, and the field that decides whether a claim succeeds. |
| `gps` | string | as recorded in EXIF or by the device | `direct` | The evidential anchor and the sensitivity in one field. |
| `route_and_date` | string | as recorded on the manifest | `validated` | The join back to dispatch, and what makes a single capture retrievable at all. |
| `media_type` | string | photograph | `validated` | §3.11's Photos schema names media type. §2.6 requires it be earned: “the system must not mistake the absence of EXIF for proof that an image is a screenshot” |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.3, §3.5):

- an image whose EXIF carries a capture time and GPS, in a set whose captures form a contiguous run across one day along a movement path — §2.6: “Camera EXIF, GPS, and capture time can support deterministic photo-event proposals.”
- OCR of a consignment label inside the frame that matches a consignment reference held in a shipment or manifest file — §2.7 is the route in: “A screenshot is always a screenshot of something”
- a scanner export pairing a labeled consignment reference, an outcome and a timestamp, whose timestamps match an image set's EXIF

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- a capture with no readable label and no scanner export, where only the content shows it is a doorstep photograph
- a set stripped of metadata by a messaging app, where §2.6's warning bites: “the system must not mistake the absence of EXIF for proof that an image is a screenshot”
- distinguishing a proof-of-delivery capture from a damage-claim capture taken at the same door minutes apart

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10):

- the absence of EXIF — §2.6: “the system must not mistake the absence of EXIF for proof that an image is a screenshot”
- OCR text density — §2.6: “OCR text density is also not a reliable screenshot detector because receipts, document scans, whiteboards, and photographs of pages can all contain dense text.”
- GPS alone, which places a capture and says nothing about why it was taken
- a consignment reference read from a partially occluded label; a misread digit sends the proof to the wrong parcel

### Work types

`proof-of-delivery photograph`, `signature capture`, `scanner event export`, `safe-place record`, `non-delivery record`, `damage or claim capture`

### Grouping reasons (§4)

- one delivery round — one device, one day, one contiguous run of captures along a path
- one consignment's captures across attempts
- one claim and the captures that answer it

### Template (§5)

`capture date → route → consignment`

Time first: **yes**

TIME FIRST, and it is §5.5's exception applied to genuinely capture-based media: “Photos and capture-based media are the major exception: time often belongs first because capture date is a defining aspect of the material.”. Three things force it. The capture timestamp is the evidential content — a proof of delivery exists to say when — not an attribute of some other subject. The consignment reference is frequently unrecoverable from the image itself, so a consignment-first template would leave most files unplaceable, which §5.9's live feedback would expose immediately. And §2.6 supplies capture time as a direct fact while everything else here needs OCR or the model, so the leading dimension is the one the engine can actually populate. Depot does not sit above the date because a device belongs to a route and a route to a day.

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| log.route-dispatch | the manifest plans the stops and the captures evidence them; both are keyed on the same date and route and neither should absorb the other | §3.11: “One file may hold facts from more than one domain without losing information.” |
| cons.progress-photos | both are geotagged, time-clustered photograph sets taken during a working day. The separating signal is movement: a delivery run's GPS traces a path, a site set's clusters at a point | §2.6: “The system should therefore use a hierarchy of signals: camera EXIF is strong photo evidence; capture time, GPS, and sensor-shaped dimensions reinforce it; exact display resolutions, PNG format, and software metadata may support a screenshot hypothesis; conflicting signals should lead to abstention rather than an invented classification.” |
| log.shipment | the consignment note is the contract and the capture is the discharge of it; they share a reference and nothing else | §3.9: “Topic answers what a file is about, while purpose answers what the file was for.” |

### Sensitivity

`potentially_sensitive` — §2.9's phrase “while treating addresses and message content as potentially sensitive” only. Every capture is a photograph of a private home's door with GPS attached, frequently including a signature and sometimes a person. §8.4 names GPS metadata in “identity documents, account statements, tax records, medical information, legal records, credentials, private correspondence, GPS metadata, employment materials, and educational records”, and a delivery round's captures together are a map of where a named driver was all day. §8.4 requires privacy policy to be enforced before content reaches any model, which is exactly the constraint on the OCR-and-model route this domain depends on. The handling class is P7's and is not set.

---

## `util.metering-billing` — Utility metering and billing operations

Readings taken from a meter at a premises and the bills calculated from them — the supplier's side of a utility account.

**Provenance:** **inference** — extends a design-named domain or template situation; the cite supports the extension, not the whole entry

**Cite:** Extends §3.11's Finance schema “Finance files may use institution, account type, tax year, and record type.” to the operational side: the institution is the supplier, the account is the supply point, and the record type is a reading rather than a statement

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `supply_point` | string | as printed on the bill | `validated` | The metered premises, identified by the network's own supply-point identifier. §3.5's model: a fact only “when the engine finds a course-code pattern together with academic context”, the corroborating context being metering language. Identifier schemes are jurisdiction-specific and none is named here. |
| `meter_identifier` | string | as printed on the meter | `validated` | §3.8: “The system must separate roles that happen to contain the same entity type.” — the supply point, the meter fitted to it and the account billed for it are three identifiers that change independently and are routinely conflated. |
| `supplier` | string | as named on the bill | `validated` | §3.11 names institution as a Finance field; here it is the energy or water supplier, distinct from the network operator and from the metering agent. |
| `reading` | string | as recorded | `direct` | §3.13: “A direct fact was read from a reliable and explicit source, such as a content hash, EXIF timestamp, document title, or labeled form field.” — a labeled field or an OCR of a meter face. This catalogue holds no value. |
| `reading_type` | string | actual | `validated` | Actual, estimated, customer-supplied and smart-read differ in reliability, and a bill built on an estimate is the single most disputed artefact in the domain. |
| `billing_period` | date range | 2026-07-01 to 2026-09-30 | `direct` | A labeled field. §3.10's explicit-regex path only: “The product must not use fuzzy date parsing because file names and documents frequently contain numbers that look like years but are course identifiers, version numbers, build numbers, ZIP codes, or other unrelated values.” |
| `tariff` | string | as named on the bill | `llm_supported` | Tariff names and structures are commercial and jurisdiction-specific and must be read from prose. |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.3, §3.5):

- metering language ('meter reading' | 'supply point' | 'units consumed' | 'standing charge' | 'estimated reading' | 'tariff') co-occurring with a supplier name and a premises address
- a supply-point or meter identifier pattern co-occurring with a labeled billing period and a reading
- a reading photograph whose OCR yields a digit sequence matching a meter identifier held in a bill in the same folder — §2.7 is the route in: “A screenshot is always a screenshot of something”

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- a photographed meter face where the register and the serial must be told apart
- a bill whose tariff and its change must be read from prose
- distinguishing a supplier's bill from a network operator's charge for the same supply point

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10):

- a long digit string — a meter serial, a supply-point identifier, an account number and a reading are all digit strings on one page
- a supplier name, which appears as supplier, as a previous supplier, as a network operator and as a merely cited company
- a premises address
- a currency amount

### Work types

`bill`, `meter reading record`, `reading photograph`, `consumption statement`, `tariff change notice`, `supplier switch record`, `dispute correspondence`

### Grouping reasons (§4)

- one supply point across suppliers and years
- one billing period's bill and the readings behind it
- one dispute and the readings and bills it turns on

### Template (§5)

`premises → supply point → billing period`

Time first: **no**

§5.5: “a parent dimension should provide the context required to understand the child” — a reading is meaningless without the meter and a meter without the premises. Premises leads rather than supplier because suppliers change and the metered building does not, which is the same reasoning that puts property above tenancy elsewhere in this slice. Period sits last: “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders.”

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| fin.financial-records | THE BOUNDARY. A utility bill is an operational document about consumption at a premises and an accounting record of a payable. The finance slice's claim is on the payment; this domain's claim is on the reading and the supply point, which no accounting record carries | §3.11: “One file may hold facts from more than one domain without losing information.” |
| prop.tenancy | meter readings at check-in and check-out are tenancy documents and metering records at once, and §3.11 keeps both fact sets | §3.11: “One file may hold facts from more than one domain without losing information.” |
| energy.renewable-generation | a generation meter and a consumption meter are both meters at one premises with different registers; conflating them makes an export look like a supply | §4.8: “that each fact or label belongs to an allowed domain schema” |
| pers.utilities | the same bill from opposite sides: the household slice holds the customer's copy, this domain holds the supplier's supply point and reading. A householder's corpus will only ever contain the first | §3.8: “The system must separate roles that happen to contain the same entity type.” |

### Sensitivity

`potentially_sensitive` — §2.9's phrase “while treating addresses and message content as potentially sensitive” only. A metering record ties a named account holder to a premises and to a consumption pattern that reveals occupancy, and the bills are account statements — §8.4 names account statements in “identity documents, account statements, tax records, medical information, legal records, credentials, private correspondence, GPS metadata, employment materials, and educational records”. §3.15's direction applies to the billing half: “Finance, identity, medical, and legal material should be implemented first as safety domains, meaning the system detects and protects them before any cloud or automated placement decision is allowed.” The handling class is P7's and is not set here.

---

## `energy.renewable-generation` — Renewable generation records

What an installation produced and what it earned — commissioning evidence, generation and export readings, performance data and incentive claims.

**Provenance:** **proposal** — new — the design does not name this domain, and nothing here is asserted as the design's

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `installation` | string | Bakers Lane roof array | `validated` | The generating asset. It is the durable subject: owners, suppliers and tariffs change and the array does not. |
| `technology` | string | solar photovoltaic | `validated` | What the asset is, which decides what performance data means and what commissioning evidence exists. |
| `generation_meter_identifier` | string | as printed on the meter | `validated` | §3.5's model: a fact only “when the engine finds a course-code pattern together with academic context”. §3.8 keeps it apart from the consumption meter at the same premises: “The system must separate roles that happen to contain the same entity type.” |
| `capacity_rating` | string | as stated on the commissioning certificate | `direct` | A labeled field. This catalogue holds no figure; ratings are data, not thresholds. |
| `reporting_period` | date range | 2026-04-01 to 2027-03-31 | `direct` | §3.13: “A direct fact was read from a reliable and explicit source, such as a content hash, EXIF timestamp, document title, or labeled form field.” Generation is reported and claimed by period. §3.10's explicit-regex path only: “The product must not use fuzzy date parsing because file names and documents frequently contain numbers that look like years but are course identifiers, version numbers, build numbers, ZIP codes, or other unrelated values.” |
| `scheme_registration` | string | as issued by the scheme | `validated` | Incentive and certification schemes are jurisdiction-defined and none is named here; the registration is what makes a claim payable. |
| `performance_note` | string | as written in the report | `llm_supported` | Underperformance and its diagnosis are prose. §3.5: “It can only propose facts that belong to the active domain schema, and it must cite exact supporting evidence already extracted from the file.” |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.3, §3.5):

- generation language ('generation meter' | 'export meter' | 'kilowatt-hours generated' | 'commissioning certificate' | 'inverter' | 'yield') co-occurring with an installation or site name
- a labeled generation-meter identifier co-occurring with a reporting period and a reading
- a monitoring export whose column headers pair a timestamp with a generation figure — §2.9: “Spreadsheets such as XLSX, XLS, CSV, TSV, ODS, and Numbers exports should yield workbook or file metadata, sheet names, column headers, visible cell values, table-like regions, formulas only when useful, and dates or identifiers from labeled cells.”

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- a photographed generation meter face, where the register and the serial must be told apart
- a performance report whose diagnosis must be read
- distinguishing a generation record from a consumption record at a premises that has both

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10):

- a long digit string — meter serials, scheme registrations and readings all share the shape
- a premises address
- a technology word such as 'solar', which appears in quotations, marketing and planning documents for the same site
- an energy-unit figure

### Work types

`commissioning certificate`, `generation meter reading`, `export statement`, `monitoring export`, `incentive claim`, `performance report`, `maintenance record`

### Grouping reasons (§4)

- one installation across its whole life
- one reporting period's readings and the claim built from them
- one performance investigation across monitoring data and maintenance records

### Template (§5)

`installation → record class → reporting period`

Time first: **no**

NOT time-first despite being a time-series domain, because the series is generated data and not capture-based media: “Photos and capture-based media are the major exception: time often belongs first because capture date is a defining aspect of the material.” does not reach it. §5.5's “a parent dimension should provide the context required to understand the child” puts the installation first, since a yield figure means nothing without the asset that produced it, and the period last so that one array's history stays in one place — “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders.”

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| util.metering-billing | generation and consumption meters sit at one premises with different registers. Conflating them turns an export into a supply, which is a wrong number rather than a misfiled document | §4.8: “that each fact or label belongs to an allowed domain schema” |
| energy.grid-connection | the connection agreement permits the export and the generation record measures it. The separating signal is whether the document is an agreement with a network operator or a reading | §3.9: “Topic answers what a file is about, while purpose answers what the file was for.” |
| trade.compliance-certificate | the commissioning certificate is an installer's certificate about an installation, which is exactly the compliance-certificate domain; it doubles and §3.11 keeps both fact sets | §3.11: “One file may hold facts from more than one domain without losing information.” |

### Sensitivity

`none` — Generation records concern an asset's output. Where the asset is a private dwelling the records tie an address to a consumption and occupancy pattern, and §8.4's classification being evidence-backed and revisable covers that per file. As a domain, none of §8.4's named categories is routine. No handling class is set; that is P7's.

---

## `energy.grid-connection` — Grid connection and network agreements

Getting an installation connected to a network and keeping it connected — applications, offers, agreements, energisation evidence and compliance with the operator's terms.

**Provenance:** **proposal** — new — the design does not name this domain, and nothing here is asserted as the design's

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `site` | string | Bakers Lane | `validated` | The connected premises or development. Connections attach to a place and transfer with it. |
| `network_operator` | string | as named on the offer | `validated` | §3.8: “The system must separate roles that happen to contain the same entity type.” — the network operator, the supplier, the metering agent and the connecting customer are four parties and a connection offer names all four. |
| `connection_reference` | string | as issued by the operator | `validated` | §3.5's model: a fact only “when the engine finds a course-code pattern together with academic context”, the corroborating context being connection language. |
| `connection_stage` | string | offer accepted | `validated` | Enquiry, budget estimate, formal offer, acceptance, works, energisation — a sequence with dated obligations and expiring offers. |
| `connection_capacity` | string | as stated on the offer | `direct` | A labeled field. This catalogue holds no figure. |
| `offer_expiry` | date | as stated on the offer | `direct` | §3.13: “A direct fact was read from a reliable and explicit source, such as a content hash, EXIF timestamp, document title, or labeled form field.” A connection offer lapses, which makes the date load-bearing rather than incidental. |
| `technical_condition` | string | as attached to the agreement | `llm_supported` | Operator conditions are numbered prose obligations. §3.5: “It can only propose facts that belong to the active domain schema, and it must cite exact supporting evidence already extracted from the file.” |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.3, §3.5):

- connection language ('connection offer' | 'point of connection' | 'network operator' | 'energisation' | 'reinforcement works' | 'export limitation') co-occurring with a site name
- an offer structure: an operator block, a connection reference, a labeled capacity and a labeled offer expiry
- a connection reference appearing in an offer and its acceptance, which builds the chain deterministically

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- correspondence about a connection that never restates the reference
- a technical schedule whose obligations must be read
- distinguishing a connection agreement from a supply contract, which name the same site and different parties

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10):

- an operator's name — §4.9's warning transfers: “A university name alone should not create a group because Columbia can appear as an authoring school, course provider, target institution, employer, research venue, or merely a cited organization.”
- a connection reference
- a capacity figure
- a site address

### Work types

`connection enquiry`, `budget estimate`, `connection offer`, `acceptance`, `connection agreement`, `energisation certificate`, `technical schedule`, `compliance correspondence`

### Grouping reasons (§4)

- one connection from enquiry to energisation
- one site's connections across generation and demand
- one operator's offers across a developer's sites

### Template (§5)

`site → connection → document type`

Time first: **no**

§5.5: “a parent dimension should provide the context required to understand the child” — a technical schedule is meaningless without the connection and a connection without the site. Time does not lead even though offers expire: “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders.”, and a connection's whole chain must sit together to be usable.

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| cons.building-control | both are authority-shaped permissions attached to a site with reference numbers and conditions, and both are consulted during a development. The separating signal is whether the issuer is a public authority or a network operator | §3.8: “The system must separate roles that happen to contain the same entity type.” |
| energy.renewable-generation | the connection permits the export and the generation record measures it | §3.9: “Topic answers what a file is about, while purpose answers what the file was for.” |
| prop.development-appraisal | a connection cost is an appraisal input and a connection offer is the evidence for it; the offer belongs here and the model belongs there | §3.11: “One file may hold facts from more than one domain without losing information.” |

### Sensitivity

`none` — Connection records concern infrastructure and companies. None of §8.4's named categories is routine. No handling class is set here; that is P7's.

---

## `energy.oil-gas-ops` — Oil and gas operations

Records generated by operating a well or field — drilling and completion reports, production allocation, permits, and the daily operational log.

**Provenance:** **proposal** — new — the design does not name this domain, and nothing here is asserted as the design's

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `asset_or_field` | string | as named in the operating agreement | `validated` | The field or facility. It is the durable parent that outlives operators, licences and partners. |
| `well_or_facility_identifier` | string | as issued by the regulator or operator | `validated` | §3.5's model: a fact only “when the engine finds a course-code pattern together with academic context”, the corroborating context being operations language. Well-naming conventions are jurisdiction and operator specific and none is named here. |
| `operator` | string | as named on the report | `validated` | §3.8: “The system must separate roles that happen to contain the same entity type.” — the operator, the non-operating partners, the regulator and the service contractors are four roles on one report. |
| `report_class` | string | daily drilling report | `validated` | Drilling, completion, production, well intervention, environmental and permit records are distinct classes with distinct regulators. |
| `reporting_period` | date range | 2026-06-01 to 2026-06-30 | `direct` | §3.13: “A direct fact was read from a reliable and explicit source, such as a content hash, EXIF timestamp, document title, or labeled form field.” Production is allocated and reported by period. §3.10's explicit-regex path only. |
| `production_figures` | string | as tabulated in the report | `direct` | §2.9: “Spreadsheets such as XLSX, XLS, CSV, TSV, ODS, and Numbers exports should yield workbook or file metadata, sheet names, column headers, visible cell values, table-like regions, formulas only when useful, and dates or identifiers from labeled cells.” — allocation lives in cells. This catalogue holds no figure. |
| `operational_event` | string | as described in the report | `llm_supported` | Non-productive time and its cause are narrative prose and are the point of a daily report. §3.13: “An LLM-supported fact was proposed by a language model from a bounded evidence packet, cited exact supporting text or metadata, and passed deterministic validation.” |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.3, §3.5):

- operations language ('daily drilling report' | 'wellbore' | 'completion report' | 'production allocation' | 'non-productive time' | 'workover') co-occurring with a well or facility identifier
- a well-identifier pattern co-occurring with a labeled operator and a labeled reporting date
- an allocation structure pairing a labeled field or well with volume columns by period

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- a scanned historic report whose well identifier follows a superseded convention
- a narrative report whose operational event must be read to be classified
- distinguishing an operator's internal report from a regulatory submission of the same data

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10):

- a well or facility identifier — jurisdiction and operator specific, and shape-colliding with equipment tags and document references
- an operator's name, which appears as operator, partner, contractor and merely cited company
- a volume figure
- a field name that is also a place name — §3.7: “It should use word-boundary matching rather than substring matching.”

### Work types

`daily drilling report`, `completion report`, `production allocation`, `well intervention report`, `permit`, `environmental report`, `joint-venture reporting`

### Grouping reasons (§4)

- one well from spud to completion
- one field's production for one period
- one intervention and the reports around it

### Template (§5)

`asset or field → well or facility → report class`

Time first: **no**

§5.5: “a parent dimension should provide the context required to understand the child” — a daily report is meaningless without the well and a well without the field. Time does not lead despite the daily reporting cadence, because a well's whole record must sit together to be usable: “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders.”

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| mining.ops | structurally the same domain at a different asset type: an extraction operation reporting daily against a permitted site. The separating signal is the asset and the regulator, not the document shape | §4.8: “that each fact or label belongs to an allowed domain schema” |
| corp.regulatory-filings | an operator's internal report and the regulatory submission built from it carry the same figures for different audiences | §3.9: “Topic answers what a file is about, while purpose answers what the file was for.” |
| cons.project | construction of a facility is a project with a contract; operating it afterwards is this domain | §3.9: “Topic answers what a file is about, while purpose answers what the file was for.” |
| mfg.production-record | a production record in manufacturing counts units made against a work order; here it allocates volumes lifted against a well. One word, two objects, and a validator that accepts either for the other is accepting a wrong number | §4.8: “that each fact or label belongs to an allowed domain schema” |

### Sensitivity

`none` — Operations records concern assets, volumes and companies. None of §8.4's named categories is routine. No handling class is set here; that is P7's.

### Open question — Joseph's call, unresolved

> Is this domain worth a template at all? It is the widest gap between the design's stated corpus — §8.4's “identity documents, account statements, tax records, medical information, legal records, credentials, private correspondence, GPS metadata, employment materials, and educational records” — and this catalogue's coverage: a personal filesystem will almost never hold a drilling report, and the recognisers are jurisdiction and operator specific to a degree that no gazetteer will fix. §3.15's own provision covers it: “Other domains remain placeholders until user demand and corpus evidence justify detailed templates.” Joseph decides whether this entry, mining, fisheries and forestry ship as schemas without templates, or not at all.

---

## `mining.ops` — Mining and quarrying operations

Records generated by extracting material from a permitted site — production and haulage records, survey and grade data, permits and restoration obligations.

**Provenance:** **proposal** — new — the design does not name this domain, and nothing here is asserted as the design's

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `site_or_mine` | string | as named in the permit | `validated` | The permitted extraction site. It is the durable parent and the unit a regulator inspects. |
| `permit_reference` | string | as issued by the authority | `validated` | §3.5's model: a fact only “when the engine finds a course-code pattern together with academic context”, the corroborating context being extraction-permit language. Permit regimes are jurisdiction-defined and none is named here. |
| `operator` | string | as named on the permit | `validated` | §3.8: “The system must separate roles that happen to contain the same entity type.” — the operator, the landowner, the mineral-rights holder and the regulator are four roles on one permit. |
| `record_class` | string | production record | `validated` | Production, haulage, survey, grade, blasting, environmental monitoring and restoration are distinct classes with distinct obligations. |
| `reporting_period` | date range | 2026-06-01 to 2026-06-30 | `direct` | §3.13: “A direct fact was read from a reliable and explicit source, such as a content hash, EXIF timestamp, document title, or labeled form field.” §3.10's explicit-regex path only. |
| `volumes_or_tonnage` | string | as tabulated in the record | `direct` | §2.9: “Spreadsheets such as XLSX, XLS, CSV, TSV, ODS, and Numbers exports should yield workbook or file metadata, sheet names, column headers, visible cell values, table-like regions, formulas only when useful, and dates or identifiers from labeled cells.” — production lives in cells. This catalogue holds no figure. |
| `environmental_obligation` | string | as stated in the permit condition | `llm_supported` | Restoration and monitoring obligations are numbered prose conditions and must be read. §3.5: “It can only propose facts that belong to the active domain schema, and it must cite exact supporting evidence already extracted from the file.” |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.3, §3.5):

- extraction language ('extraction' | 'overburden' | 'haulage' | 'weighbridge' | 'blast record' | 'restoration' | 'mineral permission') co-occurring with a site name
- a weighbridge or haulage record structure pairing a labeled load with a date and a destination
- a permit reference co-occurring with an authority block and a site name

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- a scanned historic permit whose regime and conditions must be read
- a survey or grade report whose subject must be inferred from its data
- distinguishing an internal production record from the regulatory return built from it

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10):

- a tonnage figure
- a permit reference, jurisdiction-specific and shape-colliding
- a site name that is also a place name — §3.7: “It should use word-boundary matching rather than substring matching.”
- an authority name — §4.9: “A university name alone should not create a group because Columbia can appear as an authoring school, course provider, target institution, employer, research venue, or merely a cited organization.”

### Work types

`production record`, `weighbridge and haulage record`, `survey and grade report`, `blast record`, `permit`, `environmental monitoring`, `restoration plan`

### Grouping reasons (§4)

- one site's records for one reporting period
- one permit and every condition-discharge record under it
- one restoration obligation across its evidence

### Template (§5)

`site → record class → reporting period`

Time first: **no**

§5.5: “a parent dimension should provide the context required to understand the child” — a haulage record is meaningless without the site and periods only sort within a class. Time does not lead: “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders.”, and a site's permitted life spans decades.

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| energy.oil-gas-ops | structurally the same domain at a different asset type; the separating signal is the asset and the regulator | §4.8: “that each fact or label belongs to an allowed domain schema” |
| cons.building-control | both hold authority permissions with numbered conditions attached to land, and both are discharged by evidence | §3.9: “Topic answers what a file is about, while purpose answers what the file was for.” |
| log.warehouse-ops | a weighbridge record and a goods-in record are the same shape at different kinds of gate | §4.9: “when one high-frequency entity acts as the only bridge” |

### Sensitivity

`none` — Extraction records concern land, material and companies. None of §8.4's named categories is routine. No handling class is set here; that is P7's.

---

## `agri.farm-records` — Agriculture and farm records

Running land and livestock through a season — field and crop records, livestock movements and medicines, inputs, subsidy claims and assurance inspections.

**Provenance:** **proposal** — new — the design does not name this domain, and nothing here is asserted as the design's

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `holding` | string | as registered | `validated` | The farm business and its registered land. It is the parent everything else hangs from and it is what an inspection is against. |
| `field_or_parcel` | string | as identified in the land register | `validated` | §3.5's model: a parcel identifier is a fact only “when the engine finds a course-code pattern together with academic context”, the corroborating context being cropping or land language. Parcel identification schemes are jurisdiction-defined and none is named here. |
| `season_or_crop_year` | string | harvest 2026 | `validated` | The cropping cycle, which is the farm's own accounting and operational unit and rarely matches a calendar or tax year. |
| `enterprise` | string | combinable crops | `validated` | Which enterprise the record belongs to — cropping, livestock, dairy, forestry block, diversification — since a mixed farm's records are otherwise unnavigable. |
| `record_class` | string | spray record | `validated` | Field operations, input applications, livestock movements, medicine records, subsidy claims and assurance inspections are distinct obligations with distinct retention. |
| `application_or_movement_date` | date | 2026-05-02 | `direct` | §3.13: “A direct fact was read from a reliable and explicit source, such as a content hash, EXIF timestamp, document title, or labeled form field.” Statutory intervals run from it, which is what makes the date load-bearing. §3.10's explicit-regex path only: “The product must not use fuzzy date parsing because file names and documents frequently contain numbers that look like years but are course identifiers, version numbers, build numbers, ZIP codes, or other unrelated values.” |
| `input_or_medicine` | string | as recorded on the sheet | `llm_supported` | Product names and their approvals are jurisdiction-specific and are recorded as free text. §3.5: “it may extract only fields allowed by the relevant schema” |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.3, §3.5):

- farm-record language ('field record' | 'spray record' | 'application record' | 'movement record' | 'medicine book' | 'assurance inspection' | 'cropping plan') co-occurring with a holding or parcel identifier
- a parcel-identifier pattern co-occurring with a crop name and a season, which is the cropping triple
- a movement or medicine record pairing a labeled animal or batch identifier with a date and a holding

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- a photographed paper field book completed in a tractor cab
- an unlabeled spreadsheet whose record class must be read from its columns
- distinguishing a plan from the record of what was actually applied

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10):

- a parcel identifier, jurisdiction-specific and shape-colliding with references and grid codes
- a crop name, which appears in plans, orders, invoices, contracts and market reports
- a date
- a field name that is also a place name — §3.7: “It should use word-boundary matching rather than substring matching.”

### Work types

`cropping plan`, `field operation record`, `spray and input record`, `livestock movement record`, `medicine record`, `subsidy claim`, `assurance inspection report`, `yield record`

### Grouping reasons (§4)

- one holding's records for one season
- one parcel across seasons, which is what a rotation is
- one inspection and the records produced for it

### Template (§5)

`holding → season → enterprise`

Time first: **no**

§5.5: “a parent dimension should provide the context required to understand the child” — a spray record is meaningless without the season and the season without the holding. The season sits second and is the one place in this slice where a time-shaped dimension is genuinely a subject: a crop year is a closed production cycle, not a calendar convenience, so “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders.” is satisfied by naming it as a harvest rather than a year. Parcel sits below enterprise rather than above it because a mixed farm's records are otherwise unnavigable.

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| forest.records | a farm woodland block and a forestry compartment are the same land under two regimes with different cycles; the separating signal is whether the record follows a crop year or a rotation measured in decades | §4.8: “that each fact or label belongs to an allowed domain schema” |
| corp.regulatory-filings | a subsidy claim is a regulatory submission and a farm record; the claim's evidence is the farm's own field records | §3.9: “The documents are content-incoherent but purpose-coherent.” |
| hosp.food-safety | assurance schemes at the farm gate and food-safety records in the kitchen are the same idea at two ends of a supply chain, and both are checklist-shaped | §4.9: “when one high-frequency entity acts as the only bridge” |

### Sensitivity

`none` — Farm records concern land, crops and livestock. None of §8.4's named categories is routine. Where the holding is also the family home, an address and a subsidy payment record appear together, and §8.4's classification being evidence-backed and revisable covers that per file. No handling class is set; that is P7's.

---

## `fish.catch-records` — Fisheries and catch records

What a vessel caught, where, when and under what entitlement — logbooks, landing declarations, quota records and vessel compliance.

**Provenance:** **proposal** — new — the design does not name this domain, and nothing here is asserted as the design's

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `vessel` | string | as registered | `validated` | The fishing vessel. Entitlements, logbooks and landings all attach to it and it is the unit a regulator inspects. |
| `trip` | string | as numbered in the logbook | `validated` | One departure to one return. It is the operational unit and it is time-derived without being a date: §3.11's Photos schema names the analogous idea — “Photos may use capture year, event, location, people, camera information, and media type.” uses event as a dimension in its own right. |
| `fishing_area` | string | as declared in the logbook | `validated` | Where fishing took place, declared against a management area scheme that is jurisdiction-defined and is not named here. |
| `species_and_quantity` | string | as declared | `direct` | §2.3: “Tables matter because resumes, forms, applications, invoices, and administrative documents often place their most useful information in cells rather than body paragraphs.” — a logbook page is a table. This catalogue holds no quantity. |
| `trip_dates` | date range | 2026-06-02 to 2026-06-09 | `direct` | §3.13: “A direct fact was read from a reliable and explicit source, such as a content hash, EXIF timestamp, document title, or labeled form field.” §3.10's explicit-regex path only: “The product must not use fuzzy date parsing because file names and documents frequently contain numbers that look like years but are course identifiers, version numbers, build numbers, ZIP codes, or other unrelated values.” |
| `entitlement_reference` | string | as issued by the authority | `validated` | §3.5's model: a fact only “when the engine finds a course-code pattern together with academic context”, the corroborating context being fisheries-licensing language. |
| `landing_declaration` | string | as submitted | `llm_supported` | Declaration formats and their obligations are jurisdiction-specific and must be read. |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.3, §3.5):

- fisheries language ('logbook' | 'landing declaration' | 'catch composition' | 'fishing effort' | 'quota' | 'gear type') co-occurring with a vessel identifier
- a logbook structure pairing a labeled fishing area with species rows and a trip date range
- a vessel identifier co-occurring with a labeled entitlement or licence reference

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- a photographed paper logbook page completed at sea
- a declaration in a national format the gazetteer does not cover
- distinguishing a sales note from a landing declaration when both list the same species and weights

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10):

- a vessel identifier, jurisdiction-specific and shape-colliding with registration and reference numbers
- a species name
- an area code, whose shape collides with grid references, postal codes and commodity codes
- a date range

### Work types

`logbook page`, `landing declaration`, `sales note`, `quota record`, `entitlement or licence`, `gear record`, `inspection report`

### Grouping reasons (§4)

- one trip from departure to landing
- one vessel's trips in one quota period
- one inspection and the records produced for it

### Template (§5)

`vessel → trip → document type`

Time first: **no**

§5.5: “a parent dimension should provide the context required to understand the child” — a landing declaration is meaningless without the trip and a trip without the vessel. The trip level is time-derived but is not a date: it is a named operational event, which is how §3.11's Photos schema treats an event too. Time therefore never leads, and “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders.” is satisfied because the trip carries the time without the calendar fragmenting the vessel's record.

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| log.shipment | a landing feeds a consignment and the sales note and the consignment note describe the same fish to different parties | §3.8: “The system must separate roles that happen to contain the same entity type.” |
| agri.farm-records | both are primary-production domains with statutory record-keeping, cycle-shaped units and assurance inspections; the separating signal is the asset — a vessel or a holding | §4.8: “that each fact or label belongs to an allowed domain schema” |
| fleet.vehicle | a vessel is an asset with registration, inspection and maintenance records exactly like a vehicle, and the two domains share every record class except the catch | §3.11: “One file may hold facts from more than one domain without losing information.” |

### Sensitivity

`none` — Catch records concern a vessel and its catch. None of §8.4's named categories is routine. Crew records are employment materials and belong with the personnel domains where they are marked. No handling class is set here; that is P7's.

---

## `forest.records` — Forestry and woodland records

Managing woodland over decades — management plans, felling permissions, compartment records, harvesting and timber sales, and replanting obligations.

**Provenance:** **proposal** — new — the design does not name this domain, and nothing here is asserted as the design's

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `woodland` | string | as named in the management plan | `validated` | The managed property. Forestry's unit of ownership and the parent everything hangs from. |
| `compartment` | string | as identified in the plan | `validated` | §3.5's model: a compartment identifier is a fact only “when the engine finds a course-code pattern together with academic context”, the corroborating context being forestry language. It is the field that makes a stand record legible. |
| `operation_class` | string | felling | `validated` | Planting, thinning, felling, restocking, road building and pest control are distinct operations with distinct permissions. |
| `permission_reference` | string | as issued by the forestry authority | `validated` | Felling and management permissions are jurisdiction-defined and none is named here; the reference is what makes an operation lawful. |
| `operation_period` | date range | 2026-10-01 to 2027-02-28 | `direct` | §3.13: “A direct fact was read from a reliable and explicit source, such as a content hash, EXIF timestamp, document title, or labeled form field.” Operations are seasonally constrained, which is what makes the range a schema field. §3.10's explicit-regex path only. |
| `species_and_volume` | string | as recorded | `direct` | §2.9: “Spreadsheets such as XLSX, XLS, CSV, TSV, ODS, and Numbers exports should yield workbook or file metadata, sheet names, column headers, visible cell values, table-like regions, formulas only when useful, and dates or identifiers from labeled cells.” — timber records live in cells. This catalogue holds no volume. |
| `restocking_obligation` | string | as stated in the permission condition | `llm_supported` | Replanting conditions are numbered prose obligations that bind for years. §3.5: “It can only propose facts that belong to the active domain schema, and it must cite exact supporting evidence already extracted from the file.” |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.3, §3.5):

- forestry language ('felling licence' | 'management plan' | 'compartment' | 'restocking' | 'thinning' | 'standing sale' | 'timber measurement') co-occurring with a woodland name
- a compartment identifier co-occurring with a species and an area or volume figure
- a permission reference co-occurring with an authority block and a woodland name

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- a scanned historic management plan whose compartment scheme has since been renumbered
- a timber sale contract that must be distinguished from a harvesting contract
- a restocking condition whose obligation must be read to be tracked

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10):

- a compartment identifier, whose shape collides with parcel, plot and grid references
- a species name
- a woodland name that is also a place name — §3.7: “It should use word-boundary matching rather than substring matching.”
- an area or volume figure

### Work types

`management plan`, `felling permission`, `compartment record`, `harvesting contract`, `timber sale record`, `restocking record`, `inspection or certification audit`

### Grouping reasons (§4)

- one woodland's management plan and the operations under it
- one felling permission and its restocking evidence, which may span a decade
- one compartment across its rotation

### Template (§5)

`woodland → compartment → operation class`

Time first: **no**

§5.5: “a parent dimension should provide the context required to understand the child” — a restocking record is meaningless without the compartment and a compartment without the woodland. Time never leads and this is the clearest case in the slice: forestry's cycles are measured in decades and a permission granted in one year is discharged in another, so “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders.” applies with unusual force.

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| agri.farm-records | a farm woodland block sits in both, under a crop-year regime in one and a rotation regime in the other; the separating signal is the cycle the records follow | §4.8: “that each fact or label belongs to an allowed domain schema” |
| cons.building-control | both are authority permissions with numbered conditions attached to land and discharged by later evidence | §3.9: “Topic answers what a file is about, while purpose answers what the file was for.” |
| prop.sale-purchase | woodland is bought and sold as land, and the management plan and permissions become pack members in that transaction | §3.9: “The documents are content-incoherent but purpose-coherent.” |

### Sensitivity

`none` — Forestry records concern land and timber. None of §8.4's named categories is routine. No handling class is set here; that is P7's.

---
