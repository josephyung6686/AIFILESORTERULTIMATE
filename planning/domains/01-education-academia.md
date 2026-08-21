# 01 — Education and academia (domain catalogue slice)

- **supercategory**: `education-academia`
- **authored**: 2026-08-21
- **entries**: 40
- **conforms to**: [`_CONTRACT.md`](_CONTRACT.md)
- **source of truth**: [`../00-database-agent-product-design.md`](../00-database-agent-product-design.md)
- **machine-readable form**: [`01-education-academia.json`](01-education-academia.json) — this file is rendered from it and must not be edited independently.

## What this file is

A domain here is not a label. Per the contract it is **a schema (which fact fields are legal) plus a template (how its branch is shaped)** — simultaneously the allow-list the §3.6 validator enforces and the menu §5.3 draws branch proposals from. A shallow entry produces a validator that lets nonsense through, or a tree that proposes folders nobody wants.

## How to read the provenance column — it is load-bearing

| provenance | count | what it claims |
|---|---|---|
| `design` | 2 | A design sentence names this domain **and its fields**. Only the two exemplars the design actually spells out qualify: Academic and College applications. |
| `inference` | 12 | An extension of a domain the design names. The `design_cite` quotes the sentence being extended and says plainly that the design does not name this domain. |
| `proposal` | 26 | New here. `design_cite` is **null** on every one of these, so no proposal row can be misread as carrying design support. §3.15 and §5.7 are what permit the library to grow; they do not endorse any particular addition. |

Every quotation in this file was checked verbatim against the source of truth by a script before the file was written; a quotation that could not be matched was deleted rather than paraphrased inside quote marks.

## Rules this catalogue obeys

1. **No fabricated quotation.** Every `§X.Y '…'` span comes from a verified quote bank. Prose outside those spans is the author's and is not presented as the design's.
2. **No numbers, thresholds or confidence scores.** The only digits in this file are section references and the design's own example values (`BUSIB 4300`, `Spring 2026`, `AY 2024-25`, `Homework 3`). Every threshold in this product is injected.
3. **No handling classes.** `sensitivity` is `none` or `potentially_sensitive` — §2.9's phrase and nothing more. Handling classes are P7's (§8.4) and are never set here.
4. **Deterministic rules are never bare patterns.** Every rule in the `deterministic` column pairs a pattern with a corroborating context, on the model of §3.5's course rule. Bare patterns live in `never_alone`.
5. **`reliability_ceiling` uses §3.13's six states only**, and a field claiming `validated` is claiming a rule will confirm it — so the entry's deterministic rules must actually support it.
6. **Undecidable things stay undecided.** Anything that is Joseph's call — especially where a domain implies a default folder shape for someone's real life — is in `open_question` and collected at the end of this file.

## Cross-file references

collides_with.domain ids beginning acad. resolve inside this file. Ids beginning research., career., financial., photos., travel., code., identity., medical., legal. or residual. are forward references to other supercategory slices and to the residual library (design §7.3); they are unresolved here and must be reconciled at merge.

## The entries at a glance

| # | id | name | prov. | sensitivity | recommended dimension order |
|---|---|---|---|---|---|
| 1 | `acad.course-enrollment` | Course enrollment and coursework | design | — | school → term → subject → work_type |
| 2 | `acad.course-instruction` | Teaching a course | inference | sensitive | school → subject → term → instruction_work_type |
| 3 | `acad.k12-schooling` | K-12 schooling records | proposal | sensitive | student → school_year → record_type |
| 4 | `acad.undergraduate-program` | Undergraduate degree programme | inference | — | school → programme → programme_record_type |
| 5 | `acad.graduate-program` | Graduate programme milestones | inference | — | school → programme → milestone |
| 6 | `acad.professional-school` | Professional degree programme | proposal | — | school → programme → programme_stage |
| 7 | `acad.continuing-education` | Continuing education and professional development | proposal | — | credential → reporting_period → activity |
| 8 | `acad.bootcamp-cohort` | Bootcamp or intensive cohort programme | proposal | — | provider → programme → module |
| 9 | `acad.self-study` | Self-directed study | proposal | — | subject → source → study_artifact_type |
| 10 | `acad.lab-course` | Laboratory course work | inference | — | school → term → subject → experiment |
| 11 | `acad.teaching-assistantship` | Teaching assistantship | proposal | sensitive | school → term → subject → assistantship_duty_type |
| 12 | `acad.tutoring` | Tutoring engagements | proposal | sensitive | subject → engagement → session |
| 13 | `acad.curriculum-development` | Curriculum and programme development | proposal | — | school → programme → curriculum_unit |
| 14 | `acad.college-application` | College application packet | design | sensitive | target_institution → application_cycle → application_document_type |
| 15 | `acad.k12-school-admission` | K-12 and secondary school admission | inference | sensitive | applicant → target_school → admission_document_type |
| 16 | `acad.grad-school-application` | Graduate and professional school application | inference | — | target_institution → target_programme → application_cycle → application_document_type |
| 17 | `acad.standardized-testing` | Standardised testing | proposal | — | test → test_sitting → testing_record_type |
| 18 | `acad.recommendation-letter` | Letters and forms of recommendation | inference | sensitive | target → cycle → letter_direction |
| 19 | `acad.transcript-record` | Transcripts and official academic records | inference | sensitive | issuing_school → record_type → issue_date |
| 20 | `acad.transfer-credit` | Transfer credit and credit by examination | proposal | — | receiving_institution → sending_institution → credit_basis |
| 21 | `acad.financial-aid` | Financial aid and student loans | proposal | sensitive | awarding_body → award_year → aid_type |
| 22 | `acad.scholarship-fellowship` | Scholarship and fellowship applications | proposal | — | funder → award → competition_cycle |
| 23 | `acad.tuition-billing` | Tuition billing and the student account | proposal | sensitive | institution → term_billed → account_record_type |
| 24 | `acad.campus-employment` | Campus employment | proposal | sensitive | institution → department_or_unit → position |
| 25 | `acad.thesis-dissertation` | Thesis or dissertation | inference | — | degree → thesis_stage → chapter |
| 26 | `acad.undergrad-research` | Undergraduate research placement | inference | — | lab → placement_period → placement_artifact_type |
| 27 | `acad.conference-travel-student` | Student conference travel and presentation | inference | — | venue → edition → conference_artifact_type |
| 28 | `acad.study-abroad` | Study abroad and exchange | proposal | sensitive | host_institution → term_abroad → mobility_document_type |
| 29 | `acad.clinical-rotation` | Clinical rotation and supervised practicum | proposal | sensitive | programme → service_or_specialty → site |
| 30 | `acad.internship-for-credit` | Internship or co-op taken for credit | proposal | sensitive | host_organisation → term → credit_requirement_type |
| 31 | `acad.language-study` | Language study and proficiency certification | proposal | — | language → level → language_study_artifact_type |
| 32 | `acad.arts-jury-portfolio` | Music and arts juries, recitals and portfolio review | proposal | — | discipline → assessment_event → arts_artifact_type |
| 33 | `acad.athletics-eligibility` | Athletics eligibility and student-athlete compliance | proposal | sensitive | sport → season → compliance_record_type |
| 34 | `acad.advising` | Academic advising and registration planning | proposal | — | school → advising_term → advising_record_type |
| 35 | `acad.accommodations` | Disability accommodations and access services | proposal | sensitive | institution → approval_period → access_record_type |
| 36 | `acad.integrity-case` | Academic integrity and conduct cases | proposal | sensitive | institution → case_reference → process_stage |
| 37 | `acad.student-organization` | Student organisations and clubs | proposal | sensitive | organisation → activity_year → organisation_record_type |
| 38 | `acad.accreditation-institutional` | Accreditation and institutional assessment | proposal | sensitive | accreditor → review_cycle → standard |
| 39 | `acad.alumni-record` | Alumni relations and post-graduation records | proposal | — | institution → alumni_record_type → engagement |
| 40 | `acad.credential-certificate` | Diplomas, certificates and verifiable credentials | inference | sensitive | awarding_body → credential → credential_form |

`time_first` is `false` on every entry in this slice. That is not an oversight: §5.5 says "For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders", and names photos and capture-based media as the exception. Nothing in education is capture-based media. Where a period does sit high in an order — a continuing-education reporting period, a bursar term, an aid award year — it is because that period is a compliance or reconciliation boundary, not a calendar, and the reason is stated in that entry's template note.

---

## The entries

### 1. Course enrollment and coursework

`acad.course-enrollment` · **design** · sensitivity: `none`

> Files a student produces or receives by taking one specific course in one specific term.

**Design basis** — §3.11 'Academic files may use school, term, course, instructor, and work type.'; §3.1 'subject = BUSIB 4300'; §3.1 'term = Spring 2026'; §3.1 'work type = syllabus'; §5.4 'An Academic template may define school → term → course → work type'

**Schema — the fields this domain, and only this domain, legitimises**

| field | type | example | reliability ceiling | why this field exists and why that ceiling |
|---|---|---|---|---|
| `school` | string | Columbia | `validated` | Named in §3.11 'Academic files may use school, term, course, instructor, and work type.'. A school name only reaches validated through a gazetteer match at a word boundary, because §3.7 'names such as MIT can be found inside "submit,"'. |
| `term` | string | Spring 2026 | `validated` | §3.1 'term = Spring 2026', and §3.10 'Academic terms such as Spring 2025, AY 2024-25, and Michaelmas Term 2024 require dedicated patterns rather than generic parsing.'. |
| `subject` | string | BUSIB 4300 | `validated` | §3.5 'BUSIB 4300 becomes a course fact only when the engine finds a course-code pattern together with academic context such as "syllabus," "lecture," "credits," "instructor," or "semester."'. The five context terms in that sentence are the only ones the design states literally. |
| `instructor` | string | the name on a syllabus line labelled Instructor | `direct` | Named in §3.11 'Academic files may use school, term, course, instructor, and work type.'. Read from a labelled slot, which §3.5 'such as a content hash, EXIF timestamp, a document title, or a labeled form field' makes direct. It is a role, not authorship: §3.8 'It should avoid using authorship or creator identity as a destination dimension.', so it is metadata here and is not in the dimension order. |
| `work_type` | string | syllabus | `validated` | §3.1 'work type = syllabus', and it is the leaf of the design's own Academic template: §5.5 'A work type such as Homework 3 is meaningful only after the course is known, and a course code may require the school or term to disambiguate it.'. |

**Recognition**

*Deterministic — each rule is a pattern **plus** a corroborating context:*

- a course-code pattern co-occurring with any of 'syllabus', 'lecture', 'credits', 'instructor', 'semester' — §3.5 'BUSIB 4300 becomes a course fact only when the engine finds a course-code pattern together with academic context such as "syllabus," "lecture," "credits," "instructor," or "semester."'
- an academic-term pattern of the Spring 2025 / AY 2024-25 / Michaelmas Term 2024 shape (§3.10 'Academic terms such as Spring 2025, AY 2024-25, and Michaelmas Term 2024 require dedicated patterns rather than generic parsing.') co-occurring with an already-validated course code in the same document
- a gazetteer school name matched at a word boundary (§3.7 'It should use word-boundary matching rather than substring matching.') co-occurring with an already-validated course code
- a filename or document-title occurrence of a work-type term ('syllabus', 'problem set', 'midterm') co-occurring with a validated course code — §3.7 'a value in a filename or document title carries more meaning than the same value in a footer or a late body-page reference'

*Needs the LLM — language interpretation a rule cannot do safely:*

- an unlabelled essay or problem set whose only course signal is the prose topic: §4.3 'may contain only equations and the phrase "Homework 3,"'
- a syllabus written in a language whose course identifier is spelled out in words rather than as a code
- an OCR'd lecture handout whose header is the only course signal and is partially unreadable
- a course whose local name and official code differ, where deciding they are one course needs reading

*Never alone — bare signals that must not establish this domain by themselves:*

- a bare four-digit number — §3.10 'file names and documents frequently contain numbers that look like years but are course identifiers, version numbers, build numbers, ZIP codes, or other unrelated values'
- a university name on its own — §4.9 'A university name alone should not create a group because Columbia can appear as an authoring school, course provider, target institution, employer, research venue, or merely a cited organization.'
- a course-code-shaped token with no academic context term anywhere in the document
- membership in a download session — §3.9 'A session should never be treated as proof of topic'
- a folder named after a school, without any in-file academic evidence

**Work types** — syllabus, lecture slides, lecture notes, problem set, homework, reading, midterm, final exam, quiz, course project, grading rubric, course schedule, term paper, presentation

**Why files in this domain group together**

- one course in one term — §4.9 'A course code alone should not merge different semesters; course packet identity should include a term when it is available.'
- one assignment across its drafts, as a version family (§3.1 'A file can simultaneously be a syllabus, part of a particular course, created for a particular semester, related to a university, included in an application package, a member of a version family, and potentially sensitive.')
- a syllabus plus the lectures, problem sets and midterm that independently name the same course
- the seed the design names for this domain: §4.2 'a syllabus or lecture file containing a validated course code'

**Template**

| dimension order | time first | why |
|---|---|---|
| school → term → subject → work_type | no | §5.4 'An Academic template may define school → term → course → work type'. The order follows §5.5 'a parent dimension should provide the context required to understand the child' and §5.5 'A work type such as Homework 3 is meaningful only after the course is known, and a course code may require the school or term to disambiguate it.'. |

**Collides with** — where this domain and another will fight over the same file

| other domain | the confusion, and what separates them | design cite |
|---|---|---|
| `acad.college-application` | both carry a university name; only the application carries a target-institution and cycle pair, and the school on a transcript is the issuing school, not the target | §4.8 'an application packet does not silently absorb a document with a conflicting target institution' |
| `acad.course-instruction` | the same syllabus PDF appears on both sides; the teaching corpus additionally holds rosters, grade files and unreleased exam keys that a student's corpus never contains | §3.8 'An application essay can mention the author's current school and the university to which the essay is addressed.' |
| `acad.lab-course` | a lab report is coursework and lab-course output at once; only the lab course carries an experiment or session identifier | — |
| `acad.self-study` | both carry a course name; only enrolment carries an institution-issued course code together with a term | §3.5 'BUSIB 4300 becomes a course fact only when the engine finds a course-code pattern together with academic context such as "syllabus," "lecture," "credits," "instructor," or "semester."' |
| `res.research-project` | a term paper and a manuscript both cite literature; the Research template keys on project, not on school and course | §5.4 'a Research template may define project → stage → artifact type' |

**Sensitivity** — `none`. Ordinary coursework carries nothing the design names as potentially sensitive. A graded artifact bearing a student identifier is a separate question and no handling class is assigned here.

**Open question (unresolved — for Joseph)**

> When a file has a validated course and work type but no school evidence, should the tree still open a school level for it, or should it land in a scoped General under the course? §5.9 'It should also support a scoped General or Other branch within a meaningful parent.' permits the second; the design never says which is the default for Academics.

---

### 2. Teaching a course

`acad.course-instruction` · **inference** · sensitivity: `potentially_sensitive`

> The instructor's corpus for one course offering they teach, as distinct from a student's corpus for the same course.

**Design basis** — Extends the Academic domain of §3.11 'Academic files may use school, term, course, instructor, and work type.' to the teaching side. §3.8 'An application essay can mention the author's current school and the university to which the essay is addressed.' is the design's rule that the same entity in a different role is a different field; the design names no teaching-side domain.

**Schema — the fields this domain, and only this domain, legitimises**

| field | type | example | reliability ceiling | why this field exists and why that ceiling |
|---|---|---|---|---|
| `school` | string | Columbia | `validated` | Shared with the Academic schema, §3.11 'Academic files may use school, term, course, instructor, and work type.'. |
| `term` | string | Spring 2026 | `validated` | §3.10 'Academic terms such as Spring 2025, AY 2024-25, and Michaelmas Term 2024 require dedicated patterns rather than generic parsing.'. |
| `subject` | string | BUSIB 4300 | `validated` | §3.5 'BUSIB 4300 becomes a course fact only when the engine finds a course-code pattern together with academic context such as "syllabus," "lecture," "credits," "instructor," or "semester."'. |
| `offering` | string | the section or offering identifier the school issues for one delivery of the course | `validated` | Inference. Teaching material is versioned per delivery: two years of the same course are different corpora. Reaches validated only through the same rule shape as course — a section-code pattern beside a validated course code. |
| `teaching_role` | enum | instructor of record | `llm_supported` | Inference. Whether the holder taught, assisted, or guest-lectured is stated in prose far more often than in a labelled field, so it needs §3.5 'The LLM creates LLM-supported facts only when a file requires language interpretation that rules cannot resolve safely.'. |
| `instruction_work_type` | string | grading rubric | `validated` | Inference. The teaching-side work types are disjoint from the student-side ones (an answer key and a roster have no student-side counterpart); recognised the same way, by a work-type term beside a validated course code. |

**Recognition**

*Deterministic — each rule is a pattern **plus** a corroborating context:*

- a validated course code co-occurring with a teaching-side work-type term ('answer key', 'grade sheet', 'roster', 'course proposal', 'office hours')
- a validated course code co-occurring with a term and with the corpus holder's own name in an instructor-labelled slot — §3.5 'such as a content hash, EXIF timestamp, a document title, or a labeled form field'
- a section-code pattern co-occurring with a validated course code and an academic-term pattern
- a gazetteer school name matched at a word boundary co-occurring with a validated course code and a teaching-side work-type term

*Needs the LLM — language interpretation a rule cannot do safely:*

- a syllabus that could be the instructor's authoring copy or the student's received copy, where only the draft language distinguishes them
- prose that establishes the holder taught rather than took the course
- distinguishing a guest lecture deck from a course the holder owns

*Never alone — bare signals that must not establish this domain by themselves:*

- the holder's name appearing anywhere in a course document — §3.8 'It should avoid using authorship or creator identity as a destination dimension.'
- a course code with no teaching-side signal
- possession of a syllabus, which is equally consistent with enrolment

**Work types** — syllabus draft, lecture deck, assignment brief, answer key, grading rubric, grade sheet, class roster, course proposal, office-hours record, teaching evaluation, make-up exam

**Why files in this domain group together**

- one course offering in one term, on the teaching side
- an assignment brief with its answer key and rubric
- successive deliveries of the same course as a version family

**Template**

| dimension order | time first | why |
|---|---|---|
| school → subject → term → instruction_work_type | no | Inference, and deliberately not the Academic order. A teacher returns to the same course across years, so the course is the stable parent and the term is the child that varies — the reverse of a student's single-term view. §5.5 'a parent dimension should provide the context required to understand the child' supports either reading, so the divergence is flagged in the open question. |

**Collides with** — where this domain and another will fight over the same file

| other domain | the confusion, and what separates them | design cite |
|---|---|---|
| `acad.course-enrollment` | an identical syllabus file; the teaching side is established by an answer key, roster or grade file in the same group, never by the syllabus alone | §3.8 'An application essay can mention the author's current school and the university to which the essay is addressed.' |
| `acad.teaching-assistantship` | both hold grading material for the same course; only the assistantship carries an appointment and a supervising instructor | — |
| `acad.curriculum-development` | both hold syllabus drafts; curriculum work is scoped to a programme and has no term of delivery | — |
| `acad.campus-employment` | both may hold an appointment letter; only employment carries a pay period | — |

**Sensitivity** — `potentially_sensitive`. Inference, not design: the design names no student-record category. Rosters, grade sheets and unreleased exam keys carry other people's names and identifiers, which is the kind of material §2.9 'treating addresses and message content as potentially sensitive' applies the phrase to. No handling class is assigned here.

**Open question (unresolved — for Joseph)**

> Should a teaching branch nest term under course (a teacher's stable-course view) or course under term (the Academic template's order)? The design gives one Academic template and does not say whether the teaching side reuses it.

---

### 3. K-12 schooling records

`acad.k12-schooling` · **proposal** · sensitivity: `potentially_sensitive`

> The school-year record for a child in primary or secondary school, usually held by a parent rather than the student.

**Design basis** — none. `design_cite` is null: no design sentence names this domain. It is a proposal for Joseph.

**Schema — the fields this domain, and only this domain, legitimises**

| field | type | example | reliability ceiling | why this field exists and why that ceiling |
|---|---|---|---|---|
| `school` | string | Georgetown Prep | `validated` | A gazetteer school name at a word boundary. The design's own worked example uses a secondary school by name under Academics, but names no K-12 domain. |
| `school_year` | string | 2025-26 | `validated` | A K-12 year is a hyphenated span, not a semester; it needs its own pattern for the same reason §3.10 'Academic terms such as Spring 2025, AY 2024-25, and Michaelmas Term 2024 require dedicated patterns rather than generic parsing.'. |
| `grade_level` | string | Grade 7 | `validated` | A grade-level pattern beside a school name or school-year span. The primary organising fact for a family: a parent thinks in years of a child's schooling, not in courses. |
| `student` | string | the child the record is about | `user_confirmed` | The child is the subject of the record, not its author, so §3.8 'It should avoid using authorship or creator identity as a destination dimension.' does not bar it — but a person's name is exactly the value that must not be guessed, so only the user establishes it. |
| `record_type` | string | report card | `validated` | A record-type term beside a school name and a school-year span. K-12 record types are administrative (report card, permission slip, immunisation form) and barely overlap the higher-education work types. |
| `subject` | string | Mathematics | `llm_supported` | K-12 subjects are named in prose, not as codes, so no course-code rule reaches them. |

**Recognition**

*Deterministic — each rule is a pattern **plus** a corroborating context:*

- a hyphenated school-year span ('2025-26') co-occurring with a gazetteer school name at a word boundary
- a grade-level pattern ('Grade 7', '7th grade') co-occurring with a school name or a school-year span
- a K-12 record-type term ('report card', 'permission slip', 'parent-teacher conference') co-occurring with a school name

*Needs the LLM — language interpretation a rule cannot do safely:*

- a handwritten or scanned assignment whose only signal is childlike content and a first name
- school correspondence that names neither the year nor the grade
- distinguishing a child's own work from material the school issued about the child

*Never alone — bare signals that must not establish this domain by themselves:*

- a first name in a filename
- a hyphenated year span, which is equally an academic year, a fiscal year, or a season
- a school name alone — §4.9 'A university name alone should not create a group because Columbia can appear as an authoring school, course provider, target institution, employer, research venue, or merely a cited organization.' applies to schools of every level

**Work types** — report card, progress report, permission slip, enrolment form, immunisation record, school calendar, parent-teacher conference note, child's schoolwork, school photograph order, standardised score report, IEP or plan document, supply list

**Why files in this domain group together**

- one child in one school year
- one school across the years a child attended it
- an enrolment packet issued as one set at the start of a year

**Template**

| dimension order | time first | why |
|---|---|---|
| student → school_year → record_type | no | Proposal. A family corpus is organised per child first, because the child is the retrieval key a parent actually uses; the school is often constant for years and makes a poor top level. This departs from §5.5 'For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders.' and is the reason for the open question. |

**Collides with** — where this domain and another will fight over the same file

| other domain | the confusion, and what separates them | design cite |
|---|---|---|
| `acad.course-enrollment` | both carry a school and a period; K-12 records carry a grade level and no institution-issued course code | — |
| `acad.k12-school-admission` | an acceptance letter and an enrolment form arrive together; only the admission carries a decision and an applied-to school that may differ from the attended one | §4.8 'an application packet does not silently absorb a document with a conflicting target institution' |
| `acad.accommodations` | a plan document is both a schooling record and an accommodations record; the accommodations reading is the one that carries medical support | §7.3 'passport scans, medical documents, account statements, visas, legal forms, or credentials' |
| `pers.photo-event` | a scanned child's drawing or school photo is an image with school context; the photo domain keys on capture metadata, this one on the school year | §5.4 'a Photos template may define year → event' |

**Sensitivity** — `potentially_sensitive`. Proposal, not design. These are records about a minor and frequently name other children; that is the kind of third-party identifying content §2.9 'treating addresses and message content as potentially sensitive' applies the phrase to. No handling class is assigned here.

**Open question (unresolved — for Joseph)**

