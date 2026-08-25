# J-DEPTH — clinical_practice.teaching-material deepening memo

Verdict: **REFUSED.** This reverses the gist draft. Its fixtures were useful and are preserved, but they prove education structure plus a separate privacy boundary—not a clinical teaching template. Medical teaching is teaching whose topic is clinical. Patient identifiers and governed protocols create their own clinical readings.

## Sources and comparison set

Read the standing brief, deepening addendum, stamped `make_prompt.py clinical_practice.teaching-material` output, `ALIGNMENT.md`, `00-database-agent-product-design.md`, `CONNECTION.md`, `CONNECTION-EXAMPLES.md`, `_CONTRACT.md`, canonical fields, roster, and deepened `clinical_practice` anchor. Compared the required `clinical_practice.licensure-credentialing` refusal, `patient-chart`, `protocol-guideline`, `academic.teaching`, `academic.coursework`, and `academic.continuing-education` rows.

All quotations were checked against `00`. The controlling distinction is: “Topic answers what a file is about, while purpose answers what the file was for.” The controlling safety rule is: “Privacy policy must be enforced before content reaches any model or external connector.” Both hold without this node.

Legacy `med.medical-teaching-material` coverage is routed rather than erased.

## What changed

The gist draft kept the row on objectives-plus-audience detection and stricter privacy for anonymised cases, while conceding dimensions could not differ. Full comparison defeats both claimed distinctions. Objectives, audience, assessments, simulation, attendance, feedback, and recordings are already academic teaching/coursework structures. Burnt-in patient identifiers are a clinical/P7 signal on the affected file, not proof every medical lecture belongs to clinical_practice.

JSON changed first: refusal is true; fields/proposals remain empty; claimed work types and edges are emptied; nine fixtures remain as routing tests; residuals are explicit.

## Node test

### Fields

`clinical_practice` declares no fields. This row cannot introduce session, audience, specialty, educator, or learner. `specialty` is topic. Educator/learner are roles already handled by academic teaching versus coursework. The leg is unsatisfiable, not a pass.

### Detection

The draft's learning-objectives plus intended-audience pair distinguishes teaching from chart or guideline, but not clinical teaching from teaching. The same subtraction applies throughout:

- case discussion sequence: teaching structure plus clinical topic;
- option lists, answer key, examiner checklist, blueprint: assessment work types;
- faculty script, timed prompts, debrief: simulation teaching;
- attendance, certificates, ratings: course/session administration;
- lecture-capture metadata: source clue, never alone;
- presenter and hospital: person/organization values.

Delete specialty terms, hospital/society names, clinician titles, presenter names, extensions, and teaching/rounds/case words. Objectives, audience, curriculum, assessment, authored master, received copy, administration, and feedback remain. Those are academic signals. Nothing uniquely clinical remains.

Practitioner-versus-learner does not rescue it. A practitioner authoring rounds occupies an instructor role; receiving MRCP revision material occupies a learner role. A byte-identical deck may reveal neither. Academic teaching already recognizes this ambiguity. “Correct abstention is a successful outcome because the product’s goal is reliable organization, not maximum file movement.”

### Dimensions

No legal fields means no dimensions. “Session then function” is an education organization populated with clinical values. Presenter is no substitute: “It should avoid using authorship or creator identity as a destination dimension.” Patient identity is an even less acceptable folder level.

### Privacy without blanket rescue

A genuinely anonymised vignette has no real subject relation and is teaching about medicine. A vignette retaining name, record number, accession, voice, or pixel text triggers protection and possibly the clinical anchor/patient-chart. This is two-stage routing: inspect safely for identifiers, then route education and real-subject evidence independently.

Proximity propagates nothing: “The graph does not automatically copy those missing facts onto sparse files.” A clean deck does not cleanse an embedded image; an unsafe image does not turn every handout into a patient chart. Staff attendance and feedback can be protected academic/employment-adjacent records without a clinical node.

## Concrete file audit

