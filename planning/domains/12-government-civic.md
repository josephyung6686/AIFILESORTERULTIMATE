# Domain catalogue — government, public sector, education administration, nonprofit and civic life

Supercategory: `government-civic`  
Slice: 12  
Entries: 44 — 0 design, 2 inference, 42 proposal  
Contract: [`_CONTRACT.md`](_CONTRACT.md) · Source of truth: [`00-database-agent-product-design.md`](../00-database-agent-product-design.md)

## How to read this file

- **Double quotes are verbatim quotations** from the source of truth and nothing else. Every one is checked by a literal substring test at build time; a quotation that does not appear in the source fails the build. Where a claim is mine rather than the design's it is written as plain prose with no quote marks.
- **Single quotes are pattern literals** — tokens a recogniser looks for in a document — following the convention in the contract's own worked example.
- `reliability_ceiling` uses §3.13's six states only. `direct` means a labeled field, a document title or explicit metadata. `validated` means a rule found a pattern **and** passed a context check, so every `validated` field has a matching `recognition.deterministic` line that could actually confirm it. `llm_supported` means the value needs language interpretation and cannot be produced without the model route. `possible` appears on `jurisdiction` fields throughout this slice, and that is a finding rather than laziness — see below.
- `sensitivity` is §2.9's phrase `potentially sensitive` and nothing more. No handling class is assigned anywhere in this file; handling classes are P7's (§8.4).
- No thresholds, no scores, no counts, no retention periods. Digits appear only inside `example` values, which are data in the same way the contract's own `BUSIB 4300` is.
- **No reference number, form number, statute citation, agency acronym or programme name is asserted anywhere in this file.** Where a real corpus would carry one, the `example` describes the string's role instead — *the case reference as printed on the document, retained verbatim*. A plausible-looking invented reference in a shipped catalogue would be worse than an empty field, and this slice is the one where the temptation is strongest.

## Eight findings that apply to the whole slice

**1 — Jurisdiction is the defining hazard here, and it is sharper than for tax or law.** For finance and legal practice, jurisdiction changes vocabulary and thresholds around objects that mostly still exist everywhere: a bank statement is a bank statement. For government it changes the objects. Which tier of government performs a function, whether a function exists at all, what its documents are called, which of them are public, and how they are numbered are all set by each polity — and often differ between regions inside one polity. A two-tier local system and a single-tier one do not produce the same papers with different names; they produce different papers. So this slice is written **functionally** everywhere it can be: *a permit application to a local planning authority*, not a named agency; *the statutory return as named*, not a form number; *a body with rule-making power*, not a regulator. Five entries additionally carry an explicit `jurisdiction` field — the branch root, intergovernmental agreements, elections, defence and veterans, and nonprofit governance — always at ceiling `possible`, because a document assumes its jurisdiction rather than stating it.

Where functional writing does **not** reach, the entry says so and raises an `open_question`. Those places are: legislative stage and session vocabulary (`gov.legislative-record`), procurement procedure types (`gov.procurement-tender`), permit types (`gov.permit-licensing-authority`), social-care case types (`gov.social-services-casework`), protective markings on diplomatic and defence material (`gov.diplomatic-consular-record`), and the scope question itself on the branch root (`gov.public-authority-record`). In each of them the field is an open enum with no allow-list, which is precisely what §3.6's validator has nothing to check against. **The cost of neutrality is that no gazetteer can be built.** Almost every `recognition.deterministic` line in this slice pairs a *generic* context term with a *structural* signal, because the one thing that would make these recognisers strong — a list of real authority names, form numbers and reference formats — cannot be written until Joseph fixes the scope.

**2 — The citizen and the administrator hold the same bytes, and no field on the page separates them.** A planning application, a permit certificate, a consultation response, a grant monitoring report and an information-request response are byte-identical in the applicant's folder and in the authority's case file. Three things do distinguish the two corpora and none of them is a document fact:

- **Internal apparatus.** An authority's file additionally contains material that never leaves the building — case-officer assessments, consultee responses, delegated-decision reports, panel notes, redaction working copies. Its *presence* is a strong signal; its *absence* is not, because a partial export looks exactly like a citizen's folder.
- **Corpus shape.** An authority holds many cases with few documents each; a citizen holds one case with many documents. That is a §4 observation about the neighbourhood, not a §3 fact about a file.
- **Arrival pattern.** Authority copies arrive as a batch export from a case-management system; citizen copies arrive one at a time over months.

All three mean the product would be **inferring the user's institutional role from the shape of their filesystem**. This catalogue does not decide whether it may. Three entries carry an explicit `record_side` field at ceiling `llm_supported` — `gov.public-authority-record`, `gov.planning-application` and `gov.public-records-foi` — present so the product can be honest that it usually cannot fill it rather than because a rule could. The question is raised sharpest on `gov.planning-application` and `gov.public-consultation`. Meanwhile every affected entry names its counterpart in `collides_with` — `admin.licences-permits` for permits, `res.grant-proposal` for grants, `pers.home-tenure` for planning, `acad.accreditation-institutional` for accreditation — so that whichever way Joseph decides, both halves exist.

**3 — Nothing in this slice is `design` provenance, and that is the honest count.** The design names seven exemplar domains and none is governmental. §5.1's candidate top-level branches are "Academics, Applications, Research, Career, Personal Records, Finance and Administration, Photos and Captures, Code and Projects, and Media or Miscellaneous Personal Material". §5.7's template-library list covers "academic programs, university applications, recruiting processes, client engagements, research workflows, financial records, travel, legal matters, creative projects, software repositories, personal administration, and photo collections". Neither mentions government, civic life, the nonprofit sector or education administration. Two entries are marked `inference` because they extend §3.11's named academic schema — "Academic files may use school, term, course, instructor, and work type." — onto the institution's side of the same relationship. The other forty-two are `proposal`, which is what §3.15 anticipates: "Other domains remain placeholders until user demand and corpus evidence justify detailed templates."

**4 — The sensitivity marking splits, and the split is the finding.** Twenty-eight entries are `potentially_sensitive` and sixteen are `none`. Unlike the finance slice, where the whole supercategory sits inside one design sentence, this one genuinely divides: policy papers, legislative proceedings, procurement, contract awards, environmental regulation, land management, standards work and institutional governance are about subjects and organisations, while casework, registers, elections, donors, volunteers, membership and children's records are about identified people. The line is drawn at whether the domain's **ordinary** content names individuals and their circumstances, not at whether any file in it ever could.

**5 — A caseload is other people's records, and that is a scope question the catalogue must not answer.** `gov.constituent-casework` and `gov.social-services-casework` — and to a lesser degree `gov.professional-regulator`, `civic.trade-union` and `edadmin.school-district` — describe corpora made almost entirely of third parties' most sensitive circumstances, held under duties the product knows nothing about. The ordinary pipeline would extract, index, retain evidence for, and propose folder labels derived from all of it. A handling class would not answer this; the prior question is whether such corpora are in scope at all. It is raised as an `open_question` on both casework entries.

**6 — Three entries produce folder labels more disclosing than their contents.** A folder level named for a political campaign, a religious congregation or a trade union publishes something about the user to anything that lists the directory — a backup, a sync client, a screen-share — that the file inside would reveal only on opening. The product has no notion of a label being more revealing than what it holds. This is raised three times, on `civic.political-campaign`, `npo.religious-institution` and `civic.trade-union`, but **it is one decision, not three**.

**7 — `time_first` is `no` on all forty-four, and the near-misses are instructive.** §5.5 makes capture-based media the exception — "Photos and capture-based media are the major exception: time often belongs first because capture date is a defining aspect of the material." — and nothing in a public-administration slice is capture-based. Four entries look like exceptions and are not: a council meeting date, an election, an emergency incident and a legislative session all sit at or near the top of their template, but each is an **event or a structural container whose label happens to contain a date**, not a calendar bucket. §5.5's actual rule — "For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders." — is satisfied in every one of them. Six entries do carry a period or year as the **last** dimension — the branch root, transport, environmental regulation, public lands, fundraising and volunteering — because monitoring returns, superseded timetables, appeal results and rotas are genuinely serial and otherwise indistinguishable. A period as a leaf is not a period as a root.

**8 — Eleven folder levels in this slice cannot be filled by a rule, and each one says so.** §3.14 is explicit that templates use validated facts to create folder proposals. A policy area, a rule subject, a campaign name, a community group, a bargaining round, an electoral area and a consular or claim matter are all things a corpus contains and no pattern can confirm — they are proper nouns and prose subjects with no detectable shape and, for the electoral case, no shippable gazetteer for the reason finding 1 gives. The catalogue does not quietly promote them: each is marked `possible` or `llm_supported`, and each template that uses one as a level says in its `why` that the level should be offered only from an existing folder name or a user-confirmed label. §3.9's "Purpose may be supported strongly by an existing user-created folder name or explicit language in a form or portal." and §5.10's "A carefully curated existing folder should be treated as a strong expression of user intent." are what make that route legitimate rather than a workaround. Every other dimension in all forty-four templates is backed by a `direct` or `validated` field of the same name.

## What this slice deliberately does not own

- **Coursework and the student's side of education** — the education slice owns `acad.*`. `edadmin.*` here is the institution's own administration and defers on every seam, including `acad.accreditation-institutional`, which already models institutional accreditation from the institution's side.
- **The applicant side of research grants** — `res.grant-proposal` and `res.grant-reporting` own it. `gov.grant-programme-administration` is the funder's side, and `npo.grant-reporting-recipient` covers only the non-research recipient, which the catalogue flags as a seam that may not be clean.
- **The holder's copy of a licence** — `admin.licences-permits` owns it; `gov.permit-licensing-authority` is the issuer's side.
- **A nonprofit's finance records** — `biz.bookkeeping`, `corp.regulatory-filings`, `corp.business-formation` and `fin.charitable-giving` own them; `npo.governance` adds only the governance layer and says so.
- **Handling classes.** §8.4's "The system should classify data into handling classes before LLM escalation" is P7's work. Nothing here assigns one, including on social-services casework and constituent records, where the temptation is strongest.

## Index

| id | name | provenance | sensitivity | time first |
|---|---|---|---|---|
| `gov.public-authority-record` | Public authority records (branch root) | proposal | potentially sensitive | no |
| `gov.policy-development` | Policy development | proposal | none | no |
| `gov.legislative-record` | Legislative and parliamentary records | proposal | none | no |
| `gov.regulatory-rulemaking` | Regulatory rulemaking | proposal | none | no |
| `gov.public-consultation` | Public consultation exercises | proposal | potentially sensitive | no |
| `gov.intergovernmental-agreement` | Intergovernmental agreements | proposal | none | no |
| `gov.municipal-administration` | Municipal and local authority administration | proposal | none | no |
| `gov.grant-programme-administration` | Grant programme administration (funder side) | proposal | potentially sensitive | no |
| `gov.procurement-tender` | Public procurement and tendering | proposal | none | no |
| `gov.contract-award-record` | Public contract award and contract management records | proposal | none | no |
| `gov.planning-application` | Planning, zoning and development applications | proposal | potentially sensitive | no |
| `gov.permit-licensing-authority` | Permits and licensing (issuing authority side) | proposal | potentially sensitive | no |
| `gov.public-records-foi` | Public records access and information requests | proposal | potentially sensitive | no |
| `gov.census-statistical-programme` | Census and official statistics programmes | proposal | potentially sensitive | no |
| `gov.elections-administration` | Elections administration | proposal | potentially sensitive | no |
| `civic.political-campaign` | Political campaigning and party organising | proposal | potentially sensitive | no |
| `gov.constituent-casework` | Constituent and citizen casework | proposal | potentially sensitive | no |
| `gov.international-development-programme` | International development programmes | proposal | potentially sensitive | no |
| `gov.diplomatic-consular-record` | Diplomatic and consular records | proposal | potentially sensitive | no |
| `gov.defence-veterans-administration` | Defence and veterans' affairs administration | proposal | potentially sensitive | no |
| `gov.emergency-management` | Emergency management and civil protection | proposal | potentially sensitive | no |
| `gov.public-health-administration` | Public health administration | proposal | potentially sensitive | no |
| `gov.social-services-casework` | Social services and welfare casework | proposal | potentially sensitive | no |
| `gov.housing-authority` | Public and social housing administration | proposal | potentially sensitive | no |
| `gov.transport-authority` | Transport authority administration | proposal | none | no |
| `gov.environmental-regulation` | Environmental regulation and monitoring | proposal | none | no |
| `gov.parks-public-lands` | Parks, public lands and heritage site management | proposal | none | no |
| `gov.professional-regulator` | Professional regulation (regulator side) | proposal | potentially sensitive | no |
| `gov.library-administration` | Library service administration | proposal | potentially sensitive | no |
| `gov.archives-recordkeeping` | Archives and records management | proposal | potentially sensitive | no |
| `gov.museum-collection` | Museum and gallery collection management | proposal | none | no |
| `edadmin.school-district` | School district and local education administration | inference | potentially sensitive | no |
| `edadmin.institution-governance` | Education institution governance and administration | inference | none | no |
| `edadmin.accreditation-body` | Accreditation and quality assurance bodies (assessor side) | proposal | none | no |
| `civic.standards-body` | Standards development bodies | proposal | none | no |
| `npo.governance` | Nonprofit and charity governance | proposal | none | no |
| `npo.fundraising-donor` | Fundraising and donor records | proposal | potentially sensitive | no |
| `npo.volunteer-management` | Volunteer management | proposal | potentially sensitive | no |
| `npo.grant-reporting-recipient` | Grant reporting (recipient side, non-research) | proposal | none | no |
| `civic.advocacy-campaign` | Advocacy and public campaigning | proposal | potentially sensitive | no |
| `civic.community-organising` | Community organising and mutual aid | proposal | potentially sensitive | no |
| `npo.religious-institution` | Religious institution administration | proposal | potentially sensitive | no |
| `npo.residents-association` | Residents' and homeowners' associations | proposal | potentially sensitive | no |
| `civic.trade-union` | Trade union and staff association records | proposal | potentially sensitive | no |

---

## `gov.public-authority-record` — Public authority records (branch root)

A document issued by, or addressed to, a public body that carries an authority and a record type but no more specific governmental sub-domain — the branch root for this slice.

**Provenance:** **proposal** — new; the design names nothing like it

**Cite:** No design sentence names a governmental domain. §5.1's candidate top-level branches are “Academics, Applications, Research, Career, Personal Records, Finance and Administration, Photos and Captures, Code and Projects, and Media or Miscellaneous Personal Material” — none of which is a governmental branch. §5.7 lists the template library's intended coverage — “covering common organizational situations such as academic programs, university applications, recruiting processes, client engagements, research workflows, financial records, travel, legal matters, creative projects, software repositories, personal administration, and photo collections” — and names nothing governmental. This root exists because §3.15: “Other domains remain placeholders until user demand and corpus evidence justify detailed templates.”

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `authority` | string | municipal licensing department | `validated` | The issuing body is the one dimension every record in this slice carries. §3.8: “The system must separate roles that happen to contain the same entity type.” — the authority is not the same field as the person the record concerns, and a folder keyed on the authority must not become a bin for everything that body ever sent. §3.8: “A folder should not become a collection point for everything produced by the same person or organization.” |
| `record_type` | string | decision notice | `validated` | The work-type analogue for this branch, and the field that decides whether a more specific sub-domain should take over. It is confirmable by rule only alongside an authority name, per §3.5's model for a deterministic recogniser: “BUSIB 4300 becomes a course fact only when the engine finds a course-code pattern together with academic context” |
| `reference` | string | the case or file reference as printed on the document, retained verbatim | `direct` | §3.13 direct: “A direct fact was read from a reliable and explicit source, such as a content hash, EXIF timestamp, document title, or labeled form field.” — a labeled 'Reference' or 'Our ref' field is exactly that source. The catalogue deliberately gives no example format: reference-number shapes are jurisdiction-specific and inventing one would be worse than leaving the field shapeless |
| `jurisdiction` | string | the polity whose law the authority acts under, as named on the document | `possible` | Ceiling is deliberately low. A document rarely states its own jurisdiction — it assumes it. §3.13 possible: “A possible fact is a useful but insufficient clue”, which is the honest state for a value inferred from an address block or a body name. See the open question |
| `party` | string | the named person or organisation the record concerns | `direct` | §3.8's worked pair: “A consulting document may mention the author’s firm and the client organization.” — the authority and the party are the governmental instance of that pair. Direct only when read from a labeled addressee or applicant field |
| `record_side` | string | held by the party the record concerns | `llm_supported` | Whether a file sits in the citizen's folder or the authority's own case file. Almost never recoverable from one document — see the slice-level finding and the open question on gov.planning-application. §3.11 permits “several additional fields used only for search, privacy protection, explanation, or later review”; this is an explanation field, never a folder dimension |
| `issue_date` | date | 2026-03-14 | `direct` | §3.10: “Date candidates should be identified with explicit regular expressions and then parsed without fuzzy matching.”. A labeled 'Date of this notice' field is direct; a date recovered from prose is not |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.4, §3.5):

- an authority-shaped organisation name matched on a word boundary co-occurring with a governmental record term — 'notice' | 'determination' | 'decision' | 'appeal' | 'statutory' | 'the authority' | 'issued under'
- a labeled reference field ('reference' | 'case number' | 'our ref' | 'your ref') appearing in a letterhead zone or document title together with an authority-shaped name

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- a letter whose issuing body is identifiable only from prose, and whose record type must be read from the body text rather than a heading
- a photographed or OCR'd notice where the authority name survives only in a logo region and the record type must be inferred from the sentence structure
- a document that is governmental in form but whose function belongs to a sub-domain the rules could not pick between

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10):

- a bare reference string — §3.10 is explicit that file names and documents “frequently contain numbers that look like years but are course identifiers, version numbers, build numbers, ZIP codes, or other unrelated values”, and a case reference is the same hazard in a different costume
- the words 'official' or 'government' — they appear in letter templates, marketing copy and document themes far more often than in actual public records
- an authority name alone. §4.9's warning generalises: “A university name alone should not create a group because Columbia can appear as an authoring school, course provider, target institution, employer, research venue, or merely a cited organization.”; a council appears as a landlord, an employer, a supplier, a grant funder and a merely cited body
- a crest, seal or coat of arms in an image region — it is not text, and OCR will not make it a fact

### Work types

`notice`, `decision letter`, `certificate`, `statutory form`, `correspondence`, `guidance note`, `register extract`

### Grouping reasons (§4)

- one authority's correspondence about one matter, joined by a shared reference
- one reference number appearing across the authority's notices and the party's replies

### Template (§5)

`authority → record type → issue year`

Time first: **no**

The issue year is derived from the `issue_date` fact rather than being a field of its own; §5.7 requires the other two levels to be fields, and they are. §5.5: “a parent dimension should provide the context required to understand the child” — a record type is only meaningful once the issuing body is known, and a year is only meaningful once the matter is. §5.5: “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders.”, which keeps the year last. §5.9: “It should also support a scoped General or Other branch within a meaningful parent.” — a one-off notice with no matter belongs directly under the authority, not in a deeper invented path

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| pers.household-admin | a notice from a public body about the user's own household is both a public-authority record and household administration; nothing in the document separates them, and the split is a choice about the user's tree rather than a fact about the file | §3.11: “One file may hold facts from more than one domain without losing information.” |
| admin.licences-permits | the finance-admin slice owns the licence or permit as a document the holder keeps; this root owns it as a record of an authority's act. Same paper, two owners | §6.9: “A file may have multiple valid organizational relationships, and the placement engine must preserve that complexity.” |
| legal.court-records | a tribunal or court is a public body, but its records are a legal-practice object with parties, hearings and orders. The separating signal is a court or tribunal name plus a case-party structure, not an authority letterhead | §4.8: the validator checks “that each fact or label belongs to an allowed domain schema” |
| gov.constituent-casework | an elected representative's office holds authority correspondence about someone else's case; the separating signal is a third party as the subject and the representative's office as the correspondent, not the authority name | §3.8: “The system must separate roles that happen to contain the same entity type.” |

### Sensitivity

`potentially_sensitive` — §2.9's phrase “while treating addresses and message content as potentially sensitive” applies directly: an authority record ordinarily carries a named person and a postal address, and §2.9 on address-book data: it “should normally be privacy-protected rather than used to create folder proposals”. §4.9: “Rare but sensitive files such as passports, visas, and legal documents may be surfaced as protected records even when they do not meet a normal group-size threshold.” covers the sharp end of this branch. handling classes are P7's — §8.4: “The system should classify data into handling classes before LLM escalation” — and none is assigned here

### Open question — Joseph's call, unresolved

> WHICH JURISDICTIONS DOES THIS PRODUCT SUPPORT, AND IS THERE A GOVERNMENT BRANCH AT ALL? Two questions that only Joseph can close. First, the design states no jurisdiction anywhere, and this slice is the sharpest case in the whole catalogue: the names of governmental functions, the document types they produce, the reference-number shapes, and even which tier of government performs a function differ between countries and between regions inside one country. Every entry here is written functionally for that reason, but functional wording is a holding position, not a decision — it costs the deterministic recognisers their gazetteers, because no list of authority names, form numbers or statutory instrument shapes can be built until the scope is fixed. Second, §5.1's candidate top-level branches contain no governmental branch and §5.7's template-library list names nothing governmental. So either these domains hang under Personal Records and Finance and Administration as sub-branches, or the product grows a top-level area the design never proposed. Joseph decides; the catalogue supplies the schemas either way.

---

## `gov.policy-development` — Policy development

The working papers by which a public body develops a policy position — options papers, evidence reviews, impact assessments, drafts and the decision that closes them.

**Provenance:** **proposal** — new; the design names nothing like it

**Cite:** No design sentence names policy work. §5.7 lists the template library's intended coverage — “covering common organizational situations such as academic programs, university applications, recruiting processes, client engagements, research workflows, financial records, travel, legal matters, creative projects, software repositories, personal administration, and photo collections” — and names nothing governmental. Modelled on the design's project-shaped domains: §3.3 gives rules “routing obvious files into plausible domains” and sends the rest to the model

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `policy_area` | string | residential waste collection | `llm_supported` | The subject a policy addresses is a prose fact, not a labeled one. §3.5: the model “can only propose facts that belong to the active domain schema, and it must cite exact supporting evidence already extracted from the file.” — the model may name the area only when the document says it |
| `policy_instrument` | string | consultation paper | `validated` | The document's role in the policy cycle, confirmable by rule when an instrument term appears in a title or heading zone alongside an authority name. §3.7: “It should use positional weighting because a value in a filename or document title carries more meaning than the same value in a footer or a late body-page reference.” |
| `stage` | string | options appraisal | `validated` | The research slice's project domains use a stage field for the same reason — §3.3 gives rules “routing obvious files into plausible domains” and sends the rest to the model — and a policy file's stage is what makes a draft legible next to a final. Confirmable only with an instrument or decision term beside it |
| `authority` | string | a national department with responsibility for the policy area | `validated` | §3.8: “The system must separate roles that happen to contain the same entity type.”: the body that owns the policy is not the body that responded to it, and not the body that will implement it |
| `version_label` | string | draft for internal comment | `direct` | §3.13 direct: “A direct fact was read from a reliable and explicit source, such as a content hash, EXIF timestamp, document title, or labeled form field.” — a labeled status line or a title-page marking. Policy corpora are dominated by near-identical drafts, so the version label carries more weight here than in most domains |
| `decision_date` | date | 2026-05-02 | `direct` | §3.10: “Date candidates should be identified with explicit regular expressions and then parsed without fuzzy matching.”. Only a labeled approval or publication date qualifies; a date in prose does not |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.4, §3.5):

- a policy-instrument term in a title or first-page heading — 'consultation paper' | 'options appraisal' | 'impact assessment' | 'policy statement' | 'strategy' — co-occurring with an authority-shaped name in a letterhead or footer zone
- an impact-assessment structure detected as labeled headings ('option 1' | 'option 2' | 'do nothing' | 'preferred option') co-occurring with a policy-instrument term

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- an untitled internal paper whose only policy signal is prose arguing between courses of action
- a slide deck that presents a policy option set without any instrument term in its title
- a document that is a policy paper in one jurisdiction's vocabulary and a legislative explanatory memorandum in another's

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10):

- the word 'policy' — it names an insurance contract, a privacy notice, a company handbook and a configuration file at least as often as a public policy paper
- the word 'strategy' — the same hazard, and heavily used in commercial decks
- 'option 1' / 'option 2' headings alone — they appear in vendor proposals, architecture documents and consulting decks
- an authority name alone. §4.9's warning generalises: “A university name alone should not create a group because Columbia can appear as an authoring school, course provider, target institution, employer, research venue, or merely a cited organization.”

### Work types

`issues paper`, `evidence review`, `options appraisal`, `impact assessment`, `draft policy`, `final policy statement`, `ministerial or executive submission`, `implementation plan`

### Grouping reasons (§4)

- one policy question across its evidence, options, drafts and decision — §3.9: “The documents are content-incoherent but purpose-coherent.” describes this packet exactly
- one drafting family: the same paper across its versions, joined by version stem rather than topic

### Template (§5)

`policy area → stage → version`

Time first: **no**

§5.5: “a parent dimension should provide the context required to understand the child” — a stage such as 'options appraisal' means nothing until the policy question is known. §5.5: “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders.”, so no date level appears; where a policy runs over years the year belongs inside the version label, not as a folder. The policy-area level is backed by an `llm_supported` fact against §3.14's rule that templates use validated facts, so it should be offered only from an existing folder name or a user-confirmed label: §3.9: “Purpose may be supported strongly by an existing user-created folder name or explicit language in a form or portal.”

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| gov.regulatory-rulemaking | a policy paper becomes a rulemaking record the moment it is the statement of reasons attached to a draft rule; the separating signal is a citation to the rule-making power, not the subject matter | §4.8: the validator checks “that each fact or label belongs to an allowed domain schema” |
| gov.legislative-record | in some systems the policy paper and the explanatory material accompanying a bill are the same document; where a bill identifier is present the legislative domain owns it | §4.8: “an application packet does not silently absorb a document with a conflicting target institution” |
| gov.public-consultation | a consultation paper is a policy instrument and the opening move of a consultation exercise. It legitimately holds both sets of facts | §3.11: “One file may hold facts from more than one domain without losing information.” |
| res.research-project | an evidence review commissioned from a research team is a research output and a policy input; the separating signal is whether the file carries a project identifier and a lab, or a policy area and a stage | §3.11: “Research files may use project, stage, artifact type, lab, and venue.” — the fields differ even where the prose does not |

### Sensitivity

`none` — Policy working papers are ordinarily about a subject rather than about identified people. Pre-decision papers are frequently confidential, but confidentiality is a per-file property and a handling decision, not a domain fact — handling classes are P7's — §8.4: “The system should classify data into handling classes before LLM escalation” — and none is assigned here

---

## `gov.legislative-record` — Legislative and parliamentary records

Records of a legislature's own business — bills and their versions, amendments, committee papers, evidence, votes and the transcript of proceedings.

**Provenance:** **proposal** — new; the design names nothing like it

**Cite:** No design sentence names legislative work. §5.7 lists the template library's intended coverage — “covering common organizational situations such as academic programs, university applications, recruiting processes, client engagements, research workflows, financial records, travel, legal matters, creative projects, software repositories, personal administration, and photo collections” — and names nothing governmental. The bill-plus-stage structure is modelled on the design's stage-bearing domains, per §3.3 gives rules “routing obvious files into plausible domains” and sends the rest to the model

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `measure` | string | the short title of the bill or motion as printed on its first page | `validated` | The bill or motion is the object everything else hangs from. Confirmable by rule when a measure identifier co-occurs with a legislative context term, following §3.5's model for a deterministic recogniser: “BUSIB 4300 becomes a course fact only when the engine finds a course-code pattern together with academic context” |
| `measure_identifier` | string | the bill or docket number exactly as printed | `validated` | Bill-numbering schemes differ completely between legislatures and no universal pattern exists, so the field stores the string verbatim and the recogniser needs a legislative context term beside it. No example format is given because inventing one would assert a numbering scheme that may not exist |
| `stage` | string | committee stage | `validated` | The procedural step a document belongs to. Stage vocabulary is jurisdiction-specific — see the open question — so the rule matches a stage term only alongside a measure identifier |
| `session` | string | the sitting period or legislature number as printed | `direct` | §3.13 direct: “A direct fact was read from a reliable and explicit source, such as a content hash, EXIF timestamp, document title, or labeled form field.” — sessions are printed on the header of legislative papers. The field matters structurally rather than chronologically: a measure that does not pass usually dies with its session, so the session is a container, not a calendar year |
| `chamber_or_committee` | string | the committee named on the paper | `validated` | §3.8: “The system must separate roles that happen to contain the same entity type.” — the committee that took evidence is not the body that introduced the measure and not the witness who gave the evidence |
| `document_role` | string | amendment paper | `validated` | The work-type field. It is what separates a bill text from an amendment list from a transcript, all of which carry the same measure identifier |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.4, §3.5):

- a measure identifier pattern co-occurring with a legislative context term — 'bill' | 'amendment' | 'reading' | 'committee' | 'enacted' | 'ordered to be printed' | 'question put' — which is §3.5's model for a deterministic recogniser: “BUSIB 4300 becomes a course fact only when the engine finds a course-code pattern together with academic context” transposed onto a bill number
- a transcript structure detected as repeated speaker-attribution lines co-occurring with a chamber or committee name in a title or header zone

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- a written evidence submission whose only legislative signal is prose addressed to an inquiry
- a briefing prepared for a legislator that never names the measure it concerns
- a document whose stage vocabulary belongs to a legislature the recogniser has no gazetteer for

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10):

- a bare bill-shaped number. §3.10 is explicit that file names and documents “frequently contain numbers that look like years but are course identifiers, version numbers, build numbers, ZIP codes, or other unrelated values”, and short alphanumeric identifiers collide with invoice numbers, docket numbers, standard numbers and version tags
- the word 'act' — it is a filename word, a theatre term and a verb
- the word 'amendment' — contracts, leases and specifications are amended far more often than bills
- a chamber or legislature name alone. §4.9's warning generalises: “A university name alone should not create a group because Columbia can appear as an authoring school, course provider, target institution, employer, research venue, or merely a cited organization.”

### Work types

`bill text`, `amendment paper`, `explanatory material`, `committee report`, `written evidence`, `oral evidence transcript`, `division or vote record`, `proceedings transcript`

### Grouping reasons (§4)

- one measure across its versions, amendments, committee papers and transcripts
- one inquiry across its call for evidence, written submissions, transcripts and report

### Template (§5)

`session → measure → stage`

Time first: **no**

