# Domain catalogue — healthcare, medicine, and clinical work

Supercategory: `healthcare-medicine`  ·  Authored: 2026-08-21  ·  Entries: **43**

Conforms to [`_CONTRACT.md`](_CONTRACT.md). Source of truth:
[`../00-database-agent-product-design.md`](../00-database-agent-product-design.md). Every quotation in
this file and in the JSON was checked character-for-character against that file before publication.

## What the design actually says about this supercategory

It says one thing, in §3.15:

> Finance, identity, medical, and legal material should be implemented first as safety domains,
> meaning the system detects and protects them before any cloud or automated placement decision is
> allowed.

That is the whole of it. The design names **no medical domain and no medical fact field anywhere** —
§3.11's field table has six rows and none of them is medical; P6's SPEC records the same gap, listing
**Identity, medical, legal** fact-schema fields among its deferred items with the note that
*no fields stated anywhere*. Consequently **no entry in this file carries `provenance: "design"`**, and
none ever could. Thirty-nine are `proposal`. Four are `inference`, and each of those four extends a
field set §3.11 does name (finance) or a domain §3.3 does name (travel) — the `design_cite` on each says
exactly which.

### Sensitivity

Forty-two of forty-three entries are marked `potentially_sensitive`. That is §2.9's own phrase and it is
the entire assertion — **no handling class is set anywhere in this file**, because handling classes are
P7's under §8.4 and inventing a medical-severity taxonomy here would be inventing P7's vocabulary. The
single `none` is `med.clinical-protocol-guideline`, which concerns a population rather than an identified
person.

### How to read `recognition`

`deterministic` follows §3.5's model — a pattern **plus corroborating context**, never a bare pattern:

> For example, BUSIB 4300 becomes a course fact only when the engine finds a course-code pattern
> together with academic context such as “syllabus,” “lecture,” “credits,” “instructor,” or “semester.”

