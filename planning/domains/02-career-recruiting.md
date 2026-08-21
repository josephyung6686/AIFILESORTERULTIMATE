# Domain catalogue — career, recruiting and professional life

Supercategory: `career-recruiting` · Authored: 2026-08-21 · Entries: **43**

Conforms to [`_CONTRACT.md`](_CONTRACT.md). Machine-readable form: [`02-career-recruiting.json`](02-career-recruiting.json) — the JSON is the artifact the §3.6 validator consumes; this file is the same content as tables.

Provenance: **design 4 · inference 13 · proposal 26**. Sensitivity: **potentially_sensitive 35 · none 8**.

Every quotation in this file was extracted verbatim from `00-database-agent-product-design.md` by the generator and machine-checked against it; no quotation was typed by hand. Section numbers follow `01-product-design-structured.md`, the sectioned transcription — the source of truth itself carries no section numbers.

**The sensitivity test used here**, applied uniformly: an entry is marked `potentially_sensitive` when its typical file carries a personal or government identifier, a financial figure, health, immigration or legal-status information, another person's personal data, or material the owner holds under a confidentiality obligation. `sensitivity` is §2.9's phrase and nothing more; no handling class is assigned anywhere in this file, because handling classes are P7's (§8.4).

## Index

| # | id | Domain | Provenance | Sensitivity | Open question |
|---|---|---|---|---|---|
| 1 | `career.job-search-campaign` | Job search campaign | proposal | none | yes |
| 2 | `career.job-posting-collected` | Collected job posting | inference | none | — |
| 3 | `career.job-application` | Job application packet | design | potentially_sensitive | yes |
| 4 | `career.internship-application` | Internship and campus-recruiting application | design | potentially_sensitive | yes |
| 5 | `career.academic-job-application` | Academic job-market application | inference | potentially_sensitive | — |
| 6 | `career.resume` | Resume and its tailoring family | inference | potentially_sensitive | yes |
| 7 | `career.academic-cv` | Academic CV and its supporting statements | inference | potentially_sensitive | — |
| 8 | `career.cover-letter` | Cover letter and letter of interest | inference | potentially_sensitive | — |
| 9 | `career.portfolio` | Professional portfolio and work samples | proposal | potentially_sensitive | — |
| 10 | `career.interview-cycle` | Interview cycle | design | none | — |
| 11 | `career.take-home-assessment` | Take-home and screening assessment | inference | potentially_sensitive | yes |
| 12 | `career.offer-and-negotiation` | Offer and negotiation | inference | potentially_sensitive | — |
| 13 | `career.reference-and-recommendation` | References and recommendations | proposal | potentially_sensitive | — |
| 14 | `career.onboarding-paperwork` | Onboarding paperwork | proposal | potentially_sensitive | — |
| 15 | `career.employment-contract` | Employment contract | proposal | potentially_sensitive | — |
| 16 | `career.restrictive-covenant` | Restrictive covenants and IP assignment | proposal | potentially_sensitive | — |
| 17 | `career.work-authorization` | Work authorisation and sponsorship | proposal | potentially_sensitive | yes |
| 18 | `career.payroll` | Payroll records | proposal | potentially_sensitive | yes |
| 19 | `career.benefits-enrollment` | Benefits enrolment | proposal | potentially_sensitive | — |
| 20 | `career.equity-compensation` | Equity compensation | proposal | potentially_sensitive | — |
| 21 | `career.compensation-record` | In-employment compensation records | proposal | potentially_sensitive | — |
| 22 | `career.performance-review` | Performance review | proposal | potentially_sensitive | — |
| 23 | `career.promotion-packet` | Promotion packet | proposal | potentially_sensitive | — |
| 24 | `career.employment-verification` | Employment and income verification | proposal | potentially_sensitive | — |
| 25 | `career.sabbatical-and-leave` | Leave, sabbatical and accommodation | proposal | potentially_sensitive | — |
| 26 | `career.layoff-and-severance` | Layoff, termination and severance | proposal | potentially_sensitive | — |
| 27 | `career.exit-and-offboarding` | Resignation and offboarding | proposal | potentially_sensitive | — |
| 28 | `career.retirement-records` | Retirement and pension records | proposal | potentially_sensitive | — |
| 29 | `career.professional-license` | Professional licence | proposal | potentially_sensitive | — |
| 30 | `career.certification` | Professional certification | proposal | none | — |
| 31 | `career.continuing-education` | Continuing professional education | proposal | none | — |
| 32 | `career.professional-membership` | Professional membership | proposal | none | — |
| 33 | `career.conference-attendance` | Conference and event attendance | proposal | none | yes |
| 34 | `career.speaking-engagement` | Speaking and contribution | proposal | none | — |
| 35 | `career.networking-and-referrals` | Networking and referrals | proposal | potentially_sensitive | — |
| 36 | `career.consulting-engagement` | Consulting engagement | design | potentially_sensitive | — |
| 37 | `career.client-proposal` | Client proposal and bid | inference | potentially_sensitive | — |
| 38 | `career.freelance-contract-work` | Freelance and contract work | inference | potentially_sensitive | — |
| 39 | `career.service-invoicing` | Invoicing for services | proposal | potentially_sensitive | — |
| 40 | `career.employer-job-requisition` | Job requisition (employer side) | inference | potentially_sensitive | — |
| 41 | `career.employer-candidate-packet` | Candidate packet (employer side) | inference | potentially_sensitive | yes |
| 42 | `career.employer-interview-scorecard` | Interview scorecard and debrief (employer side) | inference | potentially_sensitive | yes |
| 43 | `career.employer-offer-approval` | Offer approval and closing (employer side) | inference | potentially_sensitive | — |

---

## `career.job-search-campaign` — Job search campaign

Files that describe or track one person's search for work as a whole, rather than any single employer.

| | |
|---|---|
| **provenance** | `proposal` |
| **design cite** | _none — nothing in the design speaks to this domain_ |
| **sensitivity** | `none` — A tracker names employers and statuses, not identifiers, amounts or another person's data. |

**Schema** — the fields this domain, and only this domain, legitimises.

| field | type | example | ceiling | why |
|---|---|---|---|---|
| `search_cycle` | string | 2026 spring search | `user_confirmed` | No document states the boundaries of a search. Only the corpus owner can name the period; the engine may group by it but may not assert it. |
| `target_role_family` | string | Product Manager | `llm_supported` | A search plan states an intent in prose. There is no labeled field and no pattern; this is exactly the interpretation case. |
| `target_sector` | string | Healthcare | `llm_supported` | Same as target role family — stated as prose intent, not as a labeled value. |
| `search_document_type` | enum-like | application tracker | `validated` | A tracker is recognisable from co-occurring column headers, which is a deterministic rule passing a context check. |
| `search_channel` | enum-like | referral | `validated` | A channel word is only meaningful beside application-tracking headers; alone it is an ordinary English word. |
| `tracked_employer` | string | Stripe | `possible` | A company name in a tracker cell records a target considered, not an application made. It is a clue for retrieval and must not become an application fact. |

**Recognition**

| kind | entries |
|---|---|
| deterministic (pattern **plus** corroborating context) | • a spreadsheet whose header row carries employment-tracking terms together — ‘company’ with ‘role’ or ‘position’, plus ‘applied’ or ‘status’ or ‘stage’<br>• a filename token ‘job search’ \| ‘application tracker’ \| ‘job hunt’ co-occurring with search-activity language ‘recruiter’ \| ‘applied’ \| ‘interview’ \| ‘offer’ in the extracted text |
| needs the LLM | • a prose planning note that describes an intended search without naming an employer or a role title<br>• a target list whose column headers are idiosyncratic (‘them’, ‘reached out?’, ‘vibes’) and carry no standard employment vocabulary |
| never alone | • a spreadsheet with a company column — a supplier list, a CRM export and an investor tracker have the same shape<br>• a company or organisation name on its own — §4.9 ‘A university name alone should not create a group because Columbia can appear as an authoring school, course provider, target institution, employer, research venue, or merely a cited organization.’<br>• a filename containing ‘tracker’ or ‘list’ |

**Work types** — `application tracker`, `target company list`, `search plan or notes`, `networking log`, `recruiter contact list`, `weekly search status sheet`

**Grouping reasons** — one bounded search period; one tracker together with the postings it references

**Template** — `search cycle → search document type`  (time first: no)

> A document type is only interpretable once the search period is known — §5.5 ‘The recommendation should follow the practical rule that a parent dimension should provide the context required to understand the child.’ Time is not first: this is a record domain, and §5.5 ‘For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders.’

**Collides with**

| domain | separating signal | design cite |
|---|---|---|
| `career.job-application` | A tracker names many employers and applies to none of them; an application packet names exactly one employer plus one role. The decisive signal is multiplicity: several employer values inside one file is a tracker, one employer value plus a submission artifact is an application. | §4.8 ‘that an application packet does not silently absorb a document with a conflicting target institution’ |
| `career.employer-job-requisition` | A candidate's job-search tracker and a recruiter's pipeline tracker are the same spreadsheet shape with opposite roles. Only the recruiter's version carries requisition identifiers and candidate names in the row position where the candidate's version carries employers. | §3.8 ‘A consulting document may mention the author’s firm and the client organization. A finance document may mention an account holder and an issuing bank. The agent should model these as distinct facets, such as authored_by and target_school, or our_firm and client.’ |

**Open question — unresolved, Joseph's call**

> Does the fact that the corpus owner is conducting a job search count as ‘potentially sensitive’ under §2.9, which introduces the phrase for message addresses and content? A search that a current employer must not see is sensitive for a reason §2.9 does not describe, and only Joseph can say whether that belongs in this field or nowhere in the catalogue.

---

## `career.job-posting-collected` — Collected job posting

A job advertisement or description saved by a candidate, independently of whether an application was ever made against it.

| | |
|---|---|
| **provenance** | `inference` |
| **design cite** | §3.3 ‘The LLM may determine whether an extracted document appears to be an application essay, research artifact, recruiting document, travel record, or other supported domain’ |
| **sensitivity** | `none` — A public job advertisement carries no personal identifier and no confidential material. |

**Schema** — the fields this domain, and only this domain, legitimises.

| field | type | example | ceiling | why |
|---|---|---|---|---|
| `employer` | string | Stripe | `validated` | A gazetteer company name is only an employer when posting language surrounds it; that is the §3.5 ‘For example, BUSIB 4300 becomes a course fact only when the engine finds a course-code pattern together with academic context such as “syllabus,” “lecture,” “credits,” “instructor,” or “semester.”’ shape applied to a company name. |
| `role_title` | string | Senior Backend Engineer | `direct` | On a saved posting the role title is the document title or the page heading — §3.5 ‘Deterministic extractors create direct facts when the information comes from a reliable, explicit source, such as a content hash, EXIF timestamp, a document title, or a labeled form field.’ |
| `requisition_id` | string | REQ-48213 | `direct` | Public postings carry a labeled ‘Job ID’ or ‘Requisition’ field, which is a labeled form field. |
| `posting_source` | string | LinkedIn | `validated` | A job-board host name is only a posting source when posting language is present; the same host name appears in unrelated saved pages. |
| `work_mode` | string | Remote — US | `llm_supported` | Work mode is stated in prose (‘this role may be performed remotely from any US state’) far more often than in a labeled field. |
| `posted_compensation_range` | string | $150,000 – $190,000 | `direct` | Where present it sits under a labeled ‘Base pay range’ or ‘Compensation’ heading; where absent it must stay unknown rather than be inferred from a level. |
| `posting_date` | date | 2026-03-04 | `direct` | A labeled ‘Posted’ field. Any other date on the page is not the posting date. |

**Recognition**

| kind | entries |
|---|---|
| deterministic (pattern **plus** corroborating context) | • a gazetteer company name co-occurring with posting language ‘responsibilities’ \| ‘qualifications’ \| ‘what you'll do’ \| ‘equal opportunity employer’ \| ‘apply’<br>• a requisition-id pattern co-occurring with ‘requisition’ \| ‘job id’ \| ‘posting’ |
| needs the LLM | • a screenshot of a posting whose OCR text carries the role heading but no recognisable employer name<br>• a posting forwarded inside an email or pasted into a note, where the surrounding text is correspondence rather than an advertisement |
| never alone | • a company or organisation name on its own — §4.9 ‘A university name alone should not create a group because Columbia can appear as an authoring school, course provider, target institution, employer, research venue, or merely a cited organization.’<br>• a role noun such as ‘engineer’ or ‘analyst’ in a filename<br>• a salary-shaped number, which appears identically in a budget, a payslip and an offer |

**Work types** — `job description`, `saved posting page`, `posting screenshot`, `recruiter outreach message`, `role one-pager`, `levelling or scope document`

**Grouping reasons** — postings collected for one employer during one search; a posting and the application eventually made against it

**Template** — `search cycle → employer → role title`  (time first: no)

> Employer supplies the context that makes a role title readable — §5.5 ‘The recommendation should follow the practical rule that a parent dimension should provide the context required to understand the child.’ Postings collected but never applied to have no cycle of their own, so §5.8 ‘One branch may require four levels, while another should remain flat.’

**Collides with**

| domain | separating signal | design cite |
|---|---|---|
| `career.employer-job-requisition` | The same job description exists on both sides of the hiring transaction. Only the employer's copy carries approval, headcount, hiring-manager and internal-level fields; only the candidate's copy carries an application URL and public ‘apply now’ language. Filing the two together would let a candidate's saved posting inherit an employer's internal fields. | §3.8 ‘A consulting document may mention the author’s firm and the client organization. A finance document may mention an account holder and an issuing bank. The agent should model these as distinct facets, such as authored_by and target_school, or our_firm and client.’ §3.8 ‘It should avoid using authorship or creator identity as a destination dimension. A folder should not become a collection point for everything produced by the same person or organization.’ |
| `career.job-application` | A saved posting is not an application. Only the application carries a submission artifact — a confirmation, a submitted document set, or a labeled submission date. Absorbing a posting into an application packet asserts a submission that never happened. | §4.8 ‘that an application packet does not silently absorb a document with a conflicting target institution’ |

---

## `career.job-application` — Job application packet

Everything submitted to one employer for one role in one recruiting cycle, held together by purpose rather than by content.

| | |
|---|---|
| **provenance** | `design` |
| **design cite** | §3.15 ‘The initial release should fully support only the domains required to validate the product on real heterogeneous corpora: academic coursework, college applications, research and lab work, career and recruiting, photos and captures, and code projects.’ §3.3 ‘The LLM may determine whether an extracted document appears to be an application essay, research artifact, recruiting document, travel record, or other supported domain’ §5.4 ‘a Career template may define company → role or recruiting cycle → document type’ |
| **sensitivity** | `potentially_sensitive` — §2.9's phrase ‘potentially sensitive’. A submitted packet normally carries a resume contact block, and often a transcript, an identification document or a self-identification form. No handling class is assigned here. |

**Schema** — the fields this domain, and only this domain, legitimises.

| field | type | example | ceiling | why |
|---|---|---|---|---|
| `employer` | string | EY | `validated` | §5.4's ‘company’ dimension. A gazetteer name plus application language; a company name alone is never enough — §4.9 ‘A university name alone should not create a group because Columbia can appear as an authoring school, course provider, target institution, employer, research venue, or merely a cited organization.’ |
| `role_title` | string | Assurance Staff | `validated` | §5.4's ‘role’. Recognisable from a labeled position line in a confirmation or a cover-letter salutation line, both of which are context checks rather than bare patterns. |
| `requisition_id` | string | R-1049283 | `direct` | Application confirmations carry it as a labeled field, and it is the only value in this schema that identifies the application uniquely. |
| `recruiting_cycle` | string | 2026 Campus | `validated` | §5.4's ‘recruiting cycle’. A cycle name is a term-shaped or season-shaped value that only means a cycle when employment language surrounds it. |
| `application_document_type` | enum-like | cover letter | `validated` | §5.4's ‘document type’. Recognisable from document structure; the enum itself is deferred — §3.11 ‘Each domain activates only a small set of relevant fields, usually three to six that may help build a future folder proposal and several additional fields used only for search, privacy protection, explanation, or later review.’ |
| `application_channel` | string | Workday portal | `llm_supported` | A portal is usually identified only by the visual chrome of a screenshot or by prose in a confirmation email. |
| `submission_date` | date | 2026-01-15 | `direct` | A labeled ‘Submitted’ or ‘Date received’ line on a confirmation. No other date on the packet may fill it. |
| `application_status` | enum-like | submitted | `llm_supported` | Status is stated in correspondence prose (‘we are moving forward with other candidates’) and almost never as a field. |
| `purpose` | string | job application | `llm_supported` | The field that holds a content-incoherent packet together — §3.9 ‘Purpose must be a first-class facet. Topic answers what a file is about, while purpose answers what the file was for.’ §3.9 ‘A university application packet can contain an identification document, transcript, resume, certificate, and academic abstract. The documents are content-incoherent but purpose-coherent.’ It is listed here as a College-applications field in §3.11; see the open question. |

**Recognition**

| kind | entries |
|---|---|
| deterministic (pattern **plus** corroborating context) | • a gazetteer company name co-occurring with application language ‘your application’ \| ‘position’ \| ‘requisition’ \| ‘hiring manager’ \| ‘we received your application’<br>• a requisition-id pattern co-occurring with an employer name and ‘application’ \| ‘candidate’<br>• an application-portal confirmation whose extracted text carries both an employer name and a labeled submission date |
| needs the LLM | • an untitled essay or statement whose only employer signal is prose addressed to a firm<br>• a heterogeneous set — resume, transcript, certificate, writing sample — whose only shared signal is that they were submitted together, which is §3.9 ‘A university application packet can contain an identification document, transcript, resume, certificate, and academic abstract. The documents are content-incoherent but purpose-coherent.’ |
| never alone | • a company or organisation name on its own — §4.9 ‘A university name alone should not create a group because Columbia can appear as an authoring school, course provider, target institution, employer, research venue, or merely a cited organization.’<br>• a bounded download session on its own — §3.9 ‘A session should never be treated as proof of topic, and it should not carry the same confidence as a hash match or a directly extracted document fact.’<br>• a filename containing ‘application’ — university applications, grant applications, visa applications and mortgage applications all produce it<br>• a four-digit year on its own — §3.10 ‘file names and documents frequently contain numbers that look like years but are course identifiers, version numbers, build numbers, ZIP codes, or other unrelated values’ |

**Work types** — `submitted resume`, `cover letter`, `application form`, `portal confirmation`, `transcript copy`, `writing sample`, `supporting certificate`, `screening questionnaire`, `self-identification form`

**Grouping reasons** — one employer, one role, one cycle; an application and the confirmation that acknowledges it; a purpose-coherent packet of heterogeneous supporting documents

**Template** — `employer → recruiting cycle → role title → application document type`  (time first: no)

> §5.4 gives the Career template as §5.4 ‘a Career template may define company → role or recruiting cycle → document type’ and §5.5 ‘The recommendation should follow the practical rule that a parent dimension should provide the context required to understand the child.’ The order below reads the ‘or’ as cycle-then-role; see the open question, because the design does not settle it. §5.5 ‘For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders.’

**Collides with**

| domain | separating signal | design cite |
|---|---|---|
| `acad.college-application` | The single most damaging collision in this slice. Both carry essays, references, transcripts and a target organisation, and a university can be either target. They are different schemas because a job application is keyed by employer plus a role title plus a requisition — a role dimension admissions has no analogue for — while an admissions packet is keyed by target university plus admissions cycle plus programme. A packet must not absorb a document whose target organisation conflicts, and the employer form is worse than the university form because one person applies to many employers inside one cycle with near-identical documents. | §4.8 ‘that an application packet does not silently absorb a document with a conflicting target institution’ §4.9 ‘A university name alone should not create a group because Columbia can appear as an authoring school, course provider, target institution, employer, research venue, or merely a cited organization.’ |
| `career.internship-application` | An internship packet carries a cohort term (‘Summer 2026’) that a full-time packet does not, and that term is pattern-identical to an academic term. Merging them lets a cohort term be read as a course term. | §3.10 ‘file names and documents frequently contain numbers that look like years but are course identifiers, version numbers, build numbers, ZIP codes, or other unrelated values’ |
| `career.resume` | The same resume file is a member of this packet and a member of its own version family at once. Neither membership may erase the other. | §6.9 ‘A transcript may be part of several application packets; a resume may support multiple recruiting processes; a research abstract may belong to a research project and be attached to a university application.’ §3.1 ‘A file can simultaneously be a syllabus, part of a particular course, created for a particular semester, related to a university, included in an application package, a member of a version family, and potentially sensitive.’ |
| `career.employer-candidate-packet` | The identical document set exists on the employer's disk with the roles reversed. Nothing in the file distinguishes them except who the subject is. | §3.8 ‘A consulting document may mention the author’s firm and the client organization. A finance document may mention an account holder and an issuing bank. The agent should model these as distinct facets, such as authored_by and target_school, or our_firm and client.’ |

**Open question — unresolved, Joseph's call**

> §5.4 defines the Career template as company → role or recruiting cycle → document type. The design never resolves the ‘or’. Should a Career branch nest employer → cycle → role, or employer → role → cycle — and does the right answer change between someone who applies to one employer across several cycles and someone who applies to forty employers inside one cycle?

---

## `career.internship-application` — Internship and campus-recruiting application

An application to a term-bounded internship or campus programme, whose identity includes a cohort term and usually a university affiliation.

| | |
|---|---|
| **provenance** | `design` |
| **design cite** | §4.5 ‘it may label a coherent course group PHYS1401 — Spring 2026, an application group Columbia Application — 2026 Cycle, a research group PVA/RDP — Manuscripts and Figures, or a career packet EY Internship Application.’ |
| **sensitivity** | `potentially_sensitive` — §2.9's phrase ‘potentially sensitive’. Campus packets routinely carry a transcript and a resume contact block. No handling class is assigned here. |

**Schema** — the fields this domain, and only this domain, legitimises.