§5.5: “a parent dimension should provide the context required to understand the child” — a stage is meaningless without the measure, and a measure identifier is frequently reused between sessions so the session must disambiguate it. This looks like time-first and is not: §5.5: “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders.” applies to calendar years, whereas a legislative session is a structural container that a measure cannot outlive. Where a user's corpus spans one session only, §5.8: “The canvas must support uneven depth because real file trees are not and should not be perfectly symmetrical.” and the session level should be flattened away

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| gov.policy-development | explanatory material accompanying a bill is both the policy statement and a legislative document; the measure identifier is what gives this domain the claim | §4.8: “an application packet does not silently absorb a document with a conflicting target institution” |
| gov.regulatory-rulemaking | secondary or delegated instruments are made under a statute and laid before a legislature, so they carry both a measure identifier and a rule citation. The separating signal is whether the document is the instrument or the debate about it | §4.8: the validator checks “that each fact or label belongs to an allowed domain schema” |
| civic.advocacy-campaign | a written evidence submission is a legislative record for the committee and a campaign output for its author; §3.8: “The system must separate roles that happen to contain the same entity type.” separates the receiving committee from the submitting organisation | §3.8's worked pair: “A consulting document may mention the author’s firm and the client organization.” |
| law.legal-research | a lawyer's copy of a bill is research material for a matter, not a legislative record; the separating signal is the surrounding matter file, which is a corpus fact rather than a document fact | §4.2: “A seed may be a strongly identified file, a validated shared fact, a structural family, or a user-created starting point.” |

### Sensitivity

`none` — Legislative proceedings are ordinarily published records. Written evidence from named private individuals is the exception and it is a per-file property, not a domain default. handling classes are P7's — §8.4: “The system should classify data into handling classes before LLM escalation” — and none is assigned here

### Open question — Joseph's call, unresolved

> STAGE AND SESSION VOCABULARY IS NOT TRANSLATABLE. Legislative stage names, chamber structures and bill-numbering schemes are not variants of one model — a unicameral legislature, a bicameral one with differing procedures per chamber, and a system with a separate constitutional review step produce genuinely different stage sets, not different words for the same set. A `stage` field with no jurisdiction attached is therefore an open enum with no allow-list, which is exactly what §3.6's validator cannot check. Joseph decides whether stage is a free string, a per-jurisdiction enum that ships only for supported jurisdictions, or a field held back until a jurisdiction is chosen.

---

## `gov.regulatory-rulemaking` — Regulatory rulemaking

A regulator's record of making, amending or revoking a rule — the proposal, the supporting analysis, the comments received, the response to them and the final instrument.

**Provenance:** **proposal** — new; the design names nothing like it

**Cite:** No design sentence names rulemaking. §5.7 lists the template library's intended coverage — “covering common organizational situations such as academic programs, university applications, recruiting processes, client engagements, research workflows, financial records, travel, legal matters, creative projects, software repositories, personal administration, and photo collections” — and names nothing governmental. The proposal-to-final packet is a purpose-coherent group in the sense of §3.9: “The documents are content-incoherent but purpose-coherent.”

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `rule_subject` | string | labelling requirements for packaged food | `llm_supported` | What the rule governs is a prose fact. §3.5: the model “can only propose facts that belong to the active domain schema, and it must cite exact supporting evidence already extracted from the file.” |
| `regulator` | string | a sectoral regulator with rule-making power | `validated` | §3.8: “The system must separate roles that happen to contain the same entity type.” — the regulator, the regulated entity and the commenter are three roles that all appear as organisation names on the same page |
| `rulemaking_stage` | string | proposed rule | `validated` | The stage separates a proposal from a final instrument, which is the single most consequential distinction in this domain: filing a proposal as if it were the operative rule is a real-world error. Confirmable only with a rule-making context term beside it |
| `instrument_reference` | string | the docket, instrument or notice reference exactly as printed | `direct` | §3.13 direct: “A direct fact was read from a reliable and explicit source, such as a content hash, EXIF timestamp, document title, or labeled form field.” — a labeled docket or instrument field. No format example is given: rulemaking reference shapes are jurisdiction-specific and a plausible invented one would be worse than none |
| `effective_date` | date | 2027-01-01 | `direct` | §3.10: “Date candidates should be identified with explicit regular expressions and then parsed without fuzzy matching.”. Only a labeled 'effective from' or 'comes into force' field qualifies. This is the field users actually search on and it is routinely different from the publication date |
| `comment_period_close` | date | 2026-09-30 | `direct` | §3.11 permits “several additional fields used only for search, privacy protection, explanation, or later review” — a search and explanation field, not a folder dimension. Direct only from a labeled closing-date field |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.4, §3.5):

- a rule-making stage term in a title or heading zone — 'notice of proposed rule' | 'draft regulation' | 'final rule' | 'statutory instrument' | 'regulatory impact' — co-occurring with a regulator-shaped organisation name
- a labeled docket or instrument reference field co-occurring with an 'effective' or 'comes into force' date field

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- a guidance document that restates a rule without being one, which is the most common misfiling in this domain
- a regulator's letter that announces a rule change in prose with no instrument reference anywhere
- a document whose stage is expressed in a jurisdiction's vocabulary the recogniser has no list for

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10):

- the word 'regulation' — it names a software configuration, a sports rulebook and a company policy
- the word 'draft' — the highest-frequency word in any document corpus
- a docket-shaped reference alone — §3.10 is explicit that file names and documents “frequently contain numbers that look like years but are course identifiers, version numbers, build numbers, ZIP codes, or other unrelated values”
- a regulator's name alone. §4.9's warning generalises: “A university name alone should not create a group because Columbia can appear as an authoring school, course provider, target institution, employer, research venue, or merely a cited organization.”; a regulator appears as an author, an addressee, a cited body and an employer

### Work types

`proposed rule`, `regulatory impact analysis`, `comment received`, `response to comments`, `final rule or instrument`, `guidance`, `enforcement policy statement`

### Grouping reasons (§4)

- one rulemaking from proposal to final instrument, joined by the docket or instrument reference
- one regulator's instruments on one subject across amendments

### Template (§5)

`regulator → rule subject → stage`

Time first: **no**

§5.5: “a parent dimension should provide the context required to understand the child” — a stage such as 'final rule' means nothing without the rule, and rule subjects collide across regulators. §5.5: “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders.”, so the effective date stays a fact rather than a level. The rule-subject level is backed by an `llm_supported` fact, so it should come from a user-confirmed label rather than from a rule; where none exists the instrument reference is the safer level

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| gov.public-consultation | a comment period is a consultation exercise; where the file is a comment the consultation domain describes it better, and where it is the regulator's response to comments this domain does | §3.8: “The system must separate roles that happen to contain the same entity type.” |
| corp.regulatory-filings | the finance-admin slice owns what a regulated entity files WITH a regulator; this domain owns what the regulator makes. Both carry the same regulator name, so the regulator name cannot be the separating signal | §3.8's worked pair: “A consulting document may mention the author’s firm and the client organization.” |
| law.regulatory-submission | a law firm's submission on behalf of a client is a matter document; the separating signal is a client and a matter reference, not the rule | §4.8: the validator checks “that each fact or label belongs to an allowed domain schema” |
| gov.legislative-record | delegated instruments are laid before a legislature and appear in both domains; the separating signal is whether the document is the instrument or the proceedings about it | §4.8: “an application packet does not silently absorb a document with a conflicting target institution” |

### Sensitivity

`none` — Rulemaking records are published by design. Comments from named individuals are the exception and their sensitivity is a property of those files, not of the domain. handling classes are P7's — §8.4: “The system should classify data into handling classes before LLM escalation” — and none is assigned here

---

## `gov.public-consultation` — Public consultation exercises

A structured invitation for public or stakeholder comment and everything it produces — the consultation document, the responses, the analysis and the published outcome.

**Provenance:** **proposal** — new; the design names nothing like it

**Cite:** No design sentence names consultation. §5.7 lists the template library's intended coverage — “covering common organizational situations such as academic programs, university applications, recruiting processes, client engagements, research workflows, financial records, travel, legal matters, creative projects, software repositories, personal administration, and photo collections” — and names nothing governmental. The consultation packet is content-incoherent and purpose-coherent in the sense of §3.9: “The documents are content-incoherent but purpose-coherent.”

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `consultation_title` | string | the title of the consultation as printed on its front page | `direct` | §3.13 direct: “A direct fact was read from a reliable and explicit source, such as a content hash, EXIF timestamp, document title, or labeled form field.” — a document title is one of §3.13's named direct sources, and consultation documents are reliably titled |
| `consulting_body` | string | a national department running the exercise | `validated` | §3.8: “The system must separate roles that happen to contain the same entity type.” — the body running the consultation and the body responding to it are different fields even when both are public authorities |
| `respondent` | string | the organisation or individual submitting a response | `direct` | §3.8's worked pair: “A consulting document may mention the author’s firm and the client organization.” transposed: this is the consultation's our-side/their-side pair. Direct only from a labeled respondent field on a response form |
| `document_role` | string | response | `validated` | The work-type field, and the one that carries the citizen-versus-authority distinction in this domain: a consultation document and a response to it are different objects even though they share a title |
| `closing_date` | date | 2026-09-30 | `direct` | §3.10: “Date candidates should be identified with explicit regular expressions and then parsed without fuzzy matching.”. A labeled 'responses by' field is direct; the same date recovered from a sentence is not |
| `policy_area` | string | residential waste collection | `llm_supported` | Carried so a consultation can be retrieved beside the policy work it feeds. §3.5: the model “can only propose facts that belong to the active domain schema, and it must cite exact supporting evidence already extracted from the file.” |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.4, §3.5):

- a consultation term in a title or first-page heading — 'consultation' | 'call for evidence' | 'call for comment' | 'have your say' | 'invitation to comment' — co-occurring with a labeled closing-date field or a named consulting body
- a response-form structure detected as labeled question numbers together with a respondent field and a consultation term

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- a free-text response letter with no form structure whose only consultation signal is prose referring to the exercise
- a submission that argues a case without ever naming the consultation it answers
- a stakeholder workshop note that is part of a consultation in one jurisdiction's practice and a separate engagement activity in another's

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10):

- the word 'consultation' — it is a medical appointment, a legal meeting and a paid advisory service at least as often
- the word 'feedback' — ubiquitous in product, teaching and HR documents
- a closing date alone. §3.10 is explicit that file names and documents “frequently contain numbers that look like years but are course identifiers, version numbers, build numbers, ZIP codes, or other unrelated values”
- a consulting body's name alone. §4.9's warning generalises: “A university name alone should not create a group because Columbia can appear as an authoring school, course provider, target institution, employer, research venue, or merely a cited organization.”

### Work types

`consultation document`, `response form`, `response submitted`, `response received`, `summary of responses`, `consultation outcome`, `engagement event note`

### Grouping reasons (§4)

- one consultation across its document, its responses and its published outcome
- one respondent's submissions across several consultations, joined by respondent rather than by exercise

### Template (§5)

`consulting body → consultation → document role`

Time first: **no**

§5.5: “a parent dimension should provide the context required to understand the child” — a 'response' folder is meaningless until the exercise is known. Where the user is a respondent rather than the consulting body the order should invert to respondent-first, which is §3.8: “The system must separate roles that happen to contain the same entity type.” expressed as a tree; the catalogue cannot choose for them

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| gov.regulatory-rulemaking | a rulemaking comment period is a consultation; the separating signal is whether the exercise attaches to an instrument reference | §3.11: “One file may hold facts from more than one domain without losing information.” |
| gov.planning-application | neighbour notification on a planning application is a consultation in form and a case document in function; the case reference gives the planning domain the claim | §4.8: “an application packet does not silently absorb a document with a conflicting target institution” |
| civic.advocacy-campaign | a campaign's consultation response is both; §3.9: “Topic answers what a file is about, while purpose answers what the file was for.” — the topic is the consultation, the purpose is the campaign | §3.9: “Purpose must be a first-class facet.” |
| res.survey-instrument | a consultation questionnaire looks like a research survey instrument; the separating signal is a consulting body and a closing date rather than a project and an ethics reference | §3.11: “Research files may use project, stage, artifact type, lab, and venue.” |

### Sensitivity

`potentially_sensitive` — Responses from named individuals carry an identity, an address and an opinion together, which is §2.9's phrase “while treating addresses and message content as potentially sensitive” in its most literal form. Published response summaries are not sensitive, so the marking is conservative for the domain rather than descriptive of every file. handling classes are P7's — §8.4: “The system should classify data into handling classes before LLM escalation” — and none is assigned here

### Open question — Joseph's call, unresolved

> A CONSULTATION RESPONSE IS THE CLEAREST CASE WHERE THE SAME DOCUMENT SITS ON BOTH SIDES. The consulting body's copy of a response and the respondent's own copy are frequently byte-identical, and no field on the page distinguishes them. What distinguishes them is the corpus: an authority holds hundreds of responses to one exercise, a respondent holds one response to each of several exercises. That is a §4 grouping signal, not a §3 fact, and acting on it means the product infers the user's institutional role from the shape of their filesystem. Joseph decides whether the product may draw that inference at all, and whether it may be surfaced to the user as a question rather than assumed.

---

## `gov.intergovernmental-agreement` — Intergovernmental agreements

Agreements between public bodies — shared-service arrangements, funding transfers between tiers of government, mutual-aid compacts and instruments between states.

**Provenance:** **proposal** — new; the design names nothing like it

**Cite:** No design sentence names intergovernmental instruments. §5.7 lists the template library's intended coverage — “covering common organizational situations such as academic programs, university applications, recruiting processes, client engagements, research workflows, financial records, travel, legal matters, creative projects, software repositories, personal administration, and photo collections” — and names nothing governmental — it names “legal matters” but not agreements between public bodies

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `parties` | string | the public bodies named as parties on the front page | `validated` | §3.8: “The system must separate roles that happen to contain the same entity type.” — an intergovernmental instrument has no our-side/their-side asymmetry, which makes it unusual in this slice: both parties are authorities and the field is plural by nature |
| `counterparty` | string | the other public body, seen from the user's own side | `validated` | §3.8: “The system must separate roles that happen to contain the same entity type.” — `parties` records both sides as the instrument states them; `counterparty` is the role split that makes a folder level possible, because a level named for the user's own body would be a collector with one child |
| `agreement_type` | string | memorandum of understanding | `validated` | The instrument's binding character differs sharply between an operational memorandum and a treaty-level instrument, and the type term is the only reliable carrier of that. Confirmable with an agreement-structure term beside it |
| `subject` | string | shared emergency communications | `llm_supported` | What the agreement covers is prose. §3.5: the model “can only propose facts that belong to the active domain schema, and it must cite exact supporting evidence already extracted from the file.” |
| `commencement_date` | date | 2026-04-01 | `direct` | §3.10: “Date candidates should be identified with explicit regular expressions and then parsed without fuzzy matching.” — a labeled commencement or entry-into-force field only |
| `review_or_expiry_date` | date | 2029-03-31 | `direct` | §3.11 permits “several additional fields used only for search, privacy protection, explanation, or later review” — a search field that makes an expiring arrangement findable. Direct only when labeled |
| `jurisdiction` | string | the tiers or polities the parties belong to | `possible` | This domain cannot be written jurisdiction-neutrally at the level of what the tiers are called — the tiers themselves differ. §3.13 possible: “A possible fact is a useful but insufficient clue” |
| `document_role` | string | schedule or annex | `validated` | The work-type field, and the template's leaf dimension — an instrument, its schedules and its variations are different objects that share a title. §5.7 requires a template's dimensions to be drawn from the domain's allowed fact fields, so the level and the field must exist together. Confirmable from the same context-term list the deterministic recognisers use |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.4, §3.5):

- an agreement-structure term ('memorandum of understanding' | 'this agreement is made between' | 'the parties agree' | 'schedule 1') co-occurring with two or more authority-shaped names in the same title or parties block
- a labeled commencement or entry-into-force field co-occurring with an agreement-type term in the title zone

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- an exchange of letters that constitutes an agreement without ever using an agreement-type term
- a document whose parties are public bodies in one reading and arms-length entities in another, which is a genuinely contested question and not an extraction failure

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10):

- the phrase 'memorandum of understanding' — it is used constantly between commercial parties
- two organisation names on one page — invoices, letters and reports all carry several
- the word 'treaty' — it appears in academic writing far more often than on an instrument
- an authority name alone. §4.9's warning generalises: “A university name alone should not create a group because Columbia can appear as an authoring school, course provider, target institution, employer, research venue, or merely a cited organization.”

### Work types

`memorandum of understanding`, `funding agreement between bodies`, `shared-service agreement`, `mutual-aid compact`, `instrument between states`, `schedule or annex`, `variation`

### Grouping reasons (§4)

- one arrangement across its instrument, schedules, variations and review papers
- one pair of parties across the arrangements between them

### Template (§5)

`counterparty → subject → document role`

Time first: **no**

§5.5: “a parent dimension should provide the context required to understand the child”. The order is written from the user's own body outward, because §3.8: “A folder should not become a collection point for everything produced by the same person or organization.” — a level naming the user's own authority would be a collector with exactly one child. The subject level is backed by an `llm_supported` fact against §3.14's rule that templates use validated facts, so it should come from a user-confirmed label; where none exists the agreement type is the safer level. §5.5: “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders.”

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| legal.contracts | an intergovernmental agreement is a contract in form; the separating signal is that both parties are public bodies, which is a fact about the parties and not about the document structure | §3.8: “The system must separate roles that happen to contain the same entity type.” |
| gov.grant-programme-administration | a funding transfer between tiers of government is both an agreement and a grant; the separating signal is whether the recipient applied for it or is entitled to it, which is often not stated | §4.8: the validator checks “that each fact or label belongs to an allowed domain schema” |
| gov.diplomatic-consular-record | an instrument between states is diplomatic material and an intergovernmental agreement at once; where a foreign ministry's channel appears the diplomatic domain describes it better | §3.11: “One file may hold facts from more than one domain without losing information.” |

### Sensitivity

`none` — Instruments between public bodies are ordinarily about arrangements rather than identified individuals. handling classes are P7's — §8.4: “The system should classify data into handling classes before LLM escalation” — and none is assigned here

---

## `gov.municipal-administration` — Municipal and local authority administration

The running record of a local authority as an organisation — meeting agendas and minutes, reports to committee, local budgets, service performance reports and local notices.

**Provenance:** **proposal** — new; the design names nothing like it

**Cite:** No design sentence names local government. §5.7 lists the template library's intended coverage — “covering common organizational situations such as academic programs, university applications, recruiting processes, client engagements, research workflows, financial records, travel, legal matters, creative projects, software repositories, personal administration, and photo collections” — and names nothing governmental. Modelled on the meeting-cycle shape the design never names but which §5.3: “The product opens an accepted branch and proposes one or more domain templates based on the groups and facts that already belong inside it.” would have to propose for it

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `authority` | string | a city or district council | `validated` | §3.8: “The system must separate roles that happen to contain the same entity type.” — the authority is the organisation whose business this is, distinct from the applicants, suppliers and residents named inside its papers |
| `decision_body` | string | the committee named on the agenda | `validated` | The committee or executive that took the item. It is the real organising dimension of a local-government corpus, more than the authority is, because a single authority produces one stream per body |
| `meeting_date` | date | 2026-06-11 | `direct` | §3.13 direct: “A direct fact was read from a reliable and explicit source, such as a content hash, EXIF timestamp, document title, or labeled form field.” — agendas and minutes carry a labeled meeting date in a header zone. This is one of the few genuinely reliable date fields in the slice |
| `item_reference` | string | the agenda item reference as printed | `direct` | §3.13 direct: “A direct fact was read from a reliable and explicit source, such as a content hash, EXIF timestamp, document title, or labeled form field.” — a labeled item field. Item numbering is local to each authority so no format is asserted |
| `document_role` | string | report to committee | `validated` | The work-type field: agenda, report, minutes and decision notice are the recurring set and they are what a user actually looks for |
| `service_area` | string | waste and recycling | `llm_supported` | §3.11 permits “several additional fields used only for search, privacy protection, explanation, or later review” — a search field. Service-area vocabulary differs between authorities even inside one country, so no allow-list can be shipped |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.4, §3.5):

- a meeting-paper term in a title or header zone — 'agenda' | 'minutes' | 'report to' | 'notice of meeting' | 'decision notice' — co-occurring with a committee-shaped name and a labeled meeting date
- a numbered agenda-item structure detected as repeated item headings co-occurring with an authority-shaped name in a footer or header zone

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- an officer report with no cover sheet, whose committee and authority appear only in prose
- a local notice that is a statutory publication in one system and an ordinary announcement in another
- a spreadsheet of service performance whose subject must be read from sheet names and column headers

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10):

- the word 'minutes' — it is a unit of time and a meeting record, and the unit is far more common
- the word 'agenda' — ubiquitous in ordinary workplace files
- a meeting date alone. §3.10 is explicit that file names and documents “frequently contain numbers that look like years but are course identifiers, version numbers, build numbers, ZIP codes, or other unrelated values”
- an authority name alone. §4.9's warning generalises: “A university name alone should not create a group because Columbia can appear as an authoring school, course provider, target institution, employer, research venue, or merely a cited organization.”; a council is a landlord, an employer, a customer and a grant funder to different people

### Work types

`agenda`, `report to committee`, `minutes`, `decision notice`, `local budget`, `service performance report`, `public notice`, `register of interests`

### Grouping reasons (§4)

- one meeting across its agenda, its reports and its minutes — §3.9: “The documents are content-incoherent but purpose-coherent.”
- one decision body across a run of meetings

### Template (§5)

`decision body → meeting date → document role`

Time first: **no**

§5.5: “a parent dimension should provide the context required to understand the child” — a report is only findable once the body and the sitting are known. This entry is the slice's clearest apparent exception to §5.5: “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders.” and it is still not a real one: the meeting date is an event identifier rather than a calendar bucket, in the same way an event is for photographs. The dimension is the meeting, and its label happens to be a date

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| gov.public-authority-record | a decision notice is both this authority's own record and, in the hands of the person it concerns, a bare authority record with no meeting context | §6.9: “A file may have multiple valid organizational relationships, and the placement engine must preserve that complexity.” |
| gov.planning-application | a planning committee report is a meeting paper and a case document; the case reference gives the planning domain the claim and the meeting gives this one its context | §3.11: “One file may hold facts from more than one domain without losing information.” |
| npo.residents-association | an association's minutes are structurally identical to a council committee's; the separating signal is whether the body has statutory functions, which the minutes themselves rarely state | §4.8: the validator checks “that each fact or label belongs to an allowed domain schema” |
| edadmin.school-district | in some systems schools are a service of the general local authority and in others they sit under a separately elected board; the same meeting paper is therefore municipal administration in one jurisdiction and school-district administration in another, with nothing on the page to tell them apart | §4.8: “an application packet does not silently absorb a document with a conflicting target institution” |

### Sensitivity

`none` — Public meeting papers are published by design. Items withheld from publication are a per-file property. handling classes are P7's — §8.4: “The system should classify data into handling classes before LLM escalation” — and none is assigned here

### Open question — Joseph's call, unresolved

> WHOSE FILES ARE THESE? An officer's corpus of committee papers is work product and belongs beside their employment, while a resident's copy of the same papers is reference material about where they live. The design's nearest branches are Career and Personal Records, and neither fits a public servant's working corpus. This is the general form of a question the whole slice raises: does the product model professional public-sector work as a Career sub-branch, as its own area, or not at all?

---

## `gov.grant-programme-administration` — Grant programme administration (funder side)

A funder's record of running a grant programme — the call, the applications received, assessment, award and monitoring of the money it gives out.

**Provenance:** **proposal** — new; the design names nothing like it

**Cite:** No design sentence names grant administration. §5.7 lists the template library's intended coverage — “covering common organizational situations such as academic programs, university applications, recruiting processes, client engagements, research workflows, financial records, travel, legal matters, creative projects, software repositories, personal administration, and photo collections” — and names nothing governmental. The funder-side/recipient-side split is §3.8: “The system must separate roles that happen to contain the same entity type.”

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `programme` | string | the name of the funding programme as printed on the call document | `validated` | The programme is the container everything else hangs from — a call, an application and an award all belong to one. Confirmable when a programme name co-occurs with a grant context term, per §3.5's model for a deterministic recogniser: “BUSIB 4300 becomes a course fact only when the engine finds a course-code pattern together with academic context” |
| `funder` | string | a public body operating a grant scheme | `validated` | §3.8's worked pair: “A consulting document may mention the author’s firm and the client organization.” transposed onto funding: the funder and the recipient are the pair, and this domain is written from the funder's side. Getting these the wrong way round produces a folder of other people's money |
| `applicant_or_recipient` | string | the organisation named on the application | `direct` | §3.13 direct: “A direct fact was read from a reliable and explicit source, such as a content hash, EXIF timestamp, document title, or labeled form field.” — a labeled applicant field on an application form. §2.3: “Tables matter because resumes, forms, applications, invoices, and administrative documents often place their most useful information in cells rather than body paragraphs.” is the reason this is worth extracting at all: it lives in a form cell, not in prose |
| `award_reference` | string | the grant or award reference exactly as printed | `direct` | §3.13 direct: “A direct fact was read from a reliable and explicit source, such as a content hash, EXIF timestamp, document title, or labeled form field.”. No format is asserted: award-reference shapes are set per funder and per jurisdiction, and a plausible invented one would be worse than an empty field |
| `round` | string | the funding round or cycle as printed on the call | `validated` | Programmes run in rounds that reuse the same document names, so the round is what stops one year's applications merging into the next. Confirmable from a labeled round or deadline field beside a programme name |
| `stage` | string | assessment | `validated` | Call, application, assessment, award, monitoring and closure are the recurring stages, and the stage is what makes an unsuccessful application legible next to a funded one |
| `grant_period` | date range | 2026-04-01 to 2028-03-31 | `direct` | §3.10: “Date candidates should be identified with explicit regular expressions and then parsed without fuzzy matching.” — from a labeled period field only. §3.10: “Date extraction should be deliberately narrow.” |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.4, §3.5):

- a grant context term in a title or heading zone — 'call for applications' | 'grant agreement' | 'award letter' | 'assessment panel' | 'eligibility criteria' | 'monitoring report' — co-occurring with a named programme or a labeled award-reference field
- an application-form structure detected as labeled applicant and eligibility fields co-occurring with a funder-shaped organisation name

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- an assessment note whose programme is never named and must be inferred from the criteria it applies
- a letter that declines an application without using any grant vocabulary
- a document that is a grant in one system and a statutory entitlement payment in another, which changes what the file is rather than what it is called

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10):

- the word 'grant' — it is also a verb, a permission, a personal name and a database privilege
- the word 'award' — prizes, contracts, damages and honours all use it
- a currency amount — the highest-firing pattern in any administrative corpus; it needs a programme or an award reference beside it
- a funder's name alone. §4.9's warning generalises: “A university name alone should not create a group because Columbia can appear as an authoring school, course provider, target institution, employer, research venue, or merely a cited organization.”

### Work types

`call for applications`, `guidance for applicants`, `application received`, `assessment note`, `panel record`, `award letter`, `grant agreement`, `monitoring report`, `closure report`

### Grouping reasons (§4)

- one programme across its call, applications, assessments and awards
- one award across its agreement, claims and monitoring, joined by the award reference

### Template (§5)

`programme → round → stage`

Time first: **no**

§5.5: “a parent dimension should provide the context required to understand the child” — a stage is meaningless without the programme, and programmes run in rounds that reuse the same document names. §5.5: “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders.”, so the round rather than the year carries the time signal; where a programme has run once, §5.8: “The canvas must support uneven depth because real file trees are not and should not be perfectly symmetrical.”

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| res.grant-proposal | the research slice owns the applicant's side of exactly this transaction. The documents overlap almost completely — the funder holds the application the applicant wrote — and the separating signal is which party's other files surround it, not anything on the page | §3.8: “The system must separate roles that happen to contain the same entity type.” |
| npo.grant-reporting-recipient | a monitoring report exists in both files at once: the recipient wrote it, the funder holds it. Neither copy is a better claim than the other | §6.9: “A file may have multiple valid organizational relationships, and the placement engine must preserve that complexity.” |
| fin.grants-received | the finance-admin slice treats a received grant as an income record; this domain treats the same award as programme administration. The finance view keeps the money, this view keeps the process | §3.11: “One file may hold facts from more than one domain without losing information.” |
| gov.procurement-tender | a competitive grant call and a tender have nearly identical document sets — call, submissions, scoring, award — and the separating signal is whether the funder is buying something or funding an activity, which is a question about intent | §4.8: the validator checks “that each fact or label belongs to an allowed domain schema” |

### Sensitivity

`potentially_sensitive` — Applications carry named applicants, their addresses, their finances and frequently the circumstances of the people they intend to help — §2.9's phrase “while treating addresses and message content as potentially sensitive”. Unsuccessful applications are the sharp end: the funder holds identifying material about organisations that never became recipients. handling classes are P7's — §8.4: “The system should classify data into handling classes before LLM escalation” — and none is assigned here

### Open question — Joseph's call, unresolved

> THE APPLICANT SIDE IS OWNED ELSEWHERE AND THE SEAM IS NOT CLEAN. The research slice owns `res.grant-proposal` and `res.grant-reporting`, this slice owns the funder side, and `fin.grants-received` owns the money. A charity applying for a public grant sits in none of them cleanly: it is not research, it is not the funder, and the file is more than an income record. Joseph decides whether a non-research applicant-side grant domain is missing from the catalogue or whether the research entries are meant to be read generically despite their prefix.

---

## `gov.procurement-tender` — Public procurement and tendering

A public body's competitive purchase — the notice, the tender documents, the bids received, evaluation and the decision to award.

**Provenance:** **proposal** — new; the design names nothing like it

**Cite:** No design sentence names procurement. §5.7 lists the template library's intended coverage — “covering common organizational situations such as academic programs, university applications, recruiting processes, client engagements, research workflows, financial records, travel, legal matters, creative projects, software repositories, personal administration, and photo collections” — and names nothing governmental names “client engagements” but from the supplier's side, not the buyer's

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `procurement_title` | string | the title of the requirement as printed on the notice | `direct` | §3.13 direct: “A direct fact was read from a reliable and explicit source, such as a content hash, EXIF timestamp, document title, or labeled form field.” — a document title. Procurement notices are reliably titled because they must be findable by bidders |
| `contracting_authority` | string | a public body running the procurement | `validated` | §3.8: “The system must separate roles that happen to contain the same entity type.” — the buying authority, the bidding suppliers and the incumbent supplier all appear as organisation names in the same pack, and only one of them is this field |
| `procurement_reference` | string | the tender reference exactly as printed | `direct` | §3.13 direct: “A direct fact was read from a reliable and explicit source, such as a content hash, EXIF timestamp, document title, or labeled form field.”. Reference formats are set per jurisdiction and per authority, so the field is a verbatim string with no asserted shape |
| `procedure_type` | string | open procedure | `possible` | Procedure types are named differently in every procurement regime and some regimes have procedures others lack, so no allow-list can be shipped and no rule can confirm a value against one. §3.13 possible: “A possible fact is a useful but insufficient clue” is the honest ceiling — see the open question |
| `stage` | string | evaluation | `validated` | Notice, clarification, bid, evaluation, award and standstill are the recurring stages; the stage is what distinguishes a draft specification from the issued one |
| `submission_deadline` | date | 2026-07-15 | `direct` | §3.10: “Date candidates should be identified with explicit regular expressions and then parsed without fuzzy matching.” — a labeled deadline field only. It is the field bidders search on and the one most often mis-parsed from prose |
| `document_role` | string | specification | `validated` | The work-type field, and the template's leaf dimension — a procurement pack is many documents under one reference, and the role is what makes any of them findable. §5.7 requires a template's dimensions to be drawn from the domain's allowed fact fields, so the level and the field must exist together. Confirmable from the same context-term list the deterministic recognisers use |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.4, §3.5):

