# Research memo — `manufacturing.hse-incident`

Depth: J-DEPTH
Date: 2026-08-27
Output: `planning/domains/nodes/manufacturing.hse-incident.json`
Roster row: template on the fieldless `manufacturing` schema, `parent_id: null`, placeholder launch

## Result

**Accept**, narrowly and on one decisive leg. The row survives because its **privacy rule differs from the manufacturing schema's default in kind, not degree** — it is the only situation on this schema whose principal subject is an identified third party's body — and because its **detection signals reach files the schema default cannot fire on at all**. Its dimension recommendation also inverts the default's subject-first branches, because an incident routinely has no product, no lot, no instrument and often no asset to sit under.

I came close to refusing. The case against is stronger than for most templates and is set out in full before it is answered.

## THE CHARGE — the strongest case that this row should not exist

**1. It is a work_type value.** Not speculative: the `manufacturing` schema's own `work_types[]` already contains *"site HSE inspection, permit, risk assessment or incident record"*. The schema has enumerated me as one value of fifteen, and the dispatch prompt is explicit — *"`work_types[]` is an enum of values for a `work_type` (or equivalent) field. Do not ask R1a for a child node per work type."*

**2. It is a lifecycle stage of a neighbour.** The roster hint reads "the report, the investigation and what changed because of it" — report, investigate, correct. That is the arc `manufacturing.nonconformance-capa` owns, whose schema-level signal already describes *"a corrective-action structure joining problem statement, root-cause analysis, correction, corrective action, owner, due date and effectiveness-verification slots to one quality-event identifier."*

**3. Half of it is defined by an absence.** "Or nearly was." A near-miss is definitionally the non-occurrence of an injury, and a row whose evidence is that nothing happened cannot activate.

**4. "Incident report" is a document-type word.** IT service management, information security, clinical governance and hotel front desks all file documents with that exact phrase.

**5. It duplicates `construction_property.site-health-safety`**, which is on the roster and holds the identical form layouts.

**6. Never-alone evidence only.** Strip the person's name, the department name, the document-type word and the date — all never-alone — and the fear is nothing is left.

## Defeating it

**Charge 1.** The schema's work_type entry conflates four things — *inspection, permit, risk assessment, incident*. The first three are asset-or-site-anchored control records the default handles correctly. The fourth is not, and this is testable against the schema's own deterministic list: all twelve of its signals require a product-and-lot pair, an instrument identity, a work order with an asset, a specification-versus-measured-result pair, a genealogy table, an asset register population, or a line log with output counts. Take `Near miss card NM-2026-0188 coolant spill aisle 4.pdf` — labelled event identifier, hazard, explicit no-injury outcome, owner, closeout status, and **no product, lot, instrument, specification, measured result, disposition or asset** (an aisle is not a controlled asset). Under the default it fires nothing. Under this row it activates. A template whose signals reach files the default cannot reach is not a subset of it.

The deeper answer: a work_type value cannot carry a privacy rule. `record_type = incident report` is a fact written onto a file; it cannot say "this family defaults to Protected Records and must not have its filenames or content exposed in model prompts." Only a template can, and CONNECTION §2 names privacy rules as a qualifying leg for exactly this case.

**Charge 2.** Neither row is a stage of the other, because each exists without the other. A near-miss card is opened, actioned and closed with no CAPA ever raised — the closeout status *is* the card. Conversely `CAPA-2026-012` may arise from a customer complaint, a supplier lot failure or an audit finding with no incident at all. What is true is that they **collide when an incident triggers a CAPA**, authored below as a reciprocal boundary with one fixture on both sides. The discriminator is what was harmed: a person or an article.

**Charge 3.** A near-miss report is not the absence of an injury report. It is a positively authored document with its own printed form, identifier series and closeout workflow, and the "no harm" outcome is a **filled-in field**, not a missing one. Same distinction 00 draws in forbidding missing EXIF as proof of a screenshot: absence never proves, the card's presence does.

**Charge 4.** Conceded and encoded rather than argued away. `never_alone` leads with *incident, incident report, accident, near miss, investigation* and names the four rival corpora. The row activates not on the phrase but on the **co-occurrence of an event time, a person role and a harm description** — the shape the phrase merely labels. This mirrors the schema's own "the words batch or production alone" and "the word certificate alone never fires."

**Charge 5.** Answered reciprocally below. Both rows hold the same form; the discriminator is the surrounding operational anchor, never the form.