| field | type | example | ceiling | why |
|---|---|---|---|---|
| `employer` | string | EY | `validated` | The design's own worked label is a career packet named for its employer; a gazetteer name plus internship language establishes it. |
| `programme_name` | string | Summer Analyst Program | `direct` | Campus programmes are named in the document title or the offer heading, which is a document-title source. |
| `cohort_term` | string | Summer 2026 | `validated` | A term-shaped value is only a cohort when internship language surrounds it. §3.10 ‘file names and documents frequently contain numbers that look like years but are course identifiers, version numbers, build numbers, ZIP codes, or other unrelated values’ and the identical pattern is claimed by coursework. |
| `campus` | string | Columbia | `validated` | A university name here is the candidate's own school, not a target — a role distinction §3.8 requires and §4.9 ‘A university name alone should not create a group because Columbia can appear as an authoring school, course provider, target institution, employer, research venue, or merely a cited organization.’ |
| `class_year` | string | 2027 | `possible` | A class year is a year-shaped value that appears on resumes, transcripts and postings alike. It is a clue for cohort grouping, never an asserted fact on its own. |
| `application_round` | enum-like | first-round deadline | `llm_supported` | Rounds are described in prose deadlines and portal copy rather than as labeled fields. |
| `application_document_type` | enum-like | campus resume | `validated` | Same structural recognition as the general packet. |

**Recognition**

| kind | entries |
|---|---|
| deterministic (pattern **plus** corroborating context) | • a gazetteer employer name co-occurring with internship language ‘intern’ \| ‘internship’ \| ‘summer analyst’ \| ‘co-op’ \| ‘campus recruiting’ \| ‘spring week’<br>• an academic-term pattern co-occurring with internship language rather than with course language — the discriminator against §3.5 ‘For example, BUSIB 4300 becomes a course fact only when the engine finds a course-code pattern together with academic context such as “syllabus,” “lecture,” “credits,” “instructor,” or “semester.”’ |
| needs the LLM | • a campus careers-fair handout that names neither a role nor a requisition<br>• a cohort-programme acceptance whose only distinguishing prose is ‘we would like to welcome you to the 2026 cohort’ |
| never alone | • an academic-term pattern on its own — it is claimed by coursework, by internships and by fiscal reporting<br>• a university name on its own — §4.9 ‘A university name alone should not create a group because Columbia can appear as an authoring school, course provider, target institution, employer, research venue, or merely a cited organization.’<br>• a company or organisation name on its own — §4.9 ‘A university name alone should not create a group because Columbia can appear as an authoring school, course provider, target institution, employer, research venue, or merely a cited organization.’ |

**Work types** — `campus resume`, `cohort application form`, `assessment-centre invitation`, `internship offer`, `programme handbook`, `careers-fair handout`, `university careers-service correspondence`

**Grouping reasons** — one employer, one cohort term; one campus recruiting season across employers

**Template** — `employer → cohort term → application document type`  (time first: no)

> Employer before cohort term, because a cohort term is ambiguous without it — §5.5 ‘The recommendation should follow the practical rule that a parent dimension should provide the context required to understand the child.’ §5.5 ‘For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders.’ even though the cohort term looks temporal: it names a programme intake, not a calendar.

**Collides with**

| domain | separating signal | design cite |
|---|---|---|
| `acad.course-enrollment` | The cohort term and the academic term are the same string produced by the same pattern. The only separator is the surrounding vocabulary — internship language versus §3.5's academic context terms. | §3.5 ‘For example, BUSIB 4300 becomes a course fact only when the engine finds a course-code pattern together with academic context such as “syllabus,” “lecture,” “credits,” “instructor,” or “semester.”’ §3.10 ‘file names and documents frequently contain numbers that look like years but are course identifiers, version numbers, build numbers, ZIP codes, or other unrelated values’ |
| `career.job-application` | A cohort term is required here and absent there; a requisition id is usual there and rare here. Collapsing them loses the cohort dimension that makes campus material findable. | — |
| `acad.college-application` | A student applying to internships and to graduate programmes in the same months produces two packets with overlapping documents, both naming universities. Only one carries an employer and a role. | §4.8 ‘that an application packet does not silently absorb a document with a conflicting target institution’ |

**Open question — unresolved, Joseph's call**

> For a student whose internship is credit-bearing, the same packet is career material and coursework. Should it sit under Career or under Academics by default, and should the answer change when the university itself administers the placement?

---

## `career.academic-job-application` — Academic job-market application

An application for a faculty, postdoctoral or research position, whose packet has a document set no corporate application uses.

| | |
|---|---|
| **provenance** | `inference` |
| **design cite** | §4.9 ‘A university name alone should not create a group because Columbia can appear as an authoring school, course provider, target institution, employer, research venue, or merely a cited organization.’ |
| **sensitivity** | `potentially_sensitive` — §2.9's phrase ‘potentially sensitive’. Reference letters carry a third party's candid assessment and contact details. No handling class is assigned here. |

**Schema** — the fields this domain, and only this domain, legitimises.

| field | type | example | ceiling | why |
|---|---|---|---|---|
| `institution` | string | University of Michigan | `validated` | Here the university is the employer, one of the six roles §4.9 ‘A university name alone should not create a group because Columbia can appear as an authoring school, course provider, target institution, employer, research venue, or merely a cited organization.’ |
| `department` | string | Department of Statistics | `validated` | A department name is only a hiring unit when faculty-search language surrounds it; otherwise it is an affiliation on a paper. |
| `position_type` | enum-like | tenure-track assistant professor | `validated` | Recognisable from a closed vocabulary of rank terms co-occurring with search language. |
| `search_cycle` | string | AY 2026-27 | `validated` | An academic-year pattern is one §3.10 names explicitly, and it means a search only beside faculty-search language. |
| `job_ad_number` | string | F-2291 | `direct` | Faculty adverts carry a labeled posting number, and application systems echo it. |
| `packet_document_type` | enum-like | research statement | `validated` | The document set — research statement, teaching statement, diversity statement, writing sample — is recognisable structurally and exists in no corporate packet. |
| `referee` | string | Prof. A. Okonkwo | `llm_supported` | Referees appear in prose lists and in letter signatures; a person's name alone establishes nothing. |

**Recognition**

| kind | entries |
|---|---|
| deterministic (pattern **plus** corroborating context) | • an institution-gazetteer name co-occurring with faculty-search language ‘tenure-track’ \| ‘search committee’ \| ‘department chair’ \| ‘Interfolio’ \| ‘job ad’<br>• an academic-year pattern co-occurring with faculty-search language rather than with course language |
| needs the LLM | • a research statement whose text names no institution and reads like a grant narrative<br>• distinguishing a teaching statement written for a job packet from one written for a promotion file |
| never alone | • a university name on its own — §4.9 ‘A university name alone should not create a group because Columbia can appear as an authoring school, course provider, target institution, employer, research venue, or merely a cited organization.’<br>• the token ‘CV’ in a filename<br>• a person's name on its own; it identifies an author, not a domain |

**Work types** — `cover letter`, `academic CV`, `research statement`, `teaching statement`, `diversity statement`, `writing sample`, `teaching portfolio`, `letter of reference`, `job ad copy`

**Grouping reasons** — one institution, one department, one search cycle; one job-market season across institutions

**Template** — `search cycle → institution → packet document type`  (time first: no)

> Season before institution here, unusually: an academic job market is run as one bulk annual campaign and the statements are shared across institutions, so institution-first would duplicate near-identical files. §5.5 ‘The system recommends an order based on the domain template, but the user can reverse, remove, add, or flatten dimensions.’

**Collides with**

| domain | separating signal | design cite |
|---|---|---|
| `acad.college-application` | Both target a university and both include statements and references. Only the job packet carries a department and a position type; only the admissions packet carries a programme and an admissions cycle. | §4.8 ‘that an application packet does not silently absorb a document with a conflicting target institution’ §4.9 ‘A university name alone should not create a group because Columbia can appear as an authoring school, course provider, target institution, employer, research venue, or merely a cited organization.’ |
| `career.job-application` | The employer is a university, so every corporate-application recognition rule that keys on a company gazetteer misses, and every academic rule that keys on a university gazetteer fires on the wrong role. | §4.9 ‘A university name alone should not create a group because Columbia can appear as an authoring school, course provider, target institution, employer, research venue, or merely a cited organization.’ §3.8 ‘A consulting document may mention the author’s firm and the client organization. A finance document may mention an account holder and an issuing bank. The agent should model these as distinct facets, such as authored_by and target_school, or our_firm and client.’ |
| `career.academic-cv` | The CV is a member of this packet and of its own version family; the packet must not claim the CV's revision history. | §6.9 ‘A transcript may be part of several application packets; a resume may support multiple recruiting processes; a research abstract may belong to a research project and be attached to a university application.’ |
| `res.research-project` | A research statement is a career artifact; a manuscript describing the same work is a research artifact. Both name the project. | §3.11 ‘One file may hold facts from more than one domain without losing information. An academic abstract submitted as part of a university application can retain project = PVA/RDP and document type = abstract while also carrying purpose = university application and target university = UChicago.’ |

---

## `career.resume` — Resume and its tailoring family

The corpus owner's own targeted career summary, and the family of variants tailored from it.

| | |
|---|---|
| **provenance** | `inference` |
| **design cite** | §6.9 ‘A transcript may be part of several application packets; a resume may support multiple recruiting processes; a research abstract may belong to a research project and be attached to a university application.’ |
| **sensitivity** | `potentially_sensitive` — §2.9's phrase ‘potentially sensitive’. A resume header normally carries a home address, a phone number and an email address. No handling class is assigned here. |

**Schema** — the fields this domain, and only this domain, legitimises.

| field | type | example | ceiling | why |
|---|---|---|---|---|
| `document_variant` | enum-like | resume | `validated` | Recognisable from co-occurring section headings, which is a rule passing a context check rather than a filename match. |
| `tailored_for_employer` | string | Deloitte | `validated` | A gazetteer employer name in the filename or headline zone of a document whose body carries resume headings. Positional weighting is doing the work — §3.7 ‘It should use word-boundary matching rather than substring matching. Without this rule, names such as MIT can be found inside “submit,” and UNC can be found inside “uncertainty,” producing polished but completely false filing paths.’ |
| `tailored_for_role` | string | Data Analyst | `llm_supported` | Tailoring to a role usually shows only as a rewritten summary paragraph, which is interpretation. |
| `resume_version_label` | string | v4 | `possible` | A filename suffix is never sufficient on its own to establish version-family membership; it is a clue for review. |
| `format_variant` | enum-like | ATS plain text | `validated` | Distinguishable structurally — a single-column, table-free layout versus a designed multi-column one. |
| `contains_personal_contact_block` | boolean | true | `direct` | A labeled phone or email in the header zone. This is one of §3.11's fields ‘used only for search, privacy protection, explanation, or later review’ — §3.11 ‘Each domain activates only a small set of relevant fields, usually three to six that may help build a future folder proposal and several additional fields used only for search, privacy protection, explanation, or later review.’ |

**Recognition**

| kind | entries |
|---|---|
| deterministic (pattern **plus** corroborating context) | • a document whose first page carries the headings ‘Experience’ \| ‘Education’ \| ‘Skills’ \| ‘Professional Summary’ together<br>• a filename token ‘resume’ \| ‘cv’ co-occurring with those section headings in the extracted text |
| needs the LLM | • a designed one-page resume exported as an image, where only OCR fragments survive<br>• deciding whether the later of two near-identical files is a newer revision or a sideways tailoring for a different employer |
| never alone | • a filename containing ‘resume’ or ‘CV’ — a filename token alone, with no corroborating extracted text<br>• a person's name on its own; it identifies an author, not a domain<br>• a phone number or an email address<br>• a ‘v2’, ‘final’ or ‘FINAL2’ suffix |

**Work types** — `resume`, `tailored resume variant`, `ATS plain-text resume`, `editable source document`, `exported PDF`, `one-page and two-page variants`, `resume feedback markup`

**Grouping reasons** — one revision family of the same underlying resume; one tailoring family aimed at one employer; a resume and the application it was submitted with

**Template** — `document variant → recruiting cycle`  (time first: no)

> Shallow on purpose. A resume set is small and heavily interlinked, and §5.8 ‘One branch may require four levels, while another should remain flat.’ Forcing employer levels here would scatter a version family across branches.

**Collides with**

| domain | separating signal | design cite |
|---|---|---|
| `career.academic-cv` | Both are a person's own career summary and both answer to the filename ‘CV’. The separator is structural: publication, grant, teaching and peer-review sections appear in the CV and never in the resume. | — |
| `career.employer-candidate-packet` | A resume the owner wrote and a resume someone sent the owner are the same document type with opposite subjects. No signal inside the file distinguishes them unless the product knows who the owner is. | §3.8 ‘A consulting document may mention the author’s firm and the client organization. A finance document may mention an account holder and an issuing bank. The agent should model these as distinct facets, such as authored_by and target_school, or our_firm and client.’ §3.8 ‘It should avoid using authorship or creator identity as a destination dimension. A folder should not become a collection point for everything produced by the same person or organization.’ |
| `career.job-application` | One resume file legitimately belongs to several application packets at once, so packet membership must not be written back onto the resume as a fact. | §6.9 ‘A transcript may be part of several application packets; a resume may support multiple recruiting processes; a research abstract may belong to a research project and be attached to a university application.’ §6.9 ‘The user’s frozen tree should therefore include a policy for shared material: a shared branch, a primary-home convention, a reference or alias convention, or mandatory review.’ |
| `career.portfolio` | A designed resume is simultaneously a work sample for a designer. Both readings are true and neither may be dropped. | §3.11 ‘One file may hold facts from more than one domain without losing information. An academic abstract submitted as part of a university application can retain project = PVA/RDP and document type = abstract while also carrying purpose = university application and target university = UChicago.’ |

**Open question — unresolved, Joseph's call**

> Two resumes differing by one tailored paragraph and naming different employers: §3.1 makes ‘a member of a version family’ a universal fact, but is a tailoring family one version family with two live members, or two families? The answer decides whether either file may ever supersede the other, and the design does not say.

---

## `career.academic-cv` — Academic CV and its supporting statements

The long-form scholarly record — publications, grants, teaching, service — and the statement documents that travel with it.

| | |
|---|---|
| **provenance** | `inference` |
| **design cite** | §6.9 ‘A transcript may be part of several application packets; a resume may support multiple recruiting processes; a research abstract may belong to a research project and be attached to a university application.’ |
| **sensitivity** | `potentially_sensitive` — §2.9's phrase ‘potentially sensitive’. The header block carries personal contact details. No handling class is assigned here. |

**Schema** — the fields this domain, and only this domain, legitimises.

| field | type | example | ceiling | why |
|---|---|---|---|---|
| `cv_section` | enum-like | Publications | `validated` | The section vocabulary is closed and structurally recognisable, unlike resume prose. |
| `discipline` | string | Molecular Biology | `llm_supported` | Discipline is inferred from the content of the publication and teaching lists, never stated as a field. |
| `academic_rank` | string | Postdoctoral Fellow | `validated` | A closed rank vocabulary co-occurring with an institutional affiliation line. |
| `cv_variant` | enum-like | NIH biosketch | `validated` | Funder-mandated variants carry fixed mandatory headings that identify them exactly. |
| `institutional_affiliation` | string | Rockefeller University | `validated` | Here a university name is the author's own affiliation — a third distinct role beyond target and employer. §4.9 ‘A university name alone should not create a group because Columbia can appear as an authoring school, course provider, target institution, employer, research venue, or merely a cited organization.’ |
| `contains_personal_contact_block` | boolean | true | `direct` | Same privacy-only field as the resume; a labeled contact line in the header zone. |

**Recognition**

| kind | entries |
|---|---|
| deterministic (pattern **plus** corroborating context) | • a document whose headings carry ‘Publications’ \| ‘Grants’ \| ‘Teaching’ \| ‘Conference Presentations’ \| ‘Professional Service’ together<br>• a biosketch form marker co-occurring with its mandatory headings ‘Personal Statement’ \| ‘Positions and Honors’ \| ‘Contributions to Science’ |
| needs the LLM | • a short-form CV that has been trimmed until it is structurally indistinguishable from a resume<br>• separating a standalone bibliography from the publications section of a CV when only a text fragment survives |
| never alone | • the token ‘CV’ in a filename<br>• a publication list — a bibliography, a reading list and a reference section produce the same shape<br>• a person's name on its own; it identifies an author, not a domain |

**Work types** — `academic CV`, `short-form CV`, `funder biosketch`, `publication list`, `teaching statement`, `research statement`, `service record`, `grant history`

**Grouping reasons** — one CV and its revisions; a CV and the job packet it was submitted in

**Template** — `cv variant → search cycle`  (time first: no)

> Variant first, because a biosketch and a full CV are different documents rather than versions of one. §5.5 ‘The recommendation should follow the practical rule that a parent dimension should provide the context required to understand the child.’

**Collides with**

| domain | separating signal | design cite |
|---|---|---|
| `career.resume` | See the resume entry; the discriminator is the presence of scholarly sections. | — |
| `res.research-project` | A publication list is both a career document and an index of research artifacts. The CV must not become a collector for the research outputs it names. | §3.8 ‘It should avoid using authorship or creator identity as a destination dimension. A folder should not become a collection point for everything produced by the same person or organization.’ |
| `career.academic-job-application` | The CV is a member of the packet and of its own family at once. | §6.9 ‘A transcript may be part of several application packets; a resume may support multiple recruiting processes; a research abstract may belong to a research project and be attached to a university application.’ |

---

## `career.cover-letter` — Cover letter and letter of interest

A letter written to one named recipient at one employer in support of one application.

| | |
|---|---|
| **provenance** | `inference` |
| **design cite** | §3.3 ‘The LLM may determine whether an extracted document appears to be an application essay, research artifact, recruiting document, travel record, or other supported domain’ |
| **sensitivity** | `potentially_sensitive` — §2.9's phrase ‘potentially sensitive’. A letterhead carries the writer's home address. No handling class is assigned here. |

**Schema** — the fields this domain, and only this domain, legitimises.

| field | type | example | ceiling | why |
|---|---|---|---|---|
| `employer` | string | Baker McKenzie | `validated` | A gazetteer name in the addressee block of a document with letter structure. The addressee block is a positional signal — §3.7 ‘It should use word-boundary matching rather than substring matching. Without this rule, names such as MIT can be found inside “submit,” and UNC can be found inside “uncertainty,” producing polished but completely false filing paths.’ |
| `role_title` | string | Trainee Solicitor | `llm_supported` | The role is stated inside the first sentence in prose (‘I am writing to apply for the position of…’), not as a field. |
| `addressee` | string | Ms J. Whitfield, Hiring Manager | `direct` | A letter's salutation and address block are a labeled structural region. |
| `letter_date` | date | 2026-02-11 | `direct` | A letter carries its date in a fixed position; this is not the file's creation date. |
| `letter_type` | enum-like | speculative letter of interest | `llm_supported` | Whether a letter answers a posting or is unsolicited is only visible in its prose. |
| `source_template` | string | generic-consulting-v2 | `possible` | Shared boilerplate across letters is a clue that they belong to one tailoring family; it is never asserted as a fact. |

**Recognition**

| kind | entries |
|---|---|
| deterministic (pattern **plus** corroborating context) | • an address block and a salutation co-occurring with application language ‘apply’ \| ‘position’ \| ‘the role of’ \| ‘I am writing’ within the opening region<br>• a gazetteer employer name in an addressee block co-occurring with application language ‘apply’ \| ‘the role of’ \| ‘your advertisement’ in the opening region |
| needs the LLM | • an unaddressed letter whose only employer signal is a described product or mission<br>• distinguishing a cover letter from a letter of resignation or a reference letter when the address block is the only structure recovered |
| never alone | • letter structure alone — resignations, references, complaints and offers share it<br>• a company or organisation name on its own — §4.9 ‘A university name alone should not create a group because Columbia can appear as an authoring school, course provider, target institution, employer, research venue, or merely a cited organization.’<br>• a filename containing ‘letter’ |

**Work types** — `cover letter`, `letter of interest`, `speculative approach letter`, `networking follow-up letter`, `letter template`

**Grouping reasons** — one letter and the application it supports; a tailoring family sharing one boilerplate

**Template** — `employer → recruiting cycle`  (time first: no)

> Employer first, because a letter is meaningless without its addressee. §5.5 ‘The recommendation should follow the practical rule that a parent dimension should provide the context required to understand the child.’

**Collides with**

| domain | separating signal | design cite |
|---|---|---|
| `career.job-application` | The letter is a member of the packet; the packet is not a member of the letter's tailoring family. | §6.9 ‘A transcript may be part of several application packets; a resume may support multiple recruiting processes; a research abstract may belong to a research project and be attached to a university application.’ |
| `acad.college-application` | A cover letter and an admissions personal statement are both first-person persuasive documents naming a target organisation. Only the cover letter carries a role and an addressee. | §4.8 ‘that an application packet does not silently absorb a document with a conflicting target institution’ |
| `career.reference-and-recommendation` | A letter written by the owner about themselves and a letter written by someone else about the owner have identical structure and opposite authorship roles. | §3.8 ‘A consulting document may mention the author’s firm and the client organization. A finance document may mention an account holder and an issuing bank. The agent should model these as distinct facets, such as authored_by and target_school, or our_firm and client.’ |

---

## `career.portfolio` — Professional portfolio and work samples

Work the owner shows to prove capability — case studies, samples, showreels — where the right to show it is part of the record.

| | |
|---|---|
| **provenance** | `proposal` |
| **design cite** | _none — nothing in the design speaks to this domain_ |
| **sensitivity** | `potentially_sensitive` — §2.9's phrase ‘potentially sensitive’. Portfolios frequently contain client-confidential material shown under a permission that the file does not state. No handling class is assigned here. |

**Schema** — the fields this domain, and only this domain, legitimises.

| field | type | example | ceiling | why |
|---|---|---|---|---|
| `portfolio_piece_type` | enum-like | case study | `validated` | Recognisable from the structural shape of the artifact plus portfolio framing language. |
| `discipline` | string | Product Design | `llm_supported` | Discipline is read from the content of the work itself. |
| `subject_organisation` | string | Monzo | `validated` | The organisation the work was done for. This is neither employer nor client in the recruiting sense — it is the subject of a shown artifact, a fourth role. |
| `showing_permission` | enum-like | public case study | `llm_supported` | Permission is stated in prose or implied by an accompanying agreement; it is exactly the field that must never be guessed. |
| `target_audience` | string | design hiring managers | `llm_supported` | Stated only in framing prose where stated at all. |
| `presentation_format` | enum-like | PDF deck | `direct` | Read from format and structure metadata. |

**Recognition**