- a procurement term in a title or heading zone — 'invitation to tender' | 'request for proposals' | 'contract notice' | 'prior information notice' | 'instructions to bidders' | 'evaluation criteria' — co-occurring with a labeled reference or deadline field
- a pricing-schedule structure detected as a labeled table of lots or line items co-occurring with a procurement term in the document title

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- a specification document with no procurement wrapper, identifiable only by prose addressed to prospective suppliers
- a clarification log whose subject must be read from question text
- a document that is a formal regulated procurement in one jurisdiction and an ordinary quotation exercise in another

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10):

- the word 'tender' — it is a legal-tender term, an adjective and a boat
- the word 'proposal' — the single most overloaded word in a mixed corpus; research, sales and marriage all use it
- a reference-shaped string alone. §3.10 is explicit that file names and documents “frequently contain numbers that look like years but are course identifiers, version numbers, build numbers, ZIP codes, or other unrelated values”
- an authority name alone. §4.9's warning generalises: “A university name alone should not create a group because Columbia can appear as an authoring school, course provider, target institution, employer, research venue, or merely a cited organization.”

### Work types

`contract notice`, `instructions to bidders`, `specification`, `pricing schedule`, `clarification log`, `bid received`, `evaluation record`, `award decision`, `standstill letter`, `unsuccessful-bidder letter`

### Grouping reasons (§4)

- one procurement across its notice, pack, bids, evaluation and award, joined by the procurement reference
- one bidder's submissions across the several documents of a single bid — §3.9: “The documents are content-incoherent but purpose-coherent.”

### Template (§5)

`procurement → stage → document role`

Time first: **no**

§5.5: “a parent dimension should provide the context required to understand the child” — 'evaluation' means nothing without the procurement. The contracting authority does not appear as a level because in the authority's own corpus it would be a collector with one child, which is what §5.7 forbids a template that would “use an author or organization merely as a collector” forbids; in a supplier's corpus it is the correct first level instead

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| career.client-proposal | a bid is a supplier's proposal and a buyer's received document; the career slice owns the supplier's side. The same PDF exists in both corpora | §3.8's worked pair: “A consulting document may mention the author’s firm and the client organization.” |
| biz.procurement-po | the finance-admin slice owns purchase orders and ordinary buying; this domain owns the regulated competitive process that precedes them. A purchase order issued under an awarded framework belongs to both | §3.11: “One file may hold facts from more than one domain without losing information.” |
| gov.contract-award-record | the award decision closes the tender and opens the contract record; the same document is the last item of one and the first of the other | §6.9: “A file may have multiple valid organizational relationships, and the placement engine must preserve that complexity.” |
| gov.grant-programme-administration | competitive grant calls and tenders produce the same document set; the separating signal is whether the authority is buying or funding | §4.8: the validator checks “that each fact or label belongs to an allowed domain schema” |

### Sensitivity

`none` — Procurement records are ordinarily about organisations rather than individuals, and much of the pack is published. Bids received before award are commercially confidential, which is a handling decision and handling classes are P7's — §8.4: “The system should classify data into handling classes before LLM escalation” — and none is assigned here

### Open question — Joseph's call, unresolved

> PROCEDURE TYPE HAS NO JURISDICTION-NEUTRAL ENUM. Procurement regimes do not share a procedure set: thresholds, mandatory notice types, standstill obligations and even whether an award may be challenged differ by regime, and some regimes have procedures that simply have no counterpart elsewhere. Writing `procedure_type` as a free string keeps the catalogue honest but means §3.6's validator has nothing to validate against. Joseph decides whether procurement ships jurisdiction-neutral with an unvalidated field, ships per-jurisdiction, or is held back.

---

## `gov.contract-award-record` — Public contract award and contract management records

The record of a public contract once awarded — the executed contract, the published award record, variations, performance reporting and closure.

**Provenance:** **proposal** — new; the design names nothing like it

**Cite:** No design sentence names contract award registers. §5.7 lists the template library's intended coverage — “covering common organizational situations such as academic programs, university applications, recruiting processes, client engagements, research workflows, financial records, travel, legal matters, creative projects, software repositories, personal administration, and photo collections” — and names nothing governmental names “legal matters” and “client engagements”; a published award record is neither

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `contract_title` | string | the title of the contract as printed on the front page | `direct` | §3.13 direct: “A direct fact was read from a reliable and explicit source, such as a content hash, EXIF timestamp, document title, or labeled form field.” — a document title |
| `contracting_authority` | string | the public body that awarded the contract | `validated` | §3.8: “The system must separate roles that happen to contain the same entity type.”: the authority and the supplier are the pair, and a subcontractor named in a schedule is neither |
| `supplier` | string | the organisation named as the awarded party | `direct` | §3.8's worked pair: “A consulting document may mention the author’s firm and the client organization.”. Direct only from a labeled parties block; a supplier name recovered from prose is not |
| `contract_reference` | string | the contract reference exactly as printed | `direct` | §3.13 direct: “A direct fact was read from a reliable and explicit source, such as a content hash, EXIF timestamp, document title, or labeled form field.”. Deliberately without a format example — award-register identifier schemes are jurisdiction-specific |
| `contract_period` | date range | 2026-09-01 to 2030-08-31 | `direct` | §3.10: “Date candidates should be identified with explicit regular expressions and then parsed without fuzzy matching.” from a labeled term or period field. The end date is the field that makes an expiring contract surface in time to do something about it |
| `document_role` | string | variation | `validated` | The work-type field. A contract corpus is dominated by variations and extensions that are meaningless apart from the contract they amend |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.4, §3.5):

- a contract-execution structure ('this agreement is made between' | 'the parties agree' | 'signed for and on behalf of' | 'schedule 1') co-occurring with an authority-shaped party name in the parties block
- an award-record structure detected as labeled award fields (an award date field together with a supplier field and a contract reference field) in a table or form region

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- a variation letter that never restates the contract it amends
- a performance report whose contract must be inferred from the service it describes
- a document that is a published award register row in one regime and an internal-only record in another

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10):

- the word 'contract' — employment, phone, construction and smart contracts all claim it
- 'schedule 1' — it appears in leases, policies, statutes and terms of business
- a currency amount — needs a contract reference or an authority party beside it
- a supplier name alone. §4.9's warning generalises: “A university name alone should not create a group because Columbia can appear as an authoring school, course provider, target institution, employer, research venue, or merely a cited organization.”; a supplier is also a bidder, a subcontractor and a cited comparator

### Work types

`executed contract`, `award notice`, `award register extract`, `variation`, `extension`, `performance report`, `service credit record`, `termination or closure record`

### Grouping reasons (§4)

- one contract across its execution, variations, reports and closure, joined by the contract reference
- one supplier across the contracts a body holds with them

### Template (§5)

`supplier → contract → document role`

Time first: **no**

§5.5: “a parent dimension should provide the context required to understand the child” — a variation is legible only under its contract. Supplier before contract is the one place in this slice where an organisation name is the right first level, because a body genuinely holds several contracts per supplier; it is not the collector pattern §3.8: “A folder should not become a collection point for everything produced by the same person or organization.” warns against. §5.5: “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders.”

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| gov.procurement-tender | the award decision is the last document of the tender and the first of the contract; both claims are legitimate | §6.9: “A file may have multiple valid organizational relationships, and the placement engine must preserve that complexity.” |
| legal.contracts | the finance-admin slice owns contracts generally; this domain owns them as public spending records with a published dimension. A file can be both without either being wrong | §3.11: “One file may hold facts from more than one domain without losing information.” |
| biz.vendor-management | supplier performance management is the same activity in a public body and a private one; the separating signal is whether the contract is a public award, which the performance report itself rarely says | §4.8: the validator checks “that each fact or label belongs to an allowed domain schema” |
| career.freelance-contract-work | an individual contracted to a public body holds their own copy of the same contract; the career slice owns their side | §3.8: “The system must separate roles that happen to contain the same entity type.” |

### Sensitivity

`none` — Award records are ordinarily published and concern organisations. Where a contract is with a named individual it carries their identity and payment details, which is a per-file property. handling classes are P7's — §8.4: “The system should classify data into handling classes before LLM escalation” — and none is assigned here

---

## `gov.planning-application` — Planning, zoning and development applications

An application to change the use or fabric of a specific piece of land or property, and everything the deciding authority produces in determining it.

**Provenance:** **proposal** — new; the design names nothing like it

**Cite:** No design sentence names planning. §5.7 lists the template library's intended coverage — “covering common organizational situations such as academic programs, university applications, recruiting processes, client engagements, research workflows, financial records, travel, legal matters, creative projects, software repositories, personal administration, and photo collections” — and names nothing governmental. The property-plus-case shape follows §3.8: “The system must separate roles that happen to contain the same entity type.”, with the applicant and the deciding authority as the pair

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `property` | string | the site address exactly as printed on the application | `validated` | The site is the one fact every document in the case carries and the only one a resident can be relied on to recognise. Confirmable when an address-shaped string co-occurs with a planning context term — an address alone is not enough, which is why the ceiling is not `direct` |
| `case_reference` | string | the application reference exactly as printed | `direct` | §3.13 direct: “A direct fact was read from a reliable and explicit source, such as a content hash, EXIF timestamp, document title, or labeled form field.” — a labeled reference field. The reference is the strongest grouping key in this domain and the catalogue asserts no format for it: application-numbering is set per authority, not per country |
| `deciding_authority` | string | the local planning authority named on the notice | `validated` | §3.8's worked pair: “A consulting document may mention the author’s firm and the client organization.” transposed: the authority and the applicant are the pair, and the agent acting for the applicant is a third role that must not collapse into either |
| `applicant` | string | the person or organisation named as applicant | `direct` | §3.13 direct: “A direct fact was read from a reliable and explicit source, such as a content hash, EXIF timestamp, document title, or labeled form field.” — a labeled applicant field on a form. §2.3: “Tables matter because resumes, forms, applications, invoices, and administrative documents often place their most useful information in cells rather than body paragraphs.” |
| `application_type` | string | change of use | `validated` | Application types are jurisdiction-defined and are not translations of one another; the field is kept because it changes which documents should exist, but its values cannot be enumerated neutrally |
| `decision` | string | approved with conditions | `validated` | The outcome is what the user is actually looking for years later. Confirmable from a decision-notice structure; a decision recovered from correspondence prose is not |
| `record_side` | string | held by the applicant | `llm_supported` | See the open question. This field exists to be honest that the product usually cannot fill it, not because a rule can. §3.11 permits “several additional fields used only for search, privacy protection, explanation, or later review” — never a folder dimension |
| `document_role` | string | decision notice | `validated` | The work-type field, and the template's leaf dimension — a case is a form, drawings, statements, responses and a decision, and the role is the only thing separating them. §5.7 requires a template's dimensions to be drawn from the domain's allowed fact fields, so the level and the field must exist together. Confirmable from the same context-term list the deterministic recognisers use |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.4, §3.5):

- a planning context term in a title or heading zone — 'planning application' | 'application for planning permission' | 'zoning' | 'development application' | 'notice of decision' | 'conditions' — co-occurring with an address-shaped site string or a labeled reference field
- a labeled application-reference field co-occurring with a deciding-authority name in a letterhead zone, which is the pairing that also lets the case be grouped
- a drawing-sheet structure detected as a title block carrying a labeled drawing number and a site address, co-occurring with a planning context term elsewhere in the case

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- a design and access statement or supporting report whose only case signal is the site address in prose
- a neighbour objection letter with no reference number
- a photograph of a site notice, where §2.7: “A screenshot is always a screenshot of something” applies in its OCR form: the notice is a notice of something and only OCR makes it one
- a document whose application type belongs to a planning system the recogniser has no vocabulary for

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10):

- an address-shaped string. It is the strongest signal in this domain and still not sufficient: the same address appears on utility bills, insurance schedules, tenancy agreements, deliveries and the user's own letterhead
- the word 'planning' — project plans, financial planning and event planning all claim it
- the word 'permission' — a consent form, a software permission and a school trip slip use it too
- a bare reference string. §3.10 is explicit that file names and documents “frequently contain numbers that look like years but are course identifiers, version numbers, build numbers, ZIP codes, or other unrelated values”
- a drawing number alone — engineering, architecture and manufacturing all number drawings

### Work types

`application form`, `site plan and drawings`, `supporting statement`, `consultee response`, `neighbour representation`, `officer report`, `decision notice`, `conditions discharge`, `appeal record`, `enforcement notice`

### Grouping reasons (§4)

- one case across its form, drawings, statements, responses and decision, joined by the case reference — §3.9: “The documents are content-incoherent but purpose-coherent.” fits this packet precisely
- one property across the successive applications made on it over years

### Template (§5)

`property → case → document role`

Time first: **no**

§5.5: “a parent dimension should provide the context required to understand the child” — a decision notice is legible only under its case, and a case only under its site. Property before case matters because a homeowner's corpus has one site and several cases, and §5.8: “The canvas must support uneven depth because real file trees are not and should not be perfectly symmetrical.” means that user's tree should collapse the property level away entirely. An authority's corpus is the mirror image: many sites, one case each. The dimension order is therefore correct for both and produces very different trees, which is the honest outcome

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| pers.home-tenure | a homeowner's planning file is part of the record of owning that home; nothing in a decision notice distinguishes the two readings, and for most personal corpora the household reading is the one the user wants | §3.11: “One file may hold facts from more than one domain without losing information.” |
| gov.permit-licensing-authority | building-control and similar consents run alongside a planning case on the same site with a different reference; the site is shared and the reference is not, so the reference must win | §4.8: “an application packet does not silently absorb a document with a conflicting target institution” |
| law.conveyancing | planning history is assembled into a conveyancing pack at sale; the pack's purpose claims the copies without the originals ceasing to be case documents | §6.9: “A file may have multiple valid organizational relationships, and the placement engine must preserve that complexity.” |
| gov.municipal-administration | the committee report on an application is a meeting paper and a case document at once | §3.11: “One file may hold facts from more than one domain without losing information.” |

### Sensitivity

`potentially_sensitive` — A planning case ties a named person to a specific property, to drawings of the inside of their home, and often to their reason for the change — §2.9's phrase “while treating addresses and message content as potentially sensitive” covers the address half directly. Much of this material is on a public register, which does not make the copy in someone's folder less identifying. handling classes are P7's — §8.4: “The system should classify data into handling classes before LLM escalation” — and none is assigned here

### Open question — Joseph's call, unresolved

> THE CITIZEN AND THE AUTHORITY HOLD THE SAME BYTES. This is the sharpest instance of a hazard that runs through the whole slice. An applicant's folder and the deciding authority's case file contain the same application form, the same drawings and the same decision notice. Three signals do separate them and none is a document fact: the authority's file additionally contains internal apparatus that never leaves the building — case-officer assessments, consultee responses, delegated-decision reports, redaction working copies; the authority's corpus is a caseload of many sites while the citizen's is one site with many documents; and the authority's copies arrive as a batch export from a case-management system rather than as things received one at a time. All three are §4 grouping observations about the corpus, not §3 facts about a file, and acting on them means inferring the user's institutional role from the shape of their filesystem. Joseph decides: does the product infer role, ask the user once at corpus level, or refuse to distinguish and let both readings coexist as §3.11's multi-domain facts?

---

## `gov.permit-licensing-authority` — Permits and licensing (issuing authority side)

An authority's record of granting, refusing, varying or revoking permissions to individuals and businesses, and the inspection and enforcement that follows.

**Provenance:** **proposal** — new; the design names nothing like it

**Cite:** No design sentence names licensing. §5.7 lists the template library's intended coverage — “covering common organizational situations such as academic programs, university applications, recruiting processes, client engagements, research workflows, financial records, travel, legal matters, creative projects, software repositories, personal administration, and photo collections” — and names nothing governmental. Written as the counterpart to the holder-side domain the finance-admin slice already owns, which is §3.8: “The system must separate roles that happen to contain the same entity type.”

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `permit_type` | string | food business registration | `validated` | The kind of permission is what makes the record legible; the same authority issues several unrelated kinds. Permit vocabularies are jurisdiction-defined and cannot be enumerated neutrally |
| `issuing_authority` | string | a local licensing authority | `validated` | §3.8: “The system must separate roles that happen to contain the same entity type.” — the issuer and the holder are the pair. This domain is written from the issuer's side |
| `holder` | string | the person or business named on the permit | `direct` | §3.13 direct: “A direct fact was read from a reliable and explicit source, such as a content hash, EXIF timestamp, document title, or labeled form field.” — a labeled holder or licensee field |
| `application_number` | string | the application or licence number exactly as printed | `direct` | §3.13 direct: “A direct fact was read from a reliable and explicit source, such as a content hash, EXIF timestamp, document title, or labeled form field.”. No format asserted; licence numbering is set per authority |
| `status` | string | granted subject to conditions | `validated` | Granted, refused, varied, suspended, revoked, lapsed. The status is the single fact that decides whether the document still means anything, and it is confirmable from a decision-structure heading |
| `valid_until` | date | 2027-03-31 | `direct` | §3.10: “Date candidates should be identified with explicit regular expressions and then parsed without fuzzy matching.” — a labeled expiry field only. This is the field that makes a licence surface before it lapses, which is the main reason a user keeps it |
| `premises_or_asset` | string | the address or asset the permission attaches to | `validated` | Many permissions attach to a place or a thing rather than to a person, which changes the grouping key entirely. Confirmable only alongside a permit context term |
| `document_role` | string | licence certificate issued | `validated` | The work-type field, and the template's leaf dimension — a permission file mixes the application, the grant, the conditions and years of inspections. §5.7 requires a template's dimensions to be drawn from the domain's allowed fact fields, so the level and the field must exist together. Confirmable from the same context-term list the deterministic recognisers use |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.4, §3.5):

- a licensing term in a title or heading zone — 'licence' | 'license' | 'permit' | 'registration certificate' | 'authorisation' | 'conditions of this licence' — co-occurring with a labeled holder field or a labeled expiry field
- a decision structure ('the authority has decided to' | 'granted subject to' | 'refused' | 'notice of variation') co-occurring with an application or licence number field
- an inspection-report structure detected as labeled inspection date and outcome fields co-occurring with a licence number
- an address-shaped premises string or a labeled asset identifier co-occurring with a licensing term in the same document, which is what lets the permission be attached to a place rather than only to a person

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- a reminder or renewal letter with no licence number, identifiable only from prose
- an enforcement letter that describes a breach without naming the permission breached
- a photographed licence certificate where the type must be read from OCR of a decorative certificate layout

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10):

- the word 'licence' or 'license' — software licences, driving licences, music licences and open-source licences dominate a mixed corpus
- the word 'permit' — it is also a verb
- a licence-shaped number alone. §3.10 is explicit that file names and documents “frequently contain numbers that look like years but are course identifiers, version numbers, build numbers, ZIP codes, or other unrelated values”
- an expiry date alone — subscriptions, cards, passports and warranties all carry one
- an authority name alone. §4.9's warning generalises: “A university name alone should not create a group because Columbia can appear as an authoring school, course provider, target institution, employer, research venue, or merely a cited organization.”

### Work types

`application received`, `grant or refusal notice`, `licence certificate issued`, `conditions schedule`, `variation record`, `renewal record`, `inspection report`, `enforcement notice`, `register extract`

### Grouping reasons (§4)

- one permission across its application, grant, conditions, renewals and inspections
- one holder or one premises across the several permissions attaching to it

### Template (§5)

`permit type → holder or premises → document role`

Time first: **no**

§5.5: “a parent dimension should provide the context required to understand the child” — a renewal is legible only under the permission it renews. Permit type first because an authority's corpus is organised by regime and a holder's by asset; §5.8: “The canvas must support uneven depth because real file trees are not and should not be perfectly symmetrical.” lets a single-permit holder collapse the type level

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| admin.licences-permits | the finance-admin slice owns the holder's copy of the licence. This is the same certificate seen from the other end of the transaction, and the certificate itself carries nothing that says which end holds it | §3.8's worked pair: “A consulting document may mention the author’s firm and the client organization.” |
| gov.planning-application | a planning consent is a permission, and in some systems the same office issues both; the separating signal is the reference series, not the vocabulary | §4.8: “an application packet does not silently absorb a document with a conflicting target institution” |
| gov.professional-regulator | a licence to practise a profession is issued under a professional regime rather than a premises or activity regime; the separating signal is whether the permission attaches to a person's qualifications | §4.8: the validator checks “that each fact or label belongs to an allowed domain schema” |
| gov.environmental-regulation | environmental permits are licensing in form and regulation in function; where monitoring and emissions reporting attach, the environmental domain describes the file better | §3.11: “One file may hold facts from more than one domain without losing information.” |

### Sensitivity

`potentially_sensitive` — The record ties a named person or business to a place, an activity and often a compliance history — §2.9's phrase “while treating addresses and message content as potentially sensitive” for the address half and §4.9: “Rare but sensitive files such as passports, visas, and legal documents may be surfaced as protected records even when they do not meet a normal group-size threshold.” for the enforcement half. handling classes are P7's — §8.4: “The system should classify data into handling classes before LLM escalation” — and none is assigned here

### Open question — Joseph's call, unresolved

> PERMIT TYPES CANNOT BE ENUMERATED WITHOUT A JURISDICTION, AND THE HOLDER-SIDE DOMAIN ALREADY EXISTS. Two decisions. First, which activities require a permission, which tier of government grants it and what the permission is called are all jurisdiction-set; a neutral `permit_type` is a free string with no allow-list. Second, `admin.licences-permits` in the finance-admin slice already owns the holder's copy. Either this catalogue keeps two domains for one certificate and accepts that the recogniser cannot choose between them from the document alone, or the two merge and the side becomes a field. Joseph decides which.

---

## `gov.public-records-foi` — Public records access and information requests

A request for recorded information held by a public body, and the response — including the disclosed material, redactions, refusals and any review or appeal.

**Provenance:** **proposal** — new; the design names nothing like it

**Cite:** No design sentence names information rights. §5.7 lists the template library's intended coverage — “covering common organizational situations such as academic programs, university applications, recruiting processes, client engagements, research workflows, financial records, travel, legal matters, creative projects, software repositories, personal administration, and photo collections” — and names nothing governmental. The request-and-response pair is §3.8: “The system must separate roles that happen to contain the same entity type.”

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `request_reference` | string | the request reference exactly as printed | `direct` | §3.13 direct: “A direct fact was read from a reliable and explicit source, such as a content hash, EXIF timestamp, document title, or labeled form field.” — a labeled reference field. The reference is what binds a request, its response and its disclosed bundle together |
| `public_body` | string | the authority holding the information | `validated` | §3.8: “The system must separate roles that happen to contain the same entity type.” — the body holding the information and the person requesting it are the pair |
| `requester` | string | the person or organisation who made the request | `direct` | §3.13 direct: “A direct fact was read from a reliable and explicit source, such as a content hash, EXIF timestamp, document title, or labeled form field.” from a labeled requester field. Whether the requester's identity may be retained at all is a privacy question rather than an extraction one |
| `request_subject` | string | correspondence about a road closure | `llm_supported` | What was asked for is always prose — it is the request. §3.5: the model “can only propose facts that belong to the active domain schema, and it must cite exact supporting evidence already extracted from the file.” |
| `outcome` | string | disclosed in part | `validated` | Disclosed, disclosed in part, refused, not held, transferred. This decides whether the bundle beside it is the answer or an explanation of why there is none |
| `response_date` | date | 2026-08-03 | `direct` | §3.10: “Date candidates should be identified with explicit regular expressions and then parsed without fuzzy matching.” — a labeled response date. Statutory response periods differ by jurisdiction so no period is asserted, only the date |
| `record_side` | string | held by the requester | `llm_supported` | See the open question. §3.11 permits “several additional fields used only for search, privacy protection, explanation, or later review” |
| `document_role` | string | disclosed bundle | `validated` | The work-type field, and the template's leaf dimension — the request, the response and the bundle are three objects sharing one reference. §5.7 requires a template's dimensions to be drawn from the domain's allowed fact fields, so the level and the field must exist together. Confirmable from the same context-term list the deterministic recognisers use |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.4, §3.5):

- an information-rights term in a title or heading zone — 'freedom of information' | 'information request' | 'access to information' | 'request for records' | 'public records request' — co-occurring with a labeled reference field or a public-body name
- a disposition term in a response letter's heading or decision zone — 'disclosed in full' | 'disclosed in part' | 'refused' | 'information not held' | 'transferred' — co-occurring with a labeled request reference, which is what confirms the outcome field
- a refusal or exemption structure detected as a labeled exemption or exception citation co-occurring with an information-rights term
- a redaction marking pattern (blacked-out regions detected at extraction, or a labeled 'redacted' annotation) co-occurring with a request reference

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- a disclosed bundle with no covering letter, whose only signal that it is a disclosure is redaction and heterogeneity
- a request written as an ordinary email with no statutory language
- a document whose regime is named differently in the requester's jurisdiction than in the body's

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10):

- the word 'request' — the highest-frequency administrative word there is
- the presence of redaction — legal, medical and commercial documents are redacted constantly
- the word 'disclosure' — it is a financial term, a legal-practice term and a privacy notice heading
- a public body's name alone. §4.9's warning generalises: “A university name alone should not create a group because Columbia can appear as an authoring school, course provider, target institution, employer, research venue, or merely a cited organization.”

### Work types

`request`, `acknowledgement`, `response letter`, `disclosed bundle`, `refusal notice`, `internal review request`, `review outcome`, `appeal or complaint record`, `disclosure log extract`

### Grouping reasons (§4)

- one request across its acknowledgement, response, bundle and review, joined by the request reference
- one subject across the several requests a person made about it to different bodies

### Template (§5)

`public body → request → document role`

Time first: **no**

§5.5: “a parent dimension should provide the context required to understand the child” — a disclosed bundle is meaningless without the request that produced it. Body before request because a requester's corpus groups naturally by who they asked. §5.5: “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders.”

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| gov.public-authority-record | a disclosed bundle contains the authority's own records, which individually belong to whatever domain they came from; the bundle's purpose does not overwrite its contents' domains | §3.11: “One file may hold facts from more than one domain without losing information.” |
| civic.advocacy-campaign | campaigns use information requests as a research method; the request is then both a records request and a campaign artefact | §3.9: “Purpose must be a first-class facet.” |
| res.research-project | a researcher's request is a data-collection step in a project; the separating signal is a project identifier, not the request | §4.8: the validator checks “that each fact or label belongs to an allowed domain schema” |
| law.discovery-requests | litigation disclosure and an information-rights request are different regimes that produce similar bundles; the separating signal is a matter reference and a court, not the redactions | §4.8: “an application packet does not silently absorb a document with a conflicting target institution” |

### Sensitivity

`potentially_sensitive` — Both halves carry risk: a request reveals what its author wanted to know, and a disclosed bundle routinely contains third-party personal data that survived redaction. §2.9's phrase “while treating addresses and message content as potentially sensitive” covers the second directly. handling classes are P7's — §8.4: “The system should classify data into handling classes before LLM escalation” — and none is assigned here

### Open question — Joseph's call, unresolved

> DOES A DISCLOSED BUNDLE INHERIT ITS OWN CONTENTS' DOMAINS, AND MAY IT REACH A MODEL? A bundle disclosed to a requester is a heterogeneous set of someone else's records — meeting papers, emails, spreadsheets — that the requester now holds. It is purpose-coherent as one disclosure and content-incoherent as a pile of unrelated administrative material, which is exactly §3.9's tension. Filing it by its contents scatters it; filing it by the request buries records the user obtained precisely so they could read them. Separately, the bundle contains third-party data the user did not choose to receive, so whether it may enter a model prompt at all is a privacy decision Joseph must make and not a handling class this catalogue may assign.

---

## `gov.census-statistical-programme` — Census and official statistics programmes

The production of official statistics — the instrument, the collection round, the methodology, the published outputs and the microdata access that surrounds them.

**Provenance:** **proposal** — new; the design names nothing like it

**Cite:** No design sentence names statistical programmes. §5.7 lists the template library's intended coverage — “covering common organizational situations such as academic programs, university applications, recruiting processes, client engagements, research workflows, financial records, travel, legal matters, creative projects, software repositories, personal administration, and photo collections” — and names nothing governmental. The programme-and-round shape borrows from §3.3 gives rules “routing obvious files into plausible domains” and sends the rest to the model

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `programme` | string | a national household survey | `validated` | The statistical programme is the container; outputs, methodology and instruments all belong to one. Confirmable with a statistics context term beside it |
| `producing_body` | string | a national statistics office | `validated` | §3.8: “The system must separate roles that happen to contain the same entity type.” — the producer, the sponsoring department and the analyst reusing the data are three roles carrying organisation names |
| `reference_period` | string | the collection period or reference date as printed | `direct` | §3.13 direct: “A direct fact was read from a reliable and explicit source, such as a content hash, EXIF timestamp, document title, or labeled form field.” — a labeled reference-period field. This is the field statistical users actually key on, and it is routinely different from the publication date, which is why both are kept |
| `output_type` | string | statistical bulletin | `validated` | Bulletin, table, methodology note, microdata file and quality report are different objects with different lifetimes |
| `geography_level` | string | the smallest area the output is published for | `llm_supported` | §3.11 permits “several additional fields used only for search, privacy protection, explanation, or later review” — a search field. Geography hierarchies are jurisdiction-specific and their level names do not translate |
| `publication_date` | date | 2026-11-19 | `direct` | §3.10: “Date candidates should be identified with explicit regular expressions and then parsed without fuzzy matching.” — a labeled release date only. §3.10: “Date extraction should be deliberately narrow.” |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.4, §3.5):

- a statistics context term in a title or heading zone — 'statistical bulletin' | 'census' | 'official statistics' | 'methodology note' | 'quality report' | 'reference period' — co-occurring with a producing-body name or a labeled release-date field
- the programme name taken from the title zone only when a statistics context term is present in the same zone, which is §3.7: “It should use positional weighting because a value in a filename or document title carries more meaning than the same value in a footer or a late body-page reference.” doing the work a gazetteer cannot
- a statistical-table structure detected as labeled row and column headers together with a footnote block, co-occurring with a statistics context term. §2.3: “Tables matter because resumes, forms, applications, invoices, and administrative documents often place their most useful information in cells rather than body paragraphs.”

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- a spreadsheet of aggregated figures with no title, whose statistical character must be read from sheet names and header rows
- a questionnaire whose statistical purpose is stated only in an introductory paragraph
- a document that is a census in one country and a population register extract in another, which are genuinely different objects rather than different words

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10):

