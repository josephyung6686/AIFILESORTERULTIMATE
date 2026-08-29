# Research memo — `hr.workplace-health-safety`

Date: 2026-08-26
Depth: J-DEPTH
Output: `planning/domains/nodes/hr.workplace-health-safety.json`
Roster row: template on the fieldless `hr` schema, `parent_id: null`, `launch: placeholder`
Absorbs: the legacy row `med.occupational-health-screening` (employer side only)

## Result

**Accept**, with a stated shrink-tolerance and one contested boundary escalated. The row survives the node
test on all three legs, but its acceptance is conditional on NJ-HR-1 (does the `hr` schema survive at all)
and its size is conditional on NJ-WHS-2 (the contested split with `business_operations.facilities-workplace`).
Both conditions are written into the JSON's `open_question` rather than smoothed away.

## The charge — the strongest case that this row should not exist

I built the case against the row before writing anything, in five forms, strongest first.

**(1) It is a single `work_type` value on its own schema.** This is the sharpest form and it is not
hypothetical: `hr.json`'s `work_types[]` array contains, verbatim, the entry `"workplace risk assessment,
safe system, inspection, incident, occupational-health, or statutory report"`. That is one enum member.
The dispatch prompt says outright that work types are values, not nodes. On its face this row is a request
for a child node per work type — the recorded 574 failure.

**(2) It is a document-type word.** "Risk assessment", "incident report", "method statement", "safety
data sheet" are document types. A row whose whole identity is a list of form names is a file-kind node.

**(3) It is a duplicate of neighbours that have already carved it up.** Four landed rows have each authored
a discriminator that takes a slice of this territory: `business_operations.facilities-workplace` claims the
premises assessment, `construction_property.site-health-safety` claims the job-bounded safety record,
`business_operations.compliance-audit` claims the safety audit, `business_operations.risk-register` claims
the hazard-and-control table, `government.emergency-management` claims the fire and evacuation apparatus,
`clinical_practice.malpractice-incident` claims the incident form, and `hr.employee-relations` claims the
investigation-with-a-case-reference. If every one of those holds its side, what is left?

**(4) It is a row defined by an absence.** The honest reading of (3) is that this row is "safety material
that is not a construction job, not a premises, not a patient, not a conduct case, not an audit, not a
corporate risk". That is a residue, not a filing world.

**(5) It is a duplicate of its own schema's default template.** `hr.json`'s deterministic list already
contains a bullet reading `"an employee-relations or workplace-safety case form carrying a labelled
case/incident reference together with subject/employee, event or allegation, investigator/manager, outcome
or corrective-action slots"`. The schema default already recognises the safety case. A template whose
signals are its schema's signals must be refused.

## Defeating the charge

**Against (1), (2) and (5) — the one fact that breaks all three.** The `hr` schema's activation anchor,
stated three separate times in `hr.json`, is a person or a population: it "requires a personnel process,
workforce population, or employee case structure", and its `never_alone` list explicitly refuses "a generic
policy, handbook, procedure, meeting record, project plan, risk register, survey, dashboard, org chart, or
retrospective shape alone" because "the HR side requires a workforce population, personnel process, or
employee case".

A very large share of this row's real evidence **names no employee at all and involves no personnel process
whatsoever**. A COSHH assessment of isopropanol in Lab 2 has a substance as its subject and populates its
persons-at-risk slot with *classes* — lab staff, cleaners, contractors. A fire risk assessment has a
building as its subject. A machine-guarding assessment has a press. A permit to work has a task. A statutory
annual injury summary has aggregate counts and certifies that no individual is named. Under the schema's
own default template every one of those files **fails activation** and falls to `business_operations`.

So this row's activation anchor is genuinely different in kind from its schema's default. The anchor is not
a document-type word and not a work-type value; it is a **slot set**: hazard (or task, substance, area) +
persons at risk + existing controls + residual evaluation + further action + assessor + review date, under a
stated duty. That structure is checkable, it is true of the file list, and it is the thing an SDS lacks and
a COSHH assessment has — which is exactly why the SDS is this row's collision fixture. A template that
activates on evidence its schema's default would reject is not a duplicate of that default. **Leg one of
the node test passes.**

Second independent difference: the **statutory-return spine**. An OSHA 300A summary, a RIDDOR F2508, an
annual injury log — these are the only artefacts anywhere on the `hr` schema whose intended reader is a
state regulator and whose payload is an aggregate injury count with a certification signature. Neither the
schema default (a personnel process) nor `business_operations.compliance-audit` (an audit against a
management standard) recognises that shape.

