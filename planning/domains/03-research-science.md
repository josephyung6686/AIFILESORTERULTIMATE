# 03 — Research and science domain schemas

- **supercategory**: `research-science`
- **authored**: 2026-08-21
- **entries**: 40
- **owner**: P6 (fact-schema half) and P10 (folder-template half), per P6 SPEC §3.15 split ownership
- **consumer**: The §3.6 validator's allow-list — “each fact or label belongs to an allowed domain schema” — and the §5.3 menu the vertical pass draws branch proposals from: “proposes one or more domain templates based on the groups and facts that already belong inside it”.
- **source of truth**: planning/00-database-agent-product-design.md. Every quotation in this file was located verbatim in that document before being written. The 00 document is unsectioned running prose; the `§` labels are the section numbering of 01-product-design-structured.md, which sections the same text.

## What this file is

A domain here is **a schema (which fact fields are legal) plus a template (how its branch is shaped)**. The schema half is the allow-list the §3.6 validator enforces; the template half is the menu §5.3's vertical pass draws from. Forty entries, each a genuinely different schema — not forty names for one Research folder.

## Design basis

- §3.11: “Research files may use project, stage, artifact type, lab, and venue.”
- §5.4: “a Research template may define project → stage → artifact type”
- §3.3: “The LLM may determine whether an extracted document appears to be an application essay, research artifact, recruiting document, travel record, or other supported domain”
- §3.5: “interpret an unusual research artifact”
- §4.2: “For a research group, it might be a manuscript, abstract, or protocol with a known project identifier.”
- §4.5: “a research group PVA/RDP — Manuscripts and Figures”
- §4.9: “a PVA/RDP abstract that is both a Research artifact and a supporting document in a UChicago application packet”
- §5.1: “Research supported by PVA/RDP and manuscript groups”
- §3.15: “academic coursework, college applications, research and lab work, career and recruiting, photos and captures, and code projects”
- §5.7: “research workflows”

## Rules this file obeys

1. **Provenance is honest.**
   - `design` — A sentence in the design names this domain, or names its artifact class as a research artifact.
   - `inference` — A subdivision of the design's named Research domain, reached by narrowing an artifact class or a stage the design names.
   - `proposal` — A domain the design names nowhere. It exists because real research corpora contain it.
   - Provenance describes the DOMAIN, not its fields. Every field's own `why` opens with its field-level provenance: **§3.11 literal** means the field name is quoted from “Research files may use project, stage, artifact type, lab, and venue.” (or, where said so, from another §3.11 row); **Added field** means it is beyond §3.11's Research row and is authored in this catalogue, not quoted from the design.
2. **No quotation is fabricated.** Every span inside quote marks was located verbatim in `00-database-agent-product-design.md` before being written. Three cites are deliberate paraphrases and carry no quote marks. A machine check re-verifies all of them against the source on every rebuild.
3. **No numbers.** No threshold, window, count or confidence score appears anywhere in this file. §3.7's minimum score and minimum margin, §3.9's session boundary and §4.2's neighbourhood size are all deferred and injected.
4. **No handling classes.** `sensitivity` carries §2.9's phrase `potentially sensitive` and nothing more. Handling classes are P7's (§8.4) and are never assigned here. Human-subjects, clinical and specimen material makes a handling class tempting; every such entry marks and stops.
5. **Universal fields are not repeated.** §3.11's universal set — file type, creation date, language, duplicate family, version family, sensitivity status — applies to every file and is NOT repeated in any entry's `schema`. Only domain-activated fields are listed.
6. **Reliability ceilings.** §3.13's states, and the ceiling means the highest state a PRODUCER may write; `user_confirmed` is always reachable by a user gesture and is never listed. `direct` = a labelled metadata slot or labelled form field (§3.13's own definition). `validated` = a deterministic pattern plus a context check, and every `validated` field has a matching rule in its entry's `recognition.deterministic`. `llm_supported` = reachable only by language interpretation. `possible` = a clue that may never become a fact on its own.
7. **Recognition follows §3.5.** Every `deterministic` row follows §3.5's model — a pattern together with corroborating context, never a bare pattern: “BUSIB 4300 becomes a course fact only when the engine finds a course-code pattern together with academic context”. This file authors the research half of P6 SPEC's deferred row 'Rule context-term lists beyond the five literal academic terms'.
8. **Identifier patterns are not re-derived.** DOI, arXiv, PMID, PMCID, ORCID, ISBN, ISSN, ROR, RRID, handle and in-text citation patterns are NOT re-derived here. They are authored in planning/deferred-catalogues/06-citation-identifier-patterns.json and are cited by entry id (`cid-doi`, `cid-arxiv-new`, `cid-pmid`, `cid-handle`, `cid-email`, `cid-citation-authoryear`, …). This file authors the domain schemas that consume those identifiers, and states the corroborating context each one needs before it may become a fact.

## Entries at a glance

| # | id | name | provenance | sensitivity | template order | time first |
|---|---|---|---|---|---|---|
| 1 | `res.research-project` | Research project work (the §3.11 Research schema itself) | design | none | project → stage → artifact type | no |
| 2 | `res.manuscript-preparation` | Manuscript preparation and its version family | design | none | project → manuscript → stage | no |
| 3 | `res.manuscript-submission` | Journal submission packets and editorial correspondence | inference | none | project → manuscript → submission stage | no |
| 4 | `res.peer-review-author` | Peer review received, and the revision it drives | inference | **potentially sensitive** | project → manuscript → review round | no |
| 5 | `res.peer-review-referee` | Reviewing and editorial work done for others | proposal | **potentially sensitive** | venue → review role → assignment | no |
| 6 | `res.preprint` | Preprints and preprint versions | inference | none | project → manuscript → stage | no |
| 7 | `res.published-article` | Published articles, reprints and author copies | inference | none | project → manuscript → artifact type | no |
| 8 | `res.figure-and-source` | Figures and figure source files | design | none | project → manuscript → figure | no |
| 9 | `res.dataset` | Research datasets | inference | **potentially sensitive** | project → study → data level | no |
| 10 | `res.data-dictionary` | Data dictionaries and codebooks | proposal | none | project → study → dataset version | no |
| 11 | `res.analysis-code` | Analysis code and scripts | inference | none | project → analysis step → artifact type | no |
| 12 | `res.computational-notebook` | Computational notebooks | inference | none | project → analysis step → artifact type | no |
| 13 | `res.statistical-output` | Statistical output and results tables | proposal | none | project → analysis step → output type | no |
| 14 | `res.lab-notebook` | Lab notebooks and experiment records | inference | none | project → experiment → entry date | no |
| 15 | `res.protocol-sop` | Experimental protocols and standard operating procedures | design | none | lab → protocol → version | no |
| 16 | `res.instrument-output` | Instrument runs and raw acquisition output | proposal | **potentially sensitive** | instrument → acquisition date → run | yes |
| 17 | `res.sample-specimen` | Sample, specimen and reagent records | proposal | **potentially sensitive** | project → study → record type | no |
| 18 | `res.grant-proposal` | Grant proposals and funding applications | proposal | **potentially sensitive** | funder → programme → period | no |
| 19 | `res.grant-reporting` | Grant reporting and post-award compliance | proposal | **potentially sensitive** | funder → award → reporting period | no |
| 20 | `res.irb-ethics` | Ethics, IRB and IACUC approvals | proposal | **potentially sensitive** | study → review body → protocol | no |
| 21 | `res.human-subjects-consent` | Consent and participant-facing materials | proposal | **potentially sensitive** | study → consent version → consent type | no |
| 22 | `res.clinical-trial` | Clinical trial documentation | proposal | **potentially sensitive** | sponsor → trial → document type | no |
| 23 | `res.research-agreement` | Collaboration agreements, MTAs and data-use agreements | proposal | **potentially sensitive** | counterparty → agreement type → agreement | no |
| 24 | `res.conference-abstract` | Conference and meeting abstracts | inference | none | project → venue → artifact type | no |
| 25 | `res.poster` | Conference posters | inference | none | project → venue → artifact type | no |
| 26 | `res.talk` | Talks, seminars and presentation decks | inference | none | project → venue → artifact type | no |
| 27 | `res.reading-library` | Literature and reading library | proposal | none | reading topic → venue → artifact type | no |
| 28 | `res.reference-library` | Reference-manager libraries and bibliographies | proposal | none | reading topic → library → artifact type | no |
| 29 | `res.systematic-review` | Systematic reviews and evidence screening | proposal | none | review → screening stage → artifact type | no |
| 30 | `res.thesis-supervision` | Thesis and dissertation supervision | proposal | **potentially sensitive** | student → milestone → artifact type | no |
| 31 | `res.patent-disclosure` | Invention disclosures and patents | proposal | **potentially sensitive** | docket → jurisdiction → status | no |
| 32 | `res.software-release` | Research software releases | inference | none | project → release version → artifact type | no |
| 33 | `res.reproducibility-package` | Reproducibility and replication packages | proposal | none | project → manuscript → artifact type | no |
| 34 | `res.data-management-plan` | Data management plans | proposal | none | funder → award → plan version | no |
| 35 | `res.repository-deposit` | Repository and archive deposits | proposal | none | project → artifact type → repository | no |
| 36 | `res.facility-booking` | Core-facility and equipment bookings | proposal | none | facility → instrument → session | no |
| 37 | `res.field-work` | Field work records | proposal | **potentially sensitive** | site → campaign → record type | no |
| 38 | `res.survey-instrument` | Survey instruments and fielding records | proposal | **potentially sensitive** | study → instrument → wave | no |
| 39 | `res.qualitative-coding` | Qualitative coding and interview analysis | proposal | **potentially sensitive** | study → transcript stage → artifact type | no |
| 40 | `res.correction-retraction` | Corrections, retractions and the post-publication record | proposal | none | project → manuscript → artifact type | no |

Counts by provenance: **design** 4, **inference** 12, **proposal** 24. Marked `potentially sensitive`: **16**. Open questions: **17**.

---

## Entries

### 1. `res.research-project` — Research project work (the §3.11 Research schema itself)

> Work that belongs to a named research project but that no more specific research domain below claims.

**provenance**: `design` — §3.11: “Research files may use project, stage, artifact type, lab, and venue.” §5.4: “a Research template may define project → stage → artifact type” §3.3: “The LLM may determine whether an extracted document appears to be an application essay, research artifact, recruiting document, travel record, or other supported domain”

**Schema** — the fields this domain, and only this domain, legitimises.

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `project` | string | `PVA/RDP` | `validated` | **§3.11 literal.** The organising identifier of the whole supercategory. §4.2: “For a research group, it might be a manuscript, abstract, or protocol with a known project identifier.” makes a known project identifier the seed of a research group. |
| `stage` | string | `in preparation` | `validated` | **§3.11 literal.** Where the work sits in its own lifecycle. §5.4 puts it second in the Research template, so it is a dimension, not only metadata. |
| `artifact type` | string | `manuscript` | `validated` | **§3.11 literal.** What kind of research object the file is. Every sub-domain below is, formally, one authored value of this field plus the extra fields that value legitimises. |
| `lab` | string | `Chen Lab` | `validated` | **§3.11 literal.** §3.15 names “research and lab work” as one launch domain; `lab` is the group the work was done in, not its author (§3.8). |
| `venue` | string | `Nature Communications` | `validated` | **§3.11 literal.** §4.9 names 'research venue' as one of the roles a single institution name can play, which is exactly why venue is its own field and not a generic organisation. |

**Recognition**

| | |
|---|---|
| deterministic (pattern **plus** corroborating context) | • a project identifier token co-occurring with research context such as 'aim', 'hypothesis', 'methods', 'results', 'principal investigator', or 'supplementary' — the same shape as §3.5: ''BUSIB 4300 becomes a course fact only when the engine finds a course-code pattern together with academic context such as “syllabus,” “lecture,” “credits,” “instructor,” or “semester.”''<br>• an existing user-created folder whose name is the project identifier and whose members carry at least two different research artifact types (§3.9: “Purpose may be supported strongly by an existing user-created folder name or explicit language in a form or portal.”)<br>• a lab name from a validated gazetteer (§3.7, deferred) co-occurring with an affiliation or acknowledgement line<br>• a stage token ('in preparation', 'submitted', 'under review', 'in press', 'published') co-occurring with a project identifier<br>• `venue` is §3.11's inherited Research field: a venue name from a validated gazetteer (§3.7, deferred) co-occurring with a research artifact type this entry already recognises. §4.9 is why a bare organisation name never suffices |
| needs the LLM | • a file whose only project signal is prose that reads as project work without naming the project<br>• deciding which of several projects a shared methods document belongs to |
| never alone | • a bare project acronym — §3.7's word-boundary rule exists because short acronyms hide inside ordinary words<br>• a bare lab or principal-investigator surname<br>• a bare institution name (§4.9: “A university name alone should not create a group because Columbia can appear as an authoring school, course provider, target institution, employer, research venue, or merely a cited organization.”)<br>• a bare four-digit number (§3.10: “The product must not use fuzzy date parsing because file names and documents frequently contain numbers that look like years but are course identifiers, version numbers, build numbers, ZIP codes, or other unrelated values.”) |

**Work types**: `manuscript`, `abstract`, `protocol`, `figure`, `dataset`, `analysis script`, `slide deck`, `project notes`, `meeting minutes`

**Grouping reasons**: one project across its artifact types; one lab across one project; one project stage across its outputs

**Template**: `project → stage → artifact type`

> §5.4: “a Research template may define project → stage → artifact type” — copied literally, not designed here. §5.5: “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders. Photos and capture-based media are the major exception: time often belongs first because capture date is a defining aspect of the material.”

**Collides with**

| domain | discriminating signal | design cite |
|---|---|---|
| `acad.course-enrollment` | both can carry an institution and a term; only coursework carries a course code with academic context, and only research carries a project identifier | §3.5: ''BUSIB 4300 becomes a course fact only when the engine finds a course-code pattern together with academic context such as “syllabus,” “lecture,” “credits,” “instructor,” or “semester.”'' |
| `code.project` | both carry `project` as a literal field name; §3.11 gives Code its own row, so the same value can legitimately activate both schemas at once | §3.11: “Code files may use project, repository, programming language, and artifact type.” |
| `app.application-packet` | a research artifact can be a supporting document in an application packet without leaving Research | §4.9: “a PVA/RDP abstract that is both a Research artifact and a supporting document in a UChicago application packet” |

**Sensitivity**: `none` — No `potentially sensitive` content is intrinsic to this domain. A handling class is P7's (§8.4) and is not set here.