- the word 'census' — it names a software feature, a network scan and a school headcount
- the presence of a table — every administrative corpus is full of tables
- a reference year alone. §3.10 is explicit that file names and documents “frequently contain numbers that look like years but are course identifiers, version numbers, build numbers, ZIP codes, or other unrelated values”
- a producing body's name alone. §4.9's warning generalises: “A university name alone should not create a group because Columbia can appear as an authoring school, course provider, target institution, employer, research venue, or merely a cited organization.”

### Work types

`questionnaire or instrument`, `collection guidance`, `methodology note`, `statistical bulletin`, `data table`, `microdata file`, `quality report`, `revision notice`, `microdata access agreement`

### Grouping reasons (§4)

- one programme across one collection round's instrument, outputs and quality material
- one output across its revisions

### Template (§5)

`programme → reference period → output type`

Time first: **no**

§5.5: “a parent dimension should provide the context required to understand the child” — an output type is meaningless without the programme and a table is ambiguous without its reference period. This is the one entry in the slice where a period level is genuinely load-bearing rather than calendar scatter, because statistical outputs are defined by their reference period; §5.5: “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders.” still applies in that the programme comes first

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| res.dataset | a microdata file is a research dataset in use and a statistical output in origin; the separating signal is whether the file carries a project identifier or a programme and reference period | §3.11: “Research files may use project, stage, artifact type, lab, and venue.” |
| gov.public-health-administration | health statistics are produced under both regimes; the separating signal is whether the output is a statistical release or a surveillance report to an operational audience | §4.8: the validator checks “that each fact or label belongs to an allowed domain schema” |
| soft.dataset-artifact | a downloaded statistical table used as an input to code is a data artefact in a repository; its statistical provenance does not follow it into the repo | §3.11: “One file may hold facts from more than one domain without losing information.” |
| gov.policy-development | statistics gathered as evidence for a policy question are both; the topic is statistical, the purpose is the policy — §3.9: “Topic answers what a file is about, while purpose answers what the file was for.” | §3.9: “Purpose must be a first-class facet.” |

### Sensitivity

`potentially_sensitive` — Published aggregates are not sensitive; individual returns and microdata are among the most sensitive material any public body holds, and both live under one programme. The marking is set by the domain's worst case rather than its typical one — §4.9: “Rare but sensitive files such as passports, visas, and legal documents may be surfaced as protected records even when they do not meet a normal group-size threshold.”. handling classes are P7's — §8.4: “The system should classify data into handling classes before LLM escalation” — and none is assigned here

### Open question — Joseph's call, unresolved

> COMPLETED INDIVIDUAL RETURNS AND PUBLISHED AGGREGATES SHOULD PROBABLY NOT BE ONE DOMAIN. A household's own completed census return and a published statistical bulletin share a programme and share nothing else: one identifies a family at an address, the other is a public good. Splitting them makes two domains where the evidence supports one; keeping them together means the domain's sensitivity marking is driven by a file type most users will never hold. Joseph decides whether the individual-return case is a separate domain, a personal-records domain, or a case the product declines to model.

---

## `gov.elections-administration` — Elections administration

The conduct of an election or referendum by the body responsible for it — registration, nominations, ballots, polling operations, counting and declaration.

**Provenance:** **proposal** — new; the design names nothing like it

**Cite:** No design sentence names elections. §5.7 lists the template library's intended coverage — “covering common organizational situations such as academic programs, university applications, recruiting processes, client engagements, research workflows, financial records, travel, legal matters, creative projects, software repositories, personal administration, and photo collections” — and names nothing governmental. Modelled as an event-shaped administrative domain, which §5.3: “The product opens an accepted branch and proposes one or more domain templates based on the groups and facts that already belong inside it.” would have to propose from the evidence

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `election` | string | the name of the poll as printed on its notice | `validated` | The poll is the event everything belongs to. Its label almost always embeds a date, which is why the template's first level is an event rather than a year |
| `administering_body` | string | the body responsible for conducting the poll | `validated` | §3.8: “The system must separate roles that happen to contain the same entity type.” — the administering body, the candidates, the parties and the observers all appear as names in the same pack and only one is this field |
| `electoral_area` | string | the district or constituency named on the notice | `possible` | The area is the second organising dimension, and it is the clearest case in the slice of a field a rule cannot confirm: an area name has no detectable shape, and the gazetteer that would recognise one is jurisdiction-set and therefore unbuildable until the scope question is answered. §3.13 possible: “A possible fact is a useful but insufficient clue” |
| `function` | string | nomination | `validated` | Registration, nomination, ballot production, postal voting, polling, counting and declaration are the recurring functions, and the function is the work-type field for this domain |
| `poll_date` | date | 2026-05-07 | `direct` | §3.10: “Date candidates should be identified with explicit regular expressions and then parsed without fuzzy matching.” — a labeled date of poll only. §3.10: “Date extraction should be deliberately narrow.” |
| `jurisdiction` | string | the polity whose electoral law governs the poll | `possible` | Electoral systems differ in every dimension that matters here — who administers, what documents exist, what may be published. §3.13 possible: “A possible fact is a useful but insufficient clue” |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.4, §3.5):

- an elections term in a title or heading zone — 'notice of election' | 'nomination paper' | 'statement of persons nominated' | 'ballot paper' | 'polling station' | 'declaration of result' — co-occurring with an administering-body name or a labeled date-of-poll field
- a result-table structure detected as labeled candidate and vote-count columns co-occurring with an electoral-area name. §2.3: “Tables matter because resumes, forms, applications, invoices, and administrative documents often place their most useful information in cells rather than body paragraphs.”

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- a polling-station operations document whose election is never named
- a training pack for poll workers that reads as generic instructional material
- a document whose function has no counterpart in the reader's electoral system, which is a genuine mismatch rather than an extraction failure

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10):

- the word 'election' — it names a corporate board vote, a union ballot, a tax election and a software option
- the word 'ballot' — clubs, unions and committees all ballot
- a candidate's name — a person's name is the weakest possible anchor and §3.8: “It should avoid using authorship or creator identity as a destination dimension.”
- a poll-shaped date alone. §3.10 is explicit that file names and documents “frequently contain numbers that look like years but are course identifiers, version numbers, build numbers, ZIP codes, or other unrelated values”

### Work types

`notice of election`, `nomination paper`, `candidate statement`, `ballot paper proof`, `postal voting record`, `polling station pack`, `count record`, `declaration of result`, `election expenses return`, `electoral register extract`

### Grouping reasons (§4)

- one poll across its notice, nominations, operations and result
- one electoral area across successive polls

### Template (§5)

`election → electoral area → function`

Time first: **no**

§5.5: “a parent dimension should provide the context required to understand the child” — a count record is legible only under its poll and area. The election level looks like a date level and is not: it is an event identifier whose label happens to contain a date, in the same way a photo event's label does. §5.5: “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders.” still governs the ordering of everything below it. NOTE that the area level is backed only by a `possible` fact, and §3.14 says templates use validated facts, so this level should be offered only once the user has confirmed the area label

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| civic.political-campaign | a nomination paper is an administrative record for the returning body and a campaign document for the candidate; the same form sits in both files | §3.8's worked pair: “A consulting document may mention the author’s firm and the client organization.” |
| gov.municipal-administration | the administering body is usually also the local authority, so its election files and its committee files share a letterhead and nothing else | §4.8: the validator checks “that each fact or label belongs to an allowed domain schema” |
| gov.census-statistical-programme | an electoral register and a population statistic are both population data with completely different legal characters; the separating signal is whether the file is a register of named electors | §4.8: “an application packet does not silently absorb a document with a conflicting target institution” |

### Sensitivity

`potentially_sensitive` — An electoral register is a list of named people at their home addresses, which is §2.9's phrase “while treating addresses and message content as potentially sensitive” at its most literal, and §2.9 on address-book data: it “should normally be privacy-protected rather than used to create folder proposals” applies to the same shape of data. handling classes are P7's — §8.4: “The system should classify data into handling classes before LLM escalation” — and none is assigned here

### Open question — Joseph's call, unresolved

> MAY A REGISTER OF NAMED ELECTORS BE INDEXED AT ALL? An electoral register, a postal-voting list and a marked register are bulk personal data about people who are not the user, held for a statutory purpose and often subject to rules about copying and retention that differ by jurisdiction. The product's ordinary behaviour — extract, index, retain, propose a folder — may be the wrong behaviour for this file type entirely. This is not a handling class; it is a prior question about whether the domain should exist. Joseph decides.

---

## `civic.political-campaign` — Political campaigning and party organising

The files of running for office or organising a party or campaign — nominations, canvassing, literature, volunteers, donations and regulated spending returns.

**Provenance:** **proposal** — new; the design names nothing like it

**Cite:** No design sentence names political activity. §5.7 lists the template library's intended coverage — “covering common organizational situations such as academic programs, university applications, recruiting processes, client engagements, research workflows, financial records, travel, legal matters, creative projects, software repositories, personal administration, and photo collections” — and names nothing governmental. Structurally a campaign in the sense the career slice uses for a job-search campaign, per §3.3 gives rules “routing obvious files into plausible domains” and sends the rest to the model

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `campaign` | string | the campaign or candidacy as the user names it | `llm_supported` | A campaign rarely names itself in a labeled field; it is named in prose and in folder names. §3.9: “Purpose may be supported strongly by an existing user-created folder name or explicit language in a form or portal.” — an existing folder is often the strongest evidence this domain has |
| `organisation` | string | the party, campaign committee or independent candidacy | `validated` | §3.8: “The system must separate roles that happen to contain the same entity type.” — the campaigning organisation, the regulator receiving its returns and the printer named on its literature are three different roles |
| `function` | string | canvassing | `validated` | Nomination, canvassing, literature, events, fundraising, volunteers and compliance returns are the recurring functions and the work-type field for this domain |
| `electoral_area` | string | the district the campaign is contesting | `possible` | Same limit as on gov.elections-administration: an area name has no shape a rule can match and no gazetteer can be shipped without a jurisdiction. §3.13 possible: “A possible fact is a useful but insufficient clue” |
| `poll_date` | date | 2026-05-07 | `direct` | §3.10: “Date candidates should be identified with explicit regular expressions and then parsed without fuzzy matching.” — from a labeled field only. It is the fact that separates one candidacy from the next in the same area |
| `document_role` | string | canvassing record | `validated` | The work-type field, and the template's leaf dimension — a campaign produces literature, records and returns that share nothing but the campaign. §5.7 requires a template's dimensions to be drawn from the domain's allowed fact fields, so the level and the field must exist together. Confirmable from the same context-term list the deterministic recognisers use |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.4, §3.5):

- a campaign term in a title or heading zone — 'nomination' | 'canvass' | 'campaign literature' | 'imprint' | 'election expenses' | 'donation return' — co-occurring with a party or campaign organisation name
- a regulated-return structure detected as labeled expense or donation columns co-occurring with a named campaign and a labeled reporting period

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- a leaflet whose political character is obvious to a reader and expressed nowhere as a labeled field
- a canvassing spreadsheet with no title, whose purpose must be read from column headers
- a supporter email that is indistinguishable in structure from any other mailing list message

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10):

- the word 'campaign' — marketing, fundraising, military and advertising campaigns all outnumber political ones
- a party name — it appears in news clippings, academic writing and unrelated correspondence
- the word 'vote' — used constantly in committees, product feedback and social media exports
- a person's name. §3.8: “It should avoid using authorship or creator identity as a destination dimension.”

### Work types

`nomination paper`, `campaign plan`, `canvassing record`, `literature and artwork`, `event record`, `donation record`, `expenses return`, `volunteer roster`, `press release`

### Grouping reasons (§4)

- one candidacy or campaign across its nomination, literature, canvassing and returns — §3.9: “The documents are content-incoherent but purpose-coherent.”
- one regulated reporting period across the records that support its return

### Template (§5)

`campaign → function → document role`

Time first: **no**

§5.5: “a parent dimension should provide the context required to understand the child” — 'canvassing' is meaningless without the campaign. The organisation does not lead because for most users there is only one, which §5.7 forbids a template that would “use an author or organization merely as a collector” rules out as a level. The campaign level is backed by an `llm_supported` fact against §3.14's rule that templates use validated facts, so it should come from an existing folder name or a user-confirmed label rather than from a rule: §3.9: “Purpose may be supported strongly by an existing user-created folder name or explicit language in a form or portal.”, and §5.10: “A carefully curated existing folder should be treated as a strong expression of user intent.”

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| gov.elections-administration | nomination papers and expenses returns are filed with the administering body and held by the campaign; the same document, two sides | §3.8's worked pair: “A consulting document may mention the author’s firm and the client organization.” |
| civic.advocacy-campaign | an issue campaign and an electoral campaign use the same tactics and produce the same artefacts; the separating signal is whether a poll and a candidacy are involved, which literature often does not say | §4.8: the validator checks “that each fact or label belongs to an allowed domain schema” |
| npo.fundraising-donor | political donation records and charitable donor records are structurally identical and legally different; the separating signal is the receiving organisation's character | §4.8: “an application packet does not silently absorb a document with a conflicting target institution” |
| career.job-search-campaign | standing for office is a candidacy in both senses; where the user is seeking a paid post the career slice's campaign shape may fit better than this one | §3.11: “One file may hold facts from more than one domain without losing information.” |

### Sensitivity

`potentially_sensitive` — Canvassing records, membership lists and donation records tie named individuals to a political position at an address — §2.9's phrase “while treating addresses and message content as potentially sensitive”, and §2.9 on address-book data: it “should normally be privacy-protected rather than used to create folder proposals” describes the canvassing file exactly. handling classes are P7's — §8.4: “The system should classify data into handling classes before LLM escalation” — and none is assigned here

### Open question — Joseph's call, unresolved

> MAY POLITICAL AFFILIATION BE A FOLDER DIMENSION? A tree with a party name as a visible folder level publishes the user's politics to anyone who opens their file manager, to any backup, and to any screen-share. The same is true of a canvassing file that records neighbours' voting intentions. The product has no concept of a folder label that is more revealing than the file inside it, and this domain is where that gap first bites. Joseph decides whether politically revealing labels are permitted as folder levels, permitted only under an explicit choice, or never proposed.

---

## `gov.constituent-casework` — Constituent and citizen casework

An elected representative's or ombudsman's office handling an individual's problem with a public body — the approach, the authorisation, the correspondence chased and the outcome.

**Provenance:** **proposal** — new; the design names nothing like it

**Cite:** No design sentence names casework. §5.7 lists the template library's intended coverage — “covering common organizational situations such as academic programs, university applications, recruiting processes, client engagements, research workflows, financial records, travel, legal matters, creative projects, software repositories, personal administration, and photo collections” — and names nothing governmental. The case-per-person shape mirrors the law slice's matter file, which is itself an §3.3 gives rules “routing obvious files into plausible domains” and sends the rest to the model case

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `case_reference` | string | the office's own case reference as printed | `direct` | §3.13 direct: “A direct fact was read from a reliable and explicit source, such as a content hash, EXIF timestamp, document title, or labeled form field.” — a labeled reference field, and the only reliable grouping key when the constituent's name must not be used as one |
| `constituent` | string | the named person the case is about | `direct` | §3.8: “The system must separate roles that happen to contain the same entity type.” — the constituent, the representative's office and the body being chased are three roles. The constituent is a third party, not the user, which is what makes this domain unlike almost everything else in the catalogue |
| `representative_office` | string | the office handling the case | `validated` | §3.8's worked pair: “A consulting document may mention the author’s firm and the client organization.” |
| `issue_category` | string | housing repairs | `llm_supported` | What the case is about is prose, and the categories offices use are local conventions. §3.5: the model “can only propose facts that belong to the active domain schema, and it must cite exact supporting evidence already extracted from the file.” |
| `body_approached` | string | the public body the office wrote to | `validated` | The third role. It is the field that connects a casework file to the authority-side record of the same complaint |
| `status` | string | closed — resolved | `possible` | Open, awaiting reply, escalated, closed. In a caseload the status is what makes the corpus navigable, and it is also almost never written on any single document — it is a property of the file that a reader infers from the last thing in it. §3.13 possible: “A possible fact is a useful but insufficient clue” |
| `document_role` | string | letter to body | `validated` | The work-type field, and the template's leaf dimension — a case is an approach, an authorisation, letters both ways and an outcome. §5.7 requires a template's dimensions to be drawn from the domain's allowed fact fields, so the level and the field must exist together. Confirmable from the same context-term list the deterministic recognisers use |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.4, §3.5):

- a casework term in a title or heading zone — 'casework' | 'on behalf of my constituent' | 'authority to act' | 'complaint reference' | 'ombudsman' — co-occurring with a labeled case-reference field
- an authorisation-form structure detected as labeled consent and signature fields co-occurring with a representative office name
- an authority-shaped name in the addressee zone co-occurring with a casework term in the body, which is what confirms the body approached rather than the office writing

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- an ordinary letter to an authority whose casework character is visible only from the phrase pattern of writing on someone else's behalf
- an email thread where the constituent, the office and the authority all appear and the roles must be read from who is addressing whom. §3.8: “The system must separate roles that happen to contain the same entity type.”
- a file that is casework in a system with elected constituency representatives and an ombudsman complaint in a system without them

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10):

- the word 'case' — legal, medical, support-ticket and packaging senses all outnumber this one
- the word 'complaint' — every consumer and HR corpus is full of them
- a constituent's name. §3.8: “It should avoid using authorship or creator identity as a destination dimension.”, and a person's name is the weakest anchor in the catalogue
- an authority's name alone. §4.9's warning generalises: “A university name alone should not create a group because Columbia can appear as an authoring school, course provider, target institution, employer, research venue, or merely a cited organization.”

### Work types

`initial approach`, `authority to act`, `letter to body`, `reply from body`, `case note`, `escalation`, `outcome letter`, `closure record`

### Grouping reasons (§4)

- one case across its approach, authorisations, correspondence and outcome, joined by the case reference
- one body across the cases an office has open with it, which is how systemic problems become visible

### Template (§5)

`case → document role`

Time first: **no**

Deliberately shallow. §5.5: “a parent dimension should provide the context required to understand the child” is satisfied by the case alone, and a deeper tree would require a level naming either the constituent — which puts third parties' names in the filesystem — or the issue category, which is an unvalidatable prose field. §5.8: “The canvas must support uneven depth because real file trees are not and should not be perfectly symmetrical.” is the licence to stop here

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| gov.public-authority-record | the authority's reply is both a casework document and an authority record; the casework claim comes from purpose rather than content — §3.9: “Topic answers what a file is about, while purpose answers what the file was for.” | §3.9: “Purpose must be a first-class facet.” |
| gov.social-services-casework | both are case files about a named person and a public service. The separating signal is whether the office holds statutory responsibility for the person or is advocating on their behalf, which the correspondence rarely states | §4.8: the validator checks “that each fact or label belongs to an allowed domain schema” |
| law.matter-file | a matter file and a casework file are the same shape; the separating signal is a retainer and a fee, not the correspondence | §4.8: “an application packet does not silently absorb a document with a conflicting target institution” |
| pers.correspondence | for the constituent themselves the whole exchange is personal correspondence about their own problem, with no case apparatus at all | §3.8: “The system must separate roles that happen to contain the same entity type.” |

### Sensitivity

`potentially_sensitive` — A caseload is bulk personal data about people who are not the user, routinely including health, housing, immigration and financial circumstances. §2.9's phrase “while treating addresses and message content as potentially sensitive” and §4.9: “Rare but sensitive files such as passports, visas, and legal documents may be surfaced as protected records even when they do not meet a normal group-size threshold.” both apply, and §8.4: “Paths, complete extracted text, OCR output, file hashes, image EXIF, GPS, user edits, group memberships, and raw sensitive values should remain local.” is the operative constraint. handling classes are P7's — §8.4: “The system should classify data into handling classes before LLM escalation” — and none is assigned here

### Open question — Joseph's call, unresolved

> SHOULD THE PRODUCT ORGANISE A CASELOAD OF OTHER PEOPLE'S RECORDS AT ALL? Every other domain in this catalogue concerns the user's own affairs or their organisation's. A caseworker's corpus is hundreds of third parties' most sensitive circumstances, held under a duty the product knows nothing about, and the ordinary pipeline would extract it, index it, retain the evidence and propose folder names derived from it. That is a decision about scope, not about handling, and this catalogue must not make it. Joseph decides whether professional caseload corpora are in scope, out of scope, or in scope only under an explicit local-only mode.

---

## `gov.international-development-programme` — International development programmes

A funded development or humanitarian programme delivered in another country — the design, the implementing agreement, delivery reporting, monitoring and evaluation.

**Provenance:** **proposal** — new; the design names nothing like it

**Cite:** No design sentence names development programmes. §5.7 lists the template library's intended coverage — “covering common organizational situations such as academic programs, university applications, recruiting processes, client engagements, research workflows, financial records, travel, legal matters, creative projects, software repositories, personal administration, and photo collections” — and names nothing governmental. The programme-plus-partner shape follows §3.8: “The system must separate roles that happen to contain the same entity type.”

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `programme` | string | the programme title as printed on the design document | `validated` | The programme is the container. Confirmable when a programme title co-occurs with a development context term |
| `funder` | string | a bilateral or multilateral donor | `validated` | §3.8: “The system must separate roles that happen to contain the same entity type.” — donor, implementing partner, host-government counterpart and evaluator are four distinct roles that all appear as organisation names on a single cover page |
| `implementing_partner` | string | the organisation delivering the programme | `validated` | §3.8's worked pair: “A consulting document may mention the author’s firm and the client organization.” — the pair here is donor and partner, and it is the pair most often collapsed by mistake |
| `country_or_region` | string | the country of delivery as named in the document | `validated` | The delivery geography is the second organising dimension. Confirmable only with a development context term beside it — a country name alone is worthless as a signal |
| `document_role` | string | annual review | `validated` | Business case, agreement, workplan, progress report, review and evaluation are the recurring set |
| `reporting_period` | date range | 2026-01-01 to 2026-12-31 | `direct` | §3.10: “Date candidates should be identified with explicit regular expressions and then parsed without fuzzy matching.” — a labeled reporting-period field only |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.4, §3.5):

- a development context term in a title or heading zone — 'implementing partner' | 'logframe' | 'theory of change' | 'annual review' | 'beneficiaries' | 'humanitarian response' — co-occurring with a named programme or a donor-shaped organisation name
- a results-framework structure detected as labeled indicator, baseline and target columns co-occurring with a programme title. §2.3: “Tables matter because resumes, forms, applications, invoices, and administrative documents often place their most useful information in cells rather than body paragraphs.”
- a country name matched on a word boundary against a country list — one of the few gazetteers this slice can ship, because countries are not jurisdiction-relative — co-occurring with a development context term. §3.7: “It should use word-boundary matching rather than substring matching.”

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- a field report whose programme is never named and must be inferred from the activities described
- a partner's own narrative report that reads as ordinary charity reporting
- a document whose funding instrument is a grant in one donor's vocabulary and a contract in another's, which changes the domain rather than the wording

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10):

- a country name — it appears in travel documents, news, address blocks and academic writing constantly
- the word 'development' — software, property, professional and child development all claim it, and this is the single worst false friend in the slice
- the word 'project' — every domain in the catalogue has projects
- a donor's name alone. §4.9's warning generalises: “A university name alone should not create a group because Columbia can appear as an authoring school, course provider, target institution, employer, research venue, or merely a cited organization.”

### Work types

`programme design or business case`, `implementing agreement`, `workplan and budget`, `progress report`, `annual review`, `monitoring data`, `evaluation report`, `closure report`, `beneficiary feedback record`

### Grouping reasons (§4)

- one programme across its design, agreement, reporting and evaluation
- one reporting period across the partner reports that feed one review

### Template (§5)

`programme → reporting period → document role`

Time first: **no**

§5.5: “a parent dimension should provide the context required to understand the child” — an annual review is legible only under its programme. The country does not lead because a programme is the funded unit and may span countries; where a user works in one country only, §5.8: “The canvas must support uneven depth because real file trees are not and should not be perfectly symmetrical.” should collapse it away. §5.5: “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders.” keeps the programme first

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| gov.grant-programme-administration | a development programme is administered as a grant or a contract by the donor; this domain describes the delivery, that one describes the award process | §6.9: “A file may have multiple valid organizational relationships, and the placement engine must preserve that complexity.” |
| npo.grant-reporting-recipient | the partner's narrative and financial reports are recipient-side grant reporting and programme delivery records at once | §3.11: “One file may hold facts from more than one domain without losing information.” |
| res.research-project | programme evaluations are research outputs with a project, a method and often an ethics approval; the separating signal is whether the file carries a research project identifier | §4.8: the validator checks “that each fact or label belongs to an allowed domain schema” |
| gov.emergency-management | humanitarian response and domestic civil protection produce similar operational documents under completely different mandates; the separating signal is whether an incident or a programme is the organising unit | §4.8: “an application packet does not silently absorb a document with a conflicting target institution” |

### Sensitivity

`potentially_sensitive` — Programme files routinely carry beneficiary records, partner staff details and location information for people in fragile settings, where §2.9's phrase “while treating addresses and message content as potentially sensitive” understates rather than overstates the risk. §8.4: “Paths, complete extracted text, OCR output, file hashes, image EXIF, GPS, user edits, group memberships, and raw sensitive values should remain local.” is the operative constraint. handling classes are P7's — §8.4: “The system should classify data into handling classes before LLM escalation” — and none is assigned here

---

## `gov.diplomatic-consular-record` — Diplomatic and consular records

The records of a diplomatic mission or consular post — reporting to the sending state, engagement with the host state, and assistance or documentary services provided to nationals.

**Provenance:** **proposal** — new; the design names nothing like it

**Cite:** No design sentence names diplomatic material. §5.7 lists the template library's intended coverage — “covering common organizational situations such as academic programs, university applications, recruiting processes, client engagements, research workflows, financial records, travel, legal matters, creative projects, software repositories, personal administration, and photo collections” — and names nothing governmental. Written functionally throughout because the document types are defined entirely by the sending state's practice

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `post_or_mission` | string | the mission or post named on the document | `validated` | The post is the organisational unit. Confirmable only with a diplomatic context term beside it |
| `sending_state` | string | the state the mission represents | `validated` | §3.8: “The system must separate roles that happen to contain the same entity type.” — sending state, host state and the national being assisted are three roles whose names all appear on the same page. Collapsing the first two is the characteristic error |
| `host_state` | string | the state the mission is accredited to | `validated` | §3.8's worked pair: “A consulting document may mention the author’s firm and the client organization.” transposed onto missions |
| `record_role` | string | consular assistance case | `validated` | Reporting, engagement, consular assistance and documentary services are different objects with very different sensitivity; the record role is the field that separates them |
| `matter` | string | the case or bilateral matter the document belongs to | `possible` | The template's middle level. It is populated from the case reference where one exists and inferred from the correspondence otherwise, which is why the ceiling is not higher. §3.13 possible: “A possible fact is a useful but insufficient clue” |
| `case_reference` | string | the post's case reference exactly as printed | `direct` | §3.13 direct: “A direct fact was read from a reliable and explicit source, such as a content hash, EXIF timestamp, document title, or labeled form field.”. No format asserted |
| `date` | date | 2026-02-09 | `direct` | §3.10: “Date candidates should be identified with explicit regular expressions and then parsed without fuzzy matching.” — a labeled date field only |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.4, §3.5):

- a diplomatic context term in a title or heading zone — 'embassy' | 'consulate' | 'consular assistance' | 'note verbale' | 'accreditation' | 'diplomatic mission' — co-occurring with two state names in the addressee or letterhead zone
- a documentary-service structure detected as labeled applicant and document-type fields co-occurring with a post name

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- a reporting telegram or note whose subject is entirely prose
- an assistance case file whose consular character is visible only from the situation described
- a document that is a consular function in one state's practice and a separate agency's function in another's

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10):

- two country names on a page — travel, trade, academic and news documents carry them constantly
- the word 'consular' — it appears in visa guidance, travel blogs and airline correspondence
- a mission name alone. §4.9's warning generalises: “A university name alone should not create a group because Columbia can appear as an authoring school, course provider, target institution, employer, research venue, or merely a cited organization.”
- a national flag or crest in an image region — not text, not a fact

### Work types

`reporting note`, `note verbale`, `engagement record`, `consular assistance case note`, `documentary service record`, `visa or entry correspondence`, `protocol and accreditation record`

### Grouping reasons (§4)

- one assistance case across its notes and correspondence, joined by the case reference
- one bilateral engagement across the notes exchanged about it

### Template (§5)

`post or mission → record role → matter`

Time first: **no**

§5.5: “a parent dimension should provide the context required to understand the child” — an assistance note is legible only under the role and the case. State names do not lead because both parties appear on every document and a level named for the sending state would be a collector, which §5.7 forbids a template that would “use an author or organization merely as a collector” forbids. The middle level is backed by a fact below `validated`, and §3.14 says templates use validated facts, so it should be offered only once the user has confirmed the label.

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| pers.travel-visa-entry | the personal-household slice owns the traveller's own visa and entry documents; this domain owns the post's record of issuing them. Same document, opposite ends | §3.8's worked pair: “A consulting document may mention the author’s firm and the client organization.” |
| admin.immigration | immigration paperwork held by an applicant is finance-admin material; a consular post's file on the same application is this domain | §3.8: “The system must separate roles that happen to contain the same entity type.” |
| gov.intergovernmental-agreement | instruments between states pass through diplomatic channels and are both | §3.11: “One file may hold facts from more than one domain without losing information.” |
| gov.defence-veterans-administration | defence attaché material sits in a mission and under a defence chain at once; the separating signal is the reporting line, which the document may not state | §4.8: the validator checks “that each fact or label belongs to an allowed domain schema” |

### Sensitivity

`potentially_sensitive` — Consular assistance cases concern named individuals in crisis abroad — detention, death, hospitalisation, destitution — and §4.9: “Rare but sensitive files such as passports, visas, and legal documents may be surfaced as protected records even when they do not meet a normal group-size threshold.” names the adjacent document types. §8.4: “Paths, complete extracted text, OCR output, file hashes, image EXIF, GPS, user edits, group memberships, and raw sensitive values should remain local.”. handling classes are P7's — §8.4: “The system should classify data into handling classes before LLM escalation” — and none is assigned here

### Open question — Joseph's call, unresolved

> CLASSIFICATION MARKINGS ARE A SIGNAL THE PRODUCT CANNOT SAFELY IGNORE OR SAFELY ACT ON. Diplomatic and defence material carries protective markings whose vocabularies and legal effects are set by each state and are not comparable across states. Detecting a marking is a strong signal that a file must not be sent anywhere, but treating an unknown marking string as authoritative is equally dangerous, and marking-shaped words appear in templates and training material. This is not a handling class — it is a question about whether the recogniser should look for markings at all, and what the product does when it finds one it does not recognise. Joseph decides.

---

## `gov.defence-veterans-administration` — Defence and veterans' affairs administration

The administrative record of military service and of the entitlements that follow it — service records, postings, discharge, benefit claims and veteran support.

**Provenance:** **proposal** — new; the design names nothing like it