> Should a family corpus branch by child first, and if so, is a child's name an acceptable folder level at all? §3.8 'It should avoid using authorship or creator identity as a destination dimension.' bars authorship as a collector but says nothing about a subject person, and this is a real-life structure decision, not a technical one.

---

### 4. Undergraduate degree programme

`acad.undergraduate-program` · **inference** · sensitivity: `none`

> Programme-level records for one undergraduate degree — requirements, declarations, audits and standing — as distinct from any single course.

**Design basis** — Extends the Academic domain of §3.11 'Academic files may use school, term, course, instructor, and work type.' upward from the course to the degree. The design names academic coursework as a launch domain (§3.15 'academic coursework, college applications, research and lab work, career and recruiting, photos and captures, and code projects') and names no programme level.

**Schema — the fields this domain, and only this domain, legitimises**

| field | type | example | reliability ceiling | why this field exists and why that ceiling |
|---|---|---|---|---|
| `school` | string | Columbia | `validated` | Shared with §3.11 'Academic files may use school, term, course, instructor, and work type.'. |
| `programme` | string | the degree programme as the school names it | `validated` | A degree-name pattern ('BA', 'BSc', 'Bachelor of') beside a validated school name. This is the fact that binds several years of courses into one thing. |
| `major_or_concentration` | string | the declared field of study | `validated` | A declaration or major term beside a school name and a degree name. It is not the course subject: a single course belongs to a department, a major is a commitment. |
| `catalogue_year` | string | the requirement year the degree is audited against | `validated` | Inference. Requirements are frozen per catalogue year, so two students in the same major graduate under different rules; a bare year would be ambiguous, so it needs the same dedicated-pattern discipline as §3.10 'Academic terms such as Spring 2025, AY 2024-25, and Michaelmas Term 2024 require dedicated patterns rather than generic parsing.'. |
| `programme_record_type` | string | degree audit | `validated` | A programme record-type term beside a school and a degree name. |
| `standing` | enum | the enrolment standing the record asserts | `llm_supported` | Standing is stated in prose in letters ('good standing', 'academic probation', 'leave of absence') and rarely in a labelled field. |

**Recognition**

*Deterministic — each rule is a pattern **plus** a corroborating context:*

- a degree-name pattern ('Bachelor of', 'BA', 'BSc') co-occurring with a gazetteer school name at a word boundary
- a programme record-type term ('degree audit', 'degree requirements', 'declaration of major', 'graduation application') co-occurring with a validated school name
- a catalogue-year pattern co-occurring with a degree name and a school name

*Needs the LLM — language interpretation a rule cannot do safely:*

- a letter whose subject is academic standing but which names no record type
- advising correspondence that discusses requirements without naming the programme
- distinguishing a completed requirement list from a prospective plan

*Never alone — bare signals that must not establish this domain by themselves:*

- a school name — §4.9 'A university name alone should not create a group because Columbia can appear as an authoring school, course provider, target institution, employer, research venue, or merely a cited organization.'
- a bare degree abbreviation, which also appears in signatures and letterheads
- a four-digit year — §3.10 'file names and documents frequently contain numbers that look like years but are course identifiers, version numbers, build numbers, ZIP codes, or other unrelated values'

**Work types** — degree audit, degree requirements sheet, declaration of major, minor declaration, graduation application, enrolment verification, academic standing letter, leave of absence request, programme handbook, commencement record

**Why files in this domain group together**

- one degree programme across all of its years
- a declaration and the audit that follows it
- successive audits of the same degree as a version family

**Template**

| dimension order | time first | why |
|---|---|---|
| school → programme → programme_record_type | no | Inference. Programme records are few and durable; a term level would scatter a handful of files across years, which is exactly what §5.5 'For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders.' warns against. |

**Collides with** — where this domain and another will fight over the same file

| other domain | the confusion, and what separates them | design cite |
|---|---|---|
| `acad.course-enrollment` | both carry school and term; programme records carry a degree name and no course code | — |
| `acad.transcript-record` | a degree audit and a transcript both list completed courses; only the transcript is issued by the registrar and carries an issue date | — |
| `acad.graduate-program` | identical record types under a different degree level; the degree name is the discriminator, and mixing them merges two distinct programmes | §4.9 'members carry irreconcilable course, institution, project, term, or purpose facts' |
| `acad.advising` | an advising note and a degree audit discuss the same requirements; the audit is a registrar artifact, the note is a conversation record | — |

**Sensitivity** — `none`. Programme records concern the corpus holder and name no third parties by default. A standing or probation letter may warrant different treatment, but that is a handling decision made elsewhere.

---

### 5. Graduate programme milestones

`acad.graduate-program` · **inference** · sensitivity: `none`

> Records for one graduate degree's gated milestones — candidacy, qualifying and comprehensive exams, prospectus, and progress review.

**Design basis** — Extends the Academic domain of §3.11 'Academic files may use school, term, course, instructor, and work type.' to a degree level the design does not name. Graduate work sits between the design's academic coursework and research launch domains: §3.15 'academic coursework, college applications, research and lab work, career and recruiting, photos and captures, and code projects'.

**Schema — the fields this domain, and only this domain, legitimises**

| field | type | example | reliability ceiling | why this field exists and why that ceiling |
|---|---|---|---|---|
| `school` | string | the degree-granting institution | `validated` | Shared with §3.11 'Academic files may use school, term, course, instructor, and work type.'. |
| `programme` | string | the graduate programme or department | `validated` | A graduate-degree pattern ('PhD', 'MSc', 'Master of') beside a validated school name. |
| `milestone` | enum | qualifying exam | `validated` | Inference, and the field that makes this domain distinct from the undergraduate one: a graduate degree is a sequence of named gates, and the milestone is the retrieval key. A milestone term beside a graduate-degree name is a strong, checkable pair. |
| `advisor` | string | the faculty member supervising the degree | `direct` | Read from a labelled slot on a form. It is a role, not authorship — the same distinction §3.8 'such as authored_by and target_school' draws — and it is not a folder dimension. |
| `milestone_outcome` | enum | the recorded result of a gate | `user_confirmed` | A pass, fail, revise or defer outcome changes what a person keeps and how they feel about it; inferring it from prose would be both unreliable and intrusive, so only the user establishes it. |
| `milestone_date` | date | the date a gate was held | `validated` | Narrow date extraction only: §3.10 'file names and documents frequently contain numbers that look like years but are course identifiers, version numbers, build numbers, ZIP codes, or other unrelated values'. |

**Recognition**

*Deterministic — each rule is a pattern **plus** a corroborating context:*

- a milestone term ('qualifying exam', 'comprehensive exam', 'candidacy', 'prospectus defense', 'progress review') co-occurring with a graduate-degree name or a validated school name
- a graduate-degree pattern ('PhD', 'DPhil', 'Master of') co-occurring with a department or programme name at a word boundary
- an advisor-labelled slot ('Advisor:', 'Supervisor:') co-occurring with a milestone term

*Needs the LLM — language interpretation a rule cannot do safely:*

- a reading list that is a qualifying-exam artifact only by context
- committee correspondence that never names the milestone
- distinguishing a milestone document from an ordinary graduate course paper

*Never alone — bare signals that must not establish this domain by themselves:*

- the word 'exam', which is the most common word in the coursework corpus
- an advisor's name — §3.8 'It should avoid using authorship or creator identity as a destination dimension.'
- a school name — §4.9 'A university name alone should not create a group because Columbia can appear as an authoring school, course provider, target institution, employer, research venue, or merely a cited organization.'

**Work types** — qualifying exam, comprehensive exam, reading list, candidacy form, prospectus, committee form, annual progress review, milestone approval, programme handbook, funding continuation letter

**Why files in this domain group together**

- one milestone with its form, reading list and outcome
- one degree across its whole sequence of gates
- successive drafts of a prospectus as a version family

**Template**

| dimension order | time first | why |
|---|---|---|
| school → programme → milestone | no | Inference. The milestone is the leaf a person actually looks for, and it satisfies §5.5 'a parent dimension should provide the context required to understand the child': 'candidacy' means nothing until the programme is known. No term level, because milestones are named events rather than recurring periods. |

**Collides with** — where this domain and another will fight over the same file

| other domain | the confusion, and what separates them | design cite |
|---|---|---|
| `acad.thesis-dissertation` | a prospectus is a milestone artifact and the first chapter of the dissertation; the dissertation domain owns the manuscript, this one owns the gate | — |
| `acad.course-enrollment` | a graduate course paper and a qualifying exam are both written work; only the course paper carries a course code | §3.5 'BUSIB 4300 becomes a course fact only when the engine finds a course-code pattern together with academic context such as "syllabus," "lecture," "credits," "instructor," or "semester."' |
| `res.research-project` | a graduate corpus contains both; the milestone is institutional, the project is intellectual, and one advisor covers both | §5.4 'a Research template may define project → stage → artifact type' |
| `acad.undergraduate-program` | identical record types at a different degree level; merging them is the conflicting-fact case the design refuses | §4.9 'members carry irreconcilable course, institution, project, term, or purpose facts' |

**Sensitivity** — `none`. Milestone records concern the corpus holder. Committee correspondence naming other people is the ordinary third-party case and no handling class is assigned here.

**Open question (unresolved — for Joseph)**

> Does a graduate corpus want one branch per degree with research nested inside it, or two sibling top-level areas — Academics and Research — that a single advisor's material is split across? §5.1 'Academics, Applications, Research, Career, Personal Records, Finance and Administration, Photos and Captures, Code and Projects, and Media or Miscellaneous Personal Material' lists both as separate candidate areas and does not say how a doctoral student should resolve the overlap.

---

### 6. Professional degree programme

`acad.professional-school` · **proposal** · sensitivity: `none`

> Programme records for a licensure-track professional degree, where the degree is gated by an external board rather than only by the school.

**Design basis** — none. `design_cite` is null: no design sentence names this domain. It is a proposal for Joseph.

**Schema — the fields this domain, and only this domain, legitimises**

| field | type | example | reliability ceiling | why this field exists and why that ceiling |
|---|---|---|---|---|
| `school` | string | the professional school | `validated` | A gazetteer school name at a word boundary. |
| `programme` | string | the professional degree | `validated` | A professional-degree pattern ('JD', 'MD', 'MBA', 'DDS', 'PharmD') beside a validated school name. |
| `cohort` | string | the entering class the holder belongs to | `validated` | Proposal. Professional programmes are lock-step: the cohort, not the term, is what a person's material belongs to, and classmates share an identical course sequence. |
| `licensing_body` | string | the board that credentials the degree | `validated` | Proposal, and the field that separates this domain from a generic graduate programme: the external body's requirements are a parallel record the school does not own. |
| `board_exam` | string | the licensure examination the programme prepares for | `validated` | A board-exam name beside a professional-degree name. It anchors a large body of preparation material that has no course code and would otherwise be unfilable. |
| `programme_stage` | enum | the year or phase of the programme | `llm_supported` | Stages are named locally and inconsistently ('1L', 'preclinical', 'core year'), so a rule cannot enumerate them safely. |

**Recognition**

*Deterministic — each rule is a pattern **plus** a corroborating context:*

- a professional-degree pattern ('JD', 'MD', 'MBA', 'DDS', 'PharmD') co-occurring with a gazetteer school name at a word boundary
- a board-exam name co-occurring with a professional-degree name or a licensing-body name
- a licensing-body name co-occurring with a registration, eligibility or requirement term
- a cohort pattern ('Class of', a lettered or numbered section) co-occurring with a professional-degree name and a gazetteer school name

*Needs the LLM — language interpretation a rule cannot do safely:*

- a case brief or problem set that identifies the discipline but not the programme
- board-preparation material with no institutional marking at all
- distinguishing programme-issued material from a commercial preparation product

*Never alone — bare signals that must not establish this domain by themselves:*

- the two-letter degree abbreviations, which collide with initials and with common words
- a school name — §4.9 'A university name alone should not create a group because Columbia can appear as an authoring school, course provider, target institution, employer, research venue, or merely a cited organization.'
- a discipline term such as 'law' or 'medicine', which appears across an entire corpus

**Work types** — programme handbook, cohort schedule, board registration, board score report, licensure eligibility letter, case brief, board preparation material, professional responsibility record, externship agreement, class rank notice

**Why files in this domain group together**

- one cohort through one programme
- a board registration with its admission ticket and score report
- one board examination across its preparation material

**Template**

| dimension order | time first | why |
|---|---|---|
| school → programme → programme_stage | no | Proposal. School and programme are the durable parents; stage is the leaf people navigate by. The licensing body and board exam are metadata rather than levels, because a person holds few of each and a level with one child is the case §5.9 'It should also support a scoped General or Other branch within a meaningful parent.' context warns about. |

**Collides with** — where this domain and another will fight over the same file

| other domain | the confusion, and what separates them | design cite |
|---|---|---|
| `acad.clinical-rotation` | a medical or dental programme produces both; the rotation carries a site and a block, the programme record does not | — |
| `acad.graduate-program` | both are post-baccalaureate; only this one carries an external licensing body | — |
| `acad.standardized-testing` | an admissions test and a licensure board exam are both score reports; the admissions test precedes the programme and belongs to an application | — |
| `career.job-application` | professional-school recruiting is heavy and produces employer material inside a school corpus; the Career template keys on company | §5.4 'a Career template may define company → role or recruiting cycle → document type' |

**Sensitivity** — `none`. Programme records concern the corpus holder. A board score report is personal but is not material the design names as potentially sensitive, and no handling class is assigned here.

---

### 7. Continuing education and professional development

`acad.continuing-education` · **proposal** · sensitivity: `none`

> Credit-bearing units earned to keep a professional licence or certification current.

**Design basis** — none. `design_cite` is null: no design sentence names this domain. It is a proposal for Joseph.

**Schema — the fields this domain, and only this domain, legitimises**

| field | type | example | reliability ceiling | why this field exists and why that ceiling |
|---|---|---|---|---|
| `credentialing_body` | string | the body that requires the units | `validated` | Proposal, and the organising fact: this material exists because a body demands it, and the same course can satisfy two bodies with different reporting. |
| `credential` | string | the licence or certification being maintained | `validated` | A credential name or number pattern beside a credentialing-body name. |
| `reporting_period` | string | the renewal cycle the units count toward | `validated` | Proposal. A renewal cycle is a span, not a semester; it needs its own pattern for the reason §3.10 'Academic terms such as Spring 2025, AY 2024-25, and Michaelmas Term 2024 require dedicated patterns rather than generic parsing.' gives for academic terms. |
| `activity` | string | the course, seminar or webinar attended | `validated` | A provider or activity title beside a unit term ('CEU', 'CPD', 'contact hours'). |
| `units` | string | the unit type the certificate records | `direct` | Read from a labelled slot on a completion certificate. The unit type is recorded; no count is asserted here. |
| `provider` | string | the organisation that delivered the activity | `validated` | A provider name beside an activity title and a unit term. It is a role, not authorship. |

**Recognition**

*Deterministic — each rule is a pattern **plus** a corroborating context:*

- a unit term ('CEU', 'CPD', 'CME', 'contact hours', 'continuing education') co-occurring with a completion or attendance term
- a credentialing-body name co-occurring with a renewal, reporting or compliance term
- a credential-number pattern co-occurring with a credentialing-body name at a word boundary
- an activity title in the document title zone co-occurring with a unit term and a named provider — §3.7 'a value in a filename or document title carries more meaning than the same value in a footer or a late body-page reference'

*Needs the LLM — language interpretation a rule cannot do safely:*

- a webinar certificate that names neither the body nor the credential
- an agenda that is continuing-education material only because of who the audience is
- deciding whether a conference counts as a reportable activity

*Never alone — bare signals that must not establish this domain by themselves:*

- the word 'certificate', which spans this domain, credentials, and residual records
- a credential-number-shaped token with no body name nearby
- a provider name, which is frequently a well-known company appearing for unrelated reasons

**Work types** — completion certificate, attendance record, unit transcript, renewal application, renewal receipt, course agenda, compliance attestation, provider invoice, self-study log

**Why files in this domain group together**

- one reporting period for one credential
- an activity with its certificate and its receipt
- one credentialing body across all of its cycles

**Template**

| dimension order | time first | why |
|---|---|---|
| credential → reporting_period → activity | no | Proposal. The credential is what a person is maintaining and is the durable parent; the reporting period is the audit unit and must be enumerable, because renewal is checked per cycle. This is the one shape in this file where a period sits above the individual item, and it does so because the period is a compliance boundary rather than a calendar. |

**Collides with** — where this domain and another will fight over the same file

| other domain | the confusion, and what separates them | design cite |
|---|---|---|
| `acad.self-study` | the same online course appears in both; only continuing education carries a credentialing body and a reporting period | — |
| `acad.credential-certificate` | a completion certificate and a credential certificate look alike; the credential is the thing maintained, the completion certificate is an input to maintaining it | — |
| `career.continuing-education` | professional development is often career material; this domain is bounded by a licence requirement, career material is not | §5.4 'a Career template may define company → role or recruiting cycle → document type' |
| `fin.financial-records` | renewal fees and provider invoices are financial records with continuing-education context; finance is a domain the design protects first | §3.15 'Finance, identity, medical, and legal material should be implemented first as safety domains' |

**Sensitivity** — `none`. Completion records concern the corpus holder and name no third parties. A licence number is an identifier but is not material the design names as potentially sensitive; no handling class is assigned here.

**Open question (unresolved — for Joseph)**

> Should continuing education sit under Academics at all, or under a career or personal-administration area? §5.1 'Academics, Applications, Research, Career, Personal Records, Finance and Administration, Photos and Captures, Code and Projects, and Media or Miscellaneous Personal Material' offers several plausible parents and the answer depends on how the person thinks about their licence, not on the files.

---

### 8. Bootcamp or intensive cohort programme

`acad.bootcamp-cohort` · **proposal** · sensitivity: `none`

> A short, non-degree, cohort-based intensive programme with no institutional course codes and no term calendar.

**Design basis** — none. `design_cite` is null: no design sentence names this domain. It is a proposal for Joseph.

**Schema — the fields this domain, and only this domain, legitimises**

| field | type | example | reliability ceiling | why this field exists and why that ceiling |
|---|---|---|---|---|
| `provider` | string | the organisation running the programme | `validated` | Proposal, and the anchor: with no accreditation and no course code, the provider name is the only stable institutional fact. |
| `programme` | string | the track or curriculum name | `validated` | A track name beside a provider name at a word boundary. |
| `cohort` | string | the batch identifier | `validated` | Proposal. Cohorts are the native unit ('Cohort 14', a start month), they replace the term entirely, and a bare cohort number is exactly the kind of value §3.10 'file names and documents frequently contain numbers that look like years but are course identifiers, version numbers, build numbers, ZIP codes, or other unrelated values' warns not to read as a date. |
| `module` | string | the unit of curriculum | `validated` | A module or week term beside a provider or track name. Modules substitute for courses and carry no institutional code. |
| `deliverable_type` | string | the kind of work produced | `validated` | A deliverable term beside a module or track name. Bootcamp output is disproportionately project and portfolio work rather than exams. |

**Recognition**

*Deterministic — each rule is a pattern **plus** a corroborating context:*

- a provider name co-occurring with a cohort or module term at a word boundary
- a bootcamp vocabulary term ('cohort', 'sprint', 'capstone', 'career services') co-occurring with a named track
- a module or week pattern co-occurring with a provider name
- a deliverable term ('capstone', 'portfolio piece', 'code review', 'exercise') co-occurring with a named module or track

*Needs the LLM — language interpretation a rule cannot do safely:*

- a project repository that is bootcamp coursework only by context
- material from a programme whose name is a common word
- distinguishing a capstone from ordinary personal project work

*Never alone — bare signals that must not establish this domain by themselves:*

- the word 'cohort', which also appears in research and employment material
- a week number
- a provider name that is also a widely used product name

**Work types** — curriculum outline, module exercise, capstone project, code review, cohort schedule, career-services material, certificate of completion, enrolment agreement, mentor feedback

**Why files in this domain group together**

- one cohort of one programme
- a capstone across its drafts and its repository
- one module with its exercises and its feedback

**Template**

| dimension order | time first | why |
|---|---|---|
| provider → programme → module | no | Proposal. Provider and programme are the only durable names available; cohort is metadata rather than a level because most people attend one. Module is the leaf, and satisfies §5.5 'a parent dimension should provide the context required to understand the child' in the same way work type does for a course. |

**Collides with** — where this domain and another will fight over the same file

| other domain | the confusion, and what separates them | design cite |
|---|---|---|
| `acad.course-enrollment` | both produce assignments; a bootcamp has no institution-issued course code and no academic term, which is precisely what the course rule requires | §3.5 'BUSIB 4300 becomes a course fact only when the engine finds a course-code pattern together with academic context such as "syllabus," "lecture," "credits," "instructor," or "semester."' |
| `soft.source-project` | a capstone is simultaneously a repository and coursework; the code domain keys on repository markers, this one on the provider and module | — |
| `career.job-search-campaign` | bootcamps bundle career services, so employer material appears inside the programme corpus | §5.4 'a Career template may define company → role or recruiting cycle → document type' |
| `acad.self-study` | both are non-degree learning; only the bootcamp has a cohort and a provider relationship | — |

**Sensitivity** — `none`. Programme material concerns the corpus holder. An enrolment agreement is a contract but is not material the design names as potentially sensitive; no handling class is assigned here.

---

### 9. Self-directed study

`acad.self-study` · **proposal** · sensitivity: `none`

> Learning the holder organised for themselves — online courses, textbook work, reading programmes — with no enrolling institution.

**Design basis** — none. `design_cite` is null: no design sentence names this domain. It is a proposal for Joseph.

**Schema — the fields this domain, and only this domain, legitimises**

| field | type | example | reliability ceiling | why this field exists and why that ceiling |
|---|---|---|---|---|
| `subject` | string | the field being studied | `llm_supported` | Proposal. With no institution and no code, the subject is only recoverable by reading, which is exactly the case §3.5 'The LLM creates LLM-supported facts only when a file requires language interpretation that rules cannot resolve safely.' describes. |
| `source` | string | the platform, textbook or series being worked through | `validated` | A platform or publisher name beside a lesson, chapter or module term. The source is the strongest available anchor and the only one likely to be explicit. |
| `course_title` | string | the title of the online course or book | `direct` | Read from a document title, which §3.5 'such as a content hash, EXIF timestamp, a document title, or a labeled form field' makes direct. It is not a course in the Academic sense: no institution issued it. |
| `progress_unit` | string | the chapter, lesson or problem number | `validated` | A chapter or lesson pattern beside a source or title. It is the sequence a person navigates by. |
| `study_artifact_type` | string | the kind of material | `validated` | An artifact term beside a source name. Self-study output is notes, exercises and solutions, not graded work. |

**Recognition**

*Deterministic — each rule is a pattern **plus** a corroborating context:*

- a platform or publisher name co-occurring with a lesson, chapter or module pattern
- a chapter or lesson pattern co-occurring with a book or course title in the document title zone — §3.7 'a value in a filename or document title carries more meaning than the same value in a footer or a late body-page reference'
- a self-study vocabulary term ('exercises', 'solutions', 'problem set') co-occurring with a named textbook or platform

*Needs the LLM — language interpretation a rule cannot do safely:*

- personal notes whose subject is clear to a reader and to nothing else
- distinguishing self-study notes from course notes for an enrolled course
- a saved article that may be study material or §7.3 'papers, articles, reports, and saved PDFs that appear to be reading material but have no active research, course, or project association'

*Never alone — bare signals that must not establish this domain by themselves:*

- a chapter number
- the word 'notes'
- a platform name, which appears in many unrelated downloads

**Work types** — course notes, exercise solutions, textbook exercises, flashcard deck, study plan, downloaded lecture, certificate of completion, practice problems, reading log

**Why files in this domain group together**

- one course or book worked through in sequence
- one subject across several sources
- a study plan with the material it schedules

**Template**

| dimension order | time first | why |
|---|---|---|
| subject → source → study_artifact_type | no | Proposal. Subject leads because a self-studier returns by topic, not by platform; the source is the concrete container beneath it. This follows §5.5 'For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders.' directly — no time level at all, because self-study has no period. |