`never_alone` is the more important half of this slice. Medical vocabulary is *public* vocabulary: it
saturates coursework, journalism, insurance marketing, fitness apps, fiction, and research. A rule that
fires on it will tell a nursing student that their homework is a patient record. Every item in every
`never_alone` list is a pattern that was considered for `deterministic` and rejected; the rejections are
collected in [Appendix A](#appendix-a--deterministic-rules-that-were-rejected).

---

## Index

| # | id | Name | Side | Provenance | Sensitivity |
|---|---|---|---|---|---|
| 1 | `med.personal-health-record` | Personal health record and portal exports | Patient / person | proposal | sensitive |
| 2 | `med.lab-result` | Laboratory and diagnostic test results | Patient / person | proposal | sensitive |
| 3 | `med.imaging-radiology` | Imaging studies and radiology reports | Patient / person | proposal | sensitive |
| 4 | `med.prescription-medication` | Prescriptions and medication lists | Patient / person | proposal | sensitive |
| 5 | `med.immunisation-record` | Immunisation and vaccination records | Patient / person | proposal | sensitive |
| 6 | `med.referral-received` | Referrals and second opinions received | Patient / person | proposal | sensitive |
| 7 | `med.hospital-admission-discharge` | Hospital admissions, emergency visits, and discharge summaries | Patient / person | proposal | sensitive |
| 8 | `med.surgical-procedure-record` | Surgical and procedural records | Patient / person | proposal | sensitive |
| 9 | `med.physical-therapy-rehab` | Physical therapy and rehabilitation | Patient / person | proposal | sensitive |
| 10 | `med.mental-health-record` | Mental health and behavioural health records | Patient / person | proposal | sensitive |
| 11 | `med.dental-record` | Dental records | Patient / person | proposal | sensitive |
| 12 | `med.vision-eyecare-record` | Vision and eye care records | Patient / person | proposal | sensitive |
| 13 | `med.allergy-intolerance-record` | Allergy and intolerance records | Patient / person | proposal | sensitive |
| 14 | `med.chronic-condition-management` | Chronic condition management | Patient / person | proposal | sensitive |
| 15 | `med.pregnancy-maternity-record` | Pregnancy and maternity records | Patient / person | proposal | sensitive |
| 16 | `med.paediatric-child-health` | A child's health records held by a parent or guardian | Patient / person | proposal | sensitive |
| 17 | `med.caregiving-dependant` | Caregiving for a dependent adult | Patient / person | proposal | sensitive |
| 18 | `med.advance-directive` | Advance directives and end-of-life instructions | Patient / person | proposal | sensitive |
| 19 | `med.genetic-testing-report` | Genetic and genomic test reports | Patient / person | proposal | sensitive |
| 20 | `med.clinical-trial-participation` | Clinical trial participation as a subject | Patient / person | proposal | sensitive |
| 21 | `med.medical-travel` | Travel for medical care | Patient / person | inference | sensitive |
| 22 | `med.wearable-health-export` | Wearable, app, and home-device health exports | Patient / person | proposal | sensitive |
| 23 | `med.medical-certification-letter` | Clinician letters certifying capacity, absence, or accommodation | Patient / person | proposal | sensitive |
| 24 | `med.occupational-health-screening` | Occupational health and workplace screening | Patient / person | proposal | sensitive |
| 25 | `med.health-plan-coverage` | Health plan enrolment and coverage documents | Payer / billing | inference | sensitive |
| 26 | `med.insurance-claim-eob` | Health insurance claims and explanations of benefits | Payer / billing | inference | sensitive |
| 27 | `med.provider-billing-dispute` | Provider bills, statements, and billing disputes | Payer / billing | inference | sensitive |
| 28 | `med.clinician-patient-chart` | Patient charts held by a clinician or practice | Clinician / practice | proposal | sensitive |
| 29 | `med.clinician-clinical-note` | Clinical notes authored by a clinician | Clinician / practice | proposal | sensitive |
| 30 | `med.clinician-treatment-plan` | Treatment plans authored by a clinician | Clinician / practice | proposal | sensitive |
| 31 | `med.clinician-case-conference` | Case conferences and multidisciplinary meetings | Clinician / practice | proposal | sensitive |
| 32 | `med.clinician-licensure-credentialing` | Licensure, registration, and credentialing | Clinician / practice | proposal | sensitive |
| 33 | `med.clinician-cme` | Continuing medical education and professional development | Clinician / practice | proposal | sensitive |
| 34 | `med.clinician-malpractice-incident` | Malpractice cover, claims, and patient-safety incidents | Clinician / practice | proposal | sensitive |
| 35 | `med.clinician-referral-sent` | Referrals and correspondence sent by a clinician | Clinician / practice | proposal | sensitive |
| 36 | `med.clinical-protocol-guideline` | Clinical protocols, pathways, and guidelines | Clinician / practice | proposal | none |
| 37 | `med.medical-teaching-material` | Medical teaching material and grand rounds | Clinician / practice | proposal | sensitive |
| 38 | `med.practice-administration` | Practice administration and rostering | Clinician / practice | proposal | sensitive |
| 39 | `med.device-and-implant-record` | Medical device and implant records | Clinician / practice | proposal | sensitive |
| 40 | `med.pharmacy-operations` | Pharmacy operations | Clinician / practice | proposal | sensitive |
| 41 | `med.public-health-reporting` | Public health and registry reporting | Clinician / practice | proposal | sensitive |
| 42 | `med.veterinary-practice` | Veterinary practice records | Clinician / practice | proposal | sensitive |
| 43 | `med.veterinary-pet-owner` | An animal's records held by its owner | Clinician / practice | proposal | sensitive |

---

## Entries

## Patient / person side

### 1. `med.personal-health-record` — Personal health record and portal exports

A person's own consolidated medical record as they hold it: patient-portal exports, after-visit summaries, and records-request packets.

**Provenance:** `proposal`  — the design names neither this domain nor any of its fields.

**Schema** — the fields this domain, and only this domain, legitimises:

| Field | Type | Example | Ceiling | Why |
|---|---|---|---|---|
| `subject_person` | string | self | `direct` | Whose record this is, read from a labeled patient-identity field. §3.8: 'The system must separate roles that happen to contain the same entity type.' A caregiver's corpus contains records about several people and the holder is not the subject. §3.5: 'Deterministic extractors create direct facts when the information comes from a reliable, explicit source, such as a content hash, EXIF timestamp, a document title, or a labeled form field.' |
| `record_source` | string | a named patient-portal or EHR system | `direct` | The producing system, read from the export's own manifest or producer metadata rather than from its prose. §3.5: 'Deterministic extractors create direct facts when the information comes from a reliable, explicit source, such as a content hash, EXIF timestamp, a document title, or a labeled form field.' |
| `facility` | string | the health system that holds the record | `direct` | Organisation role, distinct from the treating clinician. §3.8: 'The system must separate roles that happen to contain the same entity type.' |
| `record_date` | date | the export or summary date | `direct` | A labeled date field only; no fuzzy parsing. §3.10: 'The product must not use fuzzy date parsing' |
| `document_type` | string | after-visit summary | `validated` | Confirmed by the document-structure rule below, not by the filename. §3.13: 'A validated fact was found by a deterministic rule and passed contextual checks, such as a course-code pattern appearing beside “lecture,” “syllabus,” or “semester.”' |

**Recognition**

*Deterministic — pattern plus corroborating context:*

- a patient-portal or EHR export manifest naming the producing system, co-occurring with a labeled patient-identity field and a labeled export or record date in the same file
- an after-visit-summary document structure in which a labeled encounter date, a named facility and a labeled patient identity all appear together in the header block

*Needs the LLM:*

- a photographed or scanned paper record whose only signal is prose
- a records-request letter that names no facility and carries no patient-identity field
- a personal note summarising one's own history, written as free prose

*Never alone — rejected as deterministic signals:*

- a folder named Health, Medical, or Records
- a bare person name
- a bare date
- the word 'patient' occurring in prose
- a medical-sounding filename token such as 'chart', 'records', or 'visit'

**Work types:** after-visit summary, portal export, records request, continuity-of-care document, scanned paper record, health summary

**Grouping reasons:** one records-request packet from one facility; one export session from one portal; one subject person's record set

**Template:** `subject person → facility → record type → year`

> §5.5: 'For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders.' Facility gives the context needed to read a record type. §5.5: 'a parent dimension should provide the context required to understand the child' `subject_person` is optional and must be dropped when it would produce a single child. §5.9: 'It should warn when a level produces only one child'

**Collides with**

| Domain | Signal that separates them | Design cite |
|---|---|---|
| `med.clinician-patient-chart` | identical vocabulary; the discriminator is holder role, not content. A patient's own portal export names one subject; a clinician's chart set names many, and carries practice-management or EHR-authoring provenance rather than portal-export provenance. | §3.8: 'The system must separate roles that happen to contain the same entity type.' |
| `med.lab-result` | a portal export bundles lab results inside itself; the bundle is the record, the individual result is the lab-result domain. Extracting both is correct — one file may hold facts from more than one domain. | — |
| `pers.identity-document` | both carry a labeled person identity; only the health record carries a facility and a clinical document type. | §3.8: 'The system must separate roles that happen to contain the same entity type.' |

**Sensitivity:** `potentially_sensitive` — A person's own medical record — 'potentially sensitive', which is §2.9's own phrase and the whole of what this field asserts. No handling class is set here; classification is P7's (§8.4).

**Open question**

> Should a person's own records and a dependant's records share one branch with `subject_person` as the first dimension, or should each subject person get their own top-level branch? For a single-person corpus `subject_person` produces exactly the one-child level §5.9 tells the product to warn about; for a caregiver it is the only sane first split. This is a default folder shape for someone's real family and is Joseph's call, not the catalogue's.


### 2. `med.lab-result` — Laboratory and diagnostic test results

Results of a laboratory or point-of-care test performed on a person's specimen, as reported back to them.

**Provenance:** `proposal`  — the design names neither this domain nor any of its fields.

**Schema** — the fields this domain, and only this domain, legitimises:

| Field | Type | Example | Ceiling | Why |
|---|---|---|---|---|
| `subject_person` | string | self | `direct` | Whose specimen. §3.8: 'The system must separate roles that happen to contain the same entity type.' |
| `test` | string | the named panel or analyte reported | `validated` | The test identity is confirmed only when the result-table rule below fires; a drug or analyte name in prose is not a test fact. §3.13: 'A validated fact was found by a deterministic rule and passed contextual checks, such as a course-code pattern appearing beside “lecture,” “syllabus,” or “semester.”' |
| `collection_date` | date | the labeled specimen collection date | `direct` | A labeled collection-date field, distinct from the report date and from the file's own timestamps. §3.5: 'Deterministic extractors create direct facts when the information comes from a reliable, explicit source, such as a content hash, EXIF timestamp, a document title, or a labeled form field.' §3.10: 'The product must not use fuzzy date parsing' |
| `report_date` | date | the labeled date the result was issued | `direct` | §3.5: 'Deterministic extractors create direct facts when the information comes from a reliable, explicit source, such as a content hash, EXIF timestamp, a document title, or a labeled form field.' |
| `ordering_provider` | string | the clinician who ordered the test | `direct` | A role distinct from the laboratory that performed it and from the subject person. §3.8: 'The system must separate roles that happen to contain the same entity type.' |
| `performing_laboratory` | string | the laboratory that ran and reported the specimen | `direct` | Organisation role. §3.8: 'The system must separate roles that happen to contain the same entity type.' |
| `specimen_type` | string | the labeled specimen descriptor | `direct` | §3.5: 'Deterministic extractors create direct facts when the information comes from a reliable, explicit source, such as a content hash, EXIF timestamp, a document title, or a labeled form field.' |
| `result_status` | string | preliminary or final, where the report labels it | `direct` | §3.5: 'Deterministic extractors create direct facts when the information comes from a reliable, explicit source, such as a content hash, EXIF timestamp, a document title, or a labeled form field.' |

**Recognition**

*Deterministic — pattern plus corroborating context:*

- a result-table structure in which an analyte or test-name column, a reference-range column label and a units column label co-occur, together with a labeled specimen or collection descriptor and a named performing laboratory or ordering provider
- a laboratory report header block carrying a labeled collection date and a labeled ordering provider in the same block as a named performing laboratory

*Needs the LLM:*

- a result table that carries reference ranges but also a course code, an assignment heading, a rubric or a due date — two plausible domains, and the academic anchor must not be overridden by the medical one
- a photographed result slip with no readable header block
- a message from a clinician that describes a result in prose without reproducing it

*Never alone — rejected as deterministic signals:*

- a filename containing 'lab', 'labs', 'lab report', 'test', 'test results', 'results' or 'panel' — 'lab report' is an academic work type in this product's own worked example, 'test results' is equally an exam score or a software test run, and 'Labs' is a common company-name suffix
- an analyte, hormone, or biomarker name occurring in prose
- a units token such as mg/dL
- a reference range with no specimen and no performing laboratory
- a bare person name plus a bare date

**Work types:** laboratory report, pathology report, point-of-care test result, screening result, specimen collection instruction, result trend printout

**Grouping reasons:** one specimen collection event across its panels; one ordering provider's series for one condition; one screening programme's recall series

**Template:** `subject person → test category → collection year`

> §5.5: 'For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders.' Test category gives the context needed to read a single result. §5.5: 'a parent dimension should provide the context required to understand the child'

**Collides with**

| Domain | Signal that separates them | Design cite |
|---|---|---|
| `acad.lab-course` | a chemistry or biology lab report carries analytes and units and the word 'lab'; it carries no reference range, no specimen collection date, and no performing laboratory. Where an academic anchor co-occurs the file has two plausible domains and belongs to the model, not to either rule. | §3.3: the LLM handles files that 'have multiple plausible domains' |
| `res.dataset` | research assay output carries analytes, units and often reference values, but names a protocol and a study rather than an ordering provider and a subject person. | — |
| `med.genetic-testing-report` | a genetic report is a laboratory report; it is separated because its schema legitimises gene and variant-interpretation fields that an ordinary panel must not be allowed to claim. | §4.8: 'each fact or label belongs to an allowed domain schema' |
| `med.occupational-health-screening` | an employment drug screen or pre-placement physical is a lab result whose recipient is an employer; the employer role belongs to the career slice and must not be written as `ordering_provider`. | §3.8: 'The system must separate roles that happen to contain the same entity type.' |

**Sensitivity:** `potentially_sensitive` — Test results about a named person — 'potentially sensitive', which is §2.9's own phrase and the whole of what this field asserts. No handling class is set here; classification is P7's (§8.4).

**Open question**

> Serial record domains — lab results, imaging, and monitoring logs — may genuinely want time as the first dimension, which contradicts §5.5's default that for document and record domains subject comes before time. §5.5's stated exception is 'Photos and capture-based media', not serial clinical results. Does the exception extend to them? Joseph's call; the catalogue follows the stated default until he says otherwise.


### 3. `med.imaging-radiology` — Imaging studies and radiology reports

Diagnostic imaging performed on a person: the image data and the radiologist's report on it.

**Provenance:** `proposal`  — the design names neither this domain nor any of its fields.

**Schema** — the fields this domain, and only this domain, legitimises:

| Field | Type | Example | Ceiling | Why |
|---|---|---|---|---|
| `subject_person` | string | self | `direct` | Whose study. §3.8: 'The system must separate roles that happen to contain the same entity type.' |
| `modality` | string | the labeled imaging modality | `direct` | Read from a populated DICOM modality header tag or a labeled report field, not inferred from the word appearing in prose. §3.5: 'Deterministic extractors create direct facts when the information comes from a reliable, explicit source, such as a content hash, EXIF timestamp, a document title, or a labeled form field.' |
| `body_region` | string | the labeled examined region | `direct` | §3.5: 'Deterministic extractors create direct facts when the information comes from a reliable, explicit source, such as a content hash, EXIF timestamp, a document title, or a labeled form field.' |
| `study_date` | date | the labeled acquisition date | `direct` | §3.5: 'Deterministic extractors create direct facts when the information comes from a reliable, explicit source, such as a content hash, EXIF timestamp, a document title, or a labeled form field.' §3.10: 'The product must not use fuzzy date parsing' |
| `referring_clinician` | string | the clinician who requested the study | `direct` | §3.8: 'The system must separate roles that happen to contain the same entity type.' |
| `reporting_radiologist` | string | the clinician who authored the report | `direct` | A role distinct from the referrer; and per §3.8: 'It should avoid using authorship or creator identity as a destination dimension.' neither may become a folder level. |
| `imaging_facility` | string | the site that acquired the study | `direct` | §3.8: 'The system must separate roles that happen to contain the same entity type.' |
| `accession_identifier` | string | the study's own labeled identifier | `direct` | A labeled identifier field, never a bare numeric string found in text. §3.5: 'Deterministic extractors create direct facts when the information comes from a reliable, explicit source, such as a content hash, EXIF timestamp, a document title, or a labeled form field.' |

**Recognition**

*Deterministic — pattern plus corroborating context:*

- a DICOM file signature together with a populated patient-identity header tag and a populated modality header tag — the signature alone is a format signal only, and §2.9: 'treat the file extension as a routing signal rather than an assumption about meaning'
- a report structure carrying a findings section heading and an impression section heading as an adjacent pair, together with a labeled study or examination descriptor and a named referring clinician

*Needs the LLM:*

- a DICOM series with a de-identified or empty patient header — research imaging and clinical imaging are indistinguishable from the format alone
- an image export (JPEG or PDF) of a scan with no surrounding report text
- a report that states an impression but names no modality and no facility

*Never alone — rejected as deterministic signals:*

- a modality word such as MRI, CT, X-ray or ultrasound occurring in prose — equipment quotes, science journalism, physics coursework and hospital-set fiction all contain it
- a DICOM extension or signature with no populated patient-identity tag
- a filename containing 'scan' — a document scan is the far more common meaning
- the section heading 'Findings' on its own, which appears in audit reports, legal opinions and inspection records
- a bare accession-shaped numeric string

**Work types:** radiology report, image series, study CD or export, imaging requisition, prior-study comparison, contrast or preparation instruction

**Grouping reasons:** one study across its report and image series; one body region followed across time for one condition; one imaging facility's release packet

**Template:** `subject person → body region → modality → study year`

> §5.5: 'For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders.' Body region gives the context that makes a modality meaningful. §5.5: 'a parent dimension should provide the context required to understand the child'

**Collides with**

| Domain | Signal that separates them | Design cite |
|---|---|---|
| `res.dataset` | identical file format and often identical modality tags; the discriminator is a populated clinical patient identity and a named referring clinician versus a study protocol and a subject code. | — |
| `med.veterinary-practice` | veterinary imaging is also DICOM and also carries a patient-identity tag; the species descriptor and the owner-and-animal pairing are the discriminator. | — |
| `med.dental-record` | dental radiographs are imaging studies; they are left in the dental domain because their schema legitimises tooth-level fields that a general imaging study must not claim. | §4.8: 'each fact or label belongs to an allowed domain schema' |

**Sensitivity:** `potentially_sensitive` — Images of a named person's body and the report on them — 'potentially sensitive', which is §2.9's own phrase and the whole of what this field asserts. No handling class is set here; classification is P7's (§8.4).


### 4. `med.prescription-medication` — Prescriptions and medication lists

What a person has been prescribed or dispensed, and the list they maintain of it.

**Provenance:** `proposal`  — the design names neither this domain nor any of its fields.

**Schema** — the fields this domain, and only this domain, legitimises:

| Field | Type | Example | Ceiling | Why |
|---|---|---|---|---|
| `subject_person` | string | self | `direct` | §3.8: 'The system must separate roles that happen to contain the same entity type.' |
| `medication` | string | the prescribed product as written on the prescription | `validated` | A medication fact only where the dispensing structure below fires; a drug name in prose is not one. §3.13: 'A validated fact was found by a deterministic rule and passed contextual checks, such as a course-code pattern appearing beside “lecture,” “syllabus,” or “semester.”' |
| `prescriber` | string | the clinician who wrote it | `direct` | §3.8: 'The system must separate roles that happen to contain the same entity type.' |
| `dispensing_pharmacy` | string | the pharmacy that filled it | `direct` | An organisation role distinct from the prescriber and from the manufacturer. §3.8: 'The system must separate roles that happen to contain the same entity type.' |
| `fill_date` | date | the labeled date dispensed | `direct` | §3.5: 'Deterministic extractors create direct facts when the information comes from a reliable, explicit source, such as a content hash, EXIF timestamp, a document title, or a labeled form field.' §3.10: 'The product must not use fuzzy date parsing' |
| `directions` | string | the labeled directions-for-use line | `direct` | §3.5: 'Deterministic extractors create direct facts when the information comes from a reliable, explicit source, such as a content hash, EXIF timestamp, a document title, or a labeled form field.' |
| `refills_remaining` | string | the labeled refills field as written | `direct` | Stored as the label's own value; the catalogue sets no numbers of its own. |
| `prescription_identifier` | string | the pharmacy's own labeled identifier | `direct` | §3.5: 'Deterministic extractors create direct facts when the information comes from a reliable, explicit source, such as a content hash, EXIF timestamp, a document title, or a labeled form field.' |

**Recognition**

*Deterministic — pattern plus corroborating context:*

- a directions-for-use line co-occurring with a labeled quantity-and-refills pair and a named prescriber in the same block
- a dispensing label or pharmacy receipt structure in which a named dispensing pharmacy, a labeled fill date and a labeled prescription identifier appear together
- a medication-list table in which a product column co-occurs with a directions column and a prescriber or start-date column

*Needs the LLM:*

- a photograph of a pill bottle whose OCR yields a product name but no directions and no pharmacy
- a message discussing a change of medication in prose
- a supplement or over-the-counter list a person keeps alongside prescribed items

*Never alone — rejected as deterministic signals:*

- a drug or brand name — pharmacology coursework, health journalism, supplement inventories, recipes and fiction all contain them
- a dose-shaped token: a quantity followed by a mass unit
- the token 'Rx', which is also a common product-name and file-naming affix
- a pharmacy chain's name on a receipt, which is far more often a receipt for shampoo
- a filename containing 'meds' or 'medication'

**Work types:** prescription, dispensing label, pharmacy receipt, medication list, prior-authorisation request, medication instruction sheet

**Grouping reasons:** one prescription across its refills; one prescriber's regimen for one condition; one pharmacy's dispensing history

**Template:** `subject person → medication or regimen → year`

> §5.5: 'For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders.'

**Collides with**

| Domain | Signal that separates them | Design cite |
|---|---|---|
| `med.pharmacy-operations` | a dispensing record exists on both sides; the person's copy names one subject, the pharmacy's ledger names many and carries a registrant identity. | §3.8: 'The system must separate roles that happen to contain the same entity type.' |
| `fin.receipts-expenses` | a pharmacy receipt is simultaneously a purchase record. Only the sig-and-refills structure makes it a prescription fact; without it, it is a receipt. | — |
| `med.insurance-claim-eob` | a pharmacy benefit statement names the same medication and the same fill date but carries a claim identifier and a payer, which belong to the claim schema. | §4.8: 'each fact or label belongs to an allowed domain schema' |

**Sensitivity:** `potentially_sensitive` — What a named person takes, which discloses their conditions — 'potentially sensitive', which is §2.9's own phrase and the whole of what this field asserts. No handling class is set here; classification is P7's (§8.4).


### 5. `med.immunisation-record` — Immunisation and vaccination records

A person's record of vaccines administered, and the certificates issued from it.

**Provenance:** `proposal`  — the design names neither this domain nor any of its fields.

**Schema** — the fields this domain, and only this domain, legitimises:

| Field | Type | Example | Ceiling | Why |
|---|---|---|---|---|
| `subject_person` | string | self | `direct` | §3.8: 'The system must separate roles that happen to contain the same entity type.' |
| `vaccine` | string | the administered product as recorded | `validated` | Confirmed only by the administration-row rule below. §3.13: 'A validated fact was found by a deterministic rule and passed contextual checks, such as a course-code pattern appearing beside “lecture,” “syllabus,” or “semester.”' |
| `administration_date` | date | the labeled date given | `direct` | §3.5: 'Deterministic extractors create direct facts when the information comes from a reliable, explicit source, such as a content hash, EXIF timestamp, a document title, or a labeled form field.' §3.10: 'The product must not use fuzzy date parsing' |
| `dose_in_series` | string | the labeled dose or series position as written | `direct` | Stored as the label's own value; no numbering is invented here. |
| `administering_provider` | string | the clinic, pharmacy or site that gave it | `direct` | §3.8: 'The system must separate roles that happen to contain the same entity type.' |
| `lot_identifier` | string | the labeled lot field | `direct` | §3.5: 'Deterministic extractors create direct facts when the information comes from a reliable, explicit source, such as a content hash, EXIF timestamp, a document title, or a labeled form field.' |
| `issuing_authority` | string | the body that issued a certificate, where one exists | `direct` | §3.8: 'The system must separate roles that happen to contain the same entity type.' |

**Recognition**

*Deterministic — pattern plus corroborating context:*

- a vaccine-administration table in which a product column co-occurs with a labeled administration date and either a dose-in-series label or a lot identifier column, together with a named administering provider
- an immunisation certificate structure carrying a named issuing authority, a labeled subject identity and at least one administration row

*Needs the LLM:*

- a school or travel form that asks for immunisation history and is partly completed
- a photograph of a paper card whose OCR yields dates but no product column

*Never alone — rejected as deterministic signals:*

- a vaccine or manufacturer name in prose — public-health reporting, policy coursework and travel advice are saturated with them
- the words 'vaccine', 'vaccination' or 'immunisation' in a filename or heading
- a bare date sequence
- a QR code or certificate-shaped image with no readable administration row

**Work types:** immunisation record, vaccination certificate, school immunisation form, travel vaccination record, titre or immunity result

**Grouping reasons:** one subject person's full immunisation history; one travel or enrolment requirement and the records assembled to satisfy it

**Template:** `subject person → record type → year`

> §5.5: 'For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders.'

**Collides with**

| Domain | Signal that separates them | Design cite |
|---|---|---|
| `acad.k12-schooling` | a school immunisation form is required by an institution and is often filed with enrolment paperwork; it carries both an educational purpose and a clinical administration record. | §3.9: 'The documents are content-incoherent but purpose-coherent.' |
| `pers.travel-record` | travel vaccination records are assembled for a trip and are purpose-coherent with it rather than with the rest of the medical corpus. | §3.9: 'Topic answers what a file is about, while purpose answers what the file was for.' |
| `med.occupational-health-screening` | employer-required immunity evidence is the same artifact addressed to an employer. | — |

**Sensitivity:** `potentially_sensitive` — A named person's immunisation history — 'potentially sensitive', which is §2.9's own phrase and the whole of what this field asserts. No handling class is set here; classification is P7's (§8.4).


### 6. `med.referral-received` — Referrals and second opinions received

A referral into specialist care as the person holds it, including a second-opinion request and the outside-records packet assembled for it.

**Provenance:** `proposal`  — the design names neither this domain nor any of its fields.

**Schema** — the fields this domain, and only this domain, legitimises:

| Field | Type | Example | Ceiling | Why |
|---|---|---|---|---|
| `subject_person` | string | self | `direct` | §3.8: 'The system must separate roles that happen to contain the same entity type.' |
| `referring_clinician` | string | the clinician sending the referral | `direct` | Distinct from the receiving clinician; the same person-entity type in two different roles. §3.8: 'The system must separate roles that happen to contain the same entity type.' |
| `receiving_clinician` | string | the specialist or service receiving it | `direct` | §3.8: 'The system must separate roles that happen to contain the same entity type.' |
| `specialty` | string | the service referred to | `validated` | §3.13: 'A validated fact was found by a deterministic rule and passed contextual checks, such as a course-code pattern appearing beside “lecture,” “syllabus,” or “semester.”' |
| `referral_date` | date | the labeled date issued | `direct` | §3.5: 'Deterministic extractors create direct facts when the information comes from a reliable, explicit source, such as a content hash, EXIF timestamp, a document title, or a labeled form field.' §3.10: 'The product must not use fuzzy date parsing' |
| `reason_for_referral` | string | the labeled reason field | `direct` | §3.5: 'Deterministic extractors create direct facts when the information comes from a reliable, explicit source, such as a content hash, EXIF timestamp, a document title, or a labeled form field.' |
| `referral_status` | string | accepted, pending or declined where the document labels it | `direct` | §3.5: 'Deterministic extractors create direct facts when the information comes from a reliable, explicit source, such as a content hash, EXIF timestamp, a document title, or a labeled form field.' |
| `records_released` | string | the labeled list of records enclosed or authorised | `direct` | §3.5: 'Deterministic extractors create direct facts when the information comes from a reliable, explicit source, such as a content hash, EXIF timestamp, a document title, or a labeled form field.' |

**Recognition**

*Deterministic — pattern plus corroborating context:*

- a referral-letter structure in which a referring-clinician block and a receiving-clinician block appear as an addressed pair, together with a labeled reason-for-referral field and a subject-person identity
- a records-release authorisation form naming a releasing facility, a receiving facility and a labeled subject identity together

*Needs the LLM:*

- an email asking a colleague to see someone, with no letter structure
- a second-opinion consultation summary that reads as a clinical note and names no referrer
- a letter whose two named clinicians cannot be assigned to sender and receiver roles from structure alone

*Never alone — rejected as deterministic signals:*

- the word 'referral' — business referrals, recruitment referrals and referral-bonus marketing are far more common in an ordinary corpus
- a 'Dr.' honorific or an MD/RN/DDS suffix, which appear in academic citations, correspondence and fiction
- a specialty name in prose
- a consent or release form with no named facilities

**Work types:** referral letter, second-opinion request, records-release authorisation, outside-records packet, consultation summary, appointment instruction

**Grouping reasons:** one referral across its letter, records packet and resulting consultation; one second opinion and the records assembled to obtain it

**Template:** `subject person → specialty → year`

> §5.5: 'For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders.' Specialty gives the context that makes a consultation summary readable. §5.5: 'a parent dimension should provide the context required to understand the child'

**Collides with**

| Domain | Signal that separates them | Design cite |
|---|---|---|
| `med.clinician-referral-sent` | the same letter, held by the other party. The discriminator is which clinician role matches the corpus owner and whether the corpus holds one subject or many. | §3.8: 'The system must separate roles that happen to contain the same entity type.' |
| `med.clinician-clinical-note` | a consultation summary is a clinical note written by the receiving clinician and sent to the person; the person's copy is not the practice's chart entry. | — |

**Sensitivity:** `potentially_sensitive` — Correspondence naming a person's condition — 'potentially sensitive', which is §2.9's own phrase and the whole of what this field asserts. No handling class is set here; classification is P7's (§8.4).

**Open question**

> Is 'second opinion' a domain or a purpose facet? §3.9 makes purpose a first-class facet answering what a file was for, and a second-opinion packet is exactly a purpose-coherent set of otherwise ordinary records — a referral, a records release, a prior report, a new consultation. The catalogue folds it into this entry rather than giving it a schema of its own, because its would-be fields are already the referral's. If Joseph wants a distinct branch for it, it becomes a purpose-defined packet in §5.6's sense rather than a new schema.


### 7. `med.hospital-admission-discharge` — Hospital admissions, emergency visits, and discharge summaries

An episode of inpatient, emergency or urgent care as the person holds it, from admission paperwork to discharge instructions.

**Provenance:** `proposal`  — the design names neither this domain nor any of its fields.

**Schema** — the fields this domain, and only this domain, legitimises:

| Field | Type | Example | Ceiling | Why |
|---|---|---|---|---|
| `subject_person` | string | self | `direct` | §3.8: 'The system must separate roles that happen to contain the same entity type.' |
| `facility` | string | the admitting hospital or unit | `direct` | §3.8: 'The system must separate roles that happen to contain the same entity type.' |
| `admission_date` | date | the labeled admission date | `direct` | §3.5: 'Deterministic extractors create direct facts when the information comes from a reliable, explicit source, such as a content hash, EXIF timestamp, a document title, or a labeled form field.' §3.10: 'The product must not use fuzzy date parsing' |
| `discharge_date` | date | the labeled discharge date | `direct` | §3.5: 'Deterministic extractors create direct facts when the information comes from a reliable, explicit source, such as a content hash, EXIF timestamp, a document title, or a labeled form field.' §3.10: 'The product must not use fuzzy date parsing' |
| `attending_clinician` | string | the clinician of record for the episode | `direct` | §3.8: 'The system must separate roles that happen to contain the same entity type.' |
| `encounter_type` | string | inpatient, emergency or observation as the record labels it | `validated` | §3.13: 'A validated fact was found by a deterministic rule and passed contextual checks, such as a course-code pattern appearing beside “lecture,” “syllabus,” or “semester.”' |
| `discharge_disposition` | string | the labeled disposition field | `direct` | §3.5: 'Deterministic extractors create direct facts when the information comes from a reliable, explicit source, such as a content hash, EXIF timestamp, a document title, or a labeled form field.' |
| `account_identifier` | string | the facility's own labeled encounter identifier | `direct` | §3.5: 'Deterministic extractors create direct facts when the information comes from a reliable, explicit source, such as a content hash, EXIF timestamp, a document title, or a labeled form field.' |

**Recognition**

*Deterministic — pattern plus corroborating context:*

- a labeled admission-date and discharge-date pair appearing as fields in the same header block, together with a named facility and either a discharge-disposition field or a discharge-instructions section heading
- an emergency or urgent-care visit record in which a labeled arrival time, a named facility and a labeled encounter identifier appear together

*Needs the LLM:*

- a discharge instruction sheet with no dates and no facility letterhead
- a personal account of a hospital stay written as prose or a journal entry
- an admission packet whose only structured content is consent forms

*Never alone — rejected as deterministic signals:*

- the word 'discharge', which is also an employment discharge, a battery discharge and an environmental discharge permit
- a hospital or medical-centre name — it appears as an employer, a research venue, a donation recipient, a birthplace and a cited affiliation, and the design's own rule is that §4.9: 'A university name alone should not create a group'
- the words 'admission' or 'admitted', which belong equally to university admissions
- an ICU, ER or ward abbreviation appearing in prose or dialogue

**Work types:** discharge summary, admission paperwork, emergency department record, consent to treat, discharge instructions, operative or procedure note copy, itemised episode statement

**Grouping reasons:** one admission across its paperwork, summary and instructions; one episode of care and the bills and claims that follow it

**Template:** `subject person → facility → episode → document type`

> §5.5: 'For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders.' The episode is the unit people actually retrieve; a discharge instruction is meaningless without knowing which stay it belongs to. §5.5: 'a parent dimension should provide the context required to understand the child'

**Collides with**

| Domain | Signal that separates them | Design cite |
|---|---|---|
| `med.provider-billing-dispute` | the same episode produces a clinical record and a bill; §4.8's rule that a packet must not silently absorb a conflicting document applies to keeping the financial and clinical halves distinguishable. | §4.8: 'an application packet does not silently absorb a document with a conflicting target institution' |
| `acad.college-application` | 'admission' is the shared token and means something entirely different on each side; only the paired admission/discharge date labels and a facility make it a clinical episode. | — |
| `med.surgical-procedure-record` | a surgical admission produces both; the operative report belongs to the surgical schema because it legitimises procedure-level fields this one must not claim. | §4.8: 'each fact or label belongs to an allowed domain schema' |

**Sensitivity:** `potentially_sensitive` — A named person's hospitalisation — 'potentially sensitive', which is §2.9's own phrase and the whole of what this field asserts. No handling class is set here; classification is P7's (§8.4).


### 8. `med.surgical-procedure-record` — Surgical and procedural records

A specific operation or invasive procedure: consent, operative report, implant documentation, and post-operative instructions.

**Provenance:** `proposal`  — the design names neither this domain nor any of its fields.

**Schema** — the fields this domain, and only this domain, legitimises:

| Field | Type | Example | Ceiling | Why |
|---|---|---|---|---|
| `subject_person` | string | self | `direct` | §3.8: 'The system must separate roles that happen to contain the same entity type.' |
| `procedure` | string | the labeled procedure-performed field | `direct` | §3.5: 'Deterministic extractors create direct facts when the information comes from a reliable, explicit source, such as a content hash, EXIF timestamp, a document title, or a labeled form field.' |
| `procedure_date` | date | the labeled date of operation | `direct` | §3.5: 'Deterministic extractors create direct facts when the information comes from a reliable, explicit source, such as a content hash, EXIF timestamp, a document title, or a labeled form field.' §3.10: 'The product must not use fuzzy date parsing' |
| `surgeon` | string | the operating clinician | `direct` | A role, and per §3.8: 'It should avoid using authorship or creator identity as a destination dimension.' it is not a folder dimension. |
| `facility` | string | the operating hospital or surgical centre | `direct` | §3.8: 'The system must separate roles that happen to contain the same entity type.' |
| `pre_operative_diagnosis` | string | the labeled pre-operative diagnosis field | `direct` | §3.5: 'Deterministic extractors create direct facts when the information comes from a reliable, explicit source, such as a content hash, EXIF timestamp, a document title, or a labeled form field.' |
| `post_operative_diagnosis` | string | the labeled post-operative diagnosis field | `direct` | §3.5: 'Deterministic extractors create direct facts when the information comes from a reliable, explicit source, such as a content hash, EXIF timestamp, a document title, or a labeled form field.' |
| `anaesthesia_type` | string | the labeled anaesthesia field | `direct` | §3.5: 'Deterministic extractors create direct facts when the information comes from a reliable, explicit source, such as a content hash, EXIF timestamp, a document title, or a labeled form field.' |
| `implanted_device` | string | the device recorded as implanted, where one is | `validated` | Confirmed by the implant-documentation rule; a device name in prose is not an implant fact. §3.13: 'A validated fact was found by a deterministic rule and passed contextual checks, such as a course-code pattern appearing beside “lecture,” “syllabus,” or “semester.”' |

**Recognition**

*Deterministic — pattern plus corroborating context:*

- an operative-report structure carrying a labeled pre-operative diagnosis and a labeled post-operative diagnosis as an adjacent pair, together with a named surgeon and a labeled procedure-performed field
- a surgical consent form in which a named procedure, a named operating clinician and a labeled subject identity appear as completed fields rather than as blank form text
- an implant or device card structure carrying a device identifier, a manufacturer and a labeled implant date together with a subject identity

*Needs the LLM:*

- post-operative instructions with no report and no consent attached
- a surgical quote or estimate, which is a financial document about a clinical event
- a person's own prose account of a procedure

*Never alone — rejected as deterministic signals:*

- a procedure name such as 'appendectomy' or 'colonoscopy' — patient-education leaflets, coursework, journalism and fiction carry them
- a blank consent form template, which carries every keyword and no facts
- the word 'surgery' in a filename
- an anatomical term in prose

**Work types:** operative report, surgical consent, pre-operative instruction, post-operative instruction, pathology report on the specimen, implant or device card, surgical estimate

**Grouping reasons:** one procedure across consent, report, pathology and follow-up; one surgical episode and the claims that follow it

**Template:** `subject person → procedure → document type`

> §5.5: 'For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders.' The procedure is the context that makes a consent or an instruction sheet interpretable. §5.5: 'a parent dimension should provide the context required to understand the child'

**Collides with**

| Domain | Signal that separates them | Design cite |
|---|---|---|
| `med.device-and-implant-record` | an implant card is held by the person and logged by the practice; the person's card is filed with the procedure that placed it, the practice's log is an asset record. | — |
| `med.hospital-admission-discharge` | a surgical admission generates both records; the operative report's diagnosis pair is the discriminator. | — |
| `legal.litigation-dispute` | an operative report is routinely a legal exhibit; the same file then carries both a clinical and a litigation purpose. | §3.9: 'Topic answers what a file is about, while purpose answers what the file was for.' |

**Sensitivity:** `potentially_sensitive` — An operation performed on a named person — 'potentially sensitive', which is §2.9's own phrase and the whole of what this field asserts. No handling class is set here; classification is P7's (§8.4).


### 9. `med.physical-therapy-rehab` — Physical therapy and rehabilitation

A course of physical, occupational, or speech therapy: the plan of care, the prescribed exercise programme, and progress notes.

**Provenance:** `proposal`  — the design names neither this domain nor any of its fields.

**Schema** — the fields this domain, and only this domain, legitimises:

| Field | Type | Example | Ceiling | Why |
|---|---|---|---|---|
| `subject_person` | string | self | `direct` | §3.8: 'The system must separate roles that happen to contain the same entity type.' |
| `therapist` | string | the treating therapist and their discipline | `direct` | §3.8: 'The system must separate roles that happen to contain the same entity type.' |
| `treating_diagnosis` | string | the labeled referring or treating diagnosis | `direct` | §3.5: 'Deterministic extractors create direct facts when the information comes from a reliable, explicit source, such as a content hash, EXIF timestamp, a document title, or a labeled form field.' |
| `plan_of_care_period` | string | the labeled authorisation or certification period as written | `direct` | Stored as the label's own value. §3.5: 'Deterministic extractors create direct facts when the information comes from a reliable, explicit source, such as a content hash, EXIF timestamp, a document title, or a labeled form field.' |
| `discipline` | string | physical, occupational or speech therapy as labeled | `validated` | §3.13: 'A validated fact was found by a deterministic rule and passed contextual checks, such as a course-code pattern appearing beside “lecture,” “syllabus,” or “semester.”' |
| `visit_date` | date | the labeled date of a session | `direct` | §3.5: 'Deterministic extractors create direct facts when the information comes from a reliable, explicit source, such as a content hash, EXIF timestamp, a document title, or a labeled form field.' §3.10: 'The product must not use fuzzy date parsing' |
| `home_programme` | string | the prescribed exercise set as labeled | `validated` | §3.13: 'A validated fact was found by a deterministic rule and passed contextual checks, such as a course-code pattern appearing beside “lecture,” “syllabus,” or “semester.”' |

**Recognition**

*Deterministic — pattern plus corroborating context:*

- a plan-of-care structure carrying a labeled treating or referring diagnosis, a named therapist with a therapy credential, and a labeled certification or authorisation period
- a progress-note structure in which a labeled visit date, a named therapist and a labeled treatment goal appear together

*Needs the LLM:*

- an exercise sheet with images and no therapist, no diagnosis and no clinic identity
- a person's own log of what they did each day
- a rehabilitation programme sent as an app export

*Never alone — rejected as deterministic signals:*

- an exercise-prescription table with sets, repetitions and frequency columns — a personal-training programme, a gym app export and a fitness magazine plan are all structurally identical, and this is the single most misleading pattern in the domain
- the words 'therapy', 'rehab', 'stretch' or 'exercise' in a filename
- an anatomical term next to a repetition count
- a clinic name alone

**Work types:** plan of care, progress note, home exercise programme, discharge summary from therapy, functional assessment, authorisation request

**Grouping reasons:** one course of therapy for one injury or condition; one authorisation period across its visits

**Template:** `subject person → condition or injury → document type`

> §5.5: 'For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders.' The condition is what makes a progress note or an exercise sheet retrievable years later. §5.5: 'a parent dimension should provide the context required to understand the child'

**Collides with**

| Domain | Signal that separates them | Design cite |
|---|---|---|
| `med.wearable-health-export` | an activity or workout log looks like a therapy adherence log; only the therapist, diagnosis and authorisation period make it clinical. | — |
| `pers.fitness-activity` | a coached training plan and a therapy home programme share their entire structure; the credentialed therapist and the referring diagnosis are the only reliable discriminators. | — |
| `med.insurance-claim-eob` | therapy authorisation and visit limits are payer artifacts that sit inside the clinical file. | — |

**Sensitivity:** `potentially_sensitive` — A named person's injury, function, and course of treatment — 'potentially sensitive', which is §2.9's own phrase and the whole of what this field asserts. No handling class is set here; classification is P7's (§8.4).


### 10. `med.mental-health-record` — Mental health and behavioural health records

A person's own therapy, counselling, or psychiatric records and the administrative artifacts around them.

**Provenance:** `proposal`  — the design names neither this domain nor any of its fields.

**Schema** — the fields this domain, and only this domain, legitimises:

| Field | Type | Example | Ceiling | Why |
|---|---|---|---|---|
| `subject_person` | string | self | `direct` | §3.8: 'The system must separate roles that happen to contain the same entity type.' |
| `treating_clinician` | string | the therapist, counsellor or psychiatrist | `direct` | §3.8: 'The system must separate roles that happen to contain the same entity type.' |
| `service_type` | string | the labeled service or modality as the document names it | `direct` | §3.5: 'Deterministic extractors create direct facts when the information comes from a reliable, explicit source, such as a content hash, EXIF timestamp, a document title, or a labeled form field.' |
| `session_date` | date | the labeled session or service date | `direct` | §3.5: 'Deterministic extractors create direct facts when the information comes from a reliable, explicit source, such as a content hash, EXIF timestamp, a document title, or a labeled form field.' §3.10: 'The product must not use fuzzy date parsing' |
| `practice` | string | the practice or clinic providing the service | `direct` | §3.8: 'The system must separate roles that happen to contain the same entity type.' |
| `authorisation_reference` | string | the labeled payer authorisation identifier | `direct` | §3.5: 'Deterministic extractors create direct facts when the information comes from a reliable, explicit source, such as a content hash, EXIF timestamp, a document title, or a labeled form field.' |

**Recognition**

*Deterministic — pattern plus corroborating context:*

- a superbill or statement structure from a named behavioural-health practice in which a labeled service date, a labeled service descriptor and a named treating clinician appear together
- an appointment or intake confirmation naming a practice, a subject identity and a labeled session date together

*Needs the LLM:*

- a personal journal, letter or note that discusses feelings and may or may not be part of a therapeutic record
- worksheets and handouts given in therapy, which are indistinguishable from self-help material bought online
- correspondence about care that names no practice

*Never alone — rejected as deterministic signals:*

- the name of a standardised screening instrument — psychology coursework, research papers and public screening tools all reproduce them, and a student's dataset is full of them
- condition vocabulary such as 'anxiety' or 'depression' anywhere in prose
- the words 'therapy', 'session', 'counselling' or 'therapist' in a filename
- a clinician name with a psychology or counselling credential suffix

**Work types:** superbill, appointment record, intake paperwork, treatment authorisation, therapy worksheet, clinician correspondence

**Grouping reasons:** one course of care with one practice; one authorisation period across its sessions

**Template:** `subject person → practice or provider → year`

> §5.5: 'For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders.'

**Collides with**

| Domain | Signal that separates them | Design cite |
|---|---|---|
| `pers.journal` | a private journal may be therapeutic material or may be an ordinary diary; nothing in the file distinguishes them, and reading further to decide is itself a privacy decision. | — |
| `res.survey-instrument` | instrument names and score sheets appear identically in coursework and research datasets. | — |
| `med.medical-certification-letter` | a clinician's letter supporting leave or accommodation is often the only mental-health artifact in a corpus and reaches an employer or a school. | — |

**Sensitivity:** `potentially_sensitive` — A named person's mental-health care — 'potentially sensitive', which is §2.9's own phrase and the whole of what this field asserts. No handling class is set here; classification is P7's (§8.4).

**Open question**

> Should the engine open the contents of a personal journal or diary at all in order to decide whether it is a mental-health record? Every deterministic route in this domain is administrative — bills, appointments, authorisations — and the content route requires reading private prose. §8.4 requires privacy policy to be enforced before content reaches any model; it does not say whether local extraction may read such a file in the first place. Joseph's call.


### 11. `med.dental-record` — Dental records

A person's dental care: charting, treatment plans, radiographs, and dental claims.

**Provenance:** `proposal`  — the design names neither this domain nor any of its fields.

**Schema** — the fields this domain, and only this domain, legitimises:

| Field | Type | Example | Ceiling | Why |
|---|---|---|---|---|
| `subject_person` | string | self | `direct` | §3.8: 'The system must separate roles that happen to contain the same entity type.' |
| `dental_practice` | string | the practice providing care | `direct` | §3.8: 'The system must separate roles that happen to contain the same entity type.' |
| `treating_dentist` | string | the dentist or hygienist of record | `direct` | §3.8: 'The system must separate roles that happen to contain the same entity type.' |
| `tooth_or_quadrant` | string | the labeled tooth or quadrant notation | `direct` | Read from the labeled notation. The charting-grid rule activates the domain; it does not confirm this value. a tooth number in prose is not a dental fact. §3.5: 'Deterministic extractors create direct facts when the information comes from a reliable, explicit source, such as a content hash, EXIF timestamp, a document title, or a labeled form field.' |
| `procedure` | string | the labeled procedure as recorded or claimed | `direct` | §3.5: 'Deterministic extractors create direct facts when the information comes from a reliable, explicit source, such as a content hash, EXIF timestamp, a document title, or a labeled form field.' |
| `service_date` | date | the labeled date of service | `direct` | §3.5: 'Deterministic extractors create direct facts when the information comes from a reliable, explicit source, such as a content hash, EXIF timestamp, a document title, or a labeled form field.' §3.10: 'The product must not use fuzzy date parsing' |
| `treatment_plan_phase` | string | the labeled phase or stage of a proposed plan | `direct` | §3.5: 'Deterministic extractors create direct facts when the information comes from a reliable, explicit source, such as a content hash, EXIF timestamp, a document title, or a labeled form field.' |

**Recognition**

*Deterministic — pattern plus corroborating context:*

- a dental charting grid in which per-tooth notation appears as a structured row or column set, together with a named dental practice
- a dental claim or treatment-plan structure in which a per-tooth or per-quadrant column co-occurs with a procedure column and a labeled service date

*Needs the LLM:*

- an orthodontic contract, which is a finance document about dental care
- an intraoral photograph with no accompanying chart
- a reminder or recall letter naming only the practice

*Never alone — rejected as deterministic signals:*

- the words 'dental', 'dentist' or 'teeth' in a filename
- a tooth number in prose, which is a bare numeric token
- a practice name alone
- a dental radiograph image with no charting or report

**Work types:** dental chart, treatment plan, dental radiograph, dental claim, periodontal assessment, orthodontic record, recall reminder

**Grouping reasons:** one treatment plan across its phases and visits; one practice's record set for one subject person

**Template:** `subject person → practice → treatment plan or year`

> §5.5: 'For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders.'

**Collides with**

| Domain | Signal that separates them | Design cite |
|---|---|---|
| `med.imaging-radiology` | dental radiographs are imaging studies but carry tooth-level fields the general imaging schema does not legitimise. | §4.8: 'each fact or label belongs to an allowed domain schema' |
| `med.insurance-claim-eob` | dental benefits are usually a separate plan with a separate payer, and the claim is filed on a dental-specific form. | — |
| `fin.loan-mortgage` | an orthodontic contract is a credit agreement whose subject happens to be dental treatment. | — |

**Sensitivity:** `potentially_sensitive` — A named person's dental treatment — 'potentially sensitive', which is §2.9's own phrase and the whole of what this field asserts. No handling class is set here; classification is P7's (§8.4).


### 12. `med.vision-eyecare-record` — Vision and eye care records

Eye examinations, spectacle and contact-lens prescriptions, and ophthalmic treatment records.

**Provenance:** `proposal`  — the design names neither this domain nor any of its fields.

**Schema** — the fields this domain, and only this domain, legitimises:

| Field | Type | Example | Ceiling | Why |
|---|---|---|---|---|
| `subject_person` | string | self | `direct` | §3.8: 'The system must separate roles that happen to contain the same entity type.' |
| `prescribing_clinician` | string | the optometrist or ophthalmologist | `direct` | §3.8: 'The system must separate roles that happen to contain the same entity type.' |
| `practice` | string | the eye-care practice or dispensary | `direct` | §3.8: 'The system must separate roles that happen to contain the same entity type.' |
| `exam_date` | date | the labeled examination date | `direct` | §3.5: 'Deterministic extractors create direct facts when the information comes from a reliable, explicit source, such as a content hash, EXIF timestamp, a document title, or a labeled form field.' §3.10: 'The product must not use fuzzy date parsing' |
| `prescription_expiry` | date | the labeled expiry date | `direct` | §3.5: 'Deterministic extractors create direct facts when the information comes from a reliable, explicit source, such as a content hash, EXIF timestamp, a document title, or a labeled form field.' |
| `correction_type` | string | spectacle, contact lens, or both as labeled | `validated` | §3.13: 'A validated fact was found by a deterministic rule and passed contextual checks, such as a course-code pattern appearing beside “lecture,” “syllabus,” or “semester.”' |
| `refraction_values` | string | the per-eye refraction row as written | `direct` | Read from the labeled table, stored as written. §3.5: 'Deterministic extractors create direct facts when the information comes from a reliable, explicit source, such as a content hash, EXIF timestamp, a document title, or a labeled form field.' |

**Recognition**

*Deterministic — pattern plus corroborating context:*

- a refraction table in which sphere, cylinder and axis column labels co-occur with per-eye row labels, together with a named prescribing clinician or dispensing practice
- a contact-lens prescription structure carrying per-eye base-curve and diameter column labels together with a labeled expiry date

*Needs the LLM:*

- an optical receipt for frames, which is a purchase with a clinical attachment
- a photograph of a prescription card with partial OCR
- a letter about a treatment plan for an eye condition

*Never alone — rejected as deterministic signals:*

- the words 'vision', 'eye', 'glasses' or 'optical' in a filename — 'vision' is also a product, strategy and company word
- a practice or optical-chain name alone
- an expiry date alone

**Work types:** spectacle prescription, contact-lens prescription, eye examination report, visual field or retinal imaging report, optical receipt, ophthalmic treatment plan

**Grouping reasons:** one examination and the prescription it produced; one course of ophthalmic treatment

**Template:** `subject person → record type → exam year`

> §5.5: 'For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders.'

**Collides with**

| Domain | Signal that separates them | Design cite |
|---|---|---|
| `med.imaging-radiology` | retinal and field imaging are imaging studies reported inside eye-care records. | — |
| `fin.receipts-expenses` | the optical purchase and the clinical prescription usually arrive in the same envelope. | — |

**Sensitivity:** `potentially_sensitive` — A named person's eye examination and correction — 'potentially sensitive', which is §2.9's own phrase and the whole of what this field asserts. No handling class is set here; classification is P7's (§8.4).


### 13. `med.allergy-intolerance-record` — Allergy and intolerance records

Documented allergies, intolerances, and the testing and emergency planning around them.

**Provenance:** `proposal`  — the design names neither this domain nor any of its fields.

**Schema** — the fields this domain, and only this domain, legitimises:

| Field | Type | Example | Ceiling | Why |
|---|---|---|---|---|
| `subject_person` | string | self | `direct` | §3.8: 'The system must separate roles that happen to contain the same entity type.' |
| `allergen` | string | the substance recorded, as labeled | `validated` | Confirmed by the allergy-list rule; a food or drug name in prose is not an allergy fact. §3.13: 'A validated fact was found by a deterministic rule and passed contextual checks, such as a course-code pattern appearing beside “lecture,” “syllabus,” or “semester.”' |
| `reaction` | string | the labeled reaction field | `direct` | §3.5: 'Deterministic extractors create direct facts when the information comes from a reliable, explicit source, such as a content hash, EXIF timestamp, a document title, or a labeled form field.' |
| `documenting_clinician` | string | the clinician who recorded it | `direct` | §3.8: 'The system must separate roles that happen to contain the same entity type.' |
| `onset_or_documented_date` | date | the labeled date | `direct` | §3.5: 'Deterministic extractors create direct facts when the information comes from a reliable, explicit source, such as a content hash, EXIF timestamp, a document title, or a labeled form field.' §3.10: 'The product must not use fuzzy date parsing' |
| `emergency_plan` | string | the labeled action-plan document, where one exists | `direct` | §3.5: 'Deterministic extractors create direct facts when the information comes from a reliable, explicit source, such as a content hash, EXIF timestamp, a document title, or a labeled form field.' |

**Recognition**

*Deterministic — pattern plus corroborating context:*

- an allergy-list structure in which an allergen column co-occurs with a reaction column and either a documenting clinician or a documented-date column, inside a record carrying a subject identity
- an allergy-testing report in which a per-allergen result table co-occurs with a named performing laboratory or allergy practice

*Needs the LLM:*

- an emergency action plan on a school or camp form
- a note a person keeps listing what they cannot eat
- a restaurant or travel card stating dietary restrictions

*Never alone — rejected as deterministic signals:*

- a food or substance name — recipes, shopping lists, menus, ingredient labels and nutrition coursework are full of them
- the word 'allergy' or 'allergic' in prose or a filename
- a reaction word such as 'rash' or 'swelling'

**Work types:** allergy list, allergy testing report, emergency action plan, immunotherapy schedule, dietary restriction card

**Grouping reasons:** one subject person's allergy record set; one testing episode and the plan that followed it

**Template:** `subject person → record type`

> §5.5: 'For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders.' The set is small; depth beyond the subject person usually produces the single-child level §5.9 warns about. §5.9: 'It should warn when a level produces only one child'

**Collides with**

| Domain | Signal that separates them | Design cite |
|---|---|---|
| `med.personal-health-record` | an allergy list is most often a section inside a larger record rather than a standalone file, and the domain exists chiefly so `allergen` and `reaction` are legal fields somewhere. | — |
| `acad.k12-schooling` | a child's allergy action plan is filed with school paperwork and is required by the school. | — |
| `pers.recipe-meal` | the same substance names appear with no clinical meaning at all. | — |

**Sensitivity:** `potentially_sensitive` — A named person's allergies — 'potentially sensitive', which is §2.9's own phrase and the whole of what this field asserts. No handling class is set here; classification is P7's (§8.4).


### 14. `med.chronic-condition-management` — Chronic condition management

The ongoing self-management of a diagnosed long-term condition: care plans, monitoring logs, and review appointments.

**Provenance:** `proposal`  — the design names neither this domain nor any of its fields.

**Schema** — the fields this domain, and only this domain, legitimises:

| Field | Type | Example | Ceiling | Why |
|---|---|---|---|---|
| `subject_person` | string | self | `direct` | §3.8: 'The system must separate roles that happen to contain the same entity type.' |
| `condition` | string | the diagnosed condition the plan addresses, as labeled | `validated` | A condition fact only where a clinician-issued plan names it in a labeled field. §3.13: 'A validated fact was found by a deterministic rule and passed contextual checks, such as a course-code pattern appearing beside “lecture,” “syllabus,” or “semester.”' |
| `care_plan_issuer` | string | the clinician or service that issued the plan | `direct` | §3.8: 'The system must separate roles that happen to contain the same entity type.' |
| `monitoring_measure` | string | the labeled measure the log records | `direct` | §3.5: 'Deterministic extractors create direct facts when the information comes from a reliable, explicit source, such as a content hash, EXIF timestamp, a document title, or a labeled form field.' |
| `review_date` | date | the labeled review or recall date | `direct` | §3.5: 'Deterministic extractors create direct facts when the information comes from a reliable, explicit source, such as a content hash, EXIF timestamp, a document title, or a labeled form field.' §3.10: 'The product must not use fuzzy date parsing' |
| `plan_period` | string | the labeled period the plan covers, as written | `direct` | §3.5: 'Deterministic extractors create direct facts when the information comes from a reliable, explicit source, such as a content hash, EXIF timestamp, a document title, or a labeled form field.' |

**Recognition**

*Deterministic — pattern plus corroborating context:*

- a care-plan structure in which a labeled condition field, a named issuing clinician or service and a labeled review or recall date appear together
- a monitoring log whose column headers pair a labeled clinical measure with a labeled target or reference band supplied by a named clinician or device programme

*Needs the LLM:*

- a self-kept spreadsheet of readings with no clinician, no target band and no plan
- educational material about a condition that a person has kept because they have it
- correspondence adjusting a treatment

*Never alone — rejected as deterministic signals:*

- a condition name such as 'diabetes' or 'hypertension' — advocacy, journalism, coursework, insurance marketing and fundraising all name conditions constantly
- a per-reading table of a measure and a timestamp, which is the exact shape of a fitness, nutrition or sleep log
- a vital-sign-shaped value such as a blood-pressure pair or a weight
- the words 'log', 'tracker' or 'readings' in a filename

**Work types:** care plan, monitoring log, review summary, self-management education material, device or meter export, specialist review letter

**Grouping reasons:** one condition's plan, logs and reviews across time; one review cycle

**Template:** `subject person → condition → document type`

> §5.5: 'For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders.' The condition is the retrieval key; a log is meaningless without it. §5.5: 'a parent dimension should provide the context required to understand the child'

**Collides with**

| Domain | Signal that separates them | Design cite |
|---|---|---|
| `med.wearable-health-export` | a device export and a clinician-directed monitoring log are the same table; only a clinician-supplied target band or an issuing care plan separates them. | — |
| `pers.fitness-activity` | weight, sleep and activity logs are kept by people with no clinical involvement whatsoever. | — |
| `med.lab-result` | monitoring measures are often lab values; the log is the person's, the result is the laboratory's. | — |

**Sensitivity:** `potentially_sensitive` — An ongoing condition and the readings taken for it — 'potentially sensitive', which is §2.9's own phrase and the whole of what this field asserts. No handling class is set here; classification is P7's (§8.4).

**Open question**

> Should a condition ever appear as a literal folder name in a proposed tree? A branch named for a diagnosis is legible to anyone who opens the file manager or sees a shared screen — §8.4 already makes this point for filenames, noting that a summary may be safe to show where a visible list of filenames is not. Whether the same reasoning forbids condition-named folders is a product decision about someone's real life, and is Joseph's.


### 15. `med.pregnancy-maternity-record` — Pregnancy and maternity records

Antenatal, birth, and postnatal care records for one pregnancy.

**Provenance:** `proposal`  — the design names neither this domain nor any of its fields.

**Schema** — the fields this domain, and only this domain, legitimises:

| Field | Type | Example | Ceiling | Why |
|---|---|---|---|---|
| `subject_person` | string | self | `direct` | §3.8: 'The system must separate roles that happen to contain the same entity type.' |
| `care_provider` | string | the obstetric practice, midwifery service or clinician | `direct` | §3.8: 'The system must separate roles that happen to contain the same entity type.' |
| `visit_date` | date | the labeled appointment or scan date | `direct` | §3.5: 'Deterministic extractors create direct facts when the information comes from a reliable, explicit source, such as a content hash, EXIF timestamp, a document title, or a labeled form field.' §3.10: 'The product must not use fuzzy date parsing' |
| `gestational_dating` | string | the labeled dating or gestation field, stored as written | `direct` | Read from a labeled field only; the catalogue computes nothing and asserts no timeline. §3.5: 'Deterministic extractors create direct facts when the information comes from a reliable, explicit source, such as a content hash, EXIF timestamp, a document title, or a labeled form field.' |
| `care_setting` | string | the planned or actual place of birth, where labeled | `direct` | §3.8: 'The system must separate roles that happen to contain the same entity type.' |
| `record_type` | string | antenatal, intrapartum or postnatal as the record labels it | `validated` | §3.13: 'A validated fact was found by a deterministic rule and passed contextual checks, such as a course-code pattern appearing beside “lecture,” “syllabus,” or “semester.”' |

**Recognition**

*Deterministic — pattern plus corroborating context:*

- an antenatal record structure in which a labeled gestational-dating field, a named obstetric or midwifery provider and a labeled visit date appear together
- an obstetric imaging report in which an obstetric study descriptor co-occurs with a labeled study date and a named reporting clinician

*Needs the LLM:*

- a birth plan written by the person themselves
- an ultrasound image saved without its report
- correspondence about a pregnancy that names no provider

*Never alone — rejected as deterministic signals:*

- the words 'pregnancy', 'baby', 'due date', 'maternity' or 'ultrasound' — pregnancy-tracking apps, parenting blogs, retail marketing, baby-shower planning and fiction all use them freely
- a scan image with no report
- a date labeled 'due'
- a tracking-app export

**Work types:** antenatal record, obstetric scan report, screening result, birth plan, birth record, postnatal check, discharge summary

**Grouping reasons:** one pregnancy across its antenatal, birth and postnatal records

**Template:** `subject person → record type`

> Deliberately shallow. §5.5: 'For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders.' applies, but any deeper default here would encode an assumption about an outcome the files do not state.

**Collides with**

| Domain | Signal that separates them | Design cite |
|---|---|---|
| `med.paediatric-child-health` | birth records straddle both subjects — one file is simultaneously the parent's maternity record and the child's earliest health record, with two different subject persons. | §3.8: 'The system must separate roles that happen to contain the same entity type.' |
| `med.imaging-radiology` | obstetric scans are imaging studies reported inside maternity care. | — |
| `pers.photo-occasion` | scan images are kept as photographs as often as they are kept as records. | — |

**Sensitivity:** `potentially_sensitive` — Pregnancy and birth records for a named person — 'potentially sensitive', which is §2.9's own phrase and the whole of what this field asserts. No handling class is set here; classification is P7's (§8.4).

**Open question**

> This domain must not be given a default folder shape by the catalogue. A branch keyed on a due date, a child's name, or a pregnancy count encodes an assumption about an outcome — a pregnancy may have ended, may be one of several, or may be one the person does not want surfaced. The catalogue therefore proposes only `subject_person` and `record_type` and states plainly that any deeper default is Joseph's decision to make deliberately, not the catalogue's to assume.


### 16. `med.paediatric-child-health` — A child's health records held by a parent or guardian

Health records whose subject is a dependent child and whose holder is the parent or guardian.

**Provenance:** `proposal`  — the design names neither this domain nor any of its fields.

**Schema** — the fields this domain, and only this domain, legitimises:

| Field | Type | Example | Ceiling | Why |
|---|---|---|---|---|
| `subject_person` | string | the named child | `direct` | The subject is not the holder. This is the clearest case of §3.8: 'The system must separate roles that happen to contain the same entity type.' |
| `guardian` | string | the parent or guardian named on the record | `direct` | A distinct role from the subject; it is also authorship-like and per §3.8: 'It should avoid using authorship or creator identity as a destination dimension.' must not become a folder level on its own. |
| `paediatric_practice` | string | the practice or service providing care | `direct` | §3.8: 'The system must separate roles that happen to contain the same entity type.' |
| `visit_date` | date | the labeled visit date | `direct` | §3.5: 'Deterministic extractors create direct facts when the information comes from a reliable, explicit source, such as a content hash, EXIF timestamp, a document title, or a labeled form field.' §3.10: 'The product must not use fuzzy date parsing' |
| `record_type` | string | well-child check, growth record, screening or referral as labeled | `validated` | §3.13: 'A validated fact was found by a deterministic rule and passed contextual checks, such as a course-code pattern appearing beside “lecture,” “syllabus,” or “semester.”' |
| `school_or_programme_requirement` | string | the institution the record was produced for, where labeled | `direct` | An organisation role that belongs to the requesting institution, not to the clinical provider. §3.8: 'The system must separate roles that happen to contain the same entity type.' |

**Recognition**

*Deterministic — pattern plus corroborating context:*

- a well-child or growth-record structure carrying a labeled child identity, a named guardian and a named paediatric practice together
- a school or programme health form in which a completed clinician attestation block co-occurs with a named child and a named institution

*Needs the LLM:*

- a note about a child's symptoms kept by a parent
- a nursery or camp form partly completed
- correspondence in which the child subject must be inferred from prose

*Never alone — rejected as deterministic signals:*

- a child's name in a filename
- the words 'kids', 'child' or a paediatric practice name
- a growth or percentile chart, which is also a data exercise in coursework and a chart in a parenting article
- a blank school health form

**Work types:** well-child record, growth record, school health form, developmental screening, paediatric referral, immunisation form

**Grouping reasons:** one child's record set; one school year's required forms

**Template:** `subject person → record type → year`

> §5.5: 'For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders.' The child is the only dimension that makes the rest legible in a household with more than one. §5.5: 'a parent dimension should provide the context required to understand the child'

**Collides with**

| Domain | Signal that separates them | Design cite |
|---|---|---|
| `acad.k12-schooling` | a school health form is required by a school and filed with enrolment paperwork; it is simultaneously an educational and a clinical artifact. | §3.9: 'The documents are content-incoherent but purpose-coherent.' |
| `med.immunisation-record` | school immunisation requirements are the most common reason a child's immunisation record exists as a file at all. | — |
| `med.caregiving-dependant` | both are records about someone other than the holder; the schemas are kept apart because a child's record legitimises guardian and school-requirement fields an adult dependant's does not. | §4.8: 'each fact or label belongs to an allowed domain schema' |

**Sensitivity:** `potentially_sensitive` — A named child's health records — 'potentially sensitive', which is §2.9's own phrase and the whole of what this field asserts. No handling class is set here; classification is P7's (§8.4).


### 17. `med.caregiving-dependant` — Caregiving for a dependent adult

Records held by a carer about another adult's health and care: care coordination, facility arrangements, and authority to act.

**Provenance:** `proposal`  — the design names neither this domain nor any of its fields.

**Schema** — the fields this domain, and only this domain, legitimises:

| Field | Type | Example | Ceiling | Why |
|---|---|---|---|---|
| `subject_person` | string | the person being cared for | `direct` | The holder is not the subject and is not the patient. §3.8: 'The system must separate roles that happen to contain the same entity type.' |
| `carer` | string | the person holding and acting on the record | `direct` | §3.8: 'The system must separate roles that happen to contain the same entity type.' |
| `authority_instrument` | string | the named instrument granting authority to act, where one exists | `validated` | §3.13: 'A validated fact was found by a deterministic rule and passed contextual checks, such as a course-code pattern appearing beside “lecture,” “syllabus,” or “semester.”' |
| `care_service` | string | the agency, facility or programme providing care | `direct` | §3.8: 'The system must separate roles that happen to contain the same entity type.' |
| `care_period` | string | the labeled period a placement or package covers, as written | `direct` | §3.5: 'Deterministic extractors create direct facts when the information comes from a reliable, explicit source, such as a content hash, EXIF timestamp, a document title, or a labeled form field.' |
| `coordination_contact` | string | the named case manager or coordinator | `direct` | §3.8: 'The system must separate roles that happen to contain the same entity type.' |

**Recognition**

*Deterministic — pattern plus corroborating context:*

- an instrument naming a principal and an attorney or agent for health decisions, carrying a witness or notary attestation block
- a care-facility admission or service agreement in which a named resident or client, a named facility and a labeled service period appear together

*Needs the LLM:*

- notes a carer keeps about appointments and medications for someone else
- correspondence with a service in which the subject must be inferred
- a benefits application whose subject is the cared-for person

*Never alone — rejected as deterministic signals:*

- the words 'care', 'carer' or 'caregiver' in a filename
- a second person's name appearing in a medical document, which is also how clinicians, next of kin and emergency contacts appear
- a facility name alone

**Work types:** care plan, facility agreement, health power of attorney, care assessment, service correspondence, benefits application

**Grouping reasons:** one cared-for person's record set; one placement across its agreement, assessments and correspondence

**Template:** `subject person → record type`

> §5.5: 'For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders.' The cared-for person is the only workable first dimension, because every other dimension repeats across the people a carer looks after. §5.5: 'a parent dimension should provide the context required to understand the child'

**Collides with**

| Domain | Signal that separates them | Design cite |
|---|---|---|
| `med.advance-directive` | a health power of attorney is both the authority a carer acts under and the cared-for person's own directive. | — |
| `legal.power-of-attorney` | powers of attorney, guardianship and deputyship are legal instruments whose subject matter is health. | — |
| `med.personal-health-record` | the carer's own records and the cared-for person's records sit in the same corpus and are separated only by `subject_person`. | §3.8: 'The system must separate roles that happen to contain the same entity type.' |

**Sensitivity:** `potentially_sensitive` — Another person's health and care arrangements — 'potentially sensitive', which is §2.9's own phrase and the whole of what this field asserts. No handling class is set here; classification is P7's (§8.4).

**Open question**

> When a corpus contains records for several people, does `subject_person` become a top-level branch, a dimension inside a single medical branch, or a facet that is never a folder at all? §3.8 forbids using authorship or creator identity as a destination dimension, but the cared-for person is a subject, not an author, and for a carer it is the only structure that works. The catalogue proposes it as the first dimension and flags that the decision is Joseph's.


### 18. `med.advance-directive` — Advance directives and end-of-life instructions

Instruments stating a person's wishes for care and who may decide for them.

**Provenance:** `proposal`  — the design names neither this domain nor any of its fields.

**Schema** — the fields this domain, and only this domain, legitimises:

| Field | Type | Example | Ceiling | Why |
|---|---|---|---|---|
| `subject_person` | string | the principal | `direct` | §3.8: 'The system must separate roles that happen to contain the same entity type.' |
| `instrument_type` | string | the named instrument as titled | `validated` | Confirmed from the document's own title or heading, not from a mention elsewhere. §3.13: 'A validated fact was found by a deterministic rule and passed contextual checks, such as a course-code pattern appearing beside “lecture,” “syllabus,” or “semester.”' |
| `designated_agent` | string | the named health agent or proxy | `direct` | A role distinct from the principal and from any witness. §3.8: 'The system must separate roles that happen to contain the same entity type.' |
| `execution_date` | date | the labeled date executed | `direct` | §3.5: 'Deterministic extractors create direct facts when the information comes from a reliable, explicit source, such as a content hash, EXIF timestamp, a document title, or a labeled form field.' §3.10: 'The product must not use fuzzy date parsing' |
| `jurisdiction` | string | the jurisdiction whose form is used, where the form states it | `direct` | §3.5: 'Deterministic extractors create direct facts when the information comes from a reliable, explicit source, such as a content hash, EXIF timestamp, a document title, or a labeled form field.' |
| `witness_or_notary` | string | the attestation block as recorded | `direct` | §3.5: 'Deterministic extractors create direct facts when the information comes from a reliable, explicit source, such as a content hash, EXIF timestamp, a document title, or a labeled form field.' |
| `registered_with` | string | any registry or facility holding a filed copy, where labeled | `direct` | §3.8: 'The system must separate roles that happen to contain the same entity type.' |

**Recognition**

*Deterministic — pattern plus corroborating context:*

- a document whose own title or first heading names a health-specific instrument, together with a principal-and-agent designation structure or a completed witness or notary attestation block
- a clinician-signed portable treatment-order form carrying a named subject, a signing clinician and a labeled execution date

*Needs the LLM:*

- a letter to family stating wishes with no instrument structure
- a blank form downloaded and never completed
- a will that contains health instructions inside a broader estate document

*Never alone — rejected as deterministic signals:*

- the phrase 'power of attorney', which is far more often financial or general
- the words 'will', 'directive' or 'wishes'
- a notary block, which appears on affidavits, deeds and consents of every kind
- a jurisdiction name

**Work types:** advance directive, living will, health power of attorney, healthcare proxy designation, portable treatment order, registry confirmation

**Grouping reasons:** one instrument across its executed copy, witnesses and filed confirmations; one person's directive set across revisions

**Template:** `subject person → instrument type → version`

> §5.5: 'For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders.' Which instrument it is governs everything else, and superseded versions must remain distinguishable from the current one. §5.5: 'a parent dimension should provide the context required to understand the child'

**Collides with**

| Domain | Signal that separates them | Design cite |
|---|---|---|
| `legal.wills-trusts-estates` | a living will and a last will are executed together, look alike, and are filed together; only the health-specific instrument name separates them. | — |
| `med.caregiving-dependant` | the same instrument is the principal's directive and the agent's authority. | — |
| `pers.identity-document` | both are rare, high-consequence documents; §4.9 already says such files may be surfaced as protected records even outside normal grouping. | §4.9: 'Rare but sensitive files such as passports, visas, and legal documents may be surfaced as protected records even when they do not meet a normal group-size threshold.' |

**Sensitivity:** `potentially_sensitive` — A person's instructions for their own care and who may decide for them — 'potentially sensitive', which is §2.9's own phrase and the whole of what this field asserts. No handling class is set here; classification is P7's (§8.4).


### 19. `med.genetic-testing-report` — Genetic and genomic test reports

Clinical genetic results and consumer genomics exports about a person, and the family history assembled around them.

**Provenance:** `proposal`  — the design names neither this domain nor any of its fields.

**Schema** — the fields this domain, and only this domain, legitimises:

| Field | Type | Example | Ceiling | Why |
|---|---|---|---|---|
| `subject_person` | string | self | `direct` | §3.8: 'The system must separate roles that happen to contain the same entity type.' |
| `test` | string | the named panel or assay | `validated` | §3.13: 'A validated fact was found by a deterministic rule and passed contextual checks, such as a course-code pattern appearing beside “lecture,” “syllabus,” or “semester.”' |
| `gene_or_region` | string | the gene or region reported on, as labeled | `validated` | Legal only inside this domain; an ordinary panel result must not be able to claim it. §4.8: 'each fact or label belongs to an allowed domain schema' |
| `interpretation` | string | the report's own labeled classification or interpretation | `direct` | Stored as the report states it; the catalogue supplies no clinical meaning of its own. §3.5: 'Deterministic extractors create direct facts when the information comes from a reliable, explicit source, such as a content hash, EXIF timestamp, a document title, or a labeled form field.' |
| `reporting_laboratory` | string | the laboratory issuing the report | `direct` | §3.8: 'The system must separate roles that happen to contain the same entity type.' |
| `ordering_provider` | string | the clinician or genetic counsellor who ordered it | `direct` | §3.8: 'The system must separate roles that happen to contain the same entity type.' |
| `collection_date` | date | the labeled specimen collection date | `direct` | §3.5: 'Deterministic extractors create direct facts when the information comes from a reliable, explicit source, such as a content hash, EXIF timestamp, a document title, or a labeled form field.' §3.10: 'The product must not use fuzzy date parsing' |
| `export_source` | string | the consumer platform that produced a raw-data export | `direct` | Read from the export's own header or manifest. §3.5: 'Deterministic extractors create direct facts when the information comes from a reliable, explicit source, such as a content hash, EXIF timestamp, a document title, or a labeled form field.' |

**Recognition**

*Deterministic — pattern plus corroborating context:*

- a variant-reporting structure in which a gene or region column co-occurs with an interpretation or classification column, together with a named reporting laboratory and a labeled specimen or collection descriptor
- a consumer genomics raw-data export carrying that platform's own file header or manifest format together with a labeled account or sample identity

*Needs the LLM:*

- a genetic counselling letter written as prose
- a family history diagram a person drew themselves
- a variant table with no interpretation column and no reporting laboratory — research output and clinical output are otherwise identical

*Never alone — rejected as deterministic signals:*

- a gene symbol, which is a short uppercase token that collides with tickers, acronyms and identifiers, and which appears throughout biology coursework and the research literature — §3.7: 'It should use word-boundary matching rather than substring matching.' applies with particular force
- a variant-notation-shaped string
- the words 'DNA', 'genome' or 'genetic' in a filename
- a sequence data file, whose format says nothing about whether its subject is a person or a specimen

**Work types:** clinical genetic report, carrier or pharmacogenomic report, consumer genomics export, genetic counselling letter, family history record, variant reanalysis notice

**Grouping reasons:** one test across its report, counselling letter and reanalysis notices; one family's shared result set

**Template:** `subject person → test → document type`

> §5.5: 'For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders.'

**Collides with**

| Domain | Signal that separates them | Design cite |
|---|---|---|
| `res.dataset` | the file formats are the same and the vocabulary is the same; a reporting laboratory and a clinical interpretation column are the only reliable clinical markers. | — |
| `med.lab-result` | a genetic report is a laboratory report; it is separated so that gene and interpretation fields are legal only where they belong. | §4.8: 'each fact or label belongs to an allowed domain schema' |
| `pers.genealogy` | consumer genomics exports are kept for ancestry as often as for health, and the same file serves both purposes. | §3.9: 'Topic answers what a file is about, while purpose answers what the file was for.' |

**Sensitivity:** `potentially_sensitive` — Genetic results, which concern the person and their relatives — 'potentially sensitive', which is §2.9's own phrase and the whole of what this field asserts. No handling class is set here; classification is P7's (§8.4).


### 20. `med.clinical-trial-participation` — Clinical trial participation as a subject

A person's own record of taking part in a study: consent, visit schedules, subject identity, and reimbursements.

**Provenance:** `proposal`  — the design names neither this domain nor any of its fields.

**Schema** — the fields this domain, and only this domain, legitimises:

| Field | Type | Example | Ceiling | Why |
|---|---|---|---|---|
| `subject_person` | string | self | `direct` | §3.8: 'The system must separate roles that happen to contain the same entity type.' |
| `trial` | string | the study as titled or registered | `validated` | §3.13: 'A validated fact was found by a deterministic rule and passed contextual checks, such as a course-code pattern appearing beside “lecture,” “syllabus,” or “semester.”' |
| `registration_identifier` | string | the trial's labeled registry identifier | `direct` | §3.5: 'Deterministic extractors create direct facts when the information comes from a reliable, explicit source, such as a content hash, EXIF timestamp, a document title, or a labeled form field.' |
| `sponsor` | string | the study sponsor | `direct` | §3.8: 'The system must separate roles that happen to contain the same entity type.' |
| `principal_investigator` | string | the investigator named on the consent | `direct` | §3.8: 'The system must separate roles that happen to contain the same entity type.' |
| `site` | string | the participating site | `direct` | §3.8: 'The system must separate roles that happen to contain the same entity type.' |
| `subject_identifier` | string | the participant identifier assigned to the person | `direct` | A labeled field, never a bare code found in text. §3.5: 'Deterministic extractors create direct facts when the information comes from a reliable, explicit source, such as a content hash, EXIF timestamp, a document title, or a labeled form field.' |
| `consent_version` | string | the labeled consent document version as written | `direct` | §3.5: 'Deterministic extractors create direct facts when the information comes from a reliable, explicit source, such as a content hash, EXIF timestamp, a document title, or a labeled form field.' |
| `visit_date` | date | the labeled study visit date | `direct` | §3.5: 'Deterministic extractors create direct facts when the information comes from a reliable, explicit source, such as a content hash, EXIF timestamp, a document title, or a labeled form field.' §3.10: 'The product must not use fuzzy date parsing' |

**Recognition**

*Deterministic — pattern plus corroborating context:*

- an informed-consent document in which a named sponsor, a named principal investigator and a signature-and-date block for the participant appear together
- a study document carrying a labeled registry identifier field together with a labeled participant identifier assigned to the holder

*Needs the LLM:*

- a recruitment advertisement a person kept
- a visit schedule with no study title
- a reimbursement receipt whose connection to the study is only contextual

*Never alone — rejected as deterministic signals:*

- a trial registration identifier, which appears in every paper, protocol, grant and news story about the study
- the words 'study', 'trial', 'protocol' or 'consent' — research consent, photo releases, school permissions and cookie banners all use 'consent'
- a sponsor or pharmaceutical company name
- a subject-code-shaped string

**Work types:** informed consent, participant information sheet, visit schedule, study diary, reimbursement record, results notification, withdrawal letter

**Grouping reasons:** one trial across its consent, schedule and visits; one participation period

**Template:** `subject person → trial → document type`

> §5.5: 'For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders.' The trial is the packet identity; a visit schedule is unreadable without it. §5.5: 'a parent dimension should provide the context required to understand the child'

**Collides with**

| Domain | Signal that separates them | Design cite |
|---|---|---|
| `res.clinical-trial` | the same study produces investigator-side files; the discriminator is whether the holder is the subject or the researcher, and a signed participant consent is the clearest marker. | §3.8: 'The system must separate roles that happen to contain the same entity type.' |
| `med.clinician-clinical-note` | study visits generate clinical records inside the trial rather than inside ordinary care. | — |
| `biz.expense-report` | participation stipends arrive as ordinary payment records. | — |

**Sensitivity:** `potentially_sensitive` — Participation in a study, which discloses a condition or an eligibility — 'potentially sensitive', which is §2.9's own phrase and the whole of what this field asserts. No handling class is set here; classification is P7's (§8.4).


### 21. `med.medical-travel` — Travel for medical care

A trip taken to receive treatment: the clinical arrangements and the travel arrangements kept together as one purpose-coherent packet.

**Provenance:** `inference`  
**Design cite:** §3.3 names 'travel record' among the domains the LLM may recognise; §3.9 supplies the packet mechanism: 'The documents are content-incoherent but purpose-coherent.' This entry extends those two named things to a medical purpose; the design names no medical-travel domain.

**Schema** — the fields this domain, and only this domain, legitimises:

| Field | Type | Example | Ceiling | Why |
|---|---|---|---|---|
| `subject_person` | string | self | `direct` | §3.8: 'The system must separate roles that happen to contain the same entity type.' |
| `treating_facility` | string | the facility abroad or away from home | `direct` | §3.8: 'The system must separate roles that happen to contain the same entity type.' |
| `procedure_or_treatment` | string | the treatment the trip is for, as labeled | `validated` | §3.13: 'A validated fact was found by a deterministic rule and passed contextual checks, such as a course-code pattern appearing beside “lecture,” “syllabus,” or “semester.”' |
| `travel_dates` | date | the labeled departure and return dates | `direct` | §3.5: 'Deterministic extractors create direct facts when the information comes from a reliable, explicit source, such as a content hash, EXIF timestamp, a document title, or a labeled form field.' §3.10: 'The product must not use fuzzy date parsing' |
| `destination` | string | the place of treatment | `direct` | §3.5: 'Deterministic extractors create direct facts when the information comes from a reliable, explicit source, such as a content hash, EXIF timestamp, a document title, or a labeled form field.' |
| `purpose` | string | medical travel | `llm_supported` | Purpose is what holds the packet together, and it is exactly what rules cannot see. §3.9: 'Topic answers what a file is about, while purpose answers what the file was for.' |
| `coordinating_service` | string | any facilitator or medical-travel agency | `direct` | §3.8: 'The system must separate roles that happen to contain the same entity type.' |

**Recognition**

*Deterministic — pattern plus corroborating context:*

- a treatment quotation or admission arrangement from a named facility co-occurring, inside one bounded set, with itinerary or booking records naming the same destination and overlapping dates

*Needs the LLM:*

- a trip whose medical purpose is stated only in correspondence
- a set of bookings and a clinical letter that share no explicit link
- a trip that was partly a holiday and partly treatment

*Never alone — rejected as deterministic signals:*

- a booking or itinerary, which is the entire travel domain
- a foreign clinic name
- a download session that happens to contain both kinds of file — a session is a purpose clue, and §3.9: 'A session should never be treated as proof of topic'

**Work types:** treatment quotation, admission arrangement, itinerary, visa or letter of invitation, post-treatment follow-up plan, insurance authorisation for care abroad

**Grouping reasons:** one trip taken for one treatment; one facility's arrangement packet

**Template:** `trip or treatment → document type`

> This is a purpose-defined packet rather than a dimension stack; §5.6 says of exactly this shape that 'The template is a recommendation mechanism, not a rule that erases purposeful heterogeneity.'

**Collides with**

| Domain | Signal that separates them | Design cite |
|---|---|---|
| `pers.travel-record` | the travel half of the packet belongs equally to the travel domain, and the user may reasonably want it filed there instead. | §5.6: 'The template is a recommendation mechanism, not a rule that erases purposeful heterogeneity.' |
| `med.surgical-procedure-record` | the clinical half is an ordinary surgical record that happens to have been performed away from home. | — |
| `med.insurance-claim-eob` | care abroad generates authorisation and reimbursement claims of its own. | — |

**Sensitivity:** `potentially_sensitive` — A trip whose purpose discloses a treatment — 'potentially sensitive', which is §2.9's own phrase and the whole of what this field asserts. No handling class is set here; classification is P7's (§8.4).


### 22. `med.wearable-health-export` — Wearable, app, and home-device health exports

Bulk exports from a consumer health platform, fitness tracker, or home monitoring device.

**Provenance:** `proposal`  — the design names neither this domain nor any of its fields.

**Schema** — the fields this domain, and only this domain, legitimises:

| Field | Type | Example | Ceiling | Why |
|---|---|---|---|---|
| `subject_person` | string | self | `direct` | §3.8: 'The system must separate roles that happen to contain the same entity type.' |
| `export_source` | string | the platform or device that produced the export | `direct` | Read from the export container's own manifest or schema markers, not from its contents. §3.5: 'Deterministic extractors create direct facts when the information comes from a reliable, explicit source, such as a content hash, EXIF timestamp, a document title, or a labeled form field.' |
| `export_date` | date | the labeled export date | `direct` | §3.5: 'Deterministic extractors create direct facts when the information comes from a reliable, explicit source, such as a content hash, EXIF timestamp, a document title, or a labeled form field.' §3.10: 'The product must not use fuzzy date parsing' |
| `coverage_period` | string | the labeled period the export covers, as written | `direct` | §3.5: 'Deterministic extractors create direct facts when the information comes from a reliable, explicit source, such as a content hash, EXIF timestamp, a document title, or a labeled form field.' |
| `measure_set` | string | the measures the export contains, as the schema names them | `validated` | §3.13: 'A validated fact was found by a deterministic rule and passed contextual checks, such as a course-code pattern appearing beside “lecture,” “syllabus,” or “semester.”' |
| `device` | string | the recording device, where the export names it | `direct` | §3.5: 'Deterministic extractors create direct facts when the information comes from a reliable, explicit source, such as a content hash, EXIF timestamp, a document title, or a labeled form field.' |

**Recognition**

*Deterministic — pattern plus corroborating context:*

- an export container carrying a named health platform's own manifest or schema markers together with a labeled export date — this is a format and provenance signal, and §2.9: 'treat the file extension as a routing signal rather than an assumption about meaning'
- a device export whose file header names the manufacturer and the recording device together with a labeled coverage period

*Needs the LLM:*

- a spreadsheet of readings a person typed themselves
- an export whose manifest has been stripped
- an export a clinician asked for, which is simultaneously a monitoring log

*Never alone — rejected as deterministic signals:*

- step, heart-rate, sleep, weight or blood-pressure columns — this is the whole point of the domain: consumer wellness data has the exact shape of clinical vitals and must not be filed as a clinical record on that resemblance
- a folder named Health, which is also the literal name of a consumer app
- a timestamp-and-measure table of any kind
- the word 'health' in a filename

**Work types:** platform export, device export, activity or sleep summary, continuous monitor export, shareable report generated by the app

**Grouping reasons:** one export event; one device's coverage period

**Template:** `export source → coverage period`  (time first)

> The exception §5.5 states for capture-based material applies: 'Photos and capture-based media are the major exception: time often belongs first because capture date is a defining aspect of the material.' An export is defined by the window it covers, and the source is what makes two overlapping windows distinguishable.

**Collides with**

| Domain | Signal that separates them | Design cite |
|---|---|---|
| `med.chronic-condition-management` | a clinician-directed monitoring log and a consumer export are the same table; only a clinician-supplied target band or an issuing care plan separates them. | — |
| `pers.fitness-activity` | the majority of these exports have no clinical involvement at all and belong to personal material, not to a medical branch. | — |
| `soft.dataset-artifact` | large structured exports are also ordinary data files, and their format alone says nothing about their subject. | §2.9: 'treat the file extension as a routing signal rather than an assumption about meaning' |

**Sensitivity:** `potentially_sensitive` — Continuous measurements of a person's body and movements — 'potentially sensitive', which is §2.9's own phrase and the whole of what this field asserts. No handling class is set here; classification is P7's (§8.4).


### 23. `med.medical-certification-letter` — Clinician letters certifying capacity, absence, or accommodation

A clinician's letter written for a third party: fitness for work or study, absence, leave, accommodation, or eligibility.

**Provenance:** `proposal`  — the design names neither this domain nor any of its fields.

**Schema** — the fields this domain, and only this domain, legitimises:

| Field | Type | Example | Ceiling | Why |
|---|---|---|---|---|
| `subject_person` | string | the person the letter is about | `direct` | §3.8: 'The system must separate roles that happen to contain the same entity type.' |
| `issuing_clinician` | string | the clinician who signed it | `direct` | §3.8: 'The system must separate roles that happen to contain the same entity type.' |
| `recipient_organisation` | string | the employer, school, agency or insurer it is addressed to | `direct` | A third role again, and the one that decides which other slice also claims the file. §3.8: 'The system must separate roles that happen to contain the same entity type.' |
| `certification_purpose` | string | the labeled purpose the letter serves | `direct` | §3.5: 'Deterministic extractors create direct facts when the information comes from a reliable, explicit source, such as a content hash, EXIF timestamp, a document title, or a labeled form field.' |
| `certification_period` | string | the labeled period certified, as written | `direct` | §3.5: 'Deterministic extractors create direct facts when the information comes from a reliable, explicit source, such as a content hash, EXIF timestamp, a document title, or a labeled form field.' |
| `issue_date` | date | the labeled date of the letter | `direct` | §3.5: 'Deterministic extractors create direct facts when the information comes from a reliable, explicit source, such as a content hash, EXIF timestamp, a document title, or a labeled form field.' §3.10: 'The product must not use fuzzy date parsing' |
| `restriction_or_accommodation` | string | the labeled restriction or accommodation stated | `direct` | §3.5: 'Deterministic extractors create direct facts when the information comes from a reliable, explicit source, such as a content hash, EXIF timestamp, a document title, or a labeled form field.' |

**Recognition**

*Deterministic — pattern plus corroborating context:*

- a letter on a named clinical practice's letterhead carrying a clinician signature block, an addressed recipient organisation and a labeled certification period
- a statutory or employer leave-certification form in which a completed clinician attestation block co-occurs with a named employer and a labeled subject identity

*Needs the LLM:*

- a letter whose purpose is stated only in prose
- an email from a practice standing in for a letter
- a school accommodation plan that quotes a clinician but was written by the school

*Never alone — rejected as deterministic signals:*

- a clinical letterhead, which every appointment reminder also carries
- the words 'letter', 'note', 'certificate' or 'accommodation'
- an employer or school name, for the same reason §4.9: 'A university name alone should not create a group'
- a signature block

**Work types:** fitness-for-work certificate, absence or sick note, leave certification form, accommodation support letter, eligibility letter, return-to-work clearance

**Grouping reasons:** one certification episode across request, letter and the organisation's response; one leave period

**Template:** `subject person → recipient organisation → year`

> §5.5: 'For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders.' The recipient organisation is what the person will search for, because that is why the letter exists. §5.5: 'a parent dimension should provide the context required to understand the child'

**Collides with**

| Domain | Signal that separates them | Design cite |
|---|---|---|
| `acad.accommodations` | a disability accommodation letter is filed by the student with their education records and by the clinician as a letter sent; the same file has two homes and two purposes. | §3.9: 'Topic answers what a file is about, while purpose answers what the file was for.' |
| `career.sabbatical-and-leave` | employer leave certification lives in the employment file as much as in the medical one. | — |
| `med.clinician-referral-sent` | on the clinician's side this is an outgoing letter in a correspondence log, not a record about them. | §3.8: 'The system must separate roles that happen to contain the same entity type.' |

**Sensitivity:** `potentially_sensitive` — A letter that states a named person's capacity or condition to a third party — 'potentially sensitive', which is §2.9's own phrase and the whole of what this field asserts. No handling class is set here; classification is P7's (§8.4).


### 24. `med.occupational-health-screening` — Occupational health and workplace screening

Health assessment carried out because of a job: pre-placement examinations, exposure monitoring, and fitness-for-duty determinations.

**Provenance:** `proposal`  — the design names neither this domain nor any of its fields.

**Schema** — the fields this domain, and only this domain, legitimises:

| Field | Type | Example | Ceiling | Why |
|---|---|---|---|---|
| `subject_person` | string | the employee or candidate assessed | `direct` | §3.8: 'The system must separate roles that happen to contain the same entity type.' |
| `employer` | string | the organisation requiring the assessment | `direct` | A third role, distinct from the assessing clinician and from the subject; it is also the role that hands the file to the career slice. §3.8: 'The system must separate roles that happen to contain the same entity type.' |
| `assessing_service` | string | the occupational health provider | `direct` | §3.8: 'The system must separate roles that happen to contain the same entity type.' |
| `assessment_type` | string | the labeled assessment as the form names it | `direct` | §3.5: 'Deterministic extractors create direct facts when the information comes from a reliable, explicit source, such as a content hash, EXIF timestamp, a document title, or a labeled form field.' |
| `exposure_agent` | string | the hazard monitored, where the record labels one | `validated` | §3.13: 'A validated fact was found by a deterministic rule and passed contextual checks, such as a course-code pattern appearing beside “lecture,” “syllabus,” or “semester.”' |
| `determination` | string | the labeled outcome or clearance statement | `direct` | §3.5: 'Deterministic extractors create direct facts when the information comes from a reliable, explicit source, such as a content hash, EXIF timestamp, a document title, or a labeled form field.' |
| `assessment_date` | date | the labeled assessment date | `direct` | §3.5: 'Deterministic extractors create direct facts when the information comes from a reliable, explicit source, such as a content hash, EXIF timestamp, a document title, or a labeled form field.' §3.10: 'The product must not use fuzzy date parsing' |

**Recognition**

*Deterministic — pattern plus corroborating context:*

- an assessment form in which a named employer, a named occupational health provider and a labeled clearance or determination field appear together
- an exposure or surveillance record in which a labeled hazard or agent field co-occurs with a labeled monitoring period and a named employer

*Needs the LLM:*

- a workplace injury account written by the employee
- a screening result forwarded without its covering assessment
- a health-and-safety training record that also records a medical check

*Never alone — rejected as deterministic signals:*

- a screening or drug-test result, which is an ordinary laboratory report until an employer role appears
- an employer name
- the words 'fit', 'clearance', 'screening' or 'medical' in a filename
- a health-and-safety document, which is an ordinary workplace policy

**Work types:** pre-placement examination, fitness-for-duty determination, exposure monitoring record, surveillance result, workplace injury medical, vaccination or immunity requirement

**Grouping reasons:** one employment relationship's health record set; one surveillance programme across its cycles

**Template:** `subject person → employer → assessment type`

> §5.5: 'For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders.' The employer is the reason the record exists and is how it will be retrieved. §5.5: 'a parent dimension should provide the context required to understand the child'

**Collides with**

| Domain | Signal that separates them | Design cite |
|---|---|---|
| `hr.health-safety` | the employer holds a copy and files it with employment records; the same document is a career artifact and a medical one. | §3.9: 'Topic answers what a file is about, while purpose answers what the file was for.' |
| `med.lab-result` | a workplace drug screen or bloodwork is a laboratory report whose recipient is an employer; `employer` must not be written into the lab schema as `ordering_provider`. | §4.8: 'each fact or label belongs to an allowed domain schema' |
| `med.medical-certification-letter` | a fitness determination is often issued as a letter, and the two domains overlap almost entirely for that work type. | — |

**Sensitivity:** `potentially_sensitive` — Health assessment of a named person disclosed to their employer — 'potentially sensitive', which is §2.9's own phrase and the whole of what this field asserts. No handling class is set here; classification is P7's (§8.4).


## Payer / billing side

### 25. `med.health-plan-coverage` — Health plan enrolment and coverage documents

What a person is covered for: the plan, its benefits schedule, its formulary, and the member's enrolment in it.

**Provenance:** `inference`  
**Design cite:** Extends §3.11's finance field set — 'Finance files may use institution, account type, tax year, and record type.' — to a health payer. The design names no health-plan domain and no health-plan field.

**Schema** — the fields this domain, and only this domain, legitimises:

| Field | Type | Example | Ceiling | Why |
|---|---|---|---|---|
| `subject_person` | string | the member or dependant covered | `direct` | §3.8: 'The system must separate roles that happen to contain the same entity type.' |
| `payer` | string | the insurer or scheme | `direct` | Corresponds to the `institution` field §3.11 grants finance files, in a payer role. §3.8: 'The system must separate roles that happen to contain the same entity type.' |
| `plan` | string | the named plan or product | `validated` | §3.13: 'A validated fact was found by a deterministic rule and passed contextual checks, such as a course-code pattern appearing beside “lecture,” “syllabus,” or “semester.”' |
| `member_identifier` | string | the labeled member or subscriber identifier | `direct` | §3.5: 'Deterministic extractors create direct facts when the information comes from a reliable, explicit source, such as a content hash, EXIF timestamp, a document title, or a labeled form field.' |
| `plan_year` | string | the labeled plan or coverage year, as written | `direct` | The health analogue of the `tax year` field §3.11 grants finance files; read from a labeled field, never parsed loosely. §3.10: 'The product must not use fuzzy date parsing' |
| `coverage_period` | string | the labeled effective and termination dates, as written | `direct` | §3.5: 'Deterministic extractors create direct facts when the information comes from a reliable, explicit source, such as a content hash, EXIF timestamp, a document title, or a labeled form field.' |
| `record_type` | string | enrolment, benefits schedule, formulary or card as labeled | `validated` | §3.13: 'A validated fact was found by a deterministic rule and passed contextual checks, such as a course-code pattern appearing beside “lecture,” “syllabus,” or “semester.”' |
| `group_or_sponsor` | string | the employer or scheme sponsoring the plan | `direct` | §3.8: 'The system must separate roles that happen to contain the same entity type.' |

**Recognition**

*Deterministic — pattern plus corroborating context:*

- a coverage document in which a named payer, a labeled member or subscriber identifier and a labeled plan year or coverage period appear together
- a benefits-schedule structure whose column labels pair a covered service with a member cost-share label, inside a document naming a payer and a plan

*Needs the LLM:*

- an open-enrolment comparison a person assembled themselves
- a plan brochure with no member identity on it
- an appeal letter about coverage rather than about a bill

*Never alone — rejected as deterministic signals:*

- an insurer's name, which also appears as an employer, an advertiser, a shareholding and a sponsor
- a member-identifier-shaped alphanumeric string
- the words 'insurance', 'plan', 'benefits' or 'coverage' — every other line of insurance uses them identically
- a plan-year-shaped four-digit number, which §3.10 already warns is as likely to be a version or an identifier

**Work types:** enrolment confirmation, benefits schedule, formulary, member card, plan brochure, coverage termination notice, open-enrolment comparison

**Grouping reasons:** one plan year across enrolment, schedule and card; one payer relationship across years

**Template:** `payer → plan year → document type`

> §5.5: 'For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders.' The payer is the stable entity; the plan year is what changes. §5.5: 'a parent dimension should provide the context required to understand the child'

**Collides with**

| Domain | Signal that separates them | Design cite |
|---|---|---|
| `fin.insurance` | motor, home, life and health policies are structurally identical documents from structurally identical senders; the member-and-dependant structure and the covered-service schedule are the health markers. | — |
| `career.benefits-enrollment` | employer-sponsored coverage arrives inside HR onboarding material and is filed there as often as here. | §3.9: 'Topic answers what a file is about, while purpose answers what the file was for.' |
| `med.insurance-claim-eob` | the plan document says what is covered; the claim says what happened. Sharing a payer and a member identifier does not make them one domain. | §4.8: 'each fact or label belongs to an allowed domain schema' |

**Sensitivity:** `potentially_sensitive` — Membership identifiers and the dependants named on a plan — 'potentially sensitive', which is §2.9's own phrase and the whole of what this field asserts. No handling class is set here; classification is P7's (§8.4).


### 26. `med.insurance-claim-eob` — Health insurance claims and explanations of benefits

What was claimed from a payer for a service and what the payer decided about it.

**Provenance:** `inference`  
**Design cite:** Extends §3.11's finance field set — 'Finance files may use institution, account type, tax year, and record type.' — to a health claim. The design names no claim domain and no claim field.

**Schema** — the fields this domain, and only this domain, legitimises:

| Field | Type | Example | Ceiling | Why |
|---|---|---|---|---|
| `subject_person` | string | the patient the service was for | `direct` | Distinct from the subscriber, who may be a different person on the same plan. §3.8: 'The system must separate roles that happen to contain the same entity type.' |
| `claim_number` | string | the payer's labeled claim identifier | `direct` | §3.5: 'Deterministic extractors create direct facts when the information comes from a reliable, explicit source, such as a content hash, EXIF timestamp, a document title, or a labeled form field.' |
| `payer` | string | the insurer or scheme processing the claim | `direct` | §3.8: 'The system must separate roles that happen to contain the same entity type.' |
| `member_identifier` | string | the labeled member or subscriber identifier | `direct` | §3.5: 'Deterministic extractors create direct facts when the information comes from a reliable, explicit source, such as a content hash, EXIF timestamp, a document title, or a labeled form field.' |
| `service_date` | date | the labeled date of service | `direct` | Distinct from the claim date, the statement date and the file's own timestamps. §3.5: 'Deterministic extractors create direct facts when the information comes from a reliable, explicit source, such as a content hash, EXIF timestamp, a document title, or a labeled form field.' §3.10: 'The product must not use fuzzy date parsing' |
| `servicing_provider` | string | the clinician or facility that delivered the service | `direct` | §3.8: 'The system must separate roles that happen to contain the same entity type.' |
| `claim_status` | string | the labeled adjudication outcome as stated | `direct` | §3.5: 'Deterministic extractors create direct facts when the information comes from a reliable, explicit source, such as a content hash, EXIF timestamp, a document title, or a labeled form field.' |
| `service_coding_system` | string | the coding system the claim states it uses | `direct` | The system is named as a system. The catalogue lists no codes and asserts nothing about any code's meaning. |

**Recognition**

*Deterministic — pattern plus corroborating context:*

- a labeled claim identifier co-occurring with a named payer, a labeled member or subscriber identifier and a labeled service date in the same document
- a benefits-statement structure carrying a named payer, a labeled member identifier and an explicit statement that the document is not a bill

*Needs the LLM:*

- a claim appeal written as a letter
- a payer statement whose fields could not be extracted from a photograph
- a spreadsheet a person built to reconcile claims against bills

*Never alone — rejected as deterministic signals:*

- the words 'claim' or 'claim number' — motor, home, travel, warranty and contents claims all carry them, and none of them are medical
- a clinical-code-shaped token; codes are also taught, and a medical-coding student's practice workbook is nothing but codes
- an amount
- a payer name
- a service-date-shaped date

**Work types:** explanation of benefits, claim form, claim status notice, denial notice, appeal letter, prior-authorisation decision, coordination-of-benefits form

**Grouping reasons:** one episode of care across its claim, statement and appeal; one plan year's claim set; one denial and the appeal that answers it

**Template:** `payer → plan year → document type`

> §5.5: 'For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders.' A claim is retrieved by who decided it and when it fell, not by which body part it concerned. §5.5: 'a parent dimension should provide the context required to understand the child'

**Collides with**

| Domain | Signal that separates them | Design cite |
|---|---|---|
| `med.provider-billing-dispute` | the two arrive together, name the same service date and the same provider, and are constantly confused by people; the payer-versus-provider sender and the claim-number-versus-account-number identifier are the discriminators. | §3.8: 'The system must separate roles that happen to contain the same entity type.' |
| `fin.insurance` | non-health claims share every structural feature; the member-and-patient pairing and the service-date label are what make a claim medical. | — |
| `med.clinician-malpractice-incident` | a liability claim and a benefits claim share the word and nothing else. | — |

**Sensitivity:** `potentially_sensitive` — What service a named person received and from whom — 'potentially sensitive', which is §2.9's own phrase and the whole of what this field asserts. No handling class is set here; classification is P7's (§8.4).


### 27. `med.provider-billing-dispute` — Provider bills, statements, and billing disputes

What a clinician or facility charged a person, and the correspondence when that is contested.

**Provenance:** `inference`  
**Design cite:** Extends §3.11's finance field set — 'Finance files may use institution, account type, tax year, and record type.' — to a provider bill. The design names no medical-billing domain.

**Schema** — the fields this domain, and only this domain, legitimises:

| Field | Type | Example | Ceiling | Why |
|---|---|---|---|---|
| `subject_person` | string | the patient billed for | `direct` | §3.8: 'The system must separate roles that happen to contain the same entity type.' |
| `billing_provider` | string | the clinician, practice or facility charging | `direct` | The provider role; distinct from the payer, who appears on the same page. §3.8: 'The system must separate roles that happen to contain the same entity type.' |
| `patient_account_identifier` | string | the provider's labeled account or guarantor identifier | `direct` | The provider's own identifier, not the payer's claim number. §3.5: 'Deterministic extractors create direct facts when the information comes from a reliable, explicit source, such as a content hash, EXIF timestamp, a document title, or a labeled form field.' |
| `service_date` | date | the labeled date of service | `direct` | §3.5: 'Deterministic extractors create direct facts when the information comes from a reliable, explicit source, such as a content hash, EXIF timestamp, a document title, or a labeled form field.' §3.10: 'The product must not use fuzzy date parsing' |
| `statement_date` | date | the labeled statement date | `direct` | §3.5: 'Deterministic extractors create direct facts when the information comes from a reliable, explicit source, such as a content hash, EXIF timestamp, a document title, or a labeled form field.' |
| `patient_responsibility` | string | the labeled amount-due field as written | `direct` | Stored as the document's own labeled value; no arithmetic is done here. |
| `dispute_status` | string | the labeled stage of a contested account | `direct` | §3.5: 'Deterministic extractors create direct facts when the information comes from a reliable, explicit source, such as a content hash, EXIF timestamp, a document title, or a labeled form field.' |

**Recognition**

*Deterministic — pattern plus corroborating context:*

- a statement in which a named billing provider or facility, a labeled patient-account identifier and a labeled service date appear together with an amount-due label
- an itemised episode statement in which a per-line service-date column co-occurs with a labeled patient-account identifier

*Needs the LLM:*

- a dispute letter written by the person
- a collections notice that names the provider only indirectly
- a payment plan agreement about a medical debt

*Never alone — rejected as deterministic signals:*

- an invoice or statement structure of any kind — this is the shape of every bill anyone receives
- an amount due
- a hospital or practice name — §4.9: 'A university name alone should not create a group', and a facility name behaves in exactly the same way
- the word 'billing' in a filename

**Work types:** provider statement, itemised bill, good-faith estimate, payment plan agreement, dispute letter, collections notice, receipt of payment

**Grouping reasons:** one episode of care across its bill, claim and payments; one dispute across its correspondence

**Template:** `billing provider → episode or year → document type`

> §5.5: 'For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders.' The provider is what a person searches for when a bill is contested. §5.5: 'a parent dimension should provide the context required to understand the child'

**Collides with**

| Domain | Signal that separates them | Design cite |
|---|---|---|
| `fin.financial-records` | a medical bill is a bill; whether it lives in a finance branch or a medical branch is a genuine user choice and both are defensible. | §3.9: 'Topic answers what a file is about, while purpose answers what the file was for.' |
| `med.insurance-claim-eob` | the pair is the most confused in the whole slice; the sender role and the identifier type separate them. | §3.8: 'The system must separate roles that happen to contain the same entity type.' |
| `med.hospital-admission-discharge` | the same episode produces the clinical record and the bill, and they share dates and a facility. | — |

**Sensitivity:** `potentially_sensitive` — Charges that disclose what care a named person received — 'potentially sensitive', which is §2.9's own phrase and the whole of what this field asserts. No handling class is set here; classification is P7's (§8.4).


## Clinician / practice side

### 28. `med.clinician-patient-chart` — Patient charts held by a clinician or practice

The longitudinal record a practice keeps about a patient, as a working file in the clinician's own corpus.

**Provenance:** `proposal`  — the design names neither this domain nor any of its fields.

**Schema** — the fields this domain, and only this domain, legitimises:

| Field | Type | Example | Ceiling | Why |
|---|---|---|---|---|
| `subject_person` | string | the patient | `direct` | Here the subject is never the holder, and a corpus holds many. §3.8: 'The system must separate roles that happen to contain the same entity type.' |
| `practice` | string | the practice or service holding the chart | `direct` | §3.8: 'The system must separate roles that happen to contain the same entity type.' |
| `chart_identifier` | string | the practice's labeled record identifier | `direct` | A labeled field in an export, never a bare numeric string in text. §3.5: 'Deterministic extractors create direct facts when the information comes from a reliable, explicit source, such as a content hash, EXIF timestamp, a document title, or a labeled form field.' |
| `record_source` | string | the EHR or practice-management system that produced the file | `direct` | Provenance from the export's own producer metadata; this is what separates a clinician's chart from a student's exercise. §3.5: 'Deterministic extractors create direct facts when the information comes from a reliable, explicit source, such as a content hash, EXIF timestamp, a document title, or a labeled form field.' |
| `chart_period` | string | the labeled period the export covers, as written | `direct` | §3.5: 'Deterministic extractors create direct facts when the information comes from a reliable, explicit source, such as a content hash, EXIF timestamp, a document title, or a labeled form field.' |
| `responsible_clinician` | string | the clinician of record | `direct` | A role, and per §3.8: 'It should avoid using authorship or creator identity as a destination dimension.' not a folder dimension. |

**Recognition**

*Deterministic — pattern plus corroborating context:*

- an EHR or practice-management export carrying that system's own producer metadata or manifest, together with a labeled patient-record identifier and a named practice
- a chart export in which a labeled record identifier and a labeled chart period appear as fields in a header block issued by a named practice

*Needs the LLM:*

- a chart assembled by hand as a document rather than exported
- a de-identified chart used for teaching
- records received from another practice and kept as an outside file

*Never alone — rejected as deterministic signals:*

- the word 'chart', which most often means a graph or a spreadsheet visualisation
- a record-identifier-shaped numeric string; §3.10 already warns that such numbers are as likely to be version, build or postal codes
- a patient name
- clinical vocabulary of any density — a nursing or medical student's coursework has more of it than a real chart

**Work types:** chart export, problem list, outside records, chart summary, record amendment, release-of-information log

**Grouping reasons:** one patient's chart across its exports and outside records; one practice's record set

**Template:** `practice → subject person → document type`

> §5.5: 'For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders.' The practice is the stable context; a chart identifier means nothing without it. §5.5: 'a parent dimension should provide the context required to understand the child'

**Collides with**

| Domain | Signal that separates them | Design cite |
|---|---|---|
| `med.personal-health-record` | the same content held by the other party. Holder role, corpus cardinality and export provenance are the discriminators; content is not. | §3.8: 'The system must separate roles that happen to contain the same entity type.' |
| `med.clinician-clinical-note` | a chart contains notes; the chart is the container and the note is the encounter, and they legitimise different fields. | §4.8: 'each fact or label belongs to an allowed domain schema' |
| `res.dataset` | de-identified chart extracts are research data, and the same export is both. | — |

**Sensitivity:** `potentially_sensitive` — Another person's complete medical record held by a professional — 'potentially sensitive', which is §2.9's own phrase and the whole of what this field asserts. No handling class is set here; classification is P7's (§8.4).

**Open question**

> A clinician's corpus contains records about many people who are not the user. §8.4's privacy rules are written for a person's own corpus; whether a professional corpus needs a different consent posture entirely — and whether the product should offer to organise it at all — is a product-scope decision, not a catalogue decision.


### 29. `med.clinician-clinical-note` — Clinical notes authored by a clinician

The record of one encounter, written by the clinician who conducted it.

**Provenance:** `proposal`  — the design names neither this domain nor any of its fields.

**Schema** — the fields this domain, and only this domain, legitimises:

| Field | Type | Example | Ceiling | Why |
|---|---|---|---|---|
| `subject_person` | string | the patient seen | `direct` | §3.8: 'The system must separate roles that happen to contain the same entity type.' |
| `encounter_date` | date | the labeled date of the encounter | `direct` | §3.5: 'Deterministic extractors create direct facts when the information comes from a reliable, explicit source, such as a content hash, EXIF timestamp, a document title, or a labeled form field.' §3.10: 'The product must not use fuzzy date parsing' |
| `authoring_clinician` | string | the clinician who wrote and signed it | `direct` | Authorship, which per §3.8: 'It should avoid using authorship or creator identity as a destination dimension.' must not become a folder level. |
| `note_type` | string | the labeled note type as the template names it | `direct` | §3.5: 'Deterministic extractors create direct facts when the information comes from a reliable, explicit source, such as a content hash, EXIF timestamp, a document title, or a labeled form field.' |
| `practice` | string | the practice or service the encounter belongs to | `direct` | §3.8: 'The system must separate roles that happen to contain the same entity type.' |
| `record_source` | string | the EHR that produced it | `direct` | §3.5: 'Deterministic extractors create direct facts when the information comes from a reliable, explicit source, such as a content hash, EXIF timestamp, a document title, or a labeled form field.' |
| `attestation` | string | the labeled signature or attestation block as recorded | `direct` | The presence of a real attestation block is the only thing that reliably separates a working clinical note from an exercise that reproduces its structure. §3.5: 'Deterministic extractors create direct facts when the information comes from a reliable, explicit source, such as a content hash, EXIF timestamp, a document title, or a labeled form field.' |

**Recognition**

*Deterministic — pattern plus corroborating context:*

- an EHR-produced note carrying that system's producer metadata together with a labeled encounter date and a completed signature or attestation block naming a credentialed clinician

*Needs the LLM:*

- a note structured as an encounter record in an ordinary word-processor file — this is exactly the shape of a nursing or medical student's assignment, and no rule should decide it
- dictation or transcription output
- a handover or ward-round note with no attestation
- any encounter-shaped document that co-occurs with a course code, an assignment heading, a rubric or a submission date

*Never alone — rejected as deterministic signals:*

- subjective, objective, assessment and plan section headings — taught in every clinical programme and reproduced in every student's coursework; this is the single most dangerous pattern in the slice and it is deliberately excluded from the deterministic rule
- the words 'patient', 'presents', 'diagnosis', 'assessment' or 'plan'
- a clinician name with a credential suffix
- high medical-vocabulary density of any kind
- an encounter-shaped date

**Work types:** encounter note, progress note, consultation note, handover note, procedure note, addendum

**Grouping reasons:** one patient's notes within one episode of care; one clinic session's notes

**Template:** `practice → subject person → encounter`

> §5.5: 'For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders.' The patient is the context that makes a single encounter legible. §5.5: 'a parent dimension should provide the context required to understand the child'

**Collides with**

| Domain | Signal that separates them | Design cite |
|---|---|---|
| `acad.course-enrollment` | a student's care-plan or SOAP-note assignment is textually indistinguishable from a real note. Where an academic anchor co-occurs the file has two plausible domains and the design routes it to the model rather than to either rule. | §3.3: the LLM handles files that 'have multiple plausible domains' |
| `med.clinician-patient-chart` | the note lives inside the chart; the chart legitimises record-level fields the note does not claim. | §4.8: 'each fact or label belongs to an allowed domain schema' |
| `med.medical-teaching-material` | case presentations are notes rewritten for teaching, often from real encounters. | — |

**Sensitivity:** `potentially_sensitive` — A written account of another person's consultation — 'potentially sensitive', which is §2.9's own phrase and the whole of what this field asserts. No handling class is set here; classification is P7's (§8.4).


### 30. `med.clinician-treatment-plan` — Treatment plans authored by a clinician

The clinician's stated plan of management for a patient, distinct from the note that records a visit.

**Provenance:** `proposal`  — the design names neither this domain nor any of its fields.

**Schema** — the fields this domain, and only this domain, legitimises:

| Field | Type | Example | Ceiling | Why |
|---|---|---|---|---|
| `subject_person` | string | the patient the plan is for | `direct` | §3.8: 'The system must separate roles that happen to contain the same entity type.' |
| `authoring_clinician` | string | the clinician responsible for the plan | `direct` | §3.8: 'It should avoid using authorship or creator identity as a destination dimension.' |
| `condition_addressed` | string | the labeled indication or problem | `direct` | §3.5: 'Deterministic extractors create direct facts when the information comes from a reliable, explicit source, such as a content hash, EXIF timestamp, a document title, or a labeled form field.' |
| `plan_period` | string | the labeled period or review interval, as written | `direct` | §3.5: 'Deterministic extractors create direct facts when the information comes from a reliable, explicit source, such as a content hash, EXIF timestamp, a document title, or a labeled form field.' |
| `plan_status` | string | the labeled status as recorded | `direct` | §3.5: 'Deterministic extractors create direct facts when the information comes from a reliable, explicit source, such as a content hash, EXIF timestamp, a document title, or a labeled form field.' |
| `practice` | string | the service delivering the plan | `direct` | §3.8: 'The system must separate roles that happen to contain the same entity type.' |
| `multidisciplinary_participants` | string | other services named as contributing | `direct` | §3.8: 'The system must separate roles that happen to contain the same entity type.' |

**Recognition**

*Deterministic — pattern plus corroborating context:*

- a plan document carrying a labeled patient identity, a labeled indication field and a named responsible clinician together with a labeled review interval, issued from a named practice

*Needs the LLM:*

- a plan embedded inside a longer note
- a plan drafted collaboratively in a shared document with no practice identity
- a plan template partially filled

*Never alone — rejected as deterministic signals:*

- the words 'treatment plan' or 'care plan' — they are also project management, marketing, dental sales and education vocabulary
- a condition name
- a review date
- a blank plan template, which carries every keyword and no facts

**Work types:** treatment plan, care plan, management plan, plan review, escalation or de-escalation record

**Grouping reasons:** one patient's plan across its revisions; one condition's management across services

**Template:** `practice → subject person → condition addressed`

> §5.5: 'For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders.'

**Collides with**

| Domain | Signal that separates them | Design cite |
|---|---|---|
| `med.clinician-clinical-note` | the plan is usually a section of a note and only sometimes a document; when it is a section it is not a separate file at all. | — |
| `med.chronic-condition-management` | the patient's copy of the same plan sits in their own corpus with a different holder role. | §3.8: 'The system must separate roles that happen to contain the same entity type.' |
| `med.clinical-protocol-guideline` | a protocol is a plan for a population and a treatment plan is a plan for a person; the documents look alike and the distinction is the presence of a patient identity. | — |

**Sensitivity:** `potentially_sensitive` — A plan of management naming an individual patient — 'potentially sensitive', which is §2.9's own phrase and the whole of what this field asserts. No handling class is set here; classification is P7's (§8.4).


### 31. `med.clinician-case-conference` — Case conferences and multidisciplinary meetings

Material prepared for or produced by a meeting at which specific cases are discussed across services.

**Provenance:** `proposal`  — the design names neither this domain nor any of its fields.

**Schema** — the fields this domain, and only this domain, legitimises:

| Field | Type | Example | Ceiling | Why |
|---|---|---|---|---|
| `meeting` | string | the named board, conference or meeting series | `validated` | §3.13: 'A validated fact was found by a deterministic rule and passed contextual checks, such as a course-code pattern appearing beside “lecture,” “syllabus,” or “semester.”' |
| `meeting_date` | date | the labeled date of the meeting | `direct` | §3.5: 'Deterministic extractors create direct facts when the information comes from a reliable, explicit source, such as a content hash, EXIF timestamp, a document title, or a labeled form field.' §3.10: 'The product must not use fuzzy date parsing' |
| `convening_service` | string | the service or facility convening it | `direct` | §3.8: 'The system must separate roles that happen to contain the same entity type.' |
| `case_list` | string | the labeled list of cases scheduled | `direct` | §3.5: 'Deterministic extractors create direct facts when the information comes from a reliable, explicit source, such as a content hash, EXIF timestamp, a document title, or a labeled form field.' |
| `subject_person` | string | a patient discussed, where the material names them | `direct` | §3.8: 'The system must separate roles that happen to contain the same entity type.' |
| `outcome_or_recommendation` | string | the labeled recorded outcome | `direct` | §3.5: 'Deterministic extractors create direct facts when the information comes from a reliable, explicit source, such as a content hash, EXIF timestamp, a document title, or a labeled form field.' |

**Recognition**

*Deterministic — pattern plus corroborating context:*

- an agenda or outcome record in which a named meeting series, a labeled meeting date and a structured case list carrying patient identities appear together, issued by a named clinical service

*Needs the LLM:*

- slides prepared for a discussion with no agenda structure
- an email thread arranging a discussion about a case
- notes taken during a meeting

*Never alone — rejected as deterministic signals:*

- an agenda structure of any kind — every meeting in every organisation produces one
- the words 'board', 'review', 'conference' or 'meeting'
- a facility name
- a list of names, which is a distribution list as often as a case list

**Work types:** meeting agenda, case list, outcome record, presentation deck, referral into the meeting, action log

**Grouping reasons:** one meeting across its agenda, presentations and outcomes; one case followed across several meetings

**Template:** `meeting → meeting date → document type`

> §5.5: 'For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders.' The meeting series is the stable identity; a single agenda is unreadable without it. §5.5: 'a parent dimension should provide the context required to understand the child'

**Collides with**

| Domain | Signal that separates them | Design cite |
|---|---|---|
| `med.medical-teaching-material` | case presentations serve teaching and decision-making with the same slides. | — |
| `med.clinician-clinical-note` | the outcome of the meeting is written into each patient's record as a note. | — |
| `ops.meeting-record` | structurally this is an ordinary meeting artifact and only its case list makes it clinical. | — |

**Sensitivity:** `potentially_sensitive` — Named patients discussed in a meeting record — 'potentially sensitive', which is §2.9's own phrase and the whole of what this field asserts. No handling class is set here; classification is P7's (§8.4).


### 32. `med.clinician-licensure-credentialing` — Licensure, registration, and credentialing

A practitioner's authority to practise and the packets assembled to prove it to employers, hospitals, and payers.

**Provenance:** `proposal`  — the design names neither this domain nor any of its fields.

**Schema** — the fields this domain, and only this domain, legitimises:

| Field | Type | Example | Ceiling | Why |
|---|---|---|---|---|
| `practitioner` | string | the licensed person | `direct` | The subject of the record is the holder here, which is the reverse of every patient-side domain. §3.8: 'The system must separate roles that happen to contain the same entity type.' |
| `issuing_board` | string | the licensing board, registrar or certifying body | `direct` | §3.8: 'The system must separate roles that happen to contain the same entity type.' |
| `licence_type` | string | the named licence, registration or certification | `validated` | §3.13: 'A validated fact was found by a deterministic rule and passed contextual checks, such as a course-code pattern appearing beside “lecture,” “syllabus,” or “semester.”' |
| `licence_identifier` | string | the labeled licence or registration number | `direct` | §3.5: 'Deterministic extractors create direct facts when the information comes from a reliable, explicit source, such as a content hash, EXIF timestamp, a document title, or a labeled form field.' |
| `licence_status` | string | the labeled status as stated | `direct` | §3.5: 'Deterministic extractors create direct facts when the information comes from a reliable, explicit source, such as a content hash, EXIF timestamp, a document title, or a labeled form field.' |
| `expiration_date` | date | the labeled expiry or renewal date | `direct` | §3.5: 'Deterministic extractors create direct facts when the information comes from a reliable, explicit source, such as a content hash, EXIF timestamp, a document title, or a labeled form field.' §3.10: 'The product must not use fuzzy date parsing' |
| `credentialing_organisation` | string | the hospital, network or payer requesting the packet | `direct` | A third role: who is asking, as opposed to who issued. §3.8: 'The system must separate roles that happen to contain the same entity type.' |
| `jurisdiction` | string | the jurisdiction the licence is valid in | `direct` | §3.5: 'Deterministic extractors create direct facts when the information comes from a reliable, explicit source, such as a content hash, EXIF timestamp, a document title, or a labeled form field.' |

**Recognition**

*Deterministic — pattern plus corroborating context:*

- a labeled licence or registration identifier co-occurring with a named licensing or certifying board and a labeled status or expiry field
- a credentialing or privileging application in which a named requesting organisation, a named practitioner and a labeled licence identifier appear together

*Needs the LLM:*

- a curriculum vitae assembled for credentialing, which is a career artifact serving a licensure purpose
- a verification letter with no identifier
- correspondence about a renewal

*Never alone — rejected as deterministic signals:*

- the word 'licence' or 'license' — software licences, business licences, driving licences and content licences all use it, and a file literally named LICENSE is a source-code convention
- an identifier-shaped alphanumeric string
- an expiry date
- a credential suffix after a name

**Work types:** licence certificate, renewal confirmation, board certification, privileging application, credentialing packet, primary-source verification, controlled-substance registration

**Grouping reasons:** one licence across its renewals; one credentialing application across its assembled evidence

**Template:** `practitioner → licence type → issuing board or jurisdiction`

> §5.5: 'For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders.' The licence type is what a practitioner searches for; the issuing body disambiguates identically-named licences across jurisdictions. §5.5: 'a parent dimension should provide the context required to understand the child'

**Collides with**

| Domain | Signal that separates them | Design cite |
|---|---|---|
| `career.professional-license` | a professional licence is a career artifact and a credentialing packet is an application packet; both readings are legitimate. | §3.9: 'Topic answers what a file is about, while purpose answers what the file was for.' |
| `soft.licence-oss-compliance` | a file named LICENSE in a code project is a licence text and nothing to do with practice authority — the strongest reason a bare licence token can never fire this domain. | — |
| `pers.identity-document` | credentialing packets bundle identity documents, and §4.9 already treats such files as protected records outside normal grouping. | §4.9: 'Rare but sensitive files such as passports, visas, and legal documents may be surfaced as protected records even when they do not meet a normal group-size threshold.' |

**Sensitivity:** `potentially_sensitive` — Licence identifiers and the identity documents bundled with a credentialing packet — 'potentially sensitive', which is §2.9's own phrase and the whole of what this field asserts. No handling class is set here; classification is P7's (§8.4).


### 33. `med.clinician-cme` — Continuing medical education and professional development

Accredited learning a practitioner completes to maintain licensure or certification, and the evidence of it.

**Provenance:** `proposal`  — the design names neither this domain nor any of its fields.

**Schema** — the fields this domain, and only this domain, legitimises:

| Field | Type | Example | Ceiling | Why |
|---|---|---|---|---|
| `practitioner` | string | the participant | `direct` | §3.8: 'The system must separate roles that happen to contain the same entity type.' |
| `activity` | string | the named accredited activity | `validated` | §3.13: 'A validated fact was found by a deterministic rule and passed contextual checks, such as a course-code pattern appearing beside “lecture,” “syllabus,” or “semester.”' |
| `accrediting_body` | string | the body accrediting the activity | `direct` | Distinct from the provider that ran it and from the board that requires it. §3.8: 'The system must separate roles that happen to contain the same entity type.' |
| `credit_designation` | string | the labeled credit type and amount as the certificate states it | `direct` | Stored exactly as designated; the catalogue asserts no credit values of its own. §3.5: 'Deterministic extractors create direct facts when the information comes from a reliable, explicit source, such as a content hash, EXIF timestamp, a document title, or a labeled form field.' |
| `activity_date` | date | the labeled completion date | `direct` | §3.5: 'Deterministic extractors create direct facts when the information comes from a reliable, explicit source, such as a content hash, EXIF timestamp, a document title, or a labeled form field.' §3.10: 'The product must not use fuzzy date parsing' |
| `reporting_cycle` | string | the labeled cycle the credit counts toward, as written | `direct` | §3.5: 'Deterministic extractors create direct facts when the information comes from a reliable, explicit source, such as a content hash, EXIF timestamp, a document title, or a labeled form field.' |
| `provider` | string | the organisation delivering the activity | `direct` | §3.8: 'The system must separate roles that happen to contain the same entity type.' |

**Recognition**

*Deterministic — pattern plus corroborating context:*

- a completion certificate carrying an explicit credit-designation statement together with a named accrediting body and a named participant
- a credit transcript in which a per-activity row pairs a labeled activity with a labeled credit designation, issued by a named accrediting or tracking body

*Needs the LLM:*

- conference material a practitioner kept without a certificate
- a reflective log written for revalidation
- an invoice for a course, which is a finance artifact about professional development

*Never alone — rejected as deterministic signals:*

- a completion certificate of any kind — online course platforms issue millions of them and none carry a credit designation
- the letters CME, or a credit-sounding word
- a conference or society name
- examination preparation material, which has the same vocabulary and awards nothing

**Work types:** completion certificate, credit transcript, activity programme, reflective log, revalidation portfolio, conference registration

**Grouping reasons:** one reporting cycle's credits; one activity across its programme, certificate and receipt

**Template:** `practitioner → reporting cycle → activity`

> §5.5: 'For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders.' The reporting cycle is the unit a practitioner is actually audited on, which makes it the useful parent for an activity. §5.5: 'a parent dimension should provide the context required to understand the child'

**Collides with**

| Domain | Signal that separates them | Design cite |
|---|---|---|
| `acad.course-enrollment` | examination preparation, degree coursework and accredited CME share vocabulary entirely; only the credit designation and accrediting body separate them. | §3.3: the LLM handles files that 'have multiple plausible domains' |
| `med.clinician-licensure-credentialing` | credits are evidence submitted for renewal, so the same certificate appears inside a credentialing packet. | — |
| `career.continuing-education` | for a non-clinical reader this is simply training, and belongs to the career slice. | §3.9: 'Topic answers what a file is about, while purpose answers what the file was for.' |

**Sensitivity:** `potentially_sensitive` — Certificates carrying a named practitioner's licence identifiers — 'potentially sensitive', which is §2.9's own phrase and the whole of what this field asserts. No handling class is set here; classification is P7's (§8.4).


### 34. `med.clinician-malpractice-incident` — Malpractice cover, claims, and patient-safety incidents

Professional liability cover and the records of adverse events, complaints, and claims against a practitioner or facility.

**Provenance:** `proposal`  — the design names neither this domain nor any of its fields.

**Schema** — the fields this domain, and only this domain, legitimises:

| Field | Type | Example | Ceiling | Why |
|---|---|---|---|---|
| `practitioner_or_facility` | string | the named insured or the service involved | `direct` | §3.8: 'The system must separate roles that happen to contain the same entity type.' |
| `carrier` | string | the liability insurer | `direct` | §3.8: 'The system must separate roles that happen to contain the same entity type.' |
| `policy_identifier` | string | the labeled policy number | `direct` | §3.5: 'Deterministic extractors create direct facts when the information comes from a reliable, explicit source, such as a content hash, EXIF timestamp, a document title, or a labeled form field.' |
| `coverage_period` | string | the labeled policy period, as written | `direct` | §3.5: 'Deterministic extractors create direct facts when the information comes from a reliable, explicit source, such as a content hash, EXIF timestamp, a document title, or a labeled form field.' |
| `incident_identifier` | string | the labeled occurrence or incident reference | `direct` | §3.5: 'Deterministic extractors create direct facts when the information comes from a reliable, explicit source, such as a content hash, EXIF timestamp, a document title, or a labeled form field.' |
| `event_date` | date | the labeled date of the occurrence | `direct` | §3.5: 'Deterministic extractors create direct facts when the information comes from a reliable, explicit source, such as a content hash, EXIF timestamp, a document title, or a labeled form field.' §3.10: 'The product must not use fuzzy date parsing' |
| `matter_status` | string | the labeled stage of a claim or investigation | `direct` | §3.5: 'Deterministic extractors create direct facts when the information comes from a reliable, explicit source, such as a content hash, EXIF timestamp, a document title, or a labeled form field.' |
| `reporting_body` | string | the regulator or programme the event was reported to | `direct` | §3.8: 'The system must separate roles that happen to contain the same entity type.' |

**Recognition**

*Deterministic — pattern plus corroborating context:*

- a liability policy document in which a named carrier, a labeled policy identifier, a named insured practitioner or facility and a labeled coverage period appear together
- a patient-safety occurrence report form in which a labeled incident reference, a labeled event date and a named clinical facility appear together with a patient identity

*Needs the LLM:*

- a complaint letter from a patient or family
- a reflective account written after an event
- correspondence with a regulator about an investigation

*Never alone — rejected as deterministic signals:*

- the phrase 'incident report', 'root cause analysis' or 'post-mortem' — these are core software-operations vocabulary and an engineer's corpus is full of them
- the words 'claim', 'liability' or 'occurrence'
- an insurer's name
- a workplace accident form, which belongs to health and safety in any industry

**Work types:** liability policy, certificate of insurance, occurrence report, root-cause review, complaint file, claim correspondence, regulatory notification

**Grouping reasons:** one policy period; one incident across its report, review and correspondence

**Template:** `practitioner or facility → matter or policy → document type`

> §5.5: 'For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders.' A single correspondence item is unreadable without the matter it belongs to. §5.5: 'a parent dimension should provide the context required to understand the child'

**Collides with**

| Domain | Signal that separates them | Design cite |
|---|---|---|
| `soft.incident-postmortem` | the phrase 'incident report' and the entire root-cause-analysis document shape belong to software operations, and in a mixed corpus they will outnumber clinical ones. | — |
| `legal.litigation-dispute` | a claim is a legal matter whose subject is clinical; both slices legitimately claim it. | §3.9: 'Topic answers what a file is about, while purpose answers what the file was for.' |
| `med.clinician-patient-chart` | an incident file contains the patient record it concerns. | — |

**Sensitivity:** `potentially_sensitive` — An adverse event naming a patient and a practitioner — 'potentially sensitive', which is §2.9's own phrase and the whole of what this field asserts. No handling class is set here; classification is P7's (§8.4).


### 35. `med.clinician-referral-sent` — Referrals and correspondence sent by a clinician

Outgoing letters a clinician writes about their patients, kept as the practice's correspondence record.

**Provenance:** `proposal`  — the design names neither this domain nor any of its fields.

**Schema** — the fields this domain, and only this domain, legitimises:

| Field | Type | Example | Ceiling | Why |
|---|---|---|---|---|
| `subject_person` | string | the patient referred | `direct` | §3.8: 'The system must separate roles that happen to contain the same entity type.' |
| `referring_clinician` | string | the clinician sending — here, the corpus owner | `direct` | §3.8: 'The system must separate roles that happen to contain the same entity type.' |
| `receiving_service` | string | the service or clinician addressed | `direct` | §3.8: 'The system must separate roles that happen to contain the same entity type.' |
| `specialty` | string | the service referred to | `validated` | §3.13: 'A validated fact was found by a deterministic rule and passed contextual checks, such as a course-code pattern appearing beside “lecture,” “syllabus,” or “semester.”' |
| `sent_date` | date | the labeled date sent | `direct` | §3.5: 'Deterministic extractors create direct facts when the information comes from a reliable, explicit source, such as a content hash, EXIF timestamp, a document title, or a labeled form field.' §3.10: 'The product must not use fuzzy date parsing' |
| `reason_for_referral` | string | the labeled reason field | `direct` | §3.5: 'Deterministic extractors create direct facts when the information comes from a reliable, explicit source, such as a content hash, EXIF timestamp, a document title, or a labeled form field.' |
| `urgency` | string | the labeled urgency or pathway as stated | `direct` | §3.5: 'Deterministic extractors create direct facts when the information comes from a reliable, explicit source, such as a content hash, EXIF timestamp, a document title, or a labeled form field.' |
| `practice` | string | the sending practice | `direct` | §3.8: 'The system must separate roles that happen to contain the same entity type.' |

**Recognition**

*Deterministic — pattern plus corroborating context:*

- an outgoing letter on a named practice's letterhead in which a sending-clinician block and an addressed receiving service appear as a pair, together with a labeled patient identity and a labeled reason field
- a referral form issued by a named practice carrying a labeled pathway or urgency field and a patient identity

*Needs the LLM:*

- an email referral with no letter structure
- a discharge letter that also functions as a referral
- a letter whose sender and receiver roles cannot be assigned from structure

*Never alone — rejected as deterministic signals:*

- the word 'referral', for the same reason it fails on the patient side
- a practice letterhead
- a specialty name
- a clinician name with a credential suffix

**Work types:** referral letter, onward referral, clinic letter to a colleague, letter to a patient, urgent pathway form, correspondence log

**Grouping reasons:** one patient's outgoing correspondence; one referral pathway across its letters and responses

**Template:** `practice → specialty or service → year`

> §5.5: 'For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders.' Correspondence is retrieved by where it went. §5.5: 'a parent dimension should provide the context required to understand the child'

**Collides with**

| Domain | Signal that separates them | Design cite |
|---|---|---|
| `med.referral-received` | the same letter held by the other party; only the role match to the corpus owner and the corpus cardinality separate them. | §3.8: 'The system must separate roles that happen to contain the same entity type.' |
| `med.medical-certification-letter` | a letter certifying capacity is also outgoing correspondence, and on the clinician's side the two work types blur completely. | — |
| `med.clinician-clinical-note` | a clinic letter is often the note, re-addressed. | — |

**Sensitivity:** `potentially_sensitive` — Correspondence naming patients and their conditions — 'potentially sensitive', which is §2.9's own phrase and the whole of what this field asserts. No handling class is set here; classification is P7's (§8.4).


### 36. `med.clinical-protocol-guideline` — Clinical protocols, pathways, and guidelines

Institutional or published instructions for how a class of patients should be managed — a document about a population, not a person.

**Provenance:** `proposal`  — the design names neither this domain nor any of its fields.

**Schema** — the fields this domain, and only this domain, legitimises:

| Field | Type | Example | Ceiling | Why |
|---|---|---|---|---|
| `protocol` | string | the named protocol, pathway or guideline | `validated` | §3.13: 'A validated fact was found by a deterministic rule and passed contextual checks, such as a course-code pattern appearing beside “lecture,” “syllabus,” or “semester.”' |
| `issuing_body` | string | the committee, society or institution issuing it | `direct` | §3.8: 'The system must separate roles that happen to contain the same entity type.' |
| `version` | string | the labeled version or revision as written | `direct` | §3.5: 'Deterministic extractors create direct facts when the information comes from a reliable, explicit source, such as a content hash, EXIF timestamp, a document title, or a labeled form field.' |
| `approval_date` | date | the labeled approval or effective date | `direct` | §3.5: 'Deterministic extractors create direct facts when the information comes from a reliable, explicit source, such as a content hash, EXIF timestamp, a document title, or a labeled form field.' §3.10: 'The product must not use fuzzy date parsing' |
| `review_date` | date | the labeled scheduled review date | `direct` | §3.5: 'Deterministic extractors create direct facts when the information comes from a reliable, explicit source, such as a content hash, EXIF timestamp, a document title, or a labeled form field.' |
| `scope` | string | the population or setting the protocol applies to, as labeled | `validated` | §3.13: 'A validated fact was found by a deterministic rule and passed contextual checks, such as a course-code pattern appearing beside “lecture,” “syllabus,” or “semester.”' |
| `clinical_area` | string | the service or specialty it governs | `validated` | §3.13: 'A validated fact was found by a deterministic rule and passed contextual checks, such as a course-code pattern appearing beside “lecture,” “syllabus,” or “semester.”' |

**Recognition**

*Deterministic — pattern plus corroborating context:*

- a document carrying a labeled version, a labeled approval or effective date and a named issuing clinical committee or society in the same control block
- an order-set or pathway structure in which a labeled scope or eligibility criterion co-occurs with a named issuing clinical service and a labeled review date

*Needs the LLM:*

- a draft protocol with no approval block
- a summary of a guideline made for teaching
- a local adaptation of a national guideline

*Never alone — rejected as deterministic signals:*

- the words 'protocol', 'SOP', 'pathway', 'guideline' or 'runbook' — laboratory protocols, manufacturing procedures, IT runbooks and research method sections all use them, and in a research corpus 'protocol' means something else entirely
- a version and approval block, which is standard for every controlled document in any regulated industry
- a society or institution name
- clinical vocabulary density

**Work types:** clinical guideline, order set, care pathway, standard operating procedure, checklist, local adaptation, escalation policy

**Grouping reasons:** one protocol across its versions; one clinical area's protocol set

**Template:** `clinical area → protocol → version`

> §5.5: 'For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders.' Superseded versions must remain distinguishable from the current one, which makes version the natural leaf. §5.5: 'a parent dimension should provide the context required to understand the child'

**Collides with**

| Domain | Signal that separates them | Design cite |
|---|---|---|
| `res.protocol-sop` | a bench protocol and a clinical protocol share the word, the document shape and the version block; the population scope and the issuing clinical committee are the discriminators. | — |
| `med.clinician-treatment-plan` | a protocol addresses a population and a treatment plan addresses a person; the presence of a patient identity is the separator. | — |
| `med.medical-teaching-material` | protocols are taught, and the teaching version is a derivative of the controlled one. | — |

**Sensitivity:** `none` — A protocol concerns a population rather than an identified person and carries no individual's health information. This is the only entry in the slice marked `none`; the classification is evidence-backed and revisable, and any handling decision remains P7's (§8.4).


### 37. `med.medical-teaching-material` — Medical teaching material and grand rounds

Material a clinician prepares to teach: lectures, case presentations, rounds decks, and assessment material.

**Provenance:** `proposal`  — the design names neither this domain nor any of its fields.

**Schema** — the fields this domain, and only this domain, legitimises:

| Field | Type | Example | Ceiling | Why |
|---|---|---|---|---|
| `series_or_programme` | string | the named rounds series, course or teaching programme | `validated` | §3.13: 'A validated fact was found by a deterministic rule and passed contextual checks, such as a course-code pattern appearing beside “lecture,” “syllabus,” or “semester.”' |
| `presenting_clinician` | string | the clinician delivering it | `direct` | §3.8: 'It should avoid using authorship or creator identity as a destination dimension.' |
| `session_date` | date | the labeled date delivered | `direct` | §3.5: 'Deterministic extractors create direct facts when the information comes from a reliable, explicit source, such as a content hash, EXIF timestamp, a document title, or a labeled form field.' §3.10: 'The product must not use fuzzy date parsing' |
| `host_institution` | string | the department or institution hosting it | `direct` | §3.8: 'The system must separate roles that happen to contain the same entity type.' |
| `audience` | string | the labeled learner group | `direct` | §3.5: 'Deterministic extractors create direct facts when the information comes from a reliable, explicit source, such as a content hash, EXIF timestamp, a document title, or a labeled form field.' |
| `clinical_topic` | string | the subject taught, as titled | `validated` | §3.13: 'A validated fact was found by a deterministic rule and passed contextual checks, such as a course-code pattern appearing beside “lecture,” “syllabus,” or “semester.”' |
| `accreditation` | string | any credit accreditation footer, where present | `direct` | §3.5: 'Deterministic extractors create direct facts when the information comes from a reliable, explicit source, such as a content hash, EXIF timestamp, a document title, or a labeled form field.' |
| `de_identification_status` | string | whether the material states that case content is de-identified | `direct` | Recorded because case material may carry patient content whether or not it says so. §3.5: 'Deterministic extractors create direct facts when the information comes from a reliable, explicit source, such as a content hash, EXIF timestamp, a document title, or a labeled form field.' |

**Recognition**

*Deterministic — pattern plus corroborating context:*

- a presentation or handout carrying a named departmental rounds or teaching series identity together with a labeled session date and a named host institution
- teaching material carrying a credit-accreditation footer naming an accrediting body

*Needs the LLM:*

- a slide deck with a clinical topic and no series, institution or date
- a case presentation that may be teaching material or may be a live case discussion
- material a clinician saved from someone else's teaching

*Never alone — rejected as deterministic signals:*

- a slide deck with clinical content — a student's presentation, a conference talk, a pharmaceutical deck and a hospital lecture are indistinguishable by content
- the words 'rounds', 'lecture', 'teaching' or 'case'
- an institution name
- an image of a scan or a specimen, which appears in coursework and journalism alike

**Work types:** lecture slides, case presentation, handout, assessment or question set, journal club material, simulation scenario

**Grouping reasons:** one teaching series across its sessions; one topic across its versions

**Template:** `series or programme → session or topic → document type`

> §5.5: 'For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders.' The series is what makes a single deck retrievable years later. §5.5: 'a parent dimension should provide the context required to understand the child'

**Collides with**

| Domain | Signal that separates them | Design cite |
|---|---|---|
| `acad.course-instruction` | for a clinician who also holds a faculty appointment this is coursework, and the academic template may be the better fit. | §3.3: the LLM handles files that 'have multiple plausible domains' |
| `med.clinician-cme` | accredited teaching produces credits for both the presenter and the audience, and the same file evidences both. | — |
| `med.clinician-case-conference` | case presentations are made once and used for both teaching and decision-making. | — |

**Sensitivity:** `potentially_sensitive` — Case-based teaching material, which may carry identifiable patient content whether or not it claims to be de-identified — 'potentially sensitive', which is §2.9's own phrase and the whole of what this field asserts. No handling class is set here; classification is P7's (§8.4).


### 38. `med.practice-administration` — Practice administration and rostering

Running a clinical practice as a business: staffing, rotas, contracts, compliance, and vendor relationships.

**Provenance:** `proposal`  — the design names neither this domain nor any of its fields.

**Schema** — the fields this domain, and only this domain, legitimises:

| Field | Type | Example | Ceiling | Why |
|---|---|---|---|---|
| `practice` | string | the practice or service | `direct` | §3.8: 'The system must separate roles that happen to contain the same entity type.' |
| `administrative_function` | string | the labeled function the document serves | `direct` | §3.5: 'Deterministic extractors create direct facts when the information comes from a reliable, explicit source, such as a content hash, EXIF timestamp, a document title, or a labeled form field.' |
| `counterparty` | string | the vendor, payer, landlord or contractor named | `direct` | §3.8: 'The system must separate roles that happen to contain the same entity type.' |
| `effective_period` | string | the labeled period a contract, rota or policy covers, as written | `direct` | §3.5: 'Deterministic extractors create direct facts when the information comes from a reliable, explicit source, such as a content hash, EXIF timestamp, a document title, or a labeled form field.' |
| `staff_member` | string | the employee a record concerns | `direct` | A subject role, not authorship; and per §3.8: 'It should avoid using authorship or creator identity as a destination dimension.' it is not a folder dimension. |
| `service_line` | string | the clinical service or site a rota or policy applies to | `validated` | §3.13: 'A validated fact was found by a deterministic rule and passed contextual checks, such as a course-code pattern appearing beside “lecture,” “syllabus,” or “semester.”' |
| `compliance_regime` | string | the accreditation, inspection or regulatory scheme named | `direct` | §3.8: 'The system must separate roles that happen to contain the same entity type.' |

**Recognition**

*Deterministic — pattern plus corroborating context:*

- a document issued by a named clinical practice in which a labeled administrative function and a labeled effective period appear together with a named counterparty or service line
- a rota or on-call schedule structure in which a per-shift row pairs a named service line with a labeled coverage period, issued by a named clinical service

*Needs the LLM:*

- an internal memo about how the practice should run
- a spreadsheet whose columns are unlabeled
- correspondence with a vendor about a clinical system

*Never alone — rejected as deterministic signals:*

- a rota, roster or shift table, which every hospitality, retail, security and manufacturing business also produces
- a contract, invoice or policy structure of any kind
- the words 'clinic', 'practice' or 'schedule'
- a vendor name

**Work types:** on-call schedule, rota, coverage swap, staff contract, vendor agreement, accreditation or inspection file, practice policy, supplier invoice, payroll record

**Grouping reasons:** one rota period; one contract across its term and renewals; one inspection cycle

**Template:** `practice → administrative function → effective period`

> §5.5: 'For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders.' Function before period, because a rota and a contract for the same year are unrelated. §5.5: 'a parent dimension should provide the context required to understand the child'

**Collides with**

| Domain | Signal that separates them | Design cite |
|---|---|---|
| `biz.payroll-employer` | staff contracts and payroll are employment records that happen to be held by a clinical employer. | §3.9: 'Topic answers what a file is about, while purpose answers what the file was for.' |
| `biz.bookkeeping` | practice accounting is ordinary business finance and belongs in a finance branch at least as much as here. | — |
| `personal.calendar` | a personal on-call calendar export is a calendar file (§2.9's ICS row) whose clinical meaning is not in the format. | §2.9: 'treat the file extension as a routing signal rather than an assumption about meaning' |

**Sensitivity:** `potentially_sensitive` — Staff records and contracts naming individuals — 'potentially sensitive', which is §2.9's own phrase and the whole of what this field asserts. No handling class is set here; classification is P7's (§8.4).


### 39. `med.device-and-implant-record` — Medical device and implant records

A specific device: what it is, who holds or received it, and its service or recall history.

**Provenance:** `proposal`  — the design names neither this domain nor any of its fields.

**Schema** — the fields this domain, and only this domain, legitimises:

| Field | Type | Example | Ceiling | Why |
|---|---|---|---|---|
| `device` | string | the device model as named on the record | `validated` | §3.13: 'A validated fact was found by a deterministic rule and passed contextual checks, such as a course-code pattern appearing beside “lecture,” “syllabus,” or “semester.”' |
| `manufacturer` | string | the manufacturer | `direct` | §3.8: 'The system must separate roles that happen to contain the same entity type.' |
| `device_identifier` | string | the labeled unique-device or serial identifier | `direct` | A labeled identifier field, never a bare serial-shaped string found in text. §3.5: 'Deterministic extractors create direct facts when the information comes from a reliable, explicit source, such as a content hash, EXIF timestamp, a document title, or a labeled form field.' |
| `subject_person` | string | the recipient, where the device was implanted or issued | `direct` | §3.8: 'The system must separate roles that happen to contain the same entity type.' |
| `implant_or_issue_date` | date | the labeled date placed or issued | `direct` | §3.5: 'Deterministic extractors create direct facts when the information comes from a reliable, explicit source, such as a content hash, EXIF timestamp, a document title, or a labeled form field.' §3.10: 'The product must not use fuzzy date parsing' |
| `holding_facility` | string | the facility owning or servicing the device | `direct` | §3.8: 'The system must separate roles that happen to contain the same entity type.' |
| `service_event` | string | the labeled maintenance, calibration or recall event | `direct` | §3.5: 'Deterministic extractors create direct facts when the information comes from a reliable, explicit source, such as a content hash, EXIF timestamp, a document title, or a labeled form field.' |
| `regulatory_notice` | string | the labeled safety notice or field action, where one exists | `direct` | §3.5: 'Deterministic extractors create direct facts when the information comes from a reliable, explicit source, such as a content hash, EXIF timestamp, a document title, or a labeled form field.' |

**Recognition**

*Deterministic — pattern plus corroborating context:*

- a device record in which a labeled unique-device or serial identifier, a named manufacturer and a named device model appear together with either a labeled implant date and a subject identity, or a labeled service or calibration event and a named holding facility
- a manufacturer safety notice naming a device model and a labeled field-action reference, addressed to a named clinical facility

*Needs the LLM:*

- a purchase order or quotation for equipment
- a device manual kept alongside the record
- a patient's photograph of an implant card

*Never alone — rejected as deterministic signals:*

- a serial number or model number of any kind — every asset register, warranty and receipt in existence carries them
- a manufacturer name
- the word 'device', which is ubiquitous in software and consumer electronics
- a maintenance or calibration log, which every industry keeps

**Work types:** implant card, device registration, asset record, maintenance or calibration log, recall or safety notice, device manual, decommissioning record

**Grouping reasons:** one device across its registration, service history and notices; one recall across the devices it affects

**Template:** `holding facility or subject person → device → record type`

> §5.5: 'For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders.' The device is the identity; a calibration log is meaningless without knowing which unit it belongs to. §5.5: 'a parent dimension should provide the context required to understand the child'

**Collides with**

| Domain | Signal that separates them | Design cite |
|---|---|---|
| `med.surgical-procedure-record` | an implant card is filed with the operation that placed it on the patient's side, and as an asset record on the facility's side. | — |
| `mro.asset-record` | a practice's device inventory is an asset register and belongs to business records as much as to clinical ones. | — |
| `soft.it-asset-inventory` | the entire structure — model, serial, manufacturer, service log — is identical to any IT asset inventory. | — |

**Sensitivity:** `potentially_sensitive` — An implant record identifies a device inside a named person — 'potentially sensitive', which is §2.9's own phrase and the whole of what this field asserts. No handling class is set here; classification is P7's (§8.4).


### 40. `med.pharmacy-operations` — Pharmacy operations

Running a pharmacy: dispensing records, inventory, controlled-substance accountability, and formulary management.

**Provenance:** `proposal`  — the design names neither this domain nor any of its fields.

**Schema** — the fields this domain, and only this domain, legitimises:

| Field | Type | Example | Ceiling | Why |
|---|---|---|---|---|
| `pharmacy` | string | the dispensing pharmacy or department | `direct` | §3.8: 'The system must separate roles that happen to contain the same entity type.' |
| `registrant` | string | the registered pharmacist or registration holder | `direct` | §3.8: 'The system must separate roles that happen to contain the same entity type.' |
| `product` | string | the dispensed or stocked product as the record names it | `validated` | §3.13: 'A validated fact was found by a deterministic rule and passed contextual checks, such as a course-code pattern appearing beside “lecture,” “syllabus,” or “semester.”' |
| `product_coding_system` | string | the product coding system the record states it uses | `direct` | Named as a system only. The catalogue enumerates no codes. |
| `record_type` | string | dispensing, inventory, accountability or formulary as labeled | `validated` | §3.13: 'A validated fact was found by a deterministic rule and passed contextual checks, such as a course-code pattern appearing beside “lecture,” “syllabus,” or “semester.”' |
| `record_period` | string | the labeled period the ledger covers, as written | `direct` | §3.5: 'Deterministic extractors create direct facts when the information comes from a reliable, explicit source, such as a content hash, EXIF timestamp, a document title, or a labeled form field.' |
| `supplier` | string | the wholesaler or supplier named | `direct` | §3.8: 'The system must separate roles that happen to contain the same entity type.' |

**Recognition**

*Deterministic — pattern plus corroborating context:*

- a dispensing or inventory ledger in which a product-identifier column co-occurs with a dispensed-or-received quantity column, inside a document naming a pharmacy and a registration holder
- a controlled-substance accountability record in which a labeled registration identifier, a named pharmacy and a labeled reconciliation period appear together

*Needs the LLM:*

- a spreadsheet of stock with unlabeled columns
- a purchase order to a wholesaler
- correspondence about a shortage or substitution

*Never alone — rejected as deterministic signals:*

- a product-code column, which is any retail inventory
- a drug name, for the same reason it fails on the prescription side
- the word 'pharmacy', which is a chain name, a receipt header and a shop sign
- an inventory or stock ledger structure of any kind

**Work types:** dispensing log, inventory record, controlled-substance register, wholesaler order, formulary decision, recall action, compounding record

**Grouping reasons:** one reconciliation period; one product line across its ordering and dispensing

**Template:** `pharmacy → record type → record period`

> §5.5: 'For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders.' Record type before period, because a dispensing log and an inventory count for the same month are different things. §5.5: 'a parent dimension should provide the context required to understand the child'

**Collides with**

| Domain | Signal that separates them | Design cite |
|---|---|---|
| `med.prescription-medication` | the same dispensing event appears as one person's prescription and as one line in the pharmacy's ledger; the corpus cardinality is the discriminator. | §3.8: 'The system must separate roles that happen to contain the same entity type.' |
| `retail.stocktake` | pharmacy stock control is ordinary retail inventory management. | — |
| `med.practice-administration` | a hospital pharmacy department's files are practice administration for a clinical service. | — |

**Sensitivity:** `potentially_sensitive` — Dispensing records that name patients and controlled products — 'potentially sensitive', which is §2.9's own phrase and the whole of what this field asserts. No handling class is set here; classification is P7's (§8.4).


### 41. `med.public-health-reporting` — Public health and registry reporting

Reports a clinician or facility is required to make to a health authority or registry.

**Provenance:** `proposal`  — the design names neither this domain nor any of its fields.

**Schema** — the fields this domain, and only this domain, legitimises:

| Field | Type | Example | Ceiling | Why |
|---|---|---|---|---|
| `reporting_facility` | string | the practice or facility making the report | `direct` | §3.8: 'The system must separate roles that happen to contain the same entity type.' |
| `receiving_authority` | string | the health department, agency or registry receiving it | `direct` | A distinct role from the reporter; the direction of the report is the domain's whole shape. §3.8: 'The system must separate roles that happen to contain the same entity type.' |
| `report_type` | string | the labeled report or submission type | `direct` | §3.5: 'Deterministic extractors create direct facts when the information comes from a reliable, explicit source, such as a content hash, EXIF timestamp, a document title, or a labeled form field.' |
| `reportable_condition_or_event` | string | the condition or event the report concerns, as labeled | `validated` | §3.13: 'A validated fact was found by a deterministic rule and passed contextual checks, such as a course-code pattern appearing beside “lecture,” “syllabus,” or “semester.”' |
| `report_identifier` | string | the labeled case or submission reference | `direct` | §3.5: 'Deterministic extractors create direct facts when the information comes from a reliable, explicit source, such as a content hash, EXIF timestamp, a document title, or a labeled form field.' |
| `report_date` | date | the labeled date submitted | `direct` | §3.5: 'Deterministic extractors create direct facts when the information comes from a reliable, explicit source, such as a content hash, EXIF timestamp, a document title, or a labeled form field.' §3.10: 'The product must not use fuzzy date parsing' |
| `reporting_period` | string | the labeled period a batch submission covers, as written | `direct` | §3.5: 'Deterministic extractors create direct facts when the information comes from a reliable, explicit source, such as a content hash, EXIF timestamp, a document title, or a labeled form field.' |
| `jurisdiction` | string | the jurisdiction whose requirement is being met | `direct` | §3.5: 'Deterministic extractors create direct facts when the information comes from a reliable, explicit source, such as a content hash, EXIF timestamp, a document title, or a labeled form field.' |

**Recognition**

*Deterministic — pattern plus corroborating context:*

- a report form in which a named receiving health authority or registry, a named reporting facility and a labeled case or submission reference appear together
- a submission confirmation or acknowledgement issued by a named authority carrying a labeled submission reference and a labeled reporting period

*Needs the LLM:*

- an internal draft of a report
- an epidemiological summary that may be a submission or may be analysis
- correspondence with an authority about a case

*Never alone — rejected as deterministic signals:*

- a condition name plus a count — epidemiology coursework, dashboards, journalism and advocacy are made of exactly this
- a health department or agency name
- the words 'surveillance', 'notifiable', 'registry' or 'case'
- a statistical table of any kind

**Work types:** notifiable condition report, registry submission, surveillance return, acknowledgement or receipt, correction submission, outbreak notification

**Grouping reasons:** one submission across its report and acknowledgement; one reporting period's returns

**Template:** `receiving authority → report type → reporting period`

> §5.5: 'For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders.' The authority is who the obligation runs to and is how a submission is found again. §5.5: 'a parent dimension should provide the context required to understand the child'

**Collides with**

| Domain | Signal that separates them | Design cite |
|---|---|---|
| `res.dataset` | the same counts and the same conditions appear in analysis that is not a submission to anyone. | — |
| `med.clinician-patient-chart` | a case report is derived from the patient's record and names them. | — |
| `acad.course-enrollment` | public health teaching material reproduces report forms as exercises. | §3.3: the LLM handles files that 'have multiple plausible domains' |

**Sensitivity:** `potentially_sensitive` — Case reports that name individuals and their conditions — 'potentially sensitive', which is §2.9's own phrase and the whole of what this field asserts. No handling class is set here; classification is P7's (§8.4).


### 42. `med.veterinary-practice` — Veterinary practice records

A veterinary clinician's working files: animal patient records, practice operations, and the client relationship behind each animal.

**Provenance:** `proposal`  — the design names neither this domain nor any of its fields.

**Schema** — the fields this domain, and only this domain, legitimises:

| Field | Type | Example | Ceiling | Why |
|---|---|---|---|---|
| `animal_patient` | string | the animal seen | `direct` | The patient here is not a person, which is the field that keeps this domain out of the human ones. §3.8: 'The system must separate roles that happen to contain the same entity type.' |
| `species` | string | the labeled species | `direct` | §3.5: 'Deterministic extractors create direct facts when the information comes from a reliable, explicit source, such as a content hash, EXIF timestamp, a document title, or a labeled form field.' |
| `breed` | string | the labeled breed, where recorded | `direct` | §3.5: 'Deterministic extractors create direct facts when the information comes from a reliable, explicit source, such as a content hash, EXIF timestamp, a document title, or a labeled form field.' |
| `owner` | string | the client responsible for the animal | `direct` | A person role distinct from the animal patient and from the attending veterinarian. §3.8: 'The system must separate roles that happen to contain the same entity type.' |
| `attending_veterinarian` | string | the treating clinician | `direct` | §3.8: 'The system must separate roles that happen to contain the same entity type.' |
| `clinic` | string | the practice | `direct` | §3.8: 'The system must separate roles that happen to contain the same entity type.' |
| `visit_date` | date | the labeled visit date | `direct` | §3.5: 'Deterministic extractors create direct facts when the information comes from a reliable, explicit source, such as a content hash, EXIF timestamp, a document title, or a labeled form field.' §3.10: 'The product must not use fuzzy date parsing' |
| `record_type` | string | consultation, procedure, vaccination or certificate as labeled | `validated` | §3.13: 'A validated fact was found by a deterministic rule and passed contextual checks, such as a course-code pattern appearing beside “lecture,” “syllabus,” or “semester.”' |

**Recognition**

*Deterministic — pattern plus corroborating context:*

- a record in which a labeled species or breed field co-occurs with a named owner and a named animal, issued by a named veterinary clinic
- a veterinary certificate or health document naming an issuing veterinarian, an identified animal and a labeled species

*Needs the LLM:*

- an animal case discussion with no owner or clinic
- a lab report on an animal specimen that names no species
- a farm or herd record covering many animals

*Never alone — rejected as deterministic signals:*

- a species or breed name — natural history, agriculture, pet-product retail, biology coursework and fiction all carry them
- an animal's name, which is indistinguishable from a person's name in a filename
- the words 'vet', 'pet' or 'animal'
- a clinic name

**Work types:** consultation record, procedure record, vaccination certificate, laboratory report, health or export certificate, prescription, invoice

**Grouping reasons:** one animal's record set; one owner's animals; one episode of care

**Template:** `clinic → animal patient → record type`

> §5.5: 'For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders.' The animal is the record identity. §5.5: 'a parent dimension should provide the context required to understand the child'

**Collides with**

| Domain | Signal that separates them | Design cite |
|---|---|---|
| `med.clinician-patient-chart` | veterinary records use the whole human clinical vocabulary — patient, chart, diagnosis, prescription, radiograph — and share the DICOM format for imaging. The species field and the owner-and-animal pairing are the only reliable separators, and without them a veterinary corpus will be filed as human medical records. | §3.8: 'The system must separate roles that happen to contain the same entity type.' |
| `med.imaging-radiology` | veterinary imaging is DICOM with a populated patient tag, which satisfies the human imaging rule verbatim. | — |
| `biz.invoice-issued` | veterinary invoicing is ordinary practice business. | — |

**Sensitivity:** `potentially_sensitive` — Records naming clients and their animals — 'potentially sensitive', which is §2.9's own phrase and the whole of what this field asserts. No handling class is set here; classification is P7's (§8.4).


### 43. `med.veterinary-pet-owner` — An animal's records held by its owner

What a pet or livestock owner keeps: vaccination certificates, treatment records, insurance, and travel documents for an animal.

**Provenance:** `proposal`  — the design names neither this domain nor any of its fields.

**Schema** — the fields this domain, and only this domain, legitimises:

| Field | Type | Example | Ceiling | Why |
|---|---|---|---|---|
| `animal` | string | the animal the records concern | `direct` | §3.8: 'The system must separate roles that happen to contain the same entity type.' |
| `species` | string | the labeled species | `direct` | §3.5: 'Deterministic extractors create direct facts when the information comes from a reliable, explicit source, such as a content hash, EXIF timestamp, a document title, or a labeled form field.' |
| `owner` | string | the holder of the records | `direct` | §3.8: 'The system must separate roles that happen to contain the same entity type.' |
| `clinic` | string | the veterinary practice providing care | `direct` | §3.8: 'The system must separate roles that happen to contain the same entity type.' |
| `identifier` | string | the labeled microchip, tag or registration identifier | `direct` | §3.5: 'Deterministic extractors create direct facts when the information comes from a reliable, explicit source, such as a content hash, EXIF timestamp, a document title, or a labeled form field.' |
| `record_type` | string | vaccination, treatment, insurance or travel as labeled | `validated` | §3.13: 'A validated fact was found by a deterministic rule and passed contextual checks, such as a course-code pattern appearing beside “lecture,” “syllabus,” or “semester.”' |
| `record_date` | date | the labeled date on the record | `direct` | §3.5: 'Deterministic extractors create direct facts when the information comes from a reliable, explicit source, such as a content hash, EXIF timestamp, a document title, or a labeled form field.' §3.10: 'The product must not use fuzzy date parsing' |

**Recognition**

*Deterministic — pattern plus corroborating context:*

- a certificate or record naming an identified animal, a labeled species and an issuing veterinary clinic, held alongside a named owner
- an animal registration or identification record carrying a labeled microchip or tag identifier together with a named owner

*Needs the LLM:*

- photographs and notes an owner keeps about an animal's health
- a pet insurance claim, which is a finance artifact about an animal
- a receipt from a clinic with no clinical content

*Never alone — rejected as deterministic signals:*

- an animal's name
- a species or breed name
- the words 'pet', 'dog', 'cat' or 'vet' in a filename
- a microchip-identifier-shaped numeric string

**Work types:** vaccination certificate, treatment record, microchip registration, pet insurance policy or claim, travel or export certificate, pedigree or registration, clinic invoice

**Grouping reasons:** one animal's record set; one travel requirement and the documents assembled for it

**Template:** `animal → record type → year`

> §5.5: 'For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders.' The animal is the only sensible first dimension in a household with more than one. §5.5: 'a parent dimension should provide the context required to understand the child'

**Collides with**

| Domain | Signal that separates them | Design cite |
|---|---|---|
| `med.veterinary-practice` | the same records held by the other party; the owner holds one animal's set, the clinic holds many. | — |
| `med.immunisation-record` | an animal vaccination certificate and a human one are the same document shape, and a household corpus contains both. | — |
| `pers.travel-record` | animal travel certificates are assembled for a specific trip and are purpose-coherent with it. | §3.9: 'Topic answers what a file is about, while purpose answers what the file was for.' |

**Sensitivity:** `potentially_sensitive` — Records naming an owner, their address, and their animals — 'potentially sensitive', which is §2.9's own phrase and the whole of what this field asserts. No handling class is set here; classification is P7's (§8.4).

---

## Appendix A — deterministic rules that were rejected

Each of these was drafted as a `deterministic` rule and demoted, because a corpus containing no medical
records at all would trip it. They survive in the `never_alone` lists above.

| Rejected rule | What it would have caught by mistake |
|---|---|
| A drug, vaccine, or brand name | pharmacology coursework, health journalism, supplement inventories, drugstore receipts, recipes, fiction |
| A condition or diagnosis name | advocacy material, insurance marketing, epidemiology coursework, fundraising letters, a novel |
| A modality or procedure word (MRI, colonoscopy, appendectomy) | equipment quotations, patient-education leaflets, science writing, a hospital scene in a screenplay |
| The word *patient* | every nursing assignment, every clinical trial paper, every health-tech product spec, every medical drama |
| SOAP / subjective-objective-assessment-plan section headings | the single most dangerous pattern in the slice: it is *taught*, so every clinical student's coursework reproduces it exactly |
| A clinical code pattern (diagnosis or procedure coding shapes) | a medical-coding student's practice workbook, a payer analyst's dataset, and — for short alphanumeric shapes — version strings and part numbers |
| `Dr.` or a credential suffix (MD, RN, DDS) | academic citations, ordinary correspondence, letterheads of every kind, fiction |
| A provider- or record-identifier-shaped numeric string | phone numbers, order numbers, invoice numbers — §3.10 already warns that such numbers are as likely to be version, build, or postal codes |
| A dose-shaped token (quantity + mass unit) | chemistry lab reports, recipes, supplement labels, any materials list |
| A hospital, clinic, or practice name | the same name appears as an employer, a research venue, a donation recipient, a birthplace, and a cited affiliation — §4.9's rule transfers directly: *A university name alone should not create a group* |
| Vital-sign-shaped values (a blood-pressure pair, a heart rate, a weight) | fitness apps, sports team logs, nutrition trackers, biology practicals — this rejection is why `med.wearable-health-export` exists as a domain of its own rather than being absorbed into a clinical record |
| An exercise table with sets, repetitions, and frequency columns | a personal-training programme, a gym app export, a fitness magazine plan — structurally identical to a prescribed therapy programme |
| A per-reading table of a measure and a timestamp | every habit tracker, sleep log, and weight log ever exported |
| Filename tokens: *labs*, *lab report*, *test results*, *scan*, *chart*, *rx* | `lab report` is an academic work type in this product's own contract example; `test results` is an exam score or a software test run; `scan` is a document scan; `chart` is a graph; `Labs` is a company-name suffix |
| A folder named *Health*, *Medical*, or *Records* | a health-writing portfolio, a health-tech product folder, a public-health course, and the literal name of a consumer phone app. §5.10 makes a curated folder strong evidence of *intent*, not of subject matter |
| The word *consent* | research consent, photo releases, school permission slips, cookie banners |
| The word *discharge* | employment discharge, battery discharge, an environmental discharge permit |
| The word *admission* | university admissions — the collision is total, and only a paired admission/discharge date label with a facility resolves it |
| The word *claim* or a claim number | motor, home, travel, warranty, and contents claims |
| *Incident report*, *root cause analysis*, *post-mortem* | core software-operations vocabulary; in a mixed corpus these will outnumber clinical ones by a wide margin |
| *Protocol*, *SOP*, *pathway*, *runbook* | bench protocols, manufacturing procedures, IT runbooks, research method sections — in a research corpus *protocol* means something else entirely |
| A completion certificate | online course platforms issue them by the million and none carry a credit designation |
| The word *licence* / a licence identifier | software licences, business licences, driving licences — and a file literally named `LICENSE` is a source-code convention |
| A gene symbol | a short uppercase token colliding with tickers, acronyms, and identifiers, and ubiquitous in biology coursework — §3.7's word-boundary warning applies with particular force |
| A trial registration identifier | every paper, protocol, grant application, and news story about that study |
| A DICOM signature or extension on its own | research imaging and veterinary imaging are the same format; §2.9 requires the extension to be *a routing signal rather than an assumption about meaning* |
| A species or breed name | natural history, agriculture, pet retail, biology coursework, fiction |
| A serial or model number with a manufacturer | every asset register, warranty, and receipt in existence |
| A rota or shift table | hospitality, retail, security, and manufacturing all produce them |
| A standardised screening-instrument name | psychology coursework, research datasets, and public self-screening tools reproduce them in full |
| High medical-vocabulary density of any kind | the density test is the worst rule of all: a pre-med student's corpus scores higher than a real patient's |

Two structural safeguards carry the rest of the load, and both are the design's own:

1. **Two plausible domains is the LLM's case, not a rule's.** §3.3 sends files that
   *have multiple plausible domains* to the model. Where a medical rule and an academic anchor fire on
   the same file — a lab-report-shaped table beside a course code, an encounter note beside a rubric —
   the file is routed, not decided.
2. **Contradiction outranks pattern.** §3.6 requires the validator to check *that no stronger direct or
   rule-validated fact contradicts it*.

---

## Appendix B — every open question, verbatim

These are copied into `NEEDS-JOSEPH.md` unchanged. Each is a decision about how someone's real life
gets shaped into folders, which the contract puts outside this catalogue's authority.

**`med.personal-health-record`**

> Should a person's own records and a dependant's records share one branch with `subject_person` as the first dimension, or should each subject person get their own top-level branch? For a single-person corpus `subject_person` produces exactly the one-child level §5.9 tells the product to warn about; for a caregiver it is the only sane first split. This is a default folder shape for someone's real family and is Joseph's call, not the catalogue's.

**`med.lab-result`**

> Serial record domains — lab results, imaging, and monitoring logs — may genuinely want time as the first dimension, which contradicts §5.5's default that for document and record domains subject comes before time. §5.5's stated exception is 'Photos and capture-based media', not serial clinical results. Does the exception extend to them? Joseph's call; the catalogue follows the stated default until he says otherwise.

**`med.referral-received`**

> Is 'second opinion' a domain or a purpose facet? §3.9 makes purpose a first-class facet answering what a file was for, and a second-opinion packet is exactly a purpose-coherent set of otherwise ordinary records — a referral, a records release, a prior report, a new consultation. The catalogue folds it into this entry rather than giving it a schema of its own, because its would-be fields are already the referral's. If Joseph wants a distinct branch for it, it becomes a purpose-defined packet in §5.6's sense rather than a new schema.

**`med.mental-health-record`**

> Should the engine open the contents of a personal journal or diary at all in order to decide whether it is a mental-health record? Every deterministic route in this domain is administrative — bills, appointments, authorisations — and the content route requires reading private prose. §8.4 requires privacy policy to be enforced before content reaches any model; it does not say whether local extraction may read such a file in the first place. Joseph's call.

**`med.chronic-condition-management`**

> Should a condition ever appear as a literal folder name in a proposed tree? A branch named for a diagnosis is legible to anyone who opens the file manager or sees a shared screen — §8.4 already makes this point for filenames, noting that a summary may be safe to show where a visible list of filenames is not. Whether the same reasoning forbids condition-named folders is a product decision about someone's real life, and is Joseph's.

**`med.pregnancy-maternity-record`**

> This domain must not be given a default folder shape by the catalogue. A branch keyed on a due date, a child's name, or a pregnancy count encodes an assumption about an outcome — a pregnancy may have ended, may be one of several, or may be one the person does not want surfaced. The catalogue therefore proposes only `subject_person` and `record_type` and states plainly that any deeper default is Joseph's decision to make deliberately, not the catalogue's to assume.

**`med.caregiving-dependant`**

> When a corpus contains records for several people, does `subject_person` become a top-level branch, a dimension inside a single medical branch, or a facet that is never a folder at all? §3.8 forbids using authorship or creator identity as a destination dimension, but the cared-for person is a subject, not an author, and for a carer it is the only structure that works. The catalogue proposes it as the first dimension and flags that the decision is Joseph's.

**`med.clinician-patient-chart`**

> A clinician's corpus contains records about many people who are not the user. §8.4's privacy rules are written for a person's own corpus; whether a professional corpus needs a different consent posture entirely — and whether the product should offer to organise it at all — is a product-scope decision, not a catalogue decision.

---

## Appendix C — domains folded in rather than given entries

| Candidate | Folded into | Why it is not a domain |
|---|---|---|
| Emergency and urgent care visits | `med.hospital-admission-discharge` | the schema is the encounter schema; *emergency department record* is a work type, not a different set of legal fields |
| Second opinions | `med.referral-received` | §3.9 makes purpose a first-class facet; a second-opinion set is purpose-coherent, and its would-be fields are already the referral's. Recorded as that entry's open question |
| On-call schedules and rotas | `med.practice-administration` | a rota is a calendar artifact (§2.9's ICS row) whose only extra fields are service line and coverage period, both already practice-administration fields |