1. `Grand rounds - chest pain in the young - 2026-03-11.pptx`: objectives/audience/session → academic teaching; clinical terms are topic. Check notes, media, metadata, and pixels.
2. `case 4 - 68yo with chest pain.docx`: age/sex plus discussion questions → education; real name/DOB/record number → patient-chart. Headings alone support neither.
3. `IM-0001-0007.jpg`: surname and hospital number burnt into pixels. Danger fixture, not node evidence; Protected Records/clinical review.
4. `Sepsis pathway v4.2 - ratified 2026-01.pdf`: approval/effective/review governance → protocol-guideline. A neighbouring deck does not change it.
5. `MRCP practice questions with answers.docx`: authored bank → academic teaching; received revision copy → coursework/continuing education; absent role → Review Later.
6. `feedback summary - teaching March.xlsx`: academic evaluation, potentially also employment/performance; identifiers require protection.
7. `attendance - simulation day.pdf`: educational administration with names/signatures; clinical scenario topic changes nothing.
8. `GMT20260311-140302_Recording.mp4`: untranscribed and sensitive; deck context may support membership but cannot copy title/topic.
9. `Teaching portfolio 2026.zip`: purpose packet across academic, career, and possibly clinical members. “The documents are content-incoherent but purpose-coherent.” Members keep their own readings.

## Considered and rejected

- Published cardiology lecture: received teaching/reading; society and clinical vocabulary never alone.
- Student case essay: learner output, academic coursework.
- Bedside-teaching plan without identifiers: educator-authored academic teaching.
- Real case-conference outcomes: named cases/actions belong to case-conference or patient records.
- Conference abstract: abstract/venue/submission belongs to research; later deck may join both groups.
- Patient-information leaflet: governed instruction belongs to protocol-guideline.
- Blank OSCE proforma: assessment document type; clinical station is topic.
- CPD certificate: academic continuing education and/or career credential evidence.
- M&M action record: real cases/actions belong to case-conference/malpractice; teaching purpose may coexist.

## Reciprocal boundaries

Academic teaching/coursework: objectives, audience, assignments, answer keys, cohort administration, and authored masters route academic regardless of specialty. Learner-received artifacts route coursework/continuing education. Clinical topic sends nothing back to this refused row.

Patient chart/anchor: filled real subject, record number, DOB, accession, or author-versus-different-subject relation triggers clinical protection. Anonymised/fictional case with objectives is academic. Unresolved identifier status goes Protected Records/Review Later, not here.

Protocol guideline: approval/effective/review governance and class-of-patient instruction route protocol; objectives/audience/assessment route academic. Quotation in a deck does not move the governed source.

Licensure/credentialing: the deepened row is itself refused into career credentials and continuing education. Portfolio is a group. Decks stay academic; certificates stay academic/career; case logs activate clinical protection.

Research presentation: abstract, acceptance, venue, and authors support research. Trainee audience/objectives support academic. Both groups may hold one deck; specialty creates no node.

## Proposed fields

None. `audience` and `session` cannot be minted here; `specialty` is topic; presenter is not destination-eligible; patient identity belongs only to the anchor's unresolved proposal and is not copied into teaching files.

## Neighbours considered without edge

This refused row authors no edges. R1c owns repointing. `medical`: only holder-specific health evidence activates it; generic course material stays academic. `legal`: discoverability is not structure. `business_operations.meeting-record`: an agenda/recording may join a meeting group but needs no clinical edge. `hr.training-development`: mandatory training overlaps by employment purpose, not specialty.

## NEEDS-JOSEPH

- **NJ-CP-TM-1:** repoint every neighbour naming this refused id; no neighbour was edited here.
- **NJ-CP-TM-2:** recommend Protected Records by default when de-identification has not been checked across notes, media, metadata, audio, and pixels. This is privacy policy on academic material, not a node.
- **NJ-CP-TM-3:** instructor-versus-learner evidence threshold remains injected; no numeric rule is invented. Abstention is valid.

## Reopening test

Reopen only for a named, routinely kept artifact whose relation cannot be expressed by educator/learner, clinician/subject, governed document, research output, credential purpose, or accepted group. Anonymised cases, practitioner occupation, specialties, and longer slide/handout lists do not qualify. No such artifact was found.