| kind | entries |
|---|---|
| deterministic (pattern **plus** corroborating context) | • portfolio framing language ‘case study’ \| ‘selected work’ \| ‘portfolio’ \| ‘my role’ \| ‘outcome’ co-occurring with an organisation name<br>• a deck whose slide titles carry ‘problem’ \| ‘process’ \| ‘outcome’ together with an authorship line naming the owner |
| needs the LLM | • a raw design or code artifact with no framing, where only the surrounding set suggests it was assembled to be shown<br>• judging whether a client deliverable has been reworked into a shareable case study or is still the original confidential deliverable |
| never alone | • a filename containing ‘portfolio’ — investment portfolios produce the same token<br>• a company or organisation name on its own — §4.9 ‘A university name alone should not create a group because Columbia can appear as an authoring school, course provider, target institution, employer, research venue, or merely a cited organization.’<br>• an image or a deck on its own |

**Work types** — `case study`, `work sample`, `showreel`, `code sample`, `writing sample`, `portfolio site export`, `project one-pager`, `before-and-after set`

**Grouping reasons** — one portfolio assembled for one search; all pieces about one subject organisation

**Template** — `discipline → subject organisation → portfolio piece type`  (time first: no)

> Subject organisation supplies the context a piece type needs — §5.5 ‘The recommendation should follow the practical rule that a parent dimension should provide the context required to understand the child.’ Not authored by employer: §3.8 ‘It should avoid using authorship or creator identity as a destination dimension. A folder should not become a collection point for everything produced by the same person or organization.’

**Collides with**

| domain | separating signal | design cite |
|---|---|---|
| `career.consulting-engagement` | A case study is a reworked deliverable. The original engagement file and the portfolio version look nearly identical and carry opposite showing permissions; treating them as one version family would let a confidential deliverable inherit a public case study's permission. | §3.8 ‘A consulting document may mention the author’s firm and the client organization. A finance document may mention an account holder and an issuing bank. The agent should model these as distinct facets, such as authored_by and target_school, or our_firm and client.’ |
| `career.take-home-assessment` | A take-home built for one employer is often recycled as a portfolio piece. The employer-owned prompt and the owner's showable write-up are different artifacts with different permissions. | — |
| `soft.source-project` | A code sample is both a portfolio piece and a repository; §3.11's Code fields and this domain's fields both apply and neither wins. | §3.11 ‘One file may hold facts from more than one domain without losing information. An academic abstract submitted as part of a university application can retain project = PVA/RDP and document type = abstract while also carrying purpose = university application and target university = UChicago.’ |

---

## `career.interview-cycle` — Interview cycle

The staged process one candidate runs with one employer for one role, and the artifacts each stage produces.

| | |
|---|---|
| **provenance** | `design` |
| **design cite** | §4.5 ‘does the supplied evidence support one understandable organizing reason, such as one course, project, application, recruiting process, photo event, or submission packet?’ §5.4 ‘a Career template may define company → role or recruiting cycle → document type’ |
| **sensitivity** | `none` — Scheduling and prep material for the owner's own interviews carries no identifier, amount or third-party personal data beyond ordinary business contact names. |

**Schema** — the fields this domain, and only this domain, legitimises.

| field | type | example | ceiling | why |
|---|---|---|---|---|
| `employer` | string | Stripe | `validated` | A gazetteer name plus interview language. §4.9 ‘A university name alone should not create a group because Columbia can appear as an authoring school, course provider, target institution, employer, research venue, or merely a cited organization.’ |
| `role_title` | string | Staff Engineer | `llm_supported` | Interview correspondence names the role in prose far more often than in a field. |
| `recruiting_cycle` | string | 2026 H1 | `validated` | §5.4's ‘recruiting cycle’ — the container that lets two attempts at the same employer stay apart. |
| `stage` | enum-like | onsite loop | `validated` | Stage vocabulary — screen, phone, loop, panel, final — is closed and recognisable beside scheduling language. |
| `interview_date` | date | 2026-04-09 | `direct` | A calendar invitation carries a labeled start time; §2.9 makes ICS a first-class extractor output. |
| `interviewer` | string | R. Devi, Engineering Manager | `llm_supported` | Names appear in invitations and schedules but a name alone establishes nothing. |
| `interview_format` | enum-like | system design | `llm_supported` | Format is described in prep prose (‘this session will focus on system design’). |

**Recognition**

| kind | entries |
|---|---|
| deterministic (pattern **plus** corroborating context) | • a gazetteer employer name co-occurring with interview language ‘interview’ \| ‘screen’ \| ‘onsite’ \| ‘panel’ \| ‘loop’ \| ‘recruiter’<br>• a calendar event whose title carries interview language and whose organiser domain matches an employer already established on the file set |
| needs the LLM | • prep notes that describe a company and a role without naming either<br>• a thread in which the stage advanced but no message states the new stage |
| never alone | • a company or organisation name on its own — §4.9 ‘A university name alone should not create a group because Columbia can appear as an authoring school, course provider, target institution, employer, research venue, or merely a cited organization.’<br>• a calendar invitation on its own — an internal meeting has the same shape<br>• the word ‘interview’ in a filename; research interviews and journalism produce it<br>• a bounded download session on its own — §3.9 ‘A session should never be treated as proof of topic, and it should not carry the same confidence as a hash match or a directly extracted document fact.’ |

**Work types** — `recruiter correspondence`, `interview schedule`, `calendar invitation`, `prep notes`, `question bank`, `post-interview debrief note`, `rejection message`, `thank-you note`

**Grouping reasons** — one employer, one role, one cycle across all stages; one stage and the artifacts produced around it

**Template** — `employer → recruiting cycle → stage`  (time first: no)

> Stage is unreadable without the employer and cycle that contain it — §5.5 ‘The recommendation should follow the practical rule that a parent dimension should provide the context required to understand the child.’ §5.5 ‘For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders.’ even though every stage carries a date.

**Collides with**

| domain | separating signal | design cite |
|---|---|---|
| `career.job-application` | The application is the submission; the cycle is what happens afterwards. They share employer, role and cycle, and a corpus where the two collapse cannot answer ‘did I ever hear back’. | — |
| `career.employer-interview-scorecard` | The candidate's debrief note and the employer's scorecard describe the same conversation from opposite sides, and both use rubric vocabulary. Only the employer's version names a candidate as its subject. | §3.8 ‘A consulting document may mention the author’s firm and the client organization. A finance document may mention an account holder and an issuing bank. The agent should model these as distinct facets, such as authored_by and target_school, or our_firm and client.’ |
| `acad.course-enrollment` | Interview prep material for a technical loop is structurally identical to coursework problem sets, and both attract the same algorithms vocabulary. | — |

---

## `career.take-home-assessment` — Take-home and screening assessment

Work produced for an employer as a test rather than as employment, together with the prompt that defined it.

| | |
|---|---|
| **provenance** | `inference` |
| **design cite** | §4.5 ‘does the supplied evidence support one understandable organizing reason, such as one course, project, application, recruiting process, photo event, or submission packet?’ |
| **sensitivity** | `potentially_sensitive` — §2.9's phrase ‘potentially sensitive’. Assessment briefs are usually employer-confidential and often carry an explicit instruction not to share. No handling class is assigned here. |

**Schema** — the fields this domain, and only this domain, legitimises.

| field | type | example | ceiling | why |
|---|---|---|---|---|
| `employer` | string | Palantir | `validated` | A gazetteer name inside an assessment brief; the brief is the only place it appears. |
| `role_title` | string | Data Scientist | `llm_supported` | Named in the brief's prose framing. |
| `assessment_type` | enum-like | take-home exercise | `validated` | A closed vocabulary — take-home, online assessment, case study, work sample, live exercise — beside assessment language. |
| `assessment_platform` | string | HackerRank | `validated` | A platform host name co-occurring with assessment language; the same host name in a bookmark means nothing. |
| `brief_or_submission` | enum-like | submission | `validated` | Structurally separable: a brief states requirements and a deadline, a submission answers them. |
| `deadline` | date | 2026-05-02 | `direct` | Briefs carry a labeled due date. |
| `stack_or_language` | string | Python | `validated` | Recognisable from repository markers and file extensions; this is §3.11's Code vocabulary borrowed, not redefined. |

**Recognition**

| kind | entries |
|---|---|
| deterministic (pattern **plus** corroborating context) | • assessment language ‘take-home’ \| ‘assessment’ \| ‘exercise’ \| ‘please submit’ \| ‘time limit’ co-occurring with a gazetteer employer name<br>• a repository or project directory whose README carries assessment language together with a gazetteer employer name |
| needs the LLM | • a bare project folder whose only assessment signal is that the surrounding correspondence mentions an employer<br>• deciding whether a solved exercise was set by an employer, a course, or the owner's own practice |
| never alone | • a repository or notebook on its own — §4.9 ‘A university name alone should not create a group because Columbia can appear as an authoring school, course provider, target institution, employer, research venue, or merely a cited organization.’ applies equally to a company name in a README<br>• the word ‘assessment’ or ‘challenge’ in a path<br>• a bounded download session on its own — §3.9 ‘A session should never be treated as proof of topic, and it should not carry the same confidence as a hash match or a directly extracted document fact.’ |

**Work types** — `assessment brief`, `submitted solution`, `solution repository`, `written analysis`, `presentation deck`, `screening test result`, `reviewer feedback`

**Grouping reasons** — one employer's brief together with the submission answering it; one cycle's assessments across stages

**Template** — `employer → recruiting cycle → assessment type`  (time first: no)

> Employer first: an exercise divorced from its employer is indistinguishable from a personal project. §5.5 ‘The recommendation should follow the practical rule that a parent dimension should provide the context required to understand the child.’

**Collides with**

| domain | separating signal | design cite |
|---|---|---|
| `soft.source-project` | A take-home repository is a repository. §3.11's Code fields — project, repository, programming language, artifact type — all apply, and so do these. Neither domain may suppress the other. | §3.11 ‘One file may hold facts from more than one domain without losing information. An academic abstract submitted as part of a university application can retain project = PVA/RDP and document type = abstract while also carrying purpose = university application and target university = UChicago.’ |
| `acad.course-enrollment` | A take-home and a problem set have the same structure, the same deadline framing, and often the same subject matter. The separator is whether an employer or a course code sits in the corroborating context. | §3.5 ‘For example, BUSIB 4300 becomes a course fact only when the engine finds a course-code pattern together with academic context such as “syllabus,” “lecture,” “credits,” “instructor,” or “semester.”’ |
| `career.portfolio` | Recycling a take-home as a portfolio piece produces two files with the same content and different showing permissions. | — |

**Open question — unresolved, Joseph's call**

> A take-home repository satisfies §3.11's Code schema and this one simultaneously. Should the Career reading or the Code reading determine its physical home by default, and should an employer-confidential brief be allowed to sit inside a code branch at all?

---

## `career.offer-and-negotiation` — Offer and negotiation

An employer's proposal of employment, everything exchanged while it is negotiated, and its acceptance or refusal.

| | |
|---|---|
| **provenance** | `inference` |
| **design cite** | §3.3 ‘The LLM may determine whether an extracted document appears to be an application essay, research artifact, recruiting document, travel record, or other supported domain’ §5.4 ‘a Career template may define company → role or recruiting cycle → document type’ |
| **sensitivity** | `potentially_sensitive` — §2.9's phrase ‘potentially sensitive’. Offer documents state compensation figures and personal terms. No handling class is assigned here. |

**Schema** — the fields this domain, and only this domain, legitimises.

| field | type | example | ceiling | why |
|---|---|---|---|---|
| `employer` | string | Novartis | `validated` | A gazetteer name on a document carrying offer language; the letterhead position adds weight — §3.7 ‘It should use word-boundary matching rather than substring matching. Without this rule, names such as MIT can be found inside “submit,” and UNC can be found inside “uncertainty,” producing polished but completely false filing paths.’ |
| `role_title` | string | Regulatory Affairs Manager | `validated` | Offer letters state the position on a labeled line beside offer language. |
| `start_date` | date | 2026-09-01 | `direct` | A labeled ‘start date’ or ‘commencement date’ line. It is not the letter's date and not the file's creation date. |
| `offer_date` | date | 2026-06-14 | `direct` | The letter's own labeled date. |
| `compensation_component` | enum-like | base salary | `validated` | Components — base, bonus, signing, relocation, equity — appear as labeled lines in a compensation table. |
| `offer_status` | enum-like | accepted | `llm_supported` | Status lives in correspondence prose and countersignature, not in a field. |
| `offer_expiry` | date | 2026-06-21 | `direct` | Stated as a labeled response-by line where present. |
| `competing_employer` | string | Roche | `possible` | A second employer named inside a negotiation thread is a leverage mention, not a second offer. It must never create an offer fact for that employer. |

**Recognition**

| kind | entries |
|---|---|
| deterministic (pattern **plus** corroborating context) | • offer language ‘offer of employment’ \| ‘we are pleased to offer’ \| ‘conditional offer’ \| ‘base salary’ \| ‘start date’ co-occurring with a gazetteer employer name<br>• a labeled compensation table co-occurring with a labeled start-date line |
| needs the LLM | • a negotiation thread in which the improved terms are described in prose and no revised letter exists<br>• distinguishing a verbal-offer summary note from a formal offer |
| never alone | • a currency-shaped amount on its own<br>• a company or organisation name on its own — §4.9 ‘A university name alone should not create a group because Columbia can appear as an authoring school, course provider, target institution, employer, research venue, or merely a cited organization.’<br>• a labeled start date — onboarding paperwork, contracts and visa petitions all carry one |

**Work types** — `offer letter`, `revised offer letter`, `compensation breakdown`, `negotiation correspondence`, `counteroffer note`, `acceptance letter`, `declination letter`, `rescission notice`, `competing-offer comparison`

**Grouping reasons** — one employer, one role, one offer and its revisions; all offers held simultaneously during one decision

**Template** — `employer → recruiting cycle → offer status`  (time first: no)

> Employer first — an offer is only interpretable against the employer making it. §5.5 ‘The recommendation should follow the practical rule that a parent dimension should provide the context required to understand the child.’ Revisions of one offer are a version family, not separate branches.

**Collides with**

| domain | separating signal | design cite |
|---|---|---|
| `career.employment-contract` | An offer is a proposal; a contract is executed. They repeat employer, role, start date and compensation, and differ by signature blocks, governing-law clauses and clause numbering. Filing them together makes it impossible to answer which terms are binding. | — |
| `career.employer-offer-approval` | The employer's internal approval and the candidate's received letter carry the same numbers. Only the approval names an approver and an internal band. | §3.8 ‘A consulting document may mention the author’s firm and the client organization. A finance document may mention an account holder and an issuing bank. The agent should model these as distinct facets, such as authored_by and target_school, or our_firm and client.’ |
| `career.compensation-record` | A merit-increase letter and an offer letter share the entire compensation vocabulary. Only the offer carries a start date and a role being entered rather than held. | — |
| `career.equity-compensation` | An offer names an equity grant in summary; the grant agreement governs it. The summary must not be treated as the grant record. | — |

---

## `career.reference-and-recommendation` — References and recommendations

Statements one person makes about another's work — written by the owner, written about the owner, or collected about someone else.

| | |
|---|---|
| **provenance** | `proposal` |
| **design cite** | _none — nothing in the design speaks to this domain_ |
| **sensitivity** | `potentially_sensitive` — §2.9's phrase ‘potentially sensitive’. A reference is a named third party's candid assessment of a named person, and reference lists carry referees' contact details. No handling class is assigned here. |

**Schema** — the fields this domain, and only this domain, legitimises.

| field | type | example | ceiling | why |
|---|---|---|---|---|
| `subject_of_reference` | string | the corpus owner | `llm_supported` | Who the letter is about. This is the field the whole domain turns on, and §3.8 requires it to be distinct from authorship — §3.8 ‘A consulting document may mention the author’s firm and the client organization. A finance document may mention an account holder and an issuing bank. The agent should model these as distinct facets, such as authored_by and target_school, or our_firm and client.’ |
| `referee` | string | Dr M. Halvorsen | `llm_supported` | The author of the statement; a signature block is structural but attributing it needs interpretation. |
| `referee_organisation` | string | Kings College Hospital | `validated` | A gazetteer organisation name inside a signature block or letterhead. |
| `relationship_to_subject` | string | former line manager | `llm_supported` | Stated in the opening sentence in prose (‘I managed X for three years’). |
| `addressee` | string | The Admissions Committee | `direct` | The letter's address block. |
| `reference_type` | enum-like | employment reference | `validated` | Employment references, academic recommendations, character references and reference-check forms are structurally distinguishable. |
| `letter_date` | date | 2026-03-02 | `direct` | The letter's own labeled date. |

**Recognition**

| kind | entries |
|---|---|
| deterministic (pattern **plus** corroborating context) | • letter structure co-occurring with recommendation language ‘I am pleased to recommend’ \| ‘in my capacity as’ \| ‘reference for’ \| ‘to whom it may concern’<br>• a reference-check form whose labeled fields carry ‘dates of employment’, ‘job title’ and ‘eligible for rehire’ together |
| needs the LLM | • deciding whether an unaddressed letter is about the corpus owner or about someone else<br>• a lukewarm reference where the assessment is entirely implicit |
| never alone | • a person's name on its own; it identifies an author, not a domain<br>• letter structure on its own<br>• a filename containing ‘reference’ — bibliographies, reference clips and API references all produce it |

**Work types** — `reference letter`, `recommendation letter`, `reference list`, `reference-check form`, `employer verification of dates`, `letter drafted for someone else`, `referee request correspondence`

**Grouping reasons** — all references supporting one application; all letters written by one referee about one subject

**Template** — `subject of reference → reference type → recruiting cycle`  (time first: no)

> Subject before everything, because a letter about the owner and a letter the owner wrote about someone else must never share a branch. Not referee-first: §3.8 ‘It should avoid using authorship or creator identity as a destination dimension. A folder should not become a collection point for everything produced by the same person or organization.’

**Collides with**

| domain | separating signal | design cite |
|---|---|---|
| `acad.college-application` | §4.7's own packet names a recommendation form as a supporting record for a university application. The same letter type serves employment references, and the two packets pull it in opposite directions. | §3.9 ‘A university application packet can contain an identification document, transcript, resume, certificate, and academic abstract. The documents are content-incoherent but purpose-coherent.’ §4.8 ‘that an application packet does not silently absorb a document with a conflicting target institution’ |
| `career.employer-candidate-packet` | A reference the owner collected about a job candidate is a third party's assessment of another third party. Its subject is neither the owner nor the employer. | §3.8 ‘A consulting document may mention the author’s firm and the client organization. A finance document may mention an account holder and an issuing bank. The agent should model these as distinct facets, such as authored_by and target_school, or our_firm and client.’ §2.9 ‘Contact formats such as VCF should yield names, organizations, email addresses, phone numbers, and address-book metadata, but should normally be privacy-protected rather than used to create folder proposals.’ |
| `career.cover-letter` | Both are first-person letters naming an employer; only the reference has a subject other than its author. | §3.8 ‘A consulting document may mention the author’s firm and the client organization. A finance document may mention an account holder and an issuing bank. The agent should model these as distinct facets, such as authored_by and target_school, or our_firm and client.’ |

---

## `career.onboarding-paperwork` — Onboarding paperwork

The one-time intake forms an employer requires before or at the start of employment.

| | |
|---|---|
| **provenance** | `proposal` |
| **design cite** | _none — nothing in the design speaks to this domain_ |
| **sensitivity** | `potentially_sensitive` — §2.9's phrase ‘potentially sensitive’. Intake forms carry government identifiers and bank account details. No handling class is assigned here. |

**Schema** — the fields this domain, and only this domain, legitimises.

| field | type | example | ceiling | why |
|---|---|---|---|---|
| `employer` | string | Kaiser Permanente | `validated` | A gazetteer name beside onboarding language; forms carry it in a labeled employer field. |
| `form_type` | enum-like | tax withholding form | `validated` | Intake forms are named documents with fixed titles and fixed labeled fields. |
| `tax_jurisdiction` | string | California | `direct` | A labeled jurisdiction field on the form itself. |
| `effective_date` | date | 2026-09-01 | `direct` | A labeled effective or start line. |
| `submission_status` | enum-like | signed and returned | `llm_supported` | Whether a form was completed is visible from signature presence and correspondence, not from a field. |
| `carries_government_identifier` | boolean | true | `direct` | A labeled national-insurance, social-security or tax-number field is present. A privacy-and-explanation field in §3.11's sense — §3.11 ‘Each domain activates only a small set of relevant fields, usually three to six that may help build a future folder proposal and several additional fields used only for search, privacy protection, explanation, or later review.’ |

**Recognition**

| kind | entries |
|---|---|
| deterministic (pattern **plus** corroborating context) | • an onboarding form title co-occurring with employment language ‘new hire’ \| ‘first day’ \| ‘employee’ \| ‘payroll’ \| ‘withholding’<br>• a labeled government-identifier field co-occurring with a labeled employer field |
| needs the LLM | • an employer's bespoke intake pack with no standard form titles<br>• distinguishing an onboarding acknowledgement from an annual policy re-acknowledgement |
| never alone | • a blank form template — an unfilled form is not a record of employment<br>• a company or organisation name on its own — §4.9 ‘A university name alone should not create a group because Columbia can appear as an authoring school, course provider, target institution, employer, research venue, or merely a cited organization.’<br>• a nine-digit number, which is a §3.10 hazard as much as a year is |

**Work types** — `tax withholding form`, `right-to-work check`, `direct-deposit form`, `emergency-contact form`, `handbook acknowledgement`, `IT and asset issue form`, `background-check authorisation`, `policy attestation`

**Grouping reasons** — one employer, one joining date; one intake pack submitted together

**Template** — `employer → form type`  (time first: no)

> Two levels only: an intake pack is small and arrives once. §5.8 ‘One branch may require four levels, while another should remain flat.’

**Collides with**

| domain | separating signal | design cite |
|---|---|---|
| `career.payroll` | A withholding form and a payslip both name employer, jurisdiction and tax figures. The form is an instruction submitted once; the payslip is a recurring statement issued back. Merging them makes the recurring series unfindable. | — |
| `career.employment-contract` | Both are signed at joining. Only the contract carries governing law and clause structure; only the paperwork carries labeled identifier fields. | — |
| `career.work-authorization` | A right-to-work check and an immigration petition both verify status. The check is an employer's file copy; the petition is a government submission. | §4.9 ‘Rare but sensitive files such as passports, visas, and legal documents may be surfaced as protected records even when they do not meet a normal group-size threshold.’ |