**Collides with** — where this domain and another will fight over the same file

| other domain | the confusion, and what separates them | design cite |
|---|---|---|
| `acad.course-enrollment` | both produce notes and problem sets; enrolment carries an institution-issued course code and a term, and self-study carries neither | §3.5 'BUSIB 4300 becomes a course fact only when the engine finds a course-code pattern together with academic context such as "syllabus," "lecture," "credits," "instructor," or "semester."' |
| `acad.continuing-education` | an online course can be either; continuing education carries a credentialing body and a reporting period | — |
| `acad.standardized-testing` | test preparation is self-study aimed at a specific sitting; the testing domain carries a registration and a score report | — |
| `acad.bootcamp-cohort` | both are non-degree; only the bootcamp has a provider relationship and a cohort | — |

**Sensitivity** — `none`. Self-study material concerns the corpus holder only.

**Open question (unresolved — for Joseph)**

> Self-study has no institution and often no clear boundary against saved reading. Should it be an Academics branch, or should unanchored study material fall to a residual area? §7.3 'papers, articles, reports, and saved PDFs that appear to be reading material but have no active research, course, or project association' already describes an overlapping residual template.

---

### 10. Laboratory course work

`acad.lab-course` · **inference** · sensitivity: `none`

> The laboratory component of a course — sessions, protocols, notebooks and reports — which carries an experiment identity a lecture course does not.

**Design basis** — Extends the Academic domain of §3.11 'Academic files may use school, term, course, instructor, and work type.'. The design names research and lab work as its own launch domain (§3.15 'academic coursework, college applications, research and lab work, career and recruiting, photos and captures, and code projects') with fields §3.11 'Research files may use project, stage, artifact type, lab, and venue.'; a lab course sits between the two and is named as neither.

**Schema — the fields this domain, and only this domain, legitimises**

| field | type | example | reliability ceiling | why this field exists and why that ceiling |
|---|---|---|---|---|
| `school` | string | Columbia | `validated` | Shared with §3.11 'Academic files may use school, term, course, instructor, and work type.'. |
| `term` | string | Spring 2026 | `validated` | §3.10 'Academic terms such as Spring 2025, AY 2024-25, and Michaelmas Term 2024 require dedicated patterns rather than generic parsing.'. |
| `subject` | string | the parent course code | `validated` | §3.5 'BUSIB 4300 becomes a course fact only when the engine finds a course-code pattern together with academic context such as "syllabus," "lecture," "credits," "instructor," or "semester."'. |
| `lab_section` | string | the section identifier for the lab meeting | `validated` | Inference. A lab section is a separate meeting from the lecture, with its own instructor and schedule; a section pattern beside a validated course code is checkable. |
| `experiment` | string | the experiment or lab number the work belongs to | `validated` | Inference, and the field that makes this domain distinct: reports, data and pre-labs cluster by experiment, not by week. An experiment pattern beside a validated course code is the same rule shape as the course rule itself. |
| `lab_artifact_type` | string | the kind of lab material | `validated` | An artifact term ('pre-lab', 'protocol', 'lab report', 'raw data') beside a validated course code or experiment identifier. |

**Recognition**

*Deterministic — each rule is a pattern **plus** a corroborating context:*

- an experiment pattern ('Lab 4', 'Experiment 3') co-occurring with a validated course code
- a lab artifact term ('pre-lab', 'lab report', 'protocol', 'lab notebook') co-occurring with a validated course code or an academic-term pattern
- a lab-section pattern co-occurring with a validated course code
- a safety or training term ('lab safety training', 'chemical hygiene') co-occurring with a validated school name

*Needs the LLM — language interpretation a rule cannot do safely:*

- a data file whose only lab signal is its column structure
- a report that reads as either coursework or research output
- a protocol that could be the course's or the lab group's

*Never alone — bare signals that must not establish this domain by themselves:*

- the word 'lab', which is also a research group, a company, and a directory name
- a bare experiment number
- a data file extension

**Work types** — pre-lab, lab protocol, lab notebook page, raw data, lab report, lab safety training record, equipment sign-out, post-lab questions, lab practical

**Why files in this domain group together**

- one experiment with its protocol, data and report
- one lab section in one term
- a lab report across its drafts as a version family

**Template**

| dimension order | time first | why |
|---|---|---|
| school → term → subject → experiment | no | Inference, and a deliberate substitution: it is the Academic template of §5.4 'An Academic template may define school → term → course → work type' with experiment replacing work type as the leaf, because in a lab course the experiment is what makes the report findable — which is the same argument §5.5 'A work type such as Homework 3 is meaningful only after the course is known, and a course code may require the school or term to disambiguate it.' makes for work type in a lecture course. |

**Collides with** — where this domain and another will fight over the same file

| other domain | the confusion, and what separates them | design cite |
|---|---|---|
| `acad.course-enrollment` | a lab course is a course; the lab reading is established by an experiment identifier or a lab artifact term, never by the course code alone | — |
| `res.research-project` | a lab report and a research artifact are the same document shape; the research reading carries a project identifier and a lab, this one carries a course code | §3.11 'Research files may use project, stage, artifact type, lab, and venue.' |
| `acad.undergrad-research` | both produce protocols and data under a named lab; the course version carries a course code and a term, the placement version carries a supervisor and no code | — |
| `acad.thesis-dissertation` | lab data feeds a thesis; the data file belongs to whichever group its own evidence supports, not to both by inheritance | — |

**Sensitivity** — `none`. Lab coursework carries nothing the design names as potentially sensitive. Human-subject coursework would be a different matter and is not assumed here.

---

### 11. Teaching assistantship

`acad.teaching-assistantship` · **proposal** · sensitivity: `potentially_sensitive`

> An appointment to assist in teaching a course — a job and a course role at once, held by someone who is also a student.

**Design basis** — none. `design_cite` is null: no design sentence names this domain. It is a proposal for Joseph.

**Schema — the fields this domain, and only this domain, legitimises**

| field | type | example | reliability ceiling | why this field exists and why that ceiling |
|---|---|---|---|---|
| `school` | string | the appointing institution | `validated` | A gazetteer school name at a word boundary. |
| `term` | string | the term of the appointment | `validated` | §3.10 'Academic terms such as Spring 2025, AY 2024-25, and Michaelmas Term 2024 require dedicated patterns rather than generic parsing.'. |
| `subject` | string | the course assisted | `validated` | §3.5 'BUSIB 4300 becomes a course fact only when the engine finds a course-code pattern together with academic context such as "syllabus," "lecture," "credits," "instructor," or "semester."'. |
| `appointment` | string | the appointment title the school issues | `direct` | Read from a labelled slot on an appointment letter, which §3.5 'such as a content hash, EXIF timestamp, a document title, or a labeled form field' makes direct. It is the fact that separates this from simply taking the course. |
| `supervising_instructor` | string | the faculty member the assistant reports to | `direct` | Read from a labelled slot. A role, not authorship: §3.8 'such as authored_by and target_school'. |
| `assistantship_duty_type` | string | the kind of duty the file records | `validated` | A duty term ('section', 'grading', 'office hours', 'lab supervision') beside a validated course code. |

**Recognition**

*Deterministic — each rule is a pattern **plus** a corroborating context:*

- an appointment term ('teaching assistant', 'TA', 'GSI', 'reader', 'grader') co-occurring with a validated course code or a school name at a word boundary
- an appointment-letter term ('appointment', 'offer of appointment', 'stipend', 'tuition remission') co-occurring with a school name and an academic-term pattern
- a duty term ('section', 'grading', 'office hours') co-occurring with a validated course code and an appointment term

*Needs the LLM — language interpretation a rule cannot do safely:*

- grading material that could belong to the assistant or to the instructor of record
- correspondence establishing the role without naming it
- distinguishing a section the holder taught from one they attended

*Never alone — bare signals that must not establish this domain by themselves:*

- the two-letter abbreviation TA, which is a substring risk of exactly the kind §3.7 'names such as MIT can be found inside "submit,"' describes
- a course code with no appointment evidence
- possession of grading material, which is equally the instructor's

**Work types** — appointment letter, section plan, grading record, answer key, office-hours log, student email thread, training material, timesheet, evaluation of the assistant

**Why files in this domain group together**

- one appointment for one course in one term
- a section across the weeks it ran
- an appointment letter with its timesheets

**Template**

| dimension order | time first | why |
|---|---|---|
| school → term → subject → assistantship_duty_type | no | Proposal. It follows the Academic order of §5.4 'An Academic template may define school → term → course → work type' because the appointment is scoped to one course in one term, and the duty type is the leaf that satisfies §5.5 'a parent dimension should provide the context required to understand the child'. |

**Collides with** — where this domain and another will fight over the same file

| other domain | the confusion, and what separates them | design cite |
|---|---|---|
| `acad.course-enrollment` | a graduate student assisting one course and taking another produces two corpora with the same school and term; the appointment letter is the discriminator | — |
| `acad.course-instruction` | both hold grading material for the same course; only the assistantship carries an appointment and a supervising instructor | — |
| `acad.campus-employment` | an assistantship is campus employment; its distinguishing evidence is a course code, which no other campus job carries | — |
| `acad.graduate-program` | an assistantship is often the funding attached to a degree, so the offer letter carries both readings | — |

**Sensitivity** — `potentially_sensitive`. Proposal, not design. Grading records and student email threads carry other people's names, marks and messages — the material §2.9 'treating addresses and message content as potentially sensitive' applies the phrase to. No handling class is assigned here.

**Open question (unresolved — for Joseph)**

> Does a teaching assistantship belong under Academics with the holder's own coursework, under a Career area as employment, or split between them? The design's candidate areas (§5.1 'Academics, Applications, Research, Career, Personal Records, Finance and Administration, Photos and Captures, Code and Projects, and Media or Miscellaneous Personal Material') make all three available and the files support all three.

---

### 12. Tutoring engagements

`acad.tutoring` · **proposal** · sensitivity: `potentially_sensitive`

> One-to-one or small-group instruction outside a course, held by either the tutor or the person tutored.

**Design basis** — none. `design_cite` is null: no design sentence names this domain. It is a proposal for Joseph.

**Schema — the fields this domain, and only this domain, legitimises**

| field | type | example | reliability ceiling | why this field exists and why that ceiling |
|---|---|---|---|---|
| `subject` | string | the subject tutored | `llm_supported` | Proposal. Tutoring material rarely names a code; the subject is usually recoverable only by reading the material, which is §3.5 'The LLM creates LLM-supported facts only when a file requires language interpretation that rules cannot resolve safely.'. |
| `engagement` | string | the named tutoring relationship or client | `user_confirmed` | The engagement is identified by a person's name in almost every real case, and a person's name must not be guessed onto a file. Only the user establishes it. |
| `tutoring_role` | enum | whether the holder tutored or was tutored | `llm_supported` | Proposal, and the field the whole domain turns on: the same worksheet means opposite things in the two directions, and only prose distinguishes them. |
| `session` | string | the session the material belongs to | `validated` | A session or date pattern beside a subject or engagement term — narrow date extraction only, per §3.10 'file names and documents frequently contain numbers that look like years but are course identifiers, version numbers, build numbers, ZIP codes, or other unrelated values'. |
| `provider` | string | the tutoring service, when one is involved | `validated` | A service name beside a tutoring term at a word boundary. |

**Recognition**

*Deterministic — each rule is a pattern **plus** a corroborating context:*

- a tutoring term ('tutoring', 'tutor', 'session notes', 'lesson plan') co-occurring with a subject term or a named service
- a service name co-occurring with an invoice, schedule or session term
- a session-date pattern co-occurring with a tutoring term in the document title zone — §3.7 'a value in a filename or document title carries more meaning than the same value in a footer or a late body-page reference'

*Needs the LLM — language interpretation a rule cannot do safely:*

- a worksheet that is tutoring material only because of who made it for whom
- establishing the direction of the relationship from correspondence
- distinguishing tutoring notes from the holder's own study notes

*Never alone — bare signals that must not establish this domain by themselves:*

- a person's name in a filename — §3.8 'It should avoid using authorship or creator identity as a destination dimension.'
- the word 'session'
- a worksheet, which is indistinguishable from coursework on its face

**Work types** — lesson plan, session notes, worksheet, practice problems, progress report, schedule, invoice, parent correspondence, diagnostic assessment

**Why files in this domain group together**

- one engagement across its sessions
- one subject across engagements
- a session with its plan, worksheet and notes

**Template**

| dimension order | time first | why |
|---|---|---|
| subject → engagement → session | no | Proposal. Subject leads because it is the reusable dimension — a tutor reuses material across students — and engagement is the concrete container beneath it. Whether a person's name may be a folder level is the open question below. |

**Collides with** — where this domain and another will fight over the same file

| other domain | the confusion, and what separates them | design cite |
|---|---|---|
| `acad.course-enrollment` | tutoring material for a course carries the same subject and often the same problems; only tutoring carries an engagement or a session | — |
| `acad.standardized-testing` | test-preparation tutoring carries a test name and a sitting date, which pulls it toward the testing domain | — |
| `acad.campus-employment` | campus tutoring centres pay tutors; the employment reading carries a pay period, the tutoring reading carries sessions | — |
| `acad.k12-schooling` | a parent's corpus holds both the child's school records and the tutor's material about the same child | — |

**Sensitivity** — `potentially_sensitive`. Proposal, not design. Tutoring records describe another person's academic difficulties by name, and frequently a minor's — third-party identifying content of the kind §2.9 'treating addresses and message content as potentially sensitive' applies the phrase to. No handling class is assigned here.

**Open question (unresolved — for Joseph)**

> May a tutee's name be a folder level? §3.8 'It should avoid using authorship or creator identity as a destination dimension.' forbids the author as a collector but is silent on the subject person, and this decides whether real names appear in a visible path.

---

### 13. Curriculum and programme development

`acad.curriculum-development` · **proposal** · sensitivity: `none`

> Designing a course or programme before anyone teaches it — proposals, outcomes, mappings and approvals.

**Design basis** — none. `design_cite` is null: no design sentence names this domain. It is a proposal for Joseph.

**Schema — the fields this domain, and only this domain, legitimises**

| field | type | example | reliability ceiling | why this field exists and why that ceiling |
|---|---|---|---|---|
| `school` | string | the institution the curriculum is for | `validated` | A gazetteer school name at a word boundary. |
| `programme` | string | the programme or department the work sits under | `validated` | A programme or department name beside a curriculum term. |
| `curriculum_unit` | string | the course or module being designed | `validated` | Proposal. The unit may not have a code yet — that is exactly what distinguishes design work from delivery — so it is recognised by a proposal or draft term beside a programme name. |
| `learning_outcome` | string | a stated outcome the unit must meet | `llm_supported` | Outcomes are prose statements, not labelled fields; extracting one requires reading. |
| `approval_stage` | enum | where the proposal sits in governance | `validated` | An approval term ('proposal', 'committee review', 'approved', 'catalogue copy') beside a curriculum unit or programme name. |
| `development_artifact_type` | string | the kind of design document | `validated` | An artifact term beside a curriculum or programme name. |

**Recognition**

*Deterministic — each rule is a pattern **plus** a corroborating context:*

- a curriculum term ('curriculum', 'course proposal', 'learning outcomes', 'programme review', 'catalogue copy') co-occurring with a school or programme name at a word boundary
- an approval term ('curriculum committee', 'faculty senate', 'approved') co-occurring with a named course or programme
- an outcomes-mapping term ('mapped to', 'outcome', 'competency') co-occurring with a programme name

*Needs the LLM — language interpretation a rule cannot do safely:*

- a syllabus draft that is design work rather than a delivered syllabus
- a mapping document whose framework is implicit
- distinguishing programme review from accreditation self-study

*Never alone — bare signals that must not establish this domain by themselves:*

- the word 'curriculum', which appears in job descriptions and marketing
- a school name — §4.9 'A university name alone should not create a group because Columbia can appear as an authoring school, course provider, target institution, employer, research venue, or merely a cited organization.'
- a syllabus, which is far more often a delivery artifact than a design artifact

**Work types** — course proposal, syllabus draft, learning outcomes document, curriculum map, programme review, committee minutes, catalogue copy, assessment plan, textbook evaluation

**Why files in this domain group together**

- one course proposal through its approval stages
- one programme review cycle
- a syllabus draft across its versions

**Template**

| dimension order | time first | why |
|---|---|---|
| school → programme → curriculum_unit | no | Proposal. No term level, because design work is not scoped to a delivery period — this is a document domain of the kind §5.5 'For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders.' describes. |

**Collides with** — where this domain and another will fight over the same file

| other domain | the confusion, and what separates them | design cite |
|---|---|---|
| `acad.course-instruction` | a syllabus draft is design work and a syllabus is delivery; only the delivered version carries a term | — |
| `acad.accreditation-institutional` | outcomes mapping serves both; accreditation carries an accreditor and a review cycle, curriculum work does not | — |
| `acad.course-enrollment` | a proposed course and a taken course share a name; a proposal has no term and often no code | §3.5 'BUSIB 4300 becomes a course fact only when the engine finds a course-code pattern together with academic context such as "syllabus," "lecture," "credits," "instructor," or "semester."' |
| `acad.advising` | a requirements sheet is produced by curriculum work and consumed by advising | — |

**Sensitivity** — `none`. Curriculum documents are institutional and name no individuals as subjects.

---

### 14. College application packet

`acad.college-application` · **design** · sensitivity: `potentially_sensitive`

> Everything submitted, or assembled to be submitted, to one target institution for one admissions cycle.

**Design basis** — §3.11 'College application files may use target university, application cycle, application document type, and purpose.'; §5.4 'an Applications template may define target institution → application cycle → document type'; §4.8 'an application packet does not silently absorb a document with a conflicting target institution'; §3.9 'A university application packet can contain an identification document, transcript, resume, certificate, and academic abstract.'

**Schema — the fields this domain, and only this domain, legitimises**

| field | type | example | reliability ceiling | why this field exists and why that ceiling |
|---|---|---|---|---|
| `target_university` | string | UChicago | `validated` | Named in §3.11 'College application files may use target university, application cycle, application document type, and purpose.'. It is a role distinct from the school the applicant attends: §3.8 'An application essay can mention the author's current school and the university to which the essay is addressed.'. Reaches validated only through a gazetteer match at a word boundary together with admissions context, because §4.9 'A university name alone should not create a group because Columbia can appear as an authoring school, course provider, target institution, employer, research venue, or merely a cited organization.'. |
| `application_cycle` | string | the admissions cycle applied in | `validated` | Named in §3.11 'College application files may use target university, application cycle, application document type, and purpose.'. The design's own worked case is a document that has the institution but not the cycle: §4.1 'a document called Columbia Essay.docx may identify a target university but omit the admissions cycle'. |
| `application_document_type` | string | supplemental essay | `validated` | Named in §3.11 'College application files may use target university, application cycle, application document type, and purpose.', and it is the leaf of the design's own template, §5.4 'an Applications template may define target institution → application cycle → document type'. |
| `purpose` | string | university application | `validated` | Named in §3.11 'College application files may use target university, application cycle, application document type, and purpose.' and made first-class by §3.9 'Topic answers what a file is about, while purpose answers what the file was for.'. It reaches validated by rule only on the strong support the design names: §3.9 'Purpose may be supported strongly by an existing user-created folder name or explicit language in a form or portal.'. The packet-level conclusion is a different route: §4.7 'The LLM may return purpose = university application submission only if the dossier includes direct application evidence, such as admissions language, a portal, a checklist, or a clearly targeted essay.'. |

**Recognition**

*Deterministic — each rule is a pattern **plus** a corroborating context:*

- a gazetteer university name matched at a word boundary co-occurring with admissions language — the design's own seed, §4.2 'an essay with a university name in its heading, a portal screenshot with admissions language, or a user-created folder that already expresses application purpose'
- an application-cycle pattern co-occurring with a gazetteer university name and an admissions term
- an explicit portal or submission term ('admissions portal', 'application checklist', 'Common Application', 'submitted') co-occurring with a gazetteer university name — the strong support named by §3.9 'Purpose may be supported strongly by an existing user-created folder name or explicit language in a form or portal.'
- an application-document-type term ('personal statement', 'supplemental essay', 'application form') co-occurring with a gazetteer university name

*Needs the LLM — language interpretation a rule cannot do safely:*

- §3.5 'It may identify that a vague document is a university application essay'
- §3.5 'determine that an OCR'd screenshot is an application portal rather than a generic image'
- §3.5 'recognize that a heterogeneous group of files has the shared purpose of a university application package'
- an essay that is clearly an application essay but names no institution, so the target must come from the packet rather than the file

*Never alone — bare signals that must not establish this domain by themselves:*

- a university name on its own — §4.9 'A university name alone should not create a group because Columbia can appear as an authoring school, course provider, target institution, employer, research venue, or merely a cited organization.'
- a four-digit year — §3.10 'file names and documents frequently contain numbers that look like years but are course identifiers, version numbers, build numbers, ZIP codes, or other unrelated values'
- a transcript, which is equally an academic record and an application component
- a download session — §4.7 'A tight download session alone is never sufficient'
- a folder name containing the word 'application', with no institution or admissions evidence inside the files

**Work types** — personal statement, supplemental essay, application form, portal screenshot, application checklist, transcript upload, resume, certificate, identification document, academic abstract, recommendation form, financial-aid form, decision letter, interview confirmation

**Why files in this domain group together**

- one target institution in one cycle — the design's own label form, §4.5 'an application group Columbia Application — 2026 Cycle'
- a purpose-coherent packet whose members are content-incoherent: §3.9 'The documents are content-incoherent but purpose-coherent.'
- the design's own dossier shape: §4.4 'show a Columbia essay, application checklist, and portal screenshot as direct anchors; list a transcript, resume, and certificate as possible supporting materials; and identify whether any candidate has a conflicting institution, such as a Duke essay'
- an existing user-created folder expressing application purpose, such as §5.6 'Chinese University Application Materials'

**Template**

| dimension order | time first | why |
|---|---|---|
| target_institution → application_cycle → application_document_type | no | §5.4 'an Applications template may define target institution → application cycle → document type', restated in §5.6 'It may propose target institution → cycle → document type' with the example path §5.6 'Applications/UChicago/2026/Supplemental Essays'. The design explicitly refuses to make this order binding: a purpose-defined packet may stay whole — §5.6 'The user may keep it as one flat purpose folder, nest it under Applications, split it by target institution, or choose a hybrid design' — and §5.6 'The template is a recommendation mechanism, not a rule that erases purposeful heterogeneity.'. |

**Collides with** — where this domain and another will fight over the same file

| other domain | the confusion, and what separates them | design cite |
|---|---|---|
| `acad.course-enrollment` | both carry a university name; only the application carries a target-institution and cycle pair, and the applicant's own school is a different role from the target | §3.8 'An application essay can mention the author's current school and the university to which the essay is addressed.' |
| `acad.transcript-record` | a transcript is an academic record and an application component at the same time; the issuing school and the target institution are different fields and must not be merged | §4.8 'an application packet does not silently absorb a document with a conflicting target institution' |
| `acad.recommendation-letter` | a letter belongs to the application it supports and to the course or relationship that produced it; the target institution on the letter must match the packet's | §4.8 'an application packet does not silently absorb a document with a conflicting target institution' |
| `acad.scholarship-fellowship` | both carry an application cycle and a target organisation; a scholarship's target is a funder, not an admitting institution | — |
| `acad.grad-school-application` | identical document types at a different level; two applications to the same university in different cycles must not merge | §4.9 'members carry irreconcilable course, institution, project, term, or purpose facts' |
| `res.research-project` | an abstract written for research and submitted with an application carries both readings at once, which is the design's own worked multi-domain case | §3.11 'An academic abstract submitted as part of a university application can retain project = PVA/RDP and document type = abstract while also carrying purpose = university application and target university = UChicago.' |

**Sensitivity** — `potentially_sensitive`. The packet the design describes contains an identification document — §3.9 'A university application packet can contain an identification document, transcript, resume, certificate, and academic abstract.' — and §7.3 'passport scans, medical documents, account statements, visas, legal forms, or credentials' names passport scans among protected material. The phrase is the design's; no handling class is assigned here.