**Open question (Joseph's call, unresolved)**

> Once the sub-domains below exist, is §3.11's Research domain still a filing domain in its own right — the branch a project's odds and ends land in — or only the schema they all inherit? The answer decides whether `Research/<project>/General` is a real node or a residual one (§5.9).

---

### 2. `res.manuscript-preparation` — Manuscript preparation and its version family

> Drafts of a paper the user is writing, and the version family those drafts form.

**provenance**: `design` — §4.5: “a research group PVA/RDP — Manuscripts and Figures” §5.1: “Research supported by PVA/RDP and manuscript groups” §4.2: “For a research group, it might be a manuscript, abstract, or protocol with a known project identifier.”

**Schema** — the fields this domain, and only this domain, legitimises.

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `project` | string | `PVA/RDP` | `validated` | **§3.11 literal.** §4.5's worked group label pairs the project with the artifact types: 'PVA/RDP — Manuscripts and Figures'. |
| `manuscript title` | string | `Photoactivatable RDP reporters in live cells` | `direct` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. §3.13 names 'document title' as a direct source. The title is the identity of the version family, not the filename. |
| `stage` | string | `under revision` | `validated` | **§3.11 literal.** §5.4 places stage between project and artifact type. |
| `venue` | string | `Nature Communications` | `validated` | **§3.11 literal.** The journal a draft is aimed at. See the open question: aiming is not publishing. |
| `draft label` | string | `v3 clean` | `validated` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. The member's position inside the version family §3.1 already makes a universal fact. A filename suffix alone is never enough — the label is only written when a revision token corroborates it. |
| `authorship position` | string | `first author` | `llm_supported` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. The author list's ordering relative to the user is prose, not a labelled slot. §3.8 makes this an authorship role, so it may describe the file and may never become a folder level. |
| `corresponding author` | string | `J. Chen` | `direct` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. From a labelled 'Corresponding author:' slot only. §3.8 authorship role; never a destination dimension. |

**Recognition**

| | |
|---|---|
| deterministic (pattern **plus** corroborating context) | • a document-title observation co-occurring with manuscript-structure headings — 'Abstract', 'Introduction', 'Methods', 'Results', 'Discussion', 'References' — in one file<br>• a project identifier co-occurring with a revision token ('draft', 'revised', 'clean copy', 'tracked changes', 'response') in the filename or a page-one heading zone (§2.2: “A course code or university name found in a filename, title, or page-one heading is more meaningful than the same text appearing once in a reference list on page eighteen.”)<br>• two files sharing a document title and differing only in a revision token, which is the version-family signal §3.1 already names<br>• a stage token ('in preparation', 'submitted', 'under revision', 'accepted') co-occurring with the manuscript title<br>• `venue` is §3.11's inherited Research field: a venue name from a validated gazetteer (§3.7, deferred) co-occurring with a cover letter, a submission portal record, or a journal-formatted template applied to the draft. §4.9 is why a bare organisation name never suffices |
| needs the LLM | • an untitled .docx whose only manuscript signal is prose that reads as a Discussion section<br>• deciding whether two differently-titled files are the same manuscript after a retitle<br>• reading an author list to place the user in it |
| never alone | • a bare four-digit number in a filename (§3.10: “The product must not use fuzzy date parsing because file names and documents frequently contain numbers that look like years but are course identifiers, version numbers, build numbers, ZIP codes, or other unrelated values.”)<br>• the word 'draft' alone<br>• a bare author surname<br>• a bare `Author` or `Last Modified By` metadata value — P6's producer/creator discount rule suppresses it before ranking (§3.8: “It should avoid using authorship or creator identity as a destination dimension.”) |

**Work types**: `manuscript draft`, `cover letter draft`, `supplementary information`, `title page`, `highlights`, `graphical abstract`, `author contribution statement`, `tracked-changes copy`, `clean copy`

**Grouping reasons**: one manuscript across its drafts; one project across its manuscripts; one manuscript and its supplementary files

**Template**: `project → manuscript → stage`

> §5.4: “a Research template may define project → stage → artifact type” narrowed one level: the manuscript title is the child that makes `stage` legible, which is §5.5: “a parent dimension should provide the context required to understand the child. A work type such as Homework 3 is meaningful only after the course is known”

**Collides with**

| domain | discriminating signal | design cite |
|---|---|---|
| `res.figure-and-source` | both carry the project and the manuscript title; only the figure carries a figure label or a design/creative source format | §4.5: “a research group PVA/RDP — Manuscripts and Figures” |
| `res.preprint` | the same version family continues into the preprint; only the preprint carries a server accession and a public posting date | — |
| `res.thesis-supervision` | a thesis chapter and a manuscript can be byte-identical; only the thesis carries a degree programme and a committee | — |
| `acad.course-enrollment` | both are sectioned prose; only the course paper carries a course code with academic context | §3.5: ''BUSIB 4300 becomes a course fact only when the engine finds a course-code pattern together with academic context such as “syllabus,” “lecture,” “credits,” “instructor,” or “semester.”'' |
| `app.application-packet` | a manuscript packet must not absorb a draft belonging to a different study, for the same reason an application packet must not absorb a conflicting institution | §4.8: “an application packet does not silently absorb a document with a conflicting target institution” |

**Sensitivity**: `none` — No `potentially sensitive` content is intrinsic to this domain. A handling class is P7's (§8.4) and is not set here.

**Open question (Joseph's call, unresolved)**

> Does a manuscript branch by `venue` at all? A paper rejected at one journal and resubmitted to another would have to move folders, which §5.10's “A carefully curated existing folder should be treated as a strong expression of user intent” argues against — but the journal is often the only name the user remembers. Real level, or metadata only?

---

### 3. `res.manuscript-submission` — Journal submission packets and editorial correspondence

> The packet actually sent to a journal, and the correspondence the submission generates.

**provenance**: `inference` — Extends the design-named manuscript domain (§4.2: “For a research group, it might be a manuscript, abstract, or protocol with a known project identifier.”) with the submission event. The design names `stage` as a Research field (§3.11: “Research files may use project, stage, artifact type, lab, and venue.”) and names no submission fields.

**Schema** — the fields this domain, and only this domain, legitimises.

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `venue` | string | `Nature Communications` | `validated` | **§3.11 literal.** Here the venue is settled, not aspirational: a submission exists at exactly one journal at a time. |
| `manuscript id` | string | `NCOMMS-25-01234` | `validated` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. The publisher's tracking identifier. It is the only value that ties a decision letter, a revision and a proof together, and it is worthless without submission context — see never_alone. |
| `submission stage` | string | `revision 1` | `validated` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. A narrowing of §3.11's `stage` for this domain: initial submission, revision, proof, accepted. |
| `submission date` | date | `2026-03-14` | `direct` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. From a labelled date slot only. §3.10 forbids fuzzy parsing. |
| `editor` | string | `Handling editor: R. Okonkwo` | `direct` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. From a labelled slot. §3.8 role field; never a destination dimension. |
| `project` | string | `PVA/RDP` | `validated` | **§3.11 literal.**  |

**Recognition**

| | |
|---|---|
| deterministic (pattern **plus** corroborating context) | • a publisher manuscript-id token co-occurring with submission context ('submitted', 'manuscript number', 'editorial office', 'corresponding author', 'decision')<br>• an EML/MSG file (§2.9: “Email formats such as EML, MBOX, MSG, and exported mail archives should yield sender, recipients, subject, sent date, thread identifiers, message body, attachment names, and reply-chain context”) whose subject carries a manuscript-id token and whose sender is an editorial-office address (a `cid-email` hit, planning/deferred-catalogues/06-citation-identifier-patterns.json)<br>• a cover-letter layout — a salutation to an editor plus a manuscript title already in the corpus<br>• `project` is §3.11's inherited Research field: it is recognised by res.research-project's rule — a project identifier token co-occurring with research context — and is not re-derived per domain; this entry's own anchors supply the corroboration<br>• `venue` is §3.11's inherited Research field: a venue name from a validated gazetteer (§3.7, deferred) co-occurring with an editorial-office sender domain or a submission-portal record. §4.9 is why a bare organisation name never suffices |
| needs the LLM | • reading a cover letter to tell an initial submission from a resubmission when no id is present<br>• deciding whether an unlabelled PDF is the submitted version or a later draft |
| never alone | • a bare alphanumeric ticket-shaped id<br>• a journal name appearing in a reference list — `cid-citation-authoryear` hits sit in the `reference_list` zone (§2.2: “A course code or university name found in a filename, title, or page-one heading is more meaningful than the same text appearing once in a reference list on page eighteen.”)<br>• the word 'submitted' |

**Work types**: `cover letter`, `submission checklist`, `author agreement or copyright transfer`, `portal confirmation`, `manuscript id acknowledgement`, `funding and ORCID declaration`, `conflict-of-interest statement`, `proofs`, `licence selection`

**Grouping reasons**: one manuscript across its submission rounds; one venue across the submissions sent to it; one submission and its confirmation correspondence

**Template**: `project → manuscript → submission stage`

> Parent-before-child (§5.5: “a parent dimension should provide the context required to understand the child. A work type such as Homework 3 is meaningful only after the course is known”): a submission stage names nothing on its own; the manuscript makes it legible.

**Collides with**

| domain | discriminating signal | design cite |
|---|---|---|
| `res.peer-review-author` | the submission packet is what the user sent; the review corpus is what came back — they share the manuscript id and nothing else | — |
| `res.published-article` | a proof and a published PDF are near-identical; only the published version carries a DOI in publisher furniture | — |
| `app.application-packet` | both are purpose-defined packets assembled for an external body; only the application carries a target institution and a cycle | §4.8: “an application packet does not silently absorb a document with a conflicting target institution” |

**Sensitivity**: `none` — No `potentially sensitive` content is intrinsic to this domain. A handling class is P7's (§8.4) and is not set here.

---

### 4. `res.peer-review-author` — Peer review received, and the revision it drives

> Referee reports and editorial decisions on the user's own manuscript, and the response written to them.

**provenance**: `inference` — Extends the design-named manuscript domain (§4.2: “For a research group, it might be a manuscript, abstract, or protocol with a known project identifier.”) along §3.11's `stage`. The design names no review fields.

**Schema** — the fields this domain, and only this domain, legitimises.

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `venue` | string | `Nature Communications` | `validated` | **§3.11 literal.**  |
| `manuscript id` | string | `NCOMMS-25-01234` | `validated` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. Shared with res.manuscript-submission; it is the join key of the whole submission lifecycle. |
| `review round` | string | `round 2` | `validated` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. A narrowing of §3.11's `stage`. A round is only asserted when a decision or report token corroborates it. |
| `decision` | string | `major revision` | `llm_supported` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. An editor's decision is prose spread over a letter; there is no labelled slot to read it from. |
| `reviewer designation` | string | `Reviewer 2` | `validated` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. A positional label inside one report, deliberately not a person. §3.8's role rule is why this is not an `authored_by`. |
| `project` | string | `PVA/RDP` | `validated` | **§3.11 literal.**  |

**Recognition**

| | |
|---|---|
| deterministic (pattern **plus** corroborating context) | • a reviewer-designation token ('Reviewer 1', 'Referee 2') co-occurring with report vocabulary ('the authors should', 'my main concern', 'minor comments') in one file<br>• a decision-letter layout — an editorial salutation plus a manuscript id plus a decision term — co-occurring with a manuscript title the corpus already holds<br>• a point-by-point document whose structure alternates quoted reviewer text with response text, co-occurring with the same manuscript id<br>• `project` is §3.11's inherited Research field: it is recognised by res.research-project's rule — a project identifier token co-occurring with research context — and is not re-derived per domain; this entry's own anchors supply the corroboration<br>• `venue` is §3.11's inherited Research field: a venue name from a validated gazetteer (§3.7, deferred) co-occurring with a decision-letter letterhead or an editorial-office sender domain. §4.9 is why a bare organisation name never suffices |
| needs the LLM | • reading a decision letter to tell a reject-and-resubmit from a revision invitation<br>• matching an unlabelled response document to the round it answers |
| never alone | • a bare 'Reviewer 1' string with no manuscript context<br>• a bare decision word such as 'accept' or 'reject'<br>• a tracked-changes file alone — it is equally a revision, a supervisor's feedback and a co-author's edit |

**Work types**: `decision letter`, `referee report`, `response to reviewers`, `point-by-point table`, `tracked-changes revision`, `rebuttal`, `appeal letter`, `revised supplementary information`

**Grouping reasons**: one manuscript across its review rounds; one round and the revision answering it

**Template**: `project → manuscript → review round`

> Parent-before-child (§5.5: “a parent dimension should provide the context required to understand the child. A work type such as Homework 3 is meaningful only after the course is known”): 'round 2' is meaningless until the manuscript is known.

**Collides with**

| domain | discriminating signal | design cite |
|---|---|---|
| `res.peer-review-referee` | the mirror corpus. The discriminator is whose manuscript it is, and nothing else — the file shapes are identical | — |
| `res.manuscript-preparation` | a revised draft is both; the review branch holds the correspondence, the manuscript branch holds the version family | §3.1: “member of a version family, and potentially sensitive” |
| `res.thesis-supervision` | supervisor feedback and referee comments are both tracked-changes-on-a-draft; only the referee report carries a venue and a round | — |

**Sensitivity**: `potentially_sensitive` — §2.9's phrase `potentially sensitive`. A decision letter carries an editor's identity and the confidential contents of an unpublished manuscript. A handling class is P7's (§8.4) and is not set here.

---

### 5. `res.peer-review-referee` — Reviewing and editorial work done for others

> Manuscripts the user was asked to review, the reports written on them, and editorial handling work.

**provenance**: `proposal` — The design names peer review nowhere. It is a distinct corpus because §3.11's `project` does not apply — the work is somebody else's.

**Schema** — the fields this domain, and only this domain, legitimises.

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `venue` | string | `Journal of Cell Biology` | `validated` | **§3.11 literal.** The only §3.11 Research field that survives into this domain intact. |
| `review assignment id` | string | `JCB-2026-00417` | `validated` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. The editorial system's handle for one assignment. |
| `review role` | string | `handling editor` | `llm_supported` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. Reviewer, handling editor, statistical reviewer and board member are distinguished by invitation prose, not by a field. |
| `reviewed manuscript title` | string | `Mitochondrial dynamics under hypoxia` | `direct` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. §3.13's 'document title'. Deliberately a different field from res.manuscript-preparation's `manuscript title`: §3.8's rule is that the same entity type in a different role is a different field. |
| `review due date` | date | `2026-04-02` | `direct` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. From a labelled slot in the invitation only. |

**Recognition**

| | |
|---|---|
| deterministic (pattern **plus** corroborating context) | • invitation vocabulary ('invited to review', 'referee report', 'confidential to the editor', 'decline this invitation') co-occurring with a venue name and an assignment id<br>• an email (§2.9: “Email formats such as EML, MBOX, MSG, and exported mail archives should yield sender, recipients, subject, sent date, thread identifiers, message body, attachment names, and reply-chain context”) from an editorial-office address (a `cid-email` hit, planning/deferred-catalogues/06-citation-identifier-patterns.json) whose body carries review-invitation language and names a manuscript title absent from the user's own version families<br>• a manuscript PDF carrying a 'Confidential' or 'For review only' watermark together with a venue name and no author identity the corpus recognises |
| needs the LLM | • deciding whether a manuscript in the corpus is the user's own or one received for review, when the author list is not decisive<br>• separating a handling-editor role from a reviewer role in an ambiguous invitation |
| never alone | • a bare venue name (§4.9: “A university name alone should not create a group because Columbia can appear as an authoring school, course provider, target institution, employer, research venue, or merely a cited organization.”)<br>• the word 'review' — it is equally a literature review, a systematic-review screening record, a book review and a performance review<br>• a bare manuscript PDF with no invitation, watermark or assignment id |

**Work types**: `review invitation`, `manuscript under review`, `referee report written`, `editor recommendation`, `conflict-of-interest declaration`, `reviewer credit record`, `editorial board correspondence`

**Grouping reasons**: one assignment and its manuscript; one venue across the assignments it sent; one review cycle across invitation, manuscript and report

**Template**: `venue → review role → assignment`

> There is no project to lead with, so §5.4's Research order does not apply. Venue is the only stable parent, and it supplies the context the assignment needs (§5.5: “a parent dimension should provide the context required to understand the child. A work type such as Homework 3 is meaningful only after the course is known”).

**Collides with**

| domain | discriminating signal | design cite |
|---|---|---|
| `res.peer-review-author` | the mirror corpus; identical file shapes, opposite ownership | — |
| `res.reading-library` | a manuscript received for review is not literature the user chose to read, and must not join the reading library's version families | §4.8: “an application packet does not silently absorb a document with a conflicting target institution” |
| `res.systematic-review` | both hold other people's papers in bulk; only the systematic review carries a review question and a screening stage | — |

**Sensitivity**: `potentially_sensitive` — §2.9's phrase `potentially sensitive`. The corpus is other people's unpublished manuscripts held under an explicit confidentiality undertaking, plus reviewer identity. A handling class is P7's (§8.4) and is not set here.

**Open question (Joseph's call, unresolved)**

> A manuscript received for review is somebody else's unpublished work held in confidence. Should it be filed into the tree at all, or surfaced the way §4.9 surfaces protected records — “Rare but sensitive files such as passports, visas, and legal documents may be surfaced as protected records” — and otherwise left alone?

---

### 6. `res.preprint` — Preprints and preprint versions

> Versions of a paper posted publicly before or alongside journal publication.

**provenance**: `inference` — Extends the design-named manuscript domain (§4.2: “For a research group, it might be a manuscript, abstract, or protocol with a known project identifier.”) along §3.11's `stage`. Preprint servers are named nowhere in the design.

**Schema** — the fields this domain, and only this domain, legitimises.

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `project` | string | `PVA/RDP` | `validated` | **§3.11 literal.**  |
| `preprint server` | string | `bioRxiv` | `validated` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. A narrowing of §3.11's `venue` for a posting rather than a publication — and deliberately a separate field, because a paper can have both at once. |
| `preprint accession` | string | `arXiv:2103.02702` | `validated` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. A `cid-arxiv-new`, `cid-arxiv-old` or `cid-doi` hit (planning/deferred-catalogues/06-citation-identifier-patterns.json) in the title or page-one zone. The pattern is that catalogue's; the corroborating context is this one's. |
| `preprint version` | string | `v2` | `validated` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. Servers version postings explicitly. Only asserted when the accession carries the version suffix or a posting notice states it. |
| `posting date` | date | `2026-02-08` | `direct` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. From the server's own stamped header line, a labelled slot. |
| `venue` | string | `Nature Communications` | `validated` | **§3.11 literal.** Present only once the preprint has a journal home. |

**Recognition**

| | |
|---|---|
| deterministic (pattern **plus** corroborating context) | • a `cid-arxiv-new` or `cid-doi` hit (planning/deferred-catalogues/06-citation-identifier-patterns.json) in the title or page-one heading zone co-occurring with server language ('preprint', 'not certified by peer review', 'posted', 'this version')<br>• a stamped server header band on page one co-occurring with a document title the corpus already holds as a manuscript draft<br>• a posting-confirmation email (§2.9: “Email formats such as EML, MBOX, MSG, and exported mail archives should yield sender, recipients, subject, sent date, thread identifiers, message body, attachment names, and reply-chain context”) whose sender is a preprint server and whose body carries the accession<br>• `project` is §3.11's inherited Research field: it is recognised by res.research-project's rule — a project identifier token co-occurring with research context — and is not re-derived per domain; this entry's own anchors supply the corroboration<br>• `venue` is §3.11's inherited Research field: a venue name from a validated gazetteer (§3.7, deferred) co-occurring with a later publication record naming the same document title. §4.9 is why a bare organisation name never suffices |
| needs the LLM | • deciding whether an unlabelled PDF is the posted version or the draft it was made from<br>• reading a licence line to tell a preprint from an accepted-manuscript deposit |
| never alone | • a bare accession-shaped token<br>• the word 'preprint' in a reference list (§2.2: “A course code or university name found in a filename, title, or page-one heading is more meaningful than the same text appearing once in a reference list on page eighteen.”)<br>• a bare four-digit number — an arXiv identifier's leading digits encode a year and month and no date may be taken from them (§3.10: “The product must not use fuzzy date parsing because file names and documents frequently contain numbers that look like years but are course identifiers, version numbers, build numbers, ZIP codes, or other unrelated values.”) |

**Work types**: `preprint PDF`, `posting confirmation`, `licence selection`, `version note`, `DOI reservation record`, `preprint comment thread`, `server metadata record`

**Grouping reasons**: one manuscript across its posted versions; one project across its preprints

**Template**: `project → manuscript → stage`

> Same order as res.manuscript-preparation deliberately: a preprint is a stage of a manuscript, not a separate object — which is what the open question tests.

**Collides with**

| domain | discriminating signal | design cite |
|---|---|---|
| `res.manuscript-preparation` | same version family, same title; only the preprint carries an accession and a posting date | §3.1: “member of a version family, and potentially sensitive” |
| `res.published-article` | the same content under two identifiers; §4.8's absorb rule applies — the published branch must not swallow the preprint's own accession | §4.8: “an application packet does not silently absorb a document with a conflicting target institution” |
| `res.repository-deposit` | an accepted-manuscript deposit and a preprint are both public postings; only the deposit carries an institutional repository and an embargo | — |

**Sensitivity**: `none` — No `potentially sensitive` content is intrinsic to this domain. A handling class is P7's (§8.4) and is not set here.

**Open question (Joseph's call, unresolved)**

> Is a preprint the same version family as the article it becomes (“member of a version family”, §3.1), or a separate artifact? The answer decides whether `Research/<project>/<manuscript>` holds both, or whether preprints get their own branch.

---

### 7. `res.published-article` — Published articles, reprints and author copies

> The user's own published outputs and the publisher artifacts that come with them.

**provenance**: `inference` — Extends the design-named manuscript domain to its terminal stage (§4.2: “For a research group, it might be a manuscript, abstract, or protocol with a known project identifier.”, §3.11: “Research files may use project, stage, artifact type, lab, and venue.”). The design names no publication fields.

**Schema** — the fields this domain, and only this domain, legitimises.

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `venue` | string | `Nature Communications` | `validated` | **§3.11 literal.** Settled at publication and never changes again, which is what makes it a safer dimension here than in res.manuscript-preparation. |
| `doi` | string | `10.1038/s41586-021-03819-2` | `validated` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. A `cid-doi` hit (planning/deferred-catalogues/06-citation-identifier-patterns.json) in the title or page-one zone, corroborated by publisher furniture. A DOI in a reference list is somebody else's (§2.2: “A course code or university name found in a filename, title, or page-one heading is more meaningful than the same text appearing once in a reference list on page eighteen.”). |
| `publication year` | date | `2026` | `direct` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. From a labelled 'Published' slot or PDF metadata only — never inferred from a filename (§3.10: “The product must not use fuzzy date parsing because file names and documents frequently contain numbers that look like years but are course identifiers, version numbers, build numbers, ZIP codes, or other unrelated values.”). |
| `article type` | string | `research article` | `llm_supported` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. Research article, review, comment, editorial and letter are distinguished by publisher labelling that varies by venue. |
| `citation locator` | string | `12(3), 45–67` | `direct` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. Volume, issue and pages as one string from the publisher's own citation block. Kept as one field because splitting it invites the fuzzy numeric parsing §3.10 forbids. |
| `authorship position` | string | `first author` | `llm_supported` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. §3.8 authorship role; describes the file, never a folder level. |
| `project` | string | `PVA/RDP` | `validated` | **§3.11 literal.**  |

**Recognition**

| | |
|---|---|
| deterministic (pattern **plus** corroborating context) | • a `cid-doi` hit (planning/deferred-catalogues/06-citation-identifier-patterns.json) in the title or page-one zone co-occurring with publisher furniture ('Received', 'Accepted', 'Published online', a licence line, a citation block)<br>• a document title that is already a manuscript version family in the corpus, co-occurring with a venue name and a DOI<br>• an offprint or reprint whose page furniture carries the venue and a citation locator<br>• `project` is §3.11's inherited Research field: it is recognised by res.research-project's rule — a project identifier token co-occurring with research context — and is not re-derived per domain; this entry's own anchors supply the corroboration |
| needs the LLM | • telling a review article from a research article when the venue does not label it<br>• reading an author list to establish the user's position in it |
| never alone | • a bare `cid-doi` hit — every paper in a reading library carries one<br>• a bare venue name (§4.9: “A university name alone should not create a group because Columbia can appear as an authoring school, course provider, target institution, employer, research venue, or merely a cited organization.”)<br>• a bare four-digit year (§3.10: “The product must not use fuzzy date parsing because file names and documents frequently contain numbers that look like years but are course identifiers, version numbers, build numbers, ZIP codes, or other unrelated values.”) |

**Work types**: `published PDF (version of record)`, `accepted manuscript`, `publisher reprint or offprint`, `supplementary files`, `licence or copyright transfer`, `press release`, `citation and metrics report`, `cover art`

**Grouping reasons**: one manuscript across preprint, accepted manuscript and version of record; one venue across the user's papers in it; one project across its publications

**Template**: `project → manuscript → artifact type`

> §5.4: “a Research template may define project → stage → artifact type” applied at the terminal stage; the manuscript is the parent that makes 'supplementary' legible (§5.5: “a parent dimension should provide the context required to understand the child. A work type such as Homework 3 is meaningful only after the course is known”).

**Collides with**

| domain | discriminating signal | design cite |
|---|---|---|
| `res.reading-library` | identical file shape — a publisher PDF with a DOI. The only discriminator is authorship, and §3.8 forbids authorship as a destination dimension; see that domain's open question | §3.8: “It should avoid using authorship or creator identity as a destination dimension.” |
| `res.preprint` | same content, different identifier | — |
| `res.correction-retraction` | a correction notice must attach to the article and must not silently join its version family | §4.8: “an application packet does not silently absorb a document with a conflicting target institution” |
| `res.repository-deposit` | the deposited copy and the version of record are the same bytes under two custodians | — |

**Sensitivity**: `none` — No `potentially sensitive` content is intrinsic to this domain. A handling class is P7's (§8.4) and is not set here.

---

### 8. `res.figure-and-source` — Figures and figure source files

> The figures a research output is built from, and the editable sources they are exported from.

**provenance**: `design` — §4.5: “a research group PVA/RDP — Manuscripts and Figures” — 'Figures' is half of the design's own worked research group label. §2.9: “Design and creative formats such as PSD, AI, SVG, Figma exports, CAD files, and 3D files should at minimum yield filename, format, dimensions or canvas properties”

**Schema** — the fields this domain, and only this domain, legitimises.

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `project` | string | `PVA/RDP` | `validated` | **§3.11 literal.**  |
| `figure label` | string | `Figure 3` | `validated` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. The figure's identity inside its parent output. Only asserted with a caption or manuscript context — see never_alone. |
| `panel label` | string | `3b` | `validated` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. Panels are edited and replaced independently of the assembled figure, so they need their own value. |
| `manuscript title` | string | `Photoactivatable RDP reporters in live cells` | `direct` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. §3.13's 'document title', read from the parent output. This is the field that stops a figure packet absorbing a figure from a different study. |
| `figure source format` | string | `Adobe Illustrator (.ai)` | `direct` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. §2.9: “Design and creative formats such as PSD, AI, SVG, Figma exports, CAD files, and 3D files should at minimum yield filename, format, dimensions or canvas properties” — the detected format is a direct observation, and it is what separates an editable source from an export. |
| `source dataset` | string | `cohort2_normalised.csv` | `llm_supported` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. Which data a plot renders is stated in a caption or a methods line, not in a slot. |

**Recognition**

| | |
|---|---|
| deterministic (pattern **plus** corroborating context) | • a figure-label token ('Figure 3', 'Fig. 3', 'Supplementary Figure 1', 'Extended Data Fig. 2') in a filename or caption zone co-occurring with a manuscript title or project identifier the corpus already holds<br>• a design or creative format (§2.9: “Design and creative formats such as PSD, AI, SVG, Figma exports, CAD files, and 3D files should at minimum yield filename, format, dimensions or canvas properties”) whose filename carries a figure-label token and whose siblings share a manuscript's version family<br>• an export and a source file with the same stem and different formats, co-occurring with one caption document |
| needs the LLM | • matching an unlabelled exported image to the figure slot it fills<br>• reading a caption to decide whether a panel belongs to the main figure or the supplement |
| never alone | • a bare `Fig1.png` filename with no caption, manuscript or project context<br>• a bare panel letter such as 'b'<br>• an image sitting in a project directory — the directory is the high-frequency entity §4.9 refuses as a sole bridge (§4.9: “one high-frequency entity acts as the only bridge”)<br>• the absence of EXIF (§2.6: “the system must not mistake the absence of EXIF for proof that an image is a screenshot”) |

**Work types**: `figure source file (AI/PSD/SVG)`, `exported figure (TIFF/EPS/PNG)`, `figure legend document`, `panel component`, `schematic`, `multi-panel assembly`, `graphical abstract`, `figure permission or licence`, `source-data file`

**Grouping reasons**: one figure across its panels and exports; one manuscript across its figures; one figure across the outputs that reuse it

**Template**: `project → manuscript → figure`

> Narrows §5.4's artifact-type level to the figure itself. 'Figure 3' names nothing until the manuscript is known (§5.5: “a parent dimension should provide the context required to understand the child. A work type such as Homework 3 is meaningful only after the course is known”).

**Collides with**

| domain | discriminating signal | design cite |
|---|---|---|
| `res.dataset` | a figure is a rendering of data: the same plot is a manuscript component and a dataset artifact at once, and §3.11 already permits a file to hold facts from more than one domain | §3.11: “An academic abstract submitted as part of a university application can retain project = PVA/RDP and document type = abstract while also carrying purpose = university application and target university = UChicago.” |
| `res.manuscript-preparation` | the figure travels inside the manuscript packet; a manuscript packet must not absorb a figure belonging to a different study | §4.8: “an application packet does not silently absorb a document with a conflicting target institution” |
| `res.statistical-output` | a diagnostic plot is statistical output; a publication figure is a manuscript component. The formats are identical | — |
| `res.poster` | the same panel is reused on a poster with a different label | — |
| `photos.event` | §3.11's Photos row claims images generically; a microscopy panel carries capture metadata and would otherwise route there | §3.11: “Photos may use capture year, event, location, people, camera information, and media type.” |

**Sensitivity**: `none` — No `potentially sensitive` content is intrinsic to this domain. A handling class is P7's (§8.4) and is not set here.

**Open question (Joseph's call, unresolved)**

> Do figures live under the manuscript that publishes them, or in one per-project figure library the manuscripts point at? §5.8's uneven depth allows either, and a figure reused across a poster, a talk and two papers has no single natural parent.

---

### 9. `res.dataset` — Research datasets

> The data a study produced or was given, at whatever level of processing.

**provenance**: `inference` — Extends §3.11's Research row with the data half of “research and lab work” (§3.15: “academic coursework, college applications, research and lab work, career and recruiting, photos and captures, and code projects”). The design names no dataset fields.

**Schema** — the fields this domain, and only this domain, legitimises.

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `study` | string | `PVA cohort 2` | `validated` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. Deliberately not `project`: a project runs several studies and a dataset belongs to exactly one. §3.8's role rule is the precedent for splitting a field rather than overloading it. |
| `data level` | string | `analysis-ready` | `validated` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. Raw, processed and analysis-ready copies of the same data are different files with the same name, and the level is the only thing that distinguishes them. |
| `collection date` | date | `2026-01-22` | `direct` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. From a labelled slot or a manifest field only (§3.10: “The product must not use fuzzy date parsing because file names and documents frequently contain numbers that look like years but are course identifiers, version numbers, build numbers, ZIP codes, or other unrelated values.”). |
| `instrument` | string | `Illumina NovaSeq 6000` | `validated` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. What produced the data. Shared with res.instrument-output, which is why the two collide below. |
| `dataset version` | string | `v2.1` | `validated` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. Datasets are re-released; §3.1's version family is universal, this is the released label. |
| `accession` | string | `GSE123456` | `validated` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. A repository accession, corroborated by deposit context. The identifier patterns live in planning/deferred-catalogues/06-citation-identifier-patterns.json. |
| `licence` | string | `CC BY 4.0` | `direct` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. From a labelled licence slot in a README or metadata record. |
| `project` | string | `PVA/RDP` | `validated` | **§3.11 literal.**  |

**Recognition**

| | |
|---|---|
| deterministic (pattern **plus** corroborating context) | • a tabular file (§2.9: spreadsheets yield “sheet names, column headers, visible cell values, table-like regions”) whose column headers co-occur with study or protocol vocabulary that a protocol document in the same project also carries<br>• a repository accession token co-occurring with deposit context ('accession', 'deposited', 'available at', 'under embargo')<br>• a README or manifest naming a data directory together with a study identifier and a data level term<br>• an instrument model name in a labelled manifest or metadata field co-occurring with a study identifier<br>• a dataset version token co-occurring with release vocabulary ('release', 'version', 'frozen', 'supersedes') |
| needs the LLM | • deciding whether a table is a dataset, a results table or an extraction sheet<br>• reading a README to establish which processing level a directory holds |
| never alone | • a bare .csv<br>• a bare column header such as 'id', 'value' or 'date'<br>• a bare accession-shaped token<br>• a bare gene, chemical or cell-line name |

**Work types**: `raw data file`, `processed data table`, `analysis-ready dataset`, `data release archive`, `README`, `checksum manifest`, `instrument export`, `metadata record`, `embargo notice`

**Grouping reasons**: one study across its data levels; one dataset across its released versions; one project across its studies' data

**Template**: `project → study → data level`

> Study before level, because 'raw' names nothing until the study is known (§5.5: “a parent dimension should provide the context required to understand the child. A work type such as Homework 3 is meaningful only after the course is known”). Collection date stays metadata: §5.5: “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders. Photos and capture-based media are the major exception: time often belongs first because capture date is a defining aspect of the material.”

**Collides with**

| domain | discriminating signal | design cite |
|---|---|---|
| `res.instrument-output` | raw acquisition output is not yet a dataset; only the dataset carries a data level and a release version | — |
| `res.data-dictionary` | the dictionary describes the dataset and is not one | — |
| `res.reproducibility-package` | a package bundles a dataset with code; the bundle is not the dataset | §2.9: “Compressed archives should yield their manifests without extraction” |
| `res.statistical-output` | an estimates table is output, not data | — |
| `res.repository-deposit` | the deposited copy and the working copy are the same bytes under different custody | — |
| `res.qualitative-coding` | a transcript corpus is data with participant-level rows and different handling | — |

**Sensitivity**: `potentially_sensitive` — §2.9's phrase `potentially sensitive`. A dataset drawn from human subjects carries participant-level rows; a dataset from a telescope carries none. The trigger is the study, not the file format, which is what the open question is about. A handling class is P7's (§8.4) and is not set here.

**Open question (Joseph's call, unresolved)**

> Does a study's sensitivity travel to everything derived from it — datasets, statistical output, figures — or is every file classified on its own evidence? §3.9 forbids using a session as “a basis for automatic semantic propagation”; nothing in the design says whether a sensitivity fact propagates along a derivation edge.

---

### 10. `res.data-dictionary` — Data dictionaries and codebooks

> The documents that say what a dataset's variables mean and how its values are coded.

**provenance**: `proposal` — The design names data dictionaries nowhere. Authored because a dictionary and the dataset it describes have different fields and different lifetimes.

**Schema** — the fields this domain, and only this domain, legitimises.

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `study` | string | `PVA cohort 2` | `validated` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. Shared with res.dataset; it is the join. |
| `variable name` | string | `bl_hba1c` | `direct` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. From a labelled dictionary column (§2.9: spreadsheets yield “sheet names, column headers, visible cell values, table-like regions”). §3.13's “labeled form field” is the precedent for calling a named column direct. |
| `variable label` | string | `Baseline HbA1c (mmol/mol)` | `direct` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. The human-readable gloss, from its own labelled column. |
| `value coding` | string | `1 = yes; 2 = no; -9 = missing` | `direct` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. The coding scheme, from its own labelled column. This is the field that makes a dictionary re-usable years later and is the reason the domain exists separately. |
| `dataset version` | string | `v2.1` | `validated` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. A dictionary is valid for one dataset version and silently wrong for another. |
| `collection instrument` | string | `PHQ-9` | `validated` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. Which instrument produced the variable, where one did. Shared with res.survey-instrument. |

**Recognition**

| | |
|---|---|
| deterministic (pattern **plus** corroborating context) | • a spreadsheet whose header row carries dictionary vocabulary ('variable', 'label', 'type', 'values', 'missing', 'units') co-occurring with a study identifier<br>• a structured-data file (§2.9: “notebook cell types, package manifests, schema keys, repository markers, and project-root signals”) whose schema keys name a dataset the corpus already holds<br>• a document whose repeated block structure is name / label / coding, co-occurring with a dataset version token<br>• an instrument name in a labelled dictionary column ('source', 'instrument', 'scale') co-occurring with the variable rows it describes |
| needs the LLM | • telling a codebook from a results table when the header row is unlabelled<br>• matching a dictionary to the dataset version it describes when neither states a version |
| never alone | • a bare column-header list<br>• the word 'codebook'<br>• a bare .json schema file |

**Work types**: `data dictionary spreadsheet`, `codebook`, `variable manifest`, `coding scheme`, `schema file (JSON Schema, .avsc)`, `platform dictionary export`, `derivation notes`, `missing-value policy`

**Grouping reasons**: one dataset and its dictionary; one study across its dictionary versions

**Template**: `project → study → dataset version`

> A dictionary is only meaningful beside its dataset version, so it inherits res.dataset's parents rather than owning a branch (§5.5: “a parent dimension should provide the context required to understand the child. A work type such as Homework 3 is meaningful only after the course is known”).

**Collides with**

| domain | discriminating signal | design cite |
|---|---|---|
| `res.dataset` | the dictionary describes; the dataset holds. They share a study and a version and nothing else | — |
| `res.survey-instrument` | the instrument asks the question; the dictionary describes the recorded answer | — |
| `res.qualitative-coding` | a qualitative codebook codes text, not variables — same word, different object | — |

**Sensitivity**: `none` — No `potentially sensitive` content is intrinsic to this domain. A handling class is P7's (§8.4) and is not set here.

---

### 11. `res.analysis-code` — Analysis code and scripts

> The code that turns a study's data into its results, written for one project rather than for release.

**provenance**: `inference` — Extends §3.11's Code row (§3.11: “Code files may use project, repository, programming language, and artifact type.”) into a research project. §5.1 names both 'Research' and “Code and Projects” as candidate top-level branches, which is the open question below.

**Schema** — the fields this domain, and only this domain, legitimises.

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `project` | string | `PVA/RDP` | `validated` | §3.11 literal in both the Research and the Code row — the one field the two domains share, which is why they collide so cleanly. |
| `repository` | string | `pva-analysis` | `direct` | §3.11 Code row, literal. Detected from a repository marker (deferred catalogue 05), which is a structural observation, not an inference. |
| `programming language` | string | `R` | `direct` | §3.11 Code row, literal. From the detected format and the file's own import or shebang lines. |
| `artifact type` | string | `analysis script` | `validated` | §3.11 literal in both rows. |
| `analysis step` | string | `Figure 3 regression` | `llm_supported` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. What a script is for is stated in a comment header or a README sentence, not in a slot. |
| `input dataset` | string | `cohort2_normalised.csv` | `llm_supported` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. Read from a load call or a documented path; a path string alone is not evidence the file it names is the corpus's. |

**Recognition**

| | |
|---|---|
| deterministic (pattern **plus** corroborating context) | • a repository marker (deferred catalogue 05) co-occurring with a project identifier that a research artifact in the same corpus also carries<br>• a source file whose imports name scientific or statistical libraries co-occurring with a dataset filename the corpus already holds<br>• a script whose comment header names a figure or table label that a manuscript in the corpus also carries |
| needs the LLM | • deciding whether a script belongs to the paper or to the general-purpose toolkit it imports<br>• reading a README to separate an analysis pipeline from a released package |
| never alone | • a bare .py or .R file<br>• a bare repository directory name<br>• a library import alone<br>• a bare directory name matching a project acronym (§4.9: “one high-frequency entity acts as the only bridge”) |

**Work types**: `analysis script`, `data-cleaning script`, `pipeline definition`, `makefile or workflow file`, `utility module`, `configuration file`, `environment file`, `script-generated log`

**Grouping reasons**: one analysis across its scripts; one project across its analysis code; one figure and the script that draws it

**Template**: `project → analysis step → artifact type`

> §5.4: “a Research template may define project → stage → artifact type” with the artifact type kept last; the analysis step is the child §5.4's `stage` becomes for code.

**Collides with**

| domain | discriminating signal | design cite |
|---|---|---|
| `res.software-release` | a research script is not a released package; only the release carries a version tag and a citation file | §3.11: “Code files may use project, repository, programming language, and artifact type.” |
| `res.computational-notebook` | a notebook is code plus narrative plus output in one file, and its schema needs an execution date that a script does not | §2.9: “notebook cell types, package manifests, schema keys, repository markers, and project-root signals” |
| `res.reproducibility-package` | the package contains the code; the code is not the package | — |
| `code.project` | §3.11 gives Code its own row, so the same repository legitimately activates both schemas at once | §3.11: “An academic abstract submitted as part of a university application can retain project = PVA/RDP and document type = abstract while also carrying purpose = university application and target university = UChicago.” |

**Sensitivity**: `none` — No `potentially sensitive` content is intrinsic to this domain. A handling class is P7's (§8.4) and is not set here.

**Open question (Joseph's call, unresolved)**

> §5.1 offers both a `Research` and a `Code and Projects` top-level branch, and a paper's analysis script is honestly both. §4.9 permits both memberships — “A file may validly belong to more than one accepted group” — but the frozen tree gives it one physical home. Which parent wins?

---

### 12. `res.computational-notebook` — Computational notebooks

> Executable documents that carry code, narrative and output together.

**provenance**: `inference` — Extends §3.11's Code row (§3.11: “Code files may use project, repository, programming language, and artifact type.”) using the notebook structure §2.9 already requires extractors to yield: §2.9: “notebook cell types, package manifests, schema keys, repository markers, and project-root signals”

**Schema** — the fields this domain, and only this domain, legitimises.

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `project` | string | `PVA/RDP` | `validated` | **§3.11 literal.**  |
| `notebook kernel` | string | `R 4.4` | `direct` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. §2.9: “notebook cell types, package manifests, schema keys, repository markers, and project-root signals” — the kernel is declared in the notebook's own metadata, a labelled slot. |
| `analysis step` | string | `cohort 2 normalisation` | `llm_supported` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. Stated in a markdown cell, which is prose. |
| `execution date` | date | `2026-03-02` | `direct` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. From execution metadata only. A notebook's saved outputs and its code can be from different days, which is precisely why this field exists here and not in res.analysis-code. |
| `input dataset` | string | `cohort2_raw.csv` | `llm_supported` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. Read from a load cell. |
| `output figure` | string | `Figure 3` | `llm_supported` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. Which figure a notebook draws is stated in a caption cell; it is the link to res.figure-and-source. |

**Recognition**

| | |
|---|---|
| deterministic (pattern **plus** corroborating context) | • an .ipynb whose cell metadata declares a kernel (§2.9: “notebook cell types, package manifests, schema keys, repository markers, and project-root signals”) co-occurring with a project identifier in a markdown cell or the filename<br>• an .Rmd or .qmd YAML header whose `title` matches a manuscript title the corpus already holds<br>• a notebook whose markdown cells carry a figure or table label a manuscript in the corpus also carries |
| needs the LLM | • deciding whether a notebook is analysis, a tutorial, or scratch exploration<br>• matching an exported HTML report back to the notebook that produced it |
| never alone | • a bare .ipynb<br>• a bare kernel name<br>• a checkpoint file alone |

**Work types**: `Jupyter notebook`, `R Markdown or Quarto document`, `exported HTML or PDF report`, `executed copy with outputs`, `stripped copy without outputs`, `checkpoint`, `notebook-generated figure`

**Grouping reasons**: one analysis across its notebooks; one notebook and its exported report; one project across its notebooks

**Template**: `project → analysis step → artifact type`

> Same order as res.analysis-code deliberately — a notebook is analysis code with a different container, and splitting the order would scatter one analysis across two shapes.

**Collides with**

| domain | discriminating signal | design cite |
|---|---|---|
| `res.analysis-code` | the same analysis in two containers; only the notebook carries a kernel and an execution date | §2.9: “notebook cell types, package manifests, schema keys, repository markers, and project-root signals” |
| `res.statistical-output` | an executed notebook contains its output; the standalone output file is a different artifact | — |
| `res.reproducibility-package` | a package's run-all notebook is both | — |
| `acad.course-enrollment` | a course assignment notebook carries a course code with academic context and is not research | §3.5: ''BUSIB 4300 becomes a course fact only when the engine finds a course-code pattern together with academic context such as “syllabus,” “lecture,” “credits,” “instructor,” or “semester.”'' |

**Sensitivity**: `none` — No `potentially sensitive` content is intrinsic to this domain. A handling class is P7's (§8.4) and is not set here.

---

### 13. `res.statistical-output` — Statistical output and results tables

> What an analysis emitted: model summaries, logs, estimate tables and diagnostics.

**provenance**: `proposal` — The design names statistical output nowhere. Authored because output has a model specification and a software provenance that neither the code nor the dataset carries.

**Schema** — the fields this domain, and only this domain, legitimises.

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `project` | string | `PVA/RDP` | `validated` | **§3.11 literal.**  |
| `analysis step` | string | `primary outcome model` | `llm_supported` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. Named in the output's own header line or the script that wrote it. |
| `model specification` | string | `mixed-effects, random intercept by site` | `llm_supported` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. A model is described in prose or in a formula line; it is the fact that makes one estimates table distinguishable from another. |
| `software` | string | `Stata 18` | `direct` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. From the package's own banner line, which is a labelled slot — distinct from the producer/creator metadata P6's discount rule suppresses, because the banner is content, not file metadata. |
| `output type` | string | `regression table` | `validated` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. Estimates table, log, diagnostic set and power analysis are recognisable from structure. |
| `input dataset` | string | `cohort2_analysis.dta` | `llm_supported` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. Named in a use or load line. |

**Recognition**

| | |
|---|---|
| deterministic (pattern **plus** corroborating context) | • a log or text file whose content carries a statistical-package banner ('Stata/MP', 'R version', 'The SAS System') co-occurring with a project identifier or a dataset filename the corpus holds<br>• a table whose header row carries estimate vocabulary ('estimate', 'std. error', 'coef.', 'CI', 'p value') co-occurring with a study identifier<br>• a file written by an analysis script the corpus already holds, whose stem matches that script's declared output |
| needs the LLM | • telling a final results table from an intermediate one<br>• reading an output header to recover which model specification produced it |
| never alone | • a bare 'output.log'<br>• a bare p-value string<br>• a bare table of numbers<br>• a bare four-digit number (§3.10: “The product must not use fuzzy date parsing because file names and documents frequently contain numbers that look like years but are course identifiers, version numbers, build numbers, ZIP codes, or other unrelated values.”) |

**Work types**: `estimates table`, `model summary`, `analysis log`, `diagnostic plot set`, `power analysis`, `sensitivity analysis output`, `exported results table`, `session info`

**Grouping reasons**: one model across its output files; one analysis step across its runs; one manuscript's results across the outputs behind them

**Template**: `project → analysis step → output type`

> Analysis step before output type: 'regression table' names nothing until the analysis is known (§5.5: “a parent dimension should provide the context required to understand the child. A work type such as Homework 3 is meaningful only after the course is known”).

**Collides with**

| domain | discriminating signal | design cite |
|---|---|---|
| `res.analysis-code` | the code produced it; the output is not the code | — |
| `res.figure-and-source` | a diagnostic plot is output, a publication figure is a manuscript component, and the file formats are identical | — |
| `res.dataset` | an estimates table is a table and is not data | — |
| `res.manuscript-preparation` | a results table pasted into a manuscript is a manuscript component; the standalone output is not | §4.8: “an application packet does not silently absorb a document with a conflicting target institution” |

**Sensitivity**: `none` — No `potentially sensitive` content is intrinsic to this domain. A handling class is P7's (§8.4) and is not set here.

---

### 14. `res.lab-notebook` — Lab notebooks and experiment records

> The dated record of what was actually done at the bench, page by page or entry by entry.

**provenance**: `inference` — Narrows the design-named launch domain to its record. §3.15: “academic coursework, college applications, research and lab work, career and recruiting, photos and captures, and code projects” names lab work as one launch domain and §3.11: “Research files may use project, stage, artifact type, lab, and venue.” gives Research the `lab` field; the notebook artifact itself is this catalogue's extension of that named domain.

**Schema** — the fields this domain, and only this domain, legitimises.

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `lab` | string | `Chen Lab` | `validated` | **§3.11 literal.** The notebook belongs to a lab, which is why §3.11's `lab` field is a real dimension here and metadata almost everywhere else. |
| `project` | string | `PVA/RDP` | `validated` | **§3.11 literal.**  |
| `experiment id` | string | `EXP-2026-014` | `validated` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. The entry's own handle, and the thing that links a page to its instrument runs and samples. |
| `entry date` | date | `2026-03-04` | `direct` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. From the entry's own dated header. A lab notebook is a chronological instrument by construction — see the open question. |
| `protocol reference` | string | `SOP-CELL-07 v3` | `validated` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. Which protocol the entry followed. It is the join to res.protocol-sop and the reason a notebook entry is reproducible at all. |
| `witness signature` | string | `Countersigned R.O. 2026-03-05` | `direct` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. From a labelled countersignature slot. It exists because a countersigned notebook is the evidentiary artifact in a patent dispute — see the collision with res.patent-disclosure. |

**Recognition**

| | |
|---|---|
| deterministic (pattern **plus** corroborating context) | • an experiment-id token co-occurring with bench context such as 'protocol', 'reagent', 'incubated', 'aliquot', 'buffer', or 'observed' — the same shape as §3.5: ''BUSIB 4300 becomes a course fact only when the engine finds a course-code pattern together with academic context such as “syllabus,” “lecture,” “credits,” “instructor,” or “semester.”''<br>• a scanned page whose OCR text (§2.7) carries a dated header line together with an experiment-id token and a protocol reference<br>• an electronic-notebook export whose per-entry structure carries a date, an experiment id and an author in labelled slots<br>• `project` is §3.11's inherited Research field: it is recognised by res.research-project's rule — a project identifier token co-occurring with research context — and is not re-derived per domain; this entry's own anchors supply the corroboration |
| needs the LLM | • reading a handwritten page to recover which experiment it records<br>• deciding whether a dated page is a notebook entry, a meeting note or a to-do list |
| never alone | • a bare date<br>• a bare experiment number<br>• a scanned image with no legible date or experiment id<br>• a bare reagent or chemical name |

**Work types**: `notebook entry`, `scanned notebook page`, `ELN export`, `daily log`, `experiment plan`, `result note`, `cross-reference index`, `countersignature page`, `notebook archive PDF`

**Grouping reasons**: one experiment across its entries; one lab notebook volume; one project across its bench work

**Template**: `project → experiment → entry date`

> Stated as project-first to match §5.4, but this is the domain where §5.5: “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders. Photos and capture-based media are the major exception: time often belongs first because capture date is a defining aspect of the material.” is genuinely contested — see the open question.

**Collides with**

| domain | discriminating signal | design cite |
|---|---|---|
| `acad.course-enrollment` | a course lab report and a notebook page are the same object in two lives; only the report carries a course code with academic context | §3.5: ''BUSIB 4300 becomes a course fact only when the engine finds a course-code pattern together with academic context such as “syllabus,” “lecture,” “credits,” “instructor,” or “semester.”'' |
| `res.protocol-sop` | the notebook records one execution; the protocol is the reusable instruction | — |
| `res.instrument-output` | the entry references the run; the run's raw file is not the entry | — |
| `res.field-work` | a field notebook is the same artifact away from the bench, with a site instead of a lab | — |
| `res.patent-disclosure` | a countersigned notebook page is evidence in a filing and inherits the filing's confidentiality | — |

**Sensitivity**: `none` — No `potentially sensitive` content is intrinsic to this domain. A handling class is P7's (§8.4) and is not set here.

**Open question (Joseph's call, unresolved)**

> A lab notebook is chronological by law and by habit, which puts it against §5.5's rule that “For document and record domains, project, function, or subject usually comes before time”. Does the notebook branch date-first, matching how it is legally maintained, or project-first, matching every other research branch?

---

### 15. `res.protocol-sop` — Experimental protocols and standard operating procedures

> The reusable instructions a bench or field procedure follows, and their versions.

**provenance**: `design` — §4.2: “For a research group, it might be a manuscript, abstract, or protocol with a known project identifier.” — 'protocol' is one of the three artifacts the design names as a research-group seed. 'SOP' is this catalogue's extension of that named class.

**Schema** — the fields this domain, and only this domain, legitimises.

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `protocol title` | string | `Live-cell photoactivation imaging` | `direct` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. §3.13's 'document title'. |
| `protocol version` | string | `v3` | `validated` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. A protocol is only safe to follow at a stated version; running an old version is a deviation. Only asserted when a version or effective-date line corroborates it. |
| `lab` | string | `Chen Lab` | `validated` | **§3.11 literal.**  |
| `approving body` | string | `IACUC 2026-0088` | `validated` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. Which committee cleared the procedure, where one did. It is the join to res.irb-ethics and is absent for most bench SOPs. |
| `effective date` | date | `2026-01-15` | `direct` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. From a labelled effective-date or revision slot (§3.10: “The product must not use fuzzy date parsing because file names and documents frequently contain numbers that look like years but are course identifiers, version numbers, build numbers, ZIP codes, or other unrelated values.”). |
| `equipment and reagents` | string | `NovaSeq 6000; Hoechst 33342` | `llm_supported` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. Listed in prose or a materials table; extracting it is language work. |
| `project` | string | `PVA/RDP` | `validated` | **§3.11 literal.** Often absent: a good SOP outlives the project that wrote it. |

**Recognition**

| | |
|---|---|
| deterministic (pattern **plus** corroborating context) | • a numbered-step structure co-occurring with procedural imperatives ('add', 'incubate', 'centrifuge', 'store at', 'repeat') and a version or effective-date line<br>• a `cid-doi` hit (planning/deferred-catalogues/06-citation-identifier-patterns.json) in the title zone co-occurring with the word 'protocol' in the same heading<br>• a materials-and-methods block co-occurring with a protocol title that a lab-notebook entry in the corpus already references<br>• an approving-body identifier on the protocol's own cover page co-occurring with an approval or effective-date line<br>• `project` is §3.11's inherited Research field: it is recognised by res.research-project's rule — a project identifier token co-occurring with research context — and is not re-derived per domain; this entry's own anchors supply the corroboration |
| needs the LLM | • telling a bench SOP from a methods section extracted out of a manuscript<br>• deciding whether an undated procedure is current or superseded |
| never alone | • the word 'protocol' — it is equally a clinical trial protocol, a network protocol, a study protocol and a meeting protocol<br>• a bare reagent or chemical name<br>• a bare version token such as 'v2'<br>• a numbered list alone |

**Work types**: `protocol`, `standard operating procedure`, `methods section draft`, `protocols.io export`, `bench checklist`, `risk assessment`, `training record`, `protocol amendment`, `equipment operating instructions`

**Grouping reasons**: one protocol across its versions; one lab across its SOPs; one protocol and the notebook entries that ran it

**Template**: `lab → protocol → version`

> Lab before protocol because an SOP belongs to the lab that maintains it, not to a project (§5.5: “a parent dimension should provide the context required to understand the child. A work type such as Homework 3 is meaningful only after the course is known”). This is the one research template where `project` is deliberately not the root.

**Collides with**

| domain | discriminating signal | design cite |
|---|---|---|
| `res.clinical-trial` | a trial protocol is a regulatory document, not a bench SOP; only the trial protocol carries a registration id and a sponsor | — |
| `res.irb-ethics` | the approved protocol attached to an ethics application is the same file under a different custodian | — |
| `res.lab-notebook` | the protocol instructs; the notebook records one execution | — |
| `res.manuscript-preparation` | a methods section and an SOP share their whole text; only the SOP carries a version and an effective date | §4.8: “an application packet does not silently absorb a document with a conflicting target institution” |
| `res.field-work` | a field protocol carries a site and a permit that a bench SOP does not | — |

**Sensitivity**: `none` — No `potentially sensitive` content is intrinsic to this domain. A handling class is P7's (§8.4) and is not set here.

---

### 16. `res.instrument-output` — Instrument runs and raw acquisition output

> What a machine wrote, in the machine's own format, before anything was made of it.

**provenance**: `proposal` — The design names instrument output nowhere. Authored because acquisition has a run identity and vendor formats that §3.11's Research row cannot express, and because §2.9: “unsupported proprietary formats should be recorded as indexed-but-unreadable rather than silently treated as empty” already anticipates formats nothing can read.

**Schema** — the fields this domain, and only this domain, legitimises.

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `instrument` | string | `Zeiss LSM 980` | `validated` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. Model identity from a vendor metadata slot or a run manifest. Shared with res.dataset and res.facility-booking. |
| `run id` | string | `RUN-20260304-002` | `direct` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. From the acquisition software's own labelled field. |
| `acquisition date` | date | `2026-03-04` | `direct` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. From acquisition metadata. This is the one research domain where the date is intrinsic to the artifact rather than descriptive of it. |
| `sample id` | string | `PVA-C2-014` | `validated` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. What was on the stage. The join to res.sample-specimen. |
| `acquisition parameters` | string | `63x/1.4 oil, 405/488 nm` | `direct` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. From the vendor metadata block, a labelled slot. It is the field that makes a run re-interpretable years later. |
| `facility` | string | `Imaging Core` | `validated` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. Where the run happened; the join to res.facility-booking and to recharge records. |
| `operator` | string | `J. Chen` | `direct` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. §3.8 role field, never a destination dimension. |

**Recognition**

| | |
|---|---|
| deterministic (pattern **plus** corroborating context) | • a vendor-specific extension or file signature (§2.9: “inspect the real MIME type or file signature where possible”) co-occurring with a run-id token and an acquisition timestamp in the file's own metadata or a sibling manifest<br>• a labelled instrument-model metadata slot co-occurring with a sample id the corpus already holds<br>• a run directory whose manifest names an instrument together with an acquisition date and a sample list<br>• a facility name in a labelled run-manifest field or on a facility letterhead, co-occurring with an instrument model |
| needs the LLM | • deciding what an unreadable proprietary blob is when only its neighbours carry evidence<br>• telling a real acquisition from a calibration or test run |
| never alone | • a bare binary with an unknown extension — §2.9: “unsupported proprietary formats should be recorded as indexed-but-unreadable rather than silently treated as empty”<br>• a bare run number<br>• a bare timestamp<br>• the absence of EXIF (§2.6: “the system must not mistake the absence of EXIF for proof that an image is a screenshot”) |

**Work types**: `raw acquisition file`, `instrument log`, `run manifest`, `calibration record`, `QC report`, `vendor-format export`, `imaging series`, `sequencing run folder`, `spectra`

**Grouping reasons**: one run across its files; one instrument across a session's runs; one sample across the runs that measured it

**Template**: `instrument → acquisition date → run`  (time first)

> The capture-based exception: §5.5: “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders. Photos and capture-based media are the major exception: time often belongs first because capture date is a defining aspect of the material.” A run is defined by when it happened, the way a photo event is.

**Collides with**

| domain | discriminating signal | design cite |
|---|---|---|
| `res.dataset` | raw output is not yet a dataset; only the dataset carries a data level and a release version | — |
| `res.sample-specimen` | the run measured the sample; the sample record is not the run | — |
| `res.facility-booking` | the booking scheduled the run; the booking is not the run | §2.9: “Calendar formats such as ICS should yield event title, start and end time, location, organizer, attendees, and recurrence metadata.” |
| `photos.event` | §3.11's Photos row claims images with capture metadata generically, and microscopy output would route there on capture date alone | §3.11: “Photos may use capture year, event, location, people, camera information, and media type.” |
| `res.field-work` | field instrument output carries a site instead of a facility | — |

**Sensitivity**: `potentially_sensitive` — §2.9's phrase `potentially sensitive`. Clinical imaging output carries patient identifiers inside the file's own headers, which travel with the file whether or not anything reads them. A handling class is P7's (§8.4) and is not set here.

**Open question (Joseph's call, unresolved)**

> Raw instrument output is often the largest and least re-readable part of a corpus, and §2.9 already permits “safe metadata-only indexing” for formats nothing can open. Does it enter the destination tree at all, or stay where the instrument wrote it and get indexed in place?

---

### 17. `res.sample-specimen` — Sample, specimen and reagent records

> The records that say what physical material exists, where it is, and what it came from.

**provenance**: `proposal` — The design names specimen records nowhere. Authored because a sample record's fields are custodial — location, lineage, chain of custody — and none of §3.11's rows can hold them.

**Schema** — the fields this domain, and only this domain, legitimises.

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `sample id` | string | `PVA-C2-014-A3` | `validated` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. The physical item's handle. Aliquots extend it, which is why lineage is its own field. |
| `specimen type` | string | `cryopreserved PBMC` | `llm_supported` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. Stated in prose or a free-text column; there is no standard slot. |
| `collection date` | date | `2026-01-22` | `direct` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. From a labelled column (§3.10: “The product must not use fuzzy date parsing because file names and documents frequently contain numbers that look like years but are course identifiers, version numbers, build numbers, ZIP codes, or other unrelated values.”). |
| `storage location` | string | `Freezer B / Rack 3 / Box 12` | `direct` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. From a labelled column. It is the field the record exists to hold and the one that goes stale fastest. |
| `study` | string | `PVA cohort 2` | `validated` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. Which study the material belongs to; shared with res.dataset. |
| `subject code` | string | `C2-014` | `direct` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. A de-identified participant key from a labelled column. It is still a key to a person, which is why this domain is marked below. |
| `aliquot lineage` | string | `derived from PVA-C2-014` | `llm_supported` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. Parent-child relationships between physical items are described, not encoded. |

**Recognition**

| | |
|---|---|
| deterministic (pattern **plus** corroborating context) | • a sample-id token co-occurring with handling vocabulary ('freezer', 'aliquot', 'passage', 'box', 'rack', 'thawed', 'chain of custody')<br>• a spreadsheet whose header row carries specimen vocabulary ('sample id', 'collection date', 'volume', 'storage', 'condition') co-occurring with a study identifier<br>• a shipping or accession manifest naming a sample list together with a study and a receiving institution |
| needs the LLM | • telling an inventory from a results table when both are sample-keyed spreadsheets<br>• reading free text to recover an aliquot's parent |
| never alone | • a bare barcode-shaped token<br>• a bare subject code — a de-identified code is still a key to a person<br>• a bare gene, cell-line or chemical name<br>• a bare freezer or box number |

**Work types**: `sample manifest`, `freezer inventory`, `chain-of-custody form`, `accession log`, `shipping manifest`, `barcode label sheet`, `specimen-to-consent linkage record`, `reagent lot record`, `cell-line authentication certificate`

**Grouping reasons**: one study across its specimens; one specimen across its aliquots; one shipment across its manifest and receipts

**Template**: `project → study → record type`

> Study before record type, matching res.dataset, so a study's physical and digital records sit as siblings (§5.5: “a parent dimension should provide the context required to understand the child. A work type such as Homework 3 is meaningful only after the course is known”).

**Collides with**

| domain | discriminating signal | design cite |
|---|---|---|
| `res.dataset` | the manifest is a table about material; the dataset is a table of measurements | — |
| `res.human-subjects-consent` | a specimen-to-consent linkage file is the re-identification key and is the most sensitive object in either domain | §4.9: “Rare but sensitive files such as passports, visas, and legal documents may be surfaced as protected records even when they do not meet a normal group-size threshold.” |
| `res.instrument-output` | the run measured the sample | — |
| `res.clinical-trial` | trial specimens carry a registration id and a site that research specimens do not | — |

**Sensitivity**: `potentially_sensitive` — §2.9's phrase `potentially sensitive`. Specimen records carry subject codes, and a linkage record maps those codes back to identifiable people. A handling class is P7's (§8.4) and is not set here.

---

### 18. `res.grant-proposal` — Grant proposals and funding applications

> Everything assembled to ask a funder for money, up to the submission.

**provenance**: `proposal` — The design names grants nowhere; §5.7's template-library list names 'research workflows' and “financial records” separately and neither covers this. Authored because funder, award number and period are fields no §3.11 row holds.

**Schema** — the fields this domain, and only this domain, legitimises.

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `funder` | string | `NIH / NIGMS` | `validated` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. The body being asked. It is the root of the whole branch and the one value that is stable across a decade of resubmissions. |
| `opportunity number` | string | `PA-24-247` | `validated` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. The funder's call identifier — distinct from the award number, which only exists after success. |
| `programme` | string | `R01` | `validated` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. The scheme applied to; it determines the entire document set. |
| `period` | string | `2027-2030` | `validated` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. The proposed period of performance, from a labelled slot. Not a date fact: it is a span the funder defines (§3.10: “The product must not use fuzzy date parsing because file names and documents frequently contain numbers that look like years but are course identifiers, version numbers, build numbers, ZIP codes, or other unrelated values.”). |
| `proposal stage` | string | `full proposal` | `validated` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. Letter of intent, full proposal, resubmission and just-in-time are different document sets under one identity. |
| `host institution` | string | `Columbia University` | `validated` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. The applicant institution — §3.8's role split: this is not the funder and not the collaborator. |
| `principal investigator` | string | `J. Chen` | `direct` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. §3.8 role field, never a destination dimension. |
| `submission deadline` | date | `2026-10-05` | `direct` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. From a labelled slot in the call. |

**Recognition**

| | |
|---|---|
| deterministic (pattern **plus** corroborating context) | • a funder opportunity-number token co-occurring with proposal context ('specific aims', 'budget justification', 'period of performance', 'principal investigator', 'facilities and resources')<br>• an existing user-created folder whose name carries a funder acronym together with a period, whose members include a budget and a narrative (§3.9: “Purpose may be supported strongly by an existing user-created folder name or explicit language in a form or portal.”)<br>• a funder-template document whose section headings match the call the corpus already holds<br>• a programme or scheme token ('R01', 'Consolidator Grant', 'Standard Grant') co-occurring with the funder's opportunity number<br>• an applicant-institution name in a labelled applicant-organisation field, distinct from the funder's own name (§3.8: “authored_by and target_school, or our_firm and client”) |
| needs the LLM | • telling a resubmission from a fresh application when neither states it<br>• reading a narrative to establish which of several projects it proposes |
| never alone | • a bare funder acronym<br>• a bare four-digit year range (§3.10: “The product must not use fuzzy date parsing because file names and documents frequently contain numbers that look like years but are course identifiers, version numbers, build numbers, ZIP codes, or other unrelated values.”)<br>• the word 'proposal'<br>• a bare institution name (§4.9: “A university name alone should not create a group because Columbia can appear as an authoring school, course provider, target institution, employer, research venue, or merely a cited organization.”) |

**Work types**: `project narrative`, `specific aims`, `budget and justification`, `biosketch`, `facilities and resources statement`, `letters of support`, `data management plan`, `submission confirmation`, `reviewer summary statement`, `just-in-time materials`

**Grouping reasons**: one call across the documents submitted to it; one funder across the user's proposals; one proposal across its resubmissions

**Template**: `funder → programme → period`

> Funder first because it is the only value that survives a rejection; §5.4's project-first order does not fit an artifact whose identity is external (§5.5: “a parent dimension should provide the context required to understand the child. A work type such as Homework 3 is meaningful only after the course is known”).

**Collides with**

| domain | discriminating signal | design cite |
|---|---|---|
| `app.application-packet` | a grant proposal and a graduate-admissions packet are both purpose-defined application packets; only the grant carries a funder and an opportunity number, and neither packet may absorb the other's documents | §4.8: “an application packet does not silently absorb a document with a conflicting target institution” |
| `res.grant-reporting` | the proposal asks; the report accounts. They share an award number only after success | — |
| `fin.records` | §3.11 gives Finance its own row and a budget is honestly financial; the narrative is not | §3.11: “Finance files may use institution, account type, tax year, and record type.” |
| `res.data-management-plan` | the DMP is a proposal component and a standalone compliance artifact at once | §3.11: “An academic abstract submitted as part of a university application can retain project = PVA/RDP and document type = abstract while also carrying purpose = university application and target university = UChicago.” |
| `res.research-agreement` | subaward paperwork sits in both | — |

**Sensitivity**: `potentially_sensitive` — §2.9's phrase `potentially sensitive`. A proposal packet carries biosketches, named personnel and salary lines for identifiable people. A handling class is P7's (§8.4) and is not set here.

**Open question (Joseph's call, unresolved)**

> §5.1 offers both a `Research` and a `Finance and Administration` top-level branch and a grant is honestly both — the narrative is research, the budget and award notice are administration. Does the grant branch split across two roots, or does one side live as a cross-reference?

---

### 19. `res.grant-reporting` — Grant reporting and post-award compliance

> What a funder requires after the money starts: progress, spending, publications and change requests.

**provenance**: `proposal` — The design names post-award reporting nowhere. Authored because it is keyed on an award number and a reporting period, neither of which exists before an award.

**Schema** — the fields this domain, and only this domain, legitimises.

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `funder` | string | `NIH / NIGMS` | `validated` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. Shared with res.grant-proposal. |
| `award number` | string | `R01GM123456` | `validated` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. Exists only after success, which is exactly what separates this domain from the proposal one. |
| `reporting period` | string | `2028-04-01 to 2029-03-31` | `validated` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. From a labelled budget-period or reporting-period slot. |
| `report type` | string | `annual progress report` | `validated` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. Progress, financial, final and closeout reports have different recipients and different retention. |
| `compliance requirement` | string | `public access deposit within twelve months` | `llm_supported` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. Requirements are stated in prose in award terms; extracting one is language work. |
| `personnel effort` | string | `2.4 calendar months, J. Chen` | `direct` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. From a labelled effort column. §3.8 role data; never a destination dimension. |

**Recognition**

| | |
|---|---|
| deterministic (pattern **plus** corroborating context) | • an award-number token co-occurring with reporting context ('reporting period', 'progress report', 'budget period', 'no-cost extension', 'closeout')<br>• a labelled 'Award Number' or 'Grant Number' form field co-occurring with a period range<br>• a funder portal export whose headings match a report type and whose award number the corpus already holds |
| needs the LLM | • separating a progress narrative from the proposal narrative it reuses verbatim<br>• reading award terms to identify which compliance obligation a document answers |
| never alone | • a bare award-shaped token<br>• a bare reporting-period range (§3.10: “The product must not use fuzzy date parsing because file names and documents frequently contain numbers that look like years but are course identifiers, version numbers, build numbers, ZIP codes, or other unrelated values.”)<br>• the word 'report' |

**Work types**: `annual progress report`, `final report`, `financial report`, `no-cost extension request`, `publication and public-access reporting`, `change of PI or scope notice`, `audit response`, `closeout package`, `award notice`

**Grouping reasons**: one award across its reporting periods; one funder across the user's awards; one reporting period across its documents

**Template**: `funder → award → reporting period`

> Award before period: a period names nothing until the award is known (§5.5: “a parent dimension should provide the context required to understand the child. A work type such as Homework 3 is meaningful only after the course is known”).

**Collides with**

| domain | discriminating signal | design cite |
|---|---|---|
| `res.grant-proposal` | proposal narratives are reused verbatim in progress reports; only the report carries an award number and a reporting period | §4.8: “an application packet does not silently absorb a document with a conflicting target institution” |
| `fin.records` | financial reports are financial records with a research purpose | §3.11: “Finance files may use institution, account type, tax year, and record type.” |
| `res.repository-deposit` | public-access compliance is discharged by a deposit, so one deposit receipt serves both domains | §3.11: “An academic abstract submitted as part of a university application can retain project = PVA/RDP and document type = abstract while also carrying purpose = university application and target university = UChicago.” |
| `res.published-article` | publication reporting lists the outputs but is not one | — |

**Sensitivity**: `potentially_sensitive` — §2.9's phrase `potentially sensitive`. Effort reports name individuals and their salary-bearing time, and participant-demographic reporting names cohorts. A handling class is P7's (§8.4) and is not set here.

---

### 20. `res.irb-ethics` — Ethics, IRB and IACUC approvals

> The regulatory approval file for research involving people or animals.

**provenance**: `proposal` — The design names ethics review nowhere. §3.15 names “identity, medical, and legal” as safety domains and this material behaves like all three — see the open question.

**Schema** — the fields this domain, and only this domain, legitimises.

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `protocol number` | string | `IRB-2026-0412` | `validated` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. The committee's handle. Every document in the file carries it, which makes it the group's anchor in §4.2's sense. |
| `review body` | string | `IACUC` | `validated` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. IRB, IACUC, IBC and external ethics committees have different scopes and different documents. |
| `review type` | string | `expedited` | `validated` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. Exempt, expedited and full-board determine what else must exist. |
| `approval date` | date | `2026-02-11` | `direct` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. From a labelled approval slot. |
| `expiry date` | date | `2027-02-10` | `direct` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. From a labelled slot. An expired approval is the single most consequential stale fact in a research corpus. |
| `amendment number` | string | `Amendment 3` | `validated` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. Approvals accrete amendments; each is a version of the approved protocol. |
| `study` | string | `PVA cohort 2` | `validated` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. The join to res.dataset and res.human-subjects-consent. |

**Recognition**

| | |
|---|---|
| deterministic (pattern **plus** corroborating context) | • a protocol-number token co-occurring with review-body vocabulary ('Institutional Review Board', 'IRB', 'IACUC', 'ethics committee', 'approved', 'continuing review', 'determination')<br>• a letterhead OCR region (§2.7) naming a review body co-occurring with an approval or expiry date line<br>• an amendment document whose protocol number matches an approval already in the corpus<br>• a study title or identifier in an approval letter's labelled subject line, matching a study the corpus already holds |
| needs the LLM | • telling an exemption determination from an approval<br>• reading a determination letter to recover which study it covers when the title differs from the corpus's |
| never alone | • a bare 'IRB' string<br>• a bare protocol-shaped number<br>• a bare approval date<br>• the word 'ethics' |

**Work types**: `protocol submission`, `approval letter`, `amendment`, `continuing review`, `adverse event report`, `protocol deviation`, `closure notice`, `human-subjects training certificate`, `determination of exemption`

**Grouping reasons**: one protocol across its approvals and amendments; one study across its regulatory file; one review body across the user's protocols

**Template**: `study → review body → protocol`

> Study first so a study's regulatory file sits beside its data and its consent materials (§5.5: “a parent dimension should provide the context required to understand the child. A work type such as Homework 3 is meaningful only after the course is known”).

**Collides with**

| domain | discriminating signal | design cite |
|---|---|---|
| `res.clinical-trial` | a trial has both an ethics file and a regulatory file, and the protocol documents overlap almost completely | — |
| `res.human-subjects-consent` | consent forms are approved *by* the IRB and live in both files | §3.11: “An academic abstract submitted as part of a university application can retain project = PVA/RDP and document type = abstract while also carrying purpose = university application and target university = UChicago.” |
| `res.protocol-sop` | the approved protocol and the bench SOP describe the same procedure to different readers | — |
| `legal.records` | §3.15 makes legal material a safety domain; an approval letter is a compliance record | §3.15: “Finance, identity, medical, and legal material should be implemented first as safety domains, meaning the system detects and protects them before any cloud or automated placement decision is allowed.” |

**Sensitivity**: `potentially_sensitive` — §2.9's phrase `potentially sensitive`. An ethics file carries the participant-facing protocol, investigator personal data and adverse-event narratives. A handling class is P7's (§8.4) and is not set here.

**Open question (Joseph's call, unresolved)**

> §3.15 makes “Finance, identity, medical, and legal material” safety domains, “meaning the system detects and protects them before any cloud or automated placement decision is allowed”. Human-subjects and animal-ethics material is none of those four by name and behaves like all of them. Is it a safety domain, and does §3.15's list need its name?

---

### 21. `res.human-subjects-consent` — Consent and participant-facing materials

> What participants were shown and what they signed.

**provenance**: `proposal` — The design names consent materials nowhere. Authored because a blank form and an executed one are the same document class with opposite privacy properties — see the open question.

**Schema** — the fields this domain, and only this domain, legitimises.

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `study` | string | `PVA cohort 2` | `validated` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. The join to res.irb-ethics and res.dataset. |
| `consent version` | string | `v4 2026-02-11` | `validated` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. Only the IRB-approved version may be used; the version is the compliance fact. |
| `consent type` | string | `re-consent` | `validated` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. Consent, assent, broad consent, re-consent and HIPAA authorization are different instruments. |
| `irb protocol number` | string | `IRB-2026-0412` | `validated` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. Carried on the approved form's footer; the join to res.irb-ethics. |
| `language version` | string | `Simplified Chinese` | `direct` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. §3.11's universal `language` fact says what a file is written in; this field says which approved translation it is, which is a different claim. |
| `participant code` | string | `C2-014` | `direct` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. Present on executed forms only. It is the field that flips the whole record's character. |
| `signature date` | date | `2026-03-01` | `direct` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. From the signature block. |

**Recognition**

| | |
|---|---|
| deterministic (pattern **plus** corroborating context) | • consent vocabulary ('informed consent', 'voluntary participation', 'you may withdraw at any time', 'principal investigator', 'risks and benefits') co-occurring with an IRB protocol number or a study identifier<br>• a signature-block layout co-occurring with the same consent version token as a blank form already in the corpus<br>• an IRB-stamped footer carrying an approval date and a version, on a participant-facing document |
| needs the LLM | • telling a blank template from an executed copy when the signature is an image with no OCR text<br>• matching a translation to the approved source version |
| never alone | • the word 'consent'<br>• a bare signature image<br>• a bare participant code<br>• a bare study name |

**Work types**: `blank consent form`, `executed consent form`, `assent form`, `participant information sheet`, `approved translation`, `withdrawal record`, `consent log`, `HIPAA authorization`, `recruitment material`

**Grouping reasons**: one study across its consent versions; one approved version across its translations; one consent log and the forms it indexes

**Template**: `study → consent version → consent type`

> Study first, matching res.irb-ethics, so the approval and the instrument it approved sit together (§5.5: “a parent dimension should provide the context required to understand the child. A work type such as Homework 3 is meaningful only after the course is known”).

**Collides with**

| domain | discriminating signal | design cite |
|---|---|---|
| `res.irb-ethics` | the form is an attachment to the approval and lives in both files | §3.11: “An academic abstract submitted as part of a university application can retain project = PVA/RDP and document type = abstract while also carrying purpose = university application and target university = UChicago.” |
| `identity.records` | §3.15 makes identity a safety domain; an executed form carries a real person's name and signature | §3.15: “Finance, identity, medical, and legal material should be implemented first as safety domains, meaning the system detects and protects them before any cloud or automated placement decision is allowed.” |
| `res.sample-specimen` | a specimen-to-consent linkage record joins the two and is the re-identification key | §4.9: “Rare but sensitive files such as passports, visas, and legal documents may be surfaced as protected records even when they do not meet a normal group-size threshold.” |
| `res.survey-instrument` | an online survey's consent page is part of the instrument file | — |

**Sensitivity**: `potentially_sensitive` — §2.9's phrase `potentially sensitive`. An executed form carries an identifiable participant's name, signature and study membership. A handling class is P7's (§8.4) and is not set here.

**Open question (Joseph's call, unresolved)**

> A blank consent form is a template; an executed one is a signed record about an identifiable person. They are the same document class with the same filename family. Does the domain split them, and does the executed side leave the ordinary tree the way §4.9's protected records do?

---

### 22. `res.clinical-trial` — Clinical trial documentation

> The regulated document set of an interventional or observational trial.

**provenance**: `proposal` — The design names clinical trials nowhere. §3.15 names medical material as a safety domain. Authored because registration id, sponsor, phase and site are fields no §3.11 row holds.

**Schema** — the fields this domain, and only this domain, legitimises.

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `trial registration id` | string | `NCT01234567` | `validated` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. The trial's public identity. It anchors the entire document set. |
| `sponsor` | string | `Columbia University` | `validated` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. §3.8 role split: the sponsor is not the site and not the funder, even when one organisation is all three. |
| `protocol version` | string | `v6.0 2026-04-18` | `validated` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. A trial protocol amendment changes what may lawfully be done; the version is a regulatory fact. |
| `site` | string | `Site 004 — Presbyterian` | `direct` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. Multi-site trials duplicate every document per site. |
| `phase` | string | `Phase II` | `direct` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. From a labelled slot; determines the required document set. |
| `indication` | string | `type 2 diabetes` | `llm_supported` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. Stated in prose in the protocol synopsis. |
| `monitoring visit` | string | `interim monitoring visit 2` | `direct` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. From the visit report's own labelled header. |

**Recognition**

| | |
|---|---|
| deterministic (pattern **plus** corroborating context) | • a trial-registration token co-occurring with trial context ('sponsor', 'investigator brochure', 'case report form', 'inclusion criteria', 'adverse event', 'monitoring visit')<br>• a labelled 'Protocol Number' or registry-identifier form field co-occurring with a sponsor name<br>• a trial master file index whose section names match documents already in the corpus |
| needs the LLM | • separating an observational study protocol from an interventional one<br>• reading a synopsis to recover the indication when no labelled field exists |
| never alone | • a bare registration-shaped token<br>• a bare phase word<br>• a bare indication or drug name<br>• the word 'trial' |

**Work types**: `trial protocol`, `statistical analysis plan`, `investigator brochure`, `case report form`, `monitoring report`, `safety or SAE report`, `site initiation record`, `trial master file index`, `registry record`, `informed consent set`

**Grouping reasons**: one trial across its document set; one site across a trial's site file; one protocol across its amendments

**Template**: `sponsor → trial → document type`

> Trials are organised by their own regulated file structure, not by project; the sponsor owns the trial and the trial owns everything else (§5.5: “a parent dimension should provide the context required to understand the child. A work type such as Homework 3 is meaningful only after the course is known”).

**Collides with**

| domain | discriminating signal | design cite |
|---|---|---|
| `res.irb-ethics` | a trial's ethics file and its regulatory file duplicate the protocol and the consent set | §3.11: “An academic abstract submitted as part of a university application can retain project = PVA/RDP and document type = abstract while also carrying purpose = university application and target university = UChicago.” |
| `res.protocol-sop` | 'protocol' means two different documents in the two domains | — |
| `medical.records` | §3.15 makes medical material a safety domain | §3.15: “Finance, identity, medical, and legal material should be implemented first as safety domains, meaning the system detects and protects them before any cloud or automated placement decision is allowed.” |
| `res.dataset` | trial data is a dataset with a regulated custody chain | — |
| `res.human-subjects-consent` | the consent set is part of the trial master file | — |

**Sensitivity**: `potentially_sensitive` — §2.9's phrase `potentially sensitive`. Trial documentation carries participant-level safety narratives, site staff identities and unblinding material. A handling class is P7's (§8.4) and is not set here.

---

### 23. `res.research-agreement` — Collaboration agreements, MTAs and data-use agreements

> The contracts that govern who may hold, share or use research material and data.

**provenance**: `proposal` — The design names research agreements nowhere; §3.15 names legal material as a safety domain and §5.7's library names 'legal matters' as a separate situation. Authored because the two-party role split is the whole point of the schema.

**Schema** — the fields this domain, and only this domain, legitimises.

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `counterparty institution` | string | `Broad Institute` | `validated` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. §3.8's rule applied literally: 'authored_by and target_school, or our_firm and client' — an agreement has two institutions in two roles and they must be two fields. |
| `our institution` | string | `Columbia University` | `validated` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. The other half of the §3.8 role split. |
| `agreement type` | string | `MTA` | `validated` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. MTA, DUA, CDA, subaward and authorship agreement carry different obligations. |
| `agreement reference` | string | `MTA-2026-0119` | `validated` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. The office's handle for the instrument. |
| `effective date` | date | `2026-05-01` | `direct` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. From a labelled 'Effective Date' slot. |
| `expiry date` | date | `2029-04-30` | `direct` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. From a labelled slot. An expired DUA makes continued data use a breach, which is why it is a fact and not a note. |
| `material or data described` | string | `de-identified cohort 2 genotypes` | `llm_supported` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. Described in a schedule or exhibit in prose. |

**Recognition**

| | |
|---|---|
| deterministic (pattern **plus** corroborating context) | • agreement vocabulary ('this Agreement', 'Provider', 'Recipient', 'Effective Date', 'Confidential Information', 'Term and Termination') co-occurring with two distinct institution names in distinct roles (§3.8: “authored_by and target_school, or our_firm and client”)<br>• a labelled 'Agreement Number' or 'Reference' field co-occurring with an effective-date line<br>• an executed signature page whose parties match an unexecuted draft already in the corpus |
| needs the LLM | • deciding which party is which when both institutions appear throughout<br>• telling a fully executed instrument from a circulated draft |
| never alone | • a single institution name (§4.9: “A university name alone should not create a group because Columbia can appear as an authoring school, course provider, target institution, employer, research venue, or merely a cited organization.”)<br>• the word 'agreement'<br>• a bare signature page<br>• a bare four-digit date range |

**Work types**: `material transfer agreement`, `data use agreement`, `confidentiality agreement`, `collaboration agreement`, `subaward`, `authorship agreement`, `IP side letter`, `executed signature page`, `amendment`, `transmittal email`

**Grouping reasons**: one agreement across its drafts and executed copy; one counterparty across the instruments with them; one project across the agreements enabling it

**Template**: `counterparty → agreement type → agreement`

> Counterparty first because that is how the office and the user both remember it; §3.8 forbids using an organisation as a mere collector, and a counterparty in a *role* is not a collector (§3.8: “It should avoid using authorship or creator identity as a destination dimension.”).

**Collides with**

| domain | discriminating signal | design cite |
|---|---|---|
| `legal.records` | §3.15 makes legal material a safety domain and an executed contract is legal material | §3.15: “Finance, identity, medical, and legal material should be implemented first as safety domains, meaning the system detects and protects them before any cloud or automated placement decision is allowed.” |
| `res.grant-proposal` | subaward paperwork is a proposal component and an executed instrument at once | §3.11: “An academic abstract submitted as part of a university application can retain project = PVA/RDP and document type = abstract while also carrying purpose = university application and target university = UChicago.” |
| `res.patent-disclosure` | IP terms in a collaboration agreement govern a later filing | — |
| `res.dataset` | a DUA governs a dataset without being one, and the two must not merge | §4.8: “an application packet does not silently absorb a document with a conflicting target institution” |

**Sensitivity**: `potentially_sensitive` — §2.9's phrase `potentially sensitive`. Executed instruments carry real signatures, negotiated confidential terms and named individuals. A handling class is P7's (§8.4) and is not set here.

---

### 24. `res.conference-abstract` — Conference and meeting abstracts

> Short submissions to a meeting, and what the meeting says back.

**provenance**: `inference` — Extends the design-named abstract artifact (§4.2: “For a research group, it might be a manuscript, abstract, or protocol with a known project identifier.”) to the meeting context. The design names 'abstract' as a research seed; it does not name conferences.

**Schema** — the fields this domain, and only this domain, legitimises.

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `project` | string | `PVA/RDP` | `validated` | **§3.11 literal.**  |
| `venue` | string | `ASCB Cell Bio 2026` | `validated` | **§3.11 literal.** A meeting is a venue in §3.11's sense; §4.9's 'research venue' role is the design's acknowledgement that the same name can be several things. |
| `abstract id` | string | `ABS-2026-1184` | `validated` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. The meeting's submission handle. |
| `presentation type` | string | `poster` | `validated` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. Oral, poster and late-breaking are decided by the meeting and determine what artifact follows. |
| `session or track` | string | `Organelle Dynamics II` | `validated` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. Where the work was programmed; often the only topical label a meeting produces. |
| `submission deadline` | date | `2026-06-15` | `direct` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. From a labelled slot in the call (§3.10: “The product must not use fuzzy date parsing because file names and documents frequently contain numbers that look like years but are course identifiers, version numbers, build numbers, ZIP codes, or other unrelated values.”). |
| `presenting author` | string | `J. Chen` | `direct` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. §3.8 role field, never a destination dimension. |

**Recognition**

| | |
|---|---|
| deterministic (pattern **plus** corroborating context) | • a meeting name co-occurring with abstract-submission vocabulary ('abstract', 'word limit', 'presenting author', 'session', 'accepted for presentation')<br>• an abstract-id token in a labelled slot co-occurring with a meeting name and an explicit date the same file carries (§3.10: “The product must not use fuzzy date parsing because file names and documents frequently contain numbers that look like years but are course identifiers, version numbers, build numbers, ZIP codes, or other unrelated values.”)<br>• an acceptance notice (§2.9: “Email formats such as EML, MBOX, MSG, and exported mail archives should yield sender, recipients, subject, sent date, thread identifiers, message body, attachment names, and reply-chain context”) whose sender is the meeting organiser and whose body carries the abstract id<br>• `project` is §3.11's inherited Research field: it is recognised by res.research-project's rule — a project identifier token co-occurring with research context — and is not re-derived per domain; this entry's own anchors supply the corroboration<br>• `venue` is §3.11's inherited Research field: a venue name from a validated gazetteer (§3.7, deferred) co-occurring with abstract-submission vocabulary in the same document — the meeting name is this domain's `venue` value. §4.9 is why a bare organisation name never suffices |
| needs the LLM | • deciding whether a short prose file is a conference abstract, a manuscript abstract or an application abstract<br>• recovering a meeting identity from a stripped abstract body |
| never alone | • a bare meeting acronym<br>• the word 'abstract' — §3.11's academic abstract in an application packet is a different domain<br>• a bare four-digit year (§3.10: “The product must not use fuzzy date parsing because file names and documents frequently contain numbers that look like years but are course identifiers, version numbers, build numbers, ZIP codes, or other unrelated values.”)<br>• a bare session title |

**Work types**: `abstract submission`, `abstract acceptance notice`, `camera-ready abstract`, `submission portal record`, `abstract book entry`, `late-breaking submission`, `travel award application`, `presentation scheduling notice`

**Grouping reasons**: one meeting across the user's submissions to it; one abstract across its versions and its acceptance; one project across its meeting outputs

**Template**: `project → venue → artifact type`

> §5.4: “a Research template may define project → stage → artifact type” with the meeting standing in for `stage`; project first keeps a project's meeting output beside its papers (§5.5: “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders. Photos and capture-based media are the major exception: time often belongs first because capture date is a defining aspect of the material.”).

**Collides with**

| domain | discriminating signal | design cite |
|---|---|---|
| `res.poster` | the abstract is accepted, then the poster is made; they share the abstract id | — |
| `res.talk` | the same abstract can become an oral presentation | — |
| `res.manuscript-preparation` | a manuscript abstract and a meeting abstract are near-identical text with different owners | §4.8: “an application packet does not silently absorb a document with a conflicting target institution” |
| `app.application-packet` | the design's own multi-membership case is exactly this artifact | §4.9: “a PVA/RDP abstract that is both a Research artifact and a supporting document in a UChicago application packet” |

**Sensitivity**: `none` — No `potentially sensitive` content is intrinsic to this domain. A handling class is P7's (§8.4) and is not set here.

---

### 25. `res.poster` — Conference posters

> The large-format artifact presented at a meeting, and the files it is built from.

**provenance**: `inference` — Extends §3.11's Research `artifact type` with a presentation form the design does not name. §2.9: “Design and creative formats such as PSD, AI, SVG, Figma exports, CAD files, and 3D files should at minimum yield filename, format, dimensions or canvas properties” supplies the format evidence.

**Schema** — the fields this domain, and only this domain, legitimises.

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `project` | string | `PVA/RDP` | `validated` | **§3.11 literal.**  |
| `venue` | string | `ASCB Cell Bio 2026` | `validated` | **§3.11 literal.**  |
| `presentation date` | date | `2026-12-08` | `direct` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. From the meeting programme or the poster's own footer. |
| `board or session` | string | `Board B-142` | `validated` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. The meeting's physical handle for the poster; the join back to the abstract. |
| `poster format` | string | `A0 portrait` | `direct` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. §2.9: “Design and creative formats such as PSD, AI, SVG, Figma exports, CAD files, and 3D files should at minimum yield filename, format, dimensions or canvas properties” — canvas properties are a direct observation and are what identify a poster file among ordinary decks. |
| `co-presenters` | string | `J. Chen; R. Okonkwo` | `llm_supported` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. Read from the author band. §3.8 role data; never a destination dimension. |

**Recognition**

| | |
|---|---|
| deterministic (pattern **plus** corroborating context) | • a design or presentation file (§2.9: “Design and creative formats such as PSD, AI, SVG, Figma exports, CAD files, and 3D files should at minimum yield filename, format, dimensions or canvas properties”) whose canvas properties are poster-shaped and whose text carries a meeting name together with a project identifier<br>• a filename carrying a meeting acronym together with a poster token, co-occurring with an abstract already accepted for that meeting<br>• a print-ready export whose stem matches a poster source file in the same version family<br>• `venue` is §3.11's inherited Research field: a venue name from a validated gazetteer (§3.7, deferred) co-occurring with a poster header band or a print-ready export made to the meeting's own template. §4.9 is why a bare organisation name never suffices<br>• a board or session token in a meeting programme co-occurring with an abstract id the corpus already holds |
| needs the LLM | • deciding whether a large-canvas PDF is a poster, a printed schematic or a flyer<br>• matching a poster to the abstract that got it accepted when neither states the id |
| never alone | • the word 'poster'<br>• a large-canvas PDF alone<br>• a bare meeting acronym<br>• a bare project directory (§4.9: “one high-frequency entity acts as the only bridge”) |

**Work types**: `poster source file`, `print-ready export`, `poster PDF handout`, `panel component`, `poster award certificate`, `QR-linked supplement`, `printing order`, `poster session schedule`

**Grouping reasons**: one poster across its source and exports; one meeting across the user's posters; one project across its posters

**Template**: `project → venue → artifact type`

> Same order as res.conference-abstract so a meeting's abstract and poster sit together (§5.5: “a parent dimension should provide the context required to understand the child. A work type such as Homework 3 is meaningful only after the course is known”).

**Collides with**

| domain | discriminating signal | design cite |
|---|---|---|
| `res.conference-abstract` | the abstract precedes the poster and shares its id | — |
| `res.figure-and-source` | poster panels are reused publication figures with different labels | — |
| `career.portfolio` | a poster is a research artifact and a portfolio piece; §3.3 lists “research artifact” and “recruiting document” as separate determinations | §3.3: “The LLM may determine whether an extracted document appears to be an application essay, research artifact, recruiting document, travel record, or other supported domain” |
| `res.talk` | a poster and a deck can be the same content in two formats | — |

**Sensitivity**: `none` — No `potentially sensitive` content is intrinsic to this domain. A handling class is P7's (§8.4) and is not set here.

**Open question (Joseph's call, unresolved)**

> A poster is a research artifact and a portfolio piece. §5.1 offers both a `Research` and a `Career` top-level branch and §4.9 permits both memberships — but the frozen tree gives it one physical home. Which one, and does the other get a cross-reference?

---

### 26. `res.talk` — Talks, seminars and presentation decks

> Spoken presentations of research and the material prepared for them.

**provenance**: `inference` — Extends §3.11's Research `artifact type` with a presentation form the design does not name. §2.9: “Presentations such as PPTX, PPT, ODP, and PDF slide decks should yield slide titles, text boxes, speaker notes where available” supplies the structural evidence.

**Schema** — the fields this domain, and only this domain, legitimises.

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `project` | string | `PVA/RDP` | `validated` | **§3.11 literal.**  |
| `venue` | string | `Gordon Research Conference — Photobiology` | `validated` | **§3.11 literal.**  |
| `talk title` | string | `Watching RDP switch in real time` | `direct` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. §3.13's 'document title', usually the first slide. |
| `talk type` | string | `invited seminar` | `validated` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. Invited seminar, contributed talk, job talk and lab meeting have completely different audiences and reuse patterns. |
| `presentation date` | date | `2026-07-22` | `direct` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. From the title slide or the invitation (§3.10: “The product must not use fuzzy date parsing because file names and documents frequently contain numbers that look like years but are course identifiers, version numbers, build numbers, ZIP codes, or other unrelated values.”). |
| `host institution` | string | `EMBL Heidelberg` | `validated` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. §3.8 role split: the host is not the author's institution and not the venue's owner. |

**Recognition**

| | |
|---|---|
| deterministic (pattern **plus** corroborating context) | • a presentation file (§2.9: “Presentations such as PPTX, PPT, ODP, and PDF slide decks should yield slide titles, text boxes, speaker notes where available”) whose slide titles carry a project identifier and whose first slide carries a meeting or host-institution name together with an explicit date<br>• speaker notes (§2.9: “Presentations such as PPTX, PPT, ODP, and PDF slide decks should yield slide titles, text boxes, speaker notes where available”) carrying talk vocabulary co-occurring with a project identifier<br>• an invitation email (§2.9: “Email formats such as EML, MBOX, MSG, and exported mail archives should yield sender, recipients, subject, sent date, thread identifiers, message body, attachment names, and reply-chain context”) naming a seminar series and a date, co-occurring with a deck of the same stem<br>• `venue` is §3.11's inherited Research field: a venue name from a validated gazetteer (§3.7, deferred) co-occurring with a title slide, a seminar-series announcement, or an invitation naming a date. §4.9 is why a bare organisation name never suffices |
| needs the LLM | • telling a research seminar deck from a teaching deck when neither names a course or a venue<br>• deciding whether a deck is the delivered version or a rehearsal draft |
| never alone | • a bare .pptx<br>• a bare institution name (§4.9: “A university name alone should not create a group because Columbia can appear as an authoring school, course provider, target institution, employer, research venue, or merely a cited organization.”)<br>• a title slide alone<br>• a bare date |

**Work types**: `slide deck`, `speaker notes`, `talk recording`, `invitation correspondence`, `handout`, `abstract pointer`, `travel and honorarium record`, `seminar series announcement`

**Grouping reasons**: one talk across its deck versions; one seminar series across its talks; one project across the talks presenting it

**Template**: `project → venue → artifact type`

> Same order as res.conference-abstract and res.poster so all three meeting outputs are siblings (§5.5: “a parent dimension should provide the context required to understand the child. A work type such as Homework 3 is meaningful only after the course is known”).

**Collides with**

| domain | discriminating signal | design cite |
|---|---|---|
| `acad.course-enrollment` | a lecture deck and a seminar deck are the same format; only the lecture carries a course code with academic context | §3.5: ''BUSIB 4300 becomes a course fact only when the engine finds a course-code pattern together with academic context such as “syllabus,” “lecture,” “credits,” “instructor,” or “semester.”'' |
| `res.poster` | the same content in two presentation formats | — |
| `res.conference-abstract` | an accepted abstract can become a talk instead of a poster | — |
| `career.portfolio` | a job talk is a recruiting document and a research artifact at once | §3.3: “The LLM may determine whether an extracted document appears to be an application essay, research artifact, recruiting document, travel record, or other supported domain” |

**Sensitivity**: `none` — No `potentially sensitive` content is intrinsic to this domain. A handling class is P7's (§8.4) and is not set here.

---

### 27. `res.reading-library` — Literature and reading library

> Other people's papers, kept because the user reads them.

**provenance**: `proposal` — The design names a reading library nowhere. Authored because its fields describe somebody else's work and §3.11's `project` does not apply.

**Schema** — the fields this domain, and only this domain, legitimises.

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `cited work title` | string | `Mitochondrial dynamics under hypoxia` | `direct` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. §3.13's 'document title'. |
| `cited authors` | string | `Okonkwo, R.; Larsen, M.` | `direct` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. §3.8 role field. Present because it is how people search a library, and explicitly never a destination dimension (§3.8: “It should avoid using authorship or creator identity as a destination dimension.”). |
| `publication venue` | string | `Journal of Cell Biology` | `validated` | **§3.11 literal.** §3.11's `venue` in the reading role rather than the publishing role. |
| `doi` | string | `10.1083/jcb.202301045` | `validated` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. A `cid-doi` or `cid-pmid` hit (planning/deferred-catalogues/06-citation-identifier-patterns.json) in the title or page-one zone, corroborated by publisher furniture. |
| `reading topic` | string | `organelle contact sites` | `llm_supported` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. Why the user keeps it is not stated anywhere in the file; only interpretation reaches it. |
| `annotation state` | string | `annotated` | `direct` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. Whether the PDF carries the user's own highlights is a structural observation, and it is the single best signal that the file was actually read. |

**Recognition**

| | |
|---|---|
| deterministic (pattern **plus** corroborating context) | • a `cid-doi` or `cid-pmid` hit (planning/deferred-catalogues/06-citation-identifier-patterns.json) in the title or page-one heading zone co-occurring with publisher furniture ('Received', 'Accepted', 'Published online', 'Downloaded from', a licence line) and no project identifier the corpus's own artifacts carry<br>• a PDF carrying reader annotations co-occurring with a bibliographic record in a reference-manager library the corpus already holds<br>• a file whose stem matches a reference-manager attachment naming convention and whose parent is that manager's attachment store<br>• a journal name in page-one publisher furniture, distinct from journal names appearing in a reference list (§2.2: “A course code or university name found in a filename, title, or page-one heading is more meaningful than the same text appearing once in a reference list on page eighteen.”) |
| needs the LLM | • deciding whether a paper is the user's own output or somebody else's<br>• grouping a reading library by the topic the user actually reads it for |
| never alone | • a bare .pdf in a downloads directory — §3.9: “A session should never be treated as proof of topic, and it should not carry the same confidence as a hash match or a directly extracted document fact.”<br>• a bare author surname<br>• a `cid-citation-authoryear` hit inside a reference list (§2.2: “A course code or university name found in a filename, title, or page-one heading is more meaningful than the same text appearing once in a reference list on page eighteen.”)<br>• a bare venue name (§4.9: “A university name alone should not create a group because Columbia can appear as an authoring school, course provider, target institution, employer, research venue, or merely a cited organization.”) |

**Work types**: `downloaded paper PDF`, `annotated PDF`, `book chapter scan`, `review article`, `downloaded thesis`, `highlights or notes export`, `saved web article`, `preprint downloaded to read`

**Grouping reasons**: one reading topic across its papers; one reference-manager collection; one systematic review's included set

**Template**: `reading topic → venue → artifact type`

> There is no project, so §5.4's order does not apply. Topic is the only parent that supplies context for the child (§5.5: “a parent dimension should provide the context required to understand the child. A work type such as Homework 3 is meaningful only after the course is known”), and §3.8 forbids the obvious alternative of foldering by author.

**Collides with**

| domain | discriminating signal | design cite |
|---|---|---|
| `res.published-article` | identical file shape — a publisher PDF with a DOI. Authorship is the only discriminator, and §3.8 bars it as a dimension | §3.8: “It should avoid using authorship or creator identity as a destination dimension.” |
| `res.reference-library` | the library file indexes these PDFs and is not one of them | — |
| `res.systematic-review` | a screened full-text set is a reading library with an inclusion decision attached | — |
| `res.peer-review-referee` | a manuscript received for review must not join the reading library | §4.8: “an application packet does not silently absorb a document with a conflicting target institution” |

**Sensitivity**: `none` — No `potentially sensitive` content is intrinsic to this domain. A handling class is P7's (§8.4) and is not set here.

**Open question (Joseph's call, unresolved)**

> §3.8 forbids authorship as a destination dimension — “A folder should not become a collection point for everything produced by the same person”. Yet 'papers I wrote' versus 'papers I read' is the most useful split in any research corpus, and self-authorship is the only thing that makes it. Is a self-authorship test a legitimate *domain-activation* signal even though it can never be a folder level?

---

### 28. `res.reference-library` — Reference-manager libraries and bibliographies

> The citation database itself: exports, collections, styles and the bibliographies built from them.

**provenance**: `proposal` — The design names reference management nowhere. Authored because a bibliography's fields describe the library, not any paper in it.

**Schema** — the fields this domain, and only this domain, legitimises.

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `library name` | string | `PVA-RDP library` | `direct` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. From the export's own header or the manager's collection metadata. |
| `reference manager` | string | `Zotero` | `direct` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. From format markers in the file itself, a structural observation. |
| `export format` | string | `BibTeX` | `direct` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. The detected format (§2.9: “inspect the real MIME type or file signature where possible”). It determines what can be recovered and is therefore a fact, not a note. |
| `collection or tag` | string | `to-read / methods` | `direct` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. From labelled collection fields in the export. |
| `linked manuscript` | string | `Photoactivatable RDP reporters in live cells` | `llm_supported` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. Which manuscript a .bib serves is inferred from co-location and citation overlap, not stated. |

**Recognition**

| | |
|---|---|
| deterministic (pattern **plus** corroborating context) | • a bibliography format (.bib, .ris, .enl) whose entries carry `cid-doi`, `cid-isbn13` or `cid-issn` hits (planning/deferred-catalogues/06-citation-identifier-patterns.json) — the file's own entry grammar is the corroborating context<br>• a reference-manager attachment store whose manifest names the library and whose members are reading-library PDFs<br>• a citation style file (.csl) co-occurring with a manuscript that cites in that style |
| needs the LLM | • deciding whether a .bib belongs to a manuscript or to the general library<br>• recovering a collection's purpose from an untitled export |
| never alone | • a bare .bib file with no resolvable entries<br>• a bare collection folder name<br>• a bare .csl file |

**Work types**: `BibTeX/RIS/EndNote export`, `reference-manager library database`, `attachment store`, `citation style file (.csl)`, `bibliography document`, `group-library sync record`, `deduplication report`

**Grouping reasons**: one library across its exports; one manuscript and the .bib it cites from; one collection across its members

**Template**: `reading topic → library → artifact type`

> Kept as a sibling of res.reading-library so the index and the indexed sit together (§5.5: “a parent dimension should provide the context required to understand the child. A work type such as Homework 3 is meaningful only after the course is known”).

**Collides with**

| domain | discriminating signal | design cite |
|---|---|---|
| `res.reading-library` | the library indexes the PDFs; it is not the PDFs | — |
| `res.systematic-review` | a review's screening export is a bibliography with a screening decision attached | — |
| `res.manuscript-preparation` | a manuscript's own .bib travels with the manuscript, not with the library | §4.8: “an application packet does not silently absorb a document with a conflicting target institution” |

**Sensitivity**: `none` — No `potentially sensitive` content is intrinsic to this domain. A handling class is P7's (§8.4) and is not set here.

---

### 29. `res.systematic-review` — Systematic reviews and evidence screening

> The auditable record of a search, a screen and an extraction.

**provenance**: `proposal` — The design names systematic reviews nowhere. Authored because a review's fields are procedural — search, stage, decision — and none of §3.11's rows holds them.

**Schema** — the fields this domain, and only this domain, legitimises.

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `review question` | string | `effect of X on Y in adults` | `llm_supported` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. Stated in a protocol narrative; there is no slot. |
| `registration id` | string | `CRD42026000123` | `validated` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. A registered review protocol's public identity, corroborated by registry context. |
| `search database` | string | `Embase` | `validated` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. Which database a strategy was run against. Reproducibility of the whole review depends on it. |
| `search date` | date | `2026-05-09` | `direct` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. From the strategy's own labelled run-date line. A search is only valid as of a date, which is why this is a fact. |
| `screening stage` | string | `full text` | `validated` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. Title/abstract and full-text screening produce different files with the same names. |
| `reviewer designation` | string | `Reviewer B` | `validated` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. A positional label, deliberately not a person, matching res.peer-review-author's treatment (§3.8: “authored_by and target_school, or our_firm and client”). |
| `inclusion criteria` | string | `adults, randomised, English` | `llm_supported` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. Stated in a protocol narrative. |

**Recognition**

| | |
|---|---|
| deterministic (pattern **plus** corroborating context) | • a search-strategy block — boolean operators with database field tags such as '[tiab]', '[MeSH]', '/exp' — co-occurring with a database name and a run date<br>• a screening spreadsheet whose header row carries screening vocabulary ('include', 'exclude', 'reason', 'reviewer', 'conflict') co-occurring with a review question or registration id<br>• a flow record whose stage labels match the screening stages the corpus already holds for the same review |
| needs the LLM | • telling a systematic review from a narrative literature review<br>• recovering which review an unlabelled screening sheet belongs to |
| never alone | • the words 'literature review'<br>• a bare database export<br>• a bare list of DOIs<br>• a bare spreadsheet of titles |

**Work types**: `registered protocol`, `search strategy`, `database export`, `deduplication log`, `title/abstract screening sheet`, `full-text set`, `extraction form`, `risk-of-bias assessment`, `flow record`, `included-studies table`

**Grouping reasons**: one review across its screening stages; one search across its database exports; one review's included set

**Template**: `review → screening stage → artifact type`

> The review is the project here; the stage is §5.4's `stage` under a different name (§5.4: “a Research template may define project → stage → artifact type”).

**Collides with**

| domain | discriminating signal | design cite |
|---|---|---|
| `res.reading-library` | a screened full-text set is a reading library with decisions attached and must not merge into it | §4.8: “an application packet does not silently absorb a document with a conflicting target institution” |
| `res.reference-library` | the exports are bibliographies | — |
| `res.dataset` | an extraction table is a dataset produced by the review | §3.11: “An academic abstract submitted as part of a university application can retain project = PVA/RDP and document type = abstract while also carrying purpose = university application and target university = UChicago.” |
| `res.manuscript-preparation` | the review's own write-up is a manuscript | — |

**Sensitivity**: `none` — No `potentially sensitive` content is intrinsic to this domain. A handling class is P7's (§8.4) and is not set here.

---

### 30. `res.thesis-supervision` — Thesis and dissertation supervision

> Supervising somebody else's degree: drafts, feedback, committees and milestones.

**provenance**: `proposal` — The design names supervision nowhere. Authored because the same file is §3.11's Academic domain for the student and a research domain for the supervisor — see the open question.

**Schema** — the fields this domain, and only this domain, legitimises.

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `student` | string | `M. Larsen` | `direct` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. §3.8 role field. The person supervised is not the author of the supervisor's corpus and never a destination dimension (§3.8: “It should avoid using authorship or creator identity as a destination dimension.”). |
| `degree programme` | string | `PhD Biological Sciences` | `validated` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. The programme determines the milestone set and the deadlines. |
| `thesis title` | string | `Photoswitchable probes for organelle contact sites` | `direct` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. §3.13's 'document title'. |
| `milestone` | string | `candidacy exam` | `validated` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. Proposal defense, candidacy, committee meeting and final defense are the skeleton of the whole relationship. |
| `committee member` | string | `R. Okonkwo (external)` | `direct` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. §3.8 role field. |
| `supervision role` | string | `primary supervisor` | `validated` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. Primary, co-supervisor and committee member produce different documents and different obligations. |
| `submission deadline` | date | `2027-05-30` | `direct` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. From a labelled programme slot. |

**Recognition**

| | |
|---|---|
| deterministic (pattern **plus** corroborating context) | • a thesis title page carrying a degree name together with a supervisor line, co-occurring with a milestone term ('defense', 'candidacy', 'viva', 'committee')<br>• a tracked-changes document whose revision metadata names the user as reviewer and whose base document is a thesis draft in the corpus's version families<br>• a programme form whose labelled fields name a student, a degree and a milestone date<br>• a supervisor-role line on a thesis title page or a programme form, naming the user in that role (§3.8: “authored_by and target_school, or our_firm and client”) |
| needs the LLM | • telling supervisor feedback from co-author edits on the same draft<br>• deciding whether a chapter is thesis material or a standalone manuscript |
| never alone | • a bare student name<br>• the word 'thesis'<br>• a bare degree abbreviation<br>• a tracked-changes file alone |

**Work types**: `thesis draft`, `chapter feedback`, `committee report`, `progress review form`, `defense scheduling`, `examiner report`, `recommendation letter`, `funding or stipend record`, `supervision meeting notes`

**Grouping reasons**: one student across their degree; one thesis across its chapters and drafts; one milestone across its paperwork

**Template**: `student → milestone → artifact type`

> Student first is the only order that matches how supervision is actually lived — and it is exactly the case §3.8 warns about, because the student here is a *subject* of the work rather than its author. Flagged, not resolved: see the open question.

**Collides with**

| domain | discriminating signal | design cite |
|---|---|---|
| `res.manuscript-preparation` | a thesis chapter and a manuscript can be byte-identical | §4.8: “an application packet does not silently absorb a document with a conflicting target institution” |
| `acad.course-enrollment` | the same file is coursework in the student's corpus and supervision in the supervisor's | §3.11: “Academic files may use school, term, course, instructor, and work type.” |
| `career.recruiting` | recommendation letters written for a student are recruiting documents | §3.3: “The LLM may determine whether an extracted document appears to be an application essay, research artifact, recruiting document, travel record, or other supported domain” |
| `res.peer-review-author` | examiner reports read exactly like referee reports | — |

**Sensitivity**: `potentially_sensitive` — §2.9's phrase `potentially sensitive`. Supervision files carry identified assessment of a named student, examiner reports and stipend records. A handling class is P7's (§8.4) and is not set here.

**Open question (Joseph's call, unresolved)**

> Whose corpus is this? On the supervisor's machine a thesis draft is research supervision; on the student's it is §3.11's Academic domain. §3.8 establishes that the same entity in a different role is a different field — does the same principle extend to a whole domain, keyed on who the user is?

---

### 31. `res.patent-disclosure` — Invention disclosures and patents

> Protecting an invention: disclosure, filing, prosecution and assignment.

**provenance**: `proposal` — The design names patents nowhere; §5.7's library names 'legal matters' as a separate situation and §3.15 makes legal material a safety domain. Authored because prosecution has its own identifiers and its own clock.

**Schema** — the fields this domain, and only this domain, legitimises.

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `docket number` | string | `CU-2026-041` | `validated` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. The technology-transfer office's handle, present from disclosure onward. |
| `application number` | string | `63/512,904` | `direct` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. From a labelled filing receipt slot. Distinct from the docket: one docket can carry several applications. |
| `filing date` | date | `2026-06-30` | `direct` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. From the filing receipt. |
| `priority date` | date | `2026-06-30` | `direct` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. The date that decides validity, and often the only reason a countersigned notebook page matters. |
| `jurisdiction` | string | `US; EP` | `validated` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. Each jurisdiction runs its own prosecution with its own deadlines. |
| `patent status` | string | `provisional filed` | `validated` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. Disclosed, provisional, national phase, office action, granted, abandoned. |
| `inventor` | string | `J. Chen; M. Larsen` | `direct` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. §3.8 role field, never a destination dimension. |
| `assignee institution` | string | `Columbia University` | `validated` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. Who owns it, which is usually not the inventor. |

**Recognition**

| | |
|---|---|
| deterministic (pattern **plus** corroborating context) | • patent vocabulary ('Invention Disclosure', 'Provisional Application', 'Office Action', 'claims', 'prior art', 'assignee') co-occurring with a docket or application number in a labelled slot<br>• a technology-transfer letterhead (§2.7 OCR) co-occurring with an inventor line and a docket number<br>• a filing receipt whose labelled fields carry an application number and a filing date<br>• a jurisdiction code in a labelled filing field co-occurring with an application number |
| needs the LLM | • telling a draft disclosure from a filed application<br>• reading an office action to identify which application it acts on when the header is an image |
| never alone | • a bare docket-shaped token<br>• a bare inventor surname<br>• the word 'patent'<br>• a bare claim-numbered list |

**Work types**: `invention disclosure form`, `provisional application`, `non-provisional application`, `prior-art search`, `office action`, `response to office action`, `assignment`, `issued patent`, `licence agreement`, `inventorship declaration`

**Grouping reasons**: one invention across its filings; one docket across its jurisdictions; one application across its prosecution history

**Template**: `docket → jurisdiction → status`

> The docket is the invention's identity across every filing; jurisdiction is the child that makes a status legible (§5.5: “a parent dimension should provide the context required to understand the child. A work type such as Homework 3 is meaningful only after the course is known”).

**Collides with**

| domain | discriminating signal | design cite |
|---|---|---|
| `legal.records` | §3.15 makes legal material a safety domain | §3.15: “Finance, identity, medical, and legal material should be implemented first as safety domains, meaning the system detects and protects them before any cloud or automated placement decision is allowed.” |
| `res.research-agreement` | collaboration IP terms govern a filing | — |
| `res.manuscript-preparation` | a disclosure filed before publication describes the same content as the paper and has the opposite confidentiality; a manuscript packet must not absorb it | §4.8: “an application packet does not silently absorb a document with a conflicting target institution” |
| `res.lab-notebook` | a countersigned notebook page is evidence for a priority date | — |

**Sensitivity**: `potentially_sensitive` — §2.9's phrase `potentially sensitive`. Pre-filing disclosures are confidential by necessity, and premature exposure destroys novelty. A handling class is P7's (§8.4) and is not set here.

---

### 32. `res.software-release` — Research software releases

> Code published as a citable, versioned artifact rather than kept as project scripts.

**provenance**: `inference` — Extends §3.11's Code row (§3.11: “Code files may use project, repository, programming language, and artifact type.”) with the release event. Release, licence and citation fields are not named in the design.

**Schema** — the fields this domain, and only this domain, legitimises.

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `project` | string | `pvatools` | `validated` | §3.11 literal in both the Research and the Code row. |
| `repository` | string | `chen-lab/pvatools` | `direct` | §3.11 Code row, literal. From a repository marker (deferred catalogue 05). |
| `programming language` | string | `Python` | `direct` | §3.11 Code row, literal. |
| `artifact type` | string | `tagged release` | `validated` | §3.11 literal in both rows. |
| `release version` | string | `v1.4.0` | `validated` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. A release is defined by its tag; without one there is no release, only code. |
| `software doi` | string | `10.5281/zenodo.1234567` | `validated` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. A `cid-doi` hit (planning/deferred-catalogues/06-citation-identifier-patterns.json) corroborated by archive-deposit context. It is what makes the software citable and is the join to res.repository-deposit. |
| `licence` | string | `MIT` | `direct` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. From a licence file, a labelled slot. |
| `citation file` | string | `CITATION.cff` | `direct` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. Its presence is a structural observation and is the clearest single signal that code was released rather than merely written. |

**Recognition**

| | |
|---|---|
| deterministic (pattern **plus** corroborating context) | • a repository marker (deferred catalogue 05) co-occurring with a release-tag token and a changelog or citation file in the same tree<br>• a CITATION.cff or codemeta.json whose fields name a project a research artifact in the corpus also carries<br>• an archive whose manifest (§2.9: “Compressed archives should yield their manifests without extraction”) names a repository and a version tag, co-occurring with a `cid-doi` hit |
| needs the LLM | • deciding whether a repository has ever been released when no tag is present<br>• matching a release archive to the publication that cites it |
| never alone | • a bare version tag<br>• a bare repository directory — deferred catalogue 05's markers identify a repository, not a release<br>• a licence file alone |

**Work types**: `tagged release archive`, `CITATION.cff`, `licence file`, `changelog`, `package manifest`, `archive deposit record`, `documentation build`, `container image manifest`, `release notes`

**Grouping reasons**: one package across its releases; one release and its archive deposit; one project across its software outputs

**Template**: `project → release version → artifact type`

> §5.4: “a Research template may define project → stage → artifact type” with the release standing in for `stage`; a changelog is meaningless until the release is known (§5.5: “a parent dimension should provide the context required to understand the child. A work type such as Homework 3 is meaningful only after the course is known”).

**Collides with**

| domain | discriminating signal | design cite |
|---|---|---|
| `res.analysis-code` | project scripts are not a release; only the release carries a tag and a citation file | §3.11: “Code files may use project, repository, programming language, and artifact type.” |
| `res.repository-deposit` | the archive deposit gives the release its DOI and is a deposit record, not the software | — |
| `code.project` | §3.11 gives Code its own row and the same repository activates both | §3.11: “An academic abstract submitted as part of a university application can retain project = PVA/RDP and document type = abstract while also carrying purpose = university application and target university = UChicago.” |
| `res.reproducibility-package` | a paper's package may embed a released version without being one | — |

**Sensitivity**: `none` — No `potentially sensitive` content is intrinsic to this domain. A handling class is P7's (§8.4) and is not set here.

---

### 33. `res.reproducibility-package` — Reproducibility and replication packages

> The bundle that lets somebody else re-run a paper's results.

**provenance**: `proposal` — The design names reproducibility packages nowhere. Authored because the package's identity is the publication it reproduces, not the project it came from.

**Schema** — the fields this domain, and only this domain, legitimises.

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `linked publication` | string | `10.1038/s41586-021-03819-2` | `validated` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. A `cid-doi` hit (planning/deferred-catalogues/06-citation-identifier-patterns.json) corroborated by package README context. The package exists for exactly one publication. |
| `package version` | string | `v1.0.1` | `validated` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. Packages are corrected after publication, which is why the version is a fact and not a filename. |
| `environment specification` | string | `renv.lock` | `direct` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. The lockfile's presence and name are structural observations, and its absence is the commonest reason a package fails to run. |
| `execution entry point` | string | `run_all.R` | `direct` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. Named in the README's own labelled instruction. |
| `included dataset` | string | `cohort2_analysis.dta` | `llm_supported` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. Described in the README; a directory listing alone does not say which files are the data. |
| `included code` | string | `analysis/` | `llm_supported` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. Same reasoning. |
| `verification badge` | string | `AEA Data Editor — reproduced` | `direct` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. From a verification report's labelled verdict, where a journal ran one. |

**Recognition**

| | |
|---|---|
| deterministic (pattern **plus** corroborating context) | • an archive whose manifest (§2.9: “Compressed archives should yield their manifests without extraction”) names both a data directory and a code directory, together with a README carrying reproduction vocabulary ('to reproduce', 'run', 'requirements', 'session info')<br>• an environment lockfile co-occurring with a `cid-doi` hit (planning/deferred-catalogues/06-citation-identifier-patterns.json) naming the publication the package supports<br>• a directory whose top level holds a README, a data directory and a code directory, co-occurring with a manuscript title the corpus already holds |
| needs the LLM | • telling a reproducibility package from an ordinary project directory<br>• reading a README to identify which paper the package reproduces |
| never alone | • a bare .zip<br>• a README alone<br>• a bare lockfile<br>• a directory containing both code and data — that is most project directories |

**Work types**: `replication archive`, `run-all script`, `environment lockfile`, `container recipe`, `README with reproduction steps`, `data and code bundle`, `journal verification report`, `codebook copy`, `expected-output snapshot`

**Grouping reasons**: one publication and its package; one package across its corrected versions

**Template**: `project → manuscript → artifact type`

> The package hangs off the publication it reproduces, so it inherits the manuscript's parents rather than opening a branch (§5.5: “a parent dimension should provide the context required to understand the child. A work type such as Homework 3 is meaningful only after the course is known”).

**Collides with**

| domain | discriminating signal | design cite |
|---|---|---|
| `res.dataset` | the package contains a dataset copy and is not the dataset | — |
| `res.analysis-code` | the package contains the code and is not the code | — |
| `res.software-release` | a release is reusable software; a package is a frozen re-run of one paper | — |
| `res.repository-deposit` | the deposit record is custody metadata; the package is the payload | — |

**Sensitivity**: `none` — No `potentially sensitive` content is intrinsic to this domain. A handling class is P7's (§8.4) and is not set here.

---

### 34. `res.data-management-plan` — Data management plans

> The document that promises a funder what will happen to the data.

**provenance**: `proposal` — The design names DMPs nowhere. Authored because a DMP's fields are the funder's, not the study's, and it outlives the proposal it was written for.

**Schema** — the fields this domain, and only this domain, legitimises.

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `funder` | string | `NIH` | `validated` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. A DMP is written to a funder's template and is unusable against another's. |
| `opportunity or award number` | string | `PA-24-247` | `validated` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. The join back to res.grant-proposal and res.grant-reporting. |
| `plan version` | string | `v2 (just-in-time)` | `validated` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. Plans are revised at award and at renewal; the version says which promise is binding. |
| `data types described` | string | `de-identified genotypes; imaging` | `llm_supported` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. Described in prose. |
| `retention period` | string | `ten years after study close` | `direct` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. From a labelled retention slot. It is the field that eventually authorises deleting something. |
| `repository named` | string | `dbGaP` | `validated` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. Which repository was promised; the join to res.repository-deposit and the thing compliance is measured against. |
| `sharing condition` | string | `controlled access via DAC` | `llm_supported` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. Stated in prose and governs whether a DUA is needed. |

**Recognition**

| | |
|---|---|
| deterministic (pattern **plus** corroborating context) | • DMP vocabulary ('data management plan', 'data sharing', 'retention', 'repository', 'metadata standard', 'preservation') co-occurring with a funder name or an opportunity number<br>• a funder DMP template whose headings match a proposal already in the corpus for the same call<br>• a plan document whose labelled retention and repository fields name a repository the corpus already holds a deposit for |
| needs the LLM | • telling a DMP from the data-sharing paragraph of a proposal narrative<br>• deciding which award version of a plan is currently binding |
| never alone | • the phrase 'data management'<br>• a bare funder acronym<br>• a bare repository name<br>• the word 'plan' |

**Work types**: `DMP document`, `DMP tool export`, `funder DMP template`, `data sharing statement`, `retention schedule`, `plan revision`, `compliance checklist`

**Grouping reasons**: one award across its plan versions; one funder across the user's plans; one plan and the deposits discharging it

**Template**: `funder → award → plan version`

> Same parents as res.grant-reporting so a grant's promises and its accounting sit together (§5.5: “a parent dimension should provide the context required to understand the child. A work type such as Homework 3 is meaningful only after the course is known”).

**Collides with**

| domain | discriminating signal | design cite |
|---|---|---|
| `res.grant-proposal` | a DMP is a proposal component and a standalone compliance artifact at once | §3.11: “An academic abstract submitted as part of a university application can retain project = PVA/RDP and document type = abstract while also carrying purpose = university application and target university = UChicago.” |
| `res.repository-deposit` | the deposit discharges the plan and is not the plan | — |
| `res.research-agreement` | a controlled-access condition becomes a DUA | — |
| `res.irb-ethics` | data-sharing promises must match what the consent permits | — |

**Sensitivity**: `none` — No `potentially sensitive` content is intrinsic to this domain. A handling class is P7's (§8.4) and is not set here.

---

### 35. `res.repository-deposit` — Repository and archive deposits

> The record that something was formally lodged somewhere permanent.

**provenance**: `proposal` — The design names deposits nowhere. Authored because the record's fields are custodial — repository, accession, embargo — and describe an act, not an artifact.

**Schema** — the fields this domain, and only this domain, legitimises.

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `repository` | string | `Zenodo` | `validated` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. Which archive holds it. Institutional, disciplinary and general repositories have different terms. |
| `accession or deposit id` | string | `10.5281/zenodo.1234567` | `validated` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. A `cid-doi`, `cid-handle` or accession hit (planning/deferred-catalogues/06-citation-identifier-patterns.json) corroborated by deposit context. |
| `deposit date` | date | `2026-08-04` | `direct` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. From the receipt's labelled slot. |
| `embargo end date` | date | `2027-08-04` | `direct` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. The date the deposit becomes public. Acting on it early is a breach, which is why it is a fact. |
| `licence` | string | `CC BY 4.0` | `direct` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. From the deposit's labelled licence field. |
| `deposited artifact` | string | `cohort2 dataset v2.1` | `llm_supported` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. Which corpus object was deposited is stated in the receipt's free-text title. |
| `linked publication` | string | `10.1038/s41586-021-03819-2` | `validated` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. The related-identifier field, corroborated by publication context. |

**Recognition**

| | |
|---|---|
| deterministic (pattern **plus** corroborating context) | • a repository accession token co-occurring with deposit vocabulary ('deposited', 'accession', 'embargo', 'version of record', 'related identifier')<br>• a metadata record (§2.9: “notebook cell types, package manifests, schema keys, repository markers, and project-root signals”) whose schema keys are a deposit standard's and whose values name an artifact the corpus already holds<br>• a receipt email (§2.9: “Email formats such as EML, MBOX, MSG, and exported mail archives should yield sender, recipients, subject, sent date, thread identifiers, message body, attachment names, and reply-chain context”) from a repository whose body carries the accession and the deposited title<br>• a related-identifier field carrying a `cid-doi` hit (planning/deferred-catalogues/06-citation-identifier-patterns.json) co-occurring with deposit vocabulary |
| needs the LLM | • deciding which local artifact a deposit record corresponds to<br>• telling an accepted-manuscript deposit from a version-of-record deposit |
| never alone | • a bare accession-shaped token<br>• a bare repository name<br>• a `cid-handle` hit alone (planning/deferred-catalogues/06-citation-identifier-patterns.json)<br>• a bare licence string |

**Work types**: `deposit confirmation`, `accession record`, `embargo notice`, `metadata record (DataCite, Dublin Core)`, `deposited file copy`, `repository link record`, `withdrawal notice`, `curation correspondence`

**Grouping reasons**: one artifact across its deposits; one repository across the user's deposits; one publication and the deposits supporting it

**Template**: `project → artifact type → repository`

> The deposit describes an artifact the tree already holds, so it hangs off that artifact rather than opening a top-level branch (§5.8: “The canvas must support uneven depth because real file trees are not and should not be perfectly symmetrical. One branch may require four levels, while another should remain flat.”).

**Collides with**

| domain | discriminating signal | design cite |
|---|---|---|
| `res.dataset` | the deposited copy and the working copy are the same bytes under different custody | — |
| `res.published-article` | an accepted-manuscript deposit is the article under a different licence | — |
| `res.software-release` | the archive deposit is what gives a release its DOI | — |
| `res.grant-reporting` | one deposit receipt can discharge a public-access obligation | §3.11: “An academic abstract submitted as part of a university application can retain project = PVA/RDP and document type = abstract while also carrying purpose = university application and target university = UChicago.” |
| `res.preprint` | a preprint posting and a repository deposit are both public lodgements | — |

**Sensitivity**: `none` — No `potentially sensitive` content is intrinsic to this domain. A handling class is P7's (§8.4) and is not set here.

---

### 36. `res.facility-booking` — Core-facility and equipment bookings

> Reserving, using and being charged for shared instruments.

**provenance**: `proposal` — The design names facility bookings nowhere. Authored because the corpus is calendar and billing shaped — §2.9: “Calendar formats such as ICS should yield event title, start and end time, location, organizer, attendees, and recurrence metadata.” — and no §3.11 row covers it.

**Schema** — the fields this domain, and only this domain, legitimises.

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `facility` | string | `Imaging Core` | `validated` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. The shared resource; the join to res.instrument-output. |
| `instrument` | string | `Zeiss LSM 980` | `validated` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. What was booked. |
| `booking id` | string | `BK-2026-3391` | `direct` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. From the confirmation's labelled slot. |
| `session start` | date | `2026-03-04T09:00` | `direct` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. §2.9: “Calendar formats such as ICS should yield event title, start and end time, location, organizer, attendees, and recurrence metadata.” — start and end are labelled ICS fields, which is why they are direct here and nowhere else in this catalogue. |
| `session end` | date | `2026-03-04T13:00` | `direct` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. Same source. The pair is what a recharge invoice is computed from. |
| `charge code` | string | `R01GM123456-2028` | `direct` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. From a labelled account field. It is the join to res.grant-reporting and the reason a booking is a research fact and not a diary entry. |
| `authorisation status` | string | `trained, independent user` | `direct` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. From the facility's labelled training record. |

**Recognition**

| | |
|---|---|
| deterministic (pattern **plus** corroborating context) | • an ICS file (§2.9: “Calendar formats such as ICS should yield event title, start and end time, location, organizer, attendees, and recurrence metadata.”) whose organizer is a core facility and whose event title names an instrument the corpus already holds<br>• an invoice or usage line whose charge code matches an award number already in the corpus, co-occurring with an instrument name<br>• a booking confirmation (§2.9: “Email formats such as EML, MBOX, MSG, and exported mail archives should yield sender, recipients, subject, sent date, thread identifiers, message body, attachment names, and reply-chain context”) whose labelled fields carry a booking id, an instrument and a session window |
| needs the LLM | • separating a facility booking from an ordinary meeting invite in a mixed calendar export<br>• deciding which project a session should be charged to when the code is shared |
| never alone | • a bare calendar event<br>• a bare instrument name<br>• a bare booking-shaped id<br>• a bare charge code |

**Work types**: `booking confirmation`, `calendar invite (.ics)`, `usage report`, `recharge invoice`, `training authorisation`, `facility SOP`, `cancellation notice`, `access badge record`, `rate schedule`

**Grouping reasons**: one facility across its bookings; one session and the run it produced; one award across the sessions charged to it

**Template**: `facility → instrument → session`

> Facility before instrument before session, each supplying the next one's context (§5.5: “a parent dimension should provide the context required to understand the child. A work type such as Homework 3 is meaningful only after the course is known”). Bookings are time-stamped but not time-defined — the recharge, not the calendar, is what makes them worth keeping.

**Collides with**

| domain | discriminating signal | design cite |
|---|---|---|
| `res.instrument-output` | the booking scheduled the run; the raw file is the run | — |
| `res.grant-reporting` | recharges land in award accounting | §3.11: “An academic abstract submitted as part of a university application can retain project = PVA/RDP and document type = abstract while also carrying purpose = university application and target university = UChicago.” |
| `fin.records` | §3.11 gives Finance its own row and an invoice is a financial record | §3.11: “Finance files may use institution, account type, tax year, and record type.” |
| `calendar.events` | §2.9 makes ICS a first-class format; most ICS files are not research | §2.9: “Calendar formats such as ICS should yield event title, start and end time, location, organizer, attendees, and recurrence metadata.” |

**Sensitivity**: `none` — No `potentially sensitive` content is intrinsic to this domain. A handling class is P7's (§8.4) and is not set here.

---

### 37. `res.field-work` — Field work records

> Research done away from the institution: sites, campaigns, permits and what was collected.

**provenance**: `proposal` — The design names field work nowhere. Authored because site and permit are the organising facts and §3.11's Photos row would otherwise claim the imagery on capture metadata alone.

**Schema** — the fields this domain, and only this domain, legitimises.

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `site` | string | `Tanjung Puting — Plot 4` | `validated` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. Where the work happened. It is the field-work analogue of `lab` and the root of the branch. |
| `site coordinates` | string | `-2.7361, 111.9214` | `direct` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. From GPS metadata or a labelled datasheet column (§2.6). See the open question before treating this like an ordinary value. |
| `campaign` | string | `2026 wet season` | `validated` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. Field work happens in discrete campaigns, and a campaign is the unit everyone remembers. |
| `collection date` | date | `2026-02-14` | `direct` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. From a labelled datasheet column (§3.10: “The product must not use fuzzy date parsing because file names and documents frequently contain numbers that look like years but are course identifiers, version numbers, build numbers, ZIP codes, or other unrelated values.”). |
| `permit number` | string | `SIP-2026-0117` | `direct` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. From the permit's labelled slot. Working without one is unlawful, so its presence is a compliance fact. |
| `field team` | string | `J. Chen; local guide M. S.` | `direct` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. §3.8 role field, never a destination dimension. |
| `sample id` | string | `TP-P4-0093` | `validated` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. The join to res.sample-specimen. |
| `conditions` | string | `overcast, 27 C, post-rain` | `llm_supported` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. Recorded in free-text field notes. |

**Recognition**

| | |
|---|---|
| deterministic (pattern **plus** corroborating context) | • a GPS-bearing file (§2.6 EXIF GPS, or a GPX/KML track) co-occurring with a site name and a collection-date line in a sibling datasheet<br>• a datasheet whose header row carries field vocabulary ('transect', 'quadrat', 'waypoint', 'habitat', 'collector') co-occurring with a campaign or permit identifier<br>• a permit document whose labelled fields name a site and a date range the corpus's records fall inside |
| needs the LLM | • telling field photographs from personal travel photographs taken on the same trip<br>• reading free-text notes to recover which transect a record belongs to |
| never alone | • a bare GPS coordinate<br>• a bare place name<br>• a photo with GPS EXIF alone — that is §4.2's deterministic photo event and belongs to the Photos domain (§4.2: “For a photo group, it might be a deterministic event created from camera, time, and GPS metadata.”)<br>• a bare date |

**Work types**: `field notebook`, `site log`, `GPS track or waypoint file`, `permit`, `field photograph set`, `collection datasheet`, `transect record`, `weather log`, `shipping manifest`, `site map`

**Grouping reasons**: one campaign across its records; one site across its campaigns; one transect across its datasheets and photos

**Template**: `site → campaign → record type`

> Site before campaign, which is §5.5's document-and-record order applied to a place rather than a project. This is the case where §5.5: “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders. Photos and capture-based media are the major exception: time often belongs first because capture date is a defining aspect of the material.” is closest to flipping.

**Collides with**

| domain | discriminating signal | design cite |
|---|---|---|
| `photos.event` | §3.11's Photos row claims images by capture year, event and location; field photographs satisfy all three and would route there | §3.11: “Photos may use capture year, event, location, people, camera information, and media type.” |
| `res.lab-notebook` | a field notebook is the same artifact with a site instead of a lab | — |
| `res.sample-specimen` | collected material becomes a specimen record | — |
| `travel.records` | §3.3 names 'travel record' as a separate LLM determination, and a field trip generates both | §3.3: “The LLM may determine whether an extracted document appears to be an application essay, research artifact, recruiting document, travel record, or other supported domain” |
| `res.dataset` | datasheets become datasets | — |

**Sensitivity**: `potentially_sensitive` — §2.9's phrase `potentially sensitive`. Field records carry precise coordinates for protected species and sites, plus named local collaborators and participants. A handling class is P7's (§8.4) and is not set here.

**Open question (Joseph's call, unresolved)**

> Precise coordinates for a protected species or an archaeological site must not leave the device, but §2.9's phrase `potentially sensitive` was written for personal data. Is site sensitivity this catalogue's to mark at all, or entirely P7's to define once §8.4's handling classes exist?

---

### 38. `res.survey-instrument` — Survey instruments and fielding records

> The questionnaire itself, how it was fielded, and what came back.

**provenance**: `proposal` — The design names survey research nowhere. Authored because an instrument has a version and a licence that its responses do not, and the two are routinely the same spreadsheet.

**Schema** — the fields this domain, and only this domain, legitimises.

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `study` | string | `PVA cohort 2` | `validated` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. The join to res.dataset and res.irb-ethics. |
| `instrument name` | string | `PHQ-9` | `validated` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. Validated scales are reused across studies and licensed by name; the name is the fact, not the filename. |
| `instrument version` | string | `2026 revision` | `validated` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. A modified scale is not the validated scale, which is why the version is a compliance fact. |
| `fielding wave` | string | `wave 2` | `validated` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. Longitudinal studies field the same instrument repeatedly; the wave is what distinguishes otherwise identical exports. |
| `platform` | string | `Qualtrics` | `direct` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. From the export's own format markers. |
| `language version` | string | `Spanish (Mexico)` | `direct` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. Which approved translation this is — a different claim from §3.11's universal `language` fact. |
| `licence or permission` | string | `licensed, per-use` | `direct` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. From a labelled permission slot. Some validated scales may not be redistributed at all. |

**Recognition**

| | |
|---|---|
| deterministic (pattern **plus** corroborating context) | • a numbered-question structure co-occurring with response-scale vocabulary ('Strongly agree', 'Not at all', 'Select one', 'Please rate') and a study or instrument name<br>• a survey-platform export whose format markers name the platform, co-occurring with a study identifier<br>• a fielding document whose labelled fields carry a wave and a field-period range |
| needs the LLM | • telling a blank instrument from an export that also carries responses<br>• recognising a modified validated scale as modified |
| never alone | • a bare list of questions<br>• a bare instrument acronym — §3.7's word-boundary rule applies to scale acronyms like any other short token (§3.7: “word-boundary matching rather than substring matching”)<br>• a bare platform export file<br>• the word 'survey' |

**Work types**: `questionnaire document`, `survey platform export (.qsf)`, `fielding plan`, `response export`, `screener`, `approved translation`, `cognitive-testing notes`, `consent page`, `invitation and reminder text`

**Grouping reasons**: one instrument across its waves; one study across its instruments; one wave across its fielding documents

**Template**: `study → instrument → wave`

> Study before instrument before wave; 'wave 2' names nothing until both parents are known (§5.5: “a parent dimension should provide the context required to understand the child. A work type such as Homework 3 is meaningful only after the course is known”).

**Collides with**

| domain | discriminating signal | design cite |
|---|---|---|
| `res.data-dictionary` | the instrument asks; the dictionary describes the recorded answer | — |
| `res.dataset` | a response export is a dataset with participant-level rows | §3.11: “An academic abstract submitted as part of a university application can retain project = PVA/RDP and document type = abstract while also carrying purpose = university application and target university = UChicago.” |
| `res.human-subjects-consent` | an online instrument's consent page is inside the instrument file | — |
| `res.qualitative-coding` | open-text responses are coded like interview data | — |

**Sensitivity**: `potentially_sensitive` — §2.9's phrase `potentially sensitive`. Response exports carry participant-level answers, and screening instruments carry the identifying data used to screen. A handling class is P7's (§8.4) and is not set here.

---

### 39. `res.qualitative-coding` — Qualitative coding and interview analysis

> Interviews and text turned into codes, themes and an auditable analysis.

**provenance**: `proposal` — The design names qualitative research nowhere. Authored because its corpus is recordings and transcripts, which §2.9 already treats as a policy-gated format class: §2.9: “only under an explicit privacy and compute policy—speech-to-text transcripts”

**Schema** — the fields this domain, and only this domain, legitimises.

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `study` | string | `PVA lived-experience study` | `validated` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. The join to res.irb-ethics and res.human-subjects-consent. |
| `participant code` | string | `P-014` | `direct` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. From the transcript's labelled header. A de-identified code is still a key to a person. |
| `session date` | date | `2026-04-11` | `direct` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. From the transcript header. |
| `transcript stage` | string | `de-identified` | `validated` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. Verbatim and de-identified transcripts are the same interview with opposite handling, and they routinely share a filename stem. This is the most consequential field in the domain. |
| `codebook version` | string | `v3` | `validated` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. Codes are revised mid-analysis and a coded extract is only interpretable against its codebook version. |
| `code or theme` | string | `navigating gatekeepers` | `llm_supported` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. Themes are named in analytic memos and are irreducibly interpretive. |
| `analysis software` | string | `NVivo` | `direct` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. From the project file's format markers. |
| `coder designation` | string | `Coder B` | `validated` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. A positional label, deliberately not a person (§3.8: “authored_by and target_school, or our_firm and client”). |

**Recognition**

| | |
|---|---|
| deterministic (pattern **plus** corroborating context) | • a transcript layout — speaker labels with turn-taking — co-occurring with a participant code and a study identifier<br>• a qualitative-analysis project file whose format markers name the software, co-occurring with a codebook the corpus already holds<br>• a memo or extract document citing a code that a codebook in the corpus defines<br>• a coder label in a coded-extract or agreement-report header co-occurring with a codebook version token |
| needs the LLM | • telling a verbatim transcript from a de-identified one when the header is missing<br>• grouping extracts under the theme a memo argues for |
| never alone | • a bare audio file — §2.9 permits transcripts “only under an explicit privacy and compute policy”<br>• a bare participant code<br>• a bare theme word<br>• a transcript layout alone — meeting minutes have the same shape |

**Work types**: `audio or video recording`, `verbatim transcript`, `de-identified transcript`, `codebook`, `coded project file (NVivo, ATLAS.ti, MAXQDA)`, `analytic memo`, `intercoder agreement record`, `theme summary`, `extract report`

**Grouping reasons**: one study across its interviews; one codebook version across the extracts coded under it; one participant across their sessions

**Template**: `study → transcript stage → artifact type`

> Transcript stage sits directly under the study because it is the field that decides handling, and §5.9's scoped-General rule means an unstaged transcript must not fall out of the study branch.

**Collides with**

| domain | discriminating signal | design cite |
|---|---|---|
| `res.survey-instrument` | open-text survey responses are coded the same way | — |
| `res.dataset` | a coded extract table is a dataset | §3.11: “An academic abstract submitted as part of a university application can retain project = PVA/RDP and document type = abstract while also carrying purpose = university application and target university = UChicago.” |
| `res.data-dictionary` | a qualitative codebook and a variable dictionary are both 'codebooks' and are different objects | — |
| `res.human-subjects-consent` | the consent governs what may be retained and for how long | — |

**Sensitivity**: `potentially_sensitive` — §2.9's phrase `potentially sensitive`. Verbatim transcripts carry identifiable speech, names spoken in passing, and recordings that are themselves biometric. A handling class is P7's (§8.4) and is not set here.

---

### 40. `res.correction-retraction` — Corrections, retractions and the post-publication record

> What happens to a paper after publication when something in it was wrong.

**provenance**: `proposal` — The design names post-publication corrections nowhere. Authored because a notice's identity is another artifact's DOI, which is a shape no other domain here has.

**Schema** — the fields this domain, and only this domain, legitimises.

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `corrected publication doi` | string | `10.1038/s41586-021-03819-2` | `validated` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. A `cid-doi` hit (planning/deferred-catalogues/06-citation-identifier-patterns.json) corroborated by notice vocabulary. The notice has no identity of its own without it. |
| `notice type` | string | `expression of concern` | `validated` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. Correction, erratum, corrigendum, expression of concern and retraction are legally and reputationally distinct. |
| `notice date` | date | `2027-01-19` | `direct` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. From the notice's labelled publication slot. |
| `venue` | string | `Nature` | `validated` | **§3.11 literal.** The journal issues the notice, which is why the venue is settled here even when the underlying paper's was contested. |
| `reason stated` | string | `figure panel duplication` | `llm_supported` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. Notices state reasons in prose, deliberately briefly. |
| `affected artifact` | string | `Figure 3b` | `llm_supported` | **Added field** — beyond §3.11's literal Research row, authored here and not quoted. Which figure, table or dataset is affected is named in the notice text; it is the join to res.figure-and-source. |

**Recognition**

| | |
|---|---|
| deterministic (pattern **plus** corroborating context) | • notice vocabulary ('Correction to:', 'Erratum', 'Corrigendum', 'Retraction Note', 'Expression of Concern') co-occurring with a `cid-doi` hit naming the corrected article (planning/deferred-catalogues/06-citation-identifier-patterns.json)<br>• a replacement figure or supplementary file whose version family already contains a published-article member and whose filename carries a correction token<br>• editorial correspondence (§2.9: “Email formats such as EML, MBOX, MSG, and exported mail archives should yield sender, recipients, subject, sent date, thread identifiers, message body, attachment names, and reply-chain context”) whose subject carries a manuscript id already in the corpus together with correction vocabulary<br>• `venue` is §3.11's inherited Research field: a venue name from a validated gazetteer (§3.7, deferred) co-occurring with notice vocabulary in the same document — the journal issues the notice, so its name is settled. §4.9 is why a bare organisation name never suffices |
| needs the LLM | • telling a correction to the user's own paper from one to a paper in the reading library<br>• identifying which artifact a notice affects when the notice names it only descriptively |
| never alone | • the word 'correction'<br>• a bare `cid-doi` hit<br>• a tracked-changes file<br>• a replacement figure alone |

**Work types**: `correction notice`, `erratum or corrigendum`, `expression of concern`, `retraction notice`, `corrected figure`, `corrected supplementary file`, `editorial correspondence`, `institutional inquiry record`, `author statement`

**Grouping reasons**: one article and everything correcting it; one notice and the replacement files it introduces

**Template**: `project → manuscript → artifact type`

> The notice attaches to the article, so it inherits the article's parents. §4.8's absorb rule matters in the reverse direction here: it must attach without joining the article's own version family.

**Collides with**

| domain | discriminating signal | design cite |
|---|---|---|
| `res.published-article` | the notice attaches to the article and must not silently join its version family | §4.8: “an application packet does not silently absorb a document with a conflicting target institution” |
| `res.figure-and-source` | a corrected figure supersedes a published one and both must remain distinguishable | §3.1: “member of a version family, and potentially sensitive” |
| `res.peer-review-author` | post-publication editorial correspondence reads exactly like review correspondence | — |
| `res.reading-library` | a retraction notice for somebody else's paper belongs with that paper, not with the user's outputs | §3.8: “It should avoid using authorship or creator identity as a destination dimension.” |

**Sensitivity**: `none` — No `potentially sensitive` content is intrinsic to this domain. A handling class is P7's (§8.4) and is not set here.

**Open question (Joseph's call, unresolved)**

> A retraction is a durable, unflattering fact about a file. §5.2 says “Sensitive groups should appear differently: a Finance or Identity proposal may be visible as a protected area”, and nothing says whether a retraction is that kind of fact. Does the tree name it in a branch label, or record it and stay quiet?

---

## Open questions — collected, verbatim

17 entries carry one. Each is Joseph's call and none is resolved here. Copy into `NEEDS-JOSEPH.md`.

- **`res.research-project`** (Research project work (the §3.11 Research schema itself)) — Once the sub-domains below exist, is §3.11's Research domain still a filing domain in its own right — the branch a project's odds and ends land in — or only the schema they all inherit? The answer decides whether `Research/<project>/General` is a real node or a residual one (§5.9).
- **`res.manuscript-preparation`** (Manuscript preparation and its version family) — Does a manuscript branch by `venue` at all? A paper rejected at one journal and resubmitted to another would have to move folders, which §5.10's “A carefully curated existing folder should be treated as a strong expression of user intent” argues against — but the journal is often the only name the user remembers. Real level, or metadata only?
- **`res.peer-review-referee`** (Reviewing and editorial work done for others) — A manuscript received for review is somebody else's unpublished work held in confidence. Should it be filed into the tree at all, or surfaced the way §4.9 surfaces protected records — “Rare but sensitive files such as passports, visas, and legal documents may be surfaced as protected records” — and otherwise left alone?
- **`res.preprint`** (Preprints and preprint versions) — Is a preprint the same version family as the article it becomes (“member of a version family”, §3.1), or a separate artifact? The answer decides whether `Research/<project>/<manuscript>` holds both, or whether preprints get their own branch.
- **`res.figure-and-source`** (Figures and figure source files) — Do figures live under the manuscript that publishes them, or in one per-project figure library the manuscripts point at? §5.8's uneven depth allows either, and a figure reused across a poster, a talk and two papers has no single natural parent.
- **`res.dataset`** (Research datasets) — Does a study's sensitivity travel to everything derived from it — datasets, statistical output, figures — or is every file classified on its own evidence? §3.9 forbids using a session as “a basis for automatic semantic propagation”; nothing in the design says whether a sensitivity fact propagates along a derivation edge.
- **`res.analysis-code`** (Analysis code and scripts) — §5.1 offers both a `Research` and a `Code and Projects` top-level branch, and a paper's analysis script is honestly both. §4.9 permits both memberships — “A file may validly belong to more than one accepted group” — but the frozen tree gives it one physical home. Which parent wins?
- **`res.lab-notebook`** (Lab notebooks and experiment records) — A lab notebook is chronological by law and by habit, which puts it against §5.5's rule that “For document and record domains, project, function, or subject usually comes before time”. Does the notebook branch date-first, matching how it is legally maintained, or project-first, matching every other research branch?
- **`res.instrument-output`** (Instrument runs and raw acquisition output) — Raw instrument output is often the largest and least re-readable part of a corpus, and §2.9 already permits “safe metadata-only indexing” for formats nothing can open. Does it enter the destination tree at all, or stay where the instrument wrote it and get indexed in place?
- **`res.grant-proposal`** (Grant proposals and funding applications) — §5.1 offers both a `Research` and a `Finance and Administration` top-level branch and a grant is honestly both — the narrative is research, the budget and award notice are administration. Does the grant branch split across two roots, or does one side live as a cross-reference?
- **`res.irb-ethics`** (Ethics, IRB and IACUC approvals) — §3.15 makes “Finance, identity, medical, and legal material” safety domains, “meaning the system detects and protects them before any cloud or automated placement decision is allowed”. Human-subjects and animal-ethics material is none of those four by name and behaves like all of them. Is it a safety domain, and does §3.15's list need its name?
- **`res.human-subjects-consent`** (Consent and participant-facing materials) — A blank consent form is a template; an executed one is a signed record about an identifiable person. They are the same document class with the same filename family. Does the domain split them, and does the executed side leave the ordinary tree the way §4.9's protected records do?
- **`res.poster`** (Conference posters) — A poster is a research artifact and a portfolio piece. §5.1 offers both a `Research` and a `Career` top-level branch and §4.9 permits both memberships — but the frozen tree gives it one physical home. Which one, and does the other get a cross-reference?
- **`res.reading-library`** (Literature and reading library) — §3.8 forbids authorship as a destination dimension — “A folder should not become a collection point for everything produced by the same person”. Yet 'papers I wrote' versus 'papers I read' is the most useful split in any research corpus, and self-authorship is the only thing that makes it. Is a self-authorship test a legitimate *domain-activation* signal even though it can never be a folder level?
- **`res.thesis-supervision`** (Thesis and dissertation supervision) — Whose corpus is this? On the supervisor's machine a thesis draft is research supervision; on the student's it is §3.11's Academic domain. §3.8 establishes that the same entity in a different role is a different field — does the same principle extend to a whole domain, keyed on who the user is?
- **`res.field-work`** (Field work records) — Precise coordinates for a protected species or an archaeological site must not leave the device, but §2.9's phrase `potentially sensitive` was written for personal data. Is site sensitivity this catalogue's to mark at all, or entirely P7's to define once §8.4's handling classes exist?
- **`res.correction-retraction`** (Corrections, retractions and the post-publication record) — A retraction is a durable, unflattering fact about a file. §5.2 says “Sensitive groups should appear differently: a Finance or Identity proposal may be visible as a protected area”, and nothing says whether a retraction is that kind of fact. Does the tree name it in a branch label, or record it and stay quiet?