---

## `career.employment-contract` — Employment contract

The executed agreement that governs an employment, and the amendments that change it.

| | |
|---|---|
| **provenance** | `proposal` |
| **design cite** | _none — nothing in the design speaks to this domain_ |
| **sensitivity** | `potentially_sensitive` — §2.9's phrase ‘potentially sensitive’, and §4.9 ‘Rare but sensitive files such as passports, visas, and legal documents may be surfaced as protected records even when they do not meet a normal group-size threshold.’ names legal documents among the material that may be surfaced as protected. No handling class is assigned here. |

**Schema** — the fields this domain, and only this domain, legitimises.

| field | type | example | ceiling | why |
|---|---|---|---|---|
| `employer` | string | Siemens AG | `validated` | The contracting party, named in the parties clause — a labeled structural region. |
| `contract_type` | enum-like | fixed-term | `validated` | A closed vocabulary — permanent, fixed-term, at-will, zero-hours, secondment — recognisable beside contract language. |
| `effective_date` | date | 2026-09-01 | `direct` | A labeled commencement clause. |
| `term_end_date` | date | 2028-08-31 | `possible` | Present only in fixed-term contracts, and often expressed as a duration rather than a date; a duration must not be turned into a date. |
| `governing_law` | string | England and Wales | `direct` | A labeled governing-law clause. This is the field that most cleanly separates a contract from an offer. |
| `clause_type` | enum-like | notice period | `validated` | Clause headings are structural and closed enough to enumerate. |
| `amendment_of` | string | the 2026 contract | `possible` | An amendment names its parent in prose; the link is a clue for version-family review, not an asserted relation. |

**Recognition**

| kind | entries |
|---|---|
| deterministic (pattern **plus** corroborating context) | • contract language ‘this agreement’ \| ‘the parties’ \| ‘governed by the laws of’ \| ‘notice period’ co-occurring with employment language ‘employee’ \| ‘employment’ \| ‘duties’<br>• a parties clause naming a gazetteer employer alongside a natural person |
| needs the LLM | • a short letter-form contract that reads like an offer but is the operative agreement<br>• identifying which of several signed copies is the operative one when none is labeled |
| never alone | • contract language on its own — leases, client agreements and terms of service all produce it<br>• a company or organisation name on its own — §4.9 ‘A university name alone should not create a group because Columbia can appear as an authoring school, course provider, target institution, employer, research venue, or merely a cited organization.’<br>• a signature block |

**Work types** — `employment agreement`, `contract amendment`, `secondment agreement`, `fixed-term extension`, `role change letter`, `handbook incorporated by reference`, `signed counterpart`

**Grouping reasons** — one employment and every document that amends it; one contract and its signed counterparts

**Template** — `employer → contract type`  (time first: no)

> Employer first — a contract is defined by its counterparty. §5.5 ‘The recommendation should follow the practical rule that a parent dimension should provide the context required to understand the child.’ Amendments belong beside their parent rather than under a date.

**Collides with**

| domain | separating signal | design cite |
|---|---|---|
| `career.offer-and-negotiation` | See the offer entry: proposal versus executed agreement, separated by governing law and signature. | — |
| `career.restrictive-covenant` | Covenants are frequently clauses inside the contract and frequently separate signed documents. When separate they must not be filed as amendments to the contract, and when embedded they must not create a second domain record. | — |
| `career.freelance-contract-work` | A contractor agreement and an employment contract are near-identical documents whose whole legal point is that they are different. Worker-classification language is the only reliable separator. | §3.8 ‘A consulting document may mention the author’s firm and the client organization. A finance document may mention an account holder and an issuing bank. The agent should model these as distinct facets, such as authored_by and target_school, or our_firm and client.’ |
| `legal.contracts` | A general contracts domain claims every signed agreement in the corpus. An employment contract is distinguished by naming a natural person as one party and carrying duties, notice and place-of-work clauses; the two entries overlap and must be reconciled before the allow-list is frozen. | — |

---

## `career.restrictive-covenant` — Restrictive covenants and IP assignment

Standalone agreements that constrain what the owner may do or own — confidentiality, non-compete, non-solicit, invention assignment.

| | |
|---|---|
| **provenance** | `proposal` |
| **design cite** | _none — nothing in the design speaks to this domain_ |
| **sensitivity** | `potentially_sensitive` — §2.9's phrase ‘potentially sensitive’, and §4.9 ‘Rare but sensitive files such as passports, visas, and legal documents may be surfaced as protected records even when they do not meet a normal group-size threshold.’ names legal documents among the material that may be surfaced as protected. No handling class is assigned here. |

**Schema** — the fields this domain, and only this domain, legitimises.

| field | type | example | ceiling | why |
|---|---|---|---|---|
| `counterparty` | string | Anthem Health | `validated` | The organisation the obligation runs to. It may be an employer, a client, or a company the owner merely interviewed with — three roles, one field, which is why the counterparty role must be recorded separately. |
| `counterparty_role` | enum-like | prospective employer | `llm_supported` | Only the surrounding correspondence says whether the NDA was signed as an employee, a contractor, or a candidate. |
| `agreement_type` | enum-like | invention assignment | `validated` | A closed vocabulary with distinctive clause headings. |
| `effective_date` | date | 2026-08-19 | `direct` | A labeled effective-date clause. |
| `restriction_duration` | string | twelve months from termination | `direct` | Stated as a labeled term clause. Recorded as its stated text; converting a duration into a date would invent a fact. |
| `restriction_scope` | string | the United Kingdom | `llm_supported` | Geographic and field-of-work scope is defined in prose that has to be read. |
| `assignment_scope` | string | inventions arising from the work | `llm_supported` | The carve-outs are the whole content and are always prose. |

**Recognition**

| kind | entries |
|---|---|
| deterministic (pattern **plus** corroborating context) | • covenant language ‘shall not, directly or indirectly’ \| ‘confidential information’ \| ‘non-competition’ \| ‘non-solicitation’ \| ‘hereby assigns’ co-occurring with a parties clause<br>• an invention-assignment schedule co-occurring with employment or engagement language |
| needs the LLM | • a mutual NDA signed before an interview, where nothing states which side the owner was on<br>• reading a prior-inventions schedule that lists work the owner excluded from assignment |
| never alone | • the token ‘NDA’ in a filename<br>• a company or organisation name on its own — §4.9 ‘A university name alone should not create a group because Columbia can appear as an authoring school, course provider, target institution, employer, research venue, or merely a cited organization.’<br>• a signature block |

**Work types** — `non-disclosure agreement`, `mutual NDA`, `non-compete agreement`, `non-solicitation agreement`, `invention assignment agreement`, `prior-inventions schedule`, `confidentiality acknowledgement`, `garden-leave letter`

**Grouping reasons** — all obligations owed to one counterparty; one agreement and the engagement that triggered it

**Template** — `counterparty → agreement type`  (time first: no)

> Counterparty first, because the whole value of the record is knowing who an obligation is owed to. §5.5 ‘The recommendation should follow the practical rule that a parent dimension should provide the context required to understand the child.’

**Collides with**

| domain | separating signal | design cite |
|---|---|---|
| `career.employment-contract` | Embedded clause versus standalone document; see the contract entry. | — |
| `career.consulting-engagement` | A client NDA and an employment NDA are the same document with a different counterparty role. Filing by counterparty name alone would put an interview NDA beside an employer's IP assignment as if they were the same relationship. | §3.8 ‘A consulting document may mention the author’s firm and the client organization. A finance document may mention an account holder and an issuing bank. The agent should model these as distinct facets, such as authored_by and target_school, or our_firm and client.’ |
| `career.interview-cycle` | An NDA signed to see an assessment brief belongs to the hiring process, not to an employment that never began. | — |

---

## `career.work-authorization` — Work authorisation and sponsorship

Documents that establish or evidence the right to work — petitions, permits, sponsorship correspondence, status evidence.

| | |
|---|---|
| **provenance** | `proposal` |
| **design cite** | _none — nothing in the design speaks to this domain_ |
| **sensitivity** | `potentially_sensitive` — §2.9's phrase ‘potentially sensitive’, and §4.9 ‘Rare but sensitive files such as passports, visas, and legal documents may be surfaced as protected records even when they do not meet a normal group-size threshold.’ names visas explicitly. No handling class is assigned here. |

**Schema** — the fields this domain, and only this domain, legitimises.

| field | type | example | ceiling | why |
|---|---|---|---|---|
| `sponsoring_employer` | string | Infosys | `validated` | The petitioner. A gazetteer name inside a petition's labeled petitioner field. |
| `authorisation_category` | string | H-1B | `validated` | Category codes are a closed, jurisdiction-specific vocabulary that only means status beside immigration language. |
| `issuing_country` | string | United States | `direct` | A labeled issuing-authority field. |
| `case_or_receipt_number` | string | EAC2690123456 | `direct` | A labeled receipt or case-number field on the notice itself. |
| `validity_start` | date | 2026-10-01 | `direct` | A labeled validity-from line. |
| `validity_end` | date | 2029-09-30 | `direct` | A labeled validity-to line. This is the one date in the slice whose expiry actually matters to the owner. |
| `beneficiary_relationship` | enum-like | self | `llm_supported` | Petitions for a spouse or dependant look identical to petitions for the owner. |

**Recognition**

| kind | entries |
|---|---|
| deterministic (pattern **plus** corroborating context) | • an authorisation-category pattern co-occurring with immigration language ‘petition’ \| ‘beneficiary’ \| ‘sponsor’ \| ‘leave to remain’ \| ‘work permit’ \| ‘certificate of sponsorship’<br>• a labeled receipt-number field co-occurring with a named immigration authority |
| needs the LLM | • employer correspondence about sponsorship that names no category and no case number<br>• a scanned status document whose OCR recovers only fragments of the labeled fields |
| never alone | • an alphanumeric identifier pattern on its own<br>• a company or organisation name on its own — §4.9 ‘A university name alone should not create a group because Columbia can appear as an authoring school, course provider, target institution, employer, research venue, or merely a cited organization.’<br>• a country name<br>• a passport-shaped scan, which is an identity document before it is a work document — §4.9 ‘Rare but sensitive files such as passports, visas, and legal documents may be surfaced as protected records even when they do not meet a normal group-size threshold.’ |

**Work types** — `petition copy`, `approval notice`, `work permit`, `certificate of sponsorship`, `visa page scan`, `right-to-work share code`, `attorney correspondence`, `status-change application`, `employment verification for immigration`

**Grouping reasons** — one petition and every document filed with it; one authorisation and its extensions

**Template** — `sponsoring employer → authorisation category`  (time first: no)

> Employer first where the authorisation is employer-tied; where it is not, the branch flattens to category alone — §5.8 ‘One branch may require four levels, while another should remain flat.’

**Collides with**

| domain | separating signal | design cite |
|---|---|---|
| `pers.travel-visa-entry` | A visa page and a passport are the same scan. §4.9 ‘Rare but sensitive files such as passports, visas, and legal documents may be surfaced as protected records even when they do not meet a normal group-size threshold.’ already places passports and visas in protected territory, and §3.15 makes identity a safety domain. | §4.9 ‘Rare but sensitive files such as passports, visas, and legal documents may be surfaced as protected records even when they do not meet a normal group-size threshold.’ §3.15 ‘Finance, identity, medical, and legal material should be implemented first as safety domains, meaning the system detects and protects them before any cloud or automated placement decision is allowed.’ |
| `career.onboarding-paperwork` | A right-to-work check is an onboarding form that evidences an authorisation without being one. | — |
| `career.employment-verification` | Verification letters written for immigration purposes read as HR letters and are filed as immigration evidence. | — |
| `admin.immigration` | A near-duplicate authored in the personal-administration slice. That entry covers residence paperwork generally; this one is scoped to authorisation that an employer petitions for and that ends when the employment does. The two must be reconciled before the allow-list is frozen. | — |

**Open question — unresolved, Joseph's call**

> §3.15 makes identity and legal safety domains, ‘detected and protected’ before automated placement. An employer-sponsored work petition is simultaneously career material and identity material. Does it activate the Career schema, the identity safety domain, or both — and if both, which one governs where the file may physically go?

---

## `career.payroll` — Payroll records

The recurring statements an employer issues to an employee about pay actually made.

| | |
|---|---|
| **provenance** | `proposal` |
| **design cite** | _none — nothing in the design speaks to this domain_ |
| **sensitivity** | `potentially_sensitive` — §2.9's phrase ‘potentially sensitive’, and §8.4 ‘The product processes a highly personal corpus that can include identity documents, account statements, tax records, medical information, legal records, credentials, private correspondence, GPS metadata, employment materials, and educational records.’ No handling class is assigned here. |

**Schema** — the fields this domain, and only this domain, legitimises.

| field | type | example | ceiling | why |
|---|---|---|---|---|
| `employer` | string | Deloitte LLP | `validated` | The paying entity, in the payslip's labeled employer field. It is the employer role, not an account holder — §3.8 ‘A consulting document may mention the author’s firm and the client organization. A finance document may mention an account holder and an issuing bank. The agent should model these as distinct facets, such as authored_by and target_school, or our_firm and client.’ |
| `payroll_document_type` | enum-like | payslip | `validated` | Payslips, year-end summaries and adjustment statements have fixed labeled layouts. |
| `pay_period` | string | 2026-03 | `direct` | A labeled pay-period field. |
| `pay_date` | date | 2026-03-27 | `direct` | A labeled payment-date field, distinct from the period. |
| `tax_year` | string | 2026-27 | `direct` | A labeled tax-year field. §3.11 gives Finance a ‘tax year’ field; this is the same concept reached from the employment side, and the two must resolve to one value, not two. |
| `employee_identifier` | string | EMP-88213 | `direct` | A labeled employee-number field; a privacy-relevant identifier in §3.11's sense. |
| `currency` | string | GBP | `direct` | A labeled currency indicator on the pay lines. |

**Recognition**

| kind | entries |
|---|---|
| deterministic (pattern **plus** corroborating context) | • payroll language ‘gross pay’ \| ‘net pay’ \| ‘deductions’ \| ‘tax code’ \| ‘year to date’ co-occurring with a labeled employer field<br>• a labeled pay-period field co-occurring with a labeled employee-number field |
| needs the LLM | • a foreign-language payslip whose labels are unrecognised<br>• a scanned payslip where OCR recovers the numbers but not the labels |
| never alone | • a currency-shaped amount on its own<br>• a company or organisation name on its own — §4.9 ‘A university name alone should not create a group because Columbia can appear as an authoring school, course provider, target institution, employer, research venue, or merely a cited organization.’<br>• a month-shaped value — §3.10 ‘file names and documents frequently contain numbers that look like years but are course identifiers, version numbers, build numbers, ZIP codes, or other unrelated values’<br>• the token ‘payslip’ or ‘payroll’ in a filename |

**Work types** — `payslip`, `year-end tax summary`, `payroll adjustment statement`, `bonus payment advice`, `expense reimbursement advice`, `pension contribution statement`, `payroll correction letter`

**Grouping reasons** — one employer across one tax year; one recurring payslip series

**Template** — `employer → tax year → payroll document type`  (time first: no)

> Employer before year: §5.5 ‘For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders.’ and §5.5 ‘The recommendation should follow the practical rule that a parent dimension should provide the context required to understand the child.’ A person with two employers in one year needs the employer level to keep the two series apart.

**Collides with**

| domain | separating signal | design cite |
|---|---|---|
| `tax.supporting-documents` | A payslip satisfies §3.11's Finance schema — institution, account type, tax year, record type — as neatly as it satisfies this one, and a year-end summary is filed as tax evidence. §3.15 makes Finance a safety domain, so which schema activates decides whether the file is treated as protected material. | §3.11 ‘One file may hold facts from more than one domain without losing information. An academic abstract submitted as part of a university application can retain project = PVA/RDP and document type = abstract while also carrying purpose = university application and target university = UChicago.’ §3.15 ‘Finance, identity, medical, and legal material should be implemented first as safety domains, meaning the system detects and protects them before any cloud or automated placement decision is allowed.’ |
| `career.service-invoicing` | The sharpest role collision in this slice. A payslip is issued to the owner as an employee; an invoice is issued by the owner as a vendor. Both name an organisation, a period and an amount, and both are income. Only the payslip carries withholding and an employee number; only the invoice carries an owner-issued invoice number and payment terms. | §3.8 ‘A consulting document may mention the author’s firm and the client organization. A finance document may mention an account holder and an issuing bank. The agent should model these as distinct facets, such as authored_by and target_school, or our_firm and client.’ |
| `career.compensation-record` | A payslip evidences pay made; a comp letter states pay agreed. Merging them makes it impossible to check one against the other. | — |

**Open question — unresolved, Joseph's call**

> §3.11 gives Finance ‘institution, account type, tax year, record type’ and §3.15 makes Finance a safety domain, while ‘career and recruiting’ is a launch domain with no stated fields. A payslip sits in both. Does payroll activate the Career schema, the Finance safety domain, or both — and does the safety domain's protection follow the file into a Career branch?

---

## `career.benefits-enrollment` — Benefits enrolment

Elections and confirmations for employer-provided health, insurance and welfare benefits, including dependants.

| | |
|---|---|
| **provenance** | `proposal` |
| **design cite** | _none — nothing in the design speaks to this domain_ |
| **sensitivity** | `potentially_sensitive` — §2.9's phrase ‘potentially sensitive’. Enrolment records carry health-plan elections and dependants' personal details. No handling class is assigned here. |

**Schema** — the fields this domain, and only this domain, legitimises.

| field | type | example | ceiling | why |
|---|---|---|---|---|
| `employer` | string | Target Corporation | `validated` | The sponsoring employer, in a labeled sponsor field. |
| `benefit_type` | enum-like | dental | `validated` | A closed vocabulary of benefit lines recognisable beside enrolment language. |
| `plan_year` | string | 2027 | `direct` | A labeled plan-year field, which is not the calendar year of the file. |
| `carrier` | string | Aetna | `validated` | The insurer is a different organisation from the employer — two organisation roles on one document. |
| `plan_name` | string | PPO Choice Plus | `direct` | A labeled plan-name field. |
| `enrolment_status` | enum-like | elected | `llm_supported` | Whether an election was completed is stated in confirmation prose. |
| `covers_dependants` | boolean | true | `direct` | A labeled dependant section is present. A privacy-relevant field: dependants are third parties. |

**Recognition**

| kind | entries |
|---|---|
| deterministic (pattern **plus** corroborating context) | • enrolment language ‘open enrollment’ \| ‘elections’ \| ‘coverage effective’ \| ‘plan year’ \| ‘premium’ co-occurring with a labeled employer or carrier field<br>• a benefits-confirmation statement listing benefit lines beside a labeled plan-year field |
| needs the LLM | • a benefits guide that describes options without recording an election<br>• correspondence about a qualifying life event that changes coverage without a form |
| never alone | • a carrier name — an insurer appears on claims, statements and marketing alike<br>• a company or organisation name on its own — §4.9 ‘A university name alone should not create a group because Columbia can appear as an authoring school, course provider, target institution, employer, research venue, or merely a cited organization.’<br>• a four-digit year on its own — §3.10 ‘file names and documents frequently contain numbers that look like years but are course identifiers, version numbers, build numbers, ZIP codes, or other unrelated values’ |

**Work types** — `enrolment confirmation`, `benefits election form`, `benefits guide`, `insurance card`, `dependant verification`, `qualifying-event change form`, `premium statement`, `flexible-spending election`

**Grouping reasons** — one employer, one plan year; one benefit line across years

**Template** — `employer → plan year → benefit type`  (time first: no)

> Employer then plan year: benefits reset annually but belong to the employment that sponsors them. §5.5 ‘The recommendation should follow the practical rule that a parent dimension should provide the context required to understand the child.’

**Collides with**

| domain | separating signal | design cite |
|---|---|---|
| `med.health-plan-coverage` | Enrolment documents name conditions, dependants and providers, and §3.15 makes medical a safety domain. The enrolment record is career material; what it discloses is not. | §3.15 ‘Finance, identity, medical, and legal material should be implemented first as safety domains, meaning the system detects and protects them before any cloud or automated placement decision is allowed.’ |
| `career.payroll` | Premiums appear as payslip deductions, so the two domains describe the same money from opposite ends. | — |
| `career.retirement-records` | Retirement plans are enrolled through the same annual process and issue statements of their own; the enrolment and the statement series are different records. | — |

---

## `career.equity-compensation` — Equity compensation

Grants of stock, options or units, the plans that govern them, and the events that vest, exercise or settle them.

| | |
|---|---|
| **provenance** | `proposal` |
| **design cite** | _none — nothing in the design speaks to this domain_ |
| **sensitivity** | `potentially_sensitive` — §2.9's phrase ‘potentially sensitive’. Grant documents state holdings and prices, and §8.4 ‘The product processes a highly personal corpus that can include identity documents, account statements, tax records, medical information, legal records, credentials, private correspondence, GPS metadata, employment materials, and educational records.’ No handling class is assigned here. |

**Schema** — the fields this domain, and only this domain, legitimises.

| field | type | example | ceiling | why |
|---|---|---|---|---|
| `employer` | string | Datadog | `validated` | The granting company, in the grant agreement's parties clause. |
| `grant_type` | enum-like | RSU | `validated` | A closed vocabulary — ISO, NSO, RSU, RSA, SAR, phantom — recognisable beside equity language. |
| `grant_identifier` | string | GR-2026-0417 | `direct` | A labeled grant-number field. |
| `grant_date` | date | 2026-02-15 | `direct` | A labeled grant-date field. |
| `vesting_start` | date | 2026-03-01 | `direct` | A labeled vesting-commencement field, routinely different from the grant date. |
| `plan_name` | string | 2021 Equity Incentive Plan | `direct` | A labeled plan-name reference. |
| `equity_document_type` | enum-like | exercise notice | `validated` | Grant notices, plan documents, exercise notices, vesting statements and tax elections are structurally distinct. |

**Recognition**