**Charge 6.** This is the charge that would have forced a refusal, and it fails on structure. An injury report is not a name plus a date; it is a labelled multi-slot form — event date and time, location, task at the time, what happened, injury and affected body part, treatment given, return-to-work status, completed-by. The OSHA Form 301 *Injury and Illness Incident Report* has exactly that slot set, and the OSHA Form 300 *Log of Work-Related Injuries and Illnesses* has a repeated-row shape (case number, job title, date, location, description and body part, mutually exclusive death / days-away / transfer-or-restriction / other-recordable columns) that nothing else in a manufacturing corpus resembles. That is structure, and structure activates. Names inside it stay never-alone.

## The node test, all three legs

The schema's **default template**, quoted from its own node file: *"product then batch/lot then record type for production and quality records; site then asset then record type for maintenance and calibration; quality event then record type for NCR/CAPA files"*, `time_first: false`, sensitivity justified by commercial confidentiality, residuals Independent Records / Receipts and Confirmations / Review Later / Unsupported or Encrypted.

**Leg 1 — detection signals: DIFFERENT.** Argued above. The default anchors on a made article, a controlled instrument, a maintained asset or a measured characteristic. This row anchors on a dated event and an exposed person, and three of its eight deterministic signals (near-miss card, witness statement, statutory injury log) carry no product, lot, instrument or asset slot at all. The schema's single HSE line requires the structure be *"tied to a controlled site or asset"* — true of an inspection and a permit, false of most incidents.

**Leg 2 — privacy: DIFFERENT, and decisive.** The schema's `sensitivity_why` is about the holder's commercial exposure — *"Production recipes, tolerances, yields, failures, supplier lots, plant layouts, asset condition and corrective actions can be commercially confidential"* — with a trailing clause that *"incident and competence records can name workers."* Here that clause is the entire subject. An injury report is a document about an identified other person's body, treatment and treating facility, held inside a business corpus. 00 says Protected Records *"may represent sensitive isolated material such as passport scans, medical documents, account statements, visas, legal forms, or credentials; it should normally remain local-only and must not cause filenames or content to be exposed in model prompts."* An injury report is a medical document by that description. **The manufacturing schema's residual set contains no Protected Records route at all.** This row's does, and leads with it. That is a different rule, reached for a different reason, about a different person.

The consent question flips with it. Every other manufacturing template protects the owner's secrets, which the owner can waive. Here the subject cannot consent, is usually not the corpus owner, and may not know the file exists.

**Leg 3 — dimension order: DIFFERENT.** The default's live branches are product-first and site-then-asset. This row cannot use the first and often cannot complete the second. Its recommendation is **site → incident event → record type**. There is also a time pressure found nowhere else on this schema: the statutory injury log and its annual summary are per-establishment, **per-calendar-year** documents, so a year level under site is defensible for that family. I still set `time_first: false`, because year-first would scatter one incident's report, statements, photographs and actions across calendar folders — the schema's own quoted reason. Left visible as NJ-HSE-3 rather than smoothed.

Two legs differ decisively, the third materially. The row stands.

## Fields

`fields: []` (PR-6) and — deliberately — **`proposed_fields: []`**. Rejected candidates:

- **An incident/event anchor.** Genuinely needed and genuinely already proposed: the schema proposes `quality_event`, and its own NJ-MFG-2 asks whether that should become a broader canonical `case`/`event` *"shared with incident, complaint and corrective-action schemas."* The brief says reuse an existing proposal rather than mint a variant; minting `incident_id` would fragment one concept across siblings and pre-empt R1c. Recorded as NJ-HSE-1.
- **`site`, `asset`, `record_type`** — already schema proposals; this row reuses and adds nothing.
- **Severity, recordability, reportability, lost-time status** — rejected outright. Each is a regulated *judgement*, not an observation. Serializing any would have the catalogue deciding a compliance question. Named in `must_not_conclude`.
- **The injured person, witness, investigator** — rejected as destinations on design authority. 00: the system *"should avoid using authorship or creator identity as a destination dimension"*, and *"A folder should not become a collection point for everything produced by the same person or organization."* That applies with more force to a person who is the *subject* of a harm record than to one who authored a document.

`role_split` is empty for the same reason. 00 says *"The system must separate roles that happen to contain the same entity type"*, and this row has four person-roles on one file — harmed party, witness, investigator, approver. With no field keys, that separation cannot be serialized; recorded here for R1c.

## Files considered and rejected