**Open question (unresolved — for Joseph)**

> When an existing folder such as §5.6 'Chinese University Application Materials' already holds the packet, should the proposed institution branch appear alongside it, replace it, or be suppressed? §5.6 'The system can present that packet as a preserved or proposed branch alongside institution-based organization.' permits the first, §5.10 'Existing folders must not be automatically flattened, renamed, or reorganized simply because a template would produce a different structure.' forbids the second, and the design leaves the default unstated.

---

### 15. K-12 and secondary school admission

`acad.k12-school-admission` · **inference** · sensitivity: `potentially_sensitive`

> Applying to a private, boarding, magnet or selective secondary school, usually run by a parent on a child's behalf.

**Design basis** — Extends the College applications domain of §3.11 'College application files may use target university, application cycle, application document type, and purpose.' downward to secondary admission, which the design does not name. The role separation it depends on is the design's: §3.8 'An application essay can mention the author's current school and the university to which the essay is addressed.'.

**Schema — the fields this domain, and only this domain, legitimises**

| field | type | example | reliability ceiling | why this field exists and why that ceiling |
|---|---|---|---|---|
| `target_school` | string | the school applied to | `validated` | The same role as target university in §3.11 'College application files may use target university, application cycle, application document type, and purpose.', at a different level. A gazetteer school name at a word boundary together with admissions context. |
| `entry_year` | string | the year of intended entry | `validated` | The cycle equivalent. It is an entry year rather than an admissions cycle because secondary admission is stated as the year a child would start. |
| `applicant` | string | the child applying | `user_confirmed` | The applicant is a minor and is not the corpus holder; a child's name must not be attached to a file by inference. |
| `entry_grade` | string | the grade applied for | `validated` | A grade-level pattern beside a target-school name and an admissions term. It is the field with no higher-education counterpart. |
| `admission_document_type` | string | the kind of application document | `validated` | An admission-document term beside a target-school name. |
| `decision` | enum | the outcome recorded | `user_confirmed` | An outcome about a child, frequently a painful one; the design's discipline against unsupported conclusions applies with extra force. §3.6 'A model that cannot cite sufficient evidence must return unknown.' |

**Recognition**

*Deterministic — each rule is a pattern **plus** a corroborating context:*

- a gazetteer school name at a word boundary co-occurring with secondary-admissions language ('admissions', 'applicant', 'entry year', 'open house', 'shadow day')
- a secondary entrance-test name co-occurring with a target-school name or a registration term
- an entry-grade pattern co-occurring with a target-school name and an admissions term

*Needs the LLM — language interpretation a rule cannot do safely:*

- a parent statement that is an admission essay only by context
- correspondence about a school that may be the current one or the prospective one
- distinguishing an enquiry from a submitted application

*Never alone — bare signals that must not establish this domain by themselves:*

- a school name — §4.9 'A university name alone should not create a group because Columbia can appear as an authoring school, course provider, target institution, employer, research venue, or merely a cited organization.' applies at every level
- a child's first name
- a four-digit year — §3.10 'file names and documents frequently contain numbers that look like years but are course identifiers, version numbers, build numbers, ZIP codes, or other unrelated values'

**Work types** — application form, parent statement, student essay, entrance test score, teacher recommendation, interview note, financial aid form, decision letter, enrolment contract, school visit note, transcript request

**Why files in this domain group together**

- one target school for one entry year
- one child's admission round across all schools applied to
- an application form with its supporting documents

**Template**

| dimension order | time first | why |
|---|---|---|
| applicant → target_school → admission_document_type | no | Inference. It mirrors §5.4 'an Applications template may define target institution → application cycle → document type' with an applicant level added first, because a family applying for two children has two disjoint corpora that share every school name. Whether a child's name may be a folder level is the open question on the K-12 schooling entry. |

**Collides with** — where this domain and another will fight over the same file

| other domain | the confusion, and what separates them | design cite |
|---|---|---|
| `acad.k12-schooling` | an acceptance letter and an enrolment form arrive together; the admission carries an applied-to school that may differ from the attended one | §4.8 'an application packet does not silently absorb a document with a conflicting target institution' |
| `acad.college-application` | identical document types at a different level; a sibling's college application and a child's school application in the same household must not merge | §4.9 'members carry irreconcilable course, institution, project, term, or purpose facts' |
| `acad.standardized-testing` | a secondary entrance test is a score report; the testing domain owns the sitting, this domain owns the submission | — |
| `acad.financial-aid` | secondary financial aid forms are submitted with the application and carry household financial detail | §3.15 'Finance, identity, medical, and legal material should be implemented first as safety domains' |

**Sensitivity** — `potentially_sensitive`. Inference, not design. These files concern a minor and the aid forms carry household finances — §3.15 'Finance, identity, medical, and legal material should be implemented first as safety domains' puts financial material behind protection. The phrase is the design's; no handling class is assigned here.

---

### 16. Graduate and professional school application

`acad.grad-school-application` · **inference** · sensitivity: `none`

> Applying to a graduate or professional programme, where the unit applied to is a named programme within an institution rather than the institution itself.

**Design basis** — Extends the College applications domain of §3.11 'College application files may use target university, application cycle, application document type, and purpose.' to a level the design does not name. It reuses the design's own template, §5.4 'an Applications template may define target institution → application cycle → document type', with one added dimension.

**Schema — the fields this domain, and only this domain, legitimises**

| field | type | example | reliability ceiling | why this field exists and why that ceiling |
|---|---|---|---|---|
| `target_university` | string | the institution applied to | `validated` | Shared with §3.11 'College application files may use target university, application cycle, application document type, and purpose.'; the same gazetteer-plus-context rule. |
| `target_programme` | string | the specific programme or department applied to | `validated` | Inference, and the field that makes this domain distinct: two applications to the same university for different programmes are different applications, and the university alone cannot separate them. |
| `application_cycle` | string | the admissions cycle applied in | `validated` | Shared with §3.11 'College application files may use target university, application cycle, application document type, and purpose.'. |
| `application_document_type` | string | the kind of application document | `validated` | Shared with §3.11 'College application files may use target university, application cycle, application document type, and purpose.'. The graduate document types differ in kind: a statement of purpose and a writing sample have no undergraduate counterpart. |
| `faculty_of_interest` | string | a named potential supervisor | `llm_supported` | Inference. Naming a prospective advisor is a graduate-specific move, stated in prose inside a statement of purpose; it is a role, never a destination dimension — §3.8 'It should avoid using authorship or creator identity as a destination dimension.'. |
| `purpose` | string | graduate application | `validated` | Shared with §3.11 'College application files may use target university, application cycle, application document type, and purpose.' on the strong support named by §3.9 'Purpose may be supported strongly by an existing user-created folder name or explicit language in a form or portal.'. |

**Recognition**

*Deterministic — each rule is a pattern **plus** a corroborating context:*

- a graduate-application term ('statement of purpose', 'writing sample', 'graduate admissions', 'programme of study') co-occurring with a gazetteer university name at a word boundary
- a graduate-degree pattern ('PhD', 'MSc', 'MFA', 'Master of') co-occurring with a gazetteer university name and an admissions term
- an application-cycle pattern co-occurring with a gazetteer university name and a graduate-application term
- a graduate admissions-test name co-occurring with a target university name

*Needs the LLM — language interpretation a rule cannot do safely:*

- a statement of purpose that names a field but not a programme
- distinguishing a statement of purpose from a personal statement written for a different level
- prose that establishes which of two programmes at one university a document was written for

*Never alone — bare signals that must not establish this domain by themselves:*

- a university name — §4.9 'A university name alone should not create a group because Columbia can appear as an authoring school, course provider, target institution, employer, research venue, or merely a cited organization.'
- a department name, which appears throughout an academic corpus for unrelated reasons
- a four-digit year — §3.10 'file names and documents frequently contain numbers that look like years but are course identifiers, version numbers, build numbers, ZIP codes, or other unrelated values'

**Work types** — statement of purpose, personal history statement, writing sample, research proposal, CV, transcript upload, recommendation request, admissions test score, application form, portal screenshot, interview confirmation, funding offer, decision letter

**Why files in this domain group together**

- one target programme at one institution in one cycle
- a statement of purpose across its per-programme variants as a version family
- one cycle across every programme applied to

**Template**

| dimension order | time first | why |
|---|---|---|
| target_institution → target_programme → application_cycle → application_document_type | no | Inference. It is §5.4 'an Applications template may define target institution → application cycle → document type' with a programme level inserted, because §5.5 'a parent dimension should provide the context required to understand the child': a statement of purpose is only interpretable once the programme it targets is known. |

**Collides with** — where this domain and another will fight over the same file

| other domain | the confusion, and what separates them | design cite |
|---|---|---|
| `acad.college-application` | identical document types at a different level; the target programme is the discriminator and undergraduate applications carry none | §4.9 'members carry irreconcilable course, institution, project, term, or purpose facts' |
| `acad.scholarship-fellowship` | a graduate application and a fellowship application share a cycle and a research proposal; the fellowship's target is a funder | — |
| `res.research-project` | a research proposal written for an application is also a research artifact, which is the design's own worked multi-domain case | §3.11 'An academic abstract submitted as part of a university application can retain project = PVA/RDP and document type = abstract while also carrying purpose = university application and target university = UChicago.' |
| `acad.recommendation-letter` | letters are requested per programme; a letter with a conflicting target programme must not be absorbed | §4.8 'an application packet does not silently absorb a document with a conflicting target institution' |

**Sensitivity** — `none`. A graduate application packet does not by default contain the identification document the design names in an undergraduate packet. Where it does, the collision with an identity record is the route to protection, not a class assigned here.

**Open question (unresolved — for Joseph)**

> Should applications to different programmes at the same university nest under one institution branch, or stand as siblings? The design's template names only the institution level (§5.4 'an Applications template may define target institution → application cycle → document type') and a doctoral applicant may apply to several programmes at one school.

---

### 17. Standardised testing

`acad.standardized-testing` · **proposal** · sensitivity: `none`

> Registering for, preparing for, sitting, and receiving scores from a standardised test.

**Design basis** — none. `design_cite` is null: no design sentence names this domain. It is a proposal for Joseph.

**Schema — the fields this domain, and only this domain, legitimises**

| field | type | example | reliability ceiling | why this field exists and why that ceiling |
|---|---|---|---|---|
| `test` | string | the test taken | `validated` | Proposal, and the anchor: a test name is a closed, well-known vocabulary and matches cleanly at a word boundary, which §3.7 'It should use word-boundary matching rather than substring matching.' requires. |
| `test_sitting` | string | the administration the record belongs to | `validated` | Proposal. A person may sit the same test several times; the sitting is what separates two otherwise identical score reports, and merging them would be the conflicting-fact failure of §4.9 'members carry irreconcilable course, institution, project, term, or purpose facts'. |
| `testing_body` | string | the organisation that administers the test | `validated` | A testing-body name beside a test name. |
| `score_recipient` | string | an institution the scores were sent to | `validated` | Proposal. It is the link into an application, and it is a distinct role from the target university: sending a score is not applying. |
| `testing_record_type` | string | the kind of testing document | `validated` | A record-type term ('registration', 'admission ticket', 'score report') beside a test name. |

**Recognition**

*Deterministic — each rule is a pattern **plus** a corroborating context:*

- a test name matched at a word boundary co-occurring with a testing term ('score report', 'registration', 'admission ticket', 'test date')
- a testing-body name co-occurring with a test name or a registration term
- a test-date pattern co-occurring with a test name — narrow date extraction only, per §3.10 'file names and documents frequently contain numbers that look like years but are course identifiers, version numbers, build numbers, ZIP codes, or other unrelated values'

*Needs the LLM — language interpretation a rule cannot do safely:*

- practice material with no branding that is preparation for a specific test
- distinguishing an official score report from a practice-score screenshot
- correspondence about scores that names no test

*Never alone — bare signals that must not establish this domain by themselves:*

- a short test acronym, which is the substring hazard §3.7 'names such as MIT can be found inside "submit,"' describes
- a date
- the word 'score', which appears across athletics, gaming and finance material

**Work types** — registration confirmation, admission ticket, score report, score-send receipt, practice test, preparation material, accommodation approval, fee waiver, cancellation notice

**Why files in this domain group together**

- one test across all of its sittings
- one sitting with its registration, ticket and score report
- preparation material for one test

**Template**

| dimension order | time first | why |
|---|---|---|
| test → test_sitting → testing_record_type | no | Proposal. The test is the durable parent, the sitting is the enumerable child, and the record type is the leaf — the same shape as §5.4 'an Applications template may define target institution → application cycle → document type' with the cycle replaced by a sitting. |

**Collides with** — where this domain and another will fight over the same file

| other domain | the confusion, and what separates them | design cite |
|---|---|---|
| `acad.college-application` | a score report is a testing record and an application component; the score recipient and the target university are different roles | §4.8 'an application packet does not silently absorb a document with a conflicting target institution' |
| `acad.self-study` | test preparation is self-study; the testing reading is established by a registration or a sitting | — |
| `acad.language-study` | a language proficiency test is both; the language domain owns the language and level, this one owns the sitting | — |
| `acad.accommodations` | a testing accommodation approval carries medical support and belongs to both | §7.3 'passport scans, medical documents, account statements, visas, legal forms, or credentials' |

**Sensitivity** — `none`. A score report concerns the corpus holder and is not material the design names as potentially sensitive. An attached accommodation approval is, and reaches protection through that collision rather than through a class assigned here.

---

### 18. Letters and forms of recommendation

`acad.recommendation-letter` · **inference** · sensitivity: `potentially_sensitive`

> A letter written about one person for one target, held by the writer, the subject, or both.

**Design basis** — The design names the artifact — §4.7 'a transcript, resume, personal statement, recommendation form, certificate, or ID' lists a recommendation form among the compatible record types of an application packet — but names no domain for it.

**Schema — the fields this domain, and only this domain, legitimises**

| field | type | example | reliability ceiling | why this field exists and why that ceiling |
|---|---|---|---|---|
| `subject_of_letter` | string | the person the letter is about | `user_confirmed` | Inference. The subject is a named person and the letter's whole meaning; attaching a person's name by inference is precisely what must not happen, so only the user establishes it. |
| `recommender` | string | the person writing the letter | `direct` | Read from a signature block or labelled slot, which §3.5 'such as a content hash, EXIF timestamp, a document title, or a labeled form field' makes direct. Never a folder dimension: §3.8 'It should avoid using authorship or creator identity as a destination dimension.'. |
| `target` | string | the institution, programme or employer the letter was written for | `validated` | Inference, and the field that makes a letter filable: a gazetteer institution name beside recommendation language. It is the same target role as in §3.11 'College application files may use target university, application cycle, application document type, and purpose.'. |
| `relationship_basis` | string | the course, lab or job that gave rise to the letter | `llm_supported` | Inference. The basis is stated in the letter's opening prose and is what links a letter to a course or a lab; it is recoverable only by reading. |
| `letter_direction` | enum | whether the holder wrote the letter or is its subject | `llm_supported` | Inference, and the field that decides which corpus the file belongs to. The same PDF means opposite things in the two directions. |
| `cycle` | string | the application cycle the letter was written for | `validated` | Shared with §3.11 'College application files may use target university, application cycle, application document type, and purpose.'; a letter is written for one cycle and is often re-requested in the next. |

**Recognition**

*Deterministic — each rule is a pattern **plus** a corroborating context:*

- a recommendation term ('letter of recommendation', 'letter of reference', 'recommender', 'recommendation form') co-occurring with a gazetteer institution name at a word boundary
- a recommendation term co-occurring with an application-cycle pattern
- a recommendation-waiver term co-occurring with a recommendation term and an institution name

*Needs the LLM — language interpretation a rule cannot do safely:*

- a letter with no header that is a recommendation only by its prose
- establishing whether the holder is the writer or the subject
- recovering the relationship basis when the letter names no course

*Never alone — bare signals that must not establish this domain by themselves:*

- the word 'letter'
- a person's name — §3.8 'It should avoid using authorship or creator identity as a destination dimension.'
- an institution name — §4.9 'A university name alone should not create a group because Columbia can appear as an authoring school, course provider, target institution, employer, research venue, or merely a cited organization.'

**Work types** — letter of recommendation, recommendation form, waiver form, recommendation request, brag sheet, reminder correspondence, submission confirmation, draft letter

**Why files in this domain group together**

- one letter across the targets it was submitted to
- one subject across all letters written about them
- a request with its letter and its submission confirmation

**Template**

| dimension order | time first | why |
|---|---|---|
| target → cycle → letter_direction | no | Inference. It deliberately does not lead with the person: §3.8 'It should avoid using authorship or creator identity as a destination dimension.'. The target and cycle place a letter beside the application it supports, which is where a person looks for it. |

**Collides with** — where this domain and another will fight over the same file

| other domain | the confusion, and what separates them | design cite |
|---|---|---|
| `acad.college-application` | a letter belongs to the packet it supports; a letter naming a different target institution must not be absorbed into the packet | §4.8 'an application packet does not silently absorb a document with a conflicting target institution' |
| `acad.course-enrollment` | a letter's relationship basis is often a course, so the same letter carries a course fact and an application fact at once | §3.1 'A file can simultaneously be a syllabus, part of a particular course, created for a particular semester, related to a university, included in an application package, a member of a version family, and potentially sensitive.' |
| `acad.course-instruction` | on the writing side the letter sits in the teaching corpus and is about a student, not about the holder | §3.8 'An application essay can mention the author's current school and the university to which the essay is addressed.' |
| `acad.scholarship-fellowship` | the same letter is frequently reused for a funder; the target is what separates the two copies | §4.8 'an application packet does not silently absorb a document with a conflicting target institution' |

**Sensitivity** — `potentially_sensitive`. Inference, not design. A letter is a candid third-party assessment of a named person, and on the writing side the subject has usually waived access to it — third-party content of the kind §2.9 'treating addresses and message content as potentially sensitive' applies the phrase to. No handling class is assigned here.

**Open question (unresolved — for Joseph)**

> On the writing side, should letters be collected under the person they are about, or under the target they were sent to? §3.8 'It should avoid using authorship or creator identity as a destination dimension.' bars the writer as a collector but says nothing about the subject, and a recommender's corpus is naturally organised per student.

---

### 19. Transcripts and official academic records

`acad.transcript-record` · **inference** · sensitivity: `potentially_sensitive`

> Registrar-issued records of what a person studied and how they did — the authoritative account, as distinct from the coursework itself.

**Design basis** — The design names the artifact repeatedly as a packet member — §5.6 'containing a transcript, ID, personal statement, resume, certificate, and research abstract' — and gives it no domain of its own.

**Schema — the fields this domain, and only this domain, legitimises**

| field | type | example | reliability ceiling | why this field exists and why that ceiling |
|---|---|---|---|---|
| `issuing_school` | string | the institution that issued the record | `validated` | Inference, and a distinct role from the target of an application: the issuer is where the person studied. A gazetteer school name beside registrar language. |
| `record_type` | enum | official transcript | `validated` | A registrar record-type term beside an issuing-school name. The design uses the noun for exactly this artifact in §3.9 'A university application packet can contain an identification document, transcript, resume, certificate, and academic abstract.'. |
| `issue_date` | date | the date the record was issued | `validated` | Narrow date extraction only: §3.10 'file names and documents frequently contain numbers that look like years but are course identifiers, version numbers, build numbers, ZIP codes, or other unrelated values'. A transcript's issue date is what separates two otherwise identical copies. |
| `official_status` | enum | whether the copy is official or unofficial | `validated` | Inference, and the field a person actually searches by, because an unofficial copy cannot be submitted. The words 'official' and 'unofficial' appear literally on the artifact beside registrar language. |
| `coverage` | string | the period or programme the record covers | `llm_supported` | Inference. Coverage is implied by the table of terms inside the document rather than stated in a field. |
| `recipient` | string | the institution the record was sent to | `validated` | Inference. A send-to institution is a distinct role from the issuer, and confusing them is exactly the failure §3.8 'An application essay can mention the author's current school and the university to which the essay is addressed.' describes. |

**Recognition**

*Deterministic — each rule is a pattern **plus** a corroborating context:*

- a registrar term ('official transcript', 'academic record', 'registrar', 'enrolment verification') co-occurring with a gazetteer school name at a word boundary
- an official-status term ('official', 'unofficial', 'issued to') co-occurring with a registrar term
- a degree-verification term co-occurring with a school name and an issue-date pattern
- a send-to term ('issued to', 'sent to', 'delivered to', 'recipient') co-occurring with a registrar term and a second gazetteer institution name distinct from the issuer

*Needs the LLM — language interpretation a rule cannot do safely:*

- a scanned transcript whose header OCRs poorly and whose school must be read from the body
- a foreign transcript whose record type is named in another language
- distinguishing a registrar transcript from a self-made record of courses

*Never alone — bare signals that must not establish this domain by themselves:*

- a school name — §4.9 'A university name alone should not create a group because Columbia can appear as an authoring school, course provider, target institution, employer, research venue, or merely a cited organization.'
- a table of course codes and grades, which a degree audit also contains
- the word 'record'

**Work types** — official transcript, unofficial transcript, enrolment verification, degree verification, grade report, transcript request, transcript-send receipt, diploma supplement, credential evaluation

**Why files in this domain group together**

- one issuing school across every record it has issued
- a request with the transcript it produced and the send receipt
- successive issues of the same transcript as a version family

**Template**

| dimension order | time first | why |
|---|---|---|
| issuing_school → record_type → issue_date | no | Inference. The issuing school is the durable parent; the issue date sits last because a person looks for a transcript by school and kind first, which is the ordering §5.5 'For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders.' prescribes. |

**Collides with** — where this domain and another will fight over the same file

| other domain | the confusion, and what separates them | design cite |
|---|---|---|
| `acad.college-application` | a transcript is an academic record and an application component simultaneously; the issuing school and the target institution are different fields and merging them is the packet failure the design names | §4.8 'an application packet does not silently absorb a document with a conflicting target institution' |
| `acad.undergraduate-program` | a degree audit and a transcript both list completed courses; only the transcript is registrar-issued and carries an issue date | — |
| `acad.transfer-credit` | a credential evaluation is built from a transcript and is not one; the evaluation carries a receiving school | — |
| `acad.credential-certificate` | a diploma and a transcript are both proof of study; the diploma asserts the award, the transcript asserts the record | — |
| `pers.identity-document` | a transcript carries a student identifier and a date of birth, which pulls it toward material the design protects first | §3.15 'Finance, identity, medical, and legal material should be implemented first as safety domains' |

**Sensitivity** — `potentially_sensitive`. Inference, not design. A transcript carries a student identifier and often a date of birth, and §7.3 'passport scans, medical documents, account statements, visas, legal forms, or credentials' puts comparable identity material behind protection. The phrase is the design's; no handling class is assigned here.

**Open question (unresolved — for Joseph)**

> Does a transcript live under an academic-records branch and appear inside an application packet by reference, or is it copied into the packet? §3.1 'A file can simultaneously be a syllabus, part of a particular course, created for a particular semester, related to a university, included in an application package, a member of a version family, and potentially sensitive.' says a file holds several facts at once, but the tree has to put the bytes somewhere.

---

### 20. Transfer credit and credit by examination

`acad.transfer-credit` · **proposal** · sensitivity: `none`

> Getting work done at one institution, or outside any institution, recognised by another.

**Design basis** — none. `design_cite` is null: no design sentence names this domain. It is a proposal for Joseph.

**Schema — the fields this domain, and only this domain, legitimises**