| kind | entries |
|---|---|
| deterministic (pattern **plus** corroborating context) | • equity language ‘vesting schedule’ \| ‘exercise price’ \| ‘restricted stock units’ \| ‘option grant’ \| ‘cliff’ co-occurring with a labeled grant or plan reference<br>• a labeled grant-number field co-occurring with a labeled grant-date field |
| needs the LLM | • a summary email describing a refresh grant with no attached notice<br>• distinguishing an equity plan document that governs many grants from a notice that creates one |
| never alone | • a share-count or price-shaped number<br>• a company or organisation name on its own — §4.9 ‘A university name alone should not create a group because Columbia can appear as an authoring school, course provider, target institution, employer, research venue, or merely a cited organization.’<br>• the word ‘equity’, which appears in accounting, in diversity policy and in mortgages |

**Work types** — `grant notice`, `equity plan document`, `vesting statement`, `exercise notice`, `tax election filing`, `cap-table letter`, `broker account confirmation`, `grant summary portal export`

**Grouping reasons** — one grant and every document that governs or settles it; one employer's grants across years

**Template** — `employer → grant identifier → equity document type`  (time first: no)

> Grant identifier, not year, is the organising middle level: a grant is a long-lived object whose documents span years. §5.5 ‘The recommendation should follow the practical rule that a parent dimension should provide the context required to understand the child.’

**Collides with**

| domain | separating signal | design cite |
|---|---|---|
| `fin.investment-brokerage` | A broker statement showing vested shares satisfies §3.11's Finance schema; the grant notice that produced them does not. The two are usually filed together by the owner and belong to different domains. | §3.11 ‘One file may hold facts from more than one domain without losing information. An academic abstract submitted as part of a university application can retain project = PVA/RDP and document type = abstract while also carrying purpose = university application and target university = UChicago.’ §3.15 ‘Finance, identity, medical, and legal material should be implemented first as safety domains, meaning the system detects and protects them before any cloud or automated placement decision is allowed.’ |
| `career.offer-and-negotiation` | An offer letter summarises a grant it does not create. | — |
| `career.exit-and-offboarding` | Leaving triggers exercise windows and forfeiture notices that are simultaneously equity documents and exit documents. | — |

---

## `career.compensation-record` — In-employment compensation records

Letters and statements that change or state pay during an employment, as distinct from the offer that started it.

| | |
|---|---|
| **provenance** | `proposal` |
| **design cite** | _none — nothing in the design speaks to this domain_ |
| **sensitivity** | `potentially_sensitive` — §2.9's phrase ‘potentially sensitive’. These documents state the owner's pay. No handling class is assigned here. |

**Schema** — the fields this domain, and only this domain, legitimises.

| field | type | example | ceiling | why |
|---|---|---|---|---|
| `employer` | string | Unilever | `validated` | The issuing employer, on letterhead beside compensation language. |
| `compensation_cycle` | string | 2026 merit review | `validated` | Cycle names appear beside review language; they are the link between a review and the money it produced. |
| `effective_date` | date | 2026-04-01 | `direct` | A labeled effective-from line. |
| `compensation_component` | enum-like | annual bonus | `validated` | Same closed component vocabulary as the offer domain, which is why the two collide. |
| `change_reason` | enum-like | promotion | `llm_supported` | The reason is prose (‘in recognition of your promotion to…’) and is the field a summary would most readily invent. |
| `currency` | string | EUR | `direct` | A labeled currency indicator. |
| `statement_type` | enum-like | total reward statement | `validated` | Merit letters, bonus letters, band documents and total-reward statements are structurally distinct. |

**Recognition**

| kind | entries |
|---|---|
| deterministic (pattern **plus** corroborating context) | • compensation language ‘your new base salary’ \| ‘merit increase’ \| ‘bonus award’ \| ‘effective from’ co-occurring with a labeled employer letterhead<br>• a total-reward statement whose labeled sections carry ‘base’, ‘bonus’ and ‘benefits’ together |
| needs the LLM | • a manager's email confirming a raise with no formal letter<br>• separating an individual award letter from a company-wide policy circular that quotes the same figures |
| never alone | • a currency-shaped amount on its own<br>• a company or organisation name on its own — §4.9 ‘A university name alone should not create a group because Columbia can appear as an authoring school, course provider, target institution, employer, research venue, or merely a cited organization.’<br>• a labeled effective date, which appears on contracts, benefits and visas alike |

**Work types** — `merit increase letter`, `bonus award letter`, `total reward statement`, `salary band document`, `promotion pay letter`, `market adjustment letter`, `compensation policy circular`

**Grouping reasons** — one employer across one compensation cycle; one employment's compensation history in sequence

**Template** — `employer → compensation cycle`  (time first: no)

> Employer then cycle. §5.5 ‘The recommendation should follow the practical rule that a parent dimension should provide the context required to understand the child.’ §5.5 ‘For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders.’

**Collides with**

| domain | separating signal | design cite |
|---|---|---|
| `career.offer-and-negotiation` | Identical compensation vocabulary. The separator is that an offer carries a start date and a role being entered, while a comp record carries an effective date inside a role already held. | — |
| `career.performance-review` | A merit letter is the financial output of a review cycle and shares its cycle name. The review is an assessment; the letter is a decision. | — |
| `career.payroll` | Pay agreed versus pay made; see the payroll entry. | — |

---

## `career.performance-review` — Performance review

The periodic assessment of one employee's work, from every side that contributes to it.

| | |
|---|---|
| **provenance** | `proposal` |
| **design cite** | _none — nothing in the design speaks to this domain_ |
| **sensitivity** | `potentially_sensitive` — §2.9's phrase ‘potentially sensitive’. Reviews carry candid assessments, and in a manager's corpus they are assessments of named third parties. No handling class is assigned here. |

**Schema** — the fields this domain, and only this domain, legitimises.

| field | type | example | ceiling | why |
|---|---|---|---|---|
| `employer` | string | Atlassian | `validated` | The employing organisation, from form headers and system exports. |
| `review_cycle` | string | H2 2026 | `validated` | Cycle names are half-year or quarter-shaped values that only mean a review beside review language. |
| `review_document_type` | enum-like | self-assessment | `validated` | Self-assessment, manager review, peer feedback, calibration note and improvement plan are structurally distinct. |
| `subject_of_review` | string | the corpus owner | `llm_supported` | A manager's corpus contains reviews of other people in the identical form. §3.8's role separation is the only defence — §3.8 ‘A consulting document may mention the author’s firm and the client organization. A finance document may mention an account holder and an issuing bank. The agent should model these as distinct facets, such as authored_by and target_school, or our_firm and client.’ |
| `reviewer` | string | P. Nakamura | `llm_supported` | Named in prose or in a system export field. |
| `competency_area` | enum-like | technical judgement | `validated` | Competency frameworks are enumerated headings inside the form. |
| `outcome_statement` | string | exceeds expectations | `llm_supported` | Ratings are stated in the employer's own vocabulary, which varies per employer and must not be normalised across them. |

**Recognition**

| kind | entries |
|---|---|
| deterministic (pattern **plus** corroborating context) | • review language ‘self-assessment’ \| ‘performance review’ \| ‘goals for the next period’ \| ‘calibration’ \| ‘development areas’ co-occurring with a review-cycle value<br>• a review form export whose labeled sections carry ‘objectives’, ‘competencies’ and ‘manager comments’ together |
| needs the LLM | • free-form manager notes that assess someone without any form structure<br>• deciding whether an improvement plan is a review artifact or the opening of an exit process |
| never alone | • the word ‘review’ — code review, literature review and product review all produce it<br>• a person's name on its own; it identifies an author, not a domain<br>• a company or organisation name on its own — §4.9 ‘A university name alone should not create a group because Columbia can appear as an authoring school, course provider, target institution, employer, research venue, or merely a cited organization.’ |

**Work types** — `self-assessment`, `manager review`, `peer feedback`, `upward feedback`, `goal or OKR document`, `calibration note`, `performance improvement plan`, `one-to-one notes`

**Grouping reasons** — one employee, one cycle, every contributing document; one employment's review history in sequence

**Template** — `employer → subject of review → review cycle`  (time first: no)

> Subject sits above cycle, because a manager's corpus holds reviews of many people in one cycle and mixing them is the failure that matters. §3.8 ‘It should avoid using authorship or creator identity as a destination dimension. A folder should not become a collection point for everything produced by the same person or organization.’ forbids collecting by reviewer instead.

**Collides with**

| domain | separating signal | design cite |
|---|---|---|
| `career.employer-interview-scorecard` | Both are structured assessments of a named person against a competency rubric, and both are written by the owner about someone else. Only the scorecard attaches to a requisition rather than to an employment. | §3.8 ‘A consulting document may mention the author’s firm and the client organization. A finance document may mention an account holder and an issuing bank. The agent should model these as distinct facets, such as authored_by and target_school, or our_firm and client.’ |
| `career.promotion-packet` | A promotion packet is assembled largely out of review documents. The packet's membership must not rewrite the reviews' own cycle facts. | §3.9 ‘A university application packet can contain an identification document, transcript, resume, certificate, and academic abstract. The documents are content-incoherent but purpose-coherent.’ |
| `career.layoff-and-severance` | An improvement plan sits at the boundary and is read differently depending on what followed it. | — |

---

## `career.promotion-packet` — Promotion packet

A purpose-defined case for advancement, assembled from documents that individually belong to other domains.

| | |
|---|---|
| **provenance** | `proposal` |
| **design cite** | _none — nothing in the design speaks to this domain_ |
| **sensitivity** | `potentially_sensitive` — §2.9's phrase ‘potentially sensitive’. Packets quote review content and peer statements about named people. No handling class is assigned here. |

**Schema** — the fields this domain, and only this domain, legitimises.

| field | type | example | ceiling | why |
|---|---|---|---|---|
| `employer` | string | Google | `validated` | The employing organisation, from packet framing. |
| `promotion_cycle` | string | 2026 autumn promo | `validated` | A cycle value beside promotion language; the same cycle name also names the review it draws on. |
| `current_level` | string | L4 | `validated` | Level codes are employer-specific patterns that mean nothing without promotion language beside them — the same shape as §3.5 ‘For example, BUSIB 4300 becomes a course fact only when the engine finds a course-code pattern together with academic context such as “syllabus,” “lecture,” “credits,” “instructor,” or “semester.”’ |
| `target_level` | string | L5 | `validated` | Same recognition, opposite field; the pair is what makes the packet a promotion case. |
| `packet_document_type` | enum-like | sponsor statement | `validated` | Case document, artifact index, sponsor statement and committee outcome are structurally distinct. |
| `sponsor` | string | the owner's skip-level manager | `llm_supported` | Named in prose. |
| `purpose` | string | promotion case | `llm_supported` | The field that holds heterogeneous evidence together — §3.9 ‘Purpose must be a first-class facet. Topic answers what a file is about, while purpose answers what the file was for.’ This packet is the career analogue of §3.9 ‘A university application packet can contain an identification document, transcript, resume, certificate, and academic abstract. The documents are content-incoherent but purpose-coherent.’ |

**Recognition**

| kind | entries |
|---|---|
| deterministic (pattern **plus** corroborating context) | • promotion language ‘promotion packet’ \| ‘case for promotion’ \| ‘promo committee’ \| ‘scope at the next level’ co-occurring with a level pattern<br>• a level-code pattern appearing twice in one document beside ‘current’ and ‘proposed’ or ‘target’ |
| needs the LLM | • a set of unrelated project documents whose only shared signal is that they were gathered as evidence<br>• a case narrative that never states a level |
| never alone | • a level code such as ‘L5’ or ‘Band 7’ on its own — it is a bare pattern in exactly the way §3.5 forbids<br>• a company or organisation name on its own — §4.9 ‘A university name alone should not create a group because Columbia can appear as an authoring school, course provider, target institution, employer, research venue, or merely a cited organization.’<br>• the word ‘promotion’, which is also marketing vocabulary |

**Work types** — `promotion case document`, `artifact index`, `sponsor statement`, `peer support letter`, `scope comparison`, `committee outcome letter`, `evidence appendix`

**Grouping reasons** — one packet, purpose-coherent across heterogeneous evidence; one employer's promotion attempts in sequence

**Template** — `employer → promotion cycle`  (time first: no)

> Kept shallow deliberately: the packet's members mostly live in other domains and are referenced, not moved. §6.9 ‘The user’s frozen tree should therefore include a policy for shared material: a shared branch, a primary-home convention, a reference or alias convention, or mandatory review.’

**Collides with**

| domain | separating signal | design cite |
|---|---|---|
| `career.performance-review` | The packet consumes reviews without owning them; see the review entry. | §6.9 ‘The user’s frozen tree should therefore include a policy for shared material: a shared branch, a primary-home convention, a reference or alias convention, or mandatory review.’ |
| `career.portfolio` | An artifact index for a promotion and a portfolio for a job search are the same act of assembling proof for different audiences. | — |
| `career.job-application` | Both are purpose-defined packets of heterogeneous documents. One targets an outside employer, the other the current one, and a resume can sit in both. | §3.9 ‘A university application packet can contain an identification document, transcript, resume, certificate, and academic abstract. The documents are content-incoherent but purpose-coherent.’ §6.9 ‘A transcript may be part of several application packets; a resume may support multiple recruiting processes; a research abstract may belong to a research project and be attached to a university application.’ |

---

## `career.employment-verification` — Employment and income verification

Letters an employer issues to a third party attesting that the owner works there and on what terms.

| | |
|---|---|
| **provenance** | `proposal` |
| **design cite** | _none — nothing in the design speaks to this domain_ |
| **sensitivity** | `potentially_sensitive` — §2.9's phrase ‘potentially sensitive’. These letters attach the owner's income and address to a named third party. No handling class is assigned here. |

**Schema** — the fields this domain, and only this domain, legitimises.

| field | type | example | ceiling | why |
|---|---|---|---|---|
| `employer` | string | BNP Paribas | `validated` | The attesting employer, on letterhead beside verification language. |
| `verification_purpose` | enum-like | tenancy reference | `llm_supported` | Purpose is stated in the letter's opening prose and is the whole reason the document exists — §3.9 ‘Purpose must be a first-class facet. Topic answers what a file is about, while purpose answers what the file was for.’ |
| `requesting_party` | string | Foxtons Lettings | `validated` | A third organisation named as addressee — a role distinct from both employer and owner. |
| `issue_date` | date | 2026-05-20 | `direct` | The letter's labeled date. |
| `verified_role_title` | string | Vice President | `direct` | A labeled position line inside the attestation. |
| `verified_period` | string | since 2023-06-01 | `direct` | A labeled service-dates line. |
| `states_income` | boolean | true | `direct` | Whether the letter discloses pay. A privacy-relevant field, because the same letter type exists with and without figures. |

**Recognition**

| kind | entries |
|---|---|
| deterministic (pattern **plus** corroborating context) | • verification language ‘this letter confirms’ \| ‘is currently employed’ \| ‘to whom it may concern’ \| ‘annual gross salary of’ co-occurring with an employer letterhead and a named addressee<br>• a labeled service-dates line co-occurring with a labeled position line |
| needs the LLM | • an informal manager email used as a verification<br>• distinguishing a verification letter from a reference letter when both are addressed ‘to whom it may concern’ |
| never alone | • the phrase ‘to whom it may concern’<br>• a company or organisation name on its own — §4.9 ‘A university name alone should not create a group because Columbia can appear as an authoring school, course provider, target institution, employer, research venue, or merely a cited organization.’<br>• employer letterhead |

**Work types** — `employment verification letter`, `income verification letter`, `service certificate`, `visa support letter`, `mortgage employer reference`, `verification request correspondence`

**Grouping reasons** — one verification and the application it was produced for

**Template** — `employer → verification purpose`  (time first: no)

> Purpose is the second level because the same letter is reissued for different recipients. §3.9 ‘Purpose must be a first-class facet. Topic answers what a file is about, while purpose answers what the file was for.’

**Collides with**

| domain | separating signal | design cite |
|---|---|---|
| `career.reference-and-recommendation` | Both are letters about the owner addressed to a third party. A verification states facts an HR system holds; a reference states an opinion a person holds. | §3.8 ‘A consulting document may mention the author’s firm and the client organization. A finance document may mention an account holder and an issuing bank. The agent should model these as distinct facets, such as authored_by and target_school, or our_firm and client.’ |
| `career.work-authorization` | Verification letters produced for immigration are filed as immigration evidence. | — |
| `career.payroll` | An income verification restates payroll figures without being a payroll record. | — |

---

## `career.sabbatical-and-leave` — Leave, sabbatical and accommodation

Records of an authorised absence from work, and of adjustments made to how work is performed.

| | |
|---|---|
| **provenance** | `proposal` |
| **design cite** | _none — nothing in the design speaks to this domain_ |
| **sensitivity** | `potentially_sensitive` — §2.9's phrase ‘potentially sensitive’. Leave records routinely carry medical and family circumstances. No handling class is assigned here. |

**Schema** — the fields this domain, and only this domain, legitimises.

| field | type | example | ceiling | why |
|---|---|---|---|---|
| `employer` | string | NHS Trust | `validated` | The employing organisation, from form headers. |
| `leave_type` | enum-like | parental leave | `validated` | A closed, jurisdiction-flavoured vocabulary recognisable beside leave language. |
| `leave_start` | date | 2026-11-02 | `direct` | A labeled leave-from field. |
| `leave_end` | date | 2027-05-01 | `direct` | A labeled leave-to or expected-return field. |
| `approval_status` | enum-like | approved | `llm_supported` | Stated in correspondence rather than as a field. |
| `return_to_work_date` | date | 2027-05-04 | `direct` | A labeled return date, distinct from the leave end. |
| `carries_medical_documentation` | boolean | true | `direct` | Whether a certificate or occupational-health report is attached. A privacy-relevant field, not a judgement about the leave. |

**Recognition**

| kind | entries |
|---|---|
| deterministic (pattern **plus** corroborating context) | • leave language ‘leave of absence’ \| ‘sabbatical’ \| ‘parental leave’ \| ‘return to work’ \| ‘accommodation request’ co-occurring with a labeled employer field<br>• a labeled leave-from field co-occurring with a labeled leave-to or expected-return field |
| needs the LLM | • correspondence negotiating an adjustment with no form and no dates<br>• deciding whether a fit note belongs to an employment record or to a medical record |
| never alone | • a date range<br>• a company or organisation name on its own — §4.9 ‘A university name alone should not create a group because Columbia can appear as an authoring school, course provider, target institution, employer, research venue, or merely a cited organization.’<br>• the word ‘leave’, which is ordinary English |

**Work types** — `leave request form`, `leave approval letter`, `sabbatical proposal`, `return-to-work plan`, `fit note or medical certificate`, `occupational health report`, `accommodation agreement`, `career-break correspondence`

**Grouping reasons** — one leave and every document about it; one employment's absence history

**Template** — `employer → leave type`  (time first: no)

> Two levels only: leave records are few and episodic. §5.8 ‘One branch may require four levels, while another should remain flat.’

**Collides with**

| domain | separating signal | design cite |
|---|---|---|
| `med.medical-certification-letter` | Fit notes and occupational-health reports are medical documents filed for an employment reason, and §3.15 makes medical a safety domain. | §3.15 ‘Finance, identity, medical, and legal material should be implemented first as safety domains, meaning the system detects and protects them before any cloud or automated placement decision is allowed.’ |
| `career.benefits-enrollment` | Leave triggers benefit continuation elections that look like ordinary enrolment forms. | — |
| `career.exit-and-offboarding` | A career break and a resignation produce overlapping correspondence. | — |

---

## `career.layoff-and-severance` — Layoff, termination and severance

Documents of an involuntary end to employment and the settlement that accompanies it.

| | |
|---|---|
| **provenance** | `proposal` |
| **design cite** | _none — nothing in the design speaks to this domain_ |
| **sensitivity** | `potentially_sensitive` — §2.9's phrase ‘potentially sensitive’, and §4.9 ‘Rare but sensitive files such as passports, visas, and legal documents may be surfaced as protected records even when they do not meet a normal group-size threshold.’ names legal documents among the material that may be surfaced as protected. No handling class is assigned here. |

**Schema** — the fields this domain, and only this domain, legitimises.

| field | type | example | ceiling | why |
|---|---|---|---|---|
| `employer` | string | Meta Platforms | `validated` | The terminating employer, in the notice's parties or letterhead position. |
| `separation_type` | enum-like | redundancy | `validated` | A closed vocabulary — redundancy, reduction in force, dismissal, non-renewal, mutual termination — beside separation language. |
| `notice_date` | date | 2026-07-08 | `direct` | A labeled notice-date line. |
| `separation_date` | date | 2026-09-30 | `direct` | A labeled last-day line, routinely months after the notice date; conflating the two would misstate the record. |
| `severance_component` | enum-like | notice pay in lieu | `validated` | Components appear as labeled lines in a settlement schedule. |
| `release_status` | enum-like | signed | `llm_supported` | Whether a release of claims was executed is visible only from signature and correspondence. |
| `consultation_reference` | string | collective consultation 2026-07 | `possible` | Group processes are referenced in prose; a reference in one letter must not create a group fact for other files. |

**Recognition**

| kind | entries |
|---|---|
| deterministic (pattern **plus** corroborating context) | • separation language ‘your role is at risk’ \| ‘redundancy’ \| ‘reduction in force’ \| ‘settlement agreement’ \| ‘release of claims’ \| ‘termination of employment’ co-occurring with an employer letterhead<br>• a labeled last-day field co-occurring with a labeled notice-date field |
| needs the LLM | • a settlement negotiated through solicitors where the operative terms sit in correspondence<br>• distinguishing a genuine mutual termination from a redundancy documented as one |
| never alone | • the word ‘termination’, which appears in every contract's clause headings<br>• a company or organisation name on its own — §4.9 ‘A university name alone should not create a group because Columbia can appear as an authoring school, course provider, target institution, employer, research venue, or merely a cited organization.’<br>• a currency-shaped amount on its own |

**Work types** — `at-risk notice`, `redundancy consultation letter`, `termination letter`, `settlement or severance agreement`, `release of claims`, `outplacement service enrolment`, `final pay statement`, `solicitor correspondence`, `reference agreement`

**Grouping reasons** — one separation and every document about it; one employer's collective process across affected documents

**Template** — `employer → separation type`  (time first: no)

> Employer first and shallow. §5.8 ‘One branch may require four levels, while another should remain flat.’ A separation produces a small dense set, not a deep tree.

**Collides with**