**Cite:** No design sentence names defence or veterans' administration. §5.7 lists the template library's intended coverage — “covering common organizational situations such as academic programs, university applications, recruiting processes, client engagements, research workflows, financial records, travel, legal matters, creative projects, software repositories, personal administration, and photo collections” — and names nothing governmental. Written functionally: rank structures, benefit schemes and discharge vocabularies are defined per state

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `service_person` | string | the named individual the record concerns | `direct` | §3.13 direct: “A direct fact was read from a reliable and explicit source, such as a content hash, EXIF timestamp, document title, or labeled form field.” — a labeled name field on a service or claim document. For a veteran's own corpus this is the user; for an administering body's corpus it is a third party, which is the same split the whole slice carries |
| `administering_body` | string | the department or agency administering the entitlement | `validated` | §3.8: “The system must separate roles that happen to contain the same entity type.” — the service branch that employed the person and the body that administers their benefits are usually different organisations |
| `record_role` | string | discharge record | `validated` | Service record, posting order, discharge, benefit claim, appeal and support record are the recurring set, and the role is what determines the record's lifetime |
| `matter` | string | the claim or service episode the document belongs to | `possible` | The template's middle level, populated from the service or claim reference where one is present and inferred from the correspondence otherwise. §3.13 possible: “A possible fact is a useful but insufficient clue” |
| `service_reference` | string | the service or claim number exactly as printed | `direct` | §3.13 direct: “A direct fact was read from a reliable and explicit source, such as a content hash, EXIF timestamp, document title, or labeled form field.”. Deliberately without a format: service-number schemes are per state and per branch, and inventing one would be a fabrication in a domain where a wrong number has consequences |
| `service_period` | date range | 2008-09-01 to 2020-06-30 | `direct` | §3.10: “Date candidates should be identified with explicit regular expressions and then parsed without fuzzy matching.” — labeled enlistment and discharge fields only |
| `jurisdiction` | string | the state whose armed forces the record belongs to | `possible` | The document rarely states it because it assumes it. §3.13 possible: “A possible fact is a useful but insufficient clue” |
| `document_role` | string | medical board record | `validated` | The work-type field, and the template's leaf dimension — a claim file mixes forms, evidence, decisions and appeals. §5.7 requires a template's dimensions to be drawn from the domain's allowed fact fields, so the level and the field must exist together. Confirmable from the same context-term list the deterministic recognisers use |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.4, §3.5):

- a service context term in a title or heading zone — 'service record' | 'discharge' | 'enlistment' | 'posting order' | 'veteran' | 'disability compensation claim' — co-occurring with a labeled service or claim number field
- a claim-form structure detected as labeled claimant, condition and decision fields co-occurring with an administering-body name

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- a letter about an entitlement that never uses service vocabulary
- a medical report written for a service-related claim, which is simultaneously a health record
- a record whose rank, unit or discharge vocabulary belongs to a force the recogniser has no list for

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10):

- a rank-shaped word — 'major', 'general', 'private' and 'captain' are all ordinary English words, and this is a textbook instance of why §3.7: “It should use word-boundary matching rather than substring matching.” is not sufficient on its own
- the word 'service' — the most overloaded administrative word there is
- a service-number-shaped string. §3.10 is explicit that file names and documents “frequently contain numbers that look like years but are course identifiers, version numbers, build numbers, ZIP codes, or other unrelated values”
- a unit name alone. §4.9's warning generalises: “A university name alone should not create a group because Columbia can appear as an authoring school, course provider, target institution, employer, research venue, or merely a cited organization.”

### Work types

`service record`, `posting or assignment order`, `training and qualification record`, `discharge document`, `benefit or compensation claim`, `medical board record`, `appeal record`, `veteran support record`, `commemoration or medal record`

### Grouping reasons (§4)

- one person's service across its enlistment, postings, qualifications and discharge
- one claim across its application, evidence, decision and appeal

### Template (§5)

`record role → matter → document role`

Time first: **no**

§5.5: “a parent dimension should provide the context required to understand the child”. The service person does not lead: in a veteran's own corpus it would be a one-child collector, which §5.7 forbids a template that would “use an author or organization merely as a collector” forbids, and in an administering body's corpus a level named for a third party puts people's names in the filesystem. The middle level is backed by a fact below `validated`, and §3.14 says templates use validated facts, so it should be offered only once the user has confirmed the label. §5.5: “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders.”

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| career.employment-verification | for the individual, service is employment history; the career slice's shape fits a veteran's own corpus better than this domain does | §3.11: “One file may hold facts from more than one domain without losing information.” |
| med.personal-health-record | service-related medical evidence is a health record and a claim document at once, and the health reading is usually the more protective one | §6.9: “A file may have multiple valid organizational relationships, and the placement engine must preserve that complexity.” |
| pers.identity-document | an identity card or discharge certificate used as proof of identity is both | §4.9: “Rare but sensitive files such as passports, visas, and legal documents may be surfaced as protected records even when they do not meet a normal group-size threshold.” |
| gov.social-services-casework | veteran support casework is casework; the separating signal is the administering body's mandate rather than the document | §4.8: the validator checks “that each fact or label belongs to an allowed domain schema” |

### Sensitivity

`potentially_sensitive` — Service records combine identity, health, and location history for a named person, and §4.9: “Rare but sensitive files such as passports, visas, and legal documents may be surfaced as protected records even when they do not meet a normal group-size threshold.” names the adjacent categories directly. §8.4: “Paths, complete extracted text, OCR output, file hashes, image EXIF, GPS, user edits, group memberships, and raw sensitive values should remain local.”. handling classes are P7's — §8.4: “The system should classify data into handling classes before LLM escalation” — and none is assigned here

---

## `gov.emergency-management` — Emergency management and civil protection

Preparing for and responding to incidents — risk assessments, plans, exercises, live incident logs, situation reports and post-incident review.

**Provenance:** **proposal** — new; the design names nothing like it

**Cite:** No design sentence names emergency management. §5.7 lists the template library's intended coverage — “covering common organizational situations such as academic programs, university applications, recruiting processes, client engagements, research workflows, financial records, travel, legal matters, creative projects, software repositories, personal administration, and photo collections” — and names nothing governmental. The incident-as-event shape is the nearest thing in the slice to the design's photo-event pattern, though it is not capture-based

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `incident_or_plan` | string | the incident or plan name as printed | `validated` | The organising unit is either a named incident or a named plan; the domain has two modes and this field carries which. Confirmable with an emergency context term beside it |
| `lead_authority` | string | the body with lead responsibility | `validated` | §3.8: “The system must separate roles that happen to contain the same entity type.” — lead authority, supporting agencies and affected organisations are three roles, and multi-agency documents list all three in one table |
| `phase` | string | response | `validated` | Preparedness, response, recovery and review. The phase decides whether a document is a plan to be maintained or a record to be closed, which is the most consequential distinction here |
| `document_role` | string | situation report | `validated` | Risk assessment, plan, exercise record, log, situation report and debrief are the recurring set |
| `activation_period` | date range | 2026-01-14 to 2026-01-21 | `direct` | §3.10: “Date candidates should be identified with explicit regular expressions and then parsed without fuzzy matching.” — labeled activation or reporting fields only. Situation reports are serial and the period is what orders them |
| `geography` | string | the area affected as named in the document | `llm_supported` | §3.11 permits “several additional fields used only for search, privacy protection, explanation, or later review” — a search field. Area names are jurisdiction-specific |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.4, §3.5):

- an emergency context term in a title or heading zone — 'emergency plan' | 'incident log' | 'situation report' | 'civil protection' | 'multi-agency' | 'debrief' | 'exercise' — co-occurring with a lead-authority name or a labeled activation period
- a serial situation-report structure detected as a labeled report number together with a labeled reporting period and an incident name

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- an operational note taken during a response with no header at all, whose incident must be read from content
- a plan that is a statutory civil-protection document in one jurisdiction and an internal business-continuity plan in another
- a photographed whiteboard or log page, where OCR is the only route to the incident name

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10):

- the word 'emergency' — it appears in medical, IT, contact-list and building-signage contexts far more often
- the word 'incident' — every IT and HR corpus is full of incidents, and the software slice owns a whole domain of them
- the word 'exercise' — fitness, drafting and financial senses all outnumber this one
- a date range alone. §3.10 is explicit that file names and documents “frequently contain numbers that look like years but are course identifiers, version numbers, build numbers, ZIP codes, or other unrelated values”

### Work types

`risk assessment`, `emergency plan`, `exercise scenario`, `exercise report`, `incident log`, `situation report`, `multi-agency briefing`, `recovery plan`, `debrief and lessons record`

### Grouping reasons (§4)

- one incident across its logs, situation reports, briefings and debrief — §3.9: “The documents are content-incoherent but purpose-coherent.”
- one plan across its versions and the exercises that tested it

### Template (§5)

`incident or plan → phase → document role`

Time first: **no**

§5.5: “a parent dimension should provide the context required to understand the child” — a situation report is meaningless without its incident. The incident label frequently contains a date and is still an event rather than a calendar bucket, so §5.5: “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders.” is satisfied

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| soft.incident-postmortem | a technology incident and a civil-protection incident share the entire vocabulary — incident, log, situation report, debrief, lessons — and nothing but the subject separates them. This is the sharpest lexical collision in the slice | §6.3: “Conflicting evidence should actively suppress nodes.” |
| gov.public-health-administration | a public-health emergency is run under both regimes at once, and the same situation report is filed in both | §3.11: “One file may hold facts from more than one domain without losing information.” |
| gov.international-development-programme | humanitarian response documents mirror civil-protection ones under a different mandate; the organising unit is a programme rather than an incident | §4.8: “an application packet does not silently absorb a document with a conflicting target institution” |
| gov.municipal-administration | emergency plans are approved through the ordinary committee cycle, so the plan appears as a meeting paper as well | §6.9: “A file may have multiple valid organizational relationships, and the placement engine must preserve that complexity.” |

### Sensitivity

`potentially_sensitive` — Live incident material carries casualty, evacuation and vulnerable-person information about named individuals, and plans carry site and vulnerability detail that is withheld for good reason. §2.9's phrase “while treating addresses and message content as potentially sensitive” and §8.4: “Paths, complete extracted text, OCR output, file hashes, image EXIF, GPS, user edits, group memberships, and raw sensitive values should remain local.” both apply. handling classes are P7's — §8.4: “The system should classify data into handling classes before LLM escalation” — and none is assigned here

---

## `gov.public-health-administration` — Public health administration

Population-level health functions run by a public body — surveillance and notification, immunisation and screening programmes, outbreak management, inspection and health protection guidance.

**Provenance:** **proposal** — new; the design names nothing like it

**Cite:** No design sentence names public health administration. §5.7 lists the template library's intended coverage — “covering common organizational situations such as academic programs, university applications, recruiting processes, client engagements, research workflows, financial records, travel, legal matters, creative projects, software repositories, personal administration, and photo collections” — and names nothing governmental. Distinguished from the healthcare slice's clinical domains by having a population rather than a patient as its subject

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `programme_or_incident` | string | a seasonal immunisation programme | `validated` | The organising unit is a standing programme or a named outbreak. Confirmable with a public-health context term beside it |
| `responsible_body` | string | a regional health protection body | `validated` | §3.8: “The system must separate roles that happen to contain the same entity type.” — the public-health body, the clinical providers reporting to it and the premises it inspects are three roles |
| `population_or_area` | string | the area or population the record covers | `llm_supported` | §3.11 permits “several additional fields used only for search, privacy protection, explanation, or later review”. Area definitions are jurisdiction-specific and their names do not translate |
| `document_role` | string | outbreak control team minutes | `validated` | Surveillance report, notification, programme plan, inspection record, control-team record and guidance are the recurring set |
| `reporting_period` | date range | 2026-10-01 to 2027-03-31 | `direct` | §3.10: “Date candidates should be identified with explicit regular expressions and then parsed without fuzzy matching.” — from labeled period fields only. Surveillance outputs are serial and the period is what orders them |
| `notifiable_condition` | string | the condition named on the notification | `validated` | Which conditions are notifiable is set by law and differs by jurisdiction, so this is a verbatim field rather than an enum. It is confirmable only alongside a notification-structure signal |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.4, §3.5):

- a public-health context term in a title or heading zone — 'surveillance report' | 'notifiable' | 'outbreak control' | 'immunisation programme' | 'health protection' | 'screening programme' — co-occurring with a responsible-body name or a labeled reporting period
- a notification-form structure detected as labeled condition, onset-date and reporting-clinician fields co-occurring with a public-health body name

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- an epidemiological analysis with no programme header, whose public-health character must be read from method and framing
- a guidance note that reads as clinical guidance but is issued for population control
- a document whose notification regime has no counterpart in the reader's jurisdiction

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10):

- a condition name — it appears in every clinical record, every insurance document and most personal health material, and the healthcare slice owns those
- the word 'outbreak' — used loosely in news, IT and pest-control contexts
- the word 'screening' — recruitment, security and film senses all compete
- a body's name alone. §4.9's warning generalises: “A university name alone should not create a group because Columbia can appear as an authoring school, course provider, target institution, employer, research venue, or merely a cited organization.”

### Work types

`surveillance report`, `notification record`, `outbreak control record`, `programme plan`, `coverage report`, `inspection record`, `health protection guidance`, `incident debrief`

### Grouping reasons (§4)

- one outbreak across its notifications, control-team records and closure report
- one programme across one season's plan, delivery and coverage reporting

### Template (§5)

`programme or incident → reporting period → document role`

Time first: **no**

§5.5: “a parent dimension should provide the context required to understand the child” — a coverage report is legible only under its programme and season. §5.5: “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders.” keeps the programme first even though the period is unusually load-bearing here

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| med.public-health-reporting | the healthcare slice owns the clinician's obligation to report; this domain owns the receiving body's programme. The notification form is the same document at both ends | §3.8's worked pair: “A consulting document may mention the author’s firm and the client organization.” |
| gov.emergency-management | a health emergency runs under both regimes and produces one set of situation reports filed in two places | §3.11: “One file may hold facts from more than one domain without losing information.” |
| gov.census-statistical-programme | health statistics are produced under both; the separating signal is whether the output is an official statistical release or an operational surveillance product | §4.8: the validator checks “that each fact or label belongs to an allowed domain schema” |
| gov.permit-licensing-authority | food and premises inspection sits under both a licensing regime and a health-protection one, often in the same office | §4.8: “an application packet does not silently absorb a document with a conflicting target institution” |

### Sensitivity

`potentially_sensitive` — The domain is population-level by design, but notifications and outbreak records identify individual cases, which is the category §4.9: “Rare but sensitive files such as passports, visas, and legal documents may be surfaced as protected records even when they do not meet a normal group-size threshold.” names. The marking follows the worst case. handling classes are P7's — §8.4: “The system should classify data into handling classes before LLM escalation” — and none is assigned here

---

## `gov.social-services-casework` — Social services and welfare casework

A statutory service's file on a named person or household — assessment, eligibility, plan, review and the correspondence and decisions in between.

**Provenance:** **proposal** — new; the design names nothing like it

**Cite:** No design sentence names social services. §5.7 lists the template library's intended coverage — “covering common organizational situations such as academic programs, university applications, recruiting processes, client engagements, research workflows, financial records, travel, legal matters, creative projects, software repositories, personal administration, and photo collections” — and names nothing governmental. The case-per-person shape follows the same pattern as the law slice's matter file

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `case_reference` | string | the service's case reference exactly as printed | `direct` | §3.13 direct: “A direct fact was read from a reliable and explicit source, such as a content hash, EXIF timestamp, document title, or labeled form field.” — a labeled reference field, and the only grouping key that does not require putting a person's name in the tree |
| `service` | string | the statutory service holding the case | `validated` | §3.8: “The system must separate roles that happen to contain the same entity type.” — the responsible service, the other agencies involved and the person receiving support are distinct roles, and multi-agency records list all three |
| `case_type` | string | adult social care assessment | `validated` | Which services are statutory, what they are called and who delivers them differ by jurisdiction more sharply than almost anything else in this slice — see the open question |
| `stage` | string | review | `validated` | Referral, assessment, decision, plan, review and closure. The stage decides whether a document is current or historical, which in a case file is the whole question |
| `review_date` | date | 2026-09-30 | `direct` | §3.10: “Date candidates should be identified with explicit regular expressions and then parsed without fuzzy matching.” — a labeled review or decision date field only |
| `subject_person` | string | the person the case concerns | `direct` | §3.13 direct: “A direct fact was read from a reliable and explicit source, such as a content hash, EXIF timestamp, document title, or labeled form field.” from a labeled field. Retained as a fact for retrieval and explicitly excluded from the template, because §3.8: “A folder should not become a collection point for everything produced by the same person or organization.” and a folder named for a service user is worse than a collector — it is disclosure by directory listing |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.4, §3.5):

- a casework term in a title or heading zone — 'assessment' | 'care plan' | 'support plan' | 'safeguarding' | 'eligibility decision' | 'review meeting' — co-occurring with a labeled case-reference field and a service-shaped body name
- an assessment-form structure detected as labeled need, eligibility and outcome fields co-occurring with a case reference

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- a case note with no header whose service and stage must be read from prose
- a multi-agency minute where the responsible service must be inferred from who is chairing. §3.8: “The system must separate roles that happen to contain the same entity type.”
- a document whose service exists under a completely different name and mandate in another jurisdiction

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10):

- the word 'assessment' — academic, clinical, risk, tax and performance assessments all outnumber this one
- the word 'care' — the healthcare slice, the personal slice and ordinary English all claim it
- the word 'plan' — the highest-frequency document word in any corpus
- a person's name. §3.8: “It should avoid using authorship or creator identity as a destination dimension.”

### Work types

`referral`, `assessment`, `eligibility decision`, `care or support plan`, `case note`, `multi-agency minute`, `review record`, `complaint record`, `closure record`

### Grouping reasons (§4)

- one case across its referral, assessment, plan and reviews, joined by the case reference
- one review cycle across the documents produced for one meeting

### Template (§5)

`case → stage`

Time first: **no**

Deliberately two levels. §5.5: “a parent dimension should provide the context required to understand the child” is satisfied by the case alone; adding a service-user level would place identifying information in folder names, and adding a case-type level would require an enum that cannot be written jurisdiction-neutrally. §5.8: “The canvas must support uneven depth because real file trees are not and should not be perfectly symmetrical.” is the licence to stop early

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| gov.constituent-casework | both are case files about a person and a public service; the separating signal is whether the holder is responsible for the person or advocating for them, which the file rarely states | §4.8: the validator checks “that each fact or label belongs to an allowed domain schema” |
| med.caregiving-dependant | for the family, the same assessments and plans are their own caregiving records. The healthcare slice's domain is the right home for the family's copy | §3.8's worked pair: “A consulting document may mention the author’s firm and the client organization.” |
| gov.housing-authority | homelessness and housing-need casework sits under both a housing regime and a social-care one, frequently in the same file | §3.11: “One file may hold facts from more than one domain without losing information.” |
| law.family-law | care proceedings produce a legal matter file and a social-work case file about the same child, with overlapping documents and different duties attached | §4.8: “an application packet does not silently absorb a document with a conflicting target institution” |

### Sensitivity

`potentially_sensitive` — This is the most sensitive domain in the slice: statutory case files concern health, family, finances and risk for named third parties. §4.9: “Rare but sensitive files such as passports, visas, and legal documents may be surfaced as protected records even when they do not meet a normal group-size threshold.” names the adjacent categories and §8.4: “Paths, complete extracted text, OCR output, file hashes, image EXIF, GPS, user edits, group memberships, and raw sensitive values should remain local.” is the operative constraint. handling classes are P7's — §8.4: “The system should classify data into handling classes before LLM escalation” — and none is assigned here

### Open question — Joseph's call, unresolved

> SAME PRIOR QUESTION AS CONSTITUENT CASEWORK, SHARPER. A social-care caseload is other people's most sensitive information held under statutory duties, and the ordinary pipeline would extract, index, retain and label it. Nothing in this catalogue may decide whether that is permitted; a handling class would not answer it either, because the question is whether the corpus is in scope. SECOND: `case_type` cannot be enumerated. Which services are statutory, which tier delivers them, and what triggers a duty are jurisdiction-set, so the field is a free string with no allow-list for §3.6's validator to check. Joseph decides both.

---

## `gov.housing-authority` — Public and social housing administration

A social landlord's or housing authority's record of allocating and managing homes — applications, tenancies, rent accounts, repairs, and estate management.

**Provenance:** **proposal** — new; the design names nothing like it

**Cite:** No design sentence names housing administration. §5.7 lists the template library's intended coverage — “covering common organizational situations such as academic programs, university applications, recruiting processes, client engagements, research workflows, financial records, travel, legal matters, creative projects, software repositories, personal administration, and photo collections” — and names nothing governmental. Written as the landlord-side counterpart to the personal slice's tenure domain, which is §3.8: “The system must separate roles that happen to contain the same entity type.”

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `property` | string | the property address as printed on the tenancy record | `validated` | The home is the durable object; tenants change and the property does not. Confirmable only with a housing context term beside it, because an address alone is the most over-firing string in any personal corpus |
| `landlord_or_authority` | string | a social landlord or housing authority | `validated` | §3.8: “The system must separate roles that happen to contain the same entity type.” — the landlord, the tenant and the contractor doing the repair are three roles that appear together on a single work order |
| `tenancy_reference` | string | the tenancy or application reference exactly as printed | `direct` | §3.13 direct: “A direct fact was read from a reliable and explicit source, such as a content hash, EXIF timestamp, document title, or labeled form field.”. No format asserted |
| `record_role` | string | repair work order | `validated` | Application, allocation, tenancy agreement, rent account, repair, inspection and possession action are the recurring set and have very different lifetimes |
| `tenancy_period` | date range | 2021-11-01 to present | `direct` | §3.10: “Date candidates should be identified with explicit regular expressions and then parsed without fuzzy matching.” — labeled tenancy start and end fields only |
| `tenant` | string | the person named on the tenancy | `direct` | §3.13 direct: “A direct fact was read from a reliable and explicit source, such as a content hash, EXIF timestamp, document title, or labeled form field.” from a labeled field, and deliberately excluded from the template for the same reason as social-care casework |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.4, §3.5):

- a housing context term in a title or heading zone — 'tenancy agreement' | 'rent account' | 'housing application' | 'allocation' | 'repair order' | 'notice seeking possession' — co-occurring with an address-shaped property string or a labeled tenancy reference
- a rent-statement structure detected as labeled charge and balance columns co-occurring with a tenancy reference. §2.3: “Tables matter because resumes, forms, applications, invoices, and administrative documents often place their most useful information in cells rather than body paragraphs.”
- a landlord-shaped organisation name in a letterhead or footer zone co-occurring with a housing context term, which is what confirms the landlord field rather than the property one

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- a letter about a housing issue with no reference and no housing vocabulary
- a repair photograph whose subject must be read from OCR of a job sheet in the frame
- a document whose tenure type has no counterpart in the reader's housing system, which is a genuine category difference

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10):

- an address-shaped string — utilities, deliveries, insurance and the user's own letterhead all carry one
- the word 'tenancy' — commercial leases and licences use it too, and the finance-admin slice owns those
- the word 'repair' — vehicle, device and building senses compete
- a landlord's name alone. §4.9's warning generalises: “A university name alone should not create a group because Columbia can appear as an authoring school, course provider, target institution, employer, research venue, or merely a cited organization.”

### Work types

`housing application`, `allocation decision`, `tenancy agreement`, `rent statement`, `repair order`, `property inspection`, `anti-social behaviour record`, `possession notice`, `estate management record`

### Grouping reasons (§4)

- one tenancy across its agreement, rent account, repairs and notices
- one property across its successive tenancies and its repair history

### Template (§5)

`property → tenancy → record role`

Time first: **no**

§5.5: “a parent dimension should provide the context required to understand the child” — a repair order is legible only under the property, and a rent statement only under the tenancy. Property before tenancy because the property outlives every tenancy on it. For a tenant's own corpus the property level is a one-child collector and §5.8: “The canvas must support uneven depth because real file trees are not and should not be perfectly symmetrical.” should collapse it

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| pers.home-tenure | the tenant holds the same agreement, the same rent statements and the same repair correspondence; the personal slice owns their side and nothing in the documents distinguishes the copies | §3.8's worked pair: “A consulting document may mention the author’s firm and the client organization.” |
| legal.lease | the finance-admin slice owns leases and tenancies as legal instruments; this domain owns the operational record around them | §3.11: “One file may hold facts from more than one domain without losing information.” |
| gov.social-services-casework | homelessness and vulnerability casework crosses both, and the same assessment appears in each | §6.9: “A file may have multiple valid organizational relationships, and the placement engine must preserve that complexity.” |
| npo.residents-association | estate management by a landlord and by a residents' body produce near-identical minutes and notices; the separating signal is whether the body owns or manages the homes | §4.8: the validator checks “that each fact or label belongs to an allowed domain schema” |

### Sensitivity

`potentially_sensitive` — The record ties named people to the home they live in, their rent arrears and often their vulnerabilities — §2.9's phrase “while treating addresses and message content as potentially sensitive” covers the address half exactly. handling classes are P7's — §8.4: “The system should classify data into handling classes before LLM escalation” — and none is assigned here

---

## `gov.transport-authority` — Transport authority administration

A transport authority's record of running a network — service specifications and contracts, timetables and fares, asset and highway records, works notices and passenger casework.

**Provenance:** **proposal** — new; the design names nothing like it

**Cite:** No design sentence names transport administration. §5.7 lists the template library's intended coverage — “covering common organizational situations such as academic programs, university applications, recruiting processes, client engagements, research workflows, financial records, travel, legal matters, creative projects, software repositories, personal administration, and photo collections” — and names nothing governmental. Written functionally because which body owns roads, rail, parking and licensing differs completely between systems

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `authority` | string | a regional transport authority | `validated` | §3.8: “The system must separate roles that happen to contain the same entity type.” — the specifying authority, the operator running the service and the contractor doing the works are three roles on one page |
| `network_element` | string | the route, road or asset the record concerns | `validated` | The route or asset is the durable object. Route and asset identifiers are locally assigned so the field stores the string verbatim |
| `record_role` | string | works notice | `validated` | Specification, contract, timetable, fares record, asset record, works notice and passenger case are the recurring set |
| `operator` | string | the operator named on the specification | `validated` | §3.8's worked pair: “A consulting document may mention the author’s firm and the client organization.” — authority and operator are the pair, and conflating them misfiles the whole corpus |
| `effective_period` | date range | 2026-04-01 to 2027-03-31 | `direct` | §3.10: “Date candidates should be identified with explicit regular expressions and then parsed without fuzzy matching.” — labeled validity fields only. Timetables and fares are superseded rather than amended, so the period is the field that says which one is live |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.4, §3.5):

- a transport context term in a title or heading zone — 'timetable' | 'fares' | 'service specification' | 'road works' | 'traffic order' | 'highway' | 'concession' — co-occurring with an authority-shaped name or a labeled validity period
- a timetable structure detected as a labeled grid of stops against times co-occurring with an operator or route identifier
- a route or asset identifier pattern co-occurring with a transport context term, which is the only way a locally assigned identifier becomes a fact rather than a number

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- an asset condition report whose network element must be read from prose and photographs
- a passenger complaint that reads as ordinary correspondence
- a document whose regulatory instrument has no counterpart in the reader's system

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10):

- a route-shaped number — bus, road, flight, version and model numbers are indistinguishable by shape. §3.10 is explicit that file names and documents “frequently contain numbers that look like years but are course identifiers, version numbers, build numbers, ZIP codes, or other unrelated values”
- the word 'transport' — logistics, file transport and data transport senses compete
- a place name — it is in every address block in the corpus
- an operator's name alone. §4.9's warning generalises: “A university name alone should not create a group because Columbia can appear as an authoring school, course provider, target institution, employer, research venue, or merely a cited organization.”

### Work types

`service specification`, `operator contract`, `timetable`, `fares schedule`, `traffic or highway order`, `works notice`, `asset condition record`, `passenger case record`, `network performance report`

### Grouping reasons (§4)

- one route or asset across its specification, timetables and works
- one contract across its specification, variations and performance reports

### Template (§5)

`network element → record role → period`

Time first: **no**

§5.5: “a parent dimension should provide the context required to understand the child” — a timetable is legible only under its route. The period comes last and only where documents are superseded serially, which §5.5: “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders.” permits as a leaf rather than a root

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| gov.contract-award-record | an operator contract is a public contract; this domain adds the network context that the award record does not carry | §3.11: “One file may hold facts from more than one domain without losing information.” |
| gov.planning-application | highway and transport works consents sit under both regimes with different references on the same site | §4.8: “an application packet does not silently absorb a document with a conflicting target institution” |
| pers.travel-record | a passenger's own tickets and journey records are personal travel material; a downloaded timetable in a personal corpus is reference material rather than an authority record | §3.8: “The system must separate roles that happen to contain the same entity type.” |
| soft.it-asset-inventory | asset registers are structurally identical across domains; the separating signal is what the assets are, not how the register is shaped | §4.8: the validator checks “that each fact or label belongs to an allowed domain schema” |

### Sensitivity

`none` — Network administration concerns infrastructure rather than individuals. Passenger casework is the exception and it is a per-file property. handling classes are P7's — §8.4: “The system should classify data into handling classes before LLM escalation” — and none is assigned here

---

## `gov.environmental-regulation` — Environmental regulation and monitoring

A regulator's control of environmental impact — permits with conditions, monitoring returns, sampling and inspection results, incidents and enforcement.

**Provenance:** **proposal** — new; the design names nothing like it

**Cite:** No design sentence names environmental regulation. §5.7 lists the template library's intended coverage — “covering common organizational situations such as academic programs, university applications, recruiting processes, client engagements, research workflows, financial records, travel, legal matters, creative projects, software repositories, personal administration, and photo collections” — and names nothing governmental. Distinguished from general licensing by carrying a monitoring stream, which is §3.11: “It should then activate domain-specific schemas only when the evidence indicates that a domain is plausible.”

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `regulated_site` | string | the site or installation as named on the permit | `validated` | The site is the durable object and the key that binds a permit to years of monitoring data. Confirmable only with an environmental context term beside it |
| `regulator` | string | an environmental regulator | `validated` | §3.8: “The system must separate roles that happen to contain the same entity type.” — regulator, operator and accredited laboratory are three roles that appear on one monitoring report |
| `operator` | string | the organisation holding the permit | `direct` | §3.8's worked pair: “A consulting document may mention the author’s firm and the client organization.”. Direct from a labeled permit-holder field |
| `permit_reference` | string | the environmental permit reference exactly as printed | `direct` | §3.13 direct: “A direct fact was read from a reliable and explicit source, such as a content hash, EXIF timestamp, document title, or labeled form field.”. No format asserted |
| `record_role` | string | monitoring return | `validated` | Permit, variation, monitoring return, sampling result, inspection, incident and enforcement notice are the recurring set |
| `monitoring_period` | date range | 2026-01-01 to 2026-03-31 | `direct` | §3.10: “Date candidates should be identified with explicit regular expressions and then parsed without fuzzy matching.” — labeled period fields only. Monitoring is serial and the period is the only thing distinguishing otherwise identical returns |
| `determinand` | string | the substance or parameter measured, as named on the return | `validated` | §3.11 permits “several additional fields used only for search, privacy protection, explanation, or later review” — a search field. Parameter naming follows the regulator's own list, which is jurisdiction-set |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.4, §3.5):