| field | type | example | reliability ceiling | why this field exists and why that ceiling |
|---|---|---|---|---|
| `sending_institution` | string | where the credit was earned | `validated` | Proposal. Two school roles in one record is the case §3.8 'An application essay can mention the author's current school and the university to which the essay is addressed.' is about; conflating them silently merges two schools' material. |
| `receiving_institution` | string | the school being asked to recognise the credit | `validated` | The counterpart role. The evaluation is issued by the receiving school and is about the sending school's work. |
| `source_course` | string | the course as the sending institution named it | `validated` | §3.5 'BUSIB 4300 becomes a course fact only when the engine finds a course-code pattern together with academic context such as "syllabus," "lecture," "credits," "instructor," or "semester."' applies to both course fields; they are different values of the same field kind and must not be merged. |
| `equivalent_course` | string | the course the receiving institution maps it to | `validated` | The mapping is the whole point of the record and is stated as an explicit pair on an evaluation. |
| `credit_basis` | enum | how the credit was earned | `validated` | A basis term ('transfer', 'advanced placement', 'credit by examination', 'study abroad', 'dual enrolment') beside an evaluation term. |
| `evaluation_outcome` | enum | whether the credit was granted | `validated` | An outcome term beside an equivalence statement. The outcome is printed on the evaluation, not inferred. |

**Recognition**

*Deterministic — each rule is a pattern **plus** a corroborating context:*

- a transfer-credit term ('transfer credit', 'credit evaluation', 'course equivalency', 'articulation') co-occurring with a gazetteer school name at a word boundary
- an equivalence statement pattern (one course code mapped to another) co-occurring with a transfer-credit term
- a credit-basis term ('advanced placement', 'credit by examination', 'dual enrolment') co-occurring with a school name and a course code
- a role-assigning term ('transferred from', 'awarded by', 'accepted by', 'evaluated for') co-occurring with a transfer-credit term and the institution name it governs — the pair is what separates the sending role from the receiving one, per §3.8 'An application essay can mention the author's current school and the university to which the essay is addressed.'

*Needs the LLM — language interpretation a rule cannot do safely:*

- correspondence negotiating an equivalence that names no outcome
- a syllabus submitted as evidence for an equivalence request, which reads as ordinary coursework
- a foreign credential evaluation whose institutions must be read from prose

*Never alone — bare signals that must not establish this domain by themselves:*

- two course codes appearing near each other
- a school name — §4.9 'A university name alone should not create a group because Columbia can appear as an authoring school, course provider, target institution, employer, research venue, or merely a cited organization.'
- the word 'transfer', which is also financial and file-movement vocabulary

**Work types** — credit evaluation, articulation agreement, equivalency request, syllabus submitted as evidence, advanced-placement score report, credit-by-examination result, petition, decision notice, foreign credential evaluation

**Why files in this domain group together**

- one evaluation with the evidence submitted for it
- one sending institution across everything transferred from it
- one petition across its correspondence and its decision

**Template**

| dimension order | time first | why |
|---|---|---|
| receiving_institution → sending_institution → credit_basis | no | Proposal. The receiving institution leads because it owns the decision and is where the record matters; the sending institution beneath it satisfies §5.5 'a parent dimension should provide the context required to understand the child', since an equivalence is meaningless without knowing what is being equated to what. |

**Collides with** — where this domain and another will fight over the same file

| other domain | the confusion, and what separates them | design cite |
|---|---|---|
| `acad.transcript-record` | an evaluation is built from a transcript and is not one; only the evaluation carries a receiving institution | — |
| `acad.course-enrollment` | a syllabus submitted as equivalence evidence is coursework from the sending school and evidence for the receiving one at the same time | §3.1 'A file can simultaneously be a syllabus, part of a particular course, created for a particular semester, related to a university, included in an application package, a member of a version family, and potentially sensitive.' |
| `acad.study-abroad` | study-abroad credit is transfer credit; the study-abroad reading additionally carries a host institution and a term away | — |
| `acad.standardized-testing` | an advanced-placement score is a testing record and a credit basis at once | — |

**Sensitivity** — `none`. Credit evaluations concern the corpus holder and name no third parties.

---

### 21. Financial aid and student loans

`acad.financial-aid` · **proposal** · sensitivity: `potentially_sensitive`

> Need-based and institutional aid for one award year — applications, awards, disbursements and the loans that follow.

**Design basis** — none. `design_cite` is null: no design sentence names this domain. It is a proposal for Joseph.

**Schema — the fields this domain, and only this domain, legitimises**

| field | type | example | reliability ceiling | why this field exists and why that ceiling |
|---|---|---|---|---|
| `award_year` | string | the aid year the award applies to | `validated` | Proposal. An aid year is a named span that does not align with a semester or a tax year, so it needs its own pattern for the reason §3.10 'Academic terms such as Spring 2025, AY 2024-25, and Michaelmas Term 2024 require dedicated patterns rather than generic parsing.' gives for academic terms. |
| `aid_type` | enum | grant | `validated` | Proposal, and the field the whole domain turns on: a grant, a loan and a work-study allocation have different consequences and different paperwork, and they arrive in one letter. |
| `awarding_body` | string | the institution or agency making the award | `validated` | A school or agency name beside aid language. Distinct from the servicer role below — the same failure §3.8 'An application essay can mention the author's current school and the university to which the essay is addressed.' describes. |
| `aid_document_type` | string | the kind of aid document | `validated` | An aid document-type term beside an award-year pattern or an awarding-body name. |
| `servicer` | string | the organisation administering a loan after disbursement | `validated` | Proposal. The servicer is a different party from the awarding body and often changes during repayment; treating them as one field would merge a decade of correspondence with the original award. |
| `aid_application_record` | enum | the aid application the record belongs to | `validated` | An aid-application term beside an award-year pattern. The application, the award and the disbursement are three stages of one year and are frequently confused. |

**Recognition**

*Deterministic — each rule is a pattern **plus** a corroborating context:*

- an aid term ('financial aid', 'award letter', 'need analysis', 'expected family contribution', 'student aid report') co-occurring with a school name or an award-year pattern
- a loan term ('promissory note', 'disbursement', 'loan servicer', 'entrance counselling') co-occurring with a school name or an aid-year pattern
- an aid document-type term co-occurring with an awarding-body name at a word boundary

*Needs the LLM — language interpretation a rule cannot do safely:*

- an appeal letter that argues circumstances without naming an aid type
- correspondence from a servicer that names neither the school nor the loan
- distinguishing an aid offer from a tuition bill that nets aid against charges

*Never alone — bare signals that must not establish this domain by themselves:*

- a school name — §4.9 'A university name alone should not create a group because Columbia can appear as an authoring school, course provider, target institution, employer, research venue, or merely a cited organization.'
- a four-digit year — §3.10 'file names and documents frequently contain numbers that look like years but are course identifiers, version numbers, build numbers, ZIP codes, or other unrelated values'
- the word 'aid'
- a currency figure

**Work types** — aid application, student aid report, award letter, aid appeal, verification worksheet, promissory note, entrance counselling record, disbursement notice, loan statement, repayment plan, forgiveness application, work-study authorisation

**Why files in this domain group together**

- one award year across its application, award and disbursement
- one loan across its origination and servicing correspondence
- an appeal with the documentation submitted for it

**Template**

| dimension order | time first | why |
|---|---|---|
| awarding_body → award_year → aid_type | no | Proposal. The awarding body is the durable parent because a person's aid history usually spans one institution; the award year is the audit unit beneath it and must be enumerable, since aid is decided and reconciled per year. |

**Collides with** — where this domain and another will fight over the same file

| other domain | the confusion, and what separates them | design cite |
|---|---|---|
| `fin.financial-records` | aid documents are financial records with an academic subject; the design puts finance behind protection before placement, so the finance reading governs handling | §3.15 'Finance, identity, medical, and legal material should be implemented first as safety domains' |
| `acad.tuition-billing` | an award letter and a tuition bill both net charges against aid; the bill is issued per term by the bursar, the award per aid year by the aid office | — |
| `acad.scholarship-fellowship` | a scholarship is an aid type and a separate application; only the scholarship carries a funder and a competitive cycle | — |
| `acad.college-application` | aid forms are submitted with an application and carry household finances into an application packet | §4.8 'an application packet does not silently absorb a document with a conflicting target institution' |

**Sensitivity** — `potentially_sensitive`. Proposal, not design. Aid records carry household income and account detail; §3.15 'Finance, identity, medical, and legal material should be implemented first as safety domains' and §7.3 'passport scans, medical documents, account statements, visas, legal forms, or credentials' name account statements among protected material. The phrase is the design's; no handling class is assigned here.

**Open question (unresolved — for Joseph)**

> Should financial aid sit under Academics, beside the school it belongs to, or under the Finance area the design protects separately? §5.1 'Academics, Applications, Research, Career, Personal Records, Finance and Administration, Photos and Captures, Code and Projects, and Media or Miscellaneous Personal Material' lists both, and putting it under Academics may place protected material inside an unprotected branch.

---

### 22. Scholarship and fellowship applications

`acad.scholarship-fellowship` · **proposal** · sensitivity: `none`

> Competitive applications to a funder for study or research support, and the reporting the award then requires.

**Design basis** — none. `design_cite` is null: no design sentence names this domain. It is a proposal for Joseph.

**Schema — the fields this domain, and only this domain, legitimises**

| field | type | example | reliability ceiling | why this field exists and why that ceiling |
|---|---|---|---|---|
| `funder` | string | the organisation offering the award | `validated` | Proposal. The funder is a distinct role from the school: a national fellowship is administered by a body that is not the applicant's institution, and merging them is the failure §3.8 'An application essay can mention the author's current school and the university to which the essay is addressed.' describes. |
| `award` | string | the named scholarship or fellowship | `validated` | A named award beside application or funder language. Named awards are proper nouns and match cleanly at a word boundary, which §3.7 'It should use word-boundary matching rather than substring matching.' requires. |
| `competition_cycle` | string | the cycle applied in | `validated` | The same role as application cycle in §3.11 'College application files may use target university, application cycle, application document type, and purpose.': the cycle separates a failed attempt from a later successful one. |
| `application_stage` | enum | where the application sits | `validated` | A stage term ('nomination', 'submitted', 'shortlisted', 'awarded', 'declined', 'report due') beside an award name. Reapplication makes stage the field people navigate by. |
| `award_document_type` | string | the kind of document | `validated` | A document-type term beside an award or funder name. |
| `reporting_obligation` | string | a report the award requires after it is made | `llm_supported` | Proposal. Obligations are stated in prose inside award terms, and they are the reason a fellowship corpus keeps growing after the application closes. |

**Recognition**

*Deterministic — each rule is a pattern **plus** a corroborating context:*

- a named award co-occurring with an application or funding term ('application', 'nomination', 'award', 'fellowship', 'scholarship')
- a funder name co-occurring with an award name at a word boundary
- a stage term ('nomination', 'shortlisted', 'awarded', 'declined') co-occurring with a named award and a cycle pattern
- a reporting term ('interim report', 'final report', 'grant report') co-occurring with a named award

*Needs the LLM — language interpretation a rule cannot do safely:*

- a personal statement written for a fellowship that names no award
- distinguishing a nomination the holder wrote from one written about them
- a research proposal that is both a fellowship application and a research artifact

*Never alone — bare signals that must not establish this domain by themselves:*

- the words 'scholarship' or 'fellowship', which appear throughout academic prose
- a funder name that is also a well-known company or foundation appearing for unrelated reasons
- a four-digit year — §3.10 'file names and documents frequently contain numbers that look like years but are course identifiers, version numbers, build numbers, ZIP codes, or other unrelated values'

**Work types** — application form, personal statement, research proposal, budget, nomination letter, recommendation letter, award letter, decline notice, acceptance of award, interim report, final report, renewal application

**Why files in this domain group together**

- one award in one competition cycle
- one funder across every award applied for
- an award with the reports it obliges
- a proposal across its versions as a version family

**Template**

| dimension order | time first | why |
|---|---|---|
| funder → award → competition_cycle | no | Proposal. It mirrors §5.4 'an Applications template may define target institution → application cycle → document type' with the funder in the institution position, because a person reapplies to the same funder across cycles and expects those attempts side by side. |

**Collides with** — where this domain and another will fight over the same file

| other domain | the confusion, and what separates them | design cite |
|---|---|---|
| `acad.college-application` | both carry a cycle and reuse the same essays; a scholarship's target is a funder, not an admitting institution, and the two must not merge | §4.8 'an application packet does not silently absorb a document with a conflicting target institution' |
| `acad.financial-aid` | a scholarship is an aid type on the award letter and a separate competitive application in its own right | — |
| `res.research-project` | a fellowship proposal is a research artifact; the design's own multi-domain case covers the shape | §3.11 'An academic abstract submitted as part of a university application can retain project = PVA/RDP and document type = abstract while also carrying purpose = university application and target university = UChicago.' |
| `acad.recommendation-letter` | the same letter is reused for a funder and for an admissions target; the target is what separates the copies | §4.8 'an application packet does not silently absorb a document with a conflicting target institution' |

**Sensitivity** — `none`. An application concerns the corpus holder. A budget or an aid-linked scholarship carries financial detail and reaches protection through the financial collision, not through a class assigned here.

---

### 23. Tuition billing and the student account

`acad.tuition-billing` · **proposal** · sensitivity: `potentially_sensitive`

> The bursar's running account for one student at one institution — charges, payments, refunds and holds, per term.

**Design basis** — none. `design_cite` is null: no design sentence names this domain. It is a proposal for Joseph.

**Schema — the fields this domain, and only this domain, legitimises**

| field | type | example | reliability ceiling | why this field exists and why that ceiling |
|---|---|---|---|---|
| `institution` | string | the school billing the account | `validated` | The same role the design gives finance in §3.11 'Finance files may use institution, account type, tax year, and record type.', applied to a school. |
| `term_billed` | string | the term the charges belong to | `validated` | §3.10 'Academic terms such as Spring 2025, AY 2024-25, and Michaelmas Term 2024 require dedicated patterns rather than generic parsing.'. A bursar account is reconciled per term, which is what makes the term the audit unit here. |
| `account_record_type` | enum | the kind of account document | `validated` | The same field name the design gives finance in §3.11 'Finance files may use institution, account type, tax year, and record type.', with school-specific values (statement, payment receipt, refund, hold notice, payment plan). |
| `charge_category` | string | what the charge is for | `validated` | Proposal. Tuition, housing, fees and health insurance appear as separate lines and are separately disputed; treating a bill as one undifferentiated thing loses the fact people search by. |
| `payer` | string | who paid | `user_confirmed` | Proposal. A parent, an employer or a sponsor may pay, and the payer's identity must not be inferred from a name appearing on a statement. |
| `hold_status` | enum | an account hold blocking registration | `validated` | A hold term beside an institution name. A hold is the thing a person urgently searches for, and it is printed rather than inferred. |

**Recognition**

*Deterministic — each rule is a pattern **plus** a corroborating context:*

- a bursar term ('student account', 'bursar', 'tuition statement', 'account balance', 'payment plan') co-occurring with a gazetteer school name at a word boundary
- a billing record-type term co-occurring with a school name and an academic-term pattern
- a hold term ('registration hold', 'account hold') co-occurring with a school name
- a charge-category term ('tuition', 'housing', 'student fee', 'health insurance', 'meal plan') co-occurring with a bursar term and an academic-term pattern

*Needs the LLM — language interpretation a rule cannot do safely:*

- a payment receipt that names neither the school nor the term
- distinguishing a tuition refund from an aid disbursement
- correspondence disputing a charge that names no record type

*Never alone — bare signals that must not establish this domain by themselves:*

- a currency figure
- a school name — §4.9 'A university name alone should not create a group because Columbia can appear as an authoring school, course provider, target institution, employer, research venue, or merely a cited organization.'
- the word 'statement', which is shared with banking and with personal statements

**Work types** — tuition statement, payment receipt, payment plan agreement, refund notice, hold notice, tax form for tuition, housing charge, fee schedule, sponsor billing authorisation, collections notice

**Why files in this domain group together**

- one term's charges with the payments that settled them
- one institution across the whole account history
- a dispute with its correspondence and its resolution

**Template**

| dimension order | time first | why |
|---|---|---|
| institution → term_billed → account_record_type | no | Proposal. Institution leads per §5.5 'For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders.'; the term sits second because a bursar account genuinely reconciles per term, and the record type is the leaf. |

**Collides with** — where this domain and another will fight over the same file

| other domain | the confusion, and what separates them | design cite |
|---|---|---|
| `fin.financial-records` | a tuition statement is a financial record with a school on it; the design protects finance before placement, so the finance reading governs handling | §3.15 'Finance, identity, medical, and legal material should be implemented first as safety domains' |
| `acad.financial-aid` | aid appears as a credit line on the bill; the award is the aid office's record, the credit line is the bursar's | — |
| `acad.course-enrollment` | both carry school and term; a bill carries no course code and no work type | — |
| `acad.campus-employment` | a student wage and a tuition charge can offset each other on one statement | — |

**Sensitivity** — `potentially_sensitive`. Proposal, not design. A student account is an account statement, which §7.3 'passport scans, medical documents, account statements, visas, legal forms, or credentials' names among protected material, and §3.15 'Finance, identity, medical, and legal material should be implemented first as safety domains' puts financial material behind protection. The phrase is the design's; no handling class is assigned here.

---

### 24. Campus employment

`acad.campus-employment` · **proposal** · sensitivity: `potentially_sensitive`

> A job held on campus while enrolled — hiring, timesheets and pay — where the employer is also the school.

**Design basis** — none. `design_cite` is null: no design sentence names this domain. It is a proposal for Joseph.

**Schema — the fields this domain, and only this domain, legitimises**

| field | type | example | reliability ceiling | why this field exists and why that ceiling |
|---|---|---|---|---|
| `institution` | string | the employing school | `validated` | A gazetteer school name beside employment language. Employer and school are the same entity here, which is exactly why the roles must stay separate fields per §3.8 'An application essay can mention the author's current school and the university to which the essay is addressed.'. |
| `department_or_unit` | string | the hiring unit | `validated` | Proposal. A student may hold three jobs at one school; the unit is what separates them, and the school alone cannot. |
| `position` | string | the job title | `direct` | Read from a labelled slot on an offer or timesheet, which §3.5 'such as a content hash, EXIF timestamp, a document title, or a labeled form field' makes direct. |
| `employment_period` | string | the period worked | `validated` | Narrow date extraction only, per §3.10 'file names and documents frequently contain numbers that look like years but are course identifiers, version numbers, build numbers, ZIP codes, or other unrelated values'. Campus jobs are bounded by terms and by funding, not by calendar years. |
| `employment_record_type` | string | the kind of employment document | `validated` | An employment record-type term beside an institution name. |
| `funding_source` | enum | whether the position is work-study or departmentally funded | `validated` | Proposal. Work-study funding carries an aid consequence that a departmental wage does not, and the distinction is printed on the authorisation. |

**Recognition**

*Deterministic — each rule is a pattern **plus** a corroborating context:*

- an employment term ('timesheet', 'offer of employment', 'student employment', 'hourly', 'payroll') co-occurring with a gazetteer school name at a word boundary
- a work-study term co-occurring with a school name or an award-year pattern
- an onboarding term ('I-9', 'direct deposit', 'employment eligibility') co-occurring with a school or department name

*Needs the LLM — language interpretation a rule cannot do safely:*

- a supervisor's email that establishes a job without naming a position
- distinguishing a paid campus job from an unpaid volunteer role
- a training document that could be for the job or for a course

*Never alone — bare signals that must not establish this domain by themselves:*

- a school name — §4.9 'A university name alone should not create a group because Columbia can appear as an authoring school, course provider, target institution, employer, research venue, or merely a cited organization.'
- the word 'timesheet' with no employer
- a department name, which appears throughout an academic corpus

**Work types** — job posting, offer of employment, timesheet, pay statement, onboarding form, supervisor evaluation, training record, work-study authorisation, termination notice, schedule

**Why files in this domain group together**

- one position in one unit across the period worked
- an onboarding packet issued as one set
- one employer across every campus position held

**Template**

| dimension order | time first | why |
|---|---|---|
| institution → department_or_unit → position | no | Proposal. It follows §5.4 'a Career template may define company → role or recruiting cycle → document type''s shape — organisation, then role — with the unit standing in for the company, because at one school the unit is what distinguishes two jobs. |

**Collides with** — where this domain and another will fight over the same file

| other domain | the confusion, and what separates them | design cite |
|---|---|---|
| `acad.teaching-assistantship` | an assistantship is campus employment; its distinguishing evidence is a course code, which no other campus job carries | — |
| `career.offer-and-negotiation` | an offer letter and a pay statement are career artifacts; the campus reading is established by the school being the employer | §5.4 'a Career template may define company → role or recruiting cycle → document type' |
| `acad.financial-aid` | work-study wages are an aid type, so the authorisation belongs to both | — |
| `fin.financial-records` | pay statements are financial records the design protects before placement | §3.15 'Finance, identity, medical, and legal material should be implemented first as safety domains' |

**Sensitivity** — `potentially_sensitive`. Proposal, not design. Onboarding forms and pay statements carry identity and account detail of the kind §7.3 'passport scans, medical documents, account statements, visas, legal forms, or credentials' names. The phrase is the design's; no handling class is assigned here.

---

### 25. Thesis or dissertation

`acad.thesis-dissertation` · **inference** · sensitivity: `none`

> One long supervised written work submitted for a degree — its chapters, its committee, and its defence.

**Design basis** — Extends both academic coursework and research and lab work, the two launch domains named in §3.15 'academic coursework, college applications, research and lab work, career and recruiting, photos and captures, and code projects', to an artifact the design does not name. Its stage vocabulary is borrowed from §5.4 'a Research template may define project → stage → artifact type'.

**Schema — the fields this domain, and only this domain, legitimises**

| field | type | example | reliability ceiling | why this field exists and why that ceiling |
|---|---|---|---|---|
| `degree` | string | the degree the work is submitted for | `validated` | Inference. A thesis exists only in relation to a degree; a degree-name pattern beside a thesis term is checkable and is what separates a dissertation from a manuscript. |
| `advisor` | string | the supervising faculty member | `direct` | Read from a labelled slot on a title page or committee form, which §3.5 'such as a content hash, EXIF timestamp, a document title, or a labeled form field' makes direct. A role, not authorship, and never a dimension: §3.8 'It should avoid using authorship or creator identity as a destination dimension.'. |
| `committee` | string | a committee member | `direct` | Read from a signature page. Plainly multi-valued, which is the multiplicity question the fact layer already carries; recorded as metadata, never as a level. |
| `defense_date` | date | the date of the defence | `validated` | Narrow date extraction only: §3.10 'file names and documents frequently contain numbers that look like years but are course identifiers, version numbers, build numbers, ZIP codes, or other unrelated values'. The defence date is the fixed point a whole corpus is organised around. |
| `thesis_stage` | enum | the stage the artifact belongs to | `validated` | A stage term ('proposal', 'draft', 'defence copy', 'revision', 'final deposit') beside a thesis term. Borrowed from the design's Research template, §5.4 'a Research template may define project → stage → artifact type'. |
| `chapter` | string | the chapter or section | `validated` | A chapter pattern beside a thesis or degree term. Chapters are the unit a thesis corpus is actually navigated by, and a bare chapter number is exactly the value §3.10 'file names and documents frequently contain numbers that look like years but are course identifiers, version numbers, build numbers, ZIP codes, or other unrelated values' warns not to read as a date. |

**Recognition**

*Deterministic — each rule is a pattern **plus** a corroborating context:*

- a thesis term ('thesis', 'dissertation', 'defence', 'defense', 'committee') co-occurring with a degree-name pattern or a gazetteer school name at a word boundary
- an advisor- or committee-labelled slot co-occurring with a thesis term
- a chapter pattern co-occurring with a thesis or dissertation term in the document title zone — §3.7 'a value in a filename or document title carries more meaning than the same value in a footer or a late body-page reference'
- a deposit or submission term ('final deposit', 'ProQuest', 'embargo') co-occurring with a thesis term

*Needs the LLM — language interpretation a rule cannot do safely:*

- a chapter draft that reads as a standalone paper and names no thesis
- distinguishing a thesis chapter from a manuscript prepared for publication from the same work
- committee correspondence that never names the stage

*Never alone — bare signals that must not establish this domain by themselves:*

- the word 'draft'
- a chapter number
- an advisor's name — §3.8 'It should avoid using authorship or creator identity as a destination dimension.'
- a long PDF

**Work types** — proposal, chapter draft, full draft, defence copy, defence slides, committee form, signature page, revision memo, final deposit, embargo request, figure, bibliography, supplementary data