| domain | separating signal | design cite |
|---|---|---|
| `career.exit-and-offboarding` | Involuntary and voluntary endings produce overlapping paperwork — final pay, asset return, benefits continuation — and only the notice and settlement documents distinguish them. Filing them together loses whether the owner left or was let go. | — |
| `career.restrictive-covenant` | Settlement agreements restate and often extend covenants; the settlement is not the covenant's origin. | — |
| `pers.personal-legal` | A negotiated settlement is a legal matter, and §3.15 makes legal a safety domain. | §3.15 ‘Finance, identity, medical, and legal material should be implemented first as safety domains, meaning the system detects and protects them before any cloud or automated placement decision is allowed.’ §4.9 ‘Rare but sensitive files such as passports, visas, and legal documents may be surfaced as protected records even when they do not meet a normal group-size threshold.’ |

---

## `career.exit-and-offboarding` — Resignation and offboarding

The voluntary end of an employment and the administrative closure that follows it.

| | |
|---|---|
| **provenance** | `proposal` |
| **design cite** | _none — nothing in the design speaks to this domain_ |
| **sensitivity** | `potentially_sensitive` — §2.9's phrase ‘potentially sensitive’, and §8.4 ‘The product processes a highly personal corpus that can include identity documents, account statements, tax records, medical information, legal records, credentials, private correspondence, GPS metadata, employment materials, and educational records.’ No handling class is assigned here. |

**Schema** — the fields this domain, and only this domain, legitimises.

| field | type | example | ceiling | why |
|---|---|---|---|---|
| `employer` | string | Shopify | `validated` | The employer being left. |
| `resignation_date` | date | 2026-06-02 | `direct` | The labeled date on the resignation letter. |
| `last_working_day` | date | 2026-07-31 | `direct` | A labeled final-day line, distinct from the resignation date. |
| `exit_document_type` | enum-like | exit interview | `validated` | Resignation letter, acceptance, exit interview, asset return and handover note are structurally distinct. |
| `separation_reason` | string | new role elsewhere | `llm_supported` | Stated in prose where stated at all, and the field most likely to be over-read from a polite letter. |
| `asset_return_item` | string | laptop | `validated` | Asset lists are enumerated in a labeled return form. |
| `benefits_continuation` | enum-like | elected | `llm_supported` | Continuation elections are described in correspondence. |

**Recognition**

| kind | entries |
|---|---|
| deterministic (pattern **plus** corroborating context) | • resignation language ‘I am resigning’ \| ‘my last day will be’ \| ‘notice period’ \| ‘exit interview’ \| ‘return of company property’ co-occurring with an employer name<br>• a labeled final-day field co-occurring with resignation or offboarding language |
| needs the LLM | • a handover document with no framing that identifies it as an exit artifact<br>• correspondence where a resignation is agreed verbally and only referenced afterwards |
| never alone | • the word ‘exit’ or ‘handover’ in a filename<br>• a company or organisation name on its own — §4.9 ‘A university name alone should not create a group because Columbia can appear as an authoring school, course provider, target institution, employer, research venue, or merely a cited organization.’<br>• a labeled last day, which also appears on fixed-term contracts and secondments |

**Work types** — `resignation letter`, `acceptance of resignation`, `exit interview form`, `handover document`, `asset return form`, `final pay statement`, `benefits continuation election`, `leaver certificate`, `alumni access details`

**Grouping reasons** — one departure and every document about it; one employment's whole arc from contract to leaver certificate

**Template** — `employer → exit document type`  (time first: no)

> Employer first, shallow. §5.8 ‘One branch may require four levels, while another should remain flat.’

**Collides with**

| domain | separating signal | design cite |
|---|---|---|
| `career.layoff-and-severance` | See the severance entry; the separator is who ended it. | — |
| `career.equity-compensation` | Exercise-window and forfeiture notices are equity documents issued by the exit. | — |
| `career.retirement-records` | Retiring is an exit that also opens a pension record. | — |

---

## `career.retirement-records` — Retirement and pension records

Long-lived records of retirement savings attached to one or more past employments.

| | |
|---|---|
| **provenance** | `proposal` |
| **design cite** | _none — nothing in the design speaks to this domain_ |
| **sensitivity** | `potentially_sensitive` — §2.9's phrase ‘potentially sensitive’. Statements carry account balances, plan numbers and beneficiary details. No handling class is assigned here. |

**Schema** — the fields this domain, and only this domain, legitimises.

| field | type | example | ceiling | why |
|---|---|---|---|---|
| `plan_administrator` | string | Fidelity | `validated` | The administrator is a different organisation from the sponsoring employer — the account-holder and issuing-institution split §3.8 ‘A consulting document may mention the author’s firm and the client organization. A finance document may mention an account holder and an issuing bank. The agent should model these as distinct facets, such as authored_by and target_school, or our_firm and client.’ |
| `employer_sponsor` | string | IBM | `validated` | The employment the plan came from, often an employer the owner left years earlier. |
| `plan_name` | string | IBM 401(k) Plus Plan | `direct` | A labeled plan-name field. |
| `plan_type` | enum-like | defined contribution | `validated` | A closed vocabulary recognisable beside pension language. |
| `statement_period` | string | 2026 Q2 | `direct` | A labeled statement-period field. |
| `vesting_status` | enum-like | fully vested | `llm_supported` | Stated in summary prose on the statement. |
| `retirement_document_type` | enum-like | rollover confirmation | `validated` | Statements, elections, rollovers, beneficiary forms and annuity quotes are structurally distinct. |

**Recognition**

| kind | entries |
|---|---|
| deterministic (pattern **plus** corroborating context) | • pension language ‘retirement plan’ \| ‘pension scheme’ \| ‘vested balance’ \| ‘annual benefit statement’ \| ‘rollover’ co-occurring with a labeled plan-name field<br>• a labeled plan-number field co-occurring with a labeled statement period |
| needs the LLM | • a legacy scheme statement from a merged provider whose employer link is stated only in prose history<br>• deciding whether a beneficiary form is a retirement record or an estate document |
| never alone | • an administrator name — a fund manager appears on unrelated investment material<br>• a company or organisation name on its own — §4.9 ‘A university name alone should not create a group because Columbia can appear as an authoring school, course provider, target institution, employer, research venue, or merely a cited organization.’<br>• a currency-shaped amount on its own |

**Work types** — `annual benefit statement`, `contribution election`, `rollover confirmation`, `beneficiary nomination`, `annuity quotation`, `scheme booklet`, `transfer value statement`, `state pension forecast`

**Grouping reasons** — one plan across its statement series; all plans arising from one employer

**Template** — `employer sponsor → plan name → statement period`  (time first: no)

> Sponsor above plan above period: a person accumulates several plans across employers and the sponsor is what makes an old plan identifiable. §5.5 ‘For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders.’

**Collides with**

| domain | separating signal | design cite |
|---|---|---|
| `fin.retirement-account` | A pension statement satisfies §3.11's Finance schema exactly, and §3.15 makes Finance a safety domain. Its only career signal is the employer sponsor. | §3.11 ‘One file may hold facts from more than one domain without losing information. An academic abstract submitted as part of a university application can retain project = PVA/RDP and document type = abstract while also carrying purpose = university application and target university = UChicago.’ §3.15 ‘Finance, identity, medical, and legal material should be implemented first as safety domains, meaning the system detects and protects them before any cloud or automated placement decision is allowed.’ |
| `career.benefits-enrollment` | Retirement plans are elected through the benefits process and then leave it behind. | — |
| `career.equity-compensation` | Both are long-lived holdings arising from employment and settled through a broker. | — |

---

## `career.professional-license` — Professional licence

Authority granted by a jurisdiction to practise a regulated profession, and the filings that keep it current.

| | |
|---|---|
| **provenance** | `proposal` |
| **design cite** | _none — nothing in the design speaks to this domain_ |
| **sensitivity** | `potentially_sensitive` — §2.9's phrase ‘potentially sensitive’. A licence carries a government-issued identifier and, on many certificates, a registered address. No handling class is assigned here. |

**Schema** — the fields this domain, and only this domain, legitimises.

| field | type | example | ceiling | why |
|---|---|---|---|---|
| `licensing_body` | string | California Board of Accountancy | `validated` | A regulator name from a gazetteer, beside licensure language. A regulator is not an employer and not an issuer of certificates — a third organisation role. |
| `licence_type` | enum-like | Certified Public Accountant | `validated` | A closed, jurisdiction-specific vocabulary recognisable beside licensure language. |
| `licence_number` | string | CPA-118422 | `direct` | A labeled licence-number field on the certificate itself. |
| `jurisdiction` | string | California | `direct` | A labeled jurisdiction field. Jurisdiction is what separates a licence from a certification, and a person may hold the same licence in several. |
| `issue_date` | date | 2024-01-18 | `direct` | A labeled issue-date field. |
| `expiry_date` | date | 2027-01-31 | `direct` | A labeled expiry or renewal-due field. |
| `licence_status` | enum-like | active | `llm_supported` | Status is stated in renewal correspondence and verification pages rather than on the certificate. |

**Recognition**

| kind | entries |
|---|---|
| deterministic (pattern **plus** corroborating context) | • licensure language ‘licensed to practise’ \| ‘board of’ \| ‘licence number’ \| ‘renewal’ \| ‘registrant’ co-occurring with a jurisdiction field<br>• a licence-number pattern co-occurring with a regulator name from the gazetteer |
| needs the LLM | • a foreign regulator's certificate whose vocabulary is unrecognised<br>• distinguishing a licence from a membership certificate issued by the same professional body |
| never alone | • an identifier pattern on its own<br>• a regulator's name on its own — regulators publish guidance, newsletters and enforcement notices too<br>• a four-digit year on its own — §3.10 ‘file names and documents frequently contain numbers that look like years but are course identifiers, version numbers, build numbers, ZIP codes, or other unrelated values’ |

**Work types** — `licence certificate`, `renewal notice`, `renewal receipt`, `verification letter`, `licence application`, `disciplinary correspondence`, `reciprocity or endorsement filing`, `wall certificate scan`

**Grouping reasons** — one licence across its renewal history; one jurisdiction's filings for one profession

**Template** — `licence type → jurisdiction`  (time first: no)

> Type above jurisdiction, because a professional holds one profession in several places rather than several professions in one. §5.5 ‘The recommendation should follow the practical rule that a parent dimension should provide the context required to understand the child.’

**Collides with**

| domain | separating signal | design cite |
|---|---|---|
| `career.certification` | Both produce a certificate with an identifier and an expiry. A licence carries a jurisdiction and a regulator; a certification carries a vendor or association and no jurisdiction. Filing them together makes it impossible to answer what the owner is legally permitted to do. | — |
| `career.continuing-education` | Credit records exist to keep a licence alive and cite its number, but they are not licence documents. | — |
| `pers.identity-document` | A licence number is a government-issued identifier, and §3.15 makes identity a safety domain. | §3.15 ‘Finance, identity, medical, and legal material should be implemented first as safety domains, meaning the system detects and protects them before any cloud or automated placement decision is allowed.’ |
| `law.bar-admission-cle` | The law slice authors admission and CLE for one profession. This entry is the profession-neutral form; where a corpus is a lawyer's, both activate and the more specific one should win. | — |

---

## `career.certification` — Professional certification

Credentials granted by a vendor, association or examining body on the strength of an examination or assessment.

| | |
|---|---|
| **provenance** | `proposal` |
| **design cite** | _none — nothing in the design speaks to this domain_ |
| **sensitivity** | `none` — A certificate is a document the holder is expected to show; its verification code is designed to be shared. |

**Schema** — the fields this domain, and only this domain, legitimises.

| field | type | example | ceiling | why |
|---|---|---|---|---|
| `issuing_body` | string | Amazon Web Services | `validated` | A certifying organisation from a gazetteer, beside certification language. |
| `certification_name` | string | Solutions Architect – Associate | `direct` | Stated as the certificate's own title. |
| `credential_identifier` | string | AWS-04-1188223 | `direct` | A labeled credential-id or verification-code field. |
| `issue_date` | date | 2026-02-04 | `direct` | A labeled issue-date field. |
| `expiry_date` | date | 2029-02-04 | `possible` | Many certifications never expire and many certificates state a recommended rather than binding renewal; the value must not be manufactured from a validity period described in marketing text. |
| `exam_or_version` | string | SAA-C03 | `direct` | A labeled exam-code field where the body uses one. |
| `certification_document_type` | enum-like | score report | `validated` | Certificates, score reports, digital badges and renewal confirmations are structurally distinct. |

**Recognition**

| kind | entries |
|---|---|
| deterministic (pattern **plus** corroborating context) | • certification language ‘has successfully’ \| ‘is certified’ \| ‘credential id’ \| ‘verify at’ \| ‘exam code’ co-occurring with an issuing-body name<br>• a credential-identifier pattern co-occurring with a verification URL or an issuing-body name |
| needs the LLM | • a course completion certificate that does not say whether an assessment was involved<br>• separating a certificate of attendance from a certificate of competence when both use the same template |
| never alone | • a certificate-shaped document — attendance, training, insurance and share certificates share the layout<br>• a company or organisation name on its own — §4.9 ‘A university name alone should not create a group because Columbia can appear as an authoring school, course provider, target institution, employer, research venue, or merely a cited organization.’<br>• the word ‘certificate’ in a filename |

**Work types** — `certificate`, `score report`, `digital badge export`, `renewal confirmation`, `exam booking confirmation`, `candidate handbook`, `training completion record`

**Grouping reasons** — one certification across its renewals; one issuing body's credentials held by the owner

**Template** — `issuing body → certification name`  (time first: no)

> Issuing body first, because certification names collide across bodies. §5.5 ‘The recommendation should follow the practical rule that a parent dimension should provide the context required to understand the child.’

**Collides with**

| domain | separating signal | design cite |
|---|---|---|
| `acad.course-enrollment` | A course completion certificate is produced by both domains and often by the same platform. Academic material carries §3.5's course context; a certification carries a credential identifier and an issuing body. | §3.5 ‘For example, BUSIB 4300 becomes a course fact only when the engine finds a course-code pattern together with academic context such as “syllabus,” “lecture,” “credits,” “instructor,” or “semester.”’ |
| `career.professional-license` | See the licence entry: jurisdiction is the separator. | — |
| `acad.credential-certificate` | Diplomas and academic certificates share this domain's entire document shape. The separator is the issuing body: an examining or vendor body confers a certification, an educational institution confers a credential. | — |

---

## `career.continuing-education` — Continuing professional education

Records of the education a professional must keep accumulating to remain in good standing.

| | |
|---|---|
| **provenance** | `proposal` |
| **design cite** | _none — nothing in the design speaks to this domain_ |
| **sensitivity** | `none` — Credit records state activities completed; where a transcript quotes a licence number the sensitivity belongs to the licence record, not to this one. |

**Schema** — the fields this domain, and only this domain, legitimises.

| field | type | example | ceiling | why |
|---|---|---|---|---|
| `accrediting_body` | string | State Bar of Texas | `validated` | The body that recognises the credit, beside credit language. Often a different organisation from the provider. |
| `provider` | string | Practising Law Institute | `validated` | The organisation that delivered the activity — the second organisation role on the same document. |
| `credit_type` | enum-like | CLE ethics | `validated` | Credit-type codes are a closed, profession-specific vocabulary. |
| `reporting_period` | string | 2026 compliance year | `direct` | A labeled reporting-period field on the transcript. |
| `activity_title` | string | Recent Developments in Data Privacy | `direct` | The activity's own title on the completion record. |
| `linked_licence` | string | CPA-118422 | `possible` | Transcripts quote a licence number, but a quoted identifier is a reference, not a licence fact for this file. |
| `credit_record_type` | enum-like | compliance transcript | `validated` | Attendance records, completion certificates and compliance transcripts are structurally distinct. |

**Recognition**

| kind | entries |
|---|---|
| deterministic (pattern **plus** corroborating context) | • credit language ‘continuing professional’ \| ‘CPE’ \| ‘CLE’ \| ‘CME’ \| ‘credit hours’ \| ‘compliance period’ co-occurring with an accrediting-body name<br>• a credit-type code co-occurring with a labeled reporting-period field |
| needs the LLM | • an internal training record that may or may not carry accredited credit<br>• a conference agenda where only some sessions carried credit |
| never alone | • an acronym such as ‘CPE’ or ‘CME’ — §3.7 ‘It should use word-boundary matching rather than substring matching. Without this rule, names such as MIT can be found inside “submit,” and UNC can be found inside “uncertainty,” producing polished but completely false filing paths.’ applies to short acronyms most of all<br>• a company or organisation name on its own — §4.9 ‘A university name alone should not create a group because Columbia can appear as an authoring school, course provider, target institution, employer, research venue, or merely a cited organization.’<br>• a four-digit year on its own — §3.10 ‘file names and documents frequently contain numbers that look like years but are course identifiers, version numbers, build numbers, ZIP codes, or other unrelated values’ |

**Work types** — `completion certificate`, `compliance transcript`, `attendance record`, `credit claim submission`, `provider invoice`, `audit response`, `activity materials`

**Grouping reasons** — one reporting period's credits for one licence; one provider's activities across periods

**Template** — `linked licence → reporting period`  (time first: no)

> The licence gives the reporting period its meaning — §5.5 ‘The recommendation should follow the practical rule that a parent dimension should provide the context required to understand the child.’ Where no licence is linked the branch flattens to period alone.

**Collides with**

| domain | separating signal | design cite |
|---|---|---|
| `career.certification` | A completion certificate looks the same whether it carries accredited credit or not; only the credit type and reporting period distinguish them. | — |
| `career.conference-attendance` | A conference that carried credit produces both a credit record and an attendance record from one event. | §3.11 ‘One file may hold facts from more than one domain without losing information. An academic abstract submitted as part of a university application can retain project = PVA/RDP and document type = abstract while also carrying purpose = university application and target university = UChicago.’ |
| `acad.course-enrollment` | Continuing education is coursework in every respect except that it answers to a regulator rather than an institution. | §3.5 ‘For example, BUSIB 4300 becomes a course fact only when the engine finds a course-code pattern together with academic context such as “syllabus,” “lecture,” “credits,” “instructor,” or “semester.”’ |
| `acad.continuing-education` | A near-duplicate authored in the education slice. That entry reaches the material as learning; this one reaches it as a compliance obligation attached to a licence. They overlap and must be reconciled before the allow-list is frozen. | — |

---

## `career.professional-membership` — Professional membership

Standing in a professional body or association, and the dues and grades that maintain it.

| | |
|---|---|
| **provenance** | `proposal` |
| **design cite** | _none — nothing in the design speaks to this domain_ |
| **sensitivity** | `none` — Membership standing is ordinarily published in member directories; the member number is a lookup key rather than a government identifier. |

**Schema** — the fields this domain, and only this domain, legitimises.

| field | type | example | ceiling | why |
|---|---|---|---|---|
| `association` | string | Institution of Civil Engineers | `validated` | The body, from a gazetteer, beside membership language. |
| `membership_grade` | string | Chartered Member | `validated` | Grade vocabularies are closed per body and are the substance of the record. |
| `member_identifier` | string | ICE-442901 | `direct` | A labeled membership-number field. |
| `membership_year` | string | 2026 | `direct` | A labeled subscription-year field on the receipt or card. |
| `dues_status` | enum-like | paid | `llm_supported` | Stated in renewal correspondence. |
| `chapter_or_section` | string | London Region | `validated` | Sub-body names are meaningful only beside the parent association. |
| `membership_document_type` | enum-like | renewal receipt | `validated` | Cards, receipts, grade certificates and election letters are structurally distinct. |

**Recognition**

| kind | entries |
|---|---|
| deterministic (pattern **plus** corroborating context) | • membership language ‘membership’ \| ‘subscription’ \| ‘member number’ \| ‘annual dues’ \| ‘elected to the grade of’ co-occurring with an association name<br>• a member-identifier pattern co-occurring with an association name from the gazetteer |
| needs the LLM | • an association's newsletter that mentions the owner without evidencing membership<br>• distinguishing an honorary appointment from a paid membership |
| never alone | • an association name — bodies publish standards, journals and event material that mention no member<br>• an identifier pattern on its own<br>• a four-digit year on its own — §3.10 ‘file names and documents frequently contain numbers that look like years but are course identifiers, version numbers, build numbers, ZIP codes, or other unrelated values’ |

**Work types** — `membership card`, `dues receipt`, `renewal notice`, `grade election letter`, `membership application`, `chapter correspondence`, `member directory listing`, `code of conduct acknowledgement`

**Grouping reasons** — one association across its membership years; one grade application and its supporting evidence

**Template** — `association → membership year`  (time first: no)

> Association first — the year means nothing without it. §5.5 ‘The recommendation should follow the practical rule that a parent dimension should provide the context required to understand the child.’ §5.5 ‘For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders.’

**Collides with**

| domain | separating signal | design cite |
|---|---|---|
| `career.professional-license` | Some bodies both licence and admit to membership, issuing near-identical certificates for each. The licence carries a jurisdiction; the membership carries a grade. | — |
| `career.conference-attendance` | Association events produce material that belongs to both records. | §3.11 ‘One file may hold facts from more than one domain without losing information. An academic abstract submitted as part of a university application can retain project = PVA/RDP and document type = abstract while also carrying purpose = university application and target university = UChicago.’ |
| `pers.membership` | A near-duplicate authored in the personal slice. That entry covers memberships and subscriptions generally; this one is scoped to bodies that confer professional standing and grades. They overlap and must be reconciled before the allow-list is frozen. | — |

---

## `career.conference-attendance` — Conference and event attendance

Files produced by going to a professional event as a participant rather than a contributor.

| | |
|---|---|
| **provenance** | `proposal` |
| **design cite** | _none — nothing in the design speaks to this domain_ |
| **sensitivity** | `none` — Registrations and agendas carry no identifier, amount or third-party personal data beyond ordinary business contact details. |

**Schema** — the fields this domain, and only this domain, legitimises.

| field | type | example | ceiling | why |
|---|---|---|---|---|
| `event_name` | string | NeurIPS | `validated` | An event name from a gazetteer, beside event language. This is §3.11's Research ‘venue’ reached from the career side. |
| `event_edition` | string | 2026 | `validated` | The year only names an edition beside the event name; alone it is §3.10 ‘file names and documents frequently contain numbers that look like years but are course identifiers, version numbers, build numbers, ZIP codes, or other unrelated values’ |
| `event_location` | string | Vancouver | `validated` | A place name beside event language. It is also the trip's destination, which is why this domain collides with travel. |
| `registration_type` | enum-like | early-bird academic | `direct` | A labeled registration-category field. |
| `session` | string | Workshop on Efficient Inference | `direct` | Session titles are enumerated in the agenda. |
| `organiser` | string | Neural Information Processing Systems Foundation | `validated` | The organising body, distinct from the venue and from the owner's employer. |
| `attendance_document_type` | enum-like | registration confirmation | `validated` | Registrations, badges, agendas, receipts and session notes are structurally distinct. |