- **`Safety Data Sheet - Coolant XR-40.pdf`** — dense with injury vocabulary, first-aid measures and hazard pictograms. Reference material *about* a hazard, supplier-issued, no dated event, no person. Named in `never_alone`.
- **`Site safety inspection Plant 2.pdf`** — the schema's own fixture and the primary collision (below).
- **`NCR-2026-041 cracked housing.pdf`** — the schema's own fixture; shares event / containment / root cause / closure vocabulary, but the harm is to an article.
- **A machine-guarding risk assessment** — prospective, not retrospective; `manufacturing.safety-case`'s unless it back-references one incident identifier, in which case only the revision joins.
- **A scheduled training record** — structurally identical to a post-incident toolbox-talk sheet; the back-reference in the topic line is the only discriminator.
- **A corporate H&S policy or handbook** — `business_operations.policy-handbook`; the schema already warns *"generic corporate policy text is not enough."*
- **`Vehicle accident report VAN-14 2026-02-02.pdf`** — a real injury and still not this row's, because it happened on a public road under transport rules. Kept as a fixture precisely because instinct is wrong here.
- **A first-aid supply invoice inside an incident folder** — folder co-location is not evidence; it is a transaction, routed by 00 to Receipts and Confirmations.
- **An EHS software system** — a source system, not a file node. A bounded export with a readable manifest is represented; a live connector is a later security decision.

## The collision fixture

**`Site safety inspection Plant 2.pdf`**, chosen because it appears in the manufacturing schema's own default file list — so this row and its schema anchor are already looking at the same bytes. It carries hazard, control, responsible role, closeout, an inspection date, an inspector and a plant name, and reads exactly like an incident record.

**What discriminates it:** no event and no exposed person. An incident record narrates *one thing that happened at a time to someone*; an inspection enumerates *conditions found on a walk*. The operational test is a filled event date-and-time slot distinct from the document date, plus a person-exposure or no-harm-outcome slot. The inspection has neither, stays with the schema default, and falls to Independent Records when unanchored. Note the trap: `never_alone` must and does exclude the word *safety*, or this fixture would activate on its filename alone.

A harder second fixture: **the same printed accident-report form used on a construction site inside the same factory building**. The bytes are identical to a plant injury report; only the surrounding anchor separates them.

## Reciprocal boundaries

Eight are authored in `collides_with` as objects naming one fixture and the discriminating evidence in both directions. The four load-bearing ones:

- **`manufacturing.nonconformance-capa`** — fixture `CAPA-2026-012 effectiveness review.docx` opened for IR-2026-014. *Here:* the event record of harm to a person. *There:* the nonconformance workflow anchored on a product, lot, process or requirement. Both ways: injury / body-part / treatment / exposure slots versus requirement-versus-observed-condition, affected lot and disposition. A file with both is two records in one packet.
- **`construction_property.site-health-safety`** — fixture `Site safety inspection Plant 2.pdf`, plus the identical accident form on both sides. *Here:* events inside an operating plant with a controlled line, process or machine. *There:* events on a construction or property site under a professional instruction. Both ways: a line, cell, production shift or production asset versus a project or contract reference, principal-contractor or designer role, work package or construction phase. **The form is never the discriminator** — a fit-out injury inside a factory is theirs despite the address; a forklift striking a pedestrian on the line is this row's despite a contractor being involved.
- **`medical.personal-health-records`** — fixture: an occupational-health report on the person injured in IR-2026-014. *Here:* the employer-side record that an event occurred, held about a third party. *There:* the corpus owner's own clinical record. Both ways: a clinician-to-employer report with an employer addressee and an incident identifier versus the same letter addressed to the patient in the patient's own corpus. Neither row may route the other's file into a shallower privacy posture, and membership never converts a third party's health data into the holder's medical facts.
- **`business_operations.risk-register`** — fixture `HSE risk register 2026 - Plant 2.xlsx`. *Here:* individual dated events; a statutory injury log is an **event** log, not a risk register. *There:* the standing artefact of enumerated risks with owners, ratings, treatments and review dates. Both ways: repeated event date / location / outcome per row versus a likelihood-and-impact grid, treatment plan and next-review date.

The other four are authored in the same both-directions form: `manufacturing.safety-case` (retrospective event versus prospective safety argument), `manufacturing.environmental-compliance` (harmed person versus receiving medium and permit condition — a spill can genuinely be both), `logistics.driver-compliance` (plant boundary versus public road and transport rules), `finance.insurance-corporate` (event narrative versus policy, claim reference, reserve, settlement).

## Neighbours considered without an edge

- **`engineering` / `engineering.risk-analysis-fmea`** — an FMEA is prospective; that argument is already carried once against `manufacturing.safety-case` and a second copy adds nothing. An incident-driven design change is `engineering.change-order`'s and joins this pack only by explicit back-reference. (Recorded because engineering is on the must-consider list.)
- **`career.employment-records`** — return-to-work and post-incident disciplinary records sit between the two. Left as a non-edge because the third-party-personal-data seam is already carried by the medical boundary; R1c should reconsider if that row lands claiming return-to-work records.
- **`manufacturing.maintenance-work-order` / `manufacturing.asset-register`** — the machine that injured someone also gets a work order; the work order stays theirs, only the back-reference joins.
- **`photos.*`** — scene photographs are a fixture-level coactivation (`also_schema: "photos"`, `group_without_copying_facts: true`), not a mutex.
- **`clinical_practice.malpractice-incident`** — the nearest-named row on the roster and genuinely disjoint: harm to a *patient* arising from care, in a clinician's corpus. No shared fixture, no edge.