**Why files in this domain group together**

- one thesis across its chapters and drafts as a version family
- a defence with its slides, committee form and signature page
- a chapter across its revisions

**Template**

| dimension order | time first | why |
|---|---|---|
| degree → thesis_stage → chapter | no | Inference. Stage before chapter because a person looks for 'the defence copy' as a whole far more often than for 'chapter 3 of the defence copy'; both satisfy §5.5 'a parent dimension should provide the context required to understand the child'. No time level, per §5.5 'For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders.'. |

**Collides with** — where this domain and another will fight over the same file

| other domain | the confusion, and what separates them | design cite |
|---|---|---|
| `res.research-project` | a thesis chapter and a manuscript are often the same text; the research reading carries a project identifier and a venue, the thesis reading carries a degree and a committee | §3.11 'Research files may use project, stage, artifact type, lab, and venue.' |
| `acad.graduate-program` | a prospectus is a milestone artifact and the thesis's first chapter at once | — |
| `acad.lab-course` | lab data feeds a thesis; the data file belongs to whichever group its own evidence supports, not to both by inheritance | — |
| `acad.course-enrollment` | a thesis is often registered as a course with a code, which pulls the whole corpus toward the coursework template | §3.5 'BUSIB 4300 becomes a course fact only when the engine finds a course-code pattern together with academic context such as "syllabus," "lecture," "credits," "instructor," or "semester."' |

**Sensitivity** — `none`. A thesis is the holder's own work. Human-subject data under an embargo would be a different matter and is not assumed here.

**Open question (unresolved — for Joseph)**

> Should a thesis live under Academics as the capstone of a degree, or under Research beside the project it came out of? §5.1 'Academics, Applications, Research, Career, Personal Records, Finance and Administration, Photos and Captures, Code and Projects, and Media or Miscellaneous Personal Material' offers both as top-level candidates and a doctoral corpus supports either.

---

### 26. Undergraduate research placement

`acad.undergrad-research` · **inference** · sensitivity: `none`

> A time-bounded research placement held while enrolled — a summer programme or a term in a lab — with a supervisor and no course code.

**Design basis** — Extends the research and lab work launch domain of §3.15 'academic coursework, college applications, research and lab work, career and recruiting, photos and captures, and code projects', whose fields the design gives as §3.11 'Research files may use project, stage, artifact type, lab, and venue.', to the placement rather than the project.

**Schema — the fields this domain, and only this domain, legitimises**

| field | type | example | reliability ceiling | why this field exists and why that ceiling |
|---|---|---|---|---|
| `host_institution` | string | the institution hosting the placement | `validated` | Inference. The host is frequently not the student's own school, and confusing the two is the role failure §3.8 'An application essay can mention the author's current school and the university to which the essay is addressed.' describes. |
| `lab` | string | the research group | `validated` | Named in §3.11 'Research files may use project, stage, artifact type, lab, and venue.'. A lab or group name beside a research term at a word boundary. |
| `supervisor` | string | the principal investigator or mentor | `direct` | Read from a labelled slot on a placement agreement. A role, not authorship: §3.8 'It should avoid using authorship or creator identity as a destination dimension.'. |
| `placement_period` | string | the period of the placement | `validated` | Inference. A summer placement is bounded by dates rather than by a term, so it needs a date pattern rather than the academic-term patterns of §3.10 'Academic terms such as Spring 2025, AY 2024-25, and Michaelmas Term 2024 require dedicated patterns rather than generic parsing.'. |
| `programme` | string | the funded programme the placement runs under | `validated` | A named programme beside a research and application term. It is the fact that makes an otherwise anonymous summer findable years later. |
| `placement_artifact_type` | string | the kind of placement document | `validated` | An artifact term beside a lab or programme name. |

**Recognition**

*Deterministic — each rule is a pattern **plus** a corroborating context:*

- a research-placement term ('research assistant', 'summer research', 'undergraduate research', 'lab rotation') co-occurring with a gazetteer institution name at a word boundary
- a named research programme co-occurring with an application or acceptance term
- a lab or group name co-occurring with a supervisor-labelled slot
- a poster or symposium term co-occurring with a named research programme

*Needs the LLM — language interpretation a rule cannot do safely:*

- a data or analysis file that is placement output only by context
- distinguishing placement work from a lab course with the same techniques
- a report that could be a course report or a placement report

*Never alone — bare signals that must not establish this domain by themselves:*

- the word 'lab' — a research group, a course, a company and a directory all use it
- a supervisor's name — §3.8 'It should avoid using authorship or creator identity as a destination dimension.'
- an institution name — §4.9 'A university name alone should not create a group because Columbia can appear as an authoring school, course provider, target institution, employer, research venue, or merely a cited organization.'

**Work types** — placement application, acceptance letter, placement agreement, training record, literature notes, protocol, raw data, analysis notebook, poster, symposium abstract, final report, supervisor evaluation, stipend record

**Why files in this domain group together**

- one placement in one lab across its period
- a poster with the data and analysis behind it
- an application with its acceptance and its agreement

**Template**

| dimension order | time first | why |
|---|---|---|
| lab → placement_period → placement_artifact_type | no | Inference. The lab leads because it is the durable name a person remembers; the period sits second because a student may return to the same lab across several summers and needs them separated. It is §5.4 'a Research template may define project → stage → artifact type' with the placement period standing in for stage. |

**Collides with** — where this domain and another will fight over the same file

| other domain | the confusion, and what separates them | design cite |
|---|---|---|
| `res.research-project` | the placement is the container, the project is the intellectual content; a poster carries both and the project may outlive the placement | §3.11 'Research files may use project, stage, artifact type, lab, and venue.' |
| `acad.lab-course` | both produce protocols and data under a named lab; the course version carries a course code and a term, the placement carries a supervisor and no code | — |
| `acad.internship-for-credit` | a placement taken for credit is both; the credit reading carries a course code and a faculty sponsor | — |
| `acad.scholarship-fellowship` | the funded programme is often a fellowship, so the application belongs to both | — |

**Sensitivity** — `none`. Placement material concerns the corpus holder and the group's work. Human-subject or unpublished third-party data would be a different matter and is not assumed here.

---

### 27. Student conference travel and presentation

`acad.conference-travel-student` · **inference** · sensitivity: `none`

> Attending or presenting at one conference — the submission, the funding to get there, and the trip itself.

**Design basis** — Extends the research and lab work launch domain of §3.15 'academic coursework, college applications, research and lab work, career and recruiting, photos and captures, and code projects', whose field list already contains venue: §3.11 'Research files may use project, stage, artifact type, lab, and venue.'.

**Schema — the fields this domain, and only this domain, legitimises**

| field | type | example | reliability ceiling | why this field exists and why that ceiling |
|---|---|---|---|---|
| `venue` | string | the conference | `validated` | Named in §3.11 'Research files may use project, stage, artifact type, lab, and venue.'. A conference name beside a conference term at a word boundary. |
| `edition` | string | the specific instance of a recurring conference | `validated` | Inference. Conferences recur annually under one name; the edition is what separates two submissions to the same venue, and merging them would be the conflicting-fact failure of §4.9 'members carry irreconcilable course, institution, project, term, or purpose facts'. |
| `submission_type` | enum | poster | `validated` | A submission-type term beside a conference name. It determines what artifacts exist at all — a poster corpus and a talk corpus look nothing alike. |
| `submission_status` | enum | the outcome of the submission | `validated` | A status term ('submitted', 'accepted', 'rejected', 'withdrawn') beside a conference name and an edition. |
| `travel_funding_source` | string | the body funding the trip | `validated` | Inference. Student travel is funded by a grant or a department, and the reimbursement paperwork is a large part of the corpus. |
| `conference_artifact_type` | string | the kind of conference document | `validated` | An artifact term beside a conference name. |

**Recognition**

*Deterministic — each rule is a pattern **plus** a corroborating context:*

- a conference term ('conference', 'symposium', 'abstract submission', 'proceedings', 'call for papers') co-occurring with a named venue at a word boundary
- a submission-status term co-occurring with a named venue and an edition pattern
- a travel-funding term ('travel grant', 'travel award', 'reimbursement') co-occurring with a named venue

*Needs the LLM — language interpretation a rule cannot do safely:*

- a slide deck that is a conference talk only by context
- distinguishing a conference paper from a journal manuscript on the same work
- an itinerary that is conference travel rather than personal travel

*Never alone — bare signals that must not establish this domain by themselves:*

- the word 'conference'
- a four-digit year — §3.10 'file names and documents frequently contain numbers that look like years but are course identifiers, version numbers, build numbers, ZIP codes, or other unrelated values'
- an itinerary or boarding pass, which is ordinary travel material

**Work types** — abstract, submission confirmation, acceptance notice, poster, talk slides, proceedings paper, registration receipt, travel grant application, itinerary, reimbursement claim, certificate of attendance, programme booklet

**Why files in this domain group together**

- one conference edition with its submission, presentation and travel
- one venue across the editions attended
- a poster across its drafts as a version family

**Template**

| dimension order | time first | why |
|---|---|---|
| venue → edition → conference_artifact_type | no | Inference. The venue is the durable name and the edition is the enumerable child, satisfying §5.5 'a parent dimension should provide the context required to understand the child': 'poster' means nothing until the conference and year are known. |

**Collides with** — where this domain and another will fight over the same file

| other domain | the confusion, and what separates them | design cite |
|---|---|---|
| `pers.travel-record` | the itinerary, boarding pass and hotel booking are ordinary travel records that happen to serve a conference; the design lists travel as its own template area | §5.1 'Academics, Applications, Research, Career, Personal Records, Finance and Administration, Photos and Captures, Code and Projects, and Media or Miscellaneous Personal Material' |
| `res.research-project` | the abstract and poster are research artifacts with a venue; the conference reading owns the trip, the project reading owns the science | §3.11 'Research files may use project, stage, artifact type, lab, and venue.' |
| `fin.financial-records` | reimbursement claims and receipts are financial records the design protects before placement | §3.15 'Finance, identity, medical, and legal material should be implemented first as safety domains' |
| `acad.undergrad-research` | a placement's symposium is a conference for the placement's purposes and produces the same artifacts | — |

**Sensitivity** — `none`. Conference material is professional. Reimbursement receipts carry payment detail and reach protection through the financial collision, not through a class assigned here.

**Open question (unresolved — for Joseph)**

> Does a conference trip belong under Academics or Research beside the work presented, or under Travel beside the trip? §5.1 'Academics, Applications, Research, Career, Personal Records, Finance and Administration, Photos and Captures, Code and Projects, and Media or Miscellaneous Personal Material' lists these as separate top-level candidates and the same set of files supports each.

---

### 28. Study abroad and exchange

`acad.study-abroad` · **proposal** · sensitivity: `potentially_sensitive`

> A term or year studying at a host institution abroad while remaining enrolled at home.

**Design basis** — none. `design_cite` is null: no design sentence names this domain. It is a proposal for Joseph.

**Schema — the fields this domain, and only this domain, legitimises**

| field | type | example | reliability ceiling | why this field exists and why that ceiling |
|---|---|---|---|---|
| `home_institution` | string | the school the student remains enrolled at | `validated` | Proposal. Two school roles in one record, and keeping them apart is exactly what §3.8 'An application essay can mention the author's current school and the university to which the essay is addressed.' requires; a merged school field would file a year abroad under the wrong university. |
| `host_institution` | string | the school attended abroad | `validated` | The counterpart role. |
| `programme_provider` | string | the third party running the exchange, when there is one | `validated` | Proposal. A provider is neither school and owns much of the paperwork. |
| `term_abroad` | string | the term or year spent away | `validated` | §3.10 'Academic terms such as Spring 2025, AY 2024-25, and Michaelmas Term 2024 require dedicated patterns rather than generic parsing.'. |
| `host_country` | string | the country studied in | `validated` | A gazetteer country name at a word boundary beside study-abroad language. It is the fact a person actually remembers a year abroad by. |
| `mobility_document_type` | string | the kind of study-abroad document | `validated` | A document-type term beside a host-institution or provider name. Visa and enrolment paperwork dominate this corpus and have no domestic counterpart. |

**Recognition**

*Deterministic — each rule is a pattern **plus** a corroborating context:*

- a study-abroad term ('study abroad', 'exchange', 'host institution', 'learning agreement') co-occurring with a gazetteer institution name at a word boundary
- a student-visa term co-occurring with a host-institution name or a country name
- a learning-agreement or credit-approval term co-occurring with two distinct institution names
- a programme-provider name co-occurring with a study-abroad term and a host-institution or country name, where the provider name is neither institution

*Needs the LLM — language interpretation a rule cannot do safely:*

- coursework from abroad whose institution is named only in another language
- distinguishing an exchange term from a summer programme abroad
- an itinerary that is programme travel rather than personal travel

*Never alone — bare signals that must not establish this domain by themselves:*

- a country name
- an institution name — §4.9 'A university name alone should not create a group because Columbia can appear as an authoring school, course provider, target institution, employer, research venue, or merely a cited organization.'
- a boarding pass or itinerary

**Work types** — programme application, acceptance letter, learning agreement, credit pre-approval, student visa, residence permit, housing agreement, host transcript, insurance certificate, orientation material, coursework from abroad, re-entry form

**Why files in this domain group together**

- one term abroad at one host institution
- a visa application with its supporting documents
- a learning agreement with the host transcript that settles it

**Template**

| dimension order | time first | why |
|---|---|---|
| host_institution → term_abroad → mobility_document_type | no | Proposal. The host leads because the year abroad is remembered by where it was; the home institution stays metadata so a year abroad does not fragment across two school branches. |

**Collides with** — where this domain and another will fight over the same file

| other domain | the confusion, and what separates them | design cite |
|---|---|---|
| `acad.transfer-credit` | study-abroad credit is transfer credit; the study-abroad reading additionally carries a host institution and a term away | — |
| `pers.travel-record` | visas, flights and housing are travel records; a term abroad is not a trip and should not be absorbed into one | §5.1 'Academics, Applications, Research, Career, Personal Records, Finance and Administration, Photos and Captures, Code and Projects, and Media or Miscellaneous Personal Material' |
| `pers.identity-document` | a visa and a residence permit are among the protected records the design names | §4.9 'Rare but sensitive files such as passports, visas, and legal documents may be surfaced as protected records' |
| `acad.course-enrollment` | coursework from abroad carries a host course code that will not match the home school's codes | §4.9 'members carry irreconcilable course, institution, project, term, or purpose facts' |

**Sensitivity** — `potentially_sensitive`. §4.9 'Rare but sensitive files such as passports, visas, and legal documents may be surfaced as protected records' names visas explicitly, and §7.3 'passport scans, medical documents, account statements, visas, legal forms, or credentials' names visas among protected material. The phrase is the design's; no handling class is assigned here.

---

### 29. Clinical rotation and supervised practicum

`acad.clinical-rotation` · **proposal** · sensitivity: `potentially_sensitive`

> A supervised placement at a practice site that is a required part of a professional programme, logged and evaluated per block.

**Design basis** — none. `design_cite` is null: no design sentence names this domain. It is a proposal for Joseph.

**Schema — the fields this domain, and only this domain, legitimises**

| field | type | example | reliability ceiling | why this field exists and why that ceiling |
|---|---|---|---|---|
| `programme` | string | the professional programme requiring the rotation | `validated` | A professional-degree name beside rotation language. |
| `site` | string | the hospital, clinic, school or agency the placement is at | `validated` | Proposal. The site is neither the school nor an employer; it is a third party with its own onboarding, and it is the fact a person remembers a rotation by. |
| `service_or_specialty` | string | the service the block was on | `validated` | A specialty term beside a rotation term. It is the field that makes a rotation corpus navigable, because the site repeats across services. |
| `block` | string | the scheduled block the placement occupied | `validated` | Proposal. Rotations are scheduled in named blocks rather than terms, and a bare block number is exactly the value §3.10 'file names and documents frequently contain numbers that look like years but are course identifiers, version numbers, build numbers, ZIP codes, or other unrelated values' warns not to read as a date. |
| `preceptor` | string | the supervising practitioner | `direct` | Read from a labelled slot on an evaluation form. A role, not authorship: §3.8 'It should avoid using authorship or creator identity as a destination dimension.'. |
| `rotation_record_type` | string | the kind of rotation document | `validated` | A record-type term beside a site or specialty name. |

**Recognition**

*Deterministic — each rule is a pattern **plus** a corroborating context:*

- a rotation term ('clerkship', 'rotation', 'practicum', 'preceptor', 'clinical placement') co-occurring with a professional-degree name or a gazetteer institution name
- a specialty term co-occurring with a rotation term and a block pattern
- a site-onboarding term ('credentialing', 'badge', 'site orientation', 'immunisation requirement') co-occurring with a named site
- a case-log or hours-log term co-occurring with a rotation term

*Needs the LLM — language interpretation a rule cannot do safely:*

- reflective writing that is a rotation assignment only by context
- distinguishing site-issued training from programme-issued training
- notes whose specialty is implicit in the clinical vocabulary

*Never alone — bare signals that must not establish this domain by themselves:*

- a hospital or agency name, which appears in a corpus for many unrelated reasons
- a block number
- a specialty word, which is ordinary vocabulary in a health-professions corpus

**Work types** — rotation schedule, site onboarding packet, credentialing record, immunisation requirement, case log, hours log, preceptor evaluation, self-evaluation, reflective assignment, presentation, competency checklist, incident form

**Why files in this domain group together**

- one block at one site on one service
- a site's onboarding packet as one issued set
- one specialty across the blocks spent on it

**Template**

| dimension order | time first | why |
|---|---|---|
| programme → service_or_specialty → site | no | Proposal. Specialty above site because the specialty is what a person is trying to recall; the site beneath it satisfies §5.5 'a parent dimension should provide the context required to understand the child'. Block stays metadata because block labels are opaque a year later. |

**Collides with** — where this domain and another will fight over the same file

| other domain | the confusion, and what separates them | design cite |
|---|---|---|
| `med.clinician-clinical-note` | case logs and clinical notes concern patients; the design names medical material a safety domain to be protected before any automated placement | §3.15 'Finance, identity, medical, and legal material should be implemented first as safety domains' |
| `acad.professional-school` | the rotation is part of the programme; only the rotation carries a site and a block | — |
| `acad.internship-for-credit` | both are supervised placements for credit; a rotation is required and scheduled by the programme, an internship is arranged by the student | — |
| `acad.campus-employment` | a paid rotation produces employment records alongside the academic ones | — |

**Sensitivity** — `potentially_sensitive`. Proposal, not design. Case logs and clinical assignments can carry patient detail, and §3.15 'Finance, identity, medical, and legal material should be implemented first as safety domains' names medical material as protected first; §7.3 'passport scans, medical documents, account statements, visas, legal forms, or credentials' names medical documents. The phrase is the design's; no handling class is assigned here.

**Open question (unresolved — for Joseph)**

> Rotation material can contain de-identified patient detail that no rule will reliably spot. Should an entire clinical branch be treated as protected by default rather than per file? §3.15 'the system detects and protects them before any cloud or automated placement decision is allowed' requires protection before placement but does not say whether a whole branch may be marked.

---

### 30. Internship or co-op taken for credit

`acad.internship-for-credit` · **proposal** · sensitivity: `potentially_sensitive`

> A work placement that is simultaneously a job and a registered course, with an employer and a faculty sponsor.

**Design basis** — none. `design_cite` is null: no design sentence names this domain. It is a proposal for Joseph.

**Schema — the fields this domain, and only this domain, legitimises**

| field | type | example | reliability ceiling | why this field exists and why that ceiling |
|---|---|---|---|---|
| `host_organisation` | string | the employer hosting the placement | `validated` | Proposal. The host is an employer, which is the role the design gives the Career template's company: §5.4 'a Career template may define company → role or recruiting cycle → document type'. |
| `subject` | string | the course code the placement is registered under | `validated` | §3.5 'BUSIB 4300 becomes a course fact only when the engine finds a course-code pattern together with academic context such as "syllabus," "lecture," "credits," "instructor," or "semester."'. This field is what makes the placement academic rather than purely employment, and it is the discriminator against a plain internship. |
| `term` | string | the term the credit is registered in | `validated` | §3.10 'Academic terms such as Spring 2025, AY 2024-25, and Michaelmas Term 2024 require dedicated patterns rather than generic parsing.'. |
| `faculty_sponsor` | string | the faculty member supervising the credit | `direct` | Read from a labelled slot on a learning agreement. A role, not authorship: §3.8 'It should avoid using authorship or creator identity as a destination dimension.'. |
| `site_supervisor` | string | the manager at the host organisation | `direct` | Read from a labelled slot. A second, distinct supervisory role — the pair is the same separation §3.8 'An application essay can mention the author's current school and the university to which the essay is addressed.' demands. |
| `credit_requirement_type` | string | the kind of academic deliverable the credit requires | `validated` | A requirement term ('learning agreement', 'hours log', 'reflection', 'final report', 'employer evaluation') beside a validated course code or a host name. |

**Recognition**

*Deterministic — each rule is a pattern **plus** a corroborating context:*

- an internship-for-credit term ('learning agreement', 'internship credit', 'co-op', 'experiential credit') co-occurring with a validated course code or a gazetteer school name
- a validated course code co-occurring with an employer name and an internship term
- an hours-log or employer-evaluation term co-occurring with a validated course code

*Needs the LLM — language interpretation a rule cannot do safely:*

- a reflection essay that is a credit deliverable only by context
- distinguishing an internship taken for credit from one taken without it
- work product that belongs to the employer rather than to the course

*Never alone — bare signals that must not establish this domain by themselves:*

- an employer name — the same hazard §4.9 'A university name alone should not create a group because Columbia can appear as an authoring school, course provider, target institution, employer, research venue, or merely a cited organization.' describes for universities
- the word 'internship'
- a course code with no placement evidence

**Work types** — learning agreement, position description, offer letter, hours log, reflection, midpoint check-in, final report, employer evaluation, faculty evaluation, work sample, confidentiality agreement

**Why files in this domain group together**

- one placement in one term under one course registration
- a learning agreement with the deliverables it requires
- one employer across the placements held there

**Template**

| dimension order | time first | why |
|---|---|---|
| host_organisation → term → credit_requirement_type | no | Proposal. The host leads because it is what a person and a future employer both recognise, which follows §5.4 'a Career template may define company → role or recruiting cycle → document type' rather than the Academic template; the course registration stays metadata because it is an administrative wrapper, not how anyone searches. |

**Collides with** — where this domain and another will fight over the same file

| other domain | the confusion, and what separates them | design cite |
|---|---|---|
| `career.internship-application` | the offer letter and position description are career artifacts; the credit reading is established by a course code and a learning agreement | §5.4 'a Career template may define company → role or recruiting cycle → document type' |
| `acad.course-enrollment` | the placement is registered as a course, so the coursework template will claim it; only the placement carries a host organisation | §3.5 'BUSIB 4300 becomes a course fact only when the engine finds a course-code pattern together with academic context such as "syllabus," "lecture," "credits," "instructor," or "semester."' |
| `acad.clinical-rotation` | both are supervised placements for credit; a rotation is scheduled by the programme, an internship is arranged by the student | — |
| `acad.campus-employment` | an on-campus internship for credit is both, and produces payroll and academic records together | — |

**Sensitivity** — `potentially_sensitive`. Proposal, not design. Work product from a placement may belong to the host organisation and be under a confidentiality agreement — third-party content of the kind §2.9 'treating addresses and message content as potentially sensitive' applies the phrase to. No handling class is assigned here.

---

### 31. Language study and proficiency certification

`acad.language-study` · **proposal** · sensitivity: `none`

> Learning a language and proving it — levels, certificates and the proficiency tests institutions ask for.

**Design basis** — none. `design_cite` is null: no design sentence names this domain. It is a proposal for Joseph.

**Schema — the fields this domain, and only this domain, legitimises**