**Against (3) and (4).** The residue objection would be fatal if the neighbours' claims were sound and
exhaustive. They are neither. Three of the seven claims are boundaries this row *accepts and reciprocates*
without losing its core: `construction_property.site-health-safety` correctly takes the CDM-bounded job,
`clinical_practice.malpractice-incident` correctly takes the patient-subject event (and correctly gives me
the staff-subject one — its own memo says so), and `hr.employee-relations` correctly takes the capability
case. Two more are boundaries where the neighbour's own text concedes my side: `business_operations.risk-register`
says in its own fixture that reading a statutory duty-of-care assessment as corporate risk "would file a
statutory record in a management branch", and `government.emergency-management` splits on scope of duty and
leaves one premises with a responsible person to me.

That leaves **one** genuinely contested claim, `business_operations.facilities-workplace`, and it is not a
residue argument — it is a disagreement about the discriminator. It is escalated below rather than resolved
in my favour by fiat.

**Leg two — recommended dimensions differ.** `hr.json`'s default order is prose: work type or named people
programme first, then workforce unit or cohort, then people cycle, and "Never lead with the employee's name."
This row's recommendation leads with **the place or activity the duty attaches to**. `Fire Risk Assessment
2026.pdf`, `Permit 0412.pdf` and `Incident 26-031` are unintelligible without the building or the task, and
perfectly intelligible without knowing which department the injured person sat in — the inverse of a payroll
or engagement corpus. That is a different parent dimension, argued from the design's own "Homework 3 is
meaningless without the course" principle. `dimension_order` is nonetheless `[]` under PR-6, and the
recommendation is held as prose exactly as `hr.json` holds its own.

**Leg three — privacy rules differ, in both directions.** The schema's rule is uniform: employee-identifying
content is protected before any cloud step. This row needs a **split** posture. On one side it is stricter in
substance: occupational-health opinions and audiometry datasets are health information, and `00` says a
"medical document should enter a protected state immediately" and that protected material "should not display
raw content in general group summaries, and should not be moved automatically without a user policy that
explicitly permits it". On the other side it must be *looser* than the schema default, because applying a
protected posture to person-free COSHH and fire assessments would make a fire-safety folder local-only for no
protective gain. A uniform schema-level rule cannot express "protect on the person-plus-health join, treat the
person-free instrument as ordinary". **Leg three passes**, and it is the leg the row would fail if it were
only the employee-identifying residue that alternative (b) of NJ-WHS-2 would leave it.

**Verdict.** Three legs, three independent differences. Accept.

## Sources used

- `planning/domains/dispatch/RESEARCH-BRIEF.md`, and the stamped assignment from `make_prompt.py`.
- `planning/00-database-agent-product-design.md` — reached by targeted `grep -n` for the four spans quoted
  in the JSON. Every quotation was grep-verified verbatim before it was written; lines 35, 45, 120 and 185.
- `planning/domains/nodes/hr.json` — the schema anchor and the default template this row is measured against.
- `planning/domains/nodes/legal.practice-matter-file.research.md` — one landed launch row, for depth calibration.
- One grep for landed rows naming this id, which returned seven files; I read only the matched boundary
  spans from each, never the whole files.
- `planning/domains/roster.json` — every edge id in the JSON was programmatically checked against
  `nodes[].domain_id`. All eight `collides_with` ids, all four `also_holds_with` ids and all three
  `role_split` ids exist.
- `planning/domains/canonical_fields.json` — every key named in `facts_legal` checked against `fields[].key`.
  One correction made: `capture_date` is not canonical; the register has `capture_year`, and the toolbox-talk
  photograph fixture was amended.

## Files considered and rejected

Naming what this row does *not* hold was the most useful part of the pass.

- **`Safety Data Sheet - Isopropanol 99% - Merck.pdf`** — kept in the JSON as the primary **collision
  fixture**. It is the most safety-looking document in any workplace corpus, it sits in the same folder as
  the COSHH assessment, and it is a *supplier's publication* — the same bytes are downloadable by anyone.
  Discriminator: no persons-at-risk slot, no existing-controls slot, no assessor, no review date, no employer.
  Routes to Reading Inbox. Its existence is why this row's anchor is a slot set and not a vocabulary.
- **`PAT test register - Head Office - Q1 2026.csv`** — kept as the **second collision fixture**. Filed in
  every safety folder on earth; actually an asset-condition record on a maintenance cycle. It is the clean
  case that proves the structural discriminator against the facilities row: no assessment slots, so it is
  theirs. Note the near-twin that *is* mine — a statutory thorough-examination report of a hoist, which
  states a defect as a danger to persons with a timescale.
- **`Health and Safety Policy v3.pdf`** — the governing corporate policy. `business_operations` owns it under
  the policy-versus-application split the `hr` schema already draws for the handbook. An employee's signed
  acknowledgement of it is a different file with a different owner.
- **ISO 45001 audit report and certificate** — an audit against a management standard, producing
  non-conformities and a certification decision. `business_operations.compliance-audit`.
- **Employer's liability insurance certificate** — displayed for statutory reasons, but an insurance
  instrument. Finance owns the policy and premium slots; `also_holds_with: finance` records the overlap.
- **`First Aid at Work certificate - J Patel.pdf`** held in J Patel's own corpus — career. The employer's
  *matrix* of who holds which competence is mine. This became the `career` collision edge.
- **`Incident 4471 - Sev1 postmortem - checkout API.md`** — carries incident, reference number, root cause
  and corrective actions, and is a service-operations record. It is the reason the whole incident vocabulary
  is in `never_alone` rather than in `deterministic`.
- **Fire alarm servicing invoice; PPE line items in a purchase order** — finance. Subject matter is not a duty.
- **A personal injury solicitor's letter after a car crash** — a named person plus injury words plus an
  investigation. Legal or medical, never this row.
- **Construction phase plan / F10 notification** — `construction_property.site-health-safety`, conceded.
- **CCTV footage of an incident** — kept out of the fixture list deliberately. It may join an accepted
  incident group as an opaque member, but it manufactures no fact and should not be transcribed or analysed
  to improve classification.

## Reciprocal boundaries

Eight `collides_with` edges are authored, each naming the same fixture on both sides and stating the
prohibition in both directions. Five are reciprocals I owe to rows that authored against me first
(`business_operations.facilities-workplace`, `business_operations.compliance-audit`,
`business_operations.risk-register`, `construction_property.site-health-safety`,
`government.emergency-management`), one is a reciprocal that neighbour explicitly flagged as owed
(`clinical_practice.malpractice-incident` — "Authored ONE-WAY here; R1c owes the reciprocal"), one is a
boundary I accept as that row argued it (`hr.employee-relations`), and one is new (`career`).

The two worth restating here:

- **`hr.employee-relations`** — shared fixture `Occupational health referral and report - J Patel -
  capability.pdf`, named identically on both sides. That row is right and I say so in the JSON: this row must
  not take a capability case because it cites health; that row must not take an injury or hazard report
  because it names a person and has an investigation. Both rows independently reached the conclusion that the
  `hr` schema's single lumping bullet should be split, and neither may edit the schema — hence NJ-WHS-5.
- **`clinical_practice.malpractice-incident`** — shared fixture `Ward incident - sharps injury - staff.pdf`.
  One reporting system, one form, one reference vocabulary for patient harm and staff injury. The form
  structure discriminates *nothing* and must count for neither row alone; the affected-person block decides.
  This memo lands that reciprocal.

## Deliberate non-edges

- `hr.training-development` — no `collides_with`. The toolbox-talk register genuinely touches both, but the
  discriminator (is the session a named control measure, or a curriculum item?) is recorded in `needs_llm`
  and in the fixture's `must_not_conclude` instead. Elevating it to a mutex would imply a general
  training-versus-safety contest that does not exist; if landed sibling research finds a true same-evidence
  mutex, R1c can add it.
- `hr.workforce-analytics` — the audiometry cohort spreadsheet is multi-employee, but a health-surveillance
  dataset is not workforce analysis. Recorded as a `must_not_conclude` on that fixture rather than an edge.
- `business_operations.retrospective-postmortem` — the Sev1 fixture is handled by `never_alone`. A
  same-evidence mutex would overstate it: nothing in a software postmortem has a persons-at-risk slot.
- `hr.payroll-benefits-administration`, `hr.dei-program`, `hr.onboarding-offboarding` — no shared evidence.
  A safety induction is part of onboarding but the induction *record* joins on the joiner process, not the duty.

## proposed_fields — empty, deliberately

`fields: []` is mandated (PR-6). `proposed_fields: []` is a judgement and it is the one place I nearly
minted a key.

This row's recommended dimension order needs a **place** anchor, and I checked whether one exists before
proposing. It does not: `business_operations.facilities-workplace` proposes only `organization` and
`fiscal_period`; `construction_property.site-health-safety` and `government.emergency-management` propose no
fields at all. So a `premises` key would be genuinely new.

I did not mint it, because the brief says to reuse an existing proposal rather than mint a variant, and the
`hr` schema's `workforce_unit` proposal **already carries a location sense in its own example** — "Customer
Operations or Hong Kong warehouse". That single example holds two different things: a department and a site.
A payroll corpus keys on the first; this row keys on the second. Minting `premises` would fork a proposal
that R1c has not yet adjudicated. Instead the dual sense is raised as **NJ-WHS-3**, with the consequence
stated plainly: if the location sense is dropped when R1c settles `workforce_unit`, this row's recommended
dimension order becomes unusable and must be re-derived.

## Recognition notes

The `deterministic` list is deliberately structural rather than lexical. Every bullet names a *joint slot
set* or an *audience*, never a word. The `never_alone` list is built from the twelve tempting false files
above, so that each entry is tripped by a real named file rather than by a hypothetical: the Sev1 postmortem
trips the incident-vocabulary entry, the corporate risk register trips the hazard-column entry, the lease
trips the address entry, the motor-claim letter trips the person-plus-injury entry, the SDS trips the
supplier-publication entry, the first-aid certificate trips the qualification entry.

Two `00` prohibitions are carried verbatim into `never_alone` because they are directly load-bearing here:
extension-as-meaning (safety corpora are extension-diverse and folder-driven) and session-as-topic (an
incident's members are frequently downloaded together from an incident-reporting system in one burst, which
is precisely the trap).

`group_without_copying_facts: true` is set on five fixtures — the SDS, the toolbox-talk photograph, the
investigation archive, the unlabelled prose note and the drill calendar item — because each can legitimately
sit inside an accepted group while carrying none of the group's person, premises or incident facts.

## NEEDS-JOSEPH

Five items, all serialized in the JSON's `open_question`:

1. **NJ-WHS-1** — acceptance is conditional on NJ-HR-1. If the `hr` schema is refused, this coverage does
   not fall to one place, and the row should be re-refused rather than re-parented. Routing spelled out.
2. **NJ-WHS-2** — the contested boundary with `business_operations.facilities-workplace`. Three alternatives
   are spelled out: (a) my structural split (assessment instrument here, premises management there);
   (b) that row's already-authored who-is-at-risk split, which shrinks this row to the incident /
   occupational-health / statutory-return spine and **requires R1c to re-run the node test on the residue**;
   (c) premises assessments to facilities and activity assessments here, which splits one fire log across two
   rows and this row opposes.
3. **NJ-WHS-3** — the dual sense of the proposed `workforce_unit` key (department vs site).
4. **NJ-WHS-4** — whether a de-identified health-surveillance dataset is protected by default. This row says
   yes, on re-identification through small work areas, and states no threshold.
5. **NJ-WHS-5** — whether the `hr` schema's lumped employee-relations / workplace-safety recognition bullet
   should be split. Recommended independently by this row and by `hr.employee-relations`.

## Recommendations to R1c (no cross-row edits made)

- Adopt the split of the `hr` schema's lumped recognition bullet (NJ-WHS-5).
- Adjudicate NJ-WHS-2 and, if alternative (b) wins, re-run the node test on this row's residue.
- Record the reciprocals this memo lands one-way from my side onto the neighbour rows I may not edit:
  `clinical_practice.malpractice-incident` (explicitly owed by that row), `government.emergency-management`
  (explicitly owed by that row), and the new `career` edge.

## Self-verification

- `python3 -m json.tool` parses the node file. Key set matches the landed `hr` siblings.
- All eight `collides_with`, four `also_holds_with` and three `role_split` ids checked against
  `roster.json` `nodes[].domain_id` — all present.
- All four `falls_through_to` templates are `00` residual names: Protected Records, Independent Records,
  Reading Inbox, Review Later. Fixture-level `falls_through_if_inactive` values add One-Off Images, also a
  `00` residual.
- Every `file_examples.source_type` is in `SOURCE_TYPES`.
- Every key in every `facts_legal` verified against `canonical_fields.json`; `capture_date` was rejected by
  that check and corrected to `capture_year`.
- Every quoted `00` span grep-verified verbatim from `planning/00-database-agent-product-design.md`.
  Quotations of `hr.json` and of neighbour rows are marked as such, not attributed to `00`.
- No thresholds, no percentages, no file counts, no handling classes, no folder paths as facts.
- `fields: []`, `proposed_fields: []`, `template.dimension_order: []`, `time_first: false`.
- Files written: only the two assigned. No roster, canonical-fields, `check.py`, `src/`, SPEC or neighbour
  file was touched.