- an environmental context term in a title or heading zone — 'environmental permit' | 'discharge consent' | 'emissions' | 'monitoring return' | 'sampling result' | 'pollution incident' — co-occurring with a labeled permit reference or a named site
- a monitoring-return structure detected as labeled determinand, result and limit columns co-occurring with a permit reference. §2.3: “Tables matter because resumes, forms, applications, invoices, and administrative documents often place their most useful information in cells rather than body paragraphs.”
- a regulator-shaped organisation name in a letterhead or issuing zone co-occurring with an environmental permitting term, which is what separates the regulator from the operator named in the same document

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- a laboratory report with no permit reference, whose regulatory purpose must be inferred from the parameters measured
- an incident report that describes an environmental event in ordinary operational language
- a document whose permitting regime has no counterpart in the reader's jurisdiction

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10):

- the word 'environment' — development environments, working environments and environment variables all outnumber this sense, and the software slice owns two of them
- the word 'emissions' — accounting and finance use it for reporting
- a numeric measurement — a result without a determinand and a limit is not a fact this domain can use
- a site name alone. §4.9's warning generalises: “A university name alone should not create a group because Columbia can appear as an authoring school, course provider, target institution, employer, research venue, or merely a cited organization.”

### Work types

`permit application`, `environmental permit`, `permit variation`, `monitoring return`, `sampling result`, `inspection report`, `incident report`, `enforcement notice`, `environmental impact assessment`

### Grouping reasons (§4)

- one permitted site across its permit, variations, monitoring and inspections
- one monitoring period across the returns and laboratory results that support it

### Template (§5)

`site → record role → period`

Time first: **no**

§5.5: “a parent dimension should provide the context required to understand the child” — a monitoring return is meaningless without the site. The period appears as a leaf because monitoring genuinely is serial, which is the narrow case §5.5: “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders.” leaves room for

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| gov.permit-licensing-authority | an environmental permit is a permission; the monitoring stream is what gives this domain the better claim | §4.8: the validator checks “that each fact or label belongs to an allowed domain schema” |
| corp.compliance-audit | the operator's own compliance file holds the same returns and inspections from the regulated side | §3.8's worked pair: “A consulting document may mention the author’s firm and the client organization.” |
| res.dataset | monitoring data reused for research is a dataset; the separating signal is whether the file carries a permit reference or a project identifier | §3.11: “One file may hold facts from more than one domain without losing information.” |
| gov.parks-public-lands | designated-site management and environmental permitting overlap on the same land with different instruments | §4.8: “an application packet does not silently absorb a document with a conflicting target institution” |

### Sensitivity

`none` — Environmental regulation concerns sites and operators rather than individuals, and much of it is on a public register. handling classes are P7's — §8.4: “The system should classify data into handling classes before LLM escalation” — and none is assigned here

---

## `gov.parks-public-lands` — Parks, public lands and heritage site management

The management of land or a site held for public benefit — designation, management plans, access and permissions, conservation works, and visitor operations.

**Provenance:** **proposal** — new; the design names nothing like it

**Cite:** No design sentence names land management. §5.7 lists the template library's intended coverage — “covering common organizational situations such as academic programs, university applications, recruiting processes, client engagements, research workflows, financial records, travel, legal matters, creative projects, software repositories, personal administration, and photo collections” — and names nothing governmental. Written functionally because designation regimes and the tier holding the land differ per jurisdiction

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `site` | string | the park, reserve or heritage site as named | `validated` | The site is the durable object and the only stable grouping key. Confirmable only with a land-management context term beside it |
| `managing_body` | string | the body responsible for the site | `validated` | §3.8: “The system must separate roles that happen to contain the same entity type.” — the managing body, the designating authority and the contractor doing the works are three roles |
| `designation` | string | the protective designation as named on the document | `validated` | Designations are creatures of statute and are not translatable between systems; the field is verbatim. It matters because it determines what may lawfully be done on the land |
| `record_role` | string | management plan | `validated` | Designation record, management plan, works consent, access agreement, survey and visitor operations record are the recurring set |
| `plan_period` | date range | 2026-01-01 to 2030-12-31 | `direct` | §3.10: “Date candidates should be identified with explicit regular expressions and then parsed without fuzzy matching.” — a labeled plan-period field only |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.4, §3.5):

- a land-management context term in a title or heading zone — 'management plan' | 'nature reserve' | 'country park' | 'scheduled monument' | 'conservation area' | 'public right of way' — co-occurring with a named site or a managing-body name
- a survey structure detected as labeled species, condition or feature columns co-occurring with a named site

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- a works specification whose site is named only in a location paragraph
- a site photograph set whose subject is recoverable only from EXIF location and a filename pattern
- a designation whose regime has no counterpart in the reader's jurisdiction, which is a category difference rather than a wording one

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10):

- a place name — the single weakest signal available, present in every address block
- the word 'park' — car parks, business parks, theme parks and the verb all compete
- the word 'heritage' — used constantly in branding
- a managing body's name alone. §4.9's warning generalises: “A university name alone should not create a group because Columbia can appear as an authoring school, course provider, target institution, employer, research venue, or merely a cited organization.”

### Work types

`designation record`, `management plan`, `condition survey`, `works consent`, `access or right-of-way record`, `conservation works record`, `visitor operations record`, `grazing or tenancy agreement`

### Grouping reasons (§4)

- one site across its designation, plans, surveys and works
- one plan period across the surveys and works that report against it

### Template (§5)

`site → record role → period`

Time first: **no**

§5.5: “a parent dimension should provide the context required to understand the child” — a condition survey is legible only under the site. §5.5: “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders.” keeps the period a leaf

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| gov.environmental-regulation | designated land is often also permitted land, with two instruments and two references on the same ground | §4.8: “an application packet does not silently absorb a document with a conflicting target institution” |
| gov.planning-application | works on designated land need consents that look like planning permissions and are granted under a different regime | §4.8: the validator checks “that each fact or label belongs to an allowed domain schema” |
| gov.museum-collection | heritage sites frequently hold collections, so a single body produces site records and collection records that share only a name | §3.11: “One file may hold facts from more than one domain without losing information.” |
| pers.photo-event | site photographs in a personal corpus are photo-event material; a managing body's condition photographs are survey evidence with the same EXIF | §3.8: “The system must separate roles that happen to contain the same entity type.” |

### Sensitivity

`none` — Land management concerns places rather than people. Tenancy and access agreements with named individuals are the exception and are a per-file property. handling classes are P7's — §8.4: “The system should classify data into handling classes before LLM escalation” — and none is assigned here

---

## `gov.professional-regulator` — Professional regulation (regulator side)

A regulator's record of controlling entry to and conduct within a profession — registration, renewal, continuing-competence audit, complaints and fitness-to-practise decisions.

**Provenance:** **proposal** — new; the design names nothing like it

**Cite:** No design sentence names professional regulation. §5.7 lists the template library's intended coverage — “covering common organizational situations such as academic programs, university applications, recruiting processes, client engagements, research workflows, financial records, travel, legal matters, creative projects, software repositories, personal administration, and photo collections” — and names nothing governmental. Written as the regulator-side counterpart to the registrant-side domains the career, healthcare and law slices already own, which is §3.8: “The system must separate roles that happen to contain the same entity type.”

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `registrant` | string | the person or firm on the register | `direct` | §3.13 direct: “A direct fact was read from a reliable and explicit source, such as a content hash, EXIF timestamp, document title, or labeled form field.” from a labeled registrant field. In this domain the registrant is a third party, not the user, which flips the whole sensitivity picture relative to the career slice's licence domain |
| `regulator` | string | a statutory regulator for a profession | `validated` | §3.8's worked pair: “A consulting document may mention the author’s firm and the client organization.” — regulator and registrant are the pair, and a professional body that is not a regulator is a third thing again |
| `registration_reference` | string | the registration number exactly as printed | `direct` | §3.13 direct: “A direct fact was read from a reliable and explicit source, such as a content hash, EXIF timestamp, document title, or labeled form field.”. No format asserted: registration numbering is per regulator |
| `record_role` | string | fitness-to-practise decision | `validated` | Application, registration, renewal, competence audit, complaint, investigation and determination are the recurring set, and they run from routine to career-ending |
| `status` | string | registered with conditions | `validated` | Registered, lapsed, suspended, conditions imposed, removed. The status is the fact the register exists to publish |
| `decision_date` | date | 2026-04-22 | `direct` | §3.10: “Date candidates should be identified with explicit regular expressions and then parsed without fuzzy matching.” — a labeled decision or effective date field only |
| `document_role` | string | determination | `validated` | The work-type field, and the template's leaf dimension — a case is a complaint, an investigation, a hearing bundle and a determination. §5.7 requires a template's dimensions to be drawn from the domain's allowed fact fields, so the level and the field must exist together. Confirmable from the same context-term list the deterministic recognisers use |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.4, §3.5):

- a professional-regulation term in a title or heading zone — 'register of' | 'fitness to practise' | 'continuing professional development audit' | 'conditions of registration' | 'striking off' | 'renewal of registration' — co-occurring with a labeled registration reference or a regulator name
- a determination structure detected as labeled allegation, finding and sanction fields co-occurring with a registrant reference

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- a complaint letter about a professional that never names the regulator
- a competence audit return that reads as an ordinary training log
- a document from a body that regulates in one jurisdiction and merely represents members in another, which changes the domain entirely

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10):

- the word 'register' — a cash register, a registry, a verb and a database table all compete
- the word 'professional' — near-meaningless as a signal
- a registration-shaped number. §3.10 is explicit that file names and documents “frequently contain numbers that look like years but are course identifiers, version numbers, build numbers, ZIP codes, or other unrelated values”
- a regulator's name alone. §4.9's warning generalises: “A university name alone should not create a group because Columbia can appear as an authoring school, course provider, target institution, employer, research venue, or merely a cited organization.”

### Work types

`registration application`, `register entry`, `renewal record`, `competence audit record`, `complaint received`, `investigation record`, `hearing bundle`, `determination`, `sanction or restoration record`

### Grouping reasons (§4)

- one registrant across their registration, renewals and any case about them
- one case across its complaint, investigation, hearing and determination

### Template (§5)

`record role → case or registration → document role`

Time first: **no**

§5.5: “a parent dimension should provide the context required to understand the child”. The registrant deliberately does not lead: a folder level named for a person under investigation is disclosure by directory listing, which is a stronger version of what §3.8: “A folder should not become a collection point for everything produced by the same person or organization.” warns against. Function first, case second

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| career.professional-license | the career slice owns the registrant's own licence and renewal records; this domain holds the regulator's side of the same transaction, and the certificate is identical | §3.8's worked pair: “A consulting document may mention the author’s firm and the client organization.” |
| med.clinician-licensure-credentialing | the healthcare slice owns clinician credentialing from the clinician's and employer's side; the regulator's register is this domain | §3.8: “The system must separate roles that happen to contain the same entity type.” |
| law.bar-admission-cle | the law slice owns admission and continuing education from the practitioner's side | §3.11: “One file may hold facts from more than one domain without losing information.” |
| gov.permit-licensing-authority | both grant permissions; the separating signal is whether the permission attaches to a person's qualifications or to premises and activity | §4.8: the validator checks “that each fact or label belongs to an allowed domain schema” |

### Sensitivity

`potentially_sensitive` — Fitness-to-practise material concerns allegations against named individuals, frequently including their health, and §4.9: “Rare but sensitive files such as passports, visas, and legal documents may be surfaced as protected records even when they do not meet a normal group-size threshold.” names the adjacent categories. handling classes are P7's — §8.4: “The system should classify data into handling classes before LLM escalation” — and none is assigned here

---

## `gov.library-administration` — Library service administration

Running a library service — stock selection and cataloguing, membership and circulation, programming and events, and service performance.

**Provenance:** **proposal** — new; the design names nothing like it

**Cite:** No design sentence names libraries. §5.7 lists the template library's intended coverage — “covering common organizational situations such as academic programs, university applications, recruiting processes, client engagements, research workflows, financial records, travel, legal matters, creative projects, software repositories, personal administration, and photo collections” — and names nothing governmental. Kept separate from archives because the two have different organising units — an item held in many copies versus a unique record in a series

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `service_or_branch` | string | the library service or branch named on the record | `validated` | §3.8: “The system must separate roles that happen to contain the same entity type.” — the service, the supplier of stock and the publisher named in a catalogue record are three roles |
| `function` | string | stock selection | `validated` | Stock, cataloguing, membership, circulation, programming and performance are the recurring functions and the work-type field here |
| `catalogue_identifier` | string | the local catalogue or accession identifier as printed | `direct` | §3.13 direct: “A direct fact was read from a reliable and explicit source, such as a content hash, EXIF timestamp, document title, or labeled form field.” — a labeled catalogue field. Bibliographic identifiers proper belong to the item, not to the administration of it, which is why the field is named for the local record |
| `reporting_period` | date range | 2026-04-01 to 2027-03-31 | `direct` | §3.10: “Date candidates should be identified with explicit regular expressions and then parsed without fuzzy matching.” — labeled period fields only |
| `collection_area` | string | children's stock | `llm_supported` | §3.11 permits “several additional fields used only for search, privacy protection, explanation, or later review” — a search field. Collection divisions are local conventions |
| `document_role` | string | circulation report | `validated` | The work-type field, and the template's leaf dimension — a function produces plans, records and reports that are not interchangeable. §5.7 requires a template's dimensions to be drawn from the domain's allowed fact fields, so the level and the field must exist together. Confirmable from the same context-term list the deterministic recognisers use |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.4, §3.5):

- a library-administration term in a title or heading zone — 'stock selection' | 'accessions list' | 'circulation report' | 'library membership' | 'interlibrary loan' | 'reading programme' — co-occurring with a service or branch name
- a catalogue-record structure detected as labeled bibliographic fields together with a local holdings or shelfmark field

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- an events programme that reads as ordinary marketing material
- a stock report whose library character is visible only from column headers
- a document from a service whose statutory basis and naming differ entirely from the reader's

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10):

- the word 'library' — code libraries, photo libraries and asset libraries dominate a mixed corpus, and the software slice owns one of them outright
- the word 'catalogue' — retail and product catalogues are far more common
- an ISBN or similar bibliographic identifier — it identifies a published work, not this service's record of it, and it appears in reading lists and citations throughout a personal corpus
- a branch name alone. §4.9's warning generalises: “A university name alone should not create a group because Columbia can appear as an authoring school, course provider, target institution, employer, research venue, or merely a cited organization.”

### Work types

`stock selection list`, `accessions record`, `catalogue record`, `membership record`, `circulation report`, `interlibrary loan record`, `programme or event record`, `service performance report`

### Grouping reasons (§4)

- one function across one reporting period
- one programme or event across its planning, delivery and evaluation

### Template (§5)

`function → period → document role`

Time first: **no**

§5.5: “a parent dimension should provide the context required to understand the child” — a circulation report is legible under its function. The service does not lead because most users have one, which §5.7 forbids a template that would “use an author or organization merely as a collector” rules out. §5.5: “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders.” keeps function first

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| gov.archives-recordkeeping | many services run both, and a local-studies collection sits between them; the separating signal is whether the item is one of many copies or a unique record in a series | §4.8: the validator checks “that each fact or label belongs to an allowed domain schema” |
| res.reading-library | the research slice owns a personal reading collection; a library service's catalogue of the same titles is a different object entirely, sharing only the bibliographic identifiers | §3.8: “The system must separate roles that happen to contain the same entity type.” |
| gov.municipal-administration | library services are usually a function of a local authority, so their performance reports appear as committee papers too | §3.11: “One file may hold facts from more than one domain without losing information.” |

### Sensitivity

`potentially_sensitive` — Circulation and membership records tie named people to what they read, which is among the most protected categories in library practice and is §2.9's phrase “while treating addresses and message content as potentially sensitive” in form. handling classes are P7's — §8.4: “The system should classify data into handling classes before LLM escalation” — and none is assigned here

---

## `gov.archives-recordkeeping` — Archives and records management

Custody of records as evidence — accession and appraisal, arrangement and description, retention scheduling, preservation, and controlled access to closed material.

**Provenance:** **proposal** — new; the design names nothing like it

**Cite:** No design sentence names archives. §5.7 lists the template library's intended coverage — “covering common organizational situations such as academic programs, university applications, recruiting processes, client engagements, research workflows, financial records, travel, legal matters, creative projects, software repositories, personal administration, and photo collections” — and names nothing governmental. The design's own §8 fixity discipline is the nearest thing it says to archival practice

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `collection_or_series` | string | the collection or series as named in the description | `validated` | Archival material is described in hierarchies, and the series is the level at which meaning lives. Confirmable with an archival context term beside it |
| `repository` | string | the repository holding the material | `validated` | §3.8: “The system must separate roles that happen to contain the same entity type.” — the repository, the creating body and the depositor are three roles, and the creating body is the one that gives the records their meaning |
| `creating_body` | string | the body whose activity created the records | `direct` | §3.13 direct: “A direct fact was read from a reliable and explicit source, such as a content hash, EXIF timestamp, document title, or labeled form field.” — an archival description carries a labeled creator element, which is a labeled form field in §3.13's sense. §3.8: “Authorship is usually metadata; the document’s purpose, project, subject, or target is more informative for placement.” — archival practice is the one place in this catalogue where that guidance genuinely inverts, because provenance IS the organising principle. The field is retained precisely so the difference is visible |
| `reference_code` | string | the archival reference exactly as printed | `direct` | §3.13 direct: “A direct fact was read from a reliable and explicit source, such as a content hash, EXIF timestamp, document title, or labeled form field.”. Reference schemes are repository-specific and hierarchical; the field stores the string verbatim |
| `record_role` | string | finding aid | `validated` | Accession record, appraisal note, finding aid, retention schedule, preservation record and access decision are the recurring set |
| `closure_status` | string | closed until review | `direct` | §3.13 direct: “A direct fact was read from a reliable and explicit source, such as a content hash, EXIF timestamp, document title, or labeled form field.” — an archival description carries a labeled access-conditions element. Whether material is open, closed or closed-in-part is the fact that governs everything the product may do with it, and closure periods and grounds are jurisdiction-set so no period is asserted |
| `covering_dates` | string | the covering dates as printed in the description | `direct` | §3.13 direct: “A direct fact was read from a reliable and explicit source, such as a content hash, EXIF timestamp, document title, or labeled form field.”. Archival covering dates are frequently approximate or open-ended, which is precisely the case §3.10: “Date extraction should be deliberately narrow.” protects against; the field stores the description's own string rather than a parsed range |
| `document_role` | string | finding aid | `validated` | The work-type field, and the template's leaf dimension — an accession record, a description and an access decision describe the same material at different moments. §5.7 requires a template's dimensions to be drawn from the domain's allowed fact fields, so the level and the field must exist together. Confirmable from the same context-term list the deterministic recognisers use |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.4, §3.5):

- an archival term in a title or heading zone — 'finding aid' | 'accession' | 'fonds' | 'series description' | 'retention schedule' | 'archival description' | 'covering dates' — co-occurring with a repository name or a labeled reference code
- a hierarchical description structure detected as nested labeled levels each carrying a reference code and covering dates

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- a deposit agreement that reads as an ordinary contract
- an appraisal note whose archival character is visible only from the reasoning it applies
- a description written in a national standard the recogniser has no vocabulary for

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10):

- the word 'archive' — archived email, archive files and tape archives dominate any real corpus, and the extraction layer already treats archives as a file type
- the word 'record' — the most overloaded word in the catalogue
- a date range alone. §3.10 is explicit that file names and documents “frequently contain numbers that look like years but are course identifiers, version numbers, build numbers, ZIP codes, or other unrelated values”
- a repository name alone. §4.9's warning generalises: “A university name alone should not create a group because Columbia can appear as an authoring school, course provider, target institution, employer, research venue, or merely a cited organization.”

### Work types

`accession record`, `appraisal note`, `deposit agreement`, `finding aid`, `series description`, `retention schedule`, `preservation record`, `access decision`, `digitisation record`

### Grouping reasons (§4)

- one collection across its accession, description, preservation and access records
- one retention schedule across the series it governs

### Template (§5)

`collection or series → record role → document role`

Time first: **no**

§5.5: “a parent dimension should provide the context required to understand the child” — a finding aid is legible only under what it describes. This entry is the slice's clearest case of a domain whose own discipline already dictates a hierarchy, and §5.10: “A carefully curated existing folder should be treated as a strong expression of user intent.” means an archivist's existing arrangement should be adopted rather than replaced

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| gov.library-administration | shared premises and shared staff, different organising unit; local-studies material sits genuinely between them | §4.8: the validator checks “that each fact or label belongs to an allowed domain schema” |
| gov.public-records-foi | access decisions on closed archival material and information-request refusals are the same decision under two regimes | §3.11: “One file may hold facts from more than one domain without losing information.” |
| gov.museum-collection | documentary material inside a museum collection is catalogued as objects rather than described as records; the two disciplines produce incompatible descriptions of the same paper | §4.8: “an application packet does not silently absorb a document with a conflicting target institution” |
| pers.genealogy | a researcher's copies of archival records are genealogy material; the repository's description of them is this domain, and only the reference code connects the two | §3.8: “The system must separate roles that happen to contain the same entity type.” |

### Sensitivity

`potentially_sensitive` — Closed and part-closed material is closed because it identifies living people, and a repository routinely holds personal papers deposited on conditions. §4.9: “Rare but sensitive files such as passports, visas, and legal documents may be surfaced as protected records even when they do not meet a normal group-size threshold.” and §8.4: “Paths, complete extracted text, OCR output, file hashes, image EXIF, GPS, user edits, group memberships, and raw sensitive values should remain local.” apply. handling classes are P7's — §8.4: “The system should classify data into handling classes before LLM escalation” — and none is assigned here

### Open question — Joseph's call, unresolved

> ARCHIVAL PRACTICE CONTRADICTS §3.8 ON PURPOSE, AND THE PRODUCT SHOULD KNOW IT. §3.8 says the system “should avoid using authorship or creator identity as a destination dimension” and that “Authorship is usually metadata”. Archival arrangement is built on exactly the opposite principle: records are arranged by the body that created them, because provenance is what makes them evidence. Either the catalogue records a documented exception for this domain, or the product will keep proposing a rearrangement that destroys the meaning of the collection. Joseph decides whether a domain may declare an exception to a §3 rule.

---

## `gov.museum-collection` — Museum and gallery collection management

Managing objects held in a collection — acquisition, cataloguing, condition and conservation, location and movement, loans and exhibition, and disposal.

**Provenance:** **proposal** — new; the design names nothing like it

**Cite:** No design sentence names collections. §5.7 lists the template library's intended coverage — “covering common organizational situations such as academic programs, university applications, recruiting processes, client engagements, research workflows, financial records, travel, legal matters, creative projects, software repositories, personal administration, and photo collections” — and names nothing governmental. The object-as-unit shape is distinct from both the library item and the archival series

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `object_number` | string | the accession or object number exactly as printed | `direct` | §3.13 direct: “A direct fact was read from a reliable and explicit source, such as a content hash, EXIF timestamp, document title, or labeled form field.” — a labeled object-number field. This is the strongest identifier in the domain and its format is set by each institution, so none is asserted |
| `institution` | string | the museum or gallery holding the object | `validated` | §3.8: “The system must separate roles that happen to contain the same entity type.” — the holding institution, the lender, the maker and the donor are four roles that all appear as names on one catalogue record. Collapsing maker into institution is the characteristic error |
| `record_role` | string | condition report | `validated` | Acquisition, catalogue record, condition report, conservation record, location record, loan agreement and exhibition record are the recurring set |
| `maker_or_origin` | string | the maker or origin as recorded | `llm_supported` | §3.8: “It should avoid using authorship or creator identity as a destination dimension.” — the maker is retained as a fact for retrieval and kept out of the template for that reason |
| `exhibition_or_loan` | string | the exhibition or loan the record belongs to | `validated` | Loans and exhibitions are the projects of this domain and the reason most of its paperwork exists |
| `record_date` | date | 2026-02-18 | `direct` | §3.10: “Date candidates should be identified with explicit regular expressions and then parsed without fuzzy matching.” — a labeled record date only. Object dates are approximate by nature and are not parsed |
| `document_role` | string | condition report | `validated` | The work-type field, and the template's leaf dimension — an object file mixes acquisition papers, catalogue records, condition reports and movement records. §5.7 requires a template's dimensions to be drawn from the domain's allowed fact fields, so the level and the field must exist together. Confirmable from the same context-term list the deterministic recognisers use |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.4, §3.5):

- a collections term in a title or heading zone — 'accession' | 'condition report' | 'object record' | 'loan agreement' | 'conservation treatment' | 'deaccession' — co-occurring with a labeled object-number field or an institution name
- a condition-report structure detected as labeled object, condition and treatment fields co-occurring with an object number

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- an object photograph whose identity is recoverable only from OCR of a scale card or label in frame
- a conservation note that reads as a materials-science report
- a document from a documentation standard the recogniser has no vocabulary for

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10):

- an object-number-shaped string. §3.10 is explicit that file names and documents “frequently contain numbers that look like years but are course identifiers, version numbers, build numbers, ZIP codes, or other unrelated values”, and accession numbers look like invoice numbers and part numbers
- the word 'collection' — data collections, debt collection, garbage collection and clothing collections all compete
- the word 'exhibition' — trade shows and conferences use it constantly
- an institution name alone. §4.9's warning generalises: “A university name alone should not create a group because Columbia can appear as an authoring school, course provider, target institution, employer, research venue, or merely a cited organization.”

### Work types

`acquisition proposal`, `acquisition record`, `catalogue record`, `condition report`, `conservation treatment record`, `location and movement record`, `loan agreement`, `exhibition record`, `disposal record`, `valuation record`

### Grouping reasons (§4)

- one object across its acquisition, catalogue, condition and movement records, joined by the object number
- one exhibition or loan across the agreements, condition reports and lists it generated

### Template (§5)

`record role → object or exhibition → document role`

Time first: **no**

§5.5: “a parent dimension should provide the context required to understand the child”. Function leads because a collections corpus is navigated by activity — conservation, loans, documentation — and an object-first tree would produce one folder per object, which is exactly the many-tiny-folders outcome §5.9 warns the interface to flag

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| gov.archives-recordkeeping | documentary objects are catalogued in one discipline and described in the other; the same sheet of paper gets two incompatible records | §4.8: “an application packet does not silently absorb a document with a conflicting target institution” |
| gov.parks-public-lands | heritage sites hold collections, so one body produces both site and object records | §3.11: “One file may hold facts from more than one domain without losing information.” |
| pers.hobby-collection | a private collector's records are structurally identical to an institution's; the separating signal is whether an accession policy and a public-benefit purpose exist, which the condition report does not say | §4.8: the validator checks “that each fact or label belongs to an allowed domain schema” |
| fin.insurance | valuations and loan insurance schedules are collection records and insurance records at once | §6.9: “A file may have multiple valid organizational relationships, and the placement engine must preserve that complexity.” |

### Sensitivity

`none` — Collection records concern objects. Valuations, lender identities and security information are genuinely confidential but that is a per-file property rather than a domain default, and this catalogue does not assign handling. handling classes are P7's — §8.4: “The system should classify data into handling classes before LLM escalation” — and none is assigned here

### Open question — Joseph's call, unresolved

> IS A COLLECTIONS MANAGEMENT SYSTEM'S EXPORT A DOMAIN OR A DATABASE? Museum, library and archive documentation normally lives in a dedicated collections system, and what reaches a filesystem is an export, a working copy or a report. Modelling that as a domain risks the product proposing a folder tree that competes with the system of record, which is the opposite of what §5.10 says about respecting existing curated structure. The same question applies to library and archive administration. Joseph decides whether these three domains are in scope for tree proposals, search-only, or out of scope.

---

## `edadmin.school-district` — School district and local education administration

The administration of schools by a district, board or local education authority — admissions, statutory returns, funding allocation, staffing, inspection and school improvement.

**Provenance:** **inference** — extends the fields of a domain the design does name

**Cite:** No design sentence names education administration. §3.11 names the student-facing schema — “Academic files may use school, term, course, instructor, and work type.” — and this domain is the institution's side, which the design does not describe

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `authority_or_district` | string | the district or education authority | `validated` | §3.8: “The system must separate roles that happen to contain the same entity type.” — the district, the individual school and the inspectorate are three roles that all appear as names on one report |
| `school` | string | the school the record concerns | `validated` | The school is the second organising dimension and the one a user recognises. Confirmable only with an education-administration term beside it |
| `function` | string | admissions | `validated` | Admissions, funding, statutory returns, staffing, safeguarding, inspection and improvement are the recurring functions |
| `academic_year` | string | the academic year exactly as printed | `validated` | §3.10 names the analogous hazard directly: “Academic terms such as Spring 2025, AY 2024-25, and Michaelmas Term 2024 require dedicated patterns rather than generic parsing.” — the same is true of an administrative academic year, whose boundaries differ by jurisdiction |
| `return_or_report` | string | the statutory return as named | `validated` | Statutory returns are jurisdiction-defined and carry local names and numbers. The field is verbatim; no return name or number is asserted anywhere in this catalogue |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.4, §3.5):

- an education-administration term in a title or heading zone — 'admissions round' | 'school census' | 'statutory return' | 'funding allocation' | 'inspection report' | 'school improvement plan' — co-occurring with a district or school name
- an academic-year pattern co-occurring with an education-administration term, which is §3.5's model for a deterministic recogniser: “BUSIB 4300 becomes a course fact only when the engine finds a course-code pattern together with academic context” with the year rather than the course code as the pattern

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- a governing-body paper whose subject must be read from prose
- a staffing or budget spreadsheet whose education character is visible only from sheet names
- a return whose statutory basis has no counterpart in the reader's system, which is a genuine category difference

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10):

- a school name — it appears in the user's own academic files, in address blocks and in correspondence
- an academic-year-shaped string. §3.10 is explicit that file names and documents “frequently contain numbers that look like years but are course identifiers, version numbers, build numbers, ZIP codes, or other unrelated values”
- the word 'admissions' — universities, hospitals and clubs all admit
- the word 'district' — an administrative, electoral, postal and geographic term at once

### Work types

`admissions round record`, `allocation decision`, `statutory return`, `funding statement`, `staffing record`, `governing-body paper`, `inspection report`, `school improvement plan`, `exclusion or appeal record`

### Grouping reasons (§4)

- one school across one academic year's returns, funding and reports
- one admissions round across its applications, allocations and appeals

### Template (§5)

`school → academic year → function`

Time first: **no**