| field | type | example | reliability ceiling | why this field exists and why that ceiling |
|---|---|---|---|---|
| `language` | string | the language studied | `validated` | Proposal. A language name is a closed vocabulary and matches at a word boundary, which §3.7 'It should use word-boundary matching rather than substring matching.' requires; several language names are also common words and must not match as substrings. |
| `proficiency_framework` | string | the scale the level is expressed on | `validated` | Proposal, and load-bearing: a level is meaningless without its framework, and two frameworks' levels are not comparable. Recognised by a framework name beside a level pattern. |
| `level` | string | the level within that framework | `validated` | A level pattern beside a framework name. It is the field a person navigates by and the field that changes over years. |
| `certification` | string | the proficiency examination or certificate | `validated` | A certification name beside a language name at a word boundary. |
| `language_study_artifact_type` | string | the kind of study material | `validated` | An artifact term beside a language or framework name. |
| `target_requirement` | string | the institution or programme requiring the proficiency | `validated` | Proposal. A proficiency test is usually taken because something demands it, and the requirement is what links this domain to an application. |

**Recognition**

*Deterministic — each rule is a pattern **plus** a corroborating context:*

- a proficiency-framework name co-occurring with a level pattern
- a certification name co-occurring with a language name at a word boundary
- a language name co-occurring with a study term ('grammar', 'vocabulary', 'listening', 'oral exam', 'placement test') at a word boundary
- a proficiency-requirement term co-occurring with a certification name and a gazetteer institution name

*Needs the LLM — language interpretation a rule cannot do safely:*

- material written in the target language whose level is implicit
- distinguishing language coursework taken for credit from self-directed study
- a certificate whose framework is named only in the target language

*Never alone — bare signals that must not establish this domain by themselves:*

- a language name, which is also a nationality, a cuisine, a font and a programming language
- a bare level token, which collides with grades, versions and sizes
- the word 'test'

**Work types** — placement test, level certificate, proficiency score report, vocabulary list, grammar notes, listening material, oral exam recording, tutor session notes, immersion programme record, translation exercise

**Why files in this domain group together**

- one language across the levels worked through
- one certification with its preparation and its score report
- a course or programme in one language in one period

**Template**

| dimension order | time first | why |
|---|---|---|
| language → level → language_study_artifact_type | no | Proposal. Language then level is the natural progression and satisfies §5.5 'a parent dimension should provide the context required to understand the child': a level is uninterpretable without its language and framework. No time level, per §5.5 'For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders.'. |

**Collides with** — where this domain and another will fight over the same file

| other domain | the confusion, and what separates them | design cite |
|---|---|---|
| `acad.standardized-testing` | a proficiency exam is a standardised test with a sitting; the language reading owns the language and level, the testing reading owns the registration and score send | — |
| `acad.course-enrollment` | a language course taken for credit carries a course code and a term that the self-directed material does not | §3.5 'BUSIB 4300 becomes a course fact only when the engine finds a course-code pattern together with academic context such as "syllabus," "lecture," "credits," "instructor," or "semester."' |
| `acad.study-abroad` | an immersion term abroad produces both, and the proficiency certificate is often what the exchange required | — |
| `acad.college-application` | a proficiency score is an application component; the requiring institution and the target university are the same role and must be reconciled, not duplicated | §4.8 'an application packet does not silently absorb a document with a conflicting target institution' |

**Sensitivity** — `none`. Language study material concerns the corpus holder. An oral-exam recording is a voice recording of the holder and is not material the design names as potentially sensitive.

---

### 32. Music and arts juries, recitals and portfolio review

`acad.arts-jury-portfolio` · **proposal** · sensitivity: `none`

> Performance and studio assessment — the repertoire or body of work, the panel that judges it, and the recordings that document it.

**Design basis** — none. `design_cite` is null: no design sentence names this domain. It is a proposal for Joseph.

**Schema — the fields this domain, and only this domain, legitimises**

| field | type | example | reliability ceiling | why this field exists and why that ceiling |
|---|---|---|---|---|
| `school` | string | the conservatory, school or department | `validated` | A gazetteer school name at a word boundary. |
| `discipline` | string | the instrument, medium or studio | `validated` | Proposal. The instrument or medium is the organising fact of an arts corpus in the way a course code is for a lecture corpus, and a person may study two. |
| `assessment_event` | string | the jury, recital or review the work was presented at | `validated` | Proposal, and the anchor: an arts corpus clusters around dated events rather than around assignments. An event term beside a discipline or school name. |
| `repertoire_or_work` | string | the piece or work presented | `user_confirmed` | Proposal. Titles of works are ambiguous with filenames, performers, and everything else in a media corpus; asserting one by inference would be unreliable, so only the user establishes it. |
| `panel_member` | string | a member of the jury or review panel | `direct` | Read from a labelled slot on an evaluation sheet. A role, never a dimension: §3.8 'It should avoid using authorship or creator identity as a destination dimension.'. |
| `arts_artifact_type` | string | the kind of material | `validated` | An artifact term beside an assessment-event or discipline term. Recordings and scores dominate and have no counterpart in a document corpus. |

**Recognition**

*Deterministic — each rule is a pattern **plus** a corroborating context:*

- an arts-assessment term ('jury', 'recital', 'portfolio review', 'critique', 'audition') co-occurring with a gazetteer school name or a discipline term
- a repertoire term ('programme notes', 'score', 'movement', 'opus') co-occurring with a recital or jury term
- an evaluation term ('jury sheet', 'panel comments', 'rubric') co-occurring with an assessment-event term

*Needs the LLM — language interpretation a rule cannot do safely:*

- an audio or video file that is a jury recording only by context
- distinguishing a practice recording from a submitted performance
- a portfolio image whose work and series must be read from a caption

*Never alone — bare signals that must not establish this domain by themselves:*

- an audio or video file
- the word 'recital'
- a work title in a filename

**Work types** — jury sheet, panel comments, programme notes, score, performance recording, practice recording, portfolio image, artist statement, audition material, recital programme, studio critique notes, exhibition record

**Why files in this domain group together**

- one jury or recital with its programme, recording and evaluation
- one work across its rehearsal and performance recordings as a version family
- one discipline across the terms studied

**Template**

| dimension order | time first | why |
|---|---|---|
| discipline → assessment_event → arts_artifact_type | no | Proposal. Discipline leads because a musician who also paints has two disjoint bodies of work; the assessment event is the enumerable child and satisfies §5.5 'a parent dimension should provide the context required to understand the child'. |

**Collides with** — where this domain and another will fight over the same file

| other domain | the confusion, and what separates them | design cite |
|---|---|---|
| `acad.course-enrollment` | lessons and studio classes carry course codes and terms; the jury reading is established by an assessment event | §3.5 'BUSIB 4300 becomes a course fact only when the engine finds a course-code pattern together with academic context such as "syllabus," "lecture," "credits," "instructor," or "semester."' |
| `pers.photo-event` | performance photographs and recordings carry capture metadata and will be claimed by the media template, whose order the design puts time first | §5.4 'a Photos template may define year → event' |
| `acad.college-application` | an audition portfolio is an application component with a target institution | §4.8 'an application packet does not silently absorb a document with a conflicting target institution' |
| `acad.credential-certificate` | graded examination certificates from an external board are credentials as well as assessment records | — |

**Sensitivity** — `none`. Performance material is the holder's own work. Recordings of an ensemble contain other performers, which is an ordinary third-party case and no handling class is assigned here.

**Open question (unresolved — for Joseph)**

> Arts material is media-heavy, and the design puts time first for capture-based media (§5.4 'a Photos template may define year → event') but subject first for document domains (§5.5 'For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders.'). A jury corpus is both. Which rule wins?

---

### 33. Athletics eligibility and student-athlete compliance

`acad.athletics-eligibility` · **proposal** · sensitivity: `potentially_sensitive`

> The paperwork that keeps a student eligible to compete — clearinghouse registration, academic certification, and per-season compliance.

**Design basis** — none. `design_cite` is null: no design sentence names this domain. It is a proposal for Joseph.

**Schema — the fields this domain, and only this domain, legitimises**

| field | type | example | reliability ceiling | why this field exists and why that ceiling |
|---|---|---|---|---|
| `institution` | string | the school competed for | `validated` | A gazetteer school name beside athletics language. |
| `governing_body` | string | the association setting the eligibility rules | `validated` | Proposal. The rules come from a body that is not the school, and its correspondence is a separate stream; conflating them loses who decided what. |
| `sport` | string | the sport | `validated` | A sport name beside an eligibility or roster term at a word boundary. |
| `season` | string | the competition season | `validated` | Proposal. A season is a named span that does not align with an academic term, so it needs its own pattern for the reason §3.10 'Academic terms such as Spring 2025, AY 2024-25, and Michaelmas Term 2024 require dedicated patterns rather than generic parsing.' gives. |
| `eligibility_status` | enum | the certification status recorded | `validated` | A status term ('certified', 'pending', 'ineligible', 'medical hardship', 'redshirt') beside a governing-body or institution name. It is printed on the determination, not inferred. |
| `compliance_record_type` | string | the kind of compliance document | `validated` | A record-type term beside an athletics or governing-body term. |

**Recognition**

*Deterministic — each rule is a pattern **plus** a corroborating context:*

- an eligibility term ('eligibility', 'clearinghouse', 'certification', 'compliance', 'amateurism') co-occurring with a sport name or a gazetteer school name
- a governing-body name co-occurring with a registration or eligibility term
- a roster or season term co-occurring with a sport name and an institution name

*Needs the LLM — language interpretation a rule cannot do safely:*

- correspondence about a status change that names no status
- distinguishing recruiting communication from eligibility administration
- a schedule that is a competition season rather than a course schedule

*Never alone — bare signals that must not establish this domain by themselves:*

- a sport name, which is ordinary vocabulary
- a school name — §4.9 'A university name alone should not create a group because Columbia can appear as an authoring school, course provider, target institution, employer, research venue, or merely a cited organization.'
- a season-shaped year span

**Work types** — clearinghouse registration, amateurism certification, academic eligibility certification, physical clearance, roster form, team schedule, travel letter, compliance attestation, waiver request, transfer portal record, name-and-likeness agreement

**Why files in this domain group together**

- one season for one sport at one institution
- an eligibility determination with the documents submitted for it
- one governing body across its correspondence

**Template**

| dimension order | time first | why |
|---|---|---|
| sport → season → compliance_record_type | no | Proposal. Sport then season is how an athlete's material is remembered; the institution stays metadata because a transferring athlete would otherwise have their career split across two branches. |

**Collides with** — where this domain and another will fight over the same file

| other domain | the confusion, and what separates them | design cite |
|---|---|---|
| `acad.transcript-record` | academic eligibility is certified from a transcript, so the same transcript serves both | — |
| `med.medical-certification-letter` | physical clearances and medical-hardship waivers carry clinical detail the design protects first | §3.15 'Finance, identity, medical, and legal material should be implemented first as safety domains' |
| `acad.college-application` | athletic recruiting runs alongside admissions and produces institution-targeted material in the same cycle | §4.8 'an application packet does not silently absorb a document with a conflicting target institution' |
| `acad.transfer-credit` | a transfer affects both eligibility and credit, and the two records arrive together | — |

**Sensitivity** — `potentially_sensitive`. Proposal, not design. Physical clearances and hardship waivers carry medical detail, and §7.3 'passport scans, medical documents, account statements, visas, legal forms, or credentials' names medical documents among protected material. The phrase is the design's; no handling class is assigned here.

---

### 34. Academic advising and registration planning

`acad.advising` · **proposal** · sensitivity: `none`

> The conversation and the planning around what to take next — advisor notes, plans of study, holds and registration records.

**Design basis** — none. `design_cite` is null: no design sentence names this domain. It is a proposal for Joseph.

**Schema — the fields this domain, and only this domain, legitimises**

| field | type | example | reliability ceiling | why this field exists and why that ceiling |
|---|---|---|---|---|
| `school` | string | the institution advising takes place at | `validated` | A gazetteer school name at a word boundary. |
| `advisor` | string | the advisor | `direct` | Read from a labelled slot on an advising record, which §3.5 'such as a content hash, EXIF timestamp, a document title, or a labeled form field' makes direct. A role, never a dimension: §3.8 'It should avoid using authorship or creator identity as a destination dimension.'. |
| `advising_term` | string | the term being planned for | `validated` | §3.10 'Academic terms such as Spring 2025, AY 2024-25, and Michaelmas Term 2024 require dedicated patterns rather than generic parsing.'. Advising is forward-looking: the term named is usually the next one, not the current one, which is a real source of misfiling. |
| `plan_of_study` | string | the plan the record belongs to | `validated` | Proposal. A plan is revised repeatedly and its versions are the point; a plan term beside a school or programme name anchors it. |
| `advising_record_type` | string | the kind of advising document | `validated` | A record-type term beside an advising or registration term. |
| `registration_outcome` | enum | what actually happened at registration | `validated` | An outcome term ('registered', 'waitlisted', 'closed', 'hold', 'dropped', 'swapped') beside a term pattern. It is printed on a registration confirmation. |

**Recognition**

*Deterministic — each rule is a pattern **plus** a corroborating context:*

- an advising term ('advising', 'advisor meeting', 'plan of study', 'four-year plan', 'registration appointment') co-occurring with a gazetteer school name at a word boundary
- a registration term ('registration confirmation', 'waitlist', 'add/drop', 'course selection') co-occurring with an academic-term pattern
- a hold term co-occurring with a registration or advising term

*Needs the LLM — language interpretation a rule cannot do safely:*

- an email exchange that is advising without naming it
- distinguishing a plan the student drafted from one the advisor approved
- notes whose planned term is implicit

*Never alone — bare signals that must not establish this domain by themselves:*

- a list of course codes, which is equally a transcript, an audit or a plan
- the word 'plan'
- a school name — §4.9 'A university name alone should not create a group because Columbia can appear as an authoring school, course provider, target institution, employer, research venue, or merely a cited organization.'

**Work types** — advising note, plan of study, four-year plan, registration confirmation, add/drop form, waitlist notice, hold notice, course selection worksheet, advisor approval, override request

**Why files in this domain group together**

- one advising cycle for one upcoming term
- a plan of study across its revisions as a version family
- one advisor relationship across the terms it covered

**Template**

| dimension order | time first | why |
|---|---|---|
| school → advising_term → advising_record_type | no | Proposal. The term is the organising fact because advising is intrinsically per-registration-cycle, but the school still leads, per §5.5 'For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders.'. |

**Collides with** — where this domain and another will fight over the same file

| other domain | the confusion, and what separates them | design cite |
|---|---|---|
| `acad.undergraduate-program` | a plan of study and a degree audit contain the same requirement list; the audit is registrar-issued, the plan is a draft | — |
| `acad.course-enrollment` | a registration confirmation names courses that have not been taken yet, so its course facts must not become coursework facts | §4.9 'members carry irreconcilable course, institution, project, term, or purpose facts' |
| `acad.transfer-credit` | an override or substitution request is advising work and a credit decision at once | — |
| `acad.tuition-billing` | a registration hold is usually a billing hold and appears in both streams | — |

**Sensitivity** — `none`. Advising records concern the corpus holder. Notes discussing personal circumstances would be a different matter and are not assumed here.

---

### 35. Disability accommodations and access services

`acad.accommodations` · **proposal** · sensitivity: `potentially_sensitive`

> Requesting, documenting and implementing academic accommodations — a record built on medical evidence and shared with instructors.

**Design basis** — none. `design_cite` is null: no design sentence names this domain. It is a proposal for Joseph.

**Schema — the fields this domain, and only this domain, legitimises**

| field | type | example | reliability ceiling | why this field exists and why that ceiling |
|---|---|---|---|---|
| `institution` | string | the school granting the accommodation | `validated` | A gazetteer school name beside accommodations language. |
| `accommodation_type` | string | the accommodation granted or requested | `validated` | Proposal, and the field the domain turns on. An accommodation-type term beside an access-services term is checkable; the underlying condition is deliberately not a field here. |
| `approval_period` | string | the period the approval covers | `validated` | Proposal. Approvals are renewed per term or per year and lapse; the period is what distinguishes a current letter from a stale one. |
| `access_record_type` | string | the kind of accommodations document | `validated` | A record-type term beside an access-services or accommodation term. |
| `supporting_documentation` | enum | that a medical or psychological report supports the request | `user_confirmed` | Proposal, and deliberately a flag rather than a content field: the system records that supporting documentation exists, never what it says. §3.6 'A model that cannot cite sufficient evidence must return unknown.' |
| `implementing_course` | string | the course an accommodation letter was issued for | `validated` | §3.5 'BUSIB 4300 becomes a course fact only when the engine finds a course-code pattern together with academic context such as "syllabus," "lecture," "credits," "instructor," or "semester."'. Letters are issued per course and per term, which is why an accommodation record lands inside a coursework corpus. |

**Recognition**

*Deterministic — each rule is a pattern **plus** a corroborating context:*

- an accommodations term ('accommodation', 'access services', 'disability services', 'accommodation letter') co-occurring with a gazetteer school name at a word boundary
- an accommodation-type term ('extended time', 'note-taker', 'alternative format', 'reduced-distraction setting') co-occurring with an access-services term
- an accommodation-letter term co-occurring with a validated course code
- an approval-period term ('valid through', 'approved for', 'renewal due') co-occurring with an access-services term and an academic-term or date pattern

*Needs the LLM — language interpretation a rule cannot do safely:*

- correspondence that is an accommodation request without naming a type
- distinguishing a granted accommodation from a requested one
- a testing accommodation that belongs to an external testing body rather than the school

*Never alone — bare signals that must not establish this domain by themselves:*

- the word 'accommodation', which is also lodging vocabulary and would misfile travel records
- a school name — §4.9 'A university name alone should not create a group because Columbia can appear as an authoring school, course provider, target institution, employer, research venue, or merely a cited organization.'
- a medical report, which must not be assigned a purpose from its filename — §4.9 'the system should not infer a purpose from their filename alone'

**Work types** — accommodation request, accommodation letter, renewal request, intake appointment record, implementation plan, exam-proctoring arrangement, alternative-format request, appeal, instructor notification, supporting documentation cover sheet

**Why files in this domain group together**

- one approval period at one institution
- an accommodation letter with the courses it was issued for
- a request with the decision that answered it

**Template**

| dimension order | time first | why |
|---|---|---|
| institution → approval_period → access_record_type | no | Proposal. Deliberately no accommodation-type or condition level: a folder path is visible to anyone who sees the screen, and a path naming a disability discloses it. The period is the enumerable child because approvals lapse. |

**Collides with** — where this domain and another will fight over the same file

| other domain | the confusion, and what separates them | design cite |
|---|---|---|
| `med.medical-certification-letter` | supporting documentation is a medical or psychological report; the design names medical material a safety domain to be protected before placement | §3.15 'Finance, identity, medical, and legal material should be implemented first as safety domains' |
| `acad.course-enrollment` | an accommodation letter names a course and a term and will be claimed by the coursework template, which would place protected material in an open branch | §4.8 'an application packet does not silently absorb a document with a conflicting target institution' |
| `acad.standardized-testing` | testing accommodations are granted by the testing body, not the school, and travel with the sitting | — |
| `acad.integrity-case` | accommodation disputes and conduct processes generate similar correspondence with the same offices | — |

**Sensitivity** — `potentially_sensitive`. Proposal, not design. The record is built on medical documentation, which §7.3 'passport scans, medical documents, account statements, visas, legal forms, or credentials' names among protected material and §3.15 'Finance, identity, medical, and legal material should be implemented first as safety domains' puts behind protection. The phrase is the design's; no handling class is assigned here.

**Open question (unresolved — for Joseph)**

> Should an accommodations branch exist as a visible top-level folder at all? Any visible path discloses the fact of a disability to anyone who sees the screen. §5.9 'It should also support a scoped General or Other branch within a meaningful parent.' offers a scoped alternative, but whether to surface this area is Joseph's call and a user's, not the catalogue's.

---

### 36. Academic integrity and conduct cases

`acad.integrity-case` · **proposal** · sensitivity: `potentially_sensitive`

> An allegation and its process — notice, evidence, hearing and outcome — held by the accused, the reporter, or the panel.

**Design basis** — none. `design_cite` is null: no design sentence names this domain. It is a proposal for Joseph.

**Schema — the fields this domain, and only this domain, legitimises**

| field | type | example | reliability ceiling | why this field exists and why that ceiling |
|---|---|---|---|---|
| `institution` | string | the institution running the process | `validated` | A gazetteer school name beside conduct-process language. |
| `case_reference` | string | the case identifier the office issues | `validated` | Proposal. A case reference is the only unambiguous handle on a process whose documents otherwise share vocabulary with ordinary coursework, and a bare reference-shaped token is exactly what §3.10 'file names and documents frequently contain numbers that look like years but are course identifiers, version numbers, build numbers, ZIP codes, or other unrelated values' warns against reading alone. |
| `case_role` | enum | whether the holder is the respondent, the reporter, or a panel member | `user_confirmed` | Proposal, and the field that decides everything: the same file means opposite things in the three directions, and getting it wrong by inference would be a serious harm. Only the user establishes it. |
| `process_stage` | enum | the stage the document belongs to | `validated` | A stage term ('notice', 'meeting', 'hearing', 'finding', 'sanction', 'appeal') beside a case-process term. |
| `related_course` | string | the course the allegation concerns | `validated` | §3.5 'BUSIB 4300 becomes a course fact only when the engine finds a course-code pattern together with academic context such as "syllabus," "lecture," "credits," "instructor," or "semester."'. This is what pulls case material into a coursework branch, which is exactly what must not happen silently. |
| `outcome` | enum | the finding recorded | `user_confirmed` | Proposal. A finding must never be inferred from prose; §3.6 'A model that cannot cite sufficient evidence must return unknown.' applies with full force. |

**Recognition**

*Deterministic — each rule is a pattern **plus** a corroborating context:*

- a conduct-process term ('academic integrity', 'academic misconduct', 'honour code', 'student conduct', 'hearing panel') co-occurring with a gazetteer school name at a word boundary
- a case-reference pattern co-occurring with a conduct-process term
- a stage term ('notice of allegation', 'finding', 'sanction', 'appeal') co-occurring with a conduct-process term
- a validated course code co-occurring with a conduct-process term and a case-reference pattern — all three, because a course code beside the word 'integrity' is most often a syllabus policy paragraph

*Needs the LLM — language interpretation a rule cannot do safely:*

- correspondence about an allegation that never names the process
- a similarity report that may be routine plagiarism screening or case evidence
- distinguishing a policy document from a document about a specific case

*Never alone — bare signals that must not establish this domain by themselves:*

- the word 'integrity' or 'misconduct', which appear in policies, syllabi and training
- a similarity report, which most courses generate routinely
- a course code
- a filename suggesting a case — §4.9 'the system should not infer a purpose from their filename alone'

**Work types** — notice of allegation, policy extract, evidence bundle, similarity report, written response, meeting record, hearing record, finding letter, sanction notice, appeal, advisor correspondence, record-clearance confirmation

**Why files in this domain group together**

- one case from notice to outcome
- an evidence bundle as one submitted set
- an appeal with the decision it contests

**Template**

| dimension order | time first | why |
|---|---|---|
| institution → case_reference → process_stage | no | Proposal. Deliberately keyed on the case reference rather than on the course or the person: a path naming a course and 'misconduct' discloses the allegation to anyone who sees the screen. Stage is the leaf because a process is navigated chronologically. |

**Collides with** — where this domain and another will fight over the same file

| other domain | the confusion, and what separates them | design cite |
|---|---|---|
| `acad.course-enrollment` | case material names a course and a term and will be claimed by the coursework template, placing an allegation inside an open course folder | §4.8 'an application packet does not silently absorb a document with a conflicting target institution' |
| `legal.litigation-dispute` | a contested case involves counsel and legal correspondence; the design names legal material a safety domain protected before placement | §3.15 'Finance, identity, medical, and legal material should be implemented first as safety domains' |
| `acad.accommodations` | disputes and conduct processes generate similar correspondence with overlapping offices | — |
| `acad.course-instruction` | on the reporting side the file sits in the teaching corpus and is about a student, not about the holder | §3.8 'An application essay can mention the author's current school and the university to which the essay is addressed.' |