## `also_holds_with` — empty, and why

CONNECTION §5 makes `also_holds_with` **schema ↔ schema only**, and this is a template. The schema anchor already carries manufacturing's coactivations. The ones this row observes are recorded here for R1c: **manufacturing ↔ finance** (an employers-liability claim carries an event cross-reference plus independent policy / claim / reserve evidence); **manufacturing ↔ medical** (an occupational-health report carries an incident identifier plus independent clinical evidence, with the privacy caveat above); **manufacturing ↔ photos** (scene photographs carry independent capture evidence). None is a collision.

## Grouping without copied facts

Groups are bounded by an exact incident identifier, or — for near-miss cards, which often have none — an exact event date-time plus the same named location. An archive manifest is read without unpacking. Membership creates no facts: a photograph in `Incident pack IR-2026-014.zip` acquires no event, person or outcome, and a statutory log row's outcome column is never copied onto a pack member. Both marked `group_without_copying_facts: true`.

## Residual routing

Protected Records leads, on the 00 span above, and is this row's clearest departure from its schema anchor. Independent Records takes the de-identified end — a near-miss card naming no one, a safety alert, a regulator acknowledgement, a blank form — which should **not** be pushed into a protected posture merely for carrying the word incident. Review Later takes OCR-poor logbook pages and property-damage reports with no named exposed person. Unsupported or Encrypted takes encrypted registers and proprietary EHS exports.

**Receipts and Confirmations** was on the must-consider list and is deliberately **not** routed to. The tempting case is the regulator submission acknowledgement, which looks like a confirmation. It is not: 00 scopes that residual to *"isolated invoices, delivery confirmations, booking records, boarding passes, purchase receipts, event tickets, and similar transactional documents"* — all transactional. A notification that a person was injured is not a transaction, and routing it there would strip the protected posture off a record naming an injured worker. The first-aid supply invoice does belong there, and the schema anchor already routes it.

## NEEDS-JOSEPH

- **NJ-HSE-1 — the event key.** A safety event is not a quality event, but minting `incident_id` alongside `quality_event` fragments one concept. Alternatives: (a) widen `quality_event` to any controlled event with an identifier and a closure state; (b) mint one shared canonical `case`, constrained per schema; (c) accept two near-identical keys. This row is the concrete pressure on the schema's own NJ-MFG-2.
- **NJ-HSE-2 — may an incident identifier ever appear in a visible folder label?** On a small site, a branch named for one event identifies the person it happened to. Alternatives: never surfaced (redacted display, local-only alias); surfaced only on explicit opt-in; surfaced freely because it is the organisation's own reference. Same shape as the legal row's client-name question.
- **NJ-HSE-3 — one row, two dimension recommendations?** The statutory-log family is per-calendar-year while the rest of the row is event-anchored. Either a template may carry a per-family recommendation, or the log family needs separate handling, or the year level is dropped and logs sit flat under site.
- **NJ-HSE-4 — third-party health data in a business corpus.** `medical.personal-health-records` assumes the health data is the corpus owner's. This row's is not. Decide whether it needs a distinct treatment or whether Protected Records plus a no-remote-prompt rule suffices.
- **NJ-HSE-5 — the abstention floor.** This row must never infer recordability, reportability, work-relatedness, severity, fault, liability or fitness for work — yet those are exactly what a user will want answered. Confirm abstention is intended here, as it is for privilege on the legal row.

## Self-verification

`python3 -m json.tool` parses. Key set is identical to the landed `legal.practice-matter-file.json` (zero symmetric difference). All eight `collides_with` entries are objects with `domain` / `signal` / `provenance`, and all eight ids exist on `planning/domains/roster.json`. `also_holds_with` empty (template; CONNECTION §5). Every `source_type` in `file_kinds` and in all fifteen `file_examples` is in `SOURCE_TYPES`. Every `falls_through_to` and `falls_through_if_inactive` name is one of 00's nine residual homes. `fields: []`, `proposed_fields: []`, `dimension_order: []`, `design_cite: null`. All seven verbatim 00 spans quoted here and in the JSON were confirmed with `grep -cF` against `planning/00-database-agent-product-design.md` (each returns 1). No threshold numbers, no handling classes, no invented ids. Only the two assigned files were written.