**Recognition**

| kind | entries |
|---|---|
| deterministic (pattern **plus** corroborating context) | • event language ‘registration’ \| ‘badge’ \| ‘agenda’ \| ‘keynote’ \| ‘exhibit hall’ \| ‘conference’ co-occurring with an event name and an edition value<br>• a labeled registration-category field co-occurring with an event name |
| needs the LLM | • handwritten or photographed session notes whose only event signal is the subject matter<br>• deciding whether the owner attended an event or merely collected its programme |
| never alone | • a place name — §3.7 ‘It should use word-boundary matching rather than substring matching. Without this rule, names such as MIT can be found inside “submit,” and UNC can be found inside “uncertainty,” producing polished but completely false filing paths.’<br>• a four-digit year on its own — §3.10 ‘file names and documents frequently contain numbers that look like years but are course identifiers, version numbers, build numbers, ZIP codes, or other unrelated values’<br>• a booking confirmation, which §7.3's Receipts and Confirmations template also claims |

**Work types** — `registration confirmation`, `badge or ticket`, `agenda or programme`, `session notes`, `proceedings download`, `expense receipt`, `attendee list`, `post-event summary`

**Grouping reasons** — one event edition and everything produced around it; one event series across editions

**Template** — `event name → event edition`  (time first: no)

> Event above edition. §5.5 ‘The recommendation should follow the practical rule that a parent dimension should provide the context required to understand the child.’ The user may reasonably reverse this to year-first if events are one-offs — §5.5 ‘The system recommends an order based on the domain template, but the user can reverse, remove, add, or flatten dimensions.’

**Collides with**

| domain | separating signal | design cite |
|---|---|---|
| `pers.travel-record` | A conference generates flights, hotels and receipts that are indistinguishable from any other trip's, and the trip and the event share dates and a location. Both readings are true. | §3.11 ‘One file may hold facts from more than one domain without losing information. An academic abstract submitted as part of a university application can retain project = PVA/RDP and document type = abstract while also carrying purpose = university application and target university = UChicago.’ |
| `res.research-project` | §3.11 gives Research a ‘venue’ field. A proceedings paper is a research artifact whose venue is this event; the event's badge is not. | §3.11 ‘One file may hold facts from more than one domain without losing information. An academic abstract submitted as part of a university application can retain project = PVA/RDP and document type = abstract while also carrying purpose = university application and target university = UChicago.’ |
| `career.speaking-engagement` | The same event produces attendance material and contribution material, and only the contribution material names the owner as a speaker. | §3.8 ‘A consulting document may mention the author’s firm and the client organization. A finance document may mention an account holder and an issuing bank. The agent should model these as distinct facets, such as authored_by and target_school, or our_firm and client.’ |

**Open question — unresolved, Joseph's call**

> §5.5 makes time-first the exception for capture-based media and subject-first the rule for record domains, but an event record is arguably both. Should a Conferences branch read event → year or year → event by default?

---

## `career.speaking-engagement` — Speaking and contribution

Files produced by contributing to a professional event — proposing, being accepted, presenting, being paid.

| | |
|---|---|
| **provenance** | `proposal` |
| **design cite** | _none — nothing in the design speaks to this domain_ |
| **sensitivity** | `none` — Contribution material is produced to be published; the honorarium paperwork is the exception and is small. |

**Schema** — the fields this domain, and only this domain, legitimises.

| field | type | example | ceiling | why |
|---|---|---|---|---|
| `event_name` | string | PyCon US | `validated` | Same gazetteer recognition as attendance, different role. |
| `event_edition` | string | 2026 | `validated` | Meaningful only beside the event name. |
| `talk_title` | string | What Import Actually Does | `direct` | The submission's or slide deck's own title. |
| `speaking_role` | enum-like | panellist | `validated` | A closed vocabulary — speaker, keynote, panellist, workshop lead, session chair — beside contribution language. |
| `submission_status` | enum-like | accepted | `llm_supported` | Stated in acceptance or rejection correspondence prose. |
| `agreement_type` | enum-like | speaker agreement | `validated` | Speaker agreements, release forms and honorarium paperwork are named documents. |
| `honorarium_arrangement` | string | travel covered, no fee | `llm_supported` | Described in prose in the invitation; the absence of a figure must not be read as an absence of an arrangement. |

**Recognition**

| kind | entries |
|---|---|
| deterministic (pattern **plus** corroborating context) | • contribution language ‘call for proposals’ \| ‘your talk has been accepted’ \| ‘speaker agreement’ \| ‘presenter’ \| ‘abstract submission’ co-occurring with an event name<br>• a slide deck whose title slide carries an event name together with the owner's name in a presenter position |
| needs the LLM | • a slide deck with no event branding whose only contribution signal is surrounding correspondence<br>• distinguishing an internal presentation from a conference talk on the same material |
| never alone | • a slide deck<br>• a person's name on its own; it identifies an author, not a domain<br>• an event name on its own, which attendance material carries identically |

**Work types** — `proposal or abstract submission`, `acceptance letter`, `speaker agreement`, `slide deck`, `speaker notes`, `recording or transcript`, `honorarium or expense claim`, `media release form`, `post-talk feedback`

**Grouping reasons** — one talk from proposal to recording; one event edition's contribution material

**Template** — `event name → event edition → talk title`  (time first: no)

> Talk title only makes sense inside its event edition. §5.5 ‘The recommendation should follow the practical rule that a parent dimension should provide the context required to understand the child.’

**Collides with**

| domain | separating signal | design cite |
|---|---|---|
| `career.conference-attendance` | Same event, opposite role; see the attendance entry. | §3.8 ‘A consulting document may mention the author’s firm and the client organization. A finance document may mention an account holder and an issuing bank. The agent should model these as distinct facets, such as authored_by and target_school, or our_firm and client.’ |
| `career.portfolio` | A recorded talk is a work sample as well as an engagement record. | §3.11 ‘One file may hold facts from more than one domain without losing information. An academic abstract submitted as part of a university application can retain project = PVA/RDP and document type = abstract while also carrying purpose = university application and target university = UChicago.’ |
| `res.research-project` | A conference talk on a research project is a research artifact at a venue and a career contribution at an event. | §3.11 ‘One file may hold facts from more than one domain without losing information. An academic abstract submitted as part of a university application can retain project = PVA/RDP and document type = abstract while also carrying purpose = university application and target university = UChicago.’ |

---

## `career.networking-and-referrals` — Networking and referrals

Records of professional relationships used to find work — outreach, introductions, referrals and the contact data behind them.

| | |
|---|---|
| **provenance** | `proposal` |
| **design cite** | _none — nothing in the design speaks to this domain_ |
| **sensitivity** | `potentially_sensitive` — §2.9's phrase ‘potentially sensitive’. These records are almost entirely third parties' names, employers and contact details. No handling class is assigned here. |

**Schema** — the fields this domain, and only this domain, legitimises.

| field | type | example | ceiling | why |
|---|---|---|---|---|
| `contact_person` | string | S. Adeyemi | `llm_supported` | A name in an outreach record. It must never become a folder level — §3.8 ‘It should avoid using authorship or creator identity as a destination dimension. A folder should not become a collection point for everything produced by the same person or organization.’ |
| `contact_organisation` | string | Klarna | `validated` | The organisation a contact sits in, which is what makes a referral useful; distinct from an employer of the owner. |
| `relationship_type` | string | former colleague | `llm_supported` | Stated in prose in the outreach itself. |
| `outreach_purpose` | enum-like | referral request | `llm_supported` | Purpose is the point of the record — §3.9 ‘Purpose must be a first-class facet. Topic answers what a file is about, while purpose answers what the file was for.’ — and is only ever prose. |
| `referral_target_employer` | string | Klarna | `validated` | The employer the referral is into, which links this record to an application. |
| `outreach_date` | date | 2026-01-22 | `direct` | A message's labeled sent date. |
| `contact_data_source` | enum-like | exported address book | `direct` | Whether the record came from a contacts export. §2.9 ‘Contact formats such as VCF should yield names, organizations, email addresses, phone numbers, and address-book metadata, but should normally be privacy-protected rather than used to create folder proposals.’ |

**Recognition**

| kind | entries |
|---|---|
| deterministic (pattern **plus** corroborating context) | • outreach language ‘I wanted to reach out’ \| ‘referral’ \| ‘introduction to’ \| ‘coffee chat’ \| ‘happy to refer you’ co-occurring with an organisation name<br>• a message whose labeled recipient sits at a gazetteer organisation and whose body carries referral language |
| needs the LLM | • a conversation that becomes a referral without ever using the word<br>• notes from a conversation that name neither person nor organisation |
| never alone | • a person's name on its own; it identifies an author, not a domain<br>• a contacts export — §2.9 ‘Contact formats such as VCF should yield names, organizations, email addresses, phone numbers, and address-book metadata, but should normally be privacy-protected rather than used to create folder proposals.’<br>• a company or organisation name on its own — §4.9 ‘A university name alone should not create a group because Columbia can appear as an authoring school, course provider, target institution, employer, research venue, or merely a cited organization.’ |

**Work types** — `outreach message`, `introduction thread`, `referral request`, `referral submission confirmation`, `coffee-chat notes`, `contact list`, `alumni directory export`, `informational-interview notes`

**Grouping reasons** — one referral from request to application; one search's outreach across contacts

**Template** — `search cycle → referral target employer`  (time first: no)

> Never by contact: §3.8 ‘It should avoid using authorship or creator identity as a destination dimension. A folder should not become a collection point for everything produced by the same person or organization.’ Target employer is the dimension that links outreach to the application it produced.

**Collides with**

| domain | separating signal | design cite |
|---|---|---|
| `career.job-application` | A referral confirmation names the employer, the role and a date and reads exactly like an application confirmation without being one. | §4.8 ‘that an application packet does not silently absorb a document with a conflicting target institution’ |
| `career.reference-and-recommendation` | A referral is a recommendation made informally before an application; a reference is one made formally after it. | §3.8 ‘A consulting document may mention the author’s firm and the client organization. A finance document may mention an account holder and an issuing bank. The agent should model these as distinct facets, such as authored_by and target_school, or our_firm and client.’ |
| `pers.correspondence` | §2.9 already rules that contact data is normally privacy-protected rather than used to create folder proposals, which constrains this domain more than any other in the slice. | §2.9 ‘Contact formats such as VCF should yield names, organizations, email addresses, phone numbers, and address-book metadata, but should normally be privacy-protected rather than used to create folder proposals.’ |

---

## `career.consulting-engagement` — Consulting engagement

A delivered piece of work for a client organisation, where the owner's firm and the client are separate parties on the same documents.

| | |
|---|---|
| **provenance** | `design` |
| **design cite** | §3.8 ‘A consulting document may mention the author’s firm and the client organization. A finance document may mention an account holder and an issuing bank. The agent should model these as distinct facets, such as authored_by and target_school, or our_firm and client.’ §5.7 ‘covering common organizational situations such as academic programs, university applications, recruiting processes, client engagements, research workflows, financial records, travel, legal matters, creative projects, software repositories, personal administration, and photo collections.’ |
| **sensitivity** | `potentially_sensitive` — §2.9's phrase ‘potentially sensitive’. Deliverables are client-confidential and routinely contain the client's own commercial and personal data. No handling class is assigned here. |

**Schema** — the fields this domain, and only this domain, legitimises.

| field | type | example | ceiling | why |
|---|---|---|---|---|
| `client` | string | Nordea Bank | `validated` | §3.8 names this field. A gazetteer organisation name in a client position beside engagement language — §3.8 ‘A consulting document may mention the author’s firm and the client organization. A finance document may mention an account holder and an issuing bank. The agent should model these as distinct facets, such as authored_by and target_school, or our_firm and client.’ |
| `our_firm` | string | Bain & Company | `validated` | §3.8 names this field too, and the two must never collapse into one organisation facet. |
| `engagement_name_or_code` | string | NDA-2026-Ops | `direct` | Engagement codes appear as labeled references in headers and footers of every deliverable. |
| `engagement_phase` | enum-like | diagnostic | `validated` | Phase vocabulary is closed per methodology and appears in deliverable headers. |
| `deliverable_type` | enum-like | steering committee deck | `validated` | Deliverable types are structurally distinct and are §5.4's ‘document type’ reached from the client side. |
| `engagement_lead` | string | the owner's partner | `llm_supported` | Named in prose; must not become a folder level — §3.8 ‘It should avoid using authorship or creator identity as a destination dimension. A folder should not become a collection point for everything produced by the same person or organization.’ |
| `engagement_period` | string | 2026-04 to 2026-09 | `direct` | Stated as a labeled period in the engagement letter. |

**Recognition**

| kind | entries |
|---|---|
| deterministic (pattern **plus** corroborating context) | • engagement language ‘statement of work’ \| ‘engagement letter’ \| ‘deliverable’ \| ‘steering committee’ \| ‘workstream’ co-occurring with two distinct organisation names in client and provider positions<br>• an engagement-code pattern in a document header co-occurring with a client name from the gazetteer |
| needs the LLM | • an internal working document that names the client only in a footer abbreviation<br>• deciding which of two named organisations is the client when both appear in a title slide |
| never alone | • a company or organisation name on its own — §4.9 ‘A university name alone should not create a group because Columbia can appear as an authoring school, course provider, target institution, employer, research venue, or merely a cited organization.’<br>• two organisation names on one page, which is the ordinary state of any business document<br>• a deck or a model file |

**Work types** — `engagement letter`, `statement of work`, `deliverable deck`, `analysis model`, `status report`, `workshop materials`, `interview notes`, `final report`, `closure memo`

**Grouping reasons** — one client, one engagement, every deliverable; one client across engagements

**Template** — `client → engagement name or code → deliverable type`  (time first: no)

> Client above engagement above deliverable — §5.5 ‘The recommendation should follow the practical rule that a parent dimension should provide the context required to understand the child.’ Never our-firm-first: §3.8 ‘It should avoid using authorship or creator identity as a destination dimension. A folder should not become a collection point for everything produced by the same person or organization.’ §5.5 ‘For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders.’

**Collides with**

| domain | separating signal | design cite |
|---|---|---|
| `career.client-proposal` | A proposal and an engagement letter describe the same work before and after award, share the client, the scope language and often whole slides. Only the engagement carries a code and a signed scope. | — |
| `career.portfolio` | A deliverable reworked into a case study is a near-duplicate with a different showing permission; treating them as one version family would let confidential material inherit a public permission. | — |
| `career.restrictive-covenant` | Client NDAs sit inside engagements and are also standalone obligations; the counterparty role differs from an employer NDA's. | §3.8 ‘A consulting document may mention the author’s firm and the client organization. A finance document may mention an account holder and an issuing bank. The agent should model these as distinct facets, such as authored_by and target_school, or our_firm and client.’ |
| `career.freelance-contract-work` | A sole practitioner's engagement and a freelance gig are the same relationship described by different vocabularies; worker classification is the separator. | — |

---

## `career.client-proposal` — Client proposal and bid

Everything produced to win work that has not been awarded yet.

| | |
|---|---|
| **provenance** | `inference` |
| **design cite** | §5.7 ‘covering common organizational situations such as academic programs, university applications, recruiting processes, client engagements, research workflows, financial records, travel, legal matters, creative projects, software repositories, personal administration, and photo collections.’ |
| **sensitivity** | `potentially_sensitive` — §2.9's phrase ‘potentially sensitive’. Bids disclose pricing and are usually submitted under confidentiality terms. No handling class is assigned here. |

**Schema** — the fields this domain, and only this domain, legitimises.

| field | type | example | ceiling | why |
|---|---|---|---|---|
| `client` | string | Transport for London | `validated` | The prospective client, in an addressee or issuer position beside procurement language. |
| `our_firm` | string | Arup | `validated` | The bidding party; §3.8's second organisation role. |
| `solicitation_reference` | string | ITT-2026-0912 | `direct` | Procurement documents carry a labeled tender or RFP reference, which is the strongest identifier in this domain. |
| `submission_deadline` | date | 2026-04-30 | `direct` | A labeled submission-deadline field. |
| `proposed_engagement_type` | enum-like | fixed-price delivery | `llm_supported` | Described in the commercial narrative rather than as a field. |
| `pricing_model` | enum-like | day rate | `validated` | Pricing structures appear as labeled schedule headings. |
| `bid_status` | enum-like | shortlisted | `llm_supported` | Stated in award or regret correspondence. |

**Recognition**

| kind | entries |
|---|---|
| deterministic (pattern **plus** corroborating context) | • procurement language ‘request for proposal’ \| ‘invitation to tender’ \| ‘our understanding of your requirements’ \| ‘pricing schedule’ \| ‘bid’ co-occurring with a client name<br>• a solicitation-reference pattern co-occurring with a labeled submission deadline |
| needs the LLM | • a capability deck reused as a proposal with no procurement framing<br>• distinguishing a speculative pitch from a formal response when neither cites a reference |
| never alone | • a company or organisation name on its own — §4.9 ‘A university name alone should not create a group because Columbia can appear as an authoring school, course provider, target institution, employer, research venue, or merely a cited organization.’<br>• the word ‘proposal’ — research proposals, marriage proposals and policy proposals all produce it<br>• a currency-shaped amount on its own |

**Work types** — `RFP or ITT document`, `proposal document`, `pitch deck`, `pricing schedule`, `capability statement`, `reference case list`, `clarification correspondence`, `award or regret letter`

**Grouping reasons** — one solicitation and every document answering it; one client's opportunities across bids

**Template** — `client → solicitation reference`  (time first: no)

> Client first; the reference distinguishes repeat opportunities with the same client. §5.5 ‘The recommendation should follow the practical rule that a parent dimension should provide the context required to understand the child.’

**Collides with**

| domain | separating signal | design cite |
|---|---|---|
| `career.consulting-engagement` | Pre-award versus post-award; see the engagement entry. | — |
| `career.job-application` | A capability statement and a resume make the same argument at different scales, and for a sole practitioner they are the same document. | — |
| `res.research-project` | A grant proposal and a client proposal share structure, deadlines and a funding narrative. | — |

---

## `career.freelance-contract-work` — Freelance and contract work

Work done as an independent supplier rather than an employee, where worker classification is itself part of the record.

| | |
|---|---|
| **provenance** | `inference` |
| **design cite** | §5.7 ‘covering common organizational situations such as academic programs, university applications, recruiting processes, client engagements, research workflows, financial records, travel, legal matters, creative projects, software repositories, personal administration, and photo collections.’ |
| **sensitivity** | `potentially_sensitive` — §2.9's phrase ‘potentially sensitive’. Contractor agreements state rates and tax status, and §8.4 ‘The product processes a highly personal corpus that can include identity documents, account statements, tax records, medical information, legal records, credentials, private correspondence, GPS metadata, employment materials, and educational records.’ No handling class is assigned here. |

**Schema** — the fields this domain, and only this domain, legitimises.

| field | type | example | ceiling | why |
|---|---|---|---|---|
| `client` | string | Penguin Random House | `validated` | The engaging party, in a client position beside contractor language. |
| `gig_or_project` | string | Cover illustration, autumn list | `direct` | Named in the brief's own title. |
| `platform` | string | Upwork | `validated` | A marketplace host name beside engagement language; a platform is neither client nor employer. |
| `worker_classification` | enum-like | self-employed contractor | `validated` | Classification language — contractor, self-employed, umbrella, inside or outside a status rule — is closed and jurisdictional, and is the whole legal point of the record. |
| `rate_basis` | enum-like | day rate | `validated` | A labeled rate line in the contract or brief. |
| `deliverable` | string | final artwork files | `llm_supported` | Described in the brief's prose. |
| `project_period` | string | 2026-05 to 2026-06 | `direct` | A labeled period in the contract. |

**Recognition**

| kind | entries |
|---|---|
| deterministic (pattern **plus** corroborating context) | • contractor language ‘independent contractor’ \| ‘self-employed’ \| ‘not an employee’ \| ‘day rate’ \| ‘milestone payment’ co-occurring with a client name<br>• a platform host name co-occurring with contract or brief language and a named client |
| needs the LLM | • an informal gig agreed entirely in messages with no contract<br>• deciding whether a long engagement was contracted or employed when the vocabulary is mixed |
| never alone | • a company or organisation name on its own — §4.9 ‘A university name alone should not create a group because Columbia can appear as an authoring school, course provider, target institution, employer, research venue, or merely a cited organization.’<br>• a platform host name, which appears in unrelated saved pages<br>• a brief, which employers, clients and courses all issue |

**Work types** — `contractor agreement`, `project brief`, `milestone acceptance`, `time log`, `deliverable handover`, `platform contract record`, `classification determination`, `client feedback`

**Grouping reasons** — one client, one gig, every document; one platform's engagements across clients

**Template** — `client → gig or project`  (time first: no)

> Client above project. §5.5 ‘The recommendation should follow the practical rule that a parent dimension should provide the context required to understand the child.’ Not platform-first: the platform is an intermediary, not the relationship.

**Collides with**

| domain | separating signal | design cite |
|---|---|---|
| `career.employment-contract` | A contractor agreement and an employment contract are deliberately near-identical documents whose entire legal significance is that they are not the same. Classification language is the only reliable separator, and getting it wrong misstates the owner's tax position. | §3.8 ‘A consulting document may mention the author’s firm and the client organization. A finance document may mention an account holder and an issuing bank. The agent should model these as distinct facets, such as authored_by and target_school, or our_firm and client.’ |
| `career.consulting-engagement` | The same relationship in a different register; see the engagement entry. | — |
| `career.service-invoicing` | Every gig produces invoices, which are a separate record with their own identifiers. | — |

---

## `career.service-invoicing` — Invoicing for services

Invoices the owner issues and the payments received against them.

| | |
|---|---|
| **provenance** | `proposal` |
| **design cite** | _none — nothing in the design speaks to this domain_ |
| **sensitivity** | `potentially_sensitive` — §2.9's phrase ‘potentially sensitive’. Issued invoices carry the owner's bank details, trading address and tax registration. No handling class is assigned here. |