§5.5: “a parent dimension should provide the context required to understand the child” — a funding statement is legible only under its school and year. The academic year is a structural container rather than a calendar bucket, in the same way a term is in the education slice, so §5.5: “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders.” is not violated

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| acad.k12-schooling | the education slice owns a pupil's and family's side of school life; this domain is the administering body's. A school report exists in both, and the family's copy is the far more common case in a personal corpus | §3.8's worked pair: “A consulting document may mention the author’s firm and the client organization.” |
| pers.child-school-record | the personal slice owns a parent's file on their child's schooling, which contains the same admissions letters and reports | §3.8: “The system must separate roles that happen to contain the same entity type.” |
| gov.municipal-administration | in some systems schools are a service of the general local authority and the same committee cycle covers both | §4.8: “an application packet does not silently absorb a document with a conflicting target institution” |
| edadmin.institution-governance | a governing-body paper is district administration when the district writes it and institutional governance when the school does; the letterhead is the only signal and it is frequently absent | §4.8: the validator checks “that each fact or label belongs to an allowed domain schema” |

### Sensitivity

`potentially_sensitive` — Admissions, exclusion and safeguarding records concern named children, which is the most protective case in the slice after social care. §4.9: “Rare but sensitive files such as passports, visas, and legal documents may be surfaced as protected records even when they do not meet a normal group-size threshold.”. handling classes are P7's — §8.4: “The system should classify data into handling classes before LLM escalation” — and none is assigned here

---

## `edadmin.institution-governance` — Education institution governance and administration

Running an educational institution as an organisation — governing-body business, statutes and policy, registry operations, quality assurance and institutional reporting.

**Provenance:** **inference** — extends the fields of a domain the design does name

**Cite:** No design sentence names institutional administration. §3.11's academic schema — “Academic files may use school, term, course, instructor, and work type.” — describes coursework, not the institution's own business, and §5.7 lists the template library's intended coverage — “covering common organizational situations such as academic programs, university applications, recruiting processes, client engagements, research workflows, financial records, travel, legal matters, creative projects, software repositories, personal administration, and photo collections” — and names nothing governmental names “academic programs” from the student's side

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `institution` | string | the university, college or school as an organisation | `validated` | §3.8: “The system must separate roles that happen to contain the same entity type.” — the institution as employer, as awarding body, as regulated entity and as the user's own school are four roles behind one name, which is exactly the ambiguity §4.9's warning generalises: “A university name alone should not create a group because Columbia can appear as an authoring school, course provider, target institution, employer, research venue, or merely a cited organization.” describes |
| `governing_body` | string | the council, senate or committee named on the paper | `validated` | The body is the real organising dimension: one institution runs many committees each producing one document stream |
| `function` | string | quality assurance | `validated` | Governance, statutes and policy, registry, quality assurance, institutional reporting and estates are the recurring functions |
| `meeting_or_cycle` | string | the meeting or reporting cycle as printed | `direct` | §3.13 direct: “A direct fact was read from a reliable and explicit source, such as a content hash, EXIF timestamp, document title, or labeled form field.” — a labeled meeting or cycle field in a header zone |
| `academic_year` | string | the academic year exactly as printed | `validated` | §3.10: “Academic terms such as Spring 2025, AY 2024-25, and Michaelmas Term 2024 require dedicated patterns rather than generic parsing.” — and academic-year boundaries differ by jurisdiction and sometimes by institution |
| `document_role` | string | minutes | `validated` | The work-type field, and the template's leaf dimension — an agenda, its papers and its minutes are one meeting's three documents. §5.7 requires a template's dimensions to be drawn from the domain's allowed fact fields, so the level and the field must exist together. Confirmable from the same context-term list the deterministic recognisers use |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.4, §3.5):

- an institutional-governance term in a title or heading zone — 'senate' | 'academic board' | 'council papers' | 'ordinances' | 'quality assurance' | 'annual monitoring' | 'registry' — co-occurring with an institution name
- a committee-paper structure detected as a labeled paper number together with a body name and a meeting date

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- a policy document that could equally be a corporate HR policy, distinguishable only by the population it governs
- an institutional report whose audience must be read from framing
- a document whose governance structure has no counterpart in the reader's system, where 'senate', 'board' and 'council' name different things in different countries

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10):

- an institution name. §4.9's warning generalises: “A university name alone should not create a group because Columbia can appear as an authoring school, course provider, target institution, employer, research venue, or merely a cited organization.” is written about exactly this case: a university name appears as the user's own school, their employer, an application target and a cited body
- the word 'board' — corporate, sporting, circuit and surfing senses compete
- the word 'policy' — insurance, privacy and configuration senses dominate
- an academic-year-shaped string. §3.10 is explicit that file names and documents “frequently contain numbers that look like years but are course identifiers, version numbers, build numbers, ZIP codes, or other unrelated values”

### Work types

`governing-body agenda`, `committee paper`, `minutes`, `statute or ordinance`, `institutional policy`, `registry operations record`, `quality assurance report`, `institutional return`, `strategic plan`

### Grouping reasons (§4)

- one body across one academic year's meetings
- one policy across its drafts, approval paper and published version

### Template (§5)

`governing body → academic year → document role`

Time first: **no**

§5.5: “a parent dimension should provide the context required to understand the child” — minutes are legible only under their body and cycle. The institution does not lead because for most users there is one, which §5.7 forbids a template that would “use an author or organization merely as a collector” forbids as a level

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| acad.undergraduate-program | the education slice owns the programme as a student experiences it; this domain owns the institution's own record of approving and monitoring it. Overlapping paperwork, opposite viewpoints | §3.8's worked pair: “A consulting document may mention the author’s firm and the client organization.” |
| acad.curriculum-development | a programme approval document is curriculum work for the academic who wrote it and a governance paper for the committee that approved it | §3.11: “One file may hold facts from more than one domain without losing information.” |
| edadmin.accreditation-body | a self-assessment is institutional quality assurance and accreditation evidence at once; the separating signal is which body it was written for | §3.8: “The system must separate roles that happen to contain the same entity type.” |
| acad.accreditation-institutional | the education slice already owns institutional accreditation from the institution's side, so this domain must not re-model it and defers on that seam | §4.8: the validator checks “that each fact or label belongs to an allowed domain schema” |

### Sensitivity

`none` — Governance business concerns the institution rather than identified individuals. Reserved items covering staff and student cases are the exception and are a per-file property. handling classes are P7's — §8.4: “The system should classify data into handling classes before LLM escalation” — and none is assigned here

### Open question — Joseph's call, unresolved

> DOES EDUCATION ADMINISTRATION LIVE UNDER ACADEMICS OR NEXT TO IT? §5.1 names “Academics” as a candidate top-level branch, and for a student it means their coursework. For a registrar, a governor or a school administrator, this material is their work and coursework is not in their corpus at all. Filing institutional governance under Academics would put a professional's working files under a branch named for something they do not do; giving it its own branch splits one institution's name across two top-level areas. Joseph decides, and the answer probably follows whatever he decides about professional public-sector work generally.

---

## `edadmin.accreditation-body` — Accreditation and quality assurance bodies (assessor side)

An accrediting or quality-assurance body's record of reviewing an institution or programme — standards, submissions received, review visits, findings and decisions.

**Provenance:** **proposal** — new; the design names nothing like it

**Cite:** No design sentence names accreditation bodies. §5.7 lists the template library's intended coverage — “covering common organizational situations such as academic programs, university applications, recruiting processes, client engagements, research workflows, financial records, travel, legal matters, creative projects, software repositories, personal administration, and photo collections” — and names nothing governmental. Written as the assessor-side counterpart to the institution-side domain the education slice already owns, which is §3.8: “The system must separate roles that happen to contain the same entity type.”

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `accrediting_body` | string | the body conducting the review | `validated` | §3.8's worked pair: “A consulting document may mention the author’s firm and the client organization.” — the accrediting body and the institution under review are the pair. Which of the two holds the file changes the domain, not the document |
| `institution_or_programme` | string | the institution or programme under review | `validated` | The subject of the review. Confirmable only with an accreditation term beside it |
| `review_cycle` | string | the review cycle or round as printed | `direct` | §3.13 direct: “A direct fact was read from a reliable and explicit source, such as a content hash, EXIF timestamp, document title, or labeled form field.” — a labeled cycle field. Cycle lengths and their names are set by each body |
| `record_role` | string | review panel report | `validated` | Standards, self-assessment received, evidence, visit record, panel report, decision and condition-monitoring are the recurring set |
| `outcome` | string | accredited with conditions | `validated` | The decision is what the whole file exists to produce, and it is confirmable from a decision-structure heading |
| `decision_date` | date | 2026-06-30 | `direct` | §3.10: “Date candidates should be identified with explicit regular expressions and then parsed without fuzzy matching.” — a labeled decision date only |
| `document_role` | string | panel report | `validated` | The work-type field, and the template's leaf dimension — a review is a submission, evidence, a visit record, a report and a decision. §5.7 requires a template's dimensions to be drawn from the domain's allowed fact fields, so the level and the field must exist together. Confirmable from the same context-term list the deterministic recognisers use |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.4, §3.5):

- an accreditation term in a title or heading zone — 'accreditation' | 'self-assessment' | 'review panel' | 'standards for' | 'conditions of accreditation' | 'reaccreditation' — co-occurring with a named institution or programme
- a standards-mapping structure detected as labeled standard, evidence and judgement columns co-occurring with an accreditation term. §2.3: “Tables matter because resumes, forms, applications, invoices, and administrative documents often place their most useful information in cells rather than body paragraphs.”

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- an evidence document submitted for review that is an ordinary institutional document in every other respect
- a panel note whose review it belongs to must be inferred from the standards it references
- a review conducted under a national framework the recogniser has no vocabulary for

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10):

- the word 'accreditation' — laboratory, certification, press and security-clearance senses all compete
- the word 'standards' — the most generic word available, and one this slice has a whole other domain for
- an institution name alone. §4.9's warning generalises: “A university name alone should not create a group because Columbia can appear as an authoring school, course provider, target institution, employer, research venue, or merely a cited organization.”
- the word 'review' — code review, peer review, performance review and film review are all elsewhere in this catalogue

### Work types

`standards document`, `guidance for institutions`, `self-assessment received`, `evidence submission`, `visit schedule`, `panel report`, `decision letter`, `conditions monitoring record`, `appeal record`

### Grouping reasons (§4)

- one review across its self-assessment, evidence, visit, report and decision
- one institution across its successive review cycles

### Template (§5)

`institution or programme → review cycle → document role`

Time first: **no**

§5.5: “a parent dimension should provide the context required to understand the child” — a panel report is legible only under the review it concludes. §5.5: “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders.” keeps the subject first and the cycle second

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| acad.accreditation-institutional | the education slice owns the institution's side of exactly this review, and the self-assessment document is byte-identical in both files | §3.8's worked pair: “A consulting document may mention the author’s firm and the client organization.” |
| edadmin.institution-governance | quality assurance is a governance function of the institution and a core activity of the body; the same standards document appears in both | §3.11: “One file may hold facts from more than one domain without losing information.” |
| gov.professional-regulator | many professions accredit the education route and regulate the practitioner, sometimes in one body; the separating signal is whether the subject is a programme or a person | §4.8: the validator checks “that each fact or label belongs to an allowed domain schema” |
| civic.standards-body | both write standards; the separating signal is whether the standard is applied by assessing an institution or adopted voluntarily by anyone | §4.8: “an application packet does not silently absorb a document with a conflicting target institution” |

### Sensitivity

`none` — Accreditation concerns institutions and programmes. Named-staff and named-student evidence appears in submissions and is a per-file property. handling classes are P7's — §8.4: “The system should classify data into handling classes before LLM escalation” — and none is assigned here

---

## `civic.standards-body` — Standards development bodies

The process by which a standards organisation develops and maintains a voluntary standard — committees, working drafts, ballots and comment resolution, publication and review.

**Provenance:** **proposal** — new; the design names nothing like it

**Cite:** No design sentence names standards bodies. §5.7 lists the template library's intended coverage — “covering common organizational situations such as academic programs, university applications, recruiting processes, client engagements, research workflows, financial records, travel, legal matters, creative projects, software repositories, personal administration, and photo collections” — and names nothing governmental. The draft-ballot-publish cycle is a stage-bearing process in the sense of §3.3 gives rules “routing obvious files into plausible domains” and sends the rest to the model

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `standard` | string | the standard's title as printed on its cover | `validated` | The standard is the container. Its designation is a separate field because designations are assigned per body and are not interpretable without knowing which body |
| `standards_body` | string | the organisation maintaining the standard | `validated` | §3.8: “The system must separate roles that happen to contain the same entity type.” — the maintaining body, the committee, the member organisations voting and the organisation adopting the standard are four roles |
| `designation` | string | the standard's designation exactly as printed | `direct` | §3.13 direct: “A direct fact was read from a reliable and explicit source, such as a content hash, EXIF timestamp, document title, or labeled form field.” — printed on the cover. Deliberately no format example: designation schemes belong to each body and a plausible invented one would assert a standard that may not exist |
| `stage` | string | committee draft | `validated` | Working draft, committee draft, ballot, comment resolution, published and under review. The stage is what stops a superseded draft being read as the operative standard, which is the real-world harm this field prevents |
| `committee` | string | the committee or working group named on the draft | `validated` | The committee is the organising unit for anyone actually working in this domain |
| `edition_or_version` | string | the edition or amendment as printed | `direct` | §3.13 direct: “A direct fact was read from a reliable and explicit source, such as a content hash, EXIF timestamp, document title, or labeled form field.”. Standards corpora are dominated by superseded editions, so the version carries unusual weight |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.4, §3.5):

- a standards-process term in a title or heading zone — 'committee draft' | 'working draft' | 'ballot comments' | 'comment resolution' | 'normative reference' | 'this standard specifies' — co-occurring with a body name or a labeled designation
- a comment-resolution structure detected as labeled comment, disposition and clause columns co-occurring with a designation. §2.3: “Tables matter because resumes, forms, applications, invoices, and administrative documents often place their most useful information in cells rather than body paragraphs.”

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- an internal position paper on a standard that is neither a draft nor a comment
- a liaison document between bodies whose role must be read from prose
- a designation that belongs to a body the recogniser has no list for, which is the normal case rather than the exception

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10):

- a designation-shaped string. §3.10 is explicit that file names and documents “frequently contain numbers that look like years but are course identifiers, version numbers, build numbers, ZIP codes, or other unrelated values”, and standard designations look like part numbers, invoice numbers and document control numbers
- the word 'standard' — a standard rate, a standard form, a standard library and standard practice all outnumber this sense
- the word 'draft' — the highest-frequency document word there is
- a body's name alone. §4.9's warning generalises: “A university name alone should not create a group because Columbia can appear as an authoring school, course provider, target institution, employer, research venue, or merely a cited organization.”

### Work types

`work item proposal`, `working draft`, `committee draft`, `ballot record`, `comment resolution`, `published standard`, `amendment`, `review or withdrawal record`, `liaison document`

### Grouping reasons (§4)

- one standard across its drafts, ballots, comments and published editions
- one committee across the work items it holds

### Template (§5)

`standard → edition → stage`

Time first: **no**

§5.5: “a parent dimension should provide the context required to understand the child” — a ballot record is meaningless without the standard and the edition it belongs to. §5.5: “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders.”, and edition rather than year is the correct time-like dimension because standards are versioned, not dated

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| soft.api-specification | a technical specification and a published standard are the same shape of document; the separating signal is whether a standards process with ballots produced it | §4.8: the validator checks “that each fact or label belongs to an allowed domain schema” |
| res.reference-library | a downloaded published standard in someone's corpus is reference material they consult, not a record of the process that made it. This is the common case and the domain should defer to it | §3.8: “The system must separate roles that happen to contain the same entity type.” |
| corp.compliance-audit | an organisation's evidence of conforming to a standard is compliance material; the standard itself is this domain | §3.8's worked pair: “A consulting document may mention the author’s firm and the client organization.” |
| edadmin.accreditation-body | both write standards; assessment against them is what separates the two processes | §4.8: “an application packet does not silently absorb a document with a conflicting target institution” |

### Sensitivity

`none` — Standards development concerns technical content and organisational participation. Ballot positions are attributable to member organisations rather than to individuals. handling classes are P7's — §8.4: “The system should classify data into handling classes before LLM escalation” — and none is assigned here

### Open question — Joseph's call, unresolved

> MOST PEOPLE HOLDING STANDARDS ARE READERS, NOT PARTICIPANTS. A corpus containing published standards almost always belongs to someone who consults them, and the process record — drafts, ballots, comment resolutions — exists only for the small number who sit on committees. Modelling the process risks the recogniser claiming files that are simply reference documents. Joseph decides whether this domain ships at all, or whether published standards are better handled as reference material with a designation fact attached.

---

## `npo.governance` — Nonprofit and charity governance

The constitutional and board-level record of a nonprofit — governing document, registration, trustee or board business, policies, annual reporting and regulatory returns.

**Provenance:** **proposal** — new; the design names nothing like it

**Cite:** No design sentence names nonprofit governance. §5.7 lists the template library's intended coverage — “covering common organizational situations such as academic programs, university applications, recruiting processes, client engagements, research workflows, financial records, travel, legal matters, creative projects, software repositories, personal administration, and photo collections” — and names nothing governmental. Distinct from the corporate domains the finance-admin slice owns because the governing document, the regulator and the reporting duties are different objects

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `organisation` | string | the nonprofit as named in its governing document | `validated` | §3.8: “The system must separate roles that happen to contain the same entity type.” — the organisation, its regulator, its funders and its trading subsidiary are four roles behind names that appear on one annual report |
| `governing_body` | string | the board or trustee body named on the paper | `validated` | The body is the organising unit for meeting-cycle documents, in the same way a committee is for a public authority |
| `registration_reference` | string | the registration number exactly as printed | `direct` | §3.13 direct: “A direct fact was read from a reliable and explicit source, such as a content hash, EXIF timestamp, document title, or labeled form field.” — printed on formal documents. No format is asserted: nonprofit registration schemes and even whether registration exists differ by jurisdiction |
| `record_role` | string | annual report and accounts | `validated` | Governing document, board papers, policy, annual report, regulatory return and audit are the recurring set |
| `financial_year` | string | the financial year exactly as printed | `validated` | Nonprofit financial years are chosen by the organisation and rarely align to a calendar year, which is why the field stores the printed string. §3.10 is explicit that file names and documents “frequently contain numbers that look like years but are course identifiers, version numbers, build numbers, ZIP codes, or other unrelated values” |
| `jurisdiction` | string | the polity the organisation is registered in | `possible` | Legal forms for nonprofits differ so much between systems that the entity type is not translatable. §3.13 possible: “A possible fact is a useful but insufficient clue” |
| `document_role` | string | board minutes | `validated` | The work-type field, and the template's leaf dimension — a governance year mixes constitutional documents, meeting papers, accounts and returns. §5.7 requires a template's dimensions to be drawn from the domain's allowed fact fields, so the level and the field must exist together. Confirmable from the same context-term list the deterministic recognisers use |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.4, §3.5):

- a governance term in a title or heading zone — 'trustees' report' | 'constitution' | 'articles of association' | 'board minutes' | 'annual report and accounts' | 'registered charity' — co-occurring with an organisation name or a labeled registration reference
- an annual-report structure detected as labeled governance, objectives and financial-review sections co-occurring with a financial-year field

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- a policy document indistinguishable in form from a corporate one, where only the population it governs identifies it
- board minutes with no letterhead
- a document whose legal form has no counterpart in the reader's jurisdiction, which changes what the organisation is rather than what it is called

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10):

- the word 'charity' — it is a virtue, an event theme and a fundraising adjective
- the words 'board' or 'trustee' — corporate, pension and school senses compete
- a registration-shaped number. §3.10 is explicit that file names and documents “frequently contain numbers that look like years but are course identifiers, version numbers, build numbers, ZIP codes, or other unrelated values”
- an organisation name alone. §4.9's warning generalises: “A university name alone should not create a group because Columbia can appear as an authoring school, course provider, target institution, employer, research venue, or merely a cited organization.”

### Work types

`governing document`, `registration record`, `board or trustee agenda`, `board minutes`, `organisational policy`, `annual report and accounts`, `regulatory return`, `audit or examination report`, `risk register`

### Grouping reasons (§4)

- one financial year across its accounts, report, return and audit — §3.9: “The documents are content-incoherent but purpose-coherent.”
- one governing body across a run of meetings

### Template (§5)

`record role → financial year → document role`

Time first: **no**

§5.5: “a parent dimension should provide the context required to understand the child”. Function leads because a small nonprofit's corpus is navigated by what the document is for, and the organisation does not lead because there is only one, which §5.7 forbids a template that would “use an author or organization merely as a collector” forbids. §5.5: “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders.”

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| corp.business-formation | the finance-admin slice owns formation and corporate records generally; a nonprofit's governing document is the same kind of object under a different legal form | §3.11: “One file may hold facts from more than one domain without losing information.” |
| corp.regulatory-filings | a charity regulator return is a regulatory filing; the finance-admin slice's domain describes it as well as this one does | §4.8: the validator checks “that each fact or label belongs to an allowed domain schema” |
| biz.bookkeeping | a nonprofit's accounts are bookkeeping; the fund-accounting structure is the only real difference and it is not visible in a bank statement | §3.8: “The system must separate roles that happen to contain the same entity type.” |
| npo.fundraising-donor | the annual report contains fundraising results, and donor records support the accounts; the two domains feed each other without merging | §6.9: “A file may have multiple valid organizational relationships, and the placement engine must preserve that complexity.” |

### Sensitivity

`none` — Governance material concerns the organisation, and much of it is published. Board papers about named staff or beneficiaries are the exception and are a per-file property. handling classes are P7's — §8.4: “The system should classify data into handling classes before LLM escalation” — and none is assigned here

### Open question — Joseph's call, unresolved

> A NONPROFIT'S FINANCE RECORDS ARE ALREADY OWNED BY THE FINANCE SLICE. `biz.bookkeeping`, `corp.regulatory-filings`, `corp.business-formation` and `fin.charitable-giving` between them cover most of what a small charity's filing cabinet holds, and this domain adds a governance layer on top. Either the nonprofit is a lens over the finance domains — a fact rather than a domain — or it is a domain that duplicates them. Joseph decides; the risk of getting it wrong is a user whose charity's accounts land in one branch and its trustees' report in another.

---

## `npo.fundraising-donor` — Fundraising and donor records

Raising money from supporters and recording who gave — appeals and campaigns, donor and gift records, tax-relief claims, events, and stewardship.

**Provenance:** **proposal** — new; the design names nothing like it

**Cite:** No design sentence names fundraising. §5.7 lists the template library's intended coverage — “covering common organizational situations such as academic programs, university applications, recruiting processes, client engagements, research workflows, financial records, travel, legal matters, creative projects, software repositories, personal administration, and photo collections” — and names nothing governmental. Written as the recipient-organisation counterpart to the finance-admin slice's giving domain, which is §3.8: “The system must separate roles that happen to contain the same entity type.”

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `appeal_or_campaign` | string | the appeal as named in its materials | `validated` | The appeal is the container for materials, results and thanking. Confirmable with a fundraising context term beside it |
| `organisation` | string | the fundraising organisation | `validated` | §3.8's worked pair: “A consulting document may mention the author’s firm and the client organization.” — the organisation and the donor are the pair, and this domain is written from the organisation's side |
| `record_role` | string | gift record | `validated` | Appeal material, gift record, pledge, tax-relief claim, event record and stewardship communication are the recurring set |
| `donor` | string | the supporter named on the gift record | `direct` | §3.13 direct: “A direct fact was read from a reliable and explicit source, such as a content hash, EXIF timestamp, document title, or labeled form field.” from a labeled donor field, and deliberately excluded from the template: a folder named for a donor is disclosure by directory listing, and §3.8: “A folder should not become a collection point for everything produced by the same person or organization.” |
| `campaign_period` | date range | 2026-11-01 to 2026-12-31 | `direct` | §3.10: “Date candidates should be identified with explicit regular expressions and then parsed without fuzzy matching.” — labeled appeal-period fields only |
| `restriction` | string | restricted to a named project | `direct` | §3.13 direct: “A direct fact was read from a reliable and explicit source, such as a content hash, EXIF timestamp, document title, or labeled form field.” — gift and fund records carry a labeled restricted/unrestricted field. §3.11 permits “several additional fields used only for search, privacy protection, explanation, or later review”. Whether a gift is restricted governs what may be done with it, and it is the fact that connects a donor record to a grant report |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.4, §3.5):

- a fundraising term in a title or heading zone — 'appeal' | 'donation' | 'gift aid' | 'pledge' | 'supporter' | 'fundraising event' | 'legacy gift' — co-occurring with an organisation name or a labeled appeal period
- a donor-record structure detected as labeled donor, gift and date columns co-occurring with an organisation name. §2.3: “Tables matter because resumes, forms, applications, invoices, and administrative documents often place their most useful information in cells rather than body paragraphs.”

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- a thank-you letter that reads as ordinary correspondence
- an appeal leaflet with no organisational identifier outside a logo region
- a tax-relief scheme that exists in one jurisdiction and has no counterpart in another, which changes which documents should exist at all

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10):

- a currency amount — every administrative corpus is full of them
- the word 'donation' — it appears in receipts, tax records and unrelated correspondence, and the finance-admin slice owns the giver's side
- the word 'appeal' — legal appeals, regulatory appeals and the ordinary verb all compete, and two other domains in this slice use it
- an organisation name alone. §4.9's warning generalises: “A university name alone should not create a group because Columbia can appear as an authoring school, course provider, target institution, employer, research venue, or merely a cited organization.”

### Work types

`appeal material`, `donor record`, `gift record`, `pledge record`, `tax-relief claim`, `fundraising event record`, `stewardship communication`, `legacy record`, `fundraising performance report`

### Grouping reasons (§4)

- one appeal across its materials, results and thanking
- one restricted fund across the gifts to it and the reporting on it

### Template (§5)

`appeal or campaign → record role → period`

Time first: **no**

§5.5: “a parent dimension should provide the context required to understand the child” — a gift record is legible under its appeal. The donor is deliberately absent as a level for the reason given in the schema. §5.5: “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders.”

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| fin.charitable-giving | the finance-admin slice owns the donor's own record of giving; the receipt is the same document at both ends | §3.8's worked pair: “A consulting document may mention the author’s firm and the client organization.” |
| npo.governance | fundraising results appear in the annual report and donor records support the accounts | §6.9: “A file may have multiple valid organizational relationships, and the placement engine must preserve that complexity.” |
| civic.political-campaign | political and charitable donation records are structurally identical and legally distinct; the receiving organisation's character is the only signal | §4.8: “an application packet does not silently absorb a document with a conflicting target institution” |
| npo.volunteer-management | supporters are frequently volunteers and appear in both files under one name; §3.8: “The system must separate roles that happen to contain the same entity type.” | §3.8's worked pair: “A consulting document may mention the author’s firm and the client organization.” |

### Sensitivity

`potentially_sensitive` — Donor records tie named individuals to their address, their giving and often to a cause that reveals something about them; legacy records concern people's deaths. §2.9's phrase “while treating addresses and message content as potentially sensitive” and §2.9 on address-book data: it “should normally be privacy-protected rather than used to create folder proposals” both describe this data exactly. handling classes are P7's — §8.4: “The system should classify data into handling classes before LLM escalation” — and none is assigned here

---

## `npo.volunteer-management` — Volunteer management

Recruiting, checking, deploying and supporting volunteers — roles, applications and references, background checks, training, rotas, hours and recognition.

**Provenance:** **proposal** — new; the design names nothing like it

**Cite:** No design sentence names volunteering from the organisation's side. §5.7 lists the template library's intended coverage — “covering common organizational situations such as academic programs, university applications, recruiting processes, client engagements, research workflows, financial records, travel, legal matters, creative projects, software repositories, personal administration, and photo collections” — and names nothing governmental. Structurally the recruiting shape the career slice owns, applied to unpaid roles, per §3.8: “The system must separate roles that happen to contain the same entity type.”

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `organisation` | string | the organisation recruiting volunteers | `validated` | §3.8's worked pair: “A consulting document may mention the author’s firm and the client organization.” — the organisation and the volunteer are the pair, and this domain is written from the organisation's side |
| `role` | string | the volunteer role as named in its description | `validated` | The role is the organising unit: descriptions, applications, training and rotas all attach to one |
| `record_role` | string | background check record | `validated` | Role description, application, reference, background check, training, rota, hours record and recognition are the recurring set, and they have very different sensitivities |
| `volunteer` | string | the named volunteer | `direct` | §3.13 direct: “A direct fact was read from a reliable and explicit source, such as a content hash, EXIF timestamp, document title, or labeled form field.” from a labeled field, and excluded from the template for the same reason as donors and service users |
| `activity_period` | date range | 2026-03-01 to 2026-11-30 | `direct` | §3.10: “Date candidates should be identified with explicit regular expressions and then parsed without fuzzy matching.” — labeled period fields only |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.4, §3.5):

- a volunteering term in a title or heading zone — 'volunteer role' | 'volunteer application' | 'volunteer agreement' | 'rota' | 'volunteer hours' | 'safeguarding check' — co-occurring with an organisation name
- a rota structure detected as a labeled grid of names against shifts co-occurring with a volunteering term

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- an application that reads as an ordinary job application
- a training record indistinguishable from a workplace one
- a background-check regime that exists in one jurisdiction and has no counterpart in another, where the check itself is a different legal object

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10):

- the word 'volunteer' — it is a verb and appears in research recruitment, clinical trials and ordinary prose
- the word 'rota' or 'roster' — every workplace has one
- a person's name. §3.8: “It should avoid using authorship or creator identity as a destination dimension.”
- an organisation name alone. §4.9's warning generalises: “A university name alone should not create a group because Columbia can appear as an authoring school, course provider, target institution, employer, research venue, or merely a cited organization.”

### Work types

`role description`, `volunteer application`, `reference`, `background check record`, `volunteer agreement`, `training record`, `rota`, `hours record`, `expenses claim`, `recognition record`

### Grouping reasons (§4)

- one role across its description, applications, training and rotas
- one activity period across the rotas and hours records that cover it

### Template (§5)

`role → record role → period`

Time first: **no**

§5.5: “a parent dimension should provide the context required to understand the child” — a rota is legible under its role. The volunteer is deliberately not a level. §5.5: “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders.”

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| pers.volunteering | the personal slice owns the volunteer's own record of what they did; this domain is the organisation's file on them. The agreement is the same document at both ends | §3.8's worked pair: “A consulting document may mention the author’s firm and the client organization.” |
| career.job-application | a volunteer application and a job application are structurally identical; the separating signal is whether the role is paid, which the form often does not say | §4.8: the validator checks “that each fact or label belongs to an allowed domain schema” |
| career.payroll | expenses and honoraria blur the paid/unpaid line and produce payroll-shaped records in a volunteer file | §4.8: “an application packet does not silently absorb a document with a conflicting target institution” |
| npo.fundraising-donor | the same supporter is often in both files under one name | §3.8: “The system must separate roles that happen to contain the same entity type.” |

### Sensitivity