**Sensitivity** — `potentially_sensitive`. Proposal, not design. Case documents name and characterise individuals and adjoin the legal material §4.9 'Rare but sensitive files such as passports, visas, and legal documents may be surfaced as protected records' singles out. The phrase is the design's; no handling class is assigned here.

**Open question (unresolved — for Joseph)**

> Should case material ever be surfaced in a proposed tree, or only ever offered as a protected area the user opens deliberately? §5.9 'It should also support a scoped General or Other branch within a meaningful parent.' permits a scoped folder, but a visible branch discloses the allegation, and whether to surface it at all is Joseph's call.

---

### 37. Student organisations and clubs

`acad.student-organization` · **proposal** · sensitivity: `potentially_sensitive`

> Running or belonging to a campus organisation — officer records, events, budgets and recognition paperwork.

**Design basis** — none. `design_cite` is null: no design sentence names this domain. It is a proposal for Joseph.

**Schema — the fields this domain, and only this domain, legitimises**

| field | type | example | reliability ceiling | why this field exists and why that ceiling |
|---|---|---|---|---|
| `organisation` | string | the club or society | `validated` | Proposal, and the anchor: the organisation name is a proper noun that matches at a word boundary, which §3.7 'It should use word-boundary matching rather than substring matching.' requires. |
| `institution` | string | the school the organisation is recognised at | `validated` | A gazetteer school name beside a recognition or student-activities term. |
| `holder_role` | string | the office or membership the holder held | `validated` | Proposal. Officer material and member material are different corpora, and the role is what separates them. It is a role, never a dimension: §3.8 'It should avoid using authorship or creator identity as a destination dimension.'. |
| `activity_year` | string | the year of activity | `validated` | Proposal. Organisations turn over annually and their records are archived per year of leadership. |
| `organisation_record_type` | string | the kind of organisation document | `validated` | A record-type term beside an organisation name. |
| `event` | string | a specific event the organisation ran | `validated` | An event name beside an organisation name. Events are the unit most of the material actually belongs to. |

**Recognition**

*Deterministic — each rule is a pattern **plus** a corroborating context:*

- an organisation name co-occurring with a student-activities term ('student organisation', 'club', 'chapter', 'constitution', 'officer transition')
- a recognition term ('registered organisation', 'club recognition', 'student activities') co-occurring with a gazetteer school name
- an officer term ('president', 'treasurer', 'officer transition') co-occurring with a named organisation
- an event name co-occurring with a named organisation and a planning or budget term
- an activity-year pattern co-occurring with a named organisation and an officer or membership term

*Needs the LLM — language interpretation a rule cannot do safely:*

- meeting notes that name no organisation
- distinguishing club material from coursework for a project team
- a flyer that is an organisation event only by context

*Never alone — bare signals that must not establish this domain by themselves:*

- an organisation name that is also a common phrase
- the word 'meeting'
- a school name — §4.9 'A university name alone should not create a group because Columbia can appear as an authoring school, course provider, target institution, employer, research venue, or merely a cited organization.'

**Work types** — constitution, recognition paperwork, officer transition document, meeting minutes, membership roster, budget request, event plan, event flyer, sponsorship agreement, post-event report, room booking, training record

**Why files in this domain group together**

- one organisation in one activity year
- one event with its plan, promotion and report
- an officer handover as one transferred set

**Template**

| dimension order | time first | why |
|---|---|---|
| organisation → activity_year → organisation_record_type | no | Proposal. The organisation leads and the activity year sits beneath it because leadership turns over annually and each year's records are handed on as a set — a period that is an organisational boundary, not a calendar. |

**Collides with** — where this domain and another will fight over the same file

| other domain | the confusion, and what separates them | design cite |
|---|---|---|
| `acad.campus-employment` | a paid organisation role produces employment records alongside the club ones | — |
| `acad.course-enrollment` | a project team for a course looks like a club and is scoped to a term and a course code | §3.5 'BUSIB 4300 becomes a course fact only when the engine finds a course-code pattern together with academic context such as "syllabus," "lecture," "credits," "instructor," or "semester."' |
| `fin.financial-records` | budgets, sponsorships and reimbursements are financial records the design protects before placement | §3.15 'Finance, identity, medical, and legal material should be implemented first as safety domains' |
| `pers.photo-event` | event photographs carry capture metadata and will be claimed by the media template | §5.4 'a Photos template may define year → event' |

**Sensitivity** — `potentially_sensitive`. Proposal, not design. Membership rosters and contact lists are address-book material, which §2.9 'should normally be privacy-protected rather than used to create folder proposals' says should be privacy-protected rather than used to create folder proposals. The phrase is the design's; no handling class is assigned here.

---

### 38. Accreditation and institutional assessment

`acad.accreditation-institutional` · **proposal** · sensitivity: `potentially_sensitive`

> The institution's own record of being reviewed — self-studies, evidence inventories, site visits and findings.

**Design basis** — none. `design_cite` is null: no design sentence names this domain. It is a proposal for Joseph.

**Schema — the fields this domain, and only this domain, legitimises**

| field | type | example | reliability ceiling | why this field exists and why that ceiling |
|---|---|---|---|---|
| `institution` | string | the institution under review | `validated` | A gazetteer institution name beside accreditation language. |
| `accreditor` | string | the accrediting or reviewing body | `validated` | Proposal. The accreditor is a distinct party whose correspondence and standards are separate from the institution's response; conflating them loses who is asserting what. |
| `review_cycle` | string | the review the material belongs to | `validated` | Proposal. Cycles run over years and overlap; the cycle is the only thing that keeps two self-studies apart. |
| `standard` | string | the standard or criterion the evidence addresses | `validated` | Proposal, and the field that makes this domain distinct: the entire corpus is organised as evidence mapped to numbered standards, and a bare standard number is exactly the token §3.10 'file names and documents frequently contain numbers that look like years but are course identifiers, version numbers, build numbers, ZIP codes, or other unrelated values' warns against. |
| `unit_under_review` | string | the programme, department or school being reviewed | `validated` | A unit name beside a review or accreditation term. Programmatic and institutional accreditation are different scopes and produce different corpora. |
| `accreditation_record_type` | string | the kind of accreditation document | `validated` | A record-type term beside an accreditor name or a review term. |

**Recognition**

*Deterministic — each rule is a pattern **plus** a corroborating context:*

- an accreditation term ('accreditation', 'self-study', 'site visit', 'standards', 'reaffirmation') co-occurring with an accreditor name or a gazetteer institution name
- an accreditor name co-occurring with a standard or criterion pattern
- an assessment term ('assessment plan', 'evidence inventory', 'outcomes report') co-occurring with a named unit and a review cycle

*Needs the LLM — language interpretation a rule cannot do safely:*

- an evidence document that is ordinary institutional material until it is mapped to a standard
- distinguishing programmatic from institutional accreditation
- a report whose review cycle is implicit

*Never alone — bare signals that must not establish this domain by themselves:*

- a standard or criterion number
- the word 'assessment', which is also coursework vocabulary
- an institution name — §4.9 'A university name alone should not create a group because Columbia can appear as an authoring school, course provider, target institution, employer, research venue, or merely a cited organization.'

**Work types** — self-study, evidence inventory, standard narrative, assessment plan, outcomes report, site-visit schedule, site-visit report, findings letter, response to findings, monitoring report, substantive change request

**Why files in this domain group together**

- one review cycle for one unit
- one standard with the evidence mapped to it
- a self-study across its drafts as a version family

**Template**

| dimension order | time first | why |
|---|---|---|
| accreditor → review_cycle → standard | no | Proposal. The accreditor and cycle bound the work; the standard is the leaf because the corpus is genuinely indexed by standard, which satisfies §5.5 'a parent dimension should provide the context required to understand the child' — a standard number means nothing without its accreditor. |

**Collides with** — where this domain and another will fight over the same file

| other domain | the confusion, and what separates them | design cite |
|---|---|---|
| `acad.curriculum-development` | outcomes mapping serves both; accreditation carries an accreditor and a review cycle, curriculum work does not | — |
| `acad.course-instruction` | syllabi and assessment artifacts are pulled in as evidence and belong to both the course and the standard | §3.1 'A file can simultaneously be a syllabus, part of a particular course, created for a particular semester, related to a university, included in an application package, a member of a version family, and potentially sensitive.' |
| `acad.professional-school` | programmatic accreditation for a licensure-track programme overlaps the programme's own records | — |
| `acad.alumni-record` | outcomes and placement data about graduates are accreditation evidence and alumni records at once | — |

**Sensitivity** — `potentially_sensitive`. Proposal, not design. Evidence inventories routinely include student work and identifiable outcomes data — third-party content of the kind §2.9 'treating addresses and message content as potentially sensitive' applies the phrase to. No handling class is assigned here.

**Open question (unresolved — for Joseph)**

> This is an institution-side domain in a product whose worked examples are all personal corpora. Should institution-side domains be in the launch catalogue at all, or deferred? §3.15 'Other domains remain placeholders until user demand and corpus evidence justify detailed templates.' provides the deferral route.

---

### 39. Alumni relations and post-graduation records

`acad.alumni-record` · **proposal** · sensitivity: `none`

> The relationship with a school after leaving it — verification, giving, reunions and continued access.

**Design basis** — none. `design_cite` is null: no design sentence names this domain. It is a proposal for Joseph.

**Schema — the fields this domain, and only this domain, legitimises**

| field | type | example | reliability ceiling | why this field exists and why that ceiling |
|---|---|---|---|---|
| `institution` | string | the school the holder graduated from | `validated` | A gazetteer school name beside alumni language. |
| `graduation_year` | string | the class year | `validated` | Proposal. The class year is the primary alumni identifier and appears beside the school in almost every alumni communication; alone it is only a year, which §3.10 'file names and documents frequently contain numbers that look like years but are course identifiers, version numbers, build numbers, ZIP codes, or other unrelated values' forbids relying on. |
| `alumni_record_type` | string | the kind of alumni document | `validated` | A record-type term beside an alumni or institution term. |
| `engagement` | string | the reunion, chapter or programme engaged with | `validated` | An engagement name beside an alumni term. Reunions and regional chapters are the concrete events the material belongs to. |
| `giving_designation` | string | the fund or purpose a gift was directed to | `validated` | Proposal. Gift records carry a designation that determines the receipting and the acknowledgement chain. |

**Recognition**

*Deterministic — each rule is a pattern **plus** a corroborating context:*

- an alumni term ('alumni', 'alumnae', 'class of', 'reunion', 'alumni association') co-occurring with a gazetteer school name at a word boundary
- a class-year pattern co-occurring with an alumni term and a school name
- a giving term ('gift receipt', 'pledge', 'annual fund', 'donor acknowledgement') co-occurring with a school name

*Needs the LLM — language interpretation a rule cannot do safely:*

- correspondence from a school that may be alumni relations or ordinary administration
- distinguishing a reunion invitation from a general event announcement
- a verification letter whose purpose is stated only in prose

*Never alone — bare signals that must not establish this domain by themselves:*

- a school name — §4.9 'A university name alone should not create a group because Columbia can appear as an authoring school, course provider, target institution, employer, research venue, or merely a cited organization.'
- a four-digit year — §3.10 'file names and documents frequently contain numbers that look like years but are course identifiers, version numbers, build numbers, ZIP codes, or other unrelated values'
- a solicitation email, which is bulk mail

**Work types** — diploma, degree verification, alumni card, transcript request as alumnus, reunion registration, gift receipt, pledge record, donor acknowledgement, alumni directory entry, mentoring programme record, email-forwarding notice, class note

**Why files in this domain group together**

- one institution across the whole post-graduation relationship
- one reunion with its registration and travel
- a giving history across its receipts

**Template**

| dimension order | time first | why |
|---|---|---|
| institution → alumni_record_type → engagement | no | Proposal. No year level: alumni material accumulates thinly over decades and a year split would produce exactly the many-tiny-folders outcome the design warns designers about. |

**Collides with** — where this domain and another will fight over the same file

| other domain | the confusion, and what separates them | design cite |
|---|---|---|
| `acad.transcript-record` | an alumnus requesting a transcript produces a registrar record; the alumni reading adds nothing the transcript domain does not already carry | — |
| `acad.credential-certificate` | a diploma is both proof of the award and the founding alumni document | — |
| `fin.financial-records` | gift receipts are financial and tax-relevant records the design protects before placement | §3.15 'Finance, identity, medical, and legal material should be implemented first as safety domains' |
| `career.networking-and-referrals` | alumni mentoring and networking material is career material with a school attached | §5.4 'a Career template may define company → role or recruiting cycle → document type' |

**Sensitivity** — `none`. Alumni correspondence concerns the corpus holder. Gift receipts carry payment detail and reach protection through the financial collision, not through a class assigned here.

---

### 40. Diplomas, certificates and verifiable credentials

`acad.credential-certificate` · **inference** · sensitivity: `potentially_sensitive`

> The awarded credential itself — the artifact a person shows to prove a qualification, as distinct from the record of earning it.

**Design basis** — The design names the artifact as a packet member — §3.9 'A university application packet can contain an identification document, transcript, resume, certificate, and academic abstract.' lists a certificate — and §7.3 'standalone certificates, notices, confirmations, forms, and PDFs that have a durable purpose but no broader group' describes standalone certificates as residual material. It names no credential domain.

**Schema — the fields this domain, and only this domain, legitimises**

| field | type | example | reliability ceiling | why this field exists and why that ceiling |
|---|---|---|---|---|
| `awarding_body` | string | the institution or body that granted it | `validated` | Inference. A gazetteer institution or body name beside award language; the awarding body is what makes a credential mean anything. |
| `credential` | string | the qualification awarded | `validated` | A degree, certificate or licence name beside an awarding-body name at a word boundary. |
| `award_date` | date | the date of conferral | `validated` | Narrow date extraction only: §3.10 'file names and documents frequently contain numbers that look like years but are course identifiers, version numbers, build numbers, ZIP codes, or other unrelated values'. |
| `verification_handle` | string | the credential identifier or verification reference printed on it | `direct` | Read from a labelled slot on the artifact, which §3.5 'such as a content hash, EXIF timestamp, a document title, or a labeled form field' makes direct. It is what separates a credential from a decorative certificate. |
| `credential_status` | enum | current, expired, or superseded | `validated` | Inference. An expiry or renewal term beside a credential name. Whether a credential is still current is the question people actually have. |
| `credential_form` | enum | the physical or digital form the artifact takes | `validated` | Inference. A scan, a PDF and a digital badge are the same credential in three forms, which is a version family, not three credentials. |

**Recognition**

*Deterministic — each rule is a pattern **plus** a corroborating context:*

- an award term ('has been awarded', 'confer', 'certificate of completion', 'diploma', 'licence') co-occurring with a gazetteer institution or body name at a word boundary
- a verification-reference pattern co-occurring with an awarding-body name
- an expiry or renewal term co-occurring with a credential name
- a digital-badge term co-occurring with an issuing-body name

*Needs the LLM — language interpretation a rule cannot do safely:*

- a scanned certificate whose awarding body is a logo rather than text
- distinguishing a real credential from a participation or novelty certificate
- a foreign-language diploma whose credential name must be read

*Never alone — bare signals that must not establish this domain by themselves:*

- the word 'certificate', which spans this domain, continuing education, and residual records
- an institution name — §4.9 'A university name alone should not create a group because Columbia can appear as an authoring school, course provider, target institution, employer, research venue, or merely a cited organization.'
- a decorative PDF
- a filename claiming a credential — §4.9 'the system should not infer a purpose from their filename alone'

**Work types** — diploma, degree certificate, certificate of completion, professional licence, digital badge, verification letter, renewal certificate, apostille or attestation, replacement request, credential evaluation

**Why files in this domain group together**

- one credential across its scan, PDF and digital badge as a version family
- one awarding body across the credentials it granted
- a credential with its renewals over time

**Template**

| dimension order | time first | why |
|---|---|---|
| awarding_body → credential → credential_form | no | Inference. Awarding body then credential satisfies §5.5 'a parent dimension should provide the context required to understand the child': a certificate name is uninterpretable without knowing who issued it. No date level, because a person holds few credentials and a date split would leave one-child folders. |

**Collides with** — where this domain and another will fight over the same file

| other domain | the confusion, and what separates them | design cite |
|---|---|---|
| `acad.transcript-record` | a diploma and a transcript are both proof of study; the diploma asserts the award, the transcript asserts the record | — |
| `acad.continuing-education` | a completion certificate is an input to maintaining a credential and is not itself the credential | — |
| `acad.college-application` | a certificate is a named member of the design's own application packet and must not be moved out of one silently | §3.9 'A university application packet can contain an identification document, transcript, resume, certificate, and academic abstract.' |
| `pers.identity-document` | a licence with a photograph and an identifier adjoins the identity material the design protects first | §3.15 'Finance, identity, medical, and legal material should be implemented first as safety domains' |
| `residual.independent-records` | the design's residual library already holds §7.3 'standalone certificates, notices, confirmations, forms, and PDFs that have a durable purpose but no broader group', which would absorb an unrecognised certificate | §7.3 'standalone certificates, notices, confirmations, forms, and PDFs that have a durable purpose but no broader group' |

**Sensitivity** — `potentially_sensitive`. §7.3 'passport scans, medical documents, account statements, visas, legal forms, or credentials' names credentials explicitly among protected material. The phrase is the design's; no handling class is assigned here.

---

## Open questions — all 20, for `NEEDS-JOSEPH.md`

None of these is resolved here. Each is either a default folder shape for someone's real life, or a place where two design sentences both apply and the design does not say which wins.

**`acad.course-enrollment` — Course enrollment and coursework**

> When a file has a validated course and work type but no school evidence, should the tree still open a school level for it, or should it land in a scoped General under the course? §5.9 'It should also support a scoped General or Other branch within a meaningful parent.' permits the second; the design never says which is the default for Academics.

**`acad.course-instruction` — Teaching a course**

> Should a teaching branch nest term under course (a teacher's stable-course view) or course under term (the Academic template's order)? The design gives one Academic template and does not say whether the teaching side reuses it.

**`acad.k12-schooling` — K-12 schooling records**

> Should a family corpus branch by child first, and if so, is a child's name an acceptable folder level at all? §3.8 'It should avoid using authorship or creator identity as a destination dimension.' bars authorship as a collector but says nothing about a subject person, and this is a real-life structure decision, not a technical one.

**`acad.graduate-program` — Graduate programme milestones**

> Does a graduate corpus want one branch per degree with research nested inside it, or two sibling top-level areas — Academics and Research — that a single advisor's material is split across? §5.1 'Academics, Applications, Research, Career, Personal Records, Finance and Administration, Photos and Captures, Code and Projects, and Media or Miscellaneous Personal Material' lists both as separate candidate areas and does not say how a doctoral student should resolve the overlap.

**`acad.continuing-education` — Continuing education and professional development**

> Should continuing education sit under Academics at all, or under a career or personal-administration area? §5.1 'Academics, Applications, Research, Career, Personal Records, Finance and Administration, Photos and Captures, Code and Projects, and Media or Miscellaneous Personal Material' offers several plausible parents and the answer depends on how the person thinks about their licence, not on the files.

**`acad.self-study` — Self-directed study**

> Self-study has no institution and often no clear boundary against saved reading. Should it be an Academics branch, or should unanchored study material fall to a residual area? §7.3 'papers, articles, reports, and saved PDFs that appear to be reading material but have no active research, course, or project association' already describes an overlapping residual template.

**`acad.teaching-assistantship` — Teaching assistantship**

> Does a teaching assistantship belong under Academics with the holder's own coursework, under a Career area as employment, or split between them? The design's candidate areas (§5.1 'Academics, Applications, Research, Career, Personal Records, Finance and Administration, Photos and Captures, Code and Projects, and Media or Miscellaneous Personal Material') make all three available and the files support all three.

**`acad.tutoring` — Tutoring engagements**

> May a tutee's name be a folder level? §3.8 'It should avoid using authorship or creator identity as a destination dimension.' forbids the author as a collector but is silent on the subject person, and this decides whether real names appear in a visible path.

**`acad.college-application` — College application packet**

> When an existing folder such as §5.6 'Chinese University Application Materials' already holds the packet, should the proposed institution branch appear alongside it, replace it, or be suppressed? §5.6 'The system can present that packet as a preserved or proposed branch alongside institution-based organization.' permits the first, §5.10 'Existing folders must not be automatically flattened, renamed, or reorganized simply because a template would produce a different structure.' forbids the second, and the design leaves the default unstated.

**`acad.grad-school-application` — Graduate and professional school application**

> Should applications to different programmes at the same university nest under one institution branch, or stand as siblings? The design's template names only the institution level (§5.4 'an Applications template may define target institution → application cycle → document type') and a doctoral applicant may apply to several programmes at one school.

**`acad.recommendation-letter` — Letters and forms of recommendation**

> On the writing side, should letters be collected under the person they are about, or under the target they were sent to? §3.8 'It should avoid using authorship or creator identity as a destination dimension.' bars the writer as a collector but says nothing about the subject, and a recommender's corpus is naturally organised per student.

**`acad.transcript-record` — Transcripts and official academic records**

> Does a transcript live under an academic-records branch and appear inside an application packet by reference, or is it copied into the packet? §3.1 'A file can simultaneously be a syllabus, part of a particular course, created for a particular semester, related to a university, included in an application package, a member of a version family, and potentially sensitive.' says a file holds several facts at once, but the tree has to put the bytes somewhere.

**`acad.financial-aid` — Financial aid and student loans**

> Should financial aid sit under Academics, beside the school it belongs to, or under the Finance area the design protects separately? §5.1 'Academics, Applications, Research, Career, Personal Records, Finance and Administration, Photos and Captures, Code and Projects, and Media or Miscellaneous Personal Material' lists both, and putting it under Academics may place protected material inside an unprotected branch.

**`acad.thesis-dissertation` — Thesis or dissertation**

> Should a thesis live under Academics as the capstone of a degree, or under Research beside the project it came out of? §5.1 'Academics, Applications, Research, Career, Personal Records, Finance and Administration, Photos and Captures, Code and Projects, and Media or Miscellaneous Personal Material' offers both as top-level candidates and a doctoral corpus supports either.

**`acad.conference-travel-student` — Student conference travel and presentation**

> Does a conference trip belong under Academics or Research beside the work presented, or under Travel beside the trip? §5.1 'Academics, Applications, Research, Career, Personal Records, Finance and Administration, Photos and Captures, Code and Projects, and Media or Miscellaneous Personal Material' lists these as separate top-level candidates and the same set of files supports each.

**`acad.clinical-rotation` — Clinical rotation and supervised practicum**

> Rotation material can contain de-identified patient detail that no rule will reliably spot. Should an entire clinical branch be treated as protected by default rather than per file? §3.15 'the system detects and protects them before any cloud or automated placement decision is allowed' requires protection before placement but does not say whether a whole branch may be marked.

**`acad.arts-jury-portfolio` — Music and arts juries, recitals and portfolio review**

> Arts material is media-heavy, and the design puts time first for capture-based media (§5.4 'a Photos template may define year → event') but subject first for document domains (§5.5 'For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders.'). A jury corpus is both. Which rule wins?

**`acad.accommodations` — Disability accommodations and access services**

> Should an accommodations branch exist as a visible top-level folder at all? Any visible path discloses the fact of a disability to anyone who sees the screen. §5.9 'It should also support a scoped General or Other branch within a meaningful parent.' offers a scoped alternative, but whether to surface this area is Joseph's call and a user's, not the catalogue's.

**`acad.integrity-case` — Academic integrity and conduct cases**

> Should case material ever be surfaced in a proposed tree, or only ever offered as a protected area the user opens deliberately? §5.9 'It should also support a scoped General or Other branch within a meaningful parent.' permits a scoped folder, but a visible branch discloses the allegation, and whether to surface it at all is Joseph's call.

**`acad.accreditation-institutional` — Accreditation and institutional assessment**

> This is an institution-side domain in a product whose worked examples are all personal corpora. Should institution-side domains be in the launch catalogue at all, or deferred? §3.15 'Other domains remain placeholders until user demand and corpus evidence justify detailed templates.' provides the deferral route.