**Schema** — the fields this domain, and only this domain, legitimises.

| field | type | example | ceiling | why |
|---|---|---|---|---|
| `client` | string | Penguin Random House | `validated` | The billed party. The owner is the issuer here, which reverses every role a payslip assigns — §3.8 ‘A consulting document may mention the author’s firm and the client organization. A finance document may mention an account holder and an issuing bank. The agent should model these as distinct facets, such as authored_by and target_school, or our_firm and client.’ |
| `invoice_number` | string | 2026-014 | `direct` | A labeled invoice-number field issued by the owner's own sequence. It is the field that proves the owner is the vendor. |
| `invoice_date` | date | 2026-06-03 | `direct` | A labeled invoice-date field. |
| `period_covered` | string | May 2026 | `direct` | A labeled service-period line. |
| `engagement_reference` | string | Cover illustration, autumn list | `possible` | Invoices cite the work loosely; the citation links records for review but does not establish an engagement fact. |
| `payment_status` | enum-like | paid | `llm_supported` | Established from remittance correspondence rather than from the invoice. |
| `tax_treatment` | string | VAT at standard rate | `direct` | A labeled tax line, which differs structurally from a payslip's withholding line. |

**Recognition**

| kind | entries |
|---|---|
| deterministic (pattern **plus** corroborating context) | • invoicing language ‘invoice’ \| ‘amount due’ \| ‘payment terms’ \| ‘remit to’ \| ‘bill to’ co-occurring with an invoice-number field and a named client<br>• a labeled bill-to block naming a client alongside a labeled from block naming the owner or the owner's trading entity |
| needs the LLM | • a plain-text request for payment with no invoice structure<br>• distinguishing an invoice the owner issued from one the owner received when the layout is a generic template |
| never alone | • the word ‘invoice’ — received supplier invoices are the far more common case in most corpora<br>• a currency-shaped amount on its own<br>• a company or organisation name on its own — §4.9 ‘A university name alone should not create a group because Columbia can appear as an authoring school, course provider, target institution, employer, research venue, or merely a cited organization.’ |

**Work types** — `issued invoice`, `credit note`, `remittance advice`, `payment receipt`, `statement of account`, `late-payment chase`, `purchase order copy`, `self-billing document`

**Grouping reasons** — one client's invoices in sequence; one engagement's invoices and payments

**Template** — `client → tax year`  (time first: no)

> Client above year because a freelancer chases payment by client and reports by year. §5.5 ‘For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders.’

**Collides with**

| domain | separating signal | design cite |
|---|---|---|
| `career.payroll` | The core role collision of independent work. Both are income documents naming an organisation, a period and an amount. A payslip is issued to the owner as an employee and carries withholding and an employee number; an invoice is issued by the owner as a vendor and carries the owner's own invoice sequence. Confusing them misstates who employs whom. | §3.8 ‘A consulting document may mention the author’s firm and the client organization. A finance document may mention an account holder and an issuing bank. The agent should model these as distinct facets, such as authored_by and target_school, or our_firm and client.’ |
| `biz.invoice-issued` | A near-duplicate of this domain authored in the business slice. Both describe an invoice the owner issued; only this one carries the employment-versus-vendor role split that separates it from a payslip. The two entries must be reconciled before the allow-list is frozen, not merged blindly. | §3.8 ‘A consulting document may mention the author’s firm and the client organization. A finance document may mention an account holder and an issuing bank. The agent should model these as distinct facets, such as authored_by and target_school, or our_firm and client.’ |
| `career.freelance-contract-work` | The gig is the work; the invoice is the billing for it. | — |

---

## `career.employer-job-requisition` — Job requisition (employer side)

An organisation's internal record of a role it is opening, before and while it is advertised.

| | |
|---|---|
| **provenance** | `inference` |
| **design cite** | §5.4 ‘a Career template may define company → role or recruiting cycle → document type’ §3.8 ‘A consulting document may mention the author’s firm and the client organization. A finance document may mention an account holder and an issuing bank. The agent should model these as distinct facets, such as authored_by and target_school, or our_firm and client.’ |
| **sensitivity** | `potentially_sensitive` — §2.9's phrase ‘potentially sensitive’. Requisitions carry internal levels, headcount plans and salary bands. No handling class is assigned here. |

**Schema** — the fields this domain, and only this domain, legitimises.

| field | type | example | ceiling | why |
|---|---|---|---|---|
| `hiring_organisation` | string | the owner's employer | `validated` | The organisation doing the hiring. This is the same entity type as ‘employer’ in a candidate packet and the opposite role — §3.8 ‘A consulting document may mention the author’s firm and the client organization. A finance document may mention an account holder and an issuing bank. The agent should model these as distinct facets, such as authored_by and target_school, or our_firm and client.’ |
| `requisition_id` | string | REQ-48213 | `direct` | A labeled requisition-number field in the applicant-tracking export. |
| `role_title` | string | Senior Backend Engineer | `direct` | A labeled title field. |
| `internal_level` | string | P4 | `validated` | A level pattern beside requisition language; the same pattern in a promotion packet means something else. |
| `hiring_manager` | string | the owner | `llm_supported` | Named in prose or in a system field; never a folder level — §3.8 ‘It should avoid using authorship or creator identity as a destination dimension. A folder should not become a collection point for everything produced by the same person or organization.’ |
| `department_or_team` | string | Payments Platform | `direct` | A labeled team field. |
| `requisition_status` | enum-like | open | `direct` | A labeled status field in the tracking export. |
| `approval_state` | enum-like | headcount approved | `llm_supported` | Approval history lives in correspondence and workflow exports. |

**Recognition**

| kind | entries |
|---|---|
| deterministic (pattern **plus** corroborating context) | • requisition language ‘requisition’ \| ‘headcount’ \| ‘hiring manager’ \| ‘approved to open’ \| ‘intake meeting’ co-occurring with a role title and an internal level<br>• an applicant-tracking export whose labeled columns carry ‘req id’, ‘status’ and ‘hiring manager’ together |
| needs the LLM | • an intake-meeting note that describes a role with no requisition raised yet<br>• a draft job description with no internal markers, which is indistinguishable from a saved posting |
| never alone | • a job description — this is the sharpest collision in the slice and a JD alone cannot say which side it sits on<br>• a company or organisation name on its own — §4.9 ‘A university name alone should not create a group because Columbia can appear as an authoring school, course provider, target institution, employer, research venue, or merely a cited organization.’<br>• a level code on its own |

**Work types** — `requisition record`, `job description draft`, `intake meeting notes`, `headcount approval`, `scorecard template`, `sourcing plan`, `posting copy`, `requisition closure note`

**Grouping reasons** — one requisition and everything raised under it; one team's open roles in one period

**Template** — `department or team → requisition id`  (time first: no)

> Team above requisition — §5.5 ‘The recommendation should follow the practical rule that a parent dimension should provide the context required to understand the child.’ Never hiring-manager-first: §3.8 ‘It should avoid using authorship or creator identity as a destination dimension. A folder should not become a collection point for everything produced by the same person or organization.’

**Collides with**

| domain | separating signal | design cite |
|---|---|---|
| `career.job-posting-collected` | The same job description on a candidate's disk and on a hiring manager's disk, often with the identical filename. Only the requisition carries level, headcount and hiring-manager fields; only the collected posting carries public apply language. Nothing else separates them, which makes this the clearest case in the slice for the role split §3.8 requires. | §3.8 ‘A consulting document may mention the author’s firm and the client organization. A finance document may mention an account holder and an issuing bank. The agent should model these as distinct facets, such as authored_by and target_school, or our_firm and client.’ §3.8 ‘It should avoid using authorship or creator identity as a destination dimension. A folder should not become a collection point for everything produced by the same person or organization.’ |
| `career.job-search-campaign` | A recruiter's pipeline tracker and a candidate's search tracker are the same spreadsheet shape. | §3.8 ‘A consulting document may mention the author’s firm and the client organization. A finance document may mention an account holder and an issuing bank. The agent should model these as distinct facets, such as authored_by and target_school, or our_firm and client.’ |
| `career.employer-candidate-packet` | Candidates attach to requisitions; the requisition is not a candidate record. | — |

---

## `career.employer-candidate-packet` — Candidate packet (employer side)

Applications received about other people, held by whoever is hiring.

| | |
|---|---|
| **provenance** | `inference` |
| **design cite** | §3.8 ‘A consulting document may mention the author’s firm and the client organization. A finance document may mention an account holder and an issuing bank. The agent should model these as distinct facets, such as authored_by and target_school, or our_firm and client.’ |
| **sensitivity** | `potentially_sensitive` — §2.9's phrase ‘potentially sensitive’. Every file in this domain is another person's personal data held by the corpus owner. No handling class is assigned here. |

**Schema** — the fields this domain, and only this domain, legitimises.

| field | type | example | ceiling | why |
|---|---|---|---|---|
| `candidate` | string | an applicant | `llm_supported` | The subject of the packet, and the field that makes this domain the mirror image of the resume domain — §3.8 ‘A consulting document may mention the author’s firm and the client organization. A finance document may mention an account holder and an issuing bank. The agent should model these as distinct facets, such as authored_by and target_school, or our_firm and client.’ |
| `requisition_id` | string | REQ-48213 | `direct` | A labeled requisition reference in the tracking export. |
| `role_title` | string | Senior Backend Engineer | `direct` | A labeled title field. |
| `candidate_source` | enum-like | agency submission | `direct` | A labeled source field in the tracking export. |
| `pipeline_stage` | enum-like | onsite scheduled | `direct` | A labeled stage field. |
| `application_received_date` | date | 2026-03-18 | `direct` | A labeled received-date field. |
| `recruiter` | string | the owner | `llm_supported` | Named in prose or a system field; never a folder level. |
| `carries_third_party_personal_data` | boolean | true | `direct` | A resume header belonging to someone other than the owner is present. A privacy-and-explanation field in §3.11's sense. |

**Recognition**

| kind | entries |
|---|---|
| deterministic (pattern **plus** corroborating context) | • an applicant-tracking export whose labeled columns carry ‘candidate’, ‘req id’ and ‘stage’ together<br>• resume section headings co-occurring with a requisition reference or an agency submission cover note |
| needs the LLM | • a loose folder of resumes with no tracking export and no requisition reference<br>• deciding whether a resume in the corpus belongs to the owner or to an applicant |
| never alone | • resume section headings — they are identical on the owner's own resume<br>• a person's name on its own; it identifies an author, not a domain<br>• a filename such as ‘Resume.pdf’, which §8.3 ‘Case-insensitive filesystems can treat Resume.pdf and resume.pdf as one path, while a case-sensitive filesystem can store both.’ shows the filesystem itself may not keep distinct |

**Work types** — `received resume`, `received cover letter`, `agency submission note`, `candidate summary`, `portfolio submission`, `screening notes`, `pipeline export`, `right-to-work evidence copy`

**Grouping reasons** — one requisition's candidates; one candidate across the stages they reached

**Template** — `requisition id → pipeline stage`  (time first: no)

> Requisition above stage, and deliberately not candidate-first: §3.8 ‘It should avoid using authorship or creator identity as a destination dimension. A folder should not become a collection point for everything produced by the same person or organization.’ A branch per named applicant would make the tree a directory of people.

**Collides with**

| domain | separating signal | design cite |
|---|---|---|
| `career.resume` | The single hardest collision in this slice. A resume the owner wrote and a resume the owner received are the same document type with opposite subjects, frequently the same filename, and no internal signal that separates them unless the product knows who the owner is. | §3.8 ‘A consulting document may mention the author’s firm and the client organization. A finance document may mention an account holder and an issuing bank. The agent should model these as distinct facets, such as authored_by and target_school, or our_firm and client.’ §8.3 ‘Case-insensitive filesystems can treat Resume.pdf and resume.pdf as one path, while a case-sensitive filesystem can store both.’ |
| `career.job-application` | The identical packet exists on the candidate's disk with the roles reversed. | §3.8 ‘A consulting document may mention the author’s firm and the client organization. A finance document may mention an account holder and an issuing bank. The agent should model these as distinct facets, such as authored_by and target_school, or our_firm and client.’ |
| `career.reference-and-recommendation` | References collected about candidates are third-party statements about third parties. | §2.9 ‘Contact formats such as VCF should yield names, organizations, email addresses, phone numbers, and address-book metadata, but should normally be privacy-protected rather than used to create folder proposals.’ |

**Open question — unresolved, Joseph's call**

> Separating the owner's own resume from a resume the owner received requires knowing who the owner is, and the design never establishes a corpus-owner identity. Should the product hold a ‘me’ entity — and if so, does it come from the user, from the filesystem account, or from the corpus? Without it, §3.8's role separation has nothing to key on for this pair.

---

## `career.employer-interview-scorecard` — Interview scorecard and debrief (employer side)

Structured assessments of named candidates produced by the people interviewing them.

| | |
|---|---|
| **provenance** | `inference` |
| **design cite** | §3.8 ‘A consulting document may mention the author’s firm and the client organization. A finance document may mention an account holder and an issuing bank. The agent should model these as distinct facets, such as authored_by and target_school, or our_firm and client.’ |
| **sensitivity** | `potentially_sensitive` — §2.9's phrase ‘potentially sensitive’. Scorecards are candid written judgements about named third parties. No handling class is assigned here. |

**Schema** — the fields this domain, and only this domain, legitimises.

| field | type | example | ceiling | why |
|---|---|---|---|---|
| `candidate` | string | an applicant | `llm_supported` | The subject of the assessment. |
| `requisition_id` | string | REQ-48213 | `direct` | A labeled requisition reference. |
| `interview_stage` | enum-like | onsite loop | `direct` | A labeled stage field. |
| `interviewer` | string | the owner | `llm_supported` | The assessor; distinct from both candidate and recruiter. |
| `competency_area` | enum-like | system design | `validated` | Rubric headings are enumerated inside the scorecard form. |
| `recommendation` | enum-like | hire | `direct` | A labeled recommendation field in the form. |
| `debrief_date` | date | 2026-04-10 | `direct` | A labeled date field. |

**Recognition**

| kind | entries |
|---|---|
| deterministic (pattern **plus** corroborating context) | • scorecard language ‘recommendation’ \| ‘hire / no hire’ \| ‘competency’ \| ‘debrief’ \| ‘evidence observed’ co-occurring with a requisition reference<br>• a rubric form whose labeled sections carry a competency list and a recommendation field together |
| needs the LLM | • free-form interview notes with no rubric structure<br>• distinguishing a hiring debrief from a performance calibration note, which use the same vocabulary |
| never alone | • rubric structure — performance reviews and grading forms share it<br>• a person's name on its own; it identifies an author, not a domain<br>• the word ‘scorecard’, which is also a metrics-reporting term |

**Work types** — `interview scorecard`, `debrief notes`, `hiring committee packet`, `rubric template`, `calibration guidance`, `structured question set`, `assessment summary`

**Grouping reasons** — one candidate's scorecards across a loop; one requisition's debriefs

**Template** — `requisition id → interview stage`  (time first: no)

> Requisition above stage; never candidate-first, for the same reason as the candidate packet. §3.8 ‘It should avoid using authorship or creator identity as a destination dimension. A folder should not become a collection point for everything produced by the same person or organization.’

**Collides with**

| domain | separating signal | design cite |
|---|---|---|
| `career.performance-review` | Both are structured assessments of a named person written by the owner against a competency rubric. Only the scorecard attaches to a requisition rather than to an employment, and mixing them puts assessments of applicants beside assessments of reports. | §3.8 ‘A consulting document may mention the author’s firm and the client organization. A finance document may mention an account holder and an issuing bank. The agent should model these as distinct facets, such as authored_by and target_school, or our_firm and client.’ |
| `career.interview-cycle` | The candidate's own debrief note and the employer's scorecard describe the same conversation from opposite sides. | §3.8 ‘A consulting document may mention the author’s firm and the client organization. A finance document may mention an account holder and an issuing bank. The agent should model these as distinct facets, such as authored_by and target_school, or our_firm and client.’ |
| `career.employer-candidate-packet` | Scorecards attach to candidates without being candidate documents. | — |

**Open question — unresolved, Joseph's call**

> Every value in this domain's subject field is another person's name. §3.8 already forbids a folder becoming a collection point for everything produced by one person; should a domain whose organising values are third parties' names be permitted to create folder levels at all, or should it be restricted to search and review?

---

## `career.employer-offer-approval` — Offer approval and closing (employer side)

An organisation's internal decision to extend an offer, and the paperwork that issues it.

| | |
|---|---|
| **provenance** | `inference` |
| **design cite** | §3.8 ‘A consulting document may mention the author’s firm and the client organization. A finance document may mention an account holder and an issuing bank. The agent should model these as distinct facets, such as authored_by and target_school, or our_firm and client.’ |
| **sensitivity** | `potentially_sensitive` — §2.9's phrase ‘potentially sensitive’. Approval records state another person's compensation and internal level. No handling class is assigned here. |

**Schema** — the fields this domain, and only this domain, legitimises.

| field | type | example | ceiling | why |
|---|---|---|---|---|
| `candidate` | string | an applicant | `llm_supported` | The person the offer is for. |
| `requisition_id` | string | REQ-48213 | `direct` | A labeled requisition reference. |
| `approved_level` | string | P4 | `direct` | A labeled level field in the approval record. |
| `approver` | string | the owner's director | `llm_supported` | Named in workflow correspondence. |
| `approval_date` | date | 2026-05-06 | `direct` | A labeled approval-date field. |
| `compensation_band_reference` | string | P4 band, EMEA | `validated` | Band references only mean a band beside compensation-approval language. |
| `offer_outcome` | enum-like | accepted | `llm_supported` | Established from candidate correspondence. |

**Recognition**

| kind | entries |
|---|---|
| deterministic (pattern **plus** corroborating context) | • approval language ‘offer approval’ \| ‘approved to extend’ \| ‘compensation approval’ \| ‘band exception’ \| ‘level calibration’ co-occurring with a requisition reference<br>• a labeled approver field co-occurring with a labeled approval date and a level value |
| needs the LLM | • an approval agreed in a message thread with no workflow record<br>• distinguishing an internal offer template from an issued offer letter |
| never alone | • an offer letter, which is identical to the copy the candidate holds<br>• a currency-shaped amount on its own<br>• a company or organisation name on its own — §4.9 ‘A university name alone should not create a group because Columbia can appear as an authoring school, course provider, target institution, employer, research venue, or merely a cited organization.’ |

**Work types** — `offer approval record`, `compensation approval`, `band exception request`, `level calibration note`, `issued offer letter`, `offer letter template`, `background check authorisation`, `candidate acceptance record`

**Grouping reasons** — one candidate's offer from approval to acceptance; one requisition's offers

**Template** — `requisition id → offer outcome`  (time first: no)

> Requisition above outcome; never candidate-first. §3.8 ‘It should avoid using authorship or creator identity as a destination dimension. A folder should not become a collection point for everything produced by the same person or organization.’

**Collides with**

| domain | separating signal | design cite |
|---|---|---|
| `career.offer-and-negotiation` | The issued offer letter is byte-identical on both sides of the transaction. Only the approval trail distinguishes the employer's copy, and a corpus owner who has been both a candidate and a hiring manager holds both. | §3.8 ‘A consulting document may mention the author’s firm and the client organization. A finance document may mention an account holder and an issuing bank. The agent should model these as distinct facets, such as authored_by and target_school, or our_firm and client.’ |
| `career.employer-job-requisition` | Approvals close requisitions without being requisition records. | — |
| `career.compensation-record` | Band documents serve both hiring and in-employment compensation. | — |

---

## Open questions, collected

Every one of these is copied verbatim from the entry that raises it, and belongs in `NEEDS-JOSEPH.md`.

**`career.job-search-campaign`** — Does the fact that the corpus owner is conducting a job search count as ‘potentially sensitive’ under §2.9, which introduces the phrase for message addresses and content? A search that a current employer must not see is sensitive for a reason §2.9 does not describe, and only Joseph can say whether that belongs in this field or nowhere in the catalogue.

**`career.job-application`** — §5.4 defines the Career template as company → role or recruiting cycle → document type. The design never resolves the ‘or’. Should a Career branch nest employer → cycle → role, or employer → role → cycle — and does the right answer change between someone who applies to one employer across several cycles and someone who applies to forty employers inside one cycle?

**`career.internship-application`** — For a student whose internship is credit-bearing, the same packet is career material and coursework. Should it sit under Career or under Academics by default, and should the answer change when the university itself administers the placement?

**`career.resume`** — Two resumes differing by one tailored paragraph and naming different employers: §3.1 makes ‘a member of a version family’ a universal fact, but is a tailoring family one version family with two live members, or two families? The answer decides whether either file may ever supersede the other, and the design does not say.

**`career.take-home-assessment`** — A take-home repository satisfies §3.11's Code schema and this one simultaneously. Should the Career reading or the Code reading determine its physical home by default, and should an employer-confidential brief be allowed to sit inside a code branch at all?

**`career.work-authorization`** — §3.15 makes identity and legal safety domains, ‘detected and protected’ before automated placement. An employer-sponsored work petition is simultaneously career material and identity material. Does it activate the Career schema, the identity safety domain, or both — and if both, which one governs where the file may physically go?

**`career.payroll`** — §3.11 gives Finance ‘institution, account type, tax year, record type’ and §3.15 makes Finance a safety domain, while ‘career and recruiting’ is a launch domain with no stated fields. A payslip sits in both. Does payroll activate the Career schema, the Finance safety domain, or both — and does the safety domain's protection follow the file into a Career branch?

**`career.conference-attendance`** — §5.5 makes time-first the exception for capture-based media and subject-first the rule for record domains, but an event record is arguably both. Should a Conferences branch read event → year or year → event by default?

**`career.employer-candidate-packet`** — Separating the owner's own resume from a resume the owner received requires knowing who the owner is, and the design never establishes a corpus-owner identity. Should the product hold a ‘me’ entity — and if so, does it come from the user, from the filesystem account, or from the corpus? Without it, §3.8's role separation has nothing to key on for this pair.

**`career.employer-interview-scorecard`** — Every value in this domain's subject field is another person's name. §3.8 already forbids a folder becoming a collection point for everything produced by one person; should a domain whose organising values are third parties' names be permitted to create folder levels at all, or should it be restricted to search and review?