`potentially_sensitive` — Volunteer files hold references, addresses and background-check outcomes for named individuals, and a background check is among the most consequential records any small organisation holds. §4.9: “Rare but sensitive files such as passports, visas, and legal documents may be surfaced as protected records even when they do not meet a normal group-size threshold.”. handling classes are P7's — §8.4: “The system should classify data into handling classes before LLM escalation” — and none is assigned here

---

## `npo.grant-reporting-recipient` — Grant reporting (recipient side, non-research)

What a funded organisation owes its funder after the award — narrative and financial reports, claims and drawdowns, variation requests, monitoring visits and closure.

**Provenance:** **proposal** — new; the design names nothing like it

**Cite:** No design sentence names recipient-side reporting. §3.11's schema list names no grant fields at all. The research slice owns the research case; §5.7 lists the template library's intended coverage — “covering common organizational situations such as academic programs, university applications, recruiting processes, client engagements, research workflows, financial records, travel, legal matters, creative projects, software repositories, personal administration, and photo collections” — and names nothing governmental names research workflows but no general grant workflow

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `award_reference` | string | the funder's award reference exactly as printed | `direct` | §3.13 direct: “A direct fact was read from a reliable and explicit source, such as a content hash, EXIF timestamp, document title, or labeled form field.” — a labeled award field, and the key that connects everything in this domain to the funder's own file. No format asserted |
| `funder` | string | the body that made the award | `validated` | §3.8's worked pair: “A consulting document may mention the author’s firm and the client organization.” — funder and recipient, seen from the recipient's end |
| `programme` | string | the funding programme the award sits under | `possible` | Retained so a recipient's reports retrieve alongside the funder's programme records where both exist. A recipient's own reports frequently name the award and not the programme, so the value is usually inferred from the funder rather than read. §3.13 possible: “A possible fact is a useful but insufficient clue” |
| `report_type` | string | narrative report | `validated` | Narrative report, financial report, claim, variation request, monitoring visit note and closure report are the recurring set, and mixing narrative with financial is the characteristic filing error |
| `reporting_period` | date range | 2026-04-01 to 2026-09-30 | `direct` | §3.10: “Date candidates should be identified with explicit regular expressions and then parsed without fuzzy matching.” — labeled period fields only. Reports are serial and near-identical, so the period is the only thing that distinguishes them |
| `restriction` | string | restricted to a named activity | `direct` | §3.13 direct: “A direct fact was read from a reliable and explicit source, such as a content hash, EXIF timestamp, document title, or labeled form field.” — conditions of grant carry a labeled restriction. §3.11 permits “several additional fields used only for search, privacy protection, explanation, or later review”, and it is the fact that connects an award to the donor-side restriction record |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.4, §3.5):

- a grant-reporting term in a title or heading zone — 'monitoring report' | 'grant claim' | 'drawdown' | 'end of grant report' | 'variation request' | 'conditions of grant' — co-occurring with a labeled award reference or a funder name
- a claim structure detected as labeled budget-line, spend and variance columns co-occurring with an award reference. §2.3: “Tables matter because resumes, forms, applications, invoices, and administrative documents often place their most useful information in cells rather than body paragraphs.”

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- a narrative report that reads as an ordinary organisational update
- a report whose award is never referenced and must be inferred from the activities described
- a funding instrument that is a grant in one jurisdiction's law and a service contract in another's, which changes the obligations rather than the wording

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10):

- the word 'report' — the single most generic document word available
- a currency amount — needs an award reference or a budget-line structure beside it
- a reporting period alone. §3.10 is explicit that file names and documents “frequently contain numbers that look like years but are course identifiers, version numbers, build numbers, ZIP codes, or other unrelated values”
- a funder's name alone. §4.9's warning generalises: “A university name alone should not create a group because Columbia can appear as an authoring school, course provider, target institution, employer, research venue, or merely a cited organization.”

### Work types

`grant agreement received`, `conditions of grant`, `narrative report`, `financial report`, `claim or drawdown`, `variation request`, `monitoring visit note`, `closure report`, `evaluation`

### Grouping reasons (§4)

- one award across its agreement, claims, reports and closure, joined by the award reference
- one reporting period across the narrative and financial reports covering it — §3.9: “The documents are content-incoherent but purpose-coherent.”

### Template (§5)

`award → reporting period → report type`

Time first: **no**

§5.5: “a parent dimension should provide the context required to understand the child” — a claim is meaningless without the award. The period comes second because reports are serial and otherwise indistinguishable, which is the narrow case §5.5: “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders.” allows below the subject level

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| gov.grant-programme-administration | the funder holds every one of these documents too; the recipient wrote them and the funder received them, and neither copy differs | §3.8's worked pair: “A consulting document may mention the author’s firm and the client organization.” |
| res.grant-reporting | the research slice owns reporting on research awards, and a research charity's award is genuinely both. The prefix, not the document, is what separates them | §4.8: the validator checks “that each fact or label belongs to an allowed domain schema” |
| fin.grants-received | the finance-admin slice owns the received grant as income; this domain owns the obligation that came with it | §3.11: “One file may hold facts from more than one domain without losing information.” |
| npo.governance | restricted-fund reporting appears in the annual accounts, so the same figures live in both | §6.9: “A file may have multiple valid organizational relationships, and the placement engine must preserve that complexity.” |

### Sensitivity

`none` — Reporting concerns the organisation's own activity. Beneficiary case studies inside narrative reports are the exception and are a per-file property. handling classes are P7's — §8.4: “The system should classify data into handling classes before LLM escalation” — and none is assigned here

---

## `civic.advocacy-campaign` — Advocacy and public campaigning

Organised effort to change a decision or policy — campaign strategy, research and briefings, submissions, media and public materials, supporter mobilisation and outcome.

**Provenance:** **proposal** — new; the design names nothing like it

**Cite:** No design sentence names advocacy. §5.7 lists the template library's intended coverage — “covering common organizational situations such as academic programs, university applications, recruiting processes, client engagements, research workflows, financial records, travel, legal matters, creative projects, software repositories, personal administration, and photo collections” — and names nothing governmental. Held together by purpose rather than content, which is §3.9: “Purpose must be a first-class facet.”

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `campaign` | string | the campaign as its own materials name it | `llm_supported` | Campaigns are named in prose and in folder names rather than in labeled fields. §3.9: “Purpose may be supported strongly by an existing user-created folder name or explicit language in a form or portal.” — an existing folder name is frequently the strongest evidence available |
| `campaigning_organisation` | string | the organisation or coalition running the campaign | `validated` | §3.8: “The system must separate roles that happen to contain the same entity type.” — the campaigner, the decision-maker being targeted and the coalition partners are three roles |
| `target_decision` | string | the decision or policy the campaign seeks to change | `llm_supported` | §3.9: “Topic answers what a file is about, while purpose answers what the file was for.” — the target is the purpose and it is almost never a labeled field. §3.5: the model “can only propose facts that belong to the active domain schema, and it must cite exact supporting evidence already extracted from the file.” |
| `record_role` | string | briefing | `validated` | Strategy, research, briefing, submission, media material, supporter communication and outcome record are the recurring set |
| `campaign_period` | date range | 2026-02-01 to 2026-10-31 | `possible` | Campaign boundaries are rarely stated and are usually inferred from activity, which is exactly §3.13 possible: “A possible fact is a useful but insufficient clue” |
| `document_role` | string | policy briefing | `validated` | The work-type field, and the template's leaf dimension — a campaign packet is content-incoherent and purpose-coherent, so the role is what makes any single file findable inside it. §5.7 requires a template's dimensions to be drawn from the domain's allowed fact fields, so the level and the field must exist together. Confirmable from the same context-term list the deterministic recognisers use |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.4, §3.5):

- a campaigning term in a title or heading zone — 'campaign briefing' | 'call to action' | 'sign the petition' | 'our submission' | 'press release' | 'supporter update' — co-occurring with a campaigning organisation name
- a submission structure detected as a labeled addressee body together with numbered response sections and a campaigning organisation name in the footer zone

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- a briefing document indistinguishable in form from a policy paper, where only the framing identifies the advocacy purpose
- a heterogeneous packet — a briefing, a petition export, an image and a press release — that is coherent only by purpose. §3.9: “The documents are content-incoherent but purpose-coherent.”
- supporter emails that are structurally ordinary mailing-list messages

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10):

- the word 'campaign' — marketing and advertising campaigns outnumber advocacy campaigns overwhelmingly
- the word 'petition' — a legal filing in some systems and a request in others
- the word 'briefing' — every workplace produces them
- an organisation name alone. §4.9's warning generalises: “A university name alone should not create a group because Columbia can appear as an authoring school, course provider, target institution, employer, research venue, or merely a cited organization.”

### Work types

`campaign strategy`, `research or evidence brief`, `policy briefing`, `consultation or inquiry submission`, `petition record`, `press release`, `media coverage record`, `supporter communication`, `outcome or evaluation note`

### Grouping reasons (§4)

- one campaign across its strategy, research, submissions, materials and outcome — §3.9: “The documents are content-incoherent but purpose-coherent.” is the reason this group holds together at all
- one moment of the campaign — a submission deadline, a vote, a launch — across everything produced for it

### Template (§5)

`campaign → record role → document role`

Time first: **no**

§5.5: “a parent dimension should provide the context required to understand the child” — a briefing is legible only under its campaign. §5.7 forbids a template that would “use an author or organization merely as a collector” keeps the organisation out of the order for a single-organisation corpus. The campaign level is backed by an `llm_supported` fact, so in practice it comes from an existing folder name or a user-confirmed label rather than from a rule: §3.9: “Purpose may be supported strongly by an existing user-created folder name or explicit language in a form or portal.”, and §5.10: “A carefully curated existing folder should be treated as a strong expression of user intent.”

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| gov.public-consultation | a campaign submission is a consultation response and a campaign output; the topic is the consultation and the purpose is the campaign | §3.9: “Topic answers what a file is about, while purpose answers what the file was for.” |
| gov.legislative-record | written evidence to a committee is a legislative record for the committee and a campaign artefact for its author | §3.8's worked pair: “A consulting document may mention the author’s firm and the client organization.” |
| civic.political-campaign | issue campaigning and electoral campaigning produce the same artefacts; a poll and a candidacy are what separate them, and campaign literature often shows neither | §4.8: the validator checks “that each fact or label belongs to an allowed domain schema” |
| civic.community-organising | organising builds the group and campaigning targets a decision; the same meeting note can be either, and often is both | §4.8: “an application packet does not silently absorb a document with a conflicting target institution” |

### Sensitivity

`potentially_sensitive` — Supporter lists, petition exports and mobilisation records tie named individuals to a position on a contested question, which is §2.9's phrase “while treating addresses and message content as potentially sensitive” and is the same shape of data §2.9 on address-book data: it “should normally be privacy-protected rather than used to create folder proposals” describes. handling classes are P7's — §8.4: “The system should classify data into handling classes before LLM escalation” — and none is assigned here

---

## `civic.community-organising` — Community organising and mutual aid

Building and running a local or member-led group — meetings, membership, shared resources, projects, small grants and the record of what the group did.

**Provenance:** **proposal** — new; the design names nothing like it

**Cite:** No design sentence names community organising. §5.7 lists the template library's intended coverage — “covering common organizational situations such as academic programs, university applications, recruiting processes, client engagements, research workflows, financial records, travel, legal matters, creative projects, software repositories, personal administration, and photo collections” — and names nothing governmental. Included because informal groups produce real corpora that fit none of the design's named domains, which is §3.15: “Other domains remain placeholders until user demand and corpus evidence justify detailed templates.”

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `group` | string | the group as its members name it | `llm_supported` | Informal groups have no registration and no letterhead; the name lives in prose and in a folder. §3.9: “Purpose may be supported strongly by an existing user-created folder name or explicit language in a form or portal.” |
| `activity_or_project` | string | the project the group is running | `llm_supported` | The organising unit below the group. §3.5: the model “can only propose facts that belong to the active domain schema, and it must cite exact supporting evidence already extracted from the file.” |
| `record_role` | string | meeting note | `validated` | Meeting note, membership record, resource list, project record, small-grant record and communication are the recurring set |
| `locality` | string | the neighbourhood or area the group serves | `llm_supported` | §3.11 permits “several additional fields used only for search, privacy protection, explanation, or later review” — a search field, never a folder dimension: a folder named for the user's own neighbourhood is a home address in a directory listing |
| `meeting_date` | date | 2026-04-18 | `direct` | §3.10: “Date candidates should be identified with explicit regular expressions and then parsed without fuzzy matching.” — a labeled meeting date only |
| `document_role` | string | meeting note | `validated` | The work-type field, and the template's leaf dimension — an informal group's files are notes, lists and materials with no other structure. §5.7 requires a template's dimensions to be drawn from the domain's allowed fact fields, so the level and the field must exist together. Confirmable from the same context-term list the deterministic recognisers use |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.4, §3.5):

- a group-meeting structure detected as a labeled attendance or apologies section together with numbered agenda items and a group name in the title zone
- a mutual-aid or community term in a title zone — 'community group' | 'mutual aid' | 'neighbourhood' | 'members meeting' | 'volunteer sign-up' — co-occurring with a locality or group name

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- a group chat or message export where the group's purpose is only ever implicit
- a shared spreadsheet whose purpose must be read from column headers
- a note that is indistinguishable from a personal to-do list except that it uses the first person plural

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10):

- the word 'community' — open-source communities, brand communities and gated communities all compete, and the software slice owns one sense
- the word 'group' — a filesystem, social, mathematical and organisational term
- the word 'meeting' — every workplace corpus is made of them
- a locality name — it is in every address block the user owns

### Work types

`meeting note`, `membership list`, `shared resource list`, `project record`, `small-grant application`, `rota or sign-up`, `communication`, `constitution or ground rules`

### Grouping reasons (§4)

- one group across its meetings and projects
- one project across the notes, lists and materials it produced

### Template (§5)

`group → activity or project → document role`

Time first: **no**

§5.5: “a parent dimension should provide the context required to understand the child”. Deliberately shallow: informal corpora are small and §5.8: “The canvas must support uneven depth because real file trees are not and should not be perfectly symmetrical.” means a group with one project should be one folder. §5.9: “It should also support a scoped General or Other branch within a meaningful parent.” covers the notes that belong to the group and to nothing narrower. Both upper levels are `llm_supported`, so both come from an existing folder name or a user-confirmed label rather than from a rule: §3.9: “Purpose may be supported strongly by an existing user-created folder name or explicit language in a form or portal.”

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| civic.advocacy-campaign | organising and campaigning share every artefact; organising builds the group, campaigning targets a decision, and one meeting note is often both | §4.8: “an application packet does not silently absorb a document with a conflicting target institution” |
| npo.residents-association | a residents' association is a community group with a legal form and property obligations; the separating signal is whether the group has powers over a property, which its minutes may not say | §4.8: the validator checks “that each fact or label belongs to an allowed domain schema” |
| pers.hobby-collection | a hobby group's records sit between a personal interest and a civic organisation, and the personal slice's shape is usually the better fit for one member's files | §3.8: “The system must separate roles that happen to contain the same entity type.” |
| npo.governance | an informal group that incorporates becomes a nonprofit and its files change domain without changing shape | §3.11: “One file may hold facts from more than one domain without losing information.” |

### Sensitivity

`potentially_sensitive` — Membership lists and mutual-aid records hold neighbours' names, addresses and sometimes their needs — §2.9 on address-book data: it “should normally be privacy-protected rather than used to create folder proposals” describes this file type precisely. handling classes are P7's — §8.4: “The system should classify data into handling classes before LLM escalation” — and none is assigned here

---

## `npo.religious-institution` — Religious institution administration

Running a congregation or religious body as an organisation — governance, membership and life-event registers, services and programmes, giving, buildings and safeguarding.

**Provenance:** **proposal** — new; the design names nothing like it

**Cite:** No design sentence names religious institutions. §5.7 lists the template library's intended coverage — “covering common organizational situations such as academic programs, university applications, recruiting processes, client engagements, research workflows, financial records, travel, legal matters, creative projects, software repositories, personal administration, and photo collections” — and names nothing governmental. The personal slice owns an individual's faith participation; this is the institution's own administration

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `institution` | string | the congregation or religious body | `validated` | §3.8: “The system must separate roles that happen to contain the same entity type.” — the local body, the wider denomination or federation it belongs to, and the individual member are three roles |
| `function` | string | life-event register | `validated` | Governance, membership and registers, services and programmes, giving, buildings and safeguarding are the recurring functions |
| `record_role` | string | register entry | `validated` | The work-type field. Registers of life events are the distinctive object here and in some jurisdictions they have civil effect, which changes their status entirely |
| `period` | string | the year or liturgical cycle as printed | `direct` | §3.13 direct: “A direct fact was read from a reliable and explicit source, such as a content hash, EXIF timestamp, document title, or labeled form field.”. Calendars differ between traditions and are not translatable to a civil year, so the field stores the printed string rather than a parsed date |
| `property` | string | the building or site the record concerns | `possible` | Buildings work is a large part of this corpus and attaches to a place rather than to the organisation. A building name is a proper noun with no detectable shape and no gazetteer, so no rule can confirm it. §3.13 possible: “A possible fact is a useful but insufficient clue” |
| `document_role` | string | register entry | `validated` | The work-type field, and the template's leaf dimension — registers, meeting records and buildings papers share only the institution. §5.7 requires a template's dimensions to be drawn from the domain's allowed fact fields, so the level and the field must exist together. Confirmable from the same context-term list the deterministic recognisers use |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.4, §3.5):

- a congregational-administration term in a title or heading zone — 'members meeting' | 'register of' | 'annual meeting' | 'building fund' | 'safeguarding policy' — co-occurring with an institution name
- a register structure detected as labeled name, date and officiant columns co-occurring with an institution name. §2.3: “Tables matter because resumes, forms, applications, invoices, and administrative documents often place their most useful information in cells rather than body paragraphs.”

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- a programme or service sheet that reads as an event listing
- a document whose religious-administration character is visible only from its vocabulary, which differs completely between traditions
- material in a language or script the extraction layer handles but the recogniser has no terms for

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10):

- a religious term — devotional, academic, musical and historical material in a personal corpus is full of them, and misfiring here mislabels a user's reading as their institutional role
- the word 'register' — the same hazard as in professional regulation
- an institution name alone. §4.9's warning generalises: “A university name alone should not create a group because Columbia can appear as an authoring school, course provider, target institution, employer, research venue, or merely a cited organization.”
- a building name — it is a place name like any other

### Work types

`governing document`, `members meeting record`, `membership register`, `life-event register entry`, `service or programme record`, `giving record`, `buildings and fabric record`, `safeguarding record`, `annual return`

### Grouping reasons (§4)

- one function across one year
- one building project across its consents, works and funding

### Template (§5)

`function → period → document role`

Time first: **no**

§5.5: “a parent dimension should provide the context required to understand the child”. Function leads and the institution does not appear, because for a single congregation it would be a one-child collector — §5.7 forbids a template that would “use an author or organization merely as a collector”. §5.5: “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders.”

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| pers.faith-community | the personal slice owns an individual's participation; this domain is the institution's administration, and a service sheet sits in both | §3.8's worked pair: “A consulting document may mention the author’s firm and the client organization.” |
| npo.governance | religious bodies are usually nonprofits and file the same returns; the governance domain describes most of this corpus already | §3.11: “One file may hold facts from more than one domain without losing information.” |
| pers.genealogy | life-event registers are the primary source for family history; a researcher's copies are genealogy and the institution's originals are this domain | §3.8: “The system must separate roles that happen to contain the same entity type.” |
| gov.archives-recordkeeping | historic registers are archival records held by a religious body, and archival description would arrange them by creating body rather than by function | §4.8: “an application packet does not silently absorb a document with a conflicting target institution” |

### Sensitivity

`potentially_sensitive` — Membership and life-event registers tie named people to a religious affiliation and to births, marriages and deaths, and §2.9's phrase “while treating addresses and message content as potentially sensitive” covers the identifying half. handling classes are P7's — §8.4: “The system should classify data into handling classes before LLM escalation” — and none is assigned here

### Open question — Joseph's call, unresolved

> MAY A RELIGIOUS AFFILIATION APPEAR AS A FOLDER NAME? The same question as political affiliation, and for the same reason: a folder level naming a congregation or tradition discloses something about the user to anyone who lists the directory, including a backup, a sync client and a screen-share. The product has no notion of a label being more revealing than its contents. Joseph decides whether such labels may be proposed, proposed only on request, or never.

---

## `npo.residents-association` — Residents' and homeowners' associations

A body of residents or owners administering a shared property — constitution, meetings, member records, dues and accounts, rules and enforcement, maintenance and reserves.

**Provenance:** **proposal** — new; the design names nothing like it

**Cite:** No design sentence names owners' associations. §5.7 lists the template library's intended coverage — “covering common organizational situations such as academic programs, university applications, recruiting processes, client engagements, research workflows, financial records, travel, legal matters, creative projects, software repositories, personal administration, and photo collections” — and names nothing governmental. Kept separate from general nonprofit governance because the association has powers over the members' own homes, which nothing else in the catalogue does

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `association` | string | the association as named in its constitution | `validated` | §3.8: “The system must separate roles that happen to contain the same entity type.” — the association, the managing agent it employs and the individual member are three roles that all appear on one dues notice |
| `property_or_scheme` | string | the development or scheme the association covers | `validated` | The scheme is the durable object; boards and members change and the property does not |
| `record_role` | string | dues notice | `validated` | Constitution and rules, meeting record, member record, dues and accounts, enforcement, maintenance and reserve-fund records are the recurring set |
| `financial_year` | string | the financial year exactly as printed | `validated` | Association years are set by the constitution and rarely align to a calendar year. §3.10 is explicit that file names and documents “frequently contain numbers that look like years but are course identifiers, version numbers, build numbers, ZIP codes, or other unrelated values” |
| `unit` | string | the unit or lot the record concerns | `direct` | §3.13 direct: “A direct fact was read from a reliable and explicit source, such as a content hash, EXIF timestamp, document title, or labeled form field.” from a labeled unit field, and deliberately excluded from the template: a folder named for a neighbour's unit is a directory listing of who owes money |
| `document_role` | string | meeting minutes | `validated` | The work-type field, and the template's leaf dimension — rules, notices, minutes and accounts are the four things a member actually looks for. §5.7 requires a template's dimensions to be drawn from the domain's allowed fact fields, so the level and the field must exist together. Confirmable from the same context-term list the deterministic recognisers use |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.4, §3.5):

- an association term in a title or heading zone — 'residents association' | 'homeowners association' | 'service charge' | 'annual general meeting' | 'covenants' | 'reserve fund' — co-occurring with a scheme or association name
- a dues or service-charge structure detected as labeled unit, charge and balance columns co-occurring with an association name. §2.3: “Tables matter because resumes, forms, applications, invoices, and administrative documents often place their most useful information in cells rather than body paragraphs.”
- a financial-year pattern co-occurring with an association term and an accounts or budget heading, which is §3.5's model for a deterministic recogniser: “BUSIB 4300 becomes a course fact only when the engine finds a course-code pattern together with academic context” with the year in place of the course code

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- a notice to residents that reads as ordinary correspondence
- an enforcement letter whose basis in the rules is only described in prose
- an association whose legal form, powers and even existence differ by jurisdiction, which changes what the documents can do

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10):

- the word 'association' — trade, professional, sporting and statistical senses all compete
- an address-shaped string — the same hazard as in planning and housing
- a currency amount
- the word 'meeting'

### Work types

`constitution and rules`, `meeting notice`, `meeting minutes`, `member or unit register`, `dues or service-charge notice`, `annual accounts`, `enforcement correspondence`, `maintenance record`, `reserve-fund record`, `insurance record`

### Grouping reasons (§4)

- one financial year across its budget, dues, accounts and meeting
- one maintenance project across its quotes, decision and works records

### Template (§5)

`record role → financial year → document role`

Time first: **no**

§5.5: “a parent dimension should provide the context required to understand the child”. Function leads because a member's corpus is navigated by what the document is for. The scheme does not lead: for a member there is one, which §5.7 forbids a template that would “use an author or organization merely as a collector” forbids as a level

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| pers.home-tenure | for a member, association dues and notices are part of the record of owning their home, and the personal slice's shape usually fits better than this one | §3.11: “One file may hold facts from more than one domain without losing information.” |
| pers.household-admin | a dues notice is household administration in the same way a utility bill is; nothing on the notice distinguishes them | §3.8: “The system must separate roles that happen to contain the same entity type.” |
| npo.governance | an association is a nonprofit and files the same governance documents; the powers over property are the difference and they do not show on the minutes | §4.8: the validator checks “that each fact or label belongs to an allowed domain schema” |
| gov.housing-authority | estate management by a social landlord and by an owners' association produce near-identical notices and minutes | §4.8: “an application packet does not silently absorb a document with a conflicting target institution” |

### Sensitivity

`potentially_sensitive` — Member registers and arrears records tie named neighbours to their homes and their debts — §2.9's phrase “while treating addresses and message content as potentially sensitive” and §2.9 on address-book data: it “should normally be privacy-protected rather than used to create folder proposals” both apply. handling classes are P7's — §8.4: “The system should classify data into handling classes before LLM escalation” — and none is assigned here

### Open question — Joseph's call, unresolved

> IS THIS A CIVIC DOMAIN OR A HOUSEHOLD ONE? For a board member it is an organisation they run; for everyone else it is post about their home, and the personal slice already owns that. The catalogue currently answers both by keeping the domain here and colliding it with `pers.home-tenure` and `pers.household-admin`, which means the recogniser will face the same document with two equally good homes and no signal to choose. Joseph decides which side owns it by default.

---

## `civic.trade-union` — Trade union and staff association records

Running or participating in a union or staff association — membership, branch business, representation and casework, collective bargaining, industrial action ballots and reporting.

**Provenance:** **proposal** — new; the design names nothing like it

**Cite:** No design sentence names unions. §5.7 lists the template library's intended coverage — “covering common organizational situations such as academic programs, university applications, recruiting processes, client engagements, research workflows, financial records, travel, legal matters, creative projects, software repositories, personal administration, and photo collections” — and names nothing governmental. The career slice owns the employment relationship; a union sits on the other side of it, which is §3.8: “The system must separate roles that happen to contain the same entity type.”

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `union_or_association` | string | the union or staff association | `validated` | §3.8: “The system must separate roles that happen to contain the same entity type.” — the union, the employer it bargains with and the member it represents are three roles present in one grievance file |
| `branch_or_unit` | string | the branch or bargaining unit named on the record | `validated` | The branch is the organising unit for meetings, membership and local business |
| `employer` | string | the employer the record concerns | `validated` | §3.8's worked pair: “A consulting document may mention the author’s firm and the client organization.” — union and employer are the bargaining pair, and collapsing them misfiles the whole corpus |
| `record_role` | string | collective agreement | `validated` | Membership, branch meeting, representation case, collective agreement, ballot and statutory return are the recurring set, and they run from routine to legally consequential |
| `bargaining_round` | string | the pay round or negotiation as named | `llm_supported` | Negotiations are named informally and in prose. §3.5: the model “can only propose facts that belong to the active domain schema, and it must cite exact supporting evidence already extracted from the file.” |
| `case_reference` | string | the representation case reference as printed | `direct` | §3.13 direct: “A direct fact was read from a reliable and explicit source, such as a content hash, EXIF timestamp, document title, or labeled form field.”. Representation cases are casework and carry the same third-party hazard as everything else in this slice that has a case reference |
| `document_role` | string | collective agreement | `validated` | The work-type field, and the template's leaf dimension — a branch's files mix membership, meetings, agreements and casework. §5.7 requires a template's dimensions to be drawn from the domain's allowed fact fields, so the level and the field must exist together. Confirmable from the same context-term list the deterministic recognisers use |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.4, §3.5):

- a union term in a title or heading zone — 'branch meeting' | 'collective agreement' | 'recognition agreement' | 'industrial action ballot' | 'union membership' | 'shop steward' — co-occurring with a union or branch name
- a bargaining structure detected as labeled claim and response sections co-occurring with a union name and an employer name

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- a grievance file indistinguishable from an employer's HR file except for whose side wrote it. §3.8: “The system must separate roles that happen to contain the same entity type.”
- a branch communication that reads as an ordinary mailing
- a document whose industrial-relations framework has no counterpart in the reader's jurisdiction, where recognition, balloting and action are differently constituted or absent

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10):

- the word 'union' — European, credit, set and marital senses all compete, and a credit union is a financial institution
- the word 'branch' — version control, banking and botanical senses dominate, and the software slice owns one of them
- an employer name alone. §4.9's warning generalises: “A university name alone should not create a group because Columbia can appear as an authoring school, course provider, target institution, employer, research venue, or merely a cited organization.”
- the word 'ballot' — clubs, committees and elections all ballot

### Work types

`membership record`, `branch meeting record`, `representation case file`, `grievance or disciplinary record`, `collective agreement`, `pay claim`, `ballot record`, `statutory return`, `member communication`, `training record`

### Grouping reasons (§4)

- one bargaining round across its claim, negotiation notes, agreement and communications
- one representation case across its file, joined by the case reference

### Template (§5)

`record role → case or round → document role`

Time first: **no**

§5.5: “a parent dimension should provide the context required to understand the child”. Function leads and the member does not appear as a level, for the same reason as every other casework-bearing domain in this slice. The middle level is populated from `case_reference` where one exists and from `bargaining_round` otherwise, and the second of those is `llm_supported`, so it should be offered only once the user has confirmed the label. §5.5: “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders.”

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| career.professional-membership | the career slice owns an individual's own membership of a body; this domain is the union's side and the branch's business | §3.8's worked pair: “A consulting document may mention the author’s firm and the client organization.” |
| career.employment-contract | a collective agreement sets terms that appear in individual contracts; both are employment documents from opposite ends of the bargaining table | §3.8: “The system must separate roles that happen to contain the same entity type.” |
| law.matter-file | representation casework that escalates to a tribunal becomes a legal matter with a different file structure and different duties attached; the separating signal is a retainer or a tribunal reference, not the grievance | §4.8: the validator checks “that each fact or label belongs to an allowed domain schema” |
| npo.governance | unions are member organisations with constitutions and returns, so most of the governance domain applies to them as well | §3.11: “One file may hold facts from more than one domain without losing information.” |

### Sensitivity

`potentially_sensitive` — Membership records tie named people to union membership, and representation files hold grievances, discipline and health information about them. §2.9's phrase “while treating addresses and message content as potentially sensitive” and §4.9: “Rare but sensitive files such as passports, visas, and legal documents may be surfaced as protected records even when they do not meet a normal group-size threshold.” both apply. handling classes are P7's — §8.4: “The system should classify data into handling classes before LLM escalation” — and none is assigned here

### Open question — Joseph's call, unresolved

> UNION MEMBERSHIP AS A FOLDER NAME IS THE THIRD INSTANCE OF ONE PROBLEM. Political affiliation, religious affiliation and union membership all produce folder labels that reveal something about the user that the file inside would reveal only on opening. This slice raises it three times because this slice is where such labels naturally arise; the decision is one decision, not three. Joseph decides whether the product may propose a folder level whose NAME is more disclosing than its contents.

---
